<script lang="ts">
  import { store } from "../stores/store";
  import MainerAccordion from "../components/funnai/MainerAccordion.svelte";
  import ActivityFeedPanel from "../components/funnai/ActivityFeedPanel.svelte";
  import LoggedOutLanding from "../components/funnai/LoggedOutLanding.svelte";
  import Footer from "../components/funnai/Footer.svelte";
</script>

<div class="agent-page">
  <div class="agent-container">
    {#if $store.isAuthed}
      <div class="mx-auto w-full max-w-3xl flex flex-col gap-4 text-gray-200">
        <MainerAccordion />
        <ActivityFeedPanel />
      </div>
    {:else}
      <LoggedOutLanding />
    {/if}
  </div>
  <Footer />
</div>

<script context="module">
  export const Mainers = (props) => {
    return {
      component: Mainers,
      props
    };
  };
</script>
