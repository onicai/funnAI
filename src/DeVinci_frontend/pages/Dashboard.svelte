<script lang="ts">
  import MainerAccordion from "../components/MainerAccordion.svelte";
  import MainerFeed from "../components/MainerFeed.svelte";
  import CyclesDisplay from "../components/CyclesDisplay.svelte";
</script>

<div class="container mx-auto px-8 py-8">
  <h1 class="text-2xl text-gray-400 font-bold mb-6">My mAIners</h1>
  
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
    <div class="card-style p-6 rounded-lg shadow mb-2">
      <MainerAccordion />
    </div>
    <div class="card-style p-4 rounded-lg shadow mb-2">
      <CyclesDisplay cycles={2124690} />
      <MainerFeed />
    </div>
  </div>
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 