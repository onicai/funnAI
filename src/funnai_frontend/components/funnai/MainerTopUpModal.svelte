<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";

  import { ArrowUp, Info, Check } from 'lucide-svelte';
  import { MEMO_PAYMENT_PROTOCOL, store, theme } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance, formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, protocolConfig } from "../../helpers/token_helpers";
  import { createAnonymousActorHelper } from "../../helpers/utils/actorUtils";
  import { idlFactory as cmcIdlFactory } from "../../helpers/idls/cmc.idl.js";
  import { MIN_AMOUNT, MAX_AMOUNT, CELEBRATION_DURATION, CELEBRATION_ENABLED } from "../../helpers/config/topUpConfig";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId: string, canisterId: string) => void = () => {};
  export let onCelebration: (amount: string, token: string) => void = () => {};
  export let canisterId: string = "";
  export let canisterName: string = "";
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;

  console.log("in MainerTopUpModal protocolAddress ", protocolAddress);
  
  // ICP token configuration - load from token_helpers
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
        fee_fixed: "10000", // 0.0001 ICP fee
        canister_id: "ryjl3-tyaaa-aaaaa-aaaba-cai" // ICP Ledger canister ID
      };
    } finally {
      isTokenLoading = false;
    }
  }
  
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let isLoadingConversionRate: boolean = true;
  let tokenFee: bigint = BigInt(0); // Will be set once token is loaded
  let balance: bigint = BigInt(0);
  let amount: string = "";
  let cyclesAmount: string = "0";
  let conversionRate: BigNumber | null = null;
  

  
  $: isValidAmount = amount && !isNaN(Number(amount)) && Number(amount) >= MIN_AMOUNT && Number(amount) <= MAX_AMOUNT;
  $: isBelowMinimum = amount && !isNaN(Number(amount)) && Number(amount) > 0 && Number(amount) < MIN_AMOUNT;
  $: isMaxAmount = amount && !isNaN(Number(amount)) && Number(amount) === MAX_AMOUNT;
  $: isAboveMaximum = amount && !isNaN(Number(amount)) && Number(amount) > MAX_AMOUNT;
  $: amountBigInt = isValidAmount && token
    ? BigInt(new BigNumber(amount).times(new BigNumber(10).pow(token.decimals)).toString())
    : BigInt(0);
  $: hasEnoughBalance = isValidAmount && balance >= (amountBigInt + tokenFee);
  $: if (token) {
    tokenFee = BigInt(token.fee_fixed);
  }
  
  // Reactive statement to automatically calculate cycles when amount or conversion rate changes
  $: if (conversionRate && amount && token) {
    calculateCycles();
  }
  
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
  }

  // Function to get ICP to Cycles conversion rate from CMC
  async function loadConversionRate() {
    isLoadingConversionRate = true;
    try {
      // Access the CMC canister and get the conversion rate
      const cmcCanisterId = "rkp4c-7iaaa-aaaaa-aaaca-cai";
      
      try {
        // Create the CMC actor using the imported IDL factory
        const cmcActor = await createAnonymousActorHelper(cmcCanisterId, cmcIdlFactory);
        console.log("loadConversionRate cmcActor: ", cmcActor);
        
        // Get conversion rate from CMC
        const response = await cmcActor.get_icp_xdr_conversion_rate();
        console.log("loadConversionRate cmcActor response: ", response);
        
        if (response && response.data) {
          const xdrRate = Number(response.data.xdr_permyriad_per_icp);
          console.log("loadConversionRate xdrRate: ", xdrRate);
          
          // 1 XDR = 1 trillion cycles, and the rate is in 10,000ths (permyriad)
          const CYCLES_PER_XDR = new BigNumber("1000000000000"); // 1 trillion cycles
          
          // Calculate: (xdr_permyriad_per_icp * CYCLES_PER_XDR) / 10000
          conversionRate = new BigNumber(xdrRate)
            .times(CYCLES_PER_XDR)
            .div(10000);
            
          console.log("Conversion rate loaded:", conversionRate.toString());
        } else {
          throw new Error("Failed to get conversion rate data");
        }
      } catch (actorError) {
        console.error("Error creating CMC actor:", actorError);
        throw new Error("Failed to create CMC actor");
      }
    } catch (error) {
      console.error("Error loading conversion rate:", error);
      errorMessage = "Using estimated conversion rate (10T cycles per ICP)";
      
      // Use fallback conversion rate (approximation as of last known rate)
      conversionRate = new BigNumber("10000000000000"); // ~10T cycles per ICP (fallback)
    } finally {
      isLoadingConversionRate = false;
    }
  }
  
  // Handle amount input and calculate cycles
  function handleAmountInput(event: Event) {
    const input = event.target as HTMLInputElement;
    let value = input.value.trim();
    
    // Apply formatting and validation
    if (value) {
      // Replace commas with dots to support different decimal separators
      value = value.replace(',', '.');
      
      // Check if the input is a valid number
      if (!/^[0-9]*\.?[0-9]*$/.test(value)) {
        return;
      }
      
      // Prevent more than 8 decimal places (ICP limit)
      const parts = value.split('.');
      if (parts.length > 1 && parts[1].length > 8) {
        parts[1] = parts[1].substring(0, 8);
        value = parts.join('.');
      }
    }
    
    amount = value;
    
    // Calculate equivalent cycles
    calculateCycles();
  }
  
  // Calculate cycles from ICP amount with proper conversion
  function calculateCycles() {
    if (!conversionRate || !amount || isNaN(Number(amount)) || Number(amount) <= 0 || !token) {
      cyclesAmount = "0";
      return;
    }
    
    try {
      const E8S_PER_ICP = new BigNumber(`1${"0".repeat(token.decimals)}`); // 10^decimals units per ICP
      
      // Convert amount to e8s format
      const [integral, fractional = ""] = amount.split(".");
      const e8sAmount = new BigNumber(integral).times(E8S_PER_ICP)
        .plus(new BigNumber(fractional.padEnd(token.decimals, '0').substring(0, token.decimals)));
      
      // Calculate e8s to cycles ratio
      const e8sToCycleRatio = conversionRate.div(E8S_PER_ICP);
      
      // Calculate cycles
      const cycles = e8sAmount.times(e8sToCycleRatio);
      
      // Use formatLargeNumber to format trillions
      cyclesAmount = formatLargeNumber(cycles.toNumber() / 1_000_000_000_000, 4, false);
      
      console.log(`${amount} ICP equals ${cyclesAmount} Trillion (${cycles.toString()}) cycles`);
    } catch (error) {
      console.error("Error calculating cycles:", error);
      cyclesAmount = "0";
    }
  }

  // Handle modal close function explicitly
  function handleClose() {
    isOpen = false;
    onClose();
  }



  async function handleSubmit() {
    if (isValidating || !hasEnoughBalance || !token) return;
    isValidating = true;
    errorMessage = "";

    try {
      if (!$store.principal) {
        throw new Error("Authentication not initialized");
      }
      
      if (!canisterId) {
        throw new Error("Canister ID is required");
      }
      
      // Transfer ICP to the Protocol's account for top-up
      // The backend will handle the actual cycles minting and top-up process
      const result = await IcrcService.transfer(
        token,
        protocolAddress,  // Use protocol address from token_helpers
        amountBigInt,
        {
          fee: tokenFee,
          // Include the memo for transactions to the Protocol
          memo: MEMO_PAYMENT_PROTOCOL
        }
      );
      console.log("handleSubmit result: ", result);

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        console.log("handleSubmit txId: ", txId);
        
        // Check if this was a maximum amount top-up to trigger celebration
        if (isMaxAmount && CELEBRATION_ENABLED) {
          // First close the modal, then trigger celebration
          onSuccess(txId, canisterId);
          handleClose();
          
          // Small delay to ensure modal is closed before showing celebration
          setTimeout(() => {
            onCelebration(amount, token?.symbol || 'ICP');
          }, 300);
          try {
            let maxTopUpInput = {
              paymentTransactionBlockId: BigInt(txId),
              toppedUpMainerId: canisterId,
              amount: BigInt(amount),
            };
            await $store.backendActor.addMaxMainerTopup(maxTopUpInput);            
          } catch (maxTopUpStorageError) {
            console.error("Top-up storage error: ", maxTopUpStorageError);            
          };
        } else {
          onSuccess(txId, canisterId);
          handleClose();
        }
      } else if (result && typeof result === 'object' && 'Err' in result) {
        const errMsg = typeof result.Err === 'object' 
          ? Object.keys(result.Err)[0]
          : String(result.Err);
        errorMessage = `Transfer failed: ${errMsg}`;
        console.error("Transfer error details:", result.Err);
      }
    } catch (err) {
      console.error("Top-up error:", err);
      errorMessage = err.message || "Top-up failed";
    } finally {
      isValidating = false;
    }
  }

  onMount(async () => {
    await loadTokenData();
    loadBalance();
    loadConversionRate();
  });
