// Svelte 5 state-based UI store
class UIStore {
  toasts = $state<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' | 'warning'; duration: number }>>([]);

  addToast(message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info', duration = 4000) {
    const id = crypto.randomUUID();
    this.toasts.push({ id, message, type, duration });
    
    setTimeout(() => {
      this.removeToast(id);
    }, duration);
  }

  removeToast(id: string) {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }
}

export const uiStore = new UIStore();
