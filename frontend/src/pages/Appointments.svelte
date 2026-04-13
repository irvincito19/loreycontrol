<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { Calendar, Plus, ChevronLeft, ChevronRight, X, Trash2, Eye } from 'lucide-svelte';
  import dayjs from 'dayjs';
  import 'dayjs/locale/es';

  dayjs.locale('es');

  let appointments = $state<any[]>([]);
  let patients = $state<any[]>([]);
  let loading = $state(true);
  let showModal = $state(false);
  let showDayModal = $state(false);
  let currentMonth = $state(dayjs());
  let selectedDate = $state(dayjs());
  let selectedDayAppointments = $state<any[]>([]);

  let appointmentForm = $state({
    patient_id: '',
    date: dayjs().format('YYYY-MM-DD'),
    time: '',
    description: '',
    status: 'pendiente'
  });

  let slots = $state<any[]>([]);
  let loadingSlots = $state(false);

  onMount(async () => {
    await Promise.all([loadAppointments(), loadPatients()]);
  });

  async function loadSlots(date: string) {
    if (!date) return;
    loadingSlots = true;
    try {
      slots = await api.availability.getSlots(date);
    } catch (e) {
      console.error(e);
      slots = [];
    } finally {
      loadingSlots = false;
    }
  }

  // Cargar slots cuando cambie la fecha
  $effect(() => {
    if (appointmentForm.date) {
      loadSlots(appointmentForm.date);
    }
  });

  async function loadAppointments() {
    loading = true;
    try {
      const start = currentMonth.startOf('month').toISOString();
      const end = currentMonth.endOf('month').toISOString();
      appointments = await api.appointments.list(start, end);
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  async function loadPatients() {
    try {
      patients = await api.patients.list();
    } catch (e) {
      console.error(e);
    }
  }

  const daysInMonth = $derived.by(() => {
    const days = [];
    const startOfMonth = currentMonth.startOf('month');
    const endOfMonth = currentMonth.endOf('month');
    
    for (let i = 0; i < startOfMonth.day(); i++) {
      days.push(null);
    }
    
    for (let i = 1; i <= endOfMonth.date(); i++) {
      days.push(startOfMonth.date(i));
    }
    
    return days;
  });

  function nextMonth() {
    currentMonth = currentMonth.add(1, 'month');
    loadAppointments();
  }

  function prevMonth() {
    currentMonth = currentMonth.subtract(1, 'month');
    loadAppointments();
  }

  function openModal(date: any = null) {
    const dateStr = date ? dayjs(date).format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD');
    appointmentForm = {
      patient_id: '',
      date: dateStr,
      time: '',
      description: '',
      status: 'pendiente'
    };
    loadSlots(dateStr);
    showModal = true;
  }

  function openDayView(date: any) {
    if (!date) return;
    selectedDate = date;
    const apps = getAppointmentsForDay(date);
    selectedDayAppointments = apps;
    if (apps.length > 0) {
      showDayModal = true;
    } else {
      openModal(date);
    }
  }

  async function handleSubmit() {
    if (!appointmentForm.time) {
      alert('Por favor, selecciona un horario disponible.');
      return;
    }

    try {
      const dateTime = `${appointmentForm.date}T${appointmentForm.time}:00`;
      await api.appointments.create({
        patient_id: parseInt(appointmentForm.patient_id) || 0,
        date_time: dateTime,
        description: appointmentForm.description,
        status: appointmentForm.status
      });
      showModal = false;
      await loadAppointments();
    } catch (e) {
      alert('Error: ' + e);
    }
  }

  async function deleteAppointment(id: number) {
    if (confirm('¿Eliminar cita?')) {
      await api.appointments.delete(id);
      await loadAppointments();
    }
  }

  async function updateStatus(appt: any, newStatus: string) {
    try {
      await api.appointments.update(appt.id, {
        patient_id: appt.patient_id,
        date_time: appt.date_time,
        description: appt.description,
        status: newStatus
      });
      
      // Actualizar localmente la lista de citas del día si el modal está abierto
      selectedDayAppointments = selectedDayAppointments.map(a => 
        a.id === appt.id ? { ...a, status: newStatus } : a
      );
      
      await loadAppointments();
    } catch (e) {
      alert('Error al actualizar estado: ' + e);
    }
  }

  function getAppointmentsForDay(date: any) {
    if (!date) return [];
    const dateStr = date.format('YYYY-MM-DD');
    return appointments.filter(a => dayjs(a.date_time).format('YYYY-MM-DD') === dateStr);
  }

  const statusColors: any = {
    'pendiente': 'bg-orange-900/50 text-orange-300 border-orange-700/50',
    'atendido': 'bg-green-900/50 text-green-300 border-green-700/50',
    'cancelado': 'bg-red-900/50 text-red-300 border-red-700/50'
  };
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
    <div>
      <h1 class="text-4xl font-black text-white uppercase tracking-tighter">Cronograma de Citas</h1>
      <p class="text-[#ADC9CD] font-medium italic">Organiza la agenda clínica de Dental Lorey con precisión.</p>
    </div>

    <button onclick={() => openModal()} class="btn-primary flex items-center space-x-2">
      <Plus size={20} />
      <span>Nueva Cita</span>
    </button>
  </div>

  <!-- Calendar Interface -->
  <div class="card p-0 overflow-hidden border-white/10 bg-[#013B44]">
    <div class="p-6 border-b border-white/10 flex items-center justify-between bg-black/20 backdrop-blur-md">
      <h2 class="text-2xl font-black text-white capitalize tracking-tighter">
        {currentMonth.format('MMMM YYYY')}
      </h2>
      <div class="flex items-center space-x-3">
        <button onclick={prevMonth} class="p-2.5 hover:bg-white/10 rounded-2xl text-[#C2D7DA] hover:text-white transition-all">
          <ChevronLeft size={24} />
        </button>
        <button onclick={() => currentMonth = dayjs()} class="px-6 py-2 text-sm font-black bg-dent-kelly text-white rounded-xl hover:bg-white hover:text-dent-forest transition-all uppercase tracking-widest">
          Hoy
        </button>
        <button onclick={nextMonth} class="p-2.5 hover:bg-white/10 rounded-2xl text-[#C2D7DA] hover:text-white transition-all">
          <ChevronRight size={24} />
        </button>
      </div>
    </div>

    <div class="grid grid-cols-7 text-center border-b border-white/5 bg-black/40">
      {#each ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'] as day}
        <div class="py-3 text-[10px] font-black text-[#ADC9CD] uppercase tracking-[0.2em]">
          {day}
        </div>
      {/each}
    </div>

    <div class="grid grid-cols-7 grid-rows-5 auto-rows-fr min-h-[600px] bg-black/20 gap-px">
      {#each daysInMonth as date}
        <div class="bg-[#014D67]/80 p-2 flex flex-col group min-h-[120px] border-b border-r border-white/5 relative hover:bg-white/5 transition-colors">
          {#if date}
            <div class="flex justify-between items-center mb-2">
              <span class="text-sm font-black {date.isSame(dayjs(), 'day') ? 'bg-dent-kelly text-white w-8 h-8 flex items-center justify-center rounded-xl shadow-lg shadow-dent-kelly/20' : 'text-[#C2D7DA]'}">
                {date.date()}
              </span>
              {#if getAppointmentsForDay(date).length > 0}
                <span class="bg-dent-mint text-dent-forest text-[10px] font-black px-2 py-0.5 rounded-lg shadow-sm">
                  {getAppointmentsForDay(date).length}
                </span>
              {/if}
            </div>

            <div class="flex-1 space-y-1 overflow-hidden mb-8">
              {#each getAppointmentsForDay(date).slice(0, 2) as appt}
                <div class="text-[9px] p-1 rounded border shadow-sm {statusColors[appt.status]} truncate font-medium">
                  {dayjs(appt.date_time).format('HH:mm')} - {appt.patient?.name || `P#${appt.patient_id}`}
                </div>
              {/each}
              {#if getAppointmentsForDay(date).length > 2}
                <div class="text-[8px] text-[#ADC9CD] font-bold pl-1 italic">
                  + {getAppointmentsForDay(date).length - 2} más
                </div>
              {/if}
            </div>

            <div class="absolute bottom-2 left-2 right-2 flex justify-between opacity-0 group-hover:opacity-100 transition-all transform translate-y-1 group-hover:translate-y-0">
              <button 
                onclick={(e) => { e.stopPropagation(); openDayView(date); }} 
                class="flex-1 mr-1 py-1.5 bg-[#014D67] hover:bg-dent-kelly text-white rounded-xl transition-all flex items-center justify-center space-x-1 border border-white/20 shadow-xl"
                title="Ver citas"
              >
                <Eye size={12} />
                <span class="text-[9px] font-black uppercase tracking-tighter">Ver</span>
              </button>
              <button 
                onclick={(e) => { e.stopPropagation(); openModal(date); }} 
                class="flex-1 ml-1 py-1.5 bg-[#014D67] hover:bg-dent-kelly text-white rounded-xl transition-all flex items-center justify-center space-x-1 border border-white/20 shadow-xl"
                title="Añadir cita"
              >
                <Plus size={12} />
                <span class="text-[9px] font-black uppercase tracking-tighter">Cita</span>
              </button>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</div>

<!-- Modal Form -->
{#if showModal}
  <div class="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] flex items-center justify-center p-4">
    <div class="bg-[#014D67] rounded-[2.5rem] w-full max-w-4xl shadow-2xl animate-in fade-in zoom-in duration-200 border border-[#00ACB1]/30 overflow-hidden">
      <div class="p-6 border-b border-[#00ACB1]/20 flex justify-between items-center bg-black/20">
        <div>
          <h1 class="text-xl font-black uppercase tracking-tight text-white">Programar Cita</h1>
          <p class="text-[10px] text-[#ADC9CD] font-black uppercase tracking-widest">Paso 1: Selecciona fecha y horario</p>
        </div>
        <button onclick={() => showModal = false} class="text-[#ADC9CD] hover:text-white transition-colors p-2 hover:bg-white/10 rounded-full">
          <X size={24} />
        </button>
      </div>

      <div class="grid md:grid-cols-2 gap-0 overflow-y-auto max-h-[85vh]">
        <!-- Left: Basic Info -->
        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="p-8 space-y-6 border-r border-[#00ACB1]/10">
          <div>
            <label for="a-patient" class="block text-xs font-black text-[#ADC9CD] mb-3 uppercase tracking-widest">Paciente *</label>
            <select id="a-patient" bind:value={appointmentForm.patient_id} required class="input-field">
              <option value="">Selecciona un paciente</option>
              {#each patients as p}
                <option value={p.id}>{p.name}</option>
              {/each}
            </select>
          </div>
          
          <div>
            <label for="a-date" class="block text-xs font-black text-[#ADC9CD] mb-3 uppercase tracking-widest">Fecha deseada *</label>
            <input id="a-date" type="date" bind:value={appointmentForm.date} required class="input-field" />
          </div>

          <div>
            <label for="a-desc" class="block text-xs font-black text-[#ADC9CD] mb-3 uppercase tracking-widest">Descripción / Motivo</label>
            <textarea id="a-desc" bind:value={appointmentForm.description} class="input-field h-28 resize-none" placeholder="Ej. Limpieza profunda, revisión..." ></textarea>
          </div>

          <div class="flex space-x-4 pt-6">
            <button type="button" onclick={() => showModal = false} class="flex-1 px-4 py-4 border border-white/10 rounded-2xl text-[#ADC9CD] hover:bg-white/5 font-black uppercase text-xs tracking-widest transition-all">
              Cancelar
            </button>
            <button type="submit" disabled={!appointmentForm.time} class="flex-1 btn-primary py-4 disabled:opacity-30 disabled:cursor-not-allowed shadow-xl shadow-dent-blue/20">
              Confirmar
            </button>
          </div>
        </form>

        <!-- Right: Slot Selector -->
        <div class="p-8 bg-black/10 flex flex-col h-full">
          <div class="block text-xs font-black text-[#ADC9CD] mb-4 uppercase tracking-widest">Horarios Disponibles</div>
          
          {#if loadingSlots}
            <div class="flex flex-col items-center justify-center flex-1 py-12 space-y-4">
              <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-dent-kelly"></div>
              <span class="text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest animate-pulse">Consultando agenda...</span>
            </div>
          {:else if slots.length === 0}
            <div class="flex flex-col items-center justify-center flex-1 py-12 text-center space-y-4">
              <Calendar size={48} class="text-white/10" />
              <div class="space-y-1">
                <p class="text-sm font-bold text-white/50 uppercase tracking-tighter">Sin Disponibilidad</p>
                <p class="text-[10px] text-[#ADC9CD] font-medium italic">No hay horarios configurados para este día.</p>
              </div>
            </div>
          {:else}
            <div class="grid grid-cols-3 gap-3 overflow-y-auto pr-2">
              {#each slots as slot}
                <button 
                  type="button"
                  onclick={() => { if (slot.available) appointmentForm.time = slot.time; }}
                  disabled={!slot.available}
                  class="py-4 px-2 rounded-2xl border text-xs font-black transition-all transform active:scale-95
                    {slot.available 
                      ? (appointmentForm.time === slot.time 
                          ? 'bg-dent-kelly border-dent-kelly text-white shadow-xl shadow-dent-kelly/30 scale-105 z-10' 
                          : 'border-white/10 bg-white/5 text-[#ADC9CD] hover:border-dent-kelly hover:text-white hover:bg-dent-kelly/10')
                      : 'border-white/5 bg-black/40 text-white/10 cursor-not-allowed opacity-30 grayscale'}"
                >
                  {slot.time}
                </button>
              {/each}
            </div>
            <div class="mt-8 pt-6 border-t border-white/5">
                <div class="flex items-center justify-between text-[9px] font-black uppercase tracking-widest text-[#ADC9CD]">
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-dent-kelly"></div>
                        <span>Seleccionado</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-white/10"></div>
                        <span>Disponible</span>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="w-3 h-3 rounded-full bg-black/40 opacity-30"></div>
                        <span>Ocupado</span>
                    </div>
                </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Day View Modal stays mostly same but updated with cleaner UI -->
{#if showDayModal}
  <div class="fixed inset-0 bg-black/80 backdrop-blur-md z-[110] flex items-center justify-center p-4">
    <div class="bg-[#014D67] rounded-[2.5rem] w-full max-w-md shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-8 duration-500 border border-[#00ACB1]/30">
      <div class="p-6 bg-black/20 text-white flex justify-between items-center">
        <div>
          <h2 class="text-xl font-black uppercase tracking-tighter">Citas del Día</h2>
          <p class="text-[#ADC9CD] text-[10px] font-black uppercase tracking-widest mt-1">{selectedDate.format('D [de] MMMM, YYYY')}</p>
        </div>
        <button onclick={() => showDayModal = false} class="p-2 hover:bg-white/10 rounded-full transition-colors">
          <X size={24} />
        </button>
      </div>

      <div class="p-6 space-y-3 max-h-[400px] overflow-y-auto">
        {#each selectedDayAppointments as appt}
          <div class="flex items-start space-x-4 p-4 rounded-[1.5rem] border border-white/10 hover:border-[#00ACB1]/30 hover:bg-white/5 transition-all group">
            <div class="bg-dent-kelly text-white px-3 py-1.5 rounded-xl font-black text-xs shadow-lg shadow-dent-kelly/10">
              {dayjs(appt.date_time).format('HH:mm')}
            </div>
            <div class="flex-1">
              <h3 class="font-black text-white text-sm uppercase tracking-tight">{appt.patient?.name || `Paciente #${appt.patient_id}`}</h3>
              <p class="text-[11px] text-[#ADC9CD] italic mt-0.5">{appt.description || 'Sin descripción'}</p>
              <div class="flex flex-wrap items-center gap-2 mt-3">
                <button 
                  onclick={() => updateStatus(appt, 'atendido')}
                  disabled={appt.status === 'atendido'}
                  class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all
                    {appt.status === 'atendido' 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                      : 'bg-black/20 text-[#ADC9CD] border border-white/5 hover:border-green-500/50 hover:text-green-400'}"
                >
                  ✅ {appt.status === 'atendido' ? 'Atendido' : 'Atender'}
                </button>
                <button 
                  onclick={() => updateStatus(appt, 'cancelado')}
                  disabled={appt.status === 'cancelado'}
                  class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all
                    {appt.status === 'cancelado' 
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30' 
                      : 'bg-black/20 text-[#ADC9CD] border border-white/5 hover:border-red-500/50 hover:text-red-400'}"
                >
                  ❌ {appt.status === 'cancelado' ? 'Cancelado' : 'Cancelar'}
                </button>
                {#if appt.status !== 'pendiente'}
                  <button 
                    onclick={() => updateStatus(appt, 'pendiente')}
                    class="px-3 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest bg-black/20 text-[#ADC9CD] border border-white/5 hover:border-orange-500/50 hover:text-orange-400 transition-all"
                  >
                    ⏳ Reset
                  </button>
                {/if}
              </div>
            </div>
            <button 
              onclick={() => { deleteAppointment(appt.id); showDayModal = false; }} 
              class="text-[#ADC9CD] hover:text-red-400 transition-colors p-2 hover:bg-red-950/20 rounded-xl"
            >
              <Trash2 size={18} />
            </button>
          </div>
        {/each}
      </div>

      <div class="p-6 bg-black/20 border-t border-white/10">
        <button 
          onclick={() => { showDayModal = false; openModal(selectedDate); }}
          class="w-full btn-primary py-4 rounded-2xl flex items-center justify-center space-x-3 text-sm font-black uppercase tracking-widest"
        >
          <Plus size={20} />
          <span>Agregar otra cita</span>
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  @reference "../app.css";
  .input-field {
    @apply w-full bg-black/40 border-white/10 text-white p-4 rounded-2xl focus:border-dent-kelly focus:ring-1 focus:ring-dent-kelly transition-all placeholder-white/20 text-sm;
  }
</style>
