<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels } from "../../stores/store";
import { location } from 'svelte-spa-router';
import {
  Bot,
  LayoutDashboard,
  Wallet,
  ShoppingCart,
  LayoutGrid,
} from 'lucide-svelte';
import funnailogoWhite from "../../assets/funnai_white.svg";
import logoClickSound from "../../assets/wheel/1.mp3";

function playLogoSound() {
  const audio = new Audio(logoClickSound);
  audio.volume = 0.5;
  audio.play().catch(err => {
    console.log('Error playing sound:', err);
  });
}

onMount(() => {
  const sidebarToggle = document.getElementById('mainSidebarToggle');
  const mainSidebar = document.getElementById('mainSidebar');

  function toggleSidebar(event) {
    event.stopPropagation();
    mainSidebar.classList.toggle('-translate-x-full');
  };

  function closeSidebarOutside(event) {
    if (!mainSidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
      mainSidebar.classList.add('-translate-x-full');
    };
  };

  function stopPropagation(event) {
    event.stopPropagation();
  };

  sidebarToggle.addEventListener('click', toggleSidebar);
  document.body.addEventListener('click', closeSidebarOutside);
  mainSidebar.addEventListener('click', stopPropagation);

  return () => {
    sidebarToggle.removeEventListener('click', toggleSidebar);
    document.body.removeEventListener('click', closeSidebarOutside);
    mainSidebar.removeEventListener('click', stopPropagation);
  };
});

function closeSidebar() {
  const mainSidebar = document.getElementById('mainSidebar');
  mainSidebar?.classList.add('-translate-x-full');
}

$: userHasDownloadedAtLeastOneModel = $downloadedModels.length > 0;
$: currentPath = $location;

const navItems = [
  { href: '/', label: 'mAIners', icon: Bot },
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/wallet', label: 'Wallet', icon: Wallet },
  { href: '/marketplace', label: 'Marketplace', icon: ShoppingCart },
  { href: '/store', label: 'App Store', icon: LayoutGrid },
];
</script>

