<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import CyclesDisplayAgent from './CyclesDisplayAgent.svelte';
  import { store } from "../../stores/store";
  import LoginModal from '../login/LoginModal.svelte';
  import MainerPaymentModal from './MainerPaymentModal.svelte';
  import MainerTopUpModal from './MainerTopUpModal.svelte';
  import { Principal } from '@dfinity/principal';
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = $store.isAuthed;

  let agents = [
    // Add the agent entries dynamically via the calls in onMount
    // TODO: remove these dummy entries
    /* { id: 1, name: "mAIner 1", status: "active", burnedCycles: 1234567 },
    { id: 2, name: "mAIner 2", status: "inactive", burnedCycles: 890123 } */
  ];

  let selectedBurnRate: 'Low' | 'Medium' | 'High' = 'Medium'; // Default value
  let showCopyIndicator = false;
  let selectedModel = ""; // track selected model
  let addressCopied = false;
  let modelType: 'Own' | 'Shared' = 'Shared'; // Default to Shared model
  let loginModalOpen = false;
  let mainerPaymentModalOpen = false;
  let mainerTopUpModalOpen = false;
  let selectedCanister = { id: "", name: "" };
  
  // Progress tracking for mAIner creation
  let isCreatingMainer = false;
  let mainerCreationProgress: {message: string, timestamp: string, complete: boolean}[] = [];
  let shouldOpenFirstMainerAfterCreation = false; // Flag to control when to auto-open

  // Track which agents are being topped up (agent-specific loading states)
  let agentsBeingToppedUp = new Set<string>();

  // Track which agents are having their burn rate updated
  let agentsBeingUpdated = new Set<string>();

  // Reactive counters for mAIner status
  $: activeMainers = agents.filter(agent => agent.status === 'active').length;
  $: inactiveMainers = agents.filter(agent => agent.status === 'inactive').length;
  $: totalMainers = agents.length;

  // For testing UI only - set to true to use mock data for the mainer accordion displaying canister INFO
  let useMockData = false;

  /**
   * Updates the agent settings based on user-selected burn rate level.
   * 
   * @param {'Low' | 'Medium' | 'High'} level - The burn rate level selected by the user
   * @param {object} agent - The mAIner agent to update
  */
  async function updateAgentBurnRate(level, agent) {
    console.log("in MainerAccordion updateAgentBurnRate level ", level);
    console.log("in MainerAccordion updateAgentBurnRate agent ", agent);
    console.log("in MainerAccordion updateAgentBurnRate agentCanisterActors ", agentCanisterActors);
    console.log("in MainerAccordion updateAgentBurnRate agentCanisterActors[0] ", agentCanisterActors[0]);
    
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
    };
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
      console.log("in MainerAccordion updateAgentBurnRate burnRateSetting ", burnRateSetting);
      await agentActor.updateAgentSettings(burnRateSetting);
      console.log(`Successfully updated burn rate to ${level}`);
      
      // Refresh the list of agents to show updated settings
      try {
        await store.loadUserMainerCanisters();
        // Explicitly reload agents after store update  
        agents = await loadAgents();
        console.log("Agents refreshed after burn rate update");
      } catch (refreshError) {
        console.error("Error refreshing agents after burn rate update:", refreshError);
      }
    } catch (error) {
      console.error("Failed to update agent settings:", error);
    } finally {
      // Remove from updating set after processing
      agentsBeingUpdated.delete(agent.id);
      agentsBeingUpdated = agentsBeingUpdated; // Trigger reactivity
    }
  };

  function toggleAccordion(index: string) {
    // Sanitize the ID to ensure it works as a CSS selector
    const sanitizedId = index.replace(/[^a-zA-Z0-9-_]/g, '_');
    const content = document.getElementById(`content-${sanitizedId}`);
    const icon = document.getElementById(`icon-${sanitizedId}`);
    
    if (!content || !icon) {
      console.warn(`Could not find accordion elements for ID: ${sanitizedId}`);
      return;
    }

    content.classList.toggle('accordion-open');
    if (content.classList.contains('accordion-open')) {
      icon.style.transform = 'rotate(0deg)';
    } else {
      icon.style.transform = 'rotate(180deg)';
    }
  };

  function openFirstMainerAccordion() {
    // Open the last mAIner's accordion (which will be the newest one in original order)
    if (agents.length > 0 && shouldOpenFirstMainerAfterCreation) {
      const lastMainerAccordion = agents[agents.length - 1]; // Get the last (newest) mAIner
      
      setTimeout(() => {
        const sanitizedId = lastMainerAccordion.id.replace(/[^a-zA-Z0-9-_]/g, '_');
        const content = document.getElementById(`content-${sanitizedId}`);
        const icon = document.getElementById(`icon-${sanitizedId}`);
        
        if (content && icon) {
          if (!content.classList.contains('accordion-open')) {
            content.classList.add('accordion-open');
            icon.style.transform = 'rotate(0deg)';
          }
        }
        
        shouldOpenFirstMainerAfterCreation = false; // Reset the flag
      }, 300); // Increased timeout to ensure DOM is ready
    }
  };

  function createAgent() {
    // Open the MainerPaymentModal to handle the payment
    mainerPaymentModalOpen = true;
  };
  
  function openTopUpModal(agent) {
    // Set the selected canister
    selectedCanister = {
      id: agent.id,
      name: agent.name
    };
    // Open the top-up modal
    mainerTopUpModalOpen = true;
  };

  function findAgentByAddress(canisterId) {
    return agentCanistersInfo.find(canister => canister.address === canisterId) || null;
  };

  function findAgentIndexByAddress(canisterId) {
    return agentCanistersInfo.findIndex(canister => canister.address === canisterId);
  };
  
  // Helper function to extract only the original backend fields for API calls
  function getOriginalCanisterInfo(enrichedCanisterInfo) {
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
  };
  
  // Handle top-up completion
  async function handleTopUpComplete(txId: string, canisterId: string) {
    console.log("Top-up completed" + (txId ? ` with transaction ID: ${txId}` : ""));
    mainerTopUpModalOpen = false;

    // Add this agent to the loading set
    agentsBeingToppedUp.add(canisterId);
    agentsBeingToppedUp = agentsBeingToppedUp; // Trigger reactivity
    
    // Get mAIner info from agentCanistersInfo via canisterId
    let mainerAgent = findAgentByAddress(canisterId);
    console.log("handleTopUpComplete mainerAgent: ", mainerAgent);
    if (!mainerAgent) {
      console.error("Error in handleTopUpComplete: no agent for canisterId");
      // Remove from loading set on error
      agentsBeingToppedUp.delete(canisterId);
      agentsBeingToppedUp = agentsBeingToppedUp;
      return; // TODO - Implementation: decide if the top up should just be credited to the user's first agent then instead (as otherwise the payment is lost)
    };

    // Clean the enriched data to get only original backend fields
    let cleanMainerAgent = getOriginalCanisterInfo(mainerAgent);
    console.log("handleTopUpComplete cleanMainerAgent: ", cleanMainerAgent);

    let mainerAgentTopUpInput = {
      paymentTransactionBlockId: BigInt(txId),
      mainerAgent: cleanMainerAgent,
    };
    try {
      let topUpUserMainerAgentResponse = await $store.gameStateCanisterActor.topUpCyclesForMainerAgent(mainerAgentTopUpInput);
      console.log("handleTopUpComplete topUpUserMainerAgentResponse: ", topUpUserMainerAgentResponse);
      
      if ('Ok' in topUpUserMainerAgentResponse) {
        // top up was successful
        console.log("Top-up successful");
      } else if ('Err' in topUpUserMainerAgentResponse) {
        console.error("Error in topUpCyclesForMainerAgent:", topUpUserMainerAgentResponse.Err);
      };
    } catch (topUpError) {
      console.error("Failed to top up mAIner:", topUpError);
    };

    // Refresh the list of agents to show updated balances
    try {
      await store.loadUserMainerCanisters();
      // Explicitly reload agents after store update
      agents = await loadAgents();
      console.log("Agents refreshed after top-up");
    } catch (refreshError) {
      console.error("Error refreshing agents after top-up:", refreshError);
    } finally {
      // Remove from loading set after processing
      agentsBeingToppedUp.delete(canisterId);
      agentsBeingToppedUp = agentsBeingToppedUp; // Trigger reactivity
    }
  }
  
  async function handleSendComplete(txId?: string) {
    console.log("Payment completed" + (txId ? ` with transaction ID: ${txId}` : ""));
    mainerPaymentModalOpen = false;
    
    // Set the creation process as started
    isCreatingMainer = true;
    shouldOpenFirstMainerAfterCreation = true; // Set flag to auto-open the new mAIner
    
    // Start the staged creation process
    // Step 1: Begin registration
    addProgressMessage("Registering new mAIner...");
    
    // Check which backend methods are available and use the appropriate flow
    if (typeof $store.gameStateCanisterActor.createUserMainerAgent === 'function') {
      // Use the full creation flow with all backend methods
      await handleFullMainerCreation(txId);
    } else {
      addProgressMessage("Backend methods not available for mAIner creation");
      isCreatingMainer = false;
      shouldOpenFirstMainerAfterCreation = false;
    }
  };

  async function handleFullMainerCreation(txId?: string) {
    // See the Game State canister interface here: src/declarations/game_state_canister/game_state_canister.did.d.ts
    type SelectableMainerLLMs = { 'Qwen2_5_500M' : null };
    let selectableMainerLLM = { 'Qwen2_5_500M' : null }; // default
    let selectedLLM : [] | [SelectableMainerLLMs] = selectedModel === "" ? [] : [selectableMainerLLM];
    type MainerAgentCanisterType = { 'NA' : null } |
      { 'Own' : null } |
      { 'ShareAgent' : null } |
      { 'ShareService' : null };
    let mainerAgentCanisterType : MainerAgentCanisterType = { 'Own' : null }; // default
    if (modelType === "Shared") {
      mainerAgentCanisterType = { 'ShareAgent' : null };
    };
    let mainerConfig = {
      selectedLLM,
      mainerAgentCanisterType,
    };
    let mainerCreationInput = {
      owner: [$store.principal] as [] | [Principal],
      paymentTransactionBlockId: BigInt(txId),
      mainerConfig,
    };
    try {
      let createUserMainerAgentResponse = await $store.gameStateCanisterActor.createUserMainerAgent(mainerCreationInput);
      console.log("createUserMainerAgentResponse:", createUserMainerAgentResponse);
      
      // Check if the response has the Ok property (successful response)
      if ('Ok' in createUserMainerAgentResponse) {
        addProgressMessage("mAIner canister created successfully!");
        
        // Step 2: Create controller
        addProgressMessage("Creating mAIner controller...");
        let spinUpMainerControllerCanisterResponse = await $store.gameStateCanisterActor.spinUpMainerControllerCanister(createUserMainerAgentResponse.Ok);
        
        if ('Ok' in spinUpMainerControllerCanisterResponse) {
          // Step 3: Set up LLM
          if (modelType === 'Own') {
            // We don't wait for LLM canister setup anymore, just trigger it and let it run in background
            addProgressMessage("Starting LLM environment setup in the background...");
            
            // Trigger LLM setup without awaiting it
            $store.gameStateCanisterActor.setUpMainerLlmCanister(spinUpMainerControllerCanisterResponse.Ok)
              .then((response) => {
                console.log("LLM canister setup triggered successfully:", response);
              })
              .catch((error) => {
                console.error("Error triggering LLM setup:", error);
              });
            
            addProgressMessage("LLM setup will continue in the background (it may take several minutes to complete)");
          }
          
          // Step 4: Final configuration
          addProgressMessage("Configuring mAIner parameters...");
          // TODO: set default cycle burn rate, start mAIner's timer (if not done yet by backend)

          // Step 5: Completion
          setTimeout(() => {
            addProgressMessage("mAIner successfully created! You can start using it while LLM setup completes in the background.", true);
            shouldOpenFirstMainerAfterCreation = true; // Ensure flag is set before reloading
            
            // Refresh the list of agents to show the newly created one
            store.loadUserMainerCanisters().then(() => {
              // Wait for the reactive update to complete, then open the first mAIner (newest one)
              setTimeout(() => {
                openFirstMainerAccordion();
                // Reset the terminal after opening the accordion
                setTimeout(() => {
                  isCreatingMainer = false;
                  mainerCreationProgress = [];
                }, 2000);
              }, 500); // Increased timeout for better reliability
            });
          }, 2000);
        } else if ('Err' in spinUpMainerControllerCanisterResponse) {
          console.error("Error in spinUpMainerControllerCanister:", spinUpMainerControllerCanisterResponse.Err);
          addProgressMessage("Error creating controller: " + JSON.stringify(spinUpMainerControllerCanisterResponse.Err));
          isCreatingMainer = false;
        };
      } else if ('Err' in createUserMainerAgentResponse) {
        // Handle error response
        console.error("Error in createUserMainerAgent:", createUserMainerAgentResponse.Err);
        addProgressMessage("Error creating mAIner: " + JSON.stringify(createUserMainerAgentResponse.Err));
        isCreatingMainer = false;
      };
    } catch (creationError) {
      console.error("Failed to create mAIner:", creationError);
      addProgressMessage("Failed to create mAIner: " + creationError.message);
      isCreatingMainer = false;
    };
  };

  async function handleSimplifiedMainerCreation(txId?: string) {
    // This method is no longer needed since createUserMainerAgent is available
    // But keeping it for potential future use
    addProgressMessage("Simplified creation flow not implemented");
    isCreatingMainer = false;
  };

  // Helper function to add a progress message with timestamp
  function addProgressMessage(message: string, isComplete = false) {
    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    mainerCreationProgress = [
      ...mainerCreationProgress,
      { message, timestamp, complete: isComplete }
    ];
  }

  function copyAddress() {
    addressCopied = true;
  };

  async function loadAgents() {
    // The store now provides enriched canister info with status, cycles, etc.
    const enrichedCanistersInfo = agentCanistersInfo;

    // Convert the enriched info to the format expected by the component
    return enrichedCanistersInfo.map((canisterInfo, index) => {
      // Get the correct actor by index
      const agentActor = agentCanisterActors[index];
      
      // Determine mainer type from the canister info
      let mainerType = 'Unknown';
      if (canisterInfo.canisterType) {
        if ('Own' in canisterInfo.canisterType.MainerAgent) {
          mainerType = 'Own';
        } else if ('ShareAgent' in canisterInfo.canisterType.MainerAgent) {
          mainerType = 'Shared';
        }
      }

      // All the heavy lifting is now done in the store
      return {
        id: canisterInfo.address,
        name: `mAIner ${canisterInfo.address.slice(0, 5)}`,
        status: canisterInfo.uiStatus || "active",  // Use uiStatus from enriched data
        burnedCycles: canisterInfo.burnedCycles || 0,
        cycleBalance: canisterInfo.cycleBalance || 0,
        cyclesBurnRate: canisterInfo.cyclesBurnRate || {},
        cyclesBurnRateSetting: canisterInfo.cyclesBurnRateSetting || "Medium",
        mainerType,
        llmCanisters: canisterInfo.llmCanisters || [],
        llmSetupStatus: canisterInfo.llmSetupStatus || '',
        hasError: canisterInfo.hasError || false
      };
    });
  };

  $: {
    console.log("MainerAccordion reactive agentCanisterActors", agentCanisterActors); // TODO: the usage of agentCanisterActors here is needed to react to changes to it, but this should be made nicer (not via this print statement)
    console.log("MainerAccordion reactive agentCanistersInfo", agentCanistersInfo); // TODO: the usage of agentCanistersInfo here is needed to react to changes to it, but this should be made nicer (not via this print statement)

    (async () => {
      agents = await loadAgents();
      // Check if we should auto-open the first mAIner after creation
      openFirstMainerAccordion();
    })();
  };

  function toggleLoginModal() {
    loginModalOpen = !loginModalOpen;
  }

  onMount(async () => {
    //console.log("MainerAccordion onMount agentCanisterActors", agentCanisterActors);
    //console.log("MainerAccordion onMount agentCanistersInfo", agentCanistersInfo);
    // Retrieve the data from the agents' backend canisters to fill the above agents array dynamically
    agents = await loadAgents();
    //console.log("MainerAccordion onMount agents", agents);
    
    // Automatically open the create accordion if no agents exist, or open latest mAIner if agents exist
    if (agents.length === 0) {
      setTimeout(() => {
        toggleAccordion('create');
      }, 100);
    } else {
      // Open the latest mAIner if agents exist
      setTimeout(() => {
        const latestAgent = agents[agents.length - 1];
        if (latestAgent && latestAgent.id) {
          toggleAccordion(latestAgent.id);
        }
      }, 100);
    }
  });

  // Watch for changes in agents or auth status
  $: if (agents.length === 0) {
    // Only open create accordion if no agents
    setTimeout(() => {
      const content = document.getElementById(`content-create`);
      const icon = document.getElementById(`icon-create`);
      if (content && icon) {
        if (!content.classList.contains('accordion-open')) {
          content.classList.add('accordion-open');
          icon.style.transform = 'rotate(0deg)';
        }
      }
    }, 100);
  } else if (agents.length > 0 && !shouldOpenFirstMainerAfterCreation) {
    // If we have agents and this isn't triggered by creation, open the latest mAIner
    setTimeout(() => {
      // First, ensure create accordion is closed
      const createContent = document.getElementById(`content-create`);
      const createIcon = document.getElementById(`icon-create`);
      if (createContent && createIcon && createContent.classList.contains('accordion-open')) {
        createContent.classList.remove('accordion-open');
        createIcon.style.transform = 'rotate(180deg)';
      }
      
      // Then open the latest mAIner
      const latestAgent = agents[agents.length - 1];
      if (latestAgent && latestAgent.id) {
        const sanitizedId = latestAgent.id.replace(/[^a-zA-Z0-9-_]/g, '_');
        const content = document.getElementById(`content-${sanitizedId}`);
        const icon = document.getElementById(`icon-${sanitizedId}`);
        
        if (content && icon && !content.classList.contains('accordion-open')) {
          content.classList.add('accordion-open');
          icon.style.transform = 'rotate(0deg)';
        }
      }
    }, 100);
  }
</script>

<!-- Create Agent Accordion -->
<div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-purple-600/20 to-blue-600/20 dark:from-purple-900/40 dark:to-blue-900/40 rounded-t-lg">
  <button on:click={() => toggleAccordion('create')} class="w-full flex justify-between items-center py-8 px-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-base font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform border border-purple-500/20">
    <span class="flex items-center">
      <div class="flex-shrink-0 w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3 shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="flex flex-col items-start">
        <span class="text-lg font-bold">Create new mAIner</span>
        <span class="text-purple-100 text-xs font-normal">Start your AI mining journey</span>
      </div>
    </span>
    <span id="icon-create" class="text-white/80 transition-transform duration-300 bg-white/10 rounded-full p-1" style="transform: rotate(180deg)">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-5 h-5">
        <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
  <div id="content-create" class="accordion-content bg-white dark:bg-gray-900">
    <div class="pb-5 text-sm text-gray-700 dark:text-gray-300 space-y-4 p-4">
      
    {#if isAuthenticated}
      <ol class="relative mx-2 text-gray-500 dark:text-gray-400 border-s border-gray-200 dark:border-gray-700">                  
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {modelType ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                </svg>
            </span>
            <h3 class="font-medium leading-tight mb-3 dark:text-gray-300">AI Agent Type</h3>
            
            <!-- Modern Agent Type Selector -->
            <div class="space-y-3 mb-2">
              <!-- Shared Model Card -->
              <div 
                class="relative border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 hover:shadow-md {modelType === 'Shared' 
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' 
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-purple-300 dark:hover:border-purple-600'}"
                on:click={() => modelType = 'Shared'}
                on:keydown={(e) => e.key === 'Enter' && (modelType = 'Shared')}
                role="button"
                tabindex="0"
              >
                <!-- Selection indicator -->
                <div class="absolute top-3 right-3">
                  {#if modelType === 'Shared'}
                    <div class="w-5 h-5 bg-purple-600 rounded-full flex items-center justify-center">
                      <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  {:else}
                    <div class="w-5 h-5 border-2 border-gray-300 dark:border-gray-600 rounded-full"></div>
                  {/if}
                </div>

                <div class="flex items-start space-x-3 pr-8">
                  <!-- Icon -->
                  <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                  </div>

                  <!-- Content -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-2 mb-1">
                      <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">mAIner Agent</h4>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                        Ready
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                      Shared infrastructure with optimized performance
                    </p>
                    <div class="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                        </svg>
                        <span>0.0002 ICP</span>
                      </div>
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        <span>Instant deploy</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Own Model Card (Disabled/Coming Soon) -->
              <!-- 
              <div 
                class="relative border-2 border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-gray-50 dark:bg-gray-800/50 opacity-60"
              >
                <div class="absolute top-3 right-3">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                    Coming Soon
                  </span>
                </div>

                <div class="flex items-start space-x-3 pr-20">
                  <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                  </div>

                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1">Custom Model</h4>
                    <p class="text-xs text-gray-500 dark:text-gray-500 mb-2">
                      Deploy your own AI model with full control
                    </p>
                    <div class="flex items-center space-x-4 text-xs text-gray-400 dark:text-gray-500">
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                        </svg>
                        <span>0.0003 ICP</span>
                      </div>
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </svg>
                        <span>Custom setup</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              -->
            </div>

            <!-- Original button code commented out
            <div class="inline-flex rounded-full shadow-xs w-full justify-start mb-1" role="group">
              <button 
                type="button" 
                class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
                {modelType === 'Own' 
                  ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                on:click={() => modelType = 'Own'}
              >
                Own model
              </button>
              <button 
                type="button" 
                class="px-4 py-2 text-xs cursor-default font-medium border border-gray-200 dark:border-gray-600 focus:z-10 focus:ring-2 focus:ring-blue-700
                {modelType === 'Shared' 
                  ? 'bg-purple-600 dark:bg-purple-700 text-white' 
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300'}"
                on:click={() => modelType = 'Shared'}
              >
                mAIner
              </button>
            </div>
            -->
        </li>
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {selectedModel ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if selectedModel}
                  <!-- Checkmark icon for when model is selected -->
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <!-- Selection/Choose icon for default state -->
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                  </svg>
                {/if}
            </span>
            <!-- Commenting out model selection dropdown
            {#if modelType === 'Own'}
              <form class="max-w-sm">
                <label for="countries" class="block mb-2 text-sm font-medium text-gray-500 dark:text-gray-300">Choose a model</label>
                <select 
                  bind:value={selectedModel}
                  id="countries" 
                  class="bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-500 dark:text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
                  <option value="">Choose model</option>
                  <option value="SL">Small LLM</option>
                  <option value="G2">Gpt-2</option>
                  <option value="QW">Qwen</option>
                  <option disabled value="DS">DeepSeek</option>
                </select>
              </form>
            {/if}
            -->
        </li>
        <li class="mb-6 ms-6">
            <span class="absolute flex items-center justify-center w-8 h-8 {addressCopied ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-100 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if addressCopied}
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                {/if}
            </span>
            <h3 class="font-medium leading-tight mb-1 dark:text-gray-300">Pay & Spin up</h3>
            <!-- <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-md p-3 mb-3">
              <p class="text-xs text-blue-800 dark:text-blue-300">
                Creating the mAIner requires a setup fee of <span class="font-medium">{modelType === 'Own' ? '0.0003' : '0.0002'} ICP</span> for {modelType} model
              </p>
            </div> -->
        </li>
      </ol>

      <div class="flex flex-col items-end">
        <button 
          on:click={createAgent} 
          disabled={isCreatingMainer}
          class="bg-purple-600 dark:bg-purple-700 w-1/2 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-4 py-2 rounded-[16px] transition-colors"
          class:opacity-50={isCreatingMainer}
          class:cursor-not-allowed={isCreatingMainer}
        >
          Create mAIner
        </button>
        <div class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
          {modelType === 'Own' ? '0.0003' : '0.0002'} ICP
        </div>
      </div>
      
      <!-- Terminal-style progress component -->
      {#if isCreatingMainer}
        <div class="mt-4 bg-gray-900 text-green-400 font-mono text-sm rounded-lg p-3 border border-gray-700 overflow-hidden">
          <div class="flex items-center justify-between mb-2 border-b border-gray-700 pb-2">
            <div class="text-gray-300 text-xs">mAIner Creation Progress</div>
            <div class="flex items-center">
              <div class="h-4 w-4 border-2 border-gray-400/30 border-t-green-400 rounded-full animate-spin"></div>
            </div>
          </div>
          <div class="h-40 overflow-y-auto terminal-scroll">
            {#each mainerCreationProgress as progress}
              <div class="flex mb-1 items-start" class:text-green-300={progress.complete}>
                <span class="text-gray-500 mr-2">[{progress.timestamp}]</span>
                <span class="flex-1">{progress.message}</span>
                {#if progress.complete}
                  <span class="text-green-500">✓</span>
                {/if}
              </div>
            {/each}
            {#if mainerCreationProgress.length > 0 && !mainerCreationProgress[mainerCreationProgress.length - 1].complete}
              <div class="blink">_</div>
            {/if}
          </div>
        </div>
      {/if}
    {:else}
      <div class="flex flex-col items-center justify-center py-8">
        <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2 mt-8">You need to login first</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4 text-center">
          Connect your wallet to create and manage your mAIners
        </p>
        <button 
          on:click={toggleLoginModal} 
          class="bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-6 py-2 rounded-full transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
          </svg>
          Connect
        </button>
      </div>
    {/if}
    </div>
  </div>
</div>

{#if loginModalOpen}
  <LoginModal toggleModal={toggleLoginModal} />
{/if}

{#if mainerPaymentModalOpen}
  <MainerPaymentModal 
    isOpen={mainerPaymentModalOpen}
    onClose={() => mainerPaymentModalOpen = false}
    onSuccess={handleSendComplete}
    {modelType}
  />
{/if}

{#if mainerTopUpModalOpen}
  <MainerTopUpModal 
    isOpen={mainerTopUpModalOpen}
    onClose={() => mainerTopUpModalOpen = false}
    onSuccess={handleTopUpComplete}
    canisterId={selectedCanister.id}
    canisterName={selectedCanister.name}
  />
{/if}

<!-- mAIner Summary Header -->
{#if totalMainers > 0}
  <div class="mt-2 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-1">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span class="text-sm text-green-700 dark:text-green-400 font-medium">{activeMainers} Active</span>
          </div>
          <div class="flex items-center space-x-1">
            <div class="w-3 h-3 rounded-full bg-gray-400"></div>
            <span class="text-sm text-gray-600 dark:text-gray-400 font-medium">{inactiveMainers} Inactive</span>
            {#if inactiveMainers > 0}
              <div class="text-xs text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 px-2 py-1 rounded-md">
                ⚠️ {inactiveMainers} mAIner{inactiveMainers === 1 ? '' : 's'} need{inactiveMainers === 1 ? 's' : ''} cycles
              </div>
            {/if}
          </div>
        </div>
      </div>
      
    </div>
  </div>
{/if}

<!-- Existing Agents -->
{#each agents as agent, index}
  {#if agent && agent.id}
    {@const sanitizedId = agent.id.replace(/[^a-zA-Z0-9-_]/g, '_')}
    {@const buttonClasses = `w-full flex justify-between items-center py-5 px-4 text-gray-800 dark:text-gray-200 ${agent.status === 'inactive' ? 'bg-red-50 dark:bg-red-900/10' : ''}`}
    <div class="border-b border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900" class:opacity-75={agent.status === 'inactive'}>
      <button on:click={() => toggleAccordion(agent.id)} class={buttonClasses}>
        <span class="flex items-center font-medium text-sm">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-600 dark:text-gray-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v7c0 1.1.9 2 2 2h2l1 2v7h2v-7l1-2h2l1 2v7h2v-7l1-2h2c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 10H4V4h2v6zm4 0H8V4h2v6zm4 0h-2V4h2v6zm4 0h-2V4h2v6z"/>
          </svg>
          {agent.name}
          {#if agent.status === 'inactive'}
            <span class="ml-2 text-xs text-red-600 dark:text-red-400">(needs cycles)</span>
          {/if}
        </span>
        <div class="flex items-center">
          <!-- Add LLM setup status badge when applicable -->
          {#if agent.mainerType === 'Own' && agent.llmSetupStatus === 'inProgress'}
            <span class="mr-2 px-2 py-1 rounded-full text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-400">
              LLM setup in progress
            </span>
          {/if}
          <span class={`mr-4 px-2 py-1 rounded-full text-xs ${agent.status === 'active' ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-400' : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-400'}`}>
            {agent.status}
          </span>
          <span id="icon-{sanitizedId}" class="text-gray-600 dark:text-gray-400 transition-transform duration-300" style="transform: rotate(180deg)">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
              <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
            </svg>
          </span>
        </div>
      </button>
      <div id="content-{sanitizedId}" class="accordion-content">
        <div class="pb-5 text-sm text-gray-700 dark:text-gray-300 p-4 bg-gray-5 dark:bg-gray-900">
          <!-- Canister Information Section -->
          <div class="flex flex-col space-y-2 mb-2">
            <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg">
              <h2 class="text-sm mb-2 font-medium">Canister Information</h2>
              <div class="flex flex-col gap-2">
                <div class="flex items-center flex-wrap">
                  <span class="text-xs mr-2 w-24">Controller ID:</span>
                  <a href="https://dashboard.internetcomputer.org/canister/{agent.id}" target="_blank" rel="noopener noreferrer" class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-gray-700 dark:text-green-400 border border-green-400 break-all hover:bg-green-200 dark:hover:bg-gray-600 transition-colors flex items-center">
                    <span>{agent.id}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" transform="rotate(45, 10, 10)" />
                    </svg>
                  </a>
                </div>
                
                <!-- Show mAIner type 
                <div class="flex items-center">
                  <span class="text-xs mr-2 w-24">Type:</span>
                  <span class="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-gray-700 dark:text-yellow-300 border border-yellow-300">{agent.mainerType}</span>
                </div>
                -->
                
                <!-- For Own type mAIners, show LLM information or setup status -->
                {#if agent.mainerType === 'Own'}
                  <div class="flex flex-col mt-2">
                    <!-- Show LLM setup status if in progress -->
                    {#if agent.llmSetupStatus === 'inProgress'}
                      <div class="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-md p-3 my-2">
                        <div class="flex items-center">
                          <svg class="animate-spin h-4 w-4 text-yellow-600 dark:text-yellow-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <p class="text-xs text-yellow-800 dark:text-yellow-300">
                            <span class="font-medium">LLM setup in progress</span> - This may take several minutes to complete and will happen in the background. You can use the mAIner with shared LLMs in the meantime.
                          </p>
                        </div>
                      </div>
                    {/if}
                  
                    <span class="text-xs mb-1">Attached LLMs:</span>
                    {#if agent.llmCanisters && agent.llmCanisters.length > 0}
                      <div class="flex flex-col gap-2 ml-2 mt-1">
                        {#each agent.llmCanisters as llmCanister, i}
                          <div class="flex items-center flex-wrap">
                            <span class="text-xs mr-2 w-20">LLM {i+1}:</span>
                            <a href="https://dashboard.internetcomputer.org/canister/{llmCanister}" target="_blank" rel="noopener noreferrer" class="bg-indigo-100 text-indigo-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-gray-700 dark:text-indigo-400 border border-indigo-400 break-all hover:bg-indigo-200 dark:hover:bg-gray-600 transition-colors flex items-center">
                              <span>{llmCanister}</span>
                              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" transform="rotate(45, 10, 10)" />
                              </svg>
                            </a>
                          </div>
                        {/each}
                      </div>
                    {:else}
                      <div class="ml-2 mt-1">
                        {#if agent.llmSetupStatus === 'inProgress'}
                          <span class="text-xs italic text-yellow-500 dark:text-yellow-400">LLM canister setup in progress...</span>
                        {:else}
                          <span class="text-xs italic text-gray-500 dark:text-gray-400">No LLM canisters attached yet</span>
                        {/if}
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            </div>
          </div>
          
          <div class="flex flex-col space-y-2 mb-2">
            <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
              <div class="flex items-center justify-between">
                  <h2 class="text-sm mb-2">Top up cycles</h2>
                  <button 
                    type="button" 
                    class="py-2.5 px-5 me-2 text-xs font-medium text-gray-900 dark:text-gray-300 focus:outline-none bg-white dark:bg-gray-700 rounded-full border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400"
                    class:opacity-50={agentsBeingToppedUp.has(agent.id)}
                    class:cursor-not-allowed={agentsBeingToppedUp.has(agent.id)}
                    disabled={agentsBeingToppedUp.has(agent.id)}
                    on:click={() => openTopUpModal(agent)}
                  >
                    {#if agentsBeingToppedUp.has(agent.id)}
                      <span class="w-3 h-3 mr-1 border-2 border-gray-400/30 border-t-gray-400 rounded-full animate-spin"></span>
                    {/if}
                    Top-up
                  </button>
              </div>
              <!-- Cycle Balance Display -->
              <div class="mt-2 flex items-center">
                <span class="text-xs text-gray-500 dark:text-gray-400">Current balance:</span>
                {#if agentsBeingToppedUp.has(agent.id)}
                  <span class="ml-2 text-sm font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-sm dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800 flex items-center">
                    <span class="w-3 h-3 mr-2 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin"></span>
                    Updating...
                  </span>
                {:else}
                  <span class="ml-2 text-sm font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-sm dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                    {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 4, false)} T cycles
                  </span>
                {/if}
              </div>
            </div>
          </div>

          <div class="flex flex-col space-y-2 mb-2">
            <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
              <div class="flex flex-col">
                  <h2 class="text-sm mb-2">Set daily burn rate</h2>
                  <div class="inline-flex rounded-full shadow-xs w-full justify-end" role="group">
                    <button 
                      type="button" 
                      class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
                      {agent.cyclesBurnRateSetting === 'Low' 
                        ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                        : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                      class:opacity-50={agentsBeingUpdated.has(agent.id)}
                      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id)}
                      disabled={agentsBeingUpdated.has(agent.id)}
                      on:click={() => updateAgentBurnRate('Low', agent) }
                    >
                      Low
                    </button>
                    <button 
                      type="button" 
                      class="px-4 py-2 text-xs font-medium border-t border-b border-gray-200 dark:border-gray-600 focus:z-10 focus:ring-2 focus:ring-blue-700
                      {agent.cyclesBurnRateSetting === 'Medium' 
                        ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                        : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                      class:opacity-50={agentsBeingUpdated.has(agent.id)}
                      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id)}
                      disabled={agentsBeingUpdated.has(agent.id)}
                      on:click={() => updateAgentBurnRate('Medium', agent) }
                    >
                      Medium
                    </button>
                    <button 
                      type="button" 
                      class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-e-full focus:z-10 focus:ring-2 focus:ring-blue-700
                      {agent.cyclesBurnRateSetting === 'High' 
                        ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                        : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                      class:opacity-50={agentsBeingUpdated.has(agent.id)}
                      class:cursor-not-allowed={agentsBeingUpdated.has(agent.id)}
                      disabled={agentsBeingUpdated.has(agent.id)}
                      on:click={() => updateAgentBurnRate('High', agent) }
                    >
                      High
                    </button>
                  </div>
                  {#if agentsBeingUpdated.has(agent.id)}
                    <div class="flex items-center justify-center mt-2">
                      <span class="w-4 h-4 mr-2 border-2 border-purple-400/30 border-t-purple-600 rounded-full animate-spin"></span>
                      <span class="text-xs text-purple-600 dark:text-purple-400">Updating burn rate setting...</span>
                    </div>
                  {/if}
                </div>
            </div>
          </div>

          <!-- <div class="flex flex-col space-y-2 my-2">
            <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
              <div class="flex items-center justify-between">
                <h2 class="text-sm">Manage settings</h2>
              </div>
            </div>
          </div> -->
          <div class="flex flex-col space-y-2 mb-2">
            <CyclesDisplayAgent cycles={agent.burnedCycles} label="Burned Cycles" />
          </div>

        </div>
      </div>
    </div>
  {/if}
{/each}

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s ease-in-out;
  }
  
  .accordion-content.accordion-open {
    max-height: 2000px; /* High value to ensure all content is visible */
    overflow: visible;
  }
  
  /* Terminal styling */
  .terminal-scroll {
    scrollbar-width: thin;
    scrollbar-color: #4a5568 #2d3748;
  }
  
  .terminal-scroll::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  .terminal-scroll::-webkit-scrollbar-track {
    background: #2d3748;
    border-radius: 4px;
  }
  
  .terminal-scroll::-webkit-scrollbar-thumb {
    background-color: #4a5568;
    border-radius: 4px;
    border: 2px solid #2d3748;
  }
  
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }
  
  .blink {
    animation: blink 1s step-end infinite;
  }
</style>