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
  <div 
    class="p-4 rounded-lg shadow-lg text-sm {type === 'success' 
      ? 'bg-green-200 border-green-300 border-2 text-green-800' 
      : 'bg-red-200 border-red-300 border-2 text-red-800'}"
    role="alert"
  >
    {message}
  </div>
</div> 