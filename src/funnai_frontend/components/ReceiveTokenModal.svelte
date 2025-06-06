<script lang="ts">
  import { onMount } from 'svelte';
  import { Check, Copy, QrCode, X } from 'lucide-svelte';
  import { fade } from 'svelte/transition';
  import Portal from 'svelte-portal';
  import QRCode from 'qrcode';

  import Modal from "./CommonModal.svelte";
  import TokenImages from "./TokenImages.svelte";

  import { store } from "../stores/store";
  
  import { tooltip } from "../helpers/utils/tooltip";
  import { getAccountIds } from "../helpers/utils/accountUtils";
  //import { toastStore } from "$lib/stores/toastStore";

  // Props
  export let token: any;
  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};

  // State variables
  let principal = "";
  let accountId = "";
  let principalQrCode = "";
  let accountIdQrCode = "";
  let principalCopied = false;
  let accountIdCopied = false;

  // Modal visibility handling to make animations work better
  let mounted = false;
  let closing = false;

  let enlargedQrCode: { src: string; alt: string } | null = null;

  // Watch for modal open to set mounted
  $: if (!mounted && isOpen) {
    mounted = true;
  }

  // Watch for modal close to trigger closing animation
  $: if (!isOpen && mounted) {
    closing = true;
  }

  // Close the modal with animation
  function handleClose() {
    closing = true;
    // Wait for animation to complete
    setTimeout(() => {
      onClose();
    }, 200);
  }

  // Copy text to clipboard with feedback
  async function copyToClipboard(text: string, type: 'principal' | 'accountId') {
    try {
      await navigator.clipboard.writeText(text);
      
      // Set the copied state for visual feedback
      if (type === 'principal') {
        principalCopied = true;
        setTimeout(() => principalCopied = false, 2000);
      } else if (type === 'accountId') {
        accountIdCopied = true;
        setTimeout(() => accountIdCopied = false, 2000);
      }
      
      //toastStore.success(`Copied to clipboard`);
    } catch (err) {
      console.error("Failed to copy text: ", err);
      //toastStore.error("Failed to copy to clipboard");
    }
  };

  // Generate QR codes for the addresses
  async function generateQRCodes() {
    try {
      if (principal) {
        principalQrCode = await QRCode.toDataURL(principal);
      }
      
      if (token.symbol === "ICP" && accountId) {
        accountIdQrCode = await QRCode.toDataURL(accountId);
      }
    } catch (err) {
      console.error("Error generating QR code:", err);
    }
  };

  // Initialize component
  onMount(() => {
    if ($store.principal) {
      const principalObj = $store.principal;
      principal = typeof principalObj === "string" ? principalObj : principalObj.toText();
      
      // Get account IDs if available
      if (principal) {
        const accounts = getAccountIds(principal, $store.accountId);
        accountId = accounts.main;
        
        // Generate QR codes
        generateQRCodes();
      }
    }
  });

  // Handle QR code click to enlarge
  function enlargeQrCode(src: string, alt: string) {
    enlargedQrCode = { src, alt };
  }

  // Close enlarged QR code
  function closeEnlargedQrCode() {
    enlargedQrCode = null;
  }
</script>

<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Receive {token.name}"
  width="480px"
  variant="transparent"
  height="auto"
  className="receive-token-modal"
