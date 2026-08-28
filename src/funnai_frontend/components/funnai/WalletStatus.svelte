<script lang="ts">
  import { RefreshCw, Copy, Check, LogOut, Wallet } from '@lucide/svelte';
  import LoginModal from '../login/LoginModal.svelte';
  import { store } from "../../stores/store";
  import { WalletDataService } from "../../helpers/WalletDataService";

  let modalIsOpen = false;
  let isRefreshingBalances = false;
  let copySuccess = false;
  let showFullPrincipal = false;
  let refreshFeedback: 'updated' | 'unchanged' | 'failed' | null = null;
  let refreshFeedbackTimer: ReturnType<typeof setTimeout> | null = null;

  async function getWalletBalances() {
    if (!$store.principal || !$store.isAuthed) return;
    if (isRefreshingBalances) return;

    isRefreshingBalances = true;
    refreshFeedback = null;
    try {
      const result = await WalletDataService.refreshBalances(true);
      refreshFeedback = result;
      if (refreshFeedbackTimer) clearTimeout(refreshFeedbackTimer);
      refreshFeedbackTimer = setTimeout(() => {
        refreshFeedback = null;
      }, 4000);
    } catch (error) {
      console.error('Error refreshing wallet balances:', error);
      refreshFeedback = 'failed';
    } finally {
      isRefreshingBalances = false;
    }
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

  async function copyPrincipalId() {
    if (!$store.principal) return;
    try {
      await navigator.clipboard.writeText($store.principal.toString());
      copySuccess = true;
      setTimeout(() => {
        copySuccess = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy principal ID:', err);
    }
  }

  function truncatePrincipal(principal: string, maxLength: number = 28): string {
    if (principal.length <= maxLength) return principal;
    const start = Math.floor((maxLength - 3) / 2);
    const end = Math.ceil((maxLength - 3) / 2);
    return principal.slice(0, start) + '…' + principal.slice(-end);
  }

  $: principalText = $store.principal ? $store.principal.toString() : '';
</script>

<div class="agent-card bg-agent-surface! overflow-hidden">
  <div class="relative z-1">
    {#if $store.isAuthed && principalText}
      <!-- Identity header -->
      <div class="flex items-start sm:items-center gap-3 sm:gap-4 p-5 sm:p-6 pb-4 sm:pb-5">
        <div class="relative shrink-0">
          <div class="flex h-12 w-12 items-center justify-center rounded-2xl border border-agent-purple/35 bg-agent-purple/15 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
            <Wallet class="h-5 w-5 text-[#c4b5fd]" />
          </div>
          <span class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-agent-surface bg-emerald-400"></span>
        </div>

        <div class="min-w-0 flex-1">
          <div class="flex flex-wrap items-center gap-2">
            <p class="agent-eyebrow">Account</p>
            <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
              <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse"></span>
              Live
            </span>
          </div>
          <h2 class="mt-1 text-base font-semibold tracking-tight text-white">Wallet connected</h2>
          <p class="mt-0.5 text-sm text-gray-500">Your principal on the Internet Computer</p>
        </div>

        <div class="hidden sm:flex items-center gap-1.5 shrink-0">
          <button
            type="button"
            on:click={getWalletBalances}
            disabled={isRefreshingBalances}
            class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/10 bg-white/4 text-gray-300 transition-all hover:border-agent-purple/40 hover:bg-agent-purple/10 hover:text-white disabled:opacity-40"
            title={isRefreshingBalances ? 'Refreshing…' : refreshFeedback === 'updated' ? 'Balances updated' : refreshFeedback === 'unchanged' ? 'Balances unchanged' : refreshFeedback === 'failed' ? 'Refresh failed' : 'Refresh balances'}
          >
            <RefreshCw class="h-3.5 w-3.5 {isRefreshingBalances ? 'animate-spin' : ''}" />
          </button>
          <button
            type="button"
            on:click={disconnect}
            class="inline-flex h-9 items-center gap-1.5 rounded-full border border-red-500/20 bg-red-500/8 px-3 text-[13px] font-medium text-red-300 transition-all hover:border-red-400/35 hover:bg-red-500/15 hover:text-red-200"
            title="Disconnect"
          >
            <LogOut class="h-3.5 w-3.5" />
            Disconnect
          </button>
        </div>
      </div>

      <!-- Principal strip -->
      <div class="px-5 sm:px-6 pb-5 sm:pb-6">
        <div class="rounded-xl border border-white/8 bg-linear-to-b from-white/4 to-transparent p-3.5 sm:p-4">
          <div class="flex items-center justify-between gap-3 mb-2">
            <span class="text-[11px] font-medium uppercase tracking-[0.16em] text-gray-500">Principal ID</span>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="sm:hidden text-[11px] font-medium text-[#a78bfa] hover:text-white transition-colors"
                on:click={() => showFullPrincipal = !showFullPrincipal}
              >
                {showFullPrincipal ? 'Hide' : 'Show full'}
              </button>
              <button
                type="button"
                on:click={copyPrincipalId}
                class="inline-flex h-7 items-center gap-1.5 rounded-full border border-white/10 bg-white/4 px-2.5 text-[11px] font-medium text-gray-300 transition-all hover:border-agent-purple/40 hover:bg-agent-purple/10 hover:text-white"
                title={copySuccess ? 'Copied!' : 'Copy principal'}
              >
                {#if copySuccess}
                  <Check class="h-3 w-3 text-emerald-400" />
                  <span class="text-emerald-400">Copied</span>
                {:else}
                  <Copy class="h-3 w-3" />
                  Copy
                {/if}
              </button>
            </div>
          </div>

          <p class="font-mono text-[13px] sm:text-sm leading-relaxed text-gray-200 break-all tracking-tight pr-1">
            <span class="sm:hidden">
              {showFullPrincipal ? principalText : truncatePrincipal(principalText, 26)}
            </span>
            <span class="hidden sm:inline">{principalText}</span>
          </p>
          <p class="mt-2.5 text-xs leading-relaxed text-gray-500">
            Only send tokens supported in this wallet, as listed below.
          </p>
          {#if isRefreshingBalances}
            <p class="mt-2 text-xs text-[#c4b5fd]">Refreshing balances…</p>
          {:else if refreshFeedback === 'updated'}
            <p class="mt-2 text-xs text-emerald-400">Balances updated.</p>
          {:else if refreshFeedback === 'unchanged'}
            <p class="mt-2 text-xs text-gray-400">Balances unchanged. If a credit is still pending, it may take a moment to appear.</p>
          {:else if refreshFeedback === 'failed'}
            <p class="mt-2 text-xs text-red-300">Couldn't refresh balances. Please try again.</p>
          {/if}
        </div>

        <!-- Mobile actions -->
        <div class="mt-3 flex sm:hidden gap-2">
          <button
            type="button"
            on:click={getWalletBalances}
            disabled={isRefreshingBalances}
            class="agent-btn-ghost flex-1 h-9! disabled:opacity-40"
          >
            <RefreshCw class="h-3.5 w-3.5 {isRefreshingBalances ? 'animate-spin' : ''}" />
            {#if isRefreshingBalances}
              Refreshing…
            {:else if refreshFeedback === 'updated'}
              Updated
            {:else if refreshFeedback === 'unchanged'}
              Unchanged
            {:else if refreshFeedback === 'failed'}
              Failed
            {:else}
              Refresh
            {/if}
          </button>
          <button
            type="button"
            on:click={disconnect}
            class="inline-flex flex-1 h-9 items-center justify-center gap-1.5 rounded-full border border-red-500/20 bg-red-500/8 text-[13px] font-medium text-red-300"
          >
            <LogOut class="h-3.5 w-3.5" />
            Exit
          </button>
        </div>
      </div>
    {:else}
      <!-- Disconnected state -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-5 p-5 sm:p-6">
        <div class="flex items-start gap-3 sm:gap-4 min-w-0 flex-1">
          <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/4">
            <Wallet class="h-5 w-5 text-gray-500" />
          </div>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <p class="agent-eyebrow">Account</p>
              <span class="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/3 px-2 py-0.5 text-[11px] font-medium text-gray-500">
                <span class="h-1 w-1 rounded-full bg-gray-500"></span>
                Offline
              </span>
            </div>
            <h2 class="mt-1 text-base font-semibold tracking-tight text-white">Connect your wallet</h2>
            <p class="mt-0.5 text-sm text-gray-500">Link an identity to view balances and send tokens</p>
          </div>
        </div>

        <button type="button" on:click={connect} class="agent-btn-primary w-full sm:w-auto shrink-0">
          <Wallet class="h-4 w-4" />
          Connect wallet
        </button>
      </div>
    {/if}
  </div>
</div>

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}
