<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount, formatLargeNumber } from "../../helpers/utils/numberFormatUtils";

  export let title: string = "mAIner Leaderboard";
  export let maxItems: number = 10;
  export let variant: "user" | "global" = "user";

  // Conversion rate: approximately 1 ICP = 1 trillion cycles
  const CYCLES_PER_ICP = 1_000_000_000_000;

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;
  let leaderboardData: LeaderboardEntry[] = [];

  interface LeaderboardEntry {
    id: string;
    name: string;
    rank: number;
    totalRewards: string;
    firstPlaces: number;
    secondPlaces: number;
    thirdPlaces: number;
    totalSubmissions: number;
    cyclesBurned: number;
    icpSpent: number;
    isUserMainer: boolean;
  }

  function convertCyclesToIcp(cycles: number): number {
    return cycles / CYCLES_PER_ICP;
  }

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = $store.isAuthed;

  async function loadUserMainerLeaderboard() {
    if (!isAuthenticated || !agentCanisterActors || !agentCanistersInfo) {
      leaderboardData = [];
      return;
    }

    const entries: LeaderboardEntry[] = [];

    for (const [index, agent] of agentCanisterActors.entries()) {
      if (!agent) continue;

      const canisterInfo = agentCanistersInfo[index];
      if (!canisterInfo || (canisterInfo.status && 'Unlocked' in canisterInfo.status)) {
        continue; // Skip unlocked mAIners
      }

      const mainerId = canisterInfo.address;
      const mainerName = `mAIner ${mainerId?.slice(0, 5) || 'Unknown'}`;

      let totalRewards = "0";
      let firstPlaces = 0;
      let secondPlaces = 0;
      let thirdPlaces = 0;
      let totalSubmissions = 0;

      try {
        // Get recent submissions for this mAIner
        const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();
        if ("Ok" in submissionsResult) {
          totalSubmissions = submissionsResult.Ok.length;
        }

        // Get placement data from recent protocol activity
        const recentActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();
        if ("Ok" in recentActivityResult) {
          const { winners } = recentActivityResult.Ok;

          for (const winnerDeclaration of winners) {
            // Check each placement position
            if (winnerDeclaration.winner && winnerDeclaration.winner.submittedBy.toString() === mainerId) {
              firstPlaces++;
              totalRewards = (BigInt(totalRewards) + BigInt(winnerDeclaration.winner.reward.amount)).toString();
            }
            if (winnerDeclaration.secondPlace && winnerDeclaration.secondPlace.submittedBy.toString() === mainerId) {
              secondPlaces++;
              totalRewards = (BigInt(totalRewards) + BigInt(winnerDeclaration.secondPlace.reward.amount)).toString();
            }
            if (winnerDeclaration.thirdPlace && winnerDeclaration.thirdPlace.submittedBy.toString() === mainerId) {
              thirdPlaces++;
              totalRewards = (BigInt(totalRewards) + BigInt(winnerDeclaration.thirdPlace.reward.amount)).toString();
            }
          }
        }
      } catch (err) {
        console.warn(`Error loading data for mAIner ${mainerName}:`, err);
      }

      entries.push({
        id: mainerId || `mainer-${index}`,
        name: mainerName,
        rank: 0, // Will be calculated after sorting
        totalRewards,
        firstPlaces,
        secondPlaces,
        thirdPlaces,
        totalSubmissions,
        cyclesBurned: canisterInfo.burnedCycles || 0,
        icpSpent: convertCyclesToIcp(canisterInfo.burnedCycles || 0),
        isUserMainer: true,
      });
    }

    // Sort by total rewards (descending) and assign ranks
    entries.sort((a, b) => {
      const rewardsA = BigInt(a.totalRewards);
      const rewardsB = BigInt(b.totalRewards);
      if (rewardsA !== rewardsB) {
        return rewardsA > rewardsB ? -1 : 1;
      }
      // If rewards are equal, sort by first places
      if (a.firstPlaces !== b.firstPlaces) {
        return b.firstPlaces - a.firstPlaces;
      }
      // If first places are equal, sort by total submissions
      return b.totalSubmissions - a.totalSubmissions;
    });

    // Assign ranks
    entries.forEach((entry, index) => {
      entry.rank = index + 1;
    });

    // For user variant, show all mAIners; for global, limit to maxItems
    leaderboardData = variant === "user" ? entries : entries.slice(0, maxItems);
  }

  async function loadGlobalLeaderboard() {
    // For global leaderboard, we would need to fetch data from all mAIners
    // This is more complex and would require different API endpoints
    // For now, we'll show a placeholder
    leaderboardData = [];
    error = "Global leaderboard not yet implemented - requires additional backend support";
  }

  async function updateLeaderboard() {
    loading = true;
    error = "";

    try {
      if (variant === "user") {
        await loadUserMainerLeaderboard();
      } else {
        await loadGlobalLeaderboard();
      }
    } catch (err) {
      console.error("Error updating leaderboard:", err);
      error = "Failed to load leaderboard data";
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await updateLeaderboard();
    
    // Update leaderboard every 60 seconds
    updateInterval = setInterval(updateLeaderboard, 60000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  // React to authentication changes
  $: if (isAuthenticated !== undefined) {
    updateLeaderboard();
  }

  function getRankIcon(rank: number): string {
    switch (rank) {
      case 1: return "🥇";
      case 2: return "🥈";
      case 3: return "🥉";
      default: return "📍";
    }
  }

  function getRankClass(rank: number): string {
    switch (rank) {
      case 1: return "text-yellow-600 dark:text-yellow-400";
      case 2: return "text-gray-500 dark:text-gray-400";
      case 3: return "text-orange-600 dark:text-orange-400";
      default: return "text-blue-600 dark:text-blue-400";
    }
  }
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
      <span class="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
        {variant === "user" ? "My mAIners" : "Global"}
      </span>
    </div>
  </div>

  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      {error}
    </div>
  {/if}

  {#if !isAuthenticated && variant === "user"}
    <div class="text-center py-8">
      <div class="text-gray-400 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">Connect your wallet to see your mAIner leaderboard</p>
    </div>
  {:else if leaderboardData.length === 0 && !loading}
    <div class="text-center py-8">
      <div class="text-gray-400 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {variant === "user" ? "No mAIners found or no performance data available" : "Global leaderboard not yet available"}
      </p>
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="w-full min-w-full">
        <thead>
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <th class="text-left py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Rank
            </th>
            <th class="text-left py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              mAIner
            </th>
            <th class="text-right py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Total Rewards
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Participations
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              1st
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              2nd
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              3rd
            </th>
            <th class="text-right py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              ICP Spent
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          {#each leaderboardData as entry (entry.id)}
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
              <td class="py-3 px-2">
                <div class="flex items-center gap-2">
                  <span class="text-lg {getRankClass(entry.rank)}">
                    {getRankIcon(entry.rank)}
                  </span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    #{entry.rank}
                  </span>
                </div>
              </td>
              <td class="py-3 px-2">
                <div class="text-sm font-medium text-gray-900 dark:text-white">
                  {entry.name}
                </div>
              </td>
              <td class="py-3 px-2 text-right">
                <div class="text-sm font-semibold text-green-600 dark:text-green-400">
                  {formatFunnaiAmount(entry.totalRewards)} FUNNAI
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-gray-900 dark:text-white">
                  {entry.totalSubmissions}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-yellow-600 dark:text-yellow-400 font-medium">
                  {entry.firstPlaces}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-gray-500 dark:text-gray-400 font-medium">
                  {entry.secondPlaces}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-orange-600 dark:text-orange-400 font-medium">
                  {entry.thirdPlaces}
                </div>
              </td>
              <td class="py-3 px-2 text-right">
                <div class="text-sm text-blue-600 dark:text-blue-400">
                  {entry.icpSpent.toFixed(3)} ICP
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div> 