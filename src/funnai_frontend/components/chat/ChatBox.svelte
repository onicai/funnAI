<script lang="ts">
  import { onMount } from "svelte";
  import { store, chatModelIdInitiatedGlobal, chatModelGlobal, activeChatGlobal } from "../../stores/store";
  import { push } from 'svelte-spa-router';

  import { now } from "svelte/internal";

  import Message from './Message.svelte';
  import StartUpChatPanel from './StartUpChatPanel.svelte';
  import ToastNotification from "./ToastNotification.svelte";
  import LoadingSpinner from "../LoadingSpinner.svelte";

  import {
    getLocalFlag,
    getLocallyStoredChat,
    removeLocalChangeToBeSynced,
    storeChatLocally,
    storeLocalChangeToBeSynced,
    syncLocalChanges,
  } from "../../helpers/local_storage";

  import type { Action } from 'svelte/action';

  export let modelCallbackFunction;
  export let chatDisplayed;
  export let callbackSearchVectorDbTool;
  export let autofocus = false;

  let newMessageText = '';
  let messages = [];

  let replyText = 'Thinking...';

  let messageGenerationInProgress = false;
  let showToast = false;
  let toastMessage = '';

  let newLocalChatId;

  const scrollToBottom: Action<HTMLElement, any> = (node, messages) => {
    const scroll = () =>
      node.scroll({
        top: node.scrollHeight,
        behavior: 'smooth'
      });
    scroll();
    return { 
      update: scroll 
    };
  };

  async function interruptMessageGeneration() {
    if ($chatModelGlobal) {
      try {
        await $chatModelGlobal.interruptGenerate();
        console.info("Message generation interrupted successfully");
      } catch (error) {
        console.error("Error stopping the answer generation:", error);
      }
    }
    messageGenerationInProgress = false;
  }

  // Whether user wants their messages to be stored
  let saveChats = getLocalFlag("saveChatsUserSelection"); // default is save

  function formatMessagesForBackend(messagesToFormat) {
    // Map each message to a new format
    return messagesToFormat.map(message => ({
        content: message.content,
        sender: message.name
    }));
  };

  function formatMessagesForUi(messages) {
    // Map each message to the UI format
    return messages.map(message => ({
        content: message.content,
        name: message.sender,
        role: message.sender === 'DeVinci' ? 'assistant' : 'user'
    }));
  };

  const generateProgressCallback = (_step: number, message: string) => {
    replyText = message;
    messages = [...messages.slice(0, -1), { role: 'assistant', content: replyText, name: 'DeVinci' }];
  };

  function handleInputKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    };
  };

  async function sendMessage(messageTextInput=null) {
    if(messageTextInput){
      newMessageText = messageTextInput;    
    };
    const newMessage = newMessageText;
    if(newMessage && newMessage.trim() !== '') {
      messageGenerationInProgress = true;
      const newPrompt = newMessage.trim();
      const newMessageEntry = { role: 'user', content: newPrompt, name: 'You' };
      const messageHistoryWithPrompt = [...messages, newMessageEntry];
      messages = messageHistoryWithPrompt;
      newMessageText = '';
      try {
        messages = [...messages, { role: 'assistant', content: replyText, name: 'DeVinci' }];
        const reply = await modelCallbackFunction(messageHistoryWithPrompt.slice(-5), generateProgressCallback); // passing in much of the message history easily overwhelms the available device memory
        messages = [...messages.slice(0, -1), { role: 'assistant', content: reply, name: 'DeVinci' }];
      } catch (error) {
        console.error("Error getting response from model: ", error);
        messages = [...messages, { role: 'system', content: "There was an error unfortunately. Please try again.", name: 'DeVinci' }];
      };
      replyText = 'Thinking...';
      messageGenerationInProgress = false;
      // Store chat
      if (saveChats && $store.isAuthed) {
        // Get messages into format for backend
        const messagesFormattedForBackend = formatMessagesForBackend(messages);
        if(chatDisplayed) {
          // Update chat
          try {
            const chatUpdatedResponse = await $store.backendActor.update_chat_messages(chatDisplayed.id, messagesFormattedForBackend);
            // @ts-ignore
            if (chatUpdatedResponse.Err) {
              // @ts-ignore
              console.error("Error message updating chat messages: ", chatUpdatedResponse.Err);
              throw new Error("Err updating chat messages");
            } else {
              // Remove this chat from chats to sync to avoid duplicates
              const syncObject = {
                chatId: chatDisplayed.id,
              };
              removeLocalChangeToBeSynced("localChatMessagesToSync", syncObject);
              syncLocalChanges(); // Sync any local changes (from offline usage), only works if back online
            }
          } catch (error) {
            console.error("Error storing chat: ", error);
            // Store locally and sync when back online
            const syncObject = {
              chatId: chatDisplayed.id,
              chatMessages: messagesFormattedForBackend,
            };
            storeLocalChangeToBeSynced("localChatMessagesToSync", syncObject);
          }
        } else {
          // New chat
          try {
            const chatCreatedResponse = await $store.backendActor.create_chat(messagesFormattedForBackend);
            // @ts-ignore
            if (chatCreatedResponse.Err) {
              // @ts-ignore
              console.error("Error message creating new chat: ", chatCreatedResponse.Err);
              throw new Error("Err creating new chat");
            } else {
              // @ts-ignore
              let newChatId = chatCreatedResponse.Ok;
              let newChatPreview = {
                id: newChatId,
                creationTime: now(),
                firstMessagePreview: messages[0].content,
                chatTitle: "",
              };
              chatDisplayed = newChatPreview;
              // Remove the just created chat from new chats to sync to avoid duplicates
              const syncObject = {
                newLocalChatId,
                chatMessages: messagesFormattedForBackend,
              };
              removeLocalChangeToBeSynced("newLocalChatToSync", syncObject);
              syncLocalChanges(); // Sync any local changes (from offline usage), only works if back online
            }
          } catch (error) {
            console.error("Error creating new chat: ", error);
            const syncObject = {
              newLocalChatId,
              chatMessages: messagesFormattedForBackend,
            };
            storeLocalChangeToBeSynced("newLocalChatToSync", syncObject);
          }
        }
      }
    }
  };

  // User can upload a pdf and a vector database is set up including the pdf's content
  let pathToUploadedPdf = '';
  let initiatedKnowledgeDatabase = false;
  let loadingKnowledgeDatabase = false;

  async function uploadPdfToVectorDatabase() {
    const fileInput = document.getElementById('pdf_chat') as HTMLInputElement;
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      pathToUploadedPdf = URL.createObjectURL(file);
      loadingKnowledgeDatabase = true;
      await callbackSearchVectorDbTool(pathToUploadedPdf);
      initiatedKnowledgeDatabase = true;
      loadingKnowledgeDatabase = false;
      showToast = true;
      toastMessage = "PDF processed and ready to use!";
    } else {
      showToast = true;
      toastMessage = "Please select a PDF file.";
    }
  };

  function closeToast() {
    showToast = false;
  };

  // Retrieve the chat's history if an existing chat is to be displayed
  let chatRetrievalInProgress = false;

  const loadChat = async () => {
    if($chatModelGlobal) {
      try {
        await $chatModelGlobal.interruptGenerate(); // stop any previously triggered answer generations to not interfere in this chat
      } catch (error) {
        console.error("Error stopping the answer generation on loading chat ", error);
      }
    }
    chatRetrievalInProgress = true;
    if(chatDisplayed) {
      try {
        const chatHistoryResponse = await $store.backendActor.get_chat(chatDisplayed.id);
        // @ts-ignore
        if (chatHistoryResponse.Ok) {
          // @ts-ignore
          const chatHistory = chatHistoryResponse.Ok;
          const formattedMessages = formatMessagesForUi(chatHistory.messages);
          messages = formattedMessages;
          // store chat locally for offline usage
          storeChatLocally(chatDisplayed.id, chatHistory.messages);
          syncLocalChanges(); // Sync any local changes (from offline usage), only works if back online
        } else {
          // @ts-ignore
          console.error("Error loading chat: ", chatHistoryResponse.Err);
          // @ts-ignore
          throw new Error("Error loading chat: ", chatHistoryResponse.Err);
        }
      } catch (error) {
        // Likely in offline usage
        const storedMessages = getLocallyStoredChat(chatDisplayed.id);
        if (storedMessages) {
          const formattedMessages = formatMessagesForUi(storedMessages);
          messages = formattedMessages;
        } else {
          messages = [];
        }
      }
    } else {
      messages = [];
    }
    chatRetrievalInProgress = false;
  };

  onMount(() => {
    loadChat();
  });
