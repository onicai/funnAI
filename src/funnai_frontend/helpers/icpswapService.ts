// ICPSwap API Service for fetching real-time token data
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

      // Try different possible API endpoints - prioritize the working one first
      const endpoints = [
        `/info/token/${tokenId}`, // This one works!
        `/token/data?canisterId=${tokenId}`,
        `/token/data?id=${tokenId}`,
        `/token/data?token=${tokenId}`,
        `/token/${tokenId}/data`,
        `/tokens/${tokenId}`,
        `/v1/token/data?canisterId=${tokenId}`,
        `/api/token/data?canisterId=${tokenId}`
      ];

      let tokenData: ICPSwapTokenData | null = null;

      // Try each endpoint until one works
      for (const endpoint of endpoints) {
        try {
          const url = `${this.BASE_URL}${endpoint}`;
          console.log(`Trying ICPSwap endpoint: ${url}`);
          
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            // Add timeout
            signal: this.createTimeoutSignal(10000) // 10 second timeout
          });

          console.log(`Response status for ${endpoint}:`, response.status);

          if (response.ok) {
            const data = await response.json();
            console.log(`Response data for ${endpoint}:`, data);
            
            // Check if we got valid data (not a 404 message)
            if (data && data.code !== 404 && data.message !== "Token not found") {
              tokenData = this.parseTokenData(data);
              if (tokenData) {
                console.log(`Successfully parsed data from ${endpoint}`);
                break; // Found valid data, stop trying other endpoints
              }
            }
          }
        } catch (endpointError) {
          console.log(`Endpoint ${endpoint} failed:`, endpointError);
          continue; // Try next endpoint
        }
      }

      // If no API endpoint worked, try alternative approaches
      if (!tokenData) {
        console.log("All API endpoints failed, trying alternative methods...");
        tokenData = await this.fetchAlternativeTokenData(tokenId);
      }

      if (tokenData) {
        // Cache the successful result
        this.cache.set(tokenId, {
          data: tokenData,
          timestamp: Date.now()
        });
        console.log("ICPSwap data successfully cached");
        return tokenData;
      }

      console.warn("No valid token data could be retrieved from ICPSwap");
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
   * Alternative method to fetch token data using different approaches
   * @param tokenId The canister ID of the token
   * @returns Promise with token data or null
   */
  private static async fetchAlternativeTokenData(tokenId: string): Promise<ICPSwapTokenData | null> {
    try {
      console.log("Trying alternative data fetching methods...");
      
      // Try different ICPSwap subdomains or paths
      const alternativeUrls = [
        `https://info.icpswap.com/api/token/${tokenId}`,
        `https://icpswap.com/api/token/data?canisterId=${tokenId}`,
        `https://api.icpswap.com/public/token/${tokenId}`,
        `https://api.icpswap.com/v2/token/data?id=${tokenId}`
      ];

      for (const url of alternativeUrls) {
        try {
          console.log(`Trying alternative URL: ${url}`);
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            signal: this.createTimeoutSignal(10000)
          });

          if (response.ok) {
            const data = await response.json();
            if (data && data.code !== 404) {
              const tokenData = this.parseTokenData(data);
              if (tokenData) {
                console.log(`Successfully got data from alternative URL: ${url}`);
                return tokenData;
              }
            }
          }
        } catch (error) {
          console.log(`Alternative URL ${url} failed:`, error);
          continue;
        }
      }

      // Try fetching from ICPSwap's public info page endpoint
      console.log("Trying to fetch from ICPSwap info page...");
      const infoResponse = await fetch(`https://app.icpswap.com/info-tokens/details/${tokenId}`, {
        method: 'GET',
        headers: {
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent': 'Mozilla/5.0 (compatible; TokenDataFetcher/1.0)'
        },
        signal: this.createTimeoutSignal(10000)
      });

      if (infoResponse.ok) {
        const html = await infoResponse.text();
        console.log("Got HTML response from info page");
        
        // Try to extract JSON data from the page if it contains structured data
        const jsonMatch = html.match(/<script[^>]*type=["']application\/ld\+json["'][^>]*>(.*?)<\/script>/s);
        if (jsonMatch) {
          try {
            const jsonData = JSON.parse(jsonMatch[1]);
            return this.parseTokenData(jsonData);
          } catch (e) {
            console.log('No JSON-LD data found in page');
          }
        }

        // Try to extract data from window.__INITIAL_STATE__ or similar
        const stateMatch = html.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});/s) ||
                          html.match(/window\.__DATA__\s*=\s*({.*?});/s) ||
                          html.match(/"tokenData"\s*:\s*({.*?})/s);
        
        if (stateMatch) {
          try {
            const stateData = JSON.parse(stateMatch[1]);
            return this.parseTokenData(stateData);
          } catch (e) {
            console.log('Could not parse state data from page');
          }
        }
      }

      return null;
    } catch (error) {
      console.error('Error fetching alternative token data:', error);
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
}

export default ICPSwapService; 