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

<div class="agent-card">
  <!-- Header -->
  <div class="border-b border-white/[0.08] px-6 py-4">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
        <History class="w-5 h-5 text-agent-purple" />
      </div>
      <div>
        <p class="agent-eyebrow">Activity</p>
        <h2 class="text-lg font-semibold tracking-tight text-white">Transaction History</h2>
        <p class="text-sm text-gray-400">Your marketplace buys and sells</p>
      </div>
    </div>
  </div>

  <!-- Tab Navigation -->
  <div class="border-b border-white/[0.08] px-6 py-3">
    <div class="agent-tab-track">
      <button
        on:click={() => activeTab = 'all'}
        class="agent-tab {activeTab === 'all' ? 'agent-tab-active' : ''}"
      >
        All ({allTransactions.length})
      </button>
      <button
        on:click={() => activeTab = 'purchases'}
        class="agent-tab inline-flex items-center gap-1.5 {activeTab === 'purchases' ? 'agent-tab-active' : ''}"
      >
        <ArrowDownLeft class="w-4 h-4" />
        Purchases ({purchases.length})
      </button>
      <button
        on:click={() => activeTab = 'sales'}
        class="agent-tab inline-flex items-center gap-1.5 {activeTab === 'sales' ? 'agent-tab-active' : ''}"
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
        <History class="w-8 h-8 text-gray-500 mx-auto mb-4" />
        <p class="text-gray-400 mb-2">Connect your wallet</p>
        <p class="text-sm text-gray-500">Sign in to view your transaction history</p>
      </div>
    {:else if isLoading}
      <div class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-agent-purple mx-auto mb-4"></div>
          <p class="text-gray-400">Loading transactions...</p>
        </div>
      </div>
    {:else if error}
      <div class="text-center py-12">
        <History class="w-8 h-8 text-red-400 mx-auto mb-4" />
        <p class="text-red-400 mb-2">Error loading transactions</p>
        <p class="text-sm text-gray-500">{error}</p>
        <button
          on:click={loadTransactionHistory}
          class="mt-4 agent-btn-primary"
        >
          Try Again
        </button>
      </div>
    {:else if displayedTransactions.length === 0}
      <div class="text-center py-12">
        <History class="w-8 h-8 text-gray-500 mx-auto mb-4" />
        <p class="text-gray-400 mb-2">No transactions yet</p>
        <p class="text-sm text-gray-500">
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
          <div class="flex items-center justify-between p-4 bg-white/[0.03] rounded-xl border border-white/10 hover:border-agent-purple/40 transition-colors">
            <div class="flex items-center space-x-4">
              <!-- Transaction Type Icon -->
              <div class="w-10 h-10 rounded-xl flex items-center justify-center border
                          {transaction.type === 'purchase' 
                            ? 'bg-emerald-500/10 border-emerald-500/20' 
                            : 'bg-sky-500/10 border-sky-500/20'}">
                {#if transaction.type === 'purchase'}
                  <ArrowDownLeft class="w-5 h-5 text-emerald-400" />
                {:else}
                  <ArrowUpRight class="w-5 h-5 text-sky-400" />
                {/if}
              </div>

              <!-- Transaction Details -->
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-semibold text-white">
                    {transaction.type === 'purchase' ? 'Purchased' : 'Sold'}
                  </span>
                  <span class="text-sm font-medium px-2 py-0.5 rounded-full border
                              {transaction.type === 'purchase' 
                                ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-300' 
                                : 'bg-sky-500/10 border-sky-500/25 text-sky-300'}">
                    mAIner {transaction.mainerAddress.slice(0, 5)}
                  </span>
                </div>
                <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
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
              <div class="font-semibold text-lg {transaction.type === 'purchase' ? 'text-red-400' : 'text-emerald-400'}">
                {transaction.type === 'purchase' ? '-' : '+'}{formatPrice(transaction.priceICP)} ICP
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Summary -->
      {#if allTransactions.length > 0}
        <div class="mt-6 pt-6 border-t border-white/[0.08]">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-3 bg-white/[0.03] border border-white/10 rounded-xl">
              <p class="text-2xl font-semibold text-white">{allTransactions.length}</p>
              <p class="text-xs text-gray-500">Total Transactions</p>
            </div>
            <div class="text-center p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl">
              <p class="text-2xl font-semibold text-emerald-400">{purchases.length}</p>
              <p class="text-xs text-gray-500">Purchases</p>
            </div>
            <div class="text-center p-3 bg-sky-500/5 border border-sky-500/20 rounded-xl">
              <p class="text-2xl font-semibold text-sky-400">{sales.length}</p>
              <p class="text-xs text-gray-500">Sales</p>
            </div>
            <div class="text-center p-3 bg-agent-purple/10 border border-agent-purple/20 rounded-xl">
              <p class="text-2xl font-semibold text-agent-purple">
                {(sales.reduce((sum, s) => sum + s.priceICP, 0) - purchases.reduce((sum, p) => sum + p.priceICP, 0)).toFixed(2)}
              </p>
              <p class="text-xs text-gray-500">Net ICP</p>
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>
</div>

