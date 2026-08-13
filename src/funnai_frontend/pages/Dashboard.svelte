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
  import TokenInfo from "../components/dashboard/TokenInfo.svelte";
  import TokenRewardsChart from "../components/dashboard/TokenRewardsChart.svelte";
  import CyclesMetrics from "../components/dashboard/CyclesMetrics.svelte";
  
  // Import services for fetching token data
  import { IcrcService } from "../helpers/IcrcService";
  import { fetchTokens } from "../helpers/token_helpers";
  import { formatBalance, formatLargeNumber } from "../helpers/utils/numberFormatUtils";
  import { BurnService } from "../helpers/BurnService";
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

  // Total burned state
  let totalBurned = "—";
  let isLoadingBurned = true;
  let burnedError = "";
  
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
      supplyError = (error as Error).message || "Failed to load supply";
      // Keep the fallback value
    } finally {
      isLoadingSupply = false;
    }
  }
  
  async function loadTotalBurned() {
    try {
      isLoadingBurned = true;
      burnedError = "";
      const data = await BurnService.getTotalBurned();
      totalBurned = data.totalBurnedFunnai;
    } catch (error) {
      console.error("Error loading total burned:", error);
      burnedError = (error as Error).message || "Failed to load";
    } finally {
      isLoadingBurned = false;
    }
  }

  // Load total supply on mount
  onMount(() => {
    loadTotalSupply();
    loadTotalBurned();
  });
</script>

<div class="agent-page">
  <div class="agent-container">
    <!-- Dashboard Header -->
    <div class="mb-8">
      <p class="agent-eyebrow mb-2">Overview</p>
      <h1 class="agent-title mb-2">Dashboard</h1>
      <p class="agent-subtitle">Protocol health, supply, and agent network metrics</p>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <div class="agent-card !bg-agent-surface p-5">
        <div class="relative z-[1] flex items-start justify-between gap-2 min-h-[1.25rem]">
          <p class="agent-eyebrow">Current supply</p>
          <button
            type="button"
            on:click={loadTotalSupply}
            disabled={isLoadingSupply}
            class="text-[11px] font-medium text-gray-500 hover:text-[#a78bfa] transition-colors disabled:opacity-0 disabled:pointer-events-none"
            title="Refresh supply from canister"
          >
            {supplyError ? 'Retry' : 'Refresh'}
          </button>
        </div>
        <div class="relative z-[1] mt-3">
          <p class="agent-metric-value">
            {#if isLoadingSupply}
              <span class="agent-metric-pulse w-[9ch]" aria-hidden="true"></span>
            {:else if supplyError}
              <span class="min-w-[9ch] text-red-300" title={supplyError}>—</span>
            {:else}
              <span class="min-w-[9ch]">{totalSupply}</span>
            {/if}
            <span class="agent-metric-unit">$FUNNAI</span>
          </p>
          <p class="agent-metric-hint">In circulation</p>
        </div>
      </div>

      <div class="agent-card !bg-agent-surface p-5">
        <p class="relative z-[1] agent-eyebrow">Cap</p>
        <div class="relative z-[1] mt-3">
          <p class="agent-metric-value">
            <span class="min-w-[9ch]">21M</span>
            <span class="agent-metric-unit">$FUNNAI</span>
          </p>
          <p class="agent-metric-hint">Max supply · June 29, 2033</p>
        </div>
      </div>

      <div class="agent-card !bg-agent-surface p-5">
        <div class="relative z-[1] flex items-start justify-between gap-2 min-h-[1.25rem]">
          <p class="agent-eyebrow">Burned</p>
          <button
            type="button"
            on:click={loadTotalBurned}
            disabled={isLoadingBurned}
            class="text-[11px] font-medium text-gray-500 hover:text-[#a78bfa] transition-colors disabled:opacity-0 disabled:pointer-events-none"
            title={burnedError ? burnedError : "Refresh burned count from canister"}
          >
            {burnedError ? 'Retry' : 'Refresh'}
          </button>
        </div>
        <div class="relative z-[1] mt-3">
          <p class="agent-metric-value">
            {#if isLoadingBurned}
              <span class="agent-metric-pulse w-[9ch]" aria-hidden="true"></span>
            {:else}
              <span class="min-w-[9ch]">{totalBurned}</span>
            {/if}
            <span class="agent-metric-unit">$FUNNAI</span>
          </p>
          <p class="agent-metric-hint">Removed from supply</p>
        </div>
      </div>

      <SystemStatus protocolStatus="excellent" />
    </div>

    

    <!-- Dashboard Components Grid -->
    <div class="space-y-6">
      <!-- Cycles Overview Section -->
      <div class="grid grid-cols-1">
        <CyclesMetrics title="Cycles Overview" />
      </div>

      <!-- Token Information Section -->
      <div class="grid grid-cols-1">
        <TokenInfo />
      </div>

      

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

      <!-- Token Rewards Analytics Section -->
      <div class="grid grid-cols-1">
        <TokenRewardsChart />
      </div>
    </div>

    <!-- Metrics Dashboard -->
    <div class="my-6">
      <MetricsDashboard title="Daily Metrics Dashboard" />
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