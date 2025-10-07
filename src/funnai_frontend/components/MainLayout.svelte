<script lang="ts">
  import type { SvelteComponent } from 'svelte';
  import Router from "svelte-spa-router";
  import { store, theme } from "../stores/store";
  import NavigationMainLayout from "./funnai/NavigationMainLayout.svelte";
  import SidebarMainLayout from "./funnai/SidebarMainLayout.svelte";
  import ChatLayout from "./chat/ChatLayout.svelte";
  import Mainers from "../pages/Mainers.svelte";
  import Dashboard from "../pages/Dashboard.svelte";
  import Wallet from "../pages/Wallet.svelte";
  import Lottery from "../pages/Lottery.svelte";
  import Brand from "../pages/Brand.svelte";
  import AppStore from "../pages/AppStore.svelte";
  import Marketplace from "../pages/Marketplace.svelte";
  import { onMount } from 'svelte';
  import { initializeChartJS } from '../helpers/chartSetup';

  // Initialize theme from localStorage on mount
  onMount(() => {
    // Initialize Chart.js components early
    initializeChartJS();
    
    // Set dark mode as default if no preference is stored
    const savedTheme = localStorage.getItem("theme") || "dark";
    theme.set(savedTheme);
    applyTheme(savedTheme);
    try {
      // Check login state
      void store.checkExistingLoginAndConnect();      
    } catch (error) {
      console.warn("Error checking login state: ", error);      
    };
  });
  
  // React to theme changes
  theme.subscribe(newTheme => {
    applyTheme(newTheme);
  });
  
  function applyTheme(currentTheme) {
    if (typeof document !== 'undefined') {
      if (currentTheme === "dark") {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  }

  const routes: Record<string, typeof SvelteComponent> = {
    "/": Mainers,
    "/dashboard": Dashboard,
    "/chat": ChatLayout,
    "/chat/*": ChatLayout,
    "/wallet": Wallet,
    "/marketplace": Marketplace,
    "/lottery": Lottery,
    "/brand": Brand,
    "/store": AppStore,
  };
</script>

<div class="flex flex-row h-screen dark:bg-gray-900">
  <aside id="mainSidebar" class="bg-[radial-gradient(circle_at_center,_#e6e9f0,_#fafbfc,_#dfe7fd)] dark:bg-[radial-gradient(circle_at_center,_#1f2937,_#111827,_#1e293b)] fixed z-50 w-72 min-w-72 h-full md:shadow transform -translate-x-full md:translate-x-0 transition-transform duration-150 ease-in">
    <div class="sidebar-content p-4 pt-0 h-full overflow-hidden">
      <SidebarMainLayout />
    </div>
  </aside>
  <main class="main flex flex-col flex-grow ml-0 md:ml-72 transition-all duration-150 ease-in dark:bg-gray-900 dark:text-gray-200 min-h-screen w-full">
    <header class="header bg-white dark:bg-gray-800 shadow py-2 px-4 h-[60px]">
      <div class="header-content flex items-center flex-row">
        <button id="mainSidebarToggle" data-drawer-target="mainSidebar" data-drawer-toggle="mainSidebar" aria-controls="mainSidebar" type="button" class="inline-flex items-center p-2 mt-2 ms-3 text-sm text-gray-500 dark:text-gray-400 rounded-lg md:hidden hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:focus:ring-gray-600">
          <span class="sr-only">Open sidebar</span>
          <svg class="w-6 h-6" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path clip-rule="evenodd" fill-rule="evenodd" d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"></path>
          </svg>
        </button>
        <div class="flex ml-auto">
          <NavigationMainLayout />
        </div>
      </div>
    </header>
    <div class="flex-grow flex flex-col dark:bg-gray-900">
      <Router {routes} />
    </div>
  </main>
</div> 

<div id="portal-target"></div>