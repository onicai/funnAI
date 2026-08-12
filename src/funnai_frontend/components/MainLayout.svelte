<script lang="ts">
  import Router from "svelte-spa-router";
  import { store, theme } from "../stores/store";
  import NavigationMainLayout from "./funnai/NavigationMainLayout.svelte";
  import SidebarMainLayout from "./funnai/SidebarMainLayout.svelte";
  import Mainers from "../pages/Mainers.svelte";
  import Dashboard from "../pages/Dashboard.svelte";
  import Wallet from "../pages/Wallet.svelte";
  import Lottery from "../pages/Lottery.svelte";
  import Brand from "../pages/Brand.svelte";
  import AppStore from "../pages/AppStore.svelte";
  import Marketplace from "../pages/Marketplace.svelte";
  import NotificationToast from "./NotificationToast.svelte";
  import { onMount } from 'svelte';
  import { initializeChartJS } from '../helpers/chartSetup';
  import { link } from 'svelte-spa-router';

  onMount(async () => {
    initializeChartJS();

    localStorage.setItem("theme", "dark");
    theme.set("dark");
    document.documentElement.classList.add("dark");

    console.log("🚀 Starting app initialization...");
    try {
      await store.checkExistingLoginAndConnect();
      console.log("✅ App initialization complete - session restored if available");
    } catch (error) {
      console.error("❌ Error during app initialization:", error);
    }
  });

  const routes = {
    "/": Mainers,
    "/dashboard": Dashboard,
    "/wallet": Wallet,
    "/marketplace": Marketplace,
    "/lottery": Lottery,
    "/brand": Brand,
    "/store": AppStore,
  };
</script>

<div class="flex flex-row h-screen bg-agent-bg font-sans text-gray-200">
  <aside
    id="mainSidebar"
    class="bg-agent-surface/95 border-r border-white/[0.06] fixed z-50 w-72 min-w-72 h-full md:shadow-xl transform -translate-x-full md:translate-x-0 transition-transform duration-200 ease-out backdrop-blur-xl"
  >
    <!-- quieter sidebar atmosphere -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div
        class="absolute inset-0 opacity-40"
        style="background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px); background-size: 32px 32px; mask-image: linear-gradient(180deg, #000 0%, transparent 70%);"
      ></div>
      <div class="absolute -top-20 left-1/2 h-32 w-48 -translate-x-1/2 rounded-full bg-agent-purple/10 blur-3xl"></div>
      <div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent"></div>
    </div>
    <div class="sidebar-content relative z-[1] h-full overflow-hidden">
      <SidebarMainLayout />
    </div>
  </aside>

  <main class="main relative flex flex-col flex-grow ml-0 md:ml-72 transition-all duration-200 ease-out text-gray-200 min-h-screen w-full">
    <!-- calmer stage: soft wash only, no competing orbs/sheen -->
    <div class="pointer-events-none absolute inset-0 agent-atmosphere overflow-hidden" aria-hidden="true"></div>

    <header class="header relative z-40 bg-agent-surface/70 backdrop-blur-xl border-b border-white/[0.06] py-2 px-4 h-[60px]">
      <div class="agent-header-line" aria-hidden="true"></div>
      <div class="header-content flex items-center flex-row h-full gap-2">
        <button
          id="mainSidebarToggle"
          data-drawer-target="mainSidebar"
          data-drawer-toggle="mainSidebar"
          aria-controls="mainSidebar"
          type="button"
          class="inline-flex items-center p-2 text-sm text-gray-400 rounded-lg md:hidden hover:bg-white/5 hover:text-agent-purple focus:outline-none focus:ring-2 focus:ring-agent-purple/40"
        >
          <span class="sr-only">Open sidebar</span>
          <svg class="w-6 h-6" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path clip-rule="evenodd" fill-rule="evenodd" d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"></path>
          </svg>
        </button>

        <!-- Mobile brand (text-only during rebrand) -->
        <a
          use:link
          href="/"
          class="brand-mark md:hidden no-underline leading-none"
          aria-label="onicai home"
        >
          <span class="brand-mark-text font-fredoka text-lg font-semibold tracking-tight text-white">
            onicai
          </span>
        </a>

        <div class="flex ml-auto">
          <NavigationMainLayout />
        </div>
      </div>
    </header>

    <div class="relative z-[1] flex-grow flex flex-col min-h-0">
      <Router {routes} />
    </div>

    <NotificationToast />
  </main>
</div>

<div id="portal-target"></div>
