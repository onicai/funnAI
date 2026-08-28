<script lang="ts">
  import { store } from "../../stores/store";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { Crown, X } from "@lucide/svelte";
  import { MarketplaceService } from "../../helpers/marketplaceService";

  export let onCancelListing: (listingId: string, mainerId: string) => Promise<void>;
  export let isProcessing: boolean = false;
  /** Bump from parent after list/cancel so this section reloads. */
  export let refreshKey: number = 0;

  type ActiveListing = {
    id: string;
    mainerId: string;
    mainerName: string;
    price: number;
    listedAt: number;
  };

  let listings: ActiveListing[] = [];
  let isLoading = false;
  let cancelingListingId: string | null = null;
  let lastLoadKey = "";

  $: loadKey = `${$store.isAuthed ? "1" : "0"}:${refreshKey}`;
  $: if (loadKey !== lastLoadKey) {
    lastLoadKey = loadKey;
    if ($store.isAuthed) {
      loadListings();
    } else {
      listings = [];
    }
  }

  async function loadListings() {
    if (!$store.isAuthed) {
      listings = [];
      return;
    }

    isLoading = true;
    try {
      const result = await MarketplaceService.getUserListings();
      if (result.success && result.listings) {
        listings = result.listings.map((listing: any) => {
          const priceE8s = Number(listing.priceE8S);
          const listedAtMs = Number(listing.listedTimestamp) / 1_000_000;
          return {
            id: listing.address,
            mainerId: listing.address,
            mainerName: `mAIner ${listing.address.slice(0, 5)}`,
            price: parseFloat((priceE8s / 100_000_000).toFixed(8)),
            listedAt: listedAtMs,
          };
        });
      }
    } catch (error) {
      console.error("Error loading active listings:", error);
    } finally {
      isLoading = false;
    }
  }

  async function handleCancelListing(listing: ActiveListing) {
    if (isProcessing || cancelingListingId) return;

    cancelingListingId = listing.id;
    try {
      await onCancelListing(listing.id, listing.mainerId);
      listings = listings.filter((l) => l.id !== listing.id);
    } catch (error) {
      console.error("Error canceling listing:", error);
    } finally {
      cancelingListingId = null;
    }
  }

  function formatTimeAgo(timestamp: number): string {
    const diff = Date.now() - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return "Just now";
  }

  function formatPrice(price: number): string {
    return price.toFixed(8).replace(/\.?0+$/, "");
  }
</script>

{#if $store.isAuthed && (isLoading || listings.length > 0)}
  <div class="agent-card">
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

    <div class="p-6">
      {#if isLoading && listings.length === 0}
        <div class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-400"></div>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each listings as listing (listing.id)}
            {@const identity = getMainerVisualIdentity(listing.mainerId)}

            <div class="group relative overflow-hidden rounded-xl border border-amber-500/25 bg-white/3 hover:border-amber-500/40 transition-all duration-300">
              <div class="absolute inset-0 bg-linear-to-br {identity.colors.bg} opacity-[0.04]"></div>

              <div class="absolute top-3 right-3 z-10">
                <div class="flex items-center space-x-1 px-2 py-1 bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-medium rounded-full">
                  <Crown class="w-3 h-3" />
                  <span>YOURS</span>
                </div>
              </div>

              <div class="relative p-4">
                <div class="flex items-start space-x-3 mb-4">
                  <div class="w-14 h-14 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
                    {@html identity.icon}
                  </div>
                  <div class="flex-1 min-w-0 pr-20">
                    <h3 class="font-semibold text-white truncate">{listing.mainerName}</h3>
                  </div>
                </div>

                <div class="space-y-2 mb-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-400">Listed:</span>
                    <span class="font-medium text-gray-200">
                      {formatTimeAgo(listing.listedAt)}
                    </span>
                  </div>
                </div>

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
      {/if}
    </div>
  </div>
{/if}
