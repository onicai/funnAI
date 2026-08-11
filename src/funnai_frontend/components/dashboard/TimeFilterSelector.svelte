<script lang="ts">
  import type { TimeFilter } from '../../helpers/DailyMetricsService';

  export let selectedFilter: TimeFilter = "1month";
  export let onFilterChange: (filter: TimeFilter) => void = () => {};

  const filters: { value: TimeFilter; label: string; description: string }[] = [
    { value: "7days", label: "7 Days", description: "Last 7 days" },
    { value: "15days", label: "15 Days", description: "Last 15 days" },
    { value: "1month", label: "1 Month", description: "Last 30 days" },
    { value: "all", label: "All Time", description: "All available data" }
  ];

  function handleFilterChange(filter: TimeFilter) {
    selectedFilter = filter;
    onFilterChange(filter);
  }
</script>

<div class="agent-tab-track">
  {#each filters as filter}
    <button
      class="agent-tab {selectedFilter === filter.value ? 'agent-tab-active' : ''}"
      on:click={() => handleFilterChange(filter.value)}
      title={filter.description}
    >
      {filter.label}
    </button>
  {/each}
</div>
