<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";

  import { ArrowUp, Info, Check } from 'lucide-svelte';
  import { MEMO_PAYMENT_PROTOCOL, store, canisterIDLs } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance, formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, protocolConfig } from "../../helpers/token_helpers";
  import { createAnonymousActorHelper } from "../../helpers/utils/actorUtils";
  import { MIN_AMOUNT, MAX_AMOUNT, CELEBRATION_DURATION, CELEBRATION_ENABLED } from "../../helpers/config/topUpConfig";
  import { getIsProtocolActive } from "../../helpers/gameState";
  import { mainerHealthService } from "../../helpers/mainerHealthService";
  import ICPSwapService, { SwapArgs, DepositAndSwapArgs } from "../../helpers/icpswapService";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId: string, canisterId: string, backendPromise: Promise<any>) => void = () => {};
  export let onCelebration: (amount: string, token: string) => void = () => {};
  export let canisterId: string = "";
  export let canisterName: string = "";
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;

  console.log("in MainerTopUpModal protocolAddress ", protocolAddress);
  
  // Token configurations - now supporting ICP, FUNNAI, BOB, and ckBTC
  let availableTokens: any[] = [];
  let selectedTokenSymbol: 'ICP' | 'FUNNAI' | 'BOB' | 'ckBTC' = 'ICP';
  let isTokenLoading: boolean = true;
  
  // Get currently selected token
  $: selectedToken = availableTokens.find(t => t.symbol === selectedTokenSymbol);
  let icpToken;
  
  // Load token data from token_helpers
  async function loadTokenData() {
    isTokenLoading = true;
    try {
      const result = await fetchTokens({});
      icpToken = result.tokens.find(t => t.symbol === "ICP");
      const funnaiToken = result.tokens.find(t => t.symbol === "FUNNAI");
      const bobToken = result.tokens.find(t => t.symbol === "BOB");
      const ckbtcToken = result.tokens.find(t => t.symbol === "ckBTC");
      
      if (icpToken && funnaiToken && bobToken && ckbtcToken) {
        availableTokens = [icpToken, funnaiToken, bobToken, ckbtcToken];
      } else {
        throw new Error("Required tokens not found in token_helpers");
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
        },
        {
          name: "BOB",
          symbol: "BOB",
          decimals: 8,
          fee_fixed: "1000000",
          canister_id: "7pail-xaaaa-aaaas-aabmq-cai"
        },
        {
          name: "ckBTC",
          symbol: "ckBTC",
          decimals: 8,
          fee_fixed: "10",
          canister_id: "mxzaz-hqaaa-aaaar-qaada-cai"
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
  
  // FUNNAI limits - loaded dynamically from backend
  let funnaiMaxAmount: number = 0;
  let isLoadingFunnaiLimits: boolean = false;
  
  // FUNNAI constants
  const FUNNAI_MIN_CYCLES = new BigNumber("1000000000000"); // 1T cycles (hardcoded)
  
  // Helper function to round amounts sensibly based on magnitude
  function roundToSensibleDecimals(amount: BigNumber): number {
    const absAmount = amount.abs();
    
    // For amounts >= 1000: round to whole numbers
    if (absAmount.gte(1000)) {
      return Number(amount.toFixed(0));
    }
    // For amounts >= 10: round to 2 decimals
    if (absAmount.gte(10)) {
      return Number(amount.toFixed(2));
    }
    // For amounts >= 1: round to 4 decimals
    if (absAmount.gte(1)) {
      return Number(amount.toFixed(4));
    }
    // For amounts >= 0.01: round to 6 decimals
    if (absAmount.gte(0.01)) {
      return Number(amount.toFixed(6));
    }
    // For very small amounts: keep 8 decimals
    return Number(amount.toFixed(8));
  }

  // Dynamic limits based on token type and conversion rate
  $: dynamicLimits = (() => {
    if (selectedTokenSymbol === 'FUNNAI' && conversionRate && !conversionRate.isZero()) {
      // FUNNAI limits: backend max, hardcoded min (1T cycles)
      const E8S_PER_FUNNAI = new BigNumber("100000000000"); // 10^8 units per FUNNAI
      
      // Calculate FUNNAI amount for minimum (1T cycles)
      const minFunnaiAmount = FUNNAI_MIN_CYCLES.div(conversionRate);
      
      return {
        min: Number(minFunnaiAmount.toFixed(8)),
        max: funnaiMaxAmount || 0 // Use backend value or 0 if not loaded
      };
    } else if (selectedTokenSymbol === 'BOB') {
      // BOB has its own limits for easier testing (BOB is ~$0.20, ICP is ~$4.20, ratio ~21:1)
      return {
        min: 1,      // 1 BOB minimum for testing
        max: 4200    // Equivalent to 200 ICP (200 * 21 = 4200)
      };
    } else if (selectedTokenSymbol === 'ckBTC') {
      // ckBTC has its own limits (ckBTC is worth much more than ICP)
      // ckBTC is ~$60,000, ICP is ~$4.20, ratio ~1:14,285
      return {
        min: 0.00001,  // Very small minimum
        max: 0.014     // Equivalent to 200 ICP (200 / 14285 ≈ 0.014)
      };
    } else if (conversionRate && !conversionRate.isZero()) {
      // For ICP: use config limits directly
      return {
        min: MIN_AMOUNT,
        max: MAX_AMOUNT
      };
    } else {
      // Default to ICP limits from config if no conversion rate
      return {
        min: MIN_AMOUNT,
        max: MAX_AMOUNT
      };
    }
  })();

  $: currentMinAmount = dynamicLimits.min;
  $: currentMaxAmount = dynamicLimits.max;

  
  $: isValidAmount = amount && !isNaN(Number(amount)) && Number(amount) >= currentMinAmount && (currentMaxAmount === 0 || Number(amount) <= currentMaxAmount);
  $: isBelowMinimum = amount && !isNaN(Number(amount)) && Number(amount) > 0 && Number(amount) < currentMinAmount;
  $: isMaxAmount = amount && !isNaN(Number(amount)) && currentMaxAmount > 0 && Number(amount) === currentMaxAmount;
  $: isAboveMaximum = amount && !isNaN(Number(amount)) && currentMaxAmount > 0 && Number(amount) > currentMaxAmount;
  $: amountBigInt = isValidAmount && selectedToken
    ? BigInt(new BigNumber(amount).times(new BigNumber(10).pow(selectedToken.decimals)).toString())
    : BigInt(0);
  $: hasEnoughBalance = isValidAmount && balance >= (amountBigInt + tokenFee);
  $: isFunnaiUnavailable = selectedTokenSymbol === 'FUNNAI' && (!conversionRate || conversionRate.isZero() || currentMaxAmount === 0);
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
  
  // Load FUNNAI limits when FUNNAI is selected and conversion rate is available
  $: if (selectedTokenSymbol === 'FUNNAI' && conversionRate && !conversionRate.isZero()) {
    loadFunnaiLimits();
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

  // Function to load FUNNAI limits from backend
  async function loadFunnaiLimits() {
    isLoadingFunnaiLimits = true;
    
    try {
      if (!$store.gameStateCanisterActor) {
        throw new Error("Game state canister not available");
      }
      
      const maxAmountResult = await $store.gameStateCanisterActor.getMaxFunnaiTopupCyclesAmount();
      
      if (maxAmountResult && 'Ok' in maxAmountResult) {
        const maxCycles = new BigNumber(maxAmountResult.Ok.toString());
        
        // Convert max cycles to FUNNAI amount using conversion rate
        if (conversionRate && !conversionRate.isZero()) {
          funnaiMaxAmount = Number(maxCycles.div(conversionRate).toFixed(8));
          console.log("FUNNAI max amount loaded from backend:", funnaiMaxAmount, "FUNNAI");
        }
      } else {
        const errorMsg = maxAmountResult && 'Err' in maxAmountResult 
          ? (typeof maxAmountResult.Err === 'object' 
              ? Object.keys(maxAmountResult.Err)[0] 
              : String(maxAmountResult.Err))
          : "Failed to get FUNNAI max amount";
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error("Error loading FUNNAI limits:", error);
      funnaiMaxAmount = 0; // Set to 0 on error to disable max amount
    } finally {
      isLoadingFunnaiLimits = false;
    }
  }

  // Function to get conversion rate (ICP/BOB/ckBTC from CMC, FUNNAI from game state canister)
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
        // ICP, BOB, and ckBTC conversion rate from CMC
        const cmcCanisterId = "rkp4c-7iaaa-aaaaa-aaaca-cai";
        
        try {
          // Create the CMC actor using the imported IDL factory
          const cmcActor = await createAnonymousActorHelper(cmcCanisterId, canisterIDLs.cmc);
          
          // Get conversion rate from CMC
          const response = await cmcActor.get_icp_xdr_conversion_rate();
          
          if (response && response.data) {
            const xdrRate = Number(response.data.xdr_permyriad_per_icp);
            
            // 1 XDR = 1 trillion cycles, and the rate is in 10,000ths (permyriad)
            const CYCLES_PER_XDR = new BigNumber("1000000000000"); // 1 trillion cycles
            
            // Calculate base ICP rate: (xdr_permyriad_per_icp * CYCLES_PER_XDR) / 10000
            const icpConversionRate = new BigNumber(xdrRate)
              .times(CYCLES_PER_XDR)
              .div(10000);
            
            // For BOB and ckBTC, adjust the conversion rate based on a quote from the swap pool (against ICP)
            if (selectedTokenSymbol === 'BOB') {
              const numberOfTokensForQuote = 1000000000; // 8 decimals, i.e. 10 BOB
              const args : SwapArgs = {
                amountIn: numberOfTokensForQuote.toString(),
                zeroForOne: true,
                amountOutMinimum: "0"
              };
              const quoteResult = await ICPSwapService.getQuoteFromPool(selectedToken.pools[0], args);
              conversionRate = icpConversionRate.times(quoteResult).div(numberOfTokensForQuote);
              console.log("BOB conversion rate:", conversionRate.toString(), "cycles per BOB");
            } else if (selectedTokenSymbol === 'ckBTC') {
              const numberOfTokensForQuote = 10000; // 8 decimals, i.e. 0.0001;
              const args : SwapArgs = {
                amountIn: numberOfTokensForQuote.toString(),
                zeroForOne: true,
                amountOutMinimum: "0"
              };
              const quoteResult = await ICPSwapService.getQuoteFromPool(selectedToken.pools[0], args);
              conversionRate = icpConversionRate.times(quoteResult).div(numberOfTokensForQuote);
              console.log("ckBTC conversion rate:", conversionRate.toString(), "cycles per ckBTC");
            } else {
              // ICP
              conversionRate = icpConversionRate;
              console.log("ICP conversion rate loaded:", conversionRate.toString(), "cycles per ICP");
            }
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
      } else if (selectedTokenSymbol === 'BOB') {
        errorMessage = "Using estimated conversion rate";
        // BOB is ~1/21 of ICP value, so ~476B cycles per BOB (10T / 21)
        conversionRate = new BigNumber("476190476190"); // ~476B cycles per BOB (fallback)
      } else if (selectedTokenSymbol === 'ckBTC') {
        errorMessage = "Using estimated conversion rate";
        // ckBTC is ~14,285x ICP value, so ~142,850T cycles per ckBTC (10T * 14,285)
        conversionRate = new BigNumber("142850000000000000"); // ~142,850T cycles per ckBTC (fallback)
      } else {
        errorMessage = "Using estimated conversion rate";
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
  function handleTokenChange(tokenSymbol: 'ICP' | 'FUNNAI' | 'BOB' | 'ckBTC') {
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

      // Check mAIner health before proceeding (defensive: fail if health check errors)
      const mainerActor = $store.userMainerCanisterActors.find(a => a.id === canisterId)?.actor;
      if (mainerActor) {
        try {
          const healthStatus = await mainerHealthService.checkMainerHealth(canisterId, mainerActor);
          if (!healthStatus.isHealthy) {
            throw new Error(healthStatus.maintenanceMessage || "mAIner is currently unavailable for top-up");
          }
        } catch (error) {
          // If health check fails, treat as unhealthy and prevent top-up
          const errorMsg = error instanceof Error ? error.message : "Failed to verify mAIner health";
          throw new Error(errorMsg);
        }
      }

      // Additional FUNNAI-specific security checks
      if (selectedTokenSymbol === 'FUNNAI') {
        if (!conversionRate || conversionRate.isZero()) {
          throw new Error("FUNNAI top-ups are currently not available");
        }
        
        // Security check: Prevent FUNNAI top-ups if max amount is 0 (backend disabled)
        if (currentMaxAmount === 0) {
          throw new Error("FUNNAI top-ups are currently disabled by the backend");
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
      };

      let result;
      if (selectedTokenSymbol !== 'FUNNAI' && selectedTokenSymbol !== 'ICP') {
        // Swap any other tokens than FUNNAI to ICP first, then proceed with ICP flow
        const args : DepositAndSwapArgs = {
          tokenInFee: tokenFee,
          amountIn: amount,
          zeroForOne: true,
          amountOutMinimum: "0",
          tokenOutFee: icpToken.fee_fixed
        };
        const swapResult = await ICPSwapService.approveAndSwap(selectedToken, selectedToken.pools[0], args, selectedToken.pools[0]);
        if (swapResult && typeof swapResult === 'object' && 'ok' in swapResult) {
          // The user now has the corresponding ICP in their wallet
          // Transfer the ICP to the Protocol's account for top-up
          const icpToTransfer = BigInt(swapResult.ok - icpToken.fee_fixed);
          result = await IcrcService.transfer(
            icpToken,
            protocolAddress,  // Use protocol address from token_helpers
            icpToTransfer,
            {
              fee: icpToken.fee_fixed,
              // Include the memo for transactions to the Protocol
              memo: MEMO_PAYMENT_PROTOCOL
            }
          );
        } else {
          console.error("Swap error:", swapResult);
          throw new Error("Swap error");
        };
      } else {
        // Transfer tokens to the Protocol's account for top-up
        // The backend will handle the actual cycles minting and top-up process
        result = await IcrcService.transfer(
          selectedToken,
          protocolAddress,  // Use protocol address from token_helpers
          amountBigInt,
          {
            fee: tokenFee,
            // Include the memo for transactions to the Protocol
            memo: MEMO_PAYMENT_PROTOCOL
          }
        );
      };

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        console.log("handleSubmit txId: ", txId);
        
        // Create the backend promise but don't await it here
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

        // Create the backend promise based on token type
        let backendPromise: Promise<any>;
        if (selectedTokenSymbol === 'FUNNAI') {
          // For FUNNAI, use the FUNNAI-specific endpoint
          if (!$store.gameStateCanisterActor) {
            throw new Error("Game state canister not available");
          };
          backendPromise = $store.gameStateCanisterActor.topUpCyclesForMainerAgentWithFunnai(topUpInput);
        } else {
          // For ICP, BOB, and ckBTC, use the standard ICP endpoint
          if (!$store.gameStateCanisterActor) {
            throw new Error("Game state canister not available");
          };
          backendPromise = $store.gameStateCanisterActor.topUpCyclesForMainerAgent(topUpInput);
        }

        // Handle celebration for max amounts (only for ICP/BOB/ckBTC, not FUNNAI)
        const shouldCelebrate = isMaxAmount && CELEBRATION_ENABLED && selectedTokenSymbol !== 'FUNNAI';
        
        // Close modal immediately and pass promise to parent
        onSuccess(txId, canisterId, backendPromise);
        handleClose();
        
        // Trigger celebration if needed (after modal closes) - only for ICP
        if (shouldCelebrate) {
          setTimeout(() => {
            onCelebration(amount, selectedToken?.symbol || selectedTokenSymbol);
          }, 300);
          
          // Handle max top-up storage in background - only for ICP/BOB/ckBTC
          try {
            let maxTopUpInput = {
              paymentTransactionBlockId: BigInt(txId),
              toppedUpMainerId: canisterId,
              amount: BigInt(amount),
            };
            $store.backendActor.addMaxMainerTopup(maxTopUpInput).catch(maxTopUpStorageError => {
              console.error("Top-up storage error: ", maxTopUpStorageError);            
            });
          } catch (error) {
            console.error("Error setting up max top-up storage: ", error);
          }
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
        <div class="block text-xs text-gray-600 mb-1 dark:text-gray-400">Select Payment Token</div>
        <div class="grid grid-cols-2 gap-2">
          {#each availableTokens as token}
            <button
               type="button"
               class="flex items-center gap-2 p-2.5 rounded-lg border transition-colors {selectedToken?.symbol === token.symbol ? 'bg-purple-50 border-purple-300 text-purple-700 dark:bg-purple-900 dark:bg-opacity-20 dark:border-purple-600 dark:border-opacity-30 dark:text-purple-300' : 'bg-gray-50 border-gray-300 text-gray-700 dark:bg-gray-800 dark:bg-opacity-50 dark:border-gray-600 dark:border-opacity-30 dark:text-gray-300'}"
               on:click={() => handleTokenChange(token.symbol)}
             >
              <div class="w-7 h-7 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-700 dark:border-gray-600">
                <TokenImages tokens={[token]} size={26} showSymbolFallback={true} />
              </div>
              <div class="flex flex-col min-w-0 flex-1 text-left">
                <div class="font-medium text-xs truncate">{token.symbol}</div>
                <div class="text-xs opacity-60 truncate">{token.name}</div>
              </div>
              {#if selectedToken?.symbol === token.symbol}
                <Check size={14} class="text-purple-600 dark:text-purple-400 flex-shrink-0" />
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
          <div class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">mAIner canister</div>
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
            {#if currentMaxAmount > 0}
              <button
                type="button"
                class="text-xs text-purple-600 hover:text-purple-800 dark:text-purple-500 dark:hover:text-purple-400 font-medium"
                on:click={() => amount = String(currentMaxAmount)}
              >
                Top up Max ({currentMaxAmount} {selectedToken?.symbol || 'Token'})
              </button>
            {:else if selectedTokenSymbol === 'FUNNAI' && isLoadingFunnaiLimits}
              <span class="text-xs text-gray-500">Loading max amount...</span>
            {/if}
          </div>
          <div class="relative">
            <input
              id="amount-input"
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
          {#if isMaxAmount && hasEnoughBalance && selectedTokenSymbol !== 'FUNNAI'}
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
            {#if selectedTokenSymbol === 'FUNNAI' && currentMaxAmount === 0}
              FUNNAI top-ups are currently disabled by the backend. Please try again later or use ICP.
            {:else}
              FUNNAI top-ups are currently not available. Please try again later or use ICP.
            {/if}
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