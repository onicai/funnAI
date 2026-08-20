<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { RefreshCw } from 'lucide-svelte';

  import WalletStatus from '../components/funnai/WalletStatus.svelte';
  import LoginModal from '../components/login/LoginModal.svelte';
  import WalletTokenList from "../components/WalletTokenList.svelte";
  import TokenListSkeleton from "../components/TokenListSkeleton.svelte";
  import Footer from "../components/funnai/Footer.svelte";
  import TransactionHistory from "../components/dashboard/TransactionHistory.svelte";
  import { store } from "../stores/store";
  import { WalletDataService, walletDataStore } from "../helpers/WalletDataService";

  let modalIsOpen = false;
  let isLoading = false;
  let isLoadingHistory = false;
  let loadingError: string | null = null;
  let isRefreshingHoldings = false;
  let holdingsRefreshFeedback: 'updated' | 'unchanged' | 'failed' | null = null;
  let holdingsRefreshTimer: ReturnType<typeof setTimeout> | null = null;

  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isDataLoading =
    isLoading ||
    isLoadingHistory ||
    walletData.isLoading;

  $: hasHoldingsData = (walletData?.tokens?.length ?? 0) > 0;
  $: showHoldingsSkeleton = isDataLoading && !hasHoldingsData && !isRefreshingHoldings;

  $: listedCount = walletData?.tokens?.length ?? 0;
  $: holdingCount = walletData?.tokens?.filter((token) => {
    const balance = walletData.balances[token.canister_id];
    return balance && Number(balance.in_tokens || "0") > 0;
  }).length ?? 0;

  async function refreshHoldings() {
    if (!$store.principal || !$store.isAuthed || isRefreshingHoldings) return;

    isRefreshingHoldings = true;
    holdingsRefreshFeedback = null;
    try {
      const result = await WalletDataService.refreshBalances(true);
      holdingsRefreshFeedback = result;
      if (holdingsRefreshTimer) clearTimeout(holdingsRefreshTimer);
      holdingsRefreshTimer = setTimeout(() => {
        holdingsRefreshFeedback = null;
      }, 4000);
    } catch (error) {
      console.error("Failed to refresh holdings:", error);
      holdingsRefreshFeedback = 'failed';
    } finally {
      isRefreshingHoldings = false;
    }
  }

  async function loadTokensOnly(principalId: string) {
    if (isLoading || !principalId) return;

    try {
      isLoading = true;
      loadingError = null;
      await WalletDataService.loadTokensOnly(principalId);
    } catch (error) {
      console.error("Failed to load tokens:", error);
      loadingError = error instanceof Error ? error.message : "Failed to load token metadata";
    } finally {
      isLoading = false;
    }
  }

  $: {
    const walletState = get(walletDataStore);
    loadingError = walletState.error;
    const shouldBeLoading = walletState.isLoading;
    if (isLoading !== shouldBeLoading) {
      isLoading = shouldBeLoading;
    }
  }

  $: if ($store.isAuthed) {
    WalletDataService.initializeWallet($store.principal.toString());
  }

  onMount(async () => {
    await WalletDataService.initializeWallet($store?.principal?.toString());
  });

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  function connect() {
    toggleModal();
  }
</script>

