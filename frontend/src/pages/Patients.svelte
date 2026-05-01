<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "../lib/api";
  import {
    Search,
    Plus,
    User,
    Phone,
    Mail,
    MapPin,
    Edit2,
    Trash2,
    X,
    ClipboardList,
    Activity,
    Heart,
    ShieldAlert,
    CheckCircle2,
    AlertCircle,
    Save,
    RotateCcw,
  } from "lucide-svelte";
  import dayjs from "dayjs";
  import Odontogram from "../lib/components/Odontogram.svelte";
  import { fade, fly } from "svelte/transition";
  import { uiStore } from "../lib/ui.svelte";
  import ConfirmModal from "../lib/components/ConfirmModal.svelte";

  let patients = $state<any[]>([]);
  let filteredPatients = $state<any[]>([]);
  let searchTerm = $state("");
  let loading = $state(true);
  let showModal = $state(false);
  let showDeleteModal = $state(false);
  let editingPatient = $state<any>(null);
  let patientToDelete = $state<any>(null);
  let activeTab = $state("personal");
  let doctors = $state<any[]>([]);
  let patientDetails = $state<any>(null);
  let isEditingBudget = $state(false);
  let tempBudget = $state(0);
  let showBudgetConfirm = $state(false);

  // Form state structure
  let patientForm = $state({
    first_name: "",
    last_name: "",
    reference: "",
    age: null as number | null,
    sex: "Masculino",
    ethnic_group: "",
    occupation: "",
    birth_date: "",
    school_grade: "",
    phone: "",
    email: "",
    address: "",
    marital_status: "Soltero(a)",
    religion: "",
    entry_date: dayjs().format("YYYY-MM-DD"),
    doctor_id: null as number | null,
    initial_budget: 0.0,
    nationality: "Mexicana",
    locality: "",
    consultation_reason: "",
    last_dental_consultation: "",

    // Menores
    minor_father_name: "",
    minor_father_occupation: "",
    minor_mother_name: "",
    minor_mother_occupation: "",
    minor_parents_marital_status: "",
    minor_pediatrician: "",

    // Signos Vitales
    weight: null as number | null,
    height: null as number | null,
    temperature: null as number | null,
    heart_rate: null as number | null,
    respiratory_rate: null as number | null,
    blood_pressure: "",
    oxygen_saturation: null as number | null,
    glucose: null as number | null,

    // Examen Facial
    facial_profile: "Recto",
    facial_front: "Normofacial",
    facial_particular_signs: "",

    // Antecedentes (Stored as JSON strings)
    family_history_json: "{}",
    non_pathological_history_json: "{}",
    pathological_history_json: "{}",
    odontogram_json: "{}",
    notes: "",
  });

  onMount(() => {
    loadPatients();
    loadDoctors();
  });

  async function loadDoctors() {
    try {
      doctors = await api.auth.listUsers();
    } catch (e) {
      console.error("Error cargando doctores:", e);
    }
  }

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
    filteredPatients = patients.filter(
      (p) =>
        `${p.first_name} ${p.last_name}`
          .toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        p.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.phone?.includes(searchTerm),
    );
  }

  $effect(() => {
    if (searchTerm !== undefined) filterPatients();
  });

  async function openModal(patient: any = null) {
    editingPatient = patient;
    activeTab = "personal";
    patientDetails = null;
    if (patient) {
      // Cargar detalles completos (citas, pagos)
      try {
        patientDetails = await api.patients.get(patient.id);
      } catch (e) {
        console.error("Error cargando detalles:", e);
      }
      patientForm = {
        ...patient,
        doctor_id: patient.doctor_id,
        initial_budget: patient.initial_budget,
        family_history_json: patient.family_history_json || "{}",
        non_pathological_history_json:
          patient.non_pathological_history_json || "{}",
        pathological_history_json: patient.pathological_history_json || "{}",
        odontogram_json: patient.odontogram_json || "{}",
      };
    } else {
      patientForm = {
        first_name: "",
        last_name: "",
        reference: "",
        age: null,
        sex: "Masculino",
        ethnic_group: "",
        occupation: "",
        birth_date: "",
        school_grade: "",
        phone: "",
        email: "",
        address: "",
        marital_status: "Soltero(a)",
        religion: "",
        entry_date: dayjs().format("YYYY-MM-DD"),
        nationality: "Mexicana",
        locality: "",
        consultation_reason: "",
        last_dental_consultation: "",
        minor_father_name: "",
        minor_father_occupation: "",
        minor_mother_name: "",
        minor_mother_occupation: "",
        minor_parents_marital_status: "",
        minor_pediatrician: "",
        weight: null,
        height: null,
        temperature: null,
        heart_rate: null,
        respiratory_rate: null,
        blood_pressure: "",
        oxygen_saturation: null,
        glucose: null,
        facial_profile: "Recto",
        facial_front: "Normofacial",
        facial_particular_signs: "",
        family_history_json: "{}",
        non_pathological_history_json: "{}",
        pathological_history_json: "{}",
        odontogram_json: "{}",
        doctor_id: null,
        initial_budget: 0,
        notes: "",
      };
    }
    showModal = true;
  }

  async function handleSubmit() {
    // Limpiar datos: convertir strings vacíos a null para campos opcionales
    const data = { ...patientForm };
    (Object.keys(data) as Array<keyof typeof data>).forEach((key) => {
      if (data[key] === "") (data as any)[key] = null;
    });

    try {
      if (editingPatient) {
        await api.patients.update(editingPatient.id, data);
      } else {
        await api.patients.create(data);
      }
      showModal = false;
      await loadPatients();
    } catch (e) {
      alert("Error al guardar: " + e);
    }
  }

  function confirmDelete(patient: any) {
    patientToDelete = patient;
    showDeleteModal = true;
  }

  async function handleDelete() {
    if (!patientToDelete) return;
    try {
      await api.patients.delete(patientToDelete.id);
      showDeleteModal = false;
      patientToDelete = null;
      await loadPatients();
    } catch (e) {
      alert("Error al eliminar: " + e);
    }
  }

  function toggleHistory(jsonField: keyof typeof patientForm, key: string) {
    const rawValue = patientForm[jsonField];
    if (typeof rawValue !== "string") return;

    const current = JSON.parse(rawValue || "{}");
    current[key] = !current[key];
    (patientForm as any)[jsonField] = JSON.stringify(current);
  }

  function checkHistory(jsonField: keyof typeof patientForm, key: string) {
    const rawValue = patientForm[jsonField];
    if (typeof rawValue !== "string") return false;

    const current = JSON.parse(rawValue || "{}");
    return !!current[key];
  }

  function startEditingBudget() {
    tempBudget = patientForm.initial_budget || 0;
    isEditingBudget = true;
  }

  function confirmBudgetChange() {
    showBudgetConfirm = true;
  }

  function saveBudget() {
    patientForm.initial_budget = tempBudget;
    isEditingBudget = false;
    showBudgetConfirm = false;
  }

  function cancelBudgetEdit() {
    isEditingBudget = false;
    showBudgetConfirm = false;
  }
