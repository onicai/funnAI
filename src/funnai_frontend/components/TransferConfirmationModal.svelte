<script lang="ts">
  import { onMount } from 'svelte';
  import BigNumber from "bignumber.js";
  import Modal from "./CommonModal.svelte";
  import { formatBalance } from "../helpers/utils/numberFormatUtils";
  import { ArrowRight, Check, AlertTriangle } from "lucide-svelte";
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
  <div class="p-6 flex flex-col gap-4">
    <!-- Success animation -->
    {#if showSuccess}
      <div class="text-center py-8" transition:fade={{ duration: 300 }}>
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
          <Check size={32} class="text-green-600 dark:text-green-400" />
        </div>
        <p class="text-lg font-medium text-gray-900 dark:text-gray-100">Transfer Confirmed!</p>
      </div>
    {:else}
      <!-- Transfer Details -->
      <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 space-y-3">
        <h3 class="text-base font-medium text-gray-900 dark:text-gray-100">Transfer Details</h3>
        
        <!-- Amount -->
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600 dark:text-gray-400">Amount</span>
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{receiverAmount} {token.symbol}</span>
        </div>
        
        <!-- Fee -->
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600 dark:text-gray-400">Network Fee</span>
          <span class="text-sm text-gray-900 dark:text-gray-100">{formattedFee} {token.symbol}</span>
        </div>
        
        <!-- Total -->
        <div class="flex justify-between items-center pt-2 border-t border-gray-200 dark:border-gray-700">
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100">Total</span>
          <div class="text-right">
            <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{totalAmount} {token.symbol}</div>
            {#if Number(usdValue) > 0}
              <div class="text-xs text-gray-600 dark:text-gray-400">${usdValue} USD</div>
            {/if}
          </div>
        </div>
      </div>

      <!-- Recipient -->
      <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4">
        <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">Sending to</h3>
        <div class="font-mono text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
          {truncatedAddress}
        </div>
      </div>

      <!-- Warning -->
      <div class="flex items-start gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/30 rounded-lg">
        <AlertTriangle size={16} class="text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
        <div class="text-sm">
          <p class="text-yellow-800 dark:text-yellow-200 font-medium">Double-check the recipient address</p>
          <p class="text-yellow-700 dark:text-yellow-300 mt-1">Transfers cannot be reversed once confirmed.</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3 pt-2">
        <button
          type="button"
          on:click={onClose}
          class="flex-1 py-2.5 px-4 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 font-medium transition-colors"
          disabled={isProcessing}
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={handleConfirm}
          class="flex-1 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md flex items-center justify-center gap-2 transition-colors"
          disabled={isProcessing}
        >
          {#if isProcessing}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing...
          {:else}
            <ArrowRight size={16} />
            Confirm Transfer
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style scoped>
  .confirm-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
  }

  .transfer-header {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background-color: rgba(39, 39, 42, 0.4);
    border-radius: 0.75rem;
    border: 1px solid rgba(82, 82, 91, 0.3);
  }

  .token-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .token-logo {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 9999px;
    overflow: hidden;
    background-color: #1f2937;
    padding: 0.25rem;
    border: 1px solid rgba(55, 65, 81, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .token-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .token-details {
    display: flex;
    flex-direction: column;
  }

  .token-name {
    font-weight: 500;
    font-size: 0.95rem;
    color: #e5e7eb;
  }

  .token-symbol {
    font-size: 0.8rem;
    color: #9ca3af;
  }

  .transfer-amount {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.2rem;
  }

  .amount-value {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f3f4f6;
  }

  .usd-value {
    font-size: 0.8rem;
    color: #9ca3af;
  }

  .transfer-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
    background-color: rgba(39, 39, 42, 0.2);
    border-radius: 0.75rem;
    border: 1px solid rgba(82, 82, 91, 0.2);
  }

  .detail-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .section-title {
    color: #d1d5db;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .section-title::after {
    content: '';
    flex-grow: 1;
    height: 1px;
    background-color: rgba(156, 163, 175, 0.2);
  }

  .detail-rows {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
  }

  .detail-row.total {
    border-top: 1px dashed rgba(156, 163, 175, 0.2);
    margin-top: 0.25rem;
    padding-top: 0.5rem;
  }

  .detail-label {
    font-size: 0.85rem;
    color: #9ca3af;
  }

  .detail-value {
    font-size: 0.9rem;
    font-weight: 500;
    color: #e5e7eb;
  }

  .detail-value.fee {
    color: #9ca3af;
  }

  .recipient-address {
    background-color: rgba(31, 41, 55, 0.4);
    border: 1px solid rgba(75, 85, 99, 0.3);
    border-radius: 0.5rem;
    padding: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .address-display {
    word-break: break-all;
  }

  .address-value {
    font-size: 0.9rem;
    font-family: monospace;
    color: #d1d5db;
  }

  .address-type {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 0.25rem;
  }

  .warning-section {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    background-color: rgba(146, 64, 14, 0.1);
    border: 1px solid rgba(180, 83, 9, 0.2);
    border-radius: 0.5rem;
    padding: 0.75rem;
  }

  .warning-icon {
    color: #f59e0b;
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .warning-text {
    font-size: 0.8rem;
    color: #fbbf24;
    line-height: 1.4;
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .cancel-button,
  .confirm-button {
    flex: 1;
    padding: 0.75rem 0;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
  }

  .cancel-button {
    background-color: rgba(75, 85, 99, 0.2);
    color: #e5e7eb;
    border: 1px solid rgba(75, 85, 99, 0.3);
  }

  .cancel-button:hover:not(:disabled) {
    background-color: rgba(75, 85, 99, 0.3);
  }

  .confirm-button {
    background-color: #2563eb;
    color: white;
    border: 1px solid rgba(59, 130, 246, 0.5);
  }

  .confirm-button:hover:not(:disabled) {
    background-color: #3b82f6;
  }

  .confirm-button:disabled,
  .cancel-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .confirm-button.loading {
    background-color: #3b82f6;
  }

  .confirm-button.success {
    background-color: #10b981;
    border-color: #059669;
  }

  .spinner {
    width: 1rem;
    height: 1rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .success-icon {
    animation: pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes pop {
    0% {
      transform: scale(0);
    }
    70% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
    }
  }

  @media (min-width: 640px) {
    .token-logo {
      width: 3rem;
      height: 3rem;
    }
  }
  
  /* Ensure proper z-indexing */
  :global(.transfer-confirmation-modal) {
    position: relative;
    z-index: 100050 !important;
  }
</style>
