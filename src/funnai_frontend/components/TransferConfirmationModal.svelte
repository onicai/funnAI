<script lang="ts">
  import { onMount } from 'svelte';
  import BigNumber from "bignumber.js";
  import Modal from "./CommonModal.svelte";
  import { formatBalance } from "../helpers/utils/numberFormatUtils";
  import { ArrowRight, Check, AlertTriangle } from "@lucide/svelte";
  import { fly, fade } from 'svelte/transition';

  // Props
  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onConfirm: () => void = () => {};
  export let transferDetails: {
    amount: string;
    token: FE.Token;
    tokenFee: bigint;
    toPrincipal: string;
  } | null = null;
  export let isProcessing: boolean = false;
  export let isValidating: boolean = false; // For backward compatibility
  
  // Use isValidating for backward compatibility if isProcessing is not set
  $: isProcessing = isProcessing || isValidating;

  // Extract values from transferDetails
  $: amount = transferDetails?.amount || "0";
  $: token = transferDetails?.token || { name: "", symbol: "", decimals: 8, logo_url: "", metrics: { price: "0" } };
  $: tokenFee = transferDetails?.tokenFee || BigInt(0);
  $: toPrincipal = transferDetails?.toPrincipal || "";

  // State variables
  let receiverAmount: string = "";
  let totalAmount: string = "";
  let formattedFee: string = "";
  let usdValue: string = "0.00";
  let truncatedAddress: string = "";
  let showSuccess: boolean = false;

  // Reactive calculation
  $: {
    try {
      receiverAmount = new BigNumber(amount).toString();

      totalAmount = new BigNumber(amount)
        .plus(new BigNumber(tokenFee?.toString() || "10000").dividedBy(10 ** token.decimals))
        .toString();

      formattedFee = formatBalance(tokenFee?.toString() || "10000", token.decimals);

      if (token.metrics?.price) {
        usdValue = new BigNumber(amount)
          .multipliedBy(token.metrics.price)
          .toFixed(2);
      }

      if (toPrincipal && toPrincipal.length > 16) {
        truncatedAddress = `${toPrincipal.substring(0, 8)}...${toPrincipal.substring(toPrincipal.length - 8)}`;
      } else {
        truncatedAddress = toPrincipal;
      }

    } catch (error) {
      console.error('Error calculating amounts:', error);
      receiverAmount = amount;
      totalAmount = amount;
      formattedFee = '0';
    }
  }
  
  function handleConfirm() {
    showSuccess = true;
    setTimeout(() => {
      onConfirm();
      showSuccess = false;
    }, 800);
  }

  // Ensure this modal appears on top of all others
  onMount(() => {
    if (isOpen) {
      // Force the modal to have the highest z-index
      setTimeout(() => {
        const modalElements = document.querySelectorAll('[role="dialog"]');
        modalElements.forEach((element) => {
          if (element.querySelector('.transfer-confirmation-modal')) {
            (element as HTMLElement).style.zIndex = '100100';
          }
        });
      }, 100);
    }
  });

  // Watch for isOpen changes to re-apply z-index
  $: if (isOpen) {
    setTimeout(() => {
      const modalElements = document.querySelectorAll('[role="dialog"]');
      modalElements.forEach((element) => {
        if (element.querySelector('.transfer-confirmation-modal')) {
          (element as HTMLElement).style.zIndex = '100100';
        }
      });
    }, 100);
  }

  // Improve performance by using CSS custom properties
  onMount(() => {
    const container = document.querySelector('.token-logo-container') as HTMLElement;
    if (container) {
      const handleMouseOver = () => {
        container.style.setProperty('--scale', '1.1');
      };
      const handleMouseOut = () => {
        container.style.setProperty('--scale', '1');
      };
      
      container.addEventListener('mouseover', handleMouseOver);
      container.addEventListener('mouseout', handleMouseOut);
      
      return () => {
        container.removeEventListener('mouseover', handleMouseOver);
        container.removeEventListener('mouseout', handleMouseOut);
      };
    }
  });
</script>

<Modal
  isOpen={isOpen}
  onClose={onClose}
  title="Confirm Transfer"
  width="420px"
  variant="transparent"
  height="auto"
  className="transfer-confirmation-modal"
>
  <div class="px-1 sm:px-2 py-2 flex flex-col gap-4">
    {#if showSuccess}
      <div class="text-center py-8" transition:fade={{ duration: 300 }}>
        <div class="w-16 h-16 mx-auto mb-4 rounded-full border border-emerald-500/25 bg-emerald-500/10 flex items-center justify-center">
          <Check size={32} class="text-emerald-400" />
        </div>
        <p class="text-lg font-semibold tracking-tight text-white">Transfer confirmed</p>
      </div>
    {:else}
      <div class="rounded-xl border border-white/10 bg-white/3 p-4 space-y-3">
        <h3 class="text-[13px] font-medium text-gray-300">Transfer details</h3>

        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">Amount</span>
          <span class="text-sm font-medium text-white tabular-nums">{receiverAmount} {token.symbol}</span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">Network fee</span>
          <span class="text-sm text-gray-200 tabular-nums">{formattedFee} {token.symbol}</span>
        </div>

        <div class="flex justify-between items-center pt-2 border-t border-white/6">
          <span class="text-sm font-medium text-white">Total</span>
          <div class="text-right">
            <div class="text-sm font-medium text-white tabular-nums">{totalAmount} {token.symbol}</div>
            {#if Number(usdValue) > 0}
              <div class="text-xs text-gray-500">${usdValue} USD</div>
            {/if}
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-white/10 bg-white/3 p-4">
        <h3 class="text-[13px] font-medium text-gray-300 mb-2">Sending to</h3>
        <div class="font-mono text-sm text-gray-200 bg-white/3 p-2.5 rounded-xl border border-white/10 break-all">
          {truncatedAddress}
        </div>
      </div>

      <div class="flex items-start gap-3 p-3 rounded-xl border border-amber-500/25 bg-amber-500/10">
        <AlertTriangle size={16} class="text-amber-400 mt-0.5 shrink-0" />
        <div class="text-sm">
          <p class="text-amber-200 font-medium">Double-check the recipient address</p>
          <p class="text-amber-200/70 mt-1">Transfers cannot be reversed once confirmed.</p>
        </div>
      </div>

      <div class="flex gap-2.5 pt-1">
        <button
          type="button"
          on:click={onClose}
          class="agent-btn-ghost flex-1 h-10! disabled:opacity-50"
          disabled={isProcessing}
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={handleConfirm}
          class="agent-btn-primary flex-1 h-10! disabled:opacity-50"
          disabled={isProcessing}
        >
          {#if isProcessing}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing…
          {:else}
            <ArrowRight size={16} />
            Confirm transfer
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style scoped>
  /* Ensure proper z-indexing */
  :global(.transfer-confirmation-modal) {
    position: relative;
    z-index: 100050 !important;
  }
</style>
