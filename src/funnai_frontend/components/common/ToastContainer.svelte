<script lang="ts">
  import { toastStore } from '../../stores/toastStore';
  import Toast from './Toast.svelte';
  
  $: toasts = $toastStore;
</script>

<div class="fixed top-4 right-4 z-[100000] space-y-2 pointer-events-none">
  {#each toasts as toast (toast.id)}
    <div class="pointer-events-auto">
      <Toast
        message={toast.message}
        type={toast.type}
        duration={toast.duration || 5000}
        onClose={() => toastStore.remove(toast.id)}
      />
    </div>
  {/each}
</div>

