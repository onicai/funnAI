<script lang="ts">
  import { onMount } from 'svelte';
  import { Line, Bar } from 'svelte-chartjs';
  import { theme } from '../../stores/store';
  import { getBaseChartOptions, createDataset, formatChartNumber } from '../../helpers/chartUtils';
  import { TokenRewardsService, type TokenRewardsData } from '../../helpers/TokenRewardsService';

  export let title: string = "Token Rewards & Supply Analytics";
  export let height: string = "400px";
  export let activeView: 'supply' | 'combined' = 'supply';

  let loading = true;
  let error = "";
  let tokenRewardsData: TokenRewardsData | null = null;

  // Theme reactivity
  $: isDark = $theme === 'dark';

  // Load token rewards data from API canister
  async function loadTokenRewardsData() {
    try {
      loading = true;
      error = "";
      tokenRewardsData = await TokenRewardsService.fetchTokenRewardsData();
    } catch (err) {
      console.error('Error loading token rewards data:', err);
      error = "Failed to load token rewards data";
    } finally {
      loading = false;
    }
  }

  // Process the token rewards data - now include ALL data points
  $: allData = tokenRewardsData ? tokenRewardsData.data : [];
  
  // Create labels with smart spacing to avoid overcrowding
  $: chartLabels = allData.map((item, index) => {
    const date = new Date(item.date);
    // Show every other label for better readability, but always show first and last
    if (index === 0 || index === allData.length - 1 || index % 2 === 0) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return ''; // Empty string for hidden labels
  });

  // Supply Timeline Chart Data
  $: supplyChartData = {
    labels: chartLabels,
    datasets: [
      createDataset(
        'Total Supply (FUNNAI)',
        allData.map(item => item.total_minted / 1000000), // Convert to millions
        isDark ? '#60A5FA' : '#3B82F6',
        'area'
      ),
      // Max supply reached marker
      {
        label: 'Max Supply Reached',
        data: allData.map((item, index) => {
          return item.date === '2033-06-29' ? item.total_minted / 1000000 : null;
        }),
        type: 'line',
        backgroundColor: isDark ? '#EF4444' : '#DC2626',
        borderColor: isDark ? '#EF4444' : '#DC2626',
        borderWidth: 0,
        pointRadius: 10,
        pointHoverRadius: 12,
        showLine: false,
        pointStyle: 'triangle',
        pointBorderWidth: 3,
        fill: false,
        tension: 0
      }
    ]
  };

  // Rewards Decay Chart Data - filter out first data point if it's Q2 2025
  $: rewardsData = allData.filter(item => item.quarter !== 'Q2 2025' && item.quarter !== '');
  $: rewardsChartLabels = rewardsData.map((item, index) => {
    const date = new Date(item.date);
    // Show every other label for better readability, but always show first and last
    if (index === 0 || index === rewardsData.length - 1 || index % 2 === 0) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    return ''; // Empty string for hidden labels
  });
  $: rewardsChartData = {
    labels: rewardsChartLabels,
    datasets: [
      {
        label: 'Rewards per Challenge',
        data: rewardsData.map(item => item.rewards_per_challenge),
        backgroundColor: isDark ? 'rgba(248, 113, 113, 0.7)' : 'rgba(239, 68, 68, 0.8)',
        borderColor: isDark ? '#F87171' : '#EF4444',
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
        hoverBackgroundColor: isDark ? 'rgba(248, 113, 113, 0.9)' : 'rgba(239, 68, 68, 0.95)',
        hoverBorderColor: isDark ? '#FCA5A5' : '#DC2626',
        hoverBorderWidth: 3,
      },
      // Stabilization point marker
      {
        label: 'Stabilization Point',
        data: rewardsData.map((item, index) => {
          return item.date === '2027-06-29' ? item.rewards_per_challenge : null;
        }),
        type: 'line',
        backgroundColor: isDark ? '#F59E0B' : '#D97706',
        borderColor: isDark ? '#F59E0B' : '#D97706',
        borderWidth: 0,
        pointRadius: 10,
        pointHoverRadius: 12,
        showLine: false,
        pointStyle: 'rectRot',
        pointBorderWidth: 3,
        fill: false,
        tension: 0
      }
    ]
  };

  // Quarterly Growth Chart Data - use rewards_per_quarter from API
  $: growthData = allData.filter(item => item.rewards_per_quarter && item.rewards_per_quarter > 0);
  $: growthChartData = {
    labels: growthData.map(item => item.quarter),
    datasets: [
      {
        label: 'Quarterly Minting (FUNNAI)',
        data: growthData.map(item => item.rewards_per_quarter / 1000000), // Convert to millions
        backgroundColor: isDark ? 'rgba(34, 197, 94, 0.7)' : 'rgba(34, 197, 94, 0.8)',
        borderColor: isDark ? '#22C55E' : '#16A34A',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      },
      // Stabilization point marker
      {
        label: 'Stabilization Point',
        data: growthData.map((item, index) => {
          return item.quarter === 'Q3 2027' ? item.rewards_per_quarter / 1000000 : null;
        }),
        type: 'line',
        backgroundColor: isDark ? '#F59E0B' : '#D97706',
        borderColor: isDark ? '#F59E0B' : '#D97706',
        borderWidth: 0,
        pointRadius: 10,
        pointHoverRadius: 12,
        showLine: false,
        pointStyle: 'rectRot',
        pointBorderWidth: 3,
        fill: false,
        tension: 0
      }
    ]
  };

  // Combined Rewards & Growth Chart Data - filter out Q2 2025 and empty quarters
  $: combinedData = allData.filter(item => item.quarter !== 'Q2 2025' && item.quarter !== '');
  $: combinedChartData = {
    labels: combinedData.map(item => item.quarter),
    datasets: [
      // Quarterly Minting bars
      {
        label: 'Quarterly Minting (FUNNAI)',
        data: combinedData.map(item => item.rewards_per_quarter ? item.rewards_per_quarter / 1000000 : 0), // Convert to millions, show 0 for null
        backgroundColor: isDark ? 'rgba(34, 197, 94, 0.7)' : 'rgba(34, 197, 94, 0.8)',
        borderColor: isDark ? '#22C55E' : '#16A34A',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
        yAxisID: 'y1',
        type: 'bar'
      },
      // Rewards per challenge bars (directly mapped by quarter)
      {
        label: 'Rewards per Challenge',
        data: combinedData.map(item => item.rewards_per_challenge),
        backgroundColor: isDark ? 'rgba(248, 113, 113, 0.7)' : 'rgba(239, 68, 68, 0.8)',
        borderColor: isDark ? '#F87171' : '#EF4444',
        borderWidth: 3,
        borderRadius: 8,
        borderSkipped: false,
        yAxisID: 'y',
        type: 'bar',
        hoverBackgroundColor: isDark ? 'rgba(248, 113, 113, 0.9)' : 'rgba(239, 68, 68, 0.95)',
        hoverBorderColor: isDark ? '#FCA5A5' : '#DC2626',
        hoverBorderWidth: 3,
      },
      // Stabilization point marker for quarterly minting (positioned higher)
      {
        label: 'Stabilization Point',
        data: combinedData.map((item, index) => {
          return item.quarter === 'Q3 2027' ? (item.rewards_per_quarter ? item.rewards_per_quarter / 1000000 : 0) + 1.25 : null;
        }),
        type: 'line',
        backgroundColor: isDark ? '#F59E0B' : '#D97706',
        borderColor: isDark ? '#F59E0B' : '#D97706',
        borderWidth: 0,
        pointRadius: 10,
        pointHoverRadius: 12,
        showLine: false,
        pointStyle: 'rectRot',
        pointBorderWidth: 3,
        fill: false,
        tension: 0,
        yAxisID: 'y1'
      }
    ]
  };


  // Chart Options
  $: supplyChartOptions = {
    ...getBaseChartOptions(isDark),
    scales: {
      ...getBaseChartOptions(isDark).scales,
      x: {
        ...getBaseChartOptions(isDark).scales.x,
        ticks: {
          ...getBaseChartOptions(isDark).scales.x.ticks,
          maxTicksLimit: 8, // Limit number of x-axis labels
          maxRotation: 45, // Rotate labels for better fit
          minRotation: 0
        }
      },
      y: {
        ...getBaseChartOptions(isDark).scales.y,
        title: {
          display: true,
          text: 'Supply (Millions of FUNNAI)',
          color: isDark ? '#D1D5DB' : '#6B7280'
        },
        ticks: {
          ...getBaseChartOptions(isDark).scales.y.ticks,
          callback: function(value) {
            return value.toFixed(1) + 'M';
          }
        }
      }
    },
    plugins: {
      ...getBaseChartOptions(isDark).plugins,
      tooltip: {
        ...getBaseChartOptions(isDark).plugins.tooltip,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${(context.parsed.y * 1000000).toLocaleString()} FUNNAI`;
          }
        }
      }
    }
  };

  $: rewardsChartOptions = {
    ...getBaseChartOptions(isDark),
    scales: {
      ...getBaseChartOptions(isDark).scales,
      x: {
        ...getBaseChartOptions(isDark).scales.x,
        ticks: {
          ...getBaseChartOptions(isDark).scales.x.ticks,
          maxTicksLimit: 8, // Limit number of x-axis labels
          maxRotation: 45, // Rotate labels for better fit
          minRotation: 0
        }
      },
      y: {
        ...getBaseChartOptions(isDark).scales.y,
        title: {
          display: true,
          text: 'Rewards per Challenge (FUNNAI)',
          color: isDark ? '#D1D5DB' : '#6B7280'
        }
      }
    },
    plugins: {
      ...getBaseChartOptions(isDark).plugins,
      tooltip: {
        ...getBaseChartOptions(isDark).plugins.tooltip,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} FUNNAI`;
          }
        }
      }
    }
  };

  $: growthChartOptions = {
    ...getBaseChartOptions(isDark),
    scales: {
      ...getBaseChartOptions(isDark).scales,
      y: {
        ...getBaseChartOptions(isDark).scales.y,
        title: {
          display: true,
          text: 'Quarterly Minting (Millions of FUNNAI)',
          color: isDark ? '#D1D5DB' : '#6B7280'
        },
        ticks: {
          ...getBaseChartOptions(isDark).scales.y.ticks,
          callback: function(value) {
            return value.toFixed(1) + 'M';
          }
        }
      }
    },
    plugins: {
      ...getBaseChartOptions(isDark).plugins,
      tooltip: {
        ...getBaseChartOptions(isDark).plugins.tooltip,
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${(context.parsed.y * 1000000).toLocaleString()} FUNNAI`;
          }
        }
      }
    }
  };

  $: combinedChartOptions = {
    ...getBaseChartOptions(isDark),
    scales: {
      ...getBaseChartOptions(isDark).scales,
      y: {
        ...getBaseChartOptions(isDark).scales.y,
        type: 'linear',
        position: 'left',
        title: {
          display: true,
          text: 'Rewards per Challenge (FUNNAI)',
          color: isDark ? '#F87171' : '#EF4444'
        },
        ticks: {
          ...getBaseChartOptions(isDark).scales.y.ticks,
          callback: function(value) {
            return value.toFixed(2);
          }
        },
        grid: {
          color: isDark ? 'rgba(248, 113, 113, 0.1)' : 'rgba(239, 68, 68, 0.1)'
        }
      },
      y1: {
        ...getBaseChartOptions(isDark).scales.y,
        type: 'linear',
        position: 'right',
        title: {
          display: true,
          text: 'Quarterly Minting (Millions of FUNNAI)',
          color: isDark ? '#22C55E' : '#16A34A'
        },
        ticks: {
          ...getBaseChartOptions(isDark).scales.y.ticks,
          callback: function(value) {
            return value.toFixed(1) + 'M';
          }
        },
        grid: {
          drawOnChartArea: false, // Don't draw grid lines for secondary axis
        }
      }
    },
    plugins: {
      ...getBaseChartOptions(isDark).plugins,
      tooltip: {
        ...getBaseChartOptions(isDark).plugins.tooltip,
        callbacks: {
          label: function(context) {
            if (context.dataset.label === 'Quarterly Minting (FUNNAI)') {
              return `${context.dataset.label}: ${(context.parsed.y * 1000000).toLocaleString()} FUNNAI`;
            } else if (context.dataset.label === 'Rewards per Challenge') {
              return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} FUNNAI`;
            } else if (context.dataset.label.includes('Stabilization Point')) {
              return "Rewards per challenge stabilized at 34.96 from this date onward until max supply is reached";
            }
            return `${context.dataset.label}: ${context.parsed.y}`;
          }
        }
      }
    }
  };


  function setActiveView(view: typeof activeView) {
    activeView = view;
  }

  onMount(() => {
    loadTokenRewardsData();
  });
