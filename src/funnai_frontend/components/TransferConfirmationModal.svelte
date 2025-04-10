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
  export let amount: string;
  export let token: FE.Token;
  export let tokenFee: bigint;
  export let isValidating: boolean = false;
  export let toPrincipal: string;

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
        disabled={isValidating || showSuccess}
      >
        Cancel
      </button>
      
      <button
        type="button"
        class="confirm-button"
        class:loading={isValidating}
        class:success={showSuccess}
        on:click={handleConfirm}
        disabled={isValidating || showSuccess}
      >
        {#if showSuccess}
          <div class="success-icon">
            <Check size={18} />
          </div>
          Confirmed!
        {:else if isValidating}
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
    padding: 0.5rem 0.75rem;
  }

  .transfer-header {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    align-items: center;
    justify-content: center;
    padding: 0.75rem;
    background-color: rgba(var(--color-kong-surface-dark-rgb), 0.8);
    border-radius: 0.5rem;
    border: 1px solid rgba(var(--color-kong-border-rgb), 0.3);
  }

  .token-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .token-logo {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 9999px;
    overflow: hidden;
    background-color: var(--color-kong-bg-light);
    padding: 0.25rem;
    border: 1px solid rgba(var(--color-kong-border-rgb), 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  @media (min-width: 640px) {
    .token-logo {
      width: 3rem;
      height: 3rem;
    }
  }

  .token-image {
    width: 2rem;
    height: 2rem;
    border-radius: 9999px;
    object-fit: contain;
  }

  @media (min-width: 640px) {
    .token-image {
      width: 2.5rem;
      height: 2.5rem;
    }
  }

  .token-details {
    display: flex;
    flex-direction: column;
  }

  .token-name {
    color: var(--color-kong-text-primary);
    font-weight: 500;
  }

  .token-symbol {
    font-size: 0.875rem;
    color: var(--color-kong-text-secondary);
  }

  .transfer-amount {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .amount-value {
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--color-kong-text-primary);
  }

  .usd-value {
    font-size: 0.875rem;
    color: var(--color-kong-text-secondary);
  }

  .transfer-details {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .detail-section {
    background-color: rgba(var(--color-kong-surface-dark-rgb), 0.5);
    border-radius: 0.5rem;
    padding: 0.75rem;
    border: 1px solid rgba(var(--color-kong-border-rgb), 0.2);
  }

  @media (min-width: 640px) {
    .detail-section {
      padding: 1rem;
    }
  }

  .section-title {
    font-size: 0.875rem;
    font-weight: 500;
    color: rgba(var(--color-kong-text-primary-rgb), 0.9);
    margin-bottom: 0.5rem;
  }

  @media (min-width: 640px) {
    .section-title {
      margin-bottom: 0.75rem;
    }
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
  }

  .detail-row.total {
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(var(--color-kong-border-rgb), 0.1);
    font-weight: 500;
    color: var(--color-kong-text-primary);
  }

  .detail-label {
    font-size: 0.875rem;
    color: var(--color-kong-text-secondary);
  }

  .detail-value {
    font-size: 0.875rem;
    color: var(--color-kong-text-primary);
  }

  .detail-value.fee {
    color: var(--color-kong-text-secondary);
  }

  .recipient-address {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .address-display {
    background-color: rgba(var(--color-kong-bg-light-rgb), 0.5);
    border-radius: 0.5rem;
    padding: 0.75rem;
    border: 1px solid rgba(var(--color-kong-border-rgb), 0.3);
  }

  .address-value {
    font-size: 0.75rem;
    font-family: monospace;
    color: var(--color-kong-text-primary);
    word-break: break-word;
  }

  .address-type {
    font-size: 0.75rem;
    color: var(--color-kong-text-secondary);
    margin-top: 0.25rem;
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }

  .warning-section {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.625rem;
    border-radius: 0.5rem;
    background-color: rgba(var(--color-kong-accent-yellow-rgb), 0.1);
    border: 1px solid rgba(var(--color-kong-accent-yellow-rgb), 0.2);
    font-size: 0.75rem;
    color: rgba(var(--color-kong-text-primary-rgb), 0.8);
  }

  @media (min-width: 640px) {
    .warning-section {
      padding: 0.75rem;
    }
  }

  .warning-icon {
    color: var(--color-kong-accent-yellow);
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .action-buttons {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  @media (min-width: 640px) {
    .action-buttons {
      gap: 0.75rem;
    }
  }

  .cancel-button {
    height: 2.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    background-color: rgba(var(--color-kong-bg-light-rgb), 0.8);
    color: rgba(var(--color-kong-text-primary-rgb), 0.8);
    transition: all 0.2s ease;
  }

  .cancel-button:hover {
    background-color: var(--color-kong-bg-light);
    color: var(--color-kong-text-primary);
  }

  .cancel-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (min-width: 640px) {
    .cancel-button {
      height: 3rem;
    }
  }

  .confirm-button {
    height: 2.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background-color: var(--color-kong-primary);
    color: white;
    transition: all 0.2s ease;
  }

  .confirm-button:hover {
    background-color: var(--color-kong-primary-hover);
  }

  .confirm-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  @media (min-width: 640px) {
    .confirm-button {
      height: 3rem;
    }
  }

  .confirm-button.loading {
    background-color: rgba(var(--color-kong-primary-rgb), 0.9);
  }

  .confirm-button.success {
    background-color: var(--color-kong-accent-green);
  }

  .spinner {
    width: 1.25rem;
    height: 1.25rem;
    border: 2px solid white;
    border-top-color: transparent;
    border-radius: 9999px;
    animation: spin 0.8s linear infinite;
  }

  .success-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pop 0.3s ease-out;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes pop {
    0% {
      transform: scale(0.5);
      opacity: 0;
    }
    70% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
      opacity: 1;
    }
  }
</style>
