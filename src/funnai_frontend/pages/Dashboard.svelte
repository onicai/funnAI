<script lang="ts">
  import MainerAccordion from "../components/funnai/MainerAccordion.svelte";
  import MainerFeed from "../components/funnai/MainerFeed.svelte";
  import CyclesDisplay from "../components/funnai/CyclesDisplay.svelte";
  import WheelOfFortune from "../components/funnai/WheelOfFortune.svelte";
  import Footer from "../components/funnai/Footer.svelte";
  import { theme } from "../store";
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-8 py-8 flex-grow dark:bg-gray-900">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      <div class="card-style bg-white p-6 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200">
        <MainerAccordion />
      </div>
      <div class="card-style bg-white p-4 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200">
        <CyclesDisplay cycles={21246900000000} />
        <MainerFeed />
      </div>
    </div>
  </div>
  <Footer />
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 