<script lang="ts">
  import { onMount } from 'svelte';
  import { DailyMetricsService, type TimeFilter, type DailyMetricsData } from '../../helpers/DailyMetricsService';
  import { formatChartNumber } from '../../helpers/chartUtils';
  
  // Import chart components
  import MainerMetricsChart from './MainerMetricsChart.svelte';
  import TierDistributionChart from './TierDistributionChart.svelte';
  import SystemMetricsChart from './SystemMetricsChart.svelte';
  import TimeFilterSelector from './TimeFilterSelector.svelte';

  export let title: string = "Daily Metrics Dashboard";

  let selectedTimeFilter: TimeFilter = "7days";
  let latestMetrics: DailyMetricsData | null = null;
  let timeSeriesMetrics: DailyMetricsData[] = [];
  let displayMetrics: DailyMetricsData | null = null; // Metrics to display based on time filter
  let loading = true;
  let error = "";

  async function loadAllMetrics(isRefresh = false) {
    if (!isRefresh && !displayMetrics) loading = true;
    error = "";
    
    try {
      // Load both latest metrics and time series data in parallel
      const [latest, timeSeries] = await Promise.all([
        DailyMetricsService.getLatestMetrics(),
        DailyMetricsService.fetchDailyMetricsByFilter(selectedTimeFilter)
      ]);
      
      latestMetrics = latest;
      timeSeriesMetrics = timeSeries;
      
      // Always use the latest metrics for the quick stats display
      // This ensures FunnAI Index and other key metrics show the most recent data
      displayMetrics = latest;
    } catch (err) {
      console.error("Error loading metrics:", err);
      error = "Failed to load metrics data";
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filter: TimeFilter) {
    selectedTimeFilter = filter;
    loadAllMetrics(true); // Reload data when filter changes without collapsing tiles
  }

  function handleRefreshAll() {
    DailyMetricsService.clearCache();
    loadAllMetrics();
  }

  onMount(() => {
    loadAllMetrics();
  });
</script>

<div class="space-y-6">
  <!-- Dashboard Header -->
  <div class="agent-card bg-agent-surface! p-5 sm:p-6">
    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
      <div>
        <p class="agent-eyebrow">Metrics</p>
        <h2 class="mt-1 text-base font-semibold tracking-tight text-white">{title}</h2>
        <p class="mt-0.5 text-sm text-gray-500">
          Real-time insights into mAIner performance and system metrics
        </p>
      </div>
    </div>

    <div class="mt-5">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500 mb-3 min-h-4">
        {#if displayMetrics}
          Latest · {new Date(displayMetrics.metadata.date + 'T00:00:00').toLocaleDateString()}
        {:else}
          Latest
        {/if}
      </p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="rounded-xl bg-white/3 p-4">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Total mAIners</p>
          <p class="agent-metric-value">
            {#if displayMetrics}
              <span class="min-w-[4ch]">{formatChartNumber(displayMetrics.mainers.totals.created)}</span>
            {:else}
              <span class="agent-metric-pulse w-[4ch]" aria-hidden="true"></span>
            {/if}
          </p>
        </div>
        <div class="rounded-xl bg-white/3 p-4">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Active</p>
          <p class="agent-metric-value">
            {#if displayMetrics}
              <span class="min-w-[4ch]">{formatChartNumber(displayMetrics.mainers.totals.active)}</span>
            {:else}
              <span class="agent-metric-pulse w-[4ch]" aria-hidden="true"></span>
            {/if}
          </p>
          <p class="agent-metric-hint text-emerald-400/80">
            {#if displayMetrics}
              {formatChartNumber(displayMetrics.derived_metrics.active_percentage, 'percentage')} of fleet
            {:else}
              &nbsp;
            {/if}
          </p>
        </div>
        <div class="rounded-xl bg-white/3 p-4">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500 flex items-center gap-1">
            FunnAI Index
            <span class="group relative">
              <svg class="w-3.5 h-3.5 text-gray-500 cursor-help" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
              </svg>
              <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-agent-elevated text-white text-xs rounded-lg border border-white/8 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 w-48 text-center font-normal normal-case tracking-normal">
                FunnAI cycles burned as % of total IC protocol daily burn
              </span>
            </span>
          </p>
          <p class="agent-metric-value">
            {#if displayMetrics}
              <span class="min-w-[4ch]">{(displayMetrics.system_metrics.funnai_index * 100).toFixed(1)}%</span>
            {:else}
              <span class="agent-metric-pulse w-[4ch]" aria-hidden="true"></span>
            {/if}
          </p>
        </div>
        <div class="rounded-xl bg-white/3 p-4">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Daily burn</p>
          <p class="agent-metric-value-md">
            {#if displayMetrics}
              <span class="min-w-[6ch]">{formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.usd, 'currency')}</span>
            {:else}
              <span class="agent-metric-pulse w-[6ch]" aria-hidden="true"></span>
            {/if}
          </p>
          <p class="agent-metric-hint">
            {#if displayMetrics}
              {formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.cycles * 1e12, 'cycles')} cycles
            {:else}
              &nbsp;
            {/if}
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- Additional Metrics Row -->
  <div class="agent-card bg-agent-surface! p-5 sm:p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <p class="agent-eyebrow">Inventory</p>
        <h3 class="mt-1 text-base font-semibold tracking-tight text-white">Additional metrics</h3>
      </div>
      <span class="text-xs text-gray-500 min-h-4 min-w-24 text-right">
        {#if displayMetrics}
          {new Date(displayMetrics.metadata.date + 'T00:00:00').toLocaleDateString()}
        {/if}
      </span>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div class="rounded-xl bg-white/3 p-4">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Total cycles</p>
        <p class="agent-metric-value-md">
          {#if displayMetrics}
            <span class="min-w-[8ch]">{formatChartNumber(displayMetrics.mainers.totals.total_cycles * 1e12, 'cycles')}</span>
          {:else}
            <span class="agent-metric-pulse w-[8ch]" aria-hidden="true"></span>
          {/if}
        </p>
      </div>
      
      <div class="rounded-xl bg-white/3 p-4">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Avg per mAIner</p>
        <p class="agent-metric-value-md">
          {#if displayMetrics}
            <span class="min-w-[8ch]">{formatChartNumber(displayMetrics.derived_metrics.avg_cycles_per_mainer * 1e12, 'cycles')}</span>
          {:else}
            <span class="agent-metric-pulse w-[8ch]" aria-hidden="true"></span>
          {/if}
        </p>
      </div>
      
      <div class="rounded-xl bg-white/3 p-4">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Burn per active</p>
        <p class="agent-metric-value-md">
          {#if displayMetrics}
            <span class="min-w-[8ch]">{formatChartNumber(displayMetrics.derived_metrics.burn_rate_per_active_mainer * 1e12, 'cycles')}</span>
          {:else}
            <span class="agent-metric-pulse w-[8ch]" aria-hidden="true"></span>
          {/if}
        </p>
      </div>
    </div>
  </div>

  <!-- Historical Charts Section -->
  <div class="agent-card bg-agent-surface!">
    <div class="p-5 sm:p-6 border-b border-white/6">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p class="agent-eyebrow">History</p>
          <h3 class="mt-1 text-base font-semibold tracking-tight text-white">Historical charts</h3>
          <p class="mt-0.5 text-sm text-gray-500">Trends over the selected period</p>
        </div>
        
        <TimeFilterSelector 
          selectedFilter={selectedTimeFilter} 
          onFilterChange={handleFilterChange}
        />
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="p-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- mAIner Activity Chart -->
        <div class="lg:col-span-2">
          <div class="relative">
            <!-- Filter indicator -->
            <div class="absolute top-2 right-2 z-10">
              <div class="bg-agent-purple/15 text-agent-purple text-xs px-3 py-1.5 rounded-full border border-agent-purple/30">
                {selectedTimeFilter === "7days" ? "Last 7 days" : 
                 selectedTimeFilter === "15days" ? "Last 15 days" :
                 selectedTimeFilter === "1month" ? "Last month" : "All time"}
              </div>
            </div>
            <MainerMetricsChart 
              timeFilter={selectedTimeFilter}
              title="mAIner Activity Over Time"
              height="400px"
              preloadedData={timeSeriesMetrics}
              {loading}
            />
          </div>
        </div>

        <!-- Tier Distribution Chart -->
        <div class="relative">
          <!-- Filter indicator -->
          <div class="absolute top-2 right-2 z-10">
            <div class="bg-emerald-500/15 text-emerald-400 text-xs px-3 py-1.5 rounded-full border border-emerald-500/30">
              Latest data
            </div>
          </div>
          <TierDistributionChart 
            title="mAIner Tier Distribution"
            height="350px"
            preloadedLatestMetrics={latestMetrics}
            {loading}
          />
        </div>

        <!-- System Metrics Chart -->
        <div class="relative">
          <!-- Filter indicator -->
          <div class="absolute top-2 right-2 z-10">
            <div class="bg-agent-purple/15 text-agent-purple text-xs px-3 py-1.5 rounded-full border border-agent-purple/30">
              {selectedTimeFilter === "7days" ? "Last 7 days" : 
               selectedTimeFilter === "15days" ? "Last 15 days" :
               selectedTimeFilter === "1month" ? "Last month" : "All time"}
            </div>
          </div>
          <SystemMetricsChart 
            timeFilter={selectedTimeFilter}
            title="System Performance Metrics"
            height="350px"
            preloadedData={timeSeriesMetrics}
            {loading}
          />
        </div>
      </div>
    </div>
  </div>

  

  <!-- Data freshness indicator 
  {#if latestMetrics}
    <div class="text-center">
      <p class="text-xs text-gray-500">
        Data last updated: {new Date(parseInt(latestMetrics.metadata.updated_at) / 1000000).toLocaleString()}
      </p>
    </div>
  {/if}-->
</div>
