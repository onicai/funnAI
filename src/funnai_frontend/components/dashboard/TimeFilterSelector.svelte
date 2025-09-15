<script lang="ts">
  import type { TimeFilter } from '../../helpers/DailyMetricsService';

  export let selectedFilter: TimeFilter = "1month";
  export let onFilterChange: (filter: TimeFilter) => void = () => {};

  const filters: { value: TimeFilter; label: string; description: string }[] = [
    { value: "15days", label: "15 Days", description: "Last 15 days" },
    { value: "1month", label: "1 Month", description: "Last 30 days" },
    { value: "all", label: "All Time", description: "All available data" }
  ];

  function handleFilterChange(filter: TimeFilter) {
    selectedFilter = filter;
    onFilterChange(filter);
  }
</script>

<div class="flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
  {#each filters as filter}
    <button
      class="px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 {
        selectedFilter === filter.value
          ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
          : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-600/50'
      }"
      on:click={() => handleFilterChange(filter.value)}
      title={filter.description}
    >
      {filter.label}
    </button>
  {/each}
</div>
