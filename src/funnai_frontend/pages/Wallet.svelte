<script lang="ts">
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';
  import { Coins, DollarSign, TrendingUp, ArrowUp, ArrowDown } from "lucide-svelte";

  import WalletStatus from '../components/funnai/WalletStatus.svelte';
  import LoginModal from '../components/login/LoginModal.svelte';
  import WalletTokenList from "../components/WalletTokenList.svelte";
  import TokenListSkeleton from "../components/TokenListSkeleton.svelte";
  import LoadingIndicator from "../components/LoadingIndicator.svelte";
  import LoadingEllipsis from "../components/LoadingEllipsis.svelte";
  import Footer from "../components/funnai/Footer.svelte";

  import { store } from "../stores/store";
  import { WalletDataService, walletDataStore } from "../helpers/WalletDataService";

  // State variables
  let modalIsOpen = false;
  let isLoading = false;
  let isLoadingHistory = false;
  let loadingError: string | null = null;
  let hasAttemptedTokenLoad = false;

  // Reactive derived values
  //$: walletData = get(walletDataStore);
  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: tokensWithBalance = walletData.tokens.filter(token => {
    const balance = walletData.balances[token.canister_id];
    return balance && Number(balance.in_tokens || "0") > 0;
  }) || [];

  // $: totalTokenValue = Object.values(walletData.balances).reduce(
  //   (sum: number, balance) => sum + Number(balance?.in_usd || "0"),
  //   0
  // );

  $: isDataLoading =
    isLoading ||
    isLoadingHistory ||
    walletData.isLoading /* ||
    (walletData.tokens.length > 0 && Object.keys(walletData.balances).length === 0) */;

  // Format currency 
  function formatCurrency(value: number): string {
    return value.toLocaleString('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2 
    });
  };

  // Format percentage
  function formatPercentage(value: number): string {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  // Load wallet data
  async function loadTokensOnly(principalId: string) {
    if (isLoading || !principalId) return;
    
    try {
      isLoading = true;
      loadingError = null;
      
      await WalletDataService.loadTokensOnly(principalId);
      console.log(`Loaded tokens for wallet ${principalId}`);
    } catch (error) {
      console.error("Failed to load tokens:", error);
      loadingError = error instanceof Error ? error.message : "Failed to load token metadata";
    } finally {
      isLoading = false;
    }
  };

  $: {
    const principal = $store.principal;
    const walletState = get(walletDataStore); // Use store via get()

    const hasBalances = Object.keys(walletState.balances).length > 0;
    const hasTokens = walletState.tokens.length > 0;
    const isStoreLoading = walletState.isLoading;

    // Update local error state
    loadingError = walletState.error;

    // Update local loading state
    const shouldBeLoading = isStoreLoading;
    if (isLoading !== shouldBeLoading) {
      isLoading = shouldBeLoading;
    }

    if (principal && walletState.currentWallet === principal.toString() && !isStoreLoading && hasTokens && !hasBalances) {
      console.log(`Tokens page: Have tokens, no balances for ${principal}. Waiting.`);
    } else if (principal && walletState.currentWallet !== principal.toString() && !isStoreLoading) {
      console.log(`Tokens page: Store loaded for ${walletState.currentWallet}, expecting ${principal}. Waiting for layout.`);
    } else if (isStoreLoading) {
      console.log(`Tokens page: Wallet store is loading for ${walletState.currentWallet}. Waiting.`);
    }
  };

  $: if ($store.isAuthed) {
    WalletDataService.initializeWallet($store.principal.toString());
  }

  onMount(async () => {
    console.log("in Wallet $store.principal.toString() ", $store?.principal?.toString());
    await WalletDataService.initializeWallet($store?.principal?.toString());
    console.log("in Wallet walletData ", walletData);
  });


  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  function connect() {
    toggleModal();
  };
</script>
    <div class="container mx-auto px-8 py-8">
        <h1 class="text-2xl text-gray-400 dark:text-gray-300 font-bold mb-6">Wallet</h1>
        
        <div class="flex flex-col justify-center">
            <WalletStatus />
            <div class="w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
                <h2 class="text-xl font-semibold mb-4 dark:text-white">Your Assets</h2>
                {#if $store.isAuthed}
                    <!-- <WalletTable {transactions} /> -->

                    <!-- Content with consistent height to prevent flickering -->
                    <div class="min-h-[400px] relative">
                        {#if isDataLoading}
                            <!-- Show skeleton immediately with loading overlay -->
                            <TokenListSkeleton rows={4} />
                            <div class="absolute inset-0 bg-gray-800/80 flex items-center justify-center">
                                <LoadingIndicator text={"Loading wallet data..."} size={24} />
                            </div>
                        {:else if loadingError}
                            <div class="flex flex-col items-center justify-center py-12">
                                <div class="text-red-500 mb-4 text-center">{loadingError}</div>
                                <button
                                    class="text-sm text-blue-600 hover:opacity-80 transition-colors px-4 py-2 bg-gray-800 rounded-lg"
                                    on:click={() => $store.principal && loadTokensOnly($store.principal.toString())}
                                >
                                    Try Again
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
                    <div class="text-center py-8 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        <h3 class="mt-2 text-lg font-medium text-gray-600 dark:text-gray-200">Connect your wallet</h3>
                        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Please connect your wallet to view your assets</p>
                        <button 
                            on:click={connect}
                            class="mt-4 text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800 font-medium rounded-lg text-sm px-5 py-2.5"
                        >
                            Connect Wallet
                        </button>
                    </div>
                {/if}
            </div>
        </div>
    </div>

<Footer />

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}

<svelte:head>
  <title>{$store.isAuthed ? `Token balances for ${$store.principal}` : 'Connect to View Wallet'}</title>
</svelte:head>

<!-- 
<div class="container mx-auto px-8 py-8 bg-white dark:bg-gray-900 ">
  Tokens Overview Panel 

    <div class="flex items-center justify-between  mx-auto w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
      <h3 class="text-sm uppercase font-medium text-gray-100">Tokens Overview</h3>
      <div class="p-2 rounded-lg">
        <Coins class="w-3 h-3 text-blue-600" />
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-3 sm:gap-6  w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
      <div class="flex flex-col p-3 sm:p-4 rounded-lg">
        <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
          <DollarSign class="w-3 h-3 sm:w-4 sm:h-4" />
          <span>Total Value</span>
        </div>
        <div class="text-lg sm:text-xl font-medium">
          {#if isDataLoading}
            <span class="flex items-center">
              <LoadingEllipsis color="text-gray-100" size="text-lg" />
            </span>
          {:else}
            {formatCurrency(totalTokenValue)}
          {/if}
        </div>
      </div>

      <div class="flex flex-col p-3 sm:p-4 w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
        <div class="flex items-center gap-2 text-gray-400 text-sm mb-1">
          <Coins class="w-3 h-3 sm:w-4 sm:h-4" />
          <span>Active Tokens</span>
        </div>
        <div class="text-lg sm:text-xl font-medium">
          {#if isDataLoading}
            <span class="flex items-center">
              <LoadingEllipsis color="text-gray-100" size="text-lg" />
            </span>
          {:else}
            {tokensWithBalance.length}
          {/if}
        </div>
      </div>
    </div>

    -->


  <!-- Token List Panel -->
 <!-- 
    <div class="flex flex-col gap-4  w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
     <!-- Header with Filter Toggle 
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm uppercase font-medium text-gray-100">Token Balances</h3>
        <div class="p-2 rounded-lg">
          <Coins class="w-3 h-3 text-blue-600" />
        </div>
      </div>
      -->

      <!-- Content
      {#if isDataLoading}
        <h3 class="text-sm uppercase font-medium text-gray-100">isDataLoading</h3>
        <LoadingIndicator text={"Loading wallet data..."} size={24} />
      {:else if loadingError}
        <h3 class="text-sm uppercase font-medium text-gray-100">loadingError</h3>
        <div class="text-red-500 mb-4">{loadingError}</div>
        <button
          class="text-sm text-blue-600 hover:opacity-80 transition-colors"
          on:click={() => $store.principal && loadTokensOnly($store.principal.toString())}
        >
          Try Again
        </button>
      {:else if walletData.tokens.length === 0}
        <h3 class="text-sm uppercase font-medium text-gray-100">no tokens</h3>
        <LoadingIndicator text="Please connect your wallet..." size={24} />
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
     

</div>
-->

<script context="module">
  export const Wallet = (props) => {
    return {
      component: Wallet,
      props
    };
  };
</script> 