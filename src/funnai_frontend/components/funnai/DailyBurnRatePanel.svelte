<script lang="ts">
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { store } from "../../stores/store";
  import { tooltip } from "../../helpers/utils/tooltip";
  import VeryHighBurnRateModal from "./VeryHighBurnRateModal.svelte";

  // Props
  export let agent: any;
  export let agentCanisterActors: any[];
  export let agentCanistersInfo: any[];
  export let isHealthy: boolean = true; // Health status from health check service

  // Event dispatcher for communicating with parent
  const dispatch = createEventDispatcher();

  // Track which agents are having their burn rate updated
  let agentsBeingUpdated = new Set<string>();

  // Very High burn rate modal state
  let showVeryHighModal = false;

  // Timer state
  let canUpdate = true;
  let timeUntilNextUpdate = 0;
  let timerInterval: NodeJS.Timeout | null = null;
  let isCheckingBackend = false;

  // Format time remaining in human readable format
  function formatTimeRemaining(milliseconds: number): string {
    const hours = Math.floor(milliseconds / (1000 * 60 * 60));
    const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((milliseconds % (1000 * 60)) / 1000);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  }

  // Check if agent can be updated based on backend timing
  async function checkUpdateEligibility() {
    if (!agent?.id) return;
    
    // Check with backend first for accurate timing
    if (!isCheckingBackend) {
      isCheckingBackend = true;
      try {
        const actorIndex = findAgentIndexByAddress(agent.id);
        if (actorIndex >= 0) {
          const agentActor = agentCanisterActors[actorIndex];
          
          // Try to use the new timeToNextAgentSettingsUpdate function first
          if (agentActor && agentActor.timeToNextAgentSettingsUpdate) {
            try {
              const timeResponse = await agentActor.timeToNextAgentSettingsUpdate();
              
              // Handle the NatResult response format: Ok:bigint or Err:ApiError
              if ('Ok' in timeResponse) {
                const nanoseconds = timeResponse.Ok; // This is a bigint
                
                // Convert nanoseconds to milliseconds
                const timeInMs = Number(nanoseconds) / 1_000_000;
                
                if (timeInMs > 0) {
                  canUpdate = false;
                  timeUntilNextUpdate = timeInMs;
                  startTimer();
                  return;
                } else {
                  canUpdate = true;
                  timeUntilNextUpdate = 0;
                  return;
                }
              } else if ('Err' in timeResponse) {
                console.warn("Backend error checking update timing:", timeResponse.Err);
                // Fall through to use the original canAgentSettingsBeUpdated function
              }
            } catch (error) {
              console.error("Error calling timeToNextAgentSettingsUpdate:", error);
              // Fall through to legacy methods
            }
          }
          
          // Fallback to the original canAgentSettingsBeUpdated function
          if (agentActor && agentActor.canAgentSettingsBeUpdated) {
            const response = await agentActor.canAgentSettingsBeUpdated();
            if ('Ok' in response) {
              canUpdate = true;
              timeUntilNextUpdate = 0;
            } else {
              // Backend says we can't update yet, use local storage fallback
              const storageKey = `lastBurnRateUpdate_${agent.id}`;
              const lastUpdateTime = localStorage.getItem(storageKey);
              
              if (lastUpdateTime) {
                const timeSinceUpdate = Date.now() - parseInt(lastUpdateTime);
                const twentyFourHours = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
                
                if (timeSinceUpdate < twentyFourHours) {
                  canUpdate = false;
                  timeUntilNextUpdate = twentyFourHours - timeSinceUpdate;
                  startTimer();
                } else {
                  canUpdate = true;
                  timeUntilNextUpdate = 0;
                }
              } else {
                // If no local timestamp but backend says no, assume we just updated
                const now = Date.now();
                localStorage.setItem(storageKey, now.toString());
                canUpdate = false;
                timeUntilNextUpdate = 24 * 60 * 60 * 1000;
                startTimer();
              }
            }
          }
        }
      } catch (error) {
        console.warn("Could not check backend update eligibility:", error);
        // Fall back to local storage timing
        const storageKey = `lastBurnRateUpdate_${agent.id}`;
        const lastUpdateTime = localStorage.getItem(storageKey);
        
        if (lastUpdateTime) {
          const timeSinceUpdate = Date.now() - parseInt(lastUpdateTime);
          const twentyFourHours = 24 * 60 * 60 * 1000;
          
          if (timeSinceUpdate < twentyFourHours) {
            canUpdate = false;
            timeUntilNextUpdate = twentyFourHours - timeSinceUpdate;
            startTimer();
          } else {
            canUpdate = true;
            timeUntilNextUpdate = 0;
          }
        }
      } finally {
        isCheckingBackend = false;
      }
    }
  }

  // Start the countdown timer
  function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    
    timerInterval = setInterval(() => {
      timeUntilNextUpdate -= 1000;
      
      if (timeUntilNextUpdate <= 0) {
        canUpdate = true;
        timeUntilNextUpdate = 0;
        
        // Clear the timer
        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
        }
        
        // Optional: Verify with backend that we can now update
        // This ensures we're in sync with the server
        setTimeout(async () => {
          try {
            await checkUpdateEligibility();
          } catch (error) {
            console.warn("Could not verify update eligibility after timer expired:", error);
            // Even if backend check fails, keep buttons enabled if timer expired
            canUpdate = true;
          }
        }, 100);
      }
    }, 1000);
  }

  // Stop the timer
  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function findAgentIndexByAddress(canisterId: string) {
    return agentCanistersInfo.findIndex(canister => canister.address === canisterId);
  }

  // Helper function to extract only the original backend fields for API calls
  function getOriginalCanisterInfo(enrichedCanisterInfo: any) {
    // Extract only the fields that the backend expects
    const {
      // Remove UI-specific fields that we added
      uiStatus,
      cycleBalance,
      burnedCycles,
      cyclesBurnRate,
      cyclesBurnRateSetting,
      llmCanisters,
      llmSetupStatus,
      hasError,
      // Keep only original backend fields
      ...originalInfo
    } = enrichedCanisterInfo;
    
    return originalInfo;
  }

  /**
   * Updates the agent settings based on user-selected burn rate level.
   * 
   * @param {'Low' | 'Medium' | 'High' | 'VeryHigh'} level - The burn rate level selected by the user
   * @param {object} agent - The mAIner agent to update
  */
  async function updateAgentBurnRate(level: 'Low' | 'Medium' | 'High' | 'VeryHigh', agent: any) {
    if (!canUpdate) {
      console.warn("Cannot update burn rate - cooldown period active");
      return;
    }

    // Add this agent to the updating set
    agentsBeingUpdated.add(agent.id);
    agentsBeingUpdated = agentsBeingUpdated; // Trigger reactivity
    
    let actorIndex = findAgentIndexByAddress(agent.id);
    if (actorIndex < 0) {
      console.error(`updateAgentBurnRate actor not found for agent: ${agent}`);
      // Remove from updating set on error
      agentsBeingUpdated.delete(agent.id);
      agentsBeingUpdated = agentsBeingUpdated;
      return;
    }
    
    let agentActor = agentCanisterActors[actorIndex]; // Get actor for agent
    let burnRateSetting;
    switch (level) {
      case 'Low':
        burnRateSetting = { cyclesBurnRate: { Low: null } };
        break;
      case 'Medium':
        burnRateSetting = { cyclesBurnRate: { Mid: null } };
        break;
      case 'High':
        burnRateSetting = { cyclesBurnRate: { High: null } };
        break;
      case 'VeryHigh':
        burnRateSetting = { cyclesBurnRate: { VeryHigh: null } };
        break;
      default:
        console.error(`updateAgentBurnRate Unsupported level: ${level}`);
        // Remove from updating set on error
        agentsBeingUpdated.delete(agent.id);
        agentsBeingUpdated = agentsBeingUpdated;
        return;
    }

    try {
      await agentActor.updateAgentSettings(burnRateSetting);
      
      // Store the update time for fallback tracking
      const storageKey = `lastBurnRateUpdate_${agent.id}`;
      localStorage.setItem(storageKey, Date.now().toString());
      
      // Re-check eligibility to get accurate backend timing
      await checkUpdateEligibility();
      
      // Notify parent to refresh the agents list
      dispatch('burnRateUpdated');
    } catch (error) {
      console.error("Failed to update agent settings:", error);
    } finally {
      // Remove from updating set after processing
      agentsBeingUpdated.delete(agent.id);
      agentsBeingUpdated = agentsBeingUpdated; // Trigger reactivity
    }
  }

  // Initialize timer on mount
  onMount(async () => {
    await checkUpdateEligibility();
    if (!canUpdate && timeUntilNextUpdate > 0) {
      startTimer();
    }
  });

  // Clean up timer on destroy
  onDestroy(() => {
    stopTimer();
  });

  // Watch for agent changes and recheck eligibility
  $: if (agent?.id) {
    checkUpdateEligibility();
  }

  // Watch for canUpdate changes to ensure UI reactivity
  $: {
    canUpdate; timeUntilNextUpdate; // Trigger reactivity
  }

  // Handle Very High burn rate activation
  function handleVeryHighActivation() {
    showVeryHighModal = true;
  }

  // Handle modal close
  function handleVeryHighModalClose() {
    showVeryHighModal = false;
  }

  // Handle successful FUNNAI burn and activate Very High burn rate
  async function handleVeryHighSuccess(txId: string, canisterId: string, backendPromise: Promise<any>) {
    console.log('Very High burn rate activation initiated:', txId);
    
    // Add this agent to the updating set to show loading state
    agentsBeingUpdated.add(agent.id);
    agentsBeingUpdated = agentsBeingUpdated; // Trigger reactivity
    
    try {
      // Wait for the backend to process the updateAgentSettings call
      await backendPromise;
      
      // Store the update time for fallback tracking
      const storageKey = `lastBurnRateUpdate_${agent.id}`;
      localStorage.setItem(storageKey, Date.now().toString());
      
      // Re-check eligibility to get accurate backend timing
      await checkUpdateEligibility();
      
      // Update the local agent state to show VeryHigh immediately
      agent.cyclesBurnRateSetting = 'VeryHigh';
      // Trigger reactivity by reassigning the agent object
      agent = { ...agent };
      
      // Notify parent to refresh the agents list
      dispatch('burnRateUpdated');
      
      console.log('Very High burn rate successfully activated for agent:', canisterId);
    } catch (error) {
      console.error('Error activating Very High burn rate:', error);
      // You might want to show an error message to the user here
    } finally {
      // Remove from updating set after processing
      agentsBeingUpdated.delete(agent.id);
      agentsBeingUpdated = agentsBeingUpdated; // Trigger reactivity
    }
  }
