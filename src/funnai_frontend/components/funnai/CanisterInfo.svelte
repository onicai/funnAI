<script lang="ts">
  // Props
  export let agent: any;
</script>

<!-- Enhanced Canister Information Section -->
<div class="flex flex-col space-y-2 mb-2">
  <div class="agent-card">
    <div class="p-4 sm:p-5">
      <!-- Header Section -->
      <div class="flex items-center space-x-3 mb-4">
        <div class="flex-shrink-0 w-10 h-10 rounded-xl border border-white/5 bg-white/[0.05] flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-agent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
          </svg>
        </div>
        
        <div class="flex flex-col">
          <p class="agent-eyebrow">Infrastructure</p>
          <h2 class="text-sm sm:text-base font-semibold tracking-tight text-white">Canister Information</h2>
          <p class="text-xs text-gray-500">Internet Computer infrastructure details</p>
        </div>
      </div>

      <!-- Controller ID Section -->
      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <div class="flex flex-col space-y-3">
          <!-- Controller ID Header -->
          <div class="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-agent-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
            <span class="text-sm font-medium text-gray-200">Controller ID</span>
          </div>
          
          <!-- Enhanced Controller ID Link -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="font-mono text-xs text-gray-300 bg-white/[0.03] px-3 py-2 rounded-lg border border-white/10">
                <span class="break-all">{agent.id}</span>
              </div>
            </div>
            
            <a 
              href="https://dashboard.internetcomputer.org/canister/{agent.id}" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-agent-purple rounded-xl border border-agent-purple/40 hover:bg-[#5a37b5] transition-colors w-full sm:w-auto"
            >
              <div class="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
                <span>View on Dashboard</span>
              </div>
            </a>
          </div>
          
          <!-- Additional info -->
          <div class="pt-2 border-t border-white/[0.08]">
            <div class="flex items-center space-x-2 text-xs text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Canister runs on Internet Computer Protocol</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
