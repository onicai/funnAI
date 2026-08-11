<script lang="ts">
  import { onMount } from 'svelte';
  import { store, theme } from "../../stores/store";
  import { link, location } from 'svelte-spa-router';
  import LoginModal from '../login/LoginModal.svelte';
  import { ShoppingCart, LogIn } from 'lucide-svelte';

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

<div class="flex items-center justify-center w-full relative font-sans">
  <!-- Navigation & Auth - Right side -->
  <div class="ml-auto flex items-center gap-2.5">
    <!-- Buy mAIner Button -->
    <a
      use:link
      href="/marketplace"
      class="group flex items-center gap-2 h-9 px-3.5 rounded-full border border-white/10 bg-white/[0.04] text-gray-200 text-[13px] font-medium tracking-tight no-underline transition-all duration-200 hover:border-agent-purple/40 hover:bg-agent-purple/10 hover:text-white"
    >
      <ShoppingCart class="w-3.5 h-3.5 stroke-[1.75] text-gray-400 transition-colors duration-200 group-hover:text-agent-purple" />
      <span>Buy mAIner</span>
    </a>

    <!-- Navigation Dropdown -->
    {#if $store.isAuthed}
      <div class="relative">
        <button
          id="navigationDropdownButton"
          on:click={toggleNavigationDropdown}
          class="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.03] border border-white/10 hover:bg-agent-purple/10 hover:text-agent-purple transition-colors duration-150 text-gray-300"
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
            class="absolute right-0 mt-2 w-56 bg-agent-elevated rounded-xl shadow-xl border border-white/10 py-2 z-50 animate-slideDown"
          >
            {#each navItems as item}
              <a
                use:link
                href={item.href}
                on:click={closeNavigationDropdown}
                class="flex items-center gap-3 px-4 py-2.5 mx-1 rounded-lg transition-colors duration-150
                  {currentPath === item.href
                    ? 'bg-white/[0.07] text-white'
                    : 'text-gray-400 hover:bg-white/[0.05] hover:text-gray-100'}"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 {currentPath === item.href ? 'text-agent-purple' : 'text-gray-500'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d={item.icon} />
                </svg>
                <span class="text-sm font-medium">{item.label}</span>
              </a>
            {/each}
            
            <div class="border-t border-white/10 my-2"></div>
            
            <button
              on:click={() => { disconnect(); closeNavigationDropdown(); }}
              class="flex items-center gap-3 px-4 py-2.5 mx-1 rounded-lg w-[calc(100%-0.5rem)] text-left hover:bg-red-500/10 transition-colors duration-150 text-red-400"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span class="text-sm font-medium">Logout</span>
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
        class="group flex items-center gap-2 h-9 px-4 rounded-full bg-agent-purple text-white text-[13px] font-semibold tracking-tight shadow-agent-cta transition-all duration-200 hover:bg-[#5a37b5] active:scale-[0.98]"
      >
        <LogIn class="w-3.5 h-3.5 stroke-[1.75]" />
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
