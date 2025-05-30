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
  //import { toastStore } from "$lib/stores/toastStore";
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
    console.log("in handleAddressInput event ", event);
    const input = event.target as HTMLInputElement;
    console.log("in handleAddressInput input ", input);
    recipientAddress = input.value.trim();
    console.log("in handleAddressInput recipientAddress ", recipientAddress);
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
    } else {
      //toastStore.warning("No camera detected on your device");
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
      //toastStore.error("Failed to access clipboard");
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
    console.log("in handleConfirmationConfirm transferDetails ", transferDetails);
    if (!transferDetails) return;
    
    isValidating = true;
    errorMessage = "";
    showConfirmation = false;

    try {
      const decimals = token.decimals || 8;
      console.log("in handleConfirmationConfirm decimals ", decimals);
      console.log("in handleConfirmationConfirm amount ", amount);
      const amountBigInt = BigInt(
        new BigNumber(amount).times(new BigNumber(10).pow(decimals)).toString()
      );
      console.log("in handleConfirmationConfirm amountBigInt ", amountBigInt);

      //toastStore.info(`Sending ${amount} ${token.symbol}...`);

      // Ensure auth is properly initialized
      if (!$store.isAuthed) {
        throw new Error("Authentication not initialized");
      }

      // Always use main account (no fromSubaccount)
      console.log("in handleConfirmationConfirm token ", token);
      console.log("in handleConfirmationConfirm recipientAddress ", recipientAddress);
      console.log("in handleConfirmationConfirm tokenFee ", tokenFee);
      console.log("in handleConfirmationConfirm token.fee_fixed ", token.fee_fixed);
      console.log("in handleConfirmationConfirm BigInt(token.fee_fixed) ", BigInt(token.fee_fixed));
      const result = await IcrcService.transfer(
        token,
        recipientAddress,
        amountBigInt,
        {
          fee: token.fee_fixed ? BigInt(token.fee_fixed) : tokenFee
        }
      );
      console.log("in handleConfirmationConfirm result ", result);

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
        
        // Show success message and trigger callbacks
        //toastStore.success(`Successfully sent ${token.symbol}`);
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
        //toastStore.error(errorMessage);
        //@ts-ignore
        console.error("Transfer error details:", result.Err);
      }
    } catch (err) {
      console.error("Transfer error:", err);
      errorMessage = err.message || "Transfer failed";
      //toastStore.error(errorMessage);
    } finally {
      isValidating = false;
    }
  }

  // Validate address
  $: {
    console.log("in validate address recipientAddress ", recipientAddress);
    if (recipientAddress) {
      addressValidation = validateAddress(recipientAddress, token.symbol, token.name);
      console.log("in validate address addressValidation ", addressValidation);
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
  width="480px"
  variant="transparent"
  height="auto"
  className="send-token-modal"
>
  <div class="p-4 flex flex-col gap-4">
    <!-- Token Info Banner -->
    <div 
      class="flex items-center gap-3 p-3 rounded-lg bg-gray-100 border border-gray-300 text-gray-900 dark:bg-gray-700/20 dark:border-gray-600/30 dark:text-gray-100 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '10px')});"
    >
      <div class="w-10 h-10 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-800 dark:border-gray-700">
        <TokenImages tokens={[token]} size={32} showSymbolFallback={true} />
      </div>
      <div class="flex flex-col">
        <div class="text-gray-900 font-medium dark:text-gray-100">{token.name}</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Balance: {formatBalance(balances.default.toString(), token.decimals)} {token.symbol}</div>
      </div>
    </div>

    <!-- Send Form -->
    <form 
      on:submit|preventDefault={handleSubmit}
      class="flex flex-col gap-3 transition-all duration-300"
      style="opacity: {closing ? 0 : (mounted ? 1 : 0)}; transform: translateY({closing ? '-10px' : (mounted ? 0 : '20px')});"
    >
      <!-- Recipient Address Input -->
      <div>
        <label for="recipient-address" class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">Recipient Address</label>
        <div class="relative">
          <input
            id="recipient-address"
            type="text"
            class="w-full py-2 px-3 bg-white border rounded-md text-sm text-gray-900 dark:bg-gray-800 dark:text-gray-100"
            class:border-green-400={addressValidation.isValid}
            class:border-red-400={!addressValidation.isValid && recipientAddress}
            class:border-gray-300={!recipientAddress}
            class:dark:border-gray-600={!recipientAddress}
            placeholder="Enter Canister ID, Principal ID, or Account ID"
            bind:value={recipientAddress}
            on:input={handleAddressInput}
          />
          <div class="absolute inset-y-0 right-0 flex items-center gap-0.5">
            {#if addressValidation.isValid}
              <div class="p-1.5 text-green-500">
                <Check size={16} />
              </div>
            {/if}
            <button
              type="button"
              class="p-1.5 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
              on:click={handleAddressPaste}
              use:tooltip={{ text: "Paste from clipboard", direction: "top" }}
            >
              <Clipboard size={16} />
            </button>
            {#if hasCamera}
              <button
                type="button"
                class="p-1.5 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
                on:click={handleScanClick}
                use:tooltip={{ text: "Scan QR code", direction: "top" }}
              >
                <Camera size={16} />
              </button>
            {/if}
          </div>
        </div>
        {#if addressValidation.addressType && addressValidation.isValid}
          <div class="mt-1 text-xs text-green-600 dark:text-green-500">
            Valid {addressValidation.addressType} address
          </div>
        {/if}
      </div>

      <!-- Amount Input -->
      <div>
        <div class="flex justify-between items-center mb-1.5">
          <label for="amount-input" class="block text-xs text-gray-600 dark:text-gray-400">Amount</label>
          <button
            type="button"
            class="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-500 dark:hover:text-blue-400"
            on:click={handleSendMax}
          >
            Send Max
          </button>
        </div>
        <div class="relative">
          <input
            id="amount-input"
            type="text"
            inputmode="decimal"
            class="w-full py-2 px-3 bg-white border rounded-md text-sm text-gray-900 dark:bg-gray-800 dark:text-gray-100"
            class:border-green-400={amountValidation.isValid && amount}
            class:border-red-400={!amountValidation.isValid && amount}
            class:border-gray-300={!amount}
            class:dark:border-gray-600={!amount}
            placeholder={`Enter amount of ${token.symbol}`}
            bind:value={amount}
            on:input={handleAmountInput}
          />
          <div class="absolute inset-y-0 right-0 flex items-center">
            <span class="pr-3 text-sm text-gray-600 dark:text-gray-400">{token.symbol}</span>
          </div>
        </div>
        {#if Number(amount) > 0}
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Fee: {formatBalance(String(tokenFee), token.decimals)} {token.symbol}
          </div>
        {/if}
      </div>

      <!-- Error message -->
      {#if errorMessage}
        <div class="mt-1 p-2 rounded bg-red-50 border border-red-200 text-red-700 text-sm dark:bg-red-900/30 dark:border-red-900/50 dark:text-red-400">
          {errorMessage}
        </div>
      {/if}

      <!-- Send Button -->
      <button
        type="submit"
        class="mt-2 py-2.5 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors"
        class:bg-blue-600={isFormValid && !isValidating}
        class:hover:bg-blue-500={isFormValid && !isValidating}
        class:bg-gray-400={!isFormValid || isValidating}
        class:dark:bg-gray-700={!isFormValid || isValidating}
        class:cursor-not-allowed={!isFormValid || isValidating}
        disabled={!isFormValid || isValidating}
        use:tooltip={{ text: getTooltipMessage(), direction: "top" }}
      >
        {#if isValidating}
          <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          Processing...
        {:else}
          <ArrowUp size={16} />
          Send {token.symbol}
        {/if}
      </button>
    </form>
  </div>
</Modal>

<!-- QR Scanner Modal -->
{#if showScanner && QrScanner}
  <div class="fixed inset-0 bg-black/80 flex items-center justify-center z-[100001]" transition:fade={{ duration: 200 }}>
    <div class="relative bg-gray-900 rounded-lg shadow-xl overflow-hidden w-full max-w-md mx-4">
      <div class="p-4 flex justify-between items-center border-b border-gray-700">
        <h3 class="font-medium text-gray-100">Scan QR Code</h3>
        <button class="text-gray-400 hover:text-gray-300" on:click={() => showScanner = false}>
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
    max-width: 480px;
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure QR scanner is above the modal */
  :global(.qr-scanner-container) {
    z-index: 100001 !important;
  }
</style>