>
  <div class="p-4 flex flex-col gap-4">
    <!-- Token Info Banner -->
    <div 
      class="flex items-center gap-3 p-3 rounded-lg bg-gray-100 border border-gray-300 text-gray-900 dark:bg-gray-700/20 dark:border-gray-600/30 dark:text-gray-100 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '10px')});"
    >
      <div class="w-10 h-10 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-800 dark:border-gray-700">
        <TokenImages
          tokens={[token]}
          size={38}
          showSymbolFallback={true}
        />
      </div>
      <div class="flex flex-col">
        <div class="font-medium text-gray-900 dark:text-gray-100">{token.name}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Your receive address information</div>
      </div>
    </div>

    <!-- Address Information -->
    <div 
      class="flex flex-col gap-4 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '20px')});"
    >
      <!-- Principal ID -->
      <div class="rounded-lg border border-gray-300 bg-gray-50 p-4 dark:border-gray-600/50 dark:bg-gray-800/30">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-sm font-medium text-gray-900 dark:text-gray-200">Principal ID</h3>
          {#if principalQrCode}
            <div class="flex">
              <img 
                src={principalQrCode} 
                alt="Principal QR Code" 
                class="w-16 h-16 cursor-pointer hover:opacity-80 transition-opacity bg-white rounded-md" 
                on:click={() => enlargeQrCode(principalQrCode, "Principal ID QR Code")}
              />
            </div>
          {/if}
        </div>
        <div class="relative">
          <div class="rounded border border-gray-300 bg-white p-2.5 pr-10 text-sm break-all font-mono text-gray-900 dark:border-gray-600 dark:bg-gray-700/30 dark:text-gray-200">
            {principal || "Loading..."}
          </div>
          <button 
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
            on:click={() => copyToClipboard(principal, 'principal')}
            use:tooltip={{ text: principalCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
          >
            {#if principalCopied}
              <Check size={16} class="text-green-500" />
            {:else}
              <Copy size={16} />
            {/if}
          </button>
        </div>
        <p class="text-xs mt-2 text-gray-600 dark:text-gray-400">
          Use this Principal ID to receive tokens
        </p>
      </div>

      <!-- ICP Account ID (only show for ICP) -->
      {#if token.symbol === "ICP"}
        <div class="rounded-lg border border-gray-300 bg-gray-50 p-4 dark:border-gray-600/50 dark:bg-gray-800/30">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-sm font-medium text-gray-900 dark:text-gray-200">Account ID</h3>
            {#if accountIdQrCode}
              <div class="flex">
                <img 
                  src={accountIdQrCode} 
                  alt="Account ID QR Code" 
                  class="w-16 h-16 cursor-pointer hover:opacity-80 transition-opacity bg-white rounded-md" 
                  on:click={() => enlargeQrCode(accountIdQrCode, "Account ID QR Code")}
                />
              </div>
            {/if}
          </div>
          <div class="relative">
            <div class="rounded border border-gray-300 bg-white p-2.5 pr-10 text-sm break-all font-mono text-gray-900 dark:border-gray-600 dark:bg-gray-700/30 dark:text-gray-200">
              {accountId || "Loading..."}
            </div>
            <button 
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
              on:click={() => copyToClipboard(accountId, 'accountId')}
              use:tooltip={{ text: accountIdCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
            >
              {#if accountIdCopied}
                <Check size={16} class="text-green-500" />
              {:else}
                <Copy size={16} />
              {/if}
            </button>
          </div>
          <p class="text-xs mt-2 text-gray-600 dark:text-gray-400">
            Use this Account ID for legacy ICP transfers
          </p>
        </div>
      {/if}

      <!-- Information box -->
      <div class="rounded-lg border border-gray-300 bg-gray-50 p-3 text-sm dark:border-gray-600/50 dark:bg-gray-800/30">
        <div class="flex items-center gap-2 mb-1.5">
          <QrCode size={16} class="text-gray-600 dark:text-gray-300" />
          <span class="text-gray-900 dark:text-gray-200">How to receive {token.symbol}</span>
        </div>
        <p class="ml-6 text-gray-600 dark:text-gray-400">
          {#if token.symbol === "ICP"}
            Send ICP to your address. Copy the address or click the QR code to scan it.
          {:else}
            Send {token.symbol} to your address. Make sure the sender is sending the correct token type. Copy the address or click the QR code to scan it.
          {/if}
        </p>
      </div>
    </div>
  </div>
</Modal>

<!-- Enlarged QR Code Overlay -->
{#if enlargedQrCode}
  <Portal target="body">
    <div 
      class="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-[100001]"
      on:click={closeEnlargedQrCode}
      transition:fade={{ duration: 200 }}
    >
      <div 
        class="rounded-lg bg-white p-2 shadow-2xl max-w-full max-h-full"
        on:click|stopPropagation
      >
        <img 
          src={enlargedQrCode.src} 
          alt={enlargedQrCode.alt} 
          class="max-w-full max-h-[80vh]"
        />
      </div>
    </div>
  </Portal>
{/if}

<style>
  /* Custom styling for component - ensures proper z-indexing */
  :global(.receive-token-modal) {
    max-width: 480px;
    position: relative;
    z-index: 100000;
  }
</style> 