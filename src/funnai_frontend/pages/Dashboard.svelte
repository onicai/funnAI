<script lang="ts">
  import { onMount } from 'svelte';
  import { store, theme } from "../stores/store";
  import { link } from 'svelte-spa-router';
  import Footer from "../components/funnai/Footer.svelte";
  
  // Import new dashboard components
  import MainerLeaderboard from "../components/dashboard/MainerLeaderboard.svelte";
  import ProtocolMetrics from "../components/dashboard/ProtocolMetrics.svelte";
  import TokenDistribution from "../components/dashboard/TokenDistribution.svelte";
  import SystemStatus from "../components/dashboard/SystemStatus.svelte";
  import MetricsDashboard from "../components/dashboard/MetricsDashboard.svelte";
  
  // Import services for fetching token data
  import { IcrcService } from "../helpers/IcrcService";
  import { fetchTokens } from "../helpers/token_helpers";
  import { formatBalance, formatLargeNumber } from "../helpers/utils/numberFormatUtils";
  import BigNumber from "bignumber.js";

  // Sample data 
  $: totalMainers = 701; // This could come from store
  $: activeMainers = 462;
  $: totalRewards = 1250.50;
  $: totalCycles = 21246900000000;
  

  
  // FUNNAI total supply state
  let totalSupply = "210,992"; // Default fallback value
  let isLoadingSupply = true;
  let supplyError = "";
  
  // Format total supply properly (convert from smallest units to whole tokens)
  function formatTotalSupply(rawAmount: bigint, decimals: number): string {
    try {
      // Use BigNumber for precise calculations
      const rawBN = new BigNumber(rawAmount.toString());
      const divisor = new BigNumber(10).pow(decimals);
      const tokenAmount = rawBN.dividedBy(divisor);
      
      // Round down to whole tokens and format with thousands separators
      return tokenAmount.integerValue(BigNumber.ROUND_DOWN).toFormat(0);
    } catch (error) {
      console.error("Error formatting total supply:", error);
      return "0";
    }
  }
  
  // Load FUNNAI total supply from canister
  async function loadTotalSupply() {
    try {
      isLoadingSupply = true;
      supplyError = "";
      
      // Get FUNNAI token from token helpers
      const tokensResult = await fetchTokens({});
      const funnaiToken = tokensResult.tokens.find(token => token.symbol === "FUNNAI");
      
      if (!funnaiToken) {
        throw new Error("FUNNAI token not found");
      }
      
      // Fetch total supply from canister
      const totalSupplyBigInt = await IcrcService.getIcrc1TotalSupply(funnaiToken);
      
      // Format the total supply properly
      totalSupply = formatTotalSupply(totalSupplyBigInt, funnaiToken.decimals);
      
    } catch (error) {
      console.error("Error loading total supply:", error);
      supplyError = error.message || "Failed to load supply";
      // Keep the fallback value
    } finally {
      isLoadingSupply = false;
    }
  }
  
  // Load total supply on mount
  onMount(() => {
    loadTotalSupply();
  });
</script>

<div class="flex flex-col h-full min-h-[calc(100vh-60px)] dark:bg-gray-900">
  <div class="container mx-auto px-2 md:px-8 py-2 md:py-8 flex-grow dark:bg-gray-900">
    <!-- Dashboard Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
      <p class="text-gray-600 dark:text-gray-400">Welcome to your funnAI overview</p>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <!-- mAIners Card -->
      <!-- <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Global mAIners</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">{totalMainers}</p>
          </div> 
          <div class="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
            🦜
          </div>
        </div>
      </div>-->

      <!-- Current Supply Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Current supply</p>
            <div class="flex items-center space-x-2">
              {#if isLoadingSupply}
                <div class="animate-pulse flex items-center space-x-2">
                  <div class="h-6 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
                  <span class="text-xs text-green-600 dark:text-green-400">FUNNAI</span>
                </div>
              {:else if supplyError}
                <p class="text-lg font-semibold text-red-600 dark:text-red-400" title={supplyError}>
                  Error
                  <span class="text-xs text-green-600 dark:text-green-400 ml-1">
                    $FUNNAI
                  </span>
                </p>
              {:else}
                <p class="text-lg font-semibold text-gray-900 dark:text-white">
                  {totalSupply}
                  <span class="text-xs text-green-600 dark:text-green-400 ml-1">
                    $FUNNAI
                  </span>
                </p>
              {/if}
            </div>
          </div>
          <div class="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-full">
            <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
          </div>
        </div>
        {#if !isLoadingSupply && !supplyError}
          <div class="mt-2 h-4">
            <button 
              on:click={loadTotalSupply} 
              class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
              title="Refresh supply from canister"
            >
              Refresh
            </button>
          </div>
        {/if}
      </div>

      <!-- Total Rewards Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Max supply</p>
            <p class="text-lg font-semibold text-gray-900 dark:text-white">21M
              <span class="text-xs text-green-600 dark:text-green-400">
                $FUNNAI
              </span>
            </p>
          </div>
          <div class="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
        </div>
        <div class="mt-2">
          <p class="text-xs text-gray-500 dark:text-gray-400">June 29th, 2033</p>
        </div>
      </div>

      <!-- System Status Card -->
      <!-- Available options: "excellent" | "degraded" | "paused" -->
      <SystemStatus protocolStatus="excellent" />
    </div>

    <!-- Metrics Dashboard -->
    <div class="mb-8">
      <MetricsDashboard title="Daily Metrics Dashboard" />
    </div>

    <!-- Dashboard Components Grid -->
    <div class="space-y-8">
      <!-- Top Row: User mAIner Stats and Protocol Metrics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="grid grid-cols-1 gap-6">
          <ProtocolMetrics compact={false} />
        </div>
        <div class="grid grid-cols-1 gap-6">
          <TokenDistribution />
          <MainerLeaderboard variant="user" maxItems={8} />
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