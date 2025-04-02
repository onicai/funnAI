<script lang="ts">
  import WalletTable from '../components/WalletTable.svelte';
  import WalletStatus from '../components/WalletStatus.svelte';
  import LoginModal from '../components/LoginModal.svelte';
  import { store } from "../store";
  
  let modalIsOpen = false;
  
  const transactions = [
    {
      coin: "Internet Computer",
      symbol: "ICP",
      amount: "11.15",
      icon: "/icp-rounded.svg"
    },
    {
      coin: "FunnAI",
      symbol: "FUNN",
      amount: "1110.4",
      icon: "/coin.webp"
    }
  ];

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  function connect() {
    toggleModal();
  }
</script>

<div class="container mx-auto px-8 py-8">
  <h1 class="text-2xl text-gray-400 dark:text-gray-300 font-bold mb-6">Wallet</h1>
  
  <div class="flex flex-col justify-center">
      <WalletStatus />
    <div class="w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow mt-5">
      <h2 class="text-xl font-semibold mb-4 dark:text-white">Your Assets</h2>
      {#if $store.isAuthed}
        <WalletTable {transactions} />
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

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}

<script context="module">
  export const Wallet = (props) => {
    return {
      component: Wallet,
      props
    };
  };
</script> 