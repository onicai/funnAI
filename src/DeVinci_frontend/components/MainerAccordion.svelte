<script lang="ts">
  import { onMount } from 'svelte';

  let agents = [
    { id: 1, name: "mAIner 1", status: "active" },
    { id: 2, name: "mAIner 2", status: "inactive" }
  ];

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
    }
  }

  function createAgent() {
    // TODO: Implement agent creation
    console.log("Creating new agent...");
  }
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
      

    <ol class="relative mx-2 text-gray-500 border-s border-gray-200 dark:border-gray-700 dark:text-gray-400">                  
      <li class="mb-10 ms-6">            
          <span class="absolute flex items-center justify-center w-8 h-8 bg-green-200 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-green-900">
              <svg class="w-3.5 h-3.5 text-green-500 dark:text-green-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 12">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5.917 5.724 10.5 15 1.5"/>
              </svg>
          </span>
          <form class="max-w-sm mx-auto">
            <label for="countries" class="block mb-2 text-sm font-medium text-gray-500 dark:text-white">Choose a model</label>
            <select id="countries" class="bg-gray-50 border border-gray-300 text-gray-500 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
              <option selected>Choose model</option>
              <option value="SL">Small LLM</option>
              <option value="G2">Gpt-2</option>
              <option disabled value="QW">Qwen</option>
              <option disabled value="DS">DeepSeek</option>
            </select>
          </form>
      </li>
      <li class="mb-10 ms-6">
          <span class="absolute flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-gray-700">
              <svg class="w-3.5 h-3.5 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 16">
                  <path d="M18 0H2a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2ZM6.5 3a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5ZM3.014 13.021l.157-.625A3.427 3.427 0 0 1 6.5 9.571a3.426 3.426 0 0 1 3.322 2.805l.159.622-6.967.023ZM16 12h-3a1 1 0 0 1 0-2h3a1 1 0 0 1 0 2Zm0-3h-3a1 1 0 1 1 0-2h3a1 1 0 1 1 0 2Zm0-3h-3a1 1 0 1 1 0-2h3a1 1 0 1 1 0 2Z"/>
              </svg>
          </span>
          <h3 class="font-medium leading-tight">Account Info</h3>
          <p class="text-sm">Step details here</p>
      </li>
      <li class="mb-10 ms-6">
          <span class="absolute flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-gray-700">
              <svg class="w-3.5 h-3.5 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 20">
                  <path d="M16 1h-3.278A1.992 1.992 0 0 0 11 0H7a1.993 1.993 0 0 0-1.722 1H2a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2Zm-3 14H5a1 1 0 0 1 0-2h8a1 1 0 0 1 0 2Zm0-4H5a1 1 0 0 1 0-2h8a1 1 0 1 1 0 2Zm0-5H5a1 1 0 0 1 0-2h2V2h4v2h2a1 1 0 1 1 0 2Z"/>
              </svg>
          </span>
          <h3 class="font-medium leading-tight">Review</h3>
          <p class="text-sm">Step details here</p>
      </li>
      <li class="ms-6">
          <span class="absolute flex items-center justify-center w-8 h-8 bg-gray-100 rounded-full -start-4 ring-4 ring-white dark:ring-gray-900 dark:bg-gray-700">
              <svg class="w-3.5 h-3.5 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 18 20">
                  <path d="M16 1h-3.278A1.992 1.992 0 0 0 11 0H7a1.993 1.993 0 0 0-1.722 1H2a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2ZM7 2h4v3H7V2Zm5.7 8.289-3.975 3.857a1 1 0 0 1-1.393 0L5.3 12.182a1.002 1.002 0 1 1 1.4-1.436l1.328 1.289 3.28-3.181a1 1 0 1 1 1.392 1.435Z"/>
              </svg>
          </span>
          <h3 class="font-medium leading-tight">Confirmation</h3>
          <p class="text-sm">Step details here</p>
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
      <div class="pb-5 text-sm text-gray-700 p-4 bg-gray-50">
        <div class="flex flex-col space-y-2">
          <div class="font-medium">Status: <span class={agent.status === 'active' ? 'text-green-600' : 'text-gray-600'}>{agent.status}</span></div>
          <!-- Add more agent details here -->
        </div>
      </div>
    </div>
  </div>
{/each}