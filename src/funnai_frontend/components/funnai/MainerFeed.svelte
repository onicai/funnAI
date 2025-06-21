<script lang="ts">
  import { Principal } from "@dfinity/principal";

  import { onMount } from "svelte";
  import { fly } from "svelte/transition";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount } from "../../helpers/utils/numberFormatUtils";
  import ShareFeedItem from "./ShareFeedItem.svelte";

  export let showAllEvents: boolean = false;

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;

  interface FeedItem {
    id: string;
    timestamp: number;
    type: "challenge" | "response" | "score" | "winner";
    mainerName: string;
    content: {
      challenge?: string;
      response?: string;
      score?: number;
      placement?: string;
      reward?: string;
    };
  }

  let feedItems: FeedItem[] = [];
  let allItems: FeedItem[] = [];
  let loading = true;
  let interval: NodeJS.Timer;
  let currentIndex = 0;
  let updating = false;
  let updateCounter = 0;
  let lastFetchTimestamp = 0;

  // Storage keys for persistence
  const FEED_STORAGE_KEY = 'mainer_feed_items';
  const LAST_FETCH_KEY = 'mainer_feed_last_fetch';

  // Smart date filtering
  function isWithinDateRange(timestamp: number, days: number): boolean {
    const now = Date.now();
    const itemTime = timestamp / 1000000; // Convert from nanoseconds to milliseconds
    const daysDiff = (now - itemTime) / (24 * 60 * 60 * 1000);
    return daysDiff <= days && daysDiff >= 0; // Also ensure not future dates
  }

  function shouldFilterByDate(filterToUserMainers: boolean): boolean {
    // For "my mainers only" mode, don't filter by date - show all events
    return !filterToUserMainers;
  }

  function filterItemsByDate(items: FeedItem[], days: number = 3): FeedItem[] {
    return items.filter(item => isWithinDateRange(item.timestamp, days));
  }

  // Load cached feed items from localStorage
  function loadCachedFeedItems(): FeedItem[] {
    try {
      const cached = localStorage.getItem(FEED_STORAGE_KEY);
      if (cached) {
        const items = JSON.parse(cached) as FeedItem[];
        // Filter cached items to only include those from last 3 days
        return filterItemsByDate(items);
      }
    } catch (error) {
      console.error('Error loading cached feed items:', error);
    }
    return [];
  }

  // Save feed items to localStorage
  function saveFeedItemsToCache(items: FeedItem[]) {
    try {
      // Only save items from last 3 days to keep storage lean
      const recentItems = filterItemsByDate(items);
      localStorage.setItem(FEED_STORAGE_KEY, JSON.stringify(recentItems));
      localStorage.setItem(LAST_FETCH_KEY, Date.now().toString());
    } catch (error) {
      console.error('Error saving feed items to cache:', error);
    }
  }

  // Get the last fetch timestamp
  function getLastFetchTimestamp(): number {
    try {
      const cached = localStorage.getItem(LAST_FETCH_KEY);
      return cached ? parseInt(cached) : 0;
    } catch (error) {
      console.error('Error loading last fetch timestamp:', error);
      return 0;
    }
  }

  // Merge new items with existing ones, avoiding duplicates
  function mergeItems(existingItems: FeedItem[], newItems: FeedItem[]): FeedItem[] {
    const existingIds = new Set(existingItems.map(item => item.id));
    const uniqueNewItems = newItems.filter(item => !existingIds.has(item.id));
    const merged = [...existingItems, ...uniqueNewItems];
    
    // Sort by timestamp (items are already filtered by date in getFeedData)
    return sortFeedItemsByTimestamp(merged);
  }

  // Convert timestamp to readable date and time format
  function formatTimestamp(timestamp: number): { date: string; time: string } {
    // IC timestamps are typically in nanoseconds, convert to milliseconds
    const milliseconds = timestamp / 1000000;
    const dateObj = new Date(milliseconds);
    
    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      return { date: "Invalid", time: "Date" };
    }
    
    const date = dateObj.toLocaleDateString([], {
      month: "2-digit",
      day: "2-digit",
      year: "2-digit",
    });
    
    const time = dateObj.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    
    return { date, time };
  }

  function getStatusColor(type: string): string {
    switch (type) {
      case "challenge":
        return "before:bg-blue-500";
      case "response":
        return "before:bg-purple-500";
      case "score":
        return "before:bg-orange-500";
      case "winner":
        return "before:bg-gradient-to-r before:from-yellow-400 before:to-yellow-600 before:shadow-lg before:shadow-yellow-500/50";
      default:
        return "before:bg-gray-500";
    }
  }

  function getWinnerStyling(placement: string): string {
    switch (placement) {
      case "First Place":
        return "bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-300 shadow-lg shadow-yellow-500/20 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-600";
      case "Second Place":
        return "bg-gradient-to-r from-gray-50 to-slate-50 border-2 border-gray-300 shadow-lg shadow-gray-500/20 dark:from-gray-800/20 dark:to-slate-800/20 dark:border-gray-600";
      case "Third Place":
        return "bg-gradient-to-r from-orange-50 to-amber-50 border-2 border-orange-300 shadow-lg shadow-orange-500/20 dark:from-orange-900/20 dark:to-amber-900/20 dark:border-orange-600";
      default:
        return "";
    }
  }

  function getWinnerIcon(placement: string): string {
    switch (placement) {
      case "First Place":
        return "🏆";
      case "Second Place":
        return "🥈";
      case "Third Place":
        return "🥉";
      default:
        return "🏅";
    }
  }

  function sortFeedItemsByTimestamp(feedItems: FeedItem[]): FeedItem[] {
    return feedItems.sort((a, b) => b.timestamp - a.timestamp);
  }

  async function getFeedData(filterToUserMainers: boolean = false): Promise<FeedItem[]> {
    // Helper function to get items with specific date filtering
    async function getItemsWithDateFilter(dayRange: number | null): Promise<FeedItem[]> {
      let newFeedItems: FeedItem[] = [];
      let userParticipatedChallenges: Set<string> = new Set();

      try {
        let recentProtocolActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();

        if ("Ok" in recentProtocolActivityResult && $store.isAuthed) {
          const { challenges, winners } = recentProtocolActivityResult.Ok;

          if (filterToUserMainers) {
            // Collect challenge IDs that user's mAIners have participated in
            for (const [index, agent] of agentCanisterActors.entries()) {
              if (agent) {
                try {
                  const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();
                  if ("Ok" in submissionsResult) {
                    for (const submission of submissionsResult.Ok) {
                      userParticipatedChallenges.add(submission.challengeId);
                    }
                  }
                } catch (error) {
                  console.error("Error fetching submissions for challenge filtering", error);
                }
              }
            }
          }

          // Add challenges
          challenges.forEach((challenge) => {
            const challengeTimestamp = Number(challenge.challengeCreationTimestamp);
            const passesDateFilter = dayRange === null || isWithinDateRange(challengeTimestamp, dayRange);
            const passesUserFilter = !filterToUserMainers || userParticipatedChallenges.has(challenge.challengeId);
            
            if (passesDateFilter && passesUserFilter) {
              newFeedItems.push({
                id: challenge.challengeId,
                timestamp: challengeTimestamp,
                type: "challenge",
                mainerName: "Protocol",
                content: { challenge: challenge.challengeQuestion },
              });
            }
          });

          // Add winners
          winners.forEach((winnerDeclaration) => {
            const winnerTimestamp = Number(winnerDeclaration.finalizedTimestamp);
            const passesDateFilter = dayRange === null || isWithinDateRange(winnerTimestamp, dayRange);
            
            if (!passesDateFilter) {
              return;
            }

            // Only add winner events for "My mAIners only" feed (when filterToUserMainers is true)
            if (!filterToUserMainers) {
              return;
            }

            const placements = [
              { position: "First Place", entry: winnerDeclaration.winner },
              { position: "Second Place", entry: winnerDeclaration.secondPlace },
              ...(winnerDeclaration.thirdPlace
                ? [{ position: "Third Place", entry: winnerDeclaration.thirdPlace }]
                : []),
            ];

            placements.forEach(({ position, entry }) => {
              const mainerIndex = agentCanistersInfo.findIndex(
                (agent) => agent.address === entry.submittedBy.toString(),
              );
              
              if (!filterToUserMainers || mainerIndex !== -1) {
                const mainerName = mainerIndex !== -1 
                  ? `mAIner ${entry.submittedBy.toString().slice(0, 5)}` 
                  : `mAIner ${entry.submittedBy.toString().slice(0, 5)}`;

                newFeedItems.push({
                  id: `${entry.submissionId}-winner`,
                  timestamp: winnerTimestamp,
                  type: "winner",
                  mainerName,
                  content: {
                    placement: position,
                    reward: entry.reward.amount.toString(),
                  },
                });
              }
            });
          });
        }

        // Add user mainer data if authenticated
        if ($store.isAuthed) {
          try {
            for (const [index, agent] of agentCanisterActors.entries()) {
              if (agent) {
                try {
                  const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();

                  if ("Ok" in submissionsResult) {
                    for (const submission of submissionsResult.Ok) {
                      const submissionTimestamp = Number(submission.submittedTimestamp);
                      
                      // Apply date filtering only if dayRange is specified
                      const passesDateFilter = dayRange === null || isWithinDateRange(submissionTimestamp, dayRange);
                      if (!passesDateFilter) {
                        continue;
                      }

                      const mainerName = `mAIner ${agentCanistersInfo[index].address.slice(0, 5)}`;
                      newFeedItems.push({
                        id: submission.submissionId,
                        timestamp: submissionTimestamp,
                        type: "response",
                        mainerName,
                        content: { response: submission.challengeAnswer },
                      });

                      // Get score for this submission
                      try {
                        const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission({
                          challengeId: submission.challengeId,
                          submissionId: submission.submissionId,
                        });

                        if ("Ok" in scoreResult) {
                          const judgedTimestamp = Number(scoreResult.Ok.judgedTimestamp);
                          const scorePassesDateFilter = dayRange === null || isWithinDateRange(judgedTimestamp, dayRange);
                          
                          if (scorePassesDateFilter) {
                            newFeedItems.push({
                              id: `${submission.submissionId}-score`,
                              timestamp: judgedTimestamp,
                              type: "score",
                              mainerName,
                              content: { score: Number(scoreResult.Ok.score) },
                            });
                          }
                        }
                      } catch (error) {
                        console.error("Error fetching score for submission", error);
                      }
                    }
                  }
                } catch (error) {
                  console.error("Error fetching submissions", error);
                }
              }
            }
          } catch (error) {
            console.error("Error fetching user mainer data:", error);
          }
        }
      } catch (error) {
        console.error("Error fetching protocol activity:", error);
      }

      return newFeedItems;
    }

    // Helper function to get latest items regardless of age (fallback)
    async function getLatestItemsRegardlessOfAge(maxItems: number): Promise<FeedItem[]> {
      let newFeedItems: FeedItem[] = [];
      let userParticipatedChallenges: Set<string> = new Set();

      try {
        let recentProtocolActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();

        if ("Ok" in recentProtocolActivityResult && $store.isAuthed) {
          const { challenges, winners } = recentProtocolActivityResult.Ok;

          if (filterToUserMainers) {
            // Collect challenge IDs that user's mAIners have participated in
            for (const [index, agent] of agentCanisterActors.entries()) {
              if (agent) {
                try {
                  const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();
                  if ("Ok" in submissionsResult) {
                    for (const submission of submissionsResult.Ok) {
                      userParticipatedChallenges.add(submission.challengeId);
                    }
                  }
                } catch (error) {
                  console.error("Error fetching submissions for challenge filtering", error);
                }
              }
            }
          }

          // Add challenges without date filtering
          challenges.forEach((challenge) => {
            const challengeTimestamp = Number(challenge.challengeCreationTimestamp);
            const passesUserFilter = !filterToUserMainers || userParticipatedChallenges.has(challenge.challengeId);
            
            if (passesUserFilter) {
              newFeedItems.push({
                id: challenge.challengeId,
                timestamp: challengeTimestamp,
                type: "challenge",
                mainerName: "Protocol",
                content: { challenge: challenge.challengeQuestion },
              });
            }
          });

          // Add winners without date filtering
          winners.forEach((winnerDeclaration) => {
            const winnerTimestamp = Number(winnerDeclaration.finalizedTimestamp);

            // Only add winner events for "My mAIners only" feed (when filterToUserMainers is true)
            if (!filterToUserMainers) {
              return;
            }

            const placements = [
              { position: "First Place", entry: winnerDeclaration.winner },
              { position: "Second Place", entry: winnerDeclaration.secondPlace },
              ...(winnerDeclaration.thirdPlace
                ? [{ position: "Third Place", entry: winnerDeclaration.thirdPlace }]
                : []),
            ];

            placements.forEach(({ position, entry }) => {
              const mainerIndex = agentCanistersInfo.findIndex(
                (agent) => agent.address === entry.submittedBy.toString(),
              );
              
              if (!filterToUserMainers || mainerIndex !== -1) {
                const mainerName = mainerIndex !== -1 
                  ? `mAIner ${entry.submittedBy.toString().slice(0, 5)}` 
                  : `mAIner ${entry.submittedBy.toString().slice(0, 5)}`;

                newFeedItems.push({
                  id: `${entry.submissionId}-winner`,
                  timestamp: winnerTimestamp,
                  type: "winner",
                  mainerName,
                  content: {
                    placement: position,
                    reward: entry.reward.amount.toString(),
                  },
                });
              }
            });
          });

          // Add user mainer data if authenticated (without date filtering)
          if ($store.isAuthed) {
            try {
              for (const [index, agent] of agentCanisterActors.entries()) {
                if (agent) {
                  try {
                    const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();

                    if ("Ok" in submissionsResult) {
                      for (const submission of submissionsResult.Ok) {
                        const submissionTimestamp = Number(submission.submittedTimestamp);
                        const mainerName = `mAIner ${agentCanistersInfo[index].address.slice(0, 5)}`;
                        
                        newFeedItems.push({
                          id: submission.submissionId,
                          timestamp: submissionTimestamp,
                          type: "response",
                          mainerName,
                          content: { response: submission.challengeAnswer },
                        });

                        // Get score for this submission
                        try {
                          const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission({
                            challengeId: submission.challengeId,
                            submissionId: submission.submissionId,
                          });

                          if ("Ok" in scoreResult) {
                            const judgedTimestamp = Number(scoreResult.Ok.judgedTimestamp);
                            
                            newFeedItems.push({
                              id: `${submission.submissionId}-score`,
                              timestamp: judgedTimestamp,
                              type: "score",
                              mainerName,
                              content: { score: Number(scoreResult.Ok.score) },
                            });
                          }
                        } catch (error) {
                          console.error("Error fetching score for submission", error);
                        }
                      }
                    }
                  } catch (error) {
                    console.error("Error fetching submissions", error);
                  }
                }
              }
            } catch (error) {
              console.error("Error fetching user mainer data:", error);
            }
          }
        }
      } catch (error) {
        console.error("Error fetching protocol activity:", error);
      }

      // Sort by timestamp and return only the latest maxItems
      const sortedItems = sortFeedItemsByTimestamp(newFeedItems);
      return sortedItems.slice(0, maxItems);
    }

    // Smart filtering logic
    if (!shouldFilterByDate(filterToUserMainers)) {
      // For "my mainers only", show all events without date filtering
      return sortFeedItemsByTimestamp(await getItemsWithDateFilter(null));
    } else {
      // For "all events", try 3 days first, then 7 days, then latest items regardless of age
      let items = await getItemsWithDateFilter(3);
      if (items.length === 0) {
        console.log("No items found in last 3 days, trying 7 days");
        items = await getItemsWithDateFilter(7);
        
        if (items.length === 0) {
          console.log("No items found in last 7 days, showing latest available items");
          items = await getLatestItemsRegardlessOfAge(20); // Show latest 20 items
        }
      }
      return sortFeedItemsByTimestamp(items);
    }
  }

  async function updateFeed(forceUpdate = false) {
    updating = true;
    
    // Load cached items first for instant display
    if (!forceUpdate && allItems.length === 0) {
      const cachedItems = loadCachedFeedItems();
      if (cachedItems.length > 0) {
        allItems = cachedItems;
        feedItems = [...allItems];
        loading = false;
      }
    }
    
    // Check if we should fetch new data
    const lastFetch = getLastFetchTimestamp();
    const timeSinceLastFetch = Date.now() - lastFetch;
    const shouldFetch = forceUpdate || 
                       updateCounter % 6 === 0 || // Every 6th time (e.g. 6 * 10sec = 1min)
                       timeSinceLastFetch > 5 * 60 * 1000; // Or every 5 minutes
    
    if (shouldFetch) {
      console.log("Time to run getFeedData again");
      try {
        const newItems = await getFeedData(!showAllEvents);
        console.log("after getFeedData newItems");
        console.log(newItems);
        
        // Merge new items with existing cached items
        const mergedItems = allItems.length > 0 ? mergeItems(allItems, newItems) : newItems;
        allItems = mergedItems;
        feedItems = [...allItems];
        
        // Save to cache
        saveFeedItemsToCache(allItems);
        
        currentIndex = allItems.length; // Mark all items as displayed
      } catch (error) {
        console.error("Error updating feed:", error);
        // If fetch fails, keep showing cached items
      }
    }
    
    loading = false;
    updating = false;
    updateCounter++;
  }

  // Handle toggle changes
  $: if (showAllEvents !== undefined) {
    currentIndex = 0;
    feedItems = [];
    allItems = [];
    // Clear cache when switching modes since data structure changes
    try {
      localStorage.removeItem(FEED_STORAGE_KEY);
      localStorage.removeItem(LAST_FETCH_KEY);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
    updateFeed(true);
  }

  // Reset state when authentication status changes
  $: if (!$store.isAuthed) {
    feedItems = [];
    allItems = [];
    currentIndex = 0;
    loading = false;
    updating = false;
    // Clear cache when user logs out
    try {
      localStorage.removeItem(FEED_STORAGE_KEY);
      localStorage.removeItem(LAST_FETCH_KEY);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }

  $: {
    console.log("MainerFeed reactive agentCanisterActors", agentCanisterActors);
    console.log("MainerFeed reactive agentCanistersInfo", agentCanistersInfo);

    // Only update feed if authenticated
    if ($store.isAuthed) {
      (async () => {
        await updateFeed(true);
      })();
    }
  }

  // Cleanup old cached items
  function cleanupOldCachedItems() {
    try {
      const cached = localStorage.getItem(FEED_STORAGE_KEY);
      if (cached) {
        const items = JSON.parse(cached) as FeedItem[];
        const recentItems = filterItemsByDate(items);
        if (recentItems.length !== items.length) {
          // Some items were old, save the filtered list
          saveFeedItemsToCache(recentItems);
        }
      }
    } catch (error) {
      console.error('Error cleaning up cached items:', error);
    }
  }

  onMount(async () => {
    // Clean up old cached items on mount
    cleanupOldCachedItems();
    
    // Load cached items immediately for better UX
    const cachedItems = loadCachedFeedItems();
    if (cachedItems.length > 0 && $store.isAuthed) {
      allItems = cachedItems;
      feedItems = [...allItems];
      loading = false;
    }
    
    await updateFeed();
    interval = setInterval(() => {
      updateFeed();
      // Clean up old cached items periodically (every 10 calls = ~100 seconds)
      if (updateCounter % 10 === 0) {
        cleanupOldCachedItems();
      }
    }, 10000); // Update every 10 seconds

    return () => {
      if (interval) clearInterval(interval);
    };
  });
</script>

<div class="h-full dark:bg-gray-900 dark:text-white flex flex-col" style="overflow-y: auto; overflow-x: visible;">

  {#if updating && $store.isAuthed}
    <div class="flex justify-center py-2">
      <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent dark:border-blue-400"></div>
    </div>
  {/if}
  <!-- Info Panel - show when not authenticated or when authenticated but no content -->
  {#if (!$store.isAuthed) || (feedItems.length === 0 && !loading && !updating)}
    <div class="flex-1 flex flex-col justify-center items-center px-4 py-6">
      <div class="flex flex-col items-center gap-4 text-gray-500 dark:text-gray-400">
        <div class="text-6xl">🤖</div>
        <div class="max-w-md text-center">
          <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
            mAIner activity feed
          </h3>
          <p class="text-sm leading-relaxed">
            This feed displays activity from mAIner agents including:
          </p>
          <ul class="text-sm mt-3 space-y-1">
            <li>• 🎯 Challenges in the protocol</li>
            <li>• 💭 Responses from your mAIners</li>
            <li>• 📊 Scores your mAIners receive</li>
            {#if !showAllEvents}
            <li>• 🏆 Your mAIners' victories and placements</li>
            {/if}
          </ul>
          {#if !$store.isAuthed}
            <p class="text-xs mt-4 text-gray-400 dark:text-gray-500">
              Please connect your wallet to see personalized activity.
            </p>
          {:else}
            <p class="text-xs mt-4 text-gray-400 dark:text-gray-500">
              {showAllEvents ? 'No recent activity in the protocol.' : 'No activity yet from your mAIners.'}
            </p>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  {#if feedItems.length > 0 || (loading && $store.isAuthed)}
    <ul 
      aria-label="mAIner Activity feed" 
      role="feed" 
      class="relative flex flex-col gap-8 py-12 pl-6 text-sm 
             before:absolute before:top-0 before:z-0 before:left-6 before:h-full before:border-2 before:-translate-x-1/2 before:border-slate-400 before:border-dashed dark:before:border-slate-400"
    >
      {#if feedItems.length === 0 && loading}
        <li class="text-center py-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {showAllEvents ? 'No recent activity in the protocol.' : 'No activity yet from your mAIners.'}
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
            <div class="flex flex-col flex-1 gap-2 {item.type === 'winner' ? getWinnerStyling(item.content.placement || '') + ' p-4 rounded-lg animate-pulse-winner' : ''}">
              <h4
                class="text-base font-medium flex justify-between items-center mr-6 text-gray-900 dark:text-gray-100
                       {item.type === 'winner' ? 'text-lg font-bold' : ''}"
              >
                <span class="flex items-center gap-2">
                  {#if item.type === 'winner'}
                    <span class="text-2xl animate-bounce-10s">{getWinnerIcon(item.content.placement || '')}</span>
                  {/if}
                  {item.mainerName}
                  {#if item.type === 'winner'}
                    <span class="text-2xl animate-bounce-10s">{getWinnerIcon(item.content.placement || '')}</span>
                  {/if}
                </span>
                <div class="flex items-center gap-2">
                  <div class="text-2xs font-bold text-slate-600 dark:text-slate-300 text-right opacity-60">
                    <div>{formatTimestamp(item.timestamp).date}</div>
                    <div class="opacity-40">{formatTimestamp(item.timestamp).time}</div>
                  </div>
                  <ShareFeedItem feedItem={item} />
                </div>
              </h4>
              {#if item.type === 'challenge'}
                <p class="text-slate-600 dark:text-slate-300 pr-6">New challenge: <span class="font-medium text-gray-800 dark:text-gray-200">{item.content.challenge}</span></p>
              {:else if item.type === 'response'}
                <p class="text-slate-600 dark:text-slate-300 pr-6">Submitted response: <span class="font-medium text-gray-800 dark:text-gray-200">{item.content.response}</span></p>
              {:else if item.type === 'score'}
                <p class="text-slate-600 dark:text-slate-300 pr-6">Received score: <span class="font-semibold text-orange-600 dark:text-orange-400">{item.content.score}/5</span></p>
              {:else if item.type === 'winner'}
                <div class="text-center">
                  <p class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-amber-600 dark:from-yellow-400 dark:to-amber-400 mb-2">
                    🎉 CONGRATULATIONS! 🎉
                  </p>
                  <p class="text-slate-700 dark:text-slate-200">
                    Achieved <span class="font-bold text-lg {item.content.placement === 'First Place' ? 'text-yellow-600 dark:text-yellow-400' : item.content.placement === 'Second Place' ? 'text-gray-600 dark:text-gray-400' : 'text-orange-600 dark:text-orange-400'}">{item.content.placement}</span>
                  </p>
                  <p class="text-slate-700 dark:text-slate-200">
                    and earned <span class="font-bold text-lg text-green-600 dark:text-green-400">{formatFunnaiAmount(item.content.reward || '0')} FUNNAI</span>
                  </p>
                </div>
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

  @keyframes shimmer {
    0% {
      background-position: -200% 0;
    }
    100% {
      background-position: 200% 0;
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

  /* Shimmer effect for winner text */
  .winner-shimmer {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    background-size: 200% 100%;
    animation: shimmer 2s 6;
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