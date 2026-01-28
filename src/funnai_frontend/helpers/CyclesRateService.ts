import { createAnonymousActorHelper } from "./utils/actorUtils";
import { canisterIDLs } from "../stores/store";

/**
 * Service for fetching and caching cycles-to-USD conversion rates
 * 
 * Conversion logic:
 * - 1 XDR (Special Drawing Rights) = 1 trillion cycles (fixed on IC)
 * - XDR to USD rate fluctuates slightly (~$1.30-$1.40 range)
 * - We fetch ICP/XDR rate from CMC and use a known XDR/USD rate
 */
export class CyclesRateService {
  private static cachedRate: number | null = null;
  private static cacheTimestamp: number = 0;
  private static readonly CACHE_DURATION = 30 * 60 * 1000; // 30 minutes
  
  // CMC canister ID (Cycles Minting Canister)
  private static readonly CMC_CANISTER_ID = "rkp4c-7iaaa-aaaaa-aaaca-cai";
  
  // XDR to USD conversion rate (IMF SDR basket - relatively stable)
  // This can be updated periodically or fetched from an external API
  private static readonly XDR_TO_USD = 1.33;
  
  // Fallback rate if CMC call fails
  private static readonly FALLBACK_RATE = 1.37;

  /**
   * Check if cache is valid
   */
  private static isCacheValid(): boolean {
    if (!this.cachedRate || !this.cacheTimestamp) return false;
    return Date.now() - this.cacheTimestamp < this.CACHE_DURATION;
  }

  /**
   * Get the USD value per trillion cycles
   * Returns the conversion rate (e.g., 1.37 means 1 trillion cycles = $1.37 USD)
   */
  static async getCyclesToUsdRate(): Promise<number> {
    // Return cached value if valid
    if (this.isCacheValid() && this.cachedRate !== null) {
      return this.cachedRate;
    }

    try {
      // Create CMC actor
      const cmcActor = await createAnonymousActorHelper(
        this.CMC_CANISTER_ID, 
        canisterIDLs.cmc
      );
      
      // Get ICP/XDR conversion rate
      const response = await cmcActor.get_icp_xdr_conversion_rate();
      
      if (response && response.data) {
        // 1 trillion cycles = 1 XDR (fixed on IC)
        // USD per trillion cycles = XDR_TO_USD rate
        const rate = this.XDR_TO_USD;
        
        // Cache the result
        this.cachedRate = rate;
        this.cacheTimestamp = Date.now();
        
        return rate;
      }
      
      throw new Error("Invalid response from CMC");
    } catch (error) {
      // Return fallback rate if CMC call fails
      return this.FALLBACK_RATE;
    }
  }

  /**
   * Convert cycles (in trillions) to USD
   */
  static async convertCyclesToUsd(cyclesInTrillions: number): Promise<number> {
    const rate = await this.getCyclesToUsdRate();
    return cyclesInTrillions * rate;
  }

  /**
   * Clear the cache (useful for manual refresh)
   */
  static clearCache(): void {
    this.cachedRate = null;
    this.cacheTimestamp = 0;
  }

  /**
   * Get the current cached rate without fetching (returns null if not cached)
   */
  static getCachedRate(): number | null {
    if (this.isCacheValid()) {
      return this.cachedRate;
    }
    return null;
  }
}
