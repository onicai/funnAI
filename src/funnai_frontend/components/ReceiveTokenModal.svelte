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
      class="flex items-center gap-3 p-3 rounded-lg transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '10px')});"
    >
      <div class="w-10 h-10 rounded-full flex-shrink-0">
        <TokenImages
          tokens={[token]}
          size={32}
          showSymbolFallback={true}
        />
      </div>
      <div class="flex flex-col">
        <div class="font-medium">{token.name}</div>
        <div class="text-sm">Your receive address information</div>
      </div>
    </div>

    <!-- Address Information -->
    <div 
      class="flex flex-col gap-4 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '20px')});"
    >
      <!-- Principal ID -->
      <div class="rounded-lg border p-4">
        <div class="flex justify-between items-center mb-2">
          <h3 class="text-sm font-medium">Principal ID</h3>
          {#if principalQrCode}
            <div class="flex">
              <img 
                src={principalQrCode} 
                alt="Principal QR Code" 
                class="w-16 h-16 cursor-pointer hover:opacity-80 transition-opacity" 
                on:click={() => enlargeQrCode(principalQrCode, "Principal ID QR Code")}
              />
            </div>
          {/if}
        </div>
        <div class="relative">
          <div class="rounded border p-2.5 pr-10 text-sm break-all font-mono">
            {principal || "Loading..."}
          </div>
          <button 
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors"
            on:click={() => copyToClipboard(principal, 'principal')}
            use:tooltip={{ text: principalCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
          >
            {#if principalCopied}
              <Check size={16} class="" />
            {:else}
              <Copy size={16} />
            {/if}
          </button>
        </div>
        <p class="text-xs mt-2">
          Use this Principal ID to receive {token.symbol === "ICP" ? "non-ICP tokens" : "tokens"}
        </p>
      </div>

      {#if token.symbol === "ICP" && accountId}
        <!-- Account ID for ICP -->
        <div class="rounded-lg border p-4">
          <div class="flex justify-between items-center mb-2">
            <h3 class="text-sm font-medium">Account ID</h3>
            {#if accountIdQrCode}
              <div class="flex">
                <img 
                  src={accountIdQrCode} 
                  alt="Account ID QR Code" 
                  class="w-16 h-16 cursor-pointer hover:opacity-80 transition-opacity" 
                  on:click={() => enlargeQrCode(accountIdQrCode, "Account ID QR Code")}
                />
              </div>
            {/if}
          </div>
          <div class="relative">
            <div class="rounded border p-2.5 pr-10 text-sm break-all font-mono">
              {accountId || "Loading..."}
            </div>
            <button 
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors"
              on:click={() => copyToClipboard(accountId, 'accountId')}
              use:tooltip={{ text: accountIdCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
            >
              {#if accountIdCopied}
                <Check size={16} class="" />
              {:else}
                <Copy size={16} />
              {/if}
            </button>
          </div>
          <p class="text-xs mt-2">
            Use this Account ID to receive ICP tokens (recommended for exchanges)
          </p>
        </div>
      {/if}
      
      <!-- Instructions -->
      <div class="rounded-lg border p-3 text-sm">
        <div class="flex items-center gap-2 mb-1.5">
          <QrCode size={16} class="" />
          <span class="">How to receive {token.symbol}</span>
        </div>
        <p class="ml-6">
          {#if token.symbol === "ICP"}
            Send ICP to your Account ID. This is the recommended address for transfers from exchanges.
          {:else}
            Send {token.symbol} to your Principal ID. Make sure the sender is sending the correct token type.
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
      class="fixed inset-0 bg-black/70 flex items-center justify-center p-4"
      on:click={closeEnlargedQrCode}
      transition:fade={{ duration: 200 }}
      style="z-index: 999999;"
    >
      <div 
        class="relative p-4 rounded-xl max-w-md w-full flex flex-col items-center"
        on:click|stopPropagation={() => {}}
      >
        <button 
          class="absolute top-3 right-3 p-1.5 rounded-full"
          on:click={closeEnlargedQrCode}
        >
          <X size={20} />
        </button>
        
        <div class="text-center mb-4">
          <h3 class="text-lg font-medium">{enlargedQrCode.alt}</h3>
        </div>
        
        <div class="bg-white p-6 rounded-lg">
          <img 
            src={enlargedQrCode.src} 
            alt={enlargedQrCode.alt}
            class="w-80 h-80"
          />
        </div>
        
        <button
          class="mt-4 px-4 py-2 text-white rounded-md transition-colors"
          on:click={closeEnlargedQrCode}
        >
          Close
        </button>
      </div>
    </div>
  </Portal>
{/if}

<style>
  /* Add global CSS for the modal transitions */
  :global(.receive-token-modal) {
    animation: fadeIn 0.25s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  /* This will be applied when the modal is closing */
  :global(.modal-closing) {
    animation: fadeOut 0.2s ease-out forwards !important;
  }

  @keyframes fadeOut {
    from {
      opacity: 1;
      transform: translateY(0);
    }
    to {
      opacity: 0;
      transform: translateY(20px);
    }
  }
</style> 