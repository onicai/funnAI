<script lang="ts">
  import { fly, fade } from 'svelte/transition';
  import { CheckCircle2, XCircle, AlertCircle, Info, X } from 'lucide-svelte';
  
  export let message: string = '';
  export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
  export let duration: number = 5000; // ms
  export let onClose: () => void = () => {};
  
  let visible = true;
  let timeoutId: NodeJS.Timeout;
  
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
    success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
    error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200',
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
  }[type];
  
  $: iconColor = {
    success: 'text-green-600 dark:text-green-400',
    error: 'text-red-600 dark:text-red-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    info: 'text-blue-600 dark:text-blue-400'
  }[type];
</script>

{#if visible}
  <div
    class="fixed top-4 right-4 z-[100000] max-w-md"
    transition:fly={{ y: -20, duration: 300 }}
  >
    <div class="rounded-lg shadow-lg border-2 p-4 flex items-start space-x-3 {colors}">
      <svelte:component this={iconComponent} class="w-5 h-5 flex-shrink-0 mt-0.5 {iconColor}" />
      <p class="flex-1 text-sm font-medium break-words">{message}</p>
      <button
        on:click={handleClose}
        class="flex-shrink-0 hover:opacity-70 transition-opacity"
        aria-label="Close"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
{/if}

