<script lang="ts">
  import { toastStore } from '../../stores/toastStore';
  import Toast from './Toast.svelte';
  import Portal from '../Portal.svelte';
  
  $: toasts = $toastStore;
</script>

<!-- Portal out of page stacking contexts (e.g. main content z-1 under header z-50) -->
<Portal target="#portal-target">
  <div
    class="fixed top-4 right-4 space-y-2 pointer-events-none max-w-md w-[calc(100%-2rem)] sm:w-auto"
    style="z-index: 100000;"
  >
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
</Portal>
