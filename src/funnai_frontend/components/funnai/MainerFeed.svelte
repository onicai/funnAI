<script lang="ts">
  import { Principal } from "@dfinity/principal";

  import { onMount, onDestroy } from "svelte";
  import { fly, scale } from "svelte/transition";
  import { elasticOut } from "svelte/easing";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount } from "../../helpers/utils/numberFormatUtils";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import ShareFeedItem from "./ShareFeedItem.svelte";

  export let showAllEvents: boolean = true; // Will be overridden by parent based on auth status

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;

  interface FeedItem {
    id: string;
    timestamp: number;
    type: "challenge" | "response" | "score" | "winner" | "participation";
    mainerName: string;
    mainerAddress?: string;
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
  let hasLoadedOnce = false;
  let interval: NodeJS.Timer;
  let currentIndex = 0;
  let updating = false;
  let updateInFlight = false;
  let updateCounter = 0;
  let lastFetchTimestamp = 0;
  let lastMainerSourceKey = "";

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
        return "before:bg-agent-purple";
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
        return "prize-card prize-first";
      case "Second Place":
        return "prize-card prize-second";
      case "Third Place":
        return "prize-card prize-third";
      default:
        return "prize-card";
    }
  }

  function getItemBackground(type: string, placement?: string): string {
    if (type === "winner") {
      return getWinnerStyling(placement || "");
    }
    return "bg-white/3 border border-white/10 rounded-xl p-4";
  }

  function getPlacementMeta(placement: string): {
    rank: string;
    label: string;
    tone: string;
    ring: string;
  } {
    switch (placement) {
      case "First Place":
        return { rank: "1", label: "First place", tone: "text-amber-300", ring: "ring-amber-400/40" };
      case "Second Place":
        return { rank: "2", label: "Second place", tone: "text-gray-200", ring: "ring-white/25" };
      case "Third Place":
        return { rank: "3", label: "Third place", tone: "text-orange-300", ring: "ring-orange-400/35" };
      default:
        return { rank: "•", label: placement || "Placement", tone: "text-agent-purple", ring: "ring-agent-purple/30" };
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
                  mainerAddress: entry.submittedBy.toString(),
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
    // Load cached items first for instant display (no spinner flicker)
    if (!forceUpdate && allItems.length === 0) {
      const cachedItems = loadCachedFeedItems();
      if (cachedItems.length > 0) {
        allItems = cachedItems;
        feedItems = [...allItems];
        loading = false;
        hasLoadedOnce = true;
      }
    }

    // Check if we should fetch new data
    const lastFetch = getLastFetchTimestamp();
    const timeSinceLastFetch = Date.now() - lastFetch;
    const shouldFetch = forceUpdate ||
                       updateCounter % 6 === 0 || // Every 6th time (e.g. 6 * 10sec = 1min)
                       timeSinceLastFetch > 5 * 60 * 1000; // Or every 5 minutes

    if (!shouldFetch) {
      loading = false;
      updateCounter++;
      return;
    }

    if (updateInFlight) return;
    updateInFlight = true;

    // Only show the overlay spinner when there is already content.
    // An empty feed must keep its empty state visible — flipping `updating`
    // was hiding/showing that card every poll and looking like a flicker.
    if (feedItems.length > 0) {
      updating = true;
    }

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
      // If fetch fails, keep showing cached items / empty state
    } finally {
      loading = false;
      updating = false;
      updateInFlight = false;
      hasLoadedOnce = true;
      updateCounter++;
    }
  }

  // Handle toggle changes only — not every remount
  let lastShowAllEvents: boolean | undefined = undefined;
  $: if (showAllEvents !== lastShowAllEvents) {
    const isFirst = lastShowAllEvents === undefined;
    lastShowAllEvents = showAllEvents;
    if (!isFirst) {
      currentIndex = 0;
      feedItems = [];
      allItems = [];
      hasLoadedOnce = false;
      loading = true;
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
  }

  // Reset state when authentication status changes
  $: if (!$store.isAuthed) {
    feedItems = [];
    allItems = [];
    currentIndex = 0;
    loading = false;
    updating = false;
    hasLoadedOnce = false;
    lastMainerSourceKey = "";
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

  // Refresh only when the user's mAIner set actually changes — not on every
  // store write during login enrich (that forced a full feed reload for ~30s).
  $: mainerSourceKey = $store.isAuthed
    ? `${agentCanisterActors?.length ?? 0}:${(agentCanistersInfo || []).map((c) => c.address || "").join(",")}`
    : "";
  $: if ($store.isAuthed && mainerSourceKey !== lastMainerSourceKey) {
    lastMainerSourceKey = mainerSourceKey;
    updateFeed(true);
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
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
</script>

<div class="relative h-full min-h-0 bg-agent-surface text-white flex flex-col font-sans overflow-hidden">
  <!-- Overlay loader — only when content already exists (empty state stays put) -->
  <div
    class="absolute top-2 left-1/2 z-20 -translate-x-1/2 transition-opacity duration-300
           {updating && $store.isAuthed && feedItems.length > 0 ? 'opacity-100' : 'opacity-0 pointer-events-none'}"
    aria-hidden={!(updating && $store.isAuthed && feedItems.length > 0)}
  >
    <div class="animate-spin h-5 w-5 border-2 border-agent-purple rounded-full border-t-transparent"></div>
  </div>

  {#if (!$store.isAuthed) || (feedItems.length === 0 && !loading)}
    <div class="absolute inset-0 z-10 flex flex-col justify-center items-center px-5 py-8 overflow-y-auto">
      <div class="relative w-full max-w-md overflow-hidden rounded-xl border border-white/6 bg-agent-surface px-6 py-8 text-left">
        <div class="relative">
          <p class="mb-2 text-[10px] font-medium uppercase tracking-[0.2em] text-agent-purple/80">Protocol stream</p>
          <h3 class="text-base font-medium tracking-tight text-gray-300">
            Agent activity
          </h3>
          <p class="mt-2 text-sm font-normal leading-relaxed text-gray-500">
            Live signals from mAIners operating on the network:
          </p>
          <ul class="mt-4 space-y-2 text-sm font-normal text-gray-500 min-h-30">
            <li class="flex gap-2"><span class="text-gray-600">–</span> Challenges in the protocol</li>
            {#if $store.isAuthed}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Responses from your mAIners</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Scores your mAIners receive</li>
            {:else}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Responses from mAIners</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Scores received by mAIners</li>
            {/if}
            {#if !showAllEvents}
            <li class="flex gap-2"><span class="text-gray-600">–</span> Victories and placements</li>
            <li class="flex gap-2"><span class="text-gray-600">–</span> Participation rewards earned</li>
            {/if}
          </ul>
          {#if !$store.isAuthed}
            <p class="mt-5 text-xs font-normal text-gray-600">
              Connect to deploy agents and unlock a personalized stream.
            </p>
          {:else}
            <p class="mt-5 text-xs font-normal text-gray-600">
              {#if showAllEvents}
                No recent activity in the protocol.
              {:else if hasLoadedOnce}
                No activity yet. Once your mAIner submits its first response, it will show up here.
              {:else}
                Loading activity from your mAIners.
              {/if}
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
      class="relative flex-1 min-h-0 overflow-y-auto overflow-x-hidden flex flex-col gap-4 py-6 pl-6 pr-2 text-sm
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
                   before:absolute before:z-1 before:left-0 before:top-5 before:h-2.5 before:w-2.5 before:-translate-x-1/2 before:rounded-full {getStatusColor(item.type)} before:ring-2 before:ring-agent-surface"
            in:fly="{{ y: 12, duration: 280 }}"
          >
            <div class="flex flex-col flex-1 gap-2 {getItemBackground(item.type, item.content.placement)}">
              {#if item.type === 'winner'}
                {@const place = getPlacementMeta(item.content.placement || '')}
                {@const identity = getMainerVisualIdentity(item.mainerAddress || item.mainerName)}
                <div
                  class="relative overflow-hidden"
                  in:scale={{ duration: 520, start: 0.94, easing: elasticOut }}
                >
                  <div class="prize-glow" aria-hidden="true"></div>
                  <div class="relative flex items-start gap-3">
                    <div class="relative shrink-0">
                      <div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block prize-avatar">
                        {@html identity.icon}
                      </div>
                      <div class="absolute -bottom-1.5 -right-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-agent-elevated ring-2 {place.ring} prize-rank-badge">
                        <span class="text-[11px] font-semibold tabular-nums {place.tone}">{place.rank}</span>
                      </div>
                    </div>

                    <div class="min-w-0 flex-1">
                      <div class="flex items-start justify-between gap-2">
                        <div>
                          <p class="agent-eyebrow mb-1">Prize announcement</p>
                          <h4 class="text-sm font-semibold tracking-tight text-white">
                            {item.mainerName}
                          </h4>
                        </div>
                        <div class="flex items-center gap-2 shrink-0">
                          <div class="text-2xs font-medium text-gray-500 text-right">
                            <div>{formatTimestamp(item.timestamp).date}</div>
                            <div class="text-gray-600">{formatTimestamp(item.timestamp).time}</div>
                          </div>
                          <ShareFeedItem feedItem={item} />
                        </div>
                      </div>

                      <div class="mt-3 flex flex-wrap items-center gap-2">
                        <span class="inline-flex items-center gap-1.5 rounded-full bg-white/5 px-2.5 py-1 text-[11px] font-medium {place.tone} prize-place-chip">
                          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                            <path d="M12 2l2.4 4.9 5.4.8-3.9 3.8.9 5.4L12 14.9 7.2 17l.9-5.4L4.2 7.7l5.4-.8L12 2z"/>
                          </svg>
                          {place.label}
                        </span>
                        <span class="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-300 prize-reward">
                          +{formatFunnaiAmount(item.content.reward || '0')} FUNNAI
                        </span>
                      </div>

                      <p class="mt-2.5 text-sm text-gray-400">
                        Placement secured on the Proof-of-AI-Work leaderboard.
                      </p>
                    </div>
                  </div>
                </div>
              {:else}
              <h4
                class="text-sm font-medium flex justify-between items-center text-gray-200"
              >
                <span class="flex items-center gap-2">
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
              {:else if item.type === 'participation'}
                <div class="rounded-lg bg-agent-purple/10 px-3 py-2.5">
                  <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-agent-purple mb-1">Participation</p>
                  <p class="text-sm text-gray-300">
                    Earned <span class="font-semibold text-emerald-300">{formatFunnaiAmount(item.content.reward || '0')} FUNNAI</span>
                  </p>
                </div>
              {/if}
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
    font-size: 0.625rem;
    line-height: 0.75rem;
  }

  .prize-card {
    position: relative;
    overflow: hidden;
    border-radius: 0.75rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.03);
    padding: 1rem;
  }

  .prize-first {
    border-color: rgba(251, 191, 36, 0.28);
    background:
      linear-gradient(135deg, rgba(251, 191, 36, 0.08), transparent 42%),
      rgba(255, 255, 255, 0.03);
  }

  .prize-second {
    border-color: rgba(255, 255, 255, 0.16);
    background:
      linear-gradient(135deg, rgba(255, 255, 255, 0.06), transparent 42%),
      rgba(255, 255, 255, 0.03);
  }

  .prize-third {
    border-color: rgba(251, 146, 60, 0.28);
    background:
      linear-gradient(135deg, rgba(251, 146, 60, 0.08), transparent 42%),
      rgba(255, 255, 255, 0.03);
  }

  .prize-glow {
    pointer-events: none;
    position: absolute;
    inset: -40% auto auto 55%;
    width: 10rem;
    height: 10rem;
    border-radius: 9999px;
    background: rgba(101, 63, 197, 0.18);
    filter: blur(40px);
    animation: prizeGlow 3.2s ease-in-out infinite;
  }

  .prize-first .prize-glow {
    background: rgba(251, 191, 36, 0.2);
  }

  .prize-second .prize-glow {
    background: rgba(255, 255, 255, 0.1);
  }

  .prize-third .prize-glow {
    background: rgba(251, 146, 60, 0.18);
  }

  .prize-avatar {
    animation: prizeAvatarIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .prize-rank-badge {
    animation: prizeBadgePop 0.65s cubic-bezier(0.22, 1, 0.36, 1) 0.12s both;
  }

  .prize-place-chip {
    animation: prizeChipIn 0.45s ease-out 0.15s both;
  }

  .prize-reward {
    position: relative;
    overflow: hidden;
    animation: prizeChipIn 0.45s ease-out 0.22s both;
  }

  .prize-reward::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(105deg, transparent 35%, rgba(255, 255, 255, 0.22), transparent 65%);
    transform: translateX(-120%);
    animation: prizeShimmer 2.4s ease-in-out 0.6s 2;
  }

  @keyframes prizeGlow {
    0%, 100% { opacity: 0.45; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.08); }
  }

  @keyframes prizeAvatarIn {
    from { opacity: 0; transform: scale(0.86) translateY(6px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }

  @keyframes prizeBadgePop {
    0% { opacity: 0; transform: scale(0.5); }
    70% { opacity: 1; transform: scale(1.12); }
    100% { opacity: 1; transform: scale(1); }
  }

  @keyframes prizeChipIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes prizeShimmer {
    0% { transform: translateX(-120%); }
    100% { transform: translateX(120%); }
  }

  @media (prefers-reduced-motion: reduce) {
    .prize-glow,
    .prize-avatar,
    .prize-rank-badge,
    .prize-place-chip,
    .prize-reward,
    .prize-reward::after {
      animation: none !important;
    }
  }
</style> 