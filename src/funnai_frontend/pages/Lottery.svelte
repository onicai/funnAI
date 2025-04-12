<script lang="ts">
  import { store } from "../store";
  import RedeemCode from "../components/funnai/lottery/RedeemCode.svelte";
  import LotteryInfo from "../components/funnai/lottery/LotteryInfo.svelte";
  import { onMount } from "svelte";
  
  // Sample lottery data - would be replaced with data from backend
  let lotteries = [
    {
      id: 1,
      name: "General Lottery",
      description: "Win a chance to create your own mAIner. This lottery requires a deposit of 1 ICP, which will be credited toward your mAIner creation fee if you win.",
      nextDraw: new Date(Date.now() + 3600000 * 12), // 12 hours from now
      prize: "Own mAIner creation slot",
      deposit: 1, // ICP
      isRegistered: false,
      type: "general",
      participants: 156,
      slots: 10
    },
    {
      id: 2,
      name: "Charles Holders Lottery",
      description: "Exclusive lottery for Charles NFT holders. Redeem your Charles coupon to enter this lottery and get a chance to win a discounted mAIner creation slot.",
      nextDraw: new Date(Date.now() + 3600000 * 24), // 24 hours from now
      prize: "Own mAIner creation slot",
      deposit: 0,
      isRegistered: true,
      type: "whitelist",
      participants: 42,
      slots: 5
    },
    {
      id: 3,
      name: "ICPP-Art Holders Lottery",
      description: "Exclusive lottery for ICPP-Art NFT holders. Redeem your ICPP-Art coupon to enter this lottery and get a chance to win a shared mAIner creation slot.",
      nextDraw: new Date(Date.now() + 3600000 * 48), // 48 hours from now
      prize: "Shared mAIner Creation Slot",
      deposit: 0,
      isRegistered: false,
      type: "whitelist",
      participants: 28,
      slots: 3
    },
    {
      id: 4,
      name: "IConfucius x Odin Holders Perk",
      description: "Special whitelist lottery for @IConfucius_odin holders. Celebrate with us as funnAI comes together — redeem your coupon and enter for a chance to win one mAIner creation slot.",
      nextDraw: new Date(Date.now() + 3600000 * 72), // 72 hours from now
      prize: "One mAIner creation slot", 
      deposit: 0,
      isRegistered: false,
      type: "whitelist",
      participants: 0,
      slots: 5
    }
  ];
  
  // Active results - would be replaced with real data from API
  let results = [
    {
      id: 1,
      lotteryName: "General Lottery",
      result: "Winner",
      prize: "Own mAIner creation slot",
      validUntil: new Date(Date.now() + 3600000 * 24), // 24 hours from now
      claimed: false,
      drawDate: new Date(Date.now() - 3600000 * 2) // 2 hours ago
    }
  ];
  
  
  // Format date to readable string
  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };
  
  onMount(async () => {
    // Here we would fetch data from the backend
  });
</script>

<div class="container mx-auto px-4 py-8 dark:bg-gray-900">
  <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Access Codes & Lotteries</h1>
  
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Left Column -->
    <div class="lg:col-span-2">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Active Lotteries</h2>
        
        <!-- General Lottery -->
        {#if lotteries.length > 0}
          {#each lotteries.filter(l => l.type === "general") as lottery (lottery.id)}
            <div class="mb-6">
              <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-5 shadow-sm border border-blue-100 dark:border-blue-800">
                <div class="flex justify-between items-start mb-3">
                  <div>
                    <h3 class="text-xl font-bold text-blue-800 dark:text-blue-300">{lottery.name}</h3>
                    <p class="text-gray-600 dark:text-gray-400 mt-1">{lottery.description}</p>
                  </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <div class="bg-white/50 dark:bg-gray-900/30 p-3 rounded-md">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Prize</div>
                    <div class="text-base font-medium text-gray-800 dark:text-gray-200">{lottery.prize}</div>
                  </div>
                  <div class="bg-white/50 dark:bg-gray-900/30 p-3 rounded-md">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Next Draw</div>
                    <div class="text-base font-medium text-gray-800 dark:text-gray-200">{formatDate(lottery.nextDraw)}</div>
                  </div>
                  <div class="bg-white/50 dark:bg-gray-900/30 p-3 rounded-md">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Participants</div>
                    <div class="text-base font-medium text-gray-800 dark:text-gray-200">{lottery.participants} / {lottery.slots} slots</div>
                  </div>
                </div>
                
                {#if lottery.deposit > 0}
                  <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 rounded-md p-3 mt-4">
                    <div class="font-medium text-yellow-800 dark:text-yellow-300">Deposit Required</div>
                    <div class="text-sm text-gray-700 dark:text-gray-300 mt-1">
                      This lottery requires a deposit of {lottery.deposit} ICP. The deposit will be credited toward your mAIner creation fee if you win.
                    </div>
                  </div>
                {/if}
                
                <div class="mt-4 flex items-center justify-between">
                  <div>
                    <span class="text-blue-600 dark:text-blue-400 font-semibold text-lg">{lottery.nextDraw.getHours() - new Date().getHours()}h {lottery.nextDraw.getMinutes() - new Date().getMinutes()}m</span>
                    <span class="text-gray-500 dark:text-gray-400"> remaining</span>
                  </div>
                  
                  {#if lottery.isRegistered}
                    <div class="flex items-center">
                      <div class="bg-green-100 dark:bg-green-900/30 px-3 py-1.5 rounded-md flex items-center mr-2">
                        <svg class="w-4 h-4 text-green-600 dark:text-green-400 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span class="text-green-800 dark:text-green-300 font-medium">Registered</span>
                      </div>
                    </div>
                  {:else}
                    <button 
                      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium"
                    >
                      Register with {lottery.deposit} ICP
                    </button>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        {/if}
        
        <!-- Whitelist Lotteries -->
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mt-8 mb-4">Whitelist Lotteries</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each lotteries.filter(l => l.type === "whitelist") as lottery (lottery.id)}
            <div class="bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg p-4">
              <div class="flex justify-between items-start">
                <h4 class="text-base font-semibold text-gray-900 dark:text-white">{lottery.name}</h4>
                <span class="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-xs font-medium px-2 py-0.5 rounded">Whitelist</span>
              </div>
              
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">{lottery.description}</p>
              
              <div class="mt-3 grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-500 dark:text-gray-400">Draw:</span>
                  <span class="text-gray-900 dark:text-white"> {formatDate(lottery.nextDraw)}</span>
                </div>
                <div>
                  <span class="text-gray-500 dark:text-gray-400">Prize:</span>
                  <span class="text-gray-900 dark:text-white"> {lottery.prize}</span>
                </div>
              </div>
              
              <div class="mt-3 flex justify-between items-center">
                <div class="text-xs text-gray-500 dark:text-gray-400">
                  {lottery.participants} participants / {lottery.slots} slots
                </div>
                
                {#if lottery.isRegistered}
                  <div class="bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded text-xs text-green-800 dark:text-green-300 font-medium">
                    Registered
                  </div>
                {:else}
                  <div class="text-sm text-white bg-purple-600 dark:bg-purple-700 px-3 py-1 rounded-md">
                    Need Access Code
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
      
      
    </div>
    
    <!-- Right Column -->
    <div>
      <!-- Redeem Code Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <div class="mb-6">
          <RedeemCode />
        </div>
        
        <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3">Access Code Benefits</h3>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li class="flex items-start">
              <svg class="w-4 h-4 text-green-500 mt-0.5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Entry to exclusive whitelist lotteries
            </li>
            <li class="flex items-start">
              <svg class="w-4 h-4 text-green-500 mt-0.5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              First to create a mAIner
            </li>
            <li class="flex items-start">
              <svg class="w-4 h-4 text-green-500 mt-0.5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Early access to new features
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Redemption History -->
      <!-- Lottery Results -->
      {#if results.length > 0}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Your Lottery Results</h2>
          
          {#each results as result (result.id)}
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-5 shadow-sm border border-green-100 dark:border-green-800">
              <div class="flex justify-between items-start">
                <div>
                  <div class="flex items-center">
                    <span class="text-xl font-bold text-green-700 dark:text-green-300">Winner!</span>
                    <span class="ml-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs font-medium px-2 py-0.5 rounded">
                      {result.lotteryName}
                    </span>
                  </div>
                  <p class="text-gray-600 dark:text-gray-400 mt-1">
                    Congratulations! You won a {result.prize} in the {result.lotteryName}.
                  </p>
                </div>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div class="bg-white/50 dark:bg-gray-900/30 p-3 rounded-md">
                  <div class="text-sm text-gray-500 dark:text-gray-400">Draw Date</div>
                  <div class="text-base font-medium text-gray-800 dark:text-gray-200">{formatDate(result.drawDate)}</div>
                </div>
                <div class="bg-white/50 dark:bg-gray-900/30 p-3 rounded-md">
                  <div class="text-sm text-gray-500 dark:text-gray-400">Valid Until</div>
                  <div class="text-base font-medium text-gray-800 dark:text-gray-200">{formatDate(result.validUntil)}</div>
                </div>
              </div>
              
              <div class="mt-4">
                <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-100 dark:border-yellow-800 rounded-md p-3">
                  <div class="font-medium text-yellow-800 dark:text-yellow-300">Time-Limited Offer</div>
                  <div class="text-sm text-gray-700 dark:text-gray-300 mt-1">
                    Your prize must be claimed within 24 hours. After that, the slot will be given to another participant.
                  </div>
                </div>
              </div>
              
              <div class="mt-4 flex justify-end">
                <a href="/#/" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md font-medium">
                  Create mAIner
                </a>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div> 