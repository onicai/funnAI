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
      <div class="relative overflow-hidden bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 dark:from-amber-600 dark:via-yellow-600 dark:to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform">
        <!-- Background decoration -->
        <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
            <!-- Left side content -->
            <div class="flex-1">
              <div class="flex items-center space-x-3 mb-3">
                <div class="flex-shrink-0 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-sm">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                  </svg>
                </div>
                <div>
                <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                      Limited Time
                    </div>
                  <h3 class="text-lg sm:text-xl font-bold text-white drop-shadow-sm">Whitelist phase active</h3>
                  <div class="flex items-center space-x-2 mt-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                      Special pricing
                    </span>
                    {#if unlockedMainers.length > 0}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-white backdrop-blur-sm">
                        {unlockedMainers.length} Available
                      </span>
                    {/if}
                  </div>
                </div>
              </div>
              
              <div class="text-white/90 text-sm leading-relaxed">
                <p class="font-medium mb-2">🎉 Exclusive whitelist pricing now available!</p>
                <p>Create your mAIner from the unlocked options below for just <span class="font-bold text-white">{currentWhitelistPrice || 5} ICP</span> instead of the regular price of <span class="line-through opacity-75">{currentMainerPrice || 10} ICP</span>.</p>
                {#if unlockedMainers.length > 0}
                  <p class="text-xs text-white/80 mt-2">💡 <span class="font-medium">Note:</span> This is a limited whitelist expansion sale. Thank you for qualifying and happy mAIning!</p>
                {/if}
              </div>
            </div>
            
            <!-- Right side - Savings highlight -->
            <div class="flex-shrink-0 sm:ml-6">
              <div class="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center border border-white/20 shadow-lg">
                <div class="text-2xl sm:text-3xl font-bold text-white mb-1">
                  {Math.round(((currentMainerPrice || 10) - (currentWhitelistPrice || 5)) / (currentMainerPrice || 10) * 100)}%
                </div>
                <div class="text-xs sm:text-sm text-white/80 font-medium uppercase tracking-wide">
                  Savings
                </div>
                <div class="text-xs text-white/70 mt-1">
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
        <div class="relative overflow-hidden bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 dark:from-amber-900/20 dark:via-yellow-900/20 dark:to-orange-900/20 border border-amber-200/60 dark:border-amber-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-0.5">
          <!-- Background decorative elements -->
          <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-yellow-200/30 to-amber-200/30 dark:from-yellow-600/10 dark:to-amber-600/10 rounded-full -translate-y-8 translate-x-8"></div>
          <div class="absolute bottom-0 left-0 w-12 h-12 bg-gradient-to-tr from-orange-200/30 to-yellow-200/30 dark:from-orange-600/10 dark:to-yellow-600/10 rounded-full translate-y-6 -translate-x-6"></div>
          
          <div class="relative p-3 md:p-4">
            <div class="flex flex-col space-y-3 xl:flex-row xl:items-center xl:justify-between xl:space-y-0">
              <!-- Left side - mAIner info -->
              <div class="flex items-start space-x-3 min-w-0 flex-1">
                <!-- Premium icon with glow effect -->
                <div class="flex-shrink-0 w-8 h-8 md:w-10 md:h-10 bg-gradient-to-br from-yellow-400 to-amber-500 dark:from-yellow-500 dark:to-amber-600 rounded-lg shadow-lg flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
                
                <!-- mAIner details -->
                <div class="flex-1 min-w-0">
                  <div class="flex flex-col space-y-2">
                    <h3 class="font-semibold text-sm md:text-base text-amber-900 dark:text-amber-100 truncate">
                      {unlockedMainer.name}
                    </h3>
                    <div class="flex flex-wrap items-center gap-2">
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                        </svg>
                        Unlocked
                      </span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-300 border border-green-300 dark:border-green-700">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        Whitelisted
                      </span>
                    </div>
                  </div>
                  
                  <!-- Type and special pricing info -->
                  <div class="flex flex-col space-y-1 mt-2 lg:flex-row lg:items-center lg:space-x-4 lg:space-y-0">
                    <div class="flex items-center space-x-1 text-xs text-amber-700 dark:text-amber-300">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                      </svg>
                      <span class="font-medium">Quick start</span>
                    </div>
                    <div class="flex items-center space-x-1 text-xs text-emerald-700 dark:text-emerald-300">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"/>
                      </svg>
                      <span class="font-medium">Only {currentWhitelistPrice || 5} ICP</span>
                      <span class="line-through text-xs opacity-60">{currentMainerPrice || 10} ICP</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Right side - Action button -->
              <div class="flex-shrink-0 xl:ml-4">
                <button
                  on:click={() => onCreateWhitelistAgent(unlockedMainer)}
                  disabled={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class="group relative inline-flex items-center justify-center px-4 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-amber-500 to-yellow-500 dark:from-amber-600 dark:to-yellow-600 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 border border-amber-400/50 dark:border-amber-500/50 w-full xl:w-auto"
                  class:opacity-50={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:cursor-not-allowed={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:transform-none={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                  class:hover:scale-100={isPauseWhitelistMainerCreation || stopMainerCreation || !isProtocolActive || whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                >
                  {#if whitelistMainersBeingCreated.has(unlockedMainer.id || unlockedMainer.name || `unlocked-${unlockedMainer.originalCanisterInfo?.address || index}`)}
                    <div class="flex items-center space-x-2">
                      <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      <span class="text-xs md:text-sm">Processing...</span>
                    </div>
                  {:else}
                    <div class="flex items-center space-x-2">
                      <svg class="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                      <span class="text-xs md:text-sm">Create Now</span>
                    </div>
                  {/if}
                  <div class="absolute inset-0 rounded-lg bg-gradient-to-r from-yellow-100 to-amber-100 dark:from-yellow-600/20 dark:to-amber-600/20 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
                </button>
              </div>
            </div>
            
            <!-- Bottom accent line -->
            <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-amber-400 dark:via-amber-500 to-transparent"></div>
          </div>
        </div>
      {/each}
    </div>
  <!-- Case 2: User has already created mAIners (whitelist participant) -->
  {:else if totalMainers > 0}
    <div class="mb-4">
      <div class="relative overflow-hidden bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 dark:from-emerald-600 dark:via-teal-600 dark:to-cyan-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform">
        <!-- Background decoration -->
        <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
        <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-4 sm:p-6">
          <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
            <!-- Icon with enhanced styling -->
            <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
              <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            
            <!-- Content section -->
            <div class="space-y-3 sm:space-y-4">
              <div class="flex flex-col items-center text-center space-y-2">
                <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                  funnAI Member
                </div>
                <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Welcome, early supporter! 🎉</h3>
              </div>
              
              <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
                <p class="font-semibold text-base sm:text-lg">✨ You're part of the genesis community!</p>
                <p>You have successfully created your mAIner(s). Manage your existing mAIners below or check for additional whitelist opportunities.</p>
              </div>
              
              <!-- Status indicator -->
              <div class="pt-3">
                <div class="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-xl border border-white/30 shadow-sm">
                  <svg class="w-5 h-5 mr-2 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <span class="text-white font-semibold">mAIners Activated</span>
                </div>
              </div>
              
              <!-- Additional info -->
              <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
                <div class="flex items-center justify-center space-x-2">
                  <span class="text-sm">🏆</span>
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
      <div class="relative overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-800 dark:via-blue-900/20 dark:to-indigo-900/20 border border-slate-200/60 dark:border-slate-700/60 rounded-xl shadow-sm">
        <!-- Background decorative elements -->
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-200/20 to-indigo-200/20 dark:from-blue-600/10 dark:to-indigo-600/10 rounded-full -translate-y-16 translate-x-16"></div>
        <div class="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-purple-200/20 to-pink-200/20 dark:from-purple-600/10 dark:to-pink-600/10 rounded-full translate-y-12 -translate-x-12"></div>
        
        <div class="relative p-6 sm:p-8 text-center">
          <!-- Enhanced icon with background -->
          <div class="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-800/30 dark:to-indigo-800/30 rounded-2xl shadow-sm border border-blue-200/50 dark:border-blue-700/50 mx-auto mb-4">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </div>
          
          <!-- Main heading --> 
          <h3 class="text-xl sm:text-2xl font-bold text-slate-800 dark:text-slate-100 mb-3">
            Whitelist phase active! 🎉
          </h3>
          
          <!-- Description -->
          <div class="space-y-3 mb-6">
            <p class="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed max-w-md mx-auto">
              The whitelist expansion sale is here.
            </p>
            
            <!-- Public sale announcement -->
            <div class="bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 border border-emerald-200/60 dark:border-emerald-700/60 rounded-lg p-4 max-w-sm mx-auto">
              <div class="flex items-center justify-center space-x-2 mb-2">
                <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="text-sm font-semibold text-emerald-800 dark:text-emerald-200">Whitelist Sale Opens</span>
              </div>
              <div class="text-2xl sm:text-3xl font-bold text-emerald-700 dark:text-emerald-300 mb-1">
                September 01
              </div>
              <p class="text-xs text-emerald-600 dark:text-emerald-400">
                Mark your calendar!
              </p>
            </div>
          </div>
          
          <!-- Call to action -->
          <div class="space-y-3">
            <p class="text-sm text-slate-500 dark:text-slate-400">
              🚀 <span class="font-medium">Coming soon:</span> More public sales to create your own mAIner and start AI mining!
            </p>
            
            <!-- Notification signup hint -->
            <div class="inline-flex items-center space-x-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-full border border-blue-200 dark:border-blue-700">
              <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
              </svg>
              <span class="text-xs font-medium text-blue-700 dark:text-blue-300">Stay tuned for updates</span>
            </div>
          </div>
          
          <!-- Debug info - only show in development -->
          {#if import.meta.env.DEV}
            <details class="mt-4 text-left">
              <div class="mt-2 p-2 bg-slate-100 dark:bg-slate-800 rounded text-xs text-slate-500 dark:text-slate-400">
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
    <div class="relative overflow-hidden bg-gradient-to-r from-amber-500 via-yellow-500 to-orange-500 dark:from-amber-600 dark:via-yellow-600 dark:to-orange-600 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform h-full">
      <!-- Background decoration -->
      <div class="absolute inset-0 bg-gradient-to-br from-transparent via-white/10 to-transparent"></div>
      <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
      <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
      
      <div class="relative h-full flex items-center justify-center p-4 sm:p-6">
        <div class="flex flex-col items-center text-center space-y-4 sm:space-y-5 max-w-lg mx-auto">
          <!-- Icon with enhanced styling -->
          <div class="flex-shrink-0 w-16 h-16 sm:w-20 sm:h-20 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-sm">
            <svg class="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
          </div>
          
          <!-- Content section -->
          <div class="space-y-3 sm:space-y-4">
            <div class="flex flex-col items-center text-center space-y-2">
              <div class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white/20 text-white backdrop-blur-sm">
                Limited expansion sale
              </div>
              <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-white drop-shadow-sm">Whitelist phase active</h3>
            </div>
            
            <div class="text-white/90 text-sm sm:text-base leading-relaxed max-w-md mx-auto space-y-2">
              <p class="font-semibold text-base sm:text-lg">🎉 Exclusive access for whitelist members!</p>
              <p>Connect your wallet to see available whitelist mAIners and take advantage of special pricing.</p>
            </div>
            
            <!-- Enhanced button -->
            <div class="pt-3">
              <button 
                on:click={onToggleLoginModal} 
                class="group relative inline-flex items-center justify-center px-6 py-3 text-base font-bold text-amber-600 bg-white rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 hover:scale-102 border-2 border-white/20 backdrop-blur-sm"
              >
                <svg class="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
                </svg>
                Connect Wallet
                <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-100 to-yellow-100 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              </button>
            </div>
            
            <!-- Additional info -->
            <div class="text-xs text-white/80 bg-white/15 backdrop-blur-sm rounded-xl px-3 py-2 border border-white/20 shadow-sm">
              <div class="flex items-center justify-center space-x-2">
                <span class="text-sm">💡</span>
                <span class="font-medium">Get access to mAIners with exclusive whitelist pricing</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

