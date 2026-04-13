<script lang="ts">
  import { link } from 'svelte-spa-router';
  import { auth } from '../stores/auth';
  import { Users, Calendar, CreditCard, LayoutDashboard, LogOut, Menu, X, Clock } from 'lucide-svelte';

  let isMenuOpen = false;

  const toggleMenu = () => isMenuOpen = !isMenuOpen;
  const closeMenu = () => isMenuOpen = false;
  const handleLogout = () => { auth.logout(); closeMenu(); };
</script>

<nav class="bg-[#012B33] border-b border-white/10 sticky top-0 z-[50] backdrop-blur-md">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <a href="/" use:link class="flex items-center space-x-2">
          <div class="bg-dent-blue p-1.5 rounded-xl shadow-lg shadow-dent-blue/20">
            <img src="/logo.png" alt="Dental Lorey Logo" class="w-8 h-8 rounded-lg bg-white p-0.5" />
          </div>
          <span class="text-xl font-black tracking-tighter text-white uppercase">Dental Lorey</span>
        </a>
      </div>

      <!-- Desktop Menu -->
      <div class="hidden md:flex items-center space-x-4">
        <a href="/" use:link class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-dent-blue transition-all">
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </a>
        <a href="/patients" use:link class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-dent-blue transition-all">
          <Users size={18} />
          <span>Pacientes</span>
        </a>
        <a href="/appointments" use:link class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-dent-blue transition-all">
          <Calendar size={18} />
          <span>Citas</span>
        </a>
        <a href="/payments" use:link class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-dent-blue transition-all">
          <CreditCard size={18} />
          <span>Pagos</span>
        </a>
        <a href="/availability" use:link class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-slate-300 hover:bg-slate-800 hover:text-dent-blue transition-all">
          <Clock size={18} />
          <span>Agenda</span>
        </a>
        <button on:click={handleLogout} class="flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-bold text-red-400 hover:bg-red-950/30 transition-all">
          <LogOut size={18} />
          <span>Salir</span>
        </button>
      </div>

      <!-- Mobile Menu Button -->
      <div class="md:hidden flex items-center">
        <button on:click={toggleMenu} class="text-slate-300 hover:text-white">
          {#if isMenuOpen}
            <X size={24} />
          {:else}
            <Menu size={24} />
          {/if}
        </button>
      </div>
    </div>
  </div>

  <!-- Mobile Menu -->
  {#if isMenuOpen}
    <div class="md:hidden bg-[#012B33] border-t border-white/10 py-4 px-4 space-y-4 shadow-lg">
      <a href="/" use:link on:click={closeMenu} class="flex items-center space-x-3 text-[#ADC9CD] font-medium hover:text-white transition-colors">
        <LayoutDashboard size={20} />
        <span>Dashboard</span>
      </a>
      <a href="/patients" use:link on:click={closeMenu} class="flex items-center space-x-3 text-[#ADC9CD] font-medium hover:text-white transition-colors">
        <Users size={20} />
        <span>Pacientes</span>
      </a>
      <a href="/appointments" use:link on:click={closeMenu} class="flex items-center space-x-3 text-[#ADC9CD] font-medium hover:text-white transition-colors">
        <Calendar size={20} />
        <span>Citas</span>
      </a>
      <a href="/payments" use:link on:click={closeMenu} class="flex items-center space-x-3 text-[#ADC9CD] font-medium hover:text-white transition-colors">
        <CreditCard size={20} />
        <span>Pagos</span>
      </a>
      <a href="/availability" use:link on:click={closeMenu} class="flex items-center space-x-3 text-[#ADC9CD] font-medium hover:text-white transition-colors">
        <Clock size={20} />
        <span>Agenda</span>
      </a>
      <button on:click={() => { auth.logout(); closeMenu(); }} class="flex items-center space-x-3 text-red-400 font-medium w-full text-left hover:text-red-300 transition-colors">
        <LogOut size={20} />
        <span>Salir</span>
      </button>
    </div>
  {/if}
</nav>
