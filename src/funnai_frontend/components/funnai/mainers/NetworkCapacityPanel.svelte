<script lang="ts">
  // Props
  export let isVisible: boolean = false;
</script>

{#if isVisible}
  <div class="mb-4 relative overflow-hidden bg-gradient-to-br from-orange-50 via-amber-50 to-yellow-50 dark:from-orange-900/20 dark:via-amber-900/20 dark:to-yellow-900/20 border border-orange-200/60 dark:border-orange-700/60 rounded-xl shadow-sm">
    <!-- Background decorative elements -->
    <div class="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-orange-200/30 to-amber-200/30 dark:from-orange-600/10 dark:to-amber-600/10 rounded-full -translate-y-8 translate-x-8"></div>
    <div class="absolute bottom-0 left-0 w-12 h-12 bg-gradient-to-tr from-yellow-200/30 to-orange-200/30 dark:from-yellow-600/10 dark:to-orange-600/10 rounded-full translate-y-6 -translate-x-6"></div>
    
    <div class="relative p-4">
      <div class="flex items-start space-x-3">
        <!-- Icon -->
        <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-orange-500 to-amber-600 dark:from-orange-600 dark:to-amber-700 rounded-lg shadow-lg flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 00-2 2v2m0 0V9a2 2 0 012-2h14a2 2 0 012 2v2M7 7V6a3 3 0 016 0v1"/>
          </svg>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-3">
            <h3 class="text-sm font-bold text-orange-900 dark:text-orange-100">Network at full capacity</h3>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-300 border border-orange-300 dark:border-orange-700">
              Temporarily unavailable
            </span>
          </div>
          
          <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-3 border border-orange-200/40 dark:border-orange-700/40 mb-2">
            <div class="flex items-center space-x-2 text-xs text-orange-600 dark:text-orange-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="font-medium">Check our socials for updates: 
                <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">@onicaiHQ</a> 
                or 
                <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">OpenChat</a>
              </span>
            </div>
          </div>
          <div class="bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm rounded-lg p-3 border border-orange-200/40 dark:border-orange-700/40 mb-1">
            <div class="flex items-center space-x-2 text-xs text-orange-600 dark:text-orange-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="#4ade80">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
              </svg>
              <span class="font-medium">$FUNNAI available at: 
                <a href="https://app.icpswap.com/swap?input=ryjl3-tyaaa-aaaaa-aaaba-cai&output=vpyot-zqaaa-aaaaa-qavaq-cai" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">ICPSwap</a> 
                or 
                <a href="https://www.kongswap.io/stats/vpyot-zqaaa-aaaaa-qavaq-cai" target="_blank" rel="noopener noreferrer" class="text-orange-800 dark:text-orange-200 underline hover:text-orange-900 dark:hover:text-orange-100 transition-colors duration-200">KongSwap</a>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Bottom accent line -->
    <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-orange-400 dark:via-orange-500 to-transparent"></div>
  </div>
{/if}

