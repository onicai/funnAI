<script lang="ts">
  import { onMount, onDestroy } from "svelte";

  export let cycles: number;
  export let label: string = "Burned Cycles";
  
  let cyclesCount = 0;
  let intervalId: NodeJS.Timer;
  
  function animateValue(start: number, end: number, duration: number) {
    const stepTime = 50;
    const steps = duration / stepTime;
    const increment = (end - start) / steps;
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        cyclesCount = end;
        clearInterval(timer);
      } else {
        cyclesCount = Math.round(current);
      }
    }, stepTime);
  }

  onMount(async () => {
    animateValue(0, cycles, 1000);
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
  });

  $: formattedCycles = cyclesCount?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'");
</script>

<div class="agent-card p-4">
  <div class="flex flex-col gap-3">
    <div class="flex items-center space-x-3">
      <div class="flex-shrink-0 w-10 h-10 rounded-xl border border-white/5 bg-white/[0.05] flex items-center justify-center">
        <svg class="w-5 h-5 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 1-4 4-4 2.207 0 4 1.793 4 4 0 .211-.031.418-.075.618C18.003 10.755 19 11.823 19 13c0 1.657-1.343 3-3 3v-2c0-1.105.895-2 2-2s2 .895 2 2-1.343 2-3 2H8a3 3 0 01-3-3c0-1.657 1.343-3 3-3v-1c-2.209 0-4 1.791-4 4 0 2.209 1.791 4 4 4h8c2.209 0 4-1.791 4-4 0-2.209-1.791-4-4-4z" />
        </svg>
      </div>
      
      <div class="flex flex-col">
        <p class="agent-eyebrow">Metric</p>
        <span class="text-sm font-semibold text-white">{label}</span>
      </div>
    </div>
    
    <div class="flex flex-col items-start">
      <div class="flex items-baseline space-x-1">
        <span class="text-lg sm:text-xl md:text-2xl font-bold text-white font-mono tabular-nums">
          {formattedCycles}
        </span>
        <span class="hidden sm:inline text-xs text-gray-500 font-medium">cycles</span>
      </div>
      
      <div class="flex items-center space-x-1 mt-1">
        <div class="w-2 h-2 bg-emerald-400/80 rounded-full animate-pulse"></div>
        <span class="text-xs text-gray-500">Active</span>
      </div>
    </div>
  </div>
</div>
