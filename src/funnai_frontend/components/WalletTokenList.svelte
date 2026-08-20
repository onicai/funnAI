<script lang="ts">
  import { flip } from "svelte/animate";
  import { Coins } from "lucide-svelte";

  import SendTokenModal from "./SendTokenModal.svelte";
  import ReceiveTokenModal from './ReceiveTokenModal.svelte';
  import TokenImages from "./TokenImages.svelte";
  import Badge from "./Badge.svelte";
  import LoadingIndicator from "./LoadingIndicator.svelte";

  import { WalletDataService, walletDataStore } from "../helpers/WalletDataService";
  import { formatBalance } from "../helpers/utils/numberFormatUtils";

  export let tokens: FE.Token[] = [];
  export let showHeader: boolean = true;
  export let showOnlyWithBalance: boolean = true;
  export let isLoading: boolean = false;

  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isLoadingBalances =
    isLoading ||
    walletData.isLoading;

  const WHALE_THRESHOLD = 1;

  $: formattedTokens = tokens
    .map((token) => {
      const balance = walletData.balances[token.canister_id];
      const hasKnownBalance = Boolean(balance);
      const balanceAmount = balance?.in_tokens ?? BigInt(0);
      const totalSupply = token.metrics?.total_supply || "0";

      const percentOfSupply =
        Number(totalSupply) > 0
          ? (Number(balanceAmount.toString()) / Number(totalSupply)) * 100
          : 0;

      const isWhale = percentOfSupply >= WHALE_THRESHOLD;
      return {
        ...token,
        balanceAmount,
        hasKnownBalance,
        formattedUsdValue: balance?.in_usd || "0",
        percentOfSupply,
        isWhale,
      };
    })
    .filter((token) => {
      return !showOnlyWithBalance || token.balanceAmount > BigInt(0);
    })
    .sort((a, b) => {
      if (a.token_id && b.token_id) {
        return a.token_id - b.token_id;
      }
      if (Object.keys(walletData.balances).length > 0) {
        return Number(b.formattedUsdValue) - Number(a.formattedUsdValue);
      }
      return a.symbol.localeCompare(b.symbol);
    });

  function formatSupplyPercentage(percent: number): string {
    return percent.toFixed(2) + "%";
  }

  function formatUsd(value: string): string {
    const n = Number(value);
    if (!Number.isFinite(n) || n <= 0) return "";
    return n.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function displayBalance(token): string {
    const queryFailed = walletData.balancesStatus === 'error';
    if (!token.hasKnownBalance) {
      return queryFailed ? `Couldn't load ${token.symbol}` : `0 ${token.symbol}`;
    }
    if (token.balanceAmount === BigInt(0)) return `0 ${token.symbol}`;
    const formatted = formatBalance(token.balanceAmount.toString(), token.decimals);
    if (Number(formatted) < 0.00000001) return `<0.00000001 ${token.symbol}`;
    return `${formatted} ${token.symbol}`;
  }

  const whaleTooltipText = `This wallet holds at least ${WHALE_THRESHOLD}% of the token's total supply, making it a significant holder ("whale").`;

  let selectedToken = null;
  let showSendModal = false;
  let showReceiveModal = false;

  function openSendModal(token) {
    selectedToken = token;
    showSendModal = true;
  }

  function openReceiveModal(token) {
    selectedToken = token;
    showReceiveModal = true;
  }
</script>

<div>
  {#if showHeader}
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-medium text-gray-300">Token balances</h3>
      <div class="p-2 rounded-lg bg-[#653FC5]/15">
        <Coins class="w-3 h-3 text-[#a78bfa]" />
      </div>
    </div>
  {/if}

  <div class="max-h-[600px] overflow-y-auto">
    {#if isLoadingBalances && formattedTokens.length === 0}
      <div class="text-center py-8">
        <LoadingIndicator text="Loading token balances..." size={24} />
      </div>
    {:else if formattedTokens.length === 0}
      <div class="rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-8 text-center">
        <p class="text-sm text-gray-400">
          {#if showOnlyWithBalance}
            No tokens with a balance in this wallet
          {:else}
            No tokens found
          {/if}
        </p>
      </div>
    {:else}
      <div class="space-y-2">
        {#each formattedTokens as token (token.canister_id)}
          {@const hasBalance = token.balanceAmount > BigInt(0)}
          {@const usd = formatUsd(token.formattedUsdValue)}
          <div
            animate:flip={{ duration: 300 }}
            class="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3.5 sm:px-4 sm:py-3.5 transition-colors hover:border-white/[0.12] hover:bg-white/[0.04] {hasBalance ? '' : 'opacity-55'}"
          >
            <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <div class="flex h-10 w-10 sm:h-11 sm:w-11 flex-shrink-0 items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-white/[0.04]">
                  <TokenImages tokens={[token]} size={32} />
                </div>
                <div class="min-w-0">
                  <div class="flex items-center gap-1.5 min-w-0">
                    <span class="font-semibold tracking-tight text-white truncate">{token.symbol}</span>
                    {#if token.isWhale}
                      <Badge
                        variant="blue"
                        icon="🐋"
                        size="xs"
                        tooltipText={whaleTooltipText}
                      >
                        {formatSupplyPercentage(token.percentOfSupply)}
                      </Badge>
                    {/if}
                  </div>
                  <p class="text-xs text-gray-500 truncate">{token.name}</p>
                </div>
              </div>

              <div class="flex items-center justify-between sm:justify-end gap-3 sm:gap-4 sm:flex-1">
                <div class="sm:text-right min-w-0">
                  <p class="font-medium text-gray-100 tabular-nums tracking-tight truncate">
                    {displayBalance(token)}
                  </p>
                  {#if usd}
                    <p class="text-xs text-gray-500 tabular-nums">{usd}</p>
                  {:else if !token.hasKnownBalance && walletData.balancesStatus === 'error'}
                    <p class="text-xs text-amber-400">Retry to load</p>
                  {:else if !hasBalance}
                    <p class="text-xs text-gray-600">No balance</p>
                  {/if}
                </div>

                <div class="flex items-center gap-2 flex-shrink-0">
                  <button
                    type="button"
                    on:click={() => openReceiveModal(token)}
                    class="agent-btn-ghost !h-8 !px-3 !text-xs"
                  >
                    Receive
                  </button>
                  <button
                    type="button"
                    on:click={() => openSendModal(token)}
                    class="agent-btn-primary !h-8 !px-3 !text-xs {hasBalance ? '' : 'opacity-50'}"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

{#if showSendModal}
  <SendTokenModal
    token={selectedToken}
    isOpen={showSendModal}
    onClose={() => showSendModal = false}
    onSuccess={() => {
      showSendModal = false;
      WalletDataService.refreshBalances(true);
    }}
  />
{/if}

{#if showReceiveModal}
  <ReceiveTokenModal
    token={selectedToken}
    isOpen={showReceiveModal}
    onClose={() => {
      showReceiveModal = false;
      WalletDataService.refreshBalances(true);
    }}
  />
{/if}
