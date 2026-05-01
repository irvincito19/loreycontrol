<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import dayjs from 'dayjs';
  import 'dayjs/locale/es';
  import { Calendar, Clock, Phone, MapPin, CheckCircle2, ChevronRight, ChevronLeft } from 'lucide-svelte';

  // Configurar español globalmente para este componente
  dayjs.locale('es');

  let selectedDate = $state(dayjs().format('YYYY-MM-DD'));
  let selectedLocation = $state('Oaxaca'); // default
  let selectedSlot = $state<string | null>(null);
  let slots = $state<any[]>([]);
  let loading = $state(false);
  let patientName = $state('');

  // Cargar slots cuando cambie la fecha o lugar
  $effect(() => {
    if (selectedDate && selectedLocation) {
      selectedSlot = null; // Resetear selección al cambiar fecha o lugar
      loadSlots();
    }
  });

  async function loadSlots() {
    loading = true;
    try {
      slots = await api.availability.getSlots(selectedDate, selectedLocation);
    } catch (e) {
      console.error('Error cargando disponibilidad:', e);
    } finally {
      loading = false;
    }
  }

  function nextDay() {
    selectedDate = dayjs(selectedDate).add(1, 'day').format('YYYY-MM-DD');
  }

  function prevDay() {
    if (dayjs(selectedDate).isAfter(dayjs(), 'day')) {
      selectedDate = dayjs(selectedDate).subtract(1, 'day').format('YYYY-MM-DD');
    }
  }

  function sendWhatsApp() {
    if (!patientName.trim()) {
      alert("Por favor, ingresa tu nombre para continuar.");
      return;
    }
    const phone = "5219511872103";
    const dateFormatted = dayjs(selectedDate).format('dddd D [de] MMMM');
    const time = selectedSlot || "[seleccionar horario]";
    const message = `Hola, soy ${patientName}. Me gustaría agendar una cita en ${selectedLocation} para el ${dateFormatted} a las ${time}. ¿Está disponible?`;
    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/${phone}?text=${encodedMessage}`, '_blank');
  }

  const formatDisplayDate = (dateStr: string) => {
    return dayjs(dateStr).format('dddd, D [de] MMMM');
  };
</script>

<div class="min-h-screen bg-[#012B33] text-white selection:bg-dent-kelly/30">
  <!-- Header / Hero Section -->
  <div class="relative overflow-hidden bg-black/20 border-b border-white/5 pt-12 pb-8 px-6">
    <div class="max-w-2xl mx-auto text-center space-y-4">
      <div class="inline-flex items-center space-x-2 bg-dent-kelly/10 px-4 py-2 rounded-2xl border border-dent-kelly/20 mb-4 animate-in fade-in zoom-in">
        <div class="w-2 h-2 rounded-full bg-dent-kelly animate-pulse"></div>
        <span class="text-[10px] font-black uppercase tracking-[0.2em] text-dent-kelly">Consulta de Disponibilidad</span>
      </div>
      <h1 class="text-5xl font-black uppercase tracking-tighter leading-none italic animate-in slide-in-from-top-4 duration-500">Dental Lorey</h1>
      <p class="text-[#ADC9CD] text-sm font-medium italic opacity-80 decoration-dent-kelly decoration-2">Selecciona la sucursal y fecha para visualizar los horarios libres.</p>
      
      <!-- Location Selector -->
      <div class="flex justify-center mt-8">
        <div class="bg-black/40 p-1 rounded-2xl border border-white/5 flex">
          <button 
            onclick={() => selectedLocation = 'Oaxaca'}
            class="px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all
              {selectedLocation === 'Oaxaca' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
          >
            Oaxaca
          </button>
          <button 
            onclick={() => selectedLocation = 'Miahuatlán'}
            class="px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all
              {selectedLocation === 'Miahuatlán' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
          >
            Miahuatlán
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="max-w-xl mx-auto p-6 -mt-4">
    <!-- Date Navigation Card -->
    <div class="bg-[#013B44] rounded-[2.5rem] p-6 shadow-2xl border border-white/10 mb-8 animate-in slide-in-from-bottom-8 duration-700">
      <div class="flex items-center justify-between mb-8">
        <button 
          onclick={prevDay} 
          disabled={dayjs(selectedDate).isSame(dayjs(), 'day')}
          class="p-4 hover:bg-white/5 rounded-2xl transition-all disabled:opacity-20 disabled:cursor-not-allowed group"
          aria-label="Día anterior"
        >
          <ChevronLeft size={24} class="group-hover:-translate-x-1 transition-transform" />
        </button>
        
        <div class="text-center flex-1">
          <input 
            type="date" 
            bind:value={selectedDate} 
            min={dayjs().format('YYYY-MM-DD')}
            class="hidden" 
            id="public-date-picker"
          />
          <label for="public-date-picker" class="cursor-pointer group">
            <span class="block text-[10px] font-black uppercase tracking-[0.3em] text-[#ADC9CD] mb-1 group-hover:text-dent-kelly transition-colors">
              {dayjs(selectedDate).format('YYYY')}
            </span>
            <span class="block text-xl font-black capitalize tracking-tight group-hover:scale-110 transition-transform">
              {formatDisplayDate(selectedDate)}
            </span>
          </label>
        </div>

        <button 
          onclick={nextDay} 
          class="p-4 hover:bg-white/5 rounded-2xl transition-all group"
          aria-label="Siguiente día"
        >
          <ChevronRight size={24} class="group-hover:translate-x-1 transition-transform" />
        </button>
      </div>

      <!-- Slots Grid -->
      <div class="relative min-h-[300px]">
        {#if loading}
          <div class="absolute inset-0 flex flex-col items-center justify-center space-y-4">
            <div class="w-12 h-12 border-4 border-dent-kelly/20 border-t-dent-kelly rounded-full animate-spin"></div>
            <p class="text-[10px] font-black uppercase tracking-widest text-dent-kelly animate-pulse">Consultando Agenda...</p>
          </div>
        {:else if slots.length === 0}
          <div class="flex flex-col items-center justify-center py-20 text-center opacity-40 animate-in fade-in">
            <Calendar size={64} class="mb-4 text-[#ADC9CD]" />
            <p class="font-black uppercase tracking-tighter text-lg">Sin horarios disponibles</p>
            <p class="text-xs italic">Prueba con otra fecha o contáctanos directamente.</p>
          </div>
        {:else}
          <div class="grid grid-cols-3 sm:grid-cols-4 gap-3 animate-in fade-in duration-500">
            {#each slots as slot}
              <button 
                type="button"
                onclick={() => { if (slot.available) selectedSlot = slot.time; }}
                disabled={!slot.available}
                class="relative p-4 rounded-2xl border text-center transition-all duration-300 transform active:scale-95
                  {slot.available 
                    ? (selectedSlot === slot.time 
                        ? 'bg-dent-kelly border-dent-kelly text-white shadow-xl shadow-dent-kelly/40 scale-105 z-10' 
                        : 'bg-white/5 border-white/10 hover:border-dent-kelly hover:bg-dent-kelly/10 text-white') 
                    : 'bg-black/20 border-white/5 opacity-30 grayscale cursor-not-allowed'}"
              >
                <div class="text-sm font-black">
                  {slot.time}
                </div>
                {#if slot.available}
                  <div class="mt-1 text-[8px] font-black uppercase tracking-tighter {selectedSlot === slot.time ? 'text-white/80' : 'text-dent-kelly'}">
                    {selectedSlot === slot.time ? 'Seleccionado' : 'Libre'}
                  </div>
                {/if}
              </button>
            {/each}
          </div>
        {/if}
      </div>
    </div>

    <!-- Contact Info -->
    <div class="space-y-6 animate-in slide-in-from-bottom-12 duration-1000">
        <div class="p-8 bg-[#014D67] rounded-[2.5rem] border border-dent-kelly/30 shadow-xl overflow-hidden relative">
            <div class="absolute top-0 right-0 p-8 opacity-10">
                <Phone size={120} />
            </div>
            
            <h3 class="text-lg font-black uppercase tracking-tight mb-4 flex items-center space-x-2">
                <CheckCircle2 size={24} class="text-dent-kelly" />
                <span>¿Encontraste un espacio?</span>
            </h3>
            <p class="text-sm text-[#ADC9CD] font-medium leading-relaxed mb-6">
                Para apartar tu lugar, ingresa tu nombre y envíanos un mensaje por WhatsApp mencionando el horario de tu interés.
            </p>
            
            <div class="space-y-4">
                <div>
                    <label for="p-name" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-2 px-1">Tu Nombre Completo</label>
                    <input 
                        id="p-name"
                        type="text" 
                        bind:value={patientName}
                        placeholder="Escribe tu nombre aquí..."
                        class="w-full bg-black/20 border border-white/10 rounded-2xl p-4 text-white text-sm focus:border-dent-kelly focus:ring-1 focus:ring-dent-kelly transition-all placeholder:text-white/20"
                    />
                </div>

                <button 
                    onclick={sendWhatsApp}
                    class="w-full py-4 bg-dent-kelly hover:bg-white hover:text-dent-forest text-white rounded-2xl font-black uppercase tracking-widest text-xs transition-all shadow-lg shadow-dent-kelly/20 flex items-center justify-center space-x-3"
                >
                    <Phone size={16} />
                    <span>Contactar vía WhatsApp</span>
                </button>
            </div>
        </div>

        <div class="flex items-center justify-center space-x-6 text-[#ADC9CD] opacity-60">
            <div class="flex items-center space-x-2">
                <MapPin size={14} />
                <span class="text-[10px] font-bold uppercase tracking-widest">Sucursal {selectedLocation}</span>
            </div>
            <div class="w-1 h-1 bg-white/20 rounded-full"></div>
            <div class="flex items-center space-x-2">
                <Clock size={14} />
                <span class="text-[10px] font-bold uppercase tracking-widest">9:00 - 18:00</span>
            </div>
        </div>
    </div>
  </div>

  <footer class="py-12 text-center opacity-30">
    <p class="text-[10px] font-black uppercase tracking-[0.4em]">© 2026 Dental Lorey</p>
  </footer>
</div>

<style>
  @reference "../app.css";
  
  :global(body) {
    background-color: #012B33;
  }
</style>
