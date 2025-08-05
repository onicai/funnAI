<script lang="ts">
  import { onMount, afterUpdate, onDestroy } from 'svelte';
  import CyclesDisplayAgent from './CyclesDisplayAgent.svelte';
  import DailyBurnRatePanel from './DailyBurnRatePanel.svelte';
  import FlockOverview from './mainers/FlockOverview.svelte';
  import { store } from "../../stores/store";
  import LoginModal from '../login/LoginModal.svelte';
  import MainerPaymentModal from './MainerPaymentModal.svelte';
  import MainerTopUpModal from './MainerTopUpModal.svelte';
  import TopUpCelebration from './TopUpCelebration.svelte';
  import { Principal } from '@dfinity/principal';
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { tooltip } from "../../helpers/utils/tooltip";
  import { getSharedAgentPrice, getOwnAgentPrice, getIsProtocolActive, getIsMainerCreationStopped, getWhitelistAgentPrice, getPauseWhitelistMainerCreationFlag, getIsWhitelistPhaseActive } from "../../helpers/gameState";

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = $store.isAuthed;
  $: isCreatingMainer = $store.isCreatingMainer;
  $: mainerCreationProgress = $store.mainerCreationProgress;
  $: shouldOpenFirstMainerAfterCreation = $store.shouldOpenFirstMainerAfterCreation;

  // Loading state for protocol flags
  let protocolFlagsLoading = true;

  let isProtocolActiveFlag = true; // Will be loaded
  $: isProtocolActive = isProtocolActiveFlag;

  let isMainerCreationStoppedFlag = false; // Will be loaded
  $: stopMainerCreation = isMainerCreationStoppedFlag;

  // Whitelist phase variables
  let isWhitelistPhaseActiveFlag = false; // Will be loaded
  $: isWhitelistPhaseActive = isWhitelistPhaseActiveFlag;
  
  let isPauseWhitelistMainerCreationFlag = false; // Will be loaded
  $: isPauseWhitelistMainerCreation = isPauseWhitelistMainerCreationFlag;

  let agents = [];

  // Separate unlocked mAIners for whitelist phase
  let unlockedMainers = [];

  let selectedBurnRate: 'Low' | 'Medium' | 'High' = 'Medium'; // Default value
  let showCopyIndicator = false;
  let selectedModel = ""; // track selected model
  let addressCopied = false;
  let modelType: 'Own' | 'Shared' = 'Shared'; // Default to Shared model
  let loginModalOpen = false;
  let mainerPaymentModalOpen = false;
  let mainerTopUpModalOpen = false;
  let selectedCanister = { id: "", name: "" };
  
  // Track selected unlocked mAIner for whitelist creation
  let selectedUnlockedMainer = null;
  
  // Track which agents are being topped up (agent-specific loading states)
  let agentsBeingToppedUp = new Set<string>();



  // Track which agents are having their balance refreshed
  let agentsBeingRefreshed = new Set<string>();

  // Add loading state for individual whitelist mAIner creation
  let whitelistMainersBeingCreated = new Set<string>();

  // Celebration state for top-up
  let showCelebration = false;
  let celebrationAmount = "";
  let celebrationToken = "";

  // Reactive counters for mAIner status
  $: activeMainers = agents.filter(agent => agent.status === 'active').length;
  $: inactiveMainers = agents.filter(agent => agent.status === 'inactive').length;
  $: totalMainers = agents.length;

  // Reactive counters for burn rate distribution
  $: lowBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'Low').length;
  $: mediumBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'Medium').length;
  $: highBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'High').length;

  // Reactive mAIner price based on model type and whitelist phase
  let currentMainerPrice = 10; // Will be loaded
  let currentWhitelistPrice = 5; // Will be loaded
  $: mainerPrice = isWhitelistPhaseActive ? currentWhitelistPrice : currentMainerPrice;

  async function getMainerPrice() {
    try {
      let price = modelType === 'Own' ? await getOwnAgentPrice() : await getSharedAgentPrice();
      price = Number(price);

      if (price <= 0) {
        console.error("Issue getting mAIner price as it's 0 or negative.");
        // Return fallback value instead of undefined
        return 10; // Default price for all mAIner types
      };

      return price;      
    } catch (error) {
      console.error("Error getting mAIner price:", error);
      // Return fallback value instead of undefined
      return 10; // Default price for all mAIner types
    }
  };

  // Handle burn rate update from the DailyBurnRatePanel component
  async function handleBurnRateUpdate() {
    try {
      await store.loadUserMainerCanisters();
      // Explicitly reload agents after store update  
      agents = await loadAgents();
    } catch (refreshError) {
      console.error("Error refreshing agents after burn rate update:", refreshError);
    }
  }

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
    // Open the first mAIner's accordion (which will be the newest one since we reverse the order)
    if (agents.length > 0 && shouldOpenFirstMainerAfterCreation) {
      const firstMainerAccordion = agents[0]; // Get the first (newest) mAIner
      
      setTimeout(() => {
        const sanitizedId = firstMainerAccordion.id.replace(/[^a-zA-Z0-9-_]/g, '_');
        const content = document.getElementById(`content-${sanitizedId}`);
        const icon = document.getElementById(`icon-${sanitizedId}`);
        
        if (content && icon) {
          if (!content.classList.contains('accordion-open')) {
            content.classList.add('accordion-open');
            icon.style.transform = 'rotate(0deg)';
          }
        }
        
        store.resetMainerCreationAfterOpen(); // Reset the flag using store method
      }, 300); // Increased timeout to ensure DOM is ready
    }
  };

  function createAgent() {
    // Safety check: prevent starting new creation if one is already in progress
    if (isCreatingMainer) {
      console.warn("mAIner creation already in progress, ignoring button click");
      return;
    }
    
    // Open the MainerPaymentModal to handle the payment
    mainerPaymentModalOpen = true;
  };

  function createWhitelistAgent(unlockedMainer) {
    // Safety check: prevent starting new creation if one is already in progress
    if (isCreatingMainer) {
      console.warn("mAIner creation already in progress, ignoring whitelist creation button click");
      return;
    }
    
    // Set the selected unlocked mAIner for whitelist creation
    selectedUnlockedMainer = unlockedMainer;
    
    // Add this mAIner to the loading set (using consistent identifier)
    const mainerIdentifier = unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || Date.now()}`;
    whitelistMainersBeingCreated.add(mainerIdentifier);
    whitelistMainersBeingCreated = whitelistMainersBeingCreated; // Trigger reactivity
    
    // Open the MainerPaymentModal with whitelist pricing
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

  // Helper function to generate consistent visual identity for each mAIner
  function getMainerVisualIdentity(agentId: string) {
    // Create a simple hash from the agent ID for consistent colors
    let hash = 0;
    for (let i = 0; i < agentId.length; i++) {
      const char = agentId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    // Define a set of beautiful color schemes
    const colorSchemes = [
      {
        bg: 'from-purple-500 to-indigo-600',
        bgHover: 'from-purple-600 to-indigo-700',
        accent: 'bg-purple-100/30',
        icon: 'text-purple-100',
        text: 'text-purple-50',
        border: 'border-purple-400/30'
      },
      {
        bg: 'from-emerald-500 to-teal-600',
        bgHover: 'from-emerald-600 to-teal-700',
        accent: 'bg-emerald-100/30',
        icon: 'text-emerald-100',
        text: 'text-emerald-50',
        border: 'border-emerald-400/30'
      },
      {
        bg: 'from-blue-500 to-cyan-600',
        bgHover: 'from-blue-600 to-cyan-700',
        accent: 'bg-blue-100/30',
        icon: 'text-blue-100',
        text: 'text-blue-50',
        border: 'border-blue-400/30'
      },
      {
        bg: 'from-rose-500 to-pink-600',
        bgHover: 'from-rose-600 to-pink-700',
        accent: 'bg-rose-100/30',
        icon: 'text-rose-100',
        text: 'text-rose-50',
        border: 'border-rose-400/30'
      },
      {
        bg: 'from-amber-500 to-orange-600',
        bgHover: 'from-amber-600 to-orange-700',
        accent: 'bg-amber-100/30',
        icon: 'text-amber-100',
        text: 'text-amber-50',
        border: 'border-amber-400/30'
      },
      {
        bg: 'from-violet-500 to-purple-600',
        bgHover: 'from-violet-600 to-purple-700',
        accent: 'bg-violet-100/30',
        icon: 'text-violet-100',
        text: 'text-violet-50',
        border: 'border-violet-400/30'
      },
      {
        bg: 'from-teal-500 to-cyan-600',
        bgHover: 'from-teal-600 to-cyan-700',
        accent: 'bg-teal-100/30',
        icon: 'text-teal-100',
        text: 'text-teal-50',
        border: 'border-teal-400/30'
      },
      {
        bg: 'from-indigo-500 to-blue-600',
        bgHover: 'from-indigo-600 to-blue-700',
        accent: 'bg-indigo-100/30',
        icon: 'text-indigo-100',
        text: 'text-indigo-50',
        border: 'border-indigo-400/30'
      }
    ];
    
    // Define different avatar patterns/icons
    const avatarIcons = [
      // Robot variants
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zM9 12c0-.55-.45-1-1-1s-1 .45-1 1 .45 1 1 1 1-.45 1-1zm8 0c0-.55-.45-1-1-1s-1 .45-1 1 .45 1 1 1 1-.45 1-1zm-4 4c-1.1 0-2-.9-2-2h4c0 1.1-.9 2-2 2z"/>
      </svg>`,
      // Chip/processor
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M6 7h12v10H6V7zm-2-2v14h16V5H4zm5 3v8h6V8H9zm2 2h2v4h-2v-4z"/>
        <rect x="2" y="8" width="2" height="2"/>
        <rect x="2" y="12" width="2" height="2"/>
        <rect x="20" y="8" width="2" height="2"/>
        <rect x="20" y="12" width="2" height="2"/>
        <rect x="8" y="2" width="2" height="2"/>
        <rect x="12" y="2" width="2" height="2"/>
        <rect x="8" y="20" width="2" height="2"/>
        <rect x="12" y="20" width="2" height="2"/>
      </svg>`,
      // Neural network
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <circle cx="6" cy="6" r="2"/>
        <circle cx="18" cy="6" r="2"/>
        <circle cx="6" cy="18" r="2"/>
        <circle cx="18" cy="18" r="2"/>
        <circle cx="12" cy="12" r="3"/>
        <path d="M8 6l2.5 4.5M8 18l2.5-4.5M16 6l-2.5 4.5M16 18l-2.5-4.5"/>
      </svg>`,
      // Diamond
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M12 2l4 4-4 4-4-4 4-4zm6 6l4 4-4 4-4-4 4-4zM6 8l4 4-4 4-4-4 4-4zm6 6l4 4-4 4-4-4 4-4z"/>
      </svg>`,
      // Hexagon
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M17.5 3.5L22 12l-4.5 8.5h-11L2 12l4.5-8.5h11zm-1 2h-9L5 12l2.5 6.5h9L19 12l-2.5-6.5z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>`,
      // Star
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6-4.8-6 4.8 2.4-7.2-6-4.8h7.6z"/>
      </svg>`,
      // Lightning
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M13 2L4 14h7v7l9-11h-7V2z"/>
      </svg>`,
      // Crystal
      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
        <path d="M12 1l8 5v12l-8 5-8-5V6l8-5zm0 2.5L6 8v8l6 3.5L18 16V8l-6-4.5zm0 3L8 10v4l4 2 4-2v-4l-4-3.5z"/>
      </svg>`
    ];
    
    // Get consistent values based on hash
    const colorIndex = Math.abs(hash) % colorSchemes.length;
    const iconIndex = Math.abs(hash >> 3) % avatarIcons.length;
    
    return {
      colors: colorSchemes[colorIndex],
      icon: avatarIcons[iconIndex]
    };
  };
  
  // Handle top-up completion
  async function handleTopUpComplete(txId: string, canisterId: string, backendPromise: Promise<any>) {
    // Modal is already closed by MainerTopUpModal
    mainerTopUpModalOpen = false;

    // Add this agent to the loading set
    agentsBeingToppedUp.add(canisterId);
    agentsBeingToppedUp = agentsBeingToppedUp; // Trigger reactivity
    
    // Get mAIner info from agentCanistersInfo via canisterId
    let mainerAgent = findAgentByAddress(canisterId);
    if (!mainerAgent) {
      console.error("Error in handleTopUpComplete: no agent for canisterId");
      // Remove from loading set on error
      agentsBeingToppedUp.delete(canisterId);
      agentsBeingToppedUp = agentsBeingToppedUp;
      return; // TODO - Implementation: decide if the top up should just be credited to the user's first agent then instead (as otherwise the payment is lost)
    };

    // Wait for the backend promise to complete
    try {
      const backendResult = await backendPromise;
      console.log("Backend top-up completed:", backendResult);
      
      if (backendResult && 'Ok' in backendResult) {
        console.log("Top-up completed successfully");
      } else if (backendResult && 'Err' in backendResult) {
        console.error("Backend top-up error:", backendResult.Err);
      }
    } catch (backendError) {
      console.error("Backend promise failed:", backendError);
    }

    // Refresh the list of agents to show updated balances
    try {
      await store.loadUserMainerCanisters();
      // Explicitly reload agents after store update
      agents = await loadAgents();
    } catch (refreshError) {
      console.error("Error refreshing agents after top-up:", refreshError);
    } finally {
      // Remove from loading set after processing
      agentsBeingToppedUp.delete(canisterId);
      agentsBeingToppedUp = agentsBeingToppedUp; // Trigger reactivity
    };

    // Reload flags
    await loadProtocolFlags();
  }

  // Handle celebration trigger from top-up modal
  function handleTopUpCelebration(amount: string, token: string) {
    celebrationAmount = amount;
    celebrationToken = token;
    showCelebration = true;
  }

  // Handle celebration close
  function handleCelebrationClose() {
    showCelebration = false;
    celebrationAmount = "";
    celebrationToken = "";
  }
  
  async function handleSendComplete(txId?: string) {
    mainerPaymentModalOpen = false;
    
    // Store the selected unlocked mAIner before starting creation to prevent null reference
    const selectedMainerForCreation = selectedUnlockedMainer;
    
    // Clear only the specific whitelist mAIner loading state that was selected
    if (selectedMainerForCreation) {
      const mainerIdentifier = selectedMainerForCreation.id || selectedMainerForCreation.name || `unlocked-${selectedMainerForCreation.originalCanisterInfo?.address || Date.now()}`;
      whitelistMainersBeingCreated.delete(mainerIdentifier);
      whitelistMainersBeingCreated = whitelistMainersBeingCreated; // Trigger reactivity
    }
    
    // Set the creation process as started using store
    store.startMainerCreation();
    
    // Start the staged creation process
    // Step 1: Begin registration
    if (selectedMainerForCreation) {
      addProgressMessage("Creating whitelist mAIner...");
      await handleWhitelistMainerCreation(txId, selectedMainerForCreation);
    } else {
      addProgressMessage("Registering new mAIner...");
      
      // Check which backend methods are available and use the appropriate flow
      if (typeof $store.gameStateCanisterActor.createUserMainerAgent === 'function') {
        // Use the full creation flow with all backend methods
        await handleFullMainerCreation(txId);
      } else {
        addProgressMessage("Backend methods not available for mAIner creation");
        store.completeMainerCreation();
      }
    }
    
    // Reset selected unlocked mAIner
    selectedUnlockedMainer = null;

    // Reload flags
    await loadProtocolFlags();
  };

  async function loadProtocolFlags() {
    try {
      isProtocolActiveFlag = await getIsProtocolActive();
      isMainerCreationStoppedFlag = await getIsMainerCreationStopped(modelType);
      isWhitelistPhaseActiveFlag = await getIsWhitelistPhaseActive();
      isPauseWhitelistMainerCreationFlag = await getPauseWhitelistMainerCreationFlag();
    } catch (error) {
      console.error("Error loading protocol flags:", error);
      // Set safe defaults
      isProtocolActiveFlag = true;
      isMainerCreationStoppedFlag = true;
      isWhitelistPhaseActiveFlag = false;
      isPauseWhitelistMainerCreationFlag = true;
      // Retry
      setTimeout(async () => {
        await loadProtocolFlags();
      }, 2000);
    } finally {
      // Set loading to false after flags are loaded (whether successful or not)
      protocolFlagsLoading = false;
    };    
  };

  async function handleWhitelistMainerCreation(txId?: string, selectedMainer?: any) {
    try {
      addProgressMessage("Preparing whitelist mAIner creation...");
      
      // Validate input data for whitelist creation
      if (!txId) {
        throw new Error("No transaction ID provided for whitelist mAIner creation");
      }
      
      if (!selectedMainer) {
        throw new Error("No unlocked mAIner selected");
      }
      
      if (!$store.principal) {
        throw new Error("User principal not available");
      }
      
      // Use the new WhitelistMainerCreationInput structure for whitelistCreateUserMainerAgent
      const originalCanisterInfo = selectedMainer.originalCanisterInfo;
        
        // Build the WhitelistMainerCreationInput with all required fields
        let whitelistMainerCreationInput = {
          address: originalCanisterInfo.address || "",
          canisterType: originalCanisterInfo.canisterType,
          createdBy: originalCanisterInfo.createdBy,
          creationTimestamp: originalCanisterInfo.creationTimestamp,
          mainerConfig: originalCanisterInfo.mainerConfig,
          ownedBy: originalCanisterInfo.ownedBy,
          owner: [$store.principal] as [] | [Principal], // Set current user as new owner
          paymentTransactionBlockId: BigInt(txId),
          status: originalCanisterInfo.status,
          subnet: originalCanisterInfo.subnet || "",
        };
        
        // Call whitelistCreateUserMainerAgent for whitelist creation (now deployed!)
        let unlockUserMainerAgentResponse = await $store.gameStateCanisterActor.whitelistCreateUserMainerAgent(whitelistMainerCreationInput);
      
      if ('Ok' in unlockUserMainerAgentResponse) {
        addProgressMessage("Whitelist mAIner unlocked successfully!");
        
        // Step 2: Create controller
        addProgressMessage("Creating mAIner controller...");
        let spinUpMainerControllerCanisterResponse = await $store.gameStateCanisterActor.spinUpMainerControllerCanister(unlockUserMainerAgentResponse.Ok);
        
        if ('Ok' in spinUpMainerControllerCanisterResponse) {
          addProgressMessage("Controller created successfully!");
          
          // Step 3: Set up LLM if needed (same as normal flow)
          // Check if this is an Own type mAIner for LLM setup
          const isOwnType = selectedMainer.mainerType === 'Own' || 
                          (selectedMainer.originalCanisterInfo?.canisterType?.MainerAgent && 
                           'Own' in selectedMainer.originalCanisterInfo.canisterType.MainerAgent) ||
                          (whitelistMainerCreationInput.mainerConfig.mainerAgentCanisterType && 'Own' in whitelistMainerCreationInput.mainerConfig.mainerAgentCanisterType);
          
          if (isOwnType) {
            addProgressMessage("Starting LLM environment setup in the background...");
            
            // Trigger LLM setup without awaiting it
            $store.gameStateCanisterActor.setUpMainerLlmCanister(spinUpMainerControllerCanisterResponse.Ok)
              .catch((error) => {
                console.error("Error triggering LLM setup:", error);
              });
            
            addProgressMessage("LLM setup will continue in the background (it may take several minutes to complete)");
          }
          
          // Step 4: Final configuration
          addProgressMessage("Configuring mAIner parameters...");
          // TODO: set default cycle burn rate, start mAIner's timer (if not done yet by backend)

          // Step 5: Completion - Match exact timing as regular creation
          setTimeout(() => {
            addProgressMessage("mAIner successfully created!", true);
            setTimeout(() => {
              // Refresh the list of agents to show the newly created one
              store.loadUserMainerCanisters().then(() => {
                // Reload agents to get the updated list
                loadAgents().then((updatedAgents) => {
                  agents = updatedAgents;
                  // Wait for the reactive update to complete, then open the first mAIner
                  setTimeout(() => {
                    // Force open the first mAIner accordion (newest one since we reverse the order)
                    if (agents.length > 0) {
                      const firstAgent = agents[0];
                      const sanitizedId = firstAgent.id.replace(/[^a-zA-Z0-9-_]/g, '_');
                      const content = document.getElementById(`content-${sanitizedId}`);
                      const icon = document.getElementById(`icon-${sanitizedId}`);
                      
                      if (content && icon) {
                        content.classList.add('accordion-open');
                        icon.style.transform = 'rotate(0deg)';
                      }
                    }
                    // Reset the terminal after opening the accordion
                    setTimeout(() => {
                      store.completeMainerCreation();
                    }, 4000);
                  }, 1000); // Increased timeout for better reliability
                });
              }).catch((error) => {
                console.error("Error refreshing mAIner list:", error);
                addProgressMessage("Warning: mAIner created but list refresh failed. Please refresh manually.");
                store.completeMainerCreation();
              });
            }, 14000);
          }, 9000);
        } else if ('Err' in spinUpMainerControllerCanisterResponse) {
          console.error("Error in spinUpMainerControllerCanister:", spinUpMainerControllerCanisterResponse.Err);
          addProgressMessage("Error creating controller: " + JSON.stringify(spinUpMainerControllerCanisterResponse.Err));
          store.completeMainerCreation();
        }
      } else if ('Err' in unlockUserMainerAgentResponse) {

        
        let errorMessage = "Error unlocking whitelist mAIner: ";
        const err = unlockUserMainerAgentResponse.Err;
        
        if (err && typeof err === 'object') {
          if ('Unauthorized' in err) {
            errorMessage += "You are not authorized to unlock this mAIner. This mAIner may be owned by a different user.";
          } else if ('InvalidId' in err) {
            errorMessage += "Invalid mAIner ID provided.";
          } else if ('ZeroAddress' in err) {
            errorMessage += "Invalid address provided.";
          } else if ('FailedOperation' in err) {
            errorMessage += "The unlock operation failed. Please try again.";
          } else if ('InsuffientCycles' in err) {
            errorMessage += "Insufficient cycles for the operation.";
          } else if ('StatusCode' in err) {
            errorMessage += `Status code error: ${err.StatusCode}`;
          } else if ('Other' in err) {
            errorMessage += `Other error: ${err.Other}`;
          } else {
            // Try to get more details about the error
            const errorKeys = Object.keys(err);
            errorMessage += `Unknown error type. Keys: ${errorKeys.join(', ')}. `;
            errorMessage += `First key value: ${err[errorKeys[0]]}`;
          }
        } else {
          errorMessage += `Unexpected error format: ${err}`;
        }
        
        addProgressMessage(errorMessage);
        store.completeMainerCreation();
      }
    } catch (creationError) {
      console.error("Failed to create whitelist mAIner:", creationError);
      addProgressMessage("Failed to create whitelist mAIner: " + creationError.message);
      store.completeMainerCreation();
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
      subnetCtrl : "",
      subnetLlm : "",
      cyclesForMainer : 0n
    };
    let mainerCreationInput = {
      owner: [$store.principal] as [] | [Principal],
      paymentTransactionBlockId: BigInt(txId),
      mainerConfig,
    };
    try {
      let createUserMainerAgentResponse = await $store.gameStateCanisterActor.createUserMainerAgent(mainerCreationInput);
      
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
            addProgressMessage("mAIner successfully created!", true);
            setTimeout(() => {
              // Refresh the list of agents to show the newly created one
              store.loadUserMainerCanisters().then(() => {
                // Wait for the reactive update to complete, then open the first mAIner (newest one)
                setTimeout(() => {
                  openFirstMainerAccordion();
                  // Reset the terminal after opening the accordion
                  setTimeout(() => {
                    store.completeMainerCreation();
                  }, 4000);
                }, 4000); // Increased timeout for better reliability
              });
            }, 14000);
          }, 9000);
        } else if ('Err' in spinUpMainerControllerCanisterResponse) {
          console.error("Error in spinUpMainerControllerCanister:", spinUpMainerControllerCanisterResponse.Err);
          addProgressMessage("Error creating controller: " + JSON.stringify(spinUpMainerControllerCanisterResponse.Err));
          store.completeMainerCreation();
        };
      } else if ('Err' in createUserMainerAgentResponse) {
        // Handle error response
        console.error("Error in createUserMainerAgent:", createUserMainerAgentResponse.Err);
        addProgressMessage("Error creating mAIner: " + JSON.stringify(createUserMainerAgentResponse.Err));
        store.completeMainerCreation();
      };
    } catch (creationError) {
      console.error("Failed to create mAIner:", creationError);
      addProgressMessage("Failed to create mAIner: " + creationError.message);
      store.completeMainerCreation();
    };
  };

  async function handleSimplifiedMainerCreation(txId?: string) {
    // This method is no longer needed since createUserMainerAgent is available
    // But keeping it for potential future use
    addProgressMessage("Simplified creation flow not implemented");
    store.completeMainerCreation();
  };

  // Helper function to add a progress message with timestamp
  function addProgressMessage(message: string, isComplete = false) {
    store.addMainerCreationProgress(message, isComplete);
  }

  function copyAddress() {
    addressCopied = true;
  };

  async function loadAgents() {
    // The store now provides enriched canister info with status, cycles, etc.
    const enrichedCanistersInfo = agentCanistersInfo;

    // Separate unlocked mAIners from active agents
    const activeAgents = [];
    const unlockedAgents = [];

    enrichedCanistersInfo.forEach((canisterInfo, index) => {
      // Get the correct actor by index (might be null for unlocked mAIners)
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

      // Check if this is an unlocked mAIner
      const isUnlocked = canisterInfo.status && 'Unlocked' in canisterInfo.status;
      
      // Check if this unlocked mAIner is owned by the current user
      const isOwnedByCurrentUser = !canisterInfo.ownedBy || canisterInfo.ownedBy.toString() === $store.principal?.toString();
      
      const mainerData = {
        id: canisterInfo.address || `unlocked-${index}`, // Use index for unlocked without address
        name: isUnlocked ? `Unlocked mAIner ${index + 1}` : `mAIner ${canisterInfo.address?.slice(0, 5) || 'Unknown'}`,
        status: isUnlocked ? "unlocked" : (canisterInfo.uiStatus || "active"),
        burnedCycles: canisterInfo.burnedCycles || 0,
        cycleBalance: canisterInfo.cycleBalance || 0,
        cyclesBurnRate: canisterInfo.cyclesBurnRate || {},
        cyclesBurnRateSetting: canisterInfo.cyclesBurnRateSetting || "Medium",
        mainerType,
        llmCanisters: canisterInfo.llmCanisters || [],
        llmSetupStatus: canisterInfo.llmSetupStatus || '',
        hasError: canisterInfo.hasError || false,
        isUnlocked,
        isOwnedByCurrentUser,
        originalCanisterInfo: canisterInfo, // Store original for whitelist creation
        // NEW: store creation timestamp in milliseconds for easy display
        createdAt: canisterInfo.creationTimestamp ? Number(canisterInfo.creationTimestamp / 1000000n) : null
      };

      if (isUnlocked && isOwnedByCurrentUser) {
        unlockedAgents.push(mainerData);
      } else if (isUnlocked && !isOwnedByCurrentUser) {
        //console.log(`⏭️ Skipping unlocked mAIner ${index + 1} - owned by different user:`, canisterInfo.ownedBy?.toString());
      } else if (!isUnlocked) {
        activeAgents.push(mainerData);
      }
    });

    // Update unlocked mAIners list
    unlockedMainers = unlockedAgents;
    
    // Sort by creation timestamp so newest mAIners appear first
    return activeAgents.sort((a, b) => {
      const nowNs = BigInt(Date.now()) * 1000000n; // current time in nanoseconds approximation
      const tsA: bigint = (a.originalCanisterInfo?.creationTimestamp && a.originalCanisterInfo.creationTimestamp > 0n) ? a.originalCanisterInfo.creationTimestamp : nowNs;
      const tsB: bigint = (b.originalCanisterInfo?.creationTimestamp && b.originalCanisterInfo.creationTimestamp > 0n) ? b.originalCanisterInfo.creationTimestamp : nowNs;
      if (tsA === tsB) return 0;
      // Newest first => larger timestamp comes before smaller one
      return tsA < tsB ? 1 : -1;
    });
  };

  $: {
    // React to changes in agentCanisterActors and agentCanistersInfo
    agentCanisterActors;
    agentCanistersInfo;

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
    
    // Load initial state of flags
    await loadProtocolFlags();
    
    // Retrieve the data from the agents' backend canisters to fill the above agents array dynamically
    agents = await loadAgents();
    
    // Only auto-open create accordion if no agents exist and not in whitelist phase
    // In whitelist phase, show unlocked mAIners instead
    if (agents.length === 0 && !isWhitelistPhaseActive) {
      setTimeout(() => {
        toggleAccordion('create');
      }, 100);
    }
    // Don't auto-open any mAIner accordions by default

    try {
      currentMainerPrice = await getMainerPrice();
      currentWhitelistPrice = await getWhitelistAgentPrice();
    } catch (error) {
      console.error("Error loading prices:", error);
      // Set fallback values if loading fails
      currentMainerPrice = 10;
      currentWhitelistPrice = 5;
    }
  });

  // Watch for changes in agents or auth status - only auto-open create accordion when no agents
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
  }

  // Add refresh balance function
  async function refreshAgentBalance(agent) {
    // Add this agent to the refreshing set
    agentsBeingRefreshed.add(agent.id);
    agentsBeingRefreshed = agentsBeingRefreshed; // Trigger reactivity
    
    try {
      // Refresh the list of agents to show updated balances
      await store.loadUserMainerCanisters();
      // Explicitly reload agents after store update
      agents = await loadAgents();
    } catch (refreshError) {
      console.error("Error refreshing agent balance:", refreshError);
    } finally {
      // Remove from refreshing set after processing
      agentsBeingRefreshed.delete(agent.id);
      agentsBeingRefreshed = agentsBeingRefreshed; // Trigger reactivity
    }
  }

  // Handle modal close without payment completion
  async function handlePaymentModalClose() {
    mainerPaymentModalOpen = false;
    // Clear only the specific mAIner's loading state when modal closes without payment
    if (selectedUnlockedMainer) {
      const mainerIdentifier = selectedUnlockedMainer.id || selectedUnlockedMainer.name || `unlocked-${selectedUnlockedMainer.originalCanisterInfo?.address || Date.now()}`;
      whitelistMainersBeingCreated.delete(mainerIdentifier);
      whitelistMainersBeingCreated = whitelistMainersBeingCreated; // Trigger reactivity
    }
    selectedUnlockedMainer = null;
    // Reload flags
    await loadProtocolFlags();
  };

  // Helper function to format creation date for display
  function formatDate(ms: number | null) {
    if (!ms) return "";
    const date = new Date(ms);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  }

  // Browser-level warning to prevent accidental navigation/refresh during creation
  function handleBeforeUnload(event: BeforeUnloadEvent) {
    if (isCreatingMainer) {
      const message = "mAIner creation is in progress. Leaving now will stop the creation process and you'll need to start over. Are you sure you want to leave?";
      event.preventDefault();
      event.returnValue = message;
      return message;
    }
  }

  // Add/remove beforeunload listener based on creation state
  $: if (typeof window !== 'undefined') {
    if (isCreatingMainer) {
      window.addEventListener('beforeunload', handleBeforeUnload);
    } else {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  }

  // Cleanup on component destroy
  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  });
</script>

<!-- Loading state for protocol flags -->
{#if protocolFlagsLoading}
  <div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-gray-100/50 to-gray-200/50 dark:from-gray-800/50 dark:to-gray-900/50 rounded-t-lg">
    <div class="w-full flex justify-center items-center py-8 px-6 text-gray-600 dark:text-gray-400">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 border-2 border-gray-300/30 border-t-gray-600 dark:border-gray-600/30 dark:border-t-gray-400 rounded-full animate-spin"></div>
        <span class="text-sm font-medium">Loading creation options...</span>
      </div>
    </div>
  </div>
{:else}
  <!-- Create Agent Accordion (only show when not in whitelist phase) -->
  {#if !isWhitelistPhaseActive}
<div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-purple-600/20 to-blue-600/20 dark:from-purple-900/40 dark:to-blue-900/40 rounded-t-lg">
  <button on:click={() => toggleAccordion('create')} class="w-full flex justify-between items-center py-4 sm:py-8 px-4 sm:px-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-sm sm:text-base font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform border border-purple-500/20">
    <span class="flex items-center min-w-0 flex-1">
      <div class="flex-shrink-0 w-6 h-6 sm:w-8 sm:h-8 bg-white/20 rounded-lg flex items-center justify-center mr-2 sm:mr-3 shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="flex flex-col items-start min-w-0">
        <span class="text-base sm:text-lg font-bold truncate">Create new mAIner</span>
        <span class="text-purple-100 text-xs sm:text-xs font-normal hidden sm:block">Start your AI mining journey</span>
      </div>
    </span>
    <span id="icon-create" class="text-white/80 transition-transform duration-300 bg-white/10 rounded-full p-1 flex-shrink-0 ml-2" style="transform: rotate(180deg)">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4 sm:w-5 sm:h-5">
        <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
  <div id="content-create" class="accordion-content bg-white dark:bg-gray-900">
    <div class="text-sm text-gray-700 dark:text-gray-300 space-y-4 p-5 dark:bg-gray-800">
      
    {#if isAuthenticated}
      <ol class="relative mx-2 text-gray-500 dark:text-gray-400 border-s border-gray-200 dark:border-gray-700">                  
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {modelType ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                </svg>
            </span>
            <h3 class="font-medium leading-tight mb-3 dark:text-gray-300">AI Agent type</h3>
            
            <!-- Modern Agent Type Selector -->
            <div class="space-y-3 mb-2">
              <!-- Shared Model Card -->
              <div 
                class="relative border-2 rounded-xl p-3 sm:p-4 cursor-pointer transition-all duration-200 hover:shadow-md {modelType === 'Shared' 
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' 
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-purple-300 dark:hover:border-purple-600'}"
                on:click={() => modelType = 'Shared'}
                on:keydown={(e) => e.key === 'Enter' && (modelType = 'Shared')}
                role="button"
                tabindex="0"
              >
                <!-- Selection indicator -->
                <div class="absolute top-2 sm:top-3 right-2 sm:right-3">
                  {#if modelType === 'Shared'}
                    <div class="w-4 h-4 sm:w-5 sm:h-5 bg-purple-600 rounded-full flex items-center justify-center">
                      <svg class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  {:else}
                    <div class="w-4 h-4 sm:w-5 sm:h-5 border-2 border-gray-300 dark:border-gray-600 rounded-full"></div>
                  {/if}
                </div>

                <div class="flex items-start space-x-3 pr-6 sm:pr-8">
                  <!-- Icon -->
                  <div class="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                  </div>

                  <!-- Content -->
                  <div class="flex-1 min-w-0">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-2 mb-1">
                      <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">mAIner Agent</h4>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 w-fit mt-1 sm:mt-0">
                        Not available
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                      Shared infrastructure with optimized performance
                    </p>
                    <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0 text-xs text-gray-500 dark:text-gray-400">
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                        </svg>
                        <span>{mainerPrice} ICP</span>
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
            </div>
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
            <h3 class="font-medium leading-tight dark:text-gray-300">Create Agent</h3>
        </li>
      </ol>

      <div class="flex flex-col items-stretch sm:items-end">
        <button 
          on:click={createAgent} 
          disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation}
          class="bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-4 py-2 rounded-xl transition-colors mb-2 w-full sm:w-auto sm:mr-2 text-sm sm:text-base"
          class:opacity-50={isCreatingMainer || !isProtocolActive || stopMainerCreation}
          class:cursor-not-allowed={isCreatingMainer || !isProtocolActive || stopMainerCreation}
          use:tooltip={{ 
            text: isCreatingMainer 
              ? "⚠️ mAIner creation in progress! Please wait for it to complete. DO NOT refresh or navigate away - this will stop the creation and you'll need to start over."
              : stopMainerCreation 
                ? "mAIner creation is temporarily disabled due to network capacity"
                : !isProtocolActive 
                  ? "Protocol is currently inactive"
                  : "",
            direction: 'top',
            textSize: 'xs'
          }}
        >
          {#if isCreatingMainer}
            {#if mainerCreationProgress.length > 0 && mainerCreationProgress[0].message.includes("Previous creation")}
              Session on hold
            {:else}
              Creating mAIner...
            {/if}
          {:else}
            Create mAIner Agent
          {/if}
        </button>
      </div>

      <!-- Network Capacity Message Panel -->
      {#if stopMainerCreation && !protocolFlagsLoading}
        <div class="mt-3 relative overflow-hidden bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 dark:from-orange-900/20 dark:via-amber-900/20 dark:to-yellow-900/20 border border-orange-200/60 dark:border-orange-700/60 rounded-xl shadow-sm">
          <!-- Background decorative elements -->
          <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-orange-200/30 to-amber-200/30 dark:from-orange-600/10 dark:to-amber-600/10 rounded-full -translate-y-8 translate-x-8"></div>
          <div class="absolute bottom-0 left-0 w-12 h-12 bg-gradient-to-tr from-yellow-200/30 to-orange-200/30 dark:from-yellow-600/10 dark:to-orange-600/10 rounded-full translate-y-6 -translate-x-6"></div>
          
          <div class="relative p-4">
            <div class="flex items-start space-x-3">
              <!-- Icon -->
              <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-600 dark:from-orange-600 dark:to-amber-700 rounded-lg shadow-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 00-2 2v2m0 0V9a2 2 0 012-2h14a2 2 0 012 2v2M7 7V6a3 3 0 016 0v1"/>
                </svg>
              </div>
              
              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2 mb-3">
                  <h3 class="text-sm font-bold text-orange-900 dark:text-orange-100">Network at full capacity</h3>
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-300 border border-orange-300 dark:border-orange-700">
                    Temporarily unavailable
                  </span>
                </div>
                
                <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-3 border border-orange-200/40 dark:border-orange-700/40 mb-2">
                  <div class="flex items-center space-x-2 text-xs text-orange-600 dark:text-orange-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span class="font-medium">Check our socials for updates: 
                      <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">@onicaiHQ</a> 
                      or 
                      <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">OpenChat</a>
                    </span>
                  </div>
                </div>
                <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-3 border border-orange-200/40 dark:border-orange-700/40 mb-1">
                  <div class="flex items-center space-x-2 text-xs text-orange-600 dark:text-orange-400">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="#4ade80">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
                    </svg>
                    <span class="font-medium">$FUNNAI available at: 
                      <a href="https://app.icpswap.com/swap?input=ryjl3-tyaaa-aaaaa-aaaba-cai&output=vpyot-zqaaa-aaaaa-qavaq-cai" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">ICPSwap</a> 
                      or 
                      <a href="https://www.kongswap.io/stats/vpyot-zqaaa-aaaaa-qavaq-cai" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">KongSwap</a>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Bottom accent line -->
          <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-orange-400 dark:via-orange-500 to-transparent"></div>
        </div>
      {/if}

    {:else}
      <div class="h-full flex">
        <div class="relative overflow-hidden bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 dark:from-blue-600 dark:via-purple-600 dark:to-indigo-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform flex-1 flex flex-col">
          <!-- Background decoration -->
          <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
          
          <div class="relative flex-1 flex items-center justify-center p-4 sm:p-6">
            <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
              <!-- Icon with enhanced styling -->
              <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
                <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              
              <!-- Content section -->
              <div class="space-y-3 sm:space-y-4">
                <div class="flex flex-col items-center text-center space-y-2">
                  <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                    Get Started
                  </div>
                  <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Connect to begin</h3>
                </div>
                
                <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
                  <p class="font-semibold text-base sm:text-lg">🚀 Ready to start AI mining?</p>
                  <p>Connect your wallet to create and manage your mAIners, participate in challenges, and earn rewards through AI competitions.</p>
                </div>
                
                <!-- Features list -->
                <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 border border-white/20 shadow-sm text-left">
                  <div class="space-y-2 text-white/90 text-sm">
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Create and manage AI agents</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Participate in AI challenges</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Earn rewards and tokens</span>
                    </div>
                  </div>
                </div>
                
                <!-- Enhanced button -->
                <div class="pt-3">
                  <button 
                    on:click={toggleLoginModal} 
                    class="group relative inline-flex items-center justify-center px-6 py-3 text-base font-bold text-blue-600 bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-102 border-2 border-white/20 backdrop-blur-sm"
                  >
                    <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                    </svg>
                    Connect Wallet
                    <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-100 to-purple-100 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                  </button>
                </div>
                
                <!-- Additional info -->
                <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
                  <div class="flex items-center justify-center space-x-2">
                    <span class="text-sm">🔒</span>
                    <span class="font-medium">Secure connection via Internet Identity or NFID</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}
    </div>
  </div>
</div>
{/if}

<!-- Whitelist mAIners Section (only show when in whitelist phase) -->
{#if isWhitelistPhaseActive && isAuthenticated}
  <!-- Case 1: User has unlocked mAIners ready to create -->
  {#if unlockedMainers.length > 0}
    <div class="mb-4">
      <div class="relative overflow-hidden bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 dark:from-amber-600 dark:via-yellow-600 dark:to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform">
        <!-- Background decoration -->
        <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <!-- Left side content -->
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-3">
                <div class="flex-shrink-0 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-sm">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <div>
                <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                      Limited Time
                    </div>
                  <h3 class="text-lg sm:text-xl font-bold text-white drop-shadow-sm">Whitelist phase active</h3>
                  <div class="flex items-center space-x-2 mt-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                      Special pricing
                    </span>
                    {#if unlockedMainers.length > 0}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-white backdrop-blur-sm">
                        {unlockedMainers.length} Available
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
              
              <div class="text-white/90 text-sm leading-relaxed">
                <p class="font-medium mb-2">🎉 Exclusive whitelist pricing now available!</p>
                <p>Create your mAIner from the unlocked options below for just <span class="font-bold text-white">{currentWhitelistPrice || 5} ICP</span> instead of the regular price of <span class="line-through opacity-75">{currentMainerPrice || 10} ICP</span>.</p>
                {#if unlockedMainers.length > 0}
                  <p class="text-xs text-white/80 mt-2">💡 <span class="font-medium">Note:</span> More unlocked mAIners may become available as others are created. Check back periodically during the whitelist phase.</p>
                {/if}
              </div>
            </div>
            
            <!-- Right side - Savings highlight -->
            <div class="flex-shrink-0 sm:ml-6">
              <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center border border-white/20 shadow-lg">
                <div class="text-2xl sm:text-3xl font-bold text-white mb-1">
                  {Math.round(((currentMainerPrice || 10) - (currentWhitelistPrice || 5)) / (currentMainerPrice || 10) * 100)}%
                </div>
                <div class="text-xs sm:text-sm text-white/80 font-medium uppercase tracking-wide">
                  Savings
                </div>
                <div class="text-xs text-white/70 mt-1">
                  Save {((currentMainerPrice || 10) - (currentWhitelistPrice || 5)).toFixed(1)} ICP
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unlocked mAIners List -->
    <div class="space-y-3">
      {#each unlockedMainers as unlockedMainer, index}
        <div class="relative overflow-hidden bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 dark:from-amber-900/20 dark:via-yellow-900/20 dark:to-orange-900/20 border border-amber-200/60 dark:border-amber-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-0.5">
          <!-- Background decorative elements -->
          <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-yellow-200/30 to-amber-200/30 dark:from-yellow-600/10 dark:to-amber-600/10 rounded-full -translate-y-8 translate-x-8"></div>
          <div class="absolute bottom-0 left-0 w-12 h-12 bg-gradient-to-tr from-orange-200/30 to-yellow-200/30 dark:from-orange-600/10 dark:to-yellow-600/10 rounded-full translate-y-6 -translate-x-6"></div>
          
          <div class="relative p-3 md:p-4">
            <div class="flex flex-col space-y-3 xl:flex-row xl:items-center xl:justify-between xl:space-y-0">
              <!-- Left side - mAIner info -->
              <div class="flex items-start space-x-3 min-w-0 flex-1">
                <!-- Premium icon with glow effect -->
                <div class="flex-shrink-0 w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-yellow-400 to-amber-500 dark:from-yellow-500 dark:to-amber-600 rounded-lg shadow-lg flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
                
                <!-- mAIner details -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-col space-y-2">
                    <h3 class="font-semibold text-sm md:text-base text-amber-900 dark:text-amber-100 truncate">
                      {unlockedMainer.name}
                    </h3>
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                        Unlocked
                      </span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 border border-green-300 dark:border-green-700">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        Whitelisted
                      </span>
                    </div>
                  </div>
                  
                  <!-- Type and special pricing info -->
                  <div class="flex flex-col space-y-1 mt-2 lg:flex-row lg:items-center lg:space-x-4 lg:space-y-0">
                    <div class="flex items-center space-x-1 text-xs text-amber-700 dark:text-amber-300">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                      </svg>
                      <span class="font-medium">Quick start</span>
                    </div>
                    <div class="flex items-center space-x-1 text-xs text-emerald-700 dark:text-emerald-300">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                      </svg>
                      <span class="font-medium">Only {currentWhitelistPrice || 5} ICP</span>
                      <span class="line-through text-xs opacity-60">{currentMainerPrice || 10} ICP</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Right side - Action button -->
              <div class="flex-shrink-0 xl:ml-4">
                <button
                  on:click={() => createWhitelistAgent(unlockedMainer)}
                  disabled={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class="group relative inline-flex items-center justify-center px-4 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-amber-500 to-yellow-500 dark:from-amber-600 dark:to-yellow-600 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 border border-amber-400/50 dark:border-amber-500/50 w-full xl:w-auto"
                  class:opacity-50={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:cursor-not-allowed={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:transform-none={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:hover:scale-100={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                >
                  {#if whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                    <div class="flex items-center space-x-2">
                      <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      <span class="text-xs md:text-sm">Processing...</span>
                    </div>
                  {:else}
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                      <span class="text-xs md:text-sm">Create Now</span>
                    </div>
                  {/if}
                  <div class="absolute inset-0 rounded-lg bg-gradient-to-r from-yellow-100 to-amber-100 dark:from-yellow-600/20 dark:to-amber-600/20 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                </button>
              </div>
            </div>
            
            <!-- Bottom accent line -->
            <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-amber-400 dark:via-amber-500 to-transparent"></div>
          </div>
        </div>
      {/each}
    </div>
  <!-- Case 2: User has already created mAIners (whitelist participant) -->
  {:else if totalMainers > 0}
    <div class="mb-4">
      <div class="relative overflow-hidden bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 dark:from-emerald-600 dark:via-teal-600 dark:to-cyan-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform">
        <!-- Background decoration -->
        <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
            <!-- Icon with enhanced styling -->
            <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
              <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            
            <!-- Content section -->
            <div class="space-y-3 sm:space-y-4">
              <div class="flex flex-col items-center text-center space-y-2">
                <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                  Whitelist Member
                </div>
                <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Welcome, early supporter! 🎉</h3>
              </div>
              
              <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
                <p class="font-semibold text-base sm:text-lg">✨ You're part of the exclusive whitelist community!</p>
                <p>You successfully claimed your whitelist mAIner(s). Manage your existing mAIners below or check for additional whitelist opportunities.</p>
              </div>
              
              <!-- Status indicator -->
              <div class="pt-3">
                <div class="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl border border-white/30 shadow-sm">
                  <svg class="w-5 h-5 mr-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span class="text-white font-semibold">Whitelist Access Activated</span>
                </div>
              </div>
              
              <!-- Additional info -->
              <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
                <div class="flex items-center justify-center space-x-2">
                  <span class="text-sm">🏆</span>
                  <span class="font-medium">You're part of the exclusive whitelist community with {totalMainers} mAIner{totalMainers === 1 ? '' : 's'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  <!-- Case 3: User has no whitelisted principals - awaiting public sale -->
  {:else}
    <div class="mb-4">
      <div class="relative overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-800 dark:via-blue-900/20 dark:to-indigo-900/20 border border-slate-200/60 dark:border-slate-700/60 rounded-xl shadow-sm">
        <!-- Background decorative elements -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-200/20 to-indigo-200/20 dark:from-blue-600/10 dark:to-indigo-600/10 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-purple-200/20 to-pink-200/20 dark:from-purple-600/10 dark:to-pink-600/10 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-6 sm:p-8 text-center">
          <!-- Enhanced icon with background -->
          <div class="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-800/30 dark:to-indigo-800/30 rounded-2xl shadow-sm border border-blue-200/50 dark:border-blue-700/50 mx-auto mb-4">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
          
          <!-- Main heading temp change: Whitelist phase complete! 🎉 --> 
          <h3 class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-slate-100 mb-3">
            Whitelist phase active! 🎉
          </h3>
          
          <!-- Description temp change: All whitelist mAIners have been successfully claimed by early supporters. -->
          <div class="space-y-3 mb-6">
            <p class="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed max-w-md mx-auto">
              Claim your whitelist spots and become an early mAIner.
            </p>
            
            <!-- Public sale announcement temp change: Public Sale Opens June 29 -->
            <div class="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border border-emerald-200/60 dark:border-emerald-700/60 rounded-lg p-4 max-w-sm mx-auto">
              <div class="flex items-center justify-center space-x-2 mb-2">
                <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="text-sm font-semibold text-emerald-800 dark:text-emerald-200">Whitelist Sale Opens</span>
              </div>
              <div class="text-2xl sm:text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-1">
                June 28
              </div>
              <p class="text-xs text-emerald-600 dark:text-emerald-400">
                Mark your calendar!
              </p>
            </div>
          </div>
          
          <!-- Call to action -->
          <div class="space-y-3">
            <p class="text-sm text-slate-500 dark:text-slate-400">
              🚀 <span class="font-medium">Coming soon:</span> Create your own mAIner and start AI mining!
            </p>
            
            <!-- Notification signup hint -->
            <div class="inline-flex items-center space-x-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-full border border-blue-200 dark:border-blue-700">
                                              <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
                </svg>

              <span class="text-xs font-medium text-blue-700 dark:text-blue-300">Stay tuned for launch updates</span>
            </div>
          </div>
          
          <!-- Debug info - only show in development -->
          {#if import.meta.env.DEV}
            <details class="mt-4 text-left">
              <!-- <summary class="text-xs text-slate-400 dark:text-slate-500 cursor-pointer hover:text-slate-600 dark:hover:text-slate-400">Debug Info</summary> -->
              <div class="mt-2 p-2 bg-slate-100 dark:bg-slate-800 rounded text-xs text-slate-500 dark:text-slate-400">
                Total mAIners loaded: {agentCanistersInfo.length}<br>
                Unlocked for you: {unlockedMainers.length}<br>
                Total mAIners: {totalMainers}
              </div>
            </details>
          {/if}
        </div>
      </div>
    </div>
  {/if}
{:else if isWhitelistPhaseActive && !isAuthenticated}
  <div class="mb-4 h-full">
    <div class="relative overflow-hidden bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 dark:from-amber-600 dark:via-yellow-600 dark:to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform h-full">
      <!-- Background decoration -->
      <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
      <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
      <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
      
      <div class="relative h-full flex items-center justify-center p-4 sm:p-6">
        <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
          <!-- Icon with enhanced styling -->
          <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          
          <!-- Content section -->
          <div class="space-y-3 sm:space-y-4">
            <div class="flex flex-col items-center text-center space-y-2">
              <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                Limited time
              </div>
              <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Whitelist phase active</h3>
            </div>
            
            <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
              <p class="font-semibold text-base sm:text-lg">🎉 Exclusive access available!</p>
              <p>Connect your wallet to see available whitelist mAIners and take advantage of special pricing.</p>
            </div>
            
            <!-- Enhanced button -->
            <div class="pt-3">
              <button 
                on:click={toggleLoginModal} 
                class="group relative inline-flex items-center justify-center px-6 py-3 text-base font-bold text-amber-600 bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-102 border-2 border-white/20 backdrop-blur-sm"
              >
                <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                </svg>
                Connect Wallet
                <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-100 to-yellow-100 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              </button>
            </div>
            
            <!-- Additional info -->
            <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
              <div class="flex items-center justify-center space-x-2">
                <span class="text-sm">💡</span>
                <span class="font-medium">Get early access to mAIners with exclusive whitelist pricing</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Warning Banner - Don't refresh/navigate during creation -->
{#if isCreatingMainer}
  <div class="mt-4 relative overflow-hidden bg-gradient-to-r from-red-500 via-orange-500 to-red-500 dark:from-red-600 dark:via-orange-600 dark:to-red-600 rounded-xl shadow-lg border-2 border-red-400/50 dark:border-red-500/50 animate-pulse">
    <!-- Background decoration -->
    <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
    <div class="absolute top-0 right-0 w-16 h-16 bg-white/5 rounded-full -translate-y-8 translate-x-8"></div>
    <div class="absolute bottom-0 left-0 w-12 h-12 bg-white/5 rounded-full translate-y-6 -translate-x-6"></div>
    
    <div class="relative p-3 sm:p-4">
      <div class="flex items-start space-x-3">
        <!-- Warning icon -->
        <div class="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-white/20 backdrop-blur-sm rounded-xl shadow-sm flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:h-6 sm:w-6 text-white animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
        </div>
        
        <!-- Warning content -->
        <div class="flex-1 min-w-0">
          <div class="flex flex-col space-y-2">
                         <h3 class="text-sm sm:text-base font-bold text-white drop-shadow-sm">⚠️ IMPORTANT: Do NOT refresh or navigate away!</h3>
             <div class="text-white/90 text-xs sm:text-sm leading-relaxed">
               <p class="font-semibold mb-1">Your mAIner is being created right now.</p>
               <p>🚫 <span class="font-medium">DO NOT refresh this page or navigate away</span> - this will stop the creation process and you'll need to start over.</p>
               <p class="mt-1">✅ Please keep this tab open and wait for the process to complete (~1 minute).</p>
             </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bottom accent line with pulse animation -->
    <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/60 to-transparent animate-pulse"></div>
  </div>
{/if}

<!-- Terminal-style progress component (shows for both regular and whitelist creation) -->
{#if isCreatingMainer}
  <div class="mt-3 bg-gray-900 text-green-400 font-mono text-xs sm:text-sm rounded-lg p-2 sm:p-3 border border-gray-700 overflow-hidden">
    <div class="flex items-center justify-between mb-2 border-b border-gray-700 pb-2">
      <div class="text-gray-300 text-xs">mAIner Creation Progress</div>
      <div class="flex items-center">
        <div class="h-3 w-3 sm:h-4 sm:w-4 border-2 border-gray-400/30 border-t-green-400 rounded-full animate-spin"></div>
      </div>
    </div>
    <div class="h-32 sm:h-40 overflow-y-auto terminal-scroll">
      {#each mainerCreationProgress as progress}
        <div class="flex mb-1 items-start" class:text-green-300={progress.complete}>
          <span class="text-gray-500 mr-1 sm:mr-2 text-xs hidden sm:inline">[{progress.timestamp}]</span>
          <span class="flex-1 text-xs sm:text-sm break-words">{progress.message}</span>
          {#if progress.complete}
            <span class="text-green-500 ml-1">✓</span>
          {/if}
        </div>
      {/each}
      {#if mainerCreationProgress.length > 0 && !mainerCreationProgress[mainerCreationProgress.length - 1].complete}
        <div class="blink">_</div>
      {/if}
    </div>
  </div>
{/if}

{#if loginModalOpen}
  <LoginModal toggleModal={toggleLoginModal} />
{/if}

{#if mainerPaymentModalOpen}
  <MainerPaymentModal 
    isOpen={mainerPaymentModalOpen}
    onClose={handlePaymentModalClose}
    onSuccess={handleSendComplete}
    {modelType}
    {selectedUnlockedMainer}
    {isWhitelistPhaseActive}
  />
{/if}

{#if mainerTopUpModalOpen}
  <MainerTopUpModal 
    isOpen={mainerTopUpModalOpen}
    onClose={() => mainerTopUpModalOpen = false}
    onSuccess={handleTopUpComplete}
    onCelebration={handleTopUpCelebration}
    canisterId={selectedCanister.id}
    canisterName={selectedCanister.name}
  />
{/if}

{#if totalMainers > 0}
  <FlockOverview 
    {totalMainers}
    {activeMainers}
    {inactiveMainers}
    {lowBurnRateMainers}
    {mediumBurnRateMainers}
    {highBurnRateMainers}
  />
{/if}

<!-- Existing Agents -->
{#each agents as agent, index}
  {#if agent && agent.id}
    {@const sanitizedId = agent.id.replace(/[^a-zA-Z0-9-_]/g, '_')}
    {@const identity = getMainerVisualIdentity(agent.id)}
    <div class="border-b border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 mb-2 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-all duration-300" class:opacity-75={agent.status === 'inactive'}>
      <button 
        on:click={() => toggleAccordion(agent.id)} 
        class="w-full relative overflow-hidden bg-gradient-to-r {identity.colors.bg} hover:{identity.colors.bgHover} {identity.colors.border} border-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform group"
      >
        <!-- Background decorative elements -->
        <div class="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-white/5"></div>
        <div class="absolute top-0 right-0 w-32 h-32 {identity.colors.accent} rounded-full -translate-y-16 translate-x-16 opacity-30"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 {identity.colors.accent} rounded-full translate-y-12 -translate-x-12 opacity-20"></div>
        
        <div class="relative flex items-center py-3 sm:py-4 px-4 sm:px-6">
          <!-- Left section: Avatar and Info -->
          <div class="flex items-center space-x-3 sm:space-x-4 min-w-0 flex-1">
            <!-- Unique avatar with visual identity and name -->
            <div class="relative flex-shrink-0 flex flex-col items-center">
              <!-- Avatar container with glow effect -->
              <div class="w-12 h-12 sm:w-16 sm:h-16 {identity.colors.accent} backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center border-2 border-white/20 group-hover:scale-105 transition-transform duration-300">
                <div class="w-6 h-6 sm:w-8 sm:h-8 {identity.colors.icon}">
                  {@html identity.icon}
                </div>
              </div>
              
              <!-- mAIner number badge -->
              <div class="absolute -top-1 -right-1 w-6 h-6 sm:w-7 sm:h-7 bg-white/90 backdrop-blur-sm rounded-full shadow-lg flex items-center justify-center border-2 border-white/50">
                <span class="text-xs sm:text-sm font-bold text-gray-800">#{totalMainers - index}</span>
              </div>
              
              <!-- Status indicator dot -->
              <div class="absolute -bottom-1 -left-1 w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
                <div class={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${agent.status === 'active' ? 'bg-green-400' : 'bg-red-400'} animate-pulse`}></div>
              </div>
            </div>
            
            <!-- mAIner info -->
            <div class="flex flex-col items-start min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-1 sm:gap-2 mb-1">
                <!-- Status badge -->
                <span class={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm border ${agent.status === 'active' 
                  ? 'bg-green-100/80 text-green-800 border-green-300/50' 
                  : 'bg-red-100/80 text-red-800 border-red-300/50'}`}>
                  <div class={`w-2 h-2 rounded-full mr-1 ${agent.status === 'active' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  {agent.status}
                </span>
                
                <!-- Daily Burn Rate badge (only show if active) -->
                {#if agent.status === 'active' && agent.cyclesBurnRateSetting}
                  {@const burnRateColors = {
                    'Low': 'bg-green-100/80 text-green-800 border-green-300/50',
                    'Medium': 'bg-yellow-100/80 text-yellow-800 border-yellow-300/50', 
                    'High': 'bg-red-100/80 text-red-800 border-red-300/50'
                  }}
                  <span class={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm border ${burnRateColors[agent.cyclesBurnRateSetting] || 'bg-gray-100/80 text-gray-800 border-gray-300/50'}`}>
                    🔥 {agent.cyclesBurnRateSetting}
                  </span>
                {/if}
                
                <!-- LLM setup status badge -->
                {#if agent.mainerType === 'Own' && agent.llmSetupStatus === 'inProgress'}
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100/80 text-yellow-800 border border-yellow-300/50 backdrop-blur-sm">
                    <svg class="w-3 h-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke-width="4" stroke-opacity="0.25"/>
                      <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" stroke-opacity="0.75"/>
                    </svg>
                    LLM Setup
                  </span>
                {/if}
                
                <!-- Cycles warning -->
                {#if agent.status === 'inactive'}
                  <span 
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100/80 text-red-800 border border-red-300/50 backdrop-blur-sm cursor-help"
                    use:tooltip={{ 
                      text: "You still have some cycles, but not enough to keep going. Please top up to continue.",
                      direction: 'top',
                      textSize: 'xs'
                    }}
                  >
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                    </svg>
                    Needs Cycles
                  </span>
                {/if}
              </div>
              
              <!-- Cycles Balance preview -->
              <div class="text-sm {identity.colors.text} opacity-90 truncate max-w-full mt-1">
                {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 2, false)} TCYCLES
              </div>
              {#if agent.createdAt}
                <div class="text-xs {identity.colors.text} opacity-60">
                  Created: {formatDate(agent.createdAt)}
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Right section: Expand indicator -->
          <div class="flex-shrink-0 ml-4">
            <!-- Agent name  -->
            <div class="mb-2 px-2 py-0.5 bg-white/80 backdrop-blur-sm rounded-md shadow-sm border border-white/40 max-w-[80px] sm:max-w-[100px]">
              <span class="text-xs font-bold text-gray-800 truncate block text-center">
                🦜 {agent.name.replace('mAIner ', '')}
              </span>
            </div>
            <div class="w-full h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center border border-white/30 shadow-sm group-hover:bg-white/30 transition-all duration-300">
              <span id="icon-{sanitizedId}" class="{identity.colors.text} transition-transform duration-300 group-hover:scale-110" style="transform: rotate(180deg)">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4 sm:w-5 sm:h-5">
                  <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>
          </div>
        </div>
        
        <!-- Bottom accent line with pulse animation for active mAIners -->
        <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/50 to-transparent {agent.status === 'active' ? 'animate-pulse' : ''}"></div>
      </button>
      <div id="content-{sanitizedId}" class="accordion-content">
        <div class="pb-3 sm:pb-5 text-xs sm:text-sm text-gray-700 dark:text-gray-300 p-3 sm:p-4 bg-gray-50 dark:bg-gray-800">
          <!-- Enhanced Canister Information Section -->
          <div class="flex flex-col space-y-2 mb-2">
            <div class="relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 border border-blue-200/60 dark:border-blue-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
              <!-- Background decorative elements -->
              <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-200/30 to-indigo-200/30 dark:from-blue-600/10 dark:to-indigo-600/10 rounded-full -translate-y-10 translate-x-10"></div>
              <div class="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-purple-200/30 to-blue-200/30 dark:from-purple-600/10 dark:to-blue-600/10 rounded-full translate-y-8 -translate-x-8"></div>
              
              <div class="relative p-4 sm:p-5">
                <!-- Header Section -->
                <div class="flex items-center space-x-3 mb-4">
                  <!-- Enhanced icon with gradient background -->
                  <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
                    </svg>
                  </div>
                  
                  <!-- Title and subtitle -->
                  <div class="flex flex-col">
                    <h2 class="text-sm sm:text-base font-bold text-blue-900 dark:text-blue-100">Canister Information</h2>
                    <p class="text-xs text-blue-700 dark:text-blue-300">Internet Computer infrastructure details</p>
                  </div>
                </div>

                <!-- Controller ID Section -->
                <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-blue-200/40 dark:border-blue-700/40 shadow-sm">
                  <div class="flex flex-col space-y-3">
                    <!-- Controller ID Header -->
                    <div class="flex items-center space-x-2">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                      </svg>
                      <span class="text-sm font-medium text-blue-900 dark:text-blue-100">Controller ID</span>
                    </div>
                    
                    <!-- Enhanced Controller ID Link -->
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div class="flex-1 min-w-0">
                        <div class="font-mono text-xs text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-900/30 px-3 py-2 rounded-lg border border-blue-200/50 dark:border-blue-700/50">
                          <span class="break-all">{agent.id}</span>
                        </div>
                      </div>
                      
                      <a 
                        href="https://dashboard.internetcomputer.org/canister/{agent.id}" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        class="group relative inline-flex items-center justify-center px-4 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 border border-blue-400/50 dark:border-blue-500/50 w-full sm:w-auto"
                      >
                        <div class="flex items-center space-x-2">
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                          </svg>
                          <span>View on Dashboard</span>
                        </div>
                        <div class="absolute inset-0 rounded-lg bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-600/20 dark:to-blue-600/20 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                      </a>
                    </div>
                    
                    <!-- Additional info -->
                    <div class="pt-2 border-t border-blue-200/50 dark:border-blue-700/50">
                      <div class="flex items-center space-x-2 text-xs text-blue-600/80 dark:text-blue-400/80">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <span>Canister runs on Internet Computer Protocol</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Bottom accent line -->
              <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 dark:via-blue-500 to-transparent"></div>
            </div>
            
                
                <!-- For Own type mAIners, show LLM information or setup status -->
                {#if agent.mainerType === 'Own'}
                  <div class="relative overflow-hidden bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50 dark:from-purple-900/20 dark:via-indigo-900/20 dark:to-blue-900/20 border border-purple-200/60 dark:border-purple-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 mt-2">
                    <!-- Background decorative elements -->
                    <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-200/30 to-indigo-200/30 dark:from-purple-600/10 dark:to-indigo-600/10 rounded-full -translate-y-8 translate-x-8"></div>
                    <div class="absolute bottom-0 left-0 w-12 h-12 bg-gradient-to-tr from-indigo-200/30 to-purple-200/30 dark:from-indigo-600/10 dark:to-purple-600/10 rounded-full translate-y-6 -translate-x-6"></div>
                    
                    <div class="relative p-4 sm:p-5">
                      <!-- Header Section for LLM -->
                      <div class="flex items-center space-x-3 mb-4">
                        <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 dark:from-purple-600 dark:to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                          </svg>
                        </div>
                        <div class="flex flex-col">
                          <h3 class="text-sm sm:text-base font-bold text-purple-900 dark:text-purple-100">LLM Environment</h3>
                          <p class="text-xs text-purple-700 dark:text-purple-300">Private AI language model infrastructure</p>
                        </div>
                      </div>

                      <!-- Show LLM setup status if in progress -->
                      {#if agent.llmSetupStatus === 'inProgress'}
                        <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-yellow-200/60 dark:border-yellow-700/60 shadow-sm mb-4">
                          <div class="flex items-start space-x-3">
                            <svg class="animate-spin h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <div class="flex-1">
                              <p class="text-sm font-medium text-yellow-800 dark:text-yellow-300 mb-1">
                                LLM Setup in Progress
                              </p>
                              <p class="text-xs text-yellow-700 dark:text-yellow-400 leading-relaxed">
                                Setting up your private AI environment. This may take several minutes and will continue in the background. You can use shared LLMs in the meantime.
                              </p>
                            </div>
                          </div>
                        </div>
                      {/if}
                      
                      <!-- LLM Canisters Section -->
                      <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-purple-200/40 dark:border-purple-700/40 shadow-sm">
                        <div class="flex items-center space-x-2 mb-3">
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 00-2 2v2m0 0V9a2 2 0 012-2h14a2 2 0 012 2v2M7 7V6a3 3 0 016 0v1"/>
                          </svg>
                          <span class="text-sm font-medium text-purple-900 dark:text-purple-100">Attached LLMs</span>
                        </div>
                        
                        {#if agent.llmCanisters && agent.llmCanisters.length > 0}
                          <div class="space-y-3">
                            {#each agent.llmCanisters as llmCanister, i}
                              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-3 bg-purple-50/50 dark:bg-purple-900/20 rounded-lg border border-purple-200/30 dark:border-purple-700/30">
                                <div class="flex items-center space-x-2">
                                  <div class="w-6 h-6 bg-purple-100 dark:bg-purple-800/40 rounded-md flex items-center justify-center">
                                    <span class="text-xs font-bold text-purple-600 dark:text-purple-400">{i+1}</span>
                                  </div>
                                  <div class="font-mono text-xs text-purple-700 dark:text-purple-300 bg-purple-100/50 dark:bg-purple-900/30 px-2 py-1 rounded border border-purple-200/50 dark:border-purple-700/50">
                                    <span class="break-all">{llmCanister}</span>
                                  </div>
                                </div>
                                <a 
                                  href="https://dashboard.internetcomputer.org/canister/{llmCanister}" 
                                  target="_blank" 
                                  rel="noopener noreferrer" 
                                  class="group inline-flex items-center justify-center px-3 py-1.5 text-xs font-medium text-purple-700 dark:text-purple-300 bg-purple-100/60 dark:bg-purple-800/30 hover:bg-purple-200/70 dark:hover:bg-purple-700/40 rounded-md border border-purple-300/50 dark:border-purple-600/50 transition-all duration-200 hover:scale-105 hover:shadow-sm w-full sm:w-auto"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 mr-1.5 group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                                  </svg>
                                  View LLM
                                </a>
                              </div>
                            {/each}
                          </div>
                        {:else}
                          <div class="text-center py-4">
                            {#if agent.llmSetupStatus === 'inProgress'}
                              <div class="flex items-center justify-center space-x-3 text-yellow-600 dark:text-yellow-400">
                                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span class="text-sm font-medium">Setting up LLM environment...</span>
                              </div>
                            {:else}
                              <div class="text-gray-500 dark:text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
                                </svg>
                                <p class="text-sm font-medium mb-1">No LLMs attached yet</p>
                                <p class="text-xs">Your private AI environment is being prepared</p>
                              </div>
                            {/if}
                          </div>
                        {/if}
                      </div>
                    </div>
                    
                    <!-- Bottom accent line -->
                    <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-400 dark:via-purple-500 to-transparent"></div>
                  </div>
                {/if}
          </div>
          
          <div class="flex flex-col space-y-2 mb-2">
            <!-- Enhanced Cycles Management Panel -->
            <div class="relative overflow-hidden bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 dark:from-emerald-900/20 dark:via-teal-900/20 dark:to-cyan-900/20 border border-emerald-200/60 dark:border-emerald-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
              <!-- Background decorative elements -->
              <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-emerald-200/30 to-teal-200/30 dark:from-emerald-600/10 dark:to-teal-600/10 rounded-full -translate-y-10 translate-x-10"></div>
              <div class="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-cyan-200/30 to-emerald-200/30 dark:from-cyan-600/10 dark:to-emerald-600/10 rounded-full translate-y-8 -translate-x-8"></div>
              
              <div class="relative p-4 sm:p-5">
                <!-- Header Section -->
                <div class="flex flex-col space-y-3 md:flex-row md:items-center md:justify-between md:space-y-0 mb-4">
                  <div class="flex items-center space-x-3">
                    <!-- Icon with gradient background -->
                    <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 dark:from-emerald-600 dark:to-teal-700 rounded-xl shadow-lg flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    
                    <!-- Title and subtitle -->
                    <div class="flex flex-col">
                      <h2 class="text-sm sm:text-base font-bold text-emerald-900 dark:text-emerald-100">Cycles Management</h2>
                      <p class="text-xs text-emerald-700 dark:text-emerald-300">Power your mAIner with computational cycles</p>
                    </div>
                  </div>
                  
                  <!-- Primary Top-up Button -->
                  <button 
                    type="button" 
                    class="group relative inline-flex items-center justify-center px-4 sm:px-6 py-2.5 sm:py-3 text-sm font-bold text-white bg-gradient-to-r from-emerald-500 to-teal-600 dark:from-emerald-600 dark:to-teal-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 border border-emerald-400/50 dark:border-emerald-500/50 w-full md:w-auto"
                    class:opacity-50={agentsBeingToppedUp.has(agent.id) || !isProtocolActive }
                    class:cursor-not-allowed={agentsBeingToppedUp.has(agent.id) || !isProtocolActive }
                    class:transform-none={agentsBeingToppedUp.has(agent.id) || !isProtocolActive }
                    class:hover:scale-100={agentsBeingToppedUp.has(agent.id) || !isProtocolActive }
                    disabled={agentsBeingToppedUp.has(agent.id) || !isProtocolActive }
                    on:click={() => openTopUpModal(agent)}
                  >
                    {#if agentsBeingToppedUp.has(agent.id)}
                      <div class="flex items-center space-x-2">
                        <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                        <span>Processing...</span>
                      </div>
                    {:else}
                      <div class="flex items-center space-x-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                        </svg>
                        <span>Top-up Cycles</span>
                      </div>
                    {/if}
                    <div class="absolute inset-0 rounded-xl bg-gradient-to-r from-teal-100 to-emerald-100 dark:from-teal-600/20 dark:to-emerald-600/20 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                  </button>
                </div>

                <!-- Balance Display Section -->
                <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-emerald-200/40 dark:border-emerald-700/40 shadow-sm">
                  <div class="flex flex-col space-y-3">
                    <!-- Balance Header -->
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                        </svg>
                        <span class="text-sm font-medium text-emerald-900 dark:text-emerald-100">Current Balance</span>
                      </div>
                      
                      <!-- Status indicator based on balance level -->
                      {#if agent.cycleBalance > 5_000_000_000_000}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 border border-green-300 dark:border-green-700">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                          </svg>
                          Healthy
                        </span>
                      {:else if agent.cycleBalance > 1_000_000_000_000}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/40 text-yellow-800 dark:text-yellow-300 border border-yellow-300 dark:border-yellow-700">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                          </svg>
                          Low
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 dark:bg-red-900/40 text-red-800 dark:text-red-300 border border-red-300 dark:border-red-700">
                          <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                          </svg>
                          Critical
                        </span>
                      {/if}
                    </div>

                    <!-- Balance Value Display -->
                    <div class="flex items-center justify-between">
                      {#if agentsBeingToppedUp.has(agent.id) || agentsBeingRefreshed.has(agent.id)}
                        <div class="flex items-center space-x-3">
                          <span class="w-5 h-5 border-2 border-emerald-400/30 border-t-emerald-600 rounded-full animate-spin"></span>
                          <div class="flex flex-col">
                            <span class="text-sm font-medium text-emerald-700 dark:text-emerald-300">
                              {agentsBeingToppedUp.has(agent.id) ? 'Updating balance...' : 'Refreshing balance...'}
                            </span>
                            <span class="text-xs text-emerald-600 dark:text-emerald-400 opacity-75">Please wait</span>
                          </div>
                        </div>
                      {:else}
                        <div class="flex flex-col">
                          <div class="flex items-baseline space-x-2">
                            <span class="text-2xl sm:text-3xl font-bold text-emerald-900 dark:text-emerald-100">
                              {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 4, false)}
                            </span>
                            <span class="text-sm font-medium text-emerald-700 dark:text-emerald-300">T cycles</span>
                          </div>
                          <span class="text-xs text-emerald-600 dark:text-emerald-400 opacity-75">
                            ≈ {formatLargeNumber(agent.cycleBalance, 2, true)} total cycles
                          </span>
                        </div>
                      {/if}

                      <!-- Refresh Button -->
                      <button 
                        type="button" 
                        class="group inline-flex items-center justify-center w-9 h-9 text-emerald-600 dark:text-emerald-400 bg-emerald-100/50 dark:bg-emerald-800/30 hover:bg-emerald-200/70 dark:hover:bg-emerald-700/40 rounded-lg border border-emerald-300/50 dark:border-emerald-600/50 transition-all duration-200 hover:scale-105 hover:shadow-md"
                        class:opacity-50={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                        class:cursor-not-allowed={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                        class:hover:scale-100={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                        disabled={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                        on:click={() => refreshAgentBalance(agent)}
                        use:tooltip={{ 
                          text: "Refresh cycles balance",
                          direction: 'top',
                          textSize: 'xs'
                        }}
                      >
                        {#if agentsBeingRefreshed.has(agent.id)}
                          <span class="w-4 h-4 border-2 border-emerald-400/30 border-t-emerald-600 rounded-full animate-spin"></span>
                        {:else}
                          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 group-hover:rotate-180 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        {/if}
                      </button>
                    </div>

                    <!-- Balance Info Footer -->
                    {#if !agentsBeingToppedUp.has(agent.id) && !agentsBeingRefreshed.has(agent.id)}
                      <div class="pt-2 border-t border-emerald-200/50 dark:border-emerald-700/50">
                        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between text-xs space-y-1 sm:space-y-0">
                          <span class="text-emerald-600 dark:text-emerald-400 opacity-75">
                            💡 Cycles power your mAIner's computational tasks
                          </span>
                          {#if agent.cycleBalance <= 1_000_000_000_000}
                            <span class="text-red-600 dark:text-red-400 font-medium">
                              ⚠️ Top-up recommended
                            </span>
                          {/if}
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
              
              <!-- Bottom accent line -->
              <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-emerald-400 dark:via-emerald-500 to-transparent"></div>
            </div>
          </div>

          <div class="flex flex-col space-y-2 mb-2">
            <!-- Daily Burn Rate Panel Component -->
            <DailyBurnRatePanel 
              {agent} 
              {agentCanisterActors} 
              {agentCanistersInfo}
              on:burnRateUpdated={handleBurnRateUpdate}
            />
          </div>


          <div class="flex flex-col space-y-2 mb-2">
            <CyclesDisplayAgent cycles={agent.burnedCycles} label="Burned Cycles" />
          </div>

        </div>
      </div>
    </div>
  {/if}
{/each}
{/if}

<!-- Top-Up Celebration Component -->
<TopUpCelebration 
  isVisible={showCelebration}
  amount={celebrationAmount}
  token={celebrationToken}
  on:close={handleCelebrationClose}
/>

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
    width: 6px;
    height: 6px;
  }
  
  @media (min-width: 640px) {
    .terminal-scroll::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
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

  /* Mobile optimizations */
  @media (max-width: 639px) {
    /* Improve touch targets on mobile */
    button {
      min-height: 44px;
    }
    
    /* Better text wrapping on small screens */
    .break-words {
      word-break: break-word;
      overflow-wrap: break-word;
    }
    
    /* Improve spacing for mobile */
    .space-y-1 > * + * {
      margin-top: 0.25rem;
    }
    
    /* Better modal positioning on mobile */
    .fixed {
      position: fixed !important;
    }
  }
  
  /* Improve text readability on very small screens */
  @media (max-width: 375px) {
    .text-xs {
      font-size: 0.65rem;
    }
  }
</style>