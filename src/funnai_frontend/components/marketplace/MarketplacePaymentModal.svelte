<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import { ShoppingBag, Info, AlertCircle } from 'lucide-svelte';
  import { store } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId: bigint) => void = () => {};
  export let listing: any = null; // The marketplace listing being purchased
  
  // ICP Token configuration
  const ICP_LEDGER_CANISTER_ID = "ryjl3-tyaaa-aaaaa-aaaba-cai";
  const ICP_FEE = BigInt(10_000); // 0.0001 ICP
  const ICP_DECIMALS = 8;
  
  // ICP token object for IcrcService (type assertion since we only need subset of FE.Token)
  const ICP_TOKEN = {
    name: "Internet Computer",
    symbol: "ICP",
    decimals: 8,
    fee_fixed: "10000",
    canister_id: ICP_LEDGER_CANISTER_ID
  } as any;
  
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let balance: bigint = BigInt(0);
  let isLoadingBalance: boolean = true;
  
  // Reservation timer (2 minutes)
  const RESERVATION_TIMEOUT_MS = 120000; // 2 minutes
  let reservationStartTime: number = 0;
  let timeRemaining: number = 120; // seconds
  let timerInterval: NodeJS.Timeout | null = null;
  
  // Price from listing (in e8s)
  $: priceE8s = listing ? BigInt(listing.priceE8S) : BigInt(0);
  $: priceICP = Number(priceE8s) / 100_000_000;
  $: totalWithFee = priceE8s + ICP_FEE;
  $: totalICPWithFee = Number(totalWithFee) / 100_000_000;
  
  // Validation
  $: hasInsufficientBalance = balance < totalWithFee;
  $: canSubmit = !isValidating && !hasInsufficientBalance && balance > BigInt(0) && listing !== null;
  
  function startReservationTimer() {
    reservationStartTime = Date.now();
    timeRemaining = 120;
    
    // Clear any existing timer
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    
    // Update timer every second
    timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - reservationStartTime) / 1000);
      timeRemaining = Math.max(0, 120 - elapsed);
      
      if (timeRemaining === 0) {
        // Timer expired - close modal
        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
        }
        errorMessage = "Reservation expired. The mAIner will be returned to the marketplace.";
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    }, 1000);
  }
  
  function stopReservationTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }
  
  onMount(() => {
    if (isOpen && listing) {
      loadBalance();
      startReservationTimer();
    }
    
    return () => {
      stopReservationTimer();
    };
  });
  
  $: if (isOpen && listing) {
    loadBalance();
    errorMessage = "";
    startReservationTimer();
  } else if (!isOpen) {
    stopReservationTimer();
  }
  
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  async function loadBalance() {
    if (!$store.principal) {
      errorMessage = "Please connect your wallet first";
      isLoadingBalance = false;
      return;
    }
    
    isLoadingBalance = true;
    errorMessage = "";
    
    try {
      balance = await IcrcService.getIcrc1Balance(
        ICP_TOKEN,
        $store.principal
      ) as bigint;
      console.log("ICP Balance loaded:", balance.toString());
    } catch (error) {
      console.error("Error loading ICP balance:", error);
      errorMessage = "Failed to load ICP balance. Please try again.";
      balance = BigInt(0);
    } finally {
      isLoadingBalance = false;
    }
  }
  
  async function handlePayment() {
    if (!canSubmit || !listing) return;
    
    isValidating = true;
    errorMessage = "";
    
    try {
      console.log("Processing payment for mAIner:", listing.mainerId);
      console.log("Payment amount:", priceE8s.toString(), "e8s");
      console.log("Seller:", listing.seller);
      
      // Execute ICP transfer to seller using static method
      const result: any = await IcrcService.transfer(
        ICP_TOKEN,
        listing.seller, // Send to seller (Principal string)
        priceE8s,
        {
          fee: ICP_FEE
        }
      );
      
      if (result && 'Err' in result) {
        console.error("Transfer error:", result.Err);
        throw new Error(`Transfer failed: ${JSON.stringify(result.Err)}`);
      }
      
      const blockIndex = result.Ok as bigint;
      console.log("Payment successful! Block index:", blockIndex.toString());
      
      // Call success callback with transaction ID
      onSuccess(blockIndex);
      
      // Close modal
      onClose();
      
    } catch (error) {
      console.error("Error processing payment:", error);
      errorMessage = error.message || "Failed to process payment. Please try again.";
    } finally {
      isValidating = false;
    }
  }
  
  function handleClose() {
    if (!isValidating) {
      errorMessage = "";
      onClose();
    }
  }
  
  function formatICP(e8s: bigint): string {
    return (Number(e8s) / 100_000_000).toFixed(8);
  }
</script>

<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Purchase mAIner"
  className="marketplace-payment-modal"
