<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { store } from '../../stores/store';
  import { TransactionService, type ProcessedTransaction } from '../../helpers/TransactionService';
  
  export let title: string = "My $FUNNAI Ledger";
  export let refreshInterval: number = 30000; // 30 seconds
  export let showPagination: boolean = true;
  export let compact: boolean = false;
  
  let transactions: ProcessedTransaction[] = [];
  let loading = true;
  let error = "";
  let userPrincipal: string | null = null;
  let refreshTimer: NodeJS.Timeout | null = null;
  let expandedTransaction: string | null = null;
  
  // Pagination state
  let currentPage = 1;
  let totalPages = 1;
  let hasMore = true;
  let loadingMore = false;
  let jumpToPage = "";
  const transactionsPerPage = 20;
  const maxVisiblePages = 7; // Show up to 7 page numbers on desktop
  const maxVisiblePagesMobile = 3; // Show up to 3 page numbers on mobile

  // Subscribe to store to get user principal
  const unsubscribe = store.subscribe((state) => {
    const newPrincipal = state.principal?.toString();
    console.log("TransactionHistory: Principal changed from", userPrincipal, "to", newPrincipal);
    if (newPrincipal !== userPrincipal) {
      userPrincipal = newPrincipal;
      if (userPrincipal && userPrincipal !== "anonymous") {
        console.log("TransactionHistory: Loading transactions for principal:", userPrincipal);
        currentPage = 1;
        loadTransactions(1);
      } else {
        console.log("TransactionHistory: No valid principal, clearing transactions");
        transactions = [];
        loading = false;
        error = "";
        currentPage = 1;
      }
    }
  });

  async function loadTransactions(page: number = 1) {
    if (!userPrincipal || userPrincipal === "anonymous") {
      transactions = [];
      loading = false;
      return;
    }

    loading = true;
    currentPage = page;
    error = "";

    try {
      // For true pagination, we need to estimate the start index
      // Since we can't get exact pagination from the canister, we'll fetch a larger batch
      // and slice it to show the requested page
      const batchSize = Math.max(100, page * transactionsPerPage * 2);
      const fetchedTransactions = await TransactionService.fetchUserTransactions(
        userPrincipal, 
        batchSize
      );
      
      // Calculate pagination
      const startIndex = (page - 1) * transactionsPerPage;
      const endIndex = startIndex + transactionsPerPage;
      
      // Store all transactions for pagination
      const allTransactions = fetchedTransactions;
      transactions = allTransactions.slice(startIndex, endIndex);
      
      // Update pagination state
      totalPages = Math.ceil(allTransactions.length / transactionsPerPage);
      hasMore = allTransactions.length >= batchSize; // Might have more if we hit the batch limit
      
      // If we're on a page beyond what we have, adjust
      if (page > totalPages && totalPages > 0) {
        currentPage = totalPages;
        transactions = allTransactions.slice((totalPages - 1) * transactionsPerPage, totalPages * transactionsPerPage);
      }
      
    } catch (err) {
      console.error("Error loading transactions:", err);
      error = "Failed to load transaction history";
      transactions = [];
    } finally {
      loading = false;
    }
  }

  function loadNextPage() {
    if (!loading && (currentPage < totalPages || hasMore)) {
      loadTransactions(currentPage + 1);
    }
  }

  function loadPreviousPage() {
    if (currentPage > 1 && !loading) {
      loadTransactions(currentPage - 1);
    }
  }

  function goToPage(page: number) {
    if (page !== currentPage && page >= 1 && !loading) {
      loadTransactions(page);
    }
  }

  function goToFirstPage() {
    if (currentPage > 1 && !loading) {
      loadTransactions(1);
    }
  }

  function goToLastPage() {
    if (currentPage < totalPages && !loading) {
      loadTransactions(totalPages);
    }
  }

  function handleJumpToPage() {
    const page = parseInt(jumpToPage);
    if (page && page >= 1 && page <= totalPages && page !== currentPage) {
      loadTransactions(page);
      jumpToPage = "";
    }
  }

  // Generate page numbers for display with ellipsis
  function getVisiblePages(isMobile: boolean = false): (number | string)[] {
    const maxPages = isMobile ? maxVisiblePagesMobile : maxVisiblePages;
    
    if (totalPages <= maxPages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const pages: (number | string)[] = [];
    const halfVisible = Math.floor(maxPages / 2);

    if (currentPage <= halfVisible + 1) {
      // Show pages from start
      for (let i = 1; i <= maxPages - 2; i++) {
        pages.push(i);
      }
      pages.push('...');
      pages.push(totalPages);
    } else if (currentPage >= totalPages - halfVisible) {
      // Show pages near end
      pages.push(1);
      pages.push('...');
      for (let i = totalPages - (maxPages - 3); i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show pages around current
      pages.push(1);
      pages.push('...');
      for (let i = currentPage - halfVisible + 1; i <= currentPage + halfVisible - 1; i++) {
        pages.push(i);
      }
      pages.push('...');
      pages.push(totalPages);
    }

    return pages;
  }

  function toggleTransactionDetails(txId: string) {
    expandedTransaction = expandedTransaction === txId ? null : txId;
  }

  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      // You could add a toast notification here
      console.log('Copied to clipboard:', text);
    });
  }

  function handleRefresh() {
    if (userPrincipal) {
      TransactionService.clearCache(userPrincipal);
      currentPage = 1;
      loadTransactions(1);
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
          loadTransactions(currentPage);
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

<div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 {compact ? 'p-4' : 'p-6'}">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
    <div class="flex items-center space-x-3">
      <div class="p-2.5 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-sm">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <div class="min-w-0 flex-1">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">{title}</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          {#if !userPrincipal || userPrincipal === "anonymous"}
            Connect wallet to view transactions
          {:else if transactions.length > 0}
            Showing {Math.min(currentPage * transactionsPerPage, transactions.length)} of {transactions.length}{hasMore ? '+' : ''} transactions
          {:else if !loading && !error}
            No transactions found
          {:else}
            Loading...
          {/if}
        </p>
      </div>
    </div>

    <div class="flex items-center gap-3 flex-shrink-0">
      {#if loading || loadingMore}
        <div class="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      {/if}
      
      <button 
        on:click={handleRefresh}
        class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-200"
        disabled={loading || loadingMore || !userPrincipal || userPrincipal === "anonymous"}
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
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
    <!-- Table header skeleton -->
    <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 mb-3">
      <div class="grid grid-cols-12 gap-4 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
        <div class="col-span-1">Type</div>
        <div class="col-span-4">Description</div>
        <div class="col-span-2">Amount</div>
        <div class="col-span-2">Status</div>
        <div class="col-span-2">Time</div>
        <div class="col-span-1">Fee</div>
      </div>
    </div>
    
    <!-- Table rows skeleton -->
    <div class="space-y-1">
      {#each Array(5) as _}
        <div class="animate-pulse">
          <div class="grid grid-cols-12 gap-4 items-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div class="col-span-1 flex justify-center">
              <div class="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full"></div>
            </div>
            <div class="col-span-4 space-y-2">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
              <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
            <div class="col-span-2 text-right space-y-1">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-16 ml-auto"></div>
              <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-12 ml-auto"></div>
            </div>
            <div class="col-span-2">
              <div class="h-6 bg-gray-300 dark:bg-gray-600 rounded-full w-20"></div>
            </div>
            <div class="col-span-2 text-right">
              <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-16 ml-auto"></div>
            </div>
            <div class="col-span-1 text-right">
              <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-8 ml-auto"></div>
            </div>
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
    {@const displayTransactions = transactions}
    
    <!-- Desktop table header - hidden on mobile -->
    <div class="hidden md:block bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 mb-3">
      <div class="grid grid-cols-12 gap-4 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
        <div class="col-span-1">Type</div>
        <div class="col-span-4">Description</div>
        <div class="col-span-2">Amount</div>
        <div class="col-span-2">Status</div>
        <div class="col-span-2">Time</div>
        <div class="col-span-1">Fee</div>
      </div>
    </div>

    <!-- Transactions list -->
    <div class="space-y-1 max-h-96 overflow-y-auto">
      {#each displayTransactions as tx (tx.id)}
        {@const style = TransactionService.getTransactionStyle(tx.type)}
        {@const isOutgoing = tx.type === "burn" || (tx.type === "transfer" && tx.from === userPrincipal)}
        {@const amount = TransactionService.formatAmount(tx.amount)}
        {@const fee = tx.fee ? TransactionService.formatAmount(tx.fee) : null}
        
        <div class="hover:bg-gray-50 dark:hover:bg-gray-700/30 rounded-lg transition-all duration-200 border border-transparent hover:border-gray-200 dark:hover:border-gray-600 group">
          <!-- Desktop table layout -->
          <div 
            class="hidden md:grid grid-cols-12 gap-4 items-center p-3 cursor-pointer" 
            on:click={() => toggleTransactionDetails(tx.id)}
            on:keydown={(e) => e.key === 'Enter' && toggleTransactionDetails(tx.id)}
            role="button"
            tabindex="0"
          >
            <!-- Type Icon -->
            <div class="col-span-1 flex justify-center">
              <div class="w-8 h-8 rounded-full {style.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                <span class="text-sm {style.color} font-bold">{style.icon}</span>
              </div>
            </div>

            <!-- Description -->
            <div class="col-span-4 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {getTransactionDescription(tx)}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate font-mono">
                {tx.id.slice(0, 8)}...{tx.id.slice(-8)}
              </p>
            </div>

            <!-- Amount -->
            <div class="col-span-2 text-right">
              <p class="text-sm font-bold {isOutgoing ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}">
                {isOutgoing ? '-' : '+'}{amount}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">FUNNAI</p>
            </div>

            <!-- Status -->
            <div class="col-span-2">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></div>
                Confirmed
              </span>
            </div>

            <!-- Time -->
            <div class="col-span-2 text-right">
              <p class="text-sm text-gray-900 dark:text-white">
                {formatTimestamp(tx.timestamp)}
              </p>
            </div>

            <!-- Fee & Expand -->
            <div class="col-span-1 text-right flex items-center justify-end gap-2">
              {#if fee}
                <p class="text-xs text-gray-500 dark:text-gray-400">{fee}</p>
              {:else}
                <p class="text-xs text-gray-300 dark:text-gray-600">-</p>
              {/if}
              <svg class="w-4 h-4 text-gray-400 transition-transform duration-200 {expandedTransaction === tx.id ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- Mobile card layout -->
          <div 
            class="md:hidden p-4 cursor-pointer" 
            on:click={() => toggleTransactionDetails(tx.id)}
            on:keydown={(e) => e.key === 'Enter' && toggleTransactionDetails(tx.id)}
            role="button"
            tabindex="0"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-full {style.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
                  <span class="text-base {style.color} font-bold">{style.icon}</span>
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {getTransactionDescription(tx)}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-mono mt-1">
                    {tx.id.slice(0, 8)}...{tx.id.slice(-8)}
                  </p>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-lg font-bold {isOutgoing ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}">
                  {isOutgoing ? '-' : '+'}{amount}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">FUNNAI</p>
              </div>
            </div>
            
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center space-x-4">
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                  <div class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5"></div>
                  Confirmed
                </span>
                {#if fee}
                  <span class="text-xs text-gray-500 dark:text-gray-400">Fee: {fee}</span>
                {/if}
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {formatTimestamp(tx.timestamp)}
                </span>
                <svg class="w-4 h-4 text-gray-400 transition-transform duration-200 {expandedTransaction === tx.id ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Expanded details -->
          {#if expandedTransaction === tx.id}
            <div class="px-3 md:px-3 pb-3 border-t border-gray-200 dark:border-gray-600 bg-gray-50/50 dark:bg-gray-700/20">
              <div class="pt-3 space-y-3">
                <!-- Transaction ID -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Transaction ID</span>
                  <div class="flex items-center gap-2">
                    <code class="text-xs font-mono text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded break-all">
                      {tx.id}
                    </code>
                    <button 
                      on:click|stopPropagation={() => copyToClipboard(tx.id)}
                      class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors flex-shrink-0"
                    >
                      <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- From/To addresses -->
                {#if tx.from}
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <span class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">From</span>
                    <div class="flex items-center gap-2">
                      <code class="text-xs font-mono text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded">
                        <span class="sm:hidden">{truncatePrincipal(tx.from)}</span>
                        <span class="hidden sm:inline break-all">{tx.from}</span>
                      </code>
                      <button 
                        on:click|stopPropagation={() => copyToClipboard(tx.from)}
                        class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors flex-shrink-0"
                      >
                        <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                {/if}

                {#if tx.to}
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <span class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">To</span>
                    <div class="flex items-center gap-2">
                      <code class="text-xs font-mono text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded">
                        <span class="sm:hidden">{truncatePrincipal(tx.to)}</span>
                        <span class="hidden sm:inline break-all">{tx.to}</span>
                      </code>
                      <button 
                        on:click|stopPropagation={() => copyToClipboard(tx.to)}
                        class="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors flex-shrink-0"
                      >
                        <svg class="w-3 h-3 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                {/if}

                <!-- Timestamp -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Timestamp</span>
                  <span class="text-xs text-gray-800 dark:text-gray-200 font-mono">
                    {tx.timestamp.toISOString()}
                  </span>
                </div>

                <!-- Transaction Type -->
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Type</span>
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 w-fit">
                    {tx.type.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>

    <!-- Pagination Controls -->
    {#if showPagination && transactions.length > 0 && totalPages > 1}
      <div class="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <!-- Page info and jump controls -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div class="text-sm text-gray-600 dark:text-gray-400">
            Page {currentPage} of {totalPages}{hasMore ? '+' : ''} • Showing {transactions.length} transactions
          </div>
          
          <!-- Jump to page -->
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600 dark:text-gray-400 hidden sm:inline">Go to page:</span>
            <input 
              type="number" 
              bind:value={jumpToPage}
              on:keydown={(e) => e.key === 'Enter' && handleJumpToPage()}
              min="1" 
              max={totalPages}
              class="w-16 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
              placeholder={currentPage.toString()}
            />
            <button 
              on:click={handleJumpToPage}
              disabled={loading}
              class="px-2 py-1 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 disabled:opacity-50"
            >
              Go
            </button>
          </div>
        </div>

        <!-- Desktop pagination -->
        <div class="hidden sm:flex items-center justify-center gap-1">
          <!-- First page -->
          <button 
            on:click={goToFirstPage}
            disabled={currentPage <= 1 || loading}
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
            title="First page"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>

          <!-- Previous page -->
          <button 
            on:click={loadPreviousPage}
            disabled={currentPage <= 1 || loading}
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
            title="Previous page"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Page numbers with ellipsis -->
          {#each getVisiblePages(false) as page}
            {#if page === '...'}
              <span class="px-3 py-2 text-sm text-gray-400 dark:text-gray-500">...</span>
            {:else}
              <button 
                on:click={() => goToPage(typeof page === 'number' ? page : parseInt(page.toString()))}
                disabled={loading}
                class="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 {page === currentPage 
                  ? 'text-white bg-blue-600 border border-blue-600 shadow-sm' 
                  : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'} disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {page}
              </button>
            {/if}
          {/each}

          <!-- Next page -->
          <button 
            on:click={loadNextPage}
            disabled={currentPage >= totalPages && !hasMore || loading}
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
            title="Next page"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <!-- Last page -->
          <button 
            on:click={goToLastPage}
            disabled={currentPage >= totalPages || loading}
            class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
            title="Last page"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <!-- Mobile pagination - simplified -->
        <div class="sm:hidden flex items-center justify-center gap-2">
          <!-- Previous page -->
          <button 
            on:click={loadPreviousPage}
            disabled={currentPage <= 1 || loading}
            class="flex-1 max-w-24 px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
          >
            <svg class="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <!-- Limited page numbers for mobile -->
          {#each getVisiblePages(true) as page}
            {#if page === '...'}
              <span class="px-2 py-2 text-sm text-gray-400 dark:text-gray-500">...</span>
            {:else}
              <button 
                on:click={() => goToPage(typeof page === 'number' ? page : parseInt(page.toString()))}
                disabled={loading}
                class="px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 {page === currentPage 
                  ? 'text-white bg-blue-600 border border-blue-600 shadow-sm' 
                  : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300'} disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {page}
              </button>
            {/if}
          {/each}

          <!-- Next page -->
          <button 
            on:click={loadNextPage}
            disabled={currentPage >= totalPages && !hasMore || loading}
            class="flex-1 max-w-24 px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-300 transition-all duration-200"
          >
            <svg class="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    {/if}
  {/if}
</div>
