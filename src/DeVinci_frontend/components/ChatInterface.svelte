<div class="container mx-auto px-8 py-8 flex-grow dark:bg-gray-900">
  <div class="flex items-center p-4 mt-0 mb-6 text-md text-yellow-800 border border-yellow-300 rounded-lg bg-yellow-50 dark:bg-gray-800 dark:border-yellow-600 dark:text-yellow-300" role="alert">
    <svg class="shrink-0 inline w-4 h-4 me-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
      <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
    </svg>
    <span class="sr-only">Info</span>
    <div>
      <span class="font-medium">Heads up!</span> 
      Chat functionality is coming soon! In the meantime, you can experience the future of private AI with <strong>DeVinci</strong> — the end-to-end decentralized AI chat app — and explore <strong>ICGPT</strong>, the world's first on-chain Large Language Models.
    </div>
  </div>
  
  <div class="space-y-6">
    <a href="https://devinci.onicai.com/" target='_blank' rel="noreferrer" class="block w-full">
      <div class="card flex flex-col pt-16 pb-12 md:p-8 items-center rounded-[32px] shadow md:flex-row border-gray-700 bg-opacity-90 dark:bg-opacity-100 dark:border-purple-900" style="background: linear-gradient(48deg, rgba(203, 139, 208, 0.71) -32.7%, rgba(152, 98, 207, 0.85) 33.06%, rgba(42, 19, 95, 1) 129.51%);">
        <img class="object-cover rounded-t-lg mx-8 h-48 mb-12 md:mb-0 md:h-auto md:w-48 md:rounded-none md:rounded-s-lg rotate-on-hover" src="./shape_7.svg" alt="">
        <div class="flex flex-col justify-between p-4 leading-normal">
          <h5 class="mb-2 text-3xl font-bold tracking-tight text-[#f7e5d1]">DeVinci</h5>
          <p class="mb-3 text-4xl font-normal text-[#e7d7ea]">The end-to-end decentralized AI chat app.</p>
          <p class="mb-3 text-xl font-normal text-gray-800 dark:text-gray-200">Enjoy full privacy and control with state-of-the-art open-source AI models running directly on your device through the browser. Being in control of your AI experiences has never been easier. Powered by ICP.</p>
          <img src="./north_east_icon.svg" class="w-8 h-8 ml-auto rotate-on-hover" alt="Link Icon" />
        </div>
      </div>
    </a>

    <a href="https://icgpt.onicai.com/" target='_blank' rel="noreferrer" class="block w-full">
      <div class="card flex flex-col pt-16 pb-12 md:p-8 items-center rounded-[32px] shadow md:flex-row border-gray-700 bg-opacity-90 dark:bg-opacity-100 dark:border-teal-900" style="background: linear-gradient(48deg, #4DEDD3 -32.7%, #31A782 33.06%, #3B00B9 129.51%)">
        <img class="object-cover rounded-t-lg mx-8 h-48 mb-12 md:mb-0 md:h-auto md:w-48 md:rounded-none md:rounded-s-lg rotate-on-hover" src="./shape_9.svg" alt="">
        <div class="flex flex-col justify-between p-4 leading-normal">
          <h5 class="mb-2 text-3xl font-bold tracking-tight text-[#f7e5d1]">ICGPT</h5>
          <p class="mb-3 text-4xl font-normal text-[#e7d7ea]">The first ever on-chain Large Language Models</p>
          <p class="mb-3 text-xl font-normal text-gray-800 dark:text-gray-200">August 8, 2023 marks the global birthday of on-chain generative AI as we released our first Large Language Model on ICP.</p>
          <img src="./north_east_icon.svg" class="w-8 h-8 ml-auto rotate-on-hover" alt="Link Icon" />
        </div>
      </div>
    </a>
  </div>
</div>

<style>
  .card:hover .rotate-on-hover {
      transform: rotate(45deg);
      transition: transform 0.3s ease;
  }
</style>



