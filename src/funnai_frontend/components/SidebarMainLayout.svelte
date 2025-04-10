<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels, theme, toggleTheme } from "../store";
import { get } from 'svelte/store';
import { location } from 'svelte-spa-router';
import funnailogo from "../assets/funnai_black.svg";
import icLogoHex from "../assets/ic_logo_hex.svg";
import funnailogoWhite from "../assets/funnai_white.svg";
import icLogoHexWhite from "../assets/ic_logo_hex_white.svg";

// Get the current theme from the store
let currentTheme;
theme.subscribe(value => {
  currentTheme = value;
});

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

<div class="sidebar-header font-fredoka flex flex-col items-center py-4 h-lvh">    
    <h1 class="text-2xl font-semibold flex items-center gap-2">
      <a use:link href="/">
        {#if $theme === 'dark'}
          <img src={funnailogoWhite} alt="funnAI logo" class="w-24 h-auto">
        {:else}
          <img src={funnailogo} alt="funnAI logo" class="w-24 h-auto">
        {/if}
      </a>
    </h1>
    <a use:link href="/" class="w-full" on:click={closeSidebar}>
      <button class={`w-full text-gray-700 h-16 mt-12 relative transition-all duration-200
        ${currentPath === '/' ? 
          'bg-gradient-to-r from-purple-50 to-gray-100 border-l-4 border-l-purple-500 font-medium text-purple-700 dark:bg-gradient-to-r dark:from-gray-800 dark:to-gray-700 dark:text-purple-300 dark:border-l-purple-400' : 
          'bg-white hover:border-2 hover:border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:border-gray-600 dark:hover:text-white'}`} 
        style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button">
        mAIner
      </button>
    </a>
    <!-- 
      <a use:link href="/wallet" class="w-full" on:click={closeSidebar}>
        <button class={`w-full text-gray-700 h-16 mt-4 ${currentPath === '/wallet' ? 'bg-gray-100' : 'bg-white'} hover:border-2 hover:border-gray-300`} style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button">
          Wallet
        </button>
      </a>
    -->
    <a use:link href="/chat" class="w-full" on:click={closeSidebar}>
      <button class={`w-full text-gray-700 h-16 mt-4 relative transition-all duration-200
        ${currentPath === '/chat' ? 
          'bg-gradient-to-r from-purple-50 to-gray-100 border-l-4 border-l-purple-500 font-medium text-purple-700 dark:bg-gradient-to-r dark:from-gray-800 dark:to-gray-700 dark:text-purple-300 dark:border-l-purple-400' : 
          'bg-white hover:border-2 hover:border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:border-gray-600 dark:hover:text-white'}`} 
        style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button">
        Chat
      </button>
    </a>
    
    <!-- Theme Toggle moved to the bottom -->
    <div class="mt-auto mb-0">
      <label for="theme-toggle" class="inline-flex items-center cursor-pointer mb-2 text-gray-700 dark:text-gray-200">
        <span class="mr-3 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <span class="ml-1">Light</span>
        </span>
        <div class="relative">
          <input type="checkbox" id="theme-toggle" class="sr-only peer" checked={$theme === 'dark'} on:change={handleThemeToggle}>
          <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
        </div>
        <span class="ml-3 flex items-center">
          <span class="mr-1">Dark</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </span>
      </label>
    </div>
</div>
