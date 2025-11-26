<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import { ShoppingBag, Info, AlertCircle, CheckCircle, Loader2 } from 'lucide-svelte';
  import { store, canisterIds } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { Principal } from "@dfinity/principal";
  import { MarketplaceService } from "../../helpers/marketplaceService";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: () => void = () => {}; // Called after successful purchase
  export let listing: any = null; // The marketplace listing being purchased
  export let isCanceling: boolean = false; // Loading state when canceling reservation
  
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
  
  let isProcessing: boolean = false;
  let errorMessage: string = "";
  let balance: bigint = BigInt(0);
  let isLoadingBalance: boolean = true;
  
  // Purchase process state
  type PurchaseStep = 'confirm' | 'reserving' | 'approving' | 'completing' | 'success' | 'error';
  let currentStep: PurchaseStep = 'confirm';
  
  // Reservation timer (only active after reservation is made)
  let reservationActive: boolean = false;
  let reservationStartTime: number = 0;
  let timeRemaining: number = 120; // seconds
  let timerInterval: NodeJS.Timeout | null = null;
  let reservedListingInfo: any = null; // Store listing info after reservation
  
  // Price from listing (in e8s)
  $: priceE8s = listing ? BigInt(listing.priceE8S) : BigInt(0);
  $: priceICP = Number(priceE8s) / 100_000_000;
  $: totalWithFee = priceE8s + ICP_FEE;
  $: totalICPWithFee = Number(totalWithFee) / 100_000_000;
  
  // Validation
  $: hasInsufficientBalance = balance < totalWithFee;
  $: canSubmit = !isProcessing && !hasInsufficientBalance && balance > BigInt(0) && listing !== null;
  
  function startReservationTimer() {
    reservationStartTime = Date.now();
    timeRemaining = 120;
    reservationActive = true;
    
    // Clear any existing timer
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    
    // Update timer every second
    timerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - reservationStartTime) / 1000);
      timeRemaining = Math.max(0, 120 - elapsed);
      
      if (timeRemaining === 0) {
        // Timer expired - the backend will auto-cancel
        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
        }
        errorMessage = "Reservation expired. The mAIner has been returned to the marketplace.";
        currentStep = 'error';
        isProcessing = false;
        setTimeout(() => {
          onClose();
        }, 3000);
      }
    }, 1000);
  }
  
  function stopReservationTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    reservationActive = false;
  }
  
  onMount(() => {
    if (isOpen && listing) {
      loadBalance();
    }
    
    return () => {
      stopReservationTimer();
    };
  });
  
  $: if (isOpen && listing) {
    loadBalance();
    errorMessage = "";
    currentStep = 'confirm';
    reservationActive = false;
    reservedListingInfo = null;
  } else if (!isOpen) {
    stopReservationTimer();
    currentStep = 'confirm';
    isProcessing = false;
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
  
  async function handleConfirmPurchase() {
    if (!canSubmit || !listing) return;
    
    isProcessing = true;
    errorMessage = "";
    
    try {
      // STEP 1: Pre-check for existing reservations
      console.log("🔍 Pre-check: Verifying no existing reservations...");
      const preCheckResult = await MarketplaceService.getUserReservation();
      
      const hasReservation = preCheckResult.success && 
                            preCheckResult.reservation && 
                            !(Array.isArray(preCheckResult.reservation) && preCheckResult.reservation.length === 0);
      
      if (hasReservation) {
        throw new Error('You already have a pending reservation. Please wait for it to expire or refresh the page.');
      }
      
      // STEP 2: Reserve the mAIner
      console.log("Step 1/3: Reserving mAIner...");
      currentStep = 'reserving';
      
      const reserveResult = await MarketplaceService.reserveMainer(listing.mainerId);
      
      if (!reserveResult.success || !reserveResult.listing) {
        throw new Error(reserveResult.error || 'Failed to reserve mAIner');
      }
      
      // Store reserved listing info and start timer
      reservedListingInfo = {
        ...reserveResult.listing,
        mainerId: listing.mainerId,
        seller: reserveResult.listing.listedBy
      };
      startReservationTimer();
      
      console.log("✅ mAIner reserved successfully");
      
      // STEP 3: Approve ICP to Game State canister
      console.log("Step 2/3: Approving ICP...");
      currentStep = 'approving';
      
      const approveResult = await IcrcService.checkAndRequestIcrc2Allowances(
        ICP_TOKEN,
        totalWithFee,
        canisterIds.gameStateCanisterId
      );
      
      if (approveResult === null) {
        throw new Error('Failed to approve ICP allowance');
      }
      
      console.log("✅ ICP approval successful! Allowance:", approveResult.toString());
      
      // STEP 4: Complete the purchase
      console.log("Step 3/3: Completing purchase...");
      currentStep = 'completing';
      
      const completeResult = await MarketplaceService.completePurchase(
        listing.mainerId,
        reservedListingInfo.seller,
        approveResult
      );
      
      if (!completeResult.success) {
        throw new Error(completeResult.error || 'Failed to complete purchase');
      }
      
      console.log("✅ Purchase completed successfully!");
      stopReservationTimer();
      currentStep = 'success';
      
      // Wait a moment to show success state
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
      
    } catch (error) {
      console.error("Error in purchase process:", error);
      errorMessage = error.message || "Purchase failed. Please try again.";
      currentStep = 'error';
      isProcessing = false;
      
      // If we had a reservation and failed, it will auto-expire
      // The timer will keep running to show user when it expires
    }
  }
  
  async function handleClose() {
    if (isProcessing && currentStep !== 'confirm') {
      // If we're in the middle of processing after reservation, warn user
      if (reservationActive && !confirm('Purchase in progress. Closing will cancel your reservation. Continue?')) {
        return;
      }
    }
    
    if (!isProcessing || currentStep === 'confirm' || currentStep === 'error') {
      stopReservationTimer();
      errorMessage = "";
      onClose();
    }
  }
  
  function formatICP(e8s: bigint): string {
    return (Number(e8s) / 100_000_000).toFixed(8);
  }
  
  function getStepStatus(step: PurchaseStep): 'pending' | 'active' | 'complete' | 'error' {
    const steps: PurchaseStep[] = ['reserving', 'approving', 'completing'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    
    if (currentStep === 'error') return 'error';
    if (currentStep === 'success') return 'complete';
    if (currentStep === 'confirm') return 'pending';
    
    if (stepIndex < currentIndex) return 'complete';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
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
    {:else if currentStep === 'success'}
      <!-- Success State -->
      <div class="text-center py-8">
        <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle class="w-10 h-10 text-green-600 dark:text-green-400" />
        </div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">Purchase Complete!</h3>
        <p class="text-gray-600 dark:text-gray-400">
          {listing.mainerName} has been transferred to your account.
        </p>
      </div>
    {:else}
      <!-- Reservation Timer Banner (only shown after reservation is made) -->
      {#if reservationActive}
        <div class="flex items-center justify-between p-3 rounded-lg {timeRemaining <= 30 ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800' : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'}">
          <div class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 {timeRemaining <= 30 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm font-medium {timeRemaining <= 30 ? 'text-red-900 dark:text-red-200' : 'text-blue-900 dark:text-blue-200'}">
                {timeRemaining <= 30 ? 'Completing purchase...' : 'mAIner reserved for you'}
              </p>
              <p class="text-xs {timeRemaining <= 30 ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'}">
                Processing payment...
              </p>
            </div>
          </div>
          <div class="text-right">
            <div class="text-2xl font-bold {timeRemaining <= 30 ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'}">
              {formatTime(timeRemaining)}
            </div>
          </div>
        </div>
      {/if}

      <!-- Progress Steps (shown during purchase process) -->
      {#if currentStep !== 'confirm'}
        <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div class="space-y-3">
            <!-- Step 1: Reserving -->
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                {getStepStatus('reserving') === 'complete' ? 'bg-green-500' : 
                 getStepStatus('reserving') === 'active' ? 'bg-purple-500' : 
                 getStepStatus('reserving') === 'error' ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}">
                {#if getStepStatus('reserving') === 'complete'}
                  <CheckCircle class="w-4 h-4 text-white" />
                {:else if getStepStatus('reserving') === 'active'}
                  <div class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {:else}
                  <span class="text-xs text-white font-bold">1</span>
                {/if}
              </div>
              <span class="text-sm {getStepStatus('reserving') === 'active' ? 'text-purple-600 dark:text-purple-400 font-medium' : 'text-gray-600 dark:text-gray-400'}">
                {getStepStatus('reserving') === 'active' ? 'Reserving mAIner...' : 'Reserve mAIner'}
              </span>
            </div>
            
            <!-- Step 2: Approving -->
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                {getStepStatus('approving') === 'complete' ? 'bg-green-500' : 
                 getStepStatus('approving') === 'active' ? 'bg-purple-500' : 
                 getStepStatus('approving') === 'error' ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}">
                {#if getStepStatus('approving') === 'complete'}
                  <CheckCircle class="w-4 h-4 text-white" />
                {:else if getStepStatus('approving') === 'active'}
                  <div class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {:else}
                  <span class="text-xs text-white font-bold">2</span>
                {/if}
              </div>
              <span class="text-sm {getStepStatus('approving') === 'active' ? 'text-purple-600 dark:text-purple-400 font-medium' : 'text-gray-600 dark:text-gray-400'}">
                {getStepStatus('approving') === 'active' ? 'Approving ICP...' : 'Approve ICP'}
              </span>
            </div>
            
            <!-- Step 3: Completing -->
            <div class="flex items-center gap-3">
              <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0
                {getStepStatus('completing') === 'complete' ? 'bg-green-500' : 
                 getStepStatus('completing') === 'active' ? 'bg-purple-500' : 
                 getStepStatus('completing') === 'error' ? 'bg-red-500' : 'bg-gray-300 dark:bg-gray-600'}">
                {#if getStepStatus('completing') === 'complete'}
                  <CheckCircle class="w-4 h-4 text-white" />
                {:else if getStepStatus('completing') === 'active'}
                  <div class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {:else}
                  <span class="text-xs text-white font-bold">3</span>
                {/if}
              </div>
              <span class="text-sm {getStepStatus('completing') === 'active' ? 'text-purple-600 dark:text-purple-400 font-medium' : 'text-gray-600 dark:text-gray-400'}">
                {getStepStatus('completing') === 'active' ? 'Completing purchase...' : 'Complete purchase'}
              </span>
            </div>
          </div>
        </div>
      {/if}

      <!-- mAIner Info -->
      <div class="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <div class="flex items-start space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <ShoppingBag class="w-5 h-5 text-white" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-white truncate">🦜 {listing.mainerName}</h3>
            {#if listing.cycleBalance}
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Balance: <span class="font-medium">{formatLargeNumber(listing.cycleBalance / 1_000_000_000_000, 2, false)} TCYCLES</span>
              </p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Seller Info (only show in confirm step or if we have seller info) -->
      {#if listing.seller || reservedListingInfo?.seller}
        <div>
          <span class="block text-xs text-gray-600 dark:text-gray-400 mb-1.5">Seller</span>
          <div class="p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
            <p class="text-xs font-mono text-gray-700 dark:text-gray-300 break-all">{reservedListingInfo?.seller || listing.seller}</p>
          </div>
        </div>
      {/if}

      <!-- Balance Display (only in confirm step) -->
      {#if currentStep === 'confirm'}
        <div>
          <span class="block text-xs text-gray-600 dark:text-gray-400 mb-1.5">Your ICP Balance</span>
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
      {/if}

      <!-- Payment Breakdown -->
      <div class="space-y-2">
        <span class="block text-xs text-gray-600 dark:text-gray-400">Payment Details</span>
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

      <!-- Info Box (only in confirm step) -->
      {#if currentStep === 'confirm'}
        <div class="flex items-start space-x-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <Info class="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div class="text-xs text-blue-700 dark:text-blue-300">
            <p class="font-medium mb-1">Secure escrow purchase</p>
            <p>When you confirm, the mAIner will be reserved for you, then ICP will be approved and the protocol will securely complete the transfer.</p>
          </div>
        </div>
      {/if}

      <!-- Error Message -->
      {#if errorMessage}
        <div class="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <p class="text-sm text-red-700 dark:text-red-300">{errorMessage}</p>
        </div>
      {/if}

      <!-- Insufficient Balance Warning (only in confirm step) -->
      {#if currentStep === 'confirm' && hasInsufficientBalance && !isLoadingBalance}
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
      {#if currentStep === 'confirm'}
        <div class="flex space-x-3 pt-2">
          <button
            type="button"
            on:click={handleClose}
            class="flex-1 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            disabled={isProcessing}
          >
            <span>Cancel</span>
          </button>
          <button
            type="button"
            on:click={handleConfirmPurchase}
            class="flex-1 px-4 py-2.5 rounded-lg text-white font-medium flex items-center justify-center space-x-2 transition-colors"
            class:bg-purple-600={canSubmit}
            class:hover:bg-purple-700={canSubmit}
            class:bg-gray-400={!canSubmit}
            class:dark:bg-gray-700={!canSubmit}
            class:cursor-not-allowed={!canSubmit}
            disabled={!canSubmit}
          >
            <ShoppingBag class="w-4 h-4" />
            <span>Confirm Purchase</span>
          </button>
        </div>
      {:else if currentStep === 'error'}
        <div class="flex space-x-3 pt-2">
          <button
            type="button"
            on:click={handleClose}
            class="flex-1 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors flex items-center justify-center"
          >
            <span>Close</span>
          </button>
        </div>
      {/if}
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

  .spinner {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
</style>

