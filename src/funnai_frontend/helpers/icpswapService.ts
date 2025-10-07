// ICPSwap API Service for fetching real-time token data
import {
  store,
  canisterIds,
  canisterIDLs
} from "../stores/store";

import { IcrcService } from "./IcrcService";

let storeState;
store.subscribe((value) => storeState = value);

export interface ICPSwapTokenData {
  price: string;
  priceUSD: number;
  volume24h: string;
  volumeUSD24h: number;
  marketCap: string;
  marketCapUSD: number;
  totalSupply: string;
  priceChange24h: string;
  lastUpdated: number;
}

export interface ICPSwapApiResponse {
  success: boolean;
  data?: ICPSwapTokenData;
  error?: string;
}

export interface SwapArgs {
  amountIn: string;
  zeroForOne: boolean;
  amountOutMinimum: string;
}

export interface DepositAndSwapArgs {
  tokenInFee: bigint;
  amountIn: string;
  zeroForOne: boolean;
  amountOutMinimum: string;
  tokenOutFee: bigint;
}

class ICPSwapService {
  private static readonly BASE_URL = 'https://api.icpswap.com';
  private static readonly CACHE_DURATION = 60 * 1000; // 1 minute cache
  private static cache = new Map<string, { data: ICPSwapTokenData; timestamp: number }>();

  /**
   * Create a timeout signal for fetch requests (fallback for older browsers)
   * @param timeout Timeout in milliseconds
   * @returns AbortSignal
   */
  private static createTimeoutSignal(timeout: number): AbortSignal {
    // Use AbortSignal.timeout if available (modern browsers)
    if (typeof AbortSignal !== 'undefined' && 'timeout' in AbortSignal) {
      return (AbortSignal as any).timeout(timeout);
    }
    
    // Fallback for older browsers
    const controller = new AbortController();
    setTimeout(() => controller.abort(), timeout);
    return controller.signal;
  }