</script>

<!-- Nested inside agent module — compact surface -->
<div class="rounded-xl bg-white/[0.03] p-3">
  <div class="flex items-center justify-between gap-2 mb-2.5">
    <div class="flex items-center gap-2 min-w-0">
      <h2 class="text-sm font-semibold tracking-tight text-white">Burn rate</h2>
      <span class="inline-flex items-center rounded-full bg-agent-purple/20 px-2 py-0.5 text-[10px] font-medium text-[#c4b5fd]">
        {agent.cyclesBurnRateSetting === 'VeryHigh' ? 'Very High' : agent.cyclesBurnRateSetting}
      </span>
    </div>
    {#if !canUpdate && timeUntilNextUpdate > 0 && agent.uiStatus === "active"}
      <span class="text-[11px] font-medium text-orange-300 tabular-nums shrink-0">
        {formatTimeRemaining(timeUntilNextUpdate)}
      </span>
    {/if}
  </div>

  {#if !isHealthy}
    <p class="mb-2 text-[11px] leading-snug text-amber-300/90">
      Settings disabled while this mAIner is stopped or in maintenance.
    </p>
  {/if}

  <div class="grid grid-cols-4 gap-1.5" role="group">
    <button
      type="button"
      class="relative rounded-lg border px-1 py-1.5 text-center transition-colors focus:z-10 focus:ring-2 focus:ring-agent-purple/40
      {agent.cyclesBurnRateSetting === 'Low'
        ? 'bg-agent-purple text-white border-agent-purple'
        : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-emerald-500/40 hover:bg-emerald-500/10'}"
      class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      on:click={() => updateAgentBurnRate('Low', agent)}
    >
      <span class="block text-[11px] font-semibold leading-tight">Low</span>
      <span class="block text-[10px] opacity-70 leading-tight">≈1T/d</span>
    </button>

    <button
      type="button"
      class="relative rounded-lg border px-1 py-1.5 text-center transition-colors focus:z-10 focus:ring-2 focus:ring-agent-purple/40
      {agent.cyclesBurnRateSetting === 'Medium'
        ? 'bg-agent-purple text-white border-agent-purple'
        : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-amber-500/40 hover:bg-amber-500/10'}"
      class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      on:click={() => updateAgentBurnRate('Medium', agent)}
    >
      <span class="block text-[11px] font-semibold leading-tight">Medium</span>
      <span class="block text-[10px] opacity-70 leading-tight">≈2T/d</span>
    </button>

    <button
      type="button"
      class="relative rounded-lg border px-1 py-1.5 text-center transition-colors focus:z-10 focus:ring-2 focus:ring-agent-purple/40
      {agent.cyclesBurnRateSetting === 'High'
        ? 'bg-agent-purple text-white border-agent-purple'
        : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-orange-500/40 hover:bg-orange-500/10'}"
      class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      on:click={() => updateAgentBurnRate('High', agent)}
    >
      <span class="block text-[11px] font-semibold leading-tight">High</span>
      <span class="block text-[10px] opacity-70 leading-tight">≈4T/d</span>
    </button>

    <button
      type="button"
      class="relative rounded-lg border px-1 py-1.5 text-center transition-colors focus:z-10 focus:ring-2 focus:ring-agent-purple/40
      {agent.cyclesBurnRateSetting === 'VeryHigh'
        ? 'bg-agent-purple text-white border-agent-purple'
        : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-red-500/40 hover:bg-red-500/10'}"
      class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
      on:click={() => {
        if (agent.cyclesBurnRateSetting === 'VeryHigh') return;
        handleVeryHighActivation();
      }}
    >
      <span class="block text-[11px] font-semibold leading-tight">V.High</span>
      <span class="block text-[10px] opacity-70 leading-tight">≈6T/d</span>
    </button>
  </div>

  {#if agentsBeingUpdated.has(agent.id)}
    <div class="mt-2 flex items-center gap-2 text-xs text-gray-400">
      <span class="w-3.5 h-3.5 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
      Updating…
    </div>
  {:else}
    <p class="mt-2 text-[11px] leading-snug text-gray-500">
      Higher burn rates speed up AI. Can be changed once every 24 hours.
    </p>
  {/if}
</div>

<!-- Very High Burn Rate Modal -->
<VeryHighBurnRateModal
  bind:isOpen={showVeryHighModal}
  onClose={handleVeryHighModalClose}
  onSuccess={handleVeryHighSuccess}
  canisterId={agent.id}
  canisterName={agent.name || ''}
/> 