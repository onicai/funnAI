<script lang="ts">
  import { store } from "../store";
  import Footer from "../components/Footer.svelte";
  import MainerAccordion from "../components/MainerAccordion.svelte";
  import MainerFeed from "../components/MainerFeed.svelte";
  import { onMount } from "svelte";

  let cyclesCount = 0;
  const targetCycles = 6541540;
  
  function animateValue(start: number, end: number, duration: number) {
    const stepTime = 50; // Less frequent updates
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

  onMount(() => {
    animateValue(0, targetCycles, 1000); // Faster duration (1 second)
  });

  $: formattedCycles = cyclesCount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'");
</script>

<div class="container mx-auto px-8 py-8">
  <h1 class="text-2xl text-gray-400 font-bold mb-6">My mAIners</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
    <div class="card-style p-6 rounded-lg shadow mb-2">
      <MainerAccordion />
    </div>
    <div class="card-style p-4 rounded-lg shadow mb-2">
      <div class="flex items-center justify-between p-4 m-2 bg-gradient-to-r from-orange-100 to-orange-50 rounded-lg shadow-sm border border-orange-200">
        <span class="text-orange-600 font-semibold">Burned Cycles</span>
        <span class="text-xl font-bold text-orange-500 font-mono w-[8ch] text-right">{formattedCycles}</span>
      </div>
      <MainerFeed />
    </div>
  </div>
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 