  /**
   * Fetch token data from ICPSwap API
   * @param tokenId The canister ID of the token
   * @returns Promise with token data or null if failed
   */
  public static async fetchTokenData(tokenId: string): Promise<ICPSwapTokenData | null> {
    try {
      // Check cache first
      const cached = this.cache.get(tokenId);
      if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
        console.log(`Using cached ICPSwap data for ${tokenId}`);
        return cached.data;
      }

      console.log(`Fetching fresh ICPSwap data for ${tokenId}`);

      // Use the only working endpoint
      const endpoint = `/info/token/${tokenId}`;
      const url = `${this.BASE_URL}${endpoint}`;
      
      console.log(`Fetching from ICPSwap: ${url}`);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: this.createTimeoutSignal(10000) // 10 second timeout
      });

      console.log(`Response status:`, response.status);

      if (!response.ok) {
        console.warn(`ICPSwap API returned status ${response.status}`);
        return null;
      }

      const data = await response.json();
      console.log(`Response data:`, data);
      
      // Check if we got valid data (not a 404 message)
      if (!data || data.code === 404 || data.message === "Token not found") {
        console.warn("Token not found or invalid response from ICPSwap");
        return null;
      }

      const tokenData = this.parseTokenData(data);
      
      if (tokenData) {
        // Cache the successful result
        this.cache.set(tokenId, {
          data: tokenData,
          timestamp: Date.now()
        });
        console.log("ICPSwap data successfully cached");
        return tokenData;
      }

      console.warn("Could not parse valid token data from ICPSwap response");
      return null;

    } catch (error) {
      console.error('Error fetching ICPSwap token data:', error);
      return null;
    }
  }

  /**
   * Parse API response into our token data format
   * @param data Raw API response
   * @returns Parsed token data or null
   */
  private static parseTokenData(data: any): ICPSwapTokenData | null {
    try {
      console.log("Parsing token data:", data);
      
      // Handle different possible response formats
      const tokenInfo = data.data || data.token || data.result || data;

      if (!tokenInfo) {
        console.log("No token info found in response");
        return null;
      }

      console.log("Token info structure:", tokenInfo);
      console.log("Available fields:", Object.keys(tokenInfo));

      // ICPSwap specific field mappings based on actual API response
      const price = tokenInfo.price || "0";
      
      const volume24h = tokenInfo.volumeUSD24H || 
                       tokenInfo.totalVolumeUSD || 
                       "0";
      
      const marketCap = tokenInfo.tvlUSD || 
                       tokenInfo.marketCap || 
                       // Calculate from supply and price if available
                       (tokenInfo.totalSupply && price ? 
                         (parseFloat(tokenInfo.totalSupply) * parseFloat(price)).toString() : "0");
      
      const totalSupply = tokenInfo.totalSupply || 
                         tokenInfo.supply || 
                         "0";
      
      const priceChange24h = tokenInfo.priceChange24H || "0";

      // Log individual field extractions for debugging
      console.log("Extracted fields:", {
        price,
        volume24h,
        marketCap,
        totalSupply,
        priceChange24h
      });

      const parsed = {
        price: price.toString(),
        priceUSD: parseFloat(price.toString()) || 0,
        volume24h: volume24h.toString(),
        volumeUSD24h: parseFloat(volume24h.toString()) || 0,
        marketCap: marketCap.toString(),
        marketCapUSD: parseFloat(marketCap.toString()) || 0,
        totalSupply: totalSupply.toString(),
        priceChange24h: priceChange24h.toString(),
        lastUpdated: Date.now()
      };

      console.log("Final parsed token data:", parsed);
      return parsed;
    } catch (error) {
      console.error('Error parsing ICPSwap token data:', error);
      return null;
    }
  }

  /**
   * Get cached token data if available
   * @param tokenId The canister ID of the token
   * @returns Cached token data or null
   */
  public static getCachedTokenData(tokenId: string): ICPSwapTokenData | null {
    const cached = this.cache.get(tokenId);
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data;
    }
    return null;
  }

  /**
   * Clear cache for a specific token or all tokens
   * @param tokenId Optional token ID to clear, if not provided clears all
   */
  public static clearCache(tokenId?: string): void {
    if (tokenId) {
      this.cache.delete(tokenId);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Batch fetch multiple tokens (with rate limiting)
   * @param tokenIds Array of canister IDs
   * @returns Promise with map of tokenId to token data
   */
  public static async batchFetchTokenData(tokenIds: string[]): Promise<Map<string, ICPSwapTokenData>> {
    const results = new Map<string, ICPSwapTokenData>();
    const BATCH_SIZE = 3; // Limit concurrent requests
    const DELAY_BETWEEN_BATCHES = 500; // 500ms delay between batches

    for (let i = 0; i < tokenIds.length; i += BATCH_SIZE) {
      const batch = tokenIds.slice(i, i + BATCH_SIZE);
      
      const batchPromises = batch.map(async (tokenId) => {
        const data = await this.fetchTokenData(tokenId);
        if (data) {
          results.set(tokenId, data);
        }
        return { tokenId, data };
      });

      await Promise.all(batchPromises);

      // Add delay between batches to avoid rate limiting
      if (i + BATCH_SIZE < tokenIds.length) {
        await new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_BATCHES));
      }
    }

    return results;
  }

  /**
   * Get a quote from an ICPSwap pool canister by calling its `quote` method.
   * @param poolCanisterId The canister ID of the swap pool
   * @param args The swap arguments
   * @returns The quote result or null if failed
   */
  public static async getQuoteFromPool(
    poolCanisterId: string,
    args: SwapArgs
  ): Promise<any | null> {
    try {
      const poolActor = await store.getActor(
        poolCanisterId,
        canisterIDLs.swapPool,
        {
          anon: false,
          requiresSigning: true,
        },
      );

      // Call the quote method
      console.log("in getQuoteFromPool args ", args);
      const result = await poolActor.quote(args);
      console.log("in getQuoteFromPool result ", result);

      return result;
    } catch (error) {
      console.error("Error fetching quote from ICPSwap pool:", error);
      return null;
    }
  }

  /**
   * Get a quote from an ICPSwap pool with automatic direction detection based on input token.
   * This method determines the correct zeroForOne value based on pool metadata.
   * @param poolCanisterId The canister ID of the swap pool
   * @param inputTokenCanisterId The canister ID of the input token
   * @param amountIn The amount of input tokens
   * @returns The quote result or null if failed
   */
  public static async getQuoteWithAutoDirection(
    poolCanisterId: string,
    inputTokenCanisterId: string,
    amountIn: string
  ): Promise<any | null> {
    try {
      const poolActor = await store.getActor(
        poolCanisterId,
        canisterIDLs.swapPool,
        {
          anon: false,
          requiresSigning: true,
        },
      );

      // Get pool metadata to determine token order
      const metadata = await poolActor.metadata();
      console.log("Pool metadata for quote:", metadata);
      
      if (!metadata || typeof metadata !== 'object' || !('ok' in metadata)) {
        console.error("Failed to get pool metadata for quote");
        return null;
      }

      const metadataOk: any = metadata.ok;
      const token0Address = metadataOk.token0?.address;
      const token1Address = metadataOk.token1?.address;
      
      if (!token0Address || !token1Address) {
        console.error("Invalid pool metadata - missing token addresses");
        return null;
      }

      // Determine if input token is token0 or token1
      const isToken0 = inputTokenCanisterId === token0Address;
      const zeroForOne = isToken0;
      
      console.log("Quote - Input token is:", isToken0 ? "token0" : "token1");
      console.log("Quote - Swap direction (zeroForOne):", zeroForOne);

      const args: SwapArgs = {
        amountIn: amountIn,
        zeroForOne: zeroForOne,
        amountOutMinimum: "0"
      };

      console.log("Quote args:", args);
      const result = await poolActor.quote(args);
      console.log("Quote result:", result);

      return result;
    } catch (error) {
      console.error("Error fetching quote with auto direction:", error);
      return null;
    }
  }

  public static async approveAndSwap(
    token: FE.Token,
    poolCanisterId: string,
    depositAndSwapArgs: DepositAndSwapArgs,
    spender: string = poolCanisterId
  ): Promise<any | null> {
    try {
      // 1. Create the pool actor first to check metadata
      const poolActor = await store.getActor(
        poolCanisterId,
        canisterIDLs.swapPool,
        {
          anon: false,
          requiresSigning: true,
        },
      );

      // Check pool metadata to understand token order - CRITICAL for correct swap direction
      let metadata;
      let isToken0: boolean = true; // Assume token is token0 by default
      let outputTokenAddress = "ryjl3-tyaaa-aaaaa-aaaba-cai"; // Default to ICP
      
      try {
        metadata = await poolActor.metadata();
        console.log("Pool metadata:", metadata);
        
        if (metadata && 'ok' in metadata) {
          const metadataOk: any = metadata.ok;
          console.log("Token0:", metadataOk.token0);
          console.log("Token1:", metadataOk.token1);
          
          // Determine if our input token is token0 or token1
          const token0Address = metadataOk.token0?.address;
          const token1Address = metadataOk.token1?.address;
          
          if (token0Address && token1Address) {
            // Check which token we're swapping
            isToken0 = token.canister_id === token0Address;
            
            // Set output token address (opposite of input)
            outputTokenAddress = isToken0 ? token1Address : token0Address;
            
            console.log("Input token is:", isToken0 ? "token0" : "token1");
            console.log("Output token address:", outputTokenAddress);
          }
        }
      } catch (metaError) {
        console.warn("Could not fetch pool metadata:", metaError);
        throw new Error("Failed to fetch pool metadata - cannot determine token order");
      }

      // Determine swap direction based on which token we're swapping
      // zeroForOne = true means swapping token0 for token1
      // zeroForOne = false means swapping token1 for token0
      const zeroForOne = isToken0;
      console.log("Swap direction (zeroForOne):", zeroForOne);

      // 2. Approve the pool canister to spend the input token + fee
      // The pool needs to pull both the swap amount and the token fee
      const totalAmountNeeded = BigInt(depositAndSwapArgs.amountIn) + depositAndSwapArgs.tokenInFee;
      
      console.log("Approving amount:", {
        tokenCanisterId: token.canister_id,
        amountIn: depositAndSwapArgs.amountIn,
        tokenInFee: depositAndSwapArgs.tokenInFee.toString(),
        totalAmountNeeded: totalAmountNeeded.toString(),
        spender: spender
      });
      
      await IcrcService.checkAndRequestIcrc2Allowances(
        token,
        totalAmountNeeded,
        spender
      );

      // 3. Use depositFrom to pull tokens, then swap
      // depositFromAndSwap seems to have issues, so we'll do it in two steps
      console.log("Step 1: Depositing tokens via depositFrom");
      const depositArgs = {
        token: token.canister_id,
        amount: BigInt(depositAndSwapArgs.amountIn),
        fee: depositAndSwapArgs.tokenInFee
      };
      console.log("Deposit args:", depositArgs);
      
      const depositResult = await poolActor.depositFrom(depositArgs);
      console.log("Deposit result:", depositResult);
      
      if (!depositResult || (typeof depositResult === 'object' && 'err' in depositResult)) {
        console.error("Deposit failed:", depositResult);
        return depositResult;
      }

      // 4. Now swap the deposited tokens with the correct direction
      console.log("Step 2: Swapping deposited tokens");
      const swapArgs = {
        amountIn: depositAndSwapArgs.amountIn,
        zeroForOne: zeroForOne, // Use dynamically determined direction
        amountOutMinimum: depositAndSwapArgs.amountOutMinimum
      };
      console.log("Swap args:", swapArgs);
      
      const swapResult = await poolActor.swap(swapArgs);
      console.log("Swap result:", swapResult);
      
      if (!swapResult || (typeof swapResult === 'object' && 'err' in swapResult)) {
        console.error("Swap failed:", swapResult);
        return swapResult;
      }

      // 5. Withdraw the output tokens
      console.log("Step 3: Withdrawing output tokens");
      
      // The swap result should contain the amount of output tokens received
      const swapResultValue = (swapResult as any).ok;
      const outputAmount = typeof swapResultValue === 'bigint' 
        ? swapResultValue 
        : BigInt(swapResultValue || '0');
      
      console.log("Output amount from swap:", outputAmount.toString());
      
      const withdrawArgs = {
        token: outputTokenAddress,
        amount: outputAmount,
        fee: depositAndSwapArgs.tokenOutFee
      };
      console.log("Withdraw args:", withdrawArgs);
      
      const withdrawResult = await poolActor.withdraw(withdrawArgs);
      console.log("Withdraw result:", withdrawResult);

      return withdrawResult;
    } catch (error) {
      console.error("Error in approveAndSwap:", error);
      console.error("Error stack:", error.stack);
      // Return the error as an object so we can see it in the UI
      return { err: { InternalError: error.message || "Unknown error" } };
    }
  }
}

export default ICPSwapService; 