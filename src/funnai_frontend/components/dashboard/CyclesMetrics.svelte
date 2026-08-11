<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { DailyMetricsService } from "../../helpers/DailyMetricsService";
  import { CyclesRateService } from "../../helpers/CyclesRateService";

  export let title: string = "Cycles Overview";

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;

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

  async function loadMetrics() {
    try {
      loading = true;
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
    }
  }

  onMount(async () => {
    // First fetch the dynamic conversion rate
    await loadCyclesRate();
    // Then load metrics
    await loadMetrics();
    // Update metrics every 5 minutes
    updateInterval = setInterval(loadMetrics, 5 * 60 * 1000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });
</script>

<div class="agent-card p-6">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center gap-3">
      <div class="p-2 border border-white/5 bg-white/[0.05] rounded-xl">
        <svg class="w-5 h-5 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div>
        <p class="agent-eyebrow">Cycles</p>
        <h3 class="text-lg font-semibold tracking-tight text-white">{title}</h3>
        {#if lastUpdated}
          <p class="text-xs text-gray-500">Updated: {lastUpdated}</p>
        {/if}
      </div>
    </div>
    <div class="flex items-center gap-2">
      {#if loading}
        <div class="animate-spin h-4 w-4 border-2 border-agent-purple rounded-full border-t-transparent"></div>
      {:else}
        <button
          on:click={loadMetrics}
          class="p-1.5 text-gray-400 hover:text-agent-purple transition-colors"
          title="Refresh metrics"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      {/if}
      <div class="flex items-center gap-1 text-xs text-gray-500">
        <div class="w-2 h-2 rounded-full bg-emerald-500"></div>
        <span>Live</span>
      </div>
    </div>
  </div>

  {#if error}
    <div class="text-red-400 text-sm mb-4 p-3 bg-red-950/40 rounded-xl border border-red-500/30">
      {error}
    </div>
  {/if}

  <!-- Metrics Grid -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
    <!-- Daily Burn Rate -->
    <div class="bg-white/[0.03] border border-white/10 rounded-xl p-4">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
        </svg>
        <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">Daily Burn</span>
      </div>
      {#if loading}
        <div class="animate-pulse">
          <div class="h-7 bg-white/[0.06] rounded w-24 mb-1"></div>
          <div class="h-4 bg-white/[0.06] rounded w-20"></div>
        </div>
      {:else}
        <div class="text-2xl font-semibold tracking-tight text-white">
          {formatTrillionCycles(dailyBurnRateCycles)}/day
        </div>
        <div class="text-sm text-gray-400 font-medium">
          {formatUsd(dailyBurnRateUsd)}/day
        </div>
      {/if}
    </div>
    
    <!-- Total Cycles All Mainers -->
    <div class="bg-white/[0.03] border border-white/10 rounded-xl p-4">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
        <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">All mAIners</span>
      </div>
      {#if loading}
        <div class="animate-pulse">
          <div class="h-7 bg-white/[0.06] rounded w-24 mb-1"></div>
          <div class="h-4 bg-white/[0.06] rounded w-20"></div>
        </div>
      {:else}
        <div class="text-2xl font-semibold tracking-tight text-white">
          {formatTrillionCycles(totalCyclesAllMainers)}
        </div>
        <div class="text-sm text-gray-400 font-medium">
          {formatUsd(totalCyclesAllMainersUsd)}
        </div>
      {/if}
    </div>

    <!-- Total Cycles Protocol 
    <div class="bg-white/[0.03] border border-white/10 rounded-xl p-4">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">Protocol</span>
      </div>
      {#if loading}
        <div class="animate-pulse">
          <div class="h-7 bg-white/[0.06] rounded w-24 mb-1"></div>
          <div class="h-4 bg-white/[0.06] rounded w-20"></div>
        </div>
      {:else}
        <div class="text-2xl font-semibold tracking-tight text-white">
          {formatTrillionCycles(totalCyclesProtocol)}
        </div>
        <div class="text-sm text-gray-400 font-medium">
          {formatUsd(totalCyclesProtocolUsd)}
        </div>
      {/if}
    </div>
    -->

    <!-- Total Cycles All 
    <div class="bg-white/[0.03] border border-white/10 rounded-xl p-4">
      <div class="flex items-center gap-2 mb-2">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">Total</span>
      </div>
      {#if loading}
        <div class="animate-pulse">
          <div class="h-7 bg-white/[0.06] rounded w-24 mb-1"></div>
          <div class="h-4 bg-white/[0.06] rounded w-20"></div>
        </div>
      {:else}
        <div class="text-2xl font-semibold tracking-tight text-white">
          {formatTrillionCycles(totalCyclesAll)}
        </div>
        <div class="text-sm text-gray-400 font-medium">
          {formatUsd(totalCyclesAllUsd)}
        </div>
      {/if}
    </div>
    -->

    
  </div>

  <!-- Summary Footer -->
  <div class="mt-4 pt-4 border-t border-white/[0.08]">
    <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-500">
      <div class="flex items-center gap-4">
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-agent-purple"></span>
          mAIners cycles
        </span>
        <!-- Summary Footer 
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-blue-500"></span>
          Protocol cycles
        </span>
        -->
      </div>
      <span>Values shown in trillion cycles (T)</span>
    </div>
  </div>
</div>
