<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels, theme, toggleTheme, store } from "../../stores/store";
import { get } from 'svelte/store';
import { location } from 'svelte-spa-router';
import funnailogo from "../../assets/funnai_black.svg";
import funnailogoWhite from "../../assets/funnai_white.svg";
import logoClickSound from "../../assets/wheel/1.mp3";

// Get the current theme from the store
let currentTheme;
theme.subscribe(value => {
  currentTheme = value;
});

// Function to play sound on logo double-click
function playLogoSound() {
  const audio = new Audio(logoClickSound);
  audio.volume = 0.5; // Set volume to 50%
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

  function closeSidebar(event) {
    if (!mainSidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
      mainSidebar.classList.add('-translate-x-full');
    };
  };

  function stopPropagation(event) {
    event.stopPropagation();
  };

  sidebarToggle.addEventListener('click', toggleSidebar);
  document.body.addEventListener('click', closeSidebar);
  mainSidebar.addEventListener('click', stopPropagation);

  return () => {
    sidebarToggle.removeEventListener('click', toggleSidebar);
    document.body.removeEventListener('click', closeSidebar);
    mainSidebar.removeEventListener('click', stopPropagation);
  };
});

function closeSidebar() {
  const mainSidebar = document.getElementById('mainSidebar');
  mainSidebar?.classList.add('-translate-x-full');
}

// Reactive statement to check if the user has already downloaded at least one AI model
$: userHasDownloadedAtLeastOneModel = $downloadedModels.length > 0;

// Make location reactive
$: currentPath = $location;

// Add a console log to debug
$: console.log('Current path:', currentPath);

function isActive(path) {
  return currentPath === path;
}

// Handle theme toggle
function handleThemeToggle() {
  toggleTheme();
}
</script>

