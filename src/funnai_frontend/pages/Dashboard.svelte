<script lang="ts">
  import { store, theme } from "../stores/store";
  import { link } from 'svelte-spa-router';
  import CyclesDisplay from "../components/funnai/CyclesDisplay.svelte";
  import TokensDisplay from "../components/funnai/TokensDisplay.svelte";
  import WalletStatus from "../components/funnai/WalletStatus.svelte";
  import Footer from "../components/funnai/Footer.svelte";

  // Sample data - in a real app this would come from your backend
  $: totalMainers = 3; // This could come from your store
  $: activeMainers = 2;
  $: totalRewards = 1250.50;
  $: totalCycles = 21246900000000;
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-2 md:px-8 py-2 md:py-8 flex-grow dark:bg-gray-900">
    <!-- Dashboard Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
      <p class="text-gray-600 dark:text-gray-400">Welcome to your funnAI overview</p>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- mAIners Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total mAIners</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{totalMainers}</p>
          </div>
          <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs text-green-600 dark:text-green-400">
            {activeMainers} active
          </p>
        </div>
      </div>

      <!-- Wallet Status Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Wallet Status</p>
            <p class="text-lg font-semibold text-gray-900 dark:text-white">
              {$store.isAuthed ? 'Connected' : 'Not Connected'}
            </p>
          </div>
          <div class="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-full">
            <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs {$store.isAuthed ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
            {$store.isAuthed ? 'Ready to transact' : 'Connect to get started'}
          </p>
        </div>
      </div>

      <!-- Total Rewards Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Rewards</p>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{totalRewards.toFixed(2)}</p>
          </div>
          <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs text-gray-500 dark:text-gray-400">Tokens earned</p>
        </div>
      </div>

      <!-- System Status Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">System Status</p>
            <p class="text-lg font-semibold text-green-600 dark:text-green-400">Operational</p>
          </div>
          <div class="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs text-green-600 dark:text-green-400">All services running</p>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Cycles Display -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Cycles Overview</h2>
        <CyclesDisplay cycles={totalCycles} showAllEvents={false} />
      </div>

      <!-- Quick Actions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <a use:link href="/" class="block w-full">
            <button class="w-full px-4 py-3 text-left bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-700 text-purple-700 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-all duration-200 flex items-center gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              Manage mAIners
            </button>
          </a>
          
          <a use:link href="/wallet" class="block w-full">
            <button class="w-full px-4 py-3 text-left bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-700 text-orange-700 dark:text-orange-300 hover:bg-orange-100 dark:hover:bg-orange-900/30 transition-all duration-200 flex items-center gap-3">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              Open Wallet
            </button>
          </a>
        </div>
      </div>
    </div>
  </div>

  <Footer />
</div>

<script context="module">
  export const Dashboard = (props) => {
    return {
      component: Dashboard,
      props
    };
  };
</script> 