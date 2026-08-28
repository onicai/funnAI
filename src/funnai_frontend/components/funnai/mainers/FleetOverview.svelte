<script lang="ts">
  export let totalMainers: number;
  export let activeMainers: number;
  export let inactiveMainers: number;
  export let lowBurnRateMainers: number;
  export let mediumBurnRateMainers: number;
  export let highBurnRateMainers: number;
  export let veryHighBurnRateMainers: number;

  let isOpen = false;

  function toggleAccordion() {
    isOpen = !isOpen;
  }

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

<div class="relative overflow-hidden rounded-2xl border border-white/8 bg-agent-surface font-sans">
  <button
    type="button"
    on:click={toggleAccordion}
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/2"
    aria-expanded={isOpen}
  >
    <div class="relative flex items-center justify-between gap-3 px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2 mb-1">
          <p class="agent-eyebrow">Fleet</p>
          {#if activeMainers > 0}
            <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-400">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {activeMainers} mining
            </span>
          {/if}
          {#if inactiveMainers > 0}
            <span class="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-400">
              <span class="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
              {inactiveMainers} need attention
            </span>
          {/if}
        </div>
        <h2 class="text-base sm:text-lg font-semibold tracking-tight text-white">Fleet overview</h2>
        <p class="mt-0.5 text-sm font-normal text-gray-400">
          {totalMainers} mAIner{totalMainers === 1 ? '' : 's'} in your fleet
        </p>
      </div>

      <div class="shrink-0">
        <div
          class="w-9 h-9 rounded-xl border border-white/10 bg-white/4 flex items-center justify-center transition-transform duration-300"
          style="transform: rotate({isOpen ? 180 : 0}deg)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>

  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/6 p-5 sm:p-6">
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-5">
        <div class="rounded-xl bg-white/3 p-3.5">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Active</p>
          <p class="mt-2 text-2xl font-semibold tracking-tight text-white tabular-nums">{activeMainers}</p>
          <p class="mt-1 text-xs font-normal text-emerald-400/80">Mining</p>
        </div>

        <div class="rounded-xl bg-white/3 p-3.5">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Inactive</p>
          <p class="mt-2 text-2xl font-semibold tracking-tight text-white tabular-nums">{inactiveMainers}</p>
          <p class="mt-1 text-xs font-normal text-gray-500">Stopped / low cycles</p>
        </div>

        <div class="rounded-xl bg-white/3 p-3.5 col-span-2 sm:col-span-1">
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

      <div class="pt-4 border-t border-white/6">
        <div class="flex items-center justify-between mb-3">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-agent-purple">Cycle burn rate</p>
          <p class="text-[11px] font-normal text-gray-500">Distribution</p>
        </div>

        <div class="flex h-1.5 w-full overflow-hidden rounded-full bg-white/6 mb-4">
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

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-x-3 gap-y-2">
          {#each burnRates as rate}
            <div class="px-0.5 py-1">
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
</div>

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.35s ease;
  }

  .accordion-content.accordion-open {
    max-height: 1200px;
  }
</style>
