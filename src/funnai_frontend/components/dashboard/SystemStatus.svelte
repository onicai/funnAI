<script lang="ts">
  type StatusLevel = 'excellent' | 'degraded' | 'paused';

  export let protocolStatus: StatusLevel = 'excellent';

  const statusConfig = {
    excellent: {
      textColor: 'text-emerald-300',
      chip: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300',
      dot: 'bg-emerald-400',
    },
    degraded: {
      textColor: 'text-amber-300',
      chip: 'border-amber-500/20 bg-amber-500/10 text-amber-300',
      dot: 'bg-amber-400',
    },
    paused: {
      textColor: 'text-red-300',
      chip: 'border-red-500/20 bg-red-500/10 text-red-300',
      dot: 'bg-red-400',
    },
  };

  function formatStatus(status: StatusLevel): string {
    switch (status) {
      case 'excellent': return 'Operational';
      case 'degraded': return 'Degraded';
      case 'paused': return 'Paused';
      default: return 'Unknown';
    }
  }

  function getStatusDescription(status: StatusLevel): string {
    switch (status) {
      case 'excellent': return 'All services running smoothly';
      case 'degraded': return 'Some performance issues detected';
      case 'paused': return 'Protocol paused for upgrades';
      default: return 'Status unavailable';
    }
  }

  $: overallConfig = statusConfig[protocolStatus];
</script>

<div class="agent-card bg-agent-surface! p-5">
  <div class="relative z-1 flex items-center gap-2">
    <p class="agent-eyebrow">Status</p>
    <span class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-medium {overallConfig.chip}">
      <span class="h-1 w-1 rounded-full {overallConfig.dot} {protocolStatus === 'excellent' ? 'animate-pulse' : ''}"></span>
      Live
    </span>
  </div>
  <p class="relative z-1 mt-3 text-2xl font-semibold tracking-tight leading-8 min-h-8 {overallConfig.textColor}">
    {formatStatus(protocolStatus)}
  </p>
  <p class="relative z-1 mt-1 text-xs leading-4 min-h-4 text-gray-500">{getStatusDescription(protocolStatus)}</p>
</div>
