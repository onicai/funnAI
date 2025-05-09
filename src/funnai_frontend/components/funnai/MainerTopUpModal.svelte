<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";
  import { ArrowUp, Info } from 'lucide-svelte';
  import { store } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens } from "../../helpers/token_helpers";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId?: string) => void = () => {};
  export let canisterId: string = "";
  export let canisterName: string = "";
  
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
        fee_fixed: "10000", // standard ICP fee
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
  
  $: isValidAmount = amount && !isNaN(Number(amount)) && Number(amount) > 0;
  $: amountBigInt = isValidAmount && token
    ? BigInt(new BigNumber(amount).times(new BigNumber(10).pow(token.decimals)).toString())
    : BigInt(0);
  $: hasEnoughBalance = isValidAmount && balance >= (amountBigInt + tokenFee);
  $: if (token) {
    tokenFee = BigInt(token.fee_fixed);
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
      
      // Type for window.ic
      interface IcWindow extends Window {
        ic?: {
          agent?: any;
          createActor?: any;
        }
      }
      
      // Only run this if we have IC APIs available
      if ((window as IcWindow).ic && (window as IcWindow).ic.agent) {
        // Create CMC actor
        const cmcActor = await (window as IcWindow).ic.createActor({
          canisterId: cmcCanisterId,
          interfaceFactory: ({ IDL }) => {
            const IcpXdrConversionRate = IDL.Record({
              'timestamp_seconds': IDL.Nat64,
              'xdr_permyriad_per_icp': IDL.Nat64,
            });
            const IcpXdrConversionRateResponse = IDL.Record({
              'data': IcpXdrConversionRate,
              'hash_tree': IDL.Vec(IDL.Nat8),
              'certificate': IDL.Vec(IDL.Nat8),
            });
            return IDL.Service({
              'get_icp_xdr_conversion_rate': IDL.Func(
                [],
                [IcpXdrConversionRateResponse],
                ['query'],
              ),
            });
          },
        });

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
            
          console.log("Conversion rate loaded:", conversionRate.toString());
        } else {
          throw new Error("Failed to get conversion rate data");
        }
      } else {
        // Fallback if IC APIs aren't available
        throw new Error("Internet Computer APIs not available");
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
      
      // Convert to trillions for display
      const ONE_TRILLION = new BigNumber("1000000000000");
      const trillionCycles = cycles.div(ONE_TRILLION);
      
      // Format with 4 decimal places
      cyclesAmount = trillionCycles.toFixed(4);
      
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
      
      // Transfer ICP to the Cycles Minting Canister for top-up
      // This is a simplified approach - in production, you would:
      // 1. Transfer to the CMC with correct memo
      // 2. Call notify_top_up on the CMC
      
      // For now, we'll just transfer to the canister directly as placeholder
      const result = await IcrcService.transfer(
        token,
        canisterId, // Send directly to the canister (note: this is placeholder)
        amountBigInt,
        {
          fee: tokenFee
        }
      );

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        onSuccess(txId);
        handleClose();
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
  width="480px"
  variant="transparent"
  height="auto"
  className="mainer-topup-modal"
  closeOnEscape={true}
  closeOnClickOutside={true}
>
  <div class="p-4 flex flex-col gap-4">
    {#if isTokenLoading}
      <div class="flex justify-center py-4">
        <span class="w-6 h-6 border-2 border-gray-400/30 border-t-gray-400 rounded-full animate-spin"></span>
      </div>
    {:else}
      <!-- Token Info Banner -->
      <div class="flex items-center gap-3 p-3 rounded-lg bg-gray-700/20 border border-gray-600/30 text-gray-100">
        <div class="w-10 h-10 rounded-full bg-gray-800 p-1 border border-gray-700 flex-shrink-0">
          <TokenImages tokens={[token]} size={32} showSymbolFallback={true} />
        </div>
        <div class="flex flex-col">
          <div class="text-gray-100 font-medium">{token.name}</div>
          <div class="text-sm text-gray-400">Balance: {formatBalance(balance.toString(), token.decimals)} {token.symbol}</div>
        </div>
      </div>

      <!-- Top-up Info -->
      <div class="flex flex-col gap-3">
        <!-- Canister ID -->
        <div>
          <label class="block text-xs text-gray-400 mb-1.5">mAIner canister</label>
          <div class="relative">
            <input
              type="text"
              class="w-full py-2 px-3 bg-gray-800 border border-gray-600 rounded-md text-sm text-gray-100"
              value={canisterName ? `${canisterName} (${canisterId})` : canisterId}
              disabled
            />
          </div>
          <div class="mt-1 text-xs text-gray-500">mAIner's controller canister ID</div>
        </div>

        <!-- Amount -->
        <div>
          <label class="block text-xs text-gray-400 mb-1.5">ICP Amount</label>
          <div class="relative">
            <input
              type="text"
              inputmode="decimal"
              class="w-full py-2 px-3 bg-gray-800 border rounded-md text-sm text-gray-100"
              class:border-green-400={hasEnoughBalance && isValidAmount}
              class:border-red-400={!hasEnoughBalance && isValidAmount}
              class:border-gray-600={!isValidAmount}
              placeholder="Enter ICP amount to top up"
              bind:value={amount}
              on:input={handleAmountInput}
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-3 text-sm text-gray-400">{token.symbol}</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-400">
            Fee: {formatBalance(tokenFee.toString(), token.decimals)} {token.symbol}
          </div>
        </div>
        
        <!-- Cycles Conversion Display -->
        <div class="p-3 rounded-lg bg-blue-900/20 border border-blue-800/30 text-blue-200 text-sm flex flex-col gap-2">
          <div class="flex items-center gap-1">
            <Info size={14} />
            <span class="font-medium">Cycles Conversion</span>
            {#if isLoadingConversionRate}
              <span class="w-3 h-3 ml-2 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin"></span>
            {/if}
          </div>
          
          {#if !isLoadingConversionRate}
            <div class="flex justify-between">
              <span>{amount || '0'} ICP</span>
              <span class="font-medium">≈ {cyclesAmount} Trillion Cycles</span>
            </div>
          {:else}
            <div class="text-blue-300/70">Loading conversion rate...</div>
          {/if}
        </div>

        <!-- Error message -->
        {#if errorMessage}
          <div class="mt-1 p-2 rounded bg-red-900/30 border border-red-900/50 text-red-400 text-sm">
            {errorMessage}
          </div>
        {/if}

        <!-- Send Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="mt-2 py-2.5 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors"
          class:bg-purple-600={hasEnoughBalance && !isValidating}
          class:hover:bg-purple-500={hasEnoughBalance && !isValidating}
          class:bg-gray-700={!hasEnoughBalance || isValidating}
          class:cursor-not-allowed={!hasEnoughBalance || isValidating}
          disabled={!hasEnoughBalance || isValidating}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing...
          {:else}
            <ArrowUp size={16} />
            Top up {amount || '0'} {token.symbol}
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.mainer-topup-modal) {
    max-width: 480px;
    position: relative;
    z-index: 100000;
  }
</style> 