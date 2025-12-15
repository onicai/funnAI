import { writable } from "svelte/store";
import { Principal } from "@dfinity/principal";
import type { Identity } from "@dfinity/agent";
import { HttpAgent, Actor } from "@dfinity/agent";
import { AuthClient } from "@dfinity/auth-client";
import { Signer } from "@slide-computer/signer";
import { PostMessageTransport } from "@slide-computer/signer-web";
import { IdentityKit, NFIDW, IdentityKitAuthType, type IdentityKitDelegationSignerClient as DelegationSignerClient } from "@nfid/identitykit";
import UAParser from 'ua-parser-js';
import { notificationStore } from "./notificationStore";
import {
  funnai_backend,
  createActor as createBackendCanisterActor,
  canisterId as backendCanisterId,
  idlFactory as backendIdlFactory,
} from "../../declarations/funnai_backend";

import {
  game_state_canister,
  createActor as createGameStateCanisterActor,
  canisterId as gameStateCanisterId,
  idlFactory as gameStateIdlFactory,
} from "../../declarations/game_state_canister";

import {
  mainer_ctrlb_canister,
  createActor as createMainerControllerCanisterActor,
  canisterId as mainerControllerCanisterId,
  idlFactory as mainerControllerIdlFactory,
} from "../../declarations/mainer_ctrlb_canister";

import {
  api_canister,
  createActor as createApiCanisterActor,
  canisterId as apiCanisterId,
  idlFactory as apiIdlFactory,
} from "../../declarations/api_canister";

import { ICRC2_IDL as icrc2IDL } from "../helpers/idls/icrc2.idl.js";
import { idlFactory as icpIDL } from "../helpers/idls/icp.idl.js";
import { idlFactory as swapPoolIDL } from "../helpers/idls/swappool.idl.js";
import { idlFactory as cmcIDL } from "../helpers/idls/cmc.idl.js";

import {
  ic_siwb_provider,
  createActor as createSiwbProviderActor,
  canisterId as siwbProviderCanisterId,
  idlFactory as siwbProviderIdlFactory,
} from "../../declarations/ic_siwb_provider";

// TODO: move this into a utils file
const getCyclesBurnRateLabel = (cyclesBurnRate) => {
  const cycles = BigInt(cyclesBurnRate.cycles);
  // TODO: these ranges need to be kept up to date with the backend (Game State: mAIner Burn Rates)
  if (cycles === 1_000_000_000_000n) {
    return "Low";
  } else if (cycles === 2_000_000_000_000n) {
    return "Medium";
  } else if (cycles === 4_000_000_000_000n) {
    return "High";
  } else if (cycles === 6_000_000_000_000n) {
    return "VeryHigh";
  } else {
    return "Medium";
  }
};

export const canisterIds = {
  backendCanisterId,
  gameStateCanisterId,
  apiCanisterId,
  siwbProviderCanisterId
};

export const canisterIDLs = {
  backendIdlFactory,
  gameStateIdlFactory,
  icrc1: icrc2IDL,
  icrc2: icrc2IDL,
  ICP: icpIDL,
  swapPool: swapPoolIDL,
  cmc: cmcIDL,
};

//__________Local vs Mainnet Development____________
/* export const HOST =
  backendCanisterId === "vee64-zyaaa-aaaai-acpta-cai"
    ? "https://ic0.app" // Use in Production (on Mainnet)
    : "http://localhost:4943"; // to be used with http://localhost:4943/?canisterId=ryjl3-tyaaa-aaaaa-aaaba-cai#/testroom */

export const HOST =
  process.env.NODE_ENV !== "development"
    ? "https://ic0.app"
    : "http://localhost:4943";

// User's device and browser information
export const webGpuSupportedBrowsers = "Google Chrome, Microsoft Edge";
const uaParser = new UAParser();
const result = uaParser.getResult();
export const device = result.device.model || 'Unknown Device';
export let deviceType = result.device.type; // Will return 'mobile' for mobile devices, 'tablet' for tablets, and undefined for desktops
let osName = result.os.name; // Get the operating system name

export const currentModelName = writable<string>("No model selected");

if (!deviceType) {
  deviceType = 'desktop';
} else if (deviceType === 'mobile' || deviceType === 'tablet') {
  if (osName === 'Android') {
    //deviceType = 'Android ' + deviceType; // e.g., 'Android mobile'
    deviceType = 'Android';
  } else if (osName === 'iOS') {
    //deviceType = 'iOS ' + deviceType; // e.g., 'iOS mobile'
    deviceType = 'iOS';
  };
};
export const browser = result.browser.name || 'Unknown Browser';
// @ts-ignore
export const supportsWebGpu = navigator.gpu !== undefined;

export let chatModelGlobal = writable(null);
export let chatModelDownloadedGlobal = writable(false);
export let chatModelIdInitiatedGlobal = writable(null);
export let activeChatGlobal = writable(null);

export const temperatureDefaultSetting = 0.6;
export const responseLengthDefaultSetting = 'Long';
export const systemPromptDefaultSetting = "You are a helpful, respectful and honest assistant.";
export const saveChatsDefaultSetting = true;
export let userSettings = writable(null);
export let selectedAiModelId = writable(localStorage.getItem("selectedAiModelId") || null);
let selectedAiModelIdValue = null;

export let saveChatsUserSelection = writable(localStorage.getItem("saveChatsUserSelection") === "false" ? false : true); // values: true for "save" or false for "doNotSave" with true as default
let saveChatsUserSelectionValue = saveChatsDefaultSetting;

export let useKnowledgeBase = writable(localStorage.getItem("useKnowledgeBase") === "true" ? true : false);

declare global {
  interface BigInt {
    toJSON(): Number;
  }
};

BigInt.prototype.toJSON = function () { return Number(this) };

export let downloadedModels = writable(JSON.parse(localStorage.getItem("downloadedAiModels") || "[]"));

export const currentExperienceId = writable(null);
export let vectorStore = writable(null);

export let installAppDeferredPrompt = writable(null); // the installAppDeferredPrompt event cannot be stored across sessions

let authClient : AuthClient;
const APPLICATION_NAME = "funnai";
const APPLICATION_LOGO_URL = "https://onicai.com/images/poaiw/coin.webp";
//TODO: double check
const AUTH_PATH = "/authenticate/?applicationName="+APPLICATION_NAME+"&applicationLogo="+APPLICATION_LOGO_URL+"#authorize";

export const MEMO_PAYMENT_PROTOCOL : number[] = [173];

const days = BigInt(30);
const hours = BigInt(24);
const nanosecondsPerHour = BigInt(3600000000000);

// Add session refresh configuration
const SESSION_REFRESH_THRESHOLD = BigInt(24 * 60 * 60 * 1000 * 1000 * 1000); // 24 hours in nanoseconds
const SESSION_CHECK_INTERVAL = 30 * 60 * 1000; // Check every 30 minutes in milliseconds

// Add localStorage keys for mAIner creation state persistence
const STORAGE_KEYS = {
  MAINER_CREATION_STATE: 'mainerCreationState',
  MAINER_CREATION_SESSION: 'mainerCreationSession'
};

type State = {
  isAuthed: "nfid" | "internetidentity" | "bitcoin" | null;
  backendActor: typeof funnai_backend | null;
  principal: Principal | null;
  accountId: string;
  error: string;
  isLoading: boolean;
  gameStateCanisterActor: typeof game_state_canister | null;
  mainerControllerCanisterActor: typeof mainer_ctrlb_canister | null;
  apiCanisterActor: typeof api_canister | null;
  userMainerCanisterActors: any[];
  userMainerAgentCanistersInfo: any[];
  sessionExpiry: bigint | null; // Track session expiration time
  sessionRefreshTimer: NodeJS.Timeout | null; // Timer for automatic session refresh
  // mAIner creation progress state
  isCreatingMainer: boolean;
  mainerCreationProgress: {message: string, timestamp: string, complete: boolean}[];
  shouldOpenFirstMainerAfterCreation: boolean;
  // Add creation session ID to track unique creation sessions
  mainerCreationSessionId: string | null;
  // Bitcoin wallet fields
  btcAddress: string | null; // User's Bitcoin address from SIWB
};

let defaultBackendCanisterId = backendCanisterId;

