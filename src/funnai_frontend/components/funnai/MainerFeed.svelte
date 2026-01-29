<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { fly } from "svelte/transition";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount } from "../../helpers/utils/numberFormatUtils";
  import { ActivityFeedService, type ActivityFeedItem, type ActivityFeedResponse, type Challenge } from "../../helpers/ActivityFeedService";
  import ShareFeedItem from "./ShareFeedItem.svelte";

  export let showAllEvents: boolean = true;

  // State
  let feedItems: ActivityFeedItem[] = [];
  let loading = true;
  let updating = false;
  let error = "";
  let updateInterval: ReturnType<typeof setInterval>;

  // ============================================================================
  // Formatting Helpers
  // ============================================================================

  function formatTimestamp(timestamp: bigint): { date: string; time: string } {
    return ActivityFeedService.formatTimestamp(timestamp);
  }

  function getStatusColor(type: string): string {
    switch (type) {
      case "challenge":
        return "before:bg-blue-500";
      case "winner":
        return "before:bg-gradient-to-r before:from-yellow-400 before:to-yellow-600 before:shadow-lg before:shadow-yellow-500/50";
      case "second_place":
        return "before:bg-gray-400";
      case "third_place":
        return "before:bg-orange-500";
      case "participation":
        return "before:bg-green-500";
      default:
        return "before:bg-gray-500";
    }
  }

  function getWinnerStyling(type: string): string {
    switch (type) {
      case "winner":
        return "bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-300 shadow-lg shadow-yellow-500/20 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-600";
      case "second_place":
        return "bg-gradient-to-r from-gray-50 to-slate-50 border-2 border-gray-300 shadow-lg shadow-gray-500/20 dark:from-gray-800/20 dark:to-slate-800/20 dark:border-gray-600";
      case "third_place":
        return "bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 shadow-lg shadow-orange-500/20 dark:from-orange-900/20 dark:to-amber-900/20 dark:border-orange-600";
      default:
        return "";
    }
  }

  function getWinnerIcon(type: string): string {
    switch (type) {
      case "winner":
        return "🏆";
      case "second_place":
        return "🥈";
      case "third_place":
        return "🥉";
      default:
        return "🏅";
    }
  }

  function getPlacementText(type: string): string {
    switch (type) {
      case "winner":
        return "First Place";
      case "second_place":
        return "Second Place";
      case "third_place":
        return "Third Place";
      default:
        return "";
    }
  }

  function getMainerName(address: string | undefined): string {
    if (!address) return "Unknown";
    return `mAIner ${address.slice(0, 5)}`;
  }

  function isWinnerType(type: string): boolean {
    return type === "winner" || type === "second_place" || type === "third_place";
  }

  // ============================================================================
  // Data Fetching
  // ============================================================================

  async function loadFeed(forceRefresh = false) {
    if (forceRefresh) {
      ActivityFeedService.clearCache();
    }

    updating = true;
    error = "";

    try {
      if (showAllEvents) {
        // All Events tab: show open challenges + winner announcements
        const [openChallenges, activityFeed] = await Promise.all([
          ActivityFeedService.fetchOpenChallenges(),
          ActivityFeedService.fetchActivityFeed({
            winnersLimit: 50,
            challengesLimit: 0, // We get challenges from getOpenChallengesFromCache instead
          }),
        ]);

        // Convert open challenges to feed items
        const challengeItems: ActivityFeedItem[] = openChallenges.map((c: Challenge) => ({
          id: `challenge-${c.challengeId}`,
          timestamp: c.challengeCreationTimestamp,
          type: "challenge" as const,
          challengeId: c.challengeId,
          challengeQuestion: c.challengeQuestion,
          challengeTopic: c.challengeTopic,
        }));

        // Convert winner declarations to feed items
        const winnerItems = ActivityFeedService.toFeedItems(activityFeed).filter(
          item => item.type !== "challenge" // Only winners, not challenges
        );

        // Merge and sort by timestamp (newest first)
        feedItems = [...challengeItems, ...winnerItems].sort((a, b) => {
          const aTime = Number(a.timestamp);
          const bTime = Number(b.timestamp);
          return bTime - aTime;
        });
      } else {
        // My Mainers tab: No API data available yet
        feedItems = [];
      }
    } catch (err) {
      console.error("Error loading feed:", err);
      error = "Failed to load activity feed";
    } finally {
      loading = false;
      updating = false;
    }
  }

  // ============================================================================
  // Lifecycle
  // ============================================================================

  onMount(async () => {
    await loadFeed();
    
    // Refresh every 30 seconds
    updateInterval = setInterval(() => {
      loadFeed();
    }, 30000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  // Reload when tab changes
  $: if (showAllEvents !== undefined) {
    loading = true;
    feedItems = [];
    loadFeed(true);
  }
</script>

<div class="h-full dark:bg-gray-800 dark:text-white flex flex-col" style="overflow-y: auto; overflow-x: visible;">
  <!-- Loading indicator -->
  <div class="flex justify-center py-2 transition-opacity duration-300 {updating ? 'opacity-100' : 'opacity-0 pointer-events-none'}">
    <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent dark:border-blue-400"></div>
  </div>

  <!-- Error display -->
  {#if error}
    <div class="mx-4 mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
      {error}
      <button 
        on:click={() => loadFeed(true)} 
        class="ml-2 underline hover:no-underline"
      >
        Retry
      </button>
    </div>
  {/if}

  <!-- Empty state for My Mainers tab (no API data yet) -->
  {#if !showAllEvents && !loading}
    <div class="flex-1 flex flex-col justify-center items-center px-4 py-6">
      <div class="flex flex-col items-center gap-4 text-gray-500 dark:text-gray-400">
        <div class="text-6xl">🤖</div>
        <div class="max-w-md text-center">
          <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            My mAIners Activity
          </h3>
          <p class="text-sm leading-relaxed mb-4">
            This tab will show activity specific to your mAIners:
          </p>
          <ul class="text-sm space-y-1 text-left">
            <li>• 🏆 Your mAIners' victories and placements</li>
            <li>• 🎯 Challenges your mAIners participated in</li>
            <li>• 💰 Rewards earned by your mAIners</li>
          </ul>
          <p class="text-xs mt-4 text-gray-400 dark:text-gray-500 italic">
            Coming soon - this feature is under development.
          </p>
        </div>
      </div>
    </div>
  {/if}

  <!-- Empty state for All Events tab -->
  {#if showAllEvents && feedItems.length === 0 && !loading && !updating}
    <div class="flex-1 flex flex-col justify-center items-center px-4 py-6">
      <div class="flex flex-col items-center gap-4 text-gray-500 dark:text-gray-400">
        <div class="text-6xl">📡</div>
        <div class="max-w-md text-center">
          <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            Protocol Activity Feed
          </h3>
          <p class="text-sm leading-relaxed">
            No recent activity in the protocol.
          </p>
          <p class="text-xs mt-4 text-gray-400 dark:text-gray-500">
            Open challenges and winner announcements will appear here.
          </p>
        </div>
      </div>
    </div>
  {/if}

  <!-- Feed items (only for All Events tab) -->
  {#if showAllEvents && (feedItems.length > 0 || loading)}
    <ul 
      aria-label="Protocol Activity feed" 
      role="feed" 
      class="relative flex flex-col gap-8 py-12 pl-6 text-sm 
             before:absolute before:top-0 before:z-0 before:left-6 before:h-full before:border-2 before:-translate-x-1/2 before:border-slate-400 before:border-dashed dark:before:border-slate-400"
    >
      {#if feedItems.length === 0 && loading}
        <li class="text-center py-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Loading activity...
          </p>
        </li>
      {:else}
        {#each feedItems as item (item.id)}
          <li 
            role="article" 
            class="relative px-6 
                   before:absolute before:z-[1] before:left-0 before:top-2 before:h-3 before:w-3 before:-translate-x-1/2 before:rounded-full {getStatusColor(item.type)} before:ring-2 before:ring-white dark:before:ring-gray-900 before:shadow-sm"
            in:fly="{{ y: 20, duration: 500 }}"
          >
            <div class="flex flex-col flex-1 gap-2 {isWinnerType(item.type) ? getWinnerStyling(item.type) + ' p-4 rounded-lg animate-pulse-winner' : ''}">
              <h4
                class="text-base font-medium flex justify-between items-center mr-6 text-gray-900 dark:text-gray-100
                       {isWinnerType(item.type) ? 'text-lg font-bold' : ''}"
              >
                <span class="flex items-center gap-2">
                  {#if isWinnerType(item.type)}
                    <span class="text-2xl animate-bounce-10s">{getWinnerIcon(item.type)}</span>
                  {/if}
                  {item.type === "challenge" ? "Protocol" : getMainerName(item.mainerAddress)}
                  {#if isWinnerType(item.type)}
                    <span class="text-2xl animate-bounce-10s">{getWinnerIcon(item.type)}</span>
                  {/if}
                </span>
                <div class="flex items-center gap-2">
                  <div class="text-2xs font-bold text-slate-600 dark:text-slate-300 text-right opacity-60">
                    <div>{formatTimestamp(item.timestamp).date}</div>
                    <div class="opacity-40">{formatTimestamp(item.timestamp).time}</div>
                  </div>
                  <ShareFeedItem feedItem={{
                    id: item.id,
                    timestamp: Number(item.timestamp),
                    type: isWinnerType(item.type) ? "winner" : item.type === "participation" ? "participation" : "challenge",
                    mainerName: item.type === "challenge" ? "Protocol" : getMainerName(item.mainerAddress),
                    content: {
                      challenge: item.challengeQuestion,
                      placement: getPlacementText(item.type),
                      reward: item.reward?.toString()
                    }
                  }} />
                </div>
              </h4>
              
              {#if item.type === "challenge"}
                <p class="text-slate-600 dark:text-slate-300 pr-6">
                  New challenge: <span class="font-medium text-gray-800 dark:text-gray-200">{item.challengeQuestion}</span>
                </p>
              {:else if isWinnerType(item.type)}
                <div class="{showAllEvents ? '' : 'text-center'}">
                  {#if !showAllEvents}
                    <!-- Personal congratulations for My Mainers tab -->
                    <p class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-amber-600 dark:from-yellow-400 dark:to-amber-400 mb-2">
                      🎉 CONGRATULATIONS! 🎉
                    </p>
                  {/if}
                  <p class="text-slate-700 dark:text-slate-200">
                    {#if showAllEvents}
                      <!-- Neutral announcement for All Events tab -->
                      Won <span class="font-bold {item.type === 'winner' ? 'text-yellow-600 dark:text-yellow-400' : item.type === 'second_place' ? 'text-gray-600 dark:text-gray-400' : 'text-orange-600 dark:text-orange-400'}">{getPlacementText(item.type)}</span>{#if item.reward} and earned <span class="font-semibold text-green-600 dark:text-green-400">{formatFunnaiAmount(item.reward.toString())} FUNNAI</span>{/if}
                    {:else}
                      <!-- Personal message for My Mainers tab -->
                      Achieved <span class="font-bold text-lg {item.type === 'winner' ? 'text-yellow-600 dark:text-yellow-400' : item.type === 'second_place' ? 'text-gray-600 dark:text-gray-400' : 'text-orange-600 dark:text-orange-400'}">{getPlacementText(item.type)}</span>
                    {/if}
                  </p>
                  {#if !showAllEvents && item.reward}
                    <p class="text-slate-700 dark:text-slate-200">
                      and earned <span class="font-bold text-lg text-green-600 dark:text-green-400">{formatFunnaiAmount(item.reward.toString())} FUNNAI</span>
                    </p>
                  {/if}
                </div>
              {:else if item.type === "participation"}
                <p class="text-slate-600 dark:text-slate-300 pr-6">
                  🎯 Earned participation reward: <span class="font-semibold text-blue-600 dark:text-blue-400">{formatFunnaiAmount(item.reward?.toString() || '0')} FUNNAI</span>
                </p>
              {/if}
            </div>
          </li>
        {/each}
      {/if}
    </ul>
  {/if}
</div>

<style>
  /* Custom text size smaller than text-xs */
  .text-2xs {
    font-size: 0.625rem; /* 10px */
    line-height: 0.75rem; /* 12px */
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes pulseWinner {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7);
    }
    50% {
      box-shadow: 0 0 0 10px rgba(251, 191, 36, 0);
    }
  }

  @keyframes bounce10s {
    0%, 100% {
      transform: translateY(-25%);
      animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
    }
    50% {
      transform: none;
      animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.5s ease-out forwards;
  }

  .animate-bounce-10s {
    animation: bounce10s 1s ease-in-out 10;
  }

  .animate-pulse-winner {
    animation: pulseWinner 2s 5;
  }

  /* Dark mode adjustments */
  :global(.dark) .animate-spin {
    border-color: rgba(96, 165, 250, 0.8);
    border-top-color: transparent;
  }

  /* Enhanced winner glow for dark mode */
  :global(.dark) .animate-pulse-winner {
    box-shadow: 0 0 22px rgba(251, 191, 36, 0.3);
  }
</style>
