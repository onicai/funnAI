<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { tooltip } from "../../../helpers/utils/tooltip";

  // Props
  export let isAuthenticated: boolean;
  export let isProtocolActive: boolean;
  export let stopMainerCreation: boolean;
  export let isCreatingMainer: boolean;
  export let mainerCreationProgress: Array<{message: string, timestamp: string, complete: boolean}>;
  export let mainerPrice: number;
  export let selectedModel: string;
  export let addressCopied: boolean;
  export let shouldAutoOpen: boolean = false;
  export let isAuctionActive: boolean = false;
  export let availableMainers: number = 0;
  export let nextPriceDropAtNs: number = 0;
  
  // Callbacks
  export let onCreateAgent: () => void;
  export let onToggleLoginModal: () => void;
  export let onToggleAccordion: (id: string) => void;
  export let onUpdateAuctionData: () => Promise<void>;
  
  // Internal state for accordion
  let isOpen = false;
  
  // Timer state
  let timeUntilNextDrop = "";
  let countdownInterval: number | null = null;
  let auctionDataInterval: number | null = null;
  
  function toggleAccordion() {
    isOpen = !isOpen;
    onToggleAccordion('create');
  }
  
  // Calculate countdown timer
  function updateCountdown() {
    if (!isAuctionActive || nextPriceDropAtNs === 0) {
      timeUntilNextDrop = "";
      return;
    }
    
    const nowNs = Date.now() * 1_000_000; // Convert ms to ns
    const remainingNs = nextPriceDropAtNs - nowNs;
    
    if (remainingNs <= 0) {
      timeUntilNextDrop = "Updating price...";
      // Trigger data refresh when timer expires
      if (onUpdateAuctionData) {
        onUpdateAuctionData();
      }
      return;
    }
    
    const remainingSeconds = Math.floor(remainingNs / 1_000_000_000);
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    
    if (minutes > 0) {
      timeUntilNextDrop = `${minutes}m ${seconds}s`;
    } else {
      timeUntilNextDrop = `${seconds}s`;
    }
  }
  
  onMount(() => {
    if (shouldAutoOpen) {
      setTimeout(() => {
        isOpen = true;
      }, 100);
    }
    
    // Start countdown timer if auction is active
    if (isAuctionActive) {
      updateCountdown();
      countdownInterval = window.setInterval(updateCountdown, 1000);
    }
    
    // Start interval to check available mainers every 2 seconds
    auctionDataInterval = window.setInterval(() => {
      if (onUpdateAuctionData) {
        onUpdateAuctionData();
      }
    }, 2000);
  });
  
  onDestroy(() => {
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    if (auctionDataInterval) {
      clearInterval(auctionDataInterval);
    }
  });
  
  // Restart countdown when auction state changes
  $: {
    if (isAuctionActive && nextPriceDropAtNs > 0) {
      updateCountdown();
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      countdownInterval = window.setInterval(updateCountdown, 1000);
    } else {
      if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
      }
      timeUntilNextDrop = "";
    }
  }
</script>

