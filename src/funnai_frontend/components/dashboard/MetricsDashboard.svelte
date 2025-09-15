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

  let selectedTimeFilter: TimeFilter = "1month";
  let latestMetrics: DailyMetricsData | null = null;
  let loading = true;
  let error = "";

  async function loadLatestMetrics() {
    try {
      latestMetrics = await DailyMetricsService.getLatestMetrics();
    } catch (err) {
      console.error("Error loading latest metrics:", err);
      error = "Failed to load latest metrics";
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filter: TimeFilter) {
    selectedTimeFilter = filter;
  }

  function handleRefreshAll() {
    DailyMetricsService.clearCache();
    loadLatestMetrics();
    // The individual charts will refresh themselves
  }

  onMount(() => {
    loadLatestMetrics();
  });
</script>

<div class="space-y-6">
  <!-- Dashboard Header -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{title}</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Real-time insights into mAIner performance and system metrics
        </p>
      </div>
      
      <div class="flex items-center gap-4">
        <TimeFilterSelector 
          selectedFilter={selectedTimeFilter} 
          onFilterChange={handleFilterChange}
        />
        <button 
          on:click={handleRefreshAll}
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh All"}
        </button>
      </div>
    </div>

    <!-- Quick Stats Row -->
    {#if latestMetrics && !loading}
      <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-blue-600 dark:text-blue-400">Total mAIners</div>
          <div class="text-2xl font-bold text-blue-900 dark:text-blue-300">
            {formatChartNumber(latestMetrics.mainers.totals.created)}
          </div>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-green-600 dark:text-green-400">Active mAIners</div>
          <div class="text-2xl font-bold text-green-900 dark:text-green-300">
            {formatChartNumber(latestMetrics.mainers.totals.active)}
          </div>
          <div class="text-xs text-green-600 dark:text-green-400">
            {formatChartNumber(latestMetrics.derived_metrics.active_percentage, 'percentage')} active
          </div>
        </div>
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-purple-600 dark:text-purple-400">FunnAI Index</div>
          <div class="text-2xl font-bold text-purple-900 dark:text-purple-300">
            {latestMetrics.system_metrics.funnai_index.toFixed(3)}
          </div>
        </div>
        <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-orange-600 dark:text-orange-400">Daily Burn Rate</div>
          <div class="text-xl font-bold text-orange-900 dark:text-orange-300">
            {formatChartNumber(latestMetrics.system_metrics.daily_burn_rate.usd, 'currency')}
          </div>
          <div class="text-xs text-orange-600 dark:text-orange-400">
            {formatChartNumber(latestMetrics.system_metrics.daily_burn_rate.cycles, 'cycles')} cycles
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Charts Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- mAIner Activity Chart -->
    <div class="lg:col-span-2">
      <MainerMetricsChart 
        timeFilter={selectedTimeFilter}
        title="mAIner Activity Over Time"
        height="400px"
      />
    </div>

    <!-- Tier Distribution Chart -->
    <TierDistributionChart 
      title="Current Tier Distribution"
      height="350px"
    />

    <!-- System Metrics Chart -->
    <SystemMetricsChart 
      timeFilter={selectedTimeFilter}
      title="System Performance Metrics"
      height="350px"
    />
  </div>

  <!-- Additional Metrics Row -->
  {#if latestMetrics && !loading}
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Additional Metrics
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
          (as of {new Date(latestMetrics.metadata.date).toLocaleDateString()})
        </span>
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="space-y-2">
          <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Cycles</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-white">
            {formatChartNumber(latestMetrics.mainers.totals.total_cycles, 'cycles')}
          </div>
        </div>
        
        <div class="space-y-2">
          <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Cycles per mAIner</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-white">
            {formatChartNumber(latestMetrics.derived_metrics.avg_cycles_per_mainer)}
          </div>
        </div>
        
        <div class="space-y-2">
          <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Burn Rate per Active</div>
          <div class="text-lg font-semibold text-gray-900 dark:text-white">
            {formatChartNumber(latestMetrics.derived_metrics.burn_rate_per_active_mainer)}
          </div>
        </div>
        
        <div class="space-y-2">
          <div class="text-sm font-medium text-gray-600 dark:text-gray-400">Paused Percentage</div>
          <div class="text-lg font-semibold text-red-600 dark:text-red-400">
            {formatChartNumber(latestMetrics.derived_metrics.paused_percentage, 'percentage')}
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Data freshness indicator -->
  {#if latestMetrics}
    <div class="text-center">
      <p class="text-xs text-gray-500 dark:text-gray-400">
        Data last updated: {new Date(parseInt(latestMetrics.metadata.updated_at) / 1000000).toLocaleString()}
      </p>
    </div>
  {/if}
</div>
