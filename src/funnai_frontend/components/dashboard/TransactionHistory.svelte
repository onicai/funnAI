<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { store } from '../../stores/store';
  import { TransactionService, type ProcessedTransaction } from '../../helpers/TransactionService';
  import { isAnonymousPrincipal } from '../../helpers/utils/accountUtils';
  
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
      // IMPORTANT: Check for anonymous principal (2vxsx-fae) to prevent
      // displaying data for the wrong identity
      if (!isAnonymousPrincipal(userPrincipal)) {
        console.log("TransactionHistory: Loading transactions for principal:", userPrincipal);
        currentPage = 1;
        loadTransactions(1);
      } else {
        console.log("TransactionHistory: No valid principal (anonymous or null), clearing transactions");
        transactions = [];
        loading = false;
        error = "";
        currentPage = 1;
      }
    }
  });

  async function loadTransactions(page: number = 1) {
    if (isAnonymousPrincipal(userPrincipal)) {
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

  $: hasValidPrincipal = !isAnonymousPrincipal(userPrincipal);
</script>

<div class="agent-card !bg-agent-surface {compact ? 'p-4' : 'p-5 sm:p-6'}">
  <div class="relative z-[1] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
    <div class="min-w-0">
      <p class="agent-eyebrow">Ledger</p>
      <h3 class="mt-0.5 text-base font-semibold tracking-tight text-white">{title}</h3>
      <p class="mt-1 text-sm text-gray-500">
        {#if !hasValidPrincipal}
          Connect wallet to view transactions
        {:else if transactions.length > 0}
          Showing {Math.min(currentPage * transactionsPerPage, transactions.length)} of {transactions.length}{hasMore ? '+' : ''} transactions
        {:else if !loading && !error}
          No transactions found
        {:else}
          Loading…
        {/if}
      </p>
    </div>

    <div class="flex items-center gap-2 flex-shrink-0">
      {#if loading || loadingMore}
        <div class="animate-spin h-4 w-4 border-2 border-[#653FC5] rounded-full border-t-transparent"></div>
      {/if}
      <button
        type="button"
        on:click={handleRefresh}
        class="agent-btn-ghost !h-8 !px-3"
        disabled={loading || loadingMore || !hasValidPrincipal}
        title="Refresh"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
  </div>

  {#if error}
    <div class="relative z-[1] text-red-300 text-sm mb-4 p-3 rounded-xl border border-red-500/25 bg-red-500/10">
      {error}
    </div>
  {/if}

  {#if loading}
    <div class="relative z-[1] space-y-2">
      {#each Array(5) as _}
        <div class="animate-pulse grid grid-cols-12 gap-4 items-center p-3 rounded-xl bg-white/[0.03] border border-white/[0.04]">
          <div class="col-span-1 flex justify-center">
            <div class="w-8 h-8 bg-white/[0.08] rounded-full"></div>
          </div>
          <div class="col-span-4 space-y-2">
            <div class="h-3.5 bg-white/[0.08] rounded w-3/4"></div>
            <div class="h-3 bg-white/[0.05] rounded w-1/2"></div>
          </div>
          <div class="col-span-2"><div class="h-3.5 bg-white/[0.08] rounded w-16 ml-auto"></div></div>
          <div class="col-span-2"><div class="h-6 bg-white/[0.08] rounded-full w-20"></div></div>
          <div class="col-span-2"><div class="h-3.5 bg-white/[0.08] rounded w-14 ml-auto"></div></div>
          <div class="col-span-1"><div class="h-3 bg-white/[0.05] rounded w-8 ml-auto"></div></div>
        </div>
      {/each}
    </div>
  {:else if !hasValidPrincipal}
    <div class="relative z-[1] text-center py-10 rounded-xl border border-white/[0.06] bg-white/[0.03]">
      <p class="text-sm text-gray-400">Connect your wallet to view your FUNNAI transaction history</p>
    </div>
  {:else if transactions.length === 0 && !error}
    <div class="relative z-[1] text-center py-10 rounded-xl border border-white/[0.06] bg-white/[0.03]">
      <p class="text-sm text-gray-400">No transactions found. Your FUNNAI transactions will appear here.</p>
    </div>
  {:else}
    {@const displayTransactions = transactions}

    <div class="relative z-[1] hidden md:grid grid-cols-12 gap-4 px-3 py-2 mb-2 text-[11px] uppercase tracking-[0.14em] text-gray-500 font-medium border-b border-white/[0.06]">
      <div class="col-span-1">Type</div>
      <div class="col-span-4">Description</div>
      <div class="col-span-2 text-right">Amount</div>
      <div class="col-span-2">Status</div>
      <div class="col-span-2 text-right">Time</div>
      <div class="col-span-1 text-right">Fee</div>
    </div>

    <div class="relative z-[1] space-y-1 max-h-96 overflow-y-auto">
      {#each displayTransactions as tx (tx.id)}
        {@const style = TransactionService.getTransactionStyle(tx.type)}
        {@const isOutgoing = tx.type === "burn" || (tx.type === "transfer" && tx.from === userPrincipal)}
        {@const amount = TransactionService.formatAmount(tx.amount)}
        {@const fee = tx.fee ? TransactionService.formatAmount(tx.fee) : null}

        <div class="rounded-xl border border-transparent hover:border-white/[0.08] hover:bg-white/[0.03] transition-all duration-200 group">
          <div
            class="hidden md:grid grid-cols-12 gap-4 items-center p-3 cursor-pointer"
            on:click={() => toggleTransactionDetails(tx.id)}
            on:keydown={(e) => e.key === 'Enter' && toggleTransactionDetails(tx.id)}
            role="button"
            tabindex="0"
          >
            <div class="col-span-1 flex justify-center">
              <div class="w-8 h-8 rounded-full {style.bgColor} flex items-center justify-center">
                <span class="text-sm {style.color} font-bold">{style.icon}</span>
              </div>
            </div>
            <div class="col-span-4 min-w-0">
              <p class="text-sm font-medium text-white truncate">{getTransactionDescription(tx)}</p>
              <p class="text-xs text-gray-500 truncate font-mono">{tx.id.slice(0, 8)}...{tx.id.slice(-8)}</p>
            </div>
            <div class="col-span-2 text-right">
              <p class="text-sm font-semibold tabular-nums {isOutgoing ? 'text-red-400' : 'text-emerald-400'}">
                {isOutgoing ? '-' : '+'}{amount}
              </p>
              <p class="text-xs text-gray-500">FUNNAI</p>
            </div>
            <div class="col-span-2">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border border-emerald-500/25 bg-emerald-500/10 text-emerald-300">
                <span class="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-1.5"></span>
                Confirmed
              </span>
            </div>
            <div class="col-span-2 text-right">
              <p class="text-sm text-gray-300">{formatTimestamp(tx.timestamp)}</p>
            </div>
            <div class="col-span-1 text-right flex items-center justify-end gap-2">
              <p class="text-xs text-gray-500">{fee || '-'}</p>
              <svg class="w-4 h-4 text-gray-500 transition-transform duration-200 {expandedTransaction === tx.id ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <div
            class="md:hidden p-4 cursor-pointer"
            on:click={() => toggleTransactionDetails(tx.id)}
            on:keydown={(e) => e.key === 'Enter' && toggleTransactionDetails(tx.id)}
            role="button"
            tabindex="0"
          >
            <div class="flex items-start justify-between mb-3 gap-3">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-10 h-10 rounded-full {style.bgColor} flex items-center justify-center flex-shrink-0">
                  <span class="text-base {style.color} font-bold">{style.icon}</span>
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-white">{getTransactionDescription(tx)}</p>
                  <p class="text-xs text-gray-500 font-mono mt-1">{tx.id.slice(0, 8)}...{tx.id.slice(-8)}</p>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-base font-semibold tabular-nums {isOutgoing ? 'text-red-400' : 'text-emerald-400'}">
                  {isOutgoing ? '-' : '+'}{amount}
                </p>
                <p class="text-xs text-gray-500">FUNNAI</p>
              </div>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border border-emerald-500/25 bg-emerald-500/10 text-emerald-300">
                Confirmed
              </span>
              <span class="text-sm text-gray-400">{formatTimestamp(tx.timestamp)}</span>
            </div>
          </div>

          {#if expandedTransaction === tx.id}
            <div class="px-3 pb-3 border-t border-white/[0.06] bg-white/[0.02]">
              <div class="pt-3 space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-[11px] font-medium text-gray-500 uppercase tracking-[0.14em]">Transaction ID</span>
                  <div class="flex items-center gap-2 min-w-0">
                    <code class="text-xs font-mono text-gray-300 bg-white/[0.04] border border-white/[0.06] px-2 py-1 rounded-lg break-all">{tx.id}</code>
                    <button type="button" on:click|stopPropagation={() => copyToClipboard(tx.id)} class="p-1.5 rounded-lg hover:bg-white/[0.06] text-gray-500 hover:text-gray-300 transition-colors flex-shrink-0">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                    </button>
                  </div>
                </div>
                {#if tx.from}
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <span class="text-[11px] font-medium text-gray-500 uppercase tracking-[0.14em]">From</span>
                    <code class="text-xs font-mono text-gray-300 bg-white/[0.04] border border-white/[0.06] px-2 py-1 rounded-lg break-all">{tx.from}</code>
                  </div>
                {/if}
                {#if tx.to}
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <span class="text-[11px] font-medium text-gray-500 uppercase tracking-[0.14em]">To</span>
                    <code class="text-xs font-mono text-gray-300 bg-white/[0.04] border border-white/[0.06] px-2 py-1 rounded-lg break-all">{tx.to}</code>
                  </div>
                {/if}
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-[11px] font-medium text-gray-500 uppercase tracking-[0.14em]">Timestamp</span>
                  <span class="text-xs text-gray-300 font-mono">{tx.timestamp.toISOString()}</span>
                </div>
                <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <span class="text-[11px] font-medium text-gray-500 uppercase tracking-[0.14em]">Type</span>
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border border-[#653FC5]/30 bg-[#653FC5]/15 text-[#c4b5fd] w-fit">
                    {tx.type.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>

    {#if showPagination && transactions.length > 0 && totalPages > 1}
      <div class="relative z-[1] mt-5 pt-4 border-t border-white/[0.06]">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
          <div class="text-sm text-gray-500">
            Page {currentPage} of {totalPages}{hasMore ? '+' : ''}
          </div>
          <div class="flex items-center gap-2">
            <input
              type="number"
              bind:value={jumpToPage}
              on:keydown={(e) => e.key === 'Enter' && handleJumpToPage()}
              min="1"
              max={totalPages}
              class="agent-input !w-16 !py-1.5 !px-2 !text-sm"
              placeholder={currentPage.toString()}
            />
            <button type="button" on:click={handleJumpToPage} disabled={loading} class="agent-btn-ghost !h-8 !px-3 disabled:opacity-50">
              Go
            </button>
          </div>
        </div>

        <div class="hidden sm:flex items-center justify-center gap-1">
          <button type="button" on:click={goToFirstPage} disabled={currentPage <= 1 || loading} class="agent-btn-ghost !h-9 !px-3 disabled:opacity-40" title="First page">«</button>
          <button type="button" on:click={loadPreviousPage} disabled={currentPage <= 1 || loading} class="agent-btn-ghost !h-9 !px-3 disabled:opacity-40" title="Previous">‹</button>
          {#each getVisiblePages(false) as page}
            {#if page === '...'}
              <span class="px-2 text-sm text-gray-600">…</span>
            {:else}
              <button
                type="button"
                on:click={() => goToPage(typeof page === 'number' ? page : parseInt(page.toString()))}
                disabled={loading}
                class="!h-9 !min-w-[2.25rem] !px-3 rounded-full text-[13px] font-medium transition-all duration-200 disabled:opacity-50 {page === currentPage
                  ? 'bg-[#653FC5] text-white shadow-sm'
                  : 'border border-white/10 bg-white/[0.04] text-gray-300 hover:border-[#653FC5]/40 hover:text-white'}"
              >
                {page}
              </button>
            {/if}
          {/each}
          <button type="button" on:click={loadNextPage} disabled={(currentPage >= totalPages && !hasMore) || loading} class="agent-btn-ghost !h-9 !px-3 disabled:opacity-40" title="Next">›</button>
          <button type="button" on:click={goToLastPage} disabled={currentPage >= totalPages || loading} class="agent-btn-ghost !h-9 !px-3 disabled:opacity-40" title="Last page">»</button>
        </div>

        <div class="sm:hidden flex items-center justify-center gap-2">
          <button type="button" on:click={loadPreviousPage} disabled={currentPage <= 1 || loading} class="agent-btn-ghost flex-1 max-w-24 disabled:opacity-40">‹</button>
          {#each getVisiblePages(true) as page}
            {#if page === '...'}
              <span class="px-2 text-sm text-gray-600">…</span>
            {:else}
              <button
                type="button"
                on:click={() => goToPage(typeof page === 'number' ? page : parseInt(page.toString()))}
                disabled={loading}
                class="!h-9 !min-w-[2.25rem] !px-3 rounded-full text-[13px] font-medium {page === currentPage
                  ? 'bg-[#653FC5] text-white'
                  : 'border border-white/10 bg-white/[0.04] text-gray-300'}"
              >
                {page}
              </button>
            {/if}
          {/each}
          <button type="button" on:click={loadNextPage} disabled={(currentPage >= totalPages && !hasMore) || loading} class="agent-btn-ghost flex-1 max-w-24 disabled:opacity-40">›</button>
        </div>
      </div>
    {/if}
  {/if}
</div>
