<script lang="ts">
  import { store } from "../../stores/store";
  import { toastStore } from "../../stores/toastStore";
  import { onMount, onDestroy } from "svelte";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { ShoppingBag, Crown, X, Eye, Tag, Clock, RefreshCw } from "lucide-svelte";
  import { MarketplaceService } from "../../helpers/marketplaceService";
  import { Principal } from '@dfinity/principal';
  import LoginModal from "../login/LoginModal.svelte";

  export let onBuyMainer: (listingId: string, mainerId: string, price: number) => Promise<void>;
  export let onCancelListing: (listingId: string, mainerId: string) => Promise<void>;
  export let isProcessing: boolean = false;
  
  // Export refresh function so parent can trigger updates
  export async function forceRefresh() {
    await loadListings();
  }

  let listings: MarketplaceListing[] = [];
  let isLoading = true;
  let selectedListing: MarketplaceListing | null = null;
  let showDetailsModal = false;
  let cancelingListingId: string | null = null; // Track which listing is being canceled

  // Connect wallet modal state
  let modalIsOpen = false;

  // Real-time update state
  const REFRESH_INTERVAL_MS = 15000; // 15 seconds
  let refreshInterval: ReturnType<typeof setInterval> | null = null;
  let isRefreshing = false; // Background refresh indicator (different from initial load)
  let lastRefreshTime: number = Date.now();
  let isPageVisible = true;

  // Pagination state
  let currentPage = 1;
  let itemsPerPage = 12;
  const itemsPerPageOptions = [12, 24, 48, 96];
  
  // Sorting state
  type SortOption = 'newest' | 'oldest' | 'price-low' | 'price-high';
  let sortBy: SortOption = 'newest';
  let isSorting = false; // Visual indicator for sorting

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  // Sort listings based on selected option
  function sortListings(items: MarketplaceListing[]): MarketplaceListing[] {
    return [...items].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return b.listedAt - a.listedAt;
        case 'oldest':
          return a.listedAt - b.listedAt;
        case 'price-low':
          return a.price - b.price;
        case 'price-high':
          return b.price - a.price;
        default:
          return 0;
      }
    });
  }

  // Pagination helpers
  function goToPage(page: number) {
    currentPage = Math.max(1, Math.min(page, totalPages));
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
    }
  }

  function handleItemsPerPageChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    itemsPerPage = parseInt(select.value);
    currentPage = 1; // Reset to first page when changing items per page
  }

  async function handleSortChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    const newSortBy = select.value as SortOption;
    
    // Show sorting indicator immediately
    isSorting = true;
    
    // Use requestAnimationFrame to ensure the UI updates before sorting
    await new Promise(resolve => requestAnimationFrame(resolve));
    
    // Apply the sort
    sortBy = newSortBy;
    currentPage = 1; // Reset to first page when changing sort
    
    // Brief delay to show the indicator (minimum visible time)
    await new Promise(resolve => setTimeout(resolve, 150));
    
    isSorting = false;
  }

  // Start auto-refresh polling
  function startAutoRefresh() {
    if (refreshInterval) return; // Already running
    
    console.log('🔄 Starting marketplace auto-refresh (every 15s)');
    refreshInterval = setInterval(async () => {
      if (isPageVisible && !isProcessing && !isLoading) {
        await refreshListings();
      }
    }, REFRESH_INTERVAL_MS);
  }

  // Stop auto-refresh polling
  function stopAutoRefresh() {
    if (refreshInterval) {
      console.log('⏹️ Stopping marketplace auto-refresh');
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  }

  // Handle visibility change (refresh when user returns to tab)
  function handleVisibilityChange() {
    isPageVisible = !document.hidden;
    
    if (isPageVisible) {
      console.log('👁️ Page became visible, checking if refresh needed');
      const timeSinceLastRefresh = Date.now() - lastRefreshTime;
      
      // If more than 10 seconds since last refresh, refresh immediately
      if (timeSinceLastRefresh > 10000) {
        refreshListings();
      }
    }
  }

  // Soft refresh (doesn't show loading spinner, just updates data)
  async function refreshListings() {
    if (isRefreshing || isLoading) return;
    
    isRefreshing = true;
    console.log('🔄 Refreshing marketplace listings...');
    
    try {
      const result = await MarketplaceService.getAllListings();
      
      if (result.success && result.listings) {
        const newListings = result.listings.map(listing => {
          const priceE8s = Number(listing.priceE8S);
          const priceICP = parseFloat((priceE8s / 100_000_000).toFixed(8));
          const isOwnListing = currentUserPrincipal && 
            listing.listedBy.toString() === currentUserPrincipal;
          const listedAtMs = Number(listing.listedTimestamp) / 1_000_000;
          
          return {
            id: listing.address,
            mainerId: listing.address,
            mainerName: `mAIner ${listing.address.slice(0, 5)}`,
            price: priceICP,
            seller: listing.listedBy.toString(),
            listedAt: listedAtMs,
            status: 'active',
            isOwnListing,
            createdAt: null,
            priceE8S: priceE8s
          };
        });
        
        // Check if listings changed
        const oldIds = new Set(listings.map(l => l.id));
        const newIds = new Set(newListings.map(l => l.id));
        const addedCount = [...newIds].filter(id => !oldIds.has(id)).length;
        const removedCount = [...oldIds].filter(id => !newIds.has(id)).length;
        const hasChanges = addedCount > 0 || removedCount > 0;
        
        if (hasChanges) {
          console.log('📊 Listings updated:', {
            before: listings.length,
            after: newListings.length,
            added: addedCount,
            removed: removedCount
          });
          
          // Notify user of changes (only if not the initial load)
          if (listings.length > 0) {
            if (addedCount > 0 && removedCount > 0) {
              toastStore.info(`Marketplace updated: ${addedCount} new, ${removedCount} sold/removed`, 3000);
            } else if (addedCount > 0) {
              toastStore.info(`${addedCount} new mAIner${addedCount > 1 ? 's' : ''} listed!`, 3000);
            } else if (removedCount > 0) {
              toastStore.info(`${removedCount} mAIner${removedCount > 1 ? 's' : ''} sold or removed`, 3000);
            }
          }
        }
        
        listings = newListings;
        lastRefreshTime = Date.now();
      }
    } catch (error) {
      console.error('Error refreshing listings:', error);
    } finally {
      isRefreshing = false;
    }
  }

  // Manual refresh (user clicks refresh button)
  async function manualRefresh() {
    if (isRefreshing || isLoading) return;
    await refreshListings();
  }

  interface MarketplaceListing {
    id: string;
    mainerId: string;
    mainerName: string;
    price: number;
    seller: string;
    listedAt: number;
    status: string;
    isOwnListing: boolean;
    createdAt: number | null;
  }

  $: currentUserPrincipal = $store.principal?.toString();

  onMount(() => {
    loadListings();
    startAutoRefresh();
    
    // Listen for visibility changes to refresh when user returns to tab
    document.addEventListener('visibilitychange', handleVisibilityChange);
  });

  onDestroy(() => {
    stopAutoRefresh();
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  });

  // Reload when user changes
  $: if ($store.principal) {
    loadListings();
  }

  async function loadListings() {
    isLoading = true;
    try {
      const result = await MarketplaceService.getAllListings();
      
      if (result.success && result.listings) {
        // Convert backend listings to frontend format
        listings = result.listings.map(listing => {
          const priceE8s = Number(listing.priceE8S);
          // Use parseFloat with toFixed to avoid floating point display issues
          const priceICP = parseFloat((priceE8s / 100_000_000).toFixed(8));
          const isOwnListing = currentUserPrincipal && 
            listing.listedBy.toString() === currentUserPrincipal;
          
          // Convert timestamp from nanoseconds to milliseconds
          const listedAtMs = Number(listing.listedTimestamp) / 1_000_000;
          
          console.log('📊 Listing Data:', {
            address: listing.address.slice(0, 10) + '...',
            priceE8S: priceE8s,
            priceICP: priceICP,
            listedTimestampRaw: listing.listedTimestamp.toString(),
            listedTimestampMs: listedAtMs,
            listedDate: new Date(listedAtMs).toISOString(),
            nowMs: Date.now(),
            diffMs: Date.now() - listedAtMs,
            diffMinutes: (Date.now() - listedAtMs) / 60000
          });
          
          return {
            id: listing.address, // Use address as unique ID
            mainerId: listing.address,
            mainerName: `mAIner ${listing.address.slice(0, 5)}`,
            price: priceICP,
            seller: listing.listedBy.toString(),
            listedAt: listedAtMs,
            status: 'active',
            isOwnListing,
            createdAt: null,
            priceE8S: priceE8s
          };
        });
        
        console.log(`Loaded ${listings.length} marketplace listings`);
      } else {
        console.error("Failed to load listings:", result.error);
        listings = [];
      }
    } catch (error) {
      console.error("Error loading listings:", error);
      listings = [];
    } finally {
      isLoading = false;
    }
  }

  function handleViewDetails(listing: MarketplaceListing) {
    selectedListing = listing;
    showDetailsModal = true;
  }

  function closeDetailsModal() {
    showDetailsModal = false;
    selectedListing = null;
  }

  async function handleBuy(listing: MarketplaceListing) {
    if (isProcessing) return;
    
    // Pause auto-refresh during purchase to avoid UI changes mid-transaction
    stopAutoRefresh();
    
    try {
      await onBuyMainer(listing.id, listing.mainerId, listing.price);
      closeDetailsModal();
      await loadListings(); // Refresh listings
    } catch (error) {
      console.error("Error buying mAIner:", error);
    } finally {
      // Resume auto-refresh after purchase attempt
      startAutoRefresh();
    }
  }

  async function handleCancelListing(listing: MarketplaceListing) {
    if (isProcessing || cancelingListingId) return;
    
    cancelingListingId = listing.id;
    try {
      await onCancelListing(listing.id, listing.mainerId);
      closeDetailsModal();
      await loadListings(); // Refresh listings
    } catch (error) {
      console.error("Error canceling listing:", error);
    } finally {
      cancelingListingId = null;
    }
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function formatTimeAgo(timestamp: number): string {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    // Debug logging
    console.log('⏰ Time Ago Calculation:', {
      timestamp,
      now,
      diff,
      minutes,
      hours,
      days,
      timestampDate: new Date(timestamp).toISOString()
    });
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  }

  function shortenPrincipal(principal: string): string {
    if (principal.length <= 10) return principal;
    return `${principal.slice(0, 5)}...${principal.slice(-5)}`;
  }

  function formatPrice(price: number): string {
    // Format to 2 decimal places, but remove trailing zeros
    return price.toFixed(8).replace(/\.?0+$/, '');
  }

  $: ownListings = listings.filter(l => l.isOwnListing);
  $: otherListings = listings.filter(l => !l.isOwnListing);
  
  // Apply sorting and pagination to other listings
  $: sortedOtherListings = sortListings(otherListings);
  $: totalPages = Math.ceil(sortedOtherListings.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = Math.min(startIndex + itemsPerPage, sortedOtherListings.length);
  $: paginatedListings = sortedOtherListings.slice(startIndex, endIndex);
  
  // Reset to page 1 if current page exceeds total pages (e.g., after filtering)
  $: if (currentPage > totalPages && totalPages > 0) {
    currentPage = 1;
  }
</script>

<div class="space-y-6">
  <!-- Own Listings Section (if any) -->
  {#if ownListings.length > 0}
    <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
            <Crown class="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-white">My Listings</h2>
            <p class="text-sm text-white/80">Manage your mAIners on sale</p>
          </div>
        </div>
      </div>

      <!-- Own Listings Grid -->
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each ownListings as listing}
            {@const identity = getMainerVisualIdentity(listing.mainerId)}
            
            <div class="group relative overflow-hidden rounded-xl border-2 border-amber-300 dark:border-amber-600 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 shadow-lg hover:shadow-xl transition-all duration-300">
              <!-- Featured Badge -->
              <div class="absolute top-3 right-3 z-10">
                <div class="flex items-center space-x-1 px-2 py-1 bg-amber-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                  <Crown class="w-3 h-3" />
                  <span>YOURS</span>
                </div>
              </div>

              <div class="p-4">
                <!-- mAIner Avatar & Info -->
                <div class="flex items-start space-x-3 mb-4">
                  <div class="w-14 h-14 {identity.colors.accent} backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center border-2 border-white/20">
                    <div class="w-7 h-7 {identity.colors.icon}">
                      {@html identity.icon}
                    </div>
                  </div>
                  
                  <div class="flex-1 min-w-0">
                    <h3 class="font-bold text-gray-900 dark:text-white truncate">🦜 {listing.mainerName}</h3>
                  </div>
                </div>

                <!-- Stats -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">Listed:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">
                      {formatTimeAgo(listing.listedAt)}
                    </span>
                  </div>
                </div>

                <!-- Price & Actions -->
                <div class="border-t border-amber-200 dark:border-amber-700 pt-4">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm text-gray-600 dark:text-gray-400">Price:</span>
                    <span class="text-2xl font-bold text-amber-600 dark:text-amber-400">
                      {formatPrice(listing.price)} ICP
                    </span>
                  </div>
                  
                  <button
                    on:click={() => handleCancelListing(listing)}
                    disabled={isProcessing || cancelingListingId === listing.id}
                    class="w-full px-4 py-2 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {#if cancelingListingId === listing.id}
                      <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full spinner"></div>
                      <span>Canceling...</span>
                    {:else}
                      <X class="w-4 h-4" />
                      <span>Cancel Listing</span>
                    {/if}
                  </button>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}

  <!-- All Marketplace Listings -->
  <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-purple-500 to-blue-500 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
            <ShoppingBag class="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 class="text-xl font-bold text-white">Marketplace Listings</h2>
            <p class="text-sm text-white/80">Browse and purchase mAIners</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <!-- Refresh Button & Status -->
          <button
            on:click={manualRefresh}
            disabled={isRefreshing || isLoading}
            class="flex items-center space-x-1.5 px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Refresh listings"
          >
            <RefreshCw class="w-4 h-4 text-white {isRefreshing ? 'animate-spin' : ''}" />
            <span class="text-xs text-white/90">
              {isRefreshing ? 'Updating...' : 'Refresh'}
            </span>
          </button>
          
          <!-- Live indicator -->
          <div class="flex items-center space-x-1.5" title="Auto-refreshes every 15 seconds">
            <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-xs text-white/80">Live</span>
          </div>
          
          <div class="text-right">
            <p class="text-2xl font-bold text-white">{otherListings.length}</p>
            <p class="text-xs text-white/80">Available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Sorting & Pagination Controls -->
    {#if !isLoading && otherListings.length > 0}
      <div class="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <!-- Sort controls -->
          <div class="flex items-center space-x-3">
            <label for="sort-select" class="text-sm text-gray-600 dark:text-gray-400">Sort by:</label>
            <div class="relative">
              <select
                id="sort-select"
                value={sortBy}
                on:change={handleSortChange}
                disabled={isSorting}
                class="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white disabled:opacity-70 disabled:cursor-wait pr-8"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
              </select>
              {#if isSorting}
                <div class="absolute right-2 top-1/2 -translate-y-1/2">
                  <div class="w-4 h-4 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Items per page -->
          <div class="flex items-center space-x-3">
            <label for="items-per-page" class="text-sm text-gray-600 dark:text-gray-400">Show:</label>
            <select
              id="items-per-page"
              value={itemsPerPage}
              on:change={handleItemsPerPageChange}
              class="px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white"
            >
              {#each itemsPerPageOptions as option}
                <option value={option}>{option} per page</option>
              {/each}
            </select>
          </div>
          
          <!-- Page info -->
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Showing <span class="font-semibold text-gray-900 dark:text-white">{startIndex + 1}-{endIndex}</span> of <span class="font-semibold text-gray-900 dark:text-white">{sortedOtherListings.length}</span>
          </div>
        </div>
      </div>
    {/if}

    <!-- Listings Content -->
    <div class="p-6">
      {#if isLoading}
        <div class="flex items-center justify-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      {:else if otherListings.length === 0}
        <div class="text-center py-12">
          <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <ShoppingBag class="w-8 h-8 text-gray-400" />
          </div>
          <p class="text-gray-600 dark:text-gray-400 mb-2">No listings available</p>
          <p class="text-sm text-gray-500 dark:text-gray-500">Check back later for new mAIners</p>
        </div>
      {:else}
        <!-- Listings Grid -->
        <div class="relative">
          {#if isSorting}
            <div class="absolute inset-0 bg-white/50 dark:bg-gray-900/50 backdrop-blur-[1px] z-10 flex items-center justify-center rounded-lg">
              <div class="flex items-center space-x-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
                <div class="w-5 h-5 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Sorting...</span>
              </div>
            </div>
          {/if}
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each paginatedListings as listing}
            {@const identity = getMainerVisualIdentity(listing.mainerId)}
            
            <div class="group relative overflow-hidden rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-purple-300 dark:hover:border-purple-600 shadow-lg hover:shadow-xl transition-all duration-300">
              <!-- Background gradient -->
              <div class="absolute inset-0 bg-gradient-to-br {identity.colors.bg} opacity-5"></div>
              
              <div class="relative p-5">
                <!-- mAIner Avatar & Info -->
                <div class="flex items-start space-x-3 mb-4">
                  <div class="w-14 h-14 {identity.colors.accent} backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center border-2 border-white/20">
                    <div class="w-7 h-7 {identity.colors.icon}">
                      {@html identity.icon}
                    </div>
                  </div>
                  
                  <div class="flex-1 min-w-0">
                    <h3 class="font-bold text-gray-900 dark:text-white truncate">🦜 {listing.mainerName}</h3>
                  </div>
                </div>

                <!-- Stats Grid -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">Seller:</span>
                    <span class="font-mono text-xs text-gray-700 dark:text-gray-300">
                      {shortenPrincipal(listing.seller)}
                    </span>
                  </div>
                </div>

                <!-- Price & Actions -->
                <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-1 text-sm text-gray-600 dark:text-gray-400">
                      <Tag class="w-4 h-4" />
                      <span>Price:</span>
                    </div>
                    <span class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                      {formatPrice(listing.price)} ICP
                    </span>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      on:click={() => handleViewDetails(listing)}
                      class="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold rounded-lg transition-all duration-200 flex items-center justify-center space-x-1.5"
                    >
                      <Eye class="w-4 h-4" />
                      <span>Details</span>
                    </button>
                    
                    <button
                      on:click={() => $store.isAuthed ? handleBuy(listing) : toggleModal()}
                      disabled={isProcessing}
                      class="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
                      title={!$store.isAuthed ? 'Please connect your wallet to purchase' : ''}
                    >
                      {#if $store.isAuthed}
                        <ShoppingBag class="w-4 h-4" />
                        <span>Buy</span>
                      {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                        </svg>
                        <span>Connect Wallet</span>
                      {/if}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            {/each}
          </div>
        </div>
        
        <!-- Pagination Controls -->
        {#if totalPages > 1}
          <div class="mt-8 flex flex-wrap items-center justify-center gap-2">
            <!-- Previous Button -->
            <button
              on:click={prevPage}
              disabled={currentPage === 1}
              class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous</span>
            </button>
            
            <!-- Page Numbers -->
            <div class="flex items-center space-x-1">
              {#if totalPages <= 7}
                <!-- Show all pages if 7 or fewer -->
                {#each Array(totalPages) as _, i}
                  <button
                    on:click={() => goToPage(i + 1)}
                    class="w-10 h-10 rounded-lg font-medium transition-colors {currentPage === i + 1 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                  >
                    {i + 1}
                  </button>
                {/each}
              {:else}
                <!-- Show abbreviated pagination for many pages -->
                <!-- First page -->
                <button
                  on:click={() => goToPage(1)}
                  class="w-10 h-10 rounded-lg font-medium transition-colors {currentPage === 1 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                >
                  1
                </button>
                
                {#if currentPage > 3}
                  <span class="px-2 text-gray-500">...</span>
                {/if}
                
                <!-- Pages around current -->
                {#each Array(5) as _, i}
                  {@const pageNum = Math.max(2, Math.min(currentPage - 2 + i, totalPages - 1))}
                  {#if pageNum > 1 && pageNum < totalPages && (currentPage <= 3 ? pageNum <= 5 : currentPage >= totalPages - 2 ? pageNum >= totalPages - 4 : Math.abs(pageNum - currentPage) <= 2)}
                    <button
                      on:click={() => goToPage(pageNum)}
                      class="w-10 h-10 rounded-lg font-medium transition-colors {currentPage === pageNum 
                        ? 'bg-purple-600 text-white' 
                        : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                    >
                      {pageNum}
                    </button>
                  {/if}
                {/each}
                
                {#if currentPage < totalPages - 2}
                  <span class="px-2 text-gray-500">...</span>
                {/if}
                
                <!-- Last page -->
                <button
                  on:click={() => goToPage(totalPages)}
                  class="w-10 h-10 rounded-lg font-medium transition-colors {currentPage === totalPages 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
                >
                  {totalPages}
                </button>
              {/if}
            </div>
            
            <!-- Next Button -->
            <button
              on:click={nextPage}
              disabled={currentPage === totalPages}
              class="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
            >
              <span>Next</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
          
          <!-- Page Jump (for many pages) -->
          {#if totalPages > 10}
            <div class="mt-4 flex items-center justify-center space-x-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">Go to page:</span>
              <input
                type="number"
                min="1"
                max={totalPages}
                value={currentPage}
                on:change={(e) => goToPage(parseInt(e.currentTarget.value) || 1)}
                class="w-20 px-3 py-1.5 text-sm bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white text-center"
              />
              <span class="text-sm text-gray-600 dark:text-gray-400">of {totalPages}</span>
            </div>
          {/if}
        {/if}
      {/if}
    </div>
  </div>
</div>

<!-- Details Modal -->
  {#if showDetailsModal && selectedListing}
  {@const identity = getMainerVisualIdentity(selectedListing.mainerId)}
  
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div 
      class="absolute inset-0 bg-black/60 backdrop-blur-md"
      on:click={closeDetailsModal}
      role="button"
      tabindex="-1"
    ></div>
    
    <!-- Modal Content -->
    <div class="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
      <!-- Header -->
      <div class="sticky top-0 bg-gradient-to-r {identity.colors.bg} px-6 py-4 border-b border-gray-200 dark:border-gray-700 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 {identity.colors.accent} backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center border-2 border-white/20">
              <div class="w-6 h-6 {identity.colors.icon}">
                {@html identity.icon}
              </div>
            </div>
            <div>
              <h3 class="text-xl font-bold {identity.colors.text}">🦜 {selectedListing.mainerName}</h3>
              <p class="text-sm {identity.colors.text} opacity-75">mAIner Details</p>
            </div>
          </div>
          
          <button
            on:click={closeDetailsModal}
            class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/20 transition-colors"
          >
            <X class="w-5 h-5 {identity.colors.text}" />
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="p-6 space-y-6">
        <!-- Price Section -->
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
          <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Listed Price</p>
            <p class="text-4xl font-bold text-purple-600 dark:text-purple-400 mb-1">
              {selectedListing.price} ICP
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-500">
              Listed {formatTimeAgo(selectedListing.listedAt)}
            </p>
          </div>
        </div>

        <!-- Details Grid -->
        <div class="grid grid-cols-1 gap-4">
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Status</p>
            <p class="font-semibold text-gray-900 dark:text-white capitalize">{selectedListing.status}</p>
          </div>
        </div>

        <!-- Seller Info -->
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">Seller Principal</p>
          <p class="font-mono text-sm text-gray-900 dark:text-white break-all">
            {selectedListing.seller}
          </p>
        </div>

        <!-- Actions -->
        {#if selectedListing.isOwnListing}
          <button
            on:click={() => handleCancelListing(selectedListing)}
            disabled={isProcessing || cancelingListingId === selectedListing.id}
            class="w-full px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {#if isProcessing || cancelingListingId === selectedListing.id}
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full spinner"></div>
              <span>Canceling...</span>
            {:else}
              <X class="w-5 h-5" />
              <span>Cancel Listing</span>
            {/if}
          </button>
        {:else}
          <button
            on:click={() => handleBuy(selectedListing)}
            disabled={isProcessing || !$store.isAuthed}
            class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
          >
            {#if !$store.isAuthed}
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>Connect Wallet to Purchase</span>
            {:else if isProcessing}
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            {:else}
              <ShoppingBag class="w-5 h-5" />
              <span>Buy Now for {formatPrice(selectedListing.price)} ICP</span>
            {/if}
          </button>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- Connect Wallet Modal -->
{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}

<style>
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }

  /* Modal scroll */
  .overflow-y-auto::-webkit-scrollbar {
    width: 8px;
  }

  .overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
  }

  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: rgba(156, 163, 175, 0.5);
    border-radius: 4px;
  }

  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(156, 163, 175, 0.7);
  }
</style>

