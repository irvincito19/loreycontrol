<script lang="ts">
  import { uiStore } from '../ui.svelte';
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { CheckCircle2, AlertCircle, Info, X } from 'lucide-svelte';

  const icons = {
    success: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
    error: { icon: AlertCircle, color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20' },
    warning: { icon: AlertCircle, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
    info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' }
  };
</script>

<div class="fixed top-8 right-8 z-[500] flex flex-col space-y-3 pointer-events-none max-w-sm w-full">
  {#each uiStore.toasts as toast (toast.id)}
    <div 
      class="pointer-events-auto p-4 rounded-2xl backdrop-blur-xl border flex items-start space-x-3 shadow-2xl {icons[toast.type].bg} {icons[toast.type].border}"
      in:fly={{ x: 40, duration: 400 }}
      out:fade={{ duration: 200 }}
    >
      <div class="{icons[toast.type].color} mt-0.5">
        <svelte:component this={icons[toast.type].icon} size={20} />
      </div>
      
      <div class="flex-1">
        <p class="text-xs font-bold text-white uppercase tracking-tight">{toast.message}</p>
      </div>

      <button 
        onclick={() => uiStore.removeToast(toast.id)}
        class="text-white/20 hover:text-white transition-colors"
      >
        <X size={16} />
      </button>
    </div>
  {/each}
</div>
