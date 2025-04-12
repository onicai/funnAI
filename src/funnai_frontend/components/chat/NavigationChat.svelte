<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import { link } from 'svelte-spa-router';
  import InstallToastNotification from './InstallToastNotification.svelte';

  let visibleInstallAppToast = false;

  const showInstallAppToast = () => {
    visibleInstallAppToast = true;
    // Automatically hide the toast
    setTimeout(() => {
      visibleInstallAppToast = false;
    }, 8000);
  };

  let modalIsOpen = false;

  // Function to open the modal
  const openModal = () => {
    modalIsOpen = true;
  };

  // Function to close the modal
  const closeModal = () => {
    modalIsOpen = false;
  };

  let toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  // Function to initialize dropdown functionality
  const initializeDropdown = () => {
    const dropdownMenuIconButton = document.getElementById('dropdownMenuIconButton');
    const dropdownDots = document.getElementById('dropdownDots');

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
          };
        };
      });

      dropdownDots.addEventListener('click', function (event) {
        event.stopPropagation();
      });
    }
  };

  onMount(() => {
    initializeDropdown();
  });
</script>

<div class="relative inline-block">
  <button id="dropdownMenuIconButton" data-dropdown-toggle="dropdownDots" class="inline-flex items-center p-2.5 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 border border-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100" type="button">
    {#if !$store.isAuthed}
      <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 4 15">
        <path d="M3.5 1.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Zm0 6.041a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Zm0 5.959a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z"/>
      </svg>
    {:else}
      <div class="w-10 h-10 -m-2.5 rounded-lg bg-violet-500 text-gray-100 flex justify-center items-center content-center">
        <svg class="w-6 h-6 text-text-white" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
          <path fill-rule="evenodd" d="M12 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm-2 9a4 4 0 0 0-4 4v1a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-1a4 4 0 0 0-4-4h-4Z" clip-rule="evenodd"/>
        </svg>
      </div>
    {/if}
  </button>

  <!-- Dropdown menu -->
  <div id="dropdownDots" class="absolute right-0 top-14 z-10 hidden bg-gray-100 divide-y divide-gray-200 rounded-lg shadow-2xl w-52 border-gray-200 border-4">
    <ul class="py-2 text-sm text-gray-700" aria-labelledby="dropdownMenuIconButton">
      <li>
        <a use:link href="/chat" class="block px-4 py-2 hover:bg-white">New Chat</a>
      </li>
      <li>
        <a use:link href="/chat/models" class="block px-4 py-2 hover:bg-white">AI Models ✨</a>
      </li>
      <li>
        <a use:link href="/chat/settings" class="block px-4 py-2 hover:bg-white">Settings</a>
      </li>
      <li>
        <a use:link href="/chat/about" class="block px-4 py-2 hover:bg-white">About</a>
      </li>
      <li>
        <a use:link href="/chat/brand" class="block px-4 py-2 hover:bg-white">Brand guide</a>
      </li>
    </ul>
    <div>
      <button on:click={() => showInstallAppToast()} class="block px-4 py-2 text-sm text-gray-700 hover:bg-white w-full text-left">Install app</button>
    </div>
  </div>
</div>


{#key visibleInstallAppToast}
  <InstallToastNotification showToast={visibleInstallAppToast} />
{/key}
