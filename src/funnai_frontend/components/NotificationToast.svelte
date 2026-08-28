<script lang="ts">
  import { notificationStore, type Notification } from '../stores/notificationStore';
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Portal from './Portal.svelte';

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

  function getPanelClasses(type: Notification['type']) {
    switch (type) {
      case 'success':
        return 'bg-emerald-950/95 border-emerald-500/45 text-emerald-50 shadow-[0_8px_32px_-8px_rgba(16,185,129,0.35)]';
      case 'error':
        return 'bg-red-950/95 border-red-500/45 text-red-50 shadow-[0_8px_32px_-8px_rgba(239,68,68,0.35)]';
      case 'warning':
        return 'bg-amber-950/95 border-amber-500/45 text-amber-50 shadow-[0_8px_32px_-8px_rgba(245,158,11,0.35)]';
      case 'info':
        return 'bg-slate-900/95 border-sky-500/45 text-slate-100 shadow-[0_8px_32px_-8px_rgba(56,189,248,0.25)]';
    }
  }

  function getIconClasses(type: Notification['type']) {
    switch (type) {
      case 'success':
        return 'text-emerald-400';
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-amber-400';
      case 'info':
        return 'text-sky-400';
    }
  }

  function getActionClasses(type: Notification['type']) {
    switch (type) {
      case 'success':
        return 'border-emerald-400/55 text-emerald-100 hover:bg-emerald-500/15';
      case 'error':
        return 'border-red-400/55 text-red-100 hover:bg-red-500/15';
      case 'warning':
        return 'border-amber-400/55 text-amber-100 hover:bg-amber-500/15';
      case 'info':
        return 'border-sky-400/55 text-sky-100 hover:bg-sky-500/15';
    }
  }

  function close(id: string) {
    notificationStore.remove(id);
  }
</script>

{#if notifications.length > 0}
  <Portal target="#portal-target">
    <div
      class="fixed flex flex-col gap-2 left-1/2 -translate-x-1/2 bottom-6 w-[min(calc(100%-2rem),28rem)] md:left-auto md:right-4 md:translate-x-0 md:bottom-4 md:w-auto md:max-w-md pointer-events-none"
      style="z-index: 100000;"
    >
      {#each notifications as notification (notification.id)}
        <div
          transition:fly={{ y: 50, duration: 300, easing: quintOut }}
          class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl border backdrop-blur-md {getPanelClasses(notification.type)}"
        >
          <div class="shrink-0 mt-0.5 {getIconClasses(notification.type)}">
            {@html getIcon(notification.type)}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium leading-snug text-inherit">{notification.message}</p>
            {#if notification.action}
              <button
                type="button"
                class="mt-2.5 inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-tight transition-colors {getActionClasses(notification.type)}"
                on:click={notification.action.onClick}
              >
                {notification.action.label}
              </button>
            {/if}
          </div>
          <button
            on:click={() => close(notification.id)}
            class="shrink-0 ml-1 rounded-md p-0.5 text-white/70 hover:text-white hover:bg-white/10 transition-colors"
            aria-label="Close notification"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      {/each}
    </div>
  </Portal>
{/if}
