<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import CyclesDisplayAgent from './CyclesDisplayAgent.svelte';
  import { store } from "../../stores/store";
  import LoginModal from '../login/LoginModal.svelte';
  import SendTokenModal from '../SendTokenModal.svelte';

  $: agentCanisterActors = $store.userMainerCanisterActors;
  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;
  $: isAuthenticated = $store.isAuthed;

  let agents = [
    // Add the agent entries dynamically via the calls in onMount
    // TODO: remove these dummy entries
    /* { id: 1, name: "mAIner 1", status: "active", burnedCycles: 1234567 },
    { id: 2, name: "mAIner 2", status: "inactive", burnedCycles: 890123 } */
  ];

  let selectedBurnRate: 'Low' | 'Medium' | 'High' = 'Medium'; // Default value
  let showCopyIndicator = false;
  let selectedModel = ""; // track selected model
  let addressCopied = false;
  let modelType: 'Own' | 'Shared' = 'Own'; // Default to Own model
  let loginModalOpen = false;
  let sendTokenModalOpen = false;
  let funnai_address = "opcne-svazk-6dnsy-iejci-fsm7h-miuun-ovpm4-wtsgw-5pgbz-teu3h-eqe"; // Default address to send tokens to
  
  // Reference to the SendTokenModal's input fields
  let recipientAddressInput: HTMLInputElement;
  let amountInput: HTMLInputElement;

  function toggleAccordion(index: string) {
    const content = document.getElementById(`content-${index}`);
    const icon = document.getElementById(`icon-${index}`);
    
    if (!content || !icon) return;

    content.classList.toggle('accordion-open');
    if (content.classList.contains('accordion-open')) {
      icon.style.transform = 'rotate(0deg)';
    } else {
      icon.style.transform = 'rotate(180deg)';
    }
  };

  function createAgent() {
    // Open the SendTokenModal to handle the payment
    sendTokenModalOpen = true;
    
    // Call our function to lock and pre-fill the fields
    lockSendTokenModalFields();
  };
  
  function handleSendComplete(txId?: string) {
    console.log("Payment completed" + (txId ? ` with transaction ID: ${txId}` : ""));
    sendTokenModalOpen = false;
    
    // Here we would implement the actual agent creation logic
    console.log(`Creating new ${modelType} mAIner model after payment...`);
    
    // TODO: Call the backend API to create the mAIner with the selected model type
    // You can use the txId as proof of payment if needed
  };

  // Function to lock and pre-fill the fields in the SendTokenModal once it's opened
  function lockSendTokenModalFields() {
    // Need to use setTimeout to ensure the DOM has updated after the modal opens
    setTimeout(() => {
      // Find the recipient address input field
      const recipientInput = document.getElementById('recipient-address') as HTMLInputElement;
      if (recipientInput) {
        recipientInput.value = funnai_address;
        recipientInput.disabled = true;
        
        // Manually trigger the input event to validate the address
        const inputEvent = new Event('input', { bubbles: true });
        recipientInput.dispatchEvent(inputEvent);
      }
      
      // Find the amount input field
      const amountInputField = document.getElementById('amount-input') as HTMLInputElement;
      if (amountInputField) {
        amountInputField.value = modelType === 'Own' ? '0.05' : '0.03';
        amountInputField.disabled = true;
        
        // Manually trigger the input event to validate the amount
        const inputEvent = new Event('input', { bubbles: true });
        amountInputField.dispatchEvent(inputEvent);
      }
      
      // Hide the "Send Max" button
      const sendMaxButton = document.querySelector('[class*="text-blue-500"]') as HTMLButtonElement;
      if (sendMaxButton) {
        sendMaxButton.style.display = 'none';
      }
    }, 500); // Wait for 500ms to ensure modal is fully rendered
  }

  function copyAddress() {
    addressCopied = true;
  };

  async function loadAgents() {
    return await Promise.all(
      agentCanisterActors.map(async (agentActor, index) => {
        //console.log("in MainerAccordion agentCanisterActors.map index ", index);
        //console.log("in MainerAccordion agentCanisterActors.map agentActor", agentActor);
        
        const canisterInfo = agentCanistersInfo[index];
        //console.log("in MainerAccordion agentCanisterActors.map canisterInfo", canisterInfo);
        let status = "active";
        let burnedCycles = 0;
        let cycleBalance = 0;
        let cyclesBurnRate = {};

        try {
          const issueFlagsResult = await agentActor.getIssueFlagsAdmin();
          //console.log("in MainerAccordion agentCanisterActors.map issueFlagsResult", issueFlagsResult);
          if ('Ok' in issueFlagsResult && issueFlagsResult.Ok.lowCycleBalance) {
            status = "inactive";
          };
        } catch (error) {
          console.error("Error fetching issue flags: ", error);
          status = "inactive";
        };

        try {
          const statsResult = await agentActor.getMainerStatisticsAdmin();
          //console.log("in MainerAccordion agentCanisterActors.map statsResult", statsResult);
          if ('Ok' in statsResult) {
            burnedCycles = Number(statsResult.Ok.totalCyclesBurnt);
            cycleBalance = Number(statsResult.Ok.cycleBalance);
            cyclesBurnRate = statsResult.Ok.cyclesBurnRate;
          };
        } catch (error) {
          console.error("Error fetching statistics: ", error);
        };

        //console.log("in MainerAccordion agentCanisterActors.map before return id ", canisterInfo.address);
        //console.log("in MainerAccordion agentCanisterActors.map before return name ", `mAIner ${index + 1}`);
        //console.log("in MainerAccordion agentCanisterActors.map before return status ", status);
        //console.log("in MainerAccordion agentCanisterActors.map before return burnedCycles ", burnedCycles);
        //console.log("in MainerAccordion agentCanisterActors.map before return cycleBalance ", cycleBalance);
        //console.log("in MainerAccordion agentCanisterActors.map before return cyclesBurnRate ", cyclesBurnRate);

        return {
          id: canisterInfo.address,
          name: `mAIner ${index + 1}`,
          status,
          burnedCycles,
          cycleBalance,
          cyclesBurnRate
        };
      })
    );
  };

  $: {
    console.log("MainerAccordion reactive agentCanisterActors", agentCanisterActors);
    console.log("MainerAccordion reactive agentCanistersInfo", agentCanistersInfo);

    (async () => {
      agents = await loadAgents();
    })();
  };

  function toggleLoginModal() {
    loginModalOpen = !loginModalOpen;
  }

  onMount(async () => {
    //console.log("MainerAccordion onMount agentCanisterActors", agentCanisterActors);
    //console.log("MainerAccordion onMount agentCanistersInfo", agentCanistersInfo);
    // Retrieve the data from the agents' backend canisters to fill the above agents array dynamically
    agents = await loadAgents();
    //console.log("MainerAccordion onMount agents", agents);
    
    // Automatically open the create accordion if no agents exist, regardless of auth status
    if (agents.length === 0) {
      setTimeout(() => {
        toggleAccordion('create');
      }, 100);
    }
  });

  // Watch for changes in agents or auth status
  $: if (agents.length === 0) {
    setTimeout(() => {
      const content = document.getElementById(`content-create`);
      const icon = document.getElementById(`icon-create`);
      if (content && icon) {
        if (!content.classList.contains('accordion-open')) {
          content.classList.add('accordion-open');
          icon.style.transform = 'rotate(0deg)';
        }
      }
    }, 100);
  }
