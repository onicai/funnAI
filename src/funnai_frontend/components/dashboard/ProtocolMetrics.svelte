<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import Countdown from "../_widgets/Countdown.svelte";

  export let title: string = "Protocol Metrics";
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

  async function updateMetrics() {
    loading = true;
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
    
    // Update metrics every 30 seconds
    updateInterval = setInterval(updateMetrics, 30000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

</script>

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      {title}
    </h3>
    <div class="flex items-center gap-2">
      {#if loading}
        <div class="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      {/if}
      <div class="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
        <div class="w-2 h-2 rounded-full bg-green-500"></div>
        <span>Live</span>
      </div>
    </div>
  </div>

  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      {error}
    </div>
  {/if}

  {#if compact}
    <!-- Compact view for smaller spaces -->
    <div class="grid grid-cols-2 gap-3">
      <div class="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div class="text-lg font-bold text-blue-600 dark:text-blue-400">
          {formatLargeNumber(totalCyclesBurned)}
        </div>
        <div class="text-xs text-gray-600 dark:text-gray-400">Total TC Burned</div>
      </div>
      
      <div class="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
        <div class="text-lg font-bold text-purple-600 dark:text-purple-400">
          {totalChallenges}
        </div>
        <div class="text-xs text-gray-600 dark:text-gray-400">Challenges</div>
      </div>
    </div>
  {:else}
    <!-- Full view -->
    <div class="grid grid-cols-1 gap-4 mb-6">
      <div class="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
          {formatLargeNumber(totalCyclesBurned)}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Cycles Burned</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">All mAIners</div>
      </div>
      
      <!-- <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
        <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
          {totalChallenges}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Challenges</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">Completed</div>
      </div>
      
      <div class="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
        <div class="text-2xl font-bold text-green-600 dark:text-green-400">
          {totalSubmissions}
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Total submissions</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">All time</div>
      </div> -->
    </div>

    <!-- Reward Structure Section -->
    <div class="flex items-center my-6">
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 mr-4">Reward Structure</span>
      <div class="flex-1 h-px bg-gradient-to-r from-gray-300 to-transparent dark:from-gray-600 dark:to-transparent"></div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
      <div class="text-center p-4 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
        <div class="text-2xl font-bold text-pink-600 dark:text-pink-400">
          181.9
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">FUNNAI</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">Reward per challenge</div>
      </div>

      <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
        <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
          35%
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">1st place</div>
        <!-- <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">Active now</div> -->
      </div>
      <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
        <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
          15%
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">2nd place</div>
      </div>
      <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
        <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
          5%
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">3rd place</div>
      </div>
      <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
        <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
          45%
        </div>
        <div class="text-sm text-gray-600 dark:text-gray-400">All participants</div>
        <div class="text-xs text-gray-500 dark:text-gray-500 mt-1">Shared equally</div>
      </div>
    </div>

    <!-- Next Reward Decrease Section -->
    <div class="flex items-center my-6">
      <span class="text-sm font-medium text-gray-700 dark:text-gray-300 mr-4">Next Reward Decrease</span>
      <div class="flex-1 h-px bg-gradient-to-r from-gray-300 to-transparent dark:from-gray-600 dark:to-transparent"></div>
    </div>
      
    <div class="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
      <div class="flex flex-col items-center space-y-2">
        <div class="text-xl font-bold text-red-600 dark:text-red-400 mt-4">
          <Countdown 
            targetDate="2025-09-28" 
            format="detailed"
            className="text-red-600 dark:text-red-400"
          />
        </div>
        <div class="text-lg text-gray-600 dark:text-gray-400">Until rewards decrease</div>
        <div class="text-sm text-gray-500 dark:text-gray-500 mt-1">Sep 28th, 2025</div>
      </div>
    </div>
  {/if}
</div> 