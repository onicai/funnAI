<script lang="ts">
  import { onMount } from "svelte";
  import { ArrowUp, Info } from "@lucide/svelte";
  import BigNumber from "bignumber.js";
  import { store } from "../../../stores/store";
  import { IcrcService } from "../../../helpers/IcrcService";
  import { fetchTokens } from "../../../helpers/token_helpers";
  import { formatBalance, formatLargeNumber } from "../../../helpers/utils/numberFormatUtils";
  import { MIN_AMOUNT, MAX_AMOUNT } from "../../../helpers/config/topUpConfig";
  import { getBonusCyclesTopupInPercent } from "../../../helpers/gameState";
  import { mainerHealthService, mainerHealthStatuses } from "../../../helpers/mainerHealthService";
  import { WalletDataService } from "../../../helpers/WalletDataService";
  import {
    estimateCyclesFromIcp,
    icpAmountToE8s,
    loadIcpCyclesConversionRate,
    topUpAllMainersWithIcp,
    type BulkTopUpItemResult,
    type BulkTopUpMainer,
  } from "../../../helpers/bulkMainerTopUp";

  export let agents: BulkTopUpMainer[] = [];
  export let isProtocolActive: boolean = true;
  export let isBusy: boolean = false;
  export let onStart: (canisterIds: string[]) => void = () => {};
  export let onComplete: () => void | Promise<void> = () => {};

  const PRESET_AMOUNTS = ["1", "5", "10", "20"];

  let icpToken: FE.Token | null = null;
  let balance: bigint = 0n;
  let amount: string = "";
  let isLoading = true;
  let isSubmitting = false;
  let awaitingConfirm = false;
  let errorMessage = "";
  let conversionRate: BigNumber | null = null;
  let isLoadingConversionRate = true;
  let bonusCyclesTopupInPercent = 0;
  let results: BulkTopUpItemResult[] = [];

  $: eligibleAgents = agents.filter((agent) => {
    if (!agent?.id) return false;
    const health = $mainerHealthStatuses.get(agent.id);
    return health?.isHealthy !== false;
  });
  $: skippedCount = Math.max(agents.length - eligibleAgents.length, 0);
  $: amountNumber = Number(amount);
  $: isValidAmount =
    !!amount &&
    !Number.isNaN(amountNumber) &&
    amountNumber >= MIN_AMOUNT &&
    amountNumber <= MAX_AMOUNT;
  $: isBelowMinimum = !!amount && !Number.isNaN(amountNumber) && amountNumber > 0 && amountNumber < MIN_AMOUNT;
  $: isAboveMaximum = !!amount && !Number.isNaN(amountNumber) && amountNumber > MAX_AMOUNT;
  $: amountE8s =
    isValidAmount && icpToken ? icpAmountToE8s(amount, icpToken.decimals) : 0n;
  $: tokenFee = icpToken ? BigInt(icpToken.fee_fixed) : 0n;
  $: mainerCount = eligibleAgents.length;
  $: totalE8s = (amountE8s + tokenFee) * BigInt(mainerCount);
  $: hasEnoughBalance = isValidAmount && balance >= totalE8s;
  $: cyclesEstimate = estimateCyclesFromIcp(amount, conversionRate, bonusCyclesTopupInPercent);
  $: canSubmit =
    hasEnoughBalance &&
    !isSubmitting &&
    !isBusy &&
    !isLoading &&
    isProtocolActive &&
    mainerCount > 0 &&
    !!icpToken;

  $: if (icpToken && $store.principal) {
    loadBalance();
  }

  function handleAmountInput(event: Event) {
    const input = event.target as HTMLInputElement;
    let value = input.value.trim().replace(",", ".");
    if (value && !/^[0-9]*\.?[0-9]*$/.test(value)) return;
    const parts = value.split(".");
    if (parts.length > 1 && parts[1].length > 8) {
      value = `${parts[0]}.${parts[1].substring(0, 8)}`;
    }
    amount = value;
    awaitingConfirm = false;
    errorMessage = "";
  }

  function setPreset(value: string) {
    amount = value;
    awaitingConfirm = false;
    errorMessage = "";
  }

  async function loadBalance() {
    if (!icpToken || !$store.principal) return;
    try {
      balance = (await IcrcService.getIcrc1Balance(icpToken, $store.principal)) as bigint;
    } catch (error) {
      console.error("Error loading ICP balance:", error);
    }
  }

  async function loadTokenAndRates() {
    isLoading = true;
    isLoadingConversionRate = true;
    try {
      const result = await fetchTokens({});
      icpToken = result.tokens.find((token) => token.symbol === "ICP") || null;
      const [rate, bonus] = await Promise.all([
        loadIcpCyclesConversionRate(),
        getBonusCyclesTopupInPercent(),
      ]);
      conversionRate = rate;
      bonusCyclesTopupInPercent = bonus;
    } catch (error) {
      console.error("Error loading fleet top-up data:", error);
      errorMessage = "Could not load ICP top-up data";
    } finally {
      isLoading = false;
      isLoadingConversionRate = false;
    }
  }

  async function resolveEligibleMainers(): Promise<BulkTopUpMainer[]> {
    const checks = await Promise.all(
      agents.map(async (agent) => {
        const agentIndex = $store.userMainerAgentCanistersInfo.findIndex(
          (canister) => canister.address === agent.id || canister.id === agent.id,
        );
        const actor = agentIndex !== -1 ? $store.userMainerCanisterActors[agentIndex] : null;
        if (!actor) {
          const cached = $mainerHealthStatuses.get(agent.id);
          return cached?.isHealthy === false ? null : agent;
        }
        try {
          const health = await mainerHealthService.checkMainerHealth(agent.id, actor);
          return health.isHealthy ? agent : null;
        } catch (error) {
          console.warn(`Skipping mAIner ${agent.id}: health check failed`, error);
          return null;
        }
      }),
    );
    return checks.filter((agent): agent is BulkTopUpMainer => !!agent);
  }

  async function handleSubmit() {
    if (!canSubmit || !icpToken) return;

    if (!awaitingConfirm) {
      awaitingConfirm = true;
      return;
    }

    isSubmitting = true;
    awaitingConfirm = false;
    errorMessage = "";
    results = eligibleAgents.map((agent) => ({
      id: agent.id,
      name: agent.name,
      status: "pending",
    }));

    try {
      const candidateIds = eligibleAgents.map((agent) => agent.id);
      onStart(candidateIds);

      const healthyMainers = await resolveEligibleMainers();
      if (healthyMainers.length === 0) {
        throw new Error("No healthy mAIners available to top up");
      }

      results = healthyMainers.map((agent) => ({
        id: agent.id,
        name: agent.name,
        status: "pending",
      }));

      const nextResults = await topUpAllMainersWithIcp({
        mainers: healthyMainers,
        amount,
        icpToken,
        onProgress: (item) => {
          results = results.map((current) => (current.id === item.id ? item : current));
        },
      });
      results = nextResults;

      WalletDataService.refreshBalances(true).catch((error) => {
        console.error("Error refreshing wallet balances after fleet top-up:", error);
      });
      await loadBalance();
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : "Fleet top-up failed";
    } finally {
      try {
        await onComplete();
      } catch (completeError) {
        console.error("Error finishing fleet top-up:", completeError);
      }
      isSubmitting = false;
    }
  }

  function cancelConfirm() {
    awaitingConfirm = false;
  }

  $: successCount = results.filter((item) => item.status === "success").length;
  $: errorCount = results.filter((item) => item.status === "error").length;
  $: inFlightCount = results.filter(
    (item) => item.status === "sending" || item.status === "confirming" || item.status === "pending",
  ).length;

  let isOpen = false;

  function toggleAccordion() {
    if (isSubmitting && isOpen) return;
    isOpen = !isOpen;
  }

  onMount(() => {
    loadTokenAndRates();
  });
</script>

<div class="relative overflow-hidden rounded-2xl border border-white/8 bg-agent-surface font-sans">
  <button
    type="button"
    on:click={toggleAccordion}
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/2"
    aria-expanded={isOpen}
  >
    <div class="relative flex items-center justify-between gap-3 px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0 flex-1">
        <p class="agent-eyebrow mb-1">Top up</p>
        <h2 class="text-base sm:text-lg font-semibold tracking-tight text-white">Top up all mAIners</h2>
        <p class="mt-0.5 text-sm font-normal text-gray-400">
          Send the same ICP amount to every mAIner in your fleet
        </p>
      </div>

      <div class="shrink-0 flex items-center gap-2">
        {#if icpToken}
          <img
            src="/icp-rounded.svg"
            alt="ICP"
            class="w-9 h-9 rounded-full object-cover pointer-events-none"
          />
        {/if}
        <div
          class="w-9 h-9 rounded-xl border border-white/10 bg-white/4 flex items-center justify-center transition-transform duration-300"
          style="transform: rotate({isOpen ? 180 : 0}deg)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>

  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/6 p-5 sm:p-6">
    {#if isLoading}
      <div class="flex justify-center py-6">
        <span class="w-6 h-6 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
      </div>
    {:else}
      <div class="space-y-4">
        {#if icpToken}
          <div class="flex items-center justify-between gap-3 rounded-xl bg-white/3 border border-white/10 px-3.5 py-3">
            <span class="text-xs text-gray-400">ICP balance</span>
            <span class="text-sm font-medium text-white tabular-nums">
              {formatBalance(balance.toString(), icpToken.decimals)} ICP
            </span>
          </div>
        {/if}

        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label for="fleet-topup-amount" class="block text-xs text-gray-400">Amount per mAIner</label>
            <span class="text-xs text-gray-500">{MIN_AMOUNT}–{MAX_AMOUNT} ICP</span>
          </div>
          <div class="relative">
            <input
              id="fleet-topup-amount"
              type="text"
              inputmode="decimal"
              class="agent-input w-full pr-14 {hasEnoughBalance && isValidAmount ? 'border-emerald-500/50' : ''} {(!hasEnoughBalance && isValidAmount) || isAboveMaximum ? 'border-red-500/50' : ''} {isBelowMinimum ? 'border-amber-500/50' : ''}"
              placeholder="Enter ICP amount"
              bind:value={amount}
              on:input={handleAmountInput}
              disabled={isSubmitting || isBusy}
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-3 text-sm text-gray-400">ICP</span>
            </div>
          </div>
          <div class="mt-2 flex flex-wrap gap-1.5">
            {#each PRESET_AMOUNTS as preset}
              <button
                type="button"
                class="px-2.5 py-1 rounded-full text-[11px] font-medium border transition-colors {amount === preset ? 'border-agent-purple/50 bg-agent-purple/15 text-white' : 'border-white/10 bg-white/3 text-gray-400 hover:border-agent-purple/30 hover:text-gray-200'}"
                on:click={() => setPreset(preset)}
                disabled={isSubmitting || isBusy}
              >
                {preset} ICP
              </button>
            {/each}
          </div>
          {#if isBelowMinimum}
            <p class="mt-1 text-xs text-amber-400">Minimum amount: {MIN_AMOUNT} ICP</p>
          {/if}
          {#if isAboveMaximum}
            <p class="mt-1 text-xs text-red-400">Maximum amount: {MAX_AMOUNT} ICP</p>
          {/if}
          {#if isValidAmount && !hasEnoughBalance}
            <p class="mt-1 text-xs text-red-400">Not enough ICP for this fleet top-up, including ledger fees</p>
          {/if}
        </div>

        <div class="rounded-xl bg-white/3 border border-white/10 p-3.5 space-y-2">
          <div class="flex justify-between gap-2 text-sm">
            <span class="text-gray-400">{mainerCount} mAIner{mainerCount === 1 ? '' : 's'} × {amount || '0'} ICP</span>
            <span class="text-white tabular-nums">{formatBalance((amountE8s * BigInt(mainerCount)).toString(), icpToken?.decimals || 8)} ICP</span>
          </div>
          <div class="flex justify-between gap-2 text-xs">
            <span class="text-gray-500">Ledger fees</span>
            <span class="text-gray-300 tabular-nums">{formatBalance((tokenFee * BigInt(mainerCount)).toString(), icpToken?.decimals || 8)} ICP</span>
          </div>
          <div class="flex justify-between gap-2 text-sm pt-2 border-t border-white/8">
            <span class="text-gray-200">Total to send</span>
            <span class="font-semibold text-white tabular-nums">{formatBalance(totalE8s.toString(), icpToken?.decimals || 8)} ICP</span>
          </div>
          {#if skippedCount > 0}
            <p class="text-xs text-amber-400">
              {skippedCount} mAIner{skippedCount === 1 ? '' : 's'} unavailable and will be skipped
            </p>
          {/if}
        </div>

        <div class="p-3 rounded-xl bg-sky-500/5 border border-sky-500/20 text-sky-300/90 text-xs sm:text-sm flex flex-col gap-2">
          <div class="flex items-center gap-1.5">
            <Info size={14} class="text-sky-400 shrink-0" />
            <span class="font-medium text-sky-200">Estimated cycles per mAIner</span>
            {#if isLoadingConversionRate}
              <span class="w-3 h-3 ml-1 border-2 border-sky-400/30 border-t-sky-400 rounded-full animate-spin shrink-0"></span>
            {/if}
          </div>
          {#if !isLoadingConversionRate}
            <div class="flex justify-between gap-2">
              <span class="text-sky-300/80">Credited each</span>
              <span class="font-medium text-white tabular-nums">≈ {formatLargeNumber(cyclesEstimate.net.toNumber() / 1_000_000_000_000, 4, false)} T cycles</span>
            </div>
            {#if bonusCyclesTopupInPercent > 0}
              <p class="text-emerald-400 text-xs">Includes +{bonusCyclesTopupInPercent}% top-up bonus</p>
            {/if}
          {/if}
        </div>

        {#if !isProtocolActive}
          <div class="p-3 bg-amber-500/10 rounded-xl border border-amber-500/25">
            <p class="text-sm text-amber-300">Protocol is paused — fleet top-up is unavailable</p>
          </div>
        {/if}

        {#if isBusy && !isSubmitting}
          <div class="p-3 bg-amber-500/10 rounded-xl border border-amber-500/25">
            <p class="text-sm text-amber-300">Finish the current mAIner top-up before topping up the fleet</p>
          </div>
        {/if}

        {#if errorMessage}
          <div class="p-3 bg-red-500/10 rounded-xl border border-red-500/25">
            <p class="text-sm text-red-300">{errorMessage}</p>
          </div>
        {/if}

        {#if awaitingConfirm}
          <div class="flex gap-2">
            <button
              type="button"
              class="flex-1 agent-btn-ghost"
              on:click={cancelConfirm}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="button"
              class="flex-[2] agent-btn-primary"
              on:click={handleSubmit}
              disabled={!canSubmit}
            >
              <ArrowUp size={16} />
              <span>Confirm send {formatBalance(totalE8s.toString(), icpToken?.decimals || 8)} ICP</span>
            </button>
          </div>
        {:else}
          <button
            type="button"
            on:click={handleSubmit}
            class="w-full agent-btn-primary disabled:opacity-50 disabled:cursor-not-allowed {!canSubmit ? 'bg-white/10 hover:bg-white/10 text-gray-500 shadow-none' : ''}"
            disabled={!canSubmit}
          >
            {#if isSubmitting}
              <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>
                {#if inFlightCount > 0}
                  Topping up {successCount + errorCount + 1} of {results.length}…
                {:else}
                  Processing…
                {/if}
              </span>
            {:else}
              <ArrowUp size={16} />
              <span>Top up {mainerCount} mAIner{mainerCount === 1 ? '' : 's'}</span>
            {/if}
          </button>
        {/if}

        {#if results.length > 0}
          <div class="rounded-xl border border-white/8 bg-white/2 p-3 space-y-2">
            <div class="flex items-center justify-between">
              <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Progress</p>
              {#if !isSubmitting}
                <p class="text-xs text-gray-400">
                  {successCount} succeeded{#if errorCount > 0}, {errorCount} failed{/if}
                </p>
              {/if}
            </div>
            <ul class="space-y-1.5 max-h-48 overflow-y-auto">
              {#each results as item (item.id)}
                <li class="flex items-start justify-between gap-2 text-xs">
                  <span class="text-gray-300 truncate">{item.name || item.id.slice(0, 5)}</span>
                  <span class="shrink-0 tabular-nums
                    {item.status === 'success' ? 'text-emerald-400' : ''}
                    {item.status === 'error' ? 'text-red-400' : ''}
                    {item.status === 'sending' || item.status === 'confirming' ? 'text-agent-purple' : ''}
                    {item.status === 'pending' ? 'text-gray-500' : ''}"
                  >
                    {#if item.status === 'pending'}Waiting
                    {:else if item.status === 'sending'}Sending ICP
                    {:else if item.status === 'confirming'}Crediting cycles
                    {:else if item.status === 'success'}Credited
                    {:else}{item.error || 'Failed'}
                    {/if}
                  </span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    {/if}
    </div>
  </div>
</div>

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.35s ease;
  }

  .accordion-content.accordion-open {
    max-height: 2500px;
  }
</style>
