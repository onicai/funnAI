<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Bar } from 'svelte-chartjs';
  import { theme } from '../../stores/store';
  import { DailyMetricsService, type DailyMetricsData, type TimeFilter } from '../../helpers/DailyMetricsService';
  import { getBaseChartOptions, createDataset, formatDateLabel, formatChartNumber } from '../../helpers/chartUtils';

  export let timeFilter: TimeFilter = "15days";
  export let title: string = "System Performance Metrics";
  export let height: string = "350px";
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
            
            if (label.includes('USD')) {
              return `${label}: ${formatChartNumber(value, 'currency')}`;
            } else if (label.includes('Cycles')) {
              return `${label}: ${formatChartNumber(value, 'cycles')}`;
            } else if (label.includes('Index')) {
              return `${label}: ${value.toFixed(3)}`;
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
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        ticks: {
          color: isDark ? '#f9fafb' : '#111827',
          font: {
            size: 11
          },
          callback: function(value) {
            return Number(value).toFixed(3);
          }
        },
        grid: {
          drawOnChartArea: false,
        },
      }
    },
    interaction: {
      mode: 'index' as const,
      intersect: false
    }
  };

  async function loadChartData() {
    loading = true;
    error = "";

    try {
      const metrics = await DailyMetricsService.fetchDailyMetricsByFilter(timeFilter);
      
      if (metrics.length === 0) {
        error = "No data available for the selected time period";
        return;
      }

      // Sort by date to ensure proper chronological order
      metrics.sort((a, b) => new Date(a.metadata.date).getTime() - new Date(b.metadata.date).getTime());

      const labels = metrics.map(m => formatDateLabel(m.metadata.date, 'short'));
      
      // Prepare data for different system metrics
      const dailyBurnRateUSDData = metrics.map(m => m.system_metrics.daily_burn_rate.usd);
      const dailyBurnRateCyclesData = metrics.map(m => m.system_metrics.daily_burn_rate.cycles);
      const funnaiIndexData = metrics.map(m => m.system_metrics.funnai_index);
      const avgCyclesPerMainerData = metrics.map(m => m.derived_metrics.avg_cycles_per_mainer);

      chartData = {
        labels,
        datasets: [
          {
            ...createDataset("Daily Burn Rate (USD)", dailyBurnRateUSDData, "#ef4444", "bar"),
            yAxisID: 'y'
          },
          {
            ...createDataset("Daily Burn Rate (Cycles)", dailyBurnRateCyclesData, "#f59e0b", "bar"),
            yAxisID: 'y'
          },
          {
            ...createDataset("FunnAI Index", funnaiIndexData, "#8b5cf6", "line"),
            type: 'line' as const,
            yAxisID: 'y1',
            borderWidth: 3,
            tension: 0.4,
            fill: false
          },
          {
            ...createDataset("Avg Cycles/mAIner", avgCyclesPerMainerData, "#06b6d4", "bar"),
            yAxisID: 'y'
          }
        ]
      };

    } catch (err) {
      console.error("Error loading system metrics chart data:", err);
      error = "Failed to load chart data";
    } finally {
      loading = false;
    }
  }

  // Refresh data when time filter changes
  $: if (timeFilter) {
    loadChartData();
  }

  onMount(() => {
    loadChartData();
    
    // Update every 5 minutes
    updateInterval = setInterval(loadChartData, 5 * 60 * 1000);
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
      <Bar data={chartData} options={chartOptions} />
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

  <!-- Legend explanation for dual axis -->
  {#if !loading && !error && chartData.labels.length > 0}
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-gray-400 dark:bg-gray-500 rounded"></div>
          <span>Left axis: USD, Cycles, Avg Cycles/mAIner</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-purple-500 rounded"></div>
          <span>Right axis: FunnAI Index</span>
        </div>
      </div>
    </div>
  {/if}
</div>
