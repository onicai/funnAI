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

<div class="agent-page">
  <div class="agent-container">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full min-h-0">
      <!-- Left column: no outer frame — each module keeps its own border -->
      <div class="mb-2 flex flex-col min-h-0 text-gray-200">
        <div class="flex-grow min-h-0">
          <MainerAccordion />
        </div>
      </div>
      <div class="agent-card !bg-agent-surface rounded-2xl p-0 mb-2 flex flex-col overflow-hidden min-h-0 text-gray-200">
        <div class="relative z-[1] flex flex-col flex-grow min-h-0 bg-agent-surface">
        <div class="flex-shrink-0 mb-4 p-4 pb-0">
          <CyclesDisplay cycles={21246900000000} {showAllEvents} />
        </div>
        <!-- Toggle controls -->
        <div class="flex-shrink-0 px-4 pb-3">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <p class="text-[10px] font-medium uppercase tracking-[0.2em] text-[#653FC5]">Live</p>
              <h2 class="mt-0.5 text-base font-semibold tracking-tight text-white">Activity feed</h2>
            </div>
            <div class="inline-flex items-center rounded-full border border-white/10 bg-white/[0.03] p-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
              <button
                type="button"
                class="relative px-3.5 py-1.5 text-[13px] font-medium rounded-full transition-all duration-200
                       {!showAllEvents 
                         ? 'bg-[#653FC5] text-white shadow-sm' 
                         : 'text-gray-400 hover:text-gray-200'}
                       {!$store.isAuthed ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
                       focus:outline-none focus:ring-2 focus:ring-[#653FC5]/40"
                disabled={!$store.isAuthed}
                on:click={() => {
                  if (!showAllEvents) return;
                  handleToggleChange();
                }}
              >
                {$store.isAuthed ? 'My mAIners' : 'Personal'}
              </button>
              <button
                type="button"
                class="relative px-3.5 py-1.5 text-[13px] font-medium rounded-full transition-all duration-200 cursor-pointer
                       {showAllEvents 
                         ? 'bg-[#653FC5] text-white shadow-sm' 
                         : 'text-gray-400 hover:text-gray-200'}
                       focus:outline-none focus:ring-2 focus:ring-[#653FC5]/40"
                on:click={() => {
                  if (showAllEvents) return;
                  handleToggleChange();
                }}
              >
                Protocol
              </button>
            </div>
          </div>
          <p class="mt-2.5 text-xs font-normal text-gray-500">
            {#if !$store.isAuthed}
              {showAllEvents 
                ? 'Major events across the protocol' 
                : 'Connect to see personalized agent activity'}
            {:else}
              {showAllEvents 
                ? 'Major events across the protocol' 
                : 'Activity from your mAIners, including victories and rewards'}
            {/if}
          </p>
        </div>
        
        <div class="flex-grow overflow-hidden min-h-0 border-t border-white/[0.06]">
          <MainerFeed {showAllEvents} />
        </div>
        </div>
      </div>
    </div>
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