<div class="agent-page">
  <div class="agent-container">
    <div class="mb-8">
      <p class="agent-eyebrow mb-2">Portfolio</p>
      <h1 class="agent-title mb-2">Wallet</h1>
      <p class="agent-subtitle">View balances and transaction history</p>
    </div>

    <div class="flex flex-col gap-6">
      <WalletStatus />

      <div class="agent-card !bg-agent-surface overflow-hidden">
        <div class="relative z-[1] p-5 sm:p-6">
          <div class="flex items-start justify-between gap-3 mb-5">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="agent-eyebrow">Holdings</p>
                {#if $store.isAuthed && !showHoldingsSkeleton && listedCount > 0}
                  <span class="inline-flex items-center rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[11px] font-medium text-gray-400">
                    {holdingCount} with balance
                    {#if listedCount !== holdingCount}
                      <span class="text-gray-600"> · {listedCount} listed</span>
                    {/if}
                  </span>
                {/if}
              </div>
              <h2 class="mt-1 text-base font-semibold tracking-tight text-white">Your assets</h2>
              <p class="mt-0.5 text-sm text-gray-500">Tokens you can send and receive in this wallet</p>
              {#if $store.isAuthed}
                {#if isRefreshingHoldings}
                  <p class="mt-1.5 text-xs text-[#c4b5fd]">Refreshing holdings…</p>
                {:else if holdingsRefreshFeedback === 'updated'}
                  <p class="mt-1.5 text-xs text-emerald-400">Holdings updated.</p>
                {:else if holdingsRefreshFeedback === 'unchanged'}
                  <p class="mt-1.5 text-xs text-gray-400">Holdings unchanged. If a credit is still pending, it may take a moment to appear.</p>
                {:else if holdingsRefreshFeedback === 'failed'}
                  <p class="mt-1.5 text-xs text-red-300">Couldn't refresh holdings. Please try again.</p>
                {/if}
              {/if}
            </div>
            {#if $store.isAuthed}
              <button
                type="button"
                on:click={refreshHoldings}
                disabled={isRefreshingHoldings || showHoldingsSkeleton}
                class="inline-flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/[0.04] text-gray-300 transition-all hover:border-[#653FC5]/40 hover:bg-[#653FC5]/10 hover:text-white disabled:opacity-40"
                title={isRefreshingHoldings ? 'Refreshing…' : holdingsRefreshFeedback === 'updated' ? 'Holdings updated' : holdingsRefreshFeedback === 'unchanged' ? 'Holdings unchanged' : holdingsRefreshFeedback === 'failed' ? 'Refresh failed' : 'Refresh holdings'}
              >
                <RefreshCw class="h-3.5 w-3.5 {isRefreshingHoldings ? 'animate-spin' : ''}" />
              </button>
            {/if}
          </div>

          {#if $store.isAuthed}
            {#if showHoldingsSkeleton}
              <TokenListSkeleton rows={4} />
            {:else if loadingError && Object.keys(walletData.balances || {}).length === 0}
              <div class="rounded-xl border border-red-500/20 bg-red-500/[0.08] px-4 py-8 text-center">
                <p class="text-red-300 mb-2 text-sm">{loadingError}</p>
                <p class="text-gray-500 mb-4 text-sm">This is not a zero balance — the query failed.</p>
                <button
                  type="button"
                  class="agent-btn-ghost"
                  on:click={() => $store.principal && WalletDataService.initializeWallet($store.principal.toString(), true)}
                >
                  Try again
                </button>
              </div>
            {:else if walletData.tokens.length === 0}
              <div class="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-10 text-center">
                <p class="text-sm text-gray-400">No tokens available yet</p>
              </div>
            {:else}
              {#if loadingError && !isRefreshingHoldings}
                <div class="mb-4 rounded-xl border border-amber-500/20 bg-amber-500/[0.08] px-4 py-3 text-sm text-amber-200">
                  {loadingError}. Showing last known balances.
                  <button
                    type="button"
                    class="ml-2 underline"
                    on:click={refreshHoldings}
                  >Retry</button>
                </div>
              {/if}
              {#key walletData.lastUpdated}
                <WalletTokenList
                  tokens={walletData.tokens}
                  showHeader={false}
                  showOnlyWithBalance={false}
                  isLoading={false}
                />
              {/key}
            {/if}
          {:else}
            <div class="flex flex-col sm:flex-row sm:items-center gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] p-4 sm:p-5">
              <div class="min-w-0 flex-1">
                <h3 class="text-sm font-semibold tracking-tight text-white">Connect to view balances</h3>
                <p class="mt-0.5 text-sm text-gray-500">Your supported tokens will appear here</p>
              </div>
              <button type="button" on:click={connect} class="agent-btn-primary w-full sm:w-auto flex-shrink-0">
                Connect wallet
              </button>
            </div>
          {/if}
        </div>
      </div>

      <TransactionHistory />
    </div>
  </div>

  <Footer />
</div>

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}

<svelte:head>
  <title>onicai</title>
</svelte:head>

<script context="module">
  export const Wallet = (props) => {
    return {
      component: Wallet,
      props
    };
  };
</script>
