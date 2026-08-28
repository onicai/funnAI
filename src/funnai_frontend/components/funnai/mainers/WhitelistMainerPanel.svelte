<script lang="ts">
  // Props
  export let isWhitelistPhaseActive: boolean;
  export let isAuthenticated: boolean;
  export let unlockedMainers: any[];
  export let totalMainers: number;
  export let agentCanistersInfo: any[];
  export let currentWhitelistPrice: number;
  export let currentMainerPrice: number;
  export let isPauseWhitelistMainerCreation: boolean;
  export let stopMainerCreation: boolean;
  export let isProtocolActive: boolean;
  export let whitelistMainersBeingCreated: Set<string>;
  
  // Callbacks
  export let onCreateWhitelistAgent: (unlockedMainer: any) => void;
  export let onToggleLoginModal: () => void;
</script>

{#if isWhitelistPhaseActive && isAuthenticated}
  <!-- Case 1: User has unlocked mAIners ready to create -->
  {#if unlockedMainers.length > 0}
    <div class="mb-4">
      <div class="agent-card border-amber-500/30 bg-amber-500/5">
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <!-- Left side content -->
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-3">
                <div class="shrink-0 w-10 h-10 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center justify-center">
                  <svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <div>
                  <p class="agent-eyebrow mb-1">Limited Time</p>
                  <h3 class="text-lg sm:text-xl font-semibold text-white">Whitelist phase active</h3>
                  <div class="flex items-center space-x-2 mt-1.5">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border border-amber-500/30 bg-amber-500/5 text-amber-300">
                      Special pricing
                    </span>
                    {#if unlockedMainers.length > 0}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border border-emerald-500/30 bg-emerald-500/5 text-emerald-400">
                        {unlockedMainers.length} Available
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
              
              <div class="text-gray-400 text-sm leading-relaxed">
                <p class="font-medium text-gray-300 mb-2">Exclusive whitelist pricing now available</p>
                <p>Create your mAIner from the unlocked options below for just <span class="font-semibold text-white">{currentWhitelistPrice || 5} ICP</span> instead of the regular price of <span class="line-through text-gray-500">{currentMainerPrice || 10} ICP</span>.</p>
                {#if unlockedMainers.length > 0}
                  <p class="text-xs text-gray-500 mt-2"><span class="font-medium text-gray-400">Note:</span> This is a limited whitelist expansion sale. Thank you for qualifying and happy mAIning!</p>
                {/if}
              </div>
            </div>
            
            <!-- Right side - Savings highlight -->
            <div class="shrink-0 sm:ml-6">
              <div class="rounded-xl p-4 text-center border border-white/10 bg-white/3">
                <div class="text-2xl sm:text-3xl font-semibold text-white mb-1">
                  {Math.round(((currentMainerPrice || 10) - (currentWhitelistPrice || 5)) / (currentMainerPrice || 10) * 100)}%
                </div>
                <div class="text-xs sm:text-sm text-gray-500 font-medium uppercase tracking-wide">
                  Savings
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  Save {((currentMainerPrice || 10) - (currentWhitelistPrice || 5)).toFixed(1)} ICP
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unlocked mAIners List -->
    <div class="space-y-3">
      {#each unlockedMainers as unlockedMainer, index}
        <div class="rounded-xl border border-white/10 bg-white/3 hover:border-amber-500/30 transition-colors duration-200">
          <div class="relative p-3 md:p-4">
            <div class="flex flex-col space-y-3 xl:flex-row xl:items-center xl:justify-between xl:space-y-0">
              <!-- Left side - mAIner info -->
              <div class="flex items-start space-x-3 min-w-0 flex-1">
                <!-- Icon -->
                <div class="shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 text-amber-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
                
                <!-- mAIner details -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-col space-y-2">
                    <h3 class="font-semibold text-sm md:text-base text-white truncate">
                      {unlockedMainer.name}
                    </h3>
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border border-amber-500/30 bg-amber-500/5 text-amber-300">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                        Unlocked
                      </span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border border-emerald-500/30 bg-emerald-500/5 text-emerald-400">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        Whitelisted
                      </span>
                    </div>
                  </div>
                  
                  <!-- Type and special pricing info -->
                  <div class="flex flex-col space-y-1 mt-2 lg:flex-row lg:items-center lg:space-x-4 lg:space-y-0">
                    <div class="flex items-center space-x-1 text-xs text-gray-400">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                      </svg>
                      <span class="font-medium">Quick start</span>
                    </div>
                    <div class="flex items-center space-x-1 text-xs text-emerald-400">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                      </svg>
                      <span class="font-medium">Only {currentWhitelistPrice || 5} ICP</span>
                      <span class="line-through text-xs text-gray-500">{currentMainerPrice || 10} ICP</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Right side - Action button -->
              <div class="shrink-0 xl:ml-4">
                <button
                  on:click={() => onCreateWhitelistAgent(unlockedMainer)}
                  disabled={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class="agent-btn-primary w-full xl:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
                  class:opacity-50={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:cursor-not-allowed={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                >
                  {#if whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                    <div class="flex items-center space-x-2">
                      <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      <span class="text-xs md:text-sm">Processing...</span>
                    </div>
                  {:else}
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                      <span class="text-xs md:text-sm">Create Now</span>
                    </div>
                  {/if}
                </button>
              </div>
            </div>
          </div>
        </div>
      {/each}
    </div>
  <!-- Case 2: User has already created mAIners (whitelist participant) -->
  {:else if totalMainers > 0}
    <div class="mb-4">
      <div class="agent-card border-emerald-500/30 bg-emerald-500/5">
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
            <!-- Icon -->
            <div class="shrink-0 w-14 h-14 sm:w-16 sm:h-16 rounded-xl border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center">
              <svg class="w-7 h-7 sm:w-8 sm:h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            
            <!-- Content section -->
            <div class="space-y-3 sm:space-y-4">
              <div class="flex flex-col items-center text-center space-y-2">
                <p class="agent-eyebrow">funnAI Member</p>
                <h3 class="text-lg sm:text-xl font-semibold text-white">Welcome, early supporter</h3>
              </div>
              
              <div class="text-gray-400 text-sm leading-relaxed max-w-md mx-auto space-y-2">
                <p class="font-medium text-gray-300">You're part of the genesis community</p>
                <p>You have successfully created your mAIner(s). Manage your existing mAIners below or check for additional whitelist opportunities.</p>
              </div>
              
              <!-- Status indicator -->
              <div class="pt-1">
                <div class="inline-flex items-center px-4 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
                  <svg class="w-4 h-4 mr-2 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span class="text-emerald-300 font-medium text-sm">mAIners Activated</span>
                </div>
              </div>
              
              <!-- Additional info -->
              <div class="text-xs text-gray-500 border border-white/10 bg-white/3 rounded-xl px-3 py-2">
                <div class="flex items-center justify-center">
                  <span class="font-medium">You're part of the exclusive genesis funnAI community with {totalMainers} mAIner{totalMainers === 1 ? '' : 's'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  <!-- Case 3: User has no whitelisted principals - awaiting public sale -->
  {:else}
    <div class="mb-4">
      <div class="agent-card">
        <div class="relative p-6 sm:p-8 text-center">
          <!-- Icon -->
          <div class="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 rounded-xl border border-white/10 bg-white/3 mx-auto mb-4">
            <svg class="w-7 h-7 sm:w-8 sm:h-8 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
          
          <!-- Main heading --> 
          <p class="agent-eyebrow mb-2">Whitelist</p>
          <h3 class="text-xl sm:text-2xl font-semibold text-white mb-3">
            Whitelist phase active
          </h3>
          
          <!-- Description -->
          <div class="space-y-3 mb-6">
            <p class="text-sm text-gray-400 leading-relaxed max-w-md mx-auto">
              The whitelist expansion sale is here.
            </p>
            
            <!-- Public sale announcement -->
            <div class="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 max-w-sm mx-auto">
              <div class="flex items-center justify-center space-x-2 mb-2">
                <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="text-sm font-medium text-emerald-300">Whitelist Sale Opens</span>
              </div>
              <div class="text-2xl sm:text-3xl font-semibold text-white mb-1">
                September 01
              </div>
              <p class="text-xs text-gray-500">
                Mark your calendar
              </p>
            </div>
          </div>
          
          <!-- Call to action -->
          <div class="space-y-3">
            <p class="text-sm text-gray-500">
              <span class="font-medium text-gray-400">Coming soon:</span> More public sales to create your own mAIner and start AI mining!
            </p>
            
            <!-- Notification signup hint -->
            <div class="inline-flex items-center space-x-2 px-3 py-2 rounded-full border border-white/10 bg-white/3">
              <svg class="w-4 h-4 text-agent-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
              </svg>
              <span class="text-xs font-medium text-gray-400">Stay tuned for updates</span>
            </div>
          </div>
          
          <!-- Debug info - only show in development -->
          {#if import.meta.env.DEV}
            <details class="mt-4 text-left">
              <div class="mt-2 p-2 rounded-xl border border-white/10 bg-white/3 text-xs text-gray-500">
                Total mAIners loaded: {agentCanistersInfo.length}<br>
                Unlocked for you: {unlockedMainers.length}<br>
                Total mAIners: {totalMainers}
              </div>
            </details>
          {/if}
        </div>
      </div>
    </div>
  {/if}
{:else if isWhitelistPhaseActive && !isAuthenticated}
  <div class="mb-4 h-full">
    <div class="agent-card border-amber-500/30 bg-amber-500/5 h-full">
      <div class="relative h-full flex items-center justify-center p-4 sm:p-6">
        <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
          <!-- Icon -->
          <div class="shrink-0 w-14 h-14 sm:w-16 sm:h-16 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center justify-center">
            <svg class="w-7 h-7 sm:w-8 sm:h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          
          <!-- Content section -->
          <div class="space-y-3 sm:space-y-4">
            <div class="flex flex-col items-center text-center space-y-2">
              <p class="agent-eyebrow">Limited expansion sale</p>
              <h3 class="text-lg sm:text-xl font-semibold text-white">Whitelist phase active</h3>
            </div>
            
            <div class="text-gray-400 text-sm leading-relaxed max-w-md mx-auto space-y-2">
              <p class="font-medium text-gray-300">Exclusive access for whitelist members</p>
              <p>Connect your wallet to see available whitelist mAIners and take advantage of special pricing.</p>
            </div>
            
            <!-- Enhanced button -->
            <div class="pt-3">
              <button 
                on:click={onToggleLoginModal} 
                class="agent-btn-primary h-11 px-6"
              >
                <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                </svg>
                Connect Wallet
              </button>
            </div>
            
            <!-- Additional info -->
            <div class="text-xs text-gray-500 border border-white/10 bg-white/3 rounded-xl px-3 py-2">
              <div class="flex items-center justify-center">
                <span class="font-medium">Get access to mAIners with exclusive whitelist pricing</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}
