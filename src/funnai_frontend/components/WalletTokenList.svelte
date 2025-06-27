<script lang="ts">
  import { get } from 'svelte/store';
  import { flip } from "svelte/animate";
  import { ArrowUp, ArrowDown, Coins } from "lucide-svelte";

  import SendTokenModal from "./SendTokenModal.svelte";
  import ReceiveTokenModal from './ReceiveTokenModal.svelte';
  import TokenImages from "./TokenImages.svelte";
  import Badge from "./Badge.svelte";
  import LoadingIndicator from "./LoadingIndicator.svelte";
 
  import { WalletDataService, walletDataStore } from "../helpers/WalletDataService";
  import {
    formatBalance,
    formatToNonZeroDecimal,
  } from "../helpers/utils/numberFormatUtils";
  import { tooltip } from "../helpers/utils/tooltip";

  export let tokens: FE.Token[] = [];
  export let showHeader: boolean = true;
  export let showOnlyWithBalance: boolean = true;
  export let isLoading: boolean = false;

  //$: walletData = get(walletDataStore);
  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isLoadingBalances =
    isLoading ||
    walletData.isLoading /* ||
    (tokens.length > 0 && Object.keys(walletData.balances).length === 0) */;

  // Whale threshold - percentage of total supply that makes a holder a "whale"
  const WHALE_THRESHOLD = 1; // 1% of total supply

  // Calculate formatted values reactively based on wallet balances and filter out zero balances
  $: formattedTokens = tokens
    .map((token) => {
      const balance = walletData.balances[token.canister_id];
      const balanceAmount = balance?.in_tokens || BigInt(0);
      const totalSupply = token.metrics?.total_supply || "0";

      const percentOfSupply =
        Number(totalSupply) > 0
          ? (Number(balanceAmount.toString()) / Number(totalSupply)) * 100
          : 0;

      const isWhale = percentOfSupply >= WHALE_THRESHOLD;
      return {
        ...token,
        balanceAmount,
        formattedUsdValue: balance?.in_usd || "0",
        priceChange24h: token.metrics?.price_change_24h || "0",
        price: token.metrics?.price || "0",
        percentOfSupply,
        isWhale,
      };
    })
    .filter((token) => {
      return !showOnlyWithBalance || token.balanceAmount > BigInt(0);
    })
    .sort((a, b) => {
      // Sort by token_id if available (as defined in token_helpers.ts)
      if (a.token_id && b.token_id) {
        return a.token_id - b.token_id;
      }
      // Fallback to previous sorting method if token_id not available
      if (Object.keys(walletData.balances).length > 0) {
        return Number(b.formattedUsdValue) - Number(a.formattedUsdValue);
      }
      return a.symbol.localeCompare(b.symbol);
    });

  function formatPriceChange(change: string) {
    const num = Number(change);
    return `${num > 0 ? "+" : ""}${num.toFixed(2)}%`;
  }

  function getPriceChangeColor(change: string) {
    const num = Number(change);
    if (num > 0) return "text-green-900";
    if (num < 0) return "text-red-900";
    return "text-gray-900";
  }

  // Format percentage of total supply
  function formatSupplyPercentage(percent: number): string {
    return percent.toFixed(2) + "%";
  }

  // Tooltip text for whale indicator
  const whaleTooltipText = `This wallet holds at least ${WHALE_THRESHOLD}% of the token's total supply, making it a significant holder ("whale").`;

  let selectedToken = null;
  let showSendModal = false;
  let showReceiveModal = false;

  function openSendModal(token) {
    selectedToken = token;
    showSendModal = true;
  };

  function openReceiveModal(token) {
    selectedToken = token;
    showReceiveModal = true;
  };
</script>

