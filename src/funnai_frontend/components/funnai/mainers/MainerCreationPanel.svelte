<script lang="ts">
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
  let userToggledOpen = false;
  let bonusCyclesTopupInPercent = 0;
  $: showCreationBonus = bonusCyclesTopupInPercent > 0;

  async function loadBonusPercent() {
    bonusCyclesTopupInPercent = await getBonusCyclesTopupInPercent();
  }

  $: if (isAuthenticated && $store.gameStateCanisterActor) {
    loadBonusPercent();
  }

  // Logged-out: open by default. Logged-in: closed unless the user toggled it.
  $: if (!userToggledOpen) {
    isOpen = shouldAutoOpen;
  }
  
  function toggleAccordion() {
    userToggledOpen = true;
    isOpen = !isOpen;
    onToggleAccordion('create');
  }
</script>

<!-- Accordion shell — one module border only -->
<div class="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-agent-surface font-sans">
  <button 
    on:click={toggleAccordion} 
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/[0.02]"
  >
    <div class="pointer-events-none absolute inset-0 opacity-40">
      <div class="absolute -top-16 right-0 h-32 w-48 rounded-full bg-agent-purple/20 blur-3xl"></div>
    </div>

    <div class="relative flex items-center justify-between px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0">
        <p class="mb-1 text-[10px] font-medium uppercase tracking-[0.2em] text-agent-purple">Deploy</p>
        <h2 class="text-base sm:text-lg font-semibold text-white tracking-tight">Create new mAIner</h2>
        <p class="text-sm font-normal text-gray-400 hidden sm:block mt-0.5">Spin up an autonomous mining agent</p>
      </div>
      
      <div class="flex-shrink-0 ml-4">
        <div class="w-9 h-9 rounded-xl bg-white/[0.04] flex items-center justify-center transition-transform duration-300" style="transform: rotate({isOpen ? 180 : 0}deg)">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>
  
  <!-- Accordion Content -->
  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/[0.06]">
      {#if isAuthenticated}
        <!-- Authenticated Content -->
        <div class="p-5 sm:p-6 space-y-5">
          
          <!-- Agent Type Selection -->
          <div class="space-y-4">
            <!-- Agent Type Card — soft surface, border only when selected -->
            <div 
              class="group relative overflow-hidden rounded-xl transition-all duration-300 cursor-pointer {modelType === 'Shared' 
                ? 'bg-agent-purple/10 ring-1 ring-agent-purple/40' 
                : 'bg-white/[0.03] hover:bg-white/[0.05]'}"
              on:click={() => onModelTypeChange('Shared')}
              on:keydown={(e) => e.key === 'Enter' && onModelTypeChange('Shared')}
              role="button"
              tabindex="0"
            >
              <div class="relative p-4 sm:p-5">
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4 flex-1 min-w-0">
                    <!-- Icon -->
                    <div class="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-agent-purple/15 flex items-center justify-center">
                      <svg class="w-6 h-6 sm:w-7 sm:h-7 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                        <h4 class="text-base sm:text-lg font-semibold text-white tracking-tight">mAIner Agent</h4>
                        {#if isProtocolActive && !stopMainerCreation}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 w-fit">
                            Available
                          </span>
                        {:else}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 w-fit">
                            Creation not available
                          </span>
                        {/if}
                      </div>
                      
                      <p class="text-sm text-gray-400 mb-4 leading-relaxed">
                        Shared infrastructure with optimized performance and instant deployment
                      </p>
                      
                      <!-- Features -->
                      <div class="flex flex-wrap gap-3 text-xs">
                        {#if isProtocolActive && !stopMainerCreation}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04]">
                            <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                            </svg>
                            <span class="font-medium text-gray-200">{mainerPrice} ICP</span>
                            {#if showCreationBonus}
                              <span class="text-[10px] font-medium text-agent-purple">+{bonusCyclesTopupInPercent}% bonus</span>
                            {/if}
                          </div>
                        {:else}
                          <a href="#/marketplace" class="agent-btn-ghost no-underline">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                            <span>Available on the marketplace</span>
                          </a>
                        {/if}
                        
                        <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white/[0.04]">
                          <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          <span class="font-medium text-gray-200">Instant deploy</span>
                        </div>

                        {#if showCreationBonus}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-agent-purple/10">
                            <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"/>
                            </svg>
                            <span class="font-medium text-agent-purple">+{bonusCyclesTopupInPercent}% bonus cycles</span>
                          </div>
                        {/if}
                      </div>
                    </div>
                  </div>
                  
                  <!-- Selection Indicator -->
                  <div class="flex-shrink-0 ml-4">
                    {#if modelType === 'Shared'}
                      <div class="w-6 h-6 sm:w-7 sm:h-7 bg-agent-purple rounded-full flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
                        </svg>
                      </div>
                    {:else}
                      <div class="w-6 h-6 sm:w-7 sm:h-7 border-2 border-white/20 rounded-full group-hover:border-agent-purple/50"></div>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Step 2 Indicator (if model selected) -->
          {#if selectedModel}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-xl bg-agent-purple/15 border border-agent-purple/30 text-agent-purple">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-200">Model Selected</span>
            </div>
          {/if}
          
          <!-- Step 3 Indicator (if payment copied) -->
          {#if addressCopied}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-xl bg-agent-purple/15 border border-agent-purple/30 text-agent-purple">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-200">Payment Ready</span>
            </div>
          {/if}
          
          <!-- Create Button -->
          <div class="pt-4 border-t border-white/[0.06]">
            <button 
              on:click={onCreateAgent} 
              disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation}
              class="agent-btn-primary w-full h-11 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-agent-purple"
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
              {#if isCreatingMainer}
                <svg class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>
                  {#if mainerCreationProgress.length > 0 && mainerCreationProgress[0].message.includes("Previous creation")}
                    Session on hold
                  {:else}
                    Creating mAIner...
                  {/if}
                </span>
              {:else}
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
                <span>Create mAIner Agent</span>
              {/if}
            </button>
          </div>
          
          <!-- Network Capacity Warning (if applicable) -->
          <NetworkCapacityPanel isVisible={stopMainerCreation} />
        </div>
        
      {:else}
        <!-- Guest — agentic connect CTA -->
        <div class="relative p-6 sm:p-8 overflow-hidden">
          <div class="pointer-events-none absolute inset-0">
            <div class="absolute -top-20 left-1/2 h-40 w-64 -translate-x-1/2 rounded-full bg-agent-purple/15 blur-3xl"></div>
            <div class="absolute inset-0 opacity-30" style="background-image: linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px); background-size: 24px 24px; mask-image: radial-gradient(ellipse at top, black 15%, transparent 65%);"></div>
          </div>

          <div class="relative max-w-lg mx-auto">
            <p class="mb-3 text-[10px] font-medium uppercase tracking-[0.22em] text-agent-purple">
              Autonomous network
            </p>
            <h3 class="text-2xl sm:text-[1.65rem] font-semibold tracking-tight text-white leading-tight">
              Enter the agentic world
            </h3>
            <p class="mt-3 text-sm font-normal leading-relaxed text-gray-400">
              Authenticate to deploy mAIners, compete in Proof-of-AI-Work challenges, and earn protocol rewards.
            </p>

            <div class="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div class="rounded-xl bg-white/[0.04] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Create agents</p>
              </div>
              <div class="rounded-xl bg-white/[0.04] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Join challenges</p>
              </div>
              <div class="rounded-xl bg-white/[0.04] px-3 py-3 text-center">
                <p class="text-xs font-medium text-gray-200">Earn rewards</p>
              </div>
            </div>

            <button 
              on:click={onToggleLoginModal} 
              class="agent-btn-primary mt-6 w-full sm:w-auto h-10"
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
