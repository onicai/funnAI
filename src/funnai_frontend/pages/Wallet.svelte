<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';

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

  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isDataLoading =
    isLoading ||
    isLoadingHistory ||
    walletData.isLoading;

  $: listedCount = walletData?.tokens?.length ?? 0;
  $: holdingCount = walletData?.tokens?.filter((token) => {
    const balance = walletData.balances[token.canister_id];
    return balance && Number(balance.in_tokens || "0") > 0;
  }).length ?? 0;

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
                {#if $store.isAuthed && !isDataLoading && listedCount > 0}
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
            </div>
          </div>

          {#if $store.isAuthed}
            {#if isDataLoading}
              <TokenListSkeleton rows={4} />
            {:else if loadingError}
              <div class="rounded-xl border border-red-500/20 bg-red-500/[0.08] px-4 py-8 text-center">
                <p class="text-red-300 mb-4 text-sm">{loadingError}</p>
                <button
                  type="button"
                  class="agent-btn-ghost"
                  on:click={() => $store.principal && loadTokensOnly($store.principal.toString())}
                >
                  Try again
                </button>
              </div>
            {:else if walletData.tokens.length === 0}
              <div class="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-10 text-center">
                <p class="text-sm text-gray-400">No tokens available yet</p>
              </div>
            {:else}
              {#key walletData}
                <WalletTokenList
                  tokens={walletData.tokens}
                  showHeader={false}
                  showOnlyWithBalance={false}
                  isLoading={isDataLoading}
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
  <title>{$store.isAuthed ? `Token balances for ${$store.principal}` : 'Connect to View Wallet'}</title>
</svelte:head>

<script context="module">
  export const Wallet = (props) => {
    return {
      component: Wallet,
      props
    };
  };
</script>
