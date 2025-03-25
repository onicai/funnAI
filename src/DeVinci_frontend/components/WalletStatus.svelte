<script lang="ts">
  // Placeholder values instead of store values
  let isAuthed = false;
  let principal = null;

  // Placeholder function for wallet actions
  function getWalletBalances() {
    console.log('Getting wallet balances...');
  }

  function disconnect() {
    console.log('Disconnecting...');
  }

  function connect() {
    console.log('Connecting...');
  }
</script>

<div class="w-full bg-white card-style p-6 rounded-lg shadow">
  <h2 class="text-xl font-semibold mb-4">Wallet Status</h2>
  <div class="flex flex-col md:flex-row gap-4 items-start">
    <div class="bg-gray-50 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500">Connection Status</div>
      <div class="font-medium text-lg">
        {#if isAuthed}
          <span class="text-green-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Connected ({isAuthed})
          </span>
        {:else}
          <span class="text-red-600 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            Not Connected
          </span>
        {/if}
      </div>
    </div>
    <div class="bg-gray-50 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500">Principal ID</div>
      <div class="font-mono text-sm break-all">
        {principal ? principal.toString() : 'Not available'}
      </div>
    </div>
    <div class="bg-gray-50 p-4 rounded-lg flex-1">
      <div class="text-sm text-gray-500">Wallet Actions</div>
      <div class="flex gap-2 mt-2">
        {#if isAuthed}
          <button 
            on:click={getWalletBalances}
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Balances
          </button>
          <button 
            on:click={disconnect}
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Disconnect
          </button>
        {:else}
          <button 
            on:click={connect}
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Connect Wallet
          </button>
        {/if}
      </div>
    </div>
  </div>
</div> 