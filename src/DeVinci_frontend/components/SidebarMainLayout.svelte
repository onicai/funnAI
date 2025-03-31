<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels } from "../store";
import { get } from 'svelte/store';
import { location } from 'svelte-spa-router';
import funnailogo from "/funnai.webp";

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
</script>

<div class="sidebar-header font-fredoka flex flex-col items-center py-4 h-lvh">
    <h1 class="text-2xl font-semibold flex items-center gap-2">
      <a use:link href="/"><img src={funnailogo} alt="funnAI logo" class="w-24 h-auto"></a>
    </h1>
    <a use:link href="/" class="w-full" on:click={closeSidebar}>
      <button class={`w-full text-gray-700 h-16 mt-12 ${currentPath === '/' ? 'bg-gray-100' : 'bg-white'} hover:border-2 hover:border-gray-300`} style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button">
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
      <button class={`w-full text-gray-700 h-16 mt-4 ${currentPath === '/chat' ? 'bg-gray-100' : 'bg-white'} hover:border-2 hover:border-gray-300`} style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button">
        Chat
      </button>
    </a>
</div>
