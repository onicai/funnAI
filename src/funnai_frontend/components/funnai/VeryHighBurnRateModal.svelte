<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import TokenImages from "../TokenImages.svelte";

  import { ArrowUp, Info, Flame } from 'lucide-svelte';
  import { MEMO_PAYMENT_PROTOCOL, store, theme } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import BigNumber from "bignumber.js";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, protocolConfig } from "../../helpers/token_helpers";
  import { getIsProtocolActive } from "../../helpers/gameState";

  export let isOpen: boolean = false;
  export let onClose: () => void = () => {};
  export let onSuccess: (txId: string, canisterId: string, backendPromise: Promise<any>) => void = () => {};
  export let canisterId: string = "";
  export let canisterName: string = "";
  
  // Protocol address from token_helpers
  const { address: protocolAddress } = protocolConfig;

  console.log("in VeryHighBurnRateModal protocolAddress ", protocolAddress);
  
  // Fixed FUNNAI burn amount (42 FUNNAI)
  const BURN_AMOUNT = "42";
  const BURN_AMOUNT_BIGINT = BigInt("4200000000"); // 42 FUNNAI in e8s (42 * 10^8)
  
  // Token configurations - only FUNNAI for burning
  let funnaiToken: any = null;
  let isTokenLoading: boolean = true;
  
  // Load FUNNAI token data from token_helpers
  async function loadTokenData() {
    isTokenLoading = true;
    try {
      const result = await fetchTokens({});
      const token = result.tokens.find(t => t.symbol === "FUNNAI");
      
      if (token) {
        funnaiToken = token;
      } else {
        throw new Error("FUNNAI token not found in token_helpers");
      }
    } catch (error) {
      console.error("Error loading FUNNAI token data:", error);
      // Fallback to default values if token data can't be loaded
      funnaiToken = {
        name: "FUNNAI",
        symbol: "FUNNAI", 
        decimals: 8,
        fee_fixed: "1", // 0.00000001 FUNNAI fee
        canister_id: "vpyot-zqaaa-aaaaa-qavaq-cai" // FUNNAI canister ID
      };
    } finally {
      isTokenLoading = false;
    }
  }
  
  let isValidating: boolean = false;
  let errorMessage: string = "";
  let balance: bigint = BigInt(0);
  let tokenFee: bigint = BigInt(0); // FUNNAI fee
  
  // Check if user has enough FUNNAI balance (no fee required for burning)
  $: hasEnoughBalance = funnaiToken && balance >= BURN_AMOUNT_BIGINT;
  $: canSubmit = hasEnoughBalance && !isValidating && funnaiToken;
  
  // Load balance when FUNNAI token is available
  $: if (funnaiToken && $store.principal) {
    loadBalance();
  }
  
  // Set token fee when FUNNAI token is loaded
  $: if (funnaiToken) {
    tokenFee = BigInt(funnaiToken.fee_fixed);
  }
  
  async function loadBalance() {
    try {
      if (!$store.principal || !funnaiToken) return;
      
      balance = await IcrcService.getIcrc1Balance(
        funnaiToken,
        $store.principal
      ) as bigint;
    } catch (error) {
      console.error("Error loading FUNNAI balance:", error);
    }
  }

  // Handle modal close function explicitly
  function handleClose() {
    isOpen = false;
    onClose();
  }

  async function handleSubmit() {
    if (isValidating || !hasEnoughBalance || !funnaiToken) return;
    isValidating = true;
    errorMessage = "";

    try {
      // Security checks
      const isProtocolActive = await getIsProtocolActive();
      if (!isProtocolActive) {
        throw new Error("Protocol is not active and actions are paused");
      };

      if (!$store.principal) {
        throw new Error("Authentication not initialized");
      }
      
      if (!canisterId) {
        throw new Error("Canister ID is required");
      }

      // Verify the game state canister is available for FUNNAI operations
      if (!$store.gameStateCanisterActor) {
        throw new Error("Game state canister not available for FUNNAI operations");
      }

      tokenFee = BigInt(0); // for burn transactions, set to 0

      // Transfer FUNNAI tokens to the Protocol's account (same logic as top-up)
      // The backend will handle this as a burn for enabling Very High burn rate
      const result = await IcrcService.transfer(
        funnaiToken,
        protocolAddress,  // Use protocol address from token_helpers
        BURN_AMOUNT_BIGINT,
        {
          fee: tokenFee,
          // Include the memo for transactions to the Protocol
          memo: MEMO_PAYMENT_PROTOCOL
        }
      );

      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        console.log("handleSubmit burn txId: ", txId);
        
        // Create the backend promise but don't await it here
        const mainerAgent = $store.userMainerAgentCanistersInfo.find(agent => agent.address === canisterId);
        if (!mainerAgent) {
          throw new Error("mAIner agent not found in user data");
        }

        // Helper function to clean enriched data (extract only original backend fields)
        function getOriginalCanisterInfo(enrichedCanisterInfo) {
          const {
            // Remove UI-specific fields that we added
            uiStatus,
            cycleBalance,
            burnedCycles,
            cyclesBurnRate,
            cyclesBurnRateSetting,
            llmCanisters,
            llmSetupStatus,
            hasError,
            // Keep only original backend fields
            ...originalInfo
          } = enrichedCanisterInfo;
          return originalInfo;
        }

        // Clean the enriched data to get only original backend fields
        const cleanMainerAgent = getOriginalCanisterInfo(mainerAgent);

        let burnInput = {
          paymentTransactionBlockId: BigInt(txId),
          mainerAgent: cleanMainerAgent,
        };

        // Create the backend promise to update the mAIner agent settings to Very High burn rate
        let backendPromise: Promise<any>;
        
        // Get the mAIner actor to call updateAgentSettings directly
        const actorIndex = $store.userMainerAgentCanistersInfo.findIndex(agent => agent.address === canisterId);
        if (actorIndex < 0) {
          throw new Error("mAIner agent actor not found");
        }
        
        const agentActor = $store.userMainerCanisterActors[actorIndex];
        if (!agentActor) {
          throw new Error("mAIner agent actor not available");
        }
        
        // Prepare the burn rate setting for Very High
        const burnRateSetting = { cyclesBurnRate: { VeryHigh: null } };
        
        // Create the backend promise to update agent settings
        backendPromise = agentActor.updateAgentSettings(burnRateSetting);

        // Close modal immediately and pass promise to parent
        onSuccess(txId, canisterId, backendPromise);
        handleClose();
        
      } else if (result && typeof result === 'object' && 'Err' in result) {
        const errMsg = typeof result.Err === 'object' 
          ? Object.keys(result.Err)[0]
          : String(result.Err);
        errorMessage = `FUNNAI burn failed: ${errMsg}`;
        console.error("FUNNAI burn error details:", result.Err);
      }
    } catch (err) {
      console.error("Very High burn rate activation error:", err);
      errorMessage = err.message || "FUNNAI burn failed";
    } finally {
      isValidating = false;
    }
  }

  onMount(async () => {
    await loadTokenData();
    loadBalance();
  });
