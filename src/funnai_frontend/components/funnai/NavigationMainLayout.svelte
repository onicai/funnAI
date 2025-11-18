<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import { link } from 'svelte-spa-router';
  import LoginModal from '../login/LoginModal.svelte';
  import NotificationsCenter from './NotificationsCenter.svelte';
  import AccessCodesCenter from './lottery/AccessCodesCenter.svelte';

  let visibleInstallAppToast = false;

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

  async function disconnect() {
    await store.disconnect();
  }

  // Function to initialize dropdown and sidebar functionality
  const initializeDropdown = () => {
    const dropdownMenuIconButton = document.getElementById('dropdownMenuIconButton');
    const dropdownDots = document.getElementById('dropdownDots');
    const sidebarToggle = document.getElementById('mainSidebarToggle');
    const mainSidebar = document.getElementById('main-sidebar');

    if (dropdownMenuIconButton && dropdownDots) {
      dropdownMenuIconButton.addEventListener('click', function (event) {
        event.stopPropagation();
        dropdownDots.classList.toggle('hidden');
      });

      document.body.addEventListener('click', function (event) {
        const target = event.target as Node;
        if (!dropdownDots.contains(target) && !dropdownMenuIconButton.contains(target)) {
          if (!dropdownDots.classList.contains('hidden')) {
            dropdownDots.classList.add('hidden');
          }
        }
      });
    }

    if (sidebarToggle && mainSidebar) {
      sidebarToggle.addEventListener('click', function(event) {
        event.stopPropagation();
        mainSidebar.classList.toggle('-translate-x-full');
      });

      document.body.addEventListener('click', function(event) {
        const target = event.target as Node;
        if (!mainSidebar.contains(target) && !sidebarToggle.contains(target)) {
          mainSidebar.classList.add('-translate-x-full');
        }
      });

      mainSidebar.addEventListener('click', function(event) {
        event.stopPropagation();
      });
    }
  };

  onMount(() => {
    initializeDropdown();
  });
</script>

  {#if !$store.isAuthed}
    <div class="flex items-center gap-3 sm:gap-3 overflow-x-auto">
      <!-- Claim Whitelist Button 
      <a href="https://docs.google.com/forms/d/e/1FAIpQLSfLF1Pfh31hzoqXF4u-t7NGZ7n19TC3SjiR6686W8l4025l0w/viewform?usp=sharing&ouid=118313353312773403627" target='_blank'
         class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 dark:from-blue-900/30 dark:to-blue-800/30 dark:hover:from-blue-800/40 dark:hover:to-blue-700/40 border border-blue-200 hover:border-blue-300 dark:border-blue-700 dark:hover:border-blue-600 text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200 font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="hidden xs:inline">Claim whitelist</span>
        <span class="xs:hidden">Whitelist</span>
      </a>-->

      <!-- Connect Button -->
       <button type="button" 
               on:click={() => {toggleModal()}} 
               data-modal-target="crypto-modal" 
               data-modal-toggle="crypto-modal" 
               class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 dark:from-purple-900/30 dark:to-purple-800/30 dark:hover:from-purple-800/40 dark:hover:to-purple-700/40 border border-purple-200 hover:border-purple-300 dark:border-purple-700 dark:hover:border-purple-600 text-purple-700 hover:text-purple-800 dark:text-purple-300 dark:hover:text-purple-200 font-medium text-sm">
         
         <span class="">Connect</span>
       </button>
    </div>
  {:else}
    <div class="flex items-center gap-3 sm:gap-3 overflow-x-auto">
      <!-- Claim Whitelist Button 
      <a href="https://docs.google.com/forms/d/e/1FAIpQLSfLF1Pfh31hzoqXF4u-t7NGZ7n19TC3SjiR6686W8l4025l0w/viewform?usp=sharing&ouid=118313353312773403627" target='_blank'
         class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 dark:from-blue-900/30 dark:to-blue-800/30 dark:hover:from-blue-800/40 dark:hover:to-blue-700/40 border border-blue-200 hover:border-blue-300 dark:border-blue-700 dark:hover:border-blue-600 text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200 font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="hidden xs:inline">Claim whitelist</span>
        <span class="xs:hidden">Whitelist</span>
      </a>
      -->

      

      <!-- mAIners Button -->
      <a use:link href="/" 
         class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 dark:from-purple-900/30 dark:to-purple-800/30 dark:hover:from-purple-800/40 dark:hover:to-purple-700/40 border border-purple-200 hover:border-purple-300 dark:border-purple-700 dark:hover:border-purple-600 text-purple-700 hover:text-purple-800 dark:text-purple-300 dark:hover:text-purple-200 font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <span class="hidden xs:inline">mAIners</span>
      </a>

      <!-- Dashboard Button -->
      <a use:link href="/dashboard" 
         class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 dark:from-blue-900/30 dark:to-blue-800/30 dark:hover:from-blue-800/40 dark:hover:to-blue-700/40 border border-blue-200 hover:border-blue-300 dark:border-blue-700 dark:hover:border-blue-600 text-blue-700 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-200 font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
        </svg>
        <span class="hidden xs:inline">Dashboard</span>
      </a>

      <!-- Wallet Button -->
      <a use:link href="/wallet" 
         class="flex-shrink-0 group relative overflow-hidden px-4 py-2.5 sm:px-5 sm:py-3 rounded-xl transition-all duration-200 flex items-center gap-2 sm:gap-3 min-h-[44px] bg-gradient-to-r from-orange-50 to-orange-100 hover:from-orange-100 hover:to-orange-200 dark:from-orange-900/30 dark:to-orange-800/30 dark:hover:from-orange-800/40 dark:hover:to-orange-700/40 border border-orange-200 hover:border-orange-300 dark:border-orange-700 dark:hover:border-orange-600 text-orange-700 hover:text-orange-800 dark:text-orange-300 dark:hover:text-orange-200 font-medium text-sm">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
        <span class="hidden xs:inline">Wallet</span>
      </a>
      <!-- <div class="relative mr-2">
        <AccessCodesCenter />
      </div> -->
      <!-- <div class="relative mr-2">
        <NotificationsCenter />
      </div> -->
      
    </div>
  {/if}

<!-- Main modal -->
<div class={modalIsOpen ? "" : "hidden"}>
  <LoginModal {toggleModal} />
</div>

<style>
  /* Custom breakpoint for extra small screens */
  @media (min-width: 480px) {
    .xs\:inline {
      display: inline !important;
    }
    .xs\:hidden {
      display: none !important;
    }
  }
  
  @media (max-width: 479px) {
    .xs\:inline {
      display: none !important;
    }
    .xs\:hidden {
      display: inline !important;
    }
  }
  
  /* Improve touch targets on mobile */
  @media (max-width: 640px) {
    button, a {
      min-height: 44px;
    }
  }
  
  /* Prevent horizontal scroll on very small screens */
  @media (max-width: 320px) {
    .overflow-x-auto {
      -webkit-overflow-scrolling: touch;
    }
  }
</style>

