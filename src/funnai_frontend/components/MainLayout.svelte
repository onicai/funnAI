<script lang="ts">
  import Router from "svelte-spa-router";
  import { store } from "../stores/store";
  import NavigationMainLayout from "./funnai/NavigationMainLayout.svelte";
  import SidebarMainLayout from "./funnai/SidebarMainLayout.svelte";
  import NotificationToast from "./NotificationToast.svelte";
  import { onMount } from 'svelte';
  import { initializeChartJS } from '../helpers/chartSetup';
  import { link } from 'svelte-spa-router';
  import { routes } from "../routes";

  let sidebarOpen = $state(false);

  function isMobileDrawer() {
    return window.matchMedia('(max-width: 767px)').matches;
  }

  function closeSidebar() {
    sidebarOpen = false;
  }

  function toggleSidebar(event: MouseEvent) {
    event.stopPropagation();
    sidebarOpen = !sidebarOpen;
  }

  $effect(() => {
    const lock = sidebarOpen && isMobileDrawer();
    document.documentElement.style.overflow = lock ? 'hidden' : '';
    document.body.style.overflow = lock ? 'hidden' : '';

    return () => {
      document.documentElement.style.overflow = '';
      document.body.style.overflow = '';
    };
  });

  $effect(() => {
    function onKeydown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        sidebarOpen = false;
      }
    }

    window.addEventListener('keydown', onKeydown);
    return () => window.removeEventListener('keydown', onKeydown);
  });

  onMount(() => {
    initializeChartJS();

    // Session restore already starts when the store module loads; this call is
    // idempotent and only waits if restoration is still in flight.
    store.checkExistingLoginAndConnect().catch((error) => {
      console.error("❌ Error during session restoration:", error);
    });
  });
</script>

<div class="flex flex-row h-screen bg-agent-bg font-sans text-gray-200">
  {#if sidebarOpen}
    <button
      type="button"
      class="fixed inset-0 z-40 bg-black/50 md:hidden"
      aria-label="Close sidebar"
      onclick={closeSidebar}
    ></button>
  {/if}

  <aside
    id="main-sidebar"
    class="agent-sidebar-drawer bg-agent-surface/95 border-r border-white/6 fixed top-0 left-0 z-50 w-72 min-w-72 overflow-hidden transform transition-transform duration-200 ease-out backdrop-blur-xl md:shadow-[8px_0_32px_-12px_rgba(0,0,0,0.45),12px_0_40px_-20px_rgba(101,63,197,0.12)] {sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0"
  >
    <!-- quieter sidebar atmosphere -->
    <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div
        class="absolute inset-0 opacity-55"
        style="background-image: linear-gradient(rgba(196,181,253,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(196,181,253,0.05) 1px, transparent 1px); background-size: 32px 32px; mask-image: linear-gradient(180deg, #000 0%, transparent 72%);"
      ></div>
      <div class="absolute -top-20 left-1/2 h-32 w-48 -translate-x-1/2 rounded-full bg-agent-purple/10 blur-3xl"></div>
      <div class="absolute inset-x-0 top-0 h-px bg-linear-to-r from-transparent via-white/15 to-transparent"></div>
    </div>
    <div class="sidebar-content relative z-1 flex h-full min-h-0 flex-col overflow-hidden">
      <SidebarMainLayout {closeSidebar} />
    </div>
  </aside>

  <main class="main relative flex flex-col grow ml-0 md:ml-72 transition-all duration-200 ease-out text-gray-200 h-screen max-h-screen w-full overflow-hidden">
    <!-- calmer stage: soft wash only, no competing orbs/sheen -->
    <div class="pointer-events-none absolute inset-0 agent-atmosphere overflow-hidden" aria-hidden="true"></div>

    <header class="header relative z-50 shrink-0 bg-agent-surface/70 backdrop-blur-xl border-b border-white/6 py-2 px-4 h-[60px] shadow-[0_10px_28px_-18px_rgba(0,0,0,0.55),0_16px_40px_-24px_rgba(101,63,197,0.16)]">
      <div class="agent-header-line" aria-hidden="true"></div>
      <div class="header-content flex items-center flex-row h-full gap-2">
        <button
          type="button"
          aria-controls="main-sidebar"
          aria-expanded={sidebarOpen}
          onclick={toggleSidebar}
          class="inline-flex items-center p-2 text-sm text-gray-400 rounded-lg md:hidden hover:bg-white/5 hover:text-agent-purple focus:outline-hidden focus:ring-2 focus:ring-agent-purple/40"
        >
          <span class="sr-only">{sidebarOpen ? 'Close sidebar' : 'Open sidebar'}</span>
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

        <div class="flex ml-auto shrink-0">
          <NavigationMainLayout />
        </div>
      </div>
    </header>

    <div class="relative z-1 flex-1 min-h-0 overflow-y-auto overscroll-contain" style="scrollbar-gutter: stable;">
      <Router {routes} />
    </div>

    <NotificationToast />
  </main>
</div>

<div id="portal-target"></div>
