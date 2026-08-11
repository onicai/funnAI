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
  import { getSharedAgentPrice, getOwnAgentPrice, getIsProtocolActive, getIsMainerCreationStopped, getWhitelistAgentPrice, getPauseWhitelistMainerCreationFlag, getBonusCyclesTopupInPercent } from "../../helpers/gameState";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId?: string) => void = () => {};
  export let modelType: 'Own' | 'Shared' = 'Own';
  export let selectedUnlockedMainer: any = null;
  export let isWhitelistPhaseActive: boolean = false;
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;
  
  // Token info loaded from token_helpers.ts
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
  $: isProtocolActive = isProtocolActiveFlag; // When false, stops mAIner creation activities

  let isMainerCreationStoppedFlag = false; // Will be loaded
  $: stopMainerCreation = isMainerCreationStoppedFlag; // When true, disables mAIner creation

  let isPauseWhitelistMainerCreationFlag = false; // Will be loaded
  $: isPauseWhitelistMainerCreation = isPauseWhitelistMainerCreationFlag;

  let bonusCyclesTopupInPercent = 0;
  $: showCreationBonus = bonusCyclesTopupInPercent > 0;
  
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
      await loadProtocolFlags();
      if (!isProtocolActive) {
        throw new Error("Protocol is not active and actions are paused");
      };

      if (stopMainerCreation) {
        throw new Error("mAIner creation is currently stopped");
      };

      if (isWhitelistPhaseActive && isPauseWhitelistMainerCreation) {
        throw new Error("The whitelist sale is currently stopped");
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
  };

  async function loadProtocolFlags() {
    try {
      isProtocolActiveFlag = await getIsProtocolActive();
      isMainerCreationStoppedFlag = await getIsMainerCreationStopped(modelType);
      isPauseWhitelistMainerCreationFlag = await getPauseWhitelistMainerCreationFlag();
    } catch (error) {
      console.error("Error loading protocol flags:", error);
      // Set safe defaults
      isProtocolActiveFlag = true;
      isMainerCreationStoppedFlag = true;
      isPauseWhitelistMainerCreationFlag = true;
      // Retry
      setTimeout(async () => {
        await loadProtocolFlags();
      }, 2000);
    };
  };

  async function loadBonusPercent() {
    bonusCyclesTopupInPercent = await getBonusCyclesTopupInPercent();
  };

  onMount(async () => {
    await loadTokenData();
    loadBalance();
    await loadProtocolFlags();
    mainerPrice = await getMainerPrice();
    await loadBonusPercent();
  });

  $: if (isOpen) {
    loadBonusPercent();
  }
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
  <div class="space-y-4">
    {#if isTokenLoading}
      <div class="flex justify-center py-4">
        <span class="w-6 h-6 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
      </div>
    {:else}
      <!-- Token Info Banner -->
      <div class="flex items-center gap-2 sm:gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/10">
        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex-shrink-0 overflow-hidden">
          <div class="sm:hidden">
            <TokenImages tokens={[token]} size={32} showSymbolFallback={true} />
          </div>
          <div class="hidden sm:block">
            <TokenImages tokens={[token]} size={38} showSymbolFallback={true} />
          </div>
        </div>
        <div class="flex flex-col min-w-0 flex-1">
          <div class="text-white font-medium text-sm sm:text-base truncate">{token.name}</div>
          <div class="text-xs sm:text-sm text-gray-400 truncate">Balance: {formatBalance(balance.toString(), token.decimals)} {token.symbol}</div>
          {#if showCreationBonus}
            <div class="text-[10px] font-medium text-emerald-400 truncate">+{bonusCyclesTopupInPercent}% bonus cycles</div>
          {/if}
        </div>
      </div>

      <!-- Payment Info -->
      <div class="flex flex-col gap-3">
        <!-- Recipient Address - only show if user has enough balance -->
        {#if hasEnoughBalance}
          <div>
            <span class="block text-xs text-gray-400 mb-1.5">Recipient</span>
            <div class="relative">
              <input
                type="text"
                class="agent-input w-full pr-8 text-xs sm:text-sm"
                value={protocolAddress}
                disabled
              />
              <div class="absolute inset-y-0 right-0 flex items-center">
                <div class="p-1.5 text-emerald-400">
                  <Check size={14} class="sm:hidden" />
                  <Check size={16} class="hidden sm:block" />
                </div>
              </div>
            </div>
            <div class="mt-1 text-xs text-emerald-400/80">funnAI mAIner creation address</div>
          </div>
        {/if}

        <!-- Amount -->
        <div>
          <span class="block text-xs text-gray-400 mb-1.5">Payment Amount</span>
          <div class="relative">
            <input
              type="text"
              class="agent-input w-full pr-12 sm:pr-16 text-xs sm:text-sm"
              value={totalPaymentAmount}
              disabled
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-400">{token.symbol}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-400">
            Protocol fees included
            {#if showCreationBonus}
              <span class="text-emerald-400"> · +{bonusCyclesTopupInPercent}% bonus cycles included</span>
            {/if}
          </div>
        </div>
        
        <!-- Payment Description -->
        <div class="p-3 rounded-xl text-xs sm:text-sm {isWhitelistPhaseActive && selectedUnlockedMainer ? 'bg-amber-500/5 border border-amber-500/20 text-amber-300' : 'bg-sky-500/5 border border-sky-500/20 text-sky-300/90'}">
          {#if isWhitelistPhaseActive && selectedUnlockedMainer}
            This whitelist payment ({totalPaymentAmount} {token.symbol} total including network fees) allows you to finish the set up of your pre-unlocked mAIner at a special discounted price. Once payment is complete, your mAIner will be created automatically.
          {:else}
            This payment ({totalPaymentAmount} {token.symbol} total including network fees) is used to create your mAIner. Once payment is complete, your mAIner will be created automatically.
          {/if}
          {#if showCreationBonus}
            <div class="mt-2 text-emerald-400">
              Includes +{bonusCyclesTopupInPercent}% bonus cycles on ICP payments
            </div>
          {/if}
        </div>

        <!-- Error message -->
        {#if errorMessage}
          <div class="p-3 bg-red-500/10 rounded-xl border border-red-500/25">
            <p class="text-sm text-red-300">{errorMessage}</p>
          </div>
        {/if}

        <!-- Insufficient balance helper -->
        {#if !hasEnoughBalance && !isValidating && token}
          <div class="p-3 bg-amber-500/5 rounded-xl border border-amber-500/20">
            <p class="text-sm text-amber-300">
              You need {formatBalance((amountBigInt - balance).toString(), token.decimals)} more {token.symbol} to create this mAIner.
            </p>
          </div>
        {/if}

        <!-- Send Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="w-full agent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed {!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation) ? 'bg-white/10 hover:bg-white/10 text-gray-500 shadow-none' : ''}"
          disabled={!hasEnoughBalance || isValidating || !isProtocolActive || stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>Processing...</span>
          {:else if !hasEnoughBalance}
            <div class="flex flex-col items-center justify-center gap-1">
              <span>Insufficient Balance</span>
              <a href="/#/wallet" class="underline text-xs sm:text-sm text-amber-300 hover:text-amber-200">Please fund your wallet ↗</a>
            </div>
          {:else if !isProtocolActive}
            <span class="text-center">Protocol is currently paused. Please check back in a couple of minutes.</span>
          {:else if stopMainerCreation || (isWhitelistPhaseActive && isPauseWhitelistMainerCreation)}
            <span class="text-center">mAIner creation is currently paused. Please check official announcements.</span>
          {:else}
            <ArrowUp size={16} />
            <span>Pay {totalPaymentAmount} {token.symbol}</span>
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.mainer-payment-modal) {
    max-width: min(480px, calc(100vw - 2rem));
  }

  :global(.modal-panel.mainer-payment-modal),
  :global(.mainer-payment-modal.modal-panel) {
    background: #15141B !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 1rem !important;
    color: #e5e7eb !important;
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
