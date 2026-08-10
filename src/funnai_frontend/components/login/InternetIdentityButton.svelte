<script lang="ts">
  import { store } from "../../stores/store";
  import LoadingSpinner from "../LoadingSpinner.svelte";
  import iclogo from "/internet-computer.svg";

  export let loading;
  export let toggleModal;

  async function connect() {
    try {
      loading = "internetidentity";
      await store.internetIdentityConnect();
      loading = "";
      toggleModal();
    } catch (error) {
      console.error("Internet Identity connection failed:", error);
      loading = "";
    }
  }
</script>

<button
  type="button"
  class="group flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3.5 text-left transition-all duration-200 hover:border-[#653FC5]/40 hover:bg-[#653FC5]/10 disabled:cursor-not-allowed disabled:opacity-60"
  disabled={loading === "internetidentity" || (loading !== "" && loading !== "internetidentity")}
  on:click={connect}
>
  {#if loading === "internetidentity"}
    <div class="flex w-full items-center justify-center py-0.5">
      <LoadingSpinner size="h-5 w-5" />
    </div>
  {:else}
    <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/5 ring-1 ring-white/10">
      <img class="h-4 w-auto" src={iclogo} alt="" />
    </span>
    <span class="min-w-0 flex-1">
      <span class="block text-sm font-medium text-gray-100">Internet Identity</span>
      <span class="block text-xs font-normal text-gray-500">ICP wallet</span>
    </span>
  {/if}
</button>
