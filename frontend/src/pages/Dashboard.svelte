<script lang="ts">
  import { onMount } from 'svelte';
  import { link } from 'svelte-spa-router';
  import { api } from '../lib/api';
  import { auth } from '../lib/stores/auth';
  import { Users, Calendar, CreditCard, Clock, ChevronRight } from 'lucide-svelte';
  import dayjs from 'dayjs';
  import 'dayjs/locale/es';

  dayjs.locale('es');

  let stats = $state({
    patients: 0,
    appointmentsToday: 0,
    pendingPayments: 0
  });
  let allAppointments = $state<any[]>([]);
  let locationFilter = $state('Ambas');
  
  let filteredAppointments = $derived.by(() => {
    if (locationFilter === 'Ambas') return allAppointments.slice(0, 5);
    return allAppointments.filter(a => a.location === locationFilter).slice(0, 5);
  });
  
  let loading = $state(true);

  const statusStyles: any = {
    'pendiente': 'bg-amber-500/10 text-amber-500 border-amber-500/20',
    'atendido': 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
    'cancelado': 'bg-rose-500/10 text-rose-500 border-rose-500/20'
  };

  onMount(async () => {
    try {
      const patients = await api.patients.list();
      const today = dayjs().format('YYYY-MM-DD');
      const startOfDay = dayjs().startOf('day').format('YYYY-MM-DD[T]00:00:00');
      const endOfDay = dayjs().endOf('day').format('YYYY-MM-DD[T]23:59:59');
      
      const appointments = await api.appointments.list(startOfDay, endOfDay);
      
      stats.patients = patients.length;
      stats.appointmentsToday = appointments.length;
      allAppointments = appointments;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
    <div>
      <h1 class="text-4xl font-black text-white uppercase tracking-tighter">Bienvenido, {$auth.user?.full_name || $auth.user?.username}</h1>
      <p class="text-[#ADC9CD] font-medium italic">Resumen clínico de hoy, {dayjs().format('D [de] MMMM, YYYY')}</p>
    </div>
  </div>

  <!-- Stats Grid -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div class="card flex items-center space-x-4 border-l-4 border-dent-kelly">
      <div class="p-4 bg-dent-kelly/10 rounded-2xl text-dent-kelly shadow-inner">
        <Users size={28} />
      </div>
      <div>
        <p class="text-xs text-[#ADC9CD] font-bold uppercase tracking-widest">Pacientes</p>
        <p class="text-3xl font-black text-white tracking-tighter uppercase">{stats.patients}</p>
      </div>
    </div>

    <div class="card flex items-center space-x-4 border-l-4 border-dent-mint">
      <div class="p-4 bg-dent-mint/10 rounded-2xl text-dent-mint shadow-inner">
        <Calendar size={28} />
      </div>
      <div>
        <p class="text-xs text-[#ADC9CD] font-bold uppercase tracking-widest">Citas Hoy</p>
        <p class="text-3xl font-black text-white tracking-tighter uppercase">{stats.appointmentsToday}</p>
      </div>
    </div>

    <div class="card flex items-center space-x-4 border-l-4 border-[#4ade80]">
      <div class="p-4 bg-[#4ade80]/10 rounded-2xl text-[#4ade80] shadow-inner">
        <CreditCard size={28} />
      </div>
      <div>
        <p class="text-xs text-[#ADC9CD] font-bold uppercase tracking-widest">Actividad</p>
        <p class="text-lg font-black text-white uppercase tracking-tighter">Finanzas</p>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Today's Appointments -->
    <div class="card bg-[#013B44] border-white/10 flex flex-col">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-black text-white flex items-center space-x-2 uppercase tracking-tight">
          <Clock size={24} class="text-dent-kelly" />
          <span>Agenda Próxima</span>
        </h2>
        <a href="/appointments" use:link class="text-dent-kelly text-sm font-black hover:text-white transition-colors uppercase italic tracking-widest">Ver Todo</a>
      </div>

      <div class="flex items-center p-1 bg-black/20 rounded-xl mb-6">
        <button 
          onclick={() => locationFilter = 'Ambas'}
          class="flex-1 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all {locationFilter === 'Ambas' ? 'bg-dent-kelly text-white shadow-md' : 'text-white/40 hover:text-white'}"
        >Ambas</button>
        <button 
          onclick={() => locationFilter = 'Oaxaca'}
          class="flex-1 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all {locationFilter === 'Oaxaca' ? 'bg-dent-kelly text-white shadow-md' : 'text-white/40 hover:text-white'}"
        >Oaxaca</button>
        <button 
          onclick={() => locationFilter = 'Miahuatlán'}
          class="flex-1 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all {locationFilter === 'Miahuatlán' ? 'bg-dent-kelly text-white shadow-md' : 'text-white/40 hover:text-white'}"
        >Miahua.</button>
      </div>

      {#if loading}
        <div class="space-y-4">
          <div class="h-16 bg-white/5 animate-pulse rounded-2xl"></div>
          <div class="h-16 bg-white/5 animate-pulse rounded-2xl"></div>
        </div>
      {:else if filteredAppointments.length === 0}
        <div class="flex flex-col items-center justify-center py-8 opacity-50">
          <Calendar size={48} class="mb-4 text-[#ADC9CD]" />
          <p class="font-bold text-sm tracking-widest uppercase text-center">No hay citas para {locationFilter.toLowerCase()} hoy</p>
        </div>
      {:else}
        <div class="space-y-3 flex-1 overflow-y-auto">
          {#each filteredAppointments as appt}
            <div class="flex items-center justify-between p-5 bg-white/5 hover:bg-white/10 rounded-3xl transition-all border border-transparent hover:border-white/10 group">
              <div class="flex items-center space-x-4">
                <div class="bg-dent-kelly text-white text-xs font-black px-4 py-2 rounded-xl shadow-lg shadow-black/20">
                  {dayjs(appt.date_time).format('HH:mm')}
                </div>
                <div>
                  <p class="font-black text-white text-lg tracking-tight uppercase">{appt.patient?.first_name} {appt.patient?.last_name}</p>
                  <p class="text-xs text-[#ADC9CD] truncate max-w-[200px] font-medium italic opacity-80">{appt.description || 'Consulta Dental'}</p>
                  <div class="flex items-center space-x-2 mt-1">
                    <span class="px-2 py-0.5 rounded-lg text-[8px] font-black uppercase tracking-widest bg-black/30 border border-white/5 text-[#ADC9CD]">
                      {appt.location}
                    </span>
                    <span class="px-2 py-0.5 rounded-lg text-[8px] font-black uppercase tracking-widest border {statusStyles[appt.status]}">
                      {appt.status}
                    </span>
                  </div>
                  <p class="text-[10px] font-black uppercase tracking-widest mt-1 {appt.patient?.doctor ? 'text-dent-mint' : 'text-rose-400 animate-pulse'}">
                    {#if appt.patient?.doctor}
                      Dr(a). {appt.patient.doctor.full_name}
                    {:else}
                      Debe tener doctor asignado
                    {/if}
                  </p>
                </div>
              </div>
              <ChevronRight size={20} class="text-white/20 group-hover:text-dent-kelly transition-colors" />
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Quick Actions -->
    <div class="card bg-[#013B44] border-white/10 relative overflow-hidden flex flex-col justify-center py-10">
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-dent-kelly/10 rounded-full blur-[100px]"></div>
      <h2 class="text-2xl font-black text-white mb-8 uppercase tracking-tighter text-center">Acciones Rápidas</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 relative z-10 px-4">
        <a href="/patients" use:link class="p-8 bg-white/5 rounded-[2.5rem] border border-white/10 flex flex-col items-center text-center space-y-4 hover:bg-white/10 transition-all hover:scale-105 shadow-2xl">
          <div class="p-4 bg-dent-kelly text-white rounded-2xl shadow-xl shadow-black/20">
            <Users size={28} />
          </div>
          <span class="font-black text-white uppercase text-xs tracking-[0.2em]">Nuevo Paciente</span>
        </a>
        <a href="/appointments" use:link class="p-8 bg-white/5 rounded-[2.5rem] border border-white/10 flex flex-col items-center text-center space-y-4 hover:bg-white/10 transition-all hover:scale-105 shadow-2xl">
          <div class="p-4 bg-dent-forest text-white rounded-2xl shadow-xl shadow-black/20">
            <Calendar size={28} />
          </div>
          <span class="font-black text-white uppercase text-xs tracking-[0.2em]">Agendar Cita</span>
        </a>
      </div>
      
      <div class="mt-12 p-8 bg-black/10 rounded-[2.5rem] border border-white/5 mx-4">
        <h3 class="text-[10px] font-black text-dent-kelly uppercase tracking-[0.3em] mb-3 text-center">Inspiración Diaria</h3>
        <p class="text-sm text-[#C2D7DA] italic leading-relaxed text-center">"Tu talento y pasión cambian vidas a través de sonrisas."</p>
      </div>
    </div>
  </div>
</div>
