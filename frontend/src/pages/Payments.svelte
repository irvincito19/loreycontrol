<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../lib/api';
  import { CreditCard, Plus, Search, User, DollarSign, Calendar, X } from 'lucide-svelte';
  import dayjs from 'dayjs';

  let payments: any[] = [];
  let patients: any[] = [];
  let loading = true;
  let showModal = false;

  // Form state
  let paymentForm = {
    patient_id: '',
    amount: '',
    method: 'efectivo',
    description: ''
  };

  onMount(async () => {
    await Promise.all([loadPayments(), loadPatients()]);
  });

  async function loadPayments() {
    loading = true;
    try {
      payments = await api.payments.list();
      payments.sort((a, b) => dayjs(b.date).unix() - dayjs(a.date).unix());
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
  function openModal() {
    paymentForm = { patient_id: '', amount: '', method: 'efectivo', description: '' };
    showModal = true;
  }

  async function handleSubmit() {
    try {
      await api.payments.create({
        ...paymentForm,
        patient_id: parseInt(paymentForm.patient_id),
        amount: parseFloat(paymentForm.amount)
      });
      showModal = false;
      await loadPayments();
      paymentForm = { patient_id: '', amount: '', method: 'efectivo', description: '' };
    } catch (e) {
      alert('Error: ' + e);
    }
  }

  function getPatientName(id: number) {
    const p = patients.find(p => p.id === id);
    return p ? p.name : `ID: ${id}`;
  }

  const methodColors: any = {
    'efectivo': 'bg-green-900/40 text-green-300 border border-green-800/50',
    'tarjeta': 'bg-blue-900/40 text-blue-300 border border-blue-800/50',
    'transferencia': 'bg-purple-900/40 text-purple-300 border border-purple-800/50'
  };

</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
    <div>
      <h1 class="text-3xl font-black text-white uppercase tracking-tight">Control de Pagos</h1>
      <p class="text-[#ADC9CD] font-medium italic">Historial financiero y registro de ingresos de Dental Lorey.</p>
    </div>

    <button on:click={openModal} class="btn-primary flex items-center space-x-2">
      <Plus size={20} />
      <span>Registrar Pago</span>
    </button>

  </div>

  <!-- Summary Cards -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <div class="card bg-[#013B44] border-[#00ACB1]/30 shadow-lg shadow-black/20">
      <p class="text-[10px] text-[#ADC9CD] font-black uppercase tracking-[0.2em] mb-2">Total Cobrado (Mes)</p>
      <p class="text-3xl font-black text-white tracking-tighter">$ {payments.reduce((acc, p) => acc + p.amount, 0).toLocaleString()}</p>
    </div>
  </div>


  <!-- Payments Table -->
  <div class="card p-0 overflow-hidden border-white/10 bg-[#013B44] transition-all shadow-2xl">
    <div class="overflow-x-auto">
      <table class="w-full text-left">
        <thead class="bg-black/20 border-b border-white/5">
          <tr>
            <th class="px-6 py-4 text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest">Fecha</th>
            <th class="px-6 py-4 text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest">Paciente</th>
            <th class="px-6 py-4 text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest">Monto</th>
            <th class="px-6 py-4 text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest">Método</th>
            <th class="px-6 py-4 text-[10px] font-black text-[#ADC9CD] uppercase tracking-widest">Descripción</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-white/5">
          {#if loading}
            {#each Array(5) as _}
              <tr class="animate-pulse">
                <td colspan="5" class="px-6 py-4 h-12 bg-white/5"></td>
              </tr>
            {/each}
          {:else if payments.length === 0}
            <tr>
              <td colspan="5" class="px-6 py-12 text-center text-[#ADC9CD]">No hay pagos registrados aún.</td>
            </tr>
          {:else}
            {#each payments as payment}
              <tr class="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0 group">
                <td class="px-6 py-4 text-sm text-[#ADC9CD] font-medium italic">
                  {dayjs(payment.date).format('DD/MM/YYYY')}
                </td>
                <td class="px-6 py-4 font-black text-white text-lg tracking-tight uppercase">
                  {getPatientName(payment.patient_id)}
                </td>
                <td class="px-6 py-4 font-black text-[#4db6ac] text-xl tracking-tighter">
                  $ {payment.amount.toLocaleString()}
                </td>
                <td class="px-6 py-4">
                  <span class="px-3 py-1 rounded-xl text-[10px] font-black uppercase shadow-lg {methodColors[payment.method]}">
                    {payment.method}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-[#ADC9CD] italic font-medium">
                  {payment.description || '--'}
                </td>
              </tr>
            {/each}
          {/if}
        </tbody>
      </table>
    </div>

  </div>
</div>

<!-- Modal Form -->
{#if showModal}
  <div class="fixed inset-0 bg-black/70 backdrop-blur-md z-[100] flex items-center justify-center p-4">
    <div class="bg-[#014D67] rounded-[2.5rem] w-full max-w-lg shadow-2xl animate-in fade-in zoom-in duration-300 border border-[#00ACB1]">
      <div class="p-6 border-b border-[#00ACB1]/20 flex justify-between items-center">
        <h2 class="text-2xl font-black text-white uppercase tracking-tight">Registrar Nuevo Pago</h2>
        <button on:click={() => showModal = false} class="text-[#ADC9CD] hover:text-white transition-colors">
          <X size={28} />
        </button>
      </div>

      
      <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-4">
        <div>
          <label for="pay-patient" class="block text-sm font-medium text-[#ADC9CD] mb-1">Paciente *</label>
          <select id="pay-patient" bind:value={paymentForm.patient_id} required class="input-field bg-black/20 border-[#00ACB1]/20 text-white">
            <option value="">Selecciona un paciente</option>
            {#each patients as p}
              <option value={p.id}>{p.name}</option>
            {/each}
          </select>
        </div>

        
        <div>
          <label for="pay-amount" class="block text-sm font-medium text-[#ADC9CD] mb-1">Monto ($) *</label>
          <div class="relative">
            <DollarSign class="absolute left-3 top-1/2 -translate-y-1/2 text-[#ADC9CD]" size={18} />
            <input id="pay-amount" type="number" step="0.01" bind:value={paymentForm.amount} required class="input-field pl-10" placeholder="0.00" />
          </div>
        </div>

        <div>
          <label for="pay-method" class="block text-sm font-medium text-[#ADC9CD] mb-1">Método de Pago</label>
          <select id="pay-method" bind:value={paymentForm.method} class="input-field">
            <option value="efectivo">Efectivo</option>
            <option value="tarjeta">Tarjeta</option>
            <option value="transferencia">Transferencia</option>
          </select>
        </div>

        <div>
          <label for="pay-desc" class="block text-sm font-medium text-[#ADC9CD] mb-1">Concepto / Descripción</label>
          <input id="pay-desc" type="text" bind:value={paymentForm.description} class="input-field" placeholder="Menciona el tratamiento..." />
        </div>


        <div class="flex space-x-4 pt-4">
          <button type="button" on:click={() => showModal = false} class="flex-1 px-4 py-2 border border-white/20 rounded-xl text-[#ADC9CD] hover:bg-white/10 font-bold transition-all">
            Cancelar
          </button>
          <button type="submit" class="flex-1 btn-primary">
            Registrar Ingreso
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
