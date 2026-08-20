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
    return cycles;
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
    
    intervalId = setInterval(async () => {
      await updateCycles();
    }, 6000);
  });

  onDestroy(() => {
    if (intervalId) clearInterval(intervalId);
  });

  $: if (showAllEvents !== undefined) {
    updateCycles();
  }

  $: formattedCycles = cyclesCount?.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "'");
</script>

<div class="relative overflow-hidden rounded-2xl border border-white/8 bg-agent-surface p-5 font-sans">
  <div class="pointer-events-none absolute inset-0">
    <div class="absolute -top-16 right-0 h-32 w-40 rounded-full bg-agent-purple/15 blur-3xl"></div>
  </div>

  <div class="relative z-10 flex flex-col gap-4">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="agent-eyebrow">Metric</p>
        <p class="mt-1 text-sm font-medium text-gray-200 min-h-5">{label}</p>
      </div>
      <div class="flex items-center gap-1.5 rounded-full border border-white/10 bg-white/3 px-2.5 py-1">
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-[11px] font-normal text-gray-400">Active</span>
      </div>
    </div>
    
    <div class="flex items-baseline gap-2">
      <span class="text-2xl sm:text-3xl font-semibold tracking-tight text-white font-mono tabular-nums">
        {formattedCycles}
      </span>
      <span class="text-xs font-normal text-gray-500">cycles</span>
    </div>
  </div>
</div>
