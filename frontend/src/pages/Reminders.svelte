<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../lib/api";
  import {
    Bell,
    Settings,
    Save,
    Smartphone,
    Clock,
    CheckCircle2,
    AlertCircle,
    MessageSquare,
    ShieldCheck,
    UserCheck,
  } from "lucide-svelte";
  import { fade, fly } from "svelte/transition";
  import { uiStore } from "../lib/ui.svelte";
  import ConfirmModal from "../lib/components/ConfirmModal.svelte";

  let config = $state({
    twilio_sid: "",
    twilio_token: "",
    twilio_phone: "",
    dentist_reminder_time: "07:00",
    patient_reminder_day_before_time: "19:00",
    patient_reminder_day_of_time: "08:00",
    is_active: true,
  });

  let users = $state<any[]>([]);
  let showToken = $state(false);
  let loading = $state(true);
  let saving = $state(false);
  let showSaveConfirm = $state(false);

  onMount(async () => {
    try {
      const [configData, usersData] = await Promise.all([
        api.reminders.getConfig(),
        api.auth.listUsers(),
      ]);
      config = { ...config, ...configData };
      users = usersData;
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
  });

  async function handleSave() {
    saving = true;
    try {
      const configToSave = {
        twilio_sid: config.twilio_sid,
        twilio_token: config.twilio_token,
        twilio_phone: config.twilio_phone,
        dentist_reminder_time: config.dentist_reminder_time,
        patient_reminder_day_before_time:
          config.patient_reminder_day_before_time,
        patient_reminder_day_of_time: config.patient_reminder_day_of_time,
        is_active: config.is_active,
      };

      const updated = await api.reminders.updateConfig(configToSave);
      config = { ...config, ...updated };
      uiStore.addToast("Configuración guardada exitosamente", "success");
    } catch (e) {
      uiStore.addToast("Error al guardar: " + e, "error");
    } finally {
      saving = false;
      showSaveConfirm = false;
    }
  }

  async function updateUserPhone(user: any, phone: string) {
    try {
      await api.auth.updateUser(user.id, {
        username: user.username,
        full_name: user.full_name,
        email: user.email,
        phone: phone,
      });
      // Opcional: mostrar un mini-toast o feedback
    } catch (e) {
      console.error("Error al actualizar teléfono:", e);
      uiStore.addToast("Error al actualizar el teléfono del doctor", "error");
    }
  }
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="max-w-5xl mx-auto space-y-8">
    <div in:fly={{ y: -20, duration: 600 }}>
      <h1 class="text-5xl font-black text-white uppercase tracking-tighter">
        Recordatorios Automáticos
      </h1>
      <p class="text-[#ADC9CD] font-medium italic mt-2">
        Configuración de notificaciones vía WhatsApp (Twilio).
      </p>
    </div>

    {#if loading}
      <div class="flex items-center justify-center py-20">
        <div
          class="animate-spin rounded-full h-12 w-12 border-b-2 border-dent-kelly"
        ></div>
      </div>
    {:else}
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left: Configuration Form -->
        <div class="lg:col-span-2 space-y-8">
          <div class="card p-8 bg-white/5 border-white/10" in:fade>
            <div
              class="flex items-center space-x-3 mb-8 border-b border-white/5 pb-6"
            >
              <div class="p-3 bg-dent-kelly/20 rounded-2xl text-dent-kelly">
                <Settings size={24} />
              </div>
              <h2
                class="text-2xl font-black text-white uppercase tracking-tight"
              >
                Ajustes de Twilio
              </h2>
            </div>

            <div class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <label
                    class="text-[10px] font-black text-white/40 uppercase tracking-widest ml-1"
                    >Account SID</label
                  >
                  <input
                    type="text"
                    bind:value={config.twilio_sid}
                    class="w-full bg-black/40 border border-white/10 rounded-xl py-4 px-6 text-white font-bold outline-none focus:border-dent-kelly transition-all"
                    placeholder="AC..."
                  />
                </div>
                <div class="space-y-2">
                  <label
                    class="text-[10px] font-black text-white/40 uppercase tracking-widest ml-1"
                    >Auth Token</label
                  >
                  <div class="relative">
                    <input
                      type={showToken ? "text" : "password"}
                      bind:value={config.twilio_token}
                      class="w-full bg-black/40 border border-white/10 rounded-xl py-4 px-6 text-white font-bold outline-none focus:border-dent-kelly transition-all"
                      placeholder="••••••••••••"
                    />
                    <button
                      type="button"
                      onclick={() => (showToken = !showToken)}
                      class="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors"
                    >
                      {#if showToken}
                        <ShieldCheck size={20} />
                      {:else}
                        <Bell size={20} />
                      {/if}
                    </button>
                  </div>
                </div>
              </div>

              <div class="space-y-2">
                <label
                  class="text-[10px] font-black text-white/40 uppercase tracking-widest ml-1"
                  >Número de Twilio</label
                >
                <div class="relative">
                  <Smartphone
                    class="absolute left-6 top-1/2 -translate-y-1/2 text-white/20"
                    size={20}
                  />
                  <input
                    type="text"
                    bind:value={config.twilio_phone}
                    class="w-full bg-black/40 border border-white/10 rounded-xl py-4 pl-16 pr-6 text-white font-bold outline-none focus:border-dent-kelly transition-all"
                    placeholder="+1986..."
                  />
                </div>
              </div>
            </div>
          </div>

          <div
            class="card p-8 bg-white/5 border-white/10"
            in:fade={{ delay: 200 }}
          >
            <div
              class="flex items-center space-x-3 mb-8 border-b border-white/5 pb-6"
            >
              <div class="p-3 bg-amber-500/20 rounded-2xl text-amber-500">
                <Clock size={24} />
              </div>
              <h2
                class="text-2xl font-black text-white uppercase tracking-tight"
              >
                Horarios de Envío
              </h2>
              <span
                class="ml-auto text-[10px] font-black text-white/20 uppercase tracking-widest"
                >Zona Horaria: CDMX (UTC-6)</span
              >
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div
                class="space-y-4 p-6 bg-black/20 rounded-3xl border border-white/5"
              >
                <div class="flex items-center space-x-2 text-dent-kelly">
                  <ShieldCheck size={16} />
                  <span class="text-[10px] font-black uppercase tracking-widest"
                    >A Doctores</span
                  >
                </div>
                <p class="text-xs text-[#ADC9CD] font-medium italic">
                  Agenda del día
                </p>
                <input
                  type="time"
                  bind:value={config.dentist_reminder_time}
                  class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-black outline-none focus:border-dent-kelly"
                />
                {#if config.last_run_dentist}
                  <p class="text-[9px] text-white/30 font-medium">
                    Último envío: {new Date(
                      config.last_run_dentist,
                    ).toLocaleString()}
                  </p>
                {/if}
              </div>

              <div
                class="space-y-4 p-6 bg-black/20 rounded-3xl border border-white/5"
              >
                <div class="flex items-center space-x-2 text-blue-400">
                  <Bell size={16} />
                  <span class="text-[10px] font-black uppercase tracking-widest"
                    >A Pacientes (1 Día Antes)</span
                  >
                </div>
                <p class="text-xs text-[#ADC9CD] font-medium italic">
                  Recordatorio preventivo
                </p>
                <input
                  type="time"
                  bind:value={config.patient_reminder_day_before_time}
                  class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-black outline-none focus:border-dent-kelly"
                />
                {#if config.last_run_patient_before}
                  <p class="text-[9px] text-white/30 font-medium">
                    Último envío: {new Date(
                      config.last_run_patient_before,
                    ).toLocaleString()}
                  </p>
                {/if}
              </div>

              <div
                class="space-y-4 p-6 bg-black/20 rounded-3xl border border-white/5"
              >
                <div class="flex items-center space-x-2 text-emerald-400">
                  <MessageSquare size={16} />
                  <span class="text-[10px] font-black uppercase tracking-widest"
                    >A Pacientes (Mismo Día)</span
                  >
                </div>
                <p class="text-xs text-[#ADC9CD] font-medium italic">
                  Recordatorio matutino
                </p>
                <input
                  type="time"
                  bind:value={config.patient_reminder_day_of_time}
                  class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-black outline-none focus:border-dent-kelly"
                />
                {#if config.last_run_patient_today}
                  <p class="text-[9px] text-white/30 font-medium">
                    Último envío: {new Date(
                      config.last_run_patient_today,
                    ).toLocaleString()}
                  </p>
                {/if}
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Status & Doctors -->
        <div class="space-y-8">
          <div
            class="card p-8 bg-dent-kelly/10 border-dent-kelly/20"
            in:fade={{ delay: 300 }}
          >
            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center space-x-3">
                <CheckCircle2
                  class={config.is_active ? "text-dent-kelly" : "text-white/20"}
                />
                <span
                  class="text-sm font-black text-white uppercase tracking-tighter"
                  >Estado del Sistema</span
                >
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={config.is_active}
                  class="sr-only peer"
                />
                <div
                  class="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-dent-kelly"
                ></div>
              </label>
            </div>

            <p
              class="text-xs text-[#ADC9CD] font-medium italic leading-relaxed"
            >
              {#if config.is_active}
                El sistema enviará recordatorios automáticamente en los horarios
                configurados.
              {:else}
                Los recordatorios automáticos están pausados temporalmente.
              {/if}
            </p>
          </div>

          <div
            class="card p-8 bg-white/5 border-white/10"
            in:fade={{ delay: 400 }}
          >
            <div class="flex items-center space-x-2 mb-6">
              <UserCheck size={18} class="text-dent-kelly" />
              <h3
                class="text-sm font-black text-white uppercase tracking-widest"
              >
                Teléfonos de Doctores
              </h3>
            </div>

            <div class="space-y-4">
              {#each users as user}
                <div class="bg-black/20 p-4 rounded-2xl border border-white/5">
                  <p
                    class="text-[10px] font-black text-white/60 uppercase mb-2"
                  >
                    {user.full_name}
                  </p>
                  <input
                    type="tel"
                    placeholder="+52..."
                    bind:value={user.phone}
                    onblur={() => updateUserPhone(user, user.phone)}
                    class="w-full bg-black/20 border border-white/5 rounded-lg py-2 px-3 text-xs text-white outline-none focus:border-dent-kelly transition-all"
                  />
                </div>
              {/each}
            </div>
          </div>

          <button
            onclick={() => (showSaveConfirm = true)}
            disabled={saving}
            class="w-full btn-primary py-5 flex items-center justify-center space-x-3 shadow-2xl"
          >
            {#if saving}
              <div
                class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"
              ></div>
            {:else}
              <Save size={20} />
              <span>Guardar Configuración</span>
            {/if}
          </button>
        </div>
      </div>
    {/if}

    <ConfirmModal 
      show={showSaveConfirm}
      title="¿Guardar Configuración?"
      message="¿Estás seguro de que deseas guardar estos cambios en la configuración de recordatorios?"
      confirmText={saving ? "Guardando..." : "Confirmar y Guardar"}
      onConfirm={handleSave}
      onCancel={() => (showSaveConfirm = false)}
    />

    <!-- Info Alert -->
    <div
      class="bg-amber-500/10 border border-amber-500/20 p-6 rounded-[2rem] flex items-start space-x-4"
    >
      <AlertCircle class="text-amber-500 shrink-0 mt-1" />
      <div class="space-y-1">
        <h4 class="text-sm font-black text-white uppercase tracking-tight">
          Nota sobre WhatsApp (Twilio)
        </h4>
        <p class="text-xs text-[#ADC9CD] font-medium italic leading-relaxed">
          Para que los mensajes se envíen correctamente, los pacientes deben
          haber aceptado recibir mensajes o el número debe estar verificado si
          usas una cuenta de prueba. El formato de teléfono recomendado es el
          internacional (ej. +521234567890).
        </p>
      </div>
    </div>
  </div>
</div>

<style>
  /* Custom time input styling */
  input[type="time"]::-webkit-calendar-picker-indicator {
    filter: invert(1);
    opacity: 0.5;
  }
</style>