<!-- Accordion shell -->
<div class="relative overflow-hidden rounded-2xl border border-white/8 bg-agent-surface font-sans">
  <button 
    on:click={toggleAccordion} 
    class="group w-full relative overflow-hidden transition-colors duration-200 {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'} hover:bg-white/2"
  >
    <div class="pointer-events-none absolute inset-0 opacity-40">
      <div class="absolute -top-16 right-0 h-32 w-48 rounded-full bg-agent-purple/20 blur-3xl"></div>
    </div>

    <div class="relative flex items-center justify-between px-5 py-4 sm:px-6 sm:py-5">
      <div class="flex flex-col items-start text-left min-w-0">
        <div class="flex items-center gap-2 mb-1">
          <p class="agent-eyebrow">Auction</p>
          {#if isAuctionActive}
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wide border border-emerald-500/30 bg-emerald-500/5 text-emerald-400">
              LIVE
            </span>
          {/if}
        </div>
        <h2 class="text-base sm:text-lg font-semibold text-white tracking-tight">Reverse Auction</h2>
        {#if timeUntilNextDrop}
          <p class="text-sm font-normal text-gray-400 mt-0.5">Next price drop: {timeUntilNextDrop}</p>
        {:else}
          <p class="text-sm font-normal text-gray-400 hidden sm:block mt-0.5">Price drops over time</p>
        {/if}
      </div>
      
      <div class="shrink-0 ml-4">
        <div class="w-9 h-9 rounded-xl border border-white/10 bg-white/4 flex items-center justify-center transition-transform duration-300" style="transform: rotate({isOpen ? 180 : 0}deg)">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>
  
  <!-- Accordion Content -->
  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="border-t border-white/6 bg-agent-surface">
      {#if isAuthenticated}
        <!-- Authenticated Content -->
        <div class="p-6 sm:p-8 space-y-6">
          
          <!-- Auction Status Banner -->
          {#if isAuctionActive}
            <div class="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 sm:p-5">
              <div class="flex items-center justify-between gap-4">
                <div class="flex items-center space-x-3">
                  <div class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                  <span class="text-emerald-300 font-medium text-sm sm:text-base">Auction is Active</span>
                </div>
                {#if timeUntilNextDrop}
                  <div class="rounded-lg px-3 py-1.5 border border-white/10 bg-white/3">
                    <div class="text-[10px] uppercase tracking-wide text-gray-500 font-medium mb-0.5">Next price drop</div>
                    <div class="text-white font-semibold text-sm">{timeUntilNextDrop}</div>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
          
          <!-- Auction Info Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Current Price Card -->
            <div class="rounded-xl border border-white/10 bg-white/3 p-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-xs text-gray-500 font-medium mb-0.5">Current Price</div>
                  <div class="text-xl font-semibold text-white">{mainerPrice} ICP</div>
                  <div class="text-xs text-gray-500 font-medium">90% converted to Cycles</div>
                </div>
              </div>
            </div>
            
            <!-- Available mAIners Card -->
            <div class="rounded-xl border border-white/10 bg-white/3 p-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
                  <svg class="w-5 h-5 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-xs text-gray-500 font-medium mb-0.5">Available mAIners</div>
                  <div class="text-xl font-semibold text-white">
                    {#if availableMainers > 0}
                      {availableMainers}
                    {:else}
                      <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium border border-red-500/30 bg-red-500/5 text-red-400">
                        Not Available
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- mAIner Agent Card -->
          <div class="space-y-4">
            <div class="relative overflow-hidden rounded-xl border border-agent-purple/40 bg-white/3">
              <div class="relative p-5 sm:p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4 flex-1 min-w-0">
                    <!-- Icon -->
                    <div class="shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
                      <svg class="w-6 h-6 sm:w-7 sm:h-7 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                        <h4 class="text-base sm:text-lg font-semibold text-white">mAIner Agent</h4>
                        {#if availableMainers > 0}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium border border-emerald-500/30 bg-emerald-500/5 text-emerald-400 w-fit">
                            {availableMainers} Available
                          </span>
                        {:else}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium border border-red-500/30 bg-red-500/5 text-red-400 w-fit">
                            Creation not available
                          </span>
                        {/if}
                      </div>
                      
                      <p class="text-sm text-gray-400 mb-4 leading-relaxed">
                        Shared infrastructure with optimized performance and instant deployment
                      </p>
                      
                      <!-- Features -->
                      <div class="flex flex-wrap gap-3 text-xs">
                        {#if availableMainers > 0}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-white/10 bg-white/3">
                            <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                            </svg>
                            <span class="font-medium text-gray-300">{mainerPrice} ICP</span>
                          </div>
                        {:else}
                          <a href="#/marketplace" class="agent-btn-ghost no-underline">
                            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
                            </svg>
                            <span>Available on the marketplace</span>
                          </a>
                        {/if}
                        
                        <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-white/10 bg-white/3">
                          <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          <span class="font-medium text-gray-300">Instant deploy</span>
                        </div>
                        
                        {#if isAuctionActive}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/5">
                            <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <span class="font-medium text-emerald-400">Price dropping</span>
                          </div>
                        {/if}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Step 2 Indicator (if model selected) -->
          {#if selectedModel}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-lg border border-emerald-500/30 bg-emerald-500/5 text-emerald-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-300">Model Selected</span>
            </div>
          {/if}
          
          <!-- Step 3 Indicator (if payment copied) -->
          {#if addressCopied}
            <div class="flex items-center space-x-3 py-2">
              <div class="flex items-center justify-center w-8 h-8 rounded-lg border border-emerald-500/30 bg-emerald-500/5 text-emerald-400">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-300">Payment Ready</span>
            </div>
          {/if}
          
          <!-- Create Button -->
          <div class="pt-4 border-t border-white/6">
            <button 
              on:click={onCreateAgent} 
              disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation || availableMainers === 0}
              class="agent-btn-primary w-full h-12 text-base disabled:opacity-50 disabled:cursor-not-allowed"
              use:tooltip={{ 
                text: isCreatingMainer 
                  ? "⚠️ mAIner creation in progress! Please wait for it to complete. DO NOT refresh or navigate away - this will stop the creation and you'll need to start over."
                  : availableMainers === 0
                    ? "No mAIners available at the moment. Please check back soon!"
                    : stopMainerCreation 
                      ? "mAIner creation is temporarily disabled due to network capacity"
                      : !isProtocolActive 
                        ? "Protocol is currently inactive"
                        : "",
                direction: 'top',
                textSize: 'xs'
              }}
            >
              <span class="relative flex items-center justify-center space-x-2">
                {#if isCreatingMainer}
                  <svg class="animate-spin w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                  <span>Create mAIner Agent</span>
                {/if}
              </span>
            </button>
          </div>
        </div>
        
      {:else}
        <!-- Not Authenticated - Login Prompt -->
        <div class="p-6 sm:p-8">
          <div class="rounded-xl border border-white/10 bg-white/3 p-8 sm:p-10">
            <div class="flex flex-col items-center text-center space-y-6 max-w-xl mx-auto">
              <!-- Icon -->
              <div class="w-16 h-16 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
                <svg class="w-8 h-8 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
              
              <!-- Content -->
              <div class="space-y-4">
                <div class="space-y-2">
                  <p class="agent-eyebrow">Reverse Auction</p>
                  <h3 class="text-xl sm:text-2xl font-semibold text-white">Connect Your Wallet</h3>
                </div>
                
                <p class="text-gray-400 text-sm leading-relaxed">
                  Join the reverse auction. Connect your wallet to participate and get mAIners at decreasing prices.
                </p>
                
                <!-- Features Grid -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                  <div class="rounded-xl p-4 border border-white/10 bg-white/3">
                    <svg class="w-5 h-5 text-agent-purple mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <p class="text-xs font-medium text-gray-300">Price Drops</p>
                  </div>
                  
                  <div class="rounded-xl p-4 border border-white/10 bg-white/3">
                    <svg class="w-5 h-5 text-agent-purple mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                    <p class="text-xs font-medium text-gray-300">Instant Deploy</p>
                  </div>
                  
                  <div class="rounded-xl p-4 border border-white/10 bg-white/3">
                    <svg class="w-5 h-5 text-agent-purple mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                    </svg>
                    <p class="text-xs font-medium text-gray-300">Best Price</p>
                  </div>
                </div>
              </div>
              
              <!-- CTA Button -->
              <button 
                on:click={onToggleLoginModal} 
                class="agent-btn-primary h-11 px-8"
              >
                <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                </svg>
                Connect Wallet
              </button>
              
              <!-- Security Note -->
              <div class="flex items-center justify-center space-x-2 text-xs text-gray-500 border border-white/10 bg-white/3 rounded-xl px-4 py-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span class="font-medium">Secured by Internet Identity & NFID</span>
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
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
    opacity: 0;
  }
  
  .accordion-content.accordion-open {
    max-height: 2500px;
    opacity: 1;
    overflow: visible;
  }
</style>
