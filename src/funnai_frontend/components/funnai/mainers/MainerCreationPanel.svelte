<script lang="ts">
  import { onMount } from 'svelte';
  import { tooltip } from "../../../helpers/utils/tooltip";
  import { getBonusCyclesTopupInPercent } from "../../../helpers/gameState";
  import { store } from "../../../stores/store";
  import NetworkCapacityPanel from './NetworkCapacityPanel.svelte';

  // Props
  export let isAuthenticated: boolean;
  export let isProtocolActive: boolean;
  export let stopMainerCreation: boolean;
  export let isCreatingMainer: boolean;
  export let mainerCreationProgress: Array<{message: string, timestamp: string, complete: boolean}>;
  export let mainerPrice: number;
  export let modelType: 'Own' | 'Shared';
  export let selectedModel: string;
  export let addressCopied: boolean;
  export let shouldAutoOpen: boolean = false;
  
  // Callbacks
  export let onCreateAgent: () => void;
  export let onToggleLoginModal: () => void;
  export let onToggleAccordion: (id: string) => void;
  export let onModelTypeChange: (type: 'Own' | 'Shared') => void;
  
  // Internal state for accordion
  let isOpen = false;
  let bonusCyclesTopupInPercent = 0;
  $: showCreationBonus = bonusCyclesTopupInPercent > 0;

  async function loadBonusPercent() {
    bonusCyclesTopupInPercent = await getBonusCyclesTopupInPercent();
  }

  $: if (isAuthenticated && $store.gameStateCanisterActor) {
    loadBonusPercent();
  }
  
  function toggleAccordion() {
    isOpen = !isOpen;
    onToggleAccordion('create');
  }
  
  onMount(() => {
    if (shouldAutoOpen) {
      setTimeout(() => {
        isOpen = true;
      }, 100);
    }
  });
</script>

