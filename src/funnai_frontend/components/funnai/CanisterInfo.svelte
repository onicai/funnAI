<script lang="ts">
  // Props
  export let agent: any;
</script>

<!-- Enhanced Canister Information Section -->
<div class="flex flex-col space-y-2 mb-2">
  <div class="relative overflow-hidden bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 border border-blue-200/60 dark:border-blue-700/60 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
    <!-- Background decorative elements -->
    <div class="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-200/30 to-indigo-200/30 dark:from-blue-600/10 dark:to-indigo-600/10 rounded-full -translate-y-10 translate-x-10"></div>
    <div class="absolute bottom-0 left-0 w-16 h-16 bg-gradient-to-tr from-purple-200/30 to-blue-200/30 dark:from-purple-600/10 dark:to-blue-600/10 rounded-full translate-y-8 -translate-x-8"></div>
    
    <div class="relative p-4 sm:p-5">
      <!-- Header Section -->
      <div class="flex items-center space-x-3 mb-4">
        <!-- Enhanced icon with gradient background -->
        <div class="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-xl shadow-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
          </svg>
        </div>
        
        <!-- Title and subtitle -->
        <div class="flex flex-col">
          <h2 class="text-sm sm:text-base font-bold text-blue-900 dark:text-blue-100">Canister Information</h2>
          <p class="text-xs text-blue-700 dark:text-blue-300">Internet Computer infrastructure details</p>
        </div>
      </div>

      <!-- Controller ID Section -->
      <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-xl p-4 border border-blue-200/40 dark:border-blue-700/40 shadow-sm">
        <div class="flex flex-col space-y-3">
          <!-- Controller ID Header -->
          <div class="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
            <span class="text-sm font-medium text-blue-900 dark:text-blue-100">Controller ID</span>
          </div>
          
          <!-- Enhanced Controller ID Link -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="font-mono text-xs text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-900/30 px-3 py-2 rounded-lg border border-blue-200/50 dark:border-blue-700/50">
                <span class="break-all">{agent.id}</span>
              </div>
            </div>
            
            <a 
              href="https://dashboard.internetcomputer.org/canister/{agent.id}" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="group relative inline-flex items-center justify-center px-4 py-2.5 text-sm font-bold text-white bg-gradient-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-indigo-700 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5 hover:scale-105 border border-blue-400/50 dark:border-blue-500/50 w-full sm:w-auto"
            >
              <div class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 group-hover:rotate-12 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                <span>View on Dashboard</span>
              </div>
              <div class="absolute inset-0 rounded-lg bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-600/20 dark:to-blue-600/20 opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
            </a>
          </div>
          
          <!-- Additional info -->
          <div class="pt-2 border-t border-blue-200/50 dark:border-blue-700/50">
            <div class="flex items-center space-x-2 text-xs text-blue-600/80 dark:text-blue-400/80">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Canister runs on Internet Computer Protocol</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Bottom accent line -->
    <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 dark:via-blue-500 to-transparent"></div>
  </div>
</div>
