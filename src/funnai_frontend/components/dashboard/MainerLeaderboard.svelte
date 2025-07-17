<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount, formatLargeNumber, formatBalance } from "../../helpers/utils/numberFormatUtils";
  import { FUNNAI_CANISTER_ID } from "../../helpers/token_helpers";
  import { walletDataStore, WalletDataService } from "../../helpers/WalletDataService";

  export let title: string = "My mAIners leaderboard";
  export let maxItems: number = 10;
  export let variant: "user" | "global" = "user";

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;
  let leaderboardData: LeaderboardEntry[] = [];
  let walletInitialized = false;
  
  // Minimum FUNNAI tokens required to access leaderboard
  const MIN_FUNNAI_REQUIRED = 100;
  
  // Wallet data subscription
  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  interface LeaderboardEntry {
    id: string;
    name: string;
    rank: number;
    totalSubmissions: number;
    recentSubmissions: number;
    averageScore: number;
    bestScore: number;
    participations: number;
    winnings: string;
    cyclesBurned: number;
    isUserMainer: boolean;
  }

  async function initializeWalletIfNeeded(): Promise<void> {
    if (walletInitialized || !$store.principal || $store.principal.toString() === "anonymous") {
      return;
    }

    try {
      const principalId = $store.principal.toString();
      console.log("Initializing wallet for mAIner leaderboard:", principalId);
      await WalletDataService.initializeWallet(principalId);
      walletInitialized = true;
      loadedFunnaiBalance = getUserFunnaiBalance();
    } catch (err) {
      console.warn("Error initializing wallet for leaderboard:", err);
    }
  }

  function getUserFunnaiBalance(): number {
    // If wallet data is still loading, return 0 (user will see loading state)
    if (!walletData || walletData.isLoading) {
      return 0;
    }
    
    // If no balances or wallet not initialized, return 0
    if (!walletData.balances) {
      return 0;
    }
    
    const funnaiBalance = walletData.balances[FUNNAI_CANISTER_ID];
    
    if (funnaiBalance && funnaiBalance.in_tokens) {
      // Convert bigint balance to number using formatBalance
      const decimals = 8; // FUNNAI token decimals
      const formattedBalance = formatBalance(funnaiBalance.in_tokens.toString(), decimals);
      return parseFloat(formattedBalance.replace(/,/g, ''));
    }
    
    return 0;
  }

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = $store.isAuthed;
  
  // Check if user has enough FUNNAI tokens
  let loadedFunnaiBalance = getUserFunnaiBalance();
  $: userFunnaiBalance = loadedFunnaiBalance;
  $: hasEnoughFunnai = userFunnaiBalance >= MIN_FUNNAI_REQUIRED;
  $: isWalletLoading = walletData && walletData.isLoading;
  $: canAccessLeaderboard = isAuthenticated && hasEnoughFunnai;
  $: shouldShowLoadingForWallet = isAuthenticated && (isWalletLoading || !walletInitialized);

  async function loadUserMainerLeaderboard() {
    if (!canAccessLeaderboard || !agentCanisterActors || !agentCanistersInfo) {
      leaderboardData = [];
      return;
    }

    const entries: LeaderboardEntry[] = [];

    // First, get recent protocol activity to identify participated challenges and winners
    let recentActivityResult;
    let participatedChallenges: Set<string> = new Set();
    let winnersByMainer: Map<string, { total: string; count: number }> = new Map();

    try {
      recentActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();
      if ("Ok" in recentActivityResult) {
        const { winners } = recentActivityResult.Ok;

        // Process winners to calculate rewards by mAIner
        for (const winnerDeclaration of winners) {
          const allPlacements = [
            { entry: winnerDeclaration.winner, multiplier: 1 },
            { entry: winnerDeclaration.secondPlace, multiplier: 0.5 },
            { entry: winnerDeclaration.thirdPlace, multiplier: 0.25 }
          ].filter(p => p.entry);

          for (const { entry, multiplier } of allPlacements) {
            if (entry) {
              const mainerId = entry.submittedBy.toString();
              const reward = BigInt(entry.reward.amount);
              const existingData = winnersByMainer.get(mainerId);
              if (existingData) {
                existingData.total = (BigInt(existingData.total) + reward).toString();
                existingData.count += 1;
              } else {
                winnersByMainer.set(mainerId, {
                  total: reward.toString(),
                  count: 1
                });
              }
            }
          }
        }
      }
    } catch (err) {
      console.warn("Error loading recent protocol activity:", err);
    }

    // Process each mAIner
    for (const [index, agent] of agentCanisterActors.entries()) {
      if (!agent) continue;

      const canisterInfo = agentCanistersInfo[index];
      if (!canisterInfo || (canisterInfo.status && 'Unlocked' in canisterInfo.status)) {
        continue; // Skip unlocked mAIners
      }

      const mainerId = canisterInfo.address;
              const mainerName = `${mainerId?.slice(0, 5) || 'Unknown'}`;

      let totalSubmissions = 0;
      let recentSubmissions = 0;
      let scores: number[] = [];
      let participations = 0;

      try {
        // Get all submissions for accurate total count
        try {
          const allSubmissionsResult = await agent.getSubmittedResponsesAdmin();
          if ("Ok" in allSubmissionsResult) {
            totalSubmissions = allSubmissionsResult.Ok.length;
            
            // Get scores for recent submissions to calculate averages
            const submissions = allSubmissionsResult.Ok.slice(-10); // Last 10 for performance
            for (const submission of submissions) {
              participatedChallenges.add(submission.challengeId);
              
              try {
                const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission({
                  challengeId: submission.challengeId,
                  submissionId: submission.submissionId,
                });

                if ("Ok" in scoreResult) {
                  scores.push(Number(scoreResult.Ok.score));
                }
              } catch (scoreError) {
                console.warn(`Error getting score for submission ${submission.submissionId}:`, scoreError);
              }
            }
          }
        } catch (err) {
          console.warn(`Error getting all submissions for ${mainerName}:`, err);
        }

        // Get recent submissions count
        try {
          const recentSubmissionsResult = await agent.getRecentSubmittedResponsesAdmin();
          if ("Ok" in recentSubmissionsResult) {
            recentSubmissions = recentSubmissionsResult.Ok.length;
          }
        } catch (err) {
          console.warn(`Error getting recent submissions for ${mainerName}:`, err);
        }

        // Calculate participation count from participated challenges
        participations = participatedChallenges.size;

      } catch (err) {
        console.warn(`Error loading data for mAIner ${mainerName}:`, err);
      }

      // Calculate statistics
      const averageScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
      const bestScore = scores.length > 0 ? Math.max(...scores) : 0;
      
      // Get winnings for this mAIner
      const winnerData = winnersByMainer.get(mainerId);
      const winnings = winnerData ? winnerData.total : "0";

      entries.push({
        id: mainerId || `mainer-${index}`,
        name: mainerName,
        rank: 0, // Will be calculated after sorting
        totalSubmissions,
        recentSubmissions,
        averageScore: Math.round(averageScore * 100) / 100, // Round to 2 decimal places
        bestScore,
        participations,
        winnings,
        cyclesBurned: canisterInfo.burnedCycles || 0,
        isUserMainer: true,
      });
    }

    // Sort by a combination of factors: winnings first, then average score, then total submissions
    entries.sort((a, b) => {
      const winningsA = BigInt(a.winnings);
      const winningsB = BigInt(b.winnings);
      
      if (winningsA !== winningsB) {
        return winningsA > winningsB ? -1 : 1;
      }
      
      // If winnings are equal, sort by average score
      if (a.averageScore !== b.averageScore) {
        return b.averageScore - a.averageScore;
      }
      
      // If average scores are equal, sort by total submissions
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
    // Initialize wallet if user is already authenticated
    if (isAuthenticated) {
      await initializeWalletIfNeeded();
    }
    await updateLeaderboard();
    
    // Update leaderboard every 60 seconds
    updateInterval = setInterval(async () => {
      // Ensure wallet is initialized before each update
      if (isAuthenticated) {
        await initializeWalletIfNeeded();
      }
      await updateLeaderboard();
    }, 60000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
    // Reset initialization flag on component destruction
    walletInitialized = false;
  });

  // React to authentication and balance changes
  $: if (isAuthenticated !== undefined) {
    if (isAuthenticated) {
      // Reset wallet initialization flag when authentication state changes
      walletInitialized = false;
      initializeWalletIfNeeded().then(() => {
        updateLeaderboard();
      });
    } else {
      // Clear wallet data when user logs out
      walletInitialized = false;
      updateLeaderboard();
    }
  }
  
  // React to wallet data changes (balances loading)
  $: if (walletData && userFunnaiBalance !== undefined) {
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
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Connect your wallet to see your mAIner leaderboard</p>
      <p class="text-xs text-gray-400 dark:text-gray-500">
        Requires at least {MIN_FUNNAI_REQUIRED} FUNNAI tokens
      </p>
    </div>
  {:else if isAuthenticated && shouldShowLoadingForWallet && variant === "user"}
    <div class="text-center py-8">
      <div class="text-blue-400 mb-2">
        <div class="animate-spin h-8 w-8 mx-auto border-4 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
        Loading wallet data...
      </p>
      <p class="text-xs text-gray-400 dark:text-gray-500">
        Checking FUNNAI balance for leaderboard access
      </p>
    </div>
  {:else if isAuthenticated && !hasEnoughFunnai && !shouldShowLoadingForWallet && variant === "user"}
    <div class="text-center py-8">
      <div class="text-orange-400 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
      </div>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">
        You need at least {MIN_FUNNAI_REQUIRED} FUNNAI tokens to access the mAIner leaderboard
      </p>
      <p class="text-xs text-gray-400 dark:text-gray-500">
        Your balance: {userFunnaiBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })} FUNNAI
      </p>
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
              Winnings
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Avg Score
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Best Score
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Submissions
            </th>
            <th class="text-center py-3 px-2 text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
              Recent
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
                  {formatFunnaiAmount(entry.winnings)} FUNNAI
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-gray-900 dark:text-white">
                  {entry.averageScore > 0 ? entry.averageScore.toFixed(1) : "—"}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-blue-600 dark:text-blue-400 font-medium">
                  {entry.bestScore > 0 ? entry.bestScore : "—"}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-gray-900 dark:text-white">
                  {entry.totalSubmissions}
                </div>
              </td>
              <td class="py-3 px-2 text-center">
                <div class="text-sm text-orange-600 dark:text-orange-400">
                  {entry.recentSubmissions}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div> 