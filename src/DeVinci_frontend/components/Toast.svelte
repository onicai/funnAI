<script lang="ts">
  import { onMount } from 'svelte';

  export let message: string;
  export let type: 'success' | 'error' = 'success';
  export let duration: number = 3000;
  export let onClose: () => void;

  let visible = true;

  onMount(() => {
    const timer = setTimeout(() => {
      visible = false;
      setTimeout(onClose, 300); // Wait for fade out animation
    }, duration);

    return () => clearTimeout(timer);
  });
</script>

<div
  class="fixed bottom-4 right-4 z-50 transition-all duration-300 transform {visible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0'}"
>
  <div class="flex items-center p-4 rounded-lg shadow-lg {type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white">
    {#if type === 'success'}
      <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
    {:else}
      <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    {/if}
    <span class="font-medium">{message}</span>
  </div>
</div> 