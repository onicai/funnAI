<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";
  import { ArrowUp, Check } from 'lucide-svelte';
  import { MEMO_PAYMENT_PROTOCOL, store, theme } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, protocolConfig } from "../../helpers/token_helpers";
  import { getSharedAgentPrice, getOwnAgentPrice, getIsProtocolActive, getIsMainerCreationStopped, getWhitelistAgentPrice, getPauseWhitelistMainerCreationFlag } from "../../helpers/gameState";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId?: string) => void = () => {};
  export let modelType: 'Own' | 'Shared' = 'Own';
  export let selectedUnlockedMainer: any = null;
  export let isWhitelistPhaseActive: boolean = false;
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;

  console.log("in MainerPaymentModal protocolAddress ", protocolAddress);
  
  // TODO: load token info from token_helpers.ts
  let token: any = null;
  let isTokenLoading: boolean = true;
  
  // Load token data from token_helpers
  async function loadTokenData() {
    isTokenLoading = true;
    try {
      const result = await fetchTokens({});
      const icpToken = result.tokens.find(t => t.symbol === "ICP");
      if (icpToken) {
        token = icpToken;
      } else {
        throw new Error("ICP token not found in token_helpers");
      }
    } catch (error) {
      console.error("Error loading token data:", error);
      // Fallback to default values if token data can't be loaded
      token = {
        name: "Internet Computer",
        symbol: "ICP",
        decimals: 8,
        fee_fixed: "10000", // standard ICP fee
        canister_id: "ryjl3-tyaaa-aaaaa-aaaba-cai" // ICP Ledger canister ID
      };
    } finally {
      isTokenLoading = false;
    }
  }
  
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let tokenFee: bigint = BigInt(0); // Will be set once token is loaded
  let balance: bigint = BigInt(0);
  let mainerPrice = 1000; // Will be loaded

  let isProtocolActiveFlag = true; // Will be loaded
  $: isProtocolActive = isProtocolActiveFlag; // TODO: if protocol is not active, stop activities, especially mAIner creation

  let isMainerCreationStoppedFlag = false; // Will be loaded
  $: stopMainerCreation = isMainerCreationStoppedFlag; // TODO: if true, disable mAIner creation

  let isPauseWhitelistMainerCreationFlag = false; // Will be loaded
  $: isPauseWhitelistMainerCreation = isPauseWhitelistMainerCreationFlag;
  
  // Determine payment amount based on model type
  $: paymentAmount = mainerPrice;
  $: amountBigInt = token ? BigInt(new BigNumber(paymentAmount).times(new BigNumber(10).pow(token.decimals)).toString()) : BigInt(0);
  $: hasEnoughBalance = balance >= (amountBigInt + tokenFee);
  $: if (token) {
    tokenFee = BigInt(token.fee_fixed);
  }
  
  // Calculate total amount including fee for display
  $: totalPaymentAmount = token ? new BigNumber(paymentAmount).toString() : paymentAmount;

  async function loadBalance() {
    try {
      if (!$store.principal || !token) return;
      
      balance = await IcrcService.getIcrc1Balance(
        token,
        $store.principal
      ) as bigint;
    } catch (error) {
      console.error("Error loading balance:", error);
    }
  };

  async function getMainerPrice() {
    try {
      let price;
      
      // Use whitelist pricing if in whitelist phase and we have a selected unlocked mAIner
      if (isWhitelistPhaseActive && selectedUnlockedMainer) {
        price = await getWhitelistAgentPrice();
      } else {
        price = modelType === 'Own' ? await getOwnAgentPrice() : await getSharedAgentPrice();
      }

      if (price <= 0) {
        console.error("Issue getting mAIner price as it's 0 or negative.");
        errorMessage = `The price for the mAIner didn't load correctly. Please try again.`;
      };

      return Number(price);      
    } catch (error) {
      console.error("Error getting mAIner price:", error);
      errorMessage = `There was an error loading the price for the mAIner. Please try again.`;
    }
  };

  async function handleSubmit() {
    if (isValidating || !token) return;
    isValidating = true;
    errorMessage = "";

    try {
      if (!isProtocolActive) {
        throw new Error("Protocol is not active and actions are paused");
      };

      if (stopMainerCreation) {
        throw new Error("mAIner creation is currently stopped");
      };

      if (!$store.principal) {
        throw new Error("Authentication not initialized");
      }
      
      if (!hasEnoughBalance) {
        throw new Error("Insufficient balance for transfer + fee");
      }

      const result = await IcrcService.transfer(
        token,
        protocolAddress,
        amountBigInt,
        {
          fee: tokenFee,
          // Include the memo for transactions to the Protocol
          memo: MEMO_PAYMENT_PROTOCOL
        }
      );

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        // TODO: persist txId
        onSuccess(txId);
        onClose();
      } else if (result && typeof result === 'object' && 'Err' in result) {
        const errMsg = typeof result.Err === 'object' 
          ? Object.keys(result.Err)[0]
          : String(result.Err);
        errorMessage = `Transfer failed: ${errMsg}`;
        console.error("Transfer error details:", result.Err);
      }
    } catch (err) {
      console.error("Transfer error:", err);
      errorMessage = err.message || "Transfer failed";
    } finally {
      isValidating = false;
    }
  }

  onMount(async () => {
    await loadTokenData();
    loadBalance();
    isProtocolActiveFlag = await getIsProtocolActive();
    isMainerCreationStoppedFlag = await getIsMainerCreationStopped(modelType);
    isPauseWhitelistMainerCreationFlag = await getPauseWhitelistMainerCreationFlag();
    mainerPrice = await getMainerPrice();
  });
