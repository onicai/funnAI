<script lang="ts">
  // Props for mainer statistics
  export let totalMainers: number;
  export let activeMainers: number;
  export let inactiveMainers: number;
  export let lowBurnRateMainers: number;
  export let mediumBurnRateMainers: number;
  export let highBurnRateMainers: number;
</script>

<!-- Enhanced mAIner Summary Header -->
<div class="mt-2 mb-4 relative overflow-hidden bg-gradient-to-r from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-800/50 dark:via-blue-900/30 dark:to-indigo-900/30 border border-slate-200/60 dark:border-slate-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
  <!-- Background decorative elements matching app style -->
  <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-blue-200/20 to-indigo-200/20 dark:from-blue-600/10 dark:to-indigo-600/10 rounded-full -translate-y-12 translate-x-12"></div>
  <div class="absolute bottom-0 left-0 w-20 h-20 bg-gradient-to-tr from-purple-200/20 to-blue-200/20 dark:from-purple-600/10 dark:to-blue-600/10 rounded-full translate-y-10 -translate-x-10"></div>
  
  <div class="relative p-4 sm:p-5">
    <!-- Header Section -->
    <div class="flex flex-col space-y-3 xl:flex-row xl:items-center xl:justify-between xl:space-y-0 mb-4">
      <div class="flex items-center space-x-3">
        <!-- Enhanced icon with gradient background -->
        <div class="flex-shrink-0 w-10 h-10 xl:w-12 xl:h-12 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 xl:h-6 xl:w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        
        <!-- Title and subtitle -->
        <div class="flex flex-col">
          <h2 class="text-sm xl:text-base font-bold text-slate-900 dark:text-slate-100">Flock overview</h2>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            {totalMainers} mAIner{totalMainers === 1 ? '' : 's'} in your flock
          </p>
        </div>
      </div>
      
      <!-- Quick Stats Summary - Compact header badges -->
      <div class="flex flex-wrap items-center gap-1.5 xl:gap-2">
        {#if activeMainers > 0}
          <div class="flex items-center space-x-1.5 px-2 py-1 xl:px-2.5 xl:py-1.5 bg-green-100/60 dark:bg-green-900/30 rounded-md border border-green-200/50 dark:border-green-700/50">
            <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
            <span class="text-xs font-medium text-green-700 dark:text-green-300">{activeMainers} Mining</span>
          </div>
        {/if}
        {#if inactiveMainers > 0}
          <div class="flex items-center space-x-1.5 px-2 py-1 xl:px-2.5 xl:py-1.5 bg-orange-100/60 dark:bg-orange-900/30 rounded-md border border-orange-200/50 dark:border-orange-700/50">
            <div class="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
            <span class="text-xs font-medium text-orange-700 dark:text-orange-300">{inactiveMainers} Need attention</span>
          </div>
        {/if}
      </div>
    </div>

    <!-- Status Cards Grid - Responsive 3-column layout -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
      <!-- Active mAIners Card -->
      <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-green-200/40 dark:border-green-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
        <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-green-200/20 dark:bg-green-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
        <div class="relative">
          <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
            <!-- Number first on large screens -->
            <span class="text-base sm:text-lg font-bold text-green-600 dark:text-green-400 lg:order-1 lg:text-xl lg:mb-1">{activeMainers}</span>
            
            <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
              <div class="w-5 h-5 sm:w-6 sm:h-6 bg-green-100 dark:bg-green-900/40 rounded-md flex items-center justify-center">
                <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-green-500 rounded-full animate-pulse"></div>
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-medium text-green-700 dark:text-green-300">Active</span>
                <span class="text-xs text-green-600/70 dark:text-green-400/70 hidden sm:block">Mining</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Inactive mAIners Card -->
      <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-gray-200/40 dark:border-gray-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
        <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-gray-200/20 dark:bg-gray-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
        <div class="relative">
          <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
            <!-- Number first on large screens -->
            <span class="text-base sm:text-lg font-bold text-gray-600 dark:text-gray-400 lg:order-1 lg:text-xl lg:mb-1">{inactiveMainers}</span>
            
            <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
              <div class="w-5 h-5 sm:w-6 sm:h-6 bg-gray-100 dark:bg-gray-600/60 rounded-md flex items-center justify-center">
                <div class="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-gray-400 rounded-full"></div>
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-medium text-gray-700 dark:text-gray-300">Inactive</span>
                <span class="text-xs text-gray-600/70 dark:text-gray-400/70 hidden sm:block">Need cycles</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Required Card (only show if there are inactive mAIners) -->
      {#if inactiveMainers > 0}
        <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-orange-200/40 dark:border-orange-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
          <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-orange-200/20 dark:bg-orange-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
          <div class="relative">
            <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
              <!-- Symbol first on large screens -->
              <span class="text-base sm:text-lg font-bold text-orange-600 dark:text-orange-400 lg:order-1 lg:text-xl lg:mb-1">!</span>
              
              <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
                <div class="w-5 h-5 sm:w-6 sm:h-6 bg-orange-100 dark:bg-orange-900/40 rounded-md flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 text-orange-600 dark:text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                  </svg>
                </div>
                <div class="flex flex-col">
                  <span class="text-xs font-medium text-orange-700 dark:text-orange-300">Attention</span>
                  <span class="text-xs text-orange-600/70 dark:text-orange-400/70 hidden sm:block">
                    {inactiveMainers} need{inactiveMainers === 1 ? 's' : ''} top-up
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      {:else}
        <!-- All Good Card when no inactive mAIners -->
        <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-emerald-200/40 dark:border-emerald-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
          <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-emerald-200/20 dark:bg-emerald-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
          <div class="relative">
            <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
              <!-- Symbol first on large screens -->
              <span class="text-base sm:text-lg font-bold text-emerald-600 dark:text-emerald-400 lg:order-1 lg:text-xl lg:mb-1">✓</span>
              
              <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
                <div class="w-5 h-5 sm:w-6 sm:h-6 bg-emerald-100 dark:bg-emerald-900/40 rounded-md flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 text-emerald-600 dark:text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                  </svg>
                </div>
                <div class="flex flex-col">
                  <span class="text-xs font-medium text-emerald-700 dark:text-emerald-300">All systems</span>
                  <span class="text-xs text-emerald-600/70 dark:text-emerald-400/70 hidden sm:block">Operational</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      {/if}

      <!-- Burn Rate Distribution Header -->
      <div class="mt-3 mb-1 flex items-center space-x-2 lg:col-span-3 md:col-span-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3 sm:w-4 sm:h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 hidden sm:inline">Cycle burn rate distribution</span>
        <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 sm:hidden">Burn rates</span>
      </div>

      <!-- Low Burn Rate Card -->
      <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-green-200/40 dark:border-green-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
        <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-green-200/20 dark:bg-green-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
        <div class="relative">
          <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
            <!-- Number first on large screens -->
            <span class="text-base sm:text-lg font-bold text-green-600 dark:text-green-400 lg:order-1 lg:text-xl lg:mb-1">{lowBurnRateMainers}</span>
            
            <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
              <div class="w-5 h-5 sm:w-6 sm:h-6 bg-green-100 dark:bg-green-900/40 rounded-md flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-medium text-green-700 dark:text-green-300 sm:hidden">Low</span>
                <span class="text-xs font-medium text-green-700 dark:text-green-300 hidden sm:inline">Low burn</span>
                <span class="text-xs text-green-600/70 dark:text-green-400/70 hidden sm:block">Conservative</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Medium Burn Rate Card -->
      <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-yellow-200/40 dark:border-yellow-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
        <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-yellow-200/20 dark:bg-yellow-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
        <div class="relative">
          <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
            <!-- Number first on large screens -->
            <span class="text-base sm:text-lg font-bold text-yellow-600 dark:text-yellow-400 lg:order-1 lg:text-xl lg:mb-1">{mediumBurnRateMainers}</span>
            
            <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
              <div class="w-5 h-5 sm:w-6 sm:h-6 bg-yellow-100 dark:bg-yellow-900/40 rounded-md flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-medium text-yellow-700 dark:text-yellow-300 sm:hidden">Medium</span>
                <span class="text-xs font-medium text-yellow-700 dark:text-yellow-300 hidden sm:inline">Medium burn</span>
                <span class="text-xs text-yellow-600/70 dark:text-yellow-400/70 hidden sm:block">Balanced</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- High Burn Rate Card -->
      <div class="relative overflow-hidden bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-red-200/40 dark:border-red-700/40 shadow-sm hover:shadow-md transition-all duration-300 group">
        <div class="absolute top-0 right-0 w-6 h-6 sm:w-10 sm:h-10 bg-red-200/20 dark:bg-red-600/10 rounded-full -translate-y-3 translate-x-3 sm:-translate-y-5 sm:translate-x-5"></div>
        <div class="relative">
          <div class="flex items-center justify-between lg:flex-col lg:items-start lg:space-y-2">
            <!-- Number first on large screens -->
            <span class="text-base sm:text-lg font-bold text-red-600 dark:text-red-400 lg:order-1 lg:text-xl lg:mb-1">{highBurnRateMainers}</span>
            
            <div class="flex items-center space-x-1.5 sm:space-x-2 lg:order-2">
              <div class="w-5 h-5 sm:w-6 sm:h-6 bg-red-100 dark:bg-red-900/40 rounded-md flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-2.5 w-2.5 sm:h-3 sm:w-3 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <div class="flex flex-col">
                <span class="text-xs font-medium text-red-700 dark:text-red-300 sm:hidden">High</span>
                <span class="text-xs font-medium text-red-700 dark:text-red-300 hidden sm:inline">High burn</span>
                <span class="text-xs text-red-600/70 dark:text-red-400/70 hidden sm:block">Performance</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Bottom accent line matching app style -->
  <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 dark:via-blue-500 to-transparent"></div>
</div> 