</script>

<Modal
  {isOpen}
  onClose={handleClose}
  title="Top up mAIner with ICP"
  width="min(480px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="mainer-topup-modal"
  closeOnEscape={true}
  closeOnClickOutside={true}
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

      <!-- Top-up Info -->
      <div class="flex flex-col gap-2 sm:gap-3">
        <!-- Recipient Address 
        <div>
          <label class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">Recipient</label>
          <div class="relative">
            <input
              type="text"
              class="w-full py-2 px-3 bg-white border border-gray-300 rounded-md text-sm text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100"
              value={protocolAddress}
              disabled
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <div class="p-1.5 text-green-500">
                <Check size={16} />
              </div>
            </div>
          </div>
          <div class="mt-1 text-xs text-green-600 dark:text-green-500">FunnAI Protocol Address</div>
        </div>
        -->
        
        <!-- Canister ID -->
        <div>
          <label class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">mAIner canister</label>
          <div class="relative">
            <input
              type="text"
              class="w-full py-2 px-2 sm:px-3 bg-white border border-gray-300 rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100"
              value={canisterName ? `${canisterName} (${canisterId})` : canisterId}
              disabled
            />
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-500">mAIner to be topped up</div>
        </div>

        <!-- Amount -->
        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label for="amount-input" class="block text-xs text-gray-600 dark:text-gray-400">ICP Amount</label>
            <button
              type="button"
              class="text-xs text-purple-600 hover:text-purple-800 dark:text-purple-500 dark:hover:text-purple-400 font-medium"
              on:click={() => amount = String(MAX_AMOUNT)}
            >
              Top up Max ({MAX_AMOUNT} {token?.symbol || 'ICP'})
            </button>
          </div>
          <div class="relative">
            <input
              type="text"
              inputmode="decimal"
              class="w-full py-2 px-2 sm:px-3 bg-white border rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-800 dark:text-gray-100 pr-12 sm:pr-16"
              class:border-green-400={hasEnoughBalance && isValidAmount}
              class:border-red-400={(!hasEnoughBalance && isValidAmount) || isAboveMaximum}
              class:border-yellow-400={isBelowMinimum}
              class:border-purple-500={isMaxAmount && hasEnoughBalance}
              class:border-gray-300={!isValidAmount && !isBelowMinimum && !isAboveMaximum}
              class:dark:border-gray-600={!isValidAmount && !isBelowMinimum && !isAboveMaximum}
              placeholder="Enter ICP amount to top up"
              bind:value={amount}
              on:input={handleAmountInput}
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-600 dark:text-gray-400">{token.symbol}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Protocol fees included
          </div>
          {#if isBelowMinimum}
            <div class="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
              Minimum amount: {MIN_AMOUNT} {token.symbol}
            </div>
          {/if}
          {#if isAboveMaximum}
            <div class="mt-1 text-xs text-red-600 dark:text-red-400">
              Maximum amount: {MAX_AMOUNT} {token.symbol}
            </div>
          {/if}
          {#if isMaxAmount && hasEnoughBalance}
            <div class="mt-1 text-xs text-purple-600 dark:text-purple-400 font-medium animate-pulse">
              🎉 Maximum amount! Get ready for something special! 🎉
            </div>
          {/if}
        </div>
        
        <!-- Cycles Conversion Display -->
        <div class="p-2 sm:p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-800 text-xs sm:text-sm flex flex-col gap-2 dark:bg-blue-900/20 dark:border-blue-800/30 dark:text-blue-200">
          <div class="flex items-center gap-1">
            <Info size={12} class="sm:hidden flex-shrink-0" />
            <Info size={14} class="hidden sm:block flex-shrink-0" />
            <span class="font-medium">Cycles Conversion</span>
            {#if isLoadingConversionRate}
              <span class="w-3 h-3 ml-2 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin dark:border-blue-400/30 dark:border-t-blue-400 flex-shrink-0"></span>
            {/if}
          </div>
          
          {#if !isLoadingConversionRate}
            <div class="flex justify-between items-center gap-2">
              <span class="truncate">{amount || '0'} ICP</span>
              <span class="font-medium text-right flex-shrink-0">≈ {cyclesAmount} Trillion Cycles</span>
            </div>
          {:else}
            <div class="text-blue-600/70 dark:text-blue-300/70">Loading conversion rate...</div>
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
          class="mt-2 py-2 sm:py-2.5 px-3 sm:px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors text-sm sm:text-base"
          class:bg-purple-600={hasEnoughBalance && !isValidating}
          class:hover:bg-purple-500={hasEnoughBalance && !isValidating}
          class:bg-gray-400={!hasEnoughBalance || isValidating}
          class:cursor-not-allowed={!hasEnoughBalance || isValidating}
          class:dark:bg-gray-700={!hasEnoughBalance || isValidating}
          disabled={!hasEnoughBalance || isValidating}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing...
          {:else}
            <ArrowUp size={14} class="sm:hidden" />
            <ArrowUp size={16} class="hidden sm:block" />
            Top up {amount || '0'} {token.symbol}
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>



<style>
  :global(.mainer-topup-modal) {
    max-width: min(480px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure proper text wrapping on mobile */
  :global(.mainer-topup-modal .truncate) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 640px) {
    :global(.mainer-topup-modal) {
      margin: 0.5rem;
    }
  }
</style> 