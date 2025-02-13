<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels } from "../store";

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
</script>

<div class="sidebar-header flex flex-col items-center py-4 h-lvh">
    <h1 class="text-2xl font-bold"><a use:link href="/">funnAI</a></h1>
    <a use:link href="/" class="w-full" on:click={closeSidebar}>
      <button style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button" class="w-full h-16 mt-12 bg-white">
        Dashboard
      </button>
    </a>
    <a use:link href="/funn" class="w-full" on:click={closeSidebar}>
      <button style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button" class="w-full h-16 mt-4 bg-white">
        funnAI
      </button>
    </a>
    <a use:link href="/wallet" class="w-full" on:click={closeSidebar}>
      <button style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button" class="w-full h-16 mt-4 bg-white">
        Wallet
      </button>
    </a>
    <a use:link href="/chat" class="w-full" on:click={closeSidebar}>
      <button style="box-shadow: rgb(214, 195, 219) 0px 0px 6px 0px; border-radius: 16px;" type="button" class="w-full h-16 mt-4 bg-white">
        Chat
      </button>
    </a>
</div>
