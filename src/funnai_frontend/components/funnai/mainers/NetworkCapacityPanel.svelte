<script lang="ts">
  // Props
  export let isVisible: boolean = false;
</script>

{#if isVisible}
  <div class="my-4 agent-card border-amber-500/30 bg-amber-500/5">
    <div class="relative p-4">
      <div class="flex items-start space-x-3">
        <!-- Icon -->
        <div class="shrink-0 w-8 h-8 rounded-xl border border-amber-500/30 bg-amber-500/10 flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 00-2 2v2m0 0V9a2 2 0 012-2h14a2 2 0 012 2v2M7 7V6a3 3 0 016 0v1"/>
          </svg>
        </div>
        
        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 mb-3">
            <h3 class="text-sm font-semibold text-white">Network at full capacity</h3>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border border-amber-500/30 bg-amber-500/5 text-amber-300">
              Temporarily unavailable
            </span>
          </div>
          
          <div class="rounded-xl border border-white/10 bg-white/3 p-3 mb-2">
            <div class="flex items-center space-x-2 text-xs text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span class="font-medium">Check our socials for updates: 
                <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer" class="text-amber-300 underline hover:text-amber-200 transition-colors duration-200">X</a> 
                or 
                <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/" target="_blank" rel="noopener noreferrer" class="text-amber-300 underline hover:text-amber-200 transition-colors duration-200">OpenChat</a>
              </span>
            </div>
          </div>
          <div class="rounded-xl border border-white/10 bg-white/3 p-3 mb-1">
            <div class="flex items-center space-x-2 text-xs text-gray-400">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
              </svg>
              <span class="font-medium">$FUNNAI available at: 
                <a href="https://app.icpswap.com/swap?input=ryjl3-tyaaa-aaaaa-aaaba-cai&output=vpyot-zqaaa-aaaaa-qavaq-cai" target="_blank" rel="noopener noreferrer" class="text-amber-300 underline hover:text-amber-200 transition-colors duration-200">ICPSwap</a>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}