</script>

<Modal
  {isOpen}
  onClose={onClose}
  title={isWhitelistPhaseActive && selectedUnlockedMainer ? "Whitelist mAIner Creation Payment" : "mAIner Creation Payment"}
  width="min(480px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="mainer-payment-modal"
  isPadded={true}
>
  <div class="px-2 sm:px-4 py-4 flex flex-col gap-3 sm:gap-4">
    {#if isTokenLoading}
      <div class="flex justify-center py-4">
        <span class="w-6 h-6 border-2 border-gray-400/30 border-t-gray-400 dark:border-gray-400/30 dark:border-t-gray-400 rounded-full animate-spin"></span>
      </div>
    {:else}
      <!-- Token Info Banner -->
      <div class="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg bg-gray-100 border border-gray-300 text-gray-900 dark:bg-gray-700/20 dark:border-gray-600/30 dark:text-gray-100">
        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-800 dark:border-gray-700">
          <div class="sm:hidden">
            <TokenImages tokens={[token]} size={32} showSymbolFallback={true} />
          </div>
          <div class="hidden sm:block">
            <TokenImages tokens={[token]} size={38} showSymbolFallback={true} />
          </div>
        </div>
        <div class="flex flex-col min-w-0 flex-1">
          <div class="text-gray-900 font-medium dark:text-gray-100 text-sm sm:text-base truncate">{token.name}</div>
          <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 truncate">Balance: {formatBalance(balance.toString(), token.decimals)} {token.symbol}</div>
        </div>
      </div>

      <!-- Payment Info -->
      <div class="flex flex-col gap-2 sm:gap-3">
        <!-- Recipient Address - only show if user has enough balance -->
        {#if hasEnoughBalance}
          <div>
            <label class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">Recipient</label>
            <div class="relative">
              <input
                type="text"
                class="w-full py-2 px-2 sm:px-3 bg-white border border-gray-300 rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 pr-8"
                value={protocolAddress}
                disabled
              />
              <div class="absolute inset-y-0 right-0 flex items-center">
                <div class="p-1.5 text-green-500">
                  <Check size={14} class="sm:hidden" />
                  <Check size={16} class="hidden sm:block" />
                </div>
              </div>
            </div>
            <div class="mt-1 text-xs text-green-600 dark:text-green-500">funnAI mAIner creation address</div>
          </div>
        {/if}

        <!-- Amount -->
        <div>
          <label class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">Payment Amount</label>
          <div class="relative">
            <input
              type="text"
              class="w-full py-2 px-2 sm:px-3 bg-white border border-gray-300 rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 pr-12 sm:pr-16"
              value={totalPaymentAmount}
              disabled
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-600 dark:text-gray-400">{token.symbol}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Protocol fees included
          </div>
        </div>
        
        <!-- Payment Description -->
        <div class="p-2 sm:p-3 rounded-lg {isWhitelistPhaseActive && selectedUnlockedMainer ? 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800/30 dark:text-yellow-200' : 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800/30 dark:text-blue-200'} text-xs sm:text-sm">
          {#if isWhitelistPhaseActive && selectedUnlockedMainer}
            This whitelist payment ({totalPaymentAmount} {token.symbol} total including network fees) allows you to finish the set up of your pre-unlocked mAIner at a special discounted price. Once payment is complete, your mAIner will be created automatically.
          {:else}
            This payment ({totalPaymentAmount} {token.symbol} total including network fees) is used to create your mAIner. Once payment is complete, your mAIner will be created automatically.
          {/if}
        </div>

        <!-- Error message -->
        {#if errorMessage}
          <div class="mt-1 p-2 rounded bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm dark:bg-red-900/30 dark:border-red-900/50 dark:text-red-400">
            {errorMessage}
          </div>
        {/if}

        <!-- Send Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="mt-2 py-2 sm:py-2.5 px-3 sm:px-4 rounded-md text-white font-medium transition-colors text-sm sm:text-base"
          class:flex={!(!hasEnoughBalance && !isValidating)}
          class:items-center={!(!hasEnoughBalance && !isValidating)}
          class:justify-center={!(!hasEnoughBalance && !isValidating)}
          class:gap-2={!(!hasEnoughBalance && !isValidating)}
          class:bg-purple-600={hasEnoughBalance && !isValidating}
          class:hover:bg-purple-500={hasEnoughBalance && !isValidating}
          class:bg-gray-400={!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
          class:cursor-not-allowed={!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
          class:dark:bg-gray-700={!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
          disabled={!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
        >
          {#if isValidating}
            <div class="flex items-center justify-center gap-2">
              <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              Processing...
            </div>
          {:else if !hasEnoughBalance}
            <div class="flex flex-col items-center justify-center gap-1">
              <div class="text-center">Insufficient Balance</div>
              <a href="/#/wallet" class="underline text-xs sm:text-sm text-orange-800 dark:text-orange-200 hover:text-orange-900 dark:hover:text-orange-100">Please fund your wallet ↗</a>
            </div>
          {:else if !isProtocolActive}
            <div class="flex flex-col items-center justify-center gap-1">
              <div class="text-center">Protocol is currently paused. Please check back in a couple of minutes.</div>
            </div>
          {:else if stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
            <div class="flex flex-col items-center justify-center gap-1">
              <div class="text-center">mAIner creation is currently paused. Please check official announcements.</div>
            </div>
          {:else}
            <div class="flex items-center justify-center gap-2">
              <ArrowUp size={14} class="sm:hidden" />
              <ArrowUp size={16} class="hidden sm:block" />
              Pay {totalPaymentAmount} {token.symbol}
            </div>
          {/if}
        </button>
        
        <!-- Insufficient balance helper -->
        {#if !hasEnoughBalance && !isValidating && token}
          <div class="mt-2 p-2 rounded bg-orange-50 border border-orange-200 text-orange-700 text-xs sm:text-sm dark:bg-orange-900/30 dark:border-orange-800/30 dark:text-orange-300">
            You need {formatBalance((amountBigInt - balance).toString(), token.decimals)} more {token.symbol} to create this mAIner.
          </div>
        {/if}
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.mainer-payment-modal) {
    max-width: min(480px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure proper text wrapping on mobile */
  :global(.mainer-payment-modal .truncate) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 640px) {
    :global(.mainer-payment-modal) {
      margin: 0.5rem;
    }
  }
</style> 