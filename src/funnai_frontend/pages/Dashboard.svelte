<script lang="ts">
  import MainerAccordion from "../components/funnai/MainerAccordion.svelte";
  import MainerFeed from "../components/funnai/MainerFeed.svelte";
  import CyclesDisplay from "../components/funnai/CyclesDisplay.svelte";
  import WheelOfFortune from "../components/funnai/WheelOfFortune.svelte";
  import Footer from "../components/funnai/Footer.svelte";
  import { theme, store } from "../stores/store";

  let showAllEvents = false; // Changed default to "My mAIners only"

  // Set default based on authentication status
  // Non-logged users: "All events" (true), Logged users: "My mAIners" (false)
  $: showAllEvents = !$store.isAuthed;

  // Handle toggle change
  async function handleToggleChange() {
    showAllEvents = !showAllEvents;
  }
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-2 md:px-8 py-2 md:py-8 flex-grow dark:bg-gray-900">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-0">
      <div class="card-style bg-white p-2 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200 flex flex-col overflow-hidden min-h-0">
        <div class="flex-grow overflow-hidden">
          <MainerAccordion />
        </div>
      </div>
      <div class="card-style bg-white p-4 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200 flex flex-col overflow-hidden min-h-0">
        <!-- Toggle controls -->
        <div class="flex-shrink-0 mb-4 border-b border-gray-200 dark:border-gray-700 pb-4">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Activity Feed</h2>
            <div class="flex items-center justify-center sm:justify-end">
              <div class="inline-flex items-center bg-white dark:bg-gray-800 rounded-lg p-1 shadow-sm border border-gray-200 dark:border-gray-600">
                <button
                  type="button"
                  class="relative px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ease-in-out
                         {!showAllEvents 
                           ? 'bg-blue-600 text-white shadow-sm' 
                           : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'}
                         {!$store.isAuthed ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800"
                  disabled={!$store.isAuthed}
                  on:click={() => {
                    if (!showAllEvents) return;
                    handleToggleChange();
                  }}
                >
                  {$store.isAuthed ? 'My mAIners' : 'Personal View'}
                </button>
                <button
                  type="button"
                  class="relative px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ease-in-out
                         {showAllEvents 
                           ? 'bg-blue-600 text-white shadow-sm' 
                           : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100'}
                         cursor-pointer
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800"
                  on:click={() => {
                    if (showAllEvents) return;
                    handleToggleChange();
                  }}
                >
                  All Events
                </button>
              </div>
            </div>
          </div>
          <div class="mt-3">
            <p class="text-xs text-gray-500 dark:text-gray-400 text-center sm:text-left">
              {#if !$store.isAuthed}
                {showAllEvents 
                  ? 'Viewing major events across the protocol' 
                  : 'Connect your wallet to see personalized mAIner activity'}
              {:else}
                {showAllEvents 
                  ? 'Viewing major events across the protocol' 
                  : 'Viewing all activity from your mAIners, including victories and rewards'}
              {/if}
            </p>
          </div>
        </div>
        <div class="flex-shrink-0 mb-4">
          <CyclesDisplay cycles={21246900000000} {showAllEvents} />
        </div>
        <div class="flex-grow overflow-hidden min-h-0">
          <MainerFeed {showAllEvents} />
        </div>
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