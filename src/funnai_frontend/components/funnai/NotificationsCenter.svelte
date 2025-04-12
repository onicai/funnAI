<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../store";

  let dropdownOpen = false;

  // Sample notification data - could be replaced with real data from API
  let notifications = [
    {
      id: 1,
      sender: "mAIner 1",
      message: "mined 10 $funnai",
      time: "a few moments ago",
      type: "message"
    },
    {
      id: 2,
      sender: "General Lottery",
      message: "Winner of the $funnai lottery. Congrats.",
      time: "10 minutes ago",
      type: "follow"
    },
    {
      id: 3,
      sender: "Charles Lottery",
      message: "Your ticket is valid. Welcome to Charles Lottery.",
      time: "44 minutes ago",
      type: "like"
    },
    {
      id: 4,
      sender: "funnAI",
      message: "Profile validation complete (1 $ICP). Welcome to funnAI.",
      time: "1 hour ago",
      type: "mention"
    }
  ];

  // Toggle dropdown visibility
  const toggleDropdown = () => {
    dropdownOpen = !dropdownOpen;
  };

  // Close dropdown when clicking outside
  const handleClickOutside = (event) => {
    const button = document.getElementById('dropdownNotificationButton');
    const dropdown = document.getElementById('dropdownNotification');
    
    if (dropdown && button && !dropdown.contains(event.target) && !button.contains(event.target)) {
      dropdownOpen = false;
    }
  };


  // Get notification count for badge
  $: notificationCount = notifications.length;
  
  // Function to mark all notifications as read
  const markAllAsRead = () => {
    // In a real app, this would call an API to mark notifications as read
    notifications = [];
  };

  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });
</script>

<!-- Notification button with indicator -->
<div class="relative">
  <button 
    id="dropdownNotificationButton" 
    on:click={toggleDropdown}
    class="relative inline-flex items-center text-sm font-medium text-center text-gray-500 hover:text-gray-900 focus:outline-none dark:hover:text-white dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-md" 
    type="button"
  >
    <svg class="w-5 h-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 14 20">
      <path d="M12.133 10.632v-1.8A5.406 5.406 0 0 0 7.979 3.57.946.946 0 0 0 8 3.464V1.1a1 1 0 0 0-2 0v2.364a.946.946 0 0 0 .021.106 5.406 5.406 0 0 0-4.154 5.262v1.8C1.867 13.018 0 13.614 0 14.807 0 15.4 0 16 .538 16h12.924C14 16 14 15.4 14 14.807c0-1.193-1.867-1.789-1.867-4.175ZM3.823 17a3.453 3.453 0 0 0 6.354 0H3.823Z"/>
    </svg>
    
    <!-- Red dot indicator - only show if there are notifications -->
    {#if notificationCount > 0}
      <div class="absolute block w-3 h-3 bg-red-500 border-2 border-white rounded-full -top-0.5 start-2.5 dark:border-gray-900"></div>
    {/if}
  </button>

  <!-- Dropdown menu -->
  <div 
    id="dropdownNotification" 
    class={`z-20 ${dropdownOpen ? '' : 'hidden'} w-full max-w-sm bg-white divide-y divide-gray-100 rounded-lg shadow-lg dark:bg-gray-800 dark:divide-gray-700 absolute right-0 mt-2 border border-gray-200 dark:border-gray-700`} 
    style="min-width: 320px; right: 0;"
    aria-labelledby="dropdownNotificationButton"
  >
    <div class="flex justify-between items-center px-4 py-3 font-medium text-gray-700 rounded-t-lg bg-blue-50 dark:bg-blue-900/30 dark:text-white border-b-2 border-blue-100 dark:border-blue-800">
      <span class="font-semibold">Notifications</span>
      {#if notificationCount > 0}
        <button 
          on:click={markAllAsRead} 
          class="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-500 dark:hover:text-blue-400"
        >
          Mark all as read
        </button>
      {/if}
    </div>
    
    <div class="divide-y divide-gray-100 dark:divide-gray-700 max-h-80 overflow-y-auto">
      {#if notifications.length === 0}
        <div class="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
          No new notifications
        </div>
      {:else}
        {#each notifications as notification (notification.id)}
          <div class="flex px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 bg-white dark:bg-gray-800">
            <div class="w-full">
              <div class="text-gray-500 text-sm mb-1.5 dark:text-gray-400">
                <span class="font-semibold text-gray-900 dark:text-white">{notification.sender}</span>: {notification.message}
              </div>
              <div class="text-xs text-blue-600 dark:text-blue-500">{notification.time}</div>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</div> 