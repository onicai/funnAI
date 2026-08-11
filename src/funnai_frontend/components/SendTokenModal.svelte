<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "./CommonModal.svelte";
  import TokenImages from "./TokenImages.svelte";
  import TransferConfirmationModal from "./TransferConfirmationModal.svelte";
  import { 
    ArrowRight, 
    Clipboard, 
    Camera, 
    Info, 
    ArrowUp,
    X, 
    Check 
  } from 'lucide-svelte';
  import { tooltip } from "../helpers/utils/tooltip";
  import { store } from "../stores/store";
  import { IcrcService } from "../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { 
    calculateMaxAmount, 
    validateTokenAmount, 
    validateAddress, 
    formatTokenInput,
    getInitialBalances,
  } from "../helpers/utils/tokenValidators";
  // Lazy load QrScanner only when needed
  let QrScanner: any = null;
  import { getAccountIds } from "../helpers/utils/accountUtils";
  import { formatBalance } from "../helpers/utils/numberFormatUtils";
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  // Props type definition
  type SendTokenModalProps = {
    token: any;
    isOpen?: boolean;
    onClose?: () => void;
    onSuccess?: (txId: string) => void;
  };

  export let token: any;
  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: () => void = () => {};

  let recipientAddress: string = "";
  let amount: string = "";
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let tokenFee: bigint = BigInt(0);
  let showScanner: boolean = false;
  let hasCamera: boolean = false;
  let accounts: { subaccount: string; main: string } = { subaccount: "", main: "" };

  let showConfirmation: boolean = false;
  let transferDetails: {
    amount: string;
    token: any;
    tokenFee: bigint;
    toPrincipal: string;
  } | null = null;

  let balances: { default: bigint; subaccount?: bigint } = getInitialBalances(token?.symbol);
  let addressValidation = { isValid: false, errorMessage: "", addressType: null };
  let amountValidation = { isValid: false, errorMessage: "" };

  let mounted: boolean = false;
  let closing: boolean = false;

  $: if (!mounted && isOpen) {
    mounted = true;
  }

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

  // Load token fee
  async function loadTokenFee() {
    try {
      tokenFee = await IcrcService.getTokenFee(token);
    } catch (error) {
      console.error("Error loading token fee:", error);
      tokenFee = BigInt(10000); // Fallback to default fee
    }
  }

  // Load user balances
  async function loadBalances() {
    try {
      // Safety check to ensure token is still valid
      if (!token || !token.symbol) {
        console.debug("Token not available for balance loading");
        return;
      }
      
      console.debug("Loading balances for", token.symbol);
      
      // Only load main account balance
      const defaultResult = await IcrcService.getIcrc1Balance(token, $store.principal);
      if (typeof defaultResult === 'bigint') {
        balances.default = defaultResult;
      }
      
      console.debug("Final balance:", balances.default.toString());
    } catch (error) {
      console.error("Error loading balances:", error);
    }
  }

  // Calculate max amount user can send
  $: maxAmount = calculateMaxAmount(balances.default, token.decimals, tokenFee);

  // Handle amount input
  function handleAmountInput(event: Event) {
    const input = event.target as HTMLInputElement;
    amount = formatTokenInput(input.value, token.decimals);
  }

  // Handle "Send Max" button click
  function handleSendMax() {
    amount = String(maxAmount);
  }

  // Handle recipient address input
  function handleAddressInput(event: Event) {
    const input = event.target as HTMLInputElement;
    recipientAddress = input.value.trim();
  }

  // Handle QR scanner button click
  async function handleScanClick() {
    if (hasCamera) {
      // Lazy load QrScanner component
      if (!QrScanner) {
        const module = await import('./QrScanner.svelte');
        QrScanner = module.default;
      }
      showScanner = true;
    }
  }

  // Handle address paste
  async function handleAddressPaste() {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        recipientAddress = text.trim();
      }
    } catch (err) {
      console.error("Failed to read clipboard:", err);
    }
  }

  // Handle QR scan result
  function handleScan(data: string) {
    showScanner = false;
    if (data) {
      // Extract address from URI if needed
      const addressMatch = data.match(/(?:canister:)?([\w-]+)(?:\?|$)/);
      recipientAddress = addressMatch ? addressMatch[1] : data;
    }
  }

  // Handle token send
  async function handleSubmit() {
    isValidating = true;
    errorMessage = "";

    if (!isFormValid) {
      isValidating = false;
      return;
    }

    // Prepare transfer details for confirmation
    transferDetails = {
      amount,
      token,
      tokenFee,
      toPrincipal: recipientAddress,
    };

    // Show transfer confirmation modal
    showConfirmation = true;
    isValidating = false;
  }

  // Check if camera is available
  async function checkCameraAvailability() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      hasCamera = devices.some((device) => device.kind === "videoinput");
    } catch (err) {
      console.debug("Error checking camera:", err);
      hasCamera = false;
    }
  }

  // Handle confirmation close
  function handleConfirmationClose() {
    showConfirmation = false;
    transferDetails = null;
  }

  // Handle confirmation confirm
  async function handleConfirmationConfirm() {
    if (!transferDetails) return;
    
    isValidating = true;
    errorMessage = "";
    showConfirmation = false;

    try {
      const decimals = token.decimals || 8;
      const amountBigInt = BigInt(
        new BigNumber(amount).times(new BigNumber(10).pow(decimals)).toString()
      );

      // Ensure auth is properly initialized
      if (!$store.isAuthed) {
        throw new Error("Authentication not initialized");
      }

      const result = await IcrcService.transfer(
        token,
        recipientAddress,
        amountBigInt,
        {
          fee: token.fee_fixed ? BigInt(token.fee_fixed) : tokenFee
        }
      );

      //@ts-ignore
      if (result?.Ok) {
        //@ts-ignore
        const txId = result.Ok.toString();
        
        // Update local state first
        recipientAddress = "";
        amount = "";
        
        // Try to update balances before closing the modal
        try {
          await loadBalances();
        } catch (balanceError) {
          console.error("Failed to refresh balances:", balanceError);
          // Continue with success flow even if balance refresh fails
        }
        
        //@ts-ignore
        onSuccess(txId);
        
        // Close modal last
        onClose();
        //@ts-ignore
      } else if (result?.Err) {
        const errMsg =
        //@ts-ignore
          typeof result.Err === "object"
          //@ts-ignore
            ? Object.keys(result.Err)[0]
            //@ts-ignore
            : String(result.Err);
        errorMessage = `Transfer failed: ${errMsg}`;
        //@ts-ignore
        console.error("Transfer error details:", result.Err);
      }
    } catch (err) {
      console.error("Transfer error:", err);
      errorMessage = err.message || "Transfer failed";
    } finally {
      isValidating = false;
    }
  }

  // Validate address
  $: {
    if (recipientAddress) {
      addressValidation = validateAddress(recipientAddress, token.symbol, token.name);
    } else {
      addressValidation = { isValid: false, errorMessage: "", addressType: null };
    }
  };

  // Validate amount
  $: {
    if (amount) {
      const currentBalance = balances.default;
      amountValidation = validateTokenAmount(amount, currentBalance, token.decimals, tokenFee);
    } else {
      amountValidation = { isValid: false, errorMessage: "" };
    }
  };

  // Update error message based on validations (separate effect to avoid circular dependencies)
  $: {
    if (addressValidation.errorMessage) {
      errorMessage = addressValidation.errorMessage;
    } else if (amountValidation.errorMessage) {
      errorMessage = amountValidation.errorMessage;
    } else {
      errorMessage = "";
    }
  };

  // Check if form is valid
  $: isFormValid = Boolean(
    amount &&
    recipientAddress &&
    !errorMessage &&
    addressValidation.addressType !== null &&
    addressValidation.isValid &&
    amountValidation.isValid
  );

  // Format tooltip message
  function getTooltipMessage(): string {
    if (!recipientAddress) return "Enter recipient address";
    if (!amount) return "Enter amount";
    if (errorMessage) return errorMessage;
    return "Send tokens";
  }

  // Initialize component
  onMount(() => {
    checkCameraAvailability();
    loadTokenFee();
    loadBalances();
  });
</script>

<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Send {token.name}"
  width="min(480px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="send-token-modal"
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
        <div class="text-white font-medium text-sm sm:text-base truncate">{token.name}</div>
        <div class="text-xs sm:text-sm text-gray-400 truncate">
          Balance: {formatBalance(balances.default.toString(), token.decimals)} {token.symbol}
        </div>
      </div>
    </div>

    <form
      on:submit|preventDefault={handleSubmit}
      class="flex flex-col gap-3 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '20px')});"
    >
      <div>
        <label for="recipient-address" class="block text-[13px] font-medium text-gray-400 mb-1.5">Recipient address</label>
        <div class="relative">
          <input
            id="recipient-address"
            type="text"
            class="agent-input !pr-16 sm:!pr-20 !text-xs sm:!text-sm font-mono
              {addressValidation.isValid ? '!border-emerald-500/50 focus:!ring-emerald-500/30' : ''}
              {!addressValidation.isValid && recipientAddress ? '!border-red-500/50 focus:!ring-red-500/30' : ''}"
            placeholder="Principal ID, Account ID, or Canister ID"
            bind:value={recipientAddress}
            on:input={handleAddressInput}
          />
          <div class="absolute inset-y-0 right-0 flex items-center gap-0.5 pr-1">
            {#if addressValidation.isValid}
              <div class="p-1.5 text-emerald-400">
                <Check size={16} />
              </div>
            {/if}
            <button
              type="button"
              class="p-1.5 text-gray-500 hover:text-[#a78bfa] transition-colors"
              on:click={handleAddressPaste}
              use:tooltip={{ text: "Paste from clipboard", direction: "top" }}
            >
              <Clipboard size={16} />
            </button>
            {#if hasCamera}
              <button
                type="button"
                class="p-1.5 text-gray-500 hover:text-[#a78bfa] transition-colors"
                on:click={handleScanClick}
                use:tooltip={{ text: "Scan QR code", direction: "top" }}
              >
                <Camera size={16} />
              </button>
            {/if}
          </div>
        </div>
        {#if addressValidation.addressType && addressValidation.isValid}
          <div class="mt-1.5 text-xs text-emerald-400">
            Valid {addressValidation.addressType} address
          </div>
        {/if}
      </div>

      <div>
        <div class="flex justify-between items-center mb-1.5">
          <label for="amount-input" class="block text-[13px] font-medium text-gray-400">Amount</label>
          <button
            type="button"
            class="text-xs font-medium text-[#a78bfa] hover:text-white transition-colors"
            on:click={handleSendMax}
          >
            Send max
          </button>
        </div>
        <div class="relative">
          <input
            id="amount-input"
            type="text"
            inputmode="decimal"
            class="agent-input !pr-14 sm:!pr-16 !text-xs sm:!text-sm tabular-nums
              {amountValidation.isValid && amount ? '!border-emerald-500/50 focus:!ring-emerald-500/30' : ''}
              {!amountValidation.isValid && amount ? '!border-red-500/50 focus:!ring-red-500/30' : ''}"
            placeholder={`Enter amount of ${token.symbol}`}
            bind:value={amount}
            on:input={handleAmountInput}
          />
          <div class="absolute inset-y-0 right-0 flex items-center">
            <span class="pr-3 text-xs sm:text-sm text-gray-500">{token.symbol}</span>
          </div>
        </div>
        {#if Number(amount) > 0}
          <div class="mt-1.5 text-xs text-gray-500">
            Fee: {formatBalance(String(tokenFee), token.decimals)} {token.symbol}
          </div>
        {/if}
      </div>

      {#if errorMessage}
        <div class="p-2.5 rounded-xl border border-red-500/25 bg-red-500/10 text-red-300 text-xs sm:text-sm">
          {errorMessage}
        </div>
      {/if}

      <button
        type="submit"
        class="mt-1 w-full agent-btn-primary !h-10 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-agent-purple"
        disabled={!isFormValid || isValidating}
        use:tooltip={{ text: getTooltipMessage(), direction: "top" }}
      >
        {#if isValidating}
          <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          Processing…
        {:else}
          <ArrowUp size={16} />
          Send {token.symbol}
        {/if}
      </button>
    </form>
  </div>
</Modal>

{#if showScanner && QrScanner}
  <div class="fixed inset-0 bg-black/80 flex items-center justify-center z-[100001]" transition:fade={{ duration: 200 }}>
    <div class="relative agent-card !bg-agent-surface rounded-2xl overflow-hidden w-full max-w-md mx-4">
      <div class="relative z-[1] p-4 flex justify-between items-center border-b border-white/[0.06]">
        <h3 class="font-medium text-white">Scan QR code</h3>
        <button type="button" class="text-gray-400 hover:text-white transition-colors" on:click={() => showScanner = false}>
          <X size={20} />
        </button>
      </div>
      <svelte:component this={QrScanner} isOpen={true} onScan={handleScan} onClose={() => showScanner = false} />
    </div>
  </div>
{/if}

<!-- Confirmation Modal -->
{#if showConfirmation}
  <TransferConfirmationModal 
    isOpen={showConfirmation}
    onClose={handleConfirmationClose}
    onConfirm={handleConfirmationConfirm}
    transferDetails={transferDetails}
    isProcessing={isValidating}
  />
{/if}

<style>
  /* Custom styling for component - ensures proper z-indexing */
  :global(.send-token-modal) {
    max-width: min(480px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure proper text wrapping on mobile */
  :global(.send-token-modal .truncate) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 640px) {
    :global(.send-token-modal) {
      margin: 0.5rem;
    }
  }
  
  /* Ensure QR scanner is above the modal */
  :global(.qr-scanner-container) {
    z-index: 100001 !important;
  }
</style>