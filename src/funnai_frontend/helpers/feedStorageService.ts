interface FeedItem {
  id: string;
  timestamp: number;
  type: "challenge" | "response" | "score" | "winner" | "participation";
  mainerName: string;
  content: {
    challenge?: string;
    response?: string;
    score?: number;
    placement?: string;
    reward?: string;
  };
}

interface CachedFeedData {
  items: FeedItem[];
  lastFetch: number;
  lastCleanup: number;
}

export class FeedStorageService {
  private static readonly STORAGE_KEYS = {
    ALL_EVENTS: 'mainer_feed_cache_all_events',
    MY_MAINERS: 'mainer_feed_cache_my_mainers'
  };

  private static readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  private static readonly CLEANUP_INTERVAL = 24 * 60 * 60 * 1000; // 24 hours
  private static readonly MAX_DAYS_TO_KEEP = 7; // Keep items for 7 days max

  /**
   * Generate a content-based hash for deduplication
   * This creates a consistent hash based on the actual content rather than just ID
   */
  private static generateContentHash(item: FeedItem): string {
    const contentKey = `${item.type}-${item.mainerName}-${JSON.stringify(item.content)}`;
    
    // For challenges, include only the challenge content (ignore timestamp differences)
    if (item.type === 'challenge') {
      return `challenge-${item.content.challenge}`;
    }
    
    // For responses, include challenge context if possible (extracted from ID)
    if (item.type === 'response') {
      const challengeId = item.id.split('-')[0]; // Extract challenge ID from response ID
      return `response-${challengeId}-${item.content.response}`;
    }
    
    // For scores, include the unique scoring context
    if (item.type === 'score') {
      const challengeId = item.id.split('-')[0];
      return `score-${challengeId}-${item.mainerName}-${item.content.score}`;
    }
    
    // For winners and participation, use the full context
    if (item.type === 'winner' || item.type === 'participation') {
      const challengeId = item.id.split('-')[0];
      return `${item.type}-${challengeId}-${item.mainerName}-${item.content.placement || 'participation'}-${item.content.reward}`;
    }

    // Fallback to original ID if we can't create a better hash
    return item.id;
  }

  /**
   * Check if an item is within the allowed date range
   */
  private static isWithinDateRange(timestamp: number, maxDays: number = 7): boolean {
    const now = Date.now();
    const itemTime = timestamp / 1000000; // Convert from nanoseconds to milliseconds
    const daysDiff = (now - itemTime) / (24 * 60 * 60 * 1000);
    return daysDiff <= maxDays && daysDiff >= 0; // Ensure not future dates
  }

  /**
   * Remove duplicates using both ID-based and content-based deduplication
   */
  private static deduplicateItems(items: FeedItem[]): FeedItem[] {
    const seenIds = new Set<string>();
    const seenContentHashes = new Set<string>();
    const uniqueItems: FeedItem[] = [];

    // Sort by timestamp (newest first) to prioritize newer versions of same content
    const sortedItems = [...items].sort((a, b) => b.timestamp - a.timestamp);

    for (const item of sortedItems) {
      const contentHash = this.generateContentHash(item);
      
      // Skip if we've seen this exact ID or this content before
      if (seenIds.has(item.id) || seenContentHashes.has(contentHash)) {
        continue;
      }

      // Keep only items within allowed date range
      if (!this.isWithinDateRange(item.timestamp, this.MAX_DAYS_TO_KEEP)) {
        continue;
      }

      seenIds.add(item.id);
      seenContentHashes.add(contentHash);
      uniqueItems.push(item);
    }

    // Return sorted by timestamp (newest first)
    return uniqueItems.sort((a, b) => b.timestamp - a.timestamp);
  }

  /**
   * Get cached feed data for a specific mode
   */
  static getCachedFeedData(isAllEvents: boolean): CachedFeedData | null {
    try {
      const storageKey = isAllEvents ? this.STORAGE_KEYS.ALL_EVENTS : this.STORAGE_KEYS.MY_MAINERS;
      const cached = localStorage.getItem(storageKey);
      
      if (!cached) {
        return null;
      }

      const data: CachedFeedData = JSON.parse(cached);
      
      // Validate cache structure
      if (!data.items || !Array.isArray(data.items) || typeof data.lastFetch !== 'number') {
        console.warn('Invalid cached feed data structure, clearing cache');
        localStorage.removeItem(storageKey);
        return null;
      }

      // Filter out old items and deduplicate
      const validItems = this.deduplicateItems(data.items);
      
      return {
        items: validItems,
        lastFetch: data.lastFetch,
        lastCleanup: data.lastCleanup || 0
      };
    } catch (error) {
      console.error('Error loading cached feed data:', error);
      return null;
    }
  }

