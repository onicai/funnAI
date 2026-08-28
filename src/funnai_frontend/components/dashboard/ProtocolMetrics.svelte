<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import Countdown from "../_widgets/Countdown.svelte";

  export let title: string = "Protocol metrics";
  export let compact: boolean = false;

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;

  // Protocol metrics
  let totalCyclesBurned = 0;
  let cyclesBurnRate = 0;
  let totalChallenges = 5000;
  let totalSubmissions = 200291;
  let openSubmissions = 0;
  let rewardPerChallenge = 0;
  let activeMainers = 0;
  let timerActionRegularity = 0;

  // Recent activity metrics
  let recentChallenges = 0;
  let recentWinners = 0;
  let dailyActivity = [];

  async function loadProtocolMetrics() {
    try {
      // Get protocol total cycles burned
      const totalCyclesResult = await $store.gameStateCanisterActor.getProtocolTotalCyclesBurnt();
      if ("Ok" in totalCyclesResult) {
        totalCyclesBurned = Number(totalCyclesResult.Ok);
      }

      // Calculate approximate burn rate from total cycles and time
      // Since getCyclesBurnRate may not be available or may require complex parameters
      cyclesBurnRate = totalCyclesBurned > 0 ? Math.floor(totalCyclesBurned / 30) : 0; // Rough estimate

      // Get number of closed challenges
      try {
        const closedChallengesResult = await $store.gameStateCanisterActor.getNumClosedChallengesAdmin();
        if ("Ok" in closedChallengesResult) {
          totalChallenges = Number(closedChallengesResult.Ok);
        }
      } catch (err) {
        console.warn("getNumClosedChallengesAdmin not available:", err);
      }

      // Get total submissions
      try {
        const submissionsResult = await $store.gameStateCanisterActor.getNumSubmissionsAdmin();
        if ("Ok" in submissionsResult) {
          totalSubmissions = Number(submissionsResult.Ok);
        }
      } catch (err) {
        console.warn("getNumSubmissionsAdmin not available:", err);
      }

      // Get open submissions for open challenges
      try {
        const openSubmissionsResult = await $store.gameStateCanisterActor.getNumOpenSubmissionsForOpenChallengesAdmin();
        if ("Ok" in openSubmissionsResult) {
          openSubmissions = Number(openSubmissionsResult.Ok);
        }
      } catch (err) {
        console.warn("getNumOpenSubmissionsForOpenChallengesAdmin not available:", err);
      }

      // Get reward per challenge
      try {
        const rewardResult = await $store.gameStateCanisterActor.getRewardPerChallengeAdmin();
        if ("Ok" in rewardResult) {
          rewardPerChallenge = Number(rewardResult.Ok);
        }
      } catch (err) {
        console.warn("getRewardPerChallengeAdmin not available:", err);
      }

      // Timer action regularity - this method may not be available
      // Set a default reasonable value
      timerActionRegularity = 60; // Default to 60 seconds

      // Get recent protocol activity for additional metrics
      const recentActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();
      if ("Ok" in recentActivityResult) {
        const { challenges, winners } = recentActivityResult.Ok;
        recentChallenges = challenges?.length || 0;
        recentWinners = winners?.length || 0;
      }

    } catch (err) {
      console.error("Error loading protocol metrics:", err);
      error = "Failed to load protocol metrics";
    }
  }

  async function updateMetrics(isRefresh = false) {
    if (!isRefresh) loading = true;
    error = "";

    try {
      await loadProtocolMetrics();
    } catch (err) {
      console.error("Error updating metrics:", err);
      error = "Failed to update metrics";
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await updateMetrics();
    
    // Update metrics every 30 seconds without swapping the layout
    updateInterval = setInterval(() => updateMetrics(true), 30000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

</script>

<div class="agent-card bg-agent-surface! p-5 sm:p-6">
  <div class="relative z-1 flex items-start justify-between gap-3 mb-5">
    <div>
      <div class="flex flex-wrap items-center gap-2">
        <p class="agent-eyebrow">Protocol</p>
        <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
          <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse"></span>
          Live
        </span>
      </div>
      <h3 class="mt-1 text-base font-semibold tracking-tight text-white">{title}</h3>
      <p class="mt-0.5 text-sm text-gray-500">Burn, challenge rewards, and the next decrease</p>
    </div>
    <span class="inline-flex h-4 w-4 shrink-0 mt-1 items-center justify-center">
      {#if loading}
        <span class="h-4 w-4 border-2 border-agent-purple rounded-full border-t-transparent animate-spin"></span>
      {/if}
    </span>
  </div>

  {#if error}
    <div class="text-red-400 text-sm mb-4 p-3 bg-red-950/40 rounded-xl border border-red-500/30">
      {error}
    </div>
  {/if}

  {#if compact}
    <!-- Compact view for smaller spaces -->
    <div class="grid grid-cols-2 gap-3">
      <div class="text-center p-3 rounded-xl bg-white/3">
        <div class="text-lg font-semibold tracking-tight text-white">
          {formatLargeNumber(totalCyclesBurned)}
        </div>
        <div class="text-xs text-gray-400">Total TC Burned</div>
      </div>
      
      <div class="text-center p-3 rounded-xl bg-white/3">
        <div class="text-lg font-semibold tracking-tight text-white">
          {totalChallenges}
        </div>
        <div class="text-xs text-gray-400">Challenges</div>
      </div>
    </div>
  {:else}
    <!-- Full view -->
    <div class="grid grid-cols-1 gap-4 mb-6">
      <div class="p-4 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Total cycles burned</p>
        <p class="agent-metric-value">
          {#if loading}
            <span class="agent-metric-pulse w-[6ch]" aria-hidden="true"></span>
          {:else}
            <span class="min-w-[6ch]">{formatLargeNumber(totalCyclesBurned)}</span>
          {/if}
        </p>
        <p class="agent-metric-hint">By funnAI</p>
      </div>
      
      <!-- <div class="text-center p-4 bg-white/3 border border-white/10 rounded-xl">
        <div class="text-2xl font-semibold tracking-tight text-white">
          {totalChallenges}
        </div>
        <div class="text-sm text-gray-400">Total Challenges</div>
        <div class="text-xs text-gray-500 mt-1">Completed</div>
      </div>
      
      <div class="p-4 rounded-xl bg-white/3">
        <div class="text-2xl font-semibold tracking-tight text-white">
          {totalSubmissions}
        </div>
        <div class="text-sm text-gray-400">Total submissions</div>
        <div class="text-xs text-gray-500 mt-1">All time</div>
      </div> -->
    </div>

    <!-- Reward Structure Section -->
    <div class="flex items-center my-5">
      <span class="text-[11px] font-medium uppercase tracking-[0.14em] text-gray-500 mr-3">Reward structure</span>
      <div class="flex-1 h-px bg-white/6"></div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Per challenge</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">73.21</p>
        <p class="mt-0.5 text-xs text-gray-500">FUNNAI</p>
      </div>
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Interval</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">10</p>
        <p class="mt-0.5 text-xs text-gray-500">Minutes</p>
      </div>
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">All participants</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">45%</p>
        <p class="mt-0.5 text-xs text-gray-500">Shared equally</p>
      </div>
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">1st place</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">35%</p>
      </div>
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">2nd place</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">15%</p>
      </div>
      <div class="p-3.5 rounded-xl bg-white/3">
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">3rd place</p>
        <p class="mt-2 text-xl font-semibold tracking-tight text-white tabular-nums">5%</p>
      </div>
    </div>

    <div class="flex items-center my-5">
      <span class="text-[11px] font-medium uppercase tracking-[0.14em] text-gray-500 mr-3">Next reward decrease</span>
      <div class="flex-1 h-px bg-white/6"></div>
    </div>

    <div class="rounded-xl bg-white/3 p-4">
      <p class="text-xs text-gray-500">Sept 29, 2026 · 12pm PT / 9pm CET</p>
      <div class="mt-2 text-xl font-semibold tracking-tight text-[#c4b5fd] tabular-nums">
        <Countdown
          targetDate={new Date("2026-09-29T12:00:00-08:00")}
          format="detailed"
          className="text-[#c4b5fd]"
        />
      </div>
      <p class="mt-1 text-xs text-gray-500">until rewards decrease</p>
    </div>
  {/if}
</div> 