<script lang="ts">
  // Store import removed as it's not being used in this component
  
  // Props
  export let lottery: {
    id: number;
    name: string;
    description: string;
    nextDraw: Date;
    prize: string;
    deposit: number;
    isRegistered: boolean;
    type: string;
  };
  
  export let featured: boolean = false;
  
  // Format date to readable string
  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  // Calculate time remaining
  const getTimeRemaining = (date) => {
    const total = date.getTime() - new Date().getTime();
    const hours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };
  
</script>

{#if featured}
  <!-- Featured lottery card -->
  <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 shadow-sm border border-blue-100 dark:border-blue-800">
    <div class="flex justify-between items-start">
      <div>
        <h4 class="text-lg font-semibold text-blue-800 dark:text-blue-300">{lottery.name}</h4>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{lottery.description}</p>
      </div>
      {#if lottery.type === "whitelist"}
        <span class="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-xs font-medium px-2 py-0.5 rounded">Whitelist</span>
      {/if}
    </div>
    
    <div class="grid grid-cols-2 gap-2 mt-3">
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Prize</div>
        <div class="text-sm font-medium text-gray-800 dark:text-gray-200">{lottery.prize}</div>
      </div>
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400">Next Draw</div>
        <div class="text-sm font-medium text-gray-800 dark:text-gray-200">{formatDate(lottery.nextDraw)}</div>
      </div>
      {#if lottery.deposit > 0}
        <div class="col-span-2">
          <div class="text-xs text-gray-500 dark:text-gray-400">Deposit Required</div>
          <div class="text-sm font-medium text-gray-800 dark:text-gray-200">{lottery.deposit} ICP (credited toward mAIner creation)</div>
        </div>
      {/if}
    </div>
    
    <div class="mt-3 flex items-center justify-between">
      <div class="text-sm">
        <span class="text-blue-600 dark:text-blue-400 font-semibold">{getTimeRemaining(lottery.nextDraw)}</span>
        <span class="text-gray-500 dark:text-gray-400"> remaining</span>
      </div>
      
      {#if lottery.isRegistered}
        <button class="text-sm bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 px-3 py-1 rounded-md" disabled>
          Registered
        </button>
      {:else}
        <button
          class="text-sm text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 px-3 py-1 rounded-md"
        >
          Register
        </button>
      {/if}
    </div>
  </div>
{:else}
  <!-- Compact lottery card -->
  <div class="bg-gray-50 dark:bg-gray-800/50 rounded-md p-3 flex justify-between items-center">
    <div>
      <div class="flex items-center space-x-2">
        <h5 class="text-sm font-medium text-gray-800 dark:text-white">{lottery.name}</h5>
        {#if lottery.type === "whitelist"}
          <span class="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-xs font-medium px-2 py-0.5 rounded">Whitelist</span>
        {/if}
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
        Draw: {formatDate(lottery.nextDraw)} ({getTimeRemaining(lottery.nextDraw)} left)
      </div>
    </div>
    
    {#if lottery.isRegistered}
      <button class="text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 px-2 py-1 rounded" disabled>
        Registered
      </button>
    {:else}
      <button 
        class="text-xs min-w-[60px] text-white bg-purple-600 dark:bg-purple-700 px-1 py-1 rounded"
      >
        No Code
      </button>
    {/if}
  </div>
{/if} 