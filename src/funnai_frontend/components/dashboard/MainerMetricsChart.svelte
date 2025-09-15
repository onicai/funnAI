<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Line } from 'svelte-chartjs';
  import { theme } from '../../stores/store';
  import { DailyMetricsService, type DailyMetricsData, type TimeFilter } from '../../helpers/DailyMetricsService';
  import { getBaseChartOptions, createDataset, formatDateLabel, formatChartNumber } from '../../helpers/chartUtils';

  export let timeFilter: TimeFilter = "7days";
  export let title: string = "mAIner Activity Over Time";
  export let height: string = "300px";
  export let preloadedData: DailyMetricsData[] = [];
  export let loading: boolean = true;

  let error = "";
  let chartData = {
    labels: [],
    datasets: []
  };
  let chartOptions = {};
  let updateInterval: NodeJS.Timer;

  // Theme reactivity
  $: isDark = $theme === 'dark';
  $: chartOptions = {
    ...getBaseChartOptions(isDark),
    plugins: {
      ...getBaseChartOptions(isDark).plugins,
      title: {
        display: false
      },
      tooltip: {
        ...getBaseChartOptions(isDark).plugins.tooltip,
        callbacks: {
          label: function(context) {
            const label = context.dataset.label || '';
            const value = context.parsed.y;
            
            if (label.includes('Cycles')) {
              return `${label}: ${formatChartNumber(value, 'cycles')}`;
            } else {
              return `${label}: ${formatChartNumber(value)}`;
            }
          }
        }
      }
    },
    scales: {
      ...getBaseChartOptions(isDark).scales,
      y: {
        ...getBaseChartOptions(isDark).scales.y,
        beginAtZero: true,
        ticks: {
          ...getBaseChartOptions(isDark).scales.y.ticks,
          callback: function(value) {
            return formatChartNumber(Number(value));
          }
        }
      }
    }
  };

  function processChartData(metrics: DailyMetricsData[]) {
    error = "";

    try {
      if (metrics.length === 0) {
        error = "No data available for the selected time period";
        return;
      }

      // Sort by date to ensure proper chronological order
      const sortedMetrics = [...metrics].sort((a, b) => 
        new Date(a.metadata.date).getTime() - new Date(b.metadata.date).getTime()
      );

      const labels = sortedMetrics.map(m => formatDateLabel(m.metadata.date, 'short'));
      
      // Prepare data for different metrics
      const totalMainersData = sortedMetrics.map(m => m.mainers.totals.created);
      const activeMainersData = sortedMetrics.map(m => m.mainers.totals.active);
      const pausedMainersData = sortedMetrics.map(m => m.mainers.totals.paused);

      chartData = {
        labels,
        datasets: [
          createDataset("Total mAIners", totalMainersData, "#8b5cf6", "line"),
          createDataset("Active mAIners", activeMainersData, "#10b981", "line"),
          createDataset("Paused mAIners", pausedMainersData, "#f59e0b", "line"),
        ]
      };

    } catch (err) {
      console.error("Error processing mAIner metrics chart data:", err);
      error = "Failed to process chart data";
    }
  }

  // Fallback function for when no preloaded data is available
  async function loadChartData() {
    try {
      const metrics = await DailyMetricsService.fetchDailyMetricsByFilter(timeFilter);
      processChartData(metrics);
    } catch (err) {
      console.error("Error loading mAIner metrics chart data:", err);
      error = "Failed to load chart data";
    }
  }

  // Process preloaded data or load data when it changes
  $: if (preloadedData && preloadedData.length > 0) {
    processChartData(preloadedData);
  } else if (!loading) {
    // Only load data if not already loading and no preloaded data
    loadChartData();
  }

  onMount(() => {
    // If we have preloaded data, use it; otherwise load data
    if (preloadedData && preloadedData.length > 0) {
      processChartData(preloadedData);
    } else {
      loadChartData();
    }
    
    // Update every 5 minutes (only if no preloaded data)
    if (!preloadedData || preloadedData.length === 0) {
      updateInterval = setInterval(loadChartData, 5 * 60 * 1000);
    }
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  function handleRefresh() {
    DailyMetricsService.clearCache();
    loadChartData();
  }
</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      {title}
    </h3>
    <div class="flex items-center gap-2">
      {#if loading}
        <div class="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      {/if}
      <button 
        on:click={handleRefresh}
        class="text-xs text-blue-600 dark:text-blue-400 hover:underline px-2 py-1 rounded hover:bg-blue-50 dark:hover:bg-blue-900/20"
        disabled={loading}
      >
        Refresh
      </button>
    </div>
  </div>

  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      {error}
    </div>
  {/if}

  <div class="relative" style="height: {height}">
    {#if loading}
      <div class="absolute inset-0 flex items-center justify-center bg-gray-50 dark:bg-gray-700/50 rounded-lg">
        <div class="text-center">
          <div class="animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent mx-auto mb-2"></div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Loading chart data...</p>
        </div>
      </div>
    {:else if !error && chartData.labels.length > 0}
      <Line data={chartData} options={chartOptions} />
    {:else if !error}
      <div class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2z" />
          </svg>
          <p class="text-sm">No data available</p>
        </div>
      </div>
    {/if}
  </div>
</div>