<!-- Accordion shell -->
<div class="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c0b12] font-sans">
  <button 
    on:click={toggleAccordion} 
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/[0.02]"
  >
    <div class="pointer-events-none absolute inset-0 opacity-40">
      <div class="absolute -top-16 right-0 h-32 w-48 rounded-full bg-[#653FC5]/20 blur-3xl"></div>
    </div>

    <div class="relative flex items-center justify-between px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0">
        <p class="mb-1 text-[10px] font-medium uppercase tracking-[0.2em] text-[#653FC5]">Deploy</p>
        <h2 class="text-base sm:text-lg font-semibold text-white tracking-tight">Create new mAIner</h2>
        <p class="text-sm font-normal text-gray-400 hidden sm:block mt-0.5">Spin up an autonomous mining agent</p>
      </div>
      
      <div class="flex-shrink-0 ml-4">
        <div class="w-9 h-9 rounded-xl border border-white/10 bg-white/[0.04] flex items-center justify-center transition-transform duration-300" style="transform: rotate({isOpen ? 180 : 0}deg)">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>
  
  <!-- Accordion Content -->
  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/[0.06] bg-[#0c0b12]">
      {#if isAuthenticated}
        <!-- Authenticated Content -->
        <div class="p-6 sm:p-8 space-y-6">
          
          <!-- Agent Type Selection -->
          <div class="space-y-4">
            <!-- Agent Type Card -->
            <div 
              class="group relative overflow-hidden border-2 rounded-2xl transition-all duration-300 cursor-pointer {modelType === 'Shared' 
                ? 'border-emerald-500 dark:border-emerald-400 bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 shadow-lg shadow-emerald-500/20' 
                : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-emerald-300 dark:hover:border-emerald-600 hover:shadow-md'}"
              on:click={() => onModelTypeChange('Shared')}
              on:keydown={(e) => e.key === 'Enter' && onModelTypeChange('Shared')}
              role="button"
              tabindex="0"
            >
              <!-- Decorative background elements -->
              <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-emerald-200/20 to-cyan-200/20 dark:from-emerald-500/10 dark:to-cyan-500/10 rounded-full -translate-y-16 translate-x-16 blur-2xl"></div>
              
              <div class="relative p-5 sm:p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4 flex-1 min-w-0">
                    <!-- Icon -->
                    <div class="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 flex items-center justify-center shadow-lg">
                      <svg class="w-6 h-6 sm:w-7 sm:h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                        <h4 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white">mAIner Agent</h4>
                        {#if isProtocolActive && !stopMainerCreation}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 w-fit border border-green-200 dark:border-green-800">
                            Available
                          </span>
                        {:else}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 w-fit border border-red-200 dark:border-red-800">
                            Creation not available
                          </span>
                        {/if}
                      </div>
                      
                      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                        Shared infrastructure with optimized performance and instant deployment
                      </p>
                      
                      <!-- Features -->
                      <div class="flex flex-wrap gap-3 text-xs">
                        {#if isProtocolActive && !stopMainerCreation}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg border border-gray-200/60 dark:border-gray-600/60">
                            <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                            </svg>
                            <span class="font-semibold text-gray-700 dark:text-gray-300">{mainerPrice} ICP</span>
                            {#if showCreationBonus}
                              <span class="text-[10px] font-medium text-emerald-600 dark:text-emerald-400">+{bonusCyclesTopupInPercent}% bonus</span>
                            {/if}
                          </div>
                        {:else}
                          <a href="#/marketplace" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium transition-all duration-200 shadow-md hover:shadow-lg no-underline">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                            <span>Available on the marketplace</span>
                          </a>
                        {/if}
                        
                        <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg border border-gray-200/60 dark:border-gray-600/60">
                          <svg class="w-4 h-4 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          <span class="font-semibold text-gray-700 dark:text-gray-300">Instant deploy</span>
                        </div>

                        {#if showCreationBonus}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-50/80 dark:bg-emerald-900/20 backdrop-blur-sm rounded-lg border border-emerald-200/60 dark:border-emerald-700/60">
                            <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"/>
                            </svg>
                            <span class="font-semibold text-emerald-700 dark:text-emerald-300">+{bonusCyclesTopupInPercent}% bonus cycles</span>
                          </div>
                        {/if}
                      </div>
                    </div>
                  </div>
                  
                  <!-- Selection Indicator -->
                  <div class="flex-shrink-0 ml-4">
                    {#if modelType === 'Shared'}
                      <div class="w-6 h-6 sm:w-7 sm:h-7 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center shadow-lg">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                        </svg>
                      </div>
                    {:else}
                      <div class="w-6 h-6 sm:w-7 sm:h-7 border-2 border-gray-300 dark:border-gray-600 rounded-full"></div>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Step 2 Indicator (if model selected) -->
          {#if selectedModel}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Model Selected</span>
            </div>
          {/if}
          
          <!-- Step 3 Indicator (if payment copied) -->
          {#if addressCopied}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">Payment Ready</span>
            </div>
          {/if}
          
          <!-- Create Button -->
          <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
            <button 
              on:click={onCreateAgent} 
              disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation}
              class="group relative w-full overflow-hidden bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 text-white font-bold px-6 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60"
              use:tooltip={{ 
                text: isCreatingMainer 
                  ? "⚠️ mAIner creation in progress! Please wait for it to complete. DO NOT refresh or navigate away - this will stop the creation and you'll need to start over."
                  : stopMainerCreation 
                    ? "mAIner creation is temporarily disabled due to network capacity"
                    : !isProtocolActive 
                      ? "Protocol is currently inactive"
                      : "",
                direction: 'top',
                textSize: 'xs'
              }}
            >
              <!-- Button glow effect -->
              <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
              
              <span class="relative flex items-center justify-center space-x-2">
                {#if isCreatingMainer}
                  <svg class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="text-base sm:text-lg">
                    {#if mainerCreationProgress.length > 0 && mainerCreationProgress[0].message.includes("Previous creation")}
                      Session on hold
                    {:else}
                      Creating mAIner...
                    {/if}
                  </span>
                {:else}
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                  <span class="text-base sm:text-lg">Create mAIner Agent</span>
                {/if}
              </span>
            </button>
          </div>
          
          <!-- Network Capacity Warning (if applicable) -->
          <NetworkCapacityPanel isVisible={stopMainerCreation} />
        </div>
        
      {:else}
        <!-- Guest — agentic connect CTA -->
        <div class="relative p-6 sm:p-8 overflow-hidden">
          <div class="pointer-events-none absolute inset-0">
            <div class="absolute -top-20 left-1/2 h-40 w-64 -translate-x-1/2 rounded-full bg-[#653FC5]/15 blur-3xl"></div>
            <div class="absolute inset-0 opacity-30" style="background-image: linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px); background-size: 24px 24px; mask-image: radial-gradient(ellipse at top, black 15%, transparent 65%);"></div>
          </div>

          <div class="relative max-w-lg mx-auto">
            <p class="mb-3 text-[10px] font-medium uppercase tracking-[0.22em] text-[#653FC5]">
              Autonomous network
            </p>
            <h3 class="text-2xl sm:text-[1.65rem] font-semibold tracking-tight text-white leading-tight">
              Enter the agentic world
            </h3>
            <p class="mt-3 text-sm font-normal leading-relaxed text-gray-400">
              Authenticate to deploy mAIners, compete in Proof-of-AI-Work challenges, and earn protocol rewards.
            </p>

            <div class="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div class="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Create agents</p>
              </div>
              <div class="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Join challenges</p>
              </div>
              <div class="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Earn rewards</p>
              </div>
            </div>

            <button 
              on:click={onToggleLoginModal} 
              class="mt-6 w-full sm:w-auto inline-flex items-center justify-center h-10 px-5 rounded-full bg-[#653FC5] text-white text-[13px] font-semibold tracking-tight shadow-[0_0_0_1px_rgba(101,63,197,0.35),0_8px_20px_-8px_rgba(101,63,197,0.55)] transition-all duration-200 hover:bg-[#5a37b5]"
            >
              Connect wallet
            </button>

            <p class="mt-5 text-[11px] font-normal tracking-wide text-gray-600">
              End-to-end identity · Internet Identity & NFID
            </p>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
    opacity: 0;
  }
  
  .accordion-content.accordion-open {
    max-height: 2500px;
    opacity: 1;
    overflow: visible;
  }
</style>
