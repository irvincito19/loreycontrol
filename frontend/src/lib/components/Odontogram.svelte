<script lang="ts">
  import { Heart, AlertCircle, CheckCircle2, X } from 'lucide-svelte';
  import { fade } from 'svelte/transition';

  let { data = $bindable() } = $props();

  // Teeth numbers (FDI system)
  // Upper: 18-11, 21-28
  // Lower: 48-41, 31-38
  const upperRight = [18, 17, 16, 15, 14, 13, 12, 11];
  const upperLeft = [21, 22, 23, 24, 25, 26, 27, 28];
  const lowerRight = [48, 47, 46, 45, 44, 43, 42, 41];
  const lowerLeft = [31, 32, 33, 34, 35, 36, 37, 38];

  const states = [
    { id: 'healthy', label: 'Sano', color: 'bg-emerald-500' },
    { id: 'caries', label: 'Caries', color: 'bg-rose-500' },
    { id: 'missing', label: 'Ausente', color: 'bg-slate-700' },
    { id: 'filled', label: 'Obturado', color: 'bg-blue-500' },
    { id: 'endodontics', label: 'Endodoncia', color: 'bg-amber-500' }
  ];

  let selectedTooth = $state<number | null>(null);

  function getToothState(num: number) {
    if (!data) return 'healthy';
    try {
      const parsed = typeof data === 'string' ? JSON.parse(data) : data;
      return parsed[num] || 'healthy';
    } catch (e) {
      return 'healthy';
    }
  }

  function setToothState(num: number, state: string) {
    let current = {};
    try {
      current = typeof data === 'string' ? JSON.parse(data) : (data || {});
    } catch (e) {}
    
    current[num] = state;
    data = JSON.stringify(current);
  }
</script>

{#snippet tooth(num: number)}
  {@const state = getToothState(num)}
  {@const colorClass = states.find(s => s.id === state)?.color || 'bg-white/10'}
  <button 
    type="button"
    onclick={() => selectedTooth = num}
    class="flex flex-col items-center space-y-1 group"
  >
    <span class="text-[9px] font-bold text-white/40 group-hover:text-dent-kelly transition-colors">{num}</span>
    <div class={`w-8 h-10 rounded-lg ${colorClass} border border-white/10 shadow-lg transition-all transform group-hover:scale-110 flex items-center justify-center relative overflow-hidden`}>
       {#if state === 'caries'}
         <div class="absolute inset-0 flex items-center justify-center opacity-30">
           <AlertCircle size={14} class="text-white" />
         </div>
       {/if}
    </div>
  </button>
{/snippet}


<div class="p-6 bg-black/20 rounded-[2rem] border border-white/5">
  <div class="mb-8 flex justify-between items-center">
    <div>
      <h3 class="text-xl font-black text-white uppercase tracking-tight">Odontograma Básico</h3>
      <p class="text-xs text-[#ADC9CD] font-medium italic">Selecciona un diente para marcar su estado actual.</p>
    </div>
    
    <div class="flex flex-wrap gap-3 justify-end">
      {#each states as s}
        <div class="flex items-center space-x-1.5 bg-black/40 px-2.5 py-1 rounded-full border border-white/5">
          <div class={`w-2 h-2 rounded-full ${s.color}`}></div>
          <span class="text-[9px] font-bold text-white uppercase tracking-wider">{s.label}</span>
        </div>
      {/each}
    </div>
  </div>

  <div class="space-y-12">
    <!-- Arcada Superior -->
    <div class="space-y-4">
      <div class="flex justify-center space-x-2">
        <div class="flex space-x-1">
          {#each upperRight as num}
            {@render tooth(num)}
          {/each}
        </div>
        <div class="w-4"></div>
        <div class="flex space-x-1">
          {#each upperLeft as num}
            {@render tooth(num)}
          {/each}
        </div>
      </div>
      <div class="text-center">
        <span class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em]">Arcada Superior</span>
      </div>
    </div>

    <!-- Arcada Inferior -->
    <div class="space-y-4">
      <div class="text-center">
        <span class="text-[10px] font-black text-white/20 uppercase tracking-[0.3em]">Arcada Inferior</span>
      </div>
      <div class="flex justify-center space-x-2">
        <div class="flex space-x-1">
          {#each lowerRight as num}
            {@render tooth(num)}
          {/each}
        </div>
        <div class="w-4"></div>
        <div class="flex space-x-1">
          {#each lowerLeft as num}
            {@render tooth(num)}
          {/each}
        </div>
      </div>
    </div>
  </div>

  {#if selectedTooth}
    <div class="mt-10 p-4 bg-white/5 rounded-2xl border border-dent-kelly/20 flex items-center justify-between animate-in fade-in slide-in-from-bottom-2" transition:fade>
      <div class="flex items-center space-x-4">
        <div class="w-12 h-12 bg-dent-kelly/20 rounded-xl flex items-center justify-center font-black text-dent-kelly text-xl">
          {selectedTooth}
        </div>
        <div>
          <p class="text-xs font-bold text-[#ADC9CD] uppercase tracking-wider">Estado del Diente</p>
          <p class="text-sm font-black text-white uppercase">Pieza Seleccionada</p>
        </div>
      </div>

      <div class="flex space-x-2">
        {#each states as s}
          <button
            type="button"
            onclick={() => { setToothState(selectedTooth!, s.id); selectedTooth = null; }}
            class={`px-4 py-2 rounded-xl text-[10px] font-black uppercase transition-all border ${getToothState(selectedTooth) === s.id ? 'bg-dent-kelly text-white border-dent-kelly' : 'bg-black/40 text-white/40 border-white/10 hover:border-white/30'}`}
          >
            {s.label}
          </button>
        {/each}
        <button 
          type="button"
          onclick={() => selectedTooth = null}
          class="p-2 text-white/40 hover:text-white"
        >
          <X size={20} />
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  /* Custom scrollbar for small areas if needed */
</style>