<!-- <script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import {
    chatModelGlobal,
    activeChatGlobal,
    chatModelIdInitiatedGlobal,
    downloadedModels,
    useKnowledgeBase
  } from "../store";
  import InstallToastNotification from './InstallToastNotification.svelte';
  import {
    getSearchVectorDbTool,
    searchUserKnowledgebase,
    //storeEmbeddings,
    //loadExistingVectorStore,
    //checkUserHasKnowledgeBase
  } from "../helpers/vector_database";
  import SelectModel from "./SelectModel.svelte";
  import ChatBox from "./ChatBox.svelte";

  import { determineInferenceParameters } from '../helpers/user_settings';

  // Reactive statement to check if the user has already downloaded at least one AI model
  $: userHasDownloadedAtLeastOneModel = $downloadedModels.length > 0;

  const workerPath = './worker.ts';

  let showToast = false;

  function isPWAInstalled() {
    // @ts-ignore
    return (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone);
  };

  let isChatBoxReady = false;

  onMount(() => {
    if (!userHasDownloadedAtLeastOneModel && !isPWAInstalled()) {
      // Check if the toast has already been shown in this session
      const hasShownToast = sessionStorage.getItem('hasShownToast');

      if (!hasShownToast) {
        showToast = true; // Show toast on load

        // Set in sessionStorage that the toast has been shown
        sessionStorage.setItem('hasShownToast', 'true');

        // Automatically hide the toast after 8 seconds
        setTimeout(() => {
          showToast = false;
        }, 8000);
      };
    };
  });

  afterUpdate(() => {
    if ($chatModelIdInitiatedGlobal && !isChatBoxReady) {
      isChatBoxReady = true;
    }
  });

  let vectorDbSearchTool;
  let useSessionVectorDb = false;

  async function setVectorDbSearchTool(pathToInput) {
    vectorDbSearchTool = await getSearchVectorDbTool(pathToInput);
    useSessionVectorDb = true;
  };

  // Debug Android
  //let debugOutput = "";

  function setLabel(id: string, text: string) {
    const label = document.getElementById(id);
    if (label == null) {
      throw Error("Cannot find label " + id);
    }
    label.innerText = text;
  };

  const generateProgressCallback = (_step: number, message: string) => {
    setLabel("generate-label", message);
  };

  async function getChatModelResponse(prompt, progressCallback = generateProgressCallback) {
    try {
      /* debugOutput = "###in getChatModelResponse###";
      debugOutput += JSON.stringify(prompt);
      setLabel("debug-label", debugOutput); */
      if ((vectorDbSearchTool && useSessionVectorDb) || $useKnowledgeBase) {
        /* debugOutput += " useSessionVectorDb ";
        setLabel("debug-label", debugOutput); */
        // Add content from local knowledge base if activated
        let additionalContentToProvide = "";
        additionalContentToProvide = " Additional content (use this if relevant to the User Prompt): ";
        try {
          const promptContent = prompt[prompt.length - 1].content;
          if (vectorDbSearchTool && useSessionVectorDb) {
            try {
              let vectorDbSearchToolResponse = await vectorDbSearchTool.func(promptContent);
              vectorDbSearchToolResponse = JSON.parse(vectorDbSearchToolResponse);
              for (let index = 0; index < vectorDbSearchToolResponse.existingChatsFoundInLocalDatabase.length; index++) {
                const additionalEntry = vectorDbSearchToolResponse.existingChatsFoundInLocalDatabase[index];
                additionalContentToProvide += "  ";
                additionalContentToProvide += additionalEntry.content;
              };
            } catch (error) {
              console.error("Error in getChatModelResponse vectorDbSearchTool");
              console.error(error.toString());
              /* debugOutput += " final prompt and additionalContentEntry error ";
              debugOutput += error.toString();
                debugOutput += error.name;
                debugOutput += error.message;
              setLabel("debug-label", debugOutput);  */
            };
          };
          if ($useKnowledgeBase) {
            try {
              let userKnowledgeBaseResponse = await searchUserKnowledgebase(promptContent);
              if (userKnowledgeBaseResponse) {
                additionalContentToProvide += "  ";
                additionalContentToProvide += userKnowledgeBaseResponse;
              };
            } catch (error) {
              console.error("Error in getChatModelResponse vectorDbSearchTool");
              console.error(error.toString());
              /* debugOutput += " final prompt and additionalContentEntry error ";
              debugOutput += error.toString();
                debugOutput += error.name;
                debugOutput += error.message;
              setLabel("debug-label", debugOutput);  */
            };
          };
          // Compose the final prompt
          const additionalContentEntry = { role: 'user', content: additionalContentToProvide, name: 'UserKnowledgeBase' };
          prompt = [...prompt, additionalContentEntry];
        } catch (error) {
          console.error("Error in getChatModelResponse getting additionalContentToProvide");
          console.error(error.toString());
          /* debugOutput += " vectorDbSearchToolResponse error ";
          debugOutput += error.toString();
              debugOutput += error.name;
              debugOutput += error.message;
          setLabel("debug-label", debugOutput);   */
        };
      };
      try {
        /* debugOutput += " final prompt ";
        debugOutput += JSON.stringify(prompt);
        setLabel("debug-label", debugOutput); */
        let curMessage = "";
        let stepCount = 0;
        // determine inference parameters to use
        const inferenceParameters = await determineInferenceParameters();
        prompt.unshift({
          role: "system",
          content: inferenceParameters.system_prompt,
        });
        const completion = await $chatModelGlobal.chat.completions.create({
          stream: true,
          messages: prompt,
          temperature: inferenceParameters.temperature,
          max_tokens: inferenceParameters.max_tokens,
        });
        /* debugOutput += " completion ";
        debugOutput += JSON.stringify(completion);
        setLabel("debug-label", debugOutput); */
        try {
          for await (const chunk of completion) {
            /* debugOutput += " chunk ";
            debugOutput += JSON.stringify(chunk);
            setLabel("debug-label", debugOutput); */
            try {
              const curDelta = chunk.choices[0].delta.content;
              if (curDelta) {
                curMessage += curDelta;
              };
              progressCallback(stepCount, curMessage);
              stepCount ++;
            } catch (error) {
              console.error("Error in getChatModelResponse progressCallback");
              console.error(error.toString());
              /* debugOutput += " progressCallback error ";
              debugOutput += error.toString();
              debugOutput += error.name;
              debugOutput += error.message;
              setLabel("debug-label", debugOutput);  */
            };
          };
        } catch (error) {
          console.error("Error in getChatModelResponse completion loop");
          console.error(error.toString());
          /* debugOutput += " completion loop error ";
          debugOutput += error.toString();
          debugOutput += error.name;
          debugOutput += error.message;
          setLabel("debug-label", debugOutput);  */
        };
      } catch (error) {
        console.error("Error in getChatModelResponse completion");
        console.error(error.toString());
        /* debugOutput += " completion error ";
        debugOutput += error.toString();
              debugOutput += error.name;
              debugOutput += error.message;
        setLabel("debug-label", debugOutput);  */
      };

      try {
        /* debugOutput += " before getMessage ";
        setLabel("debug-label", debugOutput); */
        const reply = await $chatModelGlobal.getMessage();
        /* debugOutput += " reply ";
        debugOutput += reply;
        setLabel("debug-label", debugOutput); */
        return reply;
      } catch (error) {
        console.error("Error in getChatModelResponse reply");
        console.error(error.toString());
        /* debugOutput += " reply error ";
        debugOutput += error.toString();
              debugOutput += error.name;
              debugOutput += error.message;
        setLabel("debug-label", debugOutput);    */
      };
    } catch (error) {
      console.error("Error in getChatModelResponse");
      console.error(error.toString());
      /* debugOutput += " outer error ";
      debugOutput += error.toString();
              debugOutput += error.name;
              debugOutput += error.message;
      setLabel("debug-label", debugOutput);   */
    };
    // if no reply was returned, an error occurred
    throw new Error('An error occurred');
  };
</script>

<div id="chatinterface" class="flex flex-col p-4 pb-24 max-w-6xl mx-auto w-full">
  {#if !$chatModelIdInitiatedGlobal}
    <SelectModel onlyShowDownloadedModels={true} autoInitiateSelectedModel={true}/>
  {:else if isChatBoxReady}
    {#key $activeChatGlobal}
      <ChatBox modelCallbackFunction={getChatModelResponse} chatDisplayed={$activeChatGlobal} callbackSearchVectorDbTool={setVectorDbSearchTool}/>
    {/key}
  {:else}
    <p>Loading chat interface...</p>
  {/if}
</div>

{#key showToast}
  <InstallToastNotification showToast={showToast} />
{/key} -->
