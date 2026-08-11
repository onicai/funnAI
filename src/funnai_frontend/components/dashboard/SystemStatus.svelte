<script lang="ts">

  
  // System status types
  type StatusLevel = 'excellent' | 'degraded' | 'paused';

  // Props for controlling global protocol status from parent component
  export let protocolStatus: StatusLevel = 'excellent';
  
  // Status level configurations
  const statusConfig = {
    excellent: {
      bgColor: 'border border-white/5 bg-white/[0.05]',
      textColor: 'text-emerald-400',
      iconColor: 'text-emerald-400',
      dotColor: 'bg-emerald-500'
    },
    degraded: {
      bgColor: 'border border-white/5 bg-white/[0.05]',
      textColor: 'text-amber-400',
      iconColor: 'text-amber-400',
      dotColor: 'bg-amber-500'
    },
    paused: {
      bgColor: 'border border-white/5 bg-white/[0.05]',
      textColor: 'text-red-400',
      iconColor: 'text-red-400',
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
<div class="agent-card p-6">
  <div class="flex items-center justify-between">
    <div>
      <p class="agent-eyebrow">Status</p>
      <p class="mt-1 text-lg font-semibold tracking-tight {overallConfig.textColor}">{formatStatus(protocolStatus)}</p>
    </div>
    <div class="p-3 {overallConfig.bgColor} rounded-xl">
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
    <p class="text-sm text-gray-400">{statusDescription}</p>
  </div>
</div>
