<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../stores/store";
  import { toastStore } from "../stores/toastStore";
  import Footer from "../components/funnai/Footer.svelte";
  import MyMainersForSale from "../components/marketplace/MyMainersForSale.svelte";
  import MarketplaceListings from "../components/marketplace/MarketplaceListings.svelte";
  import MarketplacePaymentModal from "../components/marketplace/MarketplacePaymentModal.svelte";
  import MarketplaceTransactionHistory from "../components/marketplace/MarketplaceTransactionHistory.svelte";
  import ToastContainer from "../components/common/ToastContainer.svelte";
  import { Store, TrendingUp, Users, Zap, ShoppingCart, Tag, History } from "lucide-svelte";
  import { MarketplaceService } from "../helpers/marketplaceService";
  import type { Principal } from '@dfinity/principal';

  let isLoading = true;
  let activeTab: 'sell' | 'buy' | 'history' = 'buy';
  let stats = {
    totalListings: 0,
    totalSales: 0,
    totalVolume: "0",
    activeTraders: 0,
  };

  // User's listed mAIners (for filtering in "My mAIners" section)
  let userListedMainerAddresses: string[] = [];

  // Payment modal state
  let showPaymentModal = false;
  let selectedListingForPurchase: any = null;
  
  // Buy process state
  let isBuyingMainer = false;
  let buyProcessStep: 'idle' | 'reserving' | 'payment' | 'completing' | 'success' | 'error' = 'idle';
  let buyProcessError: string = '';
  let isCancelingReservation = false;
  
  // Reactive key to force MarketplaceListings to refresh
  let listingsRefreshKey = 0;

  let hasRunCleanup = false;
  let isCleaningReservation = false;

  onMount(() => {
    initialize();
  });

  // Reactive: Clean up stale reservations when user becomes authenticated
  $: if ($store.isAuthed && !hasRunCleanup && !isCleaningReservation) {
    console.log('🔄 Auth state changed, running cleanup check...');
    clearStaleReservationsOnAuth();
  }

  async function clearStaleReservationsOnAuth() {
    if (isCleaningReservation) {
      console.log('⚠️ Cleanup already in progress, skipping');
      return;
    }
    
    isCleaningReservation = true;
    hasRunCleanup = true;
    
    try {
      console.log('🔍 Checking for stale reservations on auth...');
      const cleanupResult = await MarketplaceService.clearStaleReservation();
      
      if (cleanupResult.hadReservation) {
        console.log('✅ Cleared stale reservation after auth');
        toastStore.success('Cleared stale reservation - marketplace is ready!', 4000);
        
        // Wait for backend to fully process
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Verify cleanup worked
        const verifyResult = await MarketplaceService.getUserReservation();
        console.log('🔍 Verification after auth cleanup:', verifyResult);
        
        if (verifyResult.reservation) {
          console.error('❌ Verification failed - reservation still exists!');
          toastStore.error('Failed to clear reservation. Please wait 2 minutes or contact support.', 8000);
        } else {
          console.log('✅ Verification passed - no reservation exists');
        }
        
        // Refresh listings
        listingsRefreshKey++;
      } else {
        console.log('✅ No stale reservations found on auth');
      }
    } catch (error) {
      console.error('❌ Error during cleanup:', error);
      toastStore.error('Error clearing reservation: ' + error.message, 6000);
    } finally {
      isCleaningReservation = false;
    }
  }

  // Manual cleanup function (for button)
  async function manualClearReservation() {
    console.log('🔧 Manual cleanup requested...');
    hasRunCleanup = false; // Reset the flag to allow cleanup
    await clearStaleReservationsOnAuth();
    
    // Reload listings after manual cleanup
    await loadMarketplaceStats();
    listingsRefreshKey++;
  }

  // Reactive: reload user listings when auth state changes
  $: if ($store.isAuthed) {
    loadUserListings();
  } else {
    userListedMainerAddresses = [];
    hasRunCleanup = false; // Reset cleanup flag when user logs out
  }

  // Reactive: reload when switching to sell tab
  $: if (activeTab === 'sell' && $store.isAuthed) {
    loadUserListings();
  }

  async function initialize() {
    isLoading = true;
    
    // If user is already authenticated on page load, run cleanup immediately
    if ($store.isAuthed && !hasRunCleanup) {
      console.log('🔄 User already authenticated on load, running cleanup...');
      await clearStaleReservationsOnAuth();
    }
    
    try {
      await loadMarketplaceStats();
      await loadUserListings();
    } catch (error) {
      console.error("Error initializing marketplace:", error);
    } finally {
      isLoading = false;
    }
  }

  async function loadMarketplaceStats() {
    const result = await MarketplaceService.getMarketplaceStats();
    
    if (result.success && result.stats) {
      stats = result.stats;
    } else {
      console.error("Failed to load marketplace stats:", result.error);
      // Keep default values
      stats = {
        totalListings: 0,
        totalSales: 0,
        totalVolume: "0",
        activeTraders: 0,
      };
    }
  }

  async function loadUserListings() {
    if (!$store.isAuthed) {
      console.log('Not authenticated, clearing user listings');
      userListedMainerAddresses = [];
      return;
    }

    try {
      console.log('Loading user listings...');
      const result = await MarketplaceService.getUserListings();
      
      if (result.success && result.listings) {
        userListedMainerAddresses = result.listings.map(listing => listing.address);
        console.log(`✅ User has ${userListedMainerAddresses.length} mAIners listed:`, userListedMainerAddresses);
      } else {
        console.error("Failed to load user listings:", result.error);
        userListedMainerAddresses = [];
      }
    } catch (error) {
      console.error("Error loading user listings:", error);
      userListedMainerAddresses = [];
    }
  }

  async function handleListToMarketplace(mainerIds: string[], prices: Record<string, number>) {
    console.log("Listing mAIners to marketplace:", mainerIds, prices);
    
    let successCount = 0;
    let errorCount = 0;
    const errors: string[] = [];
    
    try {
      for (const mainerId of mainerIds) {
        const price = prices[mainerId];
        const result = await MarketplaceService.listMainer(mainerId, price);
        
        if (result.success) {
          successCount++;
          console.log(`Successfully listed ${mainerId} for ${price} ICP`);
        } else {
          errorCount++;
          errors.push(`${mainerId.slice(0, 8)}...: ${result.error}`);
          console.error(`Failed to list ${mainerId}:`, result.error);
        }
      }
      
      // Show result
      if (successCount > 0) {
        toastStore.success(
          `Successfully listed ${successCount} mAIner${successCount > 1 ? 's' : ''} to marketplace!`,
          6000
        );
        
        if (errorCount > 0) {
          toastStore.warning(
            `Failed to list ${errorCount} mAIner${errorCount > 1 ? 's' : ''}. Check console for details.`,
            6000
          );
        }
        
        // Refresh marketplace data and user listings
        await Promise.all([
          loadMarketplaceStats(),
          loadUserListings()
        ]);
      } else {
        throw new Error(`Failed to list all mAIners. ${errors.join('; ')}`);
      }
    } catch (error) {
      console.error("Error listing mAIners:", error);
      toastStore.error(`Failed to list mAIners: ${error.message || 'Unknown error'}`, 8000);
      throw error;
    }
  }

  async function handleBuyMainer(listingId: string, mainerId: string, price: number) {
    console.log("Starting buy process for mAIner:", mainerId);
    
    // Check if user is authenticated
    if (!$store.isAuthed) {
      toastStore.warning("Please connect your wallet to purchase mAIners", 5000);
      return;
    }
    
    if (isBuyingMainer) {
      toastStore.warning("Another purchase is already in progress. Please wait.");
      return;
    }
    
    // Find the full listing object to pass to payment modal
    // We'll trigger this from MarketplaceListings component with full listing
    buyProcessStep = 'reserving';
    isBuyingMainer = true;
    buyProcessError = '';
    
    try {
      // Pre-check: Verify user doesn't have an existing reservation
      console.log("🔍 Pre-check: Verifying no existing reservations...");
      const preCheckResult = await MarketplaceService.getUserReservation();
      console.log("🔍 Pre-check result:", preCheckResult);
      
      // Check if reservation exists (handle both null and empty array)
      const hasReservation = preCheckResult.success && 
                            preCheckResult.reservation && 
                            !(Array.isArray(preCheckResult.reservation) && preCheckResult.reservation.length === 0);
      
      if (hasReservation) {
        console.error("❌ User still has a reservation:", preCheckResult.reservation);
        throw new Error('You already have a pending reservation. Please refresh the page or wait for it to expire.');
      }
      
      console.log("✅ Pre-check passed, proceeding with reservation");
      
      // Step 1: Reserve the mAIner
      console.log("Step 1: Reserving mAIner...");
      const reserveResult = await MarketplaceService.reserveMainer(mainerId);
      
      if (!reserveResult.success || !reserveResult.listing) {
        throw new Error(reserveResult.error || 'Failed to reserve mAIner');
      }
      
      console.log("Step 1: mAIner reserved successfully");
      
      // Step 2: Show payment modal
      console.log("Step 2: Opening payment modal...");
      selectedListingForPurchase = {
        ...reserveResult.listing,
        mainerId: mainerId,
        mainerName: `mAIner ${mainerId.slice(0, 5)}`,
        seller: reserveResult.listing.listedBy,
        priceE8S: Number(reserveResult.listing.priceE8S)
      };
      
      buyProcessStep = 'payment';
      showPaymentModal = true;
      
    } catch (error) {
      console.error("Error in buy process:", error);
      buyProcessStep = 'error';
      buyProcessError = error.message || 'Failed to initiate purchase';
      toastStore.error(`Failed to purchase mAIner: ${buyProcessError}`, 8000);
      isBuyingMainer = false;
      showPaymentModal = false; // Ensure modal doesn't open on error
      selectedListingForPurchase = null; // Clear any partial state
    }
  }

  async function handlePaymentSuccess(txId: bigint) {
    console.log("Step 2: ICP approval successful, allowance:", txId.toString());
    
    if (!selectedListingForPurchase) {
      console.error("No selected listing for purchase");
      isBuyingMainer = false;
      return;
    }
    
    // Save listing info before it might get cleared by modal closing
    const listingInfo = {
      mainerId: selectedListingForPurchase.mainerId,
      mainerName: selectedListingForPurchase.mainerName,
      seller: selectedListingForPurchase.seller
    };
    
    try {
      // Step 3: Complete the purchase
      console.log("Step 3: Completing purchase...");
      buyProcessStep = 'completing';
      
      const completeResult = await MarketplaceService.completePurchase(
        listingInfo.mainerId,
        listingInfo.seller,
        txId
      );
      
      if (!completeResult.success) {
        throw new Error(completeResult.error || 'Failed to complete purchase');
      }
      
      console.log("Step 3: Purchase completed successfully!");
      buyProcessStep = 'success';
      
      // Close the modal immediately after success
      showPaymentModal = false;
      
      toastStore.success(
        `Successfully purchased ${listingInfo.mainerName}! The mAIner has been transferred to your account.`,
        8000
      );
      
      // Refresh marketplace data and user's mAIner list
      await loadMarketplaceStats();
      await store.loadUserMainerCanisters();
      
    } catch (error) {
      console.error("Error completing purchase:", error);
      buyProcessStep = 'error';
      buyProcessError = error.message || 'Failed to complete purchase';
      
      // Close modal on error too
      showPaymentModal = false;
      
      toastStore.error(
        `Failed to complete purchase: ${buyProcessError}. Your ICP was approved but not transferred. The approval will expire. Please try again or contact support.`,
        12000
      );
    } finally {
      isBuyingMainer = false;
      selectedListingForPurchase = null;
    }
  }

  async function handlePaymentModalClose() {
    // If user is closing the modal during payment step, cancel the reservation
    if (buyProcessStep === 'payment' && selectedListingForPurchase) {
      console.log("User canceled purchase, canceling reservation...");
      isCancelingReservation = true;
      
      try {
        await MarketplaceService.cancelReservation(selectedListingForPurchase.mainerId);
        console.log("Reservation canceled successfully");
        
        // Refresh marketplace listings so the mAIner appears again
        await loadMarketplaceStats();
        
        // Trigger a refresh of the MarketplaceListings component
        // We'll do this by incrementing a reactive key
        listingsRefreshKey++;
        
      } catch (error) {
        console.error("Error canceling reservation:", error);
        // Don't show error to user, just log it
      } finally {
        isCancelingReservation = false;
      }
    }
    
    showPaymentModal = false;
    selectedListingForPurchase = null;
    isBuyingMainer = false;
    buyProcessStep = 'idle';
  }

  async function handleCancelListing(listingId: string, mainerId: string) {
    console.log("Canceling listing:", mainerId);
    
    try {
      const result = await MarketplaceService.cancelListing(mainerId);
      
      if (result.success) {
        toastStore.success("Successfully canceled listing!", 5000);
        
        // Refresh marketplace data and user listings
        await Promise.all([
          loadMarketplaceStats(),
          loadUserListings()
        ]);
      } else {
        throw new Error(result.error || 'Failed to cancel listing');
      }
    } catch (error) {
      console.error("Error canceling listing:", error);
      toastStore.error(`Failed to cancel listing: ${error.message}`, 8000);
      throw error;
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20">
  <div class="container mx-auto px-4 py-8">
    <!-- Header Section -->
    <div class="mb-8">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <div class="flex items-center space-x-4">
          <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl shadow-lg flex items-center justify-center">
            <Store class="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 class="text-4xl font-bold text-gray-900 dark:text-white">mAIner Marketplace</h1>
            <p class="text-lg text-gray-600 dark:text-gray-400">
              Buy and sell funnAI mAIner agents on the Internet Computer
            </p>
          </div>
        </div>

        <!-- Tab Navigation - Primary Action -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-1.5 inline-flex gap-1 shadow-sm self-start sm:self-center">
          <button
            on:click={() => activeTab = 'buy'}
            class="px-5 py-3 rounded-lg transition-all duration-200 flex items-center space-x-3
                   {activeTab === 'buy' 
                     ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md' 
                     : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'}"
          >
            <ShoppingCart class="w-5 h-5" />
            <div class="text-left">
              <span class="font-semibold block">Buy</span>
              <span class="text-xs {activeTab === 'buy' ? 'text-white/80' : 'text-gray-500 dark:text-gray-500'}">Browse listings</span>
            </div>
          </button>
          
          <button
            on:click={() => activeTab = 'sell'}
            class="px-5 py-3 rounded-lg transition-all duration-200 flex items-center space-x-3
                   {activeTab === 'sell' 
                     ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md' 
                     : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'}"
          >
            <Tag class="w-5 h-5" />
            <div class="text-left">
              <span class="font-semibold block">Sell</span>
              <span class="text-xs {activeTab === 'sell' ? 'text-white/80' : 'text-gray-500 dark:text-gray-500'}">List your mAIners</span>
            </div>
          </button>
          
          <button
            on:click={() => activeTab = 'history'}
            class="px-5 py-3 rounded-lg transition-all duration-200 flex items-center space-x-3
                   {activeTab === 'history' 
                     ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md' 
                     : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'}"
          >
            <History class="w-5 h-5" />
            <div class="text-left">
              <span class="font-semibold block">History</span>
              <span class="text-xs {activeTab === 'history' ? 'text-white/80' : 'text-gray-500 dark:text-gray-500'}">Past transactions</span>
            </div>
          </button>
        </div>
      </div>

      <!-- Stale Reservation Warning Banner -->
      {#if $store.isAuthed}
        {#await MarketplaceService.getUserReservation() then reservationCheck}
          {#if reservationCheck.success && reservationCheck.reservation}
            <div class="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-600 rounded-lg">
              <div class="flex items-start space-x-3">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-yellow-900 dark:text-yellow-200">Stale Reservation Detected</h3>
                  <p class="text-sm text-yellow-800 dark:text-yellow-300 mt-1">
                    You have a pending reservation from a previous session. This prevents you from purchasing other mAIners.
                  </p>
                  <button
                    on:click={manualClearReservation}
                    disabled={isCleaningReservation}
                    class="mt-3 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {#if isCleaningReservation}
                      <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Clearing...</span>
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                      <span>Clear Reservation Now</span>
                    {/if}
                  </button>
                </div>
              </div>
            </div>
          {/if}
        {/await}
      {/if}

      <!-- Stats Cards -->
      {#if !isLoading}
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <Store class="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Active Listings</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalListings}</p>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-amber-100 dark:bg-amber-900/30 rounded-lg flex items-center justify-center">
                <Zap class="w-5 h-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Sales</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalSales}</p>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <TrendingUp class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Sales Volume</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalVolume} ICP</p>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <Users class="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Traders</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.activeTraders}</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>

    {#if isLoading}
      <div class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400">Loading marketplace...</p>
        </div>
      </div>
    {:else}
      <!-- Tab Content -->
      {#if activeTab === 'sell'}
        <MyMainersForSale 
          onListToMarketplace={handleListToMarketplace}
          listedMainers={userListedMainerAddresses}
        />
      {:else if activeTab === 'history'}
        <MarketplaceTransactionHistory />
      {:else}
        {#key listingsRefreshKey}
          <MarketplaceListings 
            onBuyMainer={handleBuyMainer}
            onCancelListing={handleCancelListing}
            isProcessing={isBuyingMainer}
          />
        {/key}
      {/if}
    {/if}
  </div>

  <Footer />
</div>

<!-- Payment Modal -->
  <MarketplacePaymentModal
    isOpen={showPaymentModal}
    onClose={handlePaymentModalClose}
    onSuccess={handlePaymentSuccess}
    listing={selectedListingForPurchase}
    isCanceling={isCancelingReservation}
  />

<!-- Toast Notifications -->
<ToastContainer />

