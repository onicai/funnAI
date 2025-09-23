import { store } from "../stores/store";
import { get } from "svelte/store";

export interface DailyMetricsData {
  metadata: {
    updated_at: string;
    date: string;
    created_at: string;
  };
  mainers: {
    totals: {
      created: number;
      active: number;
      total_cycles: number;
      paused: number;
    };
    breakdown_by_tier: {
      active: {
        low: number;
        high: number;
        very_high: number;
        medium: number;
      };
      paused: {
        low: number;
        high: number;
        very_high: number;
        medium: number;
      };
    };
  };
  derived_metrics: {
    avg_cycles_per_mainer: number;
    paused_percentage: number;
    tier_distribution: {
      low: number;
      high: number;
      very_high: number;
      medium: number;
    };
    burn_rate_per_active_mainer: number;
    active_percentage: number;
  };
  system_metrics: {
    funnai_index: number;
    daily_burn_rate: {
      usd: number;
      cycles: number;
    };
  };
}

export interface DailyMetricsQuery {
  start_date?: string;
  end_date?: string;
  limit?: number;
}

export type TimeFilter = "7days" | "15days" | "1month" | "all";

export class DailyMetricsService {
  private static cache = new Map<string, DailyMetricsData[]>();
  private static latestMetricCache: DailyMetricsData | null = null;
  private static cacheTimestamps = new Map<string, number>();
  private static latestMetricTimestamp: number = 0;
  private static readonly CACHE_DURATION = 30 * 60 * 1000; // 30 minutes - shorter cache for fresher data
  private static readonly LATEST_CACHE_DURATION = 10 * 60 * 1000; // 10 minutes for latest metrics

  /**
   * Get date range for time filter
   */
  static getDateRange(filter: TimeFilter): { start_date?: string; end_date?: string } {
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0]; // YYYY-MM-DD format
    