</script>

<div class="agent-card !bg-agent-surface p-5 sm:p-6">
  <div class="relative z-[1] flex items-center justify-between mb-5">
    <div>
      <p class="agent-eyebrow">Analytics</p>
      <h3 class="mt-1 text-base font-semibold tracking-tight text-white">{title}</h3>
      <p class="mt-0.5 text-sm text-gray-500">Supply growth and quarterly minting</p>
    </div>
    <span class="inline-flex h-4 w-4 items-center justify-center">
      {#if loading}
        <span class="h-4 w-4 border-2 border-[#653FC5] rounded-full border-t-transparent animate-spin"></span>
      {/if}
    </span>
  </div>

  {#if error}
    <div class="text-red-400 text-sm mb-4 p-3 bg-red-950/40 rounded-lg border border-red-500/40">
      {error}
    </div>
  {/if}

  <!-- View Selector -->
  <div class="agent-tab-track mb-6 flex-wrap">
    <button
      class="agent-tab {activeView === 'supply' ? 'agent-tab-active' : ''}"
      on:click={() => setActiveView('supply')}
    >
      Supply Timeline
    </button>
    <button
      class="agent-tab {activeView === 'combined' ? 'agent-tab-active' : ''}"
      on:click={() => setActiveView('combined')}
    >
      Rewards & Minting
    </button>
  </div>

  <!-- Chart Content -->
  <div class="relative" style="height: {height}">
    {#if loading}
      <div class="absolute inset-0 flex items-center justify-center bg-agent-surface/80 rounded-lg">
        <div class="text-center">
          <div class="animate-spin h-8 w-8 border-4 border-agent-purple rounded-full border-t-transparent mx-auto mb-2"></div>
          <p class="text-sm text-gray-400">Loading token rewards data...</p>
        </div>
      </div>
    {:else if error}
      <div class="absolute inset-0 flex items-center justify-center text-red-400">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm">{error}</p>
        </div>
      </div>
    {:else if activeView === 'supply'}
      <div class="mb-4">
        <h4 class="text-md font-semibold text-white mb-2">Total Supply Growth Timeline</h4>
        <p class="text-sm text-gray-400">Projected FUNNAI token supply from launch to maximum supply</p>
      </div>
      <div style="height: 350px;">
        <Line data={supplyChartData} options={supplyChartOptions} />
      </div>
    {:else if activeView === 'combined'}
      <div class="mb-4">
        <h4 class="text-md font-semibold text-white mb-2">Quarterly Minting & Rewards Analysis</h4>
        <p class="text-sm text-gray-400">Combined view showing quarterly token minting (green bars) and rewards per challenge (red bars) with stabilization points</p>
      </div>
      <div style="height: 350px;">
        <Bar data={combinedChartData} options={combinedChartOptions} />
      </div>
    {/if}
  </div>

  <!-- Data Source Footer -->
  {#if tokenRewardsData}
    <div class="mt-4 pt-4 border-t border-white/[0.08]">
      <p class="text-xs text-gray-500 text-center">
        Data source: {tokenRewardsData.metadata.dataset} • Last updated: {tokenRewardsData.metadata.last_updated}
      </p>
    </div>
  {/if}
</div>
