<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Check, Copy, ArrowUp, ArrowDown } from 'lucide-svelte';
  import QRCode from 'qrcode';

  import { store } from "../stores/store";
  import { tooltip } from "../helpers/utils/tooltip";
  import LoadingIndicator from "./LoadingIndicator.svelte";

  // State variables
  let btcBalance: number = 0;
  let btcAddress: string = "";
  let isLoadingBalance = false;
  let showReceiveModal = false;
  let showSendModal = false;
  let addressCopied = false;
  let addressQr = "";

  // Send modal state
  let sendToAddress = "";
  let sendAmount = "";
  let isSending = false;
  let sendError: string | null = null;
  let sendSuccess: string | null = null;

  // Get wallet provider
  function getWalletProvider(): any {
    const w = window as any;
    if (w.unisat) return { provider: w.unisat, type: 'unisat' };
    if (w.wizz) return { provider: w.wizz, type: 'wizz' };
    if (w.okxwallet?.bitcoin) return { provider: w.okxwallet.bitcoin, type: 'okx' };
    return null;
  }

  // Load balance and address from wallet
  async function loadWalletInfo() {
    const wallet = getWalletProvider();
    if (!wallet) return;

    try {
      isLoadingBalance = true;
      
      // Get accounts/address
      const accounts = await wallet.provider.getAccounts();
      if (accounts && accounts.length > 0) {
        btcAddress = accounts[0];
      }

      // Get balance (in satoshis)
      const balanceResult = await wallet.provider.getBalance();
      if (balanceResult && typeof balanceResult.confirmed !== 'undefined') {
        // Some wallets return { confirmed, unconfirmed, total }
        btcBalance = (balanceResult.confirmed + (balanceResult.unconfirmed || 0)) / 100000000;
      } else if (typeof balanceResult === 'number') {
        btcBalance = balanceResult / 100000000;
      }
    } catch (err) {
      console.error("Error loading BTC wallet info:", err);
    } finally {
      isLoadingBalance = false;
    }
  }

  // Generate QR code for address
  async function generateQr() {
    if (btcAddress) {
      try {
        addressQr = await QRCode.toDataURL(`bitcoin:${btcAddress}`);
      } catch (err) {
        console.error("Error generating QR code:", err);
      }
    }
  }

  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      addressCopied = true;
      setTimeout(() => addressCopied = false, 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  }

  async function handleSend() {
    const wallet = getWalletProvider();
    if (!wallet) {
      sendError = "No Bitcoin wallet connected";
      return;
    }

    if (!sendToAddress || !sendAmount) {
      sendError = "Please enter recipient address and amount";
      return;
    }

    const amountSatoshis = Math.floor(parseFloat(sendAmount) * 100000000);
    if (isNaN(amountSatoshis) || amountSatoshis <= 0) {
      sendError = "Invalid amount";
      return;
    }

    try {
      isSending = true;
      sendError = null;
      sendSuccess = null;

      // Use wallet's sendBitcoin function
      const txid = await wallet.provider.sendBitcoin(sendToAddress, amountSatoshis);
      
      sendSuccess = `Transaction sent! TxID: ${txid.slice(0, 16)}...`;
      
      // Refresh balance after a delay
      setTimeout(() => {
        loadWalletInfo();
        showSendModal = false;
        sendToAddress = "";
        sendAmount = "";
        sendSuccess = null;
      }, 3000);
    } catch (err) {
      console.error("Error sending BTC:", err);
      sendError = err instanceof Error ? err.message : "Failed to send BTC";
    } finally {
      isSending = false;
    }
  }

  // Check if user is logged in with Bitcoin wallet (SIWB)
  $: isBitcoinUser = $store.isAuthed === "bitcoin";
  
  // Only check for active wallet connection if user logged in with Bitcoin
  // Having an extension installed doesn't mean the user wants to use BTC features
  $: hasBtcWallet = isBitcoinUser && !!getWalletProvider();

  // Load wallet info only when user is authenticated via Bitcoin wallet
  onMount(() => {
    if (isBitcoinUser) {
      loadWalletInfo();
    }
  });

  $: if (showReceiveModal && btcAddress && !addressQr) {
    generateQr();
  }
</script>

{#if isBitcoinUser}
  <div class="sm:grid sm:grid-cols-[2fr,1.5fr,1fr] sm:gap-4 sm:items-center p-4 hover:bg-zinc-800/30 transition-colors border-y border-gray-700">
    <!-- Mobile display -->
    <div class="flex flex-col gap-3 sm:hidden">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <!-- Bitcoin Logo -->
          <div class="w-7 h-7 rounded-full overflow-hidden flex items-center justify-center bg-orange-500">
            <svg class="w-5 h-5" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <path fill="#FFF" d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.113-.92-.22-1.385-.326l.695-2.783-1.728-.431-.709 2.84c-.376-.086-.744-.17-1.101-.259l.002-.01-2.384-.595-.46 1.847s1.283.294 1.256.312c.7.175.827.638.806 1.006l-.807 3.238c.048.012.11.03.18.057l-.183-.046-1.132 4.538c-.086.213-.303.533-.793.412.018.025-1.256-.313-1.256-.313l-.858 1.978 2.25.561c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.709-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z"/>
            </svg>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-1">
              <span class="font-semibold text-gray-900 dark:text-gray-100">BTC</span>
              <span class="text-xs bg-orange-100 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300 px-1.5 py-0.5 rounded">Native</span>
            </div>
            <span class="text-xs text-gray-600 dark:text-gray-400">Bitcoin</span>
          </div>
        </div>
        <div class="text-right">
          <div class="font-medium text-gray-900 dark:text-gray-100">
            {#if isLoadingBalance}
              <span class="text-gray-400">Loading...</span>
            {:else}
              {btcBalance.toFixed(8)} BTC
            {/if}
          </div>
        </div>
      </div>
    </div>

    <!-- Desktop token column -->
    <div class="hidden sm:flex items-center gap-3">
      <!-- Bitcoin Logo -->
      <div class="w-[38px] h-[38px] rounded-full overflow-hidden flex items-center justify-center bg-orange-500">
        <svg class="w-6 h-6" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
          <path fill="#FFF" d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.113-.92-.22-1.385-.326l.695-2.783-1.728-.431-.709 2.84c-.376-.086-.744-.17-1.101-.259l.002-.01-2.384-.595-.46 1.847s1.283.294 1.256.312c.7.175.827.638.806 1.006l-.807 3.238c.048.012.11.03.18.057l-.183-.046-1.132 4.538c-.086.213-.303.533-.793.412.018.025-1.256-.313-1.256-.313l-.858 1.978 2.25.561c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.709-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z"/>
        </svg>
      </div>
      <div class="flex flex-col">
        <div class="flex items-center gap-1">
          <span class="font-semibold text-gray-900 dark:text-gray-100">BTC</span>
          <span class="text-xs bg-orange-100 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300 px-1.5 py-0.5 rounded">Native</span>
        </div>
        <span class="text-xs text-gray-600 dark:text-gray-400">Bitcoin</span>
      </div>
    </div>

    <!-- Desktop balance column -->
    <div class="hidden sm:block text-right">
      <div class="font-medium text-gray-900 dark:text-gray-100">
        {#if isLoadingBalance}
          <span class="text-gray-400">Loading...</span>
        {:else}
          {btcBalance.toFixed(8)} BTC
        {/if}
      </div>
    </div>

    <!-- Desktop actions column -->
    <div class="hidden sm:block text-right">
      <div class="flex justify-end gap-2">
        <button
          on:click={() => showReceiveModal = true}
          class="text-sm font-medium px-3 py-1.5 bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition"
        >
          Receive
        </button>
        <button
          on:click={() => showSendModal = true}
          class="text-sm font-medium px-3 py-1.5 bg-orange-600 text-white hover:bg-orange-500 dark:bg-orange-500 dark:hover:bg-orange-400 rounded-lg transition"
        >
          Send
        </button>
      </div>
    </div>

    <!-- Mobile buttons -->
    <div class="flex sm:hidden justify-end gap-2 mt-4">
      <button
        on:click={() => showReceiveModal = true}
        class="text-sm font-medium px-3 py-1.5 bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition"
      >
        Receive
      </button>
      <button
        on:click={() => showSendModal = true}
        class="text-sm font-medium px-3 py-1.5 bg-orange-600 text-white hover:bg-orange-500 dark:bg-orange-500 dark:hover:bg-orange-400 rounded-lg transition"
      >
        Send
      </button>
    </div>
  </div>
{/if}

<!-- Receive Modal -->
{#if showReceiveModal}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
  <div 
    class="fixed inset-0 bg-black/60 z-[10000] flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="receive-modal-title"
    on:click={() => showReceiveModal = false}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div 
      class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-2xl"
      on:click|stopPropagation
    >
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center">
            <svg class="w-5 h-5" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <path fill="#FFF" d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.113-.92-.22-1.385-.326l.695-2.783-1.728-.431-.709 2.84c-.376-.086-.744-.17-1.101-.259l.002-.01-2.384-.595-.46 1.847s1.283.294 1.256.312c.7.175.827.638.806 1.006l-.807 3.238c.048.012.11.03.18.057l-.183-.046-1.132 4.538c-.086.213-.303.533-.793.412.018.025-1.256-.313-1.256-.313l-.858 1.978 2.25.561c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.709-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z"/>
            </svg>
          </div>
          <h3 id="receive-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">Receive BTC</h3>
        </div>
        <button 
          on:click={() => showReceiveModal = false}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-1"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="space-y-4">
        <!-- QR Code -->
        {#if addressQr}
          <div class="flex justify-center">
            <img 
              src={addressQr} 
              alt="Bitcoin Address QR" 
              class="w-48 h-48 bg-white rounded-lg p-2"
            />
          </div>
        {/if}

        <!-- Address -->
        <div>
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Bitcoin Address</p>
          <div class="relative">
            <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 font-mono text-sm break-all text-gray-900 dark:text-gray-100">
              {btcAddress || "No address available"}
            </div>
            {#if btcAddress}
              <button
                on:click={() => copyToClipboard(btcAddress)}
                class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                use:tooltip={{ text: addressCopied ? "Copied!" : "Copy address", direction: "top" }}
              >
                {#if addressCopied}
                  <Check class="w-4 h-4 text-green-500" />
                {:else}
                  <Copy class="w-4 h-4 text-gray-500 dark:text-gray-400" />
                {/if}
              </button>
            {/if}
          </div>
        </div>

        <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
          Send only BTC to this address. Sending other assets may result in permanent loss.
        </p>
      </div>
    </div>
  </div>
{/if}

<!-- Send Modal -->
{#if showSendModal}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
  <div 
    class="fixed inset-0 bg-black/60 z-[10000] flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="send-modal-title"
    on:click={() => showSendModal = false}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div 
      class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full shadow-2xl"
      on:click|stopPropagation
    >
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center">
            <svg class="w-5 h-5" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <path fill="#FFF" d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.113-.92-.22-1.385-.326l.695-2.783-1.728-.431-.709 2.84c-.376-.086-.744-.17-1.101-.259l.002-.01-2.384-.595-.46 1.847s1.283.294 1.256.312c.7.175.827.638.806 1.006l-.807 3.238c.048.012.11.03.18.057l-.183-.046-1.132 4.538c-.086.213-.303.533-.793.412.018.025-1.256-.313-1.256-.313l-.858 1.978 2.25.561c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.709-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z"/>
            </svg>
          </div>
          <h3 id="send-modal-title" class="text-lg font-semibold text-gray-900 dark:text-white">Send BTC</h3>
        </div>
        <button 
          on:click={() => showSendModal = false}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-1"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="space-y-4">
        <!-- Balance -->
        <div class="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <span class="text-sm text-gray-500 dark:text-gray-400">Available:</span>
          <span class="ml-2 font-medium text-gray-900 dark:text-white">{btcBalance.toFixed(8)} BTC</span>
        </div>

        <!-- Recipient Address -->
        <div>
          <label for="send-address" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Recipient Address
          </label>
          <input
            id="send-address"
            type="text"
            bind:value={sendToAddress}
            placeholder="bc1q..."
            class="w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>

        <!-- Amount -->
        <div>
          <label for="send-amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Amount (BTC)
          </label>
          <div class="relative">
            <input
              id="send-amount"
              type="number"
              step="0.00000001"
              bind:value={sendAmount}
              placeholder="0.00000000"
              on:wheel={(e) => e.preventDefault()}
              class="w-full p-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
            <button
              on:click={() => sendAmount = btcBalance.toFixed(8)}
              class="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-orange-600 hover:text-orange-700 font-medium"
            >
              MAX
            </button>
          </div>
        </div>

        {#if sendError}
          <div class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-700 dark:text-red-400">{sendError}</p>
          </div>
        {/if}

        {#if sendSuccess}
          <div class="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <p class="text-sm text-green-700 dark:text-green-400">{sendSuccess}</p>
          </div>
        {/if}

        <!-- Send Button -->
        <button
          on:click={handleSend}
          disabled={isSending || !sendToAddress || !sendAmount}
          class="w-full py-3 px-4 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {#if isSending}
            <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sending...
          {:else}
            <ArrowUp class="w-5 h-5" />
            Send BTC
          {/if}
        </button>

        <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
          This will open your Bitcoin wallet to confirm the transaction.
        </p>
      </div>
    </div>
  </div>
{/if}
