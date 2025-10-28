<script lang="ts">
  import { onMount } from 'svelte';
  import { tooltip } from "../../../helpers/utils/tooltip";

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

<div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-purple-600/20 to-blue-600/20 dark:from-purple-900/40 dark:to-blue-900/40 rounded-t-lg">
  <button on:click={toggleAccordion} class="w-full flex justify-between items-center py-4 sm:py-8 px-4 sm:px-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-sm sm:text-base font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform border border-purple-500/20">
    <span class="flex items-center min-w-0 flex-1">
      <div class="flex-shrink-0 w-6 h-6 sm:w-8 sm:h-8 bg-white/20 rounded-lg flex items-center justify-center mr-2 sm:mr-3 shadow-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
        </svg>
      </div>
      <div class="flex flex-col items-start min-w-0">
        <span class="text-base sm:text-lg font-bold truncate">Create new mAIner</span>
        <span class="text-purple-100 text-xs sm:text-xs font-normal hidden sm:block">Start your AI mining journey</span>
      </div>
    </span>
    <span class="text-white/80 transition-transform duration-300 bg-white/10 rounded-full p-1 flex-shrink-0 ml-2" style="transform: rotate({isOpen ? 0 : 180}deg)">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4 sm:w-5 sm:h-5">
        <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
  <div id="content-create" class="accordion-content bg-white dark:bg-gray-900" class:accordion-open={isOpen}>
    <div class="text-sm text-gray-700 dark:text-gray-300 space-y-4 p-5 dark:bg-gray-800">
      
    {#if isAuthenticated}
      <ol class="relative mx-2 text-gray-500 dark:text-gray-400 border-s border-gray-200 dark:border-gray-700">                  
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {modelType ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                </svg>
            </span>
            <h3 class="font-medium leading-tight mb-3 dark:text-gray-300">AI Agent type</h3>
            
            <!-- Modern Agent Type Selector -->
            <div class="space-y-3 mb-2">
              <!-- Shared Model Card -->
              <div 
                class="relative border-2 rounded-xl p-3 sm:p-4 cursor-pointer transition-all duration-200 hover:shadow-md {modelType === 'Shared' 
                  ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' 
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-purple-300 dark:hover:border-purple-600'}"
                on:click={() => onModelTypeChange('Shared')}
                on:keydown={(e) => e.key === 'Enter' && onModelTypeChange('Shared')}
                role="button"
                tabindex="0"
              >
                <!-- Selection indicator -->
                <div class="absolute top-2 sm:top-3 right-2 sm:right-3">
                  {#if modelType === 'Shared'}
                    <div class="w-4 h-4 sm:w-5 sm:h-5 bg-purple-600 rounded-full flex items-center justify-center">
                      <svg class="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  {:else}
                    <div class="w-4 h-4 sm:w-5 sm:h-5 border-2 border-gray-300 dark:border-gray-600 rounded-full"></div>
                  {/if}
                </div>

                <div class="flex items-start space-x-3 pr-6 sm:pr-8">
                  <!-- Icon -->
                  <div class="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                    <svg class="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                  </div>

                  <!-- Content -->
                  <div class="flex-1 min-w-0">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-2 mb-1">
                      <h4 class="text-sm font-semibold text-gray-900 dark:text-gray-100">mAIner Agent</h4>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 w-fit mt-1 sm:mt-0">
                        Not available
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-2">
                      Shared infrastructure with optimized performance
                    </p>
                    <div class="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-x-4 sm:space-y-0 text-xs text-gray-500 dark:text-gray-400">
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                        </svg>
                        <span>{mainerPrice} ICP</span>
                      </div>
                      <div class="flex items-center space-x-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        <span>Instant deploy</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </li>
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {selectedModel ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if selectedModel}
                  <!-- Checkmark icon for when model is selected -->
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <!-- Selection/Choose icon for default state -->
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                  </svg>
                {/if}
            </span>
        </li>
        <li class="mb-6 ms-6">
            <span class="absolute flex items-center justify-center w-8 h-8 {addressCopied ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-100 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if addressCopied}
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                {/if}
            </span>
            <h3 class="font-medium leading-tight dark:text-gray-300">Create Agent</h3>
        </li>
      </ol>

      <div class="flex flex-col items-stretch sm:items-end">
        <button 
          on:click={onCreateAgent} 
          disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation}
          class="bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-4 py-2 rounded-xl transition-colors mb-2 w-full sm:w-auto sm:mr-2 text-sm sm:text-base"
          class:opacity-50={isCreatingMainer || !isProtocolActive || stopMainerCreation}
          class:cursor-not-allowed={isCreatingMainer || !isProtocolActive || stopMainerCreation}
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
            {#if mainerCreationProgress.length > 0 && mainerCreationProgress[0].message.includes("Previous creation")}
              Session on hold
            {:else}
              Creating mAIner...
            {/if}
          {:else}
            Create mAIner Agent
          {/if}
        </button>
      </div>

    {:else}
      <div class="h-full flex">
        <div class="relative overflow-hidden bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 dark:from-blue-600 dark:via-purple-600 dark:to-indigo-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform flex-1 flex flex-col">
          <!-- Background decoration -->
          <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
          
          <div class="relative flex-1 flex items-center justify-center p-4 sm:p-6">
            <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
              <!-- Icon with enhanced styling -->
              <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
                <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              
              <!-- Content section -->
              <div class="space-y-3 sm:space-y-4">
                <div class="flex flex-col items-center text-center space-y-2">
                  <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                    Get Started
                  </div>
                  <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Connect to begin</h3>
                </div>
                
                <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
                  <p class="font-semibold text-base sm:text-lg">🚀 Ready to start AI mining?</p>
                  <p>Connect your wallet to create and manage your mAIners, participate in challenges, and earn rewards through AI competitions.</p>
                </div>
                
                <!-- Features list -->
                <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 border border-white/20 shadow-sm text-left">
                  <div class="space-y-2 text-white/90 text-sm">
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Create and manage AI agents</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Participate in AI challenges</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                      </svg>
                      <span>Earn rewards and tokens</span>
                    </div>
                  </div>
                </div>
                
                <!-- Enhanced button -->
                <div class="pt-3">
                  <button 
                    on:click={onToggleLoginModal} 
                    class="group relative inline-flex items-center justify-center px-6 py-3 text-base font-bold text-blue-600 bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-102 border-2 border-white/20 backdrop-blur-sm"
                  >
                    <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                    </svg>
                    Connect Wallet
                    <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-100 to-purple-100 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                  </button>
                </div>
                
                <!-- Additional info -->
                <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
                  <div class="flex items-center justify-center space-x-2">
                    <span class="text-sm">🔒</span>
                    <span class="font-medium">Secure connection via Internet Identity or NFID</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
    transition: all 0.3s ease-in-out;
  }
  
  .accordion-content.accordion-open {
    max-height: 2000px;
    overflow: visible;
  }
</style>