</script>

<Modal
  {isOpen}
  onClose={handleClose}
  title="Activate Very High Burn Rate"
  width="min(480px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="very-high-burn-rate-modal"
  closeOnEscape={true}
  closeOnClickOutside={true}
  isPadded={true}
>
  <div class="px-2 sm:px-4 py-4 flex flex-col gap-3 sm:gap-4">
    {#if isTokenLoading}
      <div class="flex justify-center py-4">
        <span class="w-6 h-6 border-2 border-gray-400/30 border-t-gray-400 dark:border-gray-400/30 dark:border-t-gray-400 rounded-full animate-spin"></span>
      </div>
    {:else}
      <!-- Header Info -->
      <div class="bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <Flame size={24} class="text-red-600 dark:text-red-400" />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold text-red-900 dark:text-red-100 mb-2">Unlock Maximum Performance</h3>
            <p class="text-sm text-red-800 dark:text-red-200 mb-3">
              Activate <span class="font-bold">Very High</span> burn rate (≈6T cycles/day) by burning <span class="font-bold">{BURN_AMOUNT} FUNNAI</span> tokens.
            </p>
            <div class="flex justify-between items-center bg-red-100 dark:bg-red-800/30 rounded-md p-2">
              <span class="text-xs text-red-700 dark:text-red-300 font-medium pr-1">🔥</span>
              <span class="text-xs text-red-600/80 dark:text-red-300/80">
                <span class="text-xs text-red-700 dark:text-red-300 font-medium">Permanent Burn</span><br/>
                Burns {BURN_AMOUNT} FUNNAI tokens to unlock Very High performance tier.
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- FUNNAI Token Info -->
      {#if funnaiToken}
        <div class="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg bg-gray-100 border border-gray-300 text-gray-900 dark:bg-gray-700/20 dark:border-gray-600/30 dark:text-gray-100">
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gray-200 border border-gray-300 flex-shrink-0 dark:bg-gray-800 dark:border-gray-700">
            <div class="sm:hidden">
              <TokenImages tokens={[funnaiToken]} size={32} showSymbolFallback={true} />
            </div>
            <div class="hidden sm:block">
              <TokenImages tokens={[funnaiToken]} size={38} showSymbolFallback={true} />
            </div>
          </div>
          <div class="flex flex-col min-w-0 flex-1">
            <div class="text-gray-900 font-medium dark:text-gray-100 text-sm sm:text-base truncate">{funnaiToken.name}</div>
            <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 truncate">Balance: {formatBalance(balance.toString(), funnaiToken.decimals)} {funnaiToken.symbol}</div>
          </div>
        </div>
      {/if}

      <!-- Burn Details -->
      <div class="flex flex-col gap-2 sm:gap-3">
        <!-- Canister ID -->
        <div>
          <label for="canister-input" class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">mAIner canister</label>
          <div class="relative">
            <input
              id="canister-input"
              type="text"
              class="w-full py-2 px-2 sm:px-3 bg-white border border-gray-300 rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100"
              value={canisterName ? `${canisterName} (${canisterId})` : canisterId}
              disabled
            />
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-500">mAIner to activate Very High burn rate</div>
        </div>

        <!-- Burn Amount Display -->
        <div>
          <label for="burn-amount-input" class="block text-xs text-gray-600 mb-1.5 dark:text-gray-400">FUNNAI Burn Amount</label>
          <div class="relative">
            <input
              id="burn-amount-input"
              type="text"
              class="w-full py-2 px-2 sm:px-3 bg-gray-50 border border-gray-300 rounded-md text-xs sm:text-sm text-gray-900 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 pr-16"
              value={BURN_AMOUNT}
              disabled
            />
            <div class="absolute inset-y-0 right-0 flex items-center">
              <span class="pr-2 sm:pr-3 text-xs sm:text-sm text-gray-600 dark:text-gray-400 font-medium">FUNNAI</span>
            </div>
          </div>
          <div class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            Required amount to unlock Very High burn rate
          </div>
        </div>

        <!-- Balance Check -->
        {#if !hasEnoughBalance && funnaiToken}
          <div class="mt-1 p-2 rounded bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm dark:bg-red-900/30 dark:border-red-900/50 dark:text-red-400">
            Insufficient FUNNAI balance. You need {formatBalance(BURN_AMOUNT_BIGINT.toString(), funnaiToken.decimals)} FUNNAI (fees handled automatically for burning) but only have {formatBalance(balance.toString(), funnaiToken.decimals)} FUNNAI.
          </div>
        {/if}

        <!-- Error message -->
        {#if errorMessage}
          <div class="mt-1 p-2 rounded bg-red-50 border border-red-200 text-red-700 text-xs sm:text-sm dark:bg-red-900/30 dark:border-red-900/50 dark:text-red-400">
            {errorMessage}
          </div>
        {/if}

        <!-- Burn Button -->
        <button
          type="button"
          on:click={handleSubmit}
          class="mt-2 py-2 sm:py-2.5 px-3 sm:px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors text-sm sm:text-base"
          class:bg-red-600={canSubmit}
          class:hover:bg-red-500={canSubmit}
          class:bg-gray-400={!canSubmit}
          class:cursor-not-allowed={!canSubmit}
          class:dark:bg-gray-700={!canSubmit}
          disabled={!canSubmit}
        >
          {#if isValidating}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            Processing Burn...
          {:else}
            <Flame size={14} class="sm:hidden" />
            <Flame size={16} class="hidden sm:block" />
            Burn {BURN_AMOUNT} FUNNAI & Activate
          {/if}
        </button>
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.very-high-burn-rate-modal) {
    max-width: min(480px, calc(100vw - 2rem));
    position: relative;
    z-index: 100000;
  }
  
  /* Ensure proper text wrapping on mobile */
  :global(.very-high-burn-rate-modal .truncate) {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  /* Mobile-specific adjustments */
  @media (max-width: 640px) {
    :global(.very-high-burn-rate-modal) {
      margin: 0.5rem;
    }
  }
</style>
