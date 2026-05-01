<script lang="ts">
  import { auth } from '../lib/stores/auth';
  import { push } from 'svelte-spa-router';
  import { LogIn } from 'lucide-svelte';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  async function handleLogin() {
    error = '';
    loading = true;
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      await auth.login(formData);
      push('/');
    } catch (e: any) {
      error = e.message || 'Error al iniciar sesión';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center px-4 bg-[#012B33]">
  <div class="max-w-md w-full bg-[#013B44] rounded-3xl shadow-2xl p-8 border border-[#00ACB1]/20">
    <div class="text-center mb-8">
      <div class="bg-[#00ACB1]/20 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto mb-6 p-3 shadow-inner border border-[#00ACB1]/40">
        <img src="/logo.png" alt="Dental Lorey Logo" class="w-full h-full object-contain rounded-2xl bg-white p-1.5 shadow-sm" />
      </div>
      <h1 class="text-3xl font-black text-white uppercase tracking-tighter">Dental Lorey</h1>
      <p class="text-[#ADC9CD] mt-2 font-medium italic">Odontología Integral</p>
    </div>


    <form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="space-y-6">
      <div>
        <label for="username" class="block text-sm font-medium text-[#ADC9CD] mb-1">Usuario</label>
        <input
          id="username"
          type="text"
          bind:value={username}
          required
          class="input-field bg-black/20 border-[#00ACB1]/20 text-white placeholder-[#ADC9CD]"
          placeholder="nombre_usuario"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-[#ADC9CD] mb-1">Contraseña</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          class="input-field bg-black/20 border-[#00ACB1]/20 text-white placeholder-[#ADC9CD]"
          placeholder="••••••••"
        />
      </div>

      {#if error}
        <div class="bg-red-900/50 text-red-300 p-3 rounded-xl text-sm border border-red-800/50">
          {error}
        </div>
      {/if}

      <button
        type="submit"
        disabled={loading}
        class="w-full btn-primary py-3 flex items-center justify-center space-x-2"
      >
        {#if loading}
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
        {:else}
          <span>Entrar al Sistema</span>
        {/if}
      </button>
    </form>
    
    <div class="mt-6 pt-6 border-t border-[#00ACB1]/20 text-center text-xs text-[#ADC9CD] italic">
      &copy; 2026 LoReyDent - Gestión Dental Profesional
    </div>
  </div>
</div>
