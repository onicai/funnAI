<script lang="ts">
  import MainerAccordion from "../components/funnai/MainerAccordion.svelte";
  import MainerFeed from "../components/funnai/MainerFeed.svelte";
  import CyclesDisplay from "../components/funnai/CyclesDisplay.svelte";
  import WheelOfFortune from "../components/funnai/WheelOfFortune.svelte";
  import Footer from "../components/funnai/Footer.svelte";
  import { theme, store } from "../stores/store";

  let showAllEvents = true; // Default to showing all events

  // Handle toggle change
  async function handleToggleChange() {
    showAllEvents = !showAllEvents;
  }
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-8 py-8 flex-grow dark:bg-gray-900">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-0">
      <div class="card-style bg-white p-6 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200 flex flex-col overflow-hidden min-h-0">
        <div class="flex-grow overflow-hidden">
          <MainerAccordion />
        </div>
      </div>
      <div class="card-style bg-white p-4 rounded-lg shadow mb-2 dark:bg-gray-800 dark:text-gray-200 flex flex-col overflow-hidden min-h-0">
        <!-- Toggle controls -->
        <div class="flex-shrink-0 mb-4 border-b border-gray-200 dark:border-gray-700 pb-3">
          <div class="flex items-center justify-between">
            <h2 class="hidden sm:block text-lg font-semibold text-gray-900 dark:text-white">Activity feed</h2>
            <div class="flex items-center gap-3">
              <label class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                <span class="text-xs">My mAIners only</span>
                <button
                  type="button"
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                         {showAllEvents ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}
                         {!$store.isAuthed ? 'opacity-50 cursor-not-allowed' : ''}"
                  role="switch"
                  aria-checked={showAllEvents}
                  disabled={!$store.isAuthed}
                  on:click={handleToggleChange}
                >
                  <span class="sr-only">Toggle between all events and my mAIners only</span>
                  <span
                    class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                           {showAllEvents ? 'translate-x-6' : 'translate-x-1'}"
                  ></span>
                </button>
                <span class="text-xs">All events</span>
              </label>
            </div>
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