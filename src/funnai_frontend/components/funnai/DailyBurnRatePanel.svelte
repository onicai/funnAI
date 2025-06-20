<script lang="ts">
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { store } from "../../stores/store";
  import { tooltip } from "../../helpers/utils/tooltip";

  // Props
  export let agent: any;
  export let agentCanisterActors: any[];
  export let agentCanistersInfo: any[];

  // Event dispatcher for communicating with parent
  const dispatch = createEventDispatcher();

  // Track which agents are having their burn rate updated
  let agentsBeingUpdated = new Set<string>();

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
   * @param {'Low' | 'Medium' | 'High'} level - The burn rate level selected by the user
   * @param {object} agent - The mAIner agent to update
  */
  async function updateAgentBurnRate(level: 'Low' | 'Medium' | 'High', agent: any) {
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
</script>

<!-- Enhanced Daily Burn Rate Panel -->
<div class="relative overflow-hidden bg-gradient-to-br from-purple-50 via-indigo-50 to-violet-50 dark:from-purple-900/20 dark:via-indigo-900/20 dark:to-violet-900/20 border border-purple-200/60 dark:border-purple-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
  <!-- Background decorative elements -->
  <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-200/30 to-indigo-200/30 dark:from-purple-600/10 dark:to-indigo-600/10 rounded-full -translate-y-10 translate-x-10"></div>
  <div class="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-violet-200/30 to-purple-200/30 dark:from-violet-600/10 dark:to-purple-600/10 rounded-full translate-y-8 -translate-x-8"></div>
  
  <div class="relative p-4 sm:p-5">
    <!-- Header Section -->
    <div class="flex flex-col space-y-3 mb-4">
      <div class="flex items-center space-x-3">
        <!-- Icon with gradient background -->
        <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 dark:from-purple-600 dark:to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        
        <!-- Title and subtitle -->
        <div class="flex flex-col">
          <h2 class="text-sm sm:text-base font-bold text-purple-900 dark:text-purple-100">Daily Burn Rate</h2>
          <p class="text-xs text-purple-700 dark:text-purple-300">Control your mAIner's computational intensity</p>
        </div>
      </div>
      
      <!-- Current Setting Display -->
      <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-3 border border-purple-200/40 dark:border-purple-700/40 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span class="text-sm font-medium text-purple-900 dark:text-purple-100">Current Setting</span>
          </div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-sm">
            {agent.cyclesBurnRateSetting}
          </span>
        </div>
      </div>

      <!-- Cooldown Timer Display -->
      {#if !canUpdate && timeUntilNextUpdate > 0 && agent.status === "active"}
        <div class="bg-orange-50 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-700 rounded-lg p-3">
          <div class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-sm font-medium text-orange-800 dark:text-orange-200">Cooldown Active</h3>
              <p class="text-xs text-orange-700 dark:text-orange-300 mt-1">
                You can change the burn rate again in: 
                <span class="font-mono font-bold text-orange-800 dark:text-orange-200">
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
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
        </svg>
        <span class="text-sm font-medium text-purple-900 dark:text-purple-100">Select Performance Level</span>
      </div>

      <!-- Enhanced Button Group -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3" role="group">
        <!-- Low Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-bold rounded-lg sm:rounded-xl transition-all duration-300 transform border-2 focus:z-10 focus:ring-2 focus:ring-purple-500
          {agent.cyclesBurnRateSetting === 'Low' 
            ? 'bg-gradient-to-r from-green-500 to-emerald-600 dark:from-green-600 dark:to-emerald-700 text-white border-green-400 shadow-lg scale-105' 
            : 'bg-white/70 dark:bg-gray-800/70 text-purple-900 dark:text-purple-200 border-purple-200 dark:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 hover:border-purple-300 dark:hover:border-purple-500 hover:scale-102'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:transform-none={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:hover:scale-100={agentsBeingUpdated.has(agent.id) || !canUpdate}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate}
          on:click={() => updateAgentBurnRate('Low', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <span>Low</span>
            <span class="text-xs opacity-75 hidden sm:block">Eco mode</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'Low'}
            <div class="absolute top-1 right-1 w-2 h-2 bg-white rounded-full shadow-sm"></div>
          {/if}
        </button>
        
        <!-- Medium Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-bold rounded-lg sm:rounded-xl transition-all duration-300 transform border-2 focus:z-10 focus:ring-2 focus:ring-purple-500
          {agent.cyclesBurnRateSetting === 'Medium' 
            ? 'bg-gradient-to-r from-yellow-500 to-orange-600 dark:from-yellow-600 dark:to-orange-700 text-white border-yellow-400 shadow-lg scale-105' 
            : 'bg-white/70 dark:bg-gray-800/70 text-purple-900 dark:text-purple-200 border-purple-200 dark:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 hover:border-purple-300 dark:hover:border-purple-500 hover:scale-102'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:transform-none={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:hover:scale-100={agentsBeingUpdated.has(agent.id) || !canUpdate}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate}
          on:click={() => updateAgentBurnRate('Medium', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            <span>Medium</span>
            <span class="text-xs opacity-75 hidden sm:block">Balanced</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'Medium'}
            <div class="absolute top-1 right-1 w-2 h-2 bg-white rounded-full shadow-sm"></div>
          {/if}
        </button>
        
        <!-- High Button -->
        <button 
          type="button" 
          class="group relative px-2 sm:px-3 md:px-4 py-2 sm:py-3 md:py-4 text-xs sm:text-sm font-bold rounded-lg sm:rounded-xl transition-all duration-300 transform border-2 focus:z-10 focus:ring-2 focus:ring-purple-500
          {agent.cyclesBurnRateSetting === 'High' 
            ? 'bg-gradient-to-r from-red-500 to-pink-600 dark:from-red-600 dark:to-pink-700 text-white border-red-400 shadow-lg scale-105' 
            : 'bg-white/70 dark:bg-gray-800/70 text-purple-900 dark:text-purple-200 border-purple-200 dark:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 hover:border-purple-300 dark:hover:border-purple-500 hover:scale-102'}"
          class:opacity-50={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:cursor-not-allowed={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:transform-none={agentsBeingUpdated.has(agent.id) || !canUpdate}
          class:hover:scale-100={agentsBeingUpdated.has(agent.id) || !canUpdate}
          disabled={agentsBeingUpdated.has(agent.id) || !canUpdate}
          on:click={() => updateAgentBurnRate('High', agent)}
        >
          <div class="flex flex-col items-center space-y-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 sm:w-5 sm:h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12.251.757l2.551 7.843h8.244a.75.75 0 01.441 1.356l-6.673 4.845 2.551 7.844a.75.75 0 01-1.154.956L12 18.756l-6.211 4.845a.75.75 0 01-1.154-.956l2.551-7.844L.513 9.956A.75.75 0 01.954 8.6h8.244L11.749.757a.75.75 0 01.502 0z"/>
            </svg>
            <span>High</span>
            <span class="text-xs opacity-75 hidden sm:block">Max power</span>
          </div>
          {#if agent.cyclesBurnRateSetting === 'High'}
            <div class="absolute top-1 right-1 w-2 h-2 bg-white rounded-full shadow-sm"></div>
          {/if}
        </button>
      </div>

      <!-- Update Status -->
      {#if agentsBeingUpdated.has(agent.id)}
        <div class="bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 rounded-lg p-3 mt-3">
          <div class="flex items-center justify-center space-x-3">
            <span class="w-5 h-5 border-2 border-purple-400/30 border-t-purple-600 rounded-full animate-spin"></span>
            <div class="flex flex-col md:flex-row md:items-center md:space-x-2">
              <span class="text-sm font-medium text-purple-700 dark:text-purple-300">Updating burn rate...</span>
              <span class="text-xs text-purple-600 dark:text-purple-400 opacity-75">Changes will take effect immediately</span>
            </div>
          </div>
        </div>
      {:else}
        <!-- Info Footer -->
        <div class="bg-white/40 dark:bg-gray-800/40 backdrop-blur-sm rounded-lg p-3 border border-purple-200/30 dark:border-purple-700/30">
          <div class="flex items-start space-x-2 text-xs text-purple-700 dark:text-purple-300">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <div class="space-y-2">
              <p><span class="font-medium">💡 Tip:</span> Higher burn rates provide faster AI responses but consume more cycles.</p>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-1 text-xs opacity-75">
                <span>🟢 <strong>Low:</strong> ~1-2T cycles/day</span>
                <span>🟡 <strong>Medium:</strong> ~3-5T cycles/day</span>
                <span>🔴 <strong>High:</strong> ~6-10T cycles/day</span>
              </div>
              <div class="border-t border-purple-200/30 dark:border-purple-700/30 pt-2 mt-2">
                <p><span class="font-medium">⏰ Important:</span> Burn rate can only be updated once every 24 hours to prevent abuse.</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Bottom accent line -->
  <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-400 dark:via-purple-500 to-transparent"></div>
</div> 