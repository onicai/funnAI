<script lang="ts">

  
  // System status types
  type StatusLevel = 'excellent' | 'degraded' | 'paused';

  // Props for controlling global protocol status from parent component
  export let protocolStatus: StatusLevel = 'excellent';
  
  // Status level configurations
  const statusConfig = {
    excellent: {
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      textColor: 'text-green-600 dark:text-green-400',
      iconColor: 'text-green-600 dark:text-green-400',
      dotColor: 'bg-green-500'
    },
    degraded: {
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      textColor: 'text-yellow-600 dark:text-yellow-400',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      dotColor: 'bg-yellow-500'
    },
    paused: {
      bgColor: 'bg-red-100 dark:bg-red-900/30',
      textColor: 'text-red-600 dark:text-red-400',
      iconColor: 'text-red-600 dark:text-red-400',
      dotColor: 'bg-red-500'
    }
  };
  

  
  // Format status text with professional wording
  function formatStatus(status: StatusLevel): string {
    switch (status) {
      case 'excellent': return 'Systems operational';
      case 'degraded': return 'Performance degraded';
      case 'paused': return 'Service paused';
      default: return 'Status Unknown';
    }
  }

  // Get status description
  function getStatusDescription(status: StatusLevel): string {
    switch (status) {
      case 'excellent': return 'All services running smoothly.';
      case 'degraded': return 'Some performance issues detected.';
      case 'paused': return 'Protocol paused for upgrades.';
      default: return 'Status unavailable.';
    }
  }
  

  
  
  
  $: overallConfig = statusConfig[protocolStatus];
  $: statusDescription = getStatusDescription(protocolStatus);
</script>

<!-- System Status Card -->
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
  <div class="flex items-center justify-between">
    <div>
      <p class="text-sm font-medium text-gray-600 dark:text-gray-400">System status</p>
              <p class="text-lg font-semibold {overallConfig.textColor}">{formatStatus(protocolStatus)}</p>
    </div>
    <div class="p-3 {overallConfig.bgColor} rounded-full">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 {overallConfig.iconColor}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        {#if protocolStatus === 'excellent'}
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        {:else if protocolStatus === 'degraded'}
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        {:else}
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        {/if}
      </svg>
    </div>
  </div>
  <div class="mt-4">
    <p class="text-sm text-gray-600 dark:text-gray-400">{statusDescription}</p>
  </div>
</div>
