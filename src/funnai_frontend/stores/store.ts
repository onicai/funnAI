import { writable } from "svelte/store";
import { Principal } from "@dfinity/principal";
import type { Identity } from "@dfinity/agent";
import { HttpAgent, Actor } from "@dfinity/agent";
import { AuthClient } from "@dfinity/auth-client";
import UAParser from 'ua-parser-js';
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

import { ICRC2_IDL as icrc2IDL } from "../helpers/idls/icrc2.idl.js";
import { idlFactory as icpIDL } from "../helpers/idls/icp.idl.js";

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
    return "Very High";
  } else {
    return "Medium";
  }
};

export const canisterIds = {
  backendCanisterId,
  gameStateCanisterId
};

export const canisterIDLs = {
  backendIdlFactory,
  gameStateIdlFactory,
  icrc1: icrc2IDL,
  icrc2: icrc2IDL,
  ICP: icpIDL,
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

type State = {
  isAuthed: "nfid" | "internetidentity" | null;
  backendActor: typeof funnai_backend;
  principal: Principal;
  accountId: string;
  error: string;
  isLoading: boolean;
  gameStateCanisterActor: typeof game_state_canister;
  mainerControllerCanisterActor: typeof mainer_ctrlb_canister;
  userMainerCanisterActors: any[];
  userMainerAgentCanistersInfo: any[];
  sessionExpiry: bigint | null; // Track session expiration time
  sessionRefreshTimer: NodeJS.Timeout | null; // Timer for automatic session refresh
  // mAIner creation progress state
  isCreatingMainer: boolean;
  mainerCreationProgress: {message: string, timestamp: string, complete: boolean}[];
  shouldOpenFirstMainerAfterCreation: boolean;
};

let defaultBackendCanisterId = backendCanisterId;

const defaultState: State = {
  isAuthed: null,
  backendActor: createBackendCanisterActor(defaultBackendCanisterId, {
    agentOptions: { host: HOST },
  }),
  principal: null,
  accountId: "",
  error: "",
  isLoading: false,
  gameStateCanisterActor: createGameStateCanisterActor(gameStateCanisterId, {
    agentOptions: { host: HOST },
  }),
  mainerControllerCanisterActor: createMainerControllerCanisterActor(mainerControllerCanisterId, {
    agentOptions: { host: HOST },
  }),
  userMainerCanisterActors: [],
  userMainerAgentCanistersInfo: [],
  sessionExpiry: null,
  sessionRefreshTimer: null,
  // mAIner creation progress state
  isCreatingMainer: false,
  mainerCreationProgress: [],
  shouldOpenFirstMainerAfterCreation: false,
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
    
    let gameStateActor = createGameStateCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return gameStateActor;
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

  const nfidConnect = async () => {
    try {
      authClient = await AuthClient.create();
      if (await authClient.isAuthenticated()) {
        const identity = await authClient.getIdentity();
        await initNfid(identity);
      } else {
        await authClient.login({
          onSuccess: async () => {
            const identity = await authClient.getIdentity();
            await initNfid(identity);
          },
          identityProvider: "https://nfid.one" + AUTH_PATH,
          maxTimeToLive: days * hours * nanosecondsPerHour,
          windowOpenerFeatures:
            `left=${window.screen.width / 2 - 525 / 2}, `+
            `top=${window.screen.height / 2 - 705 / 2},` +
            `toolbar=0,location=0,menubar=0,width=525,height=705`,
        });
      }
    } catch (error) {
      console.error("Error in nfidConnect:", error);
      update((state) => ({
        ...state,
        error: "Failed to connect with NFID"
      }));
    }
  };

  const initNfid = async (identity: Identity) => {
    const backendActor = await initBackendCanisterActor("nfid", identity);

    if (!backendActor) {
      console.warn("couldn't create backend actor");
      return;
    };

    await initUserSettings(backendActor);

    const gameStateCanisterActor = await initGameStateCanisterActor("nfid", identity);
    
    if (!gameStateCanisterActor) {
      console.warn("couldn't create Game State actor");
      return;
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
      userMainerCanisterActors,
      userMainerAgentCanistersInfo,
      sessionExpiry
    }));

    // Start automatic session refresh timer
    startSessionRefreshTimer();

    console.info("nfid is authed");
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
      userMainerCanisterActors,
      userMainerAgentCanistersInfo,
      sessionExpiry
    }));

    // Start automatic session refresh timer
    startSessionRefreshTimer();

    console.info("internetidentity is authed");
  };

  const disconnect = async () => {
    // Stop the session refresh timer
    stopSessionRefreshTimer();
    
    // Clear stored session information
    clearSessionInfo();
    
    // Check isAuthed to determine which method to use to disconnect
    if (globalState.isAuthed === "nfid") {
      try {
        await authClient.logout();
      } catch (error) {
        console.error("NFid disconnect error: ", error);
      };
    } else if (globalState.isAuthed === "internetidentity") {
      try {
        await authClient.logout();
      } catch (error) {
        console.error("Internet Identity disconnect error: ", error);
      };
    };

    update((prevState) => {
      return {
        ...defaultState,
      };
    });
  };

  const checkExistingLoginAndConnect = async () => {
    // Check login state if user is already logged in
    const sessionInfo = getStoredSessionInfo();
    
    if (sessionInfo) {
      const authClient = await AuthClient.create();
      const isAuthenticated = await authClient.isAuthenticated();
      
      if (isAuthenticated) {
        // Check if session is still valid
        const now = BigInt(Date.now()) * BigInt(1000000); // Convert to nanoseconds
        
        if (sessionInfo.expiry > now) {
          console.info(`${sessionInfo.loginType} connection detected and session is valid`);
          
          // Update the session expiry in state
          update((state) => ({ ...state, sessionExpiry: sessionInfo.expiry }));
          
          if (sessionInfo.loginType === "nfid") {
            await nfidConnect();
          } else if (sessionInfo.loginType === "internetidentity") {
            await internetIdentityConnect();
          }
        } else {
          console.info("Stored session has expired, clearing session info");
          clearSessionInfo();
          await authClient.logout();
        }
      } else {
        console.info("AuthClient shows user is not authenticated, clearing session info");
        clearSessionInfo();
      }
    } else {
      // Fallback to old method for backward compatibility
      const isAuthed = localStorage.getItem('isAuthed');
      if (isAuthed) {
        const authClient = await AuthClient.create();
        if (await authClient.isAuthenticated()) {
          if (isAuthed === "nfid") {
            console.info("NFID connection detected (legacy)");
            await nfidConnect();
          } else if (isAuthed === "internetidentity") {
            console.info("Internet Identity connection detected (legacy)");
            await internetIdentityConnect();
          }
        }
      }
    }
  };

  const loadUserMainerCanisters = async () => {
    try {
      // Get current auth client and identity
      authClient = await AuthClient.create();
      if (await authClient.isAuthenticated()) {
        const identity = await authClient.getIdentity();
        
        // Get current auth type from store
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
        
        // Reload user's mAIner agent canisters
        const { mainerActors, userCanisters } = await initializeUserMainerAgentCanisters(gameStateCanisterActor, isAuthed, identity);
        
        // Update the store with new data
        update((state) => ({
          ...state,
          userMainerCanisterActors: mainerActors,
          userMainerAgentCanistersInfo: userCanisters
        }));
        
        console.log("User mAIner canisters reloaded successfully");
      }
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
        authClient = await AuthClient.create();
        if (await authClient.isAuthenticated()) {
          const identity = await authClient.getIdentity();
          agent = new HttpAgent({
            identity,
            host: HOST,
          });
        };
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
          await nfidConnect();
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
    update((state) => ({
      ...state,
      isCreatingMainer: true,
      mainerCreationProgress: [],
      shouldOpenFirstMainerAfterCreation: true
    }));
  };

  const addMainerCreationProgress = (message: string, isComplete = false) => {
    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    
    update((state) => ({
      ...state,
      mainerCreationProgress: [
        ...state.mainerCreationProgress,
        { message, timestamp, complete: isComplete }
      ]
    }));
  };

  const completeMainerCreation = () => {
    update((state) => ({
      ...state,
      isCreatingMainer: false,
      mainerCreationProgress: [],
      shouldOpenFirstMainerAfterCreation: false
    }));
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
    internetIdentityConnect,
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
  whitelist: [backendCanisterId, gameStateCanisterId],
  host: HOST,
});
