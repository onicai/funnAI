<script lang="ts">
  import { store } from "../../stores/store";
  import { onMount } from "svelte";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { ShoppingBag, Crown, X, Eye, Tag, TrendingUp, Clock } from "lucide-svelte";
  import { MarketplaceService } from "../../helpers/marketplaceService";
  import { Principal } from '@dfinity/principal';

  export let onBuyMainer: (listingId: string, mainerId: string, price: number) => Promise<void>;
  export let onCancelListing: (listingId: string, mainerId: string) => Promise<void>;
  export let isProcessing: boolean = false;

  let listings: MarketplaceListing[] = [];
  let isLoading = true;
  let selectedListing: MarketplaceListing | null = null;
  let showDetailsModal = false;
  let cancelingListingId: string | null = null; // Track which listing is being canceled

  interface MarketplaceListing {
    id: string;
    mainerId: string;
    mainerName: string;
    price: number;
    seller: string;
    listedAt: number;
    cycleBalance: number;
    mainerType: string;
    status: string;
    isOwnListing: boolean;
    createdAt: number | null;
  }

  $: currentUserPrincipal = $store.principal?.toString();

  onMount(() => {
    loadListings();
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
          const priceICP = priceE8s / 100_000_000;
          const isOwnListing = currentUserPrincipal && 
            listing.listedBy.toString() === currentUserPrincipal;
          
          return {
            id: listing.address, // Use address as unique ID
            mainerId: listing.address,
            mainerName: `mAIner ${listing.address.slice(0, 5)}`,
            price: priceICP,
            seller: listing.listedBy.toString(),
            listedAt: Number(listing.listedTimestamp) / 1_000_000, // Convert from nanoseconds to milliseconds
            cycleBalance: 0, // Will be enriched if available
            mainerType: 'Own' in listing.mainerType ? 'Own' : 'Shared',
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
    
    try {
      await onBuyMainer(listing.id, listing.mainerId, listing.price);
      closeDetailsModal();
      await loadListings(); // Refresh listings
    } catch (error) {
      console.error("Error buying mAIner:", error);
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
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return 'Just now';
  }

  function shortenPrincipal(principal: string): string {
    if (principal.length <= 10) return principal;
    return `${principal.slice(0, 5)}...${principal.slice(-5)}`;
  }

  $: ownListings = listings.filter(l => l.isOwnListing);
  $: otherListings = listings.filter(l => !l.isOwnListing);
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
                    <span class="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                      {listing.mainerType}
                    </span>
                  </div>
                </div>

                <!-- Stats -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400">Cycles:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">
                      {formatLargeNumber(listing.cycleBalance / 1_000_000_000_000, 2, false)} T
                    </span>
                  </div>
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
                      {listing.price} ICP
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
        
        <div class="text-right">
          <p class="text-2xl font-bold text-white">{otherListings.length}</p>
          <p class="text-xs text-white/80">Available</p>
        </div>
      </div>
    </div>

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
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each otherListings as listing}
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
                    <span class="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                      {listing.mainerType}
                    </span>
                  </div>
                </div>

                <!-- Stats Grid -->
                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-600 dark:text-gray-400 flex items-center space-x-1">
                      <TrendingUp class="w-3.5 h-3.5" />
                      <span>Cycles:</span>
                    </span>
                    <span class="font-semibold text-gray-900 dark:text-white">
                      {formatLargeNumber(listing.cycleBalance / 1_000_000_000_000, 2, false)} T
                    </span>
                  </div>
                  {#if listing.createdAt}
                    <div class="flex items-center justify-between text-sm">
                      <span class="text-gray-600 dark:text-gray-400 flex items-center space-x-1">
                        <Clock class="w-3.5 h-3.5" />
                        <span>Created:</span>
                      </span>
                      <span class="font-semibold text-gray-900 dark:text-white">
                        {formatDate(listing.createdAt)}
                      </span>
                    </div>
                  {/if}
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
                      {listing.price} ICP
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
                      on:click={() => handleBuy(listing)}
                      disabled={isProcessing}
                      class="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
                    >
                      <ShoppingBag class="w-4 h-4" />
                      <span>Buy</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
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
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Type</p>
            <p class="font-semibold text-gray-900 dark:text-white">{selectedListing.mainerType}</p>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Status</p>
            <p class="font-semibold text-gray-900 dark:text-white capitalize">{selectedListing.status}</p>
          </div>
          
          <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Cycles Balance</p>
            <p class="font-semibold text-gray-900 dark:text-white">
              {formatLargeNumber(selectedListing.cycleBalance / 1_000_000_000_000, 2, false)} TCYCLES
            </p>
          </div>
          
          {#if selectedListing.createdAt}
            <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Created</p>
              <p class="font-semibold text-gray-900 dark:text-white">
                {formatDate(selectedListing.createdAt)}
              </p>
            </div>
          {/if}
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
            disabled={isProcessing}
            class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
          >
            {#if isProcessing}
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            {:else}
              <ShoppingBag class="w-5 h-5" />
              <span>Buy Now for {selectedListing.price} ICP</span>
            {/if}
          </button>
        {/if}
      </div>
    </div>
  </div>
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

