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
  import { getBonusCyclesTopupInPercent } from "../../helpers/gameState";
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
  let validatingMessage: string = "Processing...";
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

  // Top-up bonus percent for non-FUNNAI tokens (loaded from backend)
  let bonusCyclesTopupInPercent: number = 0;
  let isLoadingBonusPercent: boolean = false;
  
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
      // BOB has its own limits for easier testing
      return {
        min: 1,      // 1 BOB minimum
        max: 200     // 200 BOB maximum
      };
    } else if (selectedTokenSymbol === 'ckBTC') {
      // ckBTC has its own limits (ckBTC is worth much more than ICP)
      return {
        min: 0.00001,     // Very small minimum
        max: 0.0003456    // 0.0003456 ckBTC maximum
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
  $: showTopupBonus = selectedTokenSymbol !== 'FUNNAI' && bonusCyclesTopupInPercent > 0;
  $: bonusMultiplier = 1 + bonusCyclesTopupInPercent / 100;
  $: isFunnaiUnavailable = selectedTokenSymbol === 'FUNNAI' && (!conversionRate || conversionRate.isZero() || currentMaxAmount === 0);
  $: canSubmit = hasEnoughBalance && !isValidating && selectedToken && !isFunnaiUnavailable;
  $: if (selectedToken) {
    tokenFee = BigInt(selectedToken.fee_fixed);
  }
  
  // Reactive statement to automatically calculate cycles when amount, conversion rate, bonus, or token changes
  $: if (conversionRate && amount && selectedToken && bonusCyclesTopupInPercent >= 0) {
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
  
  async function loadBalance(loadIcp=false) {
    try {
      if (!$store.principal) return;
      if (loadIcp) {
        if (!icpToken) return;
        const icpBalance = await IcrcService.getIcrc1Balance(
          icpToken,
          $store.principal
        ) as bigint;
        return icpBalance;
      } else {
        if (!selectedToken) return;
        balance = await IcrcService.getIcrc1Balance(
          selectedToken,
          $store.principal
        ) as bigint;
      };
    } catch (error) {
      console.error("Error loading balance: ", error);
    }
  }

  // Function to load top-up bonus percent from backend
  async function loadBonusCyclesTopupPercent() {
    isLoadingBonusPercent = true;

    try {
      bonusCyclesTopupInPercent = await getBonusCyclesTopupInPercent();
      if (bonusCyclesTopupInPercent > 0) {
        console.log("Top-up bonus percent loaded from backend:", bonusCyclesTopupInPercent, "%");
      }
    } catch (error) {
      console.error("Error loading top-up bonus percent:", error);
      bonusCyclesTopupInPercent = 0;
    } finally {
      isLoadingBonusPercent = false;
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
              // Use the new method that automatically determines swap direction based on pool metadata
              const quoteResult = await ICPSwapService.getQuoteWithAutoDirection(
                selectedToken.pools[0],
                selectedToken.canister_id,
                numberOfTokensForQuote.toString()
              );
              
              if (quoteResult && typeof quoteResult === 'object' && 'ok' in quoteResult) {
                const icpAmount = new BigNumber(quoteResult.ok.toString());
                conversionRate = icpConversionRate.times(icpAmount).div(numberOfTokensForQuote);
                console.log("BOB conversion rate:", conversionRate.toString(), "cycles per BOB");
              } else {
                console.warn("Failed to get BOB quote, using fallback estimate");
                throw new Error("Quote failed for BOB");
              }
            } else if (selectedTokenSymbol === 'ckBTC') {
              const numberOfTokensForQuote = 10000; // 8 decimals, i.e. 0.0001;
              // Use the new method that automatically determines swap direction based on pool metadata
              const quoteResult = await ICPSwapService.getQuoteWithAutoDirection(
                selectedToken.pools[0],
                selectedToken.canister_id,
                numberOfTokensForQuote.toString()
              );
              
              if (quoteResult && typeof quoteResult === 'object' && 'ok' in quoteResult) {
                const icpAmount = new BigNumber(quoteResult.ok.toString());
                conversionRate = icpConversionRate.times(icpAmount).div(numberOfTokensForQuote);
                console.log("ckBTC conversion rate:", conversionRate.toString(), "cycles per ckBTC");
              } else {
                console.warn("Failed to get ckBTC quote, using fallback estimate");
                throw new Error("Quote failed for ckBTC");
              }
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
      let cycles = smallestUnitAmount.times(smallestUnitToCycleRatio);

      // Apply protocol top-up bonus for non-FUNNAI tokens
      if (selectedTokenSymbol !== 'FUNNAI' && bonusCyclesTopupInPercent > 0) {
        cycles = cycles.times(bonusMultiplier);
      }
      
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
      // Find the index of this canister in userMainerAgentCanistersInfo to get the corresponding actor
      const mainerIndex = $store.userMainerAgentCanistersInfo.findIndex(canister => 
        (canister.address === canisterId) || (canister.id === canisterId)
      );
      const mainerActor = mainerIndex !== -1 ? $store.userMainerCanisterActors[mainerIndex] : null;
      
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
          console.error("Error checking FUNNAI price: ", priceCheckError);
          throw new Error("Unable to verify FUNNAI conversion rate");
        };

        tokenFee = BigInt(0); // for burn transactions, set to 0
        // protocolAddress = "r5m5y-diaaa-aaaaa-qanaa-cai"; // hardcode address for FUNNAI token (as burn transactions need to go to prd game state canister)
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
        validatingMessage = `Swapping ${selectedToken.symbol} to ICP...`;
        console.log("Starting swap for token: ", selectedToken.symbol);
        console.log("User balance: ", balance.toString(), selectedToken.symbol);
        console.log("Amount to swap: ", amountBigInt.toString());
        console.log("Token fee: ", tokenFee.toString());
        console.log("Total needed: ", (amountBigInt + tokenFee).toString());
        console.log("Has enough? ", balance >= (amountBigInt + tokenFee));
        
        // Note: zeroForOne is now determined automatically by ICPSwapService based on pool metadata
        const args : DepositAndSwapArgs = {
          tokenInFee: tokenFee,
          amountIn: amountBigInt.toString(), // Convert amount to smallest unit (e8s)
          zeroForOne: true, // This will be overridden by ICPSwapService based on actual pool token order
          amountOutMinimum: "0",
          tokenOutFee: BigInt(icpToken.fee_fixed)
        };
        const swapResult = await ICPSwapService.approveAndSwap(selectedToken, selectedToken.pools[0], args, selectedToken.pools[0]);
        console.log("Swap result: ", swapResult);
        
        if (swapResult && typeof swapResult === 'object' && 'ok' in swapResult) {
          // The user now has the corresponding ICP in their wallet
          // Transfer the ICP to the Protocol's account for top-up
          validatingMessage = "Sending ICP to protocol...";
          
          // swapResult.ok is the withdrawal result (BigInt), subtract the ICP fee for the transfer
          const outputAmount = typeof swapResult.ok === 'bigint' ? swapResult.ok : BigInt(swapResult.ok);
          const icpFee = BigInt(icpToken.fee_fixed);
          const icpToTransfer = outputAmount - icpFee - icpFee;
          
          console.log("ICP received from swap: ", outputAmount.toString());
          await loadBalance();
          var icpBalance = await loadBalance(true);
          while (icpBalance < icpToTransfer) {
            console.log("Waiting on ICP Ledger: ", icpBalance);
            await new Promise(resolve => setTimeout(resolve, 2000)); // Wait as the ICP Ledger needs time to reflect the new ICP balance
            icpBalance = await loadBalance(true);
          };
          console.log("ICP Balance: ", icpBalance);
          
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
          // Better error logging
          const errorDetails = swapResult?.err 
            ? (typeof swapResult.err === 'object' 
                ? JSON.stringify(swapResult.err) 
                : swapResult.err)
            : 'Unknown error';
          console.error("Swap error details: ", errorDetails);
          throw new Error(`Swap failed: ${errorDetails}`);
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
        console.log("txId: ", txId);
        
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

        // Handle celebration for max amounts (only for ICP)
        const shouldCelebrate = isMaxAmount && CELEBRATION_ENABLED && selectedTokenSymbol === 'ICP';
        
        // Close modal immediately and pass promise to parent
        onSuccess(txId, canisterId, backendPromise);
        handleClose();
        
        // Trigger celebration if needed (after modal closes) - only for ICP
        if (shouldCelebrate) {
          setTimeout(() => {
            onCelebration(amount, selectedToken?.symbol || selectedTokenSymbol);
          }, 300);
          
          // Handle max top-up storage in background - only for ICP
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
        console.error("Transfer error details: ", result.Err);
      }
    } catch (err) {
      console.error("Top-up error: ", err);
      errorMessage = err.message || "Top-up failed";
    } finally {
      isValidating = false;
      validatingMessage = "Processing..."; // Reset message
    }
  }

  onMount(async () => {
    await loadTokenData();
    loadBalance();
    loadConversionRate();
    loadBonusCyclesTopupPercent();
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
  <div class="space-y-4">
    {#if isTokenLoading}
      <div class="flex justify-center py-4">
        <span class="w-6 h-6 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
      </div>
    {:else}
      <!-- Token Selector -->
      <div class="flex flex-col gap-2">
        <span class="block text-xs text-gray-400 mb-1">Select Payment Token</span>
        {#if bonusCyclesTopupInPercent > 0}
          <p class="text-[11px] text-emerald-400 -mt-1 mb-0.5">
            Non-FUNNAI tokens include +{bonusCyclesTopupInPercent}% bonus cycles
          </p>
        {/if}
        <div class="grid grid-cols-2 gap-2">
          {#each availableTokens as token}
            <button
               type="button"
               class="flex items-center gap-2 p-2.5 rounded-xl border transition-colors {selectedToken?.symbol === token.symbol ? 'border-agent-purple/50 bg-agent-purple/10 text-gray-100' : 'bg-white/[0.03] border-white/10 text-gray-300 hover:border-agent-purple/30'}"
               on:click={() => handleTokenChange(token.symbol)}
             >
              <div class="w-7 h-7 rounded-xl bg-white/[0.04] border border-white/10 flex-shrink-0 overflow-hidden">
                <TokenImages tokens={[token]} size={26} showSymbolFallback={true} />
              </div>
              <div class="flex flex-col min-w-0 flex-1 text-left">
                <div class="font-medium text-xs truncate text-white">{token.symbol}</div>
                <div class="text-xs text-gray-500 truncate">{token.name}</div>
              </div>
              {#if selectedToken?.symbol === token.symbol}
                <Check size={14} class="text-agent-purple flex-shrink-0" />
              {/if}
            </button>
          {/each}
        </div>
      </div>

      <!-- Selected Token Info Banner -->
      {#if selectedToken}
        <div class="flex items-center gap-2 sm:gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/10">
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex-shrink-0 overflow-hidden">
            <div class="sm:hidden">
              <TokenImages tokens={[selectedToken]} size={32} showSymbolFallback={true} />
            </div>
            <div class="hidden sm:block">
              <TokenImages tokens={[selectedToken]} size={38} showSymbolFallback={true} />
            </div>
          </div>
          <div class="flex flex-col min-w-0 flex-1">
            <div class="text-white font-medium text-sm sm:text-base truncate">{selectedToken.name}</div>
            <div class="text-xs sm:text-sm text-gray-400 truncate">Balance: {formatBalance(balance.toString(), selectedToken.decimals)} {selectedToken.symbol}</div>
          </div>
        </div>
      {/if}

      <!-- Top-up Info -->
      <div class="flex flex-col gap-3">
        <!-- Canister ID -->
        <div>
          <span class="block text-xs text-gray-400 mb-1.5">mAIner canister</span>
          <div class="relative">
            <input
              type="text"
              class="agent-input w-full text-xs sm:text-sm"
              value={canisterName ? `${canisterName} (${canisterId})` : canisterId}
              disabled
            />
          </div>
          <div class="mt-1 text-xs text-gray-500">mAIner to be topped up</div>
        </div>

        <!-- Amount -->
        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label for="amount-input" class="block text-xs text-gray-400">{selectedToken?.symbol || 'Token'} Amount</label>
            {#if currentMaxAmount > 0}
              <button
                type="button"
                class="text-xs text-agent-purple hover:text-agent-purple/80 font-medium"
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
              class="agent-input w-full pr-12 sm:pr-16 text-xs sm:text-sm {hasEnoughBalance && isValidAmount ? 'border-emerald-500/50' : ''} {(!hasEnoughBalance && isValidAmount) || isAboveMaximum ? 'border-red-500/50' : ''} {isBelowMinimum ? 'border-amber-500/50' : ''} {isMaxAmount && hasEnoughBalance ? 'border-agent-purple/50' : ''}"
              placeholder="Enter {selectedToken?.symbol || 'token'} amount to top up"
              bind:value={amount}
              on:input={handleAmountInput}
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-400">{selectedToken?.symbol || 'Token'}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-400">Protocol fees included</div>
          {#if isBelowMinimum}
            <div class="mt-1 text-xs text-amber-400">
              Minimum amount: {currentMinAmount} {selectedToken?.symbol || 'Token'}
            </div>
          {/if}
          {#if isAboveMaximum}
            <div class="mt-1 text-xs text-red-400">
              Maximum amount: {currentMaxAmount} {selectedToken?.symbol || 'Token'}
            </div>
          {/if}
          {#if isMaxAmount && hasEnoughBalance && selectedTokenSymbol !== 'FUNNAI'}
            <div class="mt-1 text-xs text-agent-purple font-medium">
              Maximum amount selected
            </div>
          {/if}
        </div>
        
        <!-- Cycles Conversion Display -->
        <div class="p-3 rounded-xl bg-sky-500/5 border border-sky-500/20 text-sky-300/90 text-xs sm:text-sm flex flex-col gap-2">
          <div class="flex items-center gap-1.5">
            <Info size={14} class="text-sky-400 flex-shrink-0" />
            <span class="font-medium text-sky-200">Cycles Conversion</span>
            {#if isLoadingConversionRate}
              <span class="w-3 h-3 ml-2 border-2 border-sky-400/30 border-t-sky-400 rounded-full animate-spin flex-shrink-0"></span>
            {/if}
          </div>
          
          {#if !isLoadingConversionRate}
            <div class="flex justify-between items-center gap-2">
              <span class="truncate text-sky-300/80">{amount || '0'} {selectedToken?.symbol || 'Token'}</span>
              <span class="font-medium text-right flex-shrink-0 text-white">≈ {cyclesAmount} Trillion Cycles</span>
            </div>
            {#if showTopupBonus}
              <div class="text-emerald-400 text-xs">
                Includes +{bonusCyclesTopupInPercent}% bonus cycles on {selectedToken?.symbol || 'token'} top-ups
              </div>
            {/if}
          {:else}
            <div class="text-sky-400/70">Loading conversion rate...</div>
          {/if}
        </div>

        <!-- Swap progress panel -->
        {#if isValidating && validatingMessage !== "Processing..."}
          <div class="p-3 rounded-xl bg-white/[0.03] border border-white/10">
            <div class="flex items-center gap-2">
              <span class="w-4 h-4 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
              <span class="text-sm font-medium text-gray-200">{validatingMessage}</span>
            </div>
          </div>
        {/if}

        <!-- Error message -->
        {#if errorMessage}
          <div class="p-3 bg-red-500/10 rounded-xl border border-red-500/25">
            <p class="text-sm text-red-300">{errorMessage}</p>
          </div>
        {/if}

        <!-- FUNNAI unavailable message -->
        {#if isFunnaiUnavailable}
          <div class="p-3 bg-amber-500/5 rounded-xl border border-amber-500/20">
            <p class="text-sm text-amber-300">
              {#if selectedTokenSymbol === 'FUNNAI' && currentMaxAmount === 0}
                FUNNAI top-ups are currently disabled by the backend. Please try again later or use ICP.
              {:else}
                FUNNAI top-ups are currently not available. Please try again later or use ICP.
              {/if}
            </p>
          </div>
        {/if}

        <!-- Send Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="w-full agent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed {!canSubmit ? 'bg-white/10 hover:bg-white/10 text-gray-500 shadow-none' : ''}"
          disabled={!canSubmit}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>Processing...</span>
          {:else}
            <ArrowUp size={16} />
            <span>Top up {amount || '0'} {selectedToken?.symbol || 'Token'}</span>
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.mainer-topup-modal) {
    max-width: min(480px, calc(100vw - 2rem));
  }

  :global(.modal-panel.mainer-topup-modal),
  :global(.mainer-topup-modal.modal-panel) {
    background: #15141B !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 1rem !important;
    color: #e5e7eb !important;
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
