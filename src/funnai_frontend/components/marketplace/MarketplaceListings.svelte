<script lang="ts">
  import { store } from "../../stores/store";
  import { toastStore } from "../../stores/toastStore";
  import { onMount, onDestroy } from "svelte";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { ShoppingBag, Crown, X, Eye, Tag, RefreshCw } from "@lucide/svelte";
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

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

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
        }).sort((a, b) => a.price - b.price); // Sort by price low to high
        
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

  let listingsLoadGeneration = 0;
  let lastListingsPrincipalKey: string | null | undefined = undefined;

  onMount(() => {
    startAutoRefresh();
    
    // Listen for visibility changes to refresh when user returns to tab
    document.addEventListener('visibilitychange', handleVisibilityChange);
  });

  onDestroy(() => {
    stopAutoRefresh();
    document.removeEventListener('visibilitychange', handleVisibilityChange);
  });

  // Reload only when the signed-in principal actually changes.
  // `$store` updates constantly during login/mainer enrich; reacting to the
  // whole store was re-running a full spinner load for ~30s after connect.
  $: listingsPrincipalKey = $store.principal?.toString() ?? null;
  $: if (listingsPrincipalKey !== lastListingsPrincipalKey) {
    const soft = lastListingsPrincipalKey !== undefined && listings.length > 0;
    lastListingsPrincipalKey = listingsPrincipalKey;
    loadListings({ soft });
  }

  async function loadListings(options: { soft?: boolean } = {}) {
    const soft = Boolean(options.soft);
    const generation = ++listingsLoadGeneration;

    if (soft) {
      isRefreshing = true;
    } else {
      isLoading = true;
    }

    try {
      const result = await MarketplaceService.getAllListings();
      if (generation !== listingsLoadGeneration) return;
      
      if (result.success && result.listings) {
        // Convert backend listings to frontend format
        const convertedListings = result.listings.map(listing => {
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

        // Sort by price low to high by default
        listings = convertedListings.sort((a, b) => a.price - b.price);
        
        console.log(`Loaded ${listings.length} marketplace listings`);
      } else {
        console.error("Failed to load listings:", result.error);
        // Keep last-known cards on a soft refresh so login churn doesn't blank the grid
        if (!soft) {
          listings = [];
        }
      }
    } catch (error) {
      console.error("Error loading listings:", error);
      if (!soft) {
        listings = [];
      }
    } finally {
      if (generation === listingsLoadGeneration) {
        isLoading = false;
        isRefreshing = false;
        lastRefreshTime = Date.now();
      }
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
    if (isProcessing || listing.isOwnListing) return;
    
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

  $: ownListings = listings
    .filter(l => !!(currentUserPrincipal && l.seller === currentUserPrincipal))
    .map(l => ({ ...l, isOwnListing: true }));
  $: otherListings = listings
    .filter(l => !(currentUserPrincipal && l.seller === currentUserPrincipal))
    .map(l => ({ ...l, isOwnListing: false }));
  $: browseListings = [...ownListings, ...otherListings];
  
  $: totalPages = Math.ceil(browseListings.length / itemsPerPage);
  $: startIndex = (currentPage - 1) * itemsPerPage;
  $: endIndex = Math.min(startIndex + itemsPerPage, browseListings.length);
  $: paginatedListings = browseListings.slice(startIndex, endIndex);
  
  // Reset to page 1 if current page exceeds total pages (e.g., after filtering)
  $: if (currentPage > totalPages && totalPages > 0) {
    currentPage = 1;
  }

  // Generate page numbers for pagination (simple, no duplicates)
  function getPageNumbers(current: number, total: number): (number | 'ellipsis')[] {
    if (total <= 7) {
      // Show all pages if 7 or fewer
      return Array.from({ length: total }, (_, i) => i + 1);
    }

    const pages: (number | 'ellipsis')[] = [];
    
    // Always show first page
    pages.push(1);
    
    // Calculate range around current page
    let rangeStart = Math.max(2, current - 1);
    let rangeEnd = Math.min(total - 1, current + 1);
    
    // Adjust range to always show 3 middle numbers when possible
    if (current <= 3) {
      rangeStart = 2;
      rangeEnd = Math.min(total - 1, 4);
    } else if (current >= total - 2) {
      rangeStart = Math.max(2, total - 3);
      rangeEnd = total - 1;
    }
    
    // Add ellipsis before range if needed
    if (rangeStart > 2) {
      pages.push('ellipsis');
    }
    
    // Add range pages
    for (let i = rangeStart; i <= rangeEnd; i++) {
      pages.push(i);
    }
    
    // Add ellipsis after range if needed
    if (rangeEnd < total - 1) {
      pages.push('ellipsis');
    }
    
    // Always show last page
    pages.push(total);
    
    return pages;
  }

  $: pageNumbers = getPageNumbers(currentPage, totalPages);
</script>

<div class="space-y-6">
  <!-- Own Listings Section (if any) -->
  {#if ownListings.length > 0}
    <div class="agent-card">
      <!-- Header -->
      <div class="border-b border-white/8 px-6 py-4">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Crown class="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <p class="agent-eyebrow">Yours</p>
            <h2 class="text-lg font-semibold tracking-tight text-white">My Listings</h2>
            <p class="text-sm text-gray-400">Manage your mAIners on sale</p>
          </div>
        </div>
      </div>

      <!-- Own Listings Grid -->
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each ownListings as listing (listing.id)}
            {@const identity = getMainerVisualIdentity(listing.mainerId)}

            <div class="group relative overflow-hidden rounded-xl border border-amber-500/25 bg-white/3 hover:border-amber-500/40 transition-all duration-300">
              <!-- Soft identity tint -->
              <div class="absolute inset-0 bg-linear-to-br {identity.colors.bg} opacity-[0.04]"></div>

              <!-- Featured Badge -->
              <div class="absolute top-3 right-3 z-10">
                <div class="flex items-center space-x-1 px-2 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-medium rounded-full">
                  <Crown class="w-3 h-3" />
                  <span>YOURS</span>
                </div>
              </div>

              <div class="relative p-4">
                <!-- mAIner Avatar & Info -->
                <div class="flex items-start space-x-3 mb-4">
                  <div class="w-14 h-14 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
                    {@html identity.icon}
                  </div>

                  <div class="flex-1 min-w-0 pr-20">
                    <h3 class="font-semibold text-white truncate">{listing.mainerName}</h3>
                  </div>
                </div>

                <!-- Stats -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-400">Listed:</span>
                    <span class="font-medium text-gray-200">
                      {formatTimeAgo(listing.listedAt)}
                    </span>
                  </div>
                </div>

                <!-- Price & Actions -->
                <div class="border-t border-white/10 pt-4">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm text-gray-400">Price:</span>
                    <span class="text-2xl font-semibold text-amber-400">
                      {formatPrice(listing.price)} ICP
                    </span>
                  </div>

                  <button
                    on:click={() => handleCancelListing(listing)}
                    disabled={isProcessing || cancelingListingId === listing.id}
                    class="w-full agent-btn-ghost border-red-500/30 text-red-300 hover:border-red-500/50 hover:bg-red-500/10 hover:text-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {#if cancelingListingId === listing.id}
                      <div class="w-4 h-4 border-2 border-red-300 border-t-transparent rounded-full spinner"></div>
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
  <div class="agent-card">
    <!-- Header -->
    <div class="border-b border-white/8 px-6 py-4">
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
            <ShoppingBag class="w-5 h-5 text-agent-purple" />
          </div>
          <div>
            <p class="agent-eyebrow">Browse</p>
            <h2 class="text-lg font-semibold tracking-tight text-white">Marketplace Listings</h2>
            <p class="text-sm text-gray-400">
              {#if ownListings.length > 0}
                Your mAIners show here too — tagged, and not for you to buy
              {:else}
                Browse and purchase mAIners
              {/if}
            </p>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <!-- Refresh Button & Status -->
          <button
            on:click={manualRefresh}
            disabled={isRefreshing || isLoading}
            class="agent-btn-ghost disabled:opacity-50 disabled:cursor-not-allowed"
            title="Refresh listings"
          >
            <RefreshCw class="w-4 h-4 {isRefreshing ? 'animate-spin' : ''}" />
            <span class="text-xs">
              {isRefreshing ? 'Updating...' : 'Refresh'}
            </span>
          </button>

          <!-- Live indicator -->
          <div class="flex items-center space-x-1.5" title="Auto-refreshes every 15 seconds">
            <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            <span class="text-xs text-gray-400">Live</span>
          </div>

          <div class="text-right">
            <p class="text-2xl font-semibold text-white">{listings.length}</p>
            <p class="text-xs text-gray-400">
              Listed{ownListings.length > 0 ? ` · ${ownListings.length} yours` : ''}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Sorting & Pagination Controls -->
    {#if !isLoading && browseListings.length > 0}
      <div class="px-6 py-3 border-b border-white/8 bg-white/2">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <!-- Sort controls - removed -->
          
          <!-- Items per page -->
          <div class="flex items-center space-x-3">
            <label for="items-per-page" class="text-sm text-gray-400">Show:</label>
            <select
              id="items-per-page"
              value={itemsPerPage}
              on:change={handleItemsPerPageChange}
              class="agent-input w-auto py-1.5"
            >
              {#each itemsPerPageOptions as option}
                <option value={option}>{option} per page</option>
              {/each}
            </select>
          </div>
          
          <!-- Page info -->
          <div class="text-sm text-gray-400">
            Showing <span class="font-medium text-white">{startIndex + 1}-{endIndex}</span> of <span class="font-medium text-white">{browseListings.length}</span>
          </div>
        </div>
      </div>
    {/if}

    <!-- Listings Content -->
    <div class="p-6">
      {#if isLoading}
        <div class="flex items-center justify-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-agent-purple"></div>
        </div>
      {:else if browseListings.length === 0}
        <div class="text-center py-12">
          <ShoppingBag class="w-8 h-8 text-gray-500 mx-auto mb-4" />
          <p class="text-gray-400 mb-2">No listings available</p>
          <p class="text-sm text-gray-500">Check back later for new mAIners</p>
        </div>
      {:else}
        <!-- Listings Grid -->
        <div class="relative">
          <!-- Sorting overlay removed -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each paginatedListings as listing (listing.id)}
            {@const identity = getMainerVisualIdentity(listing.mainerId)}
            
            <div class="group relative overflow-hidden rounded-xl border bg-white/3 transition-all duration-300 {listing.isOwnListing ? 'border-amber-500/30 hover:border-amber-500/50' : 'border-white/10 hover:border-agent-purple/40'}">
              <!-- Soft identity tint -->
              <div class="absolute inset-0 bg-linear-to-br {identity.colors.bg} opacity-[0.04]"></div>

              {#if listing.isOwnListing}
                <div class="absolute top-3 right-3 z-10">
                  <div class="flex items-center space-x-1 px-2 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-medium rounded-full">
                    <Crown class="w-3 h-3" />
                    <span>My mAIner</span>
                  </div>
                </div>
              {/if}
              
              <div class="relative p-5">
                <!-- mAIner Avatar & Info -->
                <div class="flex items-start space-x-3 mb-4">
                  <div class="w-14 h-14 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
                    {@html identity.icon}
                  </div>
                  
                  <div class="flex-1 min-w-0 {listing.isOwnListing ? 'pr-24' : ''}">
                    <h3 class="font-semibold text-white truncate">{listing.mainerName}</h3>
                  </div>
                </div>

                <!-- Stats Grid -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-400">Seller:</span>
                    <span class="font-mono text-xs text-gray-300">
                      {listing.isOwnListing ? 'You' : shortenPrincipal(listing.seller)}
                    </span>
                  </div>
                </div>

                <!-- Price & Actions -->
                <div class="border-t border-white/10 pt-4">
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-1 text-sm text-gray-400">
                      <Tag class="w-4 h-4" />
                      <span>Price:</span>
                    </div>
                    <span class="text-2xl font-semibold {listing.isOwnListing ? 'text-amber-400' : 'text-agent-purple'}">
                      {formatPrice(listing.price)} ICP
                    </span>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      on:click={() => handleViewDetails(listing)}
                      class="agent-btn-ghost w-full"
                    >
                      <Eye class="w-4 h-4" />
                      <span>Details</span>
                    </button>

                    {#if listing.isOwnListing}
                      <button
                        on:click={() => handleCancelListing(listing)}
                        disabled={isProcessing || cancelingListingId === listing.id}
                        class="agent-btn-ghost w-full border-red-500/30 text-red-300 hover:border-red-500/50 hover:bg-red-500/10 hover:text-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        title="You can't buy your own listing"
                      >
                        {#if cancelingListingId === listing.id}
                          <div class="w-4 h-4 border-2 border-red-300 border-t-transparent rounded-full spinner"></div>
                          <span>Canceling...</span>
                        {:else}
                          <X class="w-4 h-4" />
                          <span>Cancel</span>
                        {/if}
                      </button>
                    {:else}
                      <button
                        on:click={() => $store.isAuthed ? handleBuy(listing) : toggleModal()}
                        disabled={isProcessing}
                        class="agent-btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
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
                    {/if}
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
              class="agent-btn-ghost disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous</span>
            </button>
            
            <!-- Page Numbers -->
            <div class="flex items-center space-x-1">
              {#each pageNumbers as item}
                {#if item === 'ellipsis'}
                  <span class="px-2 text-gray-500">...</span>
                {:else}
                  <button
                    on:click={() => goToPage(item)}
                    class="w-10 h-10 rounded-full font-medium transition-colors {currentPage === item 
                      ? 'bg-agent-purple text-white' 
                      : 'border border-white/10 bg-white/3 text-gray-300 hover:border-agent-purple/40 hover:bg-agent-purple/10'}"
                  >
                    {item}
                  </button>
                {/if}
              {/each}
            </div>
            
            <!-- Next Button -->
            <button
              on:click={nextPage}
              disabled={currentPage === totalPages}
              class="agent-btn-ghost disabled:opacity-50 disabled:cursor-not-allowed"
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
              <span class="text-sm text-gray-400">Go to page:</span>
              <input
                type="number"
                min="1"
                max={totalPages}
                value={currentPage}
                on:change={(e) => goToPage(parseInt(e.currentTarget.value) || 1)}
                class="agent-input w-20 text-center py-1.5"
              />
              <span class="text-sm text-gray-400">of {totalPages}</span>
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
    <div class="relative bg-agent-elevated border border-white/10 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Soft identity tint -->
      <div class="pointer-events-none absolute inset-0 bg-linear-to-br {identity.colors.bg} opacity-[0.04] rounded-2xl"></div>

      <!-- Header -->
      <div class="sticky top-0 bg-agent-elevated/95 backdrop-blur-xs border-b border-white/8 px-6 py-4 z-10">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
              {@html identity.icon}
            </div>
            <div>
              <div class="flex items-center gap-2">
                <p class="agent-eyebrow">Details</p>
                {#if selectedListing.isOwnListing}
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-500/15 border border-amber-500/30 text-amber-300 text-[10px] font-medium rounded-full uppercase tracking-wide">
                    <Crown class="w-3 h-3" />
                    My mAIner
                  </span>
                {/if}
              </div>
              <h3 class="text-lg font-semibold tracking-tight text-white">{selectedListing.mainerName}</h3>
              <p class="text-sm text-gray-400">
                {#if selectedListing.isOwnListing}
                  Your listing
                {:else}
                  mAIner Details
                {/if}
              </p>
            </div>
          </div>
          
          <button
            on:click={closeDetailsModal}
            class="w-8 h-8 flex items-center justify-center rounded-full border border-white/10 bg-white/4 text-gray-300 hover:border-agent-purple/40 hover:text-white transition-colors"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <!-- Content -->
      <div class="relative p-6 space-y-6">
        <!-- Price Section -->
        <div class="bg-white/3 rounded-xl p-6 border border-white/10">
          <div class="text-center">
            <p class="text-sm text-gray-400 mb-2">Listed Price</p>
            <p class="text-4xl font-semibold text-agent-purple mb-1">
              {selectedListing.price} ICP
            </p>
            <p class="text-xs text-gray-500">
              Listed {formatTimeAgo(selectedListing.listedAt)}
            </p>
          </div>
        </div>

        <!-- Details Grid -->
        <div class="grid grid-cols-1 gap-4">
          <div class="bg-white/3 border border-white/10 rounded-xl p-4">
            <p class="text-xs text-gray-400 mb-1">Status</p>
            <p class="font-medium text-white capitalize">{selectedListing.status}</p>
          </div>
        </div>

        <!-- Seller Info -->
        <div class="bg-white/3 border border-white/10 rounded-xl p-4">
          <p class="text-xs text-gray-400 mb-2">Seller Principal</p>
          <p class="font-mono text-sm text-gray-200 break-all">
            {selectedListing.seller}
          </p>
        </div>

        <!-- Actions -->
        {#if selectedListing.isOwnListing}
          <p class="text-sm text-amber-300/90 text-center">This is your mAIner — you can't buy it from yourself.</p>
          <button
            on:click={() => handleCancelListing(selectedListing)}
            disabled={isProcessing || cancelingListingId === selectedListing.id}
            class="w-full agent-btn-ghost border-red-500/30 text-red-300 hover:border-red-500/50 hover:bg-red-500/10 hover:text-red-200 disabled:opacity-50 disabled:cursor-not-allowed h-11"
          >
            {#if isProcessing || cancelingListingId === selectedListing.id}
              <div class="w-5 h-5 border-2 border-red-300 border-t-transparent rounded-full spinner"></div>
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
            class="w-full agent-btn-primary h-11 disabled:opacity-50 disabled:cursor-not-allowed"
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
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
  }

  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(101, 63, 197, 0.5);
  }
</style>