<div class="sidebar-header font-fredoka flex flex-col h-lvh bg-white dark:bg-gray-800">    
    <!-- Header Section -->
    <div class="flex flex-col items-start px-4 py-3">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <a use:link href="/" on:dblclick={playLogoSound}>
          <!-- Reserve logo space to avoid CLS -->
          <div class="w-44 h-16 relative ml-3">
            {#if $theme === 'dark'}
              <img src={funnailogoWhite} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain object-left" width="96" height="84" />
            {:else}
              <img src={funnailogo} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain object-left" width="96" height="84" />
            {/if}
          </div>
        </a>
      </h1>
    </div>

    <!-- Main Navigation Section -->
    <div class="flex-1 px-4 py-3 space-y-2">
      <div class="space-y-2">
        <a use:link href="/" class="block" on:click={closeSidebar}>
          <button class={`w-full px-3 py-2.5 text-left rounded-lg transition-all duration-200 flex items-center gap-3
            ${currentPath === '/' ? 
              'bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 text-purple-700 font-medium dark:bg-gradient-to-r dark:from-purple-900/30 dark:to-purple-800/30 dark:text-purple-300 dark:border-purple-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span class="font-medium">mAIners</span>
          </button>
        </a>

        <a use:link href="/dashboard" class="block" on:click={closeSidebar}>
          <button class={`w-full px-3 py-2.5 text-left rounded-lg transition-all duration-200 flex items-center gap-3
            ${currentPath === '/dashboard' ? 
              'bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 text-blue-700 font-medium dark:bg-gradient-to-r dark:from-blue-900/30 dark:to-blue-800/30 dark:text-blue-300 dark:border-blue-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
            <span class="font-medium">Dashboard</span>
          </button>
        </a>

        <a use:link href="/wallet" class="block" on:click={closeSidebar}>
          <button class={`w-full px-3 py-2.5 text-left rounded-lg transition-all duration-200 flex items-center gap-3
            ${currentPath === '/wallet' ? 
              'bg-gradient-to-r from-orange-50 to-orange-100 border border-orange-200 text-orange-700 font-medium dark:bg-gradient-to-r dark:from-orange-900/30 dark:to-orange-800/30 dark:text-orange-300 dark:border-orange-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <span class="font-medium">Wallet</span>
          </button>
        </a>

        <a use:link href="/marketplace" class="block" on:click={closeSidebar}>
          <button class={`w-full px-3 py-2.5 text-left rounded-lg transition-all duration-200 flex items-center gap-3
            ${currentPath === '/marketplace' ? 
              'bg-gradient-to-r from-emerald-50 to-emerald-100 border border-emerald-200 text-emerald-700 font-medium dark:bg-gradient-to-r dark:from-emerald-900/30 dark:to-emerald-800/30 dark:text-emerald-300 dark:border-emerald-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span class="font-medium">Marketplace</span>
          </button>
        </a>

        <a use:link href="/store" class="block" on:click={closeSidebar}>
          <button class={`w-full px-3 py-2.5 text-left rounded-lg transition-all duration-200 flex items-center gap-3
            ${currentPath === '/store' ? 
              'bg-gradient-to-r from-indigo-50 to-indigo-100 border border-indigo-200 text-indigo-700 font-medium dark:bg-gradient-to-r dark:from-indigo-900/30 dark:to-indigo-800/30 dark:text-indigo-300 dark:border-indigo-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
            </svg>
            <span class="font-medium">App Store</span>
          </button>
        </a>

        
      </div>
    </div>

    <!-- Footer Section -->
    <div class="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
      <!-- Theme Toggle -->
      <div class="py-2">
        <label for="theme-toggle" class="flex items-center justify-between cursor-pointer p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
          <div class="flex items-center gap-2">
            {#if $theme === 'dark'}
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            {:else}
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            {/if}
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">
              {$theme === 'dark' ? 'Light' : 'Dark'}
            </span>
          </div>
          <div class="relative">
            <input type="checkbox" id="theme-toggle" class="sr-only peer" checked={$theme === 'dark'} on:change={handleThemeToggle}>
            <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
          </div>
        </label>
      </div>

      <!-- More from onicai -->
      <div class="py-1.5">
        <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">More from onicai</div>
        
        <!-- funnAI Whitepaper -->
        <a href="https://www.onicai.com/files/funnAI_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-2 group/whitepaper" on:click={closeSidebar}>
          <button class="w-full px-2 py-2 text-left bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl transition-all duration-300 flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50 hover:border-amber-300/40 dark:hover:border-amber-500/30 hover:from-amber-50/30 hover:to-orange-50/20 dark:hover:from-amber-900/10 dark:hover:to-orange-900/5">
            <!-- Document icon with sparkles -->
            <div class="relative w-6 h-6 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 absolute top-0.5 left-0.5" viewBox="0 0 24 24" fill="none">
                <defs>
                  <linearGradient id="docGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f59e0b" />
                    <stop offset="100%" style="stop-color:#ea580c" />
                  </linearGradient>
                </defs>
                <!-- Document body -->
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" fill="url(#docGradient)" opacity="0.12"/>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" stroke="url(#docGradient)" stroke-width="1.5" fill="none"/>
                <!-- Folded corner -->
                <path d="M13 3v4a2 2 0 002 2h4" stroke="url(#docGradient)" stroke-width="1.5" stroke-linecap="round"/>
                <!-- Text lines -->
                <path d="M9 12h6M9 15h4" stroke="url(#docGradient)" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <!-- Subtle sparkles -->
              <span class="absolute -top-0.5 -right-0.5 w-1 h-1 bg-amber-400 rounded-full animate-[pulse_2s_ease-in-out_infinite]"></span>
              <span class="absolute top-1 right-0 w-0.5 h-0.5 bg-orange-300 rounded-full animate-[pulse_2.5s_ease-in-out_0.5s_infinite]"></span>
              <span class="absolute -top-0.5 right-1 w-0.5 h-0.5 bg-yellow-300 rounded-full animate-[pulse_3s_ease-in-out_1s_infinite]"></span>
            </div>
            <span class="font-medium transition-colors duration-300 group-hover/whitepaper:text-amber-700 dark:group-hover/whitepaper:text-amber-400">funnAI Whitepaper</span>
            <!-- External link arrow -->
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 ml-auto text-gray-400 dark:text-gray-500 transition-colors duration-300 group-hover/whitepaper:text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
        </a>

        <!-- onicai SNS Whitepaper -->
        <a href="https://www.onicai.com/files/onicai_SNS_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-2 group/sns-whitepaper" on:click={closeSidebar}>
          <button class="w-full px-2 py-2 text-left bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-xl transition-all duration-300 flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300 border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-300/40 dark:hover:border-blue-500/30 hover:from-blue-50/30 hover:to-cyan-50/20 dark:hover:from-blue-900/10 dark:hover:to-cyan-900/5">
            <!-- Document icon with sparkles -->
            <div class="relative w-6 h-6 flex-shrink-0">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 absolute top-0.5 left-0.5" viewBox="0 0 24 24" fill="none">
                <defs>
                  <linearGradient id="docGradientBlue" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3b82f6" />
                    <stop offset="100%" style="stop-color:#06b6d4" />
                  </linearGradient>
                </defs>
                <!-- Document body -->
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" fill="url(#docGradientBlue)" opacity="0.12"/>
                <path d="M7 3a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8.414a1 1 0 00-.293-.707l-4.414-4.414A1 1 0 0013.586 3H7z" stroke="url(#docGradientBlue)" stroke-width="1.5" fill="none"/>
                <!-- Folded corner -->
                <path d="M13 3v4a2 2 0 002 2h4" stroke="url(#docGradientBlue)" stroke-width="1.5" stroke-linecap="round"/>
                <!-- Text lines -->
                <path d="M9 12h6M9 15h4" stroke="url(#docGradientBlue)" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <!-- Subtle sparkles -->
              <span class="absolute -top-0.5 -right-0.5 w-1 h-1 bg-blue-400 rounded-full animate-[pulse_2s_ease-in-out_infinite]"></span>
              <span class="absolute top-1 right-0 w-0.5 h-0.5 bg-cyan-300 rounded-full animate-[pulse_2.5s_ease-in-out_0.5s_infinite]"></span>
              <span class="absolute -top-0.5 right-1 w-0.5 h-0.5 bg-sky-300 rounded-full animate-[pulse_3s_ease-in-out_1s_infinite]"></span>
            </div>
            <span class="font-medium transition-colors duration-300 group-hover/sns-whitepaper:text-blue-700 dark:group-hover/sns-whitepaper:text-blue-400">onicai SNS Whitepaper</span>
            <!-- External link arrow -->
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
          <!-- Website Link -->
          <a href="https://www.onicai.com/#/funnai" target="_blank" rel="noopener noreferrer" 
             class="flex-1 bg-gray-200 dark:bg-gray-900 p-2 rounded-lg transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 group flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <circle cx="12" cy="12" r="9" stroke-width="2"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12h18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c-2.5 3-2.5 9 0 18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c2.5 3 2.5 9 0 18"/>
            </svg>
          </a>
          
          <!-- X (Twitter) Link -->
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
