<script lang="ts">
  import { store } from "../../stores/store";
  import CyclesDisplay from "./CyclesDisplay.svelte";
  import MainerFeed from "./MainerFeed.svelte";

  let isOpen = false;
  let showAllEvents = true;
  let hasUserToggledFeed = false;

  $: if (!hasUserToggledFeed) {
    showAllEvents = !$store.isAuthed;
  }

  function toggleAccordion() {
    isOpen = !isOpen;
  }

  function handleToggleChange() {
    hasUserToggledFeed = true;
    showAllEvents = !showAllEvents;
  }
</script>

<div class="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-agent-surface font-sans text-gray-200">
  <button
    type="button"
    on:click={toggleAccordion}
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/[0.02]"
    aria-expanded={isOpen}
  >
    <div class="relative flex items-center justify-between gap-3 px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2 mb-1">
          <p class="agent-eyebrow">Live</p>
          <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
            <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse"></span>
            Active
          </span>
        </div>
        <h2 class="text-base sm:text-lg font-semibold tracking-tight text-white">Activity feed</h2>
        <p class="mt-0.5 text-sm font-normal text-gray-400">
          {#if !$store.isAuthed}
            Protocol stream and burned cycles
          {:else}
            {showAllEvents ? 'Protocol events and burned cycles' : 'Your mAIners activity and burned cycles'}
          {/if}
        </p>
      </div>

      <div class="flex-shrink-0">
        <div
          class="w-9 h-9 rounded-xl border border-white/10 bg-white/[0.04] flex items-center justify-center transition-transform duration-300"
          style="transform: rotate({isOpen ? 180 : 0}deg)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>

  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/[0.06]">
      <div class="p-4 sm:p-5 space-y-4">
        <CyclesDisplay cycles={21246900000000} {showAllEvents} />

        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <p class="text-xs font-normal text-gray-500 min-h-[1.25rem]">
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

          <div class="inline-flex items-center self-start rounded-full border border-white/10 bg-white/[0.03] p-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
            <button
              type="button"
              class="relative px-3.5 py-1.5 text-[13px] font-medium rounded-full transition-all duration-200
                     {!showAllEvents
                       ? 'bg-[#653FC5] text-white shadow-sm'
                       : 'text-gray-400 hover:text-gray-200'}
                     {!$store.isAuthed ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
                     focus:outline-none focus:ring-2 focus:ring-[#653FC5]/40"
              disabled={!$store.isAuthed}
              on:click|stopPropagation={() => {
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
              on:click|stopPropagation={() => {
                if (showAllEvents) return;
                handleToggleChange();
              }}
            >
              Protocol
            </button>
          </div>
        </div>
      </div>

      <div class="h-[min(28rem,55vh)] border-t border-white/[0.06] overflow-hidden">
        {#if isOpen}
          <MainerFeed {showAllEvents} />
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.35s ease;
  }

  .accordion-content.accordion-open {
    max-height: 1200px;
  }
</style>
