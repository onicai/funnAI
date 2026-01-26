<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { DailyMetricsService, type DailyMetricsData } from "../../helpers/DailyMetricsService";

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

  // Cycles to USD conversion rate (approximately $1.37 per trillion cycles based on ICP/Cycles exchange)
  const CYCLES_TO_USD_RATE = 1.3713;

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
    return cyclesInTrillions * CYCLES_TO_USD_RATE;
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
          
          console.log("total_cycles not available from API, using fallback. Mainers cycles:", totalCyclesAllMainers);
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

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <!-- Header -->
  <div class="flex items-center justify-between mb-6">
    <div class="flex items-center gap-3">
      <div class="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        {#if lastUpdated}
          <p class="text-xs text-gray-500 dark:text-gray-400">Updated: {lastUpdated}</p>
        {/if}
      </div>
    </div>
    <div class="flex items-center gap-2">
      {#if loading}
        <div class="animate-spin h-4 w-4 border-2 border-cyan-500 rounded-full border-t-transparent"></div>
      {:else}
        <button
          on:click={loadMetrics}
          class="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          title="Refresh metrics"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      {/if}
      <div class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <div class="w-2 h-2 rounded-full bg-green-500"></div>
        <span>Live</span>
      </div>
    </div>
  </div>

  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      {error}
    </div>
  {/if}

  <!-- Metrics Grid -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Daily Burn Rate -->
    <div class="relative overflow-hidden bg-gradient-to-br from-orange-50 to-red-100 dark:from-orange-900/20 dark:to-red-800/20 rounded-xl p-4 border border-orange-200 dark:border-orange-700/50">
      <div class="absolute top-0 right-0 w-20 h-20 bg-orange-200/30 dark:bg-orange-700/20 rounded-full -mr-6 -mt-6"></div>
      <div class="relative">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
          </svg>
          <span class="text-xs font-medium text-orange-700 dark:text-orange-300 uppercase tracking-wide">Daily Burn</span>
        </div>
        {#if loading}
          <div class="animate-pulse">
            <div class="h-7 bg-orange-200 dark:bg-orange-700/50 rounded w-24 mb-1"></div>
            <div class="h-4 bg-orange-200 dark:bg-orange-700/50 rounded w-20"></div>
          </div>
        {:else}
          <div class="text-2xl font-bold text-orange-800 dark:text-orange-200">
            {formatTrillionCycles(dailyBurnRateCycles)}/day
          </div>
          <div class="text-sm text-orange-600 dark:text-orange-400 font-medium">
            {formatUsd(dailyBurnRateUsd)}/day
          </div>
        {/if}
      </div>
    </div>
    
    <!-- Total Cycles All Mainers -->
    <div class="relative overflow-hidden bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl p-4 border border-purple-200 dark:border-purple-700/50">
      <div class="absolute top-0 right-0 w-20 h-20 bg-purple-200/30 dark:bg-purple-700/20 rounded-full -mr-6 -mt-6"></div>
      <div class="relative">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
          <span class="text-xs font-medium text-purple-700 dark:text-purple-300 uppercase tracking-wide">All mAIners</span>
        </div>
        {#if loading}
          <div class="animate-pulse">
            <div class="h-7 bg-purple-200 dark:bg-purple-700/50 rounded w-24 mb-1"></div>
            <div class="h-4 bg-purple-200 dark:bg-purple-700/50 rounded w-20"></div>
          </div>
        {:else}
          <div class="text-2xl font-bold text-purple-800 dark:text-purple-200">
            {formatTrillionCycles(totalCyclesAllMainers)}
          </div>
          <div class="text-sm text-purple-600 dark:text-purple-400 font-medium">
            {formatUsd(totalCyclesAllMainersUsd)}
          </div>
        {/if}
      </div>
    </div>

    <!-- Total Cycles Protocol -->
    <div class="relative overflow-hidden bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl p-4 border border-blue-200 dark:border-blue-700/50">
      <div class="absolute top-0 right-0 w-20 h-20 bg-blue-200/30 dark:bg-blue-700/20 rounded-full -mr-6 -mt-6"></div>
      <div class="relative">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <span class="text-xs font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wide">Protocol</span>
        </div>
        {#if loading}
          <div class="animate-pulse">
            <div class="h-7 bg-blue-200 dark:bg-blue-700/50 rounded w-24 mb-1"></div>
            <div class="h-4 bg-blue-200 dark:bg-blue-700/50 rounded w-20"></div>
          </div>
        {:else}
          <div class="text-2xl font-bold text-blue-800 dark:text-blue-200">
            {formatTrillionCycles(totalCyclesProtocol)}
          </div>
          <div class="text-sm text-blue-600 dark:text-blue-400 font-medium">
            {formatUsd(totalCyclesProtocolUsd)}
          </div>
        {/if}
      </div>
    </div>

    <!-- Total Cycles All -->
    <div class="relative overflow-hidden bg-gradient-to-br from-cyan-50 to-cyan-100 dark:from-cyan-900/20 dark:to-cyan-800/20 rounded-xl p-4 border border-cyan-200 dark:border-cyan-700/50">
      <div class="absolute top-0 right-0 w-20 h-20 bg-cyan-200/30 dark:bg-cyan-700/20 rounded-full -mr-6 -mt-6"></div>
      <div class="relative">
        <div class="flex items-center gap-2 mb-2">
          <svg class="w-4 h-4 text-cyan-600 dark:text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span class="text-xs font-medium text-cyan-700 dark:text-cyan-300 uppercase tracking-wide">Total</span>
        </div>
        {#if loading}
          <div class="animate-pulse">
            <div class="h-7 bg-cyan-200 dark:bg-cyan-700/50 rounded w-24 mb-1"></div>
            <div class="h-4 bg-cyan-200 dark:bg-cyan-700/50 rounded w-20"></div>
          </div>
        {:else}
          <div class="text-2xl font-bold text-cyan-800 dark:text-cyan-200">
            {formatTrillionCycles(totalCyclesAll)}
          </div>
          <div class="text-sm text-cyan-600 dark:text-cyan-400 font-medium">
            {formatUsd(totalCyclesAllUsd)}
          </div>
        {/if}
      </div>
    </div>

    
  </div>

  <!-- Summary Footer -->
  <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
    <div class="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-500 dark:text-gray-400">
      <div class="flex items-center gap-4">
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-purple-500"></span>
          mAIners cycles
        </span>
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-blue-500"></span>
          Protocol cycles
        </span>
      </div>
      <span>Values shown in trillion cycles (T)</span>
    </div>
  </div>
</div>
