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

  public static async approveAndSwap(
    token: FE.Token,
    poolCanisterId: string,
    depositAndSwapArgs: DepositAndSwapArgs,
    spender: string = poolCanisterId
  ): Promise<any | null> {
    try {
      // 1. Approve the pool canister to spend the input token
      await IcrcService.checkAndRequestIcrc2Allowances(
        token,
        BigInt(depositAndSwapArgs.amountIn),
        spender
      );

      // 2. Create the pool actor
      const poolActor = await store.getActor(
        poolCanisterId,
        canisterIDLs.swapPool,
        {
          anon: false,
          requiresSigning: true,
        },
      );

      // 3. Call depositAndSwap on the pool
      const result = await poolActor.depositAndSwap(depositAndSwapArgs);

      return result;
    } catch (error) {
      console.error("Error in approveAndSwap:", error);
      return null;
    }
  }
}

export default ICPSwapService; 