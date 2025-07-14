<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { store } from "../../stores/store";
  import { formatFunnaiAmount, formatLargeNumber } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens } from "../../helpers/token_helpers";
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
  let totalSupply = "210,992"; // Default fallback value (same as Dashboard.svelte)
  let circulatingSupply = "0";
  let protocolBalance = "0";
  let burnedTokens = "0";
  let tokenPrice = 0.45;
  let marketCap = "1177191.2";
  let priceChange24h = "0";
  let isLoadingSupply = false;
  let supplyError = "";

  // User data
  let userBalance = 0;
  let funnaiToken: FE.Token | null = null;
  let icpswapData: ICPSwapTokenData | null = null;
  let isLoadingUserBalance = false;

  // Subscribe to wallet data store
  let walletData;
  walletDataStore.subscribe((value) => walletData = value);

  $: isAuthenticated = $store.isAuthed;

  // FUNNAI token canister ID from token_helpers.ts
  const FUNNAI_CANISTER_ID = "vpyot-zqaaa-aaaaa-qavaq-cai";

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
      // Get FUNNAI token info from local source first
      const tokensResult = await fetchTokens({});
      const foundFunnaiToken = tokensResult.tokens.find(token => token.symbol === "FUNNAI");
      
      if (foundFunnaiToken) {
        funnaiToken = foundFunnaiToken;
        
        // Fetch real total supply from canister (same as Dashboard.svelte)
        try {
          isLoadingSupply = true;
          supplyError = "";
          
          const totalSupplyBigInt = await IcrcService.getIcrc1TotalSupply(foundFunnaiToken);
          totalSupply = formatTotalSupply(totalSupplyBigInt, foundFunnaiToken.decimals);
          
        } catch (supplyErr) {
          console.error("Error loading total supply:", supplyErr);
          supplyError = supplyErr.message || "Failed to load supply";
          // Keep the fallback value "210,992"
        } finally {
          isLoadingSupply = false;
        }
        
        // Get price from local data as fallback
        const apiPrice = foundFunnaiToken.metrics?.price;
        if (apiPrice && parseFloat(apiPrice) > 0) {
          tokenPrice = parseFloat(apiPrice);
        }
      }

      // Try to fetch real-time data from ICPSwap
      await loadICPSwapData();

      // If we still don't have good price data, use fallback
      if (tokenPrice <= 0) {
        tokenPrice = 0.45;
      }

      // Always calculate market cap using real total supply × current price
      const totalSupplyNum = parseFloat(totalSupply.replace(/,/g, ''));
      marketCap = (totalSupplyNum * tokenPrice).toFixed(2);

      // Get user balance if authenticated
      if (isAuthenticated && $store.principal) {
        updateUserBalance();
      }

      // Calculate realistic distribution values
      circulatingSupply = (totalSupplyNum * 0.75).toLocaleString();
      protocolBalance = (totalSupplyNum * 0.20).toLocaleString();
      burnedTokens = (totalSupplyNum * 0.05).toLocaleString();

    } catch (err) {
      console.error("Error loading token data:", err);
      error = "Failed to load token distribution data";
      
      // Set fallback values on error
      totalSupply = "210,992";
      tokenPrice = 0.45;
      const totalSupplyNum = parseFloat(totalSupply.replace(/,/g, ''));
      marketCap = (totalSupplyNum * tokenPrice).toFixed(2);
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
    if (isNaN(num)) return "text-gray-600 dark:text-gray-400";
    if (num > 0) return "text-green-600 dark:text-green-400";
    if (num < 0) return "text-red-600 dark:text-red-400";
    return "text-gray-600 dark:text-gray-400";
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

<div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
      {title}
    </h3>
    <div class="flex items-center gap-2">
      {#if loading || (isAuthenticated && isLoadingUserBalance)}
        <div class="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
      {/if}
      <span class="text-xs text-gray-500 dark:text-gray-400 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
        $FUNNAI
      </span>
      {#if icpswapData}
        <span class="text-xs text-green-600 dark:text-green-400 px-2 py-1 bg-green-50 dark:bg-green-900/20 rounded">
          Live
        </span>
      {/if}
    </div>
  </div>

  {#if error}
    <div class="text-red-600 dark:text-red-400 text-sm mb-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
      {error}
    </div>
  {/if}

  <!-- Token Metrics -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
    
    <div class="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
      <div class="text-lg font-bold text-purple-600 dark:text-purple-400">
        ${tokenPrice.toFixed(4)}
      </div>
      <div class="text-sm text-gray-600 dark:text-gray-400">Price</div>
      {#if priceChange24h && priceChange24h !== "0"}
        <div class="text-xs {getPriceChangeColor(priceChange24h)} mt-1">
          {formatPriceChange(priceChange24h)} (24h)
        </div>
      {/if}
    </div>
    
    <div class="text-center p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
      <div class="text-lg font-bold text-orange-600 dark:text-orange-400">
        ${formatLargeNumber(parseFloat(marketCap))}
      </div>
      <div class="text-sm text-gray-600 dark:text-gray-400">Market Cap</div>
    </div>
  </div>

  <!-- User Balance (if authenticated) -->
  {#if isAuthenticated}
    <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 mb-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <div class="text-sm text-gray-600 dark:text-gray-400">Your balance</div>
          {#if isLoadingUserBalance}
            <div class="text-xl font-bold text-gray-900 dark:text-white">
              <div class="animate-pulse flex items-center">
                <div class="h-6 bg-gray-300 dark:bg-gray-600 rounded w-32"></div>
              </div>
            </div>
            <div class="text-lg font-semibold text-gray-600 dark:text-gray-400 mt-1">
              <div class="animate-pulse flex items-center">
                <div class="h-5 bg-gray-300 dark:bg-gray-600 rounded w-24"></div>
              </div>
            </div>
          {:else}
            <div class="text-xl font-bold text-gray-900 dark:text-white">
              {userBalance.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 8 })} FUNNAI
            </div>
            <div class="text-lg font-semibold text-green-600 dark:text-green-400 mt-1">
              ${(userBalance * tokenPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD
            </div>
          {/if}
        </div>

      </div>
    </div>
  {/if}

  <!-- Data Source Info -->
  <div class="text-xs text-gray-500 dark:text-gray-400 text-center mt-4">
    {#if icpswapData}
      Data from ICPSwap • Last updated: {new Date(icpswapData.lastUpdated).toLocaleTimeString()}
    {:else}
      Using fallback data • Consider checking your connection
    {/if}
  </div>

</div> 