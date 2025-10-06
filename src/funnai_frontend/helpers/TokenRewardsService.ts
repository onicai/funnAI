import { store } from "../stores/store";
import { get } from "svelte/store";

export interface TokenRewardsMetadata {
  dataset: string;
  description: string;
  last_updated: string;
  version: string;
  units: {
    total_minted: string;
    rewards_per_challenge: string;
  };
}

export interface TokenRewardsEntry {
  date: string;
  quarter: string;
  total_minted: number;
  rewards_per_challenge: number;
  rewards_per_quarter: number;
  notes: string;
}

export interface TokenRewardsData {
  metadata: TokenRewardsMetadata;
  data: TokenRewardsEntry[];
}

export class TokenRewardsService {
  private static cache: TokenRewardsData | null = null;
  private static cacheTimestamp: number = 0;
  private static readonly CACHE_DURATION = 60 * 60 * 1000; // 1 hour - token rewards data changes infrequently

  /**
   * Check if cache is valid
   */
  private static isCacheValid(): boolean {
    if (!this.cacheTimestamp) return false;
    return Date.now() - this.cacheTimestamp < this.CACHE_DURATION;
  }

  /**
   * Fetch token rewards data from canister
   */
  static async fetchTokenRewardsData(): Promise<TokenRewardsData> {
    // Check cache first
    if (this.isCacheValid() && this.cache) {
      console.log("Returning cached token rewards data");
      return this.cache;
    }

    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      console.log("Fetching token rewards data from canister");
      
      const result = await storeValue.apiCanisterActor.getTokenRewardsData();
      
      if ("Ok" in result) {
        const response = result.Ok;
        
        // Transform the data to match our interface
        const transformedData: TokenRewardsData = {
          metadata: {
            dataset: response.metadata.dataset,
            description: response.metadata.description,
            last_updated: response.metadata.last_updated,
            version: response.metadata.version,
            units: {
              total_minted: response.metadata.units.total_minted,
              rewards_per_challenge: response.metadata.units.rewards_per_challenge
            }
          },
          data: response.data.map((entry: any) => ({
            date: entry.date,
            quarter: entry.quarter,
            total_minted: Number(entry.total_minted),
            rewards_per_challenge: Number(entry.rewards_per_challenge),
            rewards_per_quarter: Number(entry.rewards_per_quarter),
            notes: entry.notes
          }))
        };

        // Cache the result
        this.cache = transformedData;
        this.cacheTimestamp = Date.now();
        
        console.log(`Fetched ${transformedData.data.length} token rewards entries`);
        return transformedData;
      } else {
        console.error("Error fetching token rewards data:", result.Err);
        throw new Error(JSON.stringify(result.Err) || "Failed to fetch token rewards data");
      }
    } catch (error) {
      console.error("Error in fetchTokenRewardsData:", error);
      throw error;
    }
  }

  /**
   * Clear cache (useful for manual refresh)
   */
  static clearCache(): void {
    this.cache = null;
    this.cacheTimestamp = 0;
  }
}

