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
  width="min(480px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="receive-token-modal"
  isPadded={true}
>
  <div class="px-1 sm:px-2 py-2 flex flex-col gap-3 sm:gap-4">
    <div
      class="flex items-center gap-2 sm:gap-3 p-3 rounded-xl border border-white/10 bg-white/[0.03] transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '10px')});"
    >
      <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border border-white/10 bg-white/[0.04] flex-shrink-0 overflow-hidden">
        <div class="sm:hidden">
          <TokenImages tokens={[token]} size={32} showSymbolFallback={true} />
        </div>
        <div class="hidden sm:block">
          <TokenImages tokens={[token]} size={38} showSymbolFallback={true} />
        </div>
      </div>
      <div class="flex flex-col min-w-0 flex-1">
        <div class="font-medium text-white text-sm sm:text-base truncate">{token.name}</div>
        <div class="text-xs sm:text-sm text-gray-400 truncate">Your receive address</div>
      </div>
    </div>

    <div
      class="flex flex-col gap-3 sm:gap-4 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '20px')});"
    >
      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3 sm:p-4">
        <div class="flex justify-between items-center mb-2.5 gap-3">
          <h3 class="text-[13px] font-medium text-gray-300">Principal ID</h3>
          {#if principalQrCode}
            <img
              src={principalQrCode}
              alt="Principal QR Code"
              class="w-12 h-12 sm:w-16 sm:h-16 cursor-pointer hover:opacity-90 transition-opacity bg-white rounded-lg p-0.5"
              on:click={() => enlargeQrCode(principalQrCode, "Principal ID QR Code")}
            />
          {/if}
        </div>
        <div class="relative">
          <div class="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 pr-10 text-xs sm:text-sm break-all font-mono text-gray-200">
            {principal || "Loading…"}
          </div>
          <button
            type="button"
            class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors text-gray-500 hover:text-[#a78bfa]"
            on:click={() => copyToClipboard(principal, 'principal')}
            use:tooltip={{ text: principalCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
          >
            {#if principalCopied}
              <Check size={16} class="text-emerald-400" />
            {:else}
              <Copy size={16} />
            {/if}
          </button>
        </div>
        <p class="text-xs mt-2 text-gray-500">
          Use this Principal ID to receive tokens
        </p>
      </div>

      {#if token.symbol === "ICP"}
        <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3 sm:p-4">
          <div class="flex justify-between items-center mb-2.5 gap-3">
            <h3 class="text-[13px] font-medium text-gray-300">Account ID</h3>
            {#if accountIdQrCode}
              <img
                src={accountIdQrCode}
                alt="Account ID QR Code"
                class="w-12 h-12 sm:w-16 sm:h-16 cursor-pointer hover:opacity-90 transition-opacity bg-white rounded-lg p-0.5"
                on:click={() => enlargeQrCode(accountIdQrCode, "Account ID QR Code")}
              />
            {/if}
          </div>
          <div class="relative">
            <div class="rounded-xl border border-white/10 bg-white/[0.03] p-2.5 pr-10 text-xs sm:text-sm break-all font-mono text-gray-200">
              {accountId || "Loading…"}
            </div>
            <button
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 transition-colors text-gray-500 hover:text-[#a78bfa]"
              on:click={() => copyToClipboard(accountId, 'accountId')}
              use:tooltip={{ text: accountIdCopied ? "Copied!" : "Copy to clipboard", direction: "top" }}
            >
              {#if accountIdCopied}
                <Check size={16} class="text-emerald-400" />
              {:else}
                <Copy size={16} />
              {/if}
            </button>
          </div>
          <p class="text-xs mt-2 text-gray-500">
            Use this Account ID for legacy ICP transfers
          </p>
        </div>
      {/if}

      <div class="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs sm:text-sm">
        <div class="flex items-center gap-2 mb-1.5">
          <QrCode size={16} class="text-[#a78bfa] flex-shrink-0" />
          <span class="text-gray-200 font-medium">How to receive {token.symbol}</span>
        </div>
        <p class="ml-6 text-gray-500">
          {#if token.symbol === "ICP"}
            Send ICP to your address. Copy the address or tap the QR code to enlarge it for scanning.
          {:else}
            Send {token.symbol} to your address. Make sure the sender uses the correct token type. Copy the address or tap the QR code to enlarge it.
          {/if}
        </p>
      </div>
    </div>
  </div>
</Modal>

{#if enlargedQrCode}
  <Portal target="body">
    <div
      class="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-[100001]"
      on:click={closeEnlargedQrCode}
      transition:fade={{ duration: 200 }}
    >
      <div
        class="rounded-2xl bg-white p-3 shadow-2xl max-w-full max-h-full"
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
    max-width: min(480px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure proper text wrapping on mobile */
  :global(.receive-token-modal .truncate) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 640px) {
    :global(.receive-token-modal) {
      margin: 0.5rem;
    }
  }
</style> 