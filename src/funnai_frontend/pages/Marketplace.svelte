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
  import { MARKETPLACE_DISABLED_MESSAGE, MARKETPLACE_ENABLED } from "../helpers/config/featureFlags";

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
  let reservationRefreshKey = 0; // Key to force re-check of reservation banner

  onMount(() => {
    if (!MARKETPLACE_ENABLED) {
      isLoading = false;
      return;
    }
    initialize();
  });

  // Reactive: Clean up stale reservations when user becomes authenticated
  $: if (MARKETPLACE_ENABLED && $store.isAuthed && !hasRunCleanup && !isCleaningReservation) {
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
        
        // Refresh listings and banner
        listingsRefreshKey++;
        reservationRefreshKey++;
      } else {
        console.log('✅ No stale reservations found on auth');
        // Still refresh the banner in case there was a race condition
        reservationRefreshKey++;
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
    isCleaningReservation = true;
    
    try {
      // Get the current reservation to show details
      const reservationResult = await MarketplaceService.getUserReservation();
      console.log('📋 Current reservation:', reservationResult);
      
      if (!reservationResult.reservation) {
        console.log('✅ No reservation found to clear');
        toastStore.success('No pending reservation found', 3000);
        reservationRefreshKey++; // Force banner to re-check and hide
        return;
      }
      
      const mainerAddress = reservationResult.reservation.address;
      console.log('🔧 Clearing reservation for mAIner:', mainerAddress);
      
      // Clear the reservation
      const clearResult = await MarketplaceService.cancelReservation(mainerAddress);
      
      if (clearResult.success) {
        if (clearResult.alreadyCleared) {
          console.log('✅ Reservation was already cleared (sale may have completed)');
          toastStore.success('Reservation was already cleared. The sale may have completed successfully!', 5000);
        } else {
          console.log('✅ Reservation cleared successfully');
          toastStore.success('Reservation cleared! The mAIner has been returned to the marketplace.', 5000);
        }
        
        // Wait for backend to process
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Verify it was cleared
        const verifyResult = await MarketplaceService.getUserReservation();
        if (verifyResult.reservation) {
          console.error('❌ Verification failed - reservation still exists after clear');
          toastStore.error('Reservation may not have been fully cleared. Please wait 2 minutes and try again.', 8000);
        }
      } else {
        console.error('❌ Failed to clear reservation:', clearResult.error);
        toastStore.error(`Failed to clear reservation: ${clearResult.error}`, 6000);
      }
      
    } catch (error) {
      console.error('❌ Error clearing reservation:', error);
      toastStore.error(`Error: ${error.message}`, 6000);
    } finally {
      isCleaningReservation = false;
      // Force the banner to re-check
      reservationRefreshKey++;
      // Also refresh listings in case the mAIner was returned
      await loadMarketplaceStats();
      listingsRefreshKey++;
    }
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
    // Also refresh user's mAIner canisters to catch any that were sold
    store.loadUserMainerCanisters();
  }

  // Reactive: refresh stats when switching tabs (keeps numbers up-to-date)
  $: if (activeTab) {
    loadMarketplaceStats();
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
        
        // Refresh marketplace data, user listings, and mAIner canisters
        await Promise.all([
          loadMarketplaceStats(),
          loadUserListings(),
          store.loadUserMainerCanisters()
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
    console.log("Opening purchase confirmation for mAIner:", mainerId);
    
    // Check if user is authenticated
    if (!$store.isAuthed) {
      toastStore.warning("Please connect your wallet to purchase mAIners", 5000);
      return;
    }
    
    if (isBuyingMainer) {
      toastStore.warning("Another purchase is already in progress. Please wait.");
      return;
    }
    
    // Convert price from ICP to e8s
    const priceE8S = Math.round(price * 100_000_000);
    
    // Just open the confirmation modal - NO reservation yet!
    // Reservation will happen when user confirms the purchase
    selectedListingForPurchase = {
      listingId: listingId,
      mainerId: mainerId,
      mainerName: `mAIner ${mainerId.slice(0, 5)}`,
      seller: '', // Will be filled when we have reservation info
      priceE8S: priceE8S
    };
    
    // Reset state
    buyProcessStep = 'idle';
    buyProcessError = '';
    
    // Show the confirmation modal
    showPaymentModal = true;
  }

  async function handlePurchaseComplete() {
    // Called by the payment modal after successful purchase
    // The modal handles the entire flow: reservation → approval → completion
    console.log("✅ Purchase completed successfully!");
    
    const mainerName = selectedListingForPurchase?.mainerName || 'mAIner';
    const purchasedMainerId = selectedListingForPurchase?.mainerId;
    
    toastStore.success(
      `Successfully purchased ${mainerName}! The mAIner has been transferred to your account.`,
      8000
    );
    
    // Reset state
    showPaymentModal = false;
    selectedListingForPurchase = null;
    isBuyingMainer = false;
    buyProcessStep = 'idle';
    
    // Small delay to ensure backend has finished all updates
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Refresh marketplace data and user's mAIner list
    await loadMarketplaceStats();
    await store.loadUserMainerCanisters();
    
    // Trigger listings refresh to get fresh data from backend
    listingsRefreshKey++;
    
    // Secondary refresh after a delay to catch any race conditions with backend timers
    // This ensures stale listings are cleared even if there's a timing issue
    setTimeout(() => {
      console.log("🔄 Secondary marketplace refresh to clear any stale data");
      listingsRefreshKey++;
    }, 3000);
  }

  async function handlePaymentModalClose() {
    // The modal now handles reservations internally
    // If user closes before confirming, no reservation was made
    // If user closes during processing, the modal warns them first
    
    showPaymentModal = false;
    selectedListingForPurchase = null;
    isBuyingMainer = false;
    buyProcessStep = 'idle';
    
    // Refresh listings in case state changed
    listingsRefreshKey++;
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

<div class="agent-page">
  <div class="agent-container">
    <!-- Header Section -->
    <div class="mb-8">
      <!-- Header -->
      <div class="flex items-center space-x-3 sm:space-x-4 mb-6">
        <div>
          <p class="agent-eyebrow mb-2">Trade</p>
          <div class="flex items-center gap-2 sm:gap-3">
            <h1 class="agent-title">Marketplace</h1>
            {#if !MARKETPLACE_ENABLED}
              <span class="px-2.5 py-0.5 text-[11px] font-semibold tracking-tight rounded-full border border-amber-500/30 bg-amber-500/10 text-amber-300">
                Temporarily unavailable
              </span>
            {/if}
          </div>
          <p class="agent-subtitle mt-1 hidden sm:block">
            Buy and sell autonomous mAIner agents on the network
          </p>
        </div>
      </div>

      {#if !MARKETPLACE_ENABLED}
        <div class="agent-card relative overflow-hidden p-6 sm:p-8">
          <div class="absolute -top-16 right-0 h-40 w-56 rounded-full bg-amber-500/10 blur-3xl pointer-events-none" aria-hidden="true"></div>
          <div class="relative flex flex-col sm:flex-row items-start gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-amber-500/25 bg-amber-500/10">
              <Store class="w-6 h-6 text-amber-300" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-amber-400/80">Maintenance</p>
              <h2 class="mt-1 text-xl font-semibold tracking-tight text-white">
                Marketplace will return soon
              </h2>
              <p class="mt-2 text-sm text-gray-400 leading-relaxed">
                {MARKETPLACE_DISABLED_MESSAGE} Buying and selling are paused while we complete maintenance. Check back shortly.
              </p>
              <p class="mt-4 text-xs text-gray-500">
                Updates on
                <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer" class="text-gray-300 underline decoration-white/20 underline-offset-2 hover:text-white transition-colors">X</a>
                or
                <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/" target="_blank" rel="noopener noreferrer" class="text-gray-300 underline decoration-white/20 underline-offset-2 hover:text-white transition-colors">OpenChat</a>.
              </p>
            </div>
          </div>
        </div>
      {:else}
      <!-- Tab Navigation -->
      <div class="flex justify-end mb-4">
        <div class="agent-tab-track w-full sm:w-auto">
          <button
            on:click={() => activeTab = 'buy'}
            class="agent-tab flex-1 sm:flex-none inline-flex items-center justify-center gap-2 {activeTab === 'buy' ? 'agent-tab-active' : ''}"
          >
            <ShoppingCart class="w-4 h-4" />
            <span>Buy</span>
          </button>
          
          <button
            on:click={() => activeTab = 'sell'}
            class="agent-tab flex-1 sm:flex-none inline-flex items-center justify-center gap-2 {activeTab === 'sell' ? 'agent-tab-active' : ''}"
          >
            <Tag class="w-4 h-4" />
            <span>Sell</span>
          </button>

          <button
            on:click={() => activeTab = 'history'}
            class="agent-tab flex-1 sm:flex-none inline-flex items-center justify-center gap-2 {activeTab === 'history' ? 'agent-tab-active' : ''}"
          >
            <History class="w-4 h-4" />
            <span>History</span>
          </button>
        </div>
      </div>

      <!-- Stale Reservation Warning Banner -->
      {#if $store.isAuthed}
        {#key reservationRefreshKey}
          {#await MarketplaceService.getUserReservation() then reservationCheck}
            {#if reservationCheck.success && reservationCheck.reservation}
              <div class="mt-6 p-4 agent-card border-amber-500/30 bg-amber-500/5">
                <div class="relative flex items-start gap-3">
                  <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-amber-500/20 bg-amber-500/10">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-amber-400/80">Reservation</p>
                    <h3 class="mt-1 text-base font-semibold tracking-tight text-white">Stale reservation detected</h3>
                    <p class="mt-1 text-sm font-normal text-gray-400">
                      A pending reservation from a previous session is blocking new purchases.
                    </p>
                    <p class="mt-2 text-xs font-mono text-gray-500 truncate">
                      mAIner: {reservationCheck.reservation.address}
                    </p>
                    <div class="mt-4 flex flex-wrap items-center gap-3">
                      <button
                        on:click={manualClearReservation}
                        disabled={isCleaningReservation}
                        class="agent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {#if isCleaningReservation}
                          <div class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>Clearing…</span>
                        {:else}
                          <span>Clear reservation</span>
                        {/if}
                      </button>
                      <p class="text-xs text-gray-500">
                        Returns the mAIner to the marketplace
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            {/if}
          {/await}
        {/key}
      {/if}

      <!-- Stats Cards -->
      {#if !isLoading}
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div class="agent-stat">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
                <Store class="w-5 h-5 text-agent-purple" />
              </div>
              <div>
                <p class="text-sm text-gray-400">Active Listings</p>
                <p class="text-2xl font-semibold text-white">{stats.totalListings}</p>
              </div>
            </div>
          </div>

          <div class="agent-stat">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/10 flex items-center justify-center">
                <Zap class="w-5 h-5 text-gray-300" />
              </div>
              <div>
                <p class="text-sm text-gray-400">Total Sales</p>
                <p class="text-2xl font-semibold text-white">{stats.totalSales}</p>
              </div>
            </div>
          </div>

          <div class="agent-stat">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/10 flex items-center justify-center">
                <TrendingUp class="w-5 h-5 text-gray-300" />
              </div>
              <div>
                <p class="text-sm text-gray-400">Sales Volume</p>
                <p class="text-2xl font-semibold text-white">{stats.totalVolume} ICP</p>
              </div>
            </div>
          </div>

          <div class="agent-stat">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/10 flex items-center justify-center">
                <Users class="w-5 h-5 text-gray-300" />
              </div>
              <div>
                <p class="text-sm text-gray-400">Total Traders</p>
                <p class="text-2xl font-semibold text-white">{stats.activeTraders}</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
      {/if}
    </div>

    {#if MARKETPLACE_ENABLED}
    {#if isLoading}
      <div class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-agent-purple mx-auto mb-4"></div>
          <p class="text-gray-400">Loading marketplace...</p>
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
    {/if}
  </div>

  <Footer />
</div>

<!-- Payment Modal -->
{#if MARKETPLACE_ENABLED}
  <MarketplacePaymentModal
    isOpen={showPaymentModal}
    onClose={handlePaymentModalClose}
    onSuccess={handlePurchaseComplete}
    listing={selectedListingForPurchase}
    isCanceling={isCancelingReservation}
  />
{/if}

<!-- Toast Notifications -->
<ToastContainer />

