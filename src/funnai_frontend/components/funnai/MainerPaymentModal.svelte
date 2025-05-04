<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";
  import { ArrowUp, Check } from 'lucide-svelte';
  import { store } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId?: string) => void = () => {};
  export let modelType: 'Own' | 'Shared' = 'Own';
  
  // Fixed config for mAIner creation 
  // TODO: load funnai_address dynamically for Protocol
  const funnai_address = "kwrfk-ypzrt-wwywz-qov7y-36lis-6rkyv-zdpsp-jgees-uwhhi-7c3eg-gae";
  // TODO: load token info from token_helpers.ts
  const token: any = {
    name: "Internet Computer",
    symbol: "ICP",
    decimals: 8,
    fee_fixed: "10000", // standard ICP fee
    canister_id: "ryjl3-tyaaa-aaaaa-aaaba-cai" // ICP Ledger canister ID
  };
  
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let tokenFee: bigint = BigInt(10000); // Default 0.0001 ICP fee
  let balance: bigint = BigInt(0);
  
  // Determine payment amount based on model type
  $: paymentAmount = modelType === 'Own' ? '0.005' : '0.003';
  $: amountBigInt = BigInt(new BigNumber(paymentAmount).times(new BigNumber(10).pow(token.decimals)).toString());
  $: hasEnoughBalance = balance >= (amountBigInt + tokenFee);
  
  async function loadBalance() {
    try {
      if (!$store.principal) return;
      
      balance = await IcrcService.getIcrc1Balance(
        token,
        $store.principal
      ) as bigint;
    } catch (error) {
      console.error("Error loading balance:", error);
    }
  }

  async function handleSubmit() {
    if (isValidating) return;
    isValidating = true;
    errorMessage = "";

    try {
      if (!$store.principal) {
        throw new Error("Authentication not initialized");
      }
      
      if (!hasEnoughBalance) {
        throw new Error("Insufficient balance for transfer + fee");
      }

      const result = await IcrcService.transfer(
        token,
        funnai_address,
        amountBigInt,
        {
          fee: tokenFee
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

  onMount(() => {
    loadBalance();
  });
</script>

<Modal
  {isOpen}
  onClose={onClose}
  title="mAIner Creation Payment"
  width="480px"
  variant="transparent"
  height="auto"
  className="mainer-payment-modal"
>
  <div class="p-4 flex flex-col gap-4">
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

    <!-- Payment Info -->
    <div class="flex flex-col gap-3">
      <!-- Recipient Address -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">Recipient</label>
        <div class="relative">
          <input
            type="text"
            class="w-full py-2 px-3 bg-gray-800 border border-gray-600 rounded-md text-sm text-gray-100"
            value={funnai_address}
            disabled
          />
          <div class="absolute inset-y-0 right-0 flex items-center">
            <div class="p-1.5 text-green-500">
              <Check size={16} />
            </div>
          </div>
        </div>
        <div class="mt-1 text-xs text-green-500">FunnAI mAIner Creation Address</div>
      </div>

      <!-- Amount -->
      <div>
        <label class="block text-xs text-gray-400 mb-1.5">Payment Amount</label>
        <div class="relative">
          <input
            type="text"
            class="w-full py-2 px-3 bg-gray-800 border border-gray-600 rounded-md text-sm text-gray-100"
            value={paymentAmount}
            disabled
          />
          <div class="absolute inset-y-0 right-0 flex items-center">
            <span class="pr-3 text-sm text-gray-400">{token.symbol}</span>
          </div>
        </div>
        <div class="mt-1 text-xs text-gray-400">
          Fee: {formatBalance(tokenFee.toString(), token.decimals)} {token.symbol}
        </div>
      </div>
      
      <!-- Payment Description -->
      <div class="p-3 rounded-lg bg-blue-900/20 border border-blue-800/30 text-blue-200 text-sm">
        This payment is used to create your {modelType} mAIner model. Once payment is complete, your mAIner will be created automatically.
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
          Pay {paymentAmount} {token.symbol}
        {/if}
      </button>
    </div>
  </div>
</Modal>

<style>
  :global(.mainer-payment-modal) {
    max-width: 480px;
    position: relative;
    z-index: 100000;
  }
</style> 