<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../stores/store";
  import Footer from "../components/funnai/Footer.svelte";
  import MyMainersForSale from "../components/marketplace/MyMainersForSale.svelte";
  import MarketplaceListings from "../components/marketplace/MarketplaceListings.svelte";
  import { Store, TrendingUp, Users, Zap } from "lucide-svelte";

  let isLoading = true;
  let activeTab: 'sell' | 'buy' = 'buy';
  let stats = {
    totalListings: 0,
    totalVolume: "0",
    activeTraders: 0,
  };

  onMount(() => {
    initialize();
  });

  async function initialize() {
    isLoading = true;
    try {
      await loadMarketplaceStats();
    } catch (error) {
      console.error("Error initializing marketplace:", error);
    } finally {
      isLoading = false;
    }
  }

  async function loadMarketplaceStats() {
    // TODO: Replace with actual backend call
    // const result = await $store.gameStateCanisterActor.getMarketplaceStats();
    
    // Mock data for now
    stats = {
      totalListings: 12,
      totalVolume: "45.5",
      activeTraders: 28,
    };
  }

  async function handleListToMarketplace(mainerIds: string[], prices: Record<string, number>) {
    console.log("Listing mAIners to marketplace:", mainerIds, prices);
    
    try {
      // TODO: Implement actual backend call
      // for (const mainerId of mainerIds) {
      //   const price = prices[mainerId];
      //   await $store.gameStateCanisterActor.listMainerOnMarketplace(mainerId, price);
      // }
      
      // For now, just show success
      alert(`Successfully listed ${mainerIds.length} mAIner(s) to marketplace!`);
      
      // Refresh marketplace data
      await loadMarketplaceStats();
    } catch (error) {
      console.error("Error listing mAIners:", error);
      alert("Failed to list mAIners. Please try again.");
      throw error;
    }
  }

  async function handleBuyMainer(listingId: string, mainerId: string, price: number) {
    console.log("Buying mAIner:", listingId, mainerId, price);
    
    try {
      // TODO: Implement actual backend call
      // await $store.gameStateCanisterActor.buyMainerFromMarketplace(listingId);
      
      // For now, just show success
      alert(`Successfully purchased mAIner for ${price} ICP!`);
      
      // Refresh marketplace data
      await loadMarketplaceStats();
    } catch (error) {
      console.error("Error buying mAIner:", error);
      alert("Failed to purchase mAIner. Please try again.");
      throw error;
    }
  }

  async function handleCancelListing(listingId: string) {
    console.log("Canceling listing:", listingId);
    
    try {
      // TODO: Implement actual backend call
      // await $store.gameStateCanisterActor.cancelMarketplaceListing(listingId);
      
      // For now, just show success
      alert("Successfully canceled listing!");
      
      // Refresh marketplace data
      await loadMarketplaceStats();
    } catch (error) {
      console.error("Error canceling listing:", error);
      alert("Failed to cancel listing. Please try again.");
      throw error;
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20">
  <div class="container mx-auto px-4 py-8">
    <!-- Header Section -->
    <div class="mb-8">
      <div class="flex items-center space-x-4 mb-4">
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

      <!-- Stats Cards -->
      {#if !isLoading}
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <Store class="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Listings</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalListings}</p>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <TrendingUp class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p class="text-sm text-gray-600 dark:text-gray-400">Total Volume</p>
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
                <p class="text-sm text-gray-600 dark:text-gray-400">Active Traders</p>
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
      <!-- Tab Navigation -->
      <div class="mb-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-1 inline-flex shadow-sm">
          <button
            on:click={() => activeTab = 'buy'}
            class="px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 flex items-center space-x-2
                   {activeTab === 'buy' 
                     ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md' 
                     : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}"
          >
            <Store class="w-4 h-4" />
            <span>Browse Marketplace</span>
          </button>
          
          <button
            on:click={() => activeTab = 'sell'}
            class="px-6 py-2.5 rounded-lg font-semibold transition-all duration-200 flex items-center space-x-2
                   {activeTab === 'sell' 
                     ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md' 
                     : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'}"
          >
            <Zap class="w-4 h-4" />
            <span>Sell My mAIners</span>
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      {#if activeTab === 'sell'}
        <MyMainersForSale onListToMarketplace={handleListToMarketplace} />
      {:else}
        <MarketplaceListings 
          onBuyMainer={handleBuyMainer}
          onCancelListing={handleCancelListing}
        />
      {/if}
    {/if}
  </div>

  <Footer />
</div>

