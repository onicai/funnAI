<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../store";

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

<div class="flex items-center p-4 bg-gradient-to-r from-orange-100 to-orange-50 rounded-lg shadow-sm border border-orange-200">
  <span class="text-orange-600 font-semibold">{label}</span>
  <span class="ml-4 text-xl font-bold text-orange-500 font-mono w-[8ch] text-right">{formattedCycles}</span>
</div> 