<script lang="ts">
  import LoginModal from './LoginModal.svelte';
  import { store } from "../stores/store";

  let modalIsOpen = false;

  // Placeholder function for wallet actions
  function getWalletBalances() {
    console.log('Getting wallet balances...');
  }

  async function disconnect() {
    await store.disconnect();
  }

  function connect() {
    toggleModal();
  }

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };
</script>

<div class="w-full bg-white dark:bg-gray-800 card-style p-6 rounded-lg shadow">
  <h2 class="text-xl font-semibold mb-4 dark:text-white">Wallet Status</h2>
  <div class="flex flex-col md:flex-row gap-4 items-start">
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500 dark:text-gray-400">Connection Status</div>
      <div class="font-medium text-lg">
        {#if $store.isAuthed}
          <span class="text-green-600 dark:text-green-500 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Connected
          </span>
        {:else}
          <span class="text-red-600 dark:text-red-500 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            Not Connected
          </span>
        {/if}
      </div>
    </div>
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500 dark:text-gray-400">Principal ID</div>
      <div class="font-mono text-sm break-all dark:text-gray-300">
        {$store.principal ? $store.principal.toString() : 'Not available'}
      </div>
    </div>
    <div class="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500 dark:text-gray-400">Wallet Actions</div>
      <div class="flex gap-2 mt-2">
        {#if $store.isAuthed}
          <button
            on:click={getWalletBalances}
            class="text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800"
          >
            Refresh Balances
          </button>
          <button
            on:click={disconnect}
            class="text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800"
          >
            Disconnect
          </button>
        {:else}
          <button
            on:click={connect}
            class="text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800"
          >
            Connect Wallet
          </button>
        {/if}
      </div>
    </div>
  </div>
</div>

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if} 