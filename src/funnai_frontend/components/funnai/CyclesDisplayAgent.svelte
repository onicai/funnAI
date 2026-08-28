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

<div class="rounded-xl bg-white/3 px-3 py-2.5">
  <div class="flex items-center justify-between gap-3">
    <span class="text-sm font-semibold text-white">{label}</span>
    <div class="flex items-baseline gap-1.5 min-w-0">
      <span class="text-sm font-semibold text-white font-mono tabular-nums truncate">
        {formattedCycles}
      </span>
      <span class="text-[10px] text-gray-500 shrink-0">cycles</span>
    </div>
  </div>
</div>