</script>

<!-- Create Agent Accordion -->
<div class="border-b border-gray-300 dark:border-gray-700 bg-gradient-to-r from-purple-600/20 to-blue-600/20 dark:from-purple-900/40 dark:to-blue-900/40 rounded-t-lg">
  <button on:click={() => toggleAccordion('create')} class="w-full flex justify-between items-center py-5 px-4 text-gray-800 dark:text-gray-200 text-sm font-medium">
    <span class="flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
      </svg>
      Create new mAIner
    </span>
    <span id="icon-create" class="text-gray-600 dark:text-gray-400 transition-transform duration-300" style="transform: rotate(180deg)">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
        <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
  <div id="content-create" class="accordion-content bg-white dark:bg-gray-900">
    <div class="pb-5 text-sm text-gray-700 dark:text-gray-300 space-y-4 p-4">
      
    {#if isAuthenticated}
      <ol class="relative mx-2 text-gray-500 dark:text-gray-400 border-s border-gray-200 dark:border-gray-700">                  
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {modelType ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                </svg>
            </span>
            <h3 class="font-medium leading-tight mb-2 dark:text-gray-300">Model Type</h3>
            <div class="inline-flex rounded-full shadow-xs w-full justify-start mb-1" role="group">
              <button 
                type="button" 
                class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
                {modelType === 'Own' 
                  ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                on:click={() => modelType = 'Own'}
              >
                Own model
              </button>
              <button 
                type="button" 
                class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-e-full focus:z-10 focus:ring-2 focus:ring-blue-700
                {modelType === 'Shared' 
                  ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                on:click={() => modelType = 'Shared'}
              >
                Shared model
              </button>
            </div>
        </li>
        <li class="mb-6 ms-6">            
            <span class="absolute flex items-center justify-center w-8 h-8 {selectedModel ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-200 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if selectedModel}
                  <!-- Checkmark icon for when model is selected -->
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <!-- Selection/Choose icon for default state -->
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                  </svg>
                {/if}
            </span>
            {#if modelType === 'Own'}
            <form class="max-w-sm mx-auto">
              <label for="countries" class="block mb-2 text-sm font-medium text-gray-500 dark:text-gray-300">Choose a model</label>
              <select 
                bind:value={selectedModel}
                id="countries" 
                class="bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 text-gray-500 dark:text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
                <option value="">Choose model</option>
                <option value="SL">Small LLM</option>
                <option value="G2">Gpt-2</option>
                <option value="QW">Qwen</option>
                <option disabled value="DS">DeepSeek</option>
              </select>
            </form>
            {/if}
        </li>
        <li class="mb-6 ms-6">
            <span class="absolute flex items-center justify-center w-8 h-8 {addressCopied ? 'bg-green-200 dark:bg-green-800' : 'bg-gray-100 dark:bg-gray-800'} rounded-full -start-4 ring-4 ring-white dark:ring-gray-900">
                {#if addressCopied}
                  <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                      <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                  </svg>
                {:else}
                  <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
                {/if}
            </span>
            <h3 class="font-medium leading-tight mb-1 dark:text-gray-300">Pay & Spin up</h3>
            <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-md p-3 mb-3">
              <p class="text-xs text-blue-800 dark:text-blue-300">
                Create mAIner requires a payment fee of <span class="font-medium">{modelType === 'Own' ? '0.05' : '0.03'} ICP</span> for {modelType} model
              </p>
            </div>
        </li>
      </ol>

      <div class="flex justify-end">
        <button on:click={createAgent} class="bg-purple-600 dark:bg-purple-700 w-1/2 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-4 py-2 rounded-[16px] transition-colors">
          Pay & Create mAIner ({modelType === 'Own' ? '0.05' : '0.03'} ICP)
        </button>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center py-8">
        <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2 mt-8">You need to login first</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4 text-center">
          Connect your wallet to create and manage your mAIners
        </p>
        <button 
          on:click={toggleLoginModal} 
          class="bg-purple-600 dark:bg-purple-700 hover:bg-purple-700 dark:hover:bg-purple-800 text-white px-6 py-2 rounded-full transition-colors flex items-center"
        >
          <svg class="w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2z" clip-rule="evenodd" />
          </svg>
          Login to Connect
        </button>
      </div>
    {/if}
    </div>
  </div>
</div>

{#if loginModalOpen}
  <LoginModal toggleModal={toggleLoginModal} />
{/if}

{#if sendTokenModalOpen}
  <SendTokenModal 
    isOpen={sendTokenModalOpen}
    onClose={() => sendTokenModalOpen = false}
    token={{
      name: "Internet Computer for mAIner Creation",
      symbol: "ICP",
      decimals: 8,
      fee_fixed: "10000" // standard ICP fee
    }}
    onSuccess={handleSendComplete}
  />
{/if}

<!-- Existing Agents -->
{#each agents as agent}
  <div class="border-b border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900">
    <button on:click={() => toggleAccordion(agent?.id?.toString())} class="w-full flex justify-between items-center py-5 px-4 text-gray-800 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800">
      <span class="flex items-center font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-600 dark:text-gray-400" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
        </svg>
        {agent.name}
      </span>
      <div class="flex items-center">
        <span class={`mr-4 px-2 py-1 rounded-full text-xs ${agent.status === 'active' ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-400'}`}>
          {agent.status}
        </span>
        <span id="icon-{agent.id}" class="text-gray-600 dark:text-gray-400 transition-transform duration-300" style="transform: rotate(180deg)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
            <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
          </svg>
        </span>
      </div>
    </button>
    <div id="content-{agent.id}" class="accordion-content">
      <div class="pb-5 text-sm text-gray-700 dark:text-gray-300 p-4 bg-gray-5 dark:bg-gray-900">
        <div class="flex flex-col space-y-2 mb-2">
          <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
            <div class="flex items-center justify-between">
                <h2 class="text-sm mb-2">Top up cycles</h2>
                <button type="button" class="py-2.5 px-5 me-2 text-xs font-medium text-gray-900 dark:text-gray-300 focus:outline-none bg-white dark:bg-gray-700 rounded-full border border-gray-200 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700">Top-up</button>
            </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2">
          <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
            <div class="flex flex-col">
                <h2 class="text-sm mb-2">Set daily burn rate</h2>
                <div class="inline-flex rounded-full shadow-xs w-full justify-end" role="group">
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
                    {selectedBurnRate === 'Low' 
                      ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                      : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                    on:click={() => selectedBurnRate = 'Low'}
                  >
                    Low
                  </button>
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border-t border-b border-gray-200 dark:border-gray-600 focus:z-10 focus:ring-2 focus:ring-blue-700
                    {selectedBurnRate === 'Medium' 
                      ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                      : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                    on:click={() => selectedBurnRate = 'Medium'}
                  >
                    Medium
                  </button>
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border border-gray-200 dark:border-gray-600 rounded-e-full focus:z-10 focus:ring-2 focus:ring-blue-700
                    {selectedBurnRate === 'High' 
                      ? 'bg-purple-600 dark:bg-purple-700 text-white hover:bg-purple-700 dark:hover:bg-purple-800' 
                      : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 hover:text-blue-700 dark:hover:text-blue-400'}"
                    on:click={() => selectedBurnRate = 'High'}
                  >
                    High
                  </button>
                </div>            
              </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2 my-2">
          <div class="w-full p-4 text-gray-900 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg" role="alert">
            <div class="flex items-center justify-between">
              <h2 class="text-sm">Manage settings</h2>
            </div>
          </div>
        </div>
        <div class="flex flex-col space-y-2 mb-2">
          <CyclesDisplayAgent cycles={agent.burnedCycles} label="Burned Cycles" />
        </div>

      </div>
    </div>
  </div>
{/each}

<style>
  .accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: all 0.3s ease-in-out;
  }
  
  .accordion-content.accordion-open {
    max-height: 2000px; /* High value to ensure all content is visible */
    overflow: visible;
  }
</style>