<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import LoadingSpinner from "../LoadingSpinner.svelte";
  import nfidlogo from "/nfid.webp"

  export let loading;
  export let toggleModal;

  let nfidReady = false;

  onMount(async () => {
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
  }
</script>

<button
  type="button"
  class="group flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/3 px-4 py-3.5 text-left transition-all duration-200 hover:border-agent-purple/40 hover:bg-agent-purple/10 disabled:cursor-not-allowed disabled:opacity-60"
  disabled={!nfidReady || loading === "nfid" || (loading !== "" && loading !== "nfid")}
  on:click={connect}
>
  {#if loading === "nfid"}
    <div class="flex w-full items-center justify-center py-0.5">
      <LoadingSpinner size="h-5 w-5" />
    </div>
  {:else}
    <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/5 ring-1 ring-white/10">
      <img class="h-5 w-auto" src={nfidlogo} alt="" />
    </span>
    <span class="min-w-0 flex-1">
      <span class="block text-sm font-medium text-gray-100">NFID</span>
      <span class="block text-xs font-normal text-gray-500">
        {nfidReady ? 'Includes Google sign-in' : 'Preparing…'}
      </span>
    </span>
  {/if}
</button>
