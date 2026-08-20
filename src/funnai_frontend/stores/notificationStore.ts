import { writable } from 'svelte/store';

export interface NotificationAction {
  label: string;
  onClick: () => void;
}

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  action?: NotificationAction;
}

function createNotificationStore() {
  const { subscribe, update } = writable<Notification[]>([]);

  return {
    subscribe,
    
    add: (
      message: string,
      type: Notification['type'] = 'info',
      duration: number = 5000,
      action?: NotificationAction,
    ) => {
      const id = Math.random().toString(36).substring(2, 9);
      const notification: Notification = { id, message, type, duration, action };
      
      update(notifications => [...notifications, notification]);
      
      // Auto-remove after duration
      if (duration > 0) {
        setTimeout(() => {
          update(notifications => notifications.filter(n => n.id !== id));
        }, duration);
      }
      
      return id;
    },
    
    remove: (id: string) => {
      update(notifications => notifications.filter(n => n.id !== id));
    },
    
    clear: () => {
      update(() => []);
    }
  };
}

export const notificationStore = createNotificationStore();