<div>
  {#if showHeader}
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm uppercase font-medium text-gray-900 dark:text-gray-100">
        Token Balances
      </h3>
      <div class="p-2 rounded-lg bg-blue-600/10">
        <Coins class="w-3 h-3 text-blue-600" />
      </div>
    </div>
  {/if}

  {#if !isLoadingBalances && formattedTokens.length > 0}
    <div
      class="hidden sm:grid sm:grid-cols-[2fr,1.5fr,1fr] gap-4 px-4 py-2 text-sm text-gray-600 dark:text-gray-400 font-medium border-b border-gray-700"
    >
      <div>Token</div>
      <div class="text-right">Balance</div>
      <!--<div class="text-right">Price</div>
      <div class="text-right">24h Change</div>-->
      <div class="text-right">Actions</div>
    </div>
  {/if}

  <div class="max-h-[600px] overflow-y-auto">
    {#if isLoadingBalances}
      <div class="text-center py-8">
        <LoadingIndicator text="Loading token balances..." size={24} />
      </div>
    {:else if formattedTokens.length === 0}
      <div class="text-center py-8 text-gray-600 dark:text-gray-400">
        {#if showOnlyWithBalance}
          No tokens with balance found in this wallet
        {:else}
          No tokens found
        {/if}
      </div>
    {:else}
      <div class="divide-y divide-gray-700">
        {#each formattedTokens as token (token.canister_id)}
          <div
            animate:flip={{ duration: 300 }}
            class="sm:grid sm:grid-cols-[2fr,1.5fr,1fr] sm:gap-4 sm:items-center p-4 hover:bg-zinc-800/30 transition-colors cursor-pointer"
          >
            <!-- Mobile display -->
            <div class="flex flex-col gap-3 sm:hidden">
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <TokenImages tokens={[token]} size={28} />
                  <div class="flex flex-col">
                    <div class="flex items-center gap-1">
                      <span class="font-semibold text-gray-900 dark:text-gray-100">{token.symbol}</span>
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
                    <span class="text-xs text-gray-600 dark:text-gray-400">{token.name}</span>
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-medium text-gray-900 dark:text-gray-100">
                    {#if token.balanceAmount === BigInt(0)}
                      0 {token.symbol}
                    {:else if Number(token.balanceAmount) < 0.00001}
                      &lt;0.001 {token.symbol}
                    {:else}
                      {formatBalance(token.balanceAmount.toString(), token.decimals)}
                      {token.symbol}
                    {/if}
                  </div>
                </div>
              </div>
            </div>

            <!-- Desktop token column -->
            <div class="hidden sm:flex items-center gap-3">
              <TokenImages tokens={[token]} size={38} />
              <div class="flex flex-col">
                <div class="flex items-center gap-1">
                  <span class="font-semibold text-gray-900 dark:text-gray-100">{token.symbol}</span>
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
                <span class="text-xs text-gray-600 dark:text-gray-400">{token.name}</span>
              </div>
            </div>

            <!-- Desktop balance column -->
            <div class="hidden sm:block text-right">
              <div class="font-medium text-gray-900 dark:text-gray-100">
                {#if token.balanceAmount === BigInt(0)}
                  0 {token.symbol}
                {:else if Number(formatBalance(token.balanceAmount.toString(), token.decimals)) < 0.00000001}
                  &lt;0.00000001 {token.symbol}
                {:else}
                  {formatBalance(token.balanceAmount.toString(), token.decimals)}
                  {token.symbol}
                {/if}
              </div>
            </div>

            <!-- Desktop actions column -->
            <div class="hidden sm:block text-right">
              <div class="flex justify-end gap-2">
                <button
                  on:click={() => openReceiveModal(token)}
                  class="text-sm font-medium px-3 py-1.5 bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition"
                >
                  Receive
                </button>
                <button
                  on:click={() => openSendModal(token)}
                  class="text-sm font-medium px-3 py-1.5 bg-blue-600 text-white hover:bg-blue-500 dark:bg-blue-500 dark:hover:bg-blue-400 rounded-lg transition"
                >
                  Send
                </button>
              </div>
            </div>

            <!-- Mobile buttons -->
            <div class="flex sm:hidden justify-end gap-2 mt-4">
              <button
                on:click={() => openReceiveModal(token)}
                class="text-sm font-medium px-3 py-1.5 bg-gray-700 text-white hover:bg-gray-600 dark:bg-gray-600 dark:hover:bg-gray-500 rounded-lg transition"
              >
                Receive
              </button>
              <button
                on:click={() => openSendModal(token)}
                class="text-sm font-medium px-3 py-1.5 bg-blue-600 text-white hover:bg-blue-500 dark:bg-blue-500 dark:hover:bg-blue-400 rounded-lg transition"
              >
                Send
              </button>
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
