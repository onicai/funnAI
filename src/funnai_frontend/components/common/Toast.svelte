<script lang="ts">
  import { fly } from 'svelte/transition';
  import { CheckCircle2, XCircle, AlertCircle, Info, X } from '@lucide/svelte';
  
  export let message: string = '';
  export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
  export let duration: number = 5000; // ms
  export let onClose: () => void = () => {};
  
  let visible = true;
  let timeoutId: ReturnType<typeof setTimeout>;
  
  $: if (visible && duration > 0) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      visible = false;
      setTimeout(onClose, 300); // Wait for fade out
    }, duration);
  }
  
  function handleClose() {
    clearTimeout(timeoutId);
    visible = false;
    setTimeout(onClose, 300);
  }
  
  $: iconComponent = {
    success: CheckCircle2,
    error: XCircle,
    warning: AlertCircle,
    info: Info
  }[type];
  
  $: colors = {
    success: 'bg-emerald-950/95 border-emerald-500/45 text-emerald-50 shadow-[0_8px_32px_-8px_rgba(16,185,129,0.35)]',
    error: 'bg-red-950/95 border-red-500/45 text-red-50 shadow-[0_8px_32px_-8px_rgba(239,68,68,0.35)]',
    warning: 'bg-amber-950/95 border-amber-500/45 text-amber-50 shadow-[0_8px_32px_-8px_rgba(245,158,11,0.35)]',
    info: 'bg-slate-900/95 border-sky-500/45 text-slate-100 shadow-[0_8px_32px_-8px_rgba(56,189,248,0.25)]'
  }[type];
  
  $: iconColor = {
    success: 'text-emerald-400',
    error: 'text-red-400',
    warning: 'text-amber-400',
    info: 'text-sky-400'
  }[type];
</script>

{#if visible}
  <div transition:fly={{ y: -20, duration: 300 }}>
    <div class="rounded-xl border p-4 flex items-start space-x-3 backdrop-blur-md {colors}">
      <svelte:component this={iconComponent} class="w-5 h-5 shrink-0 mt-0.5 {iconColor}" />
      <p class="flex-1 text-sm font-medium wrap-break-word">{message}</p>
      <button
        on:click={handleClose}
        class="shrink-0 rounded-md p-0.5 text-white/70 hover:text-white hover:bg-white/10 transition-colors"
        aria-label="Close"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
{/if}
