<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { Calendar, Clock, Save, ShieldAlert, Plus, Trash2, CheckCircle2, XCircle } from 'lucide-svelte';
  import dayjs from 'dayjs';

  let config = $state<any[]>([]);
  let loading = $state(true);
  let saving = $state(false);
  let successMessage = $state('');

  // Días de la semana para la configuración base
  const days = [
    { id: 0, name: 'Lunes' },
    { id: 1, name: 'Martes' },
    { id: 2, name: 'Miércoles' },
    { id: 3, name: 'Jueves' },
    { id: 4, name: 'Viernes' },
    { id: 5, name: 'Sábado' },
    { id: 6, name: 'Domingo' }
  ];

  onMount(async () => {
    await loadConfig();
  });

  async function loadConfig() {
    loading = true;
    try {
      const data = await api.availability.getConfig();
      // Inicializar días faltantes si no hay config
      const completeConfig = days.map(day => {
        const found = data.find((c: any) => c.day_of_week === day.id);
        return found || {
          day_of_week: day.id,
          start_time: '09:00',
          end_time: '18:00',
          slot_duration: 30,
          active: false
        };
      });
      config = completeConfig;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function saveDayConfig(dayConfig: any) {
    saving = true;
    try {
      await api.availability.updateConfig(dayConfig);
      successMessage = `Horario de ${days[dayConfig.day_of_week].name} actualizado`;
      setTimeout(() => successMessage = '', 3000);
    } catch (e) {
      alert('Error al guardar: ' + e);
    } finally {
      saving = false;
    }
  }

  async function toggleDay(index: number) {
    config[index].active = !config[index].active;
    await saveDayConfig(config[index]);
  }
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="max-w-5xl mx-auto space-y-8">
    <header>
      <h1 class="text-4xl font-black text-white uppercase tracking-tighter">Configuración de Agenda</h1>
      <p class="text-[#ADC9CD] font-medium italic">Define tus horarios de atención y la duración de cada consulta.</p>
    </header>

    {#if loading}
      <div class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-dent-kelly"></div>
      </div>
    {:else}
      <div class="grid gap-6">
        <!-- Weekly Config -->
        <div class="card p-6 border-white/10 bg-[#013B44]/50 backdrop-blur-xl">
          <div class="flex items-center space-x-3 mb-8">
            <div class="p-3 bg-dent-kelly/20 rounded-2xl text-dent-kelly">
              <Clock size={24} />
            </div>
            <h2 class="text-2xl font-black text-white uppercase tracking-tight">Horario Semanal</h2>
          </div>

          <div class="space-y-4">
            {#each config as day, i}
              <div class="flex flex-col md:flex-row md:items-center justify-between p-5 rounded-[2rem] border {day.active ? 'border-dent-kelly/30 bg-white/5' : 'border-white/5 bg-black/20'} transition-all group">
                <div class="flex items-center space-x-4 mb-4 md:mb-0">
                  <button 
                    onclick={() => toggleDay(i)}
                    aria-label="Activar/Desactivar día"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none {day.active ? 'bg-dent-kelly' : 'bg-white/10'}"
                  >
                    <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform {day.active ? 'translate-x-6' : 'translate-x-1'}"></span>
                  </button>
                  <div>
                    <span class="text-lg font-black {day.active ? 'text-white' : 'text-white/40'}">{days[day.day_of_week].name}</span>
                  </div>
                </div>

                {#if day.active}
                  <div class="flex flex-wrap items-center gap-4 animate-in fade-in slide-in-from-right-4 duration-300">
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-bold text-[#ADC9CD] uppercase tracking-widest">Inicia</span>
                      <input type="time" bind:value={day.start_time} class="input-field py-1 px-3 w-32" />
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-bold text-[#ADC9CD] uppercase tracking-widest">Termina</span>
                      <input type="time" bind:value={day.end_time} class="input-field py-1 px-3 w-32" />
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="text-[10px] font-bold text-[#ADC9CD] uppercase tracking-widest">Intervalo</span>
                      <select bind:value={day.slot_duration} class="input-field py-1 px-3 w-24">
                        <option value={15}>15m</option>
                        <option value={20}>20m</option>
                        <option value={30}>30m</option>
                        <option value={45}>45m</option>
                        <option value={60}>60m</option>
                      </select>
                    </div>
                    <button 
                      onclick={() => saveDayConfig(day)}
                      disabled={saving}
                      aria-label="Guardar configuración"
                      class="p-2 bg-dent-kelly/20 text-dent-kelly hover:bg-dent-kelly hover:text-white rounded-xl transition-all"
                    >
                      <Save size={20} />
                    </button>
                  </div>
                {:else}
                  <span class="text-sm font-bold text-white/20 italic uppercase tracking-widest">Día de Descanso</span>
                {/if}
              </div>
            {/each}
          </div>
        </div>

        <!-- Future Overrides / Exceptions -->
        <div class="card p-6 border-white/10 bg-[#013B44]/50 backdrop-blur-xl opacity-60 grayscale hover:grayscale-0 hover:opacity-100 transition-all cursor-not-allowed">
          <div class="flex items-center justify-between mb-8">
            <div class="flex items-center space-x-3">
              <div class="p-3 bg-orange-500/20 rounded-2xl text-orange-400">
                <ShieldAlert size={24} />
              </div>
              <div>
                <h2 class="text-2xl font-black text-white uppercase tracking-tight">Excepciones y Bloqueos</h2>
                <p class="text-[10px] uppercase font-black tracking-widest text-[#ADC9CD]">Próximamente: Gestiona vacaciones y días festivos</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}

    {#if successMessage}
      <div class="fixed bottom-8 right-8 bg-dent-kelly text-white px-6 py-4 rounded-[1.5rem] shadow-2xl flex items-center space-x-3 animate-in slide-in-from-bottom-10">
        <CheckCircle2 size={24} />
        <span class="font-black uppercase tracking-tight">{successMessage}</span>
      </div>
    {/if}
  </div>
</div>

<style>
  @reference "../app.css";
  .input-field {
    @apply bg-black/40 border-white/10 text-white rounded-xl focus:border-dent-kelly focus:ring-1 focus:ring-dent-kelly transition-all;
  }
</style>
