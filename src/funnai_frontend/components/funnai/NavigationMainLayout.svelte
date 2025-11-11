<script lang="ts">
  import { onMount } from 'svelte';
  import { store, theme } from "../../stores/store";
  import { link, location } from 'svelte-spa-router';
  import LoginModal from '../login/LoginModal.svelte';

  let visibleInstallAppToast = false;
  let navigationDropdownOpen = false;

  const showInstallAppToast = () => {
    visibleInstallAppToast = true;
    // Automatically hide the toast
    setTimeout(() => {
      visibleInstallAppToast = false;
    }, 8000);
  };

  let modalIsOpen = false;

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  const toggleNavigationDropdown = (event: Event) => {
    event.stopPropagation();
    navigationDropdownOpen = !navigationDropdownOpen;
  };

  const closeNavigationDropdown = () => {
    navigationDropdownOpen = false;
  };

  async function disconnect() {
    await store.disconnect();
  }

  // Navigation items
  const navItems = [
    { href: '/', label: 'mAIners', icon: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4', color: 'purple' },
    { href: '/dashboard', label: 'Dashboard', icon: 'M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2', color: 'blue' },
    { href: '/wallet', label: 'Wallet', icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z', color: 'orange' },
    { href: '/marketplace', label: 'Marketplace', icon: 'M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z', color: 'emerald' },
    { href: '/store', label: 'App Store', icon: 'M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z', color: 'indigo' },
  ];

  // Reactive current path
  $: currentPath = $location;

  // Function to initialize dropdown and sidebar functionality
  const initializeDropdown = () => {
    document.body.addEventListener('click', function (event) {
      const target = event.target as Node;
      const navDropdown = document.getElementById('navigationDropdown');
      const navDropdownButton = document.getElementById('navigationDropdownButton');
      
      if (navDropdown && navDropdownButton && 
          !navDropdown.contains(target) && 
          !navDropdownButton.contains(target)) {
        closeNavigationDropdown();
      }
    });
  };

  onMount(() => {
    initializeDropdown();
  });
</script>

<div class="flex items-center justify-center w-full relative">
  <!-- Navigation & Auth - Right side -->
  <div class="ml-auto flex items-center gap-3">
    <!-- Navigation Dropdown -->
    {#if $store.isAuthed}
      <div class="relative">
        <button
          id="navigationDropdownButton"
          on:click={toggleNavigationDropdown}
          class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 text-gray-700 dark:text-gray-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <span class="hidden sm:inline text-sm font-medium">Menu</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 transition-transform {navigationDropdownOpen ? 'rotate-180' : ''}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown Menu -->
        {#if navigationDropdownOpen}
          <div
            id="navigationDropdown"
            class="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-50 animate-slideDown"
          >
            {#each navItems as item}
              <a
                use:link
                href={item.href}
                on:click={closeNavigationDropdown}
                class="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150 {currentPath === item.href ? 'bg-gray-50 dark:bg-gray-700 border-l-4 border-' + item.color + '-500' : ''}"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-{item.color}-600 dark:text-{item.color}-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={item.icon} />
                </svg>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{item.label}</span>
                {#if currentPath === item.href}
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 ml-auto text-{item.color}-600 dark:text-{item.color}-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                {/if}
              </a>
            {/each}
            
            <!-- Separator -->
            <div class="border-t border-gray-200 dark:border-gray-700 my-2"></div>
            
            <!-- Logout Button -->
            <button
              on:click={() => { disconnect(); closeNavigationDropdown(); }}
              class="flex items-center gap-3 px-4 py-2.5 w-full text-left hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors duration-150"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="text-sm font-medium text-red-600 dark:text-red-400">Logout</span>
            </button>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Connect/Login Button -->
    {#if !$store.isAuthed}
      <button
        type="button"
        on:click={toggleModal}
        class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-medium text-sm transition-all duration-200 shadow-md hover:shadow-lg"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
        </svg>
        <span>Connect</span>
      </button>
    {/if}
  </div>
</div>

<!-- Main modal -->
<div class={modalIsOpen ? "" : "hidden"}>
  <LoginModal {toggleModal} />
</div>

<style>
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-slideDown {
    animation: slideDown 0.2s ease-out;
  }

  /* Improve touch targets on mobile */
  @media (max-width: 640px) {
    button, a {
      min-height: 44px;
    }
  }
</style>

