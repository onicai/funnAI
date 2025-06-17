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
    <div class="flex items-center gap-2 sm:gap-2 overflow-x-auto">
      <!-- Support Link - Always Visible -->
      <a href="https://docs.google.com/" class="flex-shrink-0 text-gray-900 dark:text-blue-400 bg-blue-100 dark:bg-gray-700 border-2 border-blue-500 hover:border-2 hover:border-blue-600 dark:hover:border-blue-400 hover:bg-blue-200 dark:hover:bg-gray-600 focus:ring-4 focus:outline-none focus:ring-blue-200 dark:focus:ring-blue-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center transition-colors min-h-[44px]" style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;">
        <span class="hidden xs:inline">Claim whitelist</span>
        <span class="xs:hidden">Whitelist</span>
      </a>
      <a 
        href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/?ref=mwte3-ciaaa-aaaaf-ad7aq-cai"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-shrink-0 text-gray-700 bg-gray-100 dark:text-gray-200 dark:bg-gray-700 border-2 border-gray-200 hover:border-2 hover:border-gray-300 dark:hover:border-gray-600 border focus:ring-4 focus:outline-none focus:ring-gray-100 dark:focus:ring-gray-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center transition-colors min-h-[44px]" 
        style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;"
      >
        <img src="https://oc.app/icon.png" alt="OpenChat" class="w-4 h-4 me-1 sm:me-2 flex-shrink-0" />
        <span class="hidden xs:inline">Support</span>
      </a>
      
      <button type="button" on:click={() => {toggleModal()}} data-modal-target="crypto-modal" data-modal-toggle="crypto-modal" class="flex-shrink-0 text-gray-700 bg-gray-100 dark:text-gray-200 dark:bg-gray-700 border-2 border-gray-200 hover:border-2 hover:border-gray-300 dark:hover:border-gray-600 border focus:ring-4 focus:outline-none focus:ring-gray-100 dark:focus:ring-gray-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center min-h-[44px]" style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;">
        <svg aria-hidden="true" class="w-4 h-4 me-1 sm:me-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
        <span class="hidden xs:inline">Connect</span>
      </button>
    </div>
  {:else}
    <div class="flex items-center gap-2 sm:gap-2 overflow-x-auto">
      <!-- Support Link - Always Visible -->
      <a href="https://docs.google.com/" class="flex-shrink-0 text-gray-900 dark:text-blue-400 bg-blue-100 dark:bg-gray-700 border-2 border-blue-500 hover:border-2 hover:border-blue-600 dark:hover:border-blue-400 hover:bg-blue-200 dark:hover:bg-gray-600 focus:ring-4 focus:outline-none focus:ring-blue-200 dark:focus:ring-blue-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center transition-colors min-h-[44px]" style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;">
        <span class="hidden xs:inline">Claim whitelist</span>
        <span class="xs:hidden">Whitelist</span>
      </a>
      <a 
        href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/?ref=mwte3-ciaaa-aaaaf-ad7aq-cai"
        target="_blank"
        rel="noopener noreferrer"
        class="flex-shrink-0 text-gray-700 bg-gray-100 dark:text-gray-200 dark:bg-gray-700 border-2 border-gray-200 hover:border-2 hover:border-gray-300 dark:hover:border-gray-600 border focus:ring-4 focus:outline-none focus:ring-gray-100 dark:focus:ring-gray-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center transition-colors min-h-[44px]" 
        style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;"
      >
        <img src="https://oc.app/icon.png" alt="OpenChat" class="w-4 h-4 me-1 sm:me-2 flex-shrink-0" />
        <span class="hidden xs:inline">Support</span>
      </a>
      
      <!-- <div class="relative mr-2">
        <AccessCodesCenter />
      </div> -->
      <a use:link href="/wallet" class="flex-shrink-0 text-gray-900 dark:text-orange-400 bg-orange-100 dark:bg-gray-700 border-2 border-orange-500 hover:border-2 hover:border-orange-600 dark:hover:border-orange-400 hover:bg-orange-200 dark:hover:bg-gray-600 focus:ring-4 focus:outline-none focus:ring-orange-200 dark:focus:ring-orange-700 font-medium rounded-lg text-xs sm:text-sm px-2 sm:px-5 py-2 sm:py-2.5 text-center inline-flex items-center transition-colors min-h-[44px]" style="box-shadow: rgb(214, 195, 219) 0px 0px 2px 0px; border-radius: 16px;">
        <svg class="w-4 h-4 me-1 sm:me-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
        <span class="hidden xs:inline">Wallet</span>
      </a>
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