    switch (filter) {
      case "7days": {
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        return {
          start_date: sevenDaysAgo.toISOString().split('T')[0],
          end_date: todayStr
        };
      }
      case "15days": {
        const fifteenDaysAgo = new Date(today);
        fifteenDaysAgo.setDate(fifteenDaysAgo.getDate() - 15);
        return {
          start_date: fifteenDaysAgo.toISOString().split('T')[0],
          end_date: todayStr
        };
      }
      case "1month": {
        const oneMonthAgo = new Date(today);
        oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
        return {
          start_date: oneMonthAgo.toISOString().split('T')[0],
          end_date: todayStr
        };
      }
      case "all":
      default:
        return {}; // No date filter for "all"
    }
  }

  /**
   * Check if cache is valid
   */
  private static isCacheValid(cacheKey: string): boolean {
    const timestamp = this.cacheTimestamps.get(cacheKey);
    if (!timestamp) return false;
    return Date.now() - timestamp < this.CACHE_DURATION;
  }

  /**
   * Generate cache key from query parameters
   */
  private static getCacheKey(query: DailyMetricsQuery): string {
    return JSON.stringify({
      start_date: query.start_date || null,
      end_date: query.end_date || null,
      limit: query.limit || null
    });
  }

  /**
   * Fetch daily metrics from canister
   */
  static async fetchDailyMetrics(query: DailyMetricsQuery = {}): Promise<DailyMetricsData[]> {
    const cacheKey = this.getCacheKey(query);
    
    // Check cache first
    if (this.isCacheValid(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (cached) {
        console.log("Returning cached daily metrics for", cacheKey);
        return cached;
      }
    }

    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      console.log("Fetching daily metrics with query:", query);
      
      // Prepare the query parameters
      const queryParam = {
        start_date: query.start_date ? [query.start_date] : [],
        end_date: query.end_date ? [query.end_date] : [],
        limit: query.limit ? [query.limit] : []
      };

      const result = await storeValue.apiCanisterActor.getDailyMetrics([queryParam]);
      
      if ("Ok" in result) {
        const response = result.Ok;
        const metrics = response.daily_metrics;
        
        // Transform the data to match our interface
        const transformedMetrics: DailyMetricsData[] = metrics.map((metric: any) => ({
          metadata: {
            updated_at: metric.metadata.updated_at.toString(),
            date: metric.metadata.date,
            created_at: metric.metadata.created_at.toString()
          },
          mainers: {
            totals: {
              created: Number(metric.mainers.totals.created),
              active: Number(metric.mainers.totals.active),
              total_cycles: Number(metric.mainers.totals.total_cycles),
              paused: Number(metric.mainers.totals.paused)
            },
            breakdown_by_tier: {
              active: {
                low: Number(metric.mainers.breakdown_by_tier.active.low),
                high: Number(metric.mainers.breakdown_by_tier.active.high),
                very_high: Number(metric.mainers.breakdown_by_tier.active.very_high),
                medium: Number(metric.mainers.breakdown_by_tier.active.medium)
              },
              paused: {
                low: Number(metric.mainers.breakdown_by_tier.paused.low),
                high: Number(metric.mainers.breakdown_by_tier.paused.high),
                very_high: Number(metric.mainers.breakdown_by_tier.paused.very_high),
                medium: Number(metric.mainers.breakdown_by_tier.paused.medium)
              }
            }
          },
          derived_metrics: {
            avg_cycles_per_mainer: Number(metric.derived_metrics.avg_cycles_per_mainer),
            paused_percentage: Number(metric.derived_metrics.paused_percentage),
            tier_distribution: {
              low: Number(metric.derived_metrics.tier_distribution.low),
              high: Number(metric.derived_metrics.tier_distribution.high),
              very_high: Number(metric.derived_metrics.tier_distribution.very_high),
              medium: Number(metric.derived_metrics.tier_distribution.medium)
            },
            burn_rate_per_active_mainer: Number(metric.derived_metrics.burn_rate_per_active_mainer),
            active_percentage: Number(metric.derived_metrics.active_percentage)
          },
          system_metrics: {
            funnai_index: Number(metric.system_metrics.funnai_index),
            daily_burn_rate: {
              usd: Number(metric.system_metrics.daily_burn_rate.usd),
              cycles: Number(metric.system_metrics.daily_burn_rate.cycles)
            }
          }
        }));

        // Cache the result
        this.cache.set(cacheKey, transformedMetrics);
        this.cacheTimestamps.set(cacheKey, Date.now());
        
        console.log(`Fetched ${transformedMetrics.length} daily metrics entries`);
        return transformedMetrics;
      } else {
        console.error("Error fetching daily metrics:", result.Err);
        throw new Error(result.Err || "Failed to fetch daily metrics");
      }
    } catch (error) {
      console.error("Error in fetchDailyMetrics:", error);
      throw error;
    }
  }

  /**
   * Fetch daily metrics with time filter
   */
  static async fetchDailyMetricsByFilter(filter: TimeFilter, limit?: number): Promise<DailyMetricsData[]> {
    const dateRange = this.getDateRange(filter);
    const query: DailyMetricsQuery = {
      ...dateRange,
      limit
    };
    return this.fetchDailyMetrics(query);
  }

  /**
   * Clear cache (useful for manual refresh)
   */
  static clearCache(): void {
    this.cache.clear();
    this.cacheTimestamps.clear();
    this.latestMetricCache = null;
    this.latestMetricTimestamp = 0;
  }

  /**
   * Check if latest metric cache is valid
   */
  private static isLatestCacheValid(): boolean {
    if (!this.latestMetricTimestamp) return false;
    return Date.now() - this.latestMetricTimestamp < this.LATEST_CACHE_DURATION;
  }

  /**
   * Get the most recent metrics entry using dedicated latest endpoint
   */
  static async getLatestMetrics(): Promise<DailyMetricsData | null> {
    // Check cache first
    if (this.isLatestCacheValid() && this.latestMetricCache) {
      console.log("Returning cached latest metric");
      return this.latestMetricCache;
    }

    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      console.log("Fetching latest daily metric using getLatestDailyMetric");
      
      const result = await storeValue.apiCanisterActor.getLatestDailyMetric();
      
      if ("Ok" in result) {
        const metric = result.Ok;
        
        // Transform the single metric to match our interface
        const transformedMetric: DailyMetricsData = {
          metadata: {
            updated_at: metric.metadata.updated_at.toString(),
            date: metric.metadata.date,
            created_at: metric.metadata.created_at.toString()
          },
          mainers: {
            totals: {
              created: Number(metric.mainers.totals.created),
              active: Number(metric.mainers.totals.active),
              total_cycles: Number(metric.mainers.totals.total_cycles),
              paused: Number(metric.mainers.totals.paused)
            },
            breakdown_by_tier: {
              active: {
                low: Number(metric.mainers.breakdown_by_tier.active.low),
                high: Number(metric.mainers.breakdown_by_tier.active.high),
                very_high: Number(metric.mainers.breakdown_by_tier.active.very_high),
                medium: Number(metric.mainers.breakdown_by_tier.active.medium)
              },
              paused: {
                low: Number(metric.mainers.breakdown_by_tier.paused.low),
                high: Number(metric.mainers.breakdown_by_tier.paused.high),
                very_high: Number(metric.mainers.breakdown_by_tier.paused.very_high),
                medium: Number(metric.mainers.breakdown_by_tier.paused.medium)
              }
            }
          },
          derived_metrics: {
            avg_cycles_per_mainer: Number(metric.derived_metrics.avg_cycles_per_mainer),
            paused_percentage: Number(metric.derived_metrics.paused_percentage),
            tier_distribution: {
              low: Number(metric.derived_metrics.tier_distribution.low),
              high: Number(metric.derived_metrics.tier_distribution.high),
              very_high: Number(metric.derived_metrics.tier_distribution.very_high),
              medium: Number(metric.derived_metrics.tier_distribution.medium)
            },
            burn_rate_per_active_mainer: Number(metric.derived_metrics.burn_rate_per_active_mainer),
            active_percentage: Number(metric.derived_metrics.active_percentage)
          },
          system_metrics: {
            funnai_index: Number(metric.system_metrics.funnai_index),
            daily_burn_rate: {
              usd: Number(metric.system_metrics.daily_burn_rate.usd),
              cycles: Number(metric.system_metrics.daily_burn_rate.cycles)
            }
          }
        };

        // Cache the result
        this.latestMetricCache = transformedMetric;
        this.latestMetricTimestamp = Date.now();
        
        console.log(`Fetched latest daily metric for date: ${transformedMetric.metadata.date}`);
        return transformedMetric;
      } else {
        console.error("Error fetching latest daily metric:", result.Err);
        // Fallback to the original method if the new one fails
        const metrics = await this.fetchDailyMetrics({ limit: 1 });
        return metrics.length > 0 ? metrics[0] : null;
      }
    } catch (error) {
      console.error("Error in getLatestMetrics:", error);
      // Fallback to the original method
      try {
        const metrics = await this.fetchDailyMetrics({ limit: 1 });
        return metrics.length > 0 ? metrics[0] : null;
      } catch (fallbackError) {
        console.error("Error in fallback getLatestMetrics:", fallbackError);
        return null;
      }
    }
  }
}
