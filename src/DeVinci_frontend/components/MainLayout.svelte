<script lang="ts">
  import type { SvelteComponent } from 'svelte';
  import Router from "svelte-spa-router";
  import { store } from "../store";
  import NavigationMainLayout from "./NavigationMainLayout.svelte";
  import SidebarMainLayout from "./SidebarMainLayout.svelte";
  import ChatLayout from "./ChatLayout.svelte";
  import Dashboard from "../pages/Dashboard.svelte";
  import funnAI from "../pages/funnAI.svelte";
  import Wallet from "../pages/Wallet.svelte";

  const routes: Record<string, typeof SvelteComponent> = {
    "/": Dashboard,
    "/funn": funnAI,
    "/chat": ChatLayout,
    "/chat/*": ChatLayout,
    "/wallet": Wallet,
  };
</script>

<div class="flex flex-row h-screen">
  <aside id="mainSidebar" class="bg-[radial-gradient(circle_at_center,_#e6e9f0,_#fafbfc,_#dfe7fd)] fixed z-50 bg-gray-200 w-72 min-w-72 h-full md:shadow transform -translate-x-full md:translate-x-0 transition-transform duration-150 ease-in">
    <div class="sidebar-content p-4 pt-0 h-full overflow-hidden">
      <SidebarMainLayout />
    </div>
  </aside>
  <main class="main flex flex-col flex-grow ml-0 md:ml-72 transition-all duration-150 ease-in">
    <header class="header bg-white shadow py-2 px-4">
      <div class="header-content flex items-center flex-row">
        <button id="mainSidebarToggle" data-drawer-target="mainSidebar" data-drawer-toggle="mainSidebar" aria-controls="mainSidebar" type="button" class="inline-flex items-center p-2 mt-2 ms-3 text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200">
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
    <Router {routes} />
  </main>
</div> 