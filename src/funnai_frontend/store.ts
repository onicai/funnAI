import { writable } from "svelte/store";
import type { Principal } from "@dfinity/principal";
import type { HttpAgent, Identity } from "@dfinity/agent";
import { StoicIdentity } from "ic-stoic-identity";
import { AuthClient } from "@dfinity/auth-client";
import UAParser from 'ua-parser-js';
import {
  funnai_backend,
  createActor as createBackendCanisterActor,
  canisterId as backendCanisterId,
  idlFactory as backendIdlFactory,
} from "../declarations/funnai_backend";

import {
  game_state_canister,
  createActor as createGameStateCanisterActor,
  canisterId as gameStateCanisterId,
  idlFactory as gameStateIdlFactory,
} from "../declarations/game_state_canister";

import {
  mainer_ctrlb_canister,
  createActor as createMainerControllerCanisterActor,
  canisterId as mainerControllerCanisterId,
  idlFactory as mainerControllerIdlFactory,
} from "../declarations/mainer_ctrlb_canister";

// TODO: remove debug print statements
console.log("funnai_backend");
console.log(funnai_backend);
console.log(backendCanisterId);

console.log("game_state_canister");
console.log(game_state_canister);
console.log(gameStateCanisterId);

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
userSettings.subscribe((value) => localStorage.setItem("userSettings", JSON.stringify(value)));
export let selectedAiModelId = writable(localStorage.getItem("selectedAiModelId") || null);
let selectedAiModelIdValue = null;
selectedAiModelId.subscribe((value) => {
  selectedAiModelIdValue = value;
  if (value === null) {
    localStorage.removeItem("selectedAiModelId");
  } else {
    localStorage.setItem("selectedAiModelId", value);
  };
});

export let saveChatsUserSelection = writable(localStorage.getItem("saveChatsUserSelection") === "false" ? false : true); // values: true for "save" or false for "doNotSave" with true as default
let saveChatsUserSelectionValue = saveChatsDefaultSetting;
saveChatsUserSelection.subscribe((value) => {
  saveChatsUserSelectionValue = value;
  // @ts-ignore
  localStorage.setItem("saveChatsUserSelection", value)
});

export let useKnowledgeBase = writable(localStorage.getItem("useKnowledgeBase") === "true" ? true : false);
useKnowledgeBase.subscribe((value) => {
  // @ts-ignore
  localStorage.setItem("useKnowledgeBase", value)
});

declare global {
  interface BigInt {
    toJSON(): Number;
  }
};

BigInt.prototype.toJSON = function () { return Number(this) };

export let downloadedModels = writable(JSON.parse(localStorage.getItem("downloadedAiModels") || "[]"));
downloadedModels.subscribe((value) => {
  localStorage.setItem("downloadedAiModels", JSON.stringify(value));
});

export const currentExperienceId = writable(null);
export let vectorStore = writable(null);

export let installAppDeferredPrompt = writable(null); // the installAppDeferredPrompt event cannot be stored across sessions

let authClient : AuthClient;
const APPLICATION_NAME = "funnai";
const APPLICATION_LOGO_URL = "https://x6occ-biaaa-aaaai-acqzq-cai.icp0.io/devinci512.png"; //TODO: update
//TODO: double check
const AUTH_PATH = "/authenticate/?applicationName="+APPLICATION_NAME+"&applicationLogo="+APPLICATION_LOGO_URL+"#authorize";

const days = BigInt(30);
const hours = BigInt(24);
const nanosecondsPerHour = BigInt(3600000000000);

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
};

// Add theme support
export const theme = writable(localStorage.getItem('theme') || 'dark');

// Toggle theme function
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
  subscribe((value) => globalState = value);

  const initUserSettings = async (backendActor) => {
    // Load the user's settings
      // Especially selected AI model to be used for chat
    if (navigator.onLine) {
      try {
        const retrievedSettingsResponse = await backendActor.get_caller_settings();
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
    
    let mainerControllerActor = createMainerControllerCanisterActor(canisterId, {
      agentOptions: {
        identity,
        host: HOST,
      },
    });
    return mainerControllerActor;
  };

  const initializeUserMainerAgentCanisters = async (gameStateCanisterActor: typeof game_state_canister, loginType, identity: Identity) => {
    try {
      const getMainersResult = await gameStateCanisterActor.getMainerAgentCanistersForUser();
      // @ts-ignore
      if (getMainersResult.Ok) {
        // @ts-ignore
        const userCanisters = getMainersResult.Ok;
        let initPromises = [];
        userCanisters.forEach(userCanister => {
          initPromises.push(initMainerAgentCanisterActor(userCanister, loginType, identity)); 
        });
        let mainerActors = await Promise.all(initPromises);
        return { mainerActors, userCanisters };
      } else {
        // @ts-ignore
        console.error("Error retrieving user mAIner agent canisters: ", getMainersResult.Err);
        // @ts-ignore
        throw new Error("Error retrieving user mAIner agent canisters: ", getMainersResult.Err);
      };
    } catch (error) {
      console.error("Error in initializeUserMainerAgentCanisters: ", error);
    };
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

    localStorage.setItem('isAuthed', "nfid"); // Set flag to indicate existing login for future sessions

    update((state) => ({
      ...state,
      backendActor,
      principal: identity.getPrincipal(),
      //accountId: accounts[0].address, // we take the default account associated with the identity
      accountId: null,
      isAuthed: "nfid",
      gameStateCanisterActor,
      userMainerCanisterActors,
      userMainerAgentCanistersInfo
    }));

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

    localStorage.setItem('isAuthed', "internetidentity"); // Set flag to indicate existing login for future sessions

    update((state) => ({
      ...state,
      backendActor,
      principal: identity.getPrincipal(),
      //accountId: accounts[0].address, // we take the default account associated with the identity
      accountId: null,
      isAuthed: "internetidentity",
      gameStateCanisterActor,
      userMainerCanisterActors,
      userMainerAgentCanistersInfo
    }));

    console.info("internetidentity is authed");
  };

  const disconnect = async () => {
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
    const isAuthed = localStorage.getItem('isAuthed'); // Accessing Local Storage to check login state
    if (isAuthed) {
      const authClient = await AuthClient.create();
      if (await authClient.isAuthenticated()) {
        if (isAuthed === "nfid") {
          console.info("NFID connection detected");
          nfidConnect();
        } else if (isAuthed === "internetidentity") {
          console.info("Internet Identity connection detected");
          internetIdentityConnect();
        };
      };
    };
  };

  return {
    subscribe,
    update,
    nfidConnect,
    internetIdentityConnect,
    disconnect,
    checkExistingLoginAndConnect,
    updateBackendCanisterActor,
  };
};

export const store = createStore({
  whitelist: [backendCanisterId, gameStateCanisterId],
  host: HOST,
});
