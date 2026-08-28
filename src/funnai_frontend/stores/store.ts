/**
 * Public store barrel. Import from here so callers do not need to know
 * which module owns a given export.
 */
export { canisterIds, canisterIDLs, HOST, MEMO_PAYMENT_PROTOCOL } from "./canisterConfig";
export {
  webGpuSupportedBrowsers,
  device,
  deviceType,
  browser,
  supportsWebGpu,
} from "./device";
export {
  currentModelName,
  chatModelGlobal,
  chatModelDownloadedGlobal,
  chatModelIdInitiatedGlobal,
  activeChatGlobal,
  temperatureDefaultSetting,
  responseLengthDefaultSetting,
  systemPromptDefaultSetting,
  saveChatsDefaultSetting,
  userSettings,
  selectedAiModelId,
  saveChatsUserSelection,
  useKnowledgeBase,
  downloadedModels,
  currentExperienceId,
  vectorStore,
  installAppDeferredPrompt,
} from "./chatStore";
export { MAINER_UI_CACHE_KEY } from "./session";
export { createStore, store } from "./authStore";

declare global {
  interface BigInt {
    toJSON(): Number;
  }
};

BigInt.prototype.toJSON = function () { return Number(this) };
