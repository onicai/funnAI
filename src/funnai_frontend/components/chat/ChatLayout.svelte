<script lang="ts">
    import Router from "svelte-spa-router";
    import { onMount } from "svelte";
    import { store, theme, deviceType, supportsWebGpu } from "../../store";
  
    import UnsupportedBrowserBanner from "./UnsupportedBrowserBanner.svelte";
    import UnsupportedDeviceBanner from "./UnsupportedDeviceBanner.svelte";
    
    // Import routes from the separate file
    import { routes } from "./routes";
  
    import { syncLocalChanges } from "../../helpers/local_storage";
  
    onMount(async () => {
      // Check login state
      await store.checkExistingLoginAndConnect();
      if ($store.isAuthed) {
        syncLocalChanges();
      }
    });
</script>
  
<div class="App">
  {#if !(deviceType === 'desktop' || deviceType === 'Android')}
    <UnsupportedDeviceBanner />
  {:else if !supportsWebGpu}
    <UnsupportedBrowserBanner />
  {:else}
    <div class="flex flex-col min-h-[calc(100vh-42px)]">
      <main class="main flex flex-col flex-grow ml-0 transition-all duration-150 ease-in dark:bg-gray-900">
        <Router {routes} />
      </main>
    </div>
  {/if}
</div>