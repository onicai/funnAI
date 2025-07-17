<script lang="ts">
  import LoginModal from '../login/LoginModal.svelte';
  import { store } from "../../stores/store";
  import { WalletDataService } from "../../helpers/WalletDataService";

  let modalIsOpen = false;
  let isRefreshingBalances = false;
  let copySuccess = false;
  let showFullPrincipal = false;

  // Function to refresh wallet balances
  async function getWalletBalances() {
    if (!$store.principal || !$store.isAuthed) {
      console.log('No wallet connected to refresh balances');
      return;
    }

    if (isRefreshingBalances) {
      console.log('Balance refresh already in progress');
      return;
    }

    isRefreshingBalances = true;
    console.log('Refreshing wallet balances...');
    
    try {
      // Force refresh balances using WalletDataService
      await WalletDataService.refreshBalances(true);
      console.log('Wallet balances refreshed successfully');
    } catch (error) {
      console.error('Error refreshing wallet balances:', error);
    } finally {
      isRefreshingBalances = false;
    }
  }

  async function disconnect() {
    await store.disconnect();
  }

  function connect() {
    toggleModal();
  }

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  // Function to copy principal ID to clipboard
  async function copyPrincipalId() {
    if (!$store.principal) return;
    
    try {
      await navigator.clipboard.writeText($store.principal.toString());
      copySuccess = true;
      setTimeout(() => {
        copySuccess = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy principal ID:', err);
    }
  }

  // Function to truncate principal ID from the middle for display
  function truncatePrincipal(principal: string, maxLength: number = 30): string {
    if (principal.length <= maxLength) return principal;
    
    const start = Math.floor((maxLength - 3) / 2);
    const end = Math.ceil((maxLength - 3) / 2);
    
    return principal.slice(0, start) + '...' + principal.slice(-end);
  }
</script>

<div class="w-full bg-white dark:bg-gray-800 p-6 rounded-lg">
  <div class="flex items-center justify-between mb-6">
    <h2 class="text-xl font-semibold dark:text-white flex items-center gap-2">
      <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
      </svg>
      Wallet Status
    </h2>
    
    <!-- Connection Status Badge -->
    <div class="flex items-center gap-2">
      {#if $store.isAuthed}
        <div class="flex items-center gap-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-3 py-1.5 rounded-full text-sm font-medium">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          Connected
        </div>
      {:else}
        <div class="flex items-center gap-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-3 py-1.5 rounded-full text-sm font-medium">
          <div class="w-2 h-2 bg-red-500 rounded-full"></div>
          Disconnected
        </div>
      {/if}
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:items-start">
    <!-- Principal ID Section -->
    <div class="space-y-3">
      <div class="flex items-center justify-between min-h-[24px]">
        <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Principal ID</label>
        {#if $store.principal}
          <button
            on:click={copyPrincipalId}
            class="flex items-center gap-1.5 text-xs text-gray-500 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
            title={copySuccess ? "Copied!" : "Copy to clipboard"}
          >
            {#if copySuccess}
              <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              Copied!
            {:else}
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              Copy
            {/if}
          </button>
        {/if}
      </div>
      
      <div class="relative">
        {#if $store.principal}
          <div class="bg-gray-50 dark:bg-gray-700/50 border dark:border-gray-600 rounded-lg p-3 font-mono text-xs">
            <!-- Mobile: Show truncated with option to expand -->
            <div class="block lg:hidden">
              {#if showFullPrincipal}
                <div class="break-all text-gray-700 dark:text-gray-300 leading-relaxed">
                  {$store.principal.toString()}
                </div>
                <button
                  on:click={() => showFullPrincipal = false}
                  class="text-xs text-purple-600 dark:text-purple-400 mt-2 hover:underline"
                >
                  Show less
                </button>
              {:else}
                <div class="text-gray-700 dark:text-gray-300">
                  {truncatePrincipal($store.principal.toString(), 24)}
                </div>
                <button
                  on:click={() => showFullPrincipal = true}
                  class="text-xs text-purple-600 dark:text-purple-400 mt-1 hover:underline"
                >
                  Show full
                </button>
              {/if}
            </div>
            
            <!-- Desktop: Show full address with smaller font -->
            <div 
              class="hidden lg:block text-gray-700 dark:text-gray-300 cursor-help leading-relaxed"
              title="Click copy button to copy full address"
            >
              {$store.principal.toString()}
            </div>
          </div>
        {:else}
          <div class="bg-gray-50 dark:bg-gray-700/50 border dark:border-gray-600 rounded-lg p-3 text-gray-500 dark:text-gray-400 italic">
            Not connected
          </div>
        {/if}
      </div>
    </div>

    <!-- Wallet Actions Section -->
    <div class="space-y-3">
      <div class="flex items-center min-h-[24px]">
        <label class="text-sm font-medium text-gray-600 dark:text-gray-400">Actions</label>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-3">
        {#if $store.isAuthed}
          <button
            on:click={getWalletBalances}
            disabled={isRefreshingBalances}
            class="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-medium rounded-lg px-4 py-2.5 transition-colors disabled:cursor-not-allowed flex-1 sm:flex-initial"
          >
            {#if isRefreshingBalances}
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Refreshing...
            {:else}
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Refresh Balances
            {/if}
          </button>
          
          <button
            on:click={disconnect}
            class="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg px-4 py-2.5 transition-colors flex-1 sm:flex-initial"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
            </svg>
            Disconnect
          </button>
        {:else}
          <button
            on:click={connect}
            class="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-lg px-6 py-3 transition-colors w-full"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            Connect Wallet
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if} 