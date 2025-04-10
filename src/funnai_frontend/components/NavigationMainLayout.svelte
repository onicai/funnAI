<script lang="ts">
  import { onMount } from 'svelte';
  import { store, theme } from "../store";
  import { link } from 'svelte-spa-router';
  import LoginModal from './LoginModal.svelte';
  import TokensDisplay  from './TokensDisplay.svelte';

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

  <!-- <TokensDisplay icpBalance={199} funnaiBalance={1929} /> -->

  {#if !$store.isAuthed}
    <div class="flex items-center gap-2">
      <button type="button" on:click={() => {toggleModal()}} data-modal-target="crypto-modal" data-modal-toggle="crypto-modal" class="mr-1 text-gray-700 bg-gray-100 dark:text-gray-200 dark:bg-gray-700 border-2 border-gray-200 hover:border-2 hover:border-gray-300 dark:hover:border-gray-600 border focus:ring-4 focus:outline-none focus:ring-gray-100 dark:focus:ring-gray-700 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center" style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;">
        <svg aria-hidden="true" class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
        Connect
      </button>
    </div>
  {:else}
    <div class="flex gap-2">
      <a href="#" class="mr-1 cursor-not-allowed text-white dark:text-orange-500 bg-gray-500 dark:bg-gray-700 border-2 border-orange-500 hover:border-2 hover:border-orange-400 dark:hover:border-orange-700 focus:ring-4 focus:outline-none focus:ring-orange-200 dark:focus:ring-orange-700 font-medium rounded-lg text-sm px-5 py-2.5 text-center inline-flex items-center" style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 me-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
        Wallet (WIP)
      </a>
    </div>
  {/if}

<!-- Main modal -->
<div class={modalIsOpen ? "" : "hidden"}>
  <LoginModal {toggleModal} />
</div>

