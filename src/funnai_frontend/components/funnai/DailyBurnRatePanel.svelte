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

<!-- Nested inside agent module — surface only, no second outline -->
<div class="rounded-xl bg-white/[0.03]">
  <div class="p-4 sm:p-5">
    <!-- Header Section -->
    <div class="flex flex-col space-y-3 mb-4">
      <div class="flex items-center space-x-3">
        <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-white/[0.05] flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-agent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        
        <div class="flex flex-col">
          <p class="agent-eyebrow">Performance</p>
          <h2 class="text-sm sm:text-base font-semibold tracking-tight text-white">Daily Burn Rate</h2>
          <p class="text-xs text-gray-500">Control your mAIner's computational intensity</p>
        </div>
      </div>
      
      <!-- Current Setting Display -->
      <div class="rounded-xl bg-agent-bg/40 p-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-agent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span class="text-sm font-medium text-gray-200">Current Setting</span>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-agent-purple text-white">
            {agent.cyclesBurnRateSetting}
          </span>
        </div>
      </div>

      <!-- Cooldown Timer Display -->
      {#if !canUpdate && timeUntilNextUpdate > 0 && agent.uiStatus === "active"}
        <div class="rounded-xl border border-orange-500/30 bg-orange-500/10 p-3">
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-sm font-medium text-orange-300">Countdown active</h3>
              <p class="text-xs text-orange-300/80 mt-1">
                You can change the burn rate again in: 
                <span class="font-mono font-bold text-orange-200">
                  {formatTimeRemaining(timeUntilNextUpdate)}
                </span>
              </p>
            </div>
          </div>
        </div>
      {/if}
    </div>

    <!-- Burn Rate Selection -->
    <div class="space-y-3">
      <div class="flex items-center space-x-2 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-agent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
        </svg>
        <span class="text-sm font-medium text-gray-200">Select Performance Level</span>
      </div>

      <!-- Health Status Warning -->
      {#if !isHealthy}
        <div class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 mb-2">
          <div class="flex items-start space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm font-medium text-amber-300">Settings temporarily disabled</p>
              <p class="text-xs text-amber-300/80 mt-1">Performance settings cannot be changed while the mAIner is stopped or in maintenance mode.</p>
            </div>
          </div>
        </div>
      {/if}

      <!-- Enhanced Button Group -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3" role="group">
        <!-- Low Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 border focus:z-10 focus:ring-2 focus:ring-agent-purple/40
          {agent.cyclesBurnRateSetting === 'Low' 
            ? 'bg-agent-purple text-white border-agent-purple' 
            : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-emerald-500/40 hover:bg-emerald-500/10'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          on:click={() => updateAgentBurnRate('Low', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 {agent.cyclesBurnRateSetting === 'Low' ? 'text-white' : 'text-emerald-400/80'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>Low</span>
            <span class="text-xs opacity-75 hidden sm:block">Eco mode</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'Low'}
            <div class="absolute top-1.5 right-1.5 w-2 h-2 bg-white/80 rounded-full"></div>
          {/if}
        </button>
        
        <!-- Medium Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 border focus:z-10 focus:ring-2 focus:ring-agent-purple/40
          {agent.cyclesBurnRateSetting === 'Medium' 
            ? 'bg-agent-purple text-white border-agent-purple' 
            : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-amber-500/40 hover:bg-amber-500/10'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          on:click={() => updateAgentBurnRate('Medium', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 {agent.cyclesBurnRateSetting === 'Medium' ? 'text-white' : 'text-amber-400/80'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <span>Medium</span>
            <span class="text-xs opacity-75 hidden sm:block">Balanced</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'Medium'}
            <div class="absolute top-1.5 right-1.5 w-2 h-2 bg-white/80 rounded-full"></div>
          {/if}
        </button>
        
        <!-- High Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 border focus:z-10 focus:ring-2 focus:ring-agent-purple/40
          {agent.cyclesBurnRateSetting === 'High' 
            ? 'bg-agent-purple text-white border-agent-purple' 
            : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-orange-500/40 hover:bg-orange-500/10'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          on:click={() => updateAgentBurnRate('High', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 {agent.cyclesBurnRateSetting === 'High' ? 'text-white' : 'text-orange-400/80'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.251.757l2.551 7.843h8.244a.75.75 0 01.441 1.356l-6.673 4.845 2.551 7.844a.75.75 0 01-1.154.956L12 18.756l-6.211 4.845a.75.75 0 01-1.154-.956l2.551-7.844L.513 9.956A.75.75 0 01.954 8.6h8.244L11.749.757a.75.75 0 01.502 0z"/>
            </svg>
            <span>High</span>
            <span class="text-xs opacity-75 hidden sm:block">Power mode</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'High'}
            <div class="absolute top-1.5 right-1.5 w-2 h-2 bg-white/80 rounded-full"></div>
          {/if}
        </button>
        
        <!-- Very High Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-semibold rounded-xl transition-all duration-200 border focus:z-10 focus:ring-2 focus:ring-agent-purple/40
          {agent.cyclesBurnRateSetting === 'VeryHigh' 
            ? 'bg-agent-purple text-white border-agent-purple' 
            : 'border-white/10 bg-white/[0.03] text-gray-300 hover:border-red-500/40 hover:bg-red-500/10'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate || !isHealthy}
          on:click={() => {
            if (agent.cyclesBurnRateSetting === 'VeryHigh') {
              // Already at Very High, no action needed
              return;
            }
            // Show modal to burn FUNNAI first
            handleVeryHighActivation();
          }}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5 {agent.cyclesBurnRateSetting === 'VeryHigh' ? 'text-white' : 'text-red-400/80'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2l1.09 3.26L16 6l-2.91 1.09L12 10l-1.09-3.26L8 6l2.91-1.09L12 2zM7 12l1.09 3.26L11 16l-2.91 1.09L7 20l-1.09-3.26L3 16l2.91-1.09L7 12zM17 12l1.09 3.26L21 16l-2.91 1.09L17 20l-1.09-3.26L13 16l2.91-1.09L17 12z"/>
            </svg>
            <span>Very High</span>
            <span class="text-xs opacity-75 hidden sm:block">Premium</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'VeryHigh'}
            <div class="absolute top-1.5 right-1.5 w-2 h-2 bg-white/80 rounded-full"></div>
          {:else}
            <div class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full border border-red-400/50 bg-red-500/40"></div>
          {/if}
        </button>
      </div>

      <!-- Update Status -->
      {#if agentsBeingUpdated.has(agent.id)}
        <div class="rounded-xl border border-agent-purple/30 bg-agent-purple/10 p-3 mt-3">
          <div class="flex items-center justify-center space-x-3">
            <span class="w-5 h-5 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
            <div class="flex flex-col md:flex-row md:items-center md:space-x-2">
              <span class="text-sm font-medium text-gray-200">Updating burn rate...</span>
              <span class="text-xs text-gray-500">Changes will take effect immediately</span>
            </div>
          </div>
        </div>
      {:else}
        <!-- Info Footer -->
        <div class="rounded-xl bg-agent-bg/40 p-3">
          <div class="flex items-start space-x-2 text-xs text-gray-400">
            <div class="space-y-2 w-full">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 text-xs">
                <span class="flex items-start gap-1.5"><span class="mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400/70 shrink-0"></span><span><strong class="text-gray-300">Low:</strong><br/> ≈1T cycles/day</span></span>
                <span class="flex items-start gap-1.5"><span class="mt-1 w-1.5 h-1.5 rounded-full bg-amber-400/70 shrink-0"></span><span><strong class="text-gray-300">Medium:</strong><br/> ≈2T cycles/day</span></span>
                <span class="flex items-start gap-1.5"><span class="mt-1 w-1.5 h-1.5 rounded-full bg-orange-400/70 shrink-0"></span><span><strong class="text-gray-300">High:</strong><br/> ≈4T cycles/day</span></span>
                <span class="flex items-start gap-1.5"><span class="mt-1 w-1.5 h-1.5 rounded-full bg-red-400/70 shrink-0"></span><span><strong class="text-gray-300">Very High:</strong><br/> ≈6T cycles/day</span></span>
              </div>
              <div class="border-t border-white/[0.08] pt-2 mt-2 space-y-1">
                <p><span class="font-medium text-gray-300">Tip:</span> Higher burn rates speed up AI but use more cycles.</p>
                <p><span class="font-medium text-gray-300">Important:</span> Burn rate can only be updated once every 24 hours.</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<!-- Very High Burn Rate Modal -->
<VeryHighBurnRateModal
  bind:isOpen={showVeryHighModal}
  onClose={handleVeryHighModalClose}
  onSuccess={handleVeryHighSuccess}
  canisterId={agent.id}
  canisterName={agent.name || ''}
/> 