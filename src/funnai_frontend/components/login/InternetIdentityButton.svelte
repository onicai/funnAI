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
  };
</script>

<a
  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow cursor-pointer"
  on:click={connect}
>
  {#if loading === "internetidentity"}
    <LoadingSpinner size="h-6 w-6" />
  {:else}
    <img class="h-3" src={iclogo}  alt="ic wallet" />
    <span class="flex-1 ms-3 whitespace-nowrap">Internet Identity</span>
  {/if}
</a>
