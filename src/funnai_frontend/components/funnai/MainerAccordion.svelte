<script lang="ts">
  import { onMount, afterUpdate, onDestroy } from 'svelte';
  import CyclesDisplayAgent from './CyclesDisplayAgent.svelte';
  import DailyBurnRatePanel from './DailyBurnRatePanel.svelte';
  import FleetOverview from './mainers/FleetOverview.svelte';
  import FleetBulkTopUp from './mainers/FleetBulkTopUp.svelte';
  import EmptyFleetBanner from './mainers/EmptyFleetBanner.svelte';
  import NetworkCapacityPanel from './mainers/NetworkCapacityPanel.svelte';
  import MainerCreationPanel from './mainers/MainerCreationPanel.svelte';
  import WhitelistMainerPanel from './mainers/WhitelistMainerPanel.svelte';
  import ReverseAuctionPanel from './mainers/ReverseAuctionPanel.svelte';
  import AnnouncementPanel from './mainers/AnnouncementPanel.svelte';
  import CanisterInfo from './CanisterInfo.svelte';
  import { get } from 'svelte/store';
  import { store, MAINER_UI_CACHE_KEY } from "../../stores/store";
  import LoginModal from '../login/LoginModal.svelte';
  import MainerPaymentModal from './MainerPaymentModal.svelte';
  import MainerTopUpModal from './MainerTopUpModal.svelte';
  import TopUpCelebration from './TopUpCelebration.svelte';
  import { Principal } from '@dfinity/principal';
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { tooltip } from "../../helpers/utils/tooltip";
  import { getSharedAgentPrice, getOwnAgentPrice, getIsProtocolActive, getIsMainerCreationStopped, getWhitelistAgentPrice, getPauseWhitelistMainerCreationFlag, getIsWhitelistPhaseActive, getIsMainerAuctionActive, getMainerAuctionTimerInfo, getNextMainerAuctionPriceDropAtNs, getAvailableMainers } from "../../helpers/gameState";
  import { mainerHealthService, mainerHealthStatuses } from "../../helpers/mainerHealthService";
  import { MarketplaceService } from "../../helpers/marketplaceService";
  import { MARKETPLACE_ENABLED } from "../../helpers/config/featureFlags";
  import { ArrowUp } from '@lucide/svelte';

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = !!$store.isAuthed;
  $: isCreatingMainer = $store.isCreatingMainer;
  $: mainerCreationProgress = $store.mainerCreationProgress;
  $: shouldOpenFirstMainerAfterCreation = $store.shouldOpenFirstMainerAfterCreation;
  $: mainersLoadError = $store.userMainersLoadError;
  $: mainersLoadStatus = $store.userMainersLoadStatus;

  const PROTOCOL_FLAGS_CACHE_KEY = 'funnai.protocolFlags';

  function readProtocolFlagsCache() {
    try {
      const raw = localStorage.getItem(PROTOCOL_FLAGS_CACHE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function writeProtocolFlagsCache(flags) {
    try {
      localStorage.setItem(PROTOCOL_FLAGS_CACHE_KEY, JSON.stringify(flags));
    } catch {
      // ignore quota / private mode
    }
  }

  function readMainerUiCache() {
    try {
      const raw = localStorage.getItem(MAINER_UI_CACHE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed?.agents)) return [];
      return parsed.agents.map((agent) => ({
        ...agent,
        originalCanisterInfo: {
          address: agent.id,
          creationTimestamp: agent.createdAtNs ? BigInt(agent.createdAtNs) : 0n,
        },
      }));
    } catch {
      return [];
    }
  }

  function writeMainerUiCache(nextAgents) {
    try {
      localStorage.setItem(MAINER_UI_CACHE_KEY, JSON.stringify({
        agents: nextAgents.map((agent) => ({
          id: agent.id,
          name: agent.name,
          uiStatus: agent.uiStatus,
          burnedCycles: agent.burnedCycles,
          cycleBalance: agent.cycleBalance,
          cyclesBurnRateSetting: agent.cyclesBurnRateSetting,
          mainerType: agent.mainerType,
          llmSetupStatus: agent.llmSetupStatus,
          hasError: agent.hasError,
          isUnlocked: agent.isUnlocked,
          createdAt: agent.createdAt,
          createdAtNs: agent.originalCanisterInfo?.creationTimestamp
            ? agent.originalCanisterInfo.creationTimestamp.toString()
            : null,
        })),
      }));
    } catch {
      // ignore quota / private mode
    }
  }

  const cachedProtocolFlags = readProtocolFlagsCache();

  // Loading state for protocol flags — skip the spinner when we already know last values
  let protocolFlagsLoading = !cachedProtocolFlags;

  let isProtocolActiveFlag = cachedProtocolFlags?.isProtocolActive ?? true;
  $: isProtocolActive = isProtocolActiveFlag;

  let isMainerCreationStoppedFlag = cachedProtocolFlags?.isMainerCreationStopped ?? false;
  $: stopMainerCreation = isMainerCreationStoppedFlag;
  $: canCreateMainer = isProtocolActive && !stopMainerCreation;

  // Whitelist phase variables
  let isWhitelistPhaseActiveFlag = cachedProtocolFlags?.isWhitelistPhaseActive ?? false;
  $: isWhitelistPhaseActive = isWhitelistPhaseActiveFlag;
  
  let isPauseWhitelistMainerCreationFlag = cachedProtocolFlags?.isPauseWhitelistMainerCreation ?? false;
  $: isPauseWhitelistMainerCreation = isPauseWhitelistMainerCreationFlag;

  // Reverse Auction variables
  let isAuctionActiveFlag = cachedProtocolFlags?.isAuctionActive ?? false;
  $: isAuctionActive = isAuctionActiveFlag;
  
  let availableMainersCount = 0; // Will be loaded
  $: availableMainers = availableMainersCount;
  
  // Announcement visibility state
  let showAnnouncement = true;
  
  let nextPriceDropAtNs = 0; // Will be loaded
  let auctionIntervalSeconds = 0; // Will be loaded
  let auctionUpdateInterval: number | null = null;

  let agents = [];
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
  let bulkTopUpIds: string[] = [];



  // Track which agents are having their balance refreshed
  let agentsBeingRefreshed = new Set<string>();

  // Add loading state for individual whitelist mAIner creation
  let whitelistMainersBeingCreated = new Set<string>();

  // Celebration state for top-up
  let showCelebration = false;
  let celebrationAmount = "";
  let celebrationToken = "";

  // Track mAIners listed for sale on marketplace
  let listedMainerAddresses = new Set<string>();

  // Reactive counters for mAIner status
  $: activeMainers = agents.filter(agent => agent.uiStatus === 'active').length;
  $: inactiveMainers = agents.filter(agent => agent.uiStatus === 'inactive').length;
  $: totalMainers = agents.length;

  // Reactive counters for burn rate distribution
  $: lowBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'Low').length;
  $: mediumBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'Medium').length;
  $: highBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'High').length;
  $: veryHighBurnRateMainers = agents.filter(agent => agent.cyclesBurnRateSetting === 'VeryHigh').length;

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
  
  async function openTopUpModal(agent) {
    // Check mAIner health before allowing top-up
    // Find the index of this agent in agentCanistersInfo to get the corresponding actor
    const agentIndex = agentCanistersInfo.findIndex(canister => 
      (canister.address === agent.id) || (canister.id === agent.id)
    );
    const actor = agentIndex !== -1 ? agentCanisterActors[agentIndex] : null;
    
    if (actor) {
      try {
        const healthStatus = await mainerHealthService.checkMainerHealth(agent.id, actor);
        if (!healthStatus.isHealthy) {
          // Don't open modal if mAIner is not healthy
          console.warn(`Cannot top-up mAIner ${agent.id}: ${healthStatus.maintenanceMessage}`);
          return;
        }
      } catch (error) {
        // If health check fails, assume unhealthy and don't allow top-up
        console.error(`Failed to check mAIner health for ${agent.id}:`, error);
        return;
      }
    }
    
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

  // Import visual identity helper
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  
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
      return; // NOTE: Edge case - payment may be lost if agent lookup fails after payment
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

  function handleBulkTopUpStart(canisterIds: string[]) {
    bulkTopUpIds = canisterIds;
    canisterIds.forEach((id) => agentsBeingToppedUp.add(id));
    agentsBeingToppedUp = agentsBeingToppedUp;
  }

  async function handleBulkTopUpComplete() {
    try {
      await store.loadUserMainerCanisters();
      agents = await loadAgents();
    } catch (refreshError) {
      console.error("Error refreshing agents after fleet top-up:", refreshError);
    } finally {
      bulkTopUpIds.forEach((id) => agentsBeingToppedUp.delete(id));
      bulkTopUpIds = [];
      agentsBeingToppedUp = agentsBeingToppedUp;
    }

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
      protocolFlagsLoading = false;
      writeProtocolFlagsCache({
        isProtocolActive: isProtocolActiveFlag,
        isMainerCreationStopped: isMainerCreationStoppedFlag,
        isWhitelistPhaseActive: isWhitelistPhaseActiveFlag,
        isPauseWhitelistMainerCreation: isPauseWhitelistMainerCreationFlag,
        isAuctionActive: isAuctionActiveFlag,
      });
    };    
  };

  async function loadMarketplaceListings() {
    if (!MARKETPLACE_ENABLED || !isAuthenticated) {
      listedMainerAddresses = new Set<string>();
      return;
    }
    
    try {
      const result = await MarketplaceService.getUserListings();
      if (result.success && result.listings) {
        listedMainerAddresses = new Set(result.listings.map(listing => listing.address));
      } else {
        listedMainerAddresses = new Set<string>();
      }
    } catch (error) {
      console.error("Error loading marketplace listings:", error);
      listedMainerAddresses = new Set<string>();
    }
  }

  async function loadAuctionData() {
    try {
      // Load auction active flag
      isAuctionActiveFlag = await getIsMainerAuctionActive();
      
      // Load available mainers count
      availableMainersCount = await getAvailableMainers();
      
      // Load auction timer info if auction is active
      if (isAuctionActiveFlag) {
        const timerInfo = await getMainerAuctionTimerInfo();
        if (timerInfo) {
          auctionIntervalSeconds = timerInfo.intervalSeconds;
        }
        
        // Load next price drop timestamp
        nextPriceDropAtNs = await getNextMainerAuctionPriceDropAtNs();
        
        // Also refresh the price when loading auction data
        currentMainerPrice = await getMainerPrice();
      }
    } catch (error) {
      console.error("Error loading auction data:", error);
      // Set safe defaults
      isAuctionActiveFlag = false;
      availableMainersCount = 0;
      nextPriceDropAtNs = 0;
      auctionIntervalSeconds = 0;
    } finally {
      writeProtocolFlagsCache({
        isProtocolActive: isProtocolActiveFlag,
        isMainerCreationStopped: isMainerCreationStoppedFlag,
        isWhitelistPhaseActive: isWhitelistPhaseActiveFlag,
        isPauseWhitelistMainerCreation: isPauseWhitelistMainerCreationFlag,
        isAuctionActive: isAuctionActiveFlag,
      });
    }
  };

  async function updateAuctionData() {
    // This function is called from the ReverseAuctionPanel to update data
    await loadAuctionData();
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
          
          // Step 4: Final configuration (burn rate and timer handled by backend)
          addProgressMessage("Configuring mAIner parameters...");

          // Step 5: Completion - Match exact timing as regular creation
          setTimeout(() => {
            addProgressMessage("mAIner successfully created!", true);
            setTimeout(() => {
              // Refresh the list of agents to show the newly created one
              refreshMainersUntilListed().then((found) => {
                if (!found) {
                  addProgressMessage("mAIner created — if it does not appear yet, it is still setting up.");
                }
                loadAgents().then((updatedAgents) => {
                  agents = updatedAgents;
                  setTimeout(() => {
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
                    setTimeout(() => {
                      store.completeMainerCreation();
                    }, 4000);
                  }, 1000);
                });
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
          
          // Step 4: Final configuration (burn rate and timer handled by backend)
          addProgressMessage("Configuring mAIner parameters...");

          // Step 5: Completion
          setTimeout(() => {
            addProgressMessage("mAIner successfully created!", true);
            setTimeout(() => {
              // Refresh the list of agents to show the newly created one
              refreshMainersUntilListed().then((found) => {
                if (!found) {
                  addProgressMessage("mAIner created — if it does not appear yet, it is still setting up.");
                }
                setTimeout(() => {
                  openFirstMainerAccordion();
                  setTimeout(() => {
                    store.completeMainerCreation();
                  }, 4000);
                }, 1000);
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

  function mapAgentsFrom(canistersInfo = [], _canisterActors = [], principalText = null) {
    const activeAgents = [];
    const unlockedAgents = [];

    canistersInfo.forEach((canisterInfo, index) => {
      let mainerType = 'Unknown';
      if (canisterInfo.canisterType?.MainerAgent) {
        if ('Own' in canisterInfo.canisterType.MainerAgent) {
          mainerType = 'Own';
        } else if ('ShareAgent' in canisterInfo.canisterType.MainerAgent) {
          mainerType = 'Shared';
        }
      }

      const isUnlocked = canisterInfo.status && 'Unlocked' in canisterInfo.status;
      const isOwnedByCurrentUser = !canisterInfo.ownedBy || canisterInfo.ownedBy.toString() === principalText;
      const creationTimestamp = canisterInfo.creationTimestamp;
      
      const mainerData = {
        id: canisterInfo.address || `unlocked-${index}`,
        name: isUnlocked ? `Unlocked mAIner ${index + 1}` : `mAIner ${canisterInfo.address?.slice(0, 5) || 'Unknown'}`,
        uiStatus: isUnlocked ? "unlocked" : (canisterInfo.uiStatus || "active"),
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
        originalCanisterInfo: canisterInfo,
        createdAt: creationTimestamp
          ? Number(typeof creationTimestamp === 'bigint' ? creationTimestamp / 1000000n : creationTimestamp)
          : null
      };

      if (isUnlocked && isOwnedByCurrentUser) {
        unlockedAgents.push(mainerData);
      } else if (!isUnlocked) {
        activeAgents.push(mainerData);
      }
    });

    const agentsSorted = activeAgents.sort((a, b) => {
      const nowNs = BigInt(Date.now()) * 1000000n;
      const tsA: bigint = (a.originalCanisterInfo?.creationTimestamp && a.originalCanisterInfo.creationTimestamp > 0n) ? a.originalCanisterInfo.creationTimestamp : nowNs;
      const tsB: bigint = (b.originalCanisterInfo?.creationTimestamp && b.originalCanisterInfo.creationTimestamp > 0n) ? b.originalCanisterInfo.creationTimestamp : nowNs;
      if (tsA === tsB) return 0;
      return tsA < tsB ? 1 : -1;
    });

    return { agents: agentsSorted, unlocked: unlockedAgents };
  }

  function loadAgents() {
    const mapped = mapAgentsFrom(
      agentCanistersInfo || [],
      agentCanisterActors || [],
      $store.principal?.toString()
    );
    unlockedMainers = mapped.unlocked;
    return mapped.agents;
  }

  {
    const initial = get(store);
    if (initial.userMainerAgentCanistersInfo?.length) {
      const mapped = mapAgentsFrom(
        initial.userMainerAgentCanistersInfo,
        initial.userMainerCanisterActors,
        initial.principal?.toString()
      );
      agents = mapped.agents;
      unlockedMainers = mapped.unlocked;
    } else if (initial.isAuthed) {
      agents = readMainerUiCache();
    }
  }

  $: {
    agentCanisterActors;
    agentCanistersInfo;

    if (agentCanistersInfo && agentCanistersInfo.length > 0) {
      agents = loadAgents();
      writeMainerUiCache(agents);
      openFirstMainerAccordion();
    } else if ($store.principal) {
      agents = [];
      unlockedMainers = [];
      writeMainerUiCache([]);
    }
  };

  function toggleLoginModal() {
    loginModalOpen = !loginModalOpen;
  }

  onMount(async () => {
    
    // Load initial state of flags and auction data in parallel (don't block each other)
    Promise.all([
      loadProtocolFlags(),
      loadAuctionData()
    ]).catch(error => {
      console.error("Error loading initial data:", error);
    });
    
    // Load marketplace listings to show "For Sale" badges
    await loadMarketplaceListings();
    
    // Note: Health checks are started reactively below when agentCanisterActors updates
    
    // Auto-open logic is now handled by MainerCreationPanel component via shouldAutoOpen prop

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

  // Track which mAIners have health checks running to prevent duplicate starts
  let healthChecksStarted = new Set();

  // Reload marketplace listings when authentication changes
  $: if (isAuthenticated !== undefined) {
    loadMarketplaceListings();
  }

  // Start health checks reactively when both actors and info are loaded
  $: {
    console.log(`[Health Check Debug] agentCanisterActors: ${agentCanisterActors?.length}, agentCanistersInfo: ${agentCanistersInfo?.length}`);
    
    // We need to combine actors with their canister IDs from the info array
    if (agentCanisterActors && agentCanisterActors.length > 0 && 
        agentCanistersInfo && agentCanistersInfo.length > 0) {
      
      console.log(`[Health Check Debug] Found ${agentCanistersInfo.length} mAIner(s) to check`);
      
      // Match actors with their info by index (they should be in the same order)
      const newMainerIds = agentCanistersInfo
        .filter((info, index) => {
          const actor = agentCanisterActors[index];
          const canisterId = info.address || info.id || info.canisterId;
          return actor && canisterId && !healthChecksStarted.has(canisterId);
        })
        .map(info => info.address || info.id || info.canisterId);
      
      console.log(`[Health Check Debug] Filtered to ${newMainerIds.length} new mAIners that need health checks`);
      
      if (newMainerIds.length > 0) {
        console.log(`Starting health checks for ${newMainerIds.length} new mAIner(s)...`);
        agentCanistersInfo.forEach((info, index) => {
          const actor = agentCanisterActors[index];
          const canisterId = info.address || info.id || info.canisterId;
          
          if (actor && canisterId && !healthChecksStarted.has(canisterId)) {
            console.log(`  - Starting health checks for: ${canisterId}`);
            mainerHealthService.startHealthChecks(canisterId, actor);
            healthChecksStarted.add(canisterId);
          }
        });
      }
    } else {
      console.log(`[Health Check Debug] Waiting for actors and info to load...`);
    }
  }

  // Update agent status based on health checks — only rewrite agents when uiStatus actually changes
  // (unconditional remap caused constant re-renders with many mainers and modal scroll flicker)
  $: if (agents && agents.length > 0 && $mainerHealthStatuses) {
    let changed = false;
    const now = Date.now();
    const PROVISIONING_WINDOW_MS = 5 * 60 * 1000;
    const nextAgents = agents.map(agent => {
      const healthStatus = $mainerHealthStatuses.get(agent.id);
      const stillProvisioning = Boolean(
        agent.createdAt && now - agent.createdAt < PROVISIONING_WINDOW_MS
      );

      if (healthStatus && !healthStatus.isHealthy) {
        if (stillProvisioning && agent.uiStatus !== 'setting-up') {
          changed = true;
          return { ...agent, uiStatus: 'setting-up' };
        }
        if (!stillProvisioning && agent.uiStatus !== 'inactive') {
          changed = true;
          return { ...agent, uiStatus: 'inactive' };
        }
      }

      return agent;
    });

    if (changed) {
      agents = nextAgents;
    }
  }

  async function refreshMainersUntilListed(attempts = 6, delayMs = 4000) {
    for (let i = 0; i < attempts; i++) {
      try {
        await store.loadUserMainerCanisters();
        agents = await loadAgents();
        if (agents.length > 0) {
          return true;
        }
      } catch (error) {
        console.error("Error refreshing mAIner list after creation:", error);
      }
      if (i < attempts - 1) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
      }
    }
    return false;
  }
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
    // Stop all health checks when component is destroyed
    mainerHealthService.stopAllHealthChecks();
    
    // Clear tracking
    healthChecksStarted.clear();
    
    // Clear auction update interval
    if (auctionUpdateInterval) {
      clearInterval(auctionUpdateInterval);
      auctionUpdateInterval = null;
    }
    
    if (typeof window !== 'undefined') {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    }
  });

  // Setup regular auction data updates when auction is active
  $: {
    if (isAuctionActive && !protocolFlagsLoading) {
      // Clear any existing interval
      if (auctionUpdateInterval) {
        clearInterval(auctionUpdateInterval);
      }
      
      // Use auction interval if it's shorter than 30 seconds, otherwise use 30 seconds
      // Convert auctionIntervalSeconds to milliseconds and default to 30 seconds if not set
      const updateIntervalMs = auctionIntervalSeconds > 0 && auctionIntervalSeconds < 30 
        ? auctionIntervalSeconds * 1000 
        : 30000;
      
      // Set up interval to refresh auction data
      auctionUpdateInterval = window.setInterval(async () => {
        await loadAuctionData();
      }, updateIntervalMs);
    } else {
      // Clear interval when auction is not active
      if (auctionUpdateInterval) {
        clearInterval(auctionUpdateInterval);
        auctionUpdateInterval = null;
      }
    }
  }

</script>

<div class="flex flex-col gap-3 p-1 sm:p-0">

<!-- Announcements Panel 
<AnnouncementPanel
  isVisible={showAnnouncement}
  title="Reverse auction completed"
  subtitle="All mAIners sold successfully on November 9th."
  variant="success"
  items={[
    { text: "Sold for 65–130 ICP per mAIner." },
    { text: "Auction closed after full sell-through." }
  ]}
  onClose={() => showAnnouncement = false}
/>
-->

<!-- Create Agent Accordion (only when creation is open and not in whitelist/auction mode) -->
{#if !isWhitelistPhaseActive && !isAuctionActive}
  {#if canCreateMainer}
    <MainerCreationPanel
      {isAuthenticated}
      {isProtocolActive}
      {stopMainerCreation}
      {isCreatingMainer}
      {mainerCreationProgress}
      {mainerPrice}
      {modelType}
      {selectedModel}
      {addressCopied}
      shouldAutoOpen={false}
      onCreateAgent={createAgent}
      onToggleLoginModal={toggleLoginModal}
      onToggleAccordion={toggleAccordion}
      onModelTypeChange={(type) => modelType = type}
    />
  {:else if !protocolFlagsLoading && !isCreatingMainer && mainersLoadStatus === 'success'}
    {#if MARKETPLACE_ENABLED}
      <EmptyFleetBanner hasMainers={totalMainers > 0} />
    {:else}
      <NetworkCapacityPanel isVisible={true} />
    {/if}
  {/if}
{/if}


<!-- Whitelist mAIners Section (only show when in whitelist phase) -->
<WhitelistMainerPanel
  {isWhitelistPhaseActive}
  {isAuthenticated}
  {unlockedMainers}
  {totalMainers}
  {agentCanistersInfo}
  {currentWhitelistPrice}
  {currentMainerPrice}
  {isPauseWhitelistMainerCreation}
  {stopMainerCreation}
  {isProtocolActive}
  {whitelistMainersBeingCreated}
  onCreateWhitelistAgent={createWhitelistAgent}
  onToggleLoginModal={toggleLoginModal}
/>

<!--Reverse Auction Section (show when auction is active and not in whitelist phase) -->
{#if isAuctionActive && !isWhitelistPhaseActive}
  <div class="mt-4">
    <ReverseAuctionPanel
      {isAuthenticated}
      {isProtocolActive}
      {stopMainerCreation}
      {isCreatingMainer}
      {mainerCreationProgress}
      {mainerPrice}
      {selectedModel}
      {addressCopied}
      shouldAutoOpen={agents.length === 0}
      {isAuctionActive}
      {availableMainers}
      {nextPriceDropAtNs}
      onCreateAgent={createAgent}
      onToggleLoginModal={toggleLoginModal}
      onToggleAccordion={toggleAccordion}
      onUpdateAuctionData={updateAuctionData}
    />
  </div>
{/if}

<!-- Warning Banner - Don't refresh/navigate during creation -->
{#if isCreatingMainer}
  <div class="mt-4 relative overflow-hidden agent-card border-red-500/40 bg-red-950/40 animate-pulse">
    <div class="relative p-3 sm:p-4">
      <div class="flex items-start space-x-3">
        <div class="shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-red-500/20 rounded-xl flex items-center justify-center border border-red-500/30">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 sm:h-6 sm:w-6 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
        </div>
        
        <div class="flex-1 min-w-0">
          <div class="flex flex-col space-y-2">
            <h3 class="text-sm sm:text-base font-semibold text-white">IMPORTANT: Do NOT refresh or navigate away</h3>
            <div class="text-gray-300 text-xs sm:text-sm leading-relaxed">
              <p class="font-medium mb-1 text-gray-200">Your mAIner is being created right now.</p>
              <p><span class="font-medium text-white">DO NOT refresh this page or navigate away</span> — this will stop the creation process and you'll need to start over.</p>
              <p class="mt-1 text-gray-400">Please keep this tab open and wait for the process to complete (~1 minute).</p>
            </div>
          </div>
        </div>
      </div>
    </div>
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
          <span class="flex-1 text-xs sm:text-sm wrap-break-word">{progress.message}</span>
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

{#if isAuthenticated && mainersLoadStatus === 'error'}
  <div class="mt-4 rounded-xl border border-amber-500/25 bg-amber-500/8 px-4 py-3 sm:px-5 sm:py-4">
    <p class="text-sm text-amber-200">
      {mainersLoadError || "Couldn't load your mAIners."}
      {#if agents.length > 0}
        Showing last known list.
      {:else}
        This is not an empty fleet — the query failed.
      {/if}
    </p>
    <button
      type="button"
      class="mt-2 agent-btn-ghost h-8! px-3! text-xs!"
      on:click={() => store.loadUserMainerCanisters()}
    >
      Retry
    </button>
  </div>
{/if}

{#if totalMainers > 0}
  <FleetOverview 
    {totalMainers}
    {activeMainers}
    {inactiveMainers}
    {lowBurnRateMainers}
    {mediumBurnRateMainers}
    {highBurnRateMainers}
    {veryHighBurnRateMainers}
  />
  <FleetBulkTopUp
    {agents}
    {isProtocolActive}
    isBusy={agentsBeingToppedUp.size > 0 && bulkTopUpIds.length === 0}
    onStart={handleBulkTopUpStart}
    onComplete={handleBulkTopUpComplete}
  />
{/if}

<!-- Existing Agents -->
{#each agents as agent, index (agent.id)}
  {#if agent && agent.id}
    {@const sanitizedId = agent.id.replace(/[^a-zA-Z0-9-_]/g, '_')}
    {@const identity = getMainerVisualIdentity(agent.id)}
    <div class="agent-card" class:opacity-75={agent.uiStatus === 'inactive'}>
      <button 
        on:click={() => toggleAccordion(agent.id)} 
        class="w-full relative overflow-hidden bg-agent-surface hover:bg-agent-elevated border-b border-white/6 transition-all duration-300 group"
      >
        <div class="absolute left-0 top-0 bottom-0 w-[3px] bg-agent-purple/60 group-hover:bg-agent-purple transition-colors"></div>
        
        <div class="relative flex items-center py-3 sm:py-4 px-4 sm:px-6">
          <!-- Left section: Avatar and Info -->
          <div class="flex items-center space-x-3 sm:space-x-4 min-w-0 flex-1">
            <!-- Unique avatar with visual identity and name -->
            <div class="relative shrink-0 flex flex-col items-center">
              <div class="w-12 h-12 sm:w-16 sm:h-16 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated group-hover:border-agent-purple/40 transition-all duration-300 [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
                {@html identity.icon}
              </div>
              
              <!-- mAIner number badge -->
              <div class="absolute -top-1 -right-1 w-6 h-6 sm:w-7 sm:h-7 bg-agent-elevated border border-white/10 rounded-full flex items-center justify-center">
                <span class="text-xs sm:text-sm font-semibold text-white">#{totalMainers - index}</span>
              </div>
              
              <!-- Status indicator dot -->
              <div class="absolute -bottom-1 -left-1 w-4 h-4 sm:w-5 sm:h-5 rounded-full border-2 border-agent-surface bg-agent-elevated flex items-center justify-center">
                <div class={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${agent.uiStatus === 'active' ? 'bg-emerald-400' : agent.uiStatus === 'setting-up' ? 'bg-amber-400' : 'bg-red-400'}`}></div>
              </div>
            </div>
            
            <!-- mAIner info -->
            <div class="flex flex-col items-start min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-1 sm:gap-2 mb-1">
                <!-- Status badge -->
                <span class={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${agent.uiStatus === 'active' 
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' 
                  : agent.uiStatus === 'setting-up'
                  ? 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                  : 'bg-red-500/15 text-red-300 border-red-500/30'}`}>
                  <div class={`w-2 h-2 rounded-full mr-1 ${agent.uiStatus === 'active' ? 'bg-emerald-400' : agent.uiStatus === 'setting-up' ? 'bg-amber-400' : 'bg-red-400'}`}></div>
                  {agent.uiStatus === 'setting-up' ? 'setting up' : agent.uiStatus}
                </span>
                
                <!-- Daily Burn Rate badge (only show if active) -->
                {#if agent.uiStatus === 'active' && agent.cyclesBurnRateSetting}
                  {@const burnRateColors = {
                    'Low': 'bg-white/4 text-gray-300 border-white/10',
                    'Medium': 'bg-agent-purple/15 text-agent-purple border-agent-purple/30', 
                    'High': 'bg-red-500/15 text-red-300 border-red-500/30'
                  }}
                  <span class={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${burnRateColors[agent.cyclesBurnRateSetting] || 'bg-white/4 text-gray-400 border-white/10'}`}>
                    {agent.cyclesBurnRateSetting}
                  </span>
                {/if}
                
                <!-- LLM setup status badge -->
                {#if agent.mainerType === 'Own' && agent.llmSetupStatus === 'inProgress'}
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    <svg class="w-3 h-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="10" stroke-width="4" stroke-opacity="0.25"/>
                      <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" stroke-opacity="0.75"/>
                    </svg>
                    LLM Setup
                  </span>
                {/if}
                
                <!-- Marketplace listing badge -->
                {#if listedMainerAddresses.has(agent.id)}
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-agent-purple/15 text-agent-purple border border-agent-purple/30">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    For Sale
                  </span>
                {/if}
                
                <!-- Cycles warning (only show if inactive due to low cycles, not if stopped) -->
                {#if agent.uiStatus === 'inactive' && $mainerHealthStatuses.get(agent.id)?.isHealthy !== false}
                  <span 
                    class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-500/15 text-red-300 border border-red-500/30 cursor-help"
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
              <div class="text-sm text-gray-400 truncate max-w-full mt-1">
                {#if $mainerHealthStatuses.get(agent.id)?.isHealthy === false}
                  <span class="opacity-60">Cycles: Unknown (mAIner stopped)</span>
                {:else}
                  {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 2, false)} TCYCLES
                {/if}
              </div>
              {#if agent.createdAt}
                <div class="text-xs text-gray-500">
                  Created: {formatDate(agent.createdAt)}
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Right section: Expand indicator -->
          <div class="shrink-0 ml-4">
            <div class="mb-2 px-2 py-0.5 bg-white/4 rounded-md border border-white/10 max-w-[80px] sm:max-w-[100px]">
              <span class="text-xs font-semibold text-gray-200 truncate block text-center">
                {agent.name.replace('mAIner ', '')}
              </span>
            </div>
            <div class="w-full h-10 bg-white/4 rounded-lg flex items-center justify-center border border-white/10 group-hover:border-agent-purple/40 group-hover:bg-agent-purple/10 transition-all duration-300">
              <span id="icon-{sanitizedId}" class="text-gray-400 group-hover:text-agent-purple transition-transform duration-300" style="transform: rotate(180deg)">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4 sm:w-5 sm:h-5">
                  <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
                </svg>
              </span>
            </div>
          </div>
        </div>
      </button>
      <div id="content-{sanitizedId}" class="accordion-content">
        <div class="text-xs sm:text-sm text-gray-300 p-3 space-y-2 border-t border-white/6">
            <div class="rounded-xl bg-white/3 px-3 py-2.5">
              <div class="flex items-center gap-2">
                <div class="min-w-0 flex-1 flex items-center gap-2 flex-wrap">
                  <h2 class="text-xs font-semibold text-white">Cycles</h2>
                  {#if agent.cycleBalance > 5_000_000_000_000}
                    <span class="inline-flex items-center rounded-full bg-emerald-500/15 px-1.5 py-px text-[10px] font-medium text-emerald-300">Healthy</span>
                  {:else if agent.cycleBalance > 1_000_000_000_000}
                    <span class="inline-flex items-center rounded-full bg-amber-500/15 px-1.5 py-px text-[10px] font-medium text-amber-300">Low</span>
                  {:else}
                    <span class="inline-flex items-center rounded-full bg-red-500/15 px-1.5 py-px text-[10px] font-medium text-red-300">Critical</span>
                  {/if}

                  {#if agentsBeingToppedUp.has(agent.id) || agentsBeingRefreshed.has(agent.id)}
                    <span class="flex items-center gap-1.5 text-gray-400">
                      <span class="w-3 h-3 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
                      <span class="text-[11px]">
                        {agentsBeingToppedUp.has(agent.id) ? 'Updating…' : 'Refreshing…'}
                      </span>
                    </span>
                  {:else if $mainerHealthStatuses.get(agent.id)?.isHealthy === false}
                    <span class="text-[11px] font-medium text-gray-400 truncate">
                      {$mainerHealthStatuses.get(agent.id)?.maintenanceMessage || 'Balance unknown'}
                    </span>
                  {:else}
                    <span class="flex items-baseline gap-1 min-w-0">
                      <span class="text-sm font-semibold text-white tabular-nums">
                        {formatLargeNumber(agent.cycleBalance / 1_000_000_000_000, 2, false)}
                      </span>
                      <span class="text-[11px] text-gray-500">T cycles</span>
                    </span>
                  {/if}
                </div>

                <button
                  type="button"
                  class="inline-flex items-center justify-center w-7 h-7 shrink-0 text-gray-400 bg-white/4 hover:bg-agent-purple/15 hover:text-agent-purple rounded-lg border border-white/10 hover:border-agent-purple/30 transition-colors"
                  class:opacity-50={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  class:cursor-not-allowed={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  disabled={agentsBeingRefreshed.has(agent.id) || agentsBeingToppedUp.has(agent.id)}
                  on:click={() => refreshAgentBalance(agent)}
                  use:tooltip={{ text: "Refresh cycles balance", direction: 'top', textSize: 'xs' }}
                >
                  {#if agentsBeingRefreshed.has(agent.id)}
                    <span class="w-3 h-3 border-2 border-agent-purple/30 border-t-agent-purple rounded-full animate-spin"></span>
                  {:else}
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  {/if}
                </button>

                {#if $mainerHealthStatuses.get(agent.id)?.isHealthy === true}
                  <button
                    type="button"
                    class="agent-btn-neon h-10! min-w-[7.5rem] px-4! rounded-xl! text-xs! font-semibold shrink-0"
                    class:opacity-50={agentsBeingToppedUp.has(agent.id) || !isProtocolActive}
                    class:cursor-not-allowed={agentsBeingToppedUp.has(agent.id) || !isProtocolActive}
                    disabled={agentsBeingToppedUp.has(agent.id) || !isProtocolActive}
                    on:click={() => openTopUpModal(agent)}
                  >
                    {#if agentsBeingToppedUp.has(agent.id)}
                      <span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    {:else}
                      <ArrowUp size={16} />
                      <span>Top up</span>
                    {/if}
                  </button>
                {/if}
              </div>

              <p class="mt-1.5 text-[10px] leading-snug text-amber-200/80">
                Top up only in this app — direct canister transfers incur high fees.
              </p>
            </div>

            <DailyBurnRatePanel
              {agent}
              {agentCanisterActors}
              {agentCanistersInfo}
              isHealthy={$mainerHealthStatuses.get(agent.id)?.isHealthy ?? true}
              on:burnRateUpdated={handleBurnRateUpdate}
            />

            <CanisterInfo {agent} />

            <CyclesDisplayAgent cycles={agent.burnedCycles} label="Burned Cycles" />
        </div>
      </div>
    </div>
  {/if}
{/each}

</div>

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
    .wrap-break-word {
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