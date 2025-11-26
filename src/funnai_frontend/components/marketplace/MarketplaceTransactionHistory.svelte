<script lang="ts">
  import { onMount } from "svelte";
  import { store } from "../../stores/store";
  import { MarketplaceService, type MarketplaceTransaction } from "../../helpers/marketplaceService";
  import { History, ArrowDownLeft, ArrowUpRight, Clock, ExternalLink } from "lucide-svelte";

  // State
  let purchases: MarketplaceTransaction[] = [];
  let sales: MarketplaceTransaction[] = [];
  let isLoading = true;
  let error: string | null = null;
  let activeTab: 'all' | 'purchases' | 'sales' = 'all';

  $: isAuthed = $store.isAuthed;
  $: allTransactions = [...purchases.map(t => ({ ...t, type: 'purchase' as const })), 
                        ...sales.map(t => ({ ...t, type: 'sale' as const }))]
                        .sort((a, b) => b.timestamp - a.timestamp);
  
  $: displayedTransactions = activeTab === 'all' 
    ? allTransactions 
    : activeTab === 'purchases' 
      ? purchases.map(t => ({ ...t, type: 'purchase' as const }))
      : sales.map(t => ({ ...t, type: 'sale' as const }));

  onMount(() => {
    if (isAuthed) {
      loadTransactionHistory();
    }
  });

  $: if (isAuthed) {
    loadTransactionHistory();
  }

  async function loadTransactionHistory() {
    if (!isAuthed) {
      isLoading = false;
      return;
    }

    isLoading = true;
    error = null;

    try {
      const result = await MarketplaceService.getUserTransactionHistory();
      
      if (result.success) {
        purchases = result.purchases || [];
        sales = result.sales || [];
      } else {
        error = result.error || "Failed to load transaction history";
      }
    } catch (e) {
      error = e.message || "An error occurred";
    } finally {
      isLoading = false;
    }
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function formatPrice(priceICP: number): string {
    return priceICP.toFixed(4);
  }

  function truncateAddress(address: string): string {
    if (address.length <= 12) return address;
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  }
</script>

<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
  <!-- Header -->
  <div class="bg-gradient-to-r from-indigo-500 to-purple-500 px-6 py-4">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
        <History class="w-6 h-6 text-white" />
      </div>
      <div>
        <h2 class="text-xl font-bold text-white">Transaction History</h2>
        <p class="text-sm text-white/80">Your marketplace buys and sells</p>
      </div>
    </div>
  </div>

  <!-- Tab Navigation -->
  <div class="border-b border-gray-200 dark:border-gray-700 px-6">
    <div class="flex space-x-1 -mb-px">
      <button
        on:click={() => activeTab = 'all'}
        class="px-4 py-3 text-sm font-medium border-b-2 transition-colors
               {activeTab === 'all' 
                 ? 'border-purple-500 text-purple-600 dark:text-purple-400' 
                 : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
      >
        All ({allTransactions.length})
      </button>
      <button
        on:click={() => activeTab = 'purchases'}
        class="px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5
               {activeTab === 'purchases' 
                 ? 'border-green-500 text-green-600 dark:text-green-400' 
                 : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
      >
        <ArrowDownLeft class="w-4 h-4" />
        Purchases ({purchases.length})
      </button>
      <button
        on:click={() => activeTab = 'sales'}
        class="px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5
               {activeTab === 'sales' 
                 ? 'border-blue-500 text-blue-600 dark:text-blue-400' 
                 : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}"
      >
        <ArrowUpRight class="w-4 h-4" />
        Sales ({sales.length})
      </button>
    </div>
  </div>

  <!-- Content -->
  <div class="p-6">
    {#if !isAuthed}
      <div class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <History class="w-8 h-8 text-gray-400" />
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-2">Connect your wallet</p>
        <p class="text-sm text-gray-500 dark:text-gray-500">Sign in to view your transaction history</p>
      </div>
    {:else if isLoading}
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400">Loading transactions...</p>
        </div>
      </div>
    {:else if error}
      <div class="text-center py-12">
        <div class="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <History class="w-8 h-8 text-red-500" />
        </div>
        <p class="text-red-600 dark:text-red-400 mb-2">Error loading transactions</p>
        <p class="text-sm text-gray-500 dark:text-gray-500">{error}</p>
        <button
          on:click={loadTransactionHistory}
          class="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    {:else if displayedTransactions.length === 0}
      <div class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <History class="w-8 h-8 text-gray-400" />
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-2">No transactions yet</p>
        <p class="text-sm text-gray-500 dark:text-gray-500">
          {#if activeTab === 'purchases'}
            You haven't purchased any mAIners yet
          {:else if activeTab === 'sales'}
            You haven't sold any mAIners yet
          {:else}
            Your marketplace transactions will appear here
          {/if}
        </p>
      </div>
    {:else}
      <!-- Transaction List -->
      <div class="space-y-3">
        {#each displayedTransactions as transaction}
          <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 transition-colors">
            <div class="flex items-center space-x-4">
              <!-- Transaction Type Icon -->
              <div class="w-10 h-10 rounded-full flex items-center justify-center
                          {transaction.type === 'purchase' 
                            ? 'bg-green-100 dark:bg-green-900/30' 
                            : 'bg-blue-100 dark:bg-blue-900/30'}">
                {#if transaction.type === 'purchase'}
                  <ArrowDownLeft class="w-5 h-5 text-green-600 dark:text-green-400" />
                {:else}
                  <ArrowUpRight class="w-5 h-5 text-blue-600 dark:text-blue-400" />
                {/if}
              </div>

              <!-- Transaction Details -->
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-gray-900 dark:text-white">
                    {transaction.type === 'purchase' ? 'Purchased' : 'Sold'}
                  </span>
                  <span class="text-sm font-medium px-2 py-0.5 rounded-full
                              {transaction.type === 'purchase' 
                                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' 
                                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'}">
                    🦜 mAIner {transaction.mainerAddress.slice(0, 5)}
                  </span>
                </div>
                <div class="flex items-center gap-3 mt-1 text-xs text-gray-500 dark:text-gray-400">
                  <span class="flex items-center gap-1">
                    <Clock class="w-3 h-3" />
                    {formatDate(transaction.timestamp)}
                  </span>
                  <span>
                    {transaction.type === 'purchase' ? 'From:' : 'To:'} 
                    {truncateAddress(transaction.type === 'purchase' ? transaction.seller : transaction.buyer)}
                  </span>
                </div>
              </div>
            </div>

            <!-- Price -->
            <div class="text-right">
              <div class="font-bold text-lg {transaction.type === 'purchase' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}">
                {transaction.type === 'purchase' ? '-' : '+'}{formatPrice(transaction.priceICP)} ICP
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                ≈ ${(transaction.priceICP * 12).toFixed(2)} USD
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Summary -->
      {#if allTransactions.length > 0}
        <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <p class="text-2xl font-bold text-gray-900 dark:text-white">{allTransactions.length}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Total Transactions</p>
            </div>
            <div class="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p class="text-2xl font-bold text-green-600 dark:text-green-400">{purchases.length}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Purchases</p>
            </div>
            <div class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">{sales.length}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Sales</p>
            </div>
            <div class="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {(sales.reduce((sum, s) => sum + s.priceICP, 0) - purchases.reduce((sum, p) => sum + p.priceICP, 0)).toFixed(2)}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">Net ICP</p>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>

