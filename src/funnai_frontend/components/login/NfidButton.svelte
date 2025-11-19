<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import LoadingSpinner from "../LoadingSpinner.svelte";
  import nfidlogo from "/nfid.webp"

  export let loading;
  export let toggleModal;

  let nfidReady = false;

  // Pre-initialize NFID IdentityKit on component mount so it's ready when user clicks
  onMount(async () => {
    // Start pre-initializing and wait for it to complete
    await store.preInitNfid?.();
    nfidReady = true;
  });

  async function connect() {
    if (!nfidReady) {
      console.warn("NFID not ready yet, please wait...");
      return;
    }
    
    try {
      loading = "nfid";
      await store.nfidConnect();
      loading = "";
      toggleModal();
    } catch (error) {
      console.error("NFID connection failed:", error);
      loading = "";
    }
  };
</script>

<a
  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow"
  class:cursor-pointer={nfidReady && loading !== "nfid"}
  class:opacity-60={!nfidReady || loading === "nfid"}
  class:cursor-not-allowed={!nfidReady && loading !== "nfid"}
  on:click={connect}
>
  {#if loading === "nfid"}
    <LoadingSpinner size="h-6 w-6" />
  {:else}
    <img class="h-5" src={nfidlogo}  alt="nfid wallet" />
    <span class="flex-1 ms-3 whitespace-nowrap">NFID (incl. Google)</span>
  {/if}
</a>
