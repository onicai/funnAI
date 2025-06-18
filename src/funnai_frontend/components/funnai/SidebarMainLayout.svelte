<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels, theme, toggleTheme } from "../../stores/store";
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
    <div class="flex flex-col items-center py-6">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <a use:link href="/" on:dblclick={playLogoSound}>
          <!-- Reserve logo space to avoid CLS -->
          <div class="w-48 h-20 relative">
            {#if $theme === 'dark'}
              <img src={funnailogoWhite} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain" width="96" height="84" />
            {:else}
              <img src={funnailogo} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain" width="96" height="84" />
            {/if}
          </div>
        </a>
      </h1>
    </div>

    <!-- Main Navigation Section -->
    <div class="flex-1 px-4 py-6 space-y-3">
      <div class="space-y-3">
        <a use:link href="/" class="block" on:click={closeSidebar}>
          <button class={`w-full px-4 py-3 text-left rounded-xl transition-all duration-200 flex items-center gap-3
            ${currentPath === '/' ? 
              'bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 text-purple-700 font-medium dark:bg-gradient-to-r dark:from-purple-900/30 dark:to-purple-800/30 dark:text-purple-300 dark:border-purple-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span class="font-medium">mAIners</span>
          </button>
        </a>

        <a use:link href="/wallet" class="block" on:click={closeSidebar}>
          <button class={`w-full px-4 py-3 text-left rounded-xl transition-all duration-200 flex items-center gap-3
            ${currentPath === '/wallet' ? 
              'bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 text-purple-700 font-medium dark:bg-gradient-to-r dark:from-purple-900/30 dark:to-purple-800/30 dark:text-purple-300 dark:border-purple-700' : 
              'text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <span class="font-medium">Wallet</span>
          </button>
        </a>

        
      </div>
    </div>

    <!-- Footer Section -->
    <div class="px-4 pb-6 border-t border-gray-200 dark:border-gray-700">
      <!-- Theme Toggle -->
      <div class="py-4">
                 <label for="theme-toggle" class="flex items-center justify-between cursor-pointer p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
           <div class="flex items-center gap-3">
             <div class="p-2 rounded-lg {$theme === 'dark' ? 'bg-yellow-100 dark:bg-yellow-900/30' : 'bg-blue-100'}">
               {#if $theme === 'dark'}
                 <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                 </svg>
               {:else}
                 <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                 </svg>
               {/if}
             </div>
             <span class="text-sm font-medium text-gray-700 dark:text-gray-200">
               {$theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
             </span>
           </div>
          <div class="relative">
            <input type="checkbox" id="theme-toggle" class="sr-only peer" checked={$theme === 'dark'} on:change={handleThemeToggle}>
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
          </div>
                 </label>
       </div>

       <!-- More from onicai -->
       <div class="py-2">
         <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 px-3">More from onicai</div>
         <a use:link href="/chat" class="block" on:click={closeSidebar}>
           <button class={`w-full px-4 py-2 text-left rounded-xl transition-all duration-200 flex items-center gap-3 text-sm
             ${currentPath === '/chat' ? 
               'bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 text-purple-700 font-medium dark:bg-gradient-to-r dark:from-purple-900/30 dark:to-purple-800/30 dark:text-purple-300 dark:border-purple-700' : 
               'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700 border border-transparent hover:border-gray-200 dark:hover:border-gray-600'}`}>
             <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
             </svg>
             <span>onicai chat apps</span>
           </button>
         </a>
       </div>

       <!-- Social Links -->
      <div class="pt-2">
        <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 px-3">Connect with us</div>
        <div class="flex items-center justify-center gap-2">
          <!-- Website Link -->
          <a href="https://www.onicai.com/#/funnai" target="_blank" rel="noopener noreferrer" 
             class="flex-1 p-3 rounded-xl transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 group flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <circle cx="12" cy="12" r="9" stroke-width="2"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12h18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c-2.5 3-2.5 9 0 18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c2.5 3 2.5 9 0 18"/>
            </svg>
          </a>
          
          <!-- X (Twitter) Link -->
          <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer"
             class="flex-1 p-3 rounded-xl transition-all duration-200 hover:bg-gray-100 dark:hover:bg-gray-700 group flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
          </a>
        </div>
      </div>
    </div>
</div>
