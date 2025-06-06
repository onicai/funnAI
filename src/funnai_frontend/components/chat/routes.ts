import ChatInterface from "./ChatInterface.svelte";
import UserSettings from "../../pages/chat/UserSettings.svelte";
import About from "../../pages/chat/About.svelte";
import Brand from "../../pages/chat/Brand.svelte";
import ModelsComponent from "../../pages/chat/Models.svelte";

// Define routes in a separate file
export const routes = {
  "/chat": ChatInterface,
  "/chat/settings": UserSettings,
  "/chat/about": About,
  "/chat/brand": Brand,
  "/chat/models": ModelsComponent,
  "*": ChatInterface,
}; 