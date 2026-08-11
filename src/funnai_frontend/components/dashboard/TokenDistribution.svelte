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

  async function updateTokenData() {
    loading = true;
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

  onMount(async () => {
    await updateTokenData();
    
    // Update token data every 2 minutes (ICPSwap data is cached for 1 minute)
    updateInterval = setInterval(updateTokenData, 120000);
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
    }
  });

  // React to authentication changes
  $: if (isAuthenticated !== undefined) {
    updateTokenData();
  }

  // React to wallet data changes to update user balance
  $: if (walletData) {
    updateUserBalance();
  }
</script>

<div class="agent-card p-6">
  <div class="flex items-center justify-between mb-4">
    <div>
      <p class="agent-eyebrow">Token</p>
      <h3 class="text-lg font-semibold tracking-tight text-white">
        {title}
      </h3>
    </div>
    <div class="flex items-center gap-2">
      {#if loading || (isAuthenticated && isLoadingUserBalance)}
        <div class="animate-spin h-4 w-4 border-2 border-agent-purple rounded-full border-t-transparent"></div>
      {/if}
      <span class="text-xs text-gray-400 px-2 py-1 bg-white/[0.03] border border-white/10 rounded-lg">
        $FUNNAI
      </span>
      {#if icpswapData}
        <span class="text-xs text-emerald-400 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
          Live
        </span>
      {/if}
    </div>
  </div>

  {#if error}
    <div class="text-red-400 text-sm mb-4 p-3 bg-red-950/40 rounded-xl border border-red-500/30">
      {error}
    </div>
  {/if}

  <!-- Token Metrics -->
  {#if loading}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="text-center p-4 bg-white/[0.03] border border-white/10 rounded-xl">
        <div class="text-lg font-semibold tracking-tight text-white">
          <div class="animate-pulse flex justify-center">
            <div class="h-6 bg-white/[0.06] rounded w-20"></div>
          </div>
        </div>
        <div class="text-sm text-gray-400">Price</div>
      </div>
      
      <div class="text-center p-4 bg-white/[0.03] border border-white/10 rounded-xl">
        <div class="text-lg font-semibold tracking-tight text-white">
          <div class="animate-pulse flex justify-center">
            <div class="h-6 bg-white/[0.06] rounded w-24"></div>
          </div>
        </div>
        <div class="text-sm text-gray-400">Market Cap</div>
      </div>
    </div>
  {:else if dataLoadedSuccessfully && tokenPrice !== null && marketCap !== null}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="text-center p-4 bg-white/[0.03] border border-white/10 rounded-xl">
        <div class="text-lg font-semibold tracking-tight text-white">
          ${tokenPrice.toFixed(4)}
        </div>
        <div class="text-sm text-gray-400">Price</div>
        {#if priceChange24h && priceChange24h !== "0"}
          <div class="text-xs {getPriceChangeColor(priceChange24h)} mt-1">
            {formatPriceChange(priceChange24h)} (24h)
          </div>
        {/if}
      </div>
      
      <div class="text-center p-4 bg-white/[0.03] border border-white/10 rounded-xl">
        <div class="text-lg font-semibold tracking-tight text-white">
          ${formatLargeNumber(parseFloat(marketCap))}
        </div>
        <div class="text-sm text-gray-400">Market Cap</div>
      </div>
    </div>
  {/if}

  <!-- User Balance (if authenticated) -->
  {#if isAuthenticated}
    <div class="bg-white/[0.03] border border-white/10 rounded-xl p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="text-sm text-gray-400">Your balance</div>
          {#if isLoadingUserBalance}
            <div class="text-xl font-semibold tracking-tight text-white">
              <div class="animate-pulse flex items-center">
                <div class="h-6 bg-white/[0.06] rounded w-32"></div>
              </div>
            </div>
            <div class="text-lg font-semibold text-gray-400 mt-1">
              <div class="animate-pulse flex items-center">
                <div class="h-5 bg-white/[0.06] rounded w-24"></div>
              </div>
            </div>
          {:else}
            <div class="text-xl font-semibold tracking-tight text-white flex items-center gap-2">
              {userBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 8 })} FUNNAI
              {#if isWhale()}
                <span class="text-2xl" title="Whale Alert! You hold {getUserSupplyPercentage()}% of total supply">🐋</span>
              {/if}
            </div>
            {#if dataLoadedSuccessfully && tokenPrice !== null}
              <div class="text-lg font-semibold text-emerald-400 mt-1">
                ${(userBalance * tokenPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD
              </div>
            {:else}
              <div class="text-sm text-gray-400 mt-1">
                USD value unavailable
              </div>
            {/if}
            {#if totalSupply && userBalance > 0}
              <div class="text-xs text-gray-500 mt-1">
                {getUserSupplyPercentage()}% of current supply
              </div>
            {/if}
          {/if}
        </div>

      </div>
    </div>
  {/if}

  <!-- Data Source Info -->
  <div class="text-xs text-gray-500 text-center mt-4">
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