<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { api } from '../lib/api';
  import { 
    Calendar as CalendarIcon, 
    Plus, 
    ChevronLeft, 
    ChevronRight, 
    X, 
    Trash2, 
    Clock, 
    CalendarDays,
    Settings,
    User,
    CheckCircle2,
    AlertCircle,
    Lock,
    Unlock,
    MapPin,
    RotateCcw
  } from 'lucide-svelte';
  import dayjs from 'dayjs';
  import 'dayjs/locale/es';
  import { fade, fly, slide } from 'svelte/transition';
  import { uiStore } from '../lib/ui.svelte';
  import ConfirmModal from '../lib/components/ConfirmModal.svelte';

  dayjs.locale('es');

  // State
  let appointments = $state<any[]>([]);
  let patients = $state<any[]>([]);
  let loading = $state(true);
  
  // Modals
  let showAppointmentModal = $state(false);
  let showDayDetailModal = $state(false);
  let showDeleteModal = $state(false);
  let appointmentToDelete = $state<any>(null);
  
  // Selection
  let currentMonth = $state(dayjs());
  let selectedDate = $state(dayjs());
  let activeTab = $state<'citas' | 'disponibilidad'>('citas');
  let selectedLocation = $state('Oaxaca');
  
  // Forms
  let appointmentForm = $state({
    patient_id: '',
    date: '',
    time: '',
    description: '',
    treatment_details: '',
    cost: 0,
    location: 'Oaxaca',
    status: 'pendiente'
  });

  let dayAvailability = $state({
    is_blocked: false,
    intervals: [{ start_time: '09:00', end_time: '14:00', slot_duration: 30 }]
  });

  let slots = $state<any[]>([]);
  let loadingSlots = $state(false);
  let savingAvailability = $state(false);
  let creatingAppointment = $state(false);

  // Derived: Citas del día seleccionado para el modal
  const selectedDayAppointments = $derived.by(() => {
    if (!selectedDate) return [];
    const dateStr = selectedDate.format('YYYY-MM-DD');
    return appointments.filter(a => dayjs(a.date_time).format('YYYY-MM-DD') === dateStr);
  });

  const slotOptions = [
    { label: '15 min', value: 15 },
    { label: '20 min', value: 20 },
    { label: '30 min', value: 30 },
    { label: '45 min', value: 45 },
    { label: '1 hora', value: 60 },
    { label: '1:30 hrs', value: 90 },
    { label: '2 horas', value: 120 },
    { label: '3 horas', value: 180 }
  ];


  // Constants
  const MAX_MONTHS_ADVANCE = 3;

  onMount(async () => {
    await Promise.all([loadAppointments(), loadPatients()]);
  });

  async function loadAppointments() {
    loading = true;
    try {
      // Usar formato local para evitar desplazamientos de zona horaria con toISOString()
      const start = currentMonth.startOf('month').format('YYYY-MM-DD[T]00:00:00');
      const end = currentMonth.endOf('month').format('YYYY-MM-DD[T]23:59:59');
      const data = await api.appointments.list(start, end, selectedLocation);
      // Asignar una nueva referencia para asegurar reactividad en Svelte 5
      appointments = [...data];
    } catch (e) {
      console.error("Error al cargar citas:", e);
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

  async function loadSlots(date: string, location: string) {
    if (!date || !location) return;
    loadingSlots = true;
    try {
      slots = await api.availability.getSlots(date, location);
    } catch (e) {
      console.error(e);
      slots = [];
    } finally {
      loadingSlots = false;
    }
  }

  async function loadDayAvailability(date: string, location: string) {
    try {
      const overrides = await api.availability.getOverrides(date, location);
      if (overrides.length > 0) {
        dayAvailability.is_blocked = overrides[0].is_blocked;
        dayAvailability.intervals = overrides
          .filter((o: any) => !o.is_blocked)
          .map((o: any) => ({ 
            start_time: o.start_time, 
            end_time: o.end_time, 
            slot_duration: o.slot_duration || 30 
          }));
        
        if (dayAvailability.intervals.length === 0 && !dayAvailability.is_blocked) {
          dayAvailability.intervals = [{ start_time: '09:00', end_time: '14:00', slot_duration: 30 }];
        }
      } else {
        dayAvailability.is_blocked = false;
        dayAvailability.intervals = [{ start_time: '09:00', end_time: '14:00', slot_duration: 30 }];
      }
    } catch (e) {
      console.error(e);
    }
  }

  // Calendar Helpers
  const daysInMonth = $derived.by(() => {
    const days = [];
    const startOfMonth = currentMonth.startOf('month');
    const endOfMonth = currentMonth.endOf('month');
    
    // Padding for first week
    for (let i = 0; i < startOfMonth.day(); i++) {
      days.push(null);
    }
    
    // Days of current month
    for (let i = 1; i <= endOfMonth.date(); i++) {
      days.push(startOfMonth.date(i));
    }
    
    return days;
  });

  function getAppointmentsForDay(date: dayjs.Dayjs) {
    const dateStr = date.format('YYYY-MM-DD');
    return appointments.filter(a => dayjs(a.date_time).format('YYYY-MM-DD') === dateStr);
  }

  // Actions
  function openDayDetail(date: dayjs.Dayjs) {
    if (!date) return;
    selectedDate = date;
    activeTab = 'citas';
    showDayDetailModal = true;
    loadDayAvailability(date.format('YYYY-MM-DD'), selectedLocation);
  }

  function openNewAppointment(date: dayjs.Dayjs | null = null) {
    const targetDate = date || selectedDate;
    const dateStr = targetDate.format('YYYY-MM-DD');
    
    appointmentForm = {
      patient_id: '',
      date: dateStr,
      time: '',
      description: '',
      treatment_details: '',
      cost: 0,
      location: selectedLocation,
      status: 'pendiente'
    };
    
    loadSlots(dateStr, selectedLocation);
    showAppointmentModal = true;
  }

  async function handleAppointmentSubmit() {
    if (!appointmentForm.time || !appointmentForm.patient_id) {
      uiStore.addToast('Por favor completa los campos requeridos.', 'warning');
      return;
    }

    creatingAppointment = true;
    try {
      const dateTime = `${appointmentForm.date}T${appointmentForm.time}:00`;
      await api.appointments.create({
        patient_id: parseInt(appointmentForm.patient_id),
        date_time: dateTime,
        description: appointmentForm.description,
        treatment_details: appointmentForm.treatment_details,
        cost: appointmentForm.cost,
        location: appointmentForm.location,
        status: appointmentForm.status
      });
      
      // Cerramos los modales
      showAppointmentModal = false;
      showDayDetailModal = false; 
      
      uiStore.addToast('Cita creada exitosamente', 'success');
      
      // Pequeño delay para asegurar que la DB haya procesado todo y forzar actualización
      setTimeout(async () => {
        await loadAppointments();
      }, 100);

    } catch (e: any) {
      const msg = e.detail && Array.isArray(e.detail) 
        ? e.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join(', ')
        : (e.detail || e.message || 'Error desconocido');
      uiStore.addToast('Error: ' + msg, 'error');
    } finally {
      creatingAppointment = false;
    }
  }

  async function saveAvailability() {
    const dateStr = selectedDate.format('YYYY-MM-DD');
    
    // Verificar límite de 3 meses
    if (selectedDate.isAfter(dayjs().add(MAX_MONTHS_ADVANCE, 'month'))) {
      uiStore.addToast(`Límite de ${MAX_MONTHS_ADVANCE} meses superado`, 'error');
      return;
    }

    // 1. Validar que la hora de inicio sea anterior a la de fin y divisibilidad exacta
    for (const interval of dayAvailability.intervals) {
      const start = dayjs(`2000-01-01 ${interval.start_time}`);
      const end = dayjs(`2000-01-01 ${interval.end_time}`);
      
      if (!start.isBefore(end)) {
        uiStore.addToast(`Intervalo inválido: ${interval.start_time} - ${interval.end_time}`, 'error');
        return;
      }

      const diffMinutes = end.diff(start, 'minute');
      if (diffMinutes % interval.slot_duration !== 0) {
        uiStore.addToast(`${interval.start_time}-${interval.end_time} no divide exacto en ${interval.slot_duration}m`, 'error');
        return;
      }
    }

    // 2. Filtrar duplicados exactos
    const uniqueIntervals = dayAvailability.intervals.filter((interval, index, self) =>
      index === self.findIndex((t) => (
        t.start_time === interval.start_time && t.end_time === interval.end_time
      ))
    );

    // 3. Validar solapamientos (Overlap)
    // Ordenamos por hora de inicio para facilitar la comparación
    const sorted = [...uniqueIntervals].sort((a, b) => a.start_time.localeCompare(b.start_time));
    
    for (let i = 0; i < sorted.length - 1; i++) {
      const current = sorted[i];
      const next = sorted[i+1];
      
      if (next.start_time < current.end_time) {
        uiStore.addToast(`Conflicto entre ${current.start_time} y ${next.start_time}`, 'error');
        return;
      }
    }

    savingAvailability = true;
    try {
      await api.availability.updateDayAvailability({
        date: dateStr,
        is_blocked: dayAvailability.is_blocked,
        intervals: uniqueIntervals
      }, selectedLocation);
      // Actualizar localmente para reflejar la limpieza de duplicados
      dayAvailability.intervals = uniqueIntervals;
      
      uiStore.addToast('Agenda Actualizada Exitosamente', 'success');
      await loadSlots(dateStr, selectedLocation);
    } catch (e: any) {
      const msg = e.detail && Array.isArray(e.detail) 
        ? e.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join(', ')
        : (e.detail || e.message || 'Error desconocido');
      uiStore.addToast('Error al guardar: ' + msg, 'error');
    } finally {
      savingAvailability = false;
    }
  }

  function addInterval() {
    dayAvailability.intervals = [...dayAvailability.intervals, { start_time: '15:00', end_time: '18:00', slot_duration: 30 }];
  }

  function removeInterval(index: number) {
    dayAvailability.intervals = dayAvailability.intervals.filter((_, i) => i !== index);
  }

  function confirmDelete(appt: any) {
    appointmentToDelete = appt;
    showDeleteModal = true;
  }

  async function handleDelete() {
    if (!appointmentToDelete) return;
    try {
      await api.appointments.delete(appointmentToDelete.id);
      showDeleteModal = false;
      uiStore.addToast('Cita eliminada', 'success');
      appointmentToDelete = null;
      await loadAppointments();
    } catch (e) {
      uiStore.addToast('Error al eliminar', 'error');
    }
  }

  async function updateStatus(appt: any, newStatus: string) {
    try {
      await api.appointments.update(appt.id, {
        patient_id: appt.patient_id,
        date_time: appt.date_time,
        description: appt.description,
        treatment_details: appt.treatment_details,
        cost: appt.cost,
        location: appt.location,
        status: newStatus
      });
      uiStore.addToast('Estado actualizado', 'success');
      await loadAppointments();
    } catch (e) {
      uiStore.addToast('Error al actualizar estado', 'error');
    }
  }

  const statusStyles: any = {
    'pendiente': 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    'atendido': 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    'cancelado': 'bg-rose-500/10 text-rose-500 border-rose-500/20'
  };

</script>

<div class="min-h-screen bg-[#011B1E] text-white p-4 md:p-8 font-sans">
  <!-- Header -->
  <header class="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6" in:fly={{ y: -20, duration: 600 }}>
    <div>
      <div class="flex items-center space-x-3 mb-2">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-dent-kelly to-dent-blue flex items-center justify-center shadow-lg shadow-dent-kelly/20">
          <CalendarDays class="text-white" size={24} />
        </div>
        <span class="text-xs font-black uppercase tracking-[0.3em] text-dent-kelly">Clínica Dental Lorey</span>
      </div>
      <h1 class="text-5xl font-black uppercase tracking-tighter leading-none italic">Agenda <span class="text-transparent bg-clip-text bg-gradient-to-r from-white to-white/40">Integral</span></h1>
      <p class="text-[#ADC9CD] mt-2 font-medium">Gestión unificada de citas y disponibilidad quirúrgica.</p>
    </div>

    <div class="flex items-center space-x-6">
      <!-- Location Selector -->
      <div class="flex p-1.5 bg-black/40 rounded-[2rem] border border-white/5">
        <button 
          onclick={async () => { selectedLocation = 'Oaxaca'; await loadAppointments(); }}
          class="px-6 py-3 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all {selectedLocation === 'Oaxaca' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
        >Oaxaca</button>
        <button 
          onclick={async () => { selectedLocation = 'Miahuatlán'; await loadAppointments(); }}
          class="px-6 py-3 rounded-[1.5rem] text-[10px] font-black uppercase tracking-widest transition-all {selectedLocation === 'Miahuatlán' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
        >Miahuatlán</button>
      </div>

       <button onclick={() => openNewAppointment()} class="group relative px-8 py-4 bg-dent-kelly rounded-[2rem] overflow-hidden transition-all hover:scale-105 active:scale-95 shadow-xl shadow-dent-kelly/20">
        <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
        <div class="relative flex items-center space-x-3 font-black uppercase tracking-widest text-sm">
          <Plus size={20} />
          <span>Nueva Cita</span>
        </div>
      </button>
    </div>
  </header>

  <!-- Main Calendar -->
  <main class="max-w-7xl mx-auto" in:fade={{ delay: 200, duration: 600 }}>
    <div class="bg-black/40 backdrop-blur-3xl rounded-[3rem] border border-white/5 overflow-hidden shadow-2xl">
      <!-- Calendar Nav -->
      <div class="p-8 border-b border-white/5 flex items-center justify-between bg-white/5">
        <div class="flex items-center space-x-6">
          <h2 class="text-3xl font-black capitalize tracking-tighter w-48 italic">
            {currentMonth.format('MMMM YYYY')}
          </h2>
          <div class="flex items-center p-1 bg-black/40 rounded-2xl border border-white/5">
            <button onclick={async () => { currentMonth = currentMonth.subtract(1, 'month'); await loadAppointments(); }} class="p-3 hover:bg-white/5 rounded-xl text-white/60 hover:text-white transition-all">
              <ChevronLeft size={20} />
            </button>
            <button onclick={async () => { currentMonth = dayjs(); await loadAppointments(); }} class="px-6 text-xs font-black uppercase tracking-widest text-dent-kelly hover:text-white transition-colors">
              Hoy
            </button>
            <button onclick={async () => { currentMonth = currentMonth.add(1, 'month'); await loadAppointments(); }} class="p-3 hover:bg-white/5 rounded-xl text-white/60 hover:text-white transition-all">
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
        
        <div class="hidden md:flex items-center space-x-8">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-dent-kelly shadow-[0_0_10px_rgba(0,172,177,0.5)]"></div>
            <span class="text-[10px] font-black uppercase tracking-widest text-white/60">Disponibilidad Activa</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]"></div>
            <span class="text-[10px] font-black uppercase tracking-widest text-white/60">Citas Confirmadas</span>
          </div>
        </div>
      </div>

      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 border-b border-white/5 bg-black/20">
        {#each ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'] as day}
          <div class="py-4 text-[10px] font-black text-[#ADC9CD]/40 uppercase tracking-[0.3em] text-center">
            {day}
          </div>
        {/each}
      </div>

      <div class="grid grid-cols-7 auto-rows-[minmax(140px,1fr)] bg-white/2 gap-px">
        {#each daysInMonth as date}
          <button 
            onclick={(e) => {
              e.preventDefault();
              if (date) openDayDetail(date);
            }}
            class="relative group bg-[#012226]/40 p-3 flex flex-col transition-all hover:bg-white/5 disabled:opacity-20 disabled:cursor-default outline-none focus:ring-2 focus:ring-dent-kelly/50"
            disabled={!date}
          >
            {#if date}
              <div class="flex justify-between items-start mb-3">
                <span class="text-sm font-black {date.isSame(dayjs(), 'day') ? 'bg-dent-kelly text-white w-8 h-8 flex items-center justify-center rounded-xl shadow-lg shadow-dent-kelly/30 scale-110' : 'text-white/40 group-hover:text-white'} transition-all">
                  {date.date()}
                </span>
                
                {#if getAppointmentsForDay(date).length > 0}
                  <div class="flex -space-x-2">
                    {#each getAppointmentsForDay(date).slice(0, 3) as _}
                      <div class="w-5 h-5 rounded-lg border-2 border-[#012226] bg-rose-500 shadow-sm"></div>
                    {/each}
                  </div>
                {/if}
              </div>

              <!-- Day Content -->
              <div class="flex-1 space-y-1.5 overflow-hidden">
                {#each getAppointmentsForDay(date).slice(0, 2) as appt}
                  <div class="flex items-center space-x-2 bg-black/30 p-1.5 rounded-lg border border-white/5 truncate">
                    <span class="text-[9px] font-black text-dent-kelly">{dayjs(appt.date_time).format('HH:mm')}</span>
                    <span class="text-[9px] font-medium text-white/80 truncate uppercase tracking-tighter">{appt.patient?.first_name} {appt.patient?.last_name}</span>
                  </div>
                {/each}
                {#if getAppointmentsForDay(date).length > 2}
                  <p class="text-[8px] font-black text-white/30 uppercase tracking-widest pl-1">
                    + {getAppointmentsForDay(date).length - 2} más
                  </p>
                {/if}
              </div>

              <!-- Hover Action -->
              <div class="absolute bottom-3 left-3 right-3 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                <div class="bg-dent-kelly text-white text-[9px] font-black uppercase tracking-[0.2em] py-2 rounded-xl text-center shadow-xl shadow-dent-kelly/20">
                  Gestionar Día
                </div>
              </div>
            {/if}
          </button>
        {/each}
      </div>
    </div>
  </main>
</div>

<!-- Modal: Detalle del Día (Citas + Agenda) -->
{#if showDayDetailModal}
  <div class="fixed inset-0 z-[200] flex items-center justify-center p-4 md:p-8" in:fade>
    <div class="absolute inset-0 bg-black/90 backdrop-blur-xl" role="presentation" onclick={() => showDayDetailModal = false}></div>
    
    <div class="relative bg-[#012B2F] w-full max-w-5xl h-[85vh] rounded-[3.5rem] border border-white/10 shadow-2xl flex flex-col overflow-hidden" in:fly={{ y: 40, duration: 500 }}>
      <!-- Modal Header -->
      <div class="p-8 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6 bg-white/2">
        <div class="flex items-center space-x-5">
          <div class="w-16 h-16 rounded-[1.5rem] bg-dent-kelly/10 border border-dent-kelly/30 flex flex-col items-center justify-center">
            <span class="text-2xl font-black text-dent-kelly leading-none">{selectedDate.date()}</span>
            <span class="text-[8px] font-black uppercase tracking-widest text-dent-kelly/60">{selectedDate.format('MMM')}</span>
          </div>
          <div>
            <h2 class="text-3xl font-black uppercase tracking-tighter italic">{selectedDate.format('dddd, D [de] MMMM')}</h2>
            <div class="flex items-center space-x-4 mt-1">
               <div class="flex items-center space-x-1.5 px-3 py-1 bg-dent-kelly/10 border border-dent-kelly/30 rounded-lg">
                  <MapPin size={12} class="text-dent-kelly" />
                  <span class="text-[10px] font-black uppercase tracking-widest text-dent-kelly">Sucursal {selectedLocation}</span>
               </div>
               <div class="flex items-center space-x-1.5">
                  <Clock size={12} class="text-[#ADC9CD]" />
                  <span class="text-[10px] font-black uppercase tracking-widest text-[#ADC9CD]">{selectedDayAppointments.length} Citas Programadas</span>
               </div>
            </div>
          </div>
        </div>

        <div class="flex items-center p-1.5 bg-black/40 rounded-2xl border border-white/5">
          <button 
            onclick={() => activeTab = 'citas'}
            class="px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all {activeTab === 'citas' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
          >
            Citas
          </button>
          <button 
            onclick={() => activeTab = 'disponibilidad'}
            class="px-6 py-3 rounded-xl text-xs font-black uppercase tracking-widest transition-all {activeTab === 'disponibilidad' ? 'bg-dent-kelly text-white shadow-lg' : 'text-white/40 hover:text-white'}"
          >
            Agenda / Disponibilidad
          </button>
        </div>

        <button onclick={() => showDayDetailModal = false} class="p-3 hover:bg-white/5 rounded-full text-white/40 hover:text-white transition-all">
          <X size={24} />
        </button>
      </div>

      <!-- Modal Content -->
      <div class="flex-1 overflow-hidden flex flex-col">
        {#if activeTab === 'citas'}
          <div class="p-8 flex-1 overflow-y-auto space-y-4" in:fade>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xs font-black uppercase tracking-[0.3em] text-[#ADC9CD]">Listado de Pacientes</h3>
              <button onclick={() => openNewAppointment(selectedDate)} class="flex items-center space-x-2 text-dent-kelly hover:text-white transition-colors">
                <Plus size={16} />
                <span class="text-[10px] font-black uppercase tracking-widest">Añadir Cita</span>
              </button>
            </div>

            {#if selectedDayAppointments.length === 0}
              <div class="flex flex-col items-center justify-center py-20 text-center space-y-4 opacity-30">
                <CalendarIcon size={64} />
                <p class="font-bold uppercase tracking-widest">No hay citas para este día</p>
              </div>
            {:else}
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {#each selectedDayAppointments as appt}
                  <div class="bg-black/20 rounded-[2rem] p-6 border border-white/5 hover:border-white/10 transition-all group flex items-start space-x-5">
                    <div class="w-14 h-14 rounded-2xl bg-dent-kelly/10 flex flex-col items-center justify-center border border-dent-kelly/20">
                      <span class="text-sm font-black text-dent-kelly">{dayjs(appt.date_time).format('HH:mm')}</span>
                    </div>
                    <div class="flex-1">
                      <div class="flex items-center justify-between">
                        <h4 class="text-lg font-black uppercase tracking-tight text-white">{appt.patient?.first_name} {appt.patient?.last_name}</h4>
                        <div class="flex items-center space-x-3">
                          <span class="px-3 py-1 rounded-full text-[8px] font-black uppercase tracking-widest border {statusStyles[appt.status]}">
                            {appt.status}
                          </span>
                          <span class="text-[9px] font-black uppercase tracking-[0.2em] {appt.patient?.doctor ? 'text-dent-kelly' : 'text-rose-500 animate-pulse'}">
                            {#if appt.patient?.doctor}
                              Dr(a). {appt.patient.doctor.full_name}
                            {:else}
                              ⚠️ Sin doctor asignado
                            {/if}
                          </span>
                        </div>
                      </div>
                      <div class="flex items-center space-x-2 mt-1">
                        <MapPin size={10} class="text-dent-kelly" />
                        <span class="text-[10px] font-black uppercase tracking-widest text-[#ADC9CD]">{appt.location || 'Sucursal N/A'}</span>
                        <span class="text-white/20">|</span>
                        <span class="text-[10px] font-black uppercase tracking-widest text-white">${appt.cost?.toLocaleString() || '0'}</span>
                      </div>
                      <p class="text-sm text-[#ADC9CD] mt-2 font-medium italic">"{appt.description || 'Consulta general'}"</p>
                      {#if appt.treatment_details}
                        <p class="text-[10px] text-white/40 mt-1 line-clamp-1">{appt.treatment_details}</p>
                      {/if}
                      
                      <div class="flex items-center space-x-3 mt-4">
                        <button onclick={() => updateStatus(appt, 'atendido')} class="p-2 hover:bg-emerald-500/10 rounded-lg text-white/20 hover:text-emerald-500 transition-all" title="Marcar como atendido">
                          <CheckCircle2 size={18} />
                        </button>
                        <button onclick={() => updateStatus(appt, 'cancelado')} class="p-2 hover:bg-rose-500/10 rounded-lg text-white/20 hover:text-rose-500 transition-all" title="Cancelar cita">
                          <X size={18} />
                        </button>
                        <button onclick={() => updateStatus(appt, 'pendiente')} class="p-2 hover:bg-amber-500/10 rounded-lg text-white/20 hover:text-amber-500 transition-all" title="Regresar a pendiente">
                          <RotateCcw size={18} />
                        </button>
                        <div class="flex-1"></div>
                        <button onclick={() => confirmDelete(appt)} class="p-2 hover:bg-rose-500/10 rounded-lg text-white/20 hover:text-rose-500 transition-all">
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {:else}
          <div class="p-8 flex-1 overflow-y-auto" in:fade>
            <div class="max-w-2xl mx-auto space-y-10">
              <div class="bg-black/30 rounded-[2.5rem] p-8 border border-white/5 shadow-inner">
                <div class="flex items-center justify-between mb-8">
                  <div class="flex items-center space-x-3">
                    <Settings class="text-dent-kelly" size={20} />
                    <h3 class="text-xl font-black uppercase tracking-tighter">Control de Disponibilidad</h3>
                  </div>
                  
                  <button 
                    onclick={() => dayAvailability.is_blocked = !dayAvailability.is_blocked}
                    class="flex items-center space-x-3 px-6 py-3 rounded-2xl border transition-all {dayAvailability.is_blocked ? 'bg-rose-500/20 border-rose-500 text-rose-500' : 'bg-dent-kelly/10 border-dent-kelly/20 text-dent-kelly'}"
                  >
                    {#if dayAvailability.is_blocked}
                      <Lock size={18} />
                      <span class="text-xs font-black uppercase tracking-widest">Día Bloqueado</span>
                    {:else}
                      <Unlock size={18} />
                      <span class="text-xs font-black uppercase tracking-widest">Abierto a Citas</span>
                    {/if}
                  </button>
                </div>

                {#if !dayAvailability.is_blocked}
                  <div class="space-y-6" in:slide>
                    <div class="flex items-center justify-between">
                       <span class="text-[10px] font-black uppercase tracking-[0.2em] text-[#ADC9CD]">Intervalos de Atención</span>
                       <button onclick={addInterval} class="text-xs font-black text-dent-kelly flex items-center space-x-1 hover:text-white transition-colors">
                          <Plus size={14} />
                          <span>Agregar Bloque</span>
                       </button>
                    </div>
                    
                    <div class="space-y-3">
                      {#each dayAvailability.intervals as interval, idx}
                        <div class="flex items-center space-x-4 bg-white/5 p-4 rounded-2xl border border-white/5 transition-all hover:border-dent-kelly/30">
                          <div class="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="space-y-1">
                              <span class="text-[8px] font-black uppercase text-white/30 ml-2">Inicio</span>
                              <input type="time" bind:value={interval.start_time} class="w-full bg-black/40 border-none text-white rounded-xl p-3 text-sm focus:ring-1 focus:ring-dent-kelly transition-all" />
                            </div>
                            <div class="space-y-1">
                              <span class="text-[8px] font-black uppercase text-white/30 ml-2">Fin</span>
                              <input type="time" bind:value={interval.end_time} class="w-full bg-black/40 border-none text-white rounded-xl p-3 text-sm focus:ring-1 focus:ring-dent-kelly transition-all" />
                            </div>
                            <div class="space-y-1">
                              <span class="text-[8px] font-black uppercase text-white/30 ml-2">Intervalos De</span>
                              <select bind:value={interval.slot_duration} class="w-full bg-black/40 border-none text-white rounded-xl p-3 text-sm focus:ring-1 focus:ring-dent-kelly transition-all appearance-none">
                                {#each slotOptions as opt}
                                  <option value={opt.value}>{opt.label}</option>
                                {/each}
                              </select>
                            </div>
                          </div>
                          <button 
                            onclick={() => removeInterval(idx)} 
                            class="p-4 text-rose-500/50 hover:text-rose-500 hover:bg-rose-500/10 rounded-xl transition-all"
                            title="Eliminar este bloque"
                          >
                            <Trash2 size={20} />
                          </button>
                        </div>
                      {/each}
                    </div>
                  </div>
                {:else}
                  <div class="py-12 text-center space-y-4" in:slide>
                     <AlertCircle size={48} class="mx-auto text-rose-500/50" />
                     <p class="text-[#ADC9CD] font-medium italic">El consultorio permanecerá cerrado este día. Ningún paciente podrá agendar citas online.</p>
                  </div>
                {/if}

                <div class="mt-12 pt-8 border-t border-white/5 relative">

                   <button 
                    onclick={saveAvailability} 
                    disabled={savingAvailability}
                    class="w-full py-5 bg-dent-kelly rounded-2xl font-black uppercase tracking-[0.3em] text-sm shadow-xl shadow-dent-kelly/20 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                   >
                    {savingAvailability ? 'Guardando...' : 'Aplicar Cambios a la Agenda'}
                   </button>
                   <p class="text-center text-[10px] text-white/20 mt-4 font-bold uppercase tracking-widest">
                    * Modificación válida para los próximos {MAX_MONTHS_ADVANCE} meses.
                   </p>
                </div>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- Modal: Nueva Cita (Concepto minimalista) -->
{#if showAppointmentModal}
  <div class="fixed inset-0 z-[250] flex items-center justify-center p-4" in:fade>
    <div class="absolute inset-0 bg-black/95 backdrop-blur-2xl" role="presentation" onclick={() => showAppointmentModal = false}></div>
    
    <div class="relative bg-[#013B44] w-full max-w-2xl rounded-[3rem] border border-white/10 shadow-2xl overflow-hidden" in:fly={{ y: 20, duration: 400 }}>
       <div class="p-10">
          <div class="flex justify-between items-center mb-10">
            <div>
              <h2 class="text-3xl font-black uppercase tracking-tighter leading-tight italic">Nueva Cita</h2>
              <div class="flex items-center space-x-3 mt-1">
                <p class="text-dent-kelly text-[10px] font-black uppercase tracking-widest">Para el {dayjs(appointmentForm.date).format('D [de] MMMM')}</p>
                <span class="w-1 h-1 bg-dent-kelly/40 rounded-full"></span>
                <div class="flex items-center space-x-1 text-white/40">
                  <MapPin size={10} />
                  <span class="text-[9px] font-black uppercase tracking-widest">{appointmentForm.location}</span>
                </div>
              </div>
            </div>
            <button onclick={() => showAppointmentModal = false} class="p-2 hover:bg-white/5 rounded-full text-white/40">
              <X size={28} />
            </button>
          </div>

          <form onsubmit={(e) => { e.preventDefault(); handleAppointmentSubmit(); }} class="space-y-8">
            <div class="grid md:grid-cols-2 gap-8">
              <div class="space-y-6">
                <div>
                  <label for="patient_select" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Paciente</label>
                  <div class="relative">
                    <User class="absolute left-4 top-1/2 -translate-y-1/2 text-white/20" size={18} />
                    <select id="patient_select" bind:value={appointmentForm.patient_id} required class="w-full bg-black/40 border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-sm focus:ring-2 focus:ring-dent-kelly outline-none appearance-none transition-all">
                      <option value="">Selecciona Paciente</option>
                      {#each patients as p}
                        <option value={p.id}>{p.first_name} {p.last_name}</option>
                      {/each}
                    </select>
                  </div>
                </div>

                <div>
                  <label for="location_select" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Sucursal</label>
                  <div class="flex p-1 bg-black/40 rounded-2xl border border-white/5 mb-6">
                    <button 
                      type="button"
                      onclick={() => { appointmentForm.location = 'Oaxaca'; loadSlots(appointmentForm.date, 'Oaxaca'); }}
                      class="flex-1 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all {appointmentForm.location === 'Oaxaca' ? 'bg-dent-kelly text-white' : 'text-white/40'}"
                    >Oaxaca</button>
                    <button 
                      type="button"
                      onclick={() => { appointmentForm.location = 'Miahuatlán'; loadSlots(appointmentForm.date, 'Miahuatlán'); }}
                      class="flex-1 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all {appointmentForm.location === 'Miahuatlán' ? 'bg-dent-kelly text-white' : 'text-white/40'}"
                    >Miahuatlán</button>
                  </div>
                </div>

                <div>
                  <label for="appt_desc" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Motivo de Consulta</label>
                  <input id="appt_desc" type="text" bind:value={appointmentForm.description} class="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm focus:ring-2 focus:ring-dent-kelly outline-none placeholder:text-white/10" placeholder="Ej. Revisión general" />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="appt_treatment" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Tratamiento Realizado</label>
                    <input id="appt_treatment" type="text" bind:value={appointmentForm.treatment_details} class="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm focus:ring-2 focus:ring-dent-kelly outline-none" placeholder="Lo que se le hizo..." />
                  </div>
                  <div>
                    <label for="appt_cost" class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Costo ($)</label>
                    <input id="appt_cost" type="number" step="0.01" bind:value={appointmentForm.cost} class="w-full bg-black/40 border border-white/5 rounded-2xl p-4 text-sm focus:ring-2 focus:ring-dent-kelly outline-none" placeholder="0.00" />
                  </div>
                </div>
              </div>

              <div class="space-y-6">
                 <div>
                  <span class="block text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] mb-3">Horario Seleccionado</span>
                  {#if loadingSlots}
                    <div class="flex items-center justify-center h-48 bg-black/20 rounded-2xl">
                       <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-dent-kelly"></div>
                    </div>
                  {:else if slots.length === 0}
                    <div class="flex flex-col items-center justify-center h-48 bg-black/20 rounded-2xl border border-white/5 text-center p-4">
                       <AlertCircle size={24} class="text-rose-500/30 mb-2" />
                       <p class="text-[10px] font-black uppercase tracking-widest text-white/30">Sin horarios disponibles para este día</p>
                    </div>
                  {:else}
                    <div class="grid grid-cols-2 gap-3 h-[260px] overflow-y-auto pr-2 custom-scrollbar">
                      {#each slots as slot}
                        <button 
                          type="button"
                          onclick={() => slot.available && (appointmentForm.time = slot.time)}
                          disabled={!slot.available}
                          class="py-4 rounded-xl border text-xs font-black transition-all
                            {slot.available 
                              ? (appointmentForm.time === slot.time 
                                  ? 'bg-dent-kelly border-dent-kelly text-white shadow-lg' 
                                  : 'bg-white/5 border-white/5 text-white/60 hover:border-dent-kelly/40 hover:text-white')
                              : 'bg-black/20 border-transparent text-white/10 cursor-not-allowed opacity-20'}"
                        >
                          {slot.time}
                        </button>
                      {/each}
                    </div>
                  {/if}
                </div>
              </div>
            </div>

            <div class="flex items-center space-x-4 pt-6">
               <button type="button" onclick={() => showAppointmentModal = false} class="flex-1 py-5 border border-white/10 rounded-[1.5rem] font-black uppercase tracking-widest text-xs text-white/40 hover:bg-white/5 transition-all">Cancelar</button>
               <button 
                type="submit" 
                disabled={creatingAppointment}
                class="flex-[2] py-5 bg-dent-kelly rounded-[1.5rem] font-black uppercase tracking-widest text-xs text-white shadow-xl shadow-dent-kelly/20 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
               >
                {creatingAppointment ? 'Procesando...' : 'Confirmar Cita Médica'}
               </button>
            </div>
          </form>
       </div>
    </div>
  </div>
{/if}

<!-- Custom Delete Confirmation Modal -->
<ConfirmModal 
  show={showDeleteModal}
  title="¿Eliminar Cita?"
  message={`¿Estás seguro de que deseas eliminar la cita de ${appointmentToDelete?.patient?.first_name} ${appointmentToDelete?.patient?.last_name}? Esta acción es irreversible.`}
  confirmText="Confirmar Eliminación"
  onConfirm={handleDelete}
  onCancel={() => showDeleteModal = false}
/>


<style>
  @reference "../app.css";

  :global(body) {
    background-color: #011B1E;
  }

  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(0, 172, 177, 0.3);
    border-radius: 10px;
  }
</style>