const defaultState: State = {
  isAuthed: null,
  backendActor: defaultBackendCanisterId ? createBackendCanisterActor(defaultBackendCanisterId, {
    agentOptions: { host: HOST },
  }) : null,
  principal: null,
  accountId: "",
  error: "",
  isLoading: false,
  gameStateCanisterActor: gameStateCanisterId ? createGameStateCanisterActor(gameStateCanisterId, {
    agentOptions: { host: HOST },
  }) : null,
  mainerControllerCanisterActor: mainerControllerCanisterId ? createMainerControllerCanisterActor(mainerControllerCanisterId, {
    agentOptions: { host: HOST },
  }) : null,
  apiCanisterActor: apiCanisterId ? createApiCanisterActor(apiCanisterId, {
    agentOptions: { host: HOST },
  }) : null,
  userMainerCanisterActors: [],
  userMainerAgentCanistersInfo: [],
  sessionExpiry: null,
  sessionRefreshTimer: null,
  // mAIner creation progress state
  isCreatingMainer: false,
  mainerCreationProgress: [],
  shouldOpenFirstMainerAfterCreation: false,
  mainerCreationSessionId: null,
  // Bitcoin wallet fields
  btcAddress: null,
};

// Add theme support
export const theme = writable(localStorage.getItem('theme') || 'dark');

// Setup store subscriptions after all variables are declared
function setupStoreSubscriptions() {
  userSettings.subscribe((value) => localStorage.setItem("userSettings", JSON.stringify(value)));
  
  selectedAiModelId.subscribe((value) => {
    selectedAiModelIdValue = value;
    if (value === null) {
      localStorage.removeItem("selectedAiModelId");
    } else {
      localStorage.setItem("selectedAiModelId", value);
    };
  });
  
  saveChatsUserSelection.subscribe((value) => {
    saveChatsUserSelectionValue = value;
    // @ts-ignore
    localStorage.setItem("saveChatsUserSelection", value)
  });
  
  useKnowledgeBase.subscribe((value) => {
    // @ts-ignore
    localStorage.setItem("useKnowledgeBase", value)
  });
  
  downloadedModels.subscribe((value) => {
    localStorage.setItem("downloadedAiModels", JSON.stringify(value));
  });
}

// Call setup function immediately
setupStoreSubscriptions();

