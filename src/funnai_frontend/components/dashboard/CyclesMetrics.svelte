<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { DailyMetricsService } from "../../helpers/DailyMetricsService";
  import { CyclesRateService } from "../../helpers/CyclesRateService";

  export let title: string = "Cycles Overview";

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;
  let inFlight = false;

  // Metrics data
  let totalCyclesAllMainers = 0;
  let totalCyclesAllMainersUsd = 0;
  let totalCyclesProtocol = 0;
  let totalCyclesProtocolUsd = 0;
  let totalCyclesAll = 0;
  let totalCyclesAllUsd = 0;
  let dailyBurnRateCycles = 0;
  let dailyBurnRateUsd = 0;
  let lastUpdated = "";

  // Dynamic cycles to USD conversion rate (fetched from CMC)
  let cyclesUsdRate = 1.37; // Default fallback

  /**
   * Format cycles with appropriate suffix
   * Note: Backend stores cycles in trillions, so value is already in T
   */
  function formatTrillionCycles(cycles: number): string {
    // Backend already stores values in trillions
    if (cycles >= 1_000_000) {
      // Quadrillions (1000+ trillion)
      return `${(cycles / 1000).toLocaleString("en-US", { maximumFractionDigits: 0 })}Q`;
    }
    if (cycles >= 1000) {
      // Thousands of trillions, show with comma
      return `${cycles.toLocaleString("en-US", { maximumFractionDigits: 0 })}T`;
    }
    // Less than 1000 trillion
    return `${cycles.toLocaleString("en-US", { maximumFractionDigits: 0 })}T`;
  }

  /**
   * Format USD value with proper formatting
   */
  function formatUsd(value: number): string {
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}M`;
    }
    if (value >= 1_000) {
      return `$${(value / 1_000).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}K`;
    }
    return `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }

  /**
   * Calculate USD value from cycles if not provided
   * Note: cycles value is already in trillions from the backend
   */
  function calculateUsdFromCycles(cyclesInTrillions: number): number {
    return cyclesInTrillions * cyclesUsdRate;
  }

  /**
   * Fetch the dynamic cycles to USD conversion rate
   */
  async function loadCyclesRate() {
    try {
      cyclesUsdRate = await CyclesRateService.getCyclesToUsdRate();
    } catch (err) {
      // Use default fallback rate
    }
  }

  async function loadMetrics(isRefresh = false) {
    if (inFlight) return;
    inFlight = true;
    try {
      if (!isRefresh) loading = true;
      error = "";

      const latestMetric = await DailyMetricsService.getLatestMetrics();
      
      if (latestMetric) {
        // Check if total_cycles breakdown is available from the API
        const totalCyclesData = latestMetric.system_metrics.total_cycles;
        
        if (totalCyclesData) {
          // Use the new API structure with breakdown
          totalCyclesAllMainers = totalCyclesData.mainers.cycles;
          totalCyclesAllMainersUsd = totalCyclesData.mainers.usd;

          totalCyclesProtocol = totalCyclesData.protocol.cycles;
          totalCyclesProtocolUsd = totalCyclesData.protocol.usd;

          totalCyclesAll = totalCyclesData.all.cycles;
          totalCyclesAllUsd = totalCyclesData.all.usd;
        } else {
          // Fallback: total_cycles not available from API
          // Use mainers.totals.total_cycles as fallback for mainer cycles
          totalCyclesAllMainers = latestMetric.mainers.totals.total_cycles;
          totalCyclesAllMainersUsd = calculateUsdFromCycles(totalCyclesAllMainers);

          // Protocol cycles not available without the total_cycles field
          totalCyclesProtocol = 0;
          totalCyclesProtocolUsd = 0;

          totalCyclesAll = totalCyclesAllMainers;
          totalCyclesAllUsd = totalCyclesAllMainersUsd;
        }

        // Daily burn rate
        dailyBurnRateCycles = latestMetric.system_metrics.daily_burn_rate.cycles;
        dailyBurnRateUsd = latestMetric.system_metrics.daily_burn_rate.usd || 
                          calculateUsdFromCycles(dailyBurnRateCycles);

        // Last updated date
        lastUpdated = latestMetric.metadata.date;
      }
    } catch (err) {
      console.error("Error loading cycles metrics:", err);
      error = "Failed to load cycles metrics";
    } finally {
      loading = false;
      inFlight = false;
    }
  }

  onMount(async () => {
    // First fetch the dynamic conversion rate
    await loadCyclesRate();
    // Then load metrics
    await loadMetrics();
    // Update metrics every 5 minutes without swapping the layout
    updateInterval = setInterval(() => loadMetrics(true), 5 * 60 * 1000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });
</script>

<div class="agent-card !bg-agent-surface p-5 sm:p-6">
  <div class="relative z-[1] flex items-start justify-between gap-3 mb-5">
    <div class="min-w-0">
      <div class="flex flex-wrap items-center gap-2">
        <p class="agent-eyebrow">Cycles</p>
        <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
          <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse"></span>
          Live
        </span>
      </div>
      <h3 class="mt-1 text-base font-semibold tracking-tight text-white">{title}</h3>
      <p class="mt-0.5 text-sm text-gray-500 truncate min-h-[1.25rem]">
        {lastUpdated ? `Updated ${lastUpdated} · trillion cycles (T)` : 'Network burn and mAIner cycle inventory'}
      </p>
    </div>
    <div class="flex items-center gap-2 flex-shrink-0">
      <button
        type="button"
        on:click={() => loadMetrics(true)}
        disabled={inFlight}
        class="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/[0.04] text-gray-400 hover:text-white hover:border-[#653FC5]/40 transition-colors disabled:opacity-60"
        title="Refresh metrics"
      >
        {#if inFlight}
          <span class="h-3.5 w-3.5 border-2 border-[#653FC5] rounded-full border-t-transparent animate-spin"></span>
        {:else}
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        {/if}
      </button>
    </div>
  </div>

  {#if error}
    <div class="relative z-[1] text-red-300 text-sm mb-4 p-3 rounded-xl border border-red-500/25 bg-red-500/10">
      {error}
    </div>
  {/if}

  <div class="relative z-[1] grid grid-cols-1 sm:grid-cols-2 gap-3">
    <div class="rounded-xl bg-white/[0.03] p-4">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Daily burn</p>
      <p class="agent-metric-value">
        {#if loading}
          <span class="agent-metric-pulse w-[4ch]" aria-hidden="true"></span>
        {:else}
          <span class="min-w-[4ch]">{formatTrillionCycles(dailyBurnRateCycles)}</span>
        {/if}
        <span class="agent-metric-unit">/day</span>
      </p>
      <p class="agent-metric-hint flex items-baseline gap-1">
        {#if loading}
          <span class="agent-metric-pulse w-[6ch]" aria-hidden="true"></span>
        {:else}
          <span class="min-w-[6ch] tabular-nums">{formatUsd(dailyBurnRateUsd)}</span>
        {/if}
        <span>/day</span>
      </p>
    </div>

    <div class="rounded-xl bg-white/[0.03] p-4">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">All mAIners</p>
      <p class="agent-metric-value">
        {#if loading}
          <span class="agent-metric-pulse w-[5ch]" aria-hidden="true"></span>
        {:else}
          <span class="min-w-[5ch]">{formatTrillionCycles(totalCyclesAllMainers)}</span>
        {/if}
      </p>
      <p class="agent-metric-hint">
        {#if loading}
          <span class="agent-metric-pulse w-[6ch]" aria-hidden="true"></span>
        {:else}
          <span class="tabular-nums">{formatUsd(totalCyclesAllMainersUsd)}</span>
        {/if}
      </p>
    </div>
  </div>
</div>
