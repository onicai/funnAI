<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, FUNNAI_CANISTER_ID } from "../../helpers/token_helpers";
  import { walletDataStore } from "../../helpers/WalletDataService";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";
  import ICPSwapService, { type ICPSwapTokenData } from "../../helpers/icpswapService";
  import { IcrcService } from "../../helpers/IcrcService";
  import { WalletDataService } from "../../helpers/WalletDataService";
  import BigNumber from "bignumber.js";

  export let title: string = "Token economics";

  let loading = true;
  let error = "";
  let updateInterval: NodeJS.Timer;

  // Token metrics
  let tokenPrice = null;
  let marketCap = null;
  let priceChange24h = null;
  let dataLoadedSuccessfully = false;
  let totalSupply = null; // Store total supply for whale calculation

  // User data
  let userBalance = 0;
  let funnaiToken: FE.Token | null = null;
  let icpswapData: ICPSwapTokenData | null = null;
  let isLoadingUserBalance = false;

  // Whale configuration
  const WHALE_THRESHOLD_PERCENT = 0.5; // 0.5% of total supply

  // Subscribe to wallet data store
  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isAuthenticated = $store.isAuthed;

  // Check if user is a whale (holds significant percentage of total supply)
  function isWhale(): boolean {
    if (!totalSupply || !userBalance || userBalance === 0) return false;
    
    const totalSupplyNum = parseFloat(totalSupply.replace(/,/g, ''));
    const userPercentage = (userBalance / totalSupplyNum) * 100;
    
    return userPercentage >= WHALE_THRESHOLD_PERCENT;
  }

  // Get user's percentage of total supply
  function getUserSupplyPercentage(): string {
    if (!totalSupply || !userBalance || userBalance === 0) return "0";
    
    const totalSupplyNum = parseFloat(totalSupply.replace(/,/g, ''));
    const userPercentage = (userBalance / totalSupplyNum) * 100;
    
    return userPercentage.toFixed(3);
  }

  // Format total supply properly (convert from smallest units to whole tokens)
  function formatTotalSupply(rawAmount: bigint, decimals: number): string {
    try {
      // Use BigNumber for precise calculations
      const rawBN = new BigNumber(rawAmount.toString());
      const divisor = new BigNumber(10).pow(decimals);
      const tokenAmount = rawBN.dividedBy(divisor);
      
      // Round down to whole tokens and format with thousands separators
      return tokenAmount.integerValue(BigNumber.ROUND_DOWN).toFormat(0);
    } catch (error) {
      console.error("Error formatting total supply:", error);
      return "0";
    }
  }

  async function loadICPSwapData() {
    try {
      console.log("Fetching FUNNAI data from ICPSwap...");
      const data = await ICPSwapService.fetchTokenData(FUNNAI_CANISTER_ID);
      
      if (data) {
        icpswapData = data;
        
        // Update token metrics with ICPSwap data
        if (data.priceUSD > 0) {
          tokenPrice = data.priceUSD;
        }
        
        // Don't use ICPSwap totalSupply - we get real supply from canister
        
                 // Always calculate market cap using current supply × price
         // Don't use ICPSwap's TVL as it's different from market cap
         
         priceChange24h = data.priceChange24h;
        
                 console.log("ICPSwap data loaded successfully:", {
           price: data.priceUSD,
           priceChange24h: data.priceChange24h
         });
      } else {
        console.warn("No data received from ICPSwap, using fallback values");
      }
    } catch (err) {
      console.error("Error loading ICPSwap data:", err);
      // Continue with fallback values - don't throw error
    }
  }

  async function loadTokenData() {
    try {
      dataLoadedSuccessfully = false;
      
      // Get FUNNAI token info from local source first
      const tokensResult = await fetchTokens({});
      const foundFunnaiToken = tokensResult.tokens.find(token => token.symbol === "FUNNAI");
      
      if (foundFunnaiToken) {
        funnaiToken = foundFunnaiToken;
        
        // Fetch real total supply from canister for market cap calculation
        try {
          const totalSupplyBigInt = await IcrcService.getIcrc1TotalSupply(foundFunnaiToken);
          totalSupply = formatTotalSupply(totalSupplyBigInt, foundFunnaiToken.decimals);
          
        } catch (supplyErr) {
          console.error("Error loading total supply:", supplyErr);
          throw supplyErr; // Re-throw to prevent using fallback calculations
        }
        
        // Get price from local data as fallback
        const apiPrice = foundFunnaiToken.metrics?.price;
        if (apiPrice && parseFloat(apiPrice) > 0) {
          tokenPrice = parseFloat(apiPrice);
        }
      } else {
        throw new Error("FUNNAI token not found in local data");
      }

      // Try to fetch real-time data from ICPSwap
      await loadICPSwapData();

      // Only proceed with calculations if we have valid data
      if (!totalSupply || tokenPrice === null || tokenPrice <= 0) {
        throw new Error("Insufficient data to calculate token metrics");
      }

      // Calculate market cap using real total supply × current price
      const totalSupplyNum = parseFloat(totalSupply.replace(/,/g, ''));
      marketCap = (totalSupplyNum * tokenPrice).toFixed(2);

      // Get user balance if authenticated
      if (isAuthenticated && $store.principal) {
        updateUserBalance();
      }
      
      dataLoadedSuccessfully = true;

    } catch (err) {
      console.error("Error loading token data:", err);
      error = "Failed to load token distribution data";
      
      // Clear all values instead of using fallbacks
      totalSupply = null;
      tokenPrice = null;
      marketCap = null;
      priceChange24h = null;
      dataLoadedSuccessfully = false;
    }
  }

  function updateUserBalance() {
    if (!isAuthenticated || !$store.principal) {
      userBalance = 0;
      isLoadingUserBalance = false;
      return;
    }

    // If wallet data is loading, mark user balance as loading
    if (walletData && walletData.isLoading) {
      isLoadingUserBalance = true;
      return;
    }

    // If no wallet data available yet, don't update balance (keep previous state)
    if (!walletData || !walletData.balances) {
      isLoadingUserBalance = true;
      return;
    }

    // Get FUNNAI balance from wallet data
    const funnaiBalance = walletData.balances[FUNNAI_CANISTER_ID];
    
    if (funnaiBalance && funnaiBalance.in_tokens) {
      // Convert bigint balance to number using formatBalance and the token's decimals
      const decimals = funnaiToken?.decimals || 8;
      const formattedBalance = formatBalance(funnaiBalance.in_tokens.toString(), decimals);
      userBalance = parseFloat(formattedBalance.replace(/,/g, ''));
    } else {
      userBalance = 0;
    }
    
    isLoadingUserBalance = false;
  }

  async function ensureWalletDataInitialized() {
    // If user is authenticated but wallet data isn't initialized or is for a different wallet
    if (isAuthenticated && $store.principal) {
      const principalString = $store.principal.toString();
      
      // Check if wallet data needs initialization
      if (!walletData || 
          !walletData.currentWallet || 
          walletData.currentWallet !== principalString ||
          (walletData.tokens.length === 0 && !walletData.isLoading)) {
        
        console.log("TokenDistribution: Initializing wallet data for", principalString);
        try {
          await WalletDataService.initializeWallet(principalString);
        } catch (err) {
          console.error("TokenDistribution: Error initializing wallet data:", err);
        }
      }
    }
  }

  async function updateTokenData(isRefresh = false) {
    if (!isRefresh) loading = true;
    error = "";

    try {
      // Ensure wallet data is initialized if user is authenticated
      await ensureWalletDataInitialized();
      
      await loadTokenData();
    } catch (err) {
      console.error("Error updating token data:", err);
      error = "Failed to update token data";
    } finally {
      loading = false;
    }
  }

  function formatPriceChange(change: string): string {
    const num = parseFloat(change);
    if (isNaN(num)) return "0.00%";
    return `${num > 0 ? '+' : ''}${num.toFixed(2)}%`;
  }

  function getPriceChangeColor(change: string): string {
    const num = parseFloat(change);
    if (isNaN(num)) return "text-gray-400";
    if (num > 0) return "text-emerald-400";
    if (num < 0) return "text-red-400";
    return "text-gray-400";
  }

  onMount(() => {
    // Initial fetch is triggered by the isAuthenticated reactive below
    updateInterval = setInterval(() => updateTokenData(true), 120000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  // React to authentication changes
  $: if (isAuthenticated !== undefined) {
    updateTokenData(true);
  }

  // React to wallet data changes to update user balance
  $: if (walletData) {
    updateUserBalance();
  }
</script>

<div class="agent-card !bg-agent-surface p-5 sm:p-6">
  <div class="relative z-[1] flex items-start justify-between gap-3 mb-5">
    <div>
      <div class="flex flex-wrap items-center gap-2">
        <p class="agent-eyebrow">Token</p>
        <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300 {icpswapData ? '' : 'invisible'}">
          <span class="h-1 w-1 rounded-full bg-emerald-400 animate-pulse"></span>
          Live
        </span>
      </div>
      <h3 class="mt-1 text-base font-semibold tracking-tight text-white">{title}</h3>
      <p class="mt-0.5 text-sm text-gray-500">FUNNAI price, market cap, and your balance</p>
    </div>
    <span class="inline-flex h-4 w-4 flex-shrink-0 mt-1 items-center justify-center">
      {#if loading || (isAuthenticated && isLoadingUserBalance)}
        <span class="h-4 w-4 border-2 border-[#653FC5] rounded-full border-t-transparent animate-spin"></span>
      {/if}
    </span>
  </div>

  {#if error}
    <div class="text-red-400 text-sm mb-4 p-3 bg-red-950/40 rounded-xl border border-red-500/30">
      {error}
    </div>
  {/if}

  <!-- Token Metrics -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
    <div class="p-4 rounded-xl bg-white/[0.03]">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Price</p>
      <p class="agent-metric-value-md">
        {#if loading || tokenPrice === null}
          <span class="agent-metric-pulse w-[7ch]" aria-hidden="true"></span>
        {:else}
          <span class="min-w-[7ch] tabular-nums">${tokenPrice.toFixed(4)}</span>
        {/if}
      </p>
      <p class="agent-metric-hint {priceChange24h && priceChange24h !== '0' ? getPriceChangeColor(priceChange24h) : ''}">
        {#if !loading && priceChange24h && priceChange24h !== "0"}
          {formatPriceChange(priceChange24h)} (24h)
        {:else}
          &nbsp;
        {/if}
      </p>
    </div>
    
    <div class="p-4 rounded-xl bg-white/[0.03]">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Market cap</p>
      <p class="agent-metric-value-md">
        {#if loading || marketCap === null}
          <span class="agent-metric-pulse w-[8ch]" aria-hidden="true"></span>
        {:else}
          <span class="min-w-[8ch] tabular-nums">${formatLargeNumber(parseFloat(marketCap))}</span>
        {/if}
      </p>
      <p class="agent-metric-hint">&nbsp;</p>
    </div>
  </div>

  <!-- User Balance (if authenticated) -->
  {#if isAuthenticated}
    <div class="rounded-xl bg-white/[0.03] p-4 mb-5">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Your balance</p>
          <p class="agent-metric-value-md">
            {#if isLoadingUserBalance}
              <span class="agent-metric-pulse w-[10ch]" aria-hidden="true"></span>
            {:else}
              <span class="min-w-[10ch] truncate">
                {userBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 8 })}
              </span>
            {/if}
            <span class="agent-metric-unit">FUNNAI</span>
            {#if !isLoadingUserBalance && isWhale()}
              <span class="text-xl leading-none" title="Whale Alert! You hold {getUserSupplyPercentage()}% of total supply">🐋</span>
            {/if}
          </p>
          <p class="mt-1 text-lg font-semibold leading-7 min-h-7 {dataLoadedSuccessfully && tokenPrice !== null ? 'text-emerald-400' : 'text-gray-500'}">
            {#if isLoadingUserBalance}
              <span class="agent-metric-pulse w-[8ch]" aria-hidden="true"></span>
            {:else if dataLoadedSuccessfully && tokenPrice !== null}
              ${(userBalance * tokenPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD
            {:else}
              USD value unavailable
            {/if}
          </p>
          <p class="agent-metric-hint">
            {#if !isLoadingUserBalance && totalSupply && userBalance > 0}
              {getUserSupplyPercentage()}% of current supply
            {:else}
              &nbsp;
            {/if}
          </p>
        </div>

      </div>
    </div>
  {/if}

  <!-- Data Source Info -->
  <div class="text-xs text-gray-500 text-center mt-4 min-h-4 truncate">
    {#if loading}
      Loading token data...
    {:else if !dataLoadedSuccessfully}
      Data unavailable • Please check your connection and try again
    {:else if icpswapData}
      Data from ICPSwap • Last updated: {new Date(icpswapData.lastUpdated).toLocaleTimeString()}
    {:else}
      Using local data • Limited real-time information
    {/if}
  </div>
</div> 