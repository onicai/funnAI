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

  console.log("in WalletTokenList tokens ", tokens);
  console.log("in WalletTokenList showOnlyWithBalance ", showOnlyWithBalance);

  $: isLoadingBalances =
    isLoading ||
    walletData.isLoading /* ||
    (tokens.length > 0 && Object.keys(walletData.balances).length === 0) */;

  // Whale threshold - percentage of total supply that makes a holder a "whale"
  const WHALE_THRESHOLD = 1; // 1% of total supply

  // Calculate formatted values reactively based on wallet balances and filter out zero balances
  $: formattedTokens = tokens
    .map((token) => {
      console.log("in WalletTokenList map tokens ", tokens);
      console.log("in WalletTokenList map showOnlyWithBalance ", showOnlyWithBalance);
      console.log("in WalletTokenList map token ", token);
      console.log("in WalletTokenList map walletData ", walletData);
      console.log("in WalletTokenList map walletData.balances ", walletData.balances);
      const balance = walletData.balances[token.canister_id];
      console.log("in WalletTokenList map balance ", balance);
      const balanceAmount = balance?.in_tokens || BigInt(0);
      const totalSupply = token.metrics?.total_supply || "0";
      console.log("in WalletTokenList map balanceAmount ", balanceAmount);
      console.log("in WalletTokenList map totalSupply ", totalSupply);

      const percentOfSupply =
        Number(totalSupply) > 0
          ? (Number(balanceAmount.toString()) / Number(totalSupply)) * 100
          : 0;

      const isWhale = percentOfSupply >= WHALE_THRESHOLD;
      console.log("in WalletTokenList map before return ", isWhale);
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
      console.log("in WalletTokenList filter token ", token);
      console.log("in WalletTokenList filter !showOnlyWithBalance ", !showOnlyWithBalance);
      return !showOnlyWithBalance || token.balanceAmount > BigInt(0);
    })
    .sort((a, b) => {
      console.log("in WalletTokenList sort a ", a);
      console.log("in WalletTokenList sort b ", b);
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
    if (num > 0) return "text-kong-text-accent-green";
    if (num < 0) return "text-kong-text-accent-red";
    return "text-kong-text-secondary";
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
      <h3 class="text-sm uppercase font-medium text-kong-text-primary">
        Token Balances
      </h3>
      <div class="p-2 rounded-lg bg-kong-primary/10">
        <Coins class="w-3 h-3 text-kong-primary" />
      </div>
    </div>
  {/if}

  <!-- Grid Headers - Hidden on mobile, visible on tablet and above -->
  {#if !isLoadingBalances && formattedTokens.length > 0}
    <div
      class="hidden sm:grid sm:grid-cols-[2fr,1.5fr,1fr,1fr,1fr] gap-4 px-4 py-2 text-sm text-kong-text-secondary font-medium border-b border-kong-border"
    >
      <div>Token</div>
      <div class="text-right">Balance</div>
      <div class="text-right">Price</div>
      <div class="text-right">24h Change</div>
      <div class="text-right">Value</div>
    </div>
  {/if}

  <div class="max-h-[600px] overflow-y-auto">
    {#if isLoadingBalances}
      <div class="text-center py-8">
        <LoadingIndicator text="Loading token balances..." size={24} />
      </div>
    {:else if formattedTokens.length === 0}
      <div class="text-center py-8 text-kong-text-secondary">
        {#if showOnlyWithBalance}
          No tokens with balance found in this wallet
        {:else}
          No tokens found
        {/if}
      </div>
    {:else}
      <!-- Grid Body -->
      <div class="divide-y divide-kong-border">
        {#each formattedTokens as token (token.canister_id)}
          <div
            animate:flip={{ duration: 300 }}
            class="sm:grid sm:grid-cols-[2fr,1.5fr,1fr,1fr,1fr] sm:gap-4 sm:items-center p-4 hover:bg-kong-bg-dark/30 transition-colors cursor-pointer"
          >
            <!-- Mobile View - Card-like layout -->
            <div class="flex flex-col gap-3 sm:hidden">
              <!-- Token and Value in a row -->
              <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                  <TokenImages tokens={[token]} size={28} />
                  <div class="flex flex-col">
                    <div class="flex items-center gap-1">
                      <span class="font-semibold text-kong-text-primary"
                        >{token.symbol}</span
                      >
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
                    <span class="text-xs text-kong-text-secondary"
                      >{token.name}</span
                    >
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-medium text-kong-text-primary">
                    ${formatToNonZeroDecimal(token.formattedUsdValue)}
                  </div>
                </div>
              </div>

              <!-- Balance, Price and 24h Change in a row -->
              <div class="flex justify-between items-center text-sm">
                <div>
                  <span class="text-kong-text-secondary">Balance: </span>
                  <span class="font-medium">
                    {Number(token.balanceAmount) < 0.00001
                    ? "&lt;0.001"
                    : formatBalance(token.balanceAmount.toString(), token.decimals)}
                  </span>
                </div>
                <div>
                  <span class="text-kong-text-secondary">Price: </span>
                  <span class="font-medium"
                    >${formatToNonZeroDecimal(token.price)}</span
                  >
                </div>
                <div class={getPriceChangeColor(token.priceChange24h)}>
                  {formatPriceChange(token.priceChange24h)}
                  {#if Number(token.priceChange24h) > 0}
                    <ArrowUp class="inline h-3 w-3" />
                  {:else if Number(token.priceChange24h) < 0}
                    <ArrowDown class="inline h-3 w-3" />
                  {/if}
                </div>
              </div>
            </div>

            <!-- Desktop View - Grid layout -->
            <!-- Token -->
            <div class="hidden sm:flex items-center gap-3">
              <TokenImages tokens={[token]} size={32} />
              <div class="flex flex-col">
                <div class="flex items-center gap-1">
                  <span class="font-semibold text-kong-text-primary"
                    >{token.symbol}</span
                  >
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
                <span class="text-xs text-kong-text-secondary"
                  >{token.name}</span
                >
              </div>
            </div>

            <!-- Balance -->
            <div class="hidden sm:block text-right">
              <div class="font-medium text-kong-text-primary">
                {#if token.balanceAmount === BigInt(0) && Number(token.formattedUsdValue) > 0}
                  &lt;0.001 {token.symbol}
                {:else}
                  {
                  Number(formatBalance(token.balanceAmount.toString(), token.decimals)) < 0.00001
                  ? "<0.00001"
                  : formatBalance(token.balanceAmount.toString(), token.decimals)}
                  {token.symbol}
                {/if}
              </div>
            </div>

            <!-- Price -->
            <div class="hidden sm:block text-right">
              <div class="font-medium text-kong-text-primary">
                {Number(token.price) < 0.00001
                  ? "<$0.00001"
                  : "$" + formatToNonZeroDecimal(token.price)}
              </div>
            </div>

            <!-- 24h Change -->
            <div class="hidden sm:block text-right">
              <div class={getPriceChangeColor(token.priceChange24h)}>
                {formatPriceChange(token.priceChange24h)}
                {#if Number(token.priceChange24h) > 0}
                  <ArrowUp class="inline h-4 w-4" />
                {:else if Number(token.priceChange24h) < 0}
                  <ArrowDown class="inline h-4 w-4" />
                {/if}
              </div>
            </div>

            <!-- Value -->
            <div class="hidden sm:block text-right">
              <div class="font-medium text-kong-text-primary">
                {Number(token.formattedUsdValue) < 0.01
                  ? "<$0.01"
                  : "$" + formatToNonZeroDecimal(token.formattedUsdValue)}
              </div>
            </div>

            <!-- Receive Button -->
            <div class="mt-2 sm:mt-0 sm:col-span-full flex justify-end">
              <button
                on:click={() => openReceiveModal(token)}
                class="text-sm font-medium px-3 py-1.5 text-white rounded-lg transition"
              >
                Receive
              </button>
            </div>

            <!-- Send Button -->
            <div class="mt-2 sm:mt-0 sm:col-span-full flex justify-end">
              <button
                on:click={() => openSendModal(token)}
                class="text-sm font-medium px-3 py-1.5 text-white rounded-lg transition"
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
