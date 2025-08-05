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
  import { MIN_AMOUNT, MAX_AMOUNT, FUNNAI_MIN_AMOUNT, FUNNAI_MAX_AMOUNT, CELEBRATION_DURATION, CELEBRATION_ENABLED } from "../../helpers/config/topUpConfig";
  import { getIsProtocolActive } from "../../helpers/gameState";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId: string, canisterId: string) => void = () => {};
  export let onCelebration: (amount: string, token: string) => void = () => {};
  export let canisterId: string = "";
  export let canisterName: string = "";
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;

  console.log("in MainerTopUpModal protocolAddress ", protocolAddress);
  
  // Token configurations - now supporting both ICP and FUNNAI
  let availableTokens: any[] = [];
  let selectedTokenSymbol: 'ICP' | 'FUNNAI' = 'FUNNAI';
  let isTokenLoading: boolean = true;
  
  // Get currently selected token
  $: selectedToken = availableTokens.find(t => t.symbol === selectedTokenSymbol);
  
  // Load token data from token_helpers
  async function loadTokenData() {
    isTokenLoading = true;
    try {
      const result = await fetchTokens({});
      const icpToken = result.tokens.find(t => t.symbol === "ICP");
      const funnaiToken = result.tokens.find(t => t.symbol === "FUNNAI");
      
      if (icpToken && funnaiToken) {
        availableTokens = [icpToken, funnaiToken];
      } else {
        throw new Error("Required tokens (ICP/FUNNAI) not found in token_helpers");
      }
    } catch (error) {
      console.error("Error loading token data:", error);
      // Fallback to default values if token data can't be loaded
      availableTokens = [
        {
          name: "Internet Computer",
          symbol: "ICP",
          decimals: 8,
          fee_fixed: "10000", // 0.0001 ICP fee
          canister_id: "ryjl3-tyaaa-aaaaa-aaaba-cai" // ICP Ledger canister ID
        },
        {
          name: "FUNNAI",
          symbol: "FUNNAI", 
          decimals: 8,
          fee_fixed: "1", // 0.00000001 FUNNAI fee
          canister_id: "vpyot-zqaaa-aaaaa-qavaq-cai" // FUNNAI canister ID
        }
      ];
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
  
  // Dynamic limits based on token type
  $: dynamicLimits = (() => {
    if (selectedTokenSymbol === 'FUNNAI') {
      // FUNNAI limits from config
      return {
        min: FUNNAI_MIN_AMOUNT,
        max: FUNNAI_MAX_AMOUNT
      };
    } else {
      // ICP limits from config
      return {
        min: MIN_AMOUNT,
        max: MAX_AMOUNT
      };
    }
  })();

  $: currentMinAmount = dynamicLimits.min;
  $: currentMaxAmount = dynamicLimits.max;

  
  $: isValidAmount = amount && !isNaN(Number(amount)) && Number(amount) >= currentMinAmount && Number(amount) <= currentMaxAmount;
  $: isBelowMinimum = amount && !isNaN(Number(amount)) && Number(amount) > 0 && Number(amount) < currentMinAmount;
  $: isMaxAmount = amount && !isNaN(Number(amount)) && Number(amount) === currentMaxAmount;
  $: isAboveMaximum = amount && !isNaN(Number(amount)) && Number(amount) > currentMaxAmount;
  $: amountBigInt = isValidAmount && selectedToken
    ? BigInt(new BigNumber(amount).times(new BigNumber(10).pow(selectedToken.decimals)).toString())
    : BigInt(0);
  $: hasEnoughBalance = isValidAmount && balance >= (amountBigInt + tokenFee);
  $: isFunnaiUnavailable = selectedTokenSymbol === 'FUNNAI' && (!conversionRate || conversionRate.isZero());
  $: canSubmit = hasEnoughBalance && !isValidating && selectedToken && !isFunnaiUnavailable;
  $: if (selectedToken) {
    tokenFee = BigInt(selectedToken.fee_fixed);
  }
  
  // Reactive statement to automatically calculate cycles when amount, conversion rate, or token changes
  $: if (conversionRate && amount && selectedToken) {
    calculateCycles();
  }
  
  // Load balance when selected token changes
  $: if (selectedToken && $store.principal) {
    loadBalance();
  }
  
  // Load conversion rate when selected token changes
  $: if (selectedToken) {
    loadConversionRate();
  }
  
  async function loadBalance() {
    try {
      if (!$store.principal || !selectedToken) return;
      
      balance = await IcrcService.getIcrc1Balance(
        selectedToken,
        $store.principal
      ) as bigint;
    } catch (error) {
      console.error("Error loading balance:", error);
    }
  }

  // Function to get conversion rate (ICP from CMC, FUNNAI from game state canister)
  async function loadConversionRate() {
    isLoadingConversionRate = true;
    errorMessage = ""; // Clear any previous error messages
    
    try {
      if (selectedTokenSymbol === 'FUNNAI') {
        // Get FUNNAI conversion rate from game state canister
        if (!$store.gameStateCanisterActor) {
          throw new Error("Game state canister not available");
        }
        
        try {
          const funnaiPriceResult = await $store.gameStateCanisterActor.getFunnaiCyclesPrice();
          
          if (funnaiPriceResult && 'Ok' in funnaiPriceResult) {
            const cyclesPerFunnai = funnaiPriceResult.Ok;
            conversionRate = new BigNumber(cyclesPerFunnai.toString());
            
            if (conversionRate.isZero()) {
              throw new Error("FUNNAI top-ups are currently not available (rate is 0)");
            }
            
            console.log("FUNNAI conversion rate loaded from backend:", conversionRate.toString(), "cycles per FUNNAI");
          } else {
            const errorMsg = funnaiPriceResult && 'Err' in funnaiPriceResult 
              ? (typeof funnaiPriceResult.Err === 'object' 
                  ? Object.keys(funnaiPriceResult.Err)[0] 
                  : String(funnaiPriceResult.Err))
              : "Failed to get FUNNAI conversion rate";
            throw new Error(errorMsg);
          }
        } catch (actorError) {
          console.error("Error getting FUNNAI conversion rate:", actorError);
          throw new Error("Failed to get FUNNAI conversion rate from backend");
        }
      } else {
        // ICP conversion rate from CMC
        const cmcCanisterId = "rkp4c-7iaaa-aaaaa-aaaca-cai";
        
        try {
          // Create the CMC actor using the imported IDL factory
          const cmcActor = await createAnonymousActorHelper(cmcCanisterId, cmcIdlFactory);
          
          // Get conversion rate from CMC
          const response = await cmcActor.get_icp_xdr_conversion_rate();
          
          if (response && response.data) {
            const xdrRate = Number(response.data.xdr_permyriad_per_icp);
            
            // 1 XDR = 1 trillion cycles, and the rate is in 10,000ths (permyriad)
            const CYCLES_PER_XDR = new BigNumber("1000000000000"); // 1 trillion cycles
            
            // Calculate: (xdr_permyriad_per_icp * CYCLES_PER_XDR) / 10000
            conversionRate = new BigNumber(xdrRate)
              .times(CYCLES_PER_XDR)
              .div(10000);
              
            console.log("ICP conversion rate loaded:", conversionRate.toString());
          } else {
            throw new Error("Failed to get conversion rate data");
          }
        } catch (actorError) {
          console.error("Error creating CMC actor:", actorError);
          throw new Error("Failed to create CMC actor");
        }
      }
    } catch (error) {
      console.error("Error loading conversion rate:", error);
      
      if (selectedTokenSymbol === 'FUNNAI') {
        if (error.message.includes("currently not available")) {
          errorMessage = "FUNNAI top-ups are currently not available";
          conversionRate = new BigNumber("0");
        } else {
          errorMessage = "Failed to get FUNNAI conversion rate from backend";
          conversionRate = new BigNumber("1000000000000"); // 1T cycles per FUNNAI (fallback)
        }
      } else {
        errorMessage = "Using estimated conversion rate (10T cycles per ICP)";
        conversionRate = new BigNumber("10000000000000"); // ~10T cycles per ICP (fallback)
      }
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
      
      // Prevent more than 8 decimal places (token limit)
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
  
  // Calculate cycles from token amount with proper conversion and validation
  function calculateCycles() {
    if (!conversionRate || !amount || isNaN(Number(amount)) || Number(amount) <= 0 || !selectedToken) {
      cyclesAmount = "0";
      return;
    }
    
    // Special handling for FUNNAI when rate is 0 (not available)
    if (selectedTokenSymbol === 'FUNNAI' && conversionRate.isZero()) {
      cyclesAmount = "0";
      return;
    }
    
    try {
      const E8S_PER_TOKEN = new BigNumber(`1${"0".repeat(selectedToken.decimals)}`); // 10^decimals units per token
      
      // Convert amount to smallest unit format (e8s for both ICP and FUNNAI)
      const [integral, fractional = ""] = amount.split(".");
      const smallestUnitAmount = new BigNumber(integral).times(E8S_PER_TOKEN)
        .plus(new BigNumber(fractional.padEnd(selectedToken.decimals, '0').substring(0, selectedToken.decimals)));
      
      // Calculate smallest unit to cycles ratio
      const smallestUnitToCycleRatio = conversionRate.div(E8S_PER_TOKEN);
      
      // Calculate cycles
      const cycles = smallestUnitAmount.times(smallestUnitToCycleRatio);
      
      // Validate cycles amount doesn't exceed limits
      const cyclesTrillion = cycles.div(new BigNumber("1000000000000"));
      
      // Use formatLargeNumber to format trillions
      cyclesAmount = formatLargeNumber(cycles.toNumber() / 1_000_000_000_000, 4, false);
      
      console.log(`${amount} ${selectedToken.symbol} equals ${cyclesAmount} Trillion (${cycles.toString()}) cycles`);
    } catch (error) {
      console.error("Error calculating cycles:", error);
      cyclesAmount = "0";
    }
  }

  // Handle token selection change
  function handleTokenChange(tokenSymbol: 'ICP' | 'FUNNAI') {
    selectedTokenSymbol = tokenSymbol;
    // Reset amount when switching tokens to avoid confusion
    amount = "";
    cyclesAmount = "0";
    errorMessage = "";
  }

  // Handle modal close function explicitly
  function handleClose() {
    isOpen = false;
    onClose();
  }

  async function handleSubmit() {
    if (isValidating || !hasEnoughBalance || !selectedToken) return;
    isValidating = true;
    errorMessage = "";

    try {
      // Security checks
      const isProtocolActive = await getIsProtocolActive();
      if (!isProtocolActive) {
        throw new Error("Protocol is not active and actions are paused");
      };

      if (!$store.principal) {
        throw new Error("Authentication not initialized");
      }
      
      if (!canisterId) {
        throw new Error("Canister ID is required");
      }

      // Additional FUNNAI-specific security checks
      if (selectedTokenSymbol === 'FUNNAI') {
        if (!conversionRate || conversionRate.isZero()) {
          throw new Error("FUNNAI top-ups are currently not available");
        }
        
        // Verify the game state canister is available for FUNNAI operations
        if (!$store.gameStateCanisterActor) {
          throw new Error("Game state canister not available for FUNNAI top-ups");
        }
        
        // Double-check conversion rate before proceeding
        try {
          const currentPriceResult = await $store.gameStateCanisterActor.getFunnaiCyclesPrice();
          if (!currentPriceResult || !('Ok' in currentPriceResult) || new BigNumber(currentPriceResult.Ok.toString()).isZero()) {
            throw new Error("FUNNAI top-ups are currently disabled");
          }
        } catch (priceCheckError) {
          console.error("Error checking FUNNAI price:", priceCheckError);
          throw new Error("Unable to verify FUNNAI conversion rate");
        };

        tokenFee = BigInt(0); // for burn transactions, set to 0
      }

      // Validate amount ranges
      if (!isValidAmount) {
        if (isBelowMinimum) {
          throw new Error(`Amount below minimum (${currentMinAmount} ${selectedToken.symbol})`);
        }
        if (isAboveMaximum) {
          throw new Error(`Amount above maximum (${currentMaxAmount} ${selectedToken.symbol})`);
        }
        throw new Error("Invalid amount");
      }

      console.log("debug selectedToken before transfer ", selectedToken);
      console.log("debug protocolAddress before transfer ", protocolAddress);
      console.log("debug tokenFee before transfer ", tokenFee);
      
      // Transfer tokens to the Protocol's account for top-up
      // The backend will handle the actual cycles minting and top-up process
      const result = await IcrcService.transfer(
        selectedToken,
        protocolAddress,  // Use protocol address from token_helpers
        amountBigInt,
        {
          fee: tokenFee,
          // Include the memo for transactions to the Protocol
          memo: MEMO_PAYMENT_PROTOCOL
        }
      );

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        console.log("handleSubmit txId: ", txId);
        
        // Call the appropriate backend endpoint to complete the top-up
        try {
          // Find the mAIner agent information from the store
          const mainerAgent = $store.userMainerAgentCanistersInfo.find(agent => agent.address === canisterId);
          if (!mainerAgent) {
            throw new Error("mAIner agent not found in user data");
          }

          // Helper function to clean enriched data (extract only original backend fields)
          function getOriginalCanisterInfo(enrichedCanisterInfo) {
            const {
              // Remove UI-specific fields that we added
              uiStatus,
              cycleBalance,
              burnedCycles,
              cyclesBurnRate,
              cyclesBurnRateSetting,
              llmCanisters,
              llmSetupStatus,
              hasError,
              // Keep only original backend fields
              ...originalInfo
            } = enrichedCanisterInfo;
            return originalInfo;
          }

          // Clean the enriched data to get only original backend fields
          const cleanMainerAgent = getOriginalCanisterInfo(mainerAgent);

          let topUpInput = {
            paymentTransactionBlockId: BigInt(txId),
            mainerAgent: cleanMainerAgent,
          };

          console.log("debug topUpInput ", topUpInput);
          console.log("debug selectedTokenSymbol ", selectedTokenSymbol);

          let backendResult;
          if (selectedTokenSymbol === 'FUNNAI') {
            // For FUNNAI, use the new FUNNAI-specific endpoint
            if (!$store.gameStateCanisterActor) {
              throw new Error("Game state canister not available");
            }
            console.log("debug before topUpCyclesForMainerAgentWithFunnai ");
            backendResult = await $store.gameStateCanisterActor.topUpCyclesForMainerAgentWithFunnai(topUpInput);
          } else {
            // For ICP, use the existing endpoint
            if (!$store.gameStateCanisterActor) {
              throw new Error("Game state canister not available");
            }
            console.log("debug before topUpCyclesForMainerAgent ");
            backendResult = await $store.gameStateCanisterActor.topUpCyclesForMainerAgent(topUpInput);
          }

          console.log("debug backendResult ", backendResult);

          // Check if backend call was successful
          if (backendResult && 'Ok' in backendResult) {
            console.log(`${selectedTokenSymbol} top-up completed successfully:`, backendResult.Ok);
            
            // Check if this was a maximum amount top-up to trigger celebration
            if (isMaxAmount && CELEBRATION_ENABLED) {
              // First close the modal, then trigger celebration
              onSuccess(txId, canisterId);
              handleClose();
              
              // Small delay to ensure modal is closed before showing celebration
              setTimeout(() => {
                onCelebration(amount, selectedToken?.symbol || selectedTokenSymbol);
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
          } else {
            const backendErrorMsg = backendResult && 'Err' in backendResult 
              ? typeof backendResult.Err === 'object' 
                ? Object.keys(backendResult.Err)[0]
                : String(backendResult.Err)
              : "Unknown backend error";
            throw new Error(`Backend top-up failed: ${backendErrorMsg}`);
          }
        } catch (backendError) {
          console.error("Backend top-up error:", backendError);
          // Even though the backend call failed, the tokens were transferred
          // Show a warning but still consider it partially successful
          errorMessage = `Token transfer succeeded but backend processing failed: ${backendError.message}. Please contact support.`;
          // Still call onSuccess to allow the user to see the transaction
          onSuccess(txId, canisterId);
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
  title="Top up mAIner with Crypto"
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
      <!-- Token Selector -->
      <div class="flex flex-col gap-2">
        <label class="block text-xs text-gray-600 mb-1 dark:text-gray-400">Select Payment Token</label>
        <div class="flex gap-2">
          {#each availableTokens as token}
                         <button
               type="button"
               class="flex-1 flex items-center gap-2 p-3 rounded-lg border transition-colors {selectedToken?.symbol === token.symbol ? 'bg-purple-50 border-purple-300 text-purple-700 dark:bg-purple-900 dark:bg-opacity-20 dark:border-purple-600 dark:border-opacity-30 dark:text-purple-300' : 'bg-gray-50 border-gray-300 text-gray-700 dark:bg-gray-800 dark:bg-opacity-50 dark:border-gray-600 dark:border-opacity-30 dark:text-gray-300'}"
               on:click={() => handleTokenChange(token.symbol)}
             >
              <div class="w-8 h-8 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-700 dark:border-gray-600">
                <TokenImages tokens={[token]} size={30} showSymbolFallback={true} />
              </div>
              <div class="flex flex-col min-w-0 flex-1 text-left">
                <div class="font-medium text-sm truncate">{token.symbol}</div>
                <div class="text-xs opacity-70 truncate">{token.name}</div>
              </div>
              {#if selectedToken?.symbol === token.symbol}
                <Check size={16} class="text-purple-600 dark:text-purple-400 flex-shrink-0" />
              {/if}
            </button>
          {/each}
        </div>
      </div>

      <!-- Selected Token Info Banner -->
      {#if selectedToken}
        <div class="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg bg-gray-100 border border-gray-300 text-gray-900 dark:bg-gray-700/20 dark:border-gray-600/30 dark:text-gray-100">
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-800 dark:border-gray-700">
            <div class="sm:hidden">
              <TokenImages tokens={[selectedToken]} size={32} showSymbolFallback={true} />
            </div>
            <div class="hidden sm:block">
              <TokenImages tokens={[selectedToken]} size={38} showSymbolFallback={true} />
            </div>
          </div>
          <div class="flex flex-col min-w-0 flex-1">
            <div class="text-gray-900 font-medium dark:text-gray-100 text-sm sm:text-base truncate">{selectedToken.name}</div>
            <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 truncate">Balance: {formatBalance(balance.toString(), selectedToken.decimals)} {selectedToken.symbol}</div>
          </div>
        </div>
      {/if}

      <!-- Top-up Info -->
      <div class="flex flex-col gap-2 sm:gap-3">
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
            <label for="amount-input" class="block text-xs text-gray-600 dark:text-gray-400">{selectedToken?.symbol || 'Token'} Amount</label>
            <button
              type="button"
              class="text-xs text-purple-600 hover:text-purple-800 dark:text-purple-500 dark:hover:text-purple-400 font-medium"
              on:click={() => amount = String(currentMaxAmount)}
            >
              Top up Max ({currentMaxAmount} {selectedToken?.symbol || 'Token'})
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
              placeholder="Enter {selectedToken?.symbol || 'token'} amount to top up"
              bind:value={amount}
              on:input={handleAmountInput}
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-600 dark:text-gray-400">{selectedToken?.symbol || 'Token'}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Protocol fees included
          </div>
          {#if isBelowMinimum}
            <div class="mt-1 text-xs text-yellow-600 dark:text-yellow-400">
              Minimum amount: {currentMinAmount} {selectedToken?.symbol || 'Token'}
            </div>
          {/if}
          {#if isAboveMaximum}
            <div class="mt-1 text-xs text-red-600 dark:text-red-400">
              Maximum amount: {currentMaxAmount} {selectedToken?.symbol || 'Token'}
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
              <span class="truncate">{amount || '0'} {selectedToken?.symbol || 'Token'}</span>
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

        <!-- FUNNAI unavailable message -->
        {#if isFunnaiUnavailable}
          <div class="mt-1 p-2 rounded bg-yellow-50 border border-yellow-200 text-yellow-700 text-xs sm:text-sm dark:bg-yellow-900/30 dark:border-yellow-900/50 dark:text-yellow-400">
            FUNNAI top-ups are currently not available. Please try again later or use ICP.
          </div>
        {/if}

        <!-- Send Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="mt-2 py-2 sm:py-2.5 px-3 sm:px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors text-sm sm:text-base"
          class:bg-purple-600={canSubmit}
          class:hover:bg-purple-500={canSubmit}
          class:bg-gray-400={!canSubmit}
          class:cursor-not-allowed={!canSubmit}
          class:dark:bg-gray-700={!canSubmit}
          disabled={!canSubmit}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing...
          {:else}
            <ArrowUp size={14} class="sm:hidden" />
            <ArrowUp size={16} class="hidden sm:block" />
            Top up {amount || '0'} {selectedToken?.symbol || 'Token'}
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