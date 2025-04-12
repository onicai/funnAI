<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../../store";
  import { push } from 'svelte-spa-router';
  // Import components
  import LotteryInfo from './LotteryInfo.svelte';
  import RedeemCode from './RedeemCode.svelte';

  let dropdownOpen = false;
  
  // Toggle dropdown visibility
  const toggleDropdown = () => {
    dropdownOpen = !dropdownOpen;
  };
  
  // Sample lottery data - would be replaced with data from backend
  let lotteries = [
    {
      id: 1,
      name: "General Lottery",
      description: "Win a chance to create your own mAIner.",
      nextDraw: new Date(Date.now() + 3600000 * 12), // 12 hours from now
      prize: "Own mAIner Creation Slot",
      deposit: 1, // ICP
      isRegistered: false,
      type: "general"
    },
    {
      id: 2,
      name: "Charles Holders Lottery",
      description: "Exclusive lottery for Charles NFT holders.",
      nextDraw: new Date(Date.now() + 3600000 * 24), // 24 hours from now
      prize: "Own mAIner Creation Slot",
      deposit: 0,
      isRegistered: true,
      type: "whitelist"
    },
    {
      id: 3,
      name: "ICPP-Art Holders Lottery",
      description: "Exclusive lottery for ICPP-Art NFT holders.",
      nextDraw: new Date(Date.now() + 3600000 * 48), // 48 hours from now
      prize: "Shared mAIner Creation Slot",
      deposit: 0,
      isRegistered: false,
      type: "whitelist"
    },
    {
      id: 4,
      name: "IConfucius x Odin Holders Perk",
      description: "Special whitelist lottery for @IConfucius_odin holders. Celebrate with us as funnAI comes together — redeem your coupon and enter for a chance to win one mAIner creation slot.",
      nextDraw: new Date(Date.now() + 3600000 * 72), // 72 hours from now
      prize: "One mAIner Creation Slot", 
      deposit: 0,
      isRegistered: false,
      type: "whitelist"
    }
  ];

  // Active results - would be replaced with real data from API
  let results = [
    {
      id: 1,
      lotteryName: "General Lottery",
      result: "Winner",
      prize: "Own mAIner Creation Slot",
      validUntil: new Date(Date.now() + 3600000 * 24), // 24 hours from now
      claimed: false
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

  // Close dropdown when clicking outside
  const handleClickOutside = (event) => {
    const button = document.getElementById('dropdownAccessCodesButton');
    const dropdown = document.getElementById('dropdownAccessCodes');
    
    if (dropdown && button && !dropdown.contains(event.target) && !button.contains(event.target)) {
      dropdownOpen = false;
    }
  };

  // Calculate time remaining
  const getTimeRemaining = (date) => {
    const total = date.getTime() - new Date().getTime();
    const hours = Math.floor((total % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((total % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<!-- Access Codes button -->
<div class="relative inline-block">
  <button 
    id="dropdownAccessCodesButton" 
    on:click={toggleDropdown}
    class="relative inline-flex items-center text-sm font-medium text-center text-gray-500 hover:text-gray-900 focus:outline-none dark:hover:text-white dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-md" 
    type="button"
  >
    <svg class="w-5 h-5 mr-1" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
    </svg>
    Access Codes
    
    <!-- Indicator for active results or registrations -->
    {#if results.length > 0}
      <div class="absolute block w-3 h-3 bg-green-500 border-2 border-white rounded-full -top-0.5 start-2.5 dark:border-gray-900"></div>
    {/if}
  </button>

  <!-- Dropdown menu - positioned based on screen size -->
  <div 
    id="dropdownAccessCodes" 
    class={`z-20 ${dropdownOpen ? '' : 'hidden'} bg-white divide-y divide-gray-100 rounded-lg shadow-lg dark:bg-gray-800 dark:divide-gray-700 mt-2 border border-gray-200 dark:border-gray-700 absolute`} 
    style="width: min(380px, calc(100vw - 20px)); max-height: 90vh; left: -50%; top: 100%;"
    aria-labelledby="dropdownAccessCodesButton"
  >
    <div class="flex justify-between items-center px-4 py-3 font-medium text-gray-700 rounded-t-lg bg-blue-50 dark:bg-blue-900/30 dark:text-white border-b-2 border-blue-100 dark:border-blue-800">
      <span class="font-semibold">Access Codes & Lotteries</span>
      <a href="#/lottery" on:click={() => dropdownOpen = false} class="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-500 dark:hover:text-blue-400">
        View All
      </a>
    </div>
    
    <div class="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
      <!-- Redeem Code Section -->
      <div class="p-4 bg-gray-50 dark:bg-gray-800/50">
        <RedeemCode />
      </div>
      
      <!-- Active Results Section -->
      {#if results.length > 0}
        <div class="p-4 bg-white dark:bg-gray-800">
          <h3 class="text-base font-semibold mb-2 text-gray-800 dark:text-white">Your Rewards</h3>
          {#each results as result (result.id)}
            <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-md mb-2">
              <div class="flex justify-between">
                <div>
                  <div class="font-semibold text-gray-900 dark:text-white">{result.lotteryName}</div>
                  <div class="text-sm text-gray-700 dark:text-gray-300">Prize: {result.prize}</div>
                </div>
                <div class="text-right">
                  <div class="text-green-600 dark:text-green-400 font-semibold">{result.result}</div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">Valid until: {formatDate(result.validUntil)}</div>
                </div>
              </div>
              <div class="mt-2">
                <a href="#/lottery" on:click={() => dropdownOpen = false} class="text-sm text-white bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-600 px-3 py-1 rounded-md inline-block">
                  Claim Prize
                </a>
              </div>
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Lotteries Section -->
      <div class="p-4 bg-gray-50 dark:bg-gray-800/50">
        <h3 class="text-base font-semibold mb-2 text-gray-800 dark:text-white">Available Lotteries</h3>
        
        <!-- Featured Lottery -->
        {#if lotteries.length > 0}
          <LotteryInfo lottery={lotteries[0]} featured={true} />
          
          <!-- Other Lotteries -->
          <div class="mt-3 space-y-2">
            {#each lotteries.slice(1) as lottery (lottery.id)}
              <LotteryInfo {lottery} featured={false} />
            {/each}
          </div>
        {:else}
          <div class="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
            No lotteries available at the moment
          </div>
        {/if}
      </div>
    </div>
  </div>
</div> 