<script lang="ts">
  import { store } from "../../stores/store";
  import LoadingSpinner from "../LoadingSpinner.svelte";
  import nfidlogo from "/nfid.webp"

  export let loading;
  export let toggleModal;

  async function connect() {
    loading = "nfid";
    store.nfidConnect();
    loading = "";
    toggleModal();
  };
</script>

<a
  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow cursor-pointer"
  on:click={connect}
>
  {#if loading === "nfid"}
    <LoadingSpinner size="h-6 w-6" />
  {:else}
    <img class="h-5" src={nfidlogo}  alt="nfid wallet" />
    <span class="flex-1 ms-3 whitespace-nowrap">NFID (incl. Google)</span>
  {/if}
</a>
