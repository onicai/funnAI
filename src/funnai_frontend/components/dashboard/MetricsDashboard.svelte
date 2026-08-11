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
  <div class="agent-card p-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-semibold text-white">{title}</h2>
        <p class="text-sm text-gray-400 mt-1">
          Real-time insights into mAIner performance and system metrics
        </p>
      </div>
    </div>

    <!-- Quick Stats Row -->
    {#if displayMetrics && !loading}
      <div class="mt-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Current Metrics</h3>
          <div class="text-sm text-gray-400">
            Latest data from {new Date(displayMetrics.metadata.date + 'T00:00:00').toLocaleDateString()}
          </div>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-blue-400">Total mAIners</div>
          <div class="text-2xl font-semibold text-white">
            {formatChartNumber(displayMetrics.mainers.totals.created)}
          </div>
        </div>
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-emerald-400">Active mAIners</div>
          <div class="text-2xl font-semibold text-white">
            {formatChartNumber(displayMetrics.mainers.totals.active)}
          </div>
          <div class="text-xs text-emerald-400/80">
            {formatChartNumber(displayMetrics.derived_metrics.active_percentage, 'percentage')} active
          </div>
        </div>
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-agent-purple flex items-center gap-1">
            FunnAI Index
            <div class="group relative">
              <svg class="w-4 h-4 text-agent-purple cursor-help" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"></path>
              </svg>
              <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-agent-elevated text-white text-xs rounded-lg border border-white/[0.08] shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 w-48">
                <div class="text-center">
                  <div class="font-medium mb-1">FunnAI cycles burned as % of total IC protocol daily burn</div>
                </div>
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-agent-elevated"></div>
              </div>
            </div>
          </div>
          <div class="text-2xl font-semibold text-white">
            {(displayMetrics.system_metrics.funnai_index * 100).toFixed(1)}%
          </div>
        </div>
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-orange-400">Daily Burn Rate</div>
          <div class="text-xl font-semibold text-white">
            {formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.usd, 'currency')}
          </div>
          <div class="text-xs text-orange-400/80">
            {formatChartNumber(displayMetrics.system_metrics.daily_burn_rate.cycles * 1e12, 'cycles')} cycles
          </div>
        </div>
      </div>
    </div>
    {/if}
  </div>

  <!-- Additional Metrics Row -->
  {#if displayMetrics && !loading}
    <div class="agent-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-white">
          Additional Metrics
        </h3>
        <div class="flex items-center gap-2">
          <div class="bg-emerald-500/15 text-emerald-400 text-xs px-3 py-1.5 rounded-full border border-emerald-500/30">
            Latest data
          </div>
          <span class="text-sm text-gray-500">
            as of {new Date(displayMetrics.metadata.date + 'T00:00:00').toLocaleDateString()}
          </span>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-cyan-400">Total Cycles</div>
          <div class="text-xl font-semibold text-white">
            {formatChartNumber(displayMetrics.mainers.totals.total_cycles * 1e12, 'cycles')}

          </div>
        </div>
        
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-indigo-400">Avg Cycles per mAIner</div>
          <div class="text-xl font-semibold text-white">
            {formatChartNumber(displayMetrics.derived_metrics.avg_cycles_per_mainer * 1e12, 'cycles')}
          </div>
        </div>
        
        <div class="rounded-xl border border-white/[0.08] bg-white/[0.03] p-4">
          <div class="text-sm font-medium text-teal-400">Burn Rate per Active</div>
          <div class="text-xl font-semibold text-white">
            {formatChartNumber(displayMetrics.derived_metrics.burn_rate_per_active_mainer * 1e12, 'cycles')}
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Historical Charts Section -->
  <div class="agent-card">
    <!-- Charts Header with Controls -->
    <div class="p-6 border-b border-white/[0.08]">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 class="text-xl font-semibold text-white">Historical Charts</h3>
          <p class="text-sm text-gray-400 mt-1">
            View trends and patterns over time • Time filter controls all charts below
          </p>
        </div>
        
        <div class="flex items-center gap-2">
          <span class="text-sm font-medium text-gray-400">Time Period:</span>
          <TimeFilterSelector 
            selectedFilter={selectedTimeFilter} 
            onFilterChange={handleFilterChange}
          />
        </div>
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