>
  <div class="space-y-4">
    {#if !listing}
      <div class="text-center py-8">
        <AlertCircle class="w-12 h-12 text-gray-400 mx-auto mb-2" />
        <p class="text-gray-600 dark:text-gray-400">No listing selected</p>
      </div>
    {:else}
      <!-- Reservation Timer Banner -->
      <div class="flex items-center justify-between p-3 rounded-lg {timeRemaining <= 30 ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'}">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 {timeRemaining <= 30 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="text-sm font-medium {timeRemaining <= 30 ? 'text-red-900 dark:text-red-200' : 'text-blue-900 dark:text-blue-200'}">
              {timeRemaining <= 30 ? 'Reservation expires soon!' : 'mAIner reserved for you'}
            </p>
            <p class="text-xs {timeRemaining <= 30 ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'}">
              Complete payment within {formatTime(timeRemaining)}
            </p>
          </div>
        </div>
        <div class="text-right">
          <div class="text-2xl font-bold {timeRemaining <= 30 ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'}">
            {formatTime(timeRemaining)}
          </div>
        </div>
      </div>

      <!-- mAIner Info -->
      <div class="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <div class="flex items-start space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <ShoppingBag class="w-5 h-5 text-white" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-white truncate">🦜 {listing.mainerName}</h3>
            <!--
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Type: <span class="font-medium">{listing.mainerType}</span>
            </p>
            -->
            {#if listing.cycleBalance}
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Balance: <span class="font-medium">{formatLargeNumber(listing.cycleBalance / 1_000_000_000_000, 2, false)} TCYCLES</span>
              </p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Seller Info -->
      <div>
        <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1.5">Seller</label>
        <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
          <p class="text-xs font-mono text-gray-700 dark:text-gray-300 break-all">{listing.seller}</p>
        </div>
      </div>

      <!-- Balance Display -->
      <div>
        <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1.5">Your ICP Balance</label>
        <div class="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          {#if isLoadingBalance}
            <div class="flex items-center space-x-2">
              <div class="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-sm text-gray-600 dark:text-gray-400">Loading balance...</span>
            </div>
          {:else}
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600 dark:text-gray-400">Available:</span>
              <span class="text-lg font-semibold text-gray-900 dark:text-white">
                {formatICP(balance)} ICP
              </span>
            </div>
          {/if}
        </div>
      </div>

      <!-- Payment Breakdown -->
      <div class="space-y-2">
        <label class="block text-xs text-gray-600 dark:text-gray-400">Payment Details</label>
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 space-y-2 border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">mAIner Price:</span>
            <span class="font-semibold text-gray-900 dark:text-white">{priceICP.toFixed(8)} ICP</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Network Fee:</span>
            <span class="font-semibold text-gray-900 dark:text-white">{formatICP(ICP_FEE)} ICP</span>
          </div>
          <div class="border-t border-gray-200 dark:border-gray-700 pt-2 flex justify-between">
            <span class="font-semibold text-gray-900 dark:text-white">Total:</span>
            <span class="font-bold text-lg text-purple-600 dark:text-purple-400">{totalICPWithFee.toFixed(8)} ICP</span>
          </div>
        </div>
      </div>

      <!-- Info Box -->
      <div class="flex items-start space-x-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <Info class="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div class="text-xs text-blue-700 dark:text-blue-300">
          <p class="font-medium mb-1">Payment will be sent directly to the seller</p>
          <p>Once payment is confirmed, the mAIner ownership will be transferred to you automatically.</p>
        </div>
      </div>

      <!-- Error Message -->
      {#if errorMessage}
        <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <p class="text-sm text-red-700 dark:text-red-300">{errorMessage}</p>
        </div>
      {/if}

      <!-- Insufficient Balance Warning -->
      {#if hasInsufficientBalance && !isLoadingBalance}
        <div class="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
          <div class="flex items-start space-x-2">
            <AlertCircle class="w-4 h-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
            <div class="text-sm text-yellow-700 dark:text-yellow-300">
              <p class="font-medium">Insufficient Balance</p>
              <p class="mt-1">You need {totalICPWithFee.toFixed(8)} ICP but only have {formatICP(balance)} ICP</p>
            </div>
          </div>
        </div>
      {/if}

      <!-- Action Buttons -->
      <div class="flex space-x-3 pt-2">
        <button
          type="button"
          on:click={handleClose}
          class="flex-1 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={isValidating}
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={handlePayment}
          class="flex-1 px-4 py-2.5 rounded-lg text-white font-medium flex items-center justify-center space-x-2 transition-colors"
          class:bg-purple-600={canSubmit}
          class:hover:bg-purple-700={canSubmit}
          class:bg-gray-400={!canSubmit}
          class:dark:bg-gray-700={!canSubmit}
          class:cursor-not-allowed={!canSubmit}
          disabled={!canSubmit}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>Processing...</span>
          {:else}
            <ShoppingBag class="w-4 h-4" />
            <span>Pay {priceICP.toFixed(4)} ICP</span>
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.marketplace-payment-modal) {
    max-width: min(500px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  @media (max-width: 640px) {
    :global(.marketplace-payment-modal) {
      margin: 0.5rem;
    }
  }
</style>

