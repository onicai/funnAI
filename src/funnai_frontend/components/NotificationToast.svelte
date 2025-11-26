<script lang="ts">
  import { notificationStore, type Notification } from '../stores/notificationStore';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  let notifications: Notification[] = [];
  
  notificationStore.subscribe(value => {
    notifications = value;
  });

  function getIcon(type: Notification['type']) {
    switch (type) {
      case 'success':
        return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>`;
      case 'error':
        return `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>`;
      case 'warning':
        return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>`;
      case 'info':
        return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
        </svg>`;
    }
  }

  function getClasses(type: Notification['type']) {
    switch (type) {
      case 'success':
        return 'bg-green-100 border-green-400 text-green-800 dark:bg-green-900/30 dark:border-green-700 dark:text-green-300';
      case 'error':
        return 'bg-red-100 border-red-400 text-red-800 dark:bg-red-900/30 dark:border-red-700 dark:text-red-300';
      case 'warning':
        return 'bg-yellow-100 border-yellow-400 text-yellow-800 dark:bg-yellow-900/30 dark:border-yellow-700 dark:text-yellow-300';
      case 'info':
        return 'bg-blue-100 border-blue-400 text-blue-800 dark:bg-blue-900/30 dark:border-blue-700 dark:text-blue-300';
    }
  }

  function close(id: string) {
    notificationStore.remove(id);
  }
</script>

{#if notifications.length > 0}
  <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-md">
    {#each notifications as notification (notification.id)}
      <div
        transition:fly={{ y: 50, duration: 300, easing: quintOut }}
        class="flex items-start gap-3 p-4 rounded-lg shadow-lg border-2 {getClasses(notification.type)} backdrop-blur-sm"
      >
        <div class="flex-shrink-0 mt-0.5">
          {@html getIcon(notification.type)}
        </div>
        <div class="flex-1 text-sm font-medium">
          {notification.message}
        </div>
        <button
          on:click={() => close(notification.id)}
          class="flex-shrink-0 ml-2 hover:opacity-70 transition-opacity"
          aria-label="Close notification"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    {/each}
  </div>
{/if}

