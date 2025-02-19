<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { store } from "../store";
  import { mockFeedData } from '../helpers/mockFeedData';

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
  }

  let feedItems: FeedItem[] = [];
  let loading = true;
  let interval: NodeJS.Timer;
  let currentIndex = 0;
  let updating = false;

  // Convert milliseconds timestamp to readable time format
  function formatTimestamp(timestamp: number): string {
    const date = new Date(timestamp * 1000); // Convert seconds to milliseconds
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  }

  function getStatusColor(type: string): string {
    switch(type) {
      case 'challenge': return 'before:bg-blue-500';
      case 'response': return 'before:bg-purple-500';
      case 'score': return 'before:bg-orange-500';
      case 'winner': return 'before:bg-emerald-500';
      default: return 'before:bg-gray-500';
    }
  }

  async function getFeedData(): Promise<FeedItem[]> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    return mockFeedData.feedItems;
  }

  async function updateFeed() {
    updating = true;
    const allItems = await getFeedData();
    if (currentIndex < allItems.length) {
      const newItem = {
        ...allItems[currentIndex],
        timestamp: Math.floor(Date.now() / 1000) // Set current timestamp in seconds
      };
      feedItems = [newItem, ...feedItems];
      currentIndex++;
    }
    loading = false;
    updating = false;
  }

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
              <p class="text-slate-500">Received score: {item.content.score}/10</p>
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