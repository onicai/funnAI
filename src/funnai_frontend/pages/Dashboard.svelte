<script lang="ts">
  import MainerAccordion from "../components/MainerAccordion.svelte";
  import MainerFeed from "../components/MainerFeed.svelte";
  import CyclesDisplay from "../components/CyclesDisplay.svelte";
  import WheelOfFortune from "../components/WheelOfFortune.svelte";
  import Footer from "../components/Footer.svelte";
  import { theme } from "../stores/store";
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-8 py-8 flex-grow dark:bg-gray-900">
    <WheelOfFortune />
    <div class="flex items-center p-4 mt-4 mb-6 text-md text-yellow-800 border border-yellow-300 rounded-lg bg-yellow-50 dark:bg-gray-800 dark:border-yellow-600 dark:text-yellow-300" role="alert">
      <svg class="shrink-0 inline w-12 h-12 me-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
      </svg>
      <span class="sr-only">Info</span>
      <div>
        <span class="font-xl">Heads up!</span> 
        The app is currently under construction, and some features are still being developed. You can check out the prototype to get a glimpse of what's coming and even get the chance to be one of the first to mine FUNNAI if you win the raffle. Keep in mind that the current UI is still a work in progress, and functionality is limited for now, but exciting things are on the way!
      </div>
    </div>
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