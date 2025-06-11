<script lang="ts">
  import { Principal } from "@dfinity/principal";

  import { onMount } from "svelte";
  import { fly } from "svelte/transition";
  import { store } from "../../stores/store";
  import { mockFeedData } from "../../helpers/mockFeedData";

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
  let showAllEvents = true; // Default to showing all events

  // Convert milliseconds timestamp to readable time format
  function formatTimestamp(timestamp: number): string {
    const date = new Date(timestamp * 1000); // Convert seconds to milliseconds
    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
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
    return feedItems.sort((a, b) => a.timestamp - b.timestamp);
  }

  async function getFeedData(filterToUserMainers: boolean = false): Promise<FeedItem[]> {
    //console.log("in MainerFeed getFeedData");
    // Get activity data for the feed from the backend canisters
    let newFeedItems: FeedItem[] = [];
    let userParticipatedChallenges: Set<string> = new Set();

    try {
      let recentProtocolActivityResult =
        await $store.gameStateCanisterActor.getRecentProtocolActivity();
      //let recentProtocolActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity_mockup();
      //console.log("MainerFeed recentProtocolActivityResult");
      //console.log(recentProtocolActivityResult);

    if ("Ok" in recentProtocolActivityResult && $store.isAuthed) {
      const { challenges, winners } = recentProtocolActivityResult.Ok;
      //console.log("in MainerFeed getFeedData winners");
      //console.log(winners);

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

      // Add challenges based on filter setting
      challenges.forEach((challenge) => {
        if (!filterToUserMainers || userParticipatedChallenges.has(challenge.challengeId)) {
          newFeedItems.push({
            id: challenge.challengeId,
            timestamp: Number(challenge.challengeCreationTimestamp),
            type: "challenge",
            mainerName: "Protocol",
            content: { challenge: challenge.challengeQuestion },
          });
        }
      });

      // Add winners based on filter setting
      winners.forEach((winnerDeclaration) => {
        //console.log("in MainerFeed getFeedData winners winnerDeclaration");
        //console.log(winnerDeclaration);
        const placements = [
          { position: "First Place", entry: winnerDeclaration.winner },
          { position: "Second Place", entry: winnerDeclaration.secondPlace },
          ...(winnerDeclaration.thirdPlace
            ? [
                {
                  position: "Third Place",
                  entry: winnerDeclaration.thirdPlace,
                },
              ]
            : []),
        ];
        //console.log("in MainerFeed getFeedData winners placements");
        //console.log(placements);

        placements.forEach(({ position, entry }) => {
          const mainerIndex = agentCanistersInfo.findIndex(
            (agent) => agent.address === entry.submittedBy.toString(),
          );
          
          // Show all winners or only user's mAIners based on filter
          if (!filterToUserMainers || mainerIndex !== -1) {
            const mainerName = mainerIndex !== -1 
              ? `mAIner ${entry.submittedBy.toString().slice(0, 5)}` 
              : `mAIner ${entry.submittedBy.toString().slice(0, 5)}`;

            newFeedItems.push({
              id: `${entry.submissionId}-winner`,
              timestamp: Number(winnerDeclaration.finalizedTimestamp),
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
      //console.log("in MainerFeed getFeedData newFeedItems after winners");
      //console.log(newFeedItems);
    }

    } catch (error) {
      console.error("Error fetching protocol activity:", error);
      // Return empty array on error, component will show appropriate message
    }

    if ($store.isAuthed) {
      //console.log("MainerFeed agentCanisterActors");
      //console.log(agentCanisterActors);
      //console.log("MainerFeed agentCanistersInfo");
      //console.log(agentCanistersInfo);
      // Add user's mAIner agents' submissions and scores (for submissions) to newFeedItems
      // for each agent in the array agentCanisterActors, retrieve the agent's submissions
      
      try {
        for (const [index, agent] of agentCanisterActors.entries()) {
        //console.log("in MainerFeed getFeedData agentCanisterActors entries index");
        //console.log(index);
        //console.log("in MainerFeed getFeedData agentCanisterActors entries agent");
        //console.log(agent);
        if (agent) {
          try {
            const submissionsResult =
              await agent.getRecentSubmittedResponsesAdmin();
            //console.log("in MainerFeed getFeedData agentCanisterActors entries submissionsResult");
            //console.log(submissionsResult);
            // ChallengeResponseSubmissionsResult looks like so: type ChallengeResponseSubmissionsResult = { 'Ok' : Array<ChallengeResponseSubmission> } | { 'Err' : ApiError };
            /* interface ChallengeResponseSubmission {
                'challengeClosedTimestamp' : [] | [bigint],
                'challengeTopicStatus' : ChallengeTopicStatus,
                'challengeTopicCreationTimestamp' : bigint,
                'challengeCreationTimestamp' : bigint,
                'challengeCreatedBy' : CanisterAddress,
                'challengeTopicId' : string,
                'submittedTimestamp' : bigint,
                'submittedBy' : Principal,
                'challengeStatus' : ChallengeStatus,
                'challengeQuestionSeed' : number,
                'submissionStatus' : ChallengeResponseSubmissionStatus,
                'challengeQuestion' : string,
                'challengeId' : string,
                'challengeTopic' : string,
                'submissionId' : string,
                'challengeAnswerSeed' : number,
                'submissionCyclesRequired' : bigint,
                'challengeQueuedId' : string,
                'challengeQueuedBy' : Principal,
                'challengeQueuedTo' : Principal,
                'challengeQueuedTimestamp' : bigint,
                'challengeAnswer' : string,
              } */

            // for each ChallengeResponseSubmission add an entry to newFeedItems
            if ("Ok" in submissionsResult) {
              for (const submission of submissionsResult.Ok) {
                //console.log("in MainerFeed getFeedData agentCanisterActors entries submission");
                //console.log(submission);
                const mainerName = `mAIner ${agentCanistersInfo[index].address.slice(0, 5)}`;
                newFeedItems.push({
                  id: submission.submissionId,
                  timestamp: Number(submission.submittedTimestamp),
                  type: "response",
                  mainerName,
                  content: { response: submission.challengeAnswer },
                });

                // then (also for each ChallengeResponseSubmission) retrieve the score this submission received
                /*   interface SubmissionRetrievalInput {
                      'challengeId' : string,
                      'submissionId' : string,
                    } */
                // which returns type ScoredResponseRetrievalResult = { 'Ok' : ScoredResponse } | { 'Err' : ApiError };
                /*   interface ScoredResponse {
                      'challengeClosedTimestamp' : [] | [bigint],
                      'challengeTopicStatus' : ChallengeTopicStatus,
                      'challengeTopicCreationTimestamp' : bigint,
                      'challengeCreationTimestamp' : bigint,
                      'challengeCreatedBy' : CanisterAddress,
                      'challengeTopicId' : string,
                      'judgedBy' : Principal,
                      'submittedTimestamp' : bigint,
                      'submittedBy' : Principal,
                      'challengeStatus' : ChallengeStatus,
                      'challengeQuestionSeed' : number,
                      'submissionStatus' : ChallengeResponseSubmissionStatus,
                      'score' : bigint,
                      'challengeQuestion' : string,
                      'challengeId' : string,
                      'challengeTopic' : string,
                      'judgedTimestamp' : bigint,
                      'submissionId' : string,
                      'challengeAnswerSeed' : number,
                      'submissionCyclesRequired' : bigint,
                      'challengeQueuedId' : string,
                      'challengeQueuedBy' : Principal,
                      'challengeQueuedTo' : Principal,
                      'challengeQueuedTimestamp' : bigint,
                      'challengeAnswer' : string,
                      'scoreSeed' : number,
                    } */
                // note that the submission might not have received a score yet (ScoredResponseRetrievalResult returns an Err in that case)

                // if there's a score for the submission, add the score as an entry to newFeedItems
                try {
                  const scoreResult =
                    await $store.gameStateCanisterActor.getScoreForSubmission({
                      challengeId: submission.challengeId,
                      submissionId: submission.submissionId,
                    });
                  /* const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission_mockup({
                    challengeId: submission.challengeId,
                    submissionId: submission.submissionId
                  }); */

                  //console.log("in MainerFeed getFeedData agentCanisterActors entries scoreResult");
                  //console.log(scoreResult);

                  if ("Ok" in scoreResult) {
                    newFeedItems.push({
                      id: `${submission.submissionId}-score`,
                      timestamp: Number(scoreResult.Ok.judgedTimestamp),
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
          };
        };
      }
      } catch (error) {
        console.error("Error fetching user mainer data:", error);
        // Continue with empty user data, component will show appropriate message
      }
    }
    //console.log("in MainerFeed getFeedData newFeedItems before return");
    //console.log(newFeedItems);
    return sortFeedItemsByTimestamp(newFeedItems);
  }

  async function updateFeed(forceUpdate = false) {
    updating = true;
    if (forceUpdate || updateCounter % 6 === 0) {
      // Retrieve items from backend every 6th time (e.g. 6 * 10sec = 1min)
      console.log("Time to run getFeedData again");
      allItems = await getFeedData(!showAllEvents);
      console.log("after getFeedData allItems");
      console.log(allItems);
    }
    // TODO: only add new items to feed
    if (currentIndex < allItems.length) {
      const newItem = {
        ...allItems[currentIndex],
        timestamp: Math.floor(Date.now() / 1000), // Set current timestamp in seconds
      };
      feedItems = [newItem, ...feedItems];
      currentIndex++;
    }
    loading = false;
    updating = false;
    updateCounter++;
  }

  // Handle toggle change
  async function handleToggleChange() {
    currentIndex = 0;
    feedItems = [];
    await updateFeed(true);
  }

  // Reset state when authentication status changes
  $: if (!$store.isAuthed) {
    feedItems = [];
    allItems = [];
    currentIndex = 0;
    loading = false;
    updating = false;
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

  onMount(async () => {
    await updateFeed();
    interval = setInterval(updateFeed, 10000); // Update every 10 seconds

    return () => {
      if (interval) clearInterval(interval);
    };
  });
</script>

<div class="h-full overflow-y-auto dark:bg-gray-900 dark:text-white flex flex-col">
  <!-- Toggle controls -->
  <div class="sticky top-0 z-10 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
    <div class="flex items-center justify-between">
      <h2 class="hidden sm:block text-lg font-semibold text-gray-900 dark:text-white">Activity Feed</h2>
      <div class="flex items-center gap-3">
        <label class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
          <span class="text-xs">My mAIners only</span>
          <button
            type="button"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                   {showAllEvents ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}"
            role="switch"
            aria-checked={showAllEvents}
            on:click={() => {
              showAllEvents = !showAllEvents;
              handleToggleChange();
            }}
          >
            <span class="sr-only">Toggle between all events and my mAIners only</span>
            <span
              class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                     {showAllEvents ? 'translate-x-6' : 'translate-x-1'}"
            ></span>
          </button>
          <span class="text-xs">All events</span>
        </label>
      </div>
    </div>
  </div>

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
            mAIner Activity Feed
          </h3>
          <p class="text-sm leading-relaxed">
            This feed displays activity from mAIner agents including:
          </p>
          <ul class="text-sm mt-3 space-y-1">
            <li>• 🎯 Challenges in the protocol</li>
            <li>• 💭 Responses from your mAIners</li>
            <li>• 📊 Scores your mAIners receive</li>
            <li>• 🏆 All victories and placements</li>
          </ul>
          {#if !$store.isAuthed}
            <p class="text-xs mt-4 text-gray-400 dark:text-gray-500">
              Please connect your wallet to see personalized activity.
            </p>
          {:else}
            <p class="text-xs mt-4 text-gray-400 dark:text-gray-500">
              {showAllEvents ? 'No activity yet in the protocol.' : 'No activity yet from your mAIners.'}
            </p>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  {#if feedItems.length > 0 || (loading && $store.isAuthed)}
    <ul 
      aria-label="mAIner Activity Feed" 
      role="feed" 
      class="relative flex flex-col gap-8 py-12 pl-6 text-sm 
             before:absolute before:top-0 before:left-6 before:h-full before:border-2 before:-translate-x-1/2 before:border-slate-400 before:border-dashed before:z-[1] dark:before:border-slate-400"
    >
      {#if feedItems.length === 0 && loading}
        <li class="text-center py-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {showAllEvents ? 'No activity yet in the protocol.' : 'No activity yet from your mAIners.'}
          </p>
        </li>
      {:else}
        {#each feedItems as item (item.id)}
          <li 
            role="article" 
            class="relative pl-6 
                   before:absolute before:z-[20] before:left-0 before:top-2 before:h-3 before:w-3 before:-translate-x-1/2 before:rounded-full {getStatusColor(item.type)} before:ring-2 before:ring-white dark:before:ring-gray-900 before:shadow-sm animate-fadeIn"
            in:fly="{{ y: 20, duration: 500 }}"
          >
            <div class="flex flex-col flex-1 gap-2 {item.type === 'winner' ? getWinnerStyling(item.content.placement || '') + ' p-4 rounded-lg animate-pulse-winner' : ''}">
              <h4
                class="text-base font-medium flex justify-between items-center mr-6 text-gray-900 dark:text-gray-100
                       {item.type === 'winner' ? 'text-lg font-bold' : ''}"
              >
                <span class="flex items-center gap-2">
                  {#if item.type === 'winner'}
                    <span class="text-2xl animate-bounce">{getWinnerIcon(item.content.placement || '')}</span>
                  {/if}
                  {item.mainerName}
                  {#if item.type === 'winner'}
                    <span class="text-2xl animate-bounce">{getWinnerIcon(item.content.placement || '')}</span>
                  {/if}
                </span>
                <span class="text-xs font-normal text-slate-600 dark:text-slate-300">{formatTimestamp(item.timestamp)}</span>
              </h4>
              {#if item.type === 'challenge'}
                <p class="text-slate-600 dark:text-slate-300">New challenge: <span class="font-medium text-gray-800 dark:text-gray-200">{item.content.challenge}</span></p>
              {:else if item.type === 'response'}
                <p class="text-slate-600 dark:text-slate-300">Submitted response: <span class="font-medium text-gray-800 dark:text-gray-200">{item.content.response}</span></p>
              {:else if item.type === 'score'}
                <p class="text-slate-600 dark:text-slate-300">Received score: <span class="font-semibold text-orange-600 dark:text-orange-400">{item.content.score}/5</span></p>
              {:else if item.type === 'winner'}
                <div class="text-center">
                  <p class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-amber-600 dark:from-yellow-400 dark:to-amber-400 mb-2">
                    🎉 CONGRATULATIONS! 🎉
                  </p>
                  <p class="text-slate-700 dark:text-slate-200">
                    Achieved <span class="font-bold text-lg {item.content.placement === 'First Place' ? 'text-yellow-600 dark:text-yellow-400' : item.content.placement === 'Second Place' ? 'text-gray-600 dark:text-gray-400' : 'text-orange-600 dark:text-orange-400'}">{item.content.placement}</span>
                  </p>
                  <p class="text-slate-700 dark:text-slate-200">
                    and earned <span class="font-bold text-lg text-green-600 dark:text-green-400">{item.content.reward} tokens</span>
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

  .animate-fadeIn {
    animation: fadeIn 0.5s ease-out forwards;
  }

  .animate-pulse-winner {
    animation: pulseWinner 2s 5;
  }

  /* Shimmer effect for winner text */
  .winner-shimmer {
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
  }

  /* Dark mode adjustments */
  :global(.dark) .animate-spin {
    border-color: rgba(96, 165, 250, 0.8);
    border-top-color: transparent;
  }

  /* Enhanced winner glow for dark mode */
  :global(.dark) .animate-pulse-winner {
    box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
  }
</style> 