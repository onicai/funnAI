import { writable } from "svelte/store";

export const currentModelName = writable<string>("No model selected");

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
export let selectedAiModelIdValue = null;

export let saveChatsUserSelection = writable(localStorage.getItem("saveChatsUserSelection") === "false" ? false : true); // values: true for "save" or false for "doNotSave" with true as default
export let saveChatsUserSelectionValue = saveChatsDefaultSetting;

export let useKnowledgeBase = writable(localStorage.getItem("useKnowledgeBase") === "true" ? true : false);

export let downloadedModels = writable(JSON.parse(localStorage.getItem("downloadedAiModels") || "[]"));

export const currentExperienceId = writable(null);
export let vectorStore = writable(null);

export let installAppDeferredPrompt = writable(null); // the installAppDeferredPrompt event cannot be stored across sessions

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

setupStoreSubscriptions();
