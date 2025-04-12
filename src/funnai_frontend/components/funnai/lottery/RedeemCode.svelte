<script lang="ts">
  import { store } from "../../../store";
  
  let code = "";
  let isSubmitting = false;
  let error = "";
  let success = "";
  
  const redeemCode = async () => {
    if (!code) {
      error = "Please enter an access code";
      return;
    }
    
    isSubmitting = true;
    error = "";
    success = "";
    
    try {
      // This would be replaced with an actual API call to the backend
      // For now we're just simulating a successful redemption
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Success simulation
      success = "Code successfully redeemed!";
      code = "";
    } catch (err) {
      error = err.message || "Failed to redeem code. Please try again.";
    } finally {
      isSubmitting = false;
    }
  };
</script>

<div>
  <h3 class="text-base font-semibold mb-2 text-gray-800 dark:text-white">Redeem Access Code</h3>
  <div class="relative">
    <form on:submit|preventDefault={redeemCode} class="flex items-center">
      <div class="relative w-full">
        <input 
          type="text" 
          bind:value={code}
          placeholder="Enter access code" 
          class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          disabled={isSubmitting}
        />
      </div>
      <button 
        type="submit" 
        class="p-2.5 ms-2 text-sm font-medium text-white bg-blue-700 rounded-lg border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        disabled={isSubmitting}
      >
        {#if isSubmitting}
          <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        {:else}
          <svg class="w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
          </svg>
          <span class="sr-only">Submit</span>
        {/if}
      </button>
    </form>
    
    <!-- Error message -->
    {#if error}
      <div class="text-xs text-red-600 mt-1">{error}</div>
    {/if}
    
    <!-- Success message -->
    {#if success}
      <div class="text-xs text-green-600 mt-1">{success}</div>
    {/if}
  </div>
  <div class="text-xs text-gray-500 mt-2 dark:text-gray-400">
    Enter your access code to redeem lottery entries and discounts for mAIner creation.
  </div>
</div> 