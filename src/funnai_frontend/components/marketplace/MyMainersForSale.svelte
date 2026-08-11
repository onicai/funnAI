<script lang="ts">
  import { store } from "../../stores/store";
  import { onMount } from "svelte";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { Check, ShoppingCart, Sparkles, AlertTriangle } from "lucide-svelte";
  import LoginModal from "../login/LoginModal.svelte";

  export let onListToMarketplace: (mainerIds: string[], prices: Record<string, number>) => Promise<void>;
  export let listedMainers: string[] = []; // Array of already-listed mAIner addresses

  // Minimum cycles required to list a mAIner (0.1T = 100 billion cycles)
  const MIN_CYCLES_TO_LIST = 100_000_000_000;

  // State
  let myMainers: any[] = [];
  let selectedMainer: string | null = null;
  let price: string = "";
  let isSubmitting = false;
  let priceError: string | null = null;

  // Connect wallet modal state
  let modalIsOpen = false;

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  $: agentCanistersInfo = $store.userMainerAgentCanistersInfo;

  onMount(() => {
    loadMyMainers();
  });

  $: if (agentCanistersInfo || listedMainers) {
    loadMyMainers();
  }

  function loadMyMainers() {
    if (!agentCanistersInfo || agentCanistersInfo.length === 0) {
      myMainers = [];
      return;
    }

    console.log('MyMainersForSale: loadMyMainers called');
    console.log('  Total canisters:', agentCanistersInfo.length);
    console.log('  Listed mAIners to filter:', listedMainers);

    // Filter out unlocked mAIners, already-listed mAIners, and only show active ones that can be sold
    myMainers = agentCanistersInfo
      .filter(canister => {
        const isUnlocked = canister.status && 'Unlocked' in canister.status;
        const isAlreadyListed = listedMainers.includes(canister.address);
        const shouldShow = !isUnlocked && canister.address && !isAlreadyListed;
        
        if (!shouldShow && canister.address) {
          console.log(`  Filtering out ${canister.address}: unlocked=${isUnlocked}, listed=${isAlreadyListed}`);
        }
        
        return shouldShow;
      })
      .map((canister, index) => {
        const cycleBalance = canister.cycleBalance || 0;
        return {
          id: canister.address,
          name: `mAIner ${canister.address?.slice(0, 5)}`,
          status: canister.uiStatus || "active",
          createdAt: canister.creationTimestamp ? Number(canister.creationTimestamp / 1000000n) : null,
          burnedCycles: canister.burnedCycles || 0,
          cycleBalance,
          hasLowCycles: cycleBalance < MIN_CYCLES_TO_LIST,
        };
      });
    
    console.log(`  ✅ Showing ${myMainers.length} available mAIners for sale`);
  }

  function toggleMainerSelection(mainerId: string, hasLowCycles: boolean) {
    // Don't allow selection of mAIners with low cycles
    if (hasLowCycles) {
      return;
    }
    
    if (selectedMainer === mainerId) {
      selectedMainer = null;
      price = "";
      priceError = null;
    } else {
      selectedMainer = mainerId;
      price = "";
      priceError = null;
    }
  }

  function handlePriceInput(value: string) {
    price = value;
    
    // Validate price
    const numValue = parseFloat(value);
    if (!value || value.trim() === "") {
      priceError = "Price is required";
    } else if (isNaN(numValue) || numValue <= 0) {
      priceError = "Price must be greater than 0";
    } else if (numValue < 0.01) {
      priceError = "Minimum price is 0.01 ICP";
    } else {
      priceError = null;
    }
  }

  async function handleListToMarketplace() {
    if (!selectedMainer) {
      return;
    }

    // Validate price
    if (!price || priceError) {
      return;
    }

    isSubmitting = true;
    try {
      const numericPrices: Record<string, number> = {
        [selectedMainer]: parseFloat(price)
      };

      await onListToMarketplace([selectedMainer], numericPrices);

      // Clear selection after successful listing
      selectedMainer = null;
      price = "";
      priceError = null;
    } catch (error) {
      console.error("Error listing mAIner:", error);
    } finally {
      isSubmitting = false;
    }
  }

  function formatDate(timestamp: number): string {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  function formatCycles(cycles: number): string {
    const trillion = 1_000_000_000_000;
    const billion = 1_000_000_000;
    if (cycles >= trillion) {
      return `${(cycles / trillion).toFixed(2)}T`;
    } else if (cycles >= billion) {
      return `${(cycles / billion).toFixed(2)}B`;
    }
    return `${cycles.toLocaleString()}`;
  }
</script>

<div class="agent-card">
  <!-- Header -->
  <div class="border-b border-white/[0.08] px-6 py-4">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-xl bg-agent-purple/15 border border-agent-purple/20 flex items-center justify-center">
        <ShoppingCart class="w-5 h-5 text-agent-purple" />
      </div>
      <div>
        <p class="agent-eyebrow">Sell</p>
        <h2 class="text-lg font-semibold tracking-tight text-white">My mAIners</h2>
        <p class="text-sm text-gray-400">Select a mAIner to list on the marketplace</p>
      </div>
    </div>
  </div>

  <!-- Content -->
  <div class="p-6">
    {#if !$store.isAuthed}
      <div class="text-center py-12">
        <ShoppingCart class="w-8 h-8 text-gray-500 mx-auto mb-4" />
        <button
          type="button"
          on:click={toggleModal}
          class="agent-btn-primary mx-auto mb-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
          </svg>
          <span>Connect Wallet</span>
        </button>
        <p class="text-sm text-gray-500">Sign in to view and sell your mAIners</p>
      </div>
    {:else if myMainers.length === 0}
      <div class="text-center py-12">
        <ShoppingCart class="w-8 h-8 text-gray-500 mx-auto mb-4" />
        <p class="text-gray-400 mb-2">No mAIners available</p>
        <p class="text-sm text-gray-500">Create a mAIner to start selling</p>
      </div>
    {:else}
      <!-- mAIner List -->
      <div class="space-y-3 mb-6">
        {#each myMainers as mainer, index}
          {@const identity = getMainerVisualIdentity(mainer.id)}
          {@const isSelected = selectedMainer === mainer.id}
          {@const isDisabled = mainer.hasLowCycles}
          
          <div 
            class="group relative overflow-hidden rounded-xl border transition-all duration-300
                   {isDisabled 
                     ? 'border-amber-500/25 bg-amber-500/5 cursor-not-allowed opacity-75' 
                     : isSelected 
                       ? 'border-agent-purple/50 bg-agent-purple/10 cursor-pointer' 
                       : 'border-white/10 bg-white/[0.03] hover:border-agent-purple/40 cursor-pointer'}"
            role="button"
            tabindex={isDisabled ? -1 : 0}
            on:click={() => toggleMainerSelection(mainer.id, mainer.hasLowCycles)}
            on:keydown={(e) => e.key === 'Enter' || e.key === ' ' ? toggleMainerSelection(mainer.id, mainer.hasLowCycles) : null}
          >
            <!-- Soft identity tint -->
            <div class="absolute inset-0 bg-gradient-to-br {identity.colors.bg} opacity-[0.04]"></div>
            
            <div class="relative p-4">
              <div class="flex items-start space-x-4">
                <!-- Checkbox / Warning -->
                <div class="flex-shrink-0 pt-1">
                  {#if isDisabled}
                    <div class="w-6 h-6 rounded-md border border-amber-500/40 bg-amber-500/10 flex items-center justify-center">
                      <AlertTriangle class="w-4 h-4 text-amber-400" />
                    </div>
                  {:else}
                    <div class="w-6 h-6 rounded-md border transition-all duration-200 flex items-center justify-center
                                {isSelected 
                                  ? 'bg-agent-purple border-agent-purple' 
                                  : 'border-white/20 group-hover:border-agent-purple/50'}">
                      {#if isSelected}
                        <Check class="w-4 h-4 text-white" />
                      {/if}
                    </div>
                  {/if}
                </div>

                <!-- mAIner Avatar & Info -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between">
                    <div class="flex items-center space-x-3">
                      <!-- Avatar -->
                      <div class="w-12 h-12 rounded-xl overflow-hidden border border-white/10 bg-agent-elevated [&>svg]:w-full [&>svg]:h-full [&>svg]:block">
                        {@html identity.icon}
                      </div>
                      
                      <div>
                        <h3 class="font-semibold text-white">{mainer.name}</h3>
                        {#if mainer.createdAt}
                          <p class="text-xs text-gray-500 mt-1">
                            Created: {formatDate(mainer.createdAt)}
                          </p>
                        {/if}
                      </div>
                    </div>

                    <!-- Status & Cycles -->
                    <div class="flex-shrink-0 flex flex-col items-end gap-1">
                      {#if isDisabled}
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 border border-amber-500/25 text-amber-300">
                          <span class="w-1.5 h-1.5 rounded-full mr-1.5 bg-amber-400"></span>
                          Please contact onicai team
                        </span>
                      {:else}
                        <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border
                                     {mainer.status === 'active' 
                                       ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-300' 
                                       : 'bg-white/[0.04] border-white/10 text-gray-300'}">
                          <span class="w-1.5 h-1.5 rounded-full mr-1.5 {mainer.status === 'active' ? 'bg-emerald-400' : 'bg-gray-500'}"></span>
                          {mainer.status}
                        </span>
                      {/if}
                      <span class="text-xs {isDisabled ? 'text-amber-400 font-medium' : 'text-gray-400'}">
                        ⚡ {formatCycles(mainer.cycleBalance)}
                      </span>
                    </div>
                  </div>

                  <!-- Low Cycles Warning -->
                  {#if isDisabled}
                    <div class="mt-3 p-3 bg-amber-500/5 rounded-xl border border-amber-500/20">
                      <p class="text-sm text-amber-300 font-medium">
                        ⚠️ Insufficient cycles to list
                      </p>
                      <p class="text-xs text-amber-400/80 mt-1">
                        Minimum 0.1T cycles required. Current: {formatCycles(mainer.cycleBalance)}. 
                        <span class="font-medium">Top up your mAIner to list.</span>
                      </p>
                    </div>
                  {/if}

                  <!-- Price Input (shown when selected) -->
                  {#if isSelected}
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div class="mt-4 pl-12" on:click|stopPropagation on:keydown|stopPropagation>
                      <label for="price-input-{mainer.id}" class="block text-sm font-medium text-gray-300 mb-2">
                        Set Price (ICP)
                      </label>
                      <div class="flex items-center space-x-2">
                        <input
                          id="price-input-{mainer.id}"
                          type="number"
                          step="0.01"
                          min="0.01"
                          placeholder="0.00"
                          value={price}
                          on:input={(e) => handlePriceInput(e.currentTarget.value)}
                          on:wheel={(e) => e.preventDefault()}
                          class="agent-input flex-1 {priceError ? 'border-red-500/50 focus:ring-red-500/30 focus:border-red-500/50' : ''}"
                        />
                        <span class="text-sm font-medium text-gray-400">ICP</span>
                      </div>
                      {#if priceError}
                        <p class="mt-1 text-sm text-red-400">{priceError}</p>
                      {/if}
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Action Button -->
      {#if selectedMainer}
        <div class="border-t border-white/[0.08] pt-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-sm text-gray-400">
                Selected: <span class="font-semibold text-white">mAIner {selectedMainer.slice(0, 5)}</span>
              </p>
              <p class="text-xs text-gray-500 mt-0.5">
                Set a price to list on the marketplace
              </p>
            </div>
          </div>
          
          <button
            on:click={handleListToMarketplace}
            disabled={isSubmitting || !!priceError || !price}
            class="w-full agent-btn-primary h-11 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if isSubmitting}
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Listing...</span>
            {:else}
              <Sparkles class="w-5 h-5" />
              <span>List to Marketplace</span>
            {/if}
          </button>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Connect Wallet Modal -->
  {#if modalIsOpen}
    <LoginModal {toggleModal} />
  {/if}
</div>

<style>
  input[type="number"]::-webkit-inner-spin-button,
  input[type="number"]::-webkit-outer-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  input[type="number"] {
    -moz-appearance: textfield;
  }
</style>


