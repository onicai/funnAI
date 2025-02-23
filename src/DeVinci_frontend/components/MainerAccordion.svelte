<script lang="ts">
  import { onMount } from 'svelte';
  import CyclesDisplay from './CyclesDisplay.svelte';
  import { userMainerAgentCanisterActors, userMainerAgentCanistersInfo } from "../store";

  $: agentCanisterActors = JSON.parse(JSON.stringify($userMainerAgentCanisterActors));
  $: agentCanistersInfo = JSON.parse(JSON.stringify($userMainerAgentCanistersInfo));

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

  function toggleAccordion(index: string) {
    const content = document.getElementById(`content-${index}`);
    const icon = document.getElementById(`icon-${index}`);
    
    if (!content || !icon) return;

    if (content.style.maxHeight && content.style.maxHeight !== '0px') {
      content.style.maxHeight = '0';
      icon.style.transform = 'rotate(180deg)';
    } else {
      content.style.maxHeight = content.scrollHeight + 'px';
      icon.style.transform = 'rotate(0deg)';
    };
  };

  function createAgent() {
    // TODO: Implement agent creation
    console.log("Creating new agent...");
  };

  function copyAddress() {
    addressCopied = true;
  };

  onMount(async () => {
    console.log("MainerAccordion agentCanisterActors", agentCanisterActors);
    console.log("MainerAccordion agentCanistersInfo", agentCanistersInfo);
    // Retrieve the data from the agents' backend canisters to fill the above agents array dynamically
    agents = await Promise.all(
      // for each agent in the array agentCanisterActors, add an entry to the agents array
      agentCanisterActors.map(async (agentActor, index) => {
        console.log("in MainerAccordion agentCanisterActors.map index ", index);
        console.log("in MainerAccordion agentCanisterActors.map agentActor");
        console.log(agentActor);
        // agentCanistersInfo is an array with each element being an object with info on an agent, it has the same order of agents as agentCanisterActors
        // each entry in agentCanistersInfo looks like so:
          /* type OfficialProtocolCanister = {
              address : CanisterAddress;
              canisterType: ProtocolCanisterType;
              creationTimestamp : Nat64;
              createdBy : Principal;
              ownedBy: Principal;
          }; */
        // use address as the agent's id
        // use mAIner 1, mAIner 2, mAIner 3, etc as the name by incrementing the number
        const canisterInfo = agentCanistersInfo[index];
        console.log("in MainerAccordion agentCanisterActors.map canisterInfo");
        console.log(canisterInfo);
        let status = "active";
        let burnedCycles = 0;
        let cycleBalance = 0;
        let cyclesBurnRate = {};

        try {
          // Retrieve flags that indicate any issues with the agent's canister
          const issueFlagsResult = await agentActor.getIssueFlagsAdmin();
          console.log("in MainerAccordion agentCanisterActors.map issueFlagsResult");
        console.log(issueFlagsResult);
          // IssueFlagsRetrievalResult looks like: type IssueFlagsRetrievalResult = { 'Ok' : IssueFlagsRecord } | { 'Err' : ApiError };
          // and interface IssueFlagsRecord { 'lowCycleBalance' : boolean }
          // if there is an issue, set status on the agent's entry to "inactive", otherwise "active"
          if ('Ok' in issueFlagsResult && issueFlagsResult.Ok.lowCycleBalance) {
            status = "inactive";
          };
        } catch (error) {
          console.error("Error fetching issue flags: ", error);
          status = "inactive";
        };

        try {
          // Retrieve cycle statistics
          const statsResult = await agentActor.getMainerStatisticsAdmin();
          console.log("in MainerAccordion agentCanisterActors.map statsResult");
        console.log(statsResult);
          // StatisticsRetrievalResult looks like: type StatisticsRetrievalResult = { 'Ok' : StatisticsRecord } |  { 'Err' : ApiError };
            /*  and interface StatisticsRecord {
              'cycleBalance' : bigint,
              'totalCyclesBurnt' : bigint,
              'cyclesBurnRate' : CyclesBurnRate,
            }; */
          if ('Ok' in statsResult) {
            burnedCycles = statsResult.Ok.totalCyclesBurnt;
            cycleBalance = statsResult.Ok.cycleBalance;
            cyclesBurnRate = statsResult.Ok.cyclesBurnRate;
          };
        } catch (error) {
          console.error("Error fetching statistics: ", error);
        };

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
  });
</script>

<!-- Create Agent Accordion -->
<div class="border-b border-gray-300 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-t-lg">
  <button on:click={() => toggleAccordion('create')} class="w-full flex justify-between items-center py-5 px-4 text-gray-800 text-sm font-medium">
    <span class="flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-purple-600" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
      </svg>
      Create new mAIner
    </span>
    <span id="icon-create" class="text-gray-600 transition-transform duration-300" style="transform: rotate(180deg)">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
        <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
      </svg>
    </span>
  </button>
  <div id="content-create" class="max-h-0 overflow-hidden transition-all duration-300 ease-in-out bg-white">
    <div class="pb-5 text-sm text-gray-700 space-y-4 p-4">
      

    <ol class="relative mx-2 text-gray-500 border-s border-gray-200">                  
      <li class="mb-10 ms-6">            
          <span class="absolute flex items-center justify-center w-8 h-8 {selectedModel ? 'bg-green-200' : 'bg-gray-200'} rounded-full -start-4 ring-4 ring-white">
              {#if selectedModel}
                <!-- Checkmark icon for when model is selected -->
                <svg class="w-3.5 h-3.5 text-green-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                </svg>
              {:else}
                <!-- Selection/Choose icon for default state -->
                <svg class="w-4 h-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 15L12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9" />
                </svg>
              {/if}
          </span>
          <form class="max-w-sm mx-auto">
            <label for="countries" class="block mb-2 text-sm font-medium text-gray-500">Choose a model</label>
            <select 
              bind:value={selectedModel}
              id="countries" 
              class="bg-gray-50 border border-gray-300 text-gray-500 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5">
              <option value="">Choose model</option>
              <option value="SL">Small LLM</option>
              <option value="G2">Gpt-2</option>
              <option disabled value="QW">Qwen</option>
              <option disabled value="DS">DeepSeek</option>
            </select>
          </form>
      </li>
      <li class="mb-10 ms-6">
          <span class="absolute flex items-center justify-center w-8 h-8 {addressCopied ? 'bg-green-200' : 'bg-gray-100'} rounded-full -start-4 ring-4 ring-white">
              {#if addressCopied}
                <svg class="w-3.5 h-3.5 text-green-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
                </svg>
              {:else}
                <svg class="w-4 h-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="12" y1="2" x2="12" y2="6"/>
                  <line x1="12" y1="18" x2="12" y2="22"/>
                  <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/>
                  <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/>
                  <line x1="2" y1="12" x2="6" y2="12"/>
                  <line x1="18" y1="12" x2="22" y2="12"/>
                  <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/>
                  <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/>
                </svg>
              {/if}
          </span>
          <h3 class="font-medium leading-tight mb-1">Pay & Spin up</h3>
          <div class="flex items-center space-x-2">
            <p class="text-sm text-gray-400 font-mono">kwrfk-ypzrt-wwywz-qov7y-36lis-6rkyv-zdpsp-jgees-uwhhi-7c3eg-gae</p>
            <div class="relative">
              <button class="p-1 hover:bg-gray-200 rounded-full" on:click={copyAddress}>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" viewBox="0 -960 960 960" fill="currentColor">
                  <path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Zm160-240v-480 480Z"/>
                </svg>
              </button>
            </div>
          </div>
      </li>
    </ol>

      <div class="flex justify-end">
        <button on:click={createAgent} class="bg-purple-600 w-1/2 hover:bg-purple-700 text-white px-4 py-2 rounded-[16px] transition-colors">
          Create mAIner
        </button>
      </div>
    </div>
  </div>
</div>

<!-- Existing Agents -->
{#each agents as agent}
  <div class="border-b border-gray-300 bg-white">
    <button on:click={() => toggleAccordion(agent.id.toString())} class="w-full flex justify-between items-center py-5 px-4 text-gray-800 hover:bg-gray-50">
      <span class="flex items-center font-medium text-sm">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-600" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
        </svg>
        {agent.name}
      </span>
      <div class="flex items-center">
        <span class={`mr-4 px-2 py-1 rounded-full text-xs ${agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
          {agent.status}
        </span>
        <span id="icon-{agent.id}" class="text-gray-600 transition-transform duration-300" style="transform: rotate(180deg)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
            <path fill-rule="evenodd" d="M11.78 9.78a.75.75 0 0 1-1.06 0L8 7.06 5.28 9.78a.75.75 0 0 1-1.06-1.06l3.25-3.25a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06Z" clip-rule="evenodd" />
          </svg>
        </span>
      </div>
    </button>
    <div id="content-{agent.id}" class="max-h-0 overflow-hidden transition-all duration-300 ease-in-out">
      <div class="pb-5 text-sm text-gray-700 p-4 bg-gray-5">
        <div class="flex flex-col space-y-2 mb-2">
          <div class="w-full p-4 text-gray-900 bg-gray-100 border border-gray-300 rounded-lg" role="alert">
            <div class="flex items-center justify-between">
                <h2 class="text-sm mb-2">Top up cycles</h2>
                <button type="button" class="py-2.5 px-5 me-2 text-xs font-medium text-gray-900 focus:outline-none bg-white rounded-full border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100">Top-up</button>
            </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2">
          <div class="w-full p-4 text-gray-900 bg-gray-100 border border-gray-300 rounded-lg" role="alert">
            <div class="flex flex-col">
                <h2 class="text-sm mb-2">Set daily burn rate</h2>
                <div class="inline-flex rounded-full shadow-xs w-full justify-end" role="group">
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border border-gray-200 rounded-s-full focus:z-10 focus:ring-2 focus:ring-blue-700 
                    {selectedBurnRate === 'Low' 
                      ? 'bg-purple-600 text-white hover:bg-purple-700' 
                      : 'bg-white text-gray-900 hover:bg-gray-100 hover:text-blue-700'}"
                    on:click={() => selectedBurnRate = 'Low'}
                  >
                    Low
                  </button>
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border-t border-b border-gray-200 focus:z-10 focus:ring-2 focus:ring-blue-700
                    {selectedBurnRate === 'Medium' 
                      ? 'bg-purple-600 text-white hover:bg-purple-700' 
                      : 'bg-white text-gray-900 hover:bg-gray-100 hover:text-blue-700'}"
                    on:click={() => selectedBurnRate = 'Medium'}
                  >
                    Medium
                  </button>
                  <button 
                    type="button" 
                    class="px-4 py-2 text-xs font-medium border border-gray-200 rounded-e-full focus:z-10 focus:ring-2 focus:ring-blue-700
                    {selectedBurnRate === 'High' 
                      ? 'bg-purple-600 text-white hover:bg-purple-700' 
                      : 'bg-white text-gray-900 hover:bg-gray-100 hover:text-blue-700'}"
                    on:click={() => selectedBurnRate = 'High'}
                  >
                    High
                  </button>
                </div>            
              </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2 my-2">
          <div class="w-full p-4 text-gray-900 bg-gray-100 border border-gray-300 rounded-lg" role="alert">
            <div class="flex items-center justify-between">
              <h2 class="text-sm">Manage settings</h2>
            </div>
          </div>
        </div>
        <div class="flex flex-col space-y-2 mb-2">
          <CyclesDisplay cycles={agent.burnedCycles} label="Burned Cycles" />
        </div>

      </div>
    </div>
  </div>
{/each}