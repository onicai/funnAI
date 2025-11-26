<script lang="ts">
  import { store } from "../../stores/store";
  import { onMount } from "svelte";
  import { getMainerVisualIdentity } from "../../helpers/utils/mainerIdentity";
  import { Check, ShoppingCart, Sparkles, AlertTriangle } from "lucide-svelte";

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

<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
  <!-- Header -->
  <div class="bg-gradient-to-r from-purple-500 to-blue-500 px-6 py-4">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
        <ShoppingCart class="w-6 h-6 text-white" />
      </div>
      <div>
        <h2 class="text-xl font-bold text-white">My mAIners</h2>
        <p class="text-sm text-white/80">Select a mAIner to list on the marketplace</p>
      </div>
    </div>
  </div>

  <!-- Content -->
  <div class="p-6">
    {#if !$store.isAuthed}
      <div class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingCart class="w-8 h-8 text-gray-400" />
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-2">Connect your wallet</p>
        <p class="text-sm text-gray-500 dark:text-gray-500">Sign in to view and sell your mAIners</p>
      </div>
    {:else if myMainers.length === 0}
      <div class="text-center py-12">
        <div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <ShoppingCart class="w-8 h-8 text-gray-400" />
        </div>
        <p class="text-gray-600 dark:text-gray-400 mb-2">No mAIners available</p>
        <p class="text-sm text-gray-500 dark:text-gray-500">Create a mAIner to start selling</p>
      </div>
    {:else}
      <!-- mAIner List -->
      <div class="space-y-3 mb-6">
        {#each myMainers as mainer, index}
          {@const identity = getMainerVisualIdentity(mainer.id)}
          {@const isSelected = selectedMainer === mainer.id}
          {@const isDisabled = mainer.hasLowCycles}
          
          <div 
            class="group relative overflow-hidden rounded-lg border-2 transition-all duration-300
                   {isDisabled 
                     ? 'border-orange-300 dark:border-orange-700 bg-orange-50 dark:bg-orange-900/10 cursor-not-allowed opacity-75' 
                     : isSelected 
                       ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-lg cursor-pointer' 
                       : 'border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600 bg-white dark:bg-gray-800 cursor-pointer'}"
            role="button"
            tabindex={isDisabled ? -1 : 0}
            on:click={() => toggleMainerSelection(mainer.id, mainer.hasLowCycles)}
            on:keydown={(e) => e.key === 'Enter' || e.key === ' ' ? toggleMainerSelection(mainer.id, mainer.hasLowCycles) : null}
          >
            <!-- Background gradient effect -->
            <div class="absolute inset-0 bg-gradient-to-br {identity.colors.bg} opacity-5"></div>
            
            <div class="relative p-4">
              <div class="flex items-start space-x-4">
                <!-- Checkbox / Warning -->
                <div class="flex-shrink-0 pt-1">
                  {#if isDisabled}
                    <div class="w-6 h-6 rounded-md border-2 border-orange-400 bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                      <AlertTriangle class="w-4 h-4 text-orange-500" />
                    </div>
                  {:else}
                    <div class="w-6 h-6 rounded-md border-2 transition-all duration-200 flex items-center justify-center
                                {isSelected 
                                  ? 'bg-purple-500 border-purple-500' 
                                  : 'border-gray-300 dark:border-gray-600 group-hover:border-purple-400'}">
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
                      <div class="w-12 h-12 {identity.colors.accent} backdrop-blur-sm rounded-xl shadow-lg flex items-center justify-center border-2 border-white/20">
                        <div class="w-6 h-6 {identity.colors.icon}">
                          {@html identity.icon}
                        </div>
                      </div>
                      
                      <div>
                        <h3 class="font-semibold text-gray-900 dark:text-white">🦜 {mainer.name}</h3>
                        {#if mainer.createdAt}
                          <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            Created: {formatDate(mainer.createdAt)}
                          </p>
                        {/if}
                      </div>
                    </div>

                    <!-- Status & Cycles -->
                    <div class="flex-shrink-0 flex flex-col items-end gap-1">
                      <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium
                                   {mainer.status === 'active' 
                                     ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' 
                                     : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}">
                        <span class="w-1.5 h-1.5 rounded-full mr-1.5 {mainer.status === 'active' ? 'bg-green-500' : 'bg-gray-500'}"></span>
                        {mainer.status}
                      </span>
                      <span class="text-xs {isDisabled ? 'text-orange-600 dark:text-orange-400 font-medium' : 'text-gray-500 dark:text-gray-400'}">
                        ⚡ {formatCycles(mainer.cycleBalance)}
                      </span>
                    </div>
                  </div>

                  <!-- Low Cycles Warning -->
                  {#if isDisabled}
                    <div class="mt-3 p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg border border-orange-200 dark:border-orange-800">
                      <p class="text-sm text-orange-700 dark:text-orange-300 font-medium">
                        ⚠️ Insufficient cycles to list
                      </p>
                      <p class="text-xs text-orange-600 dark:text-orange-400 mt-1">
                        Minimum 0.1T cycles required. Current: {formatCycles(mainer.cycleBalance)}. 
                        <span class="font-medium">Burn FUNNAI to top up cycles.</span>
                      </p>
                    </div>
                  {/if}

                  <!-- Price Input (shown when selected) -->
                  {#if isSelected}
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div class="mt-4 pl-12" on:click|stopPropagation on:keydown|stopPropagation>
                      <label for="price-input-{mainer.id}" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent
                                 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 
                                 text-gray-900 dark:text-white placeholder-gray-400
                                 {priceError ? 'border-red-500' : ''}"
                        />
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">ICP</span>
                      </div>
                      {#if priceError}
                        <p class="mt-1 text-sm text-red-600 dark:text-red-400">{priceError}</p>
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
        <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Selected: <span class="font-semibold text-gray-900 dark:text-white">mAIner {selectedMainer.slice(0, 5)}</span>
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-500 mt-0.5">
                Set a price to list on the marketplace
              </p>
            </div>
          </div>
          
          <button
            on:click={handleListToMarketplace}
            disabled={isSubmitting || !!priceError || !price}
            class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 
                   text-white font-semibold rounded-lg transition-all duration-200 
                   disabled:opacity-50 disabled:cursor-not-allowed
                   flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl
                   transform hover:scale-[1.02] active:scale-[0.98]"
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