</script>

<div class="flex flex-col h-full">
  {#if chatRetrievalInProgress}
    <div class="flex justify-center items-center h-full">
      <LoadingSpinner />
    </div>
  {:else if messages.length === 0}
    <StartUpChatPanel sendMessageCallbackFunction={sendMessage} />
  {:else}
    <div class="flex-grow overflow-y-auto p-4" use:scrollToBottom={messages}>
      {#each messages as message}
        <Message {message} />
      {/each}
      {#if messageGenerationInProgress}
        <div class="flex justify-center items-center p-4">
          <LoadingSpinner />
        </div>
      {/if}
    </div>
  {/if}

  <div class="border-t border-gray-200 p-4">
    <div class="flex items-center space-x-4">
      <input
        type="file"
        id="pdf_chat"
        accept=".pdf"
        class="hidden"
        on:change={uploadPdfToVectorDatabase}
      />
      <label
        for="pdf_chat"
        class="cursor-pointer text-gray-500 hover:text-gray-700"
        title="Upload PDF for context"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </label>
      <textarea
        bind:value={newMessageText}
        on:keydown={handleInputKeyDown}
        placeholder="Type your message..."
        class="flex-grow p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        rows="1"
        autofocus={autofocus}
      ></textarea>
      <button
        on:click={() => sendMessage()}
        class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={messageGenerationInProgress}
      >
        Send
      </button>
    </div>
  </div>
</div>

{#if showToast}
  <ToastNotification message={toastMessage} onClose={closeToast} />
{/if} 