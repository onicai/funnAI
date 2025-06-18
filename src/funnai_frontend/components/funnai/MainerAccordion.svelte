<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import CyclesDisplayAgent from './CyclesDisplayAgent.svelte';
  import { store } from "../../stores/store";
  import LoginModal from '../login/LoginModal.svelte';
  import MainerPaymentModal from './MainerPaymentModal.svelte';
  import MainerTopUpModal from './MainerTopUpModal.svelte';
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

  // Track which agents are having their burn rate updated
  let agentsBeingUpdated = new Set<string>();

  // Track which agents are having their balance refreshed
  let agentsBeingRefreshed = new Set<string>();

  // Add loading state for individual whitelist mAIner creation
  let whitelistMainersBeingCreated = new Set<string>();

  // Reactive counters for mAIner status
  $: activeMainers = agents.filter(agent => agent.status === 'active').length;
  $: inactiveMainers = agents.filter(agent => agent.status === 'inactive').length;
  $: totalMainers = agents.length;

  // Reactive mAIner price based on model type and whitelist phase
  let currentMainerPrice = 1000; // Will be loaded
  let currentWhitelistPrice = 0.5; // Will be loaded
  $: mainerPrice = isWhitelistPhaseActive ? currentWhitelistPrice : currentMainerPrice;

  async function getMainerPrice() {
    try {
      let price = modelType === 'Own' ? await getOwnAgentPrice() : await getSharedAgentPrice();

      if (price <= 0) {
        console.error("Issue getting mAIner price as it's 0 or negative.");
        // Return fallback value instead of undefined
        return modelType === 'Own' ? 1500 : 1000;
      };

      return price;      
    } catch (error) {
      console.error("Error getting mAIner price:", error);
      // Return fallback value instead of undefined
      return modelType === 'Own' ? 1500 : 1000;
    }
  };



  /**
   * Updates the agent settings based on user-selected burn rate level.
   * 
   * @param {'Low' | 'Medium' | 'High'} level - The burn rate level selected by the user
   * @param {object} agent - The mAIner agent to update
  */
  async function updateAgentBurnRate(level, agent) {
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
      await agentActor.updateAgentSettings(burnRateSetting);
      
      // Refresh the list of agents to show updated settings
      try {
        await store.loadUserMainerCanisters();
        // Explicitly reload agents after store update  
        agents = await loadAgents();
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
        
        store.resetMainerCreationAfterOpen(); // Reset the flag using store method
      }, 300); // Increased timeout to ensure DOM is ready
    }
  };

  function createAgent() {
    // Open the MainerPaymentModal to handle the payment
    mainerPaymentModalOpen = true;
  };

  function createWhitelistAgent(unlockedMainer) {
    console.log("🔵 createWhitelistAgent called with:", unlockedMainer);
    // Set the selected unlocked mAIner for whitelist creation
    selectedUnlockedMainer = unlockedMainer;
    console.log("🔵 selectedUnlockedMainer set to:", selectedUnlockedMainer);
    console.log("🔵 Opening payment modal...");
    
    // Add this mAIner to the loading set (using id or a unique identifier)
    const mainerIdentifier = unlockedMainer.id || unlockedMainer.name || `unlocked-${Date.now()}`;
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
  
  // Handle top-up completion
  async function handleTopUpComplete(txId: string, canisterId: string) {
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

    // Clean the enriched data to get only original backend fields
    let cleanMainerAgent = getOriginalCanisterInfo(mainerAgent);

    let mainerAgentTopUpInput = {
      paymentTransactionBlockId: BigInt(txId),
      mainerAgent: cleanMainerAgent,
    };
    try {
      let topUpUserMainerAgentResponse = await $store.gameStateCanisterActor.topUpCyclesForMainerAgent(mainerAgentTopUpInput);
      
      if ('Ok' in topUpUserMainerAgentResponse) {
        // top up was successful
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
    } catch (refreshError) {
      console.error("Error refreshing agents after top-up:", refreshError);
    } finally {
      // Remove from loading set after processing
      agentsBeingToppedUp.delete(canisterId);
      agentsBeingToppedUp = agentsBeingToppedUp; // Trigger reactivity
    }
  }
  
  async function handleSendComplete(txId?: string) {
    mainerPaymentModalOpen = false;
    
    // Clear the individual whitelist mAIner loading state since global creation starts
    whitelistMainersBeingCreated.clear();
    whitelistMainersBeingCreated = whitelistMainersBeingCreated; // Trigger reactivity
    
    // Set the creation process as started using store
    store.startMainerCreation();
    
    // Store the selected unlocked mAIner before starting creation to prevent null reference
    const selectedMainerForCreation = selectedUnlockedMainer;
    
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
                  // Wait for the reactive update to complete, then open the latest mAIner
                  setTimeout(() => {
                    // Force open the latest mAIner accordion (newest one)
                    if (agents.length > 0) {
                      const latestAgent = agents[agents.length - 1];
                      const sanitizedId = latestAgent.id.replace(/[^a-zA-Z0-9-_]/g, '_');
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

    console.log("🔍 loadAgents - Total canister info items:", enrichedCanistersInfo.length);

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
      
      console.log(`🔍 mAIner ${index + 1}:`, {
        isUnlocked,
        isOwnedByCurrentUser,
        mainerType,
        address: canisterInfo.address,
        ownedBy: canisterInfo.ownedBy?.toString(),
        currentUser: $store.principal?.toString()
      });
      
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
        originalCanisterInfo: canisterInfo // Store original for whitelist creation
      };

      if (isUnlocked && isOwnedByCurrentUser) {
        console.log(`✅ Adding unlocked mAIner ${index + 1} - owned by current user`);
        unlockedAgents.push(mainerData);
      } else if (isUnlocked && !isOwnedByCurrentUser) {
        console.log(`⏭️ Skipping unlocked mAIner ${index + 1} - owned by different user:`, canisterInfo.ownedBy?.toString());
      } else if (!isUnlocked) {
        activeAgents.push(mainerData);
      }
    });

    // Update unlocked mAIners list
    unlockedMainers = unlockedAgents;
    
    console.log("🔍 Final results:", {
      totalCanisters: enrichedCanistersInfo.length,
      activeAgents: activeAgents.length,
      unlockedAgents: unlockedAgents.length,
      unlockedMainers: unlockedMainers.length
    });
    
    return activeAgents;
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
    
    try {
      isProtocolActiveFlag = await getIsProtocolActive();
      isMainerCreationStoppedFlag = await getIsMainerCreationStopped(modelType);
      isWhitelistPhaseActiveFlag = await getIsWhitelistPhaseActive();
      isPauseWhitelistMainerCreationFlag = await getPauseWhitelistMainerCreationFlag();
      

    } catch (error) {
      console.error("Error loading protocol flags:", error);
      // Set safe defaults
      isProtocolActiveFlag = true;
      isMainerCreationStoppedFlag = false;
      isWhitelistPhaseActiveFlag = true; // Default to true since we manually set it to true in gameState.ts
      isPauseWhitelistMainerCreationFlag = false;
    } finally {
      // Set loading to false after flags are loaded (whether successful or not)
      protocolFlagsLoading = false;
    }
    
    // Retrieve the data from the agents' backend canisters to fill the above agents array dynamically
    agents = await loadAgents();
    
    // Automatically open the create accordion if no agents exist and not in whitelist phase
    // In whitelist phase, show unlocked mAIners instead
    if (agents.length === 0 && !isWhitelistPhaseActive) {
      setTimeout(() => {
        toggleAccordion('create');
      }, 100);
    } else if (agents.length > 0) {
      // Open the latest mAIner if agents exist
      setTimeout(() => {
        const latestAgent = agents[agents.length - 1];
        if (latestAgent && latestAgent.id) {
          toggleAccordion(latestAgent.id);
        }
      }, 100);
    };

    try {
      currentMainerPrice = await getMainerPrice();
      currentWhitelistPrice = await getWhitelistAgentPrice();
    } catch (error) {
      console.error("Error loading prices:", error);
      // Set fallback values if loading fails
      currentMainerPrice = modelType === 'Own' ? 1500 : 1000;
      currentWhitelistPrice = 0.1;
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
  } else if (agents.length > 0 && !shouldOpenFirstMainerAfterCreation && !isCreatingMainer) {
    // If we have agents and this isn't triggered by creation, and we're not currently creating a mAIner, open the latest mAIner
    setTimeout(() => {
      // First, ensure create accordion is closed (only if not creating)
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
  function handlePaymentModalClose() {
    mainerPaymentModalOpen = false;
    // Clear any individual loading states when modal closes without payment
    whitelistMainersBeingCreated.clear();
    whitelistMainersBeingCreated = whitelistMainersBeingCreated; // Trigger reactivity
    selectedUnlockedMainer = null;
  };
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
                        Available to deploy
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
            <h3 class="font-medium leading-tight mb-1 dark:text-gray-300">Pay & Spin up</h3>

        </li>
      </ol>

      <div class="flex flex-col items-stretch sm:items-end">
        <button 
          on:click={createAgent} 
          disabled={isCreatingMainer}
          class="bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-4 py-2 rounded-xl transition-colors mb-2 w-full sm:w-auto sm:mr-2 text-sm sm:text-base"
          class:opacity-50={isCreatingMainer}
          class:cursor-not-allowed={isCreatingMainer}
        >
          Create mAIner Agent
        </button>
      </div>

    {:else}
      <div class="flex flex-col items-center justify-center py-8">
        <h3 class="text-xl font-medium text-gray-700 dark:text-gray-100 mb-2 mt-8">You need to login first</h3>
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
{/if}

<!-- Whitelist mAIners Section (only show when in whitelist phase) -->
{#if isWhitelistPhaseActive && isAuthenticated}
  {#if unlockedMainers.length > 0}
    <div class="mb-4">
      <div class="relative overflow-hidden bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 dark:from-amber-600 dark:via-yellow-600 dark:to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5">
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
                <p>Create your mAIner from the unlocked options below for just <span class="font-bold text-white">{currentWhitelistPrice || 0.5} ICP</span> instead of the regular price of <span class="line-through opacity-75">{currentMainerPrice || 1000} ICP</span>.</p>
                {#if unlockedMainers.length > 0}
                  <p class="text-xs text-white/80 mt-2">💡 <span class="font-medium">Note:</span> More unlocked mAIners may become available as others are created. Check back periodically during the whitelist phase.</p>
                {/if}
              </div>
            </div>
            
            <!-- Right side - Savings highlight -->
            <div class="flex-shrink-0 sm:ml-6">
              <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center border border-white/20 shadow-lg">
                <div class="text-2xl sm:text-3xl font-bold text-white mb-1">
                  {Math.round(((currentMainerPrice || 1000) - (currentWhitelistPrice || 0.5)) / (currentMainerPrice || 1000) * 100)}%
                </div>
                <div class="text-xs sm:text-sm text-white/80 font-medium uppercase tracking-wide">
                  Savings
                </div>
                <div class="text-xs text-white/70 mt-1">
                  Save {((currentMainerPrice || 1000) - (currentWhitelistPrice || 0.5)).toFixed(1)} ICP
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unlocked mAIners List -->
    {#each unlockedMainers as unlockedMainer, index}
      <div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-yellow-50/50 to-orange-50/50 dark:from-yellow-900/10 dark:to-orange-900/10">
        <div class="w-full flex justify-between items-center py-3 sm:py-5 px-3 sm:px-4 text-gray-800 dark:text-gray-200">
          <span class="flex items-center font-medium text-sm min-w-0 flex-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 mr-2 text-yellow-600 dark:text-yellow-400 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span class="truncate">{unlockedMainer.name}</span>
          </span>
          <div class="flex items-center flex-shrink-0 ml-2 space-x-2">
            <span class="px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-400">
              Unlocked
            </span>
            <button
              on:click={() => createWhitelistAgent(unlockedMainer)}
              disabled={isCreatingMainer || isPauseWhitelistMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name)}
              class="bg-yellow-600 dark:bg-yellow-700 hover:bg-yellow-700 dark:hover:bg-yellow-800 text-white px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors flex items-center"
              class:opacity-50={isCreatingMainer || isPauseWhitelistMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name)}
              class:cursor-not-allowed={isCreatingMainer || isPauseWhitelistMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name)}
            >
              {#if isCreatingMainer}
                <span class="w-3 h-3 mr-1 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Creating...
              {:else if whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name)}
                <span class="w-3 h-3 mr-1 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Loading...
              {:else}
                Create ({currentWhitelistPrice || 0.5} ICP)
              {/if}
            </button>
          </div>
        </div>
      </div>
    {/each}
  {:else}
    <div class="mb-4">
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
        <svg class="w-8 h-8 text-gray-400 dark:text-gray-600 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
        <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">No unlocked mAIners available</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400">
          You don't have any unlocked mAIners available for whitelist creation at this time.
        </p>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">
          Debug: Total mAIners loaded: {agentCanistersInfo.length}, Unlocked for you: {unlockedMainers.length}
        </p>
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

<!-- Terminal-style progress component (shows for both regular and whitelist creation) -->
{#if isCreatingMainer}
  <div class="mt-4 bg-gray-900 text-green-400 font-mono text-xs sm:text-sm rounded-lg p-2 sm:p-3 border border-gray-700 overflow-hidden">
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
    canisterId={selectedCanister.id}
    canisterName={selectedCanister.name}
  />
{/if}

<!-- mAIner Summary Header -->
{#if totalMainers > 0}
  <div class="mt-2 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 sm:p-4 mb-2">
    <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
      <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0">
        <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-3 sm:space-y-0">
          <div class="flex items-center space-x-1">
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
            <span class="text-xs sm:text-sm text-green-700 dark:text-green-400 font-medium">{activeMainers} Active</span>
          </div>
          <div class="flex items-center space-x-1">
            <div class="w-3 h-3 rounded-full bg-gray-400"></div>
            <span class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">{inactiveMainers} Inactive</span>
          </div>
        </div>
        {#if inactiveMainers > 0}
          <div class="text-xs text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 px-2 py-1 rounded-md w-fit">
            ⚠️ {inactiveMainers} mAIner{inactiveMainers === 1 ? '' : 's'} need{inactiveMainers === 1 ? 's' : ''} cycles
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- Existing Agents -->
{#each agents as agent, index}
  {#if agent && agent.id}
    {@const sanitizedId = agent.id.replace(/[^a-zA-Z0-9-_]/g, '_')}
    {@const buttonClasses = `w-full flex justify-between items-center py-3 sm:py-5 px-3 sm:px-4 text-gray-800 dark:text-gray-200 ${agent.status === 'inactive' ? 'bg-red-50 dark:bg-red-900/10' : ''}`}
    <div class="border-b border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900" class:opacity-75={agent.status === 'inactive'}>
      <button on:click={() => toggleAccordion(agent.id)} class={buttonClasses}>
        <span class="flex items-center font-medium text-sm min-w-0 flex-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 mr-2 text-gray-600 dark:text-gray-400 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v7c0 1.1.9 2 2 2h2l1 2v7h2v-7l1-2h2l1 2v7h2v-7l1-2h2c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 10H4V4h2v6zm4 0H8V4h2v6zm4 0h-2V4h2v6zm4 0h-2V4h2v6z"/>
          </svg>
          <span class="truncate">{agent.name}</span>
          {#if agent.status === 'inactive'}
            <span 
              class="ml-1 sm:ml-2 text-xs text-red-600 dark:text-red-400 hidden sm:inline cursor-help"
              use:tooltip={{ 
                text: "You still have some cycles, but not enough to keep going. Please top up to continue.",
                direction: 'top',
                textSize: 'xs'
              }}
            >(needs cycles) <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-red-500 dark:text-red-400 inline" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg></span>
          {/if}
        </span>
        <div class="flex items-center flex-shrink-0 ml-2">
          <!-- Add LLM setup status badge when applicable -->
          {#if agent.mainerType === 'Own' && agent.llmSetupStatus === 'inProgress'}
            <span class="mr-1 sm:mr-2 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-400 hidden sm:inline-block">
              LLM setup
            </span>
          {/if}
          <span class={`mr-2 sm:mr-4 px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs ${agent.status === 'active' ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-400' : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-400'}`}>
            {agent.status}
          </span>
          <span id="icon-{sanitizedId}" class="text-gray-600 dark:text-gray-400 transition-transform duration-300" style="transform: rotate(180deg)">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3 sm:w-4 sm:h-4">
              <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
            </svg>
          </span>
        </div>
      </button>
      <div id="content-{sanitizedId}" class="accordion-content">
        <div class="pb-3 sm:pb-5 text-xs sm:text-sm text-gray-700 dark:text-gray-300 p-3 sm:p-4 bg-gray-5 dark:bg-gray-900">
          <!-- Canister Information Section -->
          <div class="flex flex-col space-y-2 mb-2">
            <div class="w-full p-3 sm:p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg">
              <h2 class="text-xs sm:text-sm mb-2 font-medium">Canister Information</h2>
              <div class="flex flex-col gap-2">
                <div class="flex flex-col sm:flex-row sm:items-center sm:flex-wrap">
                  <span class="text-xs mr-2 mb-1 sm:mb-0 sm:w-24 font-medium">Controller ID:</span>
                  <a href="https://dashboard.internetcomputer.org/canister/{agent.id}" target="_blank" rel="noopener noreferrer" class="ml-auto bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-sm dark:bg-gray-700 dark:text-green-400 border border-green-400 break-all hover:bg-green-200 dark:hover:bg-gray-600 transition-colors flex items-center w-fit">
                    <span class="truncate max-w-[200px] sm:max-w-none">{agent.id}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 ml-1 text-gray-500 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z" transform="rotate(45, 10, 10)" />
                    </svg>
                  </a>
                </div>

                
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
            <div class="w-full p-3 sm:p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
              <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
                  <h2 class="text-xs sm:text-sm font-medium">Top up cycles</h2>
                  <button 
                    type="button" 
                    class="py-2 sm:py-2.5 px-4 sm:px-5 text-xs font-medium text-gray-900 dark:text-gray-300 focus:outline-none bg-white dark:bg-gray-700 rounded-full border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400 w-full sm:w-auto"
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
              <div class="mt-2 flex flex-col sm:flex-row sm:items-center">
                <span class="text-xs text-gray-500 dark:text-gray-400 mb-1 sm:mb-0">Current balance:</span>
                {#if agentsBeingToppedUp.has(agent.id) || agentsBeingRefreshed.has(agent.id)}
                  <span class="ml-auto text-xs sm:text-sm font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800 flex items-center w-fit">
                    <span class="w-3 h-3 mr-2 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin"></span>
                    {agentsBeingToppedUp.has(agent.id) ? 'Updating...' : 'Refreshing...'}
                  </span>
                {:else}
                  <span class="ml-auto text-xs sm:text-sm font-medium bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800 w-fit">
                    {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 4, false)} T cycles
                  </span>
                {/if}
              </div>
              <!-- Refresh Balance Button -->
              <div class="mt-2 flex justify-end">
                <button 
                  type="button" 
                  class="py-1.5 px-3 text-xs font-medium text-gray-600 dark:text-gray-400 focus:outline-none bg-gray-50 dark:bg-gray-600 rounded-md border border-gray-200 dark:border-gray-500 hover:bg-gray-100 dark:hover:bg-gray-500 hover:text-gray-900 dark:hover:text-gray-200 flex items-center transition-colors"
                  class:opacity-50={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  class:cursor-not-allowed={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  disabled={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  on:click={() => refreshAgentBalance(agent)}
                >
                  {#if agentsBeingRefreshed.has(agent.id)}
                    <span class="w-3 h-3 mr-1 border-2 border-gray-400/30 border-t-gray-600 rounded-full animate-spin"></span>
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  {/if}
                  Refresh cycles balance
                </button>
              </div>
            </div>
          </div>

          <div class="flex flex-col space-y-2 mb-2">
            <div class="w-full p-3 sm:p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
              <div class="flex flex-col">
                  <h2 class="text-xs sm:text-sm mb-2 font-medium">Set daily burn rate</h2>
                  <div class="inline-flex rounded-full shadow-xs w-full justify-end" role="group">
                    <button 
                      type="button" 
                      class="px-3 sm:px-4 py-1.5 sm:py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
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
                      class="px-3 sm:px-4 py-1.5 sm:py-2 text-xs font-medium border-t border-b border-gray-200 dark:border-gray-600 focus:z-10 focus:ring-2 focus:ring-blue-700
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
                      class="px-3 sm:px-4 py-1.5 sm:py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-e-full focus:z-10 focus:ring-2 focus:ring-blue-700
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
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-center mt-2">
                      <span class="w-3 h-3 sm:w-4 sm:h-4 mr-0 sm:mr-2 border-2 border-purple-400/30 border-t-purple-600 rounded-full animate-spin mb-1 sm:mb-0 self-center"></span>
                      <span class="text-xs text-purple-600 dark:text-purple-400 text-center sm:text-left">Updating burn rate setting...</span>
                    </div>
                  {/if}
                </div>
            </div>
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