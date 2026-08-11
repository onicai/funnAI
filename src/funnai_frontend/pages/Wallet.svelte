<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';

  import WalletStatus from '../components/funnai/WalletStatus.svelte';
  import LoginModal from '../components/login/LoginModal.svelte';
  import WalletTokenList from "../components/WalletTokenList.svelte";
  import TokenListSkeleton from "../components/TokenListSkeleton.svelte";
  import LoadingIndicator from "../components/LoadingIndicator.svelte";
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

      <div class="agent-card !bg-agent-surface p-5 sm:p-6">
        <div class="relative z-[1]">
          <p class="agent-eyebrow">Holdings</p>
          <h2 class="mt-0.5 text-base font-semibold tracking-tight text-white mb-4">Your assets</h2>

          {#if $store.isAuthed}
            <div class="min-h-[340px] relative">
              {#if isDataLoading}
                <TokenListSkeleton rows={4} />
                <div class="absolute inset-0 bg-agent-surface/80 flex items-center justify-center rounded-xl">
                  <LoadingIndicator text={"Loading wallet data..."} size={24} />
                </div>
              {:else if loadingError}
                <div class="flex flex-col items-center justify-center py-12">
                  <div class="text-red-300 mb-4 text-center text-sm">{loadingError}</div>
                  <button
                    type="button"
                    class="agent-btn-ghost"
                    on:click={() => $store.principal && loadTokensOnly($store.principal.toString())}
                  >
                    Try again
                  </button>
                </div>
              {:else if walletData.tokens.length === 0}
                <div class="flex flex-col items-center justify-center py-12">
                  <LoadingIndicator text="Please connect your wallet..." size={24} />
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
            </div>
          {:else}
            <div class="text-center py-10 rounded-xl border border-white/[0.06] bg-white/[0.03]">
              <h3 class="text-lg font-semibold tracking-tight text-white">Connect your wallet</h3>
              <p class="mt-1 text-sm text-gray-400">Connect to view your assets</p>
              <button type="button" on:click={connect} class="agent-btn-primary mt-5">
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
