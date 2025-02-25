<script lang="ts">
  import { Principal } from "@dfinity/principal";

  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { store } from "../store";
  import { mockFeedData } from '../helpers/mockFeedData';

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;

  interface FeedItem {
    id: string;
    timestamp: number;
    type: 'challenge' | 'response' | 'score' | 'winner';
    mainerName: string;
    content: {
      challenge?: string;
      response?: string;
      score?: number;
      placement?: string;
      reward?: string;
    };
  };

  let feedItems: FeedItem[] = [];
  let allItems: FeedItem[] = [];
  let loading = true;
  let interval: NodeJS.Timer;
  let currentIndex = 0;
  let updating = false;
  let updateCounter = 0;

  // Convert milliseconds timestamp to readable time format
  function formatTimestamp(timestamp: number): string {
    const date = new Date(timestamp * 1000); // Convert seconds to milliseconds
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  function getStatusColor(type: string): string {
    switch(type) {
      case 'challenge': return 'before:bg-blue-500';
      case 'response': return 'before:bg-purple-500';
      case 'score': return 'before:bg-orange-500';
      case 'winner': return 'before:bg-emerald-500';
      default: return 'before:bg-gray-500';
    };
  };

  function sortFeedItemsByTimestamp(feedItems: FeedItem[]): FeedItem[] {
    return feedItems.sort((a, b) => a.timestamp - b.timestamp);
  };

  async function getFeedData(): Promise<FeedItem[]> {
    //console.log("in MainerFeed getFeedData");
    // Get activity data for the feed from the backend canisters
    // Challenges and winners from Game State
    let recentProtocolActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity();
    //let recentProtocolActivityResult = await $store.gameStateCanisterActor.getRecentProtocolActivity_mockup();
    //console.log("MainerFeed recentProtocolActivityResult");
    //console.log(recentProtocolActivityResult);
    let newFeedItems: FeedItem[] = [];
    // recentProtocolActivityResult looks like so: type ProtocolActivityResult = { 'Ok' : ProtocolActivityRecord } | { 'Err' : ApiError };
      /* export interface ProtocolActivityRecord {
        'challenges' : Array<Challenge>,
        'winners' : Array<ChallengeWinnerDeclaration>,
      } */
      /* interface Challenge {
        'challengeClosedTimestamp' : [] | [bigint],
        'challengeTopicStatus' : ChallengeTopicStatus,
        'challengeTopicCreationTimestamp' : bigint,
        'challengeCreationTimestamp' : bigint,
        'challengeCreatedBy' : CanisterAddress,
        'challengeTopicId' : string,
        'challengeStatus' : ChallengeStatus,
        'challengeQuestionSeed' : number,
        'challengeQuestion' : string,
        'challengeId' : string,
        'challengeTopic' : string,
        'submissionCyclesRequired' : bigint,
      } */
      /* interface ChallengeWinnerDeclaration {
        'participants' : List_1,
        'thirdPlace' : ChallengeParticipantEntry,
        'winner' : ChallengeParticipantEntry,
        'secondPlace' : ChallengeParticipantEntry,
        'finalizedTimestamp' : bigint,
        'challengeId' : string,
      } */

    if ('Ok' in recentProtocolActivityResult) {
      const { challenges, winners } = recentProtocolActivityResult.Ok;
        //console.log("in MainerFeed getFeedData winners");
        //console.log(winners);
      // all challenges in challenges are open, for each challenge create an entry for feedItems
      // including challengeCreationTimestamp as timestamp and challengeQuestion as content
      // as mainerName use "Protocol"
      challenges.forEach(challenge => {
        newFeedItems.push({
          id: challenge.challengeId,
          timestamp: Number(challenge.challengeCreationTimestamp),
          type: 'challenge',
          mainerName: 'Protocol',
          content: { challenge: challenge.challengeQuestion }
        });
      });

      // for each ChallengeWinnerDeclaration in winners, create several entries for feedItems
      // one feedItems entry for the winner
      // one feedItems entry for the secondPlace
      // one feedItems entry for the thirdPlace (if there is a thirdPlace)
      /* use the fields on winner, secondPlace and thirdPlace: interface ChallengeParticipantEntry {
        'result' : ChallengeParticipationResult,
        'reward' : ChallengeWinnerReward,
        'ownedBy' : Principal,
        'submittedBy' : Principal,
        'submissionId' : string,
      } */
     // submittedBy on ChallengeParticipantEntry is the mAIner agent that submitted it, compare it to the address field of the entries in agentCanistersInfo (which is an array with each element being an object with info on an agent) and use the index as mainerName (e.g. "mAIner 1", "mAIner 2")
     //console.log("in MainerFeed getFeedData agentCanistersInfo before winners");
        //console.log(agentCanistersInfo); 
        //console.log(agentCanistersInfo[0]); 
      
      if ($store.isAuthed) {
        winners.forEach(winnerDeclaration => {
          //console.log("in MainerFeed getFeedData winners winnerDeclaration");
          //console.log(winnerDeclaration);
          const placements = [
            { position: 'First Place', entry: winnerDeclaration.winner },
            { position: 'Second Place', entry: winnerDeclaration.secondPlace },
            ...(winnerDeclaration.thirdPlace ? [{ position: 'Third Place', entry: winnerDeclaration.thirdPlace }] : [])
          ];
          //console.log("in MainerFeed getFeedData winners placements");
          //console.log(placements);

          placements.forEach(({ position, entry }) => {
            //console.log("in MainerFeed getFeedData winners placements position");
          //console.log(position);
          //console.log("in MainerFeed getFeedData winners placements entry");
          //console.log(entry);
          //console.log(entry.submittedBy);
          //console.log(entry.submittedBy.toString());
          //console.log("in MainerFeed getFeedData agentCanistersInfo address");
        //console.log(agentCanistersInfo[0].address); 
        //console.log(agentCanistersInfo[1]?.address); 
          //console.log(agentCanistersInfo[0].address === entry.submittedBy.toString());
          //console.log(agentCanistersInfo[1].address === entry.submittedBy.toString());
            const mainerIndex = agentCanistersInfo.findIndex(agent => agent.address === entry.submittedBy.toString());
            //console.log("in MainerFeed getFeedData winners placements mainerIndex");
          //console.log(mainerIndex);
            const mainerName = mainerIndex !== -1 ? `mAIner ${mainerIndex + 1}` : `Other User's Agent`;
            //console.log("in MainerFeed getFeedData winners placements mainerIndex");
          //console.log(mainerIndex);
          //console.log("in MainerFeed getFeedData winners placements mainerName");
          //console.log(mainerName);

            newFeedItems.push({
              id: `${entry.submissionId}-winner`,
              timestamp: Number(winnerDeclaration.finalizedTimestamp),
              type: 'winner',
              mainerName,
              content: {
                placement: position,
                reward: entry.reward.amount.toString()
              }
            });
          });
        });
      };
      //console.log("in MainerFeed getFeedData newFeedItems after winners");
      //console.log(newFeedItems);
    };
    
    if ($store.isAuthed) {
      //console.log("MainerFeed agentCanisterActors");
      //console.log(agentCanisterActors);
      //console.log("MainerFeed agentCanistersInfo");
      //console.log(agentCanistersInfo);
      // Add user's mAIner agents' submissions and scores (for submissions) to newFeedItems
      // for each agent in the array agentCanisterActors, retrieve the agent's submissions
      for (const [index, agent] of agentCanisterActors.entries()) {
        //console.log("in MainerFeed getFeedData agentCanisterActors entries index");
        //console.log(index);
        //console.log("in MainerFeed getFeedData agentCanisterActors entries agent");
        //console.log(agent);
        try {
          const submissionsResult = await agent.getRecentSubmittedResponsesAdmin();
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
              'challengeAnswer' : string,
            } */

          // for each ChallengeResponseSubmission add an entry to newFeedItems
          if ('Ok' in submissionsResult) {
            for (const submission of submissionsResult.Ok) {
              //console.log("in MainerFeed getFeedData agentCanisterActors entries submission");
        //console.log(submission);
              const mainerName = `mAIner ${index + 1}`;
              newFeedItems.push({
                id: submission.submissionId,
                timestamp: Number(submission.submittedTimestamp),
                type: 'response',
                mainerName,
                content: { response: submission.challengeAnswer }
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
                    'challengeAnswer' : string,
                    'scoreSeed' : number,
                  } */
                // note that the submission might not have received a score yet (ScoredResponseRetrievalResult returns an Err in that case)

                // if there's a score for the submission, add the score as an entry to newFeedItems
              try {
                const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission({
                  challengeId: submission.challengeId,
                  submissionId: submission.submissionId
                });
                /* const scoreResult = await $store.gameStateCanisterActor.getScoreForSubmission_mockup({
                  challengeId: submission.challengeId,
                  submissionId: submission.submissionId
                }); */
                
                //console.log("in MainerFeed getFeedData agentCanisterActors entries scoreResult");
        //console.log(scoreResult);

                if ('Ok' in scoreResult) {
                  newFeedItems.push({
                    id: `${submission.submissionId}-score`,
                    timestamp: Number(scoreResult.Ok.judgedTimestamp),
                    type: 'score',
                    mainerName,
                    content: { score: Number(scoreResult.Ok.score) }
                  });
                };
              } catch (error) {
                console.error("Error fetching score for submission", error);
              };
            };
          };
        } catch (error) {
          console.error("Error fetching submissions", error);
        };
      };
    };
    //console.log("in MainerFeed getFeedData newFeedItems before return");
        //console.log(newFeedItems);
    return sortFeedItemsByTimestamp(newFeedItems);
  };

  async function updateFeed(forceUpdate = false) {
    updating = true;
    if (forceUpdate || updateCounter % 10 === 0) {
      console.log("Time to run getFeedData again");
      allItems = await getFeedData();
      console.log("after getFeedData allItems");
      console.log(allItems);
    };
    // TODO: only add new items to feed
    if (currentIndex < allItems.length) {
      const newItem = {
        ...allItems[currentIndex],
        timestamp: Math.floor(Date.now() / 1000) // Set current timestamp in seconds
      };
      feedItems = [newItem, ...feedItems];
      currentIndex++;
    };
    loading = false;
    updating = false;
    updateCounter++;
  };

  $: {
    console.log("MainerFeed reactive agentCanisterActors", agentCanisterActors);
    console.log("MainerFeed reactive agentCanistersInfo", agentCanistersInfo);

    (async () => {
      await updateFeed(true);
    })();
  };

  onMount(async () => {
    await updateFeed();
    interval = setInterval(updateFeed, 10000); // Update every 10 seconds

    return () => {
      if (interval) clearInterval(interval);
    };
  });
</script>

<div class="max-h-[600px] overflow-y-auto">
  {#if updating}
    <div class="flex justify-center py-2">
      <div class="animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent"></div>
    </div>
  {/if}
  <ul 
    aria-label="mAIner Activity Feed" 
    role="feed" 
    class="relative flex flex-col gap-8 py-12 pl-6 text-sm 
           before:absolute before:top-0 before:left-6 before:h-full before:border before:-translate-x-1/2 before:border-slate-200 before:border-dashed before:z-[-1] 
           after:absolute after:top-6 after:left-6 after:bottom-6 after:border after:-translate-x-1/2 after:border-slate-200 after:z-[-1]"
  >
    {#if loading}
      <li class="text-center text-gray-500">Loading feed...</li>
    {:else}
      {#each feedItems as item (item.id)}
        <li 
          role="article" 
          class="relative pl-6 
                 before:absolute before:z-10 before:left-0 before:top-2 before:h-2 before:w-2 before:-translate-x-1/2 before:rounded-full {getStatusColor(item.type)} before:ring-2 before:ring-white animate-fadeIn"
          in:fly="{{ y: 20, duration: 500 }}"
        >
          <div class="flex flex-col flex-1 gap-2">
            <h4 class="text-base font-medium flex justify-between items-center mr-6">
              {item.mainerName}
              <span class="text-xs font-normal text-slate-500">{formatTimestamp(item.timestamp)}</span>
            </h4>
            {#if item.type === 'challenge'}
              <p class="text-slate-500">Received challenge: {item.content.challenge}</p>
            {:else if item.type === 'response'}
              <p class="text-slate-500">Submitted response: {item.content.response}</p>
            {:else if item.type === 'score'}
              <p class="text-slate-500">Received score: {item.content.score}/5</p>
            {:else if item.type === 'winner'}
              <p class="text-slate-500">Achieved {item.content.placement} and earned {item.content.reward}</p>
            {/if}
          </div>
        </li>
      {/each}
    {/if}
  </ul>
</div>

<style>
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .animate-fadeIn {
    animation: fadeIn 0.5s ease-out forwards;
  }
</style> 