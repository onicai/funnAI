<script lang="ts">
  export let totalMainers: number;
  export let activeMainers: number;
  export let inactiveMainers: number;
  export let lowBurnRateMainers: number;
  export let mediumBurnRateMainers: number;
  export let highBurnRateMainers: number;
  export let veryHighBurnRateMainers: number;

  $: burnRates = [
    { label: 'Low', hint: 'Conservative', value: lowBurnRateMainers, tone: 'text-emerald-400', bar: 'bg-emerald-400' },
    { label: 'Medium', hint: 'Balanced', value: mediumBurnRateMainers, tone: 'text-amber-400', bar: 'bg-amber-400' },
    { label: 'High', hint: 'Performance', value: highBurnRateMainers, tone: 'text-orange-400', bar: 'bg-orange-400' },
    { label: 'Very high', hint: 'Maximum', value: veryHighBurnRateMainers, tone: 'text-agent-purple', bar: 'bg-agent-purple' },
  ];

  $: burnTotal = Math.max(
    lowBurnRateMainers + mediumBurnRateMainers + highBurnRateMainers + veryHighBurnRateMainers,
    1
  );
</script>

<div class="mt-2 mb-4 agent-card font-sans">
  <div class="agent-glow"></div>

  <div class="relative p-5 sm:p-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-5">
      <div>
        <p class="agent-eyebrow">Fleet</p>
        <h2 class="mt-1 text-lg font-semibold tracking-tight text-white">Flock overview</h2>
        <p class="mt-1 text-sm font-normal text-gray-400">
          {totalMainers} mAIner{totalMainers === 1 ? '' : 's'} in your flock
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        {#if activeMainers > 0}
          <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            {activeMainers} mining
          </span>
        {/if}
        {#if inactiveMainers > 0}
          <span class="inline-flex items-center gap-1.5 rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-[11px] font-medium text-amber-400">
            <span class="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
            {inactiveMainers} need attention
          </span>
        {:else}
          <span class="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-1 text-[11px] font-medium text-gray-400">
            All systems operational
          </span>
        {/if}
      </div>
    </div>

    <!-- Status metrics -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-5">
      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3.5">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Active</p>
        <p class="mt-2 text-2xl font-semibold tracking-tight text-white tabular-nums">{activeMainers}</p>
        <p class="mt-1 text-xs font-normal text-emerald-400/80">Mining</p>
      </div>

      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3.5">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Inactive</p>
        <p class="mt-2 text-2xl font-semibold tracking-tight text-white tabular-nums">{inactiveMainers}</p>
        <p class="mt-1 text-xs font-normal text-gray-500">Stopped / low cycles</p>
      </div>

      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 col-span-2 sm:col-span-1">
        {#if inactiveMainers > 0}
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-amber-400/80">Attention</p>
          <p class="mt-2 text-2xl font-semibold tracking-tight text-amber-400 tabular-nums">{inactiveMainers}</p>
          <p class="mt-1 text-xs font-normal text-gray-500">
            Need{inactiveMainers === 1 ? 's' : ''} top-up
          </p>
        {:else}
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Health</p>
          <p class="mt-2 text-2xl font-semibold tracking-tight text-emerald-400">OK</p>
          <p class="mt-1 text-xs font-normal text-gray-500">No action required</p>
        {/if}
      </div>
    </div>

    <!-- Burn rate distribution -->
    <div class="rounded-xl border border-white/10 bg-white/[0.02] p-4">
      <div class="flex items-center justify-between mb-3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-agent-purple">Cycle burn rate</p>
        <p class="text-[11px] font-normal text-gray-500">Distribution</p>
      </div>

      <div class="flex h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06] mb-4">
        {#each burnRates as rate}
          {#if rate.value > 0}
            <div
              class="{rate.bar} h-full first:rounded-l-full last:rounded-r-full"
              style="width: {(rate.value / burnTotal) * 100}%"
              title="{rate.label}: {rate.value}"
            ></div>
          {/if}
        {/each}
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {#each burnRates as rate}
          <div class="rounded-lg border border-white/[0.06] bg-agent-surface/60 px-3 py-2.5">
            <div class="flex items-center justify-between gap-2">
              <span class="text-[11px] font-medium text-gray-400">{rate.label}</span>
              <span class="text-sm font-semibold tabular-nums {rate.tone}">{rate.value}</span>
            </div>
            <p class="mt-0.5 text-[10px] font-normal text-gray-600">{rate.hint}</p>
          </div>
        {/each}
      </div>
    </div>
  </div>
</div>
