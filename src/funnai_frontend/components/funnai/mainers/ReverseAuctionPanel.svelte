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

<!-- Modern Elegant Header -->
<div class="relative overflow-hidden rounded-2xl">
  <!-- Header Button with gradient and glass effect -->
  <button 
    on:click={toggleAccordion} 
    class="group w-full relative overflow-hidden bg-gradient-to-br from-purple-600 via-pink-600 to-rose-600 dark:from-purple-700 dark:via-pink-700 dark:to-rose-700 hover:from-purple-700 hover:via-pink-700 hover:to-rose-700 dark:hover:from-purple-800 dark:hover:via-pink-800 dark:hover:to-rose-800 transition-all duration-500 shadow-xl hover:shadow-2xl {isOpen ? 'rounded-t-2xl' : 'rounded-2xl'}"
  >
    <!-- Animated background overlay -->
    <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
    
    <!-- Decorative elements -->
    <div class="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-20 translate-x-20 blur-2xl"></div>
    <div class="absolute bottom-0 left-0 w-32 h-32 bg-rose-400/10 rounded-full translate-y-16 -translate-x-16 blur-xl"></div>
    
    <!-- Content -->
    <div class="relative flex items-center justify-between px-6 py-5 sm:px-8 sm:py-6">
      <div class="flex items-center space-x-4 min-w-0 flex-1">
        <!-- Icon with glow -->
        <div class="relative flex-shrink-0">
          <div class="absolute inset-0 bg-white/20 rounded-xl blur-md"></div>
          <div class="relative w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20 shadow-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 sm:w-7 sm:h-7 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
        </div>
        
        <!-- Text content -->
        <div class="flex flex-col items-start text-left min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <h2 class="text-lg sm:text-xl font-bold text-white tracking-tight">Reverse Auction</h2>
            {#if isAuctionActive}
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-green-500/30 text-white border border-green-400/50 animate-pulse">
                LIVE
              </span>
            {/if}
          </div>
          {#if timeUntilNextDrop}
            <p class="text-sm text-white/90 font-semibold">⏱️ Next drop: {timeUntilNextDrop}</p>
          {:else}
            <p class="text-sm text-white/80 font-medium hidden sm:block">Price drops over time</p>
          {/if}
        </div>
      </div>
      
      <!-- Chevron indicator -->
      <div class="flex-shrink-0 ml-4">
        <div class="w-10 h-10 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20 transition-transform duration-300" style="transform: rotate({isOpen ? 180 : 0}deg)">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-white" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </button>
  
  <!-- Accordion Content -->
  <div class="accordion-content" class:accordion-open={isOpen}>
    <div class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 border-x border-b border-gray-200 dark:border-gray-700 rounded-b-2xl">
      {#if isAuthenticated}
        <!-- Authenticated Content -->
        <div class="p-6 sm:p-8 space-y-6">
          
          <!-- Auction Status Banner -->
          {#if isAuctionActive}
            <div class="relative overflow-hidden bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 dark:from-green-600 dark:via-emerald-600 dark:to-teal-600 rounded-xl shadow-lg">
              <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
              <div class="relative p-4 sm:p-5">
                <div class="flex items-center justify-between gap-4">
                  <div class="flex items-center space-x-3">
                    <div class="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                    <span class="text-white font-bold text-base sm:text-lg">Auction is Active!</span>
                  </div>
                  {#if timeUntilNextDrop}
                    <div class="bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1.5 border border-white/30">
                      <div class="text-xs text-white/80 font-medium mb-0.5">Next price drop in</div>
                      <div class="text-white font-bold text-sm sm:text-base">{timeUntilNextDrop}</div>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          {/if}
          
          <!-- Auction Info Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- Current Price Card -->
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 p-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-xs text-gray-600 dark:text-gray-400 font-medium mb-0.5">Current Price</div>
                  <div class="text-xl font-bold text-gray-900 dark:text-white">{mainerPrice} ICP</div>
                </div>
              </div>
            </div>
            
            <!-- Available mAIners Card -->
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 p-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-gradient-to-br from-rose-500 to-orange-600 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                  </svg>
                </div>
                <div class="flex-1">
                  <div class="text-xs text-gray-600 dark:text-gray-400 font-medium mb-0.5">Available mAIners</div>
                  <div class="text-xl font-bold text-gray-900 dark:text-white">
                    {#if availableMainers > 0}
                      {availableMainers}
                    {:else}
                      <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border border-red-200 dark:border-red-800">
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
            <div 
              class="group relative overflow-hidden border-2 rounded-2xl transition-all duration-300 border-purple-500 dark:border-purple-400 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 shadow-lg shadow-purple-500/20"
            >
              <!-- Decorative background elements -->
              <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-200/20 to-pink-200/20 dark:from-purple-500/10 dark:to-pink-500/10 rounded-full -translate-y-16 translate-x-16 blur-2xl"></div>
              
              <div class="relative p-5 sm:p-6">
                <div class="flex items-start justify-between">
                  <div class="flex items-start space-x-4 flex-1 min-w-0">
                    <!-- Icon -->
                    <div class="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-xl bg-gradient-to-br from-purple-500 via-pink-500 to-rose-600 flex items-center justify-center shadow-lg">
                      <svg class="w-6 h-6 sm:w-7 sm:h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                    </div>
                    
                    <!-- Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                        <h4 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white">mAIner Agent</h4>
                        {#if availableMainers > 0}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 w-fit border border-green-200 dark:border-green-800">
                            {availableMainers} Available
                          </span>
                        {:else}
                          <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 w-fit border border-red-200 dark:border-red-800">
                            Not Available
                          </span>
                        {/if}
                      </div>
                      
                      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 leading-relaxed">
                        Shared infrastructure with optimized performance and instant deployment
                      </p>
                      
                      <!-- Features -->
                      <div class="flex flex-wrap gap-3 text-xs">
                        <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg border border-gray-200/60 dark:border-gray-600/60">
                          <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                          </svg>
                          <span class="font-semibold text-gray-700 dark:text-gray-300">{mainerPrice} ICP</span>
                        </div>
                        
                        <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-white/60 dark:bg-gray-700/60 backdrop-blur-sm rounded-lg border border-gray-200/60 dark:border-gray-600/60">
                          <svg class="w-4 h-4 text-pink-600 dark:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          <span class="font-semibold text-gray-700 dark:text-gray-300">Instant deploy</span>
                        </div>
                        
                        {#if isAuctionActive}
                          <div class="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-green-500/10 to-emerald-500/10 backdrop-blur-sm rounded-lg border border-green-500/30">
                            <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <span class="font-semibold text-green-700 dark:text-green-300">Price dropping</span>
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
              disabled={isCreatingMainer || !isProtocolActive || stopMainerCreation || availableMainers === 0}
              class="group relative w-full overflow-hidden bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 dark:disabled:from-gray-600 dark:disabled:to-gray-700 text-white font-bold px-6 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60"
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
        </div>
        
      {:else}
        <!-- Not Authenticated - Login Prompt -->
        <div class="p-6 sm:p-8">
          <div class="relative overflow-hidden bg-gradient-to-br from-purple-500 via-pink-500 to-rose-600 dark:from-purple-600 dark:via-pink-600 dark:to-rose-700 rounded-2xl shadow-xl">
            <!-- Background decoration -->
            <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent"></div>
            <div class="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-32 translate-x-32 blur-3xl"></div>
            <div class="absolute bottom-0 left-0 w-48 h-48 bg-rose-400/10 rounded-full translate-y-24 -translate-x-24 blur-2xl"></div>
            
            <div class="relative p-8 sm:p-10">
              <div class="flex flex-col items-center text-center space-y-6 max-w-xl mx-auto">
                <!-- Icon -->
                <div class="relative">
                  <div class="absolute inset-0 bg-white/20 rounded-2xl blur-xl"></div>
                  <div class="relative w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20 shadow-2xl">
                    <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                  </div>
                </div>
                
                <!-- Content -->
                <div class="space-y-4">
                  <div class="space-y-2">
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-sm border border-white/30">
                      REVERSE AUCTION
                    </span>
                    <h3 class="text-2xl sm:text-3xl font-bold text-white">Connect Your Wallet</h3>
                  </div>
                  
                  <p class="text-white/90 text-base leading-relaxed">
                    🎯 Join the reverse auction! Connect your wallet to participate and get mAIners at decreasing prices.
                  </p>
                  
                  <!-- Features Grid -->
                  <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <svg class="w-6 h-6 text-white mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      <p class="text-xs font-semibold text-white">Price Drops</p>
                    </div>
                    
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <svg class="w-6 h-6 text-white mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                      <p class="text-xs font-semibold text-white">Instant Deploy</p>
                    </div>
                    
                    <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                      <svg class="w-6 h-6 text-white mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                      </svg>
                      <p class="text-xs font-semibold text-white">Best Price</p>
                    </div>
                  </div>
                </div>
                
                <!-- CTA Button -->
                <button 
                  on:click={onToggleLoginModal} 
                  class="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-purple-700 bg-white rounded-2xl shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-105"
                >
                  <svg class="w-6 h-6 mr-2 group-hover:rotate-12 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                  </svg>
                  Connect Wallet
                </button>
                
                <!-- Security Note -->
                <div class="flex items-center justify-center space-x-2 text-xs text-white/80 bg-white/10 backdrop-blur-sm rounded-xl px-4 py-2 border border-white/20">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                  <span class="font-medium">Secured by Internet Identity & NFID</span>
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
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
    opacity: 0;
  }
  
  .accordion-content.accordion-open {
    max-height: 2500px;
    opacity: 1;
    overflow: visible;
  }
</style>

