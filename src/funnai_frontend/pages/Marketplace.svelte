<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../stores/store";
  import Footer from "../components/funnai/Footer.svelte";

  let isLoading = true;

  onMount(() => {
    // Initialize marketplace data
    isLoading = false;
  });
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <div class="container mx-auto px-4 py-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-2">Marketplace</h1>
      <p class="text-lg text-gray-600 dark:text-gray-400">
        Discover and trade digital assets
      </p>
    </div>

    {#if isLoading}
      <div class="flex items-center justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    {:else}
      <!-- Featured Section -->
      <div class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">Featured Items</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Placeholder cards -->
          {#each [1, 2, 3] as item}
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow duration-200">
              <div class="aspect-video bg-gradient-to-br from-purple-400 to-blue-500 flex items-center justify-center">
                <svg class="w-16 h-16 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <div class="p-6">
                <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Item #{item}</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                  Description of the marketplace item goes here.
                </p>
                <div class="flex items-center justify-between">
                  <span class="text-2xl font-bold text-purple-600 dark:text-purple-400">0.5 ICP</span>
                  <button class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors duration-200">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Categories Section -->
      <div class="mb-12">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">Categories</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          {#each ['NFTs', 'Tokens', 'Services', 'Digital Art'] as category}
            <button class="p-6 bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 hover:border-purple-500 dark:hover:border-purple-500 transition-all duration-200 text-center">
              <div class="text-lg font-semibold text-gray-900 dark:text-white">{category}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400 mt-1">Explore</div>
            </button>
          {/each}
        </div>
      </div>

      <!-- Recent Listings -->
      <div>
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">Recent Listings</h2>
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Item</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Price</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Seller</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {#each [1, 2, 3, 4, 5] as item}
                  <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">Item #{item}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-900 dark:text-white font-semibold">0.{item} ICP</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm text-gray-500 dark:text-gray-400">0x1234...5678</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <button class="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 font-medium">
                        View →
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    {/if}
  </div>

  <Footer />
</div>

<style>
  /* Custom scrollbar for table */
  .overflow-x-auto::-webkit-scrollbar {
    height: 8px;
  }

  .overflow-x-auto::-webkit-scrollbar-track {
    background: transparent;
  }

  .overflow-x-auto::-webkit-scrollbar-thumb {
    background: rgba(156, 163, 175, 0.5);
    border-radius: 4px;
  }

  .overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(156, 163, 175, 0.7);
  }

  .dark .overflow-x-auto::-webkit-scrollbar-thumb {
    background: rgba(75, 85, 99, 0.5);
  }

  .dark .overflow-x-auto::-webkit-scrollbar-thumb:hover {
    background: rgba(75, 85, 99, 0.7);
  }
</style>

