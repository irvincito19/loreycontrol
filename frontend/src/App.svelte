<script lang="ts">
  import Router, { push } from 'svelte-spa-router';
  import { onMount } from 'svelte';
  import { auth } from './lib/stores/auth';
  import Navbar from './lib/components/Navbar.svelte';
  import Login from './pages/Login.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import Patients from './pages/Patients.svelte';
  import Appointments from './pages/Appointments.svelte';
  import Payments from './pages/Payments.svelte';
  import Availability from './pages/Availability.svelte';
  import PublicBooking from './pages/PublicBooking.svelte';

  const routes = {
    '/login': Login,
    '/': Dashboard,
    '/patients': Patients,
    '/appointments': Appointments,
    '/payments': Payments,
    '/availability': Availability,
    '/booking': PublicBooking,
    '*': Dashboard,
  };

  const publicRoutes = ['#/login', '#/booking'];

  onMount(async () => {
    await auth.init();
    if (!$auth.authenticated && !publicRoutes.includes(window.location.hash)) {
      push('/login');
    }
  });

  $: if (!$auth.loading && !$auth.authenticated && !publicRoutes.includes(window.location.hash)) {
    push('/login');
  }
</script>

<main class="min-h-screen bg-[#012B33] flex flex-col">
  {#if $auth.loading}
    <div class="flex-1 flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-dent-blue"></div>
    </div>
  {:else}
    {#if $auth.authenticated}
      <Navbar />
      <div class="flex-1 container mx-auto p-4 md:p-6">
        <Router {routes} />
      </div>
    {:else}
      <div class="flex-1">
        <Router {routes} />
      </div>
    {/if}
  {/if}
</main>

<style>
  :global(body) {
    background-color: #012B33;
  }
</style>