  /**
   * Save feed data to cache with smart merging
   */
  static saveFeedData(newItems: FeedItem[], isAllEvents: boolean): void {
    try {
      const storageKey = isAllEvents ? this.STORAGE_KEYS.ALL_EVENTS : this.STORAGE_KEYS.MY_MAINERS;
      const now = Date.now();
      
      // Get existing cached data
      const existingData = this.getCachedFeedData(isAllEvents);
      
      // Merge with existing items
      const allItems = existingData ? [...existingData.items, ...newItems] : newItems;
      
      // Additional filtering for "All Events" mode - remove winner and participation events
      let filteredItems = allItems;
      if (isAllEvents) {
        filteredItems = allItems.filter(item => item.type !== 'winner' && item.type !== 'participation');
      }
      
      // Deduplicate and filter by date
      const uniqueItems = this.deduplicateItems(filteredItems);
      
      const cacheData: CachedFeedData = {
        items: uniqueItems,
        lastFetch: now,
        lastCleanup: existingData?.lastCleanup || now
      };

      localStorage.setItem(storageKey, JSON.stringify(cacheData));
      
      // Perform cleanup if needed
      if (now - cacheData.lastCleanup > this.CLEANUP_INTERVAL) {
        this.performCleanup();
      }
    } catch (error) {
      console.error('Error saving feed data to cache:', error);
    }
  }

  /**
   * Check if cache is fresh enough
   */
  static isCacheFresh(isAllEvents: boolean): boolean {
    const data = this.getCachedFeedData(isAllEvents);
    if (!data) {
      return false;
    }
    
    const now = Date.now();
    return (now - data.lastFetch) < this.CACHE_DURATION;
  }

  /**
   * Get fresh feed items (cached items if cache is fresh, empty array if not)
   */
  static getFeedItems(isAllEvents: boolean): FeedItem[] {
    const data = this.getCachedFeedData(isAllEvents);
    return data ? data.items : [];
  }

  /**
   * Clear cache for a specific mode or all modes
   */
  static clearCache(isAllEvents?: boolean): void {
    try {
      if (isAllEvents === undefined) {
        // Clear both caches
        localStorage.removeItem(this.STORAGE_KEYS.ALL_EVENTS);
        localStorage.removeItem(this.STORAGE_KEYS.MY_MAINERS);
      } else {
        const storageKey = isAllEvents ? this.STORAGE_KEYS.ALL_EVENTS : this.STORAGE_KEYS.MY_MAINERS;
        localStorage.removeItem(storageKey);
      }
    } catch (error) {
      console.error('Error clearing feed cache:', error);
    }
  }

  /**
   * Perform periodic cleanup of old data and invalid cache entries
   */
  static performCleanup(): void {
    try {
      // Clean up both caches
      [true, false].forEach(isAllEvents => {
        const data = this.getCachedFeedData(isAllEvents);
        if (data) {
          // Update cleanup timestamp and save cleaned data
          const cleanedData: CachedFeedData = {
            ...data,
            lastCleanup: Date.now()
          };
          
          const storageKey = isAllEvents ? this.STORAGE_KEYS.ALL_EVENTS : this.STORAGE_KEYS.MY_MAINERS;
          localStorage.setItem(storageKey, JSON.stringify(cleanedData));
        }
      });

      // Clean up any old format cache keys
      const oldKeys = [
        'mainer_feed_items',
        'mainer_feed_last_fetch',
        'mainer_feed_items_my_mainers',
        'mainer_feed_items_all_events',
        'mainer_feed_last_fetch_my_mainers',
        'mainer_feed_last_fetch_all_events'
      ];
      
      oldKeys.forEach(key => {
        try {
          localStorage.removeItem(key);
        } catch (e) {
          // Ignore errors for individual key removals
        }
      });
    } catch (error) {
      console.error('Error during feed cache cleanup:', error);
    }
  }

  /**
   * Get cache statistics for debugging
   */
  static getCacheStats(): {
    allEvents: { itemCount: number; lastFetch: number; cacheAge: number };
    myMainers: { itemCount: number; lastFetch: number; cacheAge: number };
  } {
    const now = Date.now();
    
    const allEventsData = this.getCachedFeedData(true);
    const myMainersData = this.getCachedFeedData(false);
    
    return {
      allEvents: {
        itemCount: allEventsData?.items.length || 0,
        lastFetch: allEventsData?.lastFetch || 0,
        cacheAge: allEventsData ? now - allEventsData.lastFetch : -1
      },
      myMainers: {
        itemCount: myMainersData?.items.length || 0,
        lastFetch: myMainersData?.lastFetch || 0,
        cacheAge: myMainersData ? now - myMainersData.lastFetch : -1
      }
    };
  }
}
