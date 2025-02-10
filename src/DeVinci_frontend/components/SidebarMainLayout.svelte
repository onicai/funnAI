<script lang="ts">
import { onMount } from 'svelte';
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

  // Reactive statement to check if the user has already downloaded at least one AI model
  $: userHasDownloadedAtLeastOneModel = $downloadedModels.length > 0;
</script>

<div class="sidebar-header flex flex-col items-center justify-between py-4 h-lvh">
    funnAI
</div>
