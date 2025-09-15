<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Doughnut } from 'svelte-chartjs';
  import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale
  } from 'chart.js';
  import { theme } from '../../stores/store';
  import { DailyMetricsService, type DailyMetricsData } from '../../helpers/DailyMetricsService';
  import { getBaseChartOptions, generatePieColors, formatChartNumber } from '../../helpers/chartUtils';

  // Register Chart.js components
  ChartJS.register(
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale
  );

  export let title: string = "mAIner Tier Distribution";
  export let height: string = "300px";
  export let showLatestOnly: boolean = true;

  let loading = true;
  let error = "";
  let chartData = {
    labels: [],
    datasets: []
  };
  let chartOptions = {};
  let updateInterval: NodeJS.Timer;
  let latestMetrics: DailyMetricsData | null = null;

  // Theme reactivity
  $: isDark = $theme === 'dark';
  $: chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: isDark ? '#f9fafb' : '#111827',
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          },
          generateLabels: function(chart) {
            const data = chart.data;
            if (data.labels?.length && data.datasets?.length) {
              return data.labels.map((label, i) => {
                const dataset = data.datasets[0];
                const value = dataset.data[i];
                const percentage = ((value / dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                return {
                  text: `${label}: ${percentage}%`,
                  fillStyle: dataset.backgroundColor[i],
                  strokeStyle: dataset.backgroundColor[i],
                  lineWidth: 0,
                  pointStyle: 'circle',
                  hidden: false,
                  index: i
                };
              });
            }
            return [];
          }
        }
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#ffffff',
        titleColor: isDark ? '#f9fafb' : '#111827',
        bodyColor: isDark ? '#f9fafb' : '#111827',
        borderColor: isDark ? '#4b5563' : '#d1d5db',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${formatChartNumber(value)} (${percentage}%)`;
          }
        }
      }
    },
    cutout: '50%', // Makes it a doughnut chart
    radius: '90%'
  };

  async function loadChartData() {
    loading = true;
    error = "";

    try {
      if (showLatestOnly) {
        latestMetrics = await DailyMetricsService.getLatestMetrics();
        
        if (!latestMetrics) {
          error = "No metrics data available";
          return;
        }

        const tierData = latestMetrics.derived_metrics.tier_distribution;
        
        // Prepare data for the chart
        const labels = ['Low Tier', 'Medium Tier', 'High Tier', 'Very High Tier'];
        const data = [
          tierData.low,
          tierData.medium,
          tierData.high,
          tierData.very_high
        ];

        // Filter out zero values
        const filteredLabels = [];
        const filteredData = [];
        const colors = generatePieColors(4);
        const filteredColors = [];

        for (let i = 0; i < data.length; i++) {
          if (data[i] > 0) {
            filteredLabels.push(labels[i]);
            filteredData.push(data[i]);
            filteredColors.push(colors[i]);
          }
        }

        chartData = {
          labels: filteredLabels,
          datasets: [
            {
              data: filteredData,
              backgroundColor: filteredColors,
              borderColor: filteredColors.map(color => color + '80'),
              borderWidth: 2,
              hoverOffset: 4
            }
          ]
        };
      }

    } catch (err) {
      console.error("Error loading tier distribution chart data:", err);
      error = "Failed to load chart data";
    } finally {
      loading = false;
    }
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
    <div>
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {title}
      </h3>
      {#if latestMetrics}
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Data from {new Date(latestMetrics.metadata.date).toLocaleDateString()}
        </p>
      {/if}
    </div>
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
      <Doughnut data={chartData} options={chartOptions} />
    {:else if !error}
      <div class="absolute inset-0 flex items-center justify-center text-gray-500 dark:text-gray-400">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
          <p class="text-sm">No data available</p>
        </div>
      </div>
    {/if}
  </div>

  <!-- Summary stats below the chart -->
  {#if latestMetrics && !loading && !error}
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-600 dark:text-gray-400">Total Active:</span>
          <span class="font-medium text-gray-900 dark:text-white ml-2">
            {formatChartNumber(latestMetrics.mainers.totals.active)}
          </span>
        </div>
        <div>
          <span class="text-gray-600 dark:text-gray-400">Active %:</span>
          <span class="font-medium text-green-600 dark:text-green-400 ml-2">
            {formatChartNumber(latestMetrics.derived_metrics.active_percentage, 'percentage')}
          </span>
        </div>
      </div>
    </div>
  {/if}
</div>
