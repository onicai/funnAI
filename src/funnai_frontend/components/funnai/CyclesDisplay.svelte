<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";

  export let cycles: number;
  export let label: string = "Burned Cycles";
  export let showAllEvents: boolean = true;
  
  let cyclesCount = 0;
  let intervalId: NodeJS.Timer;
  let currentCycles = 0;
  
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  
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

  async function getProtocolCycles(): Promise<number> {
    try {
      let protocolTotalCyclesBurntResult = await $store.gameStateCanisterActor.getProtocolTotalCyclesBurnt();
      if ("Ok" in protocolTotalCyclesBurntResult) {
        return Number(protocolTotalCyclesBurntResult.Ok);
      }
    } catch (error) {
      console.error("Error fetching protocol cycles:", error);
    }
    return cycles; // fallback to provided cycles
  }

  function getUserMainersCycles(): number {
    if (!$store.isAuthed || !agentCanistersInfo || agentCanistersInfo.length === 0) {
      return 0;
    }
    return agentCanistersInfo.reduce((total, agent) => total + (agent.burnedCycles || 0), 0);
  }

  async function updateCycles() {
    let newCycles: number;
    
    if (showAllEvents) {
      newCycles = await getProtocolCycles();
      label = "Protocol burned cycles";
    } else {
      // Refresh the mAIner canister info to get the latest burned cycles
      await store.loadUserMainerCanisters();
      newCycles = getUserMainersCycles();
      label = "My mAIners burned cycles";
    }
    
    if (newCycles !== currentCycles) {
      animateValue(cyclesCount, newCycles, 1000);
      currentCycles = newCycles;
    }
  }

  onMount(async () => {
    await updateCycles();
    
    // Set up interval to update cycles every 60 seconds
    intervalId = setInterval(async () => {
      await updateCycles();
    }, 6000);
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
  });

  // Update when showAllEvents changes
  $: if (showAllEvents !== undefined) {
    updateCycles();
  }

  // Note: agentCanistersInfo is now refreshed explicitly in updateCycles() when needed

  $: formattedCycles = cyclesCount?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'");
</script>

<div class="relative overflow-hidden bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-4 transition-all duration-300 hover:shadow-xl">
  <!-- Background pattern -->
  <div class="absolute inset-0 bg-gradient-to-br from-orange-50/50 to-red-50/30 dark:from-orange-900/10 dark:to-red-900/5"></div>
  
  <!-- Content -->
  <div class="relative z-10 flex flex-col gap-3">
    <!-- Icon and Label -->
    <div class="flex items-center space-x-3">
      <!-- Fire/Burn Icon -->
      <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center shadow-md">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 1-4 4-4 2.207 0 4 1.793 4 4 0 .211-.031.418-.075.618C18.003 10.755 19 11.823 19 13c0 1.657-1.343 3-3 3v-2c0-1.105.895-2 2-2s2 .895 2 2s-1.343 2-3 2H8a3 3 0 01-3-3c0-1.657 1.343-3 3-3v-1c-2.209 0-4 1.791-4 4 0 2.209 1.791 4 4 4h8c2.209 0 4-1.791 4-4 0-2.209-1.791-4-4-4z" />
        </svg>
      </div>
      
      <!-- Label -->
      <div class="flex flex-col">
        <span class="text-gray-600 dark:text-gray-400 text-xs font-medium uppercase tracking-wide">Metric</span>
        <span class="text-gray-800 dark:text-gray-200 text-sm font-semibold">{label}</span>
      </div>
    </div>
    
    <!-- Value Section -->
    <div class="flex flex-col items-start">
      <div class="flex items-baseline space-x-1">
        <span class="text-lg sm:text-xl md:text-2xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent font-mono tabular-nums">
          {formattedCycles}
        </span>
        <span class="hidden sm:inline text-xs text-gray-500 dark:text-gray-400 font-medium">cycles</span>
      </div>
      
      <!-- Optional trend indicator -->
      <div class="flex items-center space-x-1 mt-1">
        <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        <span class="text-xs text-gray-500 dark:text-gray-400">Active</span>
      </div>
    </div>
  </div>
  
  <!-- Bottom accent bar -->
  <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-500 to-red-500"></div>
</div> 