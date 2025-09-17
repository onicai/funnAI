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

  async function loadAllMetrics() {
    loading = true;
    error = "";
    
    try {
      // Load both latest metrics and time series data in parallel
      const [latest, timeSeries] = await Promise.all([
        DailyMetricsService.getLatestMetrics(),
        DailyMetricsService.fetchDailyMetricsByFilter(selectedTimeFilter)
      ]);
      
      latestMetrics = latest;
      timeSeriesMetrics = timeSeries;
      
      // Set display metrics based on time filter
      if (selectedTimeFilter === "all" && timeSeries.length > 0) {
        // For "all" time, show the latest available data
        displayMetrics = timeSeries[timeSeries.length - 1];
      } else if (timeSeries.length > 0) {
        // For specific time filters, show the latest data within that range
        displayMetrics = timeSeries[timeSeries.length - 1];
      } else {
        // Fallback to latest metrics if no time series data
        displayMetrics = latest;
      }
    } catch (err) {
      console.error("Error loading metrics:", err);
      error = "Failed to load metrics data";
    } finally {
      loading = false;
    }
  }

  function handleFilterChange(filter: TimeFilter) {
    selectedTimeFilter = filter;
    loadAllMetrics(); // Reload data when filter changes
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
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{title}</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Real-time insights into mAIner performance and system metrics
        </p>
      </div>
    </div>

    <!-- Quick Stats Row -->
    {#if displayMetrics && !loading}
      <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-blue-600 dark:text-blue-400">Total mAIners</div>
          <div class="text-2xl font-bold text-blue-900 dark:text-blue-300">
            {formatChartNumber(displayMetrics.mainers.totals.created)}
          </div>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-green-600 dark:text-green-400">Active mAIners</div>
          <div class="text-2xl font-bold text-green-900 dark:text-green-300">
            {formatChartNumber(displayMetrics.mainers.totals.active)}
          </div>
          <div class="text-xs text-green-600 dark:text-green-400">
            {formatChartNumber(displayMetrics.derived_metrics.active_percentage, 'percentage')} active
          </div>
        </div>
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-purple-600 dark:text-purple-400 flex items-center gap-1">
            FunnAI Index
            <div class="group relative">
              <svg class="w-4 h-4 text-purple-500 dark:text-purple-400 cursor-help" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
              </svg>
              <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 w-48">
                <div class="text-center">
                  <div class="font-medium mb-1">FunnAI cycles burned as % of total IC protocol daily burn</div>
                </div>
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
              </div>
            </div>
          </div>
          <div class="text-2xl font-bold text-purple-900 dark:text-purple-300">
            {displayMetrics.system_metrics.funnai_index.toFixed(3)}
          </div>
        </div>
        <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-orange-600 dark:text-orange-400">Daily Burn Rate</div>
          <div class="text-xl font-bold text-orange-900 dark:text-orange-300">
            {formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.usd, 'currency')}
          </div>
          <div class="text-xs text-orange-600 dark:text-orange-400">
            {formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.cycles * 1e12, 'cycles')} cycles
          </div>
        </div>
      </div>
    {/if}
  </div>

  <!-- Charts Controls -->
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Historical Charts</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          View trends and patterns over time
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
  </div>

  <!-- Charts Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- mAIner Activity Chart -->
    <div class="lg:col-span-2">
      <MainerMetricsChart 
        timeFilter={selectedTimeFilter}
        title="mAIner Activity Over Time"
        height="400px"
        preloadedData={timeSeriesMetrics}
        {loading}
      />
    </div>

    <!-- Tier Distribution Chart -->
    <TierDistributionChart 
      title="mAIner Tier Distribution"
      height="350px"
      preloadedLatestMetrics={latestMetrics}
      {loading}
    />

    <!-- System Metrics Chart -->
    <SystemMetricsChart 
      timeFilter={selectedTimeFilter}
      title="System Performance Metrics"
      height="350px"
      preloadedData={timeSeriesMetrics}
      {loading}
    />
  </div>

  <!-- Additional Metrics Row -->
  {#if displayMetrics && !loading}
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Additional Metrics
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400 ml-2">
          (as of {new Date(displayMetrics.metadata.date).toLocaleDateString()})
        </span>
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="bg-cyan-50 dark:bg-cyan-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-cyan-600 dark:text-cyan-400">Total TCycles</div>
          <div class="text-xl font-bold text-cyan-900 dark:text-cyan-300">
            {formatChartNumber(displayMetrics.mainers.totals.total_cycles, 'cycles')}
          </div>
        </div>
        
        <div class="bg-indigo-50 dark:bg-indigo-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-indigo-600 dark:text-indigo-400">Avg Cycles per mAIner</div>
          <div class="text-xl font-bold text-indigo-900 dark:text-indigo-300">
            {formatChartNumber(displayMetrics.derived_metrics.avg_cycles_per_mainer)}
          </div>
        </div>
        
        <div class="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-4">
          <div class="text-sm font-medium text-teal-600 dark:text-teal-400">Burn Rate per Active</div>
          <div class="text-xl font-bold text-teal-900 dark:text-teal-300">
            {formatChartNumber(displayMetrics.derived_metrics.burn_rate_per_active_mainer)}
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