</script>

<div class="min-h-screen px-4 py-8 bg-[#012B33]">
  <div class="max-w-7xl mx-auto space-y-8">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
      <div in:fly={{ y: -20, duration: 600 }}>
        <h1 class="text-5xl font-black text-white uppercase tracking-tighter">
          Historial Clínico
        </h1>
        <p class="text-[#ADC9CD] font-medium italic mt-2">
          Gestión integral de pacientes Dental Lorey.
        </p>
      </div>
      <button
        onclick={() => openModal()}
        class="bg-dent-kelly hover:bg-dent-kelly/80 text-white px-8 py-4 rounded-2xl font-black uppercase tracking-widest shadow-xl shadow-dent-kelly/20 transition-all transform hover:scale-105 flex items-center space-x-3"
      >
        <Plus size={24} />
        <span>Registrar Paciente</span>
      </button>
    </div>

    <!-- Search Bar -->
    <div
      class="card p-6 bg-white/5 border-white/10 backdrop-blur-xl"
      in:fade={{ delay: 200 }}
    >
      <div class="relative">
        <Search
          class="absolute left-6 top-1/2 -translate-y-1/2 text-dent-kelly"
          size={24}
        />
        <input
          type="text"
          bind:value={searchTerm}
          placeholder="Buscar por nombre, apellidos o referencia (ej. 'señor de la esquina')..."
          class="w-full bg-black/40 border-2 border-white/5 rounded-2xl py-5 pl-16 pr-6 text-white font-bold placeholder-white/20 focus:border-dent-kelly/50 transition-all outline-none"
        />
      </div>
    </div>

    <!-- Patient List -->
    {#if loading && patients.length === 0}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Array(6) as _}
          <div
            class="h-64 bg-white/5 rounded-[2.5rem] animate-pulse border border-white/5"
          ></div>
        {/each}
      </div>
    {:else if filteredPatients.length === 0}
      <div
        class="card py-32 text-center bg-white/5 border-white/10 rounded-[3rem]"
        in:fade
      >
        <div
          class="bg-dent-kelly/10 w-24 h-24 rounded-[2rem] flex items-center justify-center mx-auto mb-6 text-dent-kelly shadow-inner"
        >
          <User size={48} />
        </div>
        <h3 class="text-2xl font-black text-white uppercase tracking-tight">
          No hay coincidencias
        </h3>
        <p class="text-[#ADC9CD] mt-2 italic font-medium">
          Comienza registrando un nuevo paciente para tu clínica.
        </p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {#each filteredPatients as patient, i}
          <div
            class="group bg-white/5 rounded-[2.5rem] p-8 border border-white/5 hover:border-dent-kelly/30 transition-all duration-500 relative overflow-hidden shadow-2xl"
            in:fly={{ y: 20, duration: 400, delay: i * 50 }}
          >
            <div
              class="absolute -right-10 -top-10 w-32 h-32 bg-dent-kelly/5 rounded-full blur-3xl group-hover:bg-dent-kelly/20 transition-all"
            ></div>

            <div class="flex justify-between items-start mb-6 relative z-10">
              <div
                class="w-16 h-16 bg-gradient-to-br from-dent-kelly to-emerald-600 text-white rounded-2xl flex items-center justify-center font-black text-2xl shadow-xl shadow-dent-kelly/20 uppercase"
              >
                {patient.first_name.charAt(0)}{patient.last_name.charAt(0)}
              </div>
              <div class="flex space-x-1">
                <button
                  onclick={() => openModal(patient)}
                  class="p-3 text-white/40 hover:text-white hover:bg-white/10 rounded-xl transition-all"
                >
                  <Edit2 size={20} />
                </button>
                <button
                  onclick={() => confirmDelete(patient)}
                  class="p-3 text-white/40 hover:text-rose-500 hover:bg-rose-500/10 rounded-xl transition-all"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>

            <div class="relative z-10">
              <h3
                class="font-black text-2xl text-white tracking-tight uppercase line-clamp-1"
              >
                {patient.first_name}
                {patient.last_name}
              </h3>
              {#if patient.reference}
                <p
                  class="text-dent-kelly font-black text-[10px] uppercase tracking-widest mt-1"
                >
                  Ref: {patient.reference}
                </p>
              {/if}

              <div class="grid grid-cols-2 gap-4 mt-8">
                <div class="space-y-4">
                  <div class="flex items-center space-x-3 text-white/60">
                    <Phone size={16} class="text-dent-kelly" />
                    <span class="text-xs font-bold"
                      >{patient.phone || "N/A"}</span
                    >
                  </div>
                  <div class="flex items-center space-x-3 text-white/60">
                    <Activity size={16} class="text-dent-kelly" />
                    <span class="text-xs font-bold"
                      >{patient.age ? `${patient.age} años` : "Edad N/A"}</span
                    >
                  </div>
                </div>
                <div class="space-y-4">
                  <div class="flex items-center space-x-3 text-white/60">
                    <MapPin size={16} class="text-dent-kelly" />
                    <span class="text-xs font-bold truncate"
                      >{patient.locality || "Loc. N/A"}</span
                    >
                  </div>
                  <div class="flex items-center space-x-3 text-white/60">
                    <ClipboardList size={16} class="text-dent-kelly" />
                    <span class="text-xs font-bold">Historial OK</span>
                  </div>
                </div>
              </div>
            </div>

            <button
              onclick={() => openModal(patient)}
              class="w-full mt-8 py-4 bg-white/5 hover:bg-white/10 text-white font-black uppercase text-[10px] tracking-widest rounded-2xl transition-all"
            >
              Ver Expediente Completo
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<!-- Modal Form -->
{#if showModal}
  <div
    class="fixed inset-0 bg-black/90 backdrop-blur-xl z-[100] flex items-center justify-center p-4 lg:p-12 overflow-y-auto"
  >
    <div
      class="bg-[#012B33] rounded-[3rem] w-full max-w-6xl shadow-2xl border border-white/10 flex flex-col max-h-[90vh] overflow-hidden"
    >
      <div
        class="absolute inset-0 z-[-1]"
        role="presentation"
        onclick={() => (showModal = false)}
      ></div>

      <!-- Modal Header -->
      <div
        class="p-8 border-b border-white/5 flex justify-between items-center bg-white/5"
      >
        <div class="flex items-center space-x-4">
          <div
            class="p-4 bg-dent-kelly rounded-2xl shadow-lg shadow-dent-kelly/20"
          >
            <ClipboardList size={32} class="text-white" />
          </div>
          <div>
            <h2
              class="text-3xl font-black text-white uppercase tracking-tighter"
            >
              {editingPatient ? "Expediente de" : "Nuevo"} Paciente
            </h2>
            <p
              class="text-sm font-bold text-dent-kelly uppercase tracking-widest"
            >
              {editingPatient
                ? `${patientForm.first_name} ${patientForm.last_name}`
                : "Captura de historial clínico completo"}
            </p>
          </div>
        </div>
        <button
          onclick={() => (showModal = false)}
          class="p-3 text-white/20 hover:text-white hover:bg-white/10 rounded-2xl transition-all"
        >
          <X size={32} />
        </button>
      </div>

      <!-- Tab Navigation -->
      <div
        class="px-8 py-4 flex space-x-2 overflow-x-auto border-b border-white/5 bg-black/20 scrollbar-hide"
      >
        {#each [{ id: "personal", label: "Personales", icon: User }, { id: "minor", label: "Menores", icon: ShieldAlert }, { id: "vitals", label: "Signos & Facial", icon: Activity }, { id: "history", label: "Antecedentes", icon: Heart }, { id: "odontogram", label: "Odontograma", icon: ClipboardList }, { id: "finances", label: "Citas & Finanzas", icon: CheckCircle2 }] as tab}
          <button
            onclick={() => (activeTab = tab.id)}
            class={`flex items-center space-x-2 px-6 py-3 rounded-xl font-black uppercase text-[10px] tracking-widest transition-all whitespace-nowrap ${activeTab === tab.id ? "bg-dent-kelly text-white shadow-lg shadow-dent-kelly/20" : "text-white/40 hover:bg-white/5"}`}
          >
            <tab.icon size={14} />
            <span>{tab.label}</span>
          </button>
        {/each}
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
        <form
          id="patient-form"
          onsubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          class="space-y-12"
        >
          {#if activeTab === "personal"}
            <div
              class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
              in:fade
            >
              <div class="space-y-1">
                <label for="first_name" class="label-clinical"
                  >Nombre(s) *</label
                >
                <input
                  id="first_name"
                  type="text"
                  bind:value={patientForm.first_name}
                  required
                  class="input-clinical"
                  placeholder="Nombre"
                />
              </div>
              <div class="space-y-1">
                <label for="last_name" class="label-clinical">Apellidos *</label
                >
                <input
                  id="last_name"
                  type="text"
                  bind:value={patientForm.last_name}
                  required
                  class="input-clinical"
                  placeholder="Apellidos"
                />
              </div>
              <div class="space-y-1">
                <label for="reference" class="label-clinical"
                  >Referencia (Para recordar) *</label
                >
                <input
                  id="reference"
                  type="text"
                  bind:value={patientForm.reference}
                  required
                  class="input-clinical border-dent-kelly/40"
                  placeholder="Ej. El señor de la esquina"
                />
              </div>

              <div class="space-y-1">
                <label for="doctor" class="label-clinical"
                  >Doctor(a) que lo atiende</label
                >
                <select
                  id="doctor"
                  bind:value={patientForm.doctor_id}
                  class="input-clinical appearance-none"
                >
                  <option value={null}>Seleccionar Doctor...</option>
                  {#each doctors as doctor}
                    <option value={doctor.id}>{doctor.full_name}</option>
                  {/each}
                </select>
              </div>

              <div class="space-y-1">
                <label for="budget" class="label-clinical"
                  >Presupuesto Inicial ($)</label
                >
                {#if editingPatient}
                  <div
                    class="flex items-center justify-between input-clinical border-white/5 bg-white/5 opacity-80"
                  >
                    <span class="text-xl font-black"
                      >${patientForm.initial_budget?.toLocaleString() ||
                        "0"}</span
                    >
                    <button
                      type="button"
                      onclick={() => (activeTab = "finances")}
                      class="text-[8px] font-black uppercase text-dent-kelly bg-dent-kelly/10 px-2 py-1 rounded-lg hover:bg-dent-kelly hover:text-white transition-all"
                    >
                      Modificar en Finanzas
                    </button>
                  </div>
                {:else}
                  <input
                    id="budget"
                    type="number"
                    step="0.01"
                    bind:value={patientForm.initial_budget}
                    class="input-clinical border-dent-kelly/40"
                    placeholder="0.00"
                  />
                {/if}
              </div>

              <div class="space-y-1">
                <label for="age" class="label-clinical">Edad</label>
                <input
                  id="age"
                  type="number"
                  bind:value={patientForm.age}
                  class="input-clinical"
                />
              </div>
              <div class="space-y-1">
                <label for="sex" class="label-clinical">Sexo</label>
                <select
                  id="sex"
                  bind:value={patientForm.sex}
                  class="input-clinical appearance-none"
                >
                  <option>Masculino</option>
                  <option>Femenino</option>
                  <option>Otro</option>
                </select>
              </div>
              <div class="space-y-1">
                <label for="birth_date" class="label-clinical"
                  >Fecha de Nacimiento</label
                >
                <input
                  id="birth_date"
                  type="date"
                  bind:value={patientForm.birth_date}
                  class="input-clinical"
                />
              </div>

              <div class="space-y-1">
                <label for="phone" class="label-clinical">Teléfono</label>
                <input
                  id="phone"
                  type="tel"
                  bind:value={patientForm.phone}
                  class="input-clinical"
                />
              </div>
              <div class="space-y-1">
                <label for="email" class="label-clinical">E-mail</label>
                <input
                  id="email"
                  type="email"
                  bind:value={patientForm.email}
                  class="input-clinical"
                />
              </div>
              <div class="space-y-1">
                <label for="occupation" class="label-clinical">Ocupación</label>
                <input
                  id="occupation"
                  type="text"
                  bind:value={patientForm.occupation}
                  class="input-clinical"
                />
              </div>

              <div class="space-y-1 col-span-full">
                <label for="address" class="label-clinical">Domicilio</label>
                <input
                  id="address"
                  type="text"
                  bind:value={patientForm.address}
                  class="input-clinical"
                  placeholder="Calle, Número, Colonia..."
                />
              </div>

              <div class="space-y-1">
                <label for="marital_status" class="label-clinical"
                  >Estado Civil</label
                >
                <select
                  id="marital_status"
                  bind:value={patientForm.marital_status}
                  class="input-clinical appearance-none"
                >
                  <option>Soltero(a)</option>
                  <option>Casado(a)</option>
                  <option>Divorciado(a)</option>
                  <option>Viudo(a)</option>
                  <option>Unión Libre</option>
                </select>
              </div>
              <div class="space-y-1">
                <label for="nationality" class="label-clinical"
                  >Nacionalidad</label
                >
                <input
                  id="nationality"
                  type="text"
                  bind:value={patientForm.nationality}
                  class="input-clinical"
                />
              </div>
              <div class="space-y-1">
                <label for="locality" class="label-clinical">Localidad</label>
                <input
                  id="locality"
                  type="text"
                  bind:value={patientForm.locality}
                  class="input-clinical"
                />
              </div>

              <div class="space-y-1 col-span-full">
                <label for="consultation_reason" class="label-clinical"
                  >Motivo de la Consulta</label
                >
                <textarea
                  id="consultation_reason"
                  bind:value={patientForm.consultation_reason}
                  class="input-clinical h-32 resize-none"
                  placeholder="¿Por qué acude hoy?"
                ></textarea>
              </div>
            </div>
          {/if}

          {#if activeTab === "minor"}
            <div
              class="bg-blue-950/20 p-8 rounded-[2.5rem] border border-blue-400/10 mb-8"
              in:fade
            >
              <div class="flex items-center space-x-3 mb-8">
                <ShieldAlert class="text-blue-400" />
                <h3 class="text-xl font-black text-white uppercase">
                  Información de Padres (Menores de Edad)
                </h3>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="space-y-6">
                  <div class="space-y-1">
                    <label for="minor_father_name" class="label-clinical"
                      >Nombre del Padre</label
                    >
                    <input
                      id="minor_father_name"
                      type="text"
                      bind:value={patientForm.minor_father_name}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="minor_father_occupation" class="label-clinical"
                      >Ocupación del Padre</label
                    >
                    <input
                      id="minor_father_occupation"
                      type="text"
                      bind:value={patientForm.minor_father_occupation}
                      class="input-clinical"
                    />
                  </div>
                </div>
                <div class="space-y-6">
                  <div class="space-y-1">
                    <label for="minor_mother_name" class="label-clinical"
                      >Nombre de la Madre</label
                    >
                    <input
                      id="minor_mother_name"
                      type="text"
                      bind:value={patientForm.minor_mother_name}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="minor_mother_occupation" class="label-clinical"
                      >Ocupación de la Madre</label
                    >
                    <input
                      id="minor_mother_occupation"
                      type="text"
                      bind:value={patientForm.minor_mother_occupation}
                      class="input-clinical"
                    />
                  </div>
                </div>
                <div
                  class="col-span-full grid grid-cols-1 md:grid-cols-2 gap-8"
                >
                  <div class="space-y-1">
                    <label
                      for="minor_parents_marital_status"
                      class="label-clinical">Estado Civil de los Padres</label
                    >
                    <input
                      id="minor_parents_marital_status"
                      type="text"
                      bind:value={patientForm.minor_parents_marital_status}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="minor_pediatrician" class="label-clinical"
                      >Nombre del Pediatra</label
                    >
                    <input
                      id="minor_pediatrician"
                      type="text"
                      bind:value={patientForm.minor_pediatrician}
                      class="input-clinical"
                    />
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if activeTab === "vitals"}
            <div class="space-y-12" in:fade>
              <div>
                <h3
                  class="text-xl font-black text-white uppercase mb-6 flex items-center space-x-2"
                >
                  <Activity class="text-dent-kelly" />
                  <span>Signos Vitales</span>
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div class="space-y-1">
                    <label for="weight" class="label-clinical text-[10px]"
                      >Peso (kg)</label
                    >
                    <input
                      id="weight"
                      type="number"
                      step="0.1"
                      bind:value={patientForm.weight}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="height" class="label-clinical text-[10px]"
                      >Estatura (cm)</label
                    >
                    <input
                      id="height"
                      type="number"
                      step="1"
                      bind:value={patientForm.height}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="temperature" class="label-clinical text-[10px]"
                      >Temperatura (°C)</label
                    >
                    <input
                      id="temperature"
                      type="number"
                      step="0.1"
                      bind:value={patientForm.temperature}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label
                      for="blood_pressure"
                      class="label-clinical text-[10px]"
                      >P. Arterial (T/A)</label
                    >
                    <input
                      id="blood_pressure"
                      type="text"
                      bind:value={patientForm.blood_pressure}
                      class="input-clinical"
                      placeholder="120/80"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="heart_rate" class="label-clinical text-[10px]"
                      >Freq. Cardiaca</label
                    >
                    <input
                      id="heart_rate"
                      type="number"
                      bind:value={patientForm.heart_rate}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label
                      for="respiratory_rate"
                      class="label-clinical text-[10px]"
                      >Freq. Respiratoria</label
                    >
                    <input
                      id="respiratory_rate"
                      type="number"
                      bind:value={patientForm.respiratory_rate}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label
                      for="oxygen_saturation"
                      class="label-clinical text-[10px]"
                      >Saturación O2 (%)</label
                    >
                    <input
                      id="oxygen_saturation"
                      type="number"
                      bind:value={patientForm.oxygen_saturation}
                      class="input-clinical"
                    />
                  </div>
                  <div class="space-y-1">
                    <label for="glucose" class="label-clinical text-[10px]"
                      >Glucosa (mg/dL)</label
                    >
                    <input
                      id="glucose"
                      type="number"
                      bind:value={patientForm.glucose}
                      class="input-clinical"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3
                  class="text-xl font-black text-white uppercase mb-6 flex items-center space-x-2"
                >
                  <User class="text-dent-kelly" />
                  <span>Examen Facial</span>
                </h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div class="space-y-1">
                    <label for="facial_profile" class="label-clinical"
                      >Perfil</label
                    >
                    <select
                      id="facial_profile"
                      bind:value={patientForm.facial_profile}
                      class="input-clinical appearance-none"
                    >
                      <option>Recto</option>
                      <option>Cóncavo</option>
                      <option>Convexo</option>
                    </select>
                  </div>
                  <div class="space-y-1">
                    <label for="facial_front" class="label-clinical"
                      >Frente</label
                    >
                    <select
                      id="facial_front"
                      bind:value={patientForm.facial_front}
                      class="input-clinical appearance-none"
                    >
                      <option>Braquifacial</option>
                      <option>Normofacial</option>
                      <option>Dolicofacial</option>
                    </select>
                  </div>
                  <div class="col-span-full space-y-1">
                    <label for="facial_particular_signs" class="label-clinical"
                      >Señas Particulares</label
                    >
                    <input
                      id="facial_particular_signs"
                      type="text"
                      bind:value={patientForm.facial_particular_signs}
                      class="input-clinical"
                      placeholder="Cicatrices, lunares, etc."
                    />
                  </div>
                </div>
              </div>
            </div>
          {/if}

          {#if activeTab === "history"}
            <div class="space-y-12" in:fade>
              <!-- Heredofamiliares -->
              <section>
                <h3
                  class="text-xl font-black text-white uppercase mb-6 border-l-4 border-dent-kelly pl-4"
                >
                  Antecedentes Heredofamiliares
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {#each ["Neoplasia (Cáncer)", "Diabetes", "Hipertensión Arterial", "Neurológicos", "Obesidad", "Hematológicos", "Malformaciones", "Cardiacos"] as item}
                    <button
                      type="button"
                      onclick={() => toggleHistory("family_history_json", item)}
                      class={`p-4 rounded-2xl border text-left transition-all flex items-center justify-between ${checkHistory("family_history_json", item) ? "bg-dent-kelly text-white border-dent-kelly" : "bg-white/5 text-white/40 border-white/5 hover:border-white/20"}`}
                    >
                      <span
                        class="text-[10px] font-black uppercase tracking-wider"
                        >{item}</span
                      >
                      {#if checkHistory("family_history_json", item)}
                        <CheckCircle2 size={16} />
                      {/if}
                    </button>
                  {/each}
                </div>
              </section>

              <!-- No Patológicos -->
              <section>
                <h3
                  class="text-xl font-black text-white uppercase mb-6 border-l-4 border-emerald-500 pl-4"
                >
                  Higiene y Dieta (No Patológicos)
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {#each ["Come Frutas/Verduras", "Come Carnes", "Come Cereales", "Come Chatarra", "Bebe 2L Agua/Día", "Bebe Refresco", "Vivienda con Piso", "Baño Diario"] as item}
                    <button
                      type="button"
                      onclick={() =>
                        toggleHistory("non_pathological_history_json", item)}
                      class={`p-4 rounded-2xl border text-left transition-all flex items-center justify-between ${checkHistory("non_pathological_history_json", item) ? "bg-emerald-500 text-white border-emerald-500" : "bg-white/5 text-white/40 border-white/5 hover:border-white/20"}`}
                    >
                      <span
                        class="text-[10px] font-black uppercase tracking-wider"
                        >{item}</span
                      >
                      {#if checkHistory("non_pathological_history_json", item)}
                        <CheckCircle2 size={16} />
                      {/if}
                    </button>
                  {/each}
                </div>
              </section>

              <!-- Patológicos -->
              <section>
                <h3
                  class="text-xl font-black text-white uppercase mb-6 border-l-4 border-rose-500 pl-4"
                >
                  Antecedentes Patológicos
                </h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {#each ["Tabaquismo", "Alcoholismo", "Sustancias Psicoactivas", "Tatuajes/Piercings", "Diabetes (P)", "Hipertensión (P)", "Convulsiones", "P. Cardiacos", "Radioterapia", "VIH/Transmisión Sexual", "Tuberculosis", "Asma/Vías Aéreas"] as item}
                    <button
                      type="button"
                      onclick={() =>
                        toggleHistory("pathological_history_json", item)}
                      class={`p-4 rounded-2xl border text-left transition-all flex items-center justify-between ${checkHistory("pathological_history_json", item) ? "bg-rose-500 text-white border-rose-500" : "bg-white/5 text-white/40 border-white/5 hover:border-white/20"}`}
                    >
                      <span
                        class="text-[10px] font-black uppercase tracking-wider"
                        >{item}</span
                      >
                      {#if checkHistory("pathological_history_json", item)}
                        <CheckCircle2 size={16} />
                      {/if}
                    </button>
                  {/each}
                </div>
              </section>
            </div>
          {/if}

          {#if activeTab === "odontogram"}
            <div in:fade>
              <Odontogram bind:data={patientForm.odontogram_json} />

              <div
                class="mt-8 bg-black/20 p-6 rounded-2xl border border-white/5"
              >
                <h4
                  class="text-xs font-black text-white/40 uppercase tracking-widest mb-4"
                >
                  Notas adicionales del Odontograma
                </h4>
                <textarea
                  bind:value={patientForm.notes}
                  class="input-clinical h-32 resize-none"
                  placeholder="Detalles sobre extracciones, prótesis, etc."
                ></textarea>
              </div>
            </div>
          {/if}

          {#if activeTab === "finances"}
            <div in:fade class="space-y-8">
              <!-- Financial Summary Cards -->
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div
                  class="bg-white/5 p-6 rounded-3xl border border-white/5 relative group"
                >
                  <div class="flex justify-between items-start">
                    <span
                      class="text-[10px] font-black uppercase tracking-[0.2em] text-[#ADC9CD]"
                      >Presupuesto Total</span
                    >
                    {#if !isEditingBudget}
                      <button
                        type="button"
                        onclick={startEditingBudget}
                        class="p-2 text-white/20 hover:text-dent-kelly transition-colors"
                      >
                        <Edit2 size={14} />
                      </button>
                    {/if}
                  </div>

                  {#if isEditingBudget}
                    <div class="mt-2 space-y-3">
                      <input
                        type="number"
                        bind:value={tempBudget}
                        class="w-full bg-black/40 border border-dent-kelly/50 rounded-xl py-2 px-4 text-xl font-black text-white outline-none focus:border-dent-kelly"
                      />
                      <div class="flex space-x-2">
                        {#if !showBudgetConfirm}
                          <button
                            type="button"
                            onclick={confirmBudgetChange}
                            class="flex-1 bg-dent-kelly/20 hover:bg-dent-kelly text-dent-kelly hover:text-white py-2 rounded-lg text-[10px] font-black uppercase transition-all"
                          >
                            Actualizar
                          </button>
                          <button
                            type="button"
                            onclick={cancelBudgetEdit}
                            class="px-3 bg-white/5 hover:bg-white/10 text-white/40 py-2 rounded-lg transition-all"
                          >
                            <RotateCcw size={14} />
                          </button>
                        {:else}
                          <div
                            class="flex-1 bg-rose-500/20 border border-rose-500/30 p-2 rounded-xl text-center"
                          >
                            <p
                              class="text-[8px] font-black text-rose-400 uppercase mb-2"
                            >
                              ¿Confirmar cambio?
                            </p>
                            <div class="flex space-x-2">
                              <button
                                type="button"
                                onclick={saveBudget}
                                class="flex-1 bg-rose-500 text-white py-1.5 rounded-lg text-[8px] font-black uppercase"
                              >
                                Sí, Cambiar
                              </button>
                              <button
                                type="button"
                                onclick={() => (showBudgetConfirm = false)}
                                class="flex-1 bg-white/10 text-white py-1.5 rounded-lg text-[8px] font-black uppercase"
                              >
                                No
                              </button>
                            </div>
                          </div>
                        {/if}
                      </div>
                    </div>
                  {:else}
                    <p class="text-3xl font-black text-white mt-2">
                      ${patientForm.initial_budget?.toLocaleString() || "0"}
                    </p>
                  {/if}
                </div>
                <div
                  class="bg-dent-kelly/10 p-6 rounded-3xl border border-dent-kelly/20"
                >
                  <span
                    class="text-[10px] font-black uppercase tracking-[0.2em] text-dent-kelly"
                    >Total Pagado</span
                  >
                  <p class="text-3xl font-black text-white mt-2">
                    ${(
                      patientDetails?.payments?.reduce(
                        (acc: number, p: any) => acc + p.amount,
                        0,
                      ) || 0
                    ).toLocaleString()}
                  </p>
                </div>
                <div
                  class="bg-rose-500/10 p-6 rounded-3xl border border-rose-500/20"
                >
                  <span
                    class="text-[10px] font-black uppercase tracking-[0.2em] text-rose-400"
                    >Saldo Pendiente</span
                  >
                  <p class="text-3xl font-black text-white mt-2">
                    ${Math.max(
                      0,
                      (patientForm.initial_budget || 0) -
                        (patientDetails?.payments?.reduce(
                          (acc: number, p: any) => acc + p.amount,
                          0,
                        ) || 0),
                    ).toLocaleString()}
                  </p>
                </div>
              </div>

              <!-- Appointments (Evolution) -->
              <div class="space-y-4">
                <h3
                  class="text-xl font-black text-white uppercase flex items-center space-x-2"
                >
                  <ClipboardList class="text-dent-kelly" />
                  <span>Evolución (Citas realizadas)</span>
                </h3>

                <div class="space-y-3">
                  {#if patientDetails?.appointments?.length > 0}
                    {#each patientDetails.appointments.filter((a: any) => a.status === "atendido") as appt}
                      <div
                        class="bg-black/20 p-6 rounded-3xl border border-white/5 flex justify-between items-center"
                      >
                        <div>
                          <div class="flex items-center space-x-3 mb-2">
                            <span
                              class="bg-dent-kelly text-white text-[8px] font-black px-2 py-1 rounded-full uppercase tracking-widest"
                              >{dayjs(appt.date_time).format(
                                "DD MMM YYYY",
                              )}</span
                            >
                            <span
                              class="text-white/40 text-[10px] font-black uppercase tracking-widest"
                              >{appt.location || "Sucursal N/A"}</span
                            >
                          </div>
                          <p class="text-white font-bold">{appt.description}</p>
                          {#if appt.treatment_details}
                            <p class="text-[#ADC9CD] text-xs mt-1 italic">
                              {appt.treatment_details}
                            </p>
                          {/if}
                        </div>
                        <div class="text-right">
                          <span
                            class="text-[10px] font-black uppercase tracking-widest text-[#ADC9CD] block mb-1"
                            >Costo</span
                          >
                          <span class="text-xl font-black text-white"
                            >${appt.cost?.toLocaleString() || "0"}</span
                          >
                        </div>
                      </div>
                    {/each}
                  {:else}
                    <div
                      class="py-12 text-center bg-white/5 rounded-3xl border border-white/5 border-dashed"
                    >
                      <p
                        class="text-white/20 font-black uppercase text-xs tracking-widest"
                      >
                        No hay citas registradas como atendidas
                      </p>
                    </div>
                  {/if}
                </div>
              </div>

              <!-- Payments List -->
              <div class="space-y-4">
                <h3
                  class="text-xl font-black text-white uppercase flex items-center space-x-2"
                >
                  <Activity class="text-emerald-400" />
                  <span>Historial de Pagos</span>
                </h3>
                <div class="space-y-3">
                  {#if patientDetails?.payments?.length > 0}
                    {#each patientDetails.payments as pay}
                      <div
                        class="bg-emerald-500/5 p-4 rounded-2xl border border-emerald-500/10 flex justify-between items-center"
                      >
                        <div class="flex items-center space-x-4">
                          <div
                            class="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg"
                          >
                            <CheckCircle2 size={16} />
                          </div>
                          <div>
                            <span
                              class="text-white/40 text-[8px] font-black uppercase tracking-widest"
                              >{dayjs(pay.date).format(
                                "DD/MM/YYYY HH:mm",
                              )}</span
                            >
                            <p class="text-white text-xs font-bold">
                              {pay.description || "Pago de consulta"}
                            </p>
                          </div>
                        </div>
                        <span class="text-lg font-black text-emerald-400"
                          >+ ${pay.amount.toLocaleString()}</span
                        >
                      </div>
                    {/each}
                  {:else}
                    <div
                      class="py-8 text-center bg-white/5 rounded-3xl border border-white/5 border-dashed"
                    >
                      <p
                        class="text-white/20 font-black uppercase text-xs tracking-widest"
                      >
                        No se han registrado pagos
                      </p>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          {/if}
        </form>
      </div>

      <!-- Modal Footer -->
      <div
        class="p-8 border-t border-white/5 flex justify-end space-x-4 bg-black/20"
      >
        <button
          type="button"
          onclick={() => (showModal = false)}
          class="px-8 py-4 bg-white/5 text-white/40 font-black uppercase text-xs tracking-widest rounded-2xl hover:bg-white/10 transition-all"
        >
          Cerrar sin guardar
        </button>
        <button
          type="submit"
          form="patient-form"
          class="px-12 py-4 bg-dent-kelly text-white font-black uppercase text-xs tracking-[0.3em] rounded-2xl shadow-xl shadow-dent-kelly/20 hover:scale-105 transition-all"
        >
          {editingPatient ? "Actualizar Expediente" : "Crear Historial"}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Custom Delete Confirmation Modal -->
{#if showDeleteModal}
  <div
    class="fixed inset-0 bg-black/80 backdrop-blur-md z-[200] flex items-center justify-center p-4"
    in:fade
  >
    <div
      class="bg-[#013B44] rounded-[2.5rem] w-full max-w-md border border-rose-500/30 shadow-2xl shadow-rose-500/10 overflow-hidden"
      in:fly={{ y: 20, duration: 400 }}
    >
      <div class="p-8 text-center">
        <div
          class="w-20 h-20 bg-rose-500/10 rounded-3xl flex items-center justify-center mx-auto mb-6 text-rose-500 shadow-inner"
        >
          <Trash2 size={40} />
        </div>

        <h2
          class="text-2xl font-black text-white uppercase tracking-tighter mb-2"
        >
          ¿Eliminar Paciente?
        </h2>
        <p class="text-[#ADC9CD] text-sm font-medium italic px-4">
          Estás a punto de eliminar el expediente de <span
            class="text-white font-black not-italic"
            >{patientToDelete?.first_name} {patientToDelete?.last_name}</span
          >. Esta acción no se puede deshacer.
        </p>
      </div>

      <div class="p-6 bg-black/20 flex space-x-3">
        <button
          onclick={() => (showDeleteModal = false)}
          class="flex-1 py-4 bg-white/5 text-white/40 font-black uppercase text-[10px] tracking-widest rounded-2xl hover:bg-white/10 transition-all"
        >
          Cancelar
        </button>
        <button
          onclick={handleDelete}
          class="flex-1 py-4 bg-rose-500 text-white font-black uppercase text-[10px] tracking-[0.2em] rounded-2xl shadow-xl shadow-rose-500/20 hover:scale-105 transition-all"
        >
          Confirmar Eliminación
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  @reference "../app.css";
  .label-clinical {
    @apply block text-[9px] font-black text-white/30 uppercase tracking-widest ml-4 mb-2;
  }
  .input-clinical {
    @apply w-full bg-black/40 border border-white/10 rounded-[1.25rem] py-4 px-6 text-white font-bold outline-none focus:border-dent-kelly transition-all;
  }
  .input-clinical option {
    @apply bg-[#012B33] text-white;
  }

  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    @apply bg-white/10 rounded-full;
  }
</style>