<div class="sidebar-header font-sans flex flex-col h-lvh bg-white dark:bg-gray-800">
    <!-- Header Section -->
    <div class="flex flex-col items-start px-4 py-5">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <a use:link href="/" on:dblclick={playLogoSound}>
          <div class="w-28 h-6 relative ml-3">
            <img src={funnailogoWhite} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain object-left" width="112" height="24" />
          </div>
        </a>
      </h1>
    </div>

    <!-- Manage navigation (redesigned) -->
    <nav class="flex-1 px-3 pt-2 pb-3 overflow-y-auto">
      <p class="px-3 mb-3 text-[10px] font-medium uppercase tracking-[0.14em] text-gray-400 dark:text-gray-500">
        Manage
      </p>
      <ul class="space-y-0.5">
        {#each navItems as item}
          <li>
            <a
              use:link
              href={item.href}
              class="group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] tracking-tight transition-all duration-200
                {currentPath === item.href
                  ? 'font-medium bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-white'
                  : 'font-normal text-gray-400 hover:bg-gray-50 hover:text-gray-700 dark:text-gray-500 dark:hover:bg-gray-700/60 dark:hover:text-gray-200'}"
              on:click={closeSidebar}
            >
              {#if currentPath === item.href}
                <span
                  class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r-full bg-[#653FC5]"
                  aria-hidden="true"
                ></span>
              {/if}
              <svelte:component
                this={item.icon}
                class="w-[18px] h-[18px] shrink-0 stroke-[1.6] transition-colors duration-200
                  {currentPath === item.href
                    ? 'text-[#653FC5]'
                    : 'text-gray-400 group-hover:text-[#653FC5] dark:text-gray-600 dark:group-hover:text-[#653FC5]'}"
              />
              <span class="leading-none">{item.label}</span>
            </a>
          </li>
        {/each}
      </ul>
    </nav>

    <!-- Footer Section -->
    <div class="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
      <!-- More from onicai -->
      <div class="py-3">
        <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">More from onicai</div>
        
        <!-- funnAI Whitepaper -->
        <a href="https://www.onicai.com/files/funnAI_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-2 group/whitepaper" on:click={closeSidebar}>
          <button class="w-full px-2 py-2 text-left bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl transition-all duration-300 flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50 hover:border-amber-300/40 dark:hover:border-amber-500/30 hover:from-amber-50/30 hover:to-orange-50/20 dark:hover:from-amber-900/10 dark:hover:to-orange-900/5">
            <div class="relative w-6 h-6 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 absolute top-0.5 left-0.5" viewBox="0 0 24 24" fill="none">
                <defs>
                  <linearGradient id="docGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f59e0b" />
                    <stop offset="100%" style="stop-color:#ea580c" />
                  </linearGradient>
                </defs>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" fill="url(#docGradient)" opacity="0.12"/>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" stroke="url(#docGradient)" stroke-width="1.5" fill="none"/>
                <path d="M13 3v4a2 2 0 002 2h4" stroke="url(#docGradient)" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M9 12h6M9 15h4" stroke="url(#docGradient)" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span class="absolute -top-0.5 -right-0.5 w-1 h-1 bg-amber-400 rounded-full animate-[pulse_2s_ease-in-out_infinite]"></span>
              <span class="absolute top-1 right-0 w-0.5 h-0.5 bg-orange-300 rounded-full animate-[pulse_2.5s_ease-in-out_0.5s_infinite]"></span>
              <span class="absolute -top-0.5 right-1 w-0.5 h-0.5 bg-yellow-300 rounded-full animate-[pulse_3s_ease-in-out_1s_infinite]"></span>
            </div>
            <span class="text-xs font-normal transition-colors duration-300 group-hover/whitepaper:text-amber-700 dark:group-hover/whitepaper:text-amber-400">funnAI Whitepaper</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 ml-auto text-gray-400 dark:text-gray-500 transition-colors duration-300 group-hover/whitepaper:text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
        </a>

        <!-- onicai SNS Whitepaper -->
        <a href="https://www.onicai.com/files/onicai_SNS_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-2 group/sns-whitepaper" on:click={closeSidebar}>
          <button class="w-full px-2 py-2 text-left bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl transition-all duration-300 flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-300/40 dark:hover:border-blue-500/30 hover:from-blue-50/30 hover:to-cyan-50/20 dark:hover:from-blue-900/10 dark:hover:to-cyan-900/5">
            <div class="relative w-6 h-6 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 absolute top-0.5 left-0.5" viewBox="0 0 24 24" fill="none">
                <defs>
                  <linearGradient id="docGradientBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3b82f6" />
                    <stop offset="100%" style="stop-color:#06b6d4" />
                  </linearGradient>
                </defs>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" fill="url(#docGradientBlue)" opacity="0.12"/>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" stroke="url(#docGradientBlue)" stroke-width="1.5" fill="none"/>
                <path d="M13 3v4a2 2 0 002 2h4" stroke="url(#docGradientBlue)" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M9 12h6M9 15h4" stroke="url(#docGradientBlue)" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span class="absolute -top-0.5 -right-0.5 w-1 h-1 bg-blue-400 rounded-full animate-[pulse_2s_ease-in-out_infinite]"></span>
              <span class="absolute top-1 right-0 w-0.5 h-0.5 bg-cyan-300 rounded-full animate-[pulse_2.5s_ease-in-out_0.5s_infinite]"></span>
              <span class="absolute -top-0.5 right-1 w-0.5 h-0.5 bg-sky-300 rounded-full animate-[pulse_3s_ease-in-out_1s_infinite]"></span>
            </div>
            <span class="text-xs font-normal transition-colors duration-300 group-hover/sns-whitepaper:text-blue-700 dark:group-hover/sns-whitepaper:text-blue-400">onicai SNS Whitepaper</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 ml-auto text-gray-400 dark:text-gray-500 transition-colors duration-300 group-hover/sns-whitepaper:text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
        </a>

        <!-- Support Button -->
        <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/?ref=mwte3-ciaaa-aaaaf-ad7aq-cai"
           target="_blank"
           rel="noopener noreferrer"
           class="block">
          <button class="w-full px-3 py-1.5 text-left bg-gray-200 dark:bg-gray-900 rounded-lg transition-all duration-200 flex items-center gap-2 text-sm text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600">
            <img src="https://oc.app/icon.png" alt="OpenChat" class="w-4 h-4 flex-shrink-0" />
            <span>Support</span>
          </button>
        </a>
      </div>

      <!-- Social Links -->
      <div class="pt-1.5 pb-1">
        <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">Connect</div>
        <div class="flex items-center justify-center gap-2">
          <a href="https://www.onicai.com/#/funnai" target="_blank" rel="noopener noreferrer" 
             class="flex-1 bg-gray-200 dark:bg-gray-900 p-2 rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 group flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <circle cx="12" cy="12" r="9" stroke-width="2"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12h18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c-2.5 3-2.5 9 0 18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c2.5 3 2.5 9 0 18"/>
            </svg>
          </a>
          
          <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer"
             class="flex-1 bg-gray-200 dark:bg-gray-900 p-2 rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 group flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
</div>
