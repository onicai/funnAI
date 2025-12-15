<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Check, Copy, RefreshCw, ArrowDownToLine, ArrowUpFromLine, Bitcoin, Loader2, ArrowRight, Wallet, Zap, ExternalLink, Clock, AlertCircle } from 'lucide-svelte';
  import QRCode from 'qrcode';

  import { store } from "../stores/store";
  import { BitcoinService } from "../helpers/BitcoinService";
  import { tooltip } from "../helpers/utils/tooltip";
  import LoadingIndicator from "./LoadingIndicator.svelte";

  // State variables
  let btcDepositAddress = "";
  let btcDepositAddressQr = "";
  let ckbtcBalance: bigint = BigInt(0);
  let isLoadingAddress = false;
  let isLoadingBalance = false;
  let isUpdatingBalance = false;
  let addressCopied = false;
  let error: string | null = null;
  let updateBalanceResult: string | null = null;
  let minterInfo: { min_confirmations: number; retrieve_btc_min_amount: bigint; kyt_fee: bigint } | null = null;

  // Convert BTC flow state
  let showConvertFlow = false;
  let convertAmount = "";
  let isSendingBtc = false;
  let sendSuccess = false;

  // Pending transaction tracking (from localStorage - user initiated)
  interface PendingTx {
    txId: string;
    amount: string;
    timestamp: number;
    confirmations?: number;
  }
  let pendingTx: PendingTx | null = null;
  let autoRefreshInterval: ReturnType<typeof setInterval> | null = null;
  let lastChecked: Date | null = null;

  // Pending deposits detected from ckBTC minter (server-side)
  interface MinterPendingUtxo {
    confirmations: number;
    value: bigint;
    txid: string;
  }
  let minterPendingDeposits: MinterPendingUtxo[] = [];
  let requiredConfirmations: number = 6;
  let currentConfirmations: number = 0;
  let isCheckingPending: boolean = false;

  // Load pending transaction from localStorage on mount
  function loadPendingTx() {
    try {
      const stored = localStorage.getItem(`ckbtc_pending_tx_${$store.principal?.toString()}`);
      if (stored) {
        pendingTx = JSON.parse(stored);
      }
    } catch (e) {
      console.warn("Error loading pending tx:", e);
    }
  }

  function savePendingTx(tx: PendingTx | null) {
    try {
      if (tx) {
        localStorage.setItem(`ckbtc_pending_tx_${$store.principal?.toString()}`, JSON.stringify(tx));
      } else {
        localStorage.removeItem(`ckbtc_pending_tx_${$store.principal?.toString()}`);
      }
    } catch (e) {
      console.warn("Error saving pending tx:", e);
    }
  }

  function clearPendingTx() {
    pendingTx = null;
    savePendingTx(null);
    stopAutoRefresh();
  }

  function startAutoRefresh() {
    if (autoRefreshInterval) return;
    // Auto-check every 2 minutes
    autoRefreshInterval = setInterval(() => {
      if (pendingTx && $store.principal) {
        handleUpdateBalance();
      }
    }, 120000);
  }

  function stopAutoRefresh() {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
  }

  // Calculate estimated time remaining
  function getEstimatedTimeRemaining(): string {
    if (!pendingTx || !minterInfo) return "~1 hour";
    const elapsedMs = Date.now() - pendingTx.timestamp;
    const elapsedMins = Math.floor(elapsedMs / 60000);
    const totalMins = minterInfo.min_confirmations * 10; // ~10 min per block
    const remainingMins = Math.max(0, totalMins - elapsedMins);
    
    if (remainingMins <= 0) return "Any moment now...";
    if (remainingMins < 60) return `~${remainingMins} minutes`;
    return `~${Math.ceil(remainingMins / 60)} hour(s)`;
  }

  $: if (pendingTx) {
    startAutoRefresh();
  }

  // Get wallet provider
  function getWalletProvider(): any {
    const w = window as any;
    if (w.unisat) return { provider: w.unisat, type: 'unisat' };
    if (w.wizz) return { provider: w.wizz, type: 'wizz' };
    if (w.okxwallet?.bitcoin) return { provider: w.okxwallet.bitcoin, type: 'okx' };
    return null;
  }

  $: hasBtcWallet = !!getWalletProvider();
  $: isBitcoinUser = $store.isAuthed === "bitcoin";

  // Load BTC deposit address and ckBTC balance on mount
  onMount(async () => {
    if ($store.principal) {
      loadPendingTx();
      await loadBtcDepositAddress();
      await loadCkbtcBalance();
      await loadMinterInfo();
      // Proactively check for any pending deposits from the minter
      await checkForPendingDeposits();
    }
  });

  onDestroy(() => {
    stopAutoRefresh();
  });

  // Check the ckBTC minter for any pending deposits
  async function checkForPendingDeposits() {
    if (!$store.principal) return;
    
    try {
      isCheckingPending = true;
      console.log("Checking ckBTC minter for pending deposits...");
      
      const result = await BitcoinService.updateCkBtcBalance($store.principal);
      lastChecked = new Date();
      
      if (result.Ok) {
        // Check if any UTXOs were minted
        const mintedUtxos = result.Ok.filter(status => 'Minted' in status);
        if (mintedUtxos.length > 0) {
          const totalMinted = mintedUtxos.reduce((sum, status) => {
            if ('Minted' in status && status.Minted) {
              return sum + BigInt(status.Minted.minted_amount);
            }
            return sum;
          }, BigInt(0));
          
          updateBalanceResult = `✅ Great news! ${BitcoinService.formatSatoshisToBtc(totalMinted)} ckBTC was just minted!`;
          await loadCkbtcBalance();
          clearPendingTx();
        }
      } else if (result.Err && 'NoNewUtxos' in result.Err && result.Err.NoNewUtxos) {
        const noNewUtxos = result.Err.NoNewUtxos as any;
        // pending_utxos is IDL.Opt, so it's wrapped as [array] or []
        const pendingUtxosOpt = noNewUtxos.pending_utxos as any[];
        const pendingUtxos: any[] = pendingUtxosOpt && pendingUtxosOpt.length > 0 ? pendingUtxosOpt[0] : [];
        
        console.log("NoNewUtxos response:", JSON.stringify(noNewUtxos, (k, v) => typeof v === 'bigint' ? v.toString() : v));
        console.log("Pending UTXOs extracted:", pendingUtxos);
        
        if (pendingUtxos && pendingUtxos.length > 0) {
          // We have pending deposits from the minter!
          minterPendingDeposits = pendingUtxos.map(utxo => ({
            confirmations: Number(utxo.confirmations || 0),
            value: BigInt(utxo.value || 0),
            txid: utxo.outpoint?.txid ? bytesToHex(utxo.outpoint.txid) : 'unknown'
          }));
          // current_confirmations is also IDL.Opt
          const currentConfOpt = noNewUtxos.current_confirmations as any[];
          requiredConfirmations = Number(noNewUtxos.required_confirmations || 6);
          currentConfirmations = currentConfOpt && currentConfOpt.length > 0 ? Number(currentConfOpt[0]) : 0;
          
          console.log("Found pending deposits from minter:", minterPendingDeposits);
          startAutoRefresh();
        }
      }
    } catch (err) {
      console.error("Error checking for pending deposits:", err);
      // Don't show error to user, this is a background check
    } finally {
      isCheckingPending = false;
    }
  }

  function bytesToHex(bytes: Uint8Array | number[]): string {
    return Array.from(bytes).reverse().map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Watch for principal changes
  $: if ($store.principal && !btcDepositAddress && !isLoadingAddress) {
    loadBtcDepositAddress();
    loadCkbtcBalance();
  }

  async function loadBtcDepositAddress() {
    if (!$store.principal) return;
    
    try {
      isLoadingAddress = true;
      error = null;
      
      btcDepositAddress = await BitcoinService.getBtcDepositAddress($store.principal);
      
      // Generate QR code for the address
      if (btcDepositAddress) {
        btcDepositAddressQr = await QRCode.toDataURL(`bitcoin:${btcDepositAddress}`);
      }
    } catch (err) {
      console.error("Error loading BTC deposit address:", err);
      error = err instanceof Error ? err.message : "Failed to load BTC deposit address";
    } finally {
      isLoadingAddress = false;
    }
  }

  async function loadCkbtcBalance() {
    if (!$store.principal) return;
    
    try {
      isLoadingBalance = true;
      ckbtcBalance = await BitcoinService.getCkBtcBalance($store.principal);
    } catch (err) {
      console.error("Error loading ckBTC balance:", err);
    } finally {
      isLoadingBalance = false;
    }
  }

  async function loadMinterInfo() {
    try {
      minterInfo = await BitcoinService.getMinterInfo();
    } catch (err) {
      console.error("Error loading minter info:", err);
    }
  }

  async function handleUpdateBalance() {
    if (!$store.principal) return;
    
    try {
      isUpdatingBalance = true;
      updateBalanceResult = null;
      error = null;
      lastChecked = new Date();
      
      const result = await BitcoinService.updateCkBtcBalance($store.principal);
      
      if (result.Ok) {
        // Check if any UTXOs were minted
        const mintedUtxos = result.Ok.filter(status => 'Minted' in status);
        if (mintedUtxos.length > 0) {
          const totalMinted = mintedUtxos.reduce((sum, status) => {
            if ('Minted' in status && status.Minted) {
              return sum + BigInt(status.Minted.minted_amount);
            }
            return sum;
          }, BigInt(0));
          
          updateBalanceResult = `✅ Successfully minted ${BitcoinService.formatSatoshisToBtc(totalMinted)} ckBTC!`;
          await loadCkbtcBalance(); // Refresh the balance
          sendSuccess = false; // Reset send success
          clearPendingTx(); // Clear pending transaction on success
        } else {
          updateBalanceResult = "No new deposits to process.";
        }
      } else if (result.Err) {
        if ('NoNewUtxos' in result.Err && result.Err.NoNewUtxos) {
          const noNewUtxos = result.Err.NoNewUtxos as any;
          // pending_utxos is IDL.Opt, so it's wrapped as [array] or []
          const pendingUtxosOpt = noNewUtxos.pending_utxos as any[];
          const pendingUtxos: any[] = pendingUtxosOpt && pendingUtxosOpt.length > 0 ? pendingUtxosOpt[0] : [];
          
          console.log("handleUpdateBalance - NoNewUtxos:", JSON.stringify(noNewUtxos, (k, v) => typeof v === 'bigint' ? v.toString() : v));
          
          if (pendingUtxos && pendingUtxos.length > 0) {
            const pendingCount = pendingUtxos.length;
            // current_confirmations is also IDL.Opt
            const currentConfOpt = noNewUtxos.current_confirmations as any[];
            currentConfirmations = currentConfOpt && currentConfOpt.length > 0 ? Number(currentConfOpt[0]) : 0;
            requiredConfirmations = Number(noNewUtxos.required_confirmations || 6);
            updateBalanceResult = `⏳ ${pendingCount} pending deposit(s) - ${currentConfirmations}/${requiredConfirmations} confirmations`;
            
            // Update minter pending deposits
            minterPendingDeposits = pendingUtxos.map(utxo => ({
              confirmations: Number(utxo.confirmations || 0),
              value: BigInt(utxo.value || 0),
              txid: utxo.outpoint?.txid ? bytesToHex(utxo.outpoint.txid) : 'unknown'
            }));
            
            // Update pending tx with confirmations if exists
            if (pendingTx) {
              pendingTx = { ...pendingTx, confirmations: currentConfirmations };
              savePendingTx(pendingTx);
            }
          } else {
            updateBalanceResult = "No pending BTC deposits found. It may take a few minutes for Bitcoin network to propagate the transaction.";
            minterPendingDeposits = [];
          }
        } else if ('AlreadyProcessing' in result.Err) {
          updateBalanceResult = "Balance update already in progress. Please wait.";
        } else if ('TemporarilyUnavailable' in result.Err) {
          error = `Temporarily unavailable: ${result.Err.TemporarilyUnavailable}`;
        } else if ('GenericError' in result.Err && result.Err.GenericError) {
          error = `Error: ${result.Err.GenericError.error_message}`;
        }
      }
    } catch (err) {
      console.error("Error updating balance:", err);
      error = err instanceof Error ? err.message : "Failed to update balance";
    } finally {
      isUpdatingBalance = false;
    }
  }

  async function handleSendFromWallet() {
    if (!btcDepositAddress) {
      error = "Deposit address not loaded yet";
      return;
    }

    const wallet = getWalletProvider();
    if (!wallet) {
      error = "No Bitcoin wallet connected";
      return;
    }

    const amountSatoshis = Math.floor(parseFloat(convertAmount || "0") * 100000000);
    if (isNaN(amountSatoshis) || amountSatoshis <= 0) {
      error = "Please enter a valid amount";
      return;
    }

    try {
      isSendingBtc = true;
      error = null;
      
      // Use wallet's sendBitcoin function
      const txid = await wallet.provider.sendBitcoin(btcDepositAddress, amountSatoshis);
      
      console.log("BTC sent! TxID:", txid);
      
      // Store pending transaction
      pendingTx = {
        txId: txid,
        amount: convertAmount,
        timestamp: Date.now(),
        confirmations: 0
      };
      savePendingTx(pendingTx);
      
      sendSuccess = true;
      updateBalanceResult = null;
      showConvertFlow = false;
      convertAmount = "";
      
      // Start auto-refresh
      startAutoRefresh();
      
    } catch (err) {
      console.error("Error sending BTC:", err);
      error = err instanceof Error ? err.message : "Failed to send BTC";
      if (error?.includes("User rejected")) {
        error = "Transaction cancelled by user";
      }
    } finally {
      isSendingBtc = false;
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

  function formatBtcBalance(satoshis: bigint): string {
    return BitcoinService.formatSatoshisToBtc(satoshis);
  }
</script>

<div class="w-full bg-white dark:bg-gray-800 p-6 rounded-lg shadow mb-5">
  <div class="flex items-center justify-between mb-4">
    <div class="flex items-center gap-2">
      <Bitcoin class="w-6 h-6 text-orange-500" />
      <h2 class="text-xl font-semibold dark:text-white">BTC ↔ ckBTC</h2>
    </div>
    {#if $store.btcAddress}
      <div class="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
        <Wallet class="w-4 h-4" />
        {$store.btcAddress.slice(0, 8)}...{$store.btcAddress.slice(-6)}
      </div>
    {/if}
  </div>

  {#if error}
    <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
      <p class="text-red-700 dark:text-red-400 text-sm">{error}</p>
    </div>
  {/if}

  <!-- ckBTC Balance Card -->
  <div class="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800/50">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-1">Your ckBTC Balance</p>
        <div class="flex items-center gap-2">
          {#if isLoadingBalance}
            <Loader2 class="w-5 h-5 animate-spin text-orange-500" />
          {:else}
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {formatBtcBalance(ckbtcBalance)} <span class="text-sm font-normal text-gray-500">ckBTC</span>
            </p>
          {/if}
        </div>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          <Zap class="w-3 h-3 inline" /> Fast, low-fee Bitcoin on ICP
        </p>
      </div>
      <button
        on:click={loadCkbtcBalance}
        class="p-2 hover:bg-orange-100 dark:hover:bg-orange-900/30 rounded-lg transition-colors"
        use:tooltip={{ text: "Refresh balance", direction: "top" }}
      >
        <span class:animate-spin={isLoadingBalance}>
          <RefreshCw class="w-5 h-5 text-orange-600 dark:text-orange-400" />
        </span>
      </button>
    </div>
  </div>

  <!-- Checking for pending deposits indicator -->
  {#if isCheckingPending}
    <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-center gap-2">
      <Loader2 class="w-4 h-4 animate-spin text-blue-600" />
      <span class="text-sm text-blue-700 dark:text-blue-300">Checking for pending BTC deposits...</span>
    </div>
  {/if}

  <!-- Minter-detected Pending Deposits (from ckBTC minter canister) -->
  {#if minterPendingDeposits.length > 0 && !pendingTx}
    <div class="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-lg border-2 border-amber-300 dark:border-amber-700 animate-pulse-slow">
      <div class="flex items-start gap-3">
        <div class="p-2 bg-amber-100 dark:bg-amber-900/50 rounded-full">
          <Clock class="w-6 h-6 text-amber-600 dark:text-amber-400" />
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="font-semibold text-gray-900 dark:text-white">
              🎉 BTC Deposit Detected!
            </h3>
            <span class="text-xs bg-amber-200 dark:bg-amber-800 text-amber-800 dark:text-amber-200 px-2 py-0.5 rounded-full">
              {currentConfirmations}/{requiredConfirmations} confirmations
            </span>
          </div>
          
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
            {minterPendingDeposits.length} deposit(s) waiting for Bitcoin network confirmations.
          </p>

          <!-- List of pending deposits -->
          <div class="space-y-2 mb-3">
            {#each minterPendingDeposits as deposit}
              <div class="p-2 bg-white/50 dark:bg-gray-800/50 rounded flex items-center justify-between">
                <div>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {formatBtcBalance(deposit.value)} BTC
                  </span>
                  <span class="text-xs text-gray-500 ml-2">
                    ({deposit.confirmations} conf.)
                  </span>
                </div>
                {#if deposit.txid && deposit.txid !== 'unknown'}
                  <a
                    href="https://mempool.space/tx/{deposit.txid}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                  >
                    <ExternalLink class="w-3 h-3" />
                    View TX
                  </a>
                {/if}
              </div>
            {/each}
          </div>

          <!-- Progress bar -->
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
            <div 
              class="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full transition-all duration-500"
              style="width: {Math.min(100, (currentConfirmations / requiredConfirmations) * 100)}%"
            ></div>
          </div>

          <div class="flex flex-wrap items-center gap-3">
            <!-- Check Status Button -->
            <button
              on:click={handleUpdateBalance}
              disabled={isUpdatingBalance}
              class="text-sm px-3 py-1.5 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors flex items-center gap-1"
            >
              {#if isUpdatingBalance}
                <Loader2 class="w-4 h-4 animate-spin" />
              {:else}
                <RefreshCw class="w-4 h-4" />
              {/if}
              Check Status & Mint
            </button>

            <!-- View Deposit Address on Explorer -->
            {#if btcDepositAddress}
              <a
                href="https://mempool.space/address/{btcDepositAddress}"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
              >
                <ExternalLink class="w-4 h-4" />
                View Address on Mempool
              </a>
            {/if}
          </div>

          {#if lastChecked}
            <p class="text-xs text-gray-400 mt-2">
              Last checked: {lastChecked.toLocaleTimeString()}
              {#if autoRefreshInterval}
                <span class="ml-2 text-green-600 dark:text-green-400">• Auto-refreshing every 2 min</span>
              {/if}
            </p>
          {/if}

          {#if updateBalanceResult}
            <div class="mt-3 p-2 bg-white/50 dark:bg-gray-800/50 rounded text-sm text-gray-700 dark:text-gray-300">
              {updateBalanceResult}
            </div>
          {/if}
        </div>
      </div>

      <!-- Helpful tips -->
      <div class="mt-4 pt-3 border-t border-amber-200 dark:border-amber-800/50">
        <div class="flex items-start gap-2">
          <AlertCircle class="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
          <p class="text-xs text-gray-600 dark:text-gray-400">
            <strong>Your deposit is being processed!</strong> Bitcoin transactions need {requiredConfirmations} confirmations for security (~{requiredConfirmations * 10} minutes). 
            Once confirmed, click "Check Status & Mint" to receive your ckBTC!
          </p>
        </div>
      </div>
    </div>
  {/if}

  <!-- Quick Convert Section (for users with BTC wallet) -->
  {#if (hasBtcWallet || isBitcoinUser) && !pendingTx && minterPendingDeposits.length === 0}
    <div class="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800/50">
      <div class="flex items-center gap-2 mb-3">
        <ArrowRight class="w-5 h-5 text-green-600 dark:text-green-400" />
        <h3 class="font-medium text-gray-900 dark:text-white">Convert BTC to ckBTC</h3>
      </div>
      
      {#if !showConvertFlow}
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
          Send BTC from your wallet and receive ckBTC on ICP. One-click conversion!
        </p>
        <button
          on:click={() => showConvertFlow = true}
          class="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Bitcoin class="w-5 h-5" />
          Convert BTC → ckBTC
        </button>
      {:else}
        <div class="space-y-3">
          <div>
            <label for="convert-amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Amount (BTC)
            </label>
            <input
              id="convert-amount"
              type="number"
              step="0.00001"
              bind:value={convertAmount}
              placeholder="0.001"
              class="w-full p-2.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            {#if minterInfo}
              <p class="text-xs text-gray-500 mt-1">
                Min deposit: ~0.00001 BTC | Fee: {formatBtcBalance(minterInfo.kyt_fee)} BTC
              </p>
            {/if}
          </div>
          
          <div class="flex gap-2">
            <button
              on:click={handleSendFromWallet}
              disabled={isSendingBtc || !convertAmount}
              class="flex-1 py-2.5 px-4 bg-green-600 hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {#if isSendingBtc}
                <Loader2 class="w-5 h-5 animate-spin" />
                Opening wallet...
              {:else}
                <Wallet class="w-5 h-5" />
                Send from Wallet
              {/if}
            </button>
            <button
              on:click={() => { showConvertFlow = false; convertAmount = ""; }}
              class="px-4 py-2.5 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 font-medium rounded-lg transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Status / Mint Section -->
  {#if sendSuccess || updateBalanceResult}
    <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800/50">
      <div class="flex items-center justify-between mb-3">
        <p class="text-sm text-gray-700 dark:text-gray-300">{updateBalanceResult}</p>
      </div>
      <button
        on:click={handleUpdateBalance}
        disabled={isUpdatingBalance}
        class="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        {#if isUpdatingBalance}
          <Loader2 class="w-5 h-5 animate-spin" />
          Checking for deposits...
        {:else}
          <RefreshCw class="w-5 h-5" />
          Check & Mint ckBTC
        {/if}
      </button>
    </div>
  {/if}

  <!-- Detailed Sections (collapsed by default for cleaner UI) -->
  <details class="group" open>
    <summary class="cursor-pointer text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4 flex items-center gap-2">
      <span class="group-open:rotate-90 transition-transform">▶</span>
      Manual Deposit Options
    </summary>
    
    <div class="grid md:grid-cols-2 gap-6 mt-4">
      <!-- Deposit Address -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="flex items-center gap-2 mb-3">
          <ArrowDownToLine class="w-5 h-5 text-green-600 dark:text-green-400" />
          <h3 class="font-medium text-gray-900 dark:text-white">Deposit Address</h3>
        </div>
        
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
          Send BTC from any wallet to this address.
        </p>

        {#if isLoadingAddress}
          <div class="flex items-center justify-center py-4">
            <LoadingIndicator text="Loading address..." size={20} />
          </div>
        {:else if btcDepositAddress}
          <div class="space-y-3">
            <!-- QR Code -->
            {#if btcDepositAddressQr}
              <div class="flex justify-center">
                <img 
                  src={btcDepositAddressQr} 
                  alt="BTC Deposit Address QR" 
                  class="w-28 h-28 bg-white rounded-lg p-2"
                />
              </div>
            {/if}

            <!-- Address -->
            <div class="relative">
              <div class="p-2.5 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 font-mono text-xs break-all pr-10">
                {btcDepositAddress}
              </div>
              <button
                on:click={() => copyToClipboard(btcDepositAddress)}
                class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
                use:tooltip={{ text: addressCopied ? "Copied!" : "Copy address", direction: "top" }}
              >
                {#if addressCopied}
                  <Check class="w-4 h-4 text-green-500" />
                {:else}
                  <Copy class="w-4 h-4 text-gray-500" />
                {/if}
              </button>
            </div>

            <!-- Minter Info -->
            {#if minterInfo}
              <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                <p>Confirmations needed: {minterInfo.min_confirmations}</p>
                <p>Fee: {formatBtcBalance(minterInfo.kyt_fee)} BTC</p>
              </div>
            {/if}
          </div>
        {:else}
          <p class="text-sm text-gray-500">Unable to load deposit address</p>
        {/if}
      </div>

      <!-- Mint ckBTC Section -->
      <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="flex items-center gap-2 mb-3">
          <RefreshCw class="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h3 class="font-medium text-gray-900 dark:text-white">Claim ckBTC</h3>
        </div>
        
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          After sending BTC, claim your ckBTC once confirmations complete.
        </p>

        <button
          on:click={handleUpdateBalance}
          disabled={isUpdatingBalance}
          class="text-sm px-3 py-1.5 bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors flex items-center gap-1"
        >
          {#if isUpdatingBalance}
            <Loader2 class="w-5 h-5 animate-spin" />
            Checking...
          {:else}
            <RefreshCw class="w-5 h-5" />
            Check Status & Mint
          {/if}
        </button>

        <!-- How it works -->
        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
          <h4 class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">How it works:</h4>
          <ol class="text-xs text-gray-500 dark:text-gray-400 space-y-1 list-decimal list-inside">
            <li>Send BTC to the deposit address</li>
            <li>Wait for {minterInfo?.min_confirmations || 6} confirmations (~1 hour)</li>
            <li>Click "Check & Mint" to receive ckBTC</li>
          </ol>
        </div>
      </div>
    </div>
  </details>

  <!-- Withdraw BTC Section (Future enhancement) -->
  <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg opacity-60">
    <div class="flex items-center gap-2 mb-2">
      <ArrowUpFromLine class="w-5 h-5 text-orange-600 dark:text-orange-400" />
      <h3 class="font-medium text-gray-900 dark:text-white">Convert ckBTC to BTC</h3>
      <span class="text-xs bg-orange-100 dark:bg-orange-900/50 text-gray-700 dark:text-gray-100 px-2 py-0.5 rounded">Coming Soon</span>
    </div>
    <p class="text-sm text-gray-500 dark:text-gray-400">
      Convert your ckBTC back to BTC on the Bitcoin network.
    </p>
  </div>
</div>

<style>
  /* Slow pulse animation for pending transaction card */
  .animate-pulse-slow {
    animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  
  @keyframes pulse-slow {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.85;
    }
  }
</style>

