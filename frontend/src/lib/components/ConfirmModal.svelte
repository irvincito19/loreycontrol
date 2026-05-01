<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { X, AlertTriangle, Info, CheckCircle2 } from 'lucide-svelte';

  let { 
    show = false, 
    title = 'Confirmar Acción', 
    message = '¿Estás seguro de continuar?', 
    confirmText = 'Aceptar', 
    cancelText = 'Cancelar', 
    onConfirm, 
    onCancel,
    type = 'warning' 
  } = $props();

  const icons = {
    warning: { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    danger: { icon: AlertTriangle, color: 'text-rose-500', bg: 'bg-rose-500/10' },
    info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    success: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' }
  };

  const config = $derived(icons[type as keyof typeof icons] || icons.warning);
</script>

{#if show}
  <div class="fixed inset-0 bg-black/80 backdrop-blur-md z-[300] flex items-center justify-center p-4" in:fade>
    <div 
      class="bg-[#013B44] rounded-[2.5rem] w-full max-w-md border border-white/10 shadow-2xl overflow-hidden"
      in:fly={{ y: 20, duration: 400 }}
    >
      <div class="p-8 text-center">
        <div class="w-20 h-20 {config.bg} rounded-3xl flex items-center justify-center mx-auto mb-6 {config.color} shadow-inner">
          <config.icon size={40} />
        </div>
        
        <h2 class="text-2xl font-black text-white uppercase tracking-tighter mb-2">{title}</h2>
        <p class="text-[#ADC9CD] text-sm font-medium italic px-4 leading-relaxed">
          {message}
        </p>
      </div>

      <div class="p-6 bg-black/20 flex space-x-3">
        <button 
          onclick={onCancel} 
          class="flex-1 py-4 bg-white/5 text-white/40 font-black uppercase text-[10px] tracking-widest rounded-2xl hover:bg-white/10 transition-all"
        >
          {cancelText}
        </button>
        <button 
          onclick={onConfirm}
          class="flex-1 py-4 {type === 'danger' ? 'bg-rose-500' : 'bg-dent-kelly'} text-white font-black uppercase text-[10px] tracking-[0.2em] rounded-2xl shadow-xl transition-all hover:scale-105 active:scale-95"
        >
          {confirmText}
        </button>
      </div>
    </div>
  </div>
{/if}
