<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { Search, Plus, User, Phone, Mail, MapPin, MoreHorizontal, Edit2, Trash2, X } from 'lucide-svelte';
  import dayjs from 'dayjs';

  let patients: any[] = [];
  let filteredPatients: any[] = [];
  let searchTerm = '';
  let loading = true;
  let showModal = false;
  let editingPatient: any = null;

  // Form state
  let patientForm = {
    name: '',
    phone: '',
    email: '',
    address: '',
    notes: ''
  };

  onMount(loadPatients);

  async function loadPatients() {
    loading = true;
    try {
      patients = await api.patients.list();
      filterPatients();
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  }

  function filterPatients() {
    filteredPatients = patients.filter(p => 
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.phone?.includes(searchTerm)
    );
  }

  $: if (searchTerm !== undefined) filterPatients();

  function openModal(patient: any = null) {
    editingPatient = patient;
    if (patient) {
      patientForm = { ...patient };
    } else {
      patientForm = { name: '', phone: '', email: '', address: '', notes: '' };
    }
    showModal = true;
  }

  async function handleSubmit() {
    try {
      if (editingPatient) {
        await api.patients.update(editingPatient.id, patientForm);
      } else {
        await api.patients.create(patientForm);
      }
      showModal = false;
      await loadPatients();
    } catch (e) {
      alert('Error al guardar: ' + e);
    }
  }

  async function deletePatient(id: number) {
    if (confirm('¿Estás seguro de eliminar este paciente? Esta acción no se puede deshacer.')) {
      try {
        await api.patients.delete(id);
        await loadPatients();
      } catch (e) {
        alert('Error al eliminar: ' + e);
      }
    }
  }
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">

    <div>
      <h1 class="text-4xl font-black text-white uppercase tracking-tighter">Gestión de Pacientes</h1>
      <p class="text-[#ADC9CD] font-medium italic">Base de datos centralizada de Dental Lorey.</p>
    </div>
    <button on:click={() => openModal()} class="btn-primary flex items-center space-x-2 bg-[#00ACB1] hover:bg-[#015D67] text-white">
      <Plus size={20} />
      <span>Nuevo Paciente</span>
    </button>
  </div>


  <!-- Search Bar -->
  <div class="card p-4 bg-[#013B44] border-[#00ACB1]/20">
    <div class="relative">
      <Search class="absolute left-4 top-1/2 -translate-y-1/2 text-[#ADC9CD]" size={20} />
      <input
        type="text"
        bind:value={searchTerm}
        placeholder="Buscar por nombre, email o teléfono..."
        class="input-field pl-12 bg-[#015D67]/20 border-[#00ACB1]/20 text-white placeholder-[#ADC9CD] font-medium"
      />
    </div>
  </div>




  <!-- Patient List -->
  {#if loading && patients.length === 0}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each Array(6) as _}
        <div class="card h-48 animate-pulse bg-[#015D67]/20 border-[#00ACB1]/20"></div>
      {/each}
    </div>


  {:else if filteredPatients.length === 0}
    <div class="card py-16 text-center bg-white/5 border-white/10">
      <div class="bg-black/20 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-4 text-[#ADC9CD] shadow-inner">
        <User size={40} />
      </div>
      <h3 class="text-xl font-black text-white uppercase tracking-tight">No se encontraron pacientes</h3>
      <p class="text-[#ADC9CD] mt-2 italic font-medium">Intenta con otro término de búsqueda o agrega un nuevo paciente.</p>
    </div>



  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each filteredPatients as patient}
        <div class="card hover:bg-white/10 transition-all group relative border-white/5 hover:border-dent-kelly/40 overflow-hidden shadow-2xl bg-[#014D67]">
          <div class="absolute top-4 right-4 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
            <button on:click={() => openModal(patient)} class="p-2.5 text-[#ADC9CD] hover:text-white hover:bg-white/10 rounded-xl transition-all">
              <Edit2 size={18} />
            </button>
            <button on:click={() => deletePatient(patient.id)} class="p-2.5 text-[#ADC9CD] hover:text-red-400 hover:bg-red-950/30 rounded-xl transition-all">
              <Trash2 size={18} />
            </button>
          </div>



          <div class="flex items-center space-x-4 mb-4">
            <div class="w-14 h-14 bg-[#00ACB1] text-white rounded-2xl flex items-center justify-center font-black text-xl shadow-lg shadow-[#00ACB1]/20 uppercase">
              {patient.name.charAt(0)}
            </div>
            <div>
              <h3 class="font-black text-white leading-none text-lg tracking-tight uppercase">{patient.name}</h3>
              <p class="text-[10px] text-[#ADC9CD] mt-1 font-bold uppercase tracking-wider">Desde {dayjs(patient.created_at).format('DD/MM/YYYY')}</p>
            </div>
          </div>


          <div class="space-y-3 text-sm text-[#ADC9CD] font-medium italic">
            {#if patient.phone}
              <div class="flex items-center space-x-3">
                <div class="p-1.5 bg-[#015D67]/40 rounded-lg text-[#00ACB1] shadow-inner">
                  <Phone size={14} />
                </div>
                <span>{patient.phone}</span>
              </div>
            {/if}
            {#if patient.email}
              <div class="flex items-center space-x-3">
                <div class="p-1.5 bg-[#015D67]/40 rounded-lg text-[#00ACB1] shadow-inner">
                  <Mail size={14} />
                </div>
                <span class="truncate">{patient.email}</span>
              </div>
            {/if}
            {#if patient.address}
              <div class="flex items-center space-x-3">
                <div class="p-1.5 bg-[#015D67]/40 rounded-lg text-[#00ACB1] shadow-inner">
                  <MapPin size={14} />
                </div>
                <span class="truncate">{patient.address}</span>
              </div>
            {/if}
          </div>


        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Modal Form -->
{#if showModal}
  <div class="fixed inset-0 bg-black/70 backdrop-blur-md z-[100] flex items-center justify-center p-4">
    <div class="bg-[#014D67] rounded-[2.5rem] w-full max-w-lg shadow-2xl animate-in fade-in zoom-in duration-300 border border-[#00ACB1]">
      <div class="p-6 border-b border-[#00ACB1]/20 flex justify-between items-center">
        <h2 class="text-2xl font-black text-white uppercase tracking-tight">{editingPatient ? 'Editar' : 'Nuevo'} Paciente</h2>
        <button on:click={() => showModal = false} class="text-[#ADC9CD] hover:text-white transition-colors">
          <X size={28} />
        </button>
      </div>


      
      <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-4">
        <div>
          <label for="p-name" class="block text-sm font-medium text-[#ADC9CD] mb-1">Nombre Completo *</label>
          <input id="p-name" type="text" bind:value={patientForm.name} required class="input-field bg-black/20 border-[#00ACB1]/20 text-white" placeholder="Ej. Juan Pérez" />
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="p-phone" class="block text-sm font-medium text-[#ADC9CD] mb-1">Teléfono</label>
            <input id="p-phone" type="tel" bind:value={patientForm.phone} class="input-field" placeholder="(123) 456-7890" />
          </div>
          <div>
            <label for="p-email" class="block text-sm font-medium text-[#ADC9CD] mb-1">Email</label>
            <input id="p-email" type="email" bind:value={patientForm.email} class="input-field" placeholder="juan@correo.com" />
          </div>
        </div>

        <div>
          <label for="p-address" class="block text-sm font-medium text-[#ADC9CD] mb-1">Dirección</label>
          <input id="p-address" type="text" bind:value={patientForm.address} class="input-field" placeholder="Calle #123, Colonia..." />
        </div>

        <div>
          <label for="p-notes" class="block text-sm font-medium text-[#ADC9CD] mb-1">Notas Médicas / Observaciones</label>
          <textarea id="p-notes" bind:value={patientForm.notes} class="input-field h-24 resize-none" placeholder="Alergias, tratamientos previos..."></textarea>
        </div>


        <div class="flex space-x-4 pt-6">
          <button type="button" on:click={() => showModal = false} class="flex-1 px-4 py-4 border border-white/20 rounded-2xl text-[#ADC9CD] hover:bg-white/10 font-bold transition-all">
            Cancelar
          </button>
          <button type="submit" class="flex-1 btn-primary py-4 rounded-2xl">
            {editingPatient ? 'Guardar Cambios' : 'Crear Paciente'}
          </button>
        </div>


      </form>
    </div>
  </div>
{/if}