export const toggleTheme = () => {
  theme.update(currentTheme => {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    
    // Apply theme to document
    if (typeof document !== 'undefined') {
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
    
    return newTheme;
  });
};

// Pre-initialize NFID IdentityKit to avoid async operations in click handler
let nfidIdentityKitPromise: Promise<any> | null = null;

const getOrCreateNfidIdentityKit = async () => {
  if (!nfidIdentityKitPromise) {
    nfidIdentityKitPromise = (async () => {
      const transport = new PostMessageTransport({
        url: NFIDW.providerUrl,
        windowOpenerFeatures:
          `left=${window.screen.width / 2 - 525 / 2}, `+
          `top=${window.screen.height / 2 - 705 / 2},` +
          `toolbar=0,location=0,menubar=0,width=525,height=705`,
      });
      const signer = new Signer({ transport });

      const identityKit = await IdentityKit.create({
        signerClientOptions: {
          signer,
          maxTimeToLive: days * hours * nanosecondsPerHour,
          idleOptions: {
            idleTimeout: Number(days * hours) * 60 * 60 * 1000,
            disableIdle: false,
            disableDefaultIdleCallback: true,
            onIdle: async () => {
              console.log("Session expired due to inactivity");
              // Will be set up properly when store is created
            }
          }
        },
        authType: IdentityKitAuthType.DELEGATION
      });

      return identityKit;
    })();
  }
  return nfidIdentityKitPromise;
};

export const createStore = ({
  whitelist,
  host,
}: {
  whitelist?: string[];
  host?: string;
}) => {
  const { subscribe, update } = writable<State>(defaultState);
  let globalState: State;
  
  // Defer the subscription to avoid temporal dead zone
  setTimeout(() => {
    subscribe((value) => globalState = value);
  }, 0);

  // Add helper functions for mAIner creation state persistence
  const storeMainerCreationState = (isCreating: boolean, sessionId: string | null, progress: any[] = []) => {
    try {
      const creationState = {
        isCreating,
        sessionId,
        progress,
        timestamp: Date.now(),
        principalId: globalState.principal?.toString() || null
      };
      localStorage.setItem(STORAGE_KEYS.MAINER_CREATION_STATE, JSON.stringify(creationState));
    } catch (error) {
      console.error("Error storing mAIner creation state:", error);
    }
  };

  const getStoredMainerCreationState = () => {
    console.log("Looking for previous mAIner creation state");
    try {
      const storedState = localStorage.getItem(STORAGE_KEYS.MAINER_CREATION_STATE);
      if (storedState) {
        const parsed = JSON.parse(storedState);
        // Check if the stored state is for the current user
        const currentPrincipal = globalState.principal?.toString() || null;
        if (parsed.principalId === currentPrincipal) {
          // Check if state is not too old (max 6 min)
          const maxAge = 6 * 60 * 1000; // 6 min in milliseconds
          if (Date.now() - parsed.timestamp < maxAge) {
            return parsed;
          }
        }
      }
    } catch (error) {
      console.error("Error retrieving stored mAIner creation state:", error);
    }
    return null;
  };

  const clearStoredMainerCreationState = () => {
    try {
      localStorage.removeItem(STORAGE_KEYS.MAINER_CREATION_STATE);
    } catch (error) {
      console.error("Error clearing stored mAIner creation state:", error);
    }
  };

  const restoreMainerCreationState = () => {
    const storedState = getStoredMainerCreationState();
    if (storedState && storedState.isCreating) {
      console.log("Restoring mAIner creation state from localStorage");
      update((state) => ({
        ...state,
        isCreatingMainer: true,
        mainerCreationSessionId: storedState.sessionId,
        mainerCreationProgress: storedState.progress || [],
        shouldOpenFirstMainerAfterCreation: true
      }));
      
      // Add a progress message indicating UI restoration (not actual backend resumption)
      setTimeout(() => {
        if (globalState.isCreatingMainer) {
          const now = new Date();
          const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
          
          update((state) => {
            const newProgress = [
              ...state.mainerCreationProgress,
              { message: "Previous creation session detected - UI restored but creation process was interrupted", timestamp, complete: false }
            ];
            
            // Update localStorage with new progress
            if (state.isCreatingMainer) {
              storeMainerCreationState(true, state.mainerCreationSessionId, newProgress);
            }
            
            return {
              ...state,
              mainerCreationProgress: newProgress
            };
          });
        }
      }, 100);
      // Set a timeout to automatically complete creation if it's been too long
      setTimeout(() => {
        if (globalState.isCreatingMainer) {
          const now = new Date();
          const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
          
          update((state) => {
            const newProgress = [
              ...state.mainerCreationProgress,
              { message: "Session cleanup - creation was interrupted and needs to be restarted", timestamp, complete: true }
            ];
            
            return {
              ...state,
              mainerCreationProgress: newProgress,
              isCreatingMainer: false,
              shouldOpenFirstMainerAfterCreation: false,
              mainerCreationSessionId: null
            };
          });
          
          // Clear the stored creation state
          clearStoredMainerCreationState();
        }
      }, 2 * 60 * 1000); // 2 minutes timeout
    }
  };

  const initUserSettings = async (backendActor) => {
    // Log user's login
    try {
      void backendActor.logLogin();      
    } catch (logError) {
      console.warn("Backend error: ", logError);  
    };
    // Load the user's settings
      // Especially selected AI model to be used for chat
    if (navigator.onLine) {
      try {
        const retrievedSettingsResponse = await backendActor.get_caller_chat_settings();
        // @ts-ignore
        if (retrievedSettingsResponse.Ok) {
          userSettings.set(retrievedSettingsResponse.Ok);
          const userSelectedAiModelId = retrievedSettingsResponse.Ok.selectedAiModelId;
          selectedAiModelId.set(userSelectedAiModelId);
        } else {
          console.error("Error retrieving user settings: ", retrievedSettingsResponse.Err);
          throw new Error("Error retrieving user settings: ", retrievedSettingsResponse.Err);
        };
      } catch (error) {
        console.error("Error in get_caller_settings: ", error);
        if (localStorage.getItem("userSettings")) {
          try {
            userSettings.set(JSON.parse(localStorage.getItem("userSettings")));            
          } catch (error) {
            userSettings.set({ // default settings
              temperature: temperatureDefaultSetting,
              responseLength: responseLengthDefaultSetting,
              saveChats: saveChatsUserSelectionValue,
              selectedAiModelId: selectedAiModelIdValue,
              systemPrompt: systemPromptDefaultSetting,
            });        
          };
        } else {
          userSettings.set({ // default settings
            temperature: temperatureDefaultSetting,
            responseLength: responseLengthDefaultSetting,
            saveChats: saveChatsUserSelectionValue,
            selectedAiModelId: selectedAiModelIdValue,
            systemPrompt: systemPromptDefaultSetting,
          });
        };
        if (localStorage.getItem("selectedAiModelId")) {
          selectedAiModelId.set(localStorage.getItem("selectedAiModelId"));
        };
      };
    } else {
      if (localStorage.getItem("userSettings")) {
        try {
          userSettings.set(JSON.parse(localStorage.getItem("userSettings")));            
        } catch (error) {
          userSettings.set({ // default settings
            temperature: temperatureDefaultSetting,
            responseLength: responseLengthDefaultSetting,
            saveChats: saveChatsUserSelectionValue,
            selectedAiModelId: selectedAiModelIdValue,
            systemPrompt: systemPromptDefaultSetting,
          });          
        };
      } else {
        userSettings.set({ // default settings
          temperature: temperatureDefaultSetting,
          responseLength: responseLengthDefaultSetting,
          saveChats: saveChatsUserSelectionValue,
          selectedAiModelId: selectedAiModelIdValue,
          systemPrompt: systemPromptDefaultSetting,
        });
      };
      if (localStorage.getItem("selectedAiModelId")) {
        selectedAiModelId.set(localStorage.getItem("selectedAiModelId"));
      };
    };
  };

  const initBackendCanisterActor = async (loginType, identity: Identity) => {
    let canisterId = backendCanisterId;
    
    if (!canisterId) {
      console.error("❌ Backend canister ID is undefined!");
      return null;
    }
    
    let backendActor = createBackendCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return backendActor;
  };

  const updateBackendCanisterActor = async (newBackendCanisterId) => {
    if (!newBackendCanisterId) {
      return;
    }
    if (authClient) {
      const identity = await authClient.getIdentity();
      let backendActor;
      
      backendActor = createBackendCanisterActor(newBackendCanisterId, {
        agentOptions: {
          identity,
          host: HOST,
        },
      });
      if (backendActor) {
        update((state) => {
          return {
            ...state,
            backendActor,
          };
        });
      };
      return backendActor;
    };
    return null; 
  };

  const initGameStateCanisterActor = async (loginType, identity: Identity) => {
    let canisterId = gameStateCanisterId;
    
    if (!canisterId) {
      console.error("❌ Game State canister ID is undefined!");
      return null;
    }
    
    let gameStateActor = createGameStateCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return gameStateActor;
  };

  const initApiCanisterActor = async (loginType, identity: Identity) => {
    let canisterId = apiCanisterId;
    
    // Fallback to canister_ids.json if environment variable is not set
    if (!canisterId) {
      // Import canister IDs from the JSON file
      const canisterIds = {
        "demo": "p6pu7-5aaaa-aaaap-qqdfa-cai",
        "prd": "bgm6p-5aaaa-aaaaf-qbzda-cai",
        "testing": "nyxgs-uqaaa-aaaap-qqdia-cai",
        "development": "p6pu7-5aaaa-aaaap-qqdfa-cai",
        "ic": "bgm6p-5aaaa-aaaaf-qbzda-cai"
      };
      
      // Determine current network/environment
      const network = process.env.DFX_NETWORK || 'development';
      canisterId = canisterIds[network] || canisterIds['development'];
      
      console.log("Using fallback API canister ID:", canisterId, "for network:", network);
    }
    
    if (!canisterId) {
      console.error("❌ No API canister ID found for current environment");
      return null;
    }
    
    let apiActor = createApiCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return apiActor;
  };

  const initMainerControllerCanisterActor = async (loginType, identity: Identity) => {
    let canisterId = mainerControllerCanisterId;
    
    let mainerControllerActor = createMainerControllerCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return mainerControllerActor;
  };

  const initMainerAgentCanisterActor = async (userMainerCanisterInfo, loginType, identity: Identity) => {
    let canisterId = userMainerCanisterInfo.address;
    try {
      Principal.fromText(canisterId);
    } catch {
      return;
    };
    
    let mainerControllerActor = createMainerControllerCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return mainerControllerActor;
  };

  const enrichMainerCanisterInfo = async (canisterInfo, mainerActor) => {
    // Start with default values for UI-specific properties
    let enrichedInfo = {
      ...canisterInfo,
      uiStatus: "active",  // Use uiStatus instead of status to avoid overwriting backend status
      cycleBalance: 0,
      burnedCycles: 0,
      cyclesBurnRate: {},
      cyclesBurnRateSetting: "Medium",
      llmCanisters: [],
      llmSetupStatus: '',
      hasError: false
    };

    // Check if this is an unlocked mAIner (no address and status is Unlocked)
    const isUnlocked = canisterInfo.status && 'Unlocked' in canisterInfo.status;
    if (isUnlocked) {
      enrichedInfo.uiStatus = "unlocked";
      // For unlocked mAIners, we don't need to fetch additional data as they don't have actors yet
      return enrichedInfo;
    }

    // Determine LLM setup status from canister info
    if (canisterInfo.status) {
      if ('LlmSetupInProgress' in canisterInfo.status) {
        enrichedInfo.llmSetupStatus = 'inProgress';
      } else if ('LlmSetupFinished' in canisterInfo.status) {
        enrichedInfo.llmSetupStatus = 'completed';
      }
    }

    // If no actor available, mark as having an error but still return the mAIner
    if (!mainerActor) {
      enrichedInfo.hasError = true;
      enrichedInfo.uiStatus = "inactive";
      return enrichedInfo;
    }

    try {
      // Check issue flags to determine if mAIner is inactive
      const issueFlagsResult = await mainerActor.getIssueFlagsAdmin();
      if ('Ok' in issueFlagsResult && issueFlagsResult.Ok.lowCycleBalance) {
        console.log(`[Status] ${canisterInfo.address.slice(0, 5)}: lowCycleBalance flag is TRUE - marking inactive`);
        enrichedInfo.uiStatus = "inactive";
      }
    } catch (error) {
      console.error(`Error fetching issue flags for ${canisterInfo.address.slice(0, 5)}:`, error);
      enrichedInfo.hasError = true;
      // Don't mark as inactive just because API failed - keep default active status
    }

    try {
      // Get detailed statistics
      const statsResult = await mainerActor.getMainerStatisticsAdmin();
      if ('Ok' in statsResult) {
        enrichedInfo.burnedCycles = Number(statsResult.Ok.totalCyclesBurnt);
        enrichedInfo.cycleBalance = Number(statsResult.Ok.cycleBalance);
        enrichedInfo.cyclesBurnRate = statsResult.Ok.cyclesBurnRate;
        
        // Convert burn rate to setting label
        try {
          enrichedInfo.cyclesBurnRateSetting = getCyclesBurnRateLabel(statsResult.Ok.cyclesBurnRate);
        } catch (error) {
          console.error("Error converting to cyclesBurnRateSetting: ", error);
        }
        
        // Check if cycle balance is below minimum threshold (250 billion cycles)
        // This catches cases where the mAIner has low cycles but hasn't tried to pull a challenge yet
        const CYCLE_BALANCE_MINIMUM = 250_000_000_000;
        if (enrichedInfo.cycleBalance < CYCLE_BALANCE_MINIMUM) {
          console.log(`[Status] ${canisterInfo.address.slice(0, 5)}: Balance ${(enrichedInfo.cycleBalance / 1_000_000_000).toFixed(2)}B < ${CYCLE_BALANCE_MINIMUM / 1_000_000_000}B threshold - marking inactive`);
          enrichedInfo.uiStatus = "inactive";
        } else {
          console.log(`[Status] ${canisterInfo.address.slice(0, 5)}: Balance ${(enrichedInfo.cycleBalance / 1_000_000_000).toFixed(2)}B >= ${CYCLE_BALANCE_MINIMUM / 1_000_000_000}B threshold - keeping ${enrichedInfo.uiStatus}`);
        }
      }
    } catch (error) {
      console.error(`Error fetching statistics for ${canisterInfo.address.slice(0, 5)}:`, error);
      enrichedInfo.hasError = true;
      // Don't mark as inactive just because stats API failed
    }

    // Fetch LLM canisters if this is an "Own" type mAIner
    if (canisterInfo.canisterType && 'Own' in canisterInfo.canisterType.MainerAgent) {
      try {
        if (mainerActor.getLlmCanisterIds && typeof mainerActor.getLlmCanisterIds === 'function') {
          const llmResult = await mainerActor.getLlmCanisterIds();
          if ('Ok' in llmResult && Array.isArray(llmResult.Ok)) {
            enrichedInfo.llmCanisters = llmResult.Ok;
            // If we have LLM canisters but status doesn't show 'completed', update it
            if (llmResult.Ok.length > 0 && enrichedInfo.llmSetupStatus !== 'completed') {
              enrichedInfo.llmSetupStatus = 'completed';
            }
          }
        }
      } catch (error) {
        console.error("Error fetching LLM canister IDs: ", error);
      }
    }

    console.log(`[Status] ${canisterInfo.address.slice(0, 5)}: Final uiStatus = "${enrichedInfo.uiStatus}"`);
    return enrichedInfo;
  };

  const initializeUserMainerAgentCanisters = async (gameStateCanisterActor: typeof game_state_canister, loginType, identity: Identity) => {
    let userCanisters = [];
    let mainerActors = [];
    let enrichedUserCanisters = [];
    
    try {
      const getMainersResult = await gameStateCanisterActor.getMainerAgentCanistersForUser();
      // @ts-ignore
      if (getMainersResult.Ok) {
        // @ts-ignore
        const rawUserCanisters = getMainersResult.Ok;
        
        // Filter canisters: keep valid addresses and unlocked mAIners (which may not have addresses yet)
        userCanisters = rawUserCanisters.filter(canister => {
          // Keep canisters with valid addresses
          if (canister.address && canister.address.trim() !== "") {
            return true;
          }
          // Also keep unlocked mAIners (status: Unlocked) even if they don't have addresses yet
          if (canister.status && 'Unlocked' in canister.status) {
            return true;
          }
          return false;
        });
        
        console.log(`Filtered ${rawUserCanisters.length - userCanisters.length} invalid canisters`);
        
        // Initialize actors for valid canisters
        let initPromises = [];
        userCanisters.forEach(userCanister => {
          initPromises.push(initMainerAgentCanisterActor(userCanister, loginType, identity)); 
        });
        mainerActors = await Promise.all(initPromises);
        
        // Enrich canister info with status, cycles, etc.
        let enrichPromises = [];
        userCanisters.forEach((canister, index) => {
          enrichPromises.push(enrichMainerCanisterInfo(canister, mainerActors[index]));
        });
        enrichedUserCanisters = await Promise.all(enrichPromises);
        
        console.log(`Successfully enriched ${enrichedUserCanisters.length} mAIner canisters with status information`);
        
        return { mainerActors, userCanisters: enrichedUserCanisters };
      } else {
        // @ts-ignore
        console.error("Error retrieving user mAIner agent canisters: ", getMainersResult.Err);
      };
    } catch (error) {
      console.error("Error in initializeUserMainerAgentCanisters: ", error);
    };
    return { mainerActors, userCanisters: enrichedUserCanisters };
  };

  const nfidConnect = async (isSessionRestore = false) => {
    try {
      // Get or create the IdentityKit (uses singleton pattern)
      // This ensures IdentityKit is ready before we call login()
      const identityKit = await getOrCreateNfidIdentityKit();
      
      if (identityKit.signerClient) {
        const signerClient = identityKit.signerClient;
        
        // If this is a session restore (page refresh), check if already authenticated
        if (isSessionRestore) {
          // Try to get existing identity without opening popup
          //@ts-ignore - isAuthenticated exists at runtime
          const isAuthenticated = signerClient.isAuthenticated();
          if (isAuthenticated) {
            console.log("Restoring NFID session from existing delegation");
            const identity = signerClient.getIdentity();
            
            // Store the identity kit instance for later use
            (globalThis as any).__nfid_identity_kit__ = identityKit;
            (globalThis as any).__nfid_signer_client__ = signerClient;
            
            const initSuccess = await initNfid(identity);
            if (!initSuccess) {
              console.warn("NFID session restore failed - delegation likely expired");
              clearSessionInfo();
              
              notificationStore.add(
                "Your session has expired. Please log in again.",
                "warning",
                5000
              );
              
              update((prevState) => ({
                ...defaultState,
              }));
            }
            return;
          } else {
            // Session expired or not found, user needs to login again
            console.warn("NFID session expired, user needs to login again");
            clearSessionInfo();
            
            // Show user-friendly notification
            notificationStore.add(
              "Your session has expired. Please log in again to continue.",
              "warning",
              8000 // Show for 8 seconds
            );
            
            // Reset to default logged out state
            update((prevState) => {
              return {
                ...defaultState,
              };
            });
            
            return;
          }
        }
        
        // For new logins (user clicked button), open the popup
        // CRITICAL: Call login() to open the popup - this should happen quickly
        // since IdentityKit is already initialized
        await signerClient.login();
        
        // Get the identity
        const identity = signerClient.getIdentity();
        
        // Store the identity kit instance for later use
        (globalThis as any).__nfid_identity_kit__ = identityKit;
        (globalThis as any).__nfid_signer_client__ = signerClient;
        
        const initSuccess = await initNfid(identity);
        if (!initSuccess) {
          throw new Error("Failed to initialize NFID session - please try again");
        }
      } else {
        throw new Error("SignerClient not available on IdentityKit");
      }
    } catch (error) {
      console.error("Error in nfidConnect:", error);
      // Reset the singleton so it can be retried
      nfidIdentityKitPromise = null;
      update((state) => ({
        ...state,
        error: "Failed to connect with NFID"
      }));
    }
  };

  const initNfid = async (identity: Identity): Promise<boolean> => {
    try {
      const backendActor = await initBackendCanisterActor("nfid", identity);

      if (!backendActor) {
        console.warn("❌ Couldn't create backend actor - delegation may be expired");
        return false;
      };

      await initUserSettings(backendActor);

      const gameStateCanisterActor = await initGameStateCanisterActor("nfid", identity);
      
      if (!gameStateCanisterActor) {
        console.warn("❌ Couldn't create Game State actor - delegation may be expired");
        return false;
      };

      const apiCanisterActor = await initApiCanisterActor("nfid", identity);
      
      if (!apiCanisterActor) {
        console.warn("❌ Couldn't create API canister actor - delegation may be expired");
        return false;
      };

      // Initialize user's mAIner agent (controller) canisters
      const { mainerActors, userCanisters } = await initializeUserMainerAgentCanisters(gameStateCanisterActor, "nfid", identity);
      const userMainerCanisterActors = mainerActors;
      const userMainerAgentCanistersInfo = userCanisters;

      //let accounts = JSON.parse(await identity.accounts());

      // Calculate session expiry time (30 days from now in nanoseconds)
      const sessionExpiry = BigInt(Date.now()) * BigInt(1000000) + days * hours * nanosecondsPerHour;
      
      // Store session information for persistence
      storeSessionInfo("nfid", sessionExpiry);

      update((state) => ({
        ...state,
        backendActor,
        principal: identity.getPrincipal(),
        //accountId: accounts[0].address, // we take the default account associated with the identity
        accountId: null,
        isAuthed: "nfid",
        gameStateCanisterActor,
        apiCanisterActor,
        userMainerCanisterActors,
        userMainerAgentCanistersInfo,
        sessionExpiry
      }));

      // Start automatic session refresh timer
      startSessionRefreshTimer();

      // Restore mAIner creation state if it exists
      restoreMainerCreationState();

      console.info("✅ NFID authentication successful");
      return true;
    } catch (error) {
      console.error("❌ Error during NFID initialization:", error);
      return false;
    }
  };

  const internetIdentityConnect = async () => {
    authClient = await AuthClient.create();
    if (await authClient.isAuthenticated()) {
      const identity = await authClient.getIdentity();
      initInternetIdentity(identity);
    } else {
      await authClient.login({
        onSuccess: async () => {
          const identity = await authClient.getIdentity();
          initInternetIdentity(identity);
        },
        identityProvider:
          process.env.DFX_NETWORK === "local"
            ? `http://${process.env.INTERNET_IDENTITY_CANISTER_ID}.localhost:4943/#authorize`
            : "https://identity.ic0.app/#authorize",
        // Maximum authorization expiration is 30 days
        maxTimeToLive: days * hours * nanosecondsPerHour,
        windowOpenerFeatures:
          `left=${window.screen.width / 2 - 525 / 2}, ` +
          `top=${window.screen.height / 2 - 705 / 2},` +
          `toolbar=0,location=0,menubar=0,width=525,height=705`,
      });
    };
  };

  const initInternetIdentity = async (identity: Identity) => {
    const backendActor = await initBackendCanisterActor("internetidentity", identity);

    if (!backendActor) {
      console.warn("couldn't create backend actor");
      return;
    };

    await initUserSettings(backendActor);

    const gameStateCanisterActor = await initGameStateCanisterActor("internetidentity", identity);
    
    if (!gameStateCanisterActor) {
      console.warn("couldn't create Game State actor");
      return;
    };

    const apiCanisterActor = await initApiCanisterActor("internetidentity", identity);
    
    if (!apiCanisterActor) {
      console.warn("couldn't create API canister actor");
      return;
    };

    // Initialize user's mAIner agent (controller) canisters
    const { mainerActors, userCanisters } = await initializeUserMainerAgentCanisters(gameStateCanisterActor, "internetidentity", identity);
    
    const userMainerCanisterActors = mainerActors;
    const userMainerAgentCanistersInfo = userCanisters;

    //let accounts = JSON.parse(await identity.accounts());

    // Calculate session expiry time (30 days from now in nanoseconds)
    const sessionExpiry = BigInt(Date.now()) * BigInt(1000000) + days * hours * nanosecondsPerHour;
    
    // Store session information for persistence
    storeSessionInfo("internetidentity", sessionExpiry);

    update((state) => ({
      ...state,
      backendActor,
      principal: identity.getPrincipal(),
      //accountId: accounts[0].address, // we take the default account associated with the identity
      accountId: null,
      isAuthed: "internetidentity",
      gameStateCanisterActor,
      apiCanisterActor,
      userMainerCanisterActors,
      userMainerAgentCanistersInfo,
      sessionExpiry
    }));

    // Start automatic session refresh timer
    startSessionRefreshTimer();

    // Restore mAIner creation state if it exists
    restoreMainerCreationState();

    console.info("internetidentity is authed");
  };

  // Bitcoin SIWB (Sign In With Bitcoin) authentication
  let siwbClientPromise: Promise<any> | null = null;

  const getSiwbProviderActor = async (identity?: Identity) => {
    // Use the SIWB provider canister ID - either from env or hardcoded
    // IMPORTANT: Deploy the ic_siwb_provider canister and set CANISTER_ID_IC_SIWB_PROVIDER
    const providerCanisterId = siwbProviderCanisterId || process.env.CANISTER_ID_IC_SIWB_PROVIDER;
    
    if (!providerCanisterId) {
      throw new Error(
        "Bitcoin Sign-In is not configured. The SIWB provider canister needs to be deployed. " +
        "Run: dfx deploy ic_siwb_provider --network <network> --argument '(record { domain = \"your-domain.com\"; uri = \"https://your-domain.com\"; salt = \"your-unique-salt\"; ... })'"
      );
    }

    const agentOptions: any = { host: HOST };
    if (identity) {
      agentOptions.identity = identity;
    }

    return createSiwbProviderActor(providerCanisterId, { agentOptions });
  };

  /**
   * Connect with Bitcoin wallet using SIWB (Sign In With Bitcoin)
   * 
   * This function can be called in two ways:
   * 1. With identity and btcAddress - when the BitcoinWalletButton has already performed
   *    the SIWB flow and created the identity
   * 2. Without parameters - performs the full SIWB flow internally (legacy mode)
   * 
   * @param identityOrSessionRestore - Either an Identity object or boolean for session restore
   * @param btcAddress - The Bitcoin address (required when identity is provided)
   */
  const siwbConnect = async (identityOrSessionRestore?: Identity | boolean, btcAddress?: string) => {
    // Check if called with identity directly (from BitcoinWalletButton)
    if (identityOrSessionRestore && typeof identityOrSessionRestore !== 'boolean' && btcAddress) {
      console.log("🔗 SIWB connect called with pre-authenticated identity");
      await initSiwb(identityOrSessionRestore as Identity, btcAddress);
      return;
    }

    // Legacy mode: perform full SIWB flow internally (mainly for UniSat)
    const isSessionRestore = typeof identityOrSessionRestore === 'boolean' ? identityOrSessionRestore : false;
    
    try {
      console.log("🔗 Starting Bitcoin SIWB connection (legacy mode)...");
      
      // Check if UniSat wallet is available
      const unisat = (window as any).unisat;
      if (!unisat) {
        throw new Error("No Bitcoin wallet found. Please install UniSat wallet or another compatible Bitcoin wallet.");
      }

      // Import identity modules early - we need session key before login
      const { DelegationChain, DelegationIdentity, Ed25519KeyIdentity } = await import("@dfinity/identity");
      
      // Create session key FIRST - needed for siwb_login
      const sessionKey = Ed25519KeyIdentity.generate();
      const sessionPublicKey = sessionKey.getPublicKey().toDer();

      // Request accounts from Bitcoin wallet
      const accounts = await unisat.requestAccounts();
      if (!accounts || accounts.length === 0) {
        throw new Error("No Bitcoin accounts found");
      }
      const walletBtcAddress = accounts[0];
      console.log("📋 Bitcoin address:", walletBtcAddress);

      // Get public key from wallet
      let publicKeyHex: string = '';
      try {
        publicKeyHex = await unisat.getPublicKey();
        console.log("📋 Public key:", publicKeyHex.substring(0, 20) + "...");
      } catch (e) {
        console.warn("Could not get public key from wallet");
      }

      // Get SIWB provider actor (anonymous for prepare_login)
      const siwbProvider = await getSiwbProviderActor();
      
      // Prepare login - returns a pre-formatted message string
      console.log("📝 Preparing SIWB login message...");
      const prepareResult = await siwbProvider.siwb_prepare_login(walletBtcAddress);
      
      if ('Err' in prepareResult) {
        throw new Error(`Failed to prepare SIWB login: ${prepareResult.Err}`);
      }
      
      // The message is already formatted by the canister
      const messageToSign: string = prepareResult.Ok as string;
      console.log("📋 SIWB message to sign:", messageToSign);

      // Request signature from Bitcoin wallet
      console.log("✍️ Requesting signature from Bitcoin wallet...");
      const signature = await unisat.signMessage(messageToSign, "bip322-simple");
      console.log("✅ Got signature from wallet");

      // Login with SIWB - new interface takes 5 parameters
      // siwb_login: (SiwbSignature, Address, PublickeyHex, SessionKey, SignMessageType)
      console.log("🔐 Logging in with SIWB...");
      const loginResult = await siwbProvider.siwb_login(
        signature,                              // SiwbSignature (string)
        walletBtcAddress,                       // Address
        publicKeyHex,                           // PublickeyHex (wallet's public key)
        new Uint8Array(sessionPublicKey),       // SessionKey (our session public key)
        { 'Bip322Simple': null }                // SignMessageType
      );
      
      if ('Err' in loginResult) {
        throw new Error(`SIWB login failed: ${loginResult.Err}`);
      }

      const loginDetails = loginResult.Ok;
      console.log("✅ SIWB login successful, getting delegation...");

      // Get the delegation
      const delegationResult = await siwbProvider.siwb_get_delegation(
        walletBtcAddress,
        new Uint8Array(sessionPublicKey),
        loginDetails.expiration
      );

      if ('Err' in delegationResult) {
        throw new Error(`Failed to get delegation: ${delegationResult.Err}`);
      }

      const signedDelegationResult = delegationResult.Ok;
      console.log("✅ Got signed delegation");

      // Convert to proper types for DelegationChain
      // Ensure expiration is BigInt
      const expiration = typeof signedDelegationResult.delegation.expiration === 'bigint' 
        ? signedDelegationResult.delegation.expiration 
        : BigInt(signedDelegationResult.delegation.expiration.toString());
      
      // Convert signature to Uint8Array if it isn't already
      const delegationSignature = signedDelegationResult.signature instanceof Uint8Array
        ? signedDelegationResult.signature
        : new Uint8Array(signedDelegationResult.signature);
      
      const canisterPubkey = loginDetails.user_canister_pubkey instanceof Uint8Array
        ? loginDetails.user_canister_pubkey
        : new Uint8Array(loginDetails.user_canister_pubkey);

      console.log("Creating delegation chain with:", {
        expiration: expiration.toString(),
        signatureLength: delegationSignature.length,
        canisterPubkeyLength: canisterPubkey.length,
        sessionPubkeyLength: sessionPublicKey.byteLength
      });

      // Import Delegation class for proper construction
      const { Delegation } = await import("@dfinity/identity");
      
      // Create the Delegation object with proper types
      // The delegation pubkey should be our session public key (the key being delegated TO)
      const delegation = new Delegation(
        sessionPublicKey,  // Use our session public key as the delegated key
        expiration,
        signedDelegationResult.delegation.targets?.length > 0 
          ? signedDelegationResult.delegation.targets 
          : undefined
      );

      // Create the signed delegation with proper ArrayBuffer types
      const signedDelegationForChain = {
        delegation,
        signature: delegationSignature.buffer.slice(
          delegationSignature.byteOffset,
          delegationSignature.byteOffset + delegationSignature.byteLength
        )
      };

      // Create delegation chain using fromDelegations
      // Use type assertion to satisfy the strict Signature type
      const delegationChain = DelegationChain.fromDelegations(
        [signedDelegationForChain] as any,
        canisterPubkey.buffer.slice(
          canisterPubkey.byteOffset,
          canisterPubkey.byteOffset + canisterPubkey.byteLength
        )
      );

      // Create the delegated identity
      const identity = DelegationIdentity.fromDelegation(sessionKey, delegationChain);
      
      console.log("✅ Created delegated identity with principal:", identity.getPrincipal().toString());

      // Store SIWB session info - including the delegated identity for later use
      (globalThis as any).__siwb_btc_address__ = walletBtcAddress;
      (globalThis as any).__siwb_session_key__ = sessionKey;
      (globalThis as any).__siwb_delegated_identity__ = identity;

      // Initialize with the SIWB identity
      await initSiwb(identity, walletBtcAddress);

    } catch (error) {
      console.error("❌ SIWB connection failed:", error);
      update((state) => ({
        ...state,
        error: error instanceof Error ? error.message : "Failed to connect with Bitcoin wallet"
      }));
      throw error;
    }
  };

  const initSiwb = async (identity: Identity, btcAddress: string) => {
    try {
      const backendActor = await initBackendCanisterActor("bitcoin", identity);

      if (!backendActor) {
        console.warn("❌ Couldn't create backend actor for SIWB");
        return;
      }

      await initUserSettings(backendActor);

      const gameStateCanisterActor = await initGameStateCanisterActor("bitcoin", identity);
      
      if (!gameStateCanisterActor) {
        console.warn("❌ Couldn't create Game State actor for SIWB");
        return;
      }

      const apiCanisterActor = await initApiCanisterActor("bitcoin", identity);
      
      if (!apiCanisterActor) {
        console.warn("❌ Couldn't create API canister actor for SIWB");
        return;
      }

      // Initialize user's mAIner agent (controller) canisters
      const { mainerActors, userCanisters } = await initializeUserMainerAgentCanisters(gameStateCanisterActor, "bitcoin", identity);
      const userMainerCanisterActors = mainerActors;
      const userMainerAgentCanistersInfo = userCanisters;

      // Calculate session expiry time (30 days from now in nanoseconds)
      const sessionExpiry = BigInt(Date.now()) * BigInt(1000000) + days * hours * nanosecondsPerHour;
      
      // Store session information for persistence
      storeSessionInfo("bitcoin", sessionExpiry);

      update((state) => ({
        ...state,
        backendActor,
        principal: identity.getPrincipal(),
        accountId: null,
        isAuthed: "bitcoin",
        btcAddress,
        gameStateCanisterActor,
        apiCanisterActor,
        userMainerCanisterActors,
        userMainerAgentCanistersInfo,
        sessionExpiry
      }));

      // Start automatic session refresh timer
      startSessionRefreshTimer();

      // Restore mAIner creation state if it exists
      restoreMainerCreationState();

      console.info("✅ Bitcoin SIWB authentication successful");
    } catch (error) {
      console.error("❌ Error during SIWB initialization:", error);
      throw error;
    }
  };

  const disconnect = async () => {
    // Stop the session refresh timer
    stopSessionRefreshTimer();
    
    // Clear stored session information
    clearSessionInfo();
    
    // Check isAuthed to determine which method to use to disconnect
    if (globalState.isAuthed === "nfid") {
      try {
        // Use the new IdentityKit logout if available
        const signerClient = (globalThis as any).__nfid_signer_client__;
        if (signerClient) {
          await signerClient.logout();
          delete (globalThis as any).__nfid_identity_kit__;
          delete (globalThis as any).__nfid_signer_client__;
          // Reset the singleton so a fresh IdentityKit is created on next login
          nfidIdentityKitPromise = null;
        } else {
          // Fallback to legacy AuthClient logout
          await authClient.logout();
        }
      } catch (error) {
        console.error("NFID disconnect error: ", error);
      };
    } else if (globalState.isAuthed === "internetidentity") {
      try {
        await authClient.logout();
      } catch (error) {
        console.error("Internet Identity disconnect error: ", error);
      };
    } else if (globalState.isAuthed === "bitcoin") {
      try {
        // Clean up SIWB session
        delete (globalThis as any).__siwb_btc_address__;
        delete (globalThis as any).__siwb_session_key__;
        siwbClientPromise = null;
        console.log("Bitcoin SIWB session cleared");
      } catch (error) {
        console.error("Bitcoin disconnect error: ", error);
      };
    };

    update((prevState) => {
      return {
        ...defaultState,
      };
    });
  };

  const checkExistingLoginAndConnect = async () => {
    console.log("🔄 Checking for existing login session...");

    // Check login state if user is already logged in
    const sessionInfo = getStoredSessionInfo();

    if (sessionInfo) {
      console.log(`📋 Found stored session info for ${sessionInfo.loginType}`);

      // IMPORTANT: For Internet Identity, check if AuthClient still has the delegation
      // NFID uses its own delegation mechanism (SignerClient), so skip this check for NFID
      if (sessionInfo.loginType === "internetidentity") {
        const authClient = await AuthClient.create();
        const isAuthenticated = await authClient.isAuthenticated();

        if (!isAuthenticated) {
          console.warn(`❌ Internet Identity delegation missing from AuthClient`);
          console.warn(`🧹 Clearing stale Internet Identity session`);
          clearSessionInfo();
          
          // Reset to default logged out state
          update((prevState) => {
            return {
              ...defaultState,
            };
          });
          return;
        }
      }

      // Check if session is still valid (not expired)
      const now = BigInt(Date.now()) * BigInt(1000000); // Convert to nanoseconds

      if (sessionInfo.expiry > now) {
        console.info(`✅ ${sessionInfo.loginType} session is valid (expires: ${new Date(Number(sessionInfo.expiry / BigInt(1000000))).toISOString()})`);

        // Update the session expiry in state
        update((state) => ({ ...state, sessionExpiry: sessionInfo.expiry }));

        if (sessionInfo.loginType === "nfid") {
          // For NFID, we need to restore the session properly
          console.log("🔄 Restoring NFID session...");
          try {
            const identityKit = await getOrCreateNfidIdentityKit();

            if (identityKit?.signerClient) {
              // Try to get the identity directly - NFID should persist its session
              const identity = identityKit.signerClient.getIdentity();
              if (identity) {
                const principal = identity.getPrincipal().toString();
                console.log("🔍 Found NFID identity for principal:", principal);
                (globalThis as any).__nfid_identity_kit__ = identityKit;
                (globalThis as any).__nfid_signer_client__ = identityKit.signerClient;
                
                // Try to initialize NFID and load user data
                const initSuccess = await initNfid(identity);
                
                if (initSuccess) {
                  console.log("🎉 NFID session fully restored!");
                  
                  // Show welcome back notification only if initialization succeeded
                  notificationStore.add(
                    "Welcome back! Your session has been restored.",
                    "success",
                    4000
                  );
                  
                  return;
                } else {
                  console.warn("❌ NFID session restoration failed - delegation likely expired");
                  notificationStore.add(
                    "Your session has expired. Please log in again.",
                    "warning",
                    5000
                  );
                }
              } else {
                console.warn("❌ NFID session could not be restored - no identity available");
              }
            } else {
              console.warn("❌ NFID IdentityKit not available for session restoration");
            }
          } catch (nfidError) {
            console.error("❌ Failed to restore NFID session:", nfidError);
          }

          // If restoration failed, clear the session and reset auth state
          console.warn("🧹 Clearing invalid NFID session");
          clearSessionInfo();
          
          // IMPORTANT: Also logout from AuthClient to clear the delegation from IndexedDB
          try {
            const authClient = await AuthClient.create();
            await authClient.logout();
            console.log("✅ AuthClient delegation cleared");
          } catch (logoutError) {
            console.warn("Failed to logout from AuthClient:", logoutError);
          }
          
          // Reset to default logged out state
          update((prevState) => {
            return {
              ...defaultState,
            };
          });
        } else if (sessionInfo.loginType === "internetidentity") {
          console.log("🔄 Restoring Internet Identity session...");
          await internetIdentityConnect();
          console.log("✅ Internet Identity session restored!");
        } else if (sessionInfo.loginType === "bitcoin") {
          // Bitcoin SIWB sessions cannot be automatically restored
          // The user needs to sign a new message with their wallet
          console.log("🔄 Bitcoin session detected - requires manual re-authentication");
          console.warn("🧹 Bitcoin sessions cannot be automatically restored");
          clearSessionInfo();
          
          notificationStore.add(
            "Your Bitcoin session has expired. Please sign in again with your wallet.",
            "info",
            5000
          );
          
          // Reset to default logged out state
          update((prevState) => {
            return {
              ...defaultState,
            };
          });
        }
      } else {
        console.info("⏰ Stored session has expired, clearing session info");
        clearSessionInfo();
        
        // Clear the delegation from AuthClient/IndexedDB
        try {
          await authClient.logout();
          console.log("✅ Expired session delegation cleared");
        } catch (logoutError) {
          console.warn("Failed to logout expired session:", logoutError);
        }

        // Reset to default logged out state
        update((prevState) => {
          return {
            ...defaultState,
          };
        });
      }
    } else {
      console.log("📭 No stored session info found");

      // Fallback to old method for backward compatibility
      const isAuthed = localStorage.getItem('isAuthed');
      if (isAuthed) {
        console.log(`📋 Found legacy auth info for ${isAuthed}`);
        
        if (isAuthed === "nfid") {
          // For NFID, don't check AuthClient - it uses its own delegation mechanism
          console.info("🔄 NFID connection detected (legacy method)");
          try {
            await nfidConnect(true); // Pass true for session restore
            console.log("✅ NFID session restored via legacy method!");
          } catch (error) {
            console.error("❌ Failed to restore NFID session via legacy method:", error);
            clearSessionInfo();
            
            // Try to clean up AuthClient just in case
            try {
              const authClient = await AuthClient.create();
              await authClient.logout();
            } catch (logoutError) {
              console.warn("Failed to logout after failed restore:", logoutError);
            }
            
            // Reset to default logged out state
            update((prevState) => {
              return {
                ...defaultState,
              };
            });
          }
        } else if (isAuthed === "internetidentity") {
          // For Internet Identity, check AuthClient first
          const authClient = await AuthClient.create();
          if (await authClient.isAuthenticated()) {
            console.info("🔄 Internet Identity connection detected (legacy method)");
            await internetIdentityConnect();
            console.log("✅ Internet Identity session restored via legacy method!");
          } else {
            console.log("❌ Internet Identity delegation missing, clearing session");
            clearSessionInfo();

            // Reset to default logged out state
            update((prevState) => {
              return {
                ...defaultState,
              };
            });
          }
        }
      } else {
        console.log("📭 No legacy auth info found either");
      }
    }

    console.log("🏁 Session restoration check complete");
  };

  const loadUserMainerCanisters = async () => {
    try {
      // Check authentication status from store first
      const isAuthed = globalState.isAuthed;
      if (!isAuthed) {
        console.warn("User not authenticated, cannot reload mAIner canisters");
        return;
      }
      
      // Get current game state canister actor
      const gameStateCanisterActor = globalState.gameStateCanisterActor;
      if (!gameStateCanisterActor) {
        console.warn("Game state canister actor not available");
        return;
      }
      
      // Get identity based on auth type
      let identity;
      if (isAuthed === "nfid") {
        // For NFID, try to get identity from stored signer client
        const storedSignerClient = (globalThis as any).__nfid_signer_client__;
        if (storedSignerClient && typeof storedSignerClient.getIdentity === 'function') {
          identity = storedSignerClient.getIdentity();
        } else {
          console.warn("NFID signer client not available for reload");
          return;
        }
      } else if (isAuthed === "internetidentity") {
        // For Internet Identity, use AuthClient
        authClient = await AuthClient.create();
        if (await authClient.isAuthenticated()) {
          identity = await authClient.getIdentity();
        } else {
          console.warn("Internet Identity not authenticated");
          return;
        }
      } else if (isAuthed === "bitcoin") {
        // For Bitcoin SIWB, get identity from stored session
        const storedSessionKey = (globalThis as any).__siwb_session_key__;
        if (storedSessionKey) {
          // The identity would need to be reconstructed or stored differently
          // For now, we'll use the stored session key as is
          console.warn("Bitcoin session reload requires re-authentication");
          return;
        } else {
          console.warn("Bitcoin SIWB session key not available for reload");
          return;
        }
      } else {
        console.warn("Unknown auth type:", isAuthed);
        return;
      }
      
      // Reload user's mAIner agent canisters
      const { mainerActors, userCanisters } = await initializeUserMainerAgentCanisters(gameStateCanisterActor, isAuthed, identity);
      
      // Update the store with new data
      update((state) => ({
        ...state,
        userMainerCanisterActors: mainerActors,
        userMainerAgentCanistersInfo: userCanisters
      }));
      
      console.log("User mAIner canisters reloaded successfully");
    } catch (error) {
      console.error("Error reloading user mAIner canisters:", error);
    }
  };
  
  const getActor = async (canisterId, canisterIDL, options = {}) => {
    // Anonymous agent (non-authenticated calls)
    let agent = new HttpAgent({
      host: HOST,
    });

    //@ts-ignore
    if (!options.anon) {
      // Create an agent with the logged in user's identity (for authenticated calls)
      try {
        let identityFound = false;
        
        // Check if user is logged in with NFID first
        // NFID uses a different authentication mechanism - try to restore the session
        if (globalState?.isAuthed === "nfid") {
          console.log(`Attempting to restore NFID identity for canister ${canisterId}`);

          let identity = null;

          // Method 1: Try to restore from stored signer client reference
          const storedSignerClient = (globalThis as any).__nfid_signer_client__;
          if (storedSignerClient && typeof storedSignerClient.getIdentity === 'function') {
            try {
              identity = storedSignerClient.getIdentity();
              console.log(`✅ Got NFID identity from stored signer client for canister ${canisterId}`);
            } catch (e) {
              console.warn("Failed to get identity from stored signer client:", e);
            }
          }

          // Method 2: If that didn't work, try to create a new IdentityKit and see if it can restore
          if (!identity) {
            try {
              console.log("Trying to restore NFID session via IdentityKit...");
              const nfidIdentityKit = await getOrCreateNfidIdentityKit();

              if (nfidIdentityKit?.signerClient) {
                // NFID Signer client might persist its own state
                // Try to get identity directly - it should have the session if logged in
                identity = nfidIdentityKit.signerClient.getIdentity();
                console.log(`✅ Got NFID identity from fresh IdentityKit for canister ${canisterId}`);

                // Store the reference for future use
                (globalThis as any).__nfid_identity_kit__ = nfidIdentityKit;
              }
            } catch (restoreError) {
              console.warn("Failed to restore NFID session via IdentityKit:", restoreError);
            }
          }

          // Method 3: Last resort - check if NFID stores anything in localStorage
          if (!identity) {
            try {
              // NFID might store delegation data in localStorage with specific keys
              const nfidKeys = Object.keys(localStorage).filter(key => key.includes('nfid') || key.includes('NFID'));
              console.log("NFID-related localStorage keys:", nfidKeys);

              // If we find NFID keys, it might indicate an active session
              if (nfidKeys.length > 0) {
                console.log("Found NFID data in localStorage, trying alternative restoration...");

                // Try one more time with a fresh IdentityKit
                const freshKit = await getOrCreateNfidIdentityKit();
                if (freshKit?.signerClient?.getIdentity) {
                  identity = freshKit.signerClient.getIdentity();
                  if (identity) {
                    console.log(`✅ Got NFID identity from localStorage-based restoration for canister ${canisterId}`);
                  }
                }
              }
            } catch (lsError) {
              console.warn("Failed to check localStorage for NFID data:", lsError);
            }
          }

          // If we got an identity, use it
          if (identity) {
            const principal = identity.getPrincipal().toString();
            console.log(`✅ Using NFID identity for canister ${canisterId}, principal:`, principal);

            // Verify this matches the expected principal
            if (globalState?.principal && principal !== globalState.principal.toString()) {
              console.error(`❌ Principal mismatch! Expected ${globalState.principal.toString()}, got ${principal}`);
            } else {
              agent = new HttpAgent({
                identity,
                host: HOST,
              });
              identityFound = true;
            }
          } else {
            console.warn("Could not restore NFID identity using any method");
          }
        }
        
        // Fallback to Internet Identity if NFID didn't work or if using II
        if (!identityFound) {
          authClient = await AuthClient.create();
          if (await authClient.isAuthenticated()) {
            const identity = await authClient.getIdentity();
            const principal = identity.getPrincipal().toString();
            console.log(`✅ Using Internet Identity for canister ${canisterId}, principal:`, principal);
            
            // Verify this matches the expected principal
            if (globalState?.principal && principal !== globalState.principal.toString()) {
              console.error(`❌ Principal mismatch! Expected ${globalState.principal.toString()}, got ${principal}`);
            }
            
            agent = new HttpAgent({
              identity,
              host: HOST,
            });
            identityFound = true;
          };
        }
        
        if (!identityFound) {
          console.error(`❌ No authenticated identity found for canister ${canisterId}. This will cause transfers to fail!`);
          console.error(`Store state - isAuthed: ${globalState?.isAuthed}, principal: ${globalState?.principal?.toString()}`);
        }
      } catch (error) {
        console.error("Error in getActor:", error);
        update((state) => ({
          ...state,
          error: "Failed to getActor"
        }));
      };
    };
  
    /* if (options.agent && options.agentOptions) {
      console.warn(
        "Detected both agent and agentOptions passed to getActor. Ignoring agentOptions and proceeding with the provided agent."
      );
    } */
  
    // Fetch root key for certificate validation during development
    if (process.env.DFX_NETWORK === "local") {
      agent.fetchRootKey().catch((err) => {
        console.warn(
          "Unable to fetch root key. Check to ensure that your local replica is running"
        );
        console.error(err);
      });
    }
  
    // Creates an actor with using the candid interface and the HttpAgent
    return Actor.createActor(canisterIDL, {
      agent,
      canisterId,
    });
  };

  // Enhanced session management functions
  const storeSessionInfo = (loginType: string, expiry: bigint) => {
    const sessionInfo = {
      loginType,
      expiry: expiry.toString(),
      timestamp: Date.now()
    };
    localStorage.setItem('sessionInfo', JSON.stringify(sessionInfo));
    localStorage.setItem('isAuthed', loginType);
  };

  const getStoredSessionInfo = () => {
    try {
      const sessionInfoStr = localStorage.getItem('sessionInfo');
      if (sessionInfoStr) {
        const sessionInfo = JSON.parse(sessionInfoStr);
        return {
          ...sessionInfo,
          expiry: BigInt(sessionInfo.expiry)
        };
      }
    } catch (error) {
      console.error("Error parsing stored session info:", error);
    }
    return null;
  };

  const clearSessionInfo = () => {
    localStorage.removeItem('sessionInfo');
    localStorage.removeItem('isAuthed');
  };

  const shouldRefreshSession = (expiry: bigint): boolean => {
    const now = BigInt(Date.now()) * BigInt(1000000); // Convert to nanoseconds
    const timeUntilExpiry = expiry - now;
    return timeUntilExpiry <= SESSION_REFRESH_THRESHOLD && timeUntilExpiry > 0n;
  };

  const refreshUserSession = async () => {
    try {
      const sessionInfo = getStoredSessionInfo();
      if (!sessionInfo || !authClient) return false;

      // Check if session is still valid
      const isAuthenticated = await authClient.isAuthenticated();
      if (!isAuthenticated) {
        console.log("Session expired, clearing stored session info");
        clearSessionInfo();
        await disconnect();
        return false;
      }

      // Check if we need to refresh
      if (shouldRefreshSession(sessionInfo.expiry)) {
        console.log("Refreshing user session...");
        
        // Re-initialize the connection to extend the session
        if (sessionInfo.loginType === "nfid") {
          await nfidConnect(true); // Pass true for session restore
        } else if (sessionInfo.loginType === "internetidentity") {
          await internetIdentityConnect();
        }
        return true;
      }

      return true;
    } catch (error) {
      console.error("Error refreshing session:", error);
      return false;
    }
  };

  const startSessionRefreshTimer = () => {
    // Clear existing timer
    if (globalState.sessionRefreshTimer) {
      clearInterval(globalState.sessionRefreshTimer);
    }

    // Start new timer
    const timerId = setInterval(async () => {
      const success = await refreshUserSession();
      if (!success) {
        clearInterval(timerId);
        update((state) => ({ ...state, sessionRefreshTimer: null }));
      }
    }, SESSION_CHECK_INTERVAL);

    update((state) => ({ ...state, sessionRefreshTimer: timerId }));
  };

  const stopSessionRefreshTimer = () => {
    if (globalState.sessionRefreshTimer) {
      clearInterval(globalState.sessionRefreshTimer);
      update((state) => ({ ...state, sessionRefreshTimer: null }));
    }
  };

  // mAIner creation progress management functions
  const startMainerCreation = () => {
    const sessionId = `creation_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    update((state) => ({
      ...state,
      isCreatingMainer: true,
      mainerCreationProgress: [],
      shouldOpenFirstMainerAfterCreation: true,
      mainerCreationSessionId: sessionId
    }));
    
    // Store the creation state in localStorage
    storeMainerCreationState(true, sessionId, []);
  };

  const addMainerCreationProgress = (message: string, isComplete = false) => {
    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    update((state) => {
      const newProgress = [
        ...state.mainerCreationProgress,
        { message, timestamp, complete: isComplete }
      ];
      
      // Update localStorage with new progress
      if (state.isCreatingMainer) {
        storeMainerCreationState(true, state.mainerCreationSessionId, newProgress);
      }
      
      return {
        ...state,
        mainerCreationProgress: newProgress
      };
    });
  };

  const completeMainerCreation = () => {
    update((state) => ({
      ...state,
      isCreatingMainer: false,
      mainerCreationProgress: [],
      shouldOpenFirstMainerAfterCreation: false,
      mainerCreationSessionId: null
    }));
    
    // Clear the stored creation state
    clearStoredMainerCreationState();
  };

  const preInitNfid = async () => {
    // Start pre-initializing NFID IdentityKit in the background
    // so it's ready when the user clicks the login button
    try {
      await getOrCreateNfidIdentityKit();
      console.log("NFID IdentityKit pre-initialized successfully");
    } catch (error) {
      console.warn("Failed to pre-initialize NFID:", error);
      throw error;
    }
  };

  const resetMainerCreationAfterOpen = () => {
    update((state) => ({
      ...state,
      shouldOpenFirstMainerAfterCreation: false
    }));
  };

  return {
    subscribe,
    update,
    nfidConnect,
    preInitNfid,
    internetIdentityConnect,
    siwbConnect,
    disconnect,
    checkExistingLoginAndConnect,
    loadUserMainerCanisters,
    updateBackendCanisterActor,
    getActor,
    refreshUserSession,
    getStoredSessionInfo,
    clearSessionInfo,
    startMainerCreation,
    addMainerCreationProgress,
    completeMainerCreation,
    resetMainerCreationAfterOpen
  };
};

export const store = createStore({
  whitelist: [backendCanisterId, gameStateCanisterId, apiCanisterId],
  host: HOST,
});
