<script lang="ts">
  import { Principal } from "@dfinity/principal";

  import { onMount } from "svelte";
  import { fly } from "svelte/transition";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount } from "../../helpers/utils/numberFormatUtils";
  import ShareFeedItem from "./ShareFeedItem.svelte";

  export let showAllEvents: boolean = true; // Will be overridden by parent based on auth status

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;

  interface FeedItem {
    id: string;
    timestamp: number;
    type: "challenge" | "response" | "score" | "winner" | "participation";
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

  // Storage keys for persistence - separate caches for different modes
  const FEED_STORAGE_KEY_MY_MAINERS = 'mainer_feed_items_my_mainers';
  const FEED_STORAGE_KEY_ALL_EVENTS = 'mainer_feed_items_all_events';
  const LAST_FETCH_KEY_MY_MAINERS = 'mainer_feed_last_fetch_my_mainers';
  const LAST_FETCH_KEY_ALL_EVENTS = 'mainer_feed_last_fetch_all_events';

  // Smart date filtering - simplified to only last 3 days
  function isWithinDateRange(timestamp: number, days: number = 3): boolean {
    const now = Date.now();
    const itemTime = timestamp / 1000000; // Convert from nanoseconds to milliseconds
    const daysDiff = (now - itemTime) / (24 * 60 * 60 * 1000);
    return daysDiff <= days && daysDiff >= 0; // Also ensure not future dates
  }

  function filterItemsByDate(items: FeedItem[], days: number = 3): FeedItem[] {
    return items.filter(item => isWithinDateRange(item.timestamp, days));
  }

  // Get the appropriate storage keys based on current mode
  function getStorageKeys() {
    return {
      feedKey: showAllEvents ? FEED_STORAGE_KEY_ALL_EVENTS : FEED_STORAGE_KEY_MY_MAINERS,
      fetchKey: showAllEvents ? LAST_FETCH_KEY_ALL_EVENTS : LAST_FETCH_KEY_MY_MAINERS
    };
  }

  // Load cached feed items from localStorage
  function loadCachedFeedItems(): FeedItem[] {
    try {
      const { feedKey } = getStorageKeys();
      const cached = localStorage.getItem(feedKey);
      if (cached) {
        const items = JSON.parse(cached) as FeedItem[];
        // Filter cached items to only include those from last 3 days and ensure no winner events in "All events"
        let filteredItems = filterItemsByDate(items);
        
        // Additional filter: remove winner and participation events from "All events" cache
        if (showAllEvents) {
          filteredItems = filteredItems.filter(item => item.type !== 'winner' && item.type !== 'participation');
        }
        
        return filteredItems;
      }
    } catch (error) {
      console.error('Error loading cached feed items:', error);
    }
    return [];
  }

  // Save feed items to localStorage
  function saveFeedItemsToCache(items: FeedItem[]) {
    try {
      const { feedKey, fetchKey } = getStorageKeys();
      // Only save items from last 3 days to keep storage lean
      let recentItems = filterItemsByDate(items);
      
      // Additional filter: remove winner and participation events from "All events" cache
      if (showAllEvents) {
        recentItems = recentItems.filter(item => item.type !== 'winner' && item.type !== 'participation');
      }
      
      localStorage.setItem(feedKey, JSON.stringify(recentItems));
      localStorage.setItem(fetchKey, Date.now().toString());
    } catch (error) {
      console.error('Error saving feed items to cache:', error);
    }
  }

  // Get the last fetch timestamp
  function getLastFetchTimestamp(): number {
    try {
      const { fetchKey } = getStorageKeys();
      const cached = localStorage.getItem(fetchKey);
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
    let merged = [...existingItems, ...uniqueNewItems];
    
    // Additional safety filter: remove winner and participation events from "All events" mode
    if (showAllEvents) {
      merged = merged.filter(item => item.type !== 'winner' && item.type !== 'participation');
    }
    
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
        return "before:bg-blue-400/70";
      case "response":
        return "before:bg-[#653FC5]";
      case "score":
        return "before:bg-orange-400/70";
      case "winner":
        return "before:bg-amber-400/80";
      case "participation":
        return "before:bg-emerald-400/70";
      default:
        return "before:bg-gray-500";
    }
  }

  function getWinnerStyling(placement: string): string {
    switch (placement) {
      case "First Place":
        return "border-l-2 border-l-amber-400/50";
      case "Second Place":
        return "border-l-2 border-l-gray-400/40";
      case "Third Place":
        return "border-l-2 border-l-orange-400/50";
      default:
        return "";
    }
  }

  function getItemBackground(type: string, placement?: string): string {
    const base = "bg-white/[0.03] border border-white/10 rounded-xl p-4";
    if (type === "winner") {
      return `${base} ${getWinnerStyling(placement || "")}`;
    }
    return base;
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
                  console.log(`Agent ${index} has ${submissionsResult.Ok.length} submissions`);
                  for (const submission of submissionsResult.Ok) {
                    userParticipatedChallenges.add(submission.challengeId);
                  }
                }
              } catch (error) {
                console.error("Error fetching submissions for challenge filtering", error);
              }
            }
          }
          console.log("User participated in challenges:", userParticipatedChallenges.size);
        }

        // Add challenges (only last 3 days)
        challenges.forEach((challenge) => {
          const challengeTimestamp = Number(challenge.challengeCreationTimestamp);
          const passesDateFilter = isWithinDateRange(challengeTimestamp, 3);
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

        // Add winners (only for "My mAIners" and only last 3 days)
        if (filterToUserMainers) {
          winners.forEach((winnerDeclaration) => {
            const winnerTimestamp = Number(winnerDeclaration.finalizedTimestamp);
            const passesDateFilter = isWithinDateRange(winnerTimestamp, 3);
            
            if (!passesDateFilter) {
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
              
              // Only show if it's the user's mAIner
              if (mainerIndex !== -1) {
                const mainerName = `mAIner ${entry.submittedBy.toString().slice(0, 5)}`;

                newFeedItems.push({
                  // Use challenge ID + submission ID + position to ensure unique IDs and prevent duplicates
                  id: `${winnerDeclaration.challengeId}-${entry.submissionId}-${position.replace(/\s+/g, '')}-winner`,
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

          // Add participation rewards (only for "My mAIners" and only last 3 days)
          winners.forEach((winnerDeclaration) => {
            const winnerTimestamp = Number(winnerDeclaration.finalizedTimestamp);
            const passesDateFilter = isWithinDateRange(winnerTimestamp, 3);
            
            if (!passesDateFilter) {
              return;
            }

            // Helper function to process participants list (it's a linked list structure)
            function processParticipantsList(participantsList: any): any[] {
              const participants: any[] = [];
              let current = participantsList;
              
              while (current && current.length > 0 && current[0] && current[0].length >= 2) {
                const participant = current[0][0]; // First element is the participant
                participants.push(participant);
                current = current[0][1]; // Second element is the next list node
              }
              
              return participants;
            }

            // Process all participants from the linked list
            const allParticipants = processParticipantsList(winnerDeclaration.participants);
            
            allParticipants.forEach((participant) => {
              // Check if this is a participation reward (not winner/second/third place)
              if (participant.result && "Participated" in participant.result) {
                const mainerIndex = agentCanistersInfo.findIndex(
                  (agent) => agent.address === participant.submittedBy.toString(),
                );
                
                // Only show if it's the user's mAIner
                if (mainerIndex !== -1) {
                  const mainerName = `mAIner ${participant.submittedBy.toString().slice(0, 5)}`;

                  newFeedItems.push({
                    // Use challenge ID + submission ID to ensure unique IDs and prevent duplicates
                    id: `${winnerDeclaration.challengeId}-${participant.submissionId}-participation`,
                    timestamp: winnerTimestamp,
                    type: "participation",
                    mainerName,
                    content: {
                      reward: participant.reward.amount.toString(),
                    },
                  });
                }
              }
            });
          });
        }
      }

      // Add user mainer data if authenticated (only last 3 days)
      if ($store.isAuthed) {
        try {
          for (const [index, agent] of agentCanisterActors.entries()) {
            if (agent) {
              try {
                const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();

                if ("Ok" in submissionsResult) {
                  console.log(`Agent ${index} submissions:`, submissionsResult.Ok.length);
                  for (const submission of submissionsResult.Ok) {
                    const submissionTimestamp = Number(submission.submittedTimestamp);
                    
                    // Only include submissions from last 3 days
                    const passesDateFilter = isWithinDateRange(submissionTimestamp, 3);
                    if (!passesDateFilter) {
                      continue;
                    }

                    const mainerName = `mAIner ${agentCanistersInfo[index].address.slice(0, 5)}`;
                    
                    // Add response
                    newFeedItems.push({
                      // Use challenge ID + submission ID to ensure unique IDs and prevent duplicates
                      id: `${submission.challengeId}-${submission.submissionId}-response`,
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
                        const scorePassesDateFilter = isWithinDateRange(judgedTimestamp, 3);
                        
                        if (scorePassesDateFilter) {
                          newFeedItems.push({
                            // Use challenge ID + submission ID to ensure unique IDs and prevent duplicates
                            id: `${submission.challengeId}-${submission.submissionId}-score`,
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

    return sortFeedItemsByTimestamp(newFeedItems);
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
      try {
        const newItems = await getFeedData(!showAllEvents);
        
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
      localStorage.removeItem(FEED_STORAGE_KEY_MY_MAINERS);
      localStorage.removeItem(FEED_STORAGE_KEY_ALL_EVENTS);
      localStorage.removeItem(LAST_FETCH_KEY_MY_MAINERS);
      localStorage.removeItem(LAST_FETCH_KEY_ALL_EVENTS);
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
      localStorage.removeItem(FEED_STORAGE_KEY_MY_MAINERS);
      localStorage.removeItem(FEED_STORAGE_KEY_ALL_EVENTS);
      localStorage.removeItem(LAST_FETCH_KEY_MY_MAINERS);
      localStorage.removeItem(LAST_FETCH_KEY_ALL_EVENTS);
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
      const { feedKey } = getStorageKeys();
      const cached = localStorage.getItem(feedKey);
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
    // Clean up ALL old cached items on mount (including old format)
    try {
      // Remove old format caches
      localStorage.removeItem('mainer_feed_items');
      localStorage.removeItem('mainer_feed_last_fetch');
      
      // Clean up current format caches
      cleanupOldCachedItems();
    } catch (error) {
      console.error('Error cleaning up cached items:', error);
    }
    
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

<div class="h-full bg-[#0c0b12] text-white flex flex-col font-sans" style="overflow-y: auto; overflow-x: visible;">

  <!-- Fixed space for loader to prevent UI jump -->
  <div class="flex justify-center py-2 transition-opacity duration-300 {updating && $store.isAuthed ? 'opacity-100' : 'opacity-0 pointer-events-none'}">
    <div class="animate-spin h-5 w-5 border-2 border-[#653FC5] rounded-full border-t-transparent"></div>
  </div>
  <!-- Info Panel - show when not authenticated or when authenticated but no content -->
  {#if (!$store.isAuthed) || (feedItems.length === 0 && !loading && !updating)}
    <div class="flex-1 flex flex-col justify-center items-center px-5 py-8">
      <div class="relative w-full max-w-md overflow-hidden rounded-xl border border-white/[0.06] bg-white/[0.02] px-6 py-8 text-left">
        <div class="relative">
          <p class="mb-2 text-[10px] font-medium uppercase tracking-[0.2em] text-[#653FC5]/80">Protocol stream</p>
          <h3 class="text-base font-medium tracking-tight text-gray-300">
            Agent activity
          </h3>
          <p class="mt-2 text-sm font-normal leading-relaxed text-gray-500">
            Live signals from mAIners operating on the network:
          </p>
          <ul class="mt-4 space-y-2 text-sm font-normal text-gray-500">
            <li class="flex gap-2"><span class="text-gray-600">–</span> Challenges in the protocol</li>
            {#if $store.isAuthed}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Responses from your mAIners</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Scores your mAIners receive</li>
            {/if}
            {#if !showAllEvents}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Victories and placements</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Participation rewards earned</li>
            {/if}
            {#if !$store.isAuthed}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Responses from mAIners</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Scores received by mAIners</li>
            {/if}
          </ul>
          {#if !$store.isAuthed}
            <p class="mt-5 text-xs font-normal text-gray-600">
              Connect to deploy agents and unlock a personalized stream.
            </p>
          {:else}
            <p class="mt-5 text-xs font-normal text-gray-600">
              {showAllEvents ? 'No recent activity in the protocol.' : 'Loading activity from your mAIners.'}
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
      class="relative flex flex-col gap-4 py-8 pl-6 text-sm 
             before:absolute before:top-0 before:z-0 before:left-6 before:h-full before:border before:-translate-x-1/2 before:border-white/10 before:border-dashed"
    >
      {#if feedItems.length === 0 && loading}
        <li class="text-center py-4">
          <p class="text-sm text-gray-600">
            {showAllEvents ? 'No recent activity in the protocol.' : 'Loading activity from your mAIners.'}
          </p>
        </li>
      {:else}
        {#each feedItems.filter(item => !showAllEvents || (item.type !== 'winner' && item.type !== 'participation')) as item (item.id)}
          <li 
            role="article" 
            class="relative px-4 
                   before:absolute before:z-[1] before:left-0 before:top-5 before:h-2.5 before:w-2.5 before:-translate-x-1/2 before:rounded-full {getStatusColor(item.type)} before:ring-2 before:ring-[#0c0b12]"
            in:fly="{{ y: 20, duration: 500 }}"
          >
            <div class="flex flex-col flex-1 gap-2 {getItemBackground(item.type, item.content.placement)}">
              <h4
                class="text-sm font-medium flex justify-between items-center text-gray-200
                       {item.type === 'winner' ? 'text-base' : ''}"
              >
                <span class="flex items-center gap-2">
                  {#if item.type === 'winner'}
                    <span class="text-base opacity-80">{getWinnerIcon(item.content.placement || '')}</span>
                  {/if}
                  {item.mainerName}
                </span>
                <div class="flex items-center gap-2">
                  <div class="text-2xs font-medium text-gray-500 text-right">
                    <div>{formatTimestamp(item.timestamp).date}</div>
                    <div class="text-gray-600">{formatTimestamp(item.timestamp).time}</div>
                  </div>
                  <ShareFeedItem feedItem={item} />
                </div>
              </h4>
              {#if item.type === 'challenge'}
                <p class="text-gray-500 pr-2">New challenge: <span class="font-medium text-gray-300">{item.content.challenge}</span></p>
              {:else if item.type === 'response'}
                <p class="text-gray-500 pr-2">Submitted response: <span class="font-medium text-gray-300">{item.content.response}</span></p>
              {:else if item.type === 'score'}
                <p class="text-gray-500 pr-2">Received score: <span class="font-semibold text-orange-400/90">{item.content.score}/5</span></p>
              {:else if item.type === 'winner'}
                <div class="rounded-lg border border-white/[0.06] bg-agent-elevated/80 px-3 py-3">
                  <p class="text-sm font-medium text-gray-200 mb-1.5">
                    Placement secured
                  </p>
                  <p class="text-gray-400 text-sm">
                    Achieved <span class="font-semibold {item.content.placement === 'First Place' ? 'text-amber-400/90' : item.content.placement === 'Second Place' ? 'text-gray-300' : 'text-orange-400/90'}">{item.content.placement}</span>
                  </p>
                  <p class="text-gray-400 text-sm mt-0.5">
                    Earned <span class="font-semibold text-emerald-400/90">{formatFunnaiAmount(item.content.reward || '0')} FUNNAI</span>
                  </p>
                </div>
              {:else if item.type === 'participation'}
                <p class="text-gray-500 pr-2">
                  Earned participation reward: <span class="font-semibold text-[#653FC5]">{formatFunnaiAmount(item.content.reward || '0')} FUNNAI</span>
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