<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { store } from '../../stores/store';
  import { TransactionService, type ProcessedTransaction } from '../../helpers/TransactionService';
  
  export let title: string = "My $FUNNAI Ledger";
  export let maxResults: number = 20;
  export let refreshInterval: number = 30000; // 30 seconds
  
  let transactions: ProcessedTransaction[] = [];
  let loading = true;
  let error = "";
  let userPrincipal: string | null = null;
  let refreshTimer: NodeJS.Timeout | null = null;

  // Subscribe to store to get user principal
  const unsubscribe = store.subscribe((state) => {
    const newPrincipal = state.principal?.toString();
    console.log("TransactionHistory: Principal changed from", userPrincipal, "to", newPrincipal);
    if (newPrincipal !== userPrincipal) {
      userPrincipal = newPrincipal;
      if (userPrincipal && userPrincipal !== "anonymous") {
        console.log("TransactionHistory: Loading transactions for principal:", userPrincipal);
        loadTransactions();
      } else {
        console.log("TransactionHistory: No valid principal, clearing transactions");
        transactions = [];
        loading = false;
        error = "";
      }
    }
  });

  async function loadTransactions() {
    if (!userPrincipal || userPrincipal === "anonymous") {
      transactions = [];
      loading = false;
      return;
    }

    loading = true;
    error = "";

    try {
      const fetchedTransactions = await TransactionService.fetchUserTransactions(
        userPrincipal, 
        maxResults
      );
      transactions = fetchedTransactions;
    } catch (err) {
      console.error("Error loading transactions:", err);
      error = "Failed to load transaction history";
      transactions = [];
    } finally {
      loading = false;
    }
  }

  function handleRefresh() {
    if (userPrincipal) {
      TransactionService.clearCache(userPrincipal);
      loadTransactions();
    }
  }

  function formatTimestamp(date: Date): string {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMinutes < 1) {
      return "Just now";
    } else if (diffMinutes < 60) {
      return `${diffMinutes}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  function truncatePrincipal(principal: string): string {
    if (principal.length <= 12) return principal;
    return `${principal.slice(0, 6)}...${principal.slice(-6)}`;
  }

  function getTransactionDescription(tx: ProcessedTransaction): string {
    const amount = TransactionService.formatAmount(tx.amount);
    
    switch (tx.type) {
      case "mint":
        return `Received ${amount} FUNNAI`;
      case "transfer":
        if (tx.from === userPrincipal) {
          return `Sent ${amount} FUNNAI to ${truncatePrincipal(tx.to || "")}`;
        } else {
          return `Received ${amount} FUNNAI from ${truncatePrincipal(tx.from || "")}`;
        }
      case "burn":
        return `Burned ${amount} FUNNAI`;
      case "approve":
        return `Approved ${amount} FUNNAI for ${truncatePrincipal(tx.spender || "")}`;
      default:
        return `${tx.type} ${amount} FUNNAI`;
    }
  }

  onMount(() => {
    // Start refresh timer
    if (refreshInterval > 0) {
      refreshTimer = setInterval(() => {
        if (userPrincipal && !loading) {
          loadTransactions();
        }
      }, refreshInterval);
    }
  });

  onDestroy(() => {
    unsubscribe();
    if (refreshTimer) {
      clearInterval(refreshTimer);
    }
  });
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center space-x-2">
      <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
        <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {#if !userPrincipal || userPrincipal === "anonymous"}
            Please connect your wallet to view transactions
          {:else if transactions.length > 0}
            Showing {transactions.length} recent transactions
          {:else if !loading && !error}
            No transactions found
          {:else}
            Loading transaction history...
          {/if}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-2">
      {#if loading}
        <div class="animate-spin h-4 w-4 border-2 border-purple-500 rounded-full border-t-transparent"></div>
      {/if}
      <button 
        on:click={handleRefresh}
        class="text-xs text-purple-600 dark:text-purple-400 hover:underline px-2 py-1 rounded hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors"
        disabled={loading || !userPrincipal || userPrincipal === "anonymous"}
      >
        Refresh
      </button>
    </div>
  </div>

  <!-- Error State -->
  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      <div class="flex items-center space-x-2">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{error}</span>
      </div>
    </div>
  {/if}

  <!-- Loading State -->
  {#if loading}
    <div class="space-y-3">
      {#each Array(5) as _}
        <div class="animate-pulse">
          <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div class="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            <div class="flex-1 space-y-2">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
            <div class="w-20 h-4 bg-gray-300 dark:bg-gray-600 rounded"></div>
          </div>
        </div>
      {/each}
    </div>
  <!-- No User State -->
  {:else if !userPrincipal || userPrincipal === "anonymous"}
    <div class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400 text-sm">
        Connect your wallet to view your FUNNAI transaction history
      </p>
    </div>
  <!-- Empty State -->
  {:else if transactions.length === 0 && !error}
    <div class="text-center py-8">
      <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
        </svg>
      </div>
      <p class="text-gray-500 dark:text-gray-400 text-sm">
        No transactions found. Your FUNNAI transactions will appear here.
      </p>
    </div>
  <!-- Transactions List -->
  {:else}
    <div class="space-y-2 max-h-96 overflow-y-auto">
      {#each transactions as tx (tx.id)}
        {@const style = TransactionService.getTransactionStyle(tx.type)}
        <div class="flex items-center space-x-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-600">
          <!-- Transaction Icon -->
          <div class="w-10 h-10 rounded-full {style.bgColor} flex items-center justify-center flex-shrink-0">
            <span class="text-lg {style.color}">{style.icon}</span>
          </div>

          <!-- Transaction Details -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {getTransactionDescription(tx)}
              </p>
              <p class="text-sm font-semibold {style.color} ml-2">
                {#if tx.type === "burn" || (tx.type === "transfer" && tx.from === userPrincipal)}
                  -{TransactionService.formatAmount(tx.amount)}
                {:else}
                  +{TransactionService.formatAmount(tx.amount)}
                {/if}
              </p>
            </div>
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {formatTimestamp(tx.timestamp)}
              </p>
              {#if tx.fee && tx.fee > 0n}
                <p class="text-xs text-gray-400 dark:text-gray-500">
                  Fee: {TransactionService.formatAmount(tx.fee)}
                </p>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>

    <!-- View More Link -->
    {#if transactions.length >= maxResults}
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p class="text-center text-sm text-gray-500 dark:text-gray-400">
          Showing {maxResults} most recent transactions
        </p>
      </div>
    {/if}
  {/if}
</div>
