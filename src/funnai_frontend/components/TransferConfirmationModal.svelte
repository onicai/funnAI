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
  {isOpen}
  variant="transparent"
  {onClose}
  title="Confirm Transfer"
  width="min(450px, 92vw)"
  height="auto"
  target="body"
  isPadded={false}
  className="transfer-confirmation-modal"
>
  <div class="confirm-container" in:fade={{ duration: 200 }}>
    <!-- Transfer Header -->
    <div class="transfer-header">
      <div class="token-info">
        <div class="token-logo">
          <img 
            src={token.logo_url} 
            alt={token.symbol}
            class="token-image" 
            loading="lazy"
          />
        </div>
        <div class="token-details">
          <span class="token-name">{token.name}</span>
          <span class="token-symbol">{token.symbol}</span>
        </div>
      </div>
      
      <div class="transfer-amount">
        <span class="amount-value">{amount} {token.symbol}</span>
        {#if usdValue !== "0.00"}
          <span class="usd-value">≈ ${usdValue} USD</span>
        {/if}
      </div>
    </div>
    
    <!-- Transfer Details -->
    <div class="transfer-details">
      <div class="detail-section">
        <div class="section-title">
          <span>Transaction Details</span>
        </div>
        
        <div class="detail-rows">
          <div class="detail-row">
            <span class="detail-label">You're sending</span>
            <span class="detail-value">{amount} {token.symbol}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Network fee</span>
            <span class="detail-value fee">{formattedFee} {token.symbol}</span>
          </div>
          
          <div class="detail-row total">
            <span class="detail-label">Total amount</span>
            <span class="detail-value">{totalAmount} {token.symbol}</span>
          </div>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-title">
          <span>Recipient</span>
        </div>
        
        <div class="recipient-address">
          <div class="address-display">
            <span class="address-value" title={toPrincipal}>{truncatedAddress}</span>
          </div>
          <div class="address-type">
            {toPrincipal.length === 64 ? 'Account ID' : 'Principal ID'}
          </div>
        </div>
      </div>
      
      <!-- Warning Section -->
      <div class="warning-section">
        <AlertTriangle size={16} class="warning-icon" />
        <span class="warning-text">Transfers are irreversible. Please verify all details before confirming.</span>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="action-buttons">
      <button 
        type="button" 
        class="cancel-button" 
        on:click={onClose}
        disabled={isProcessing || showSuccess}
      >
        Cancel
      </button>
      
      <button
        type="button"
        class="confirm-button"
        class:loading={isProcessing}
        class:success={showSuccess}
        on:click={handleConfirm}
        disabled={isProcessing || showSuccess}
      >
        {#if showSuccess}
          <div class="success-icon">
            <Check size={18} />
          </div>
          Confirmed!
        {:else if isProcessing}
          <div class="spinner"></div>
          Processing...
        {:else}
          <ArrowRight size={18} />
          Confirm Transfer
        {/if}
      </button>
    </div>
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
    z-index: 100000;
  }
</style>
