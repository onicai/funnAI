import { writable } from 'svelte/store';

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<Toast[]>([]);
  
  function show(message: string, type: Toast['type'] = 'info', duration: number = 5000) {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const toast: Toast = { id, message, type, duration };
    
    update(toasts => [...toasts, toast]);
    
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
    
    return id;
  }
  
  function remove(id: string) {
    update(toasts => toasts.filter(t => t.id !== id));
  }
  
  function success(message: string, duration?: number) {
    return show(message, 'success', duration);
  }
  
  function error(message: string, duration?: number) {
    return show(message, 'error', duration);
  }
  
  function warning(message: string, duration?: number) {
    return show(message, 'warning', duration);
  }
  
  function info(message: string, duration?: number) {
    return show(message, 'info', duration);
  }
  
  return {
    subscribe,
    show,
    remove,
    success,
    error,
    warning,
    info
  };
}

export const toastStore = createToastStore();

