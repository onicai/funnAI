import { store } from "../stores/store";
import { get } from "svelte/store";

/**
 * Activity Feed Service
 * 
 * Fetches paginated activity feed data from the API canister.
 * The API canister caches data from GameState and provides optimized queries.
 */

// ============================================================================
// Types matching the backend (from PoAIW/src/common/Types.mo)
// ============================================================================

export interface ActivityFeedQuery {
  winnersLimit?: number;
  winnersOffset?: number;
  challengesLimit?: number;
  challengesOffset?: number;
  sinceTimestamp?: bigint;
}

export interface ChallengeParticipantEntry {
  submissionId: string;
  submittedBy: string; // Principal as string
  ownedBy: string; // Principal as string
  result: { Winner: null } | { SecondPlace: null } | { ThirdPlace: null } | { Participated: null } | { Other: string };
  reward: {
    amount: bigint;
    rewardType: { MainerToken: null } | { Cycles: null } | { ICP: null } | { Coupon: string } | { Other: string };
    rewardDetails: string;
    distributed: boolean;
    distributedTimestamp?: bigint;
  };
}

export interface ChallengeWinnerDeclaration {
  challengeId: string;
  finalizedTimestamp: bigint;
  winner: ChallengeParticipantEntry;
  secondPlace: ChallengeParticipantEntry;
  thirdPlace: ChallengeParticipantEntry;
  participants: ChallengeParticipantEntry[];
}

export interface Challenge {
  challengeId: string;
  challengeQuestion: string;
  challengeTopic: string;
  challengeCreationTimestamp: bigint;
  challengeCreatedBy: string;
  challengeStatus: { Open: null } | { Closed: null } | { Archived: null } | { Other: string };
  challengeClosedTimestamp?: bigint;
}

export interface ActivityFeedResponse {
  winners: ChallengeWinnerDeclaration[];
  challenges: Challenge[];
  totalWinners: number;
  totalChallenges: number;
  cacheTimestamp: bigint;
}

export interface CacheStatus {
  lastSyncTimestamp: bigint;
  cachedWinnersCount: number;
  cachedChallengesCount: number;
  syncIntervalSeconds: number;
}

// Unified feed item for UI consumption
export type FeedItemType = "challenge" | "winner" | "second_place" | "third_place" | "participation";

export interface ActivityFeedItem {
  id: string;
  timestamp: bigint;
  type: FeedItemType;
  challengeId: string;
  challengeQuestion?: string;
  challengeTopic?: string;
  // Winner-specific fields
  mainerAddress?: string; // submittedBy principal
  ownerAddress?: string; // ownedBy principal
  placement?: string;
  reward?: bigint;
}

// ============================================================================
// Service Class
// ============================================================================

export class ActivityFeedService {
  private static cache: ActivityFeedResponse | null = null;
  private static cacheTimestamp: number = 0;
  private static readonly CACHE_DURATION = 30 * 1000; // 30 seconds

  /**
   * Check if cache is still valid
   */
  private static isCacheValid(): boolean {
    if (!this.cacheTimestamp || !this.cache) return false;
    return Date.now() - this.cacheTimestamp < this.CACHE_DURATION;
  }

  /**
   * Clear the cache (useful for manual refresh)
   */
  static clearCache(): void {
    this.cache = null;
    this.cacheTimestamp = 0;
  }

  /**
   * Fetch the activity feed from the API canister
   */
  static async fetchActivityFeed(query: ActivityFeedQuery = {}): Promise<ActivityFeedResponse> {
    // Return cached data if valid
    if (this.isCacheValid() && this.cache) {
      return this.cache;
    }

    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      // Build query parameters
      const queryParam = {
        winnersLimit: query.winnersLimit !== undefined ? [BigInt(query.winnersLimit)] : [],
        winnersOffset: query.winnersOffset !== undefined ? [BigInt(query.winnersOffset)] : [],
        challengesLimit: query.challengesLimit !== undefined ? [BigInt(query.challengesLimit)] : [],
        challengesOffset: query.challengesOffset !== undefined ? [BigInt(query.challengesOffset)] : [],
        sinceTimestamp: query.sinceTimestamp !== undefined ? [query.sinceTimestamp] : [],
      };

      const result = await storeValue.apiCanisterActor.getActivityFeed(queryParam);

      if ("Ok" in result) {
        const response = result.Ok;
        
        // Transform to our interface
        const transformed: ActivityFeedResponse = {
          winners: response.winners.map((w: any) => ({
            challengeId: w.challengeId,
            finalizedTimestamp: BigInt(w.finalizedTimestamp),
            winner: this.transformParticipant(w.winner),
            secondPlace: this.transformParticipant(w.secondPlace),
            thirdPlace: this.transformParticipant(w.thirdPlace),
            participants: w.participants.map((p: any) => this.transformParticipant(p)),
          })),
          challenges: response.challenges.map((c: any) => ({
            challengeId: c.challengeId,
            challengeQuestion: c.challengeQuestion,
            challengeTopic: c.challengeTopic,
            challengeCreationTimestamp: BigInt(c.challengeCreationTimestamp),
            challengeCreatedBy: c.challengeCreatedBy,
            challengeStatus: c.challengeStatus,
            challengeClosedTimestamp: c.challengeClosedTimestamp?.[0] ? BigInt(c.challengeClosedTimestamp[0]) : undefined,
          })),
          totalWinners: Number(response.totalWinners),
          totalChallenges: Number(response.totalChallenges),
          cacheTimestamp: BigInt(response.cacheTimestamp),
        };

        // Update cache
        this.cache = transformed;
        this.cacheTimestamp = Date.now();

        return transformed;
      } else {
        console.error("Error fetching activity feed:", result.Err);
        throw new Error(JSON.stringify(result.Err) || "Failed to fetch activity feed");
      }
    } catch (error) {
      console.error("Error in fetchActivityFeed:", error);
      
      // Return cached data if available, even if stale
      if (this.cache) {
        console.log("Returning stale cache due to error");
        return this.cache;
      }
      
      throw error;
    }
  }

  /**
   * Transform a participant entry from the canister response
   */
  private static transformParticipant(p: any): ChallengeParticipantEntry {
    return {
      submissionId: p.submissionId,
      submittedBy: p.submittedBy.toString(),
      ownedBy: p.ownedBy.toString(),
      result: p.result,
      reward: {
        amount: BigInt(p.reward.amount),
        rewardType: p.reward.rewardType,
        rewardDetails: p.reward.rewardDetails,
        distributed: p.reward.distributed,
        distributedTimestamp: p.reward.distributedTimestamp?.[0] ? BigInt(p.reward.distributedTimestamp[0]) : undefined,
      },
    };
  }

  /**
   * Convert raw API response to unified feed items for the UI
   */
  static toFeedItems(response: ActivityFeedResponse): ActivityFeedItem[] {
    const items: ActivityFeedItem[] = [];

    // Add challenges
    for (const challenge of response.challenges) {
      items.push({
        id: `challenge-${challenge.challengeId}`,
        timestamp: challenge.challengeCreationTimestamp,
        type: "challenge",
        challengeId: challenge.challengeId,
        challengeQuestion: challenge.challengeQuestion,
        challengeTopic: challenge.challengeTopic,
      });
    }

    // Add winners from winner declarations
    for (const winnerDecl of response.winners) {
      // First place
      items.push({
        id: `winner-${winnerDecl.challengeId}-${winnerDecl.winner.submissionId}`,
        timestamp: winnerDecl.finalizedTimestamp,
        type: "winner",
        challengeId: winnerDecl.challengeId,
        mainerAddress: winnerDecl.winner.submittedBy,
        ownerAddress: winnerDecl.winner.ownedBy,
        placement: "First Place",
        reward: winnerDecl.winner.reward.amount,
      });

      // Second place
      items.push({
        id: `second-${winnerDecl.challengeId}-${winnerDecl.secondPlace.submissionId}`,
        timestamp: winnerDecl.finalizedTimestamp,
        type: "second_place",
        challengeId: winnerDecl.challengeId,
        mainerAddress: winnerDecl.secondPlace.submittedBy,
        ownerAddress: winnerDecl.secondPlace.ownedBy,
        placement: "Second Place",
        reward: winnerDecl.secondPlace.reward.amount,
      });

      // Third place
      if (winnerDecl.thirdPlace && winnerDecl.thirdPlace.submissionId) {
        items.push({
          id: `third-${winnerDecl.challengeId}-${winnerDecl.thirdPlace.submissionId}`,
          timestamp: winnerDecl.finalizedTimestamp,
          type: "third_place",
          challengeId: winnerDecl.challengeId,
          mainerAddress: winnerDecl.thirdPlace.submittedBy,
          ownerAddress: winnerDecl.thirdPlace.ownedBy,
          placement: "Third Place",
          reward: winnerDecl.thirdPlace.reward.amount,
        });
      }

      // Participation rewards
      for (const participant of winnerDecl.participants) {
        if ("Participated" in participant.result) {
          items.push({
            id: `participation-${winnerDecl.challengeId}-${participant.submissionId}`,
            timestamp: winnerDecl.finalizedTimestamp,
            type: "participation",
            challengeId: winnerDecl.challengeId,
            mainerAddress: participant.submittedBy,
            ownerAddress: participant.ownedBy,
            reward: participant.reward.amount,
          });
        }
      }
    }

    // Sort by timestamp (newest first)
    items.sort((a, b) => {
      const aTime = Number(a.timestamp);
      const bTime = Number(b.timestamp);
      return bTime - aTime;
    });

    return items;
  }

  /**
   * Fetch only open challenges from cache
   */
  static async fetchOpenChallenges(): Promise<Challenge[]> {
    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      const result = await storeValue.apiCanisterActor.getOpenChallengesFromCache();

      if ("Ok" in result) {
        return result.Ok.map((c: any) => ({
          challengeId: c.challengeId,
          challengeQuestion: c.challengeQuestion,
          challengeTopic: c.challengeTopic,
          challengeCreationTimestamp: BigInt(c.challengeCreationTimestamp),
          challengeCreatedBy: c.challengeCreatedBy,
          challengeStatus: c.challengeStatus,
          challengeClosedTimestamp: c.challengeClosedTimestamp?.[0] ? BigInt(c.challengeClosedTimestamp[0]) : undefined,
        }));
      } else {
        console.error("Error fetching open challenges:", result.Err);
        throw new Error(JSON.stringify(result.Err) || "Failed to fetch open challenges");
      }
    } catch (error) {
      console.error("Error in fetchOpenChallenges:", error);
      throw error;
    }
  }

  /**
   * Get cache status (for debugging/monitoring)
   */
  static async getCacheStatus(): Promise<CacheStatus | null> {
    try {
      const storeValue = get(store);
      if (!storeValue.apiCanisterActor) {
        throw new Error("API canister actor not available");
      }

      const result = await storeValue.apiCanisterActor.getActivityFeedCacheStatus();

      if ("Ok" in result) {
        return {
          lastSyncTimestamp: BigInt(result.Ok.lastSyncTimestamp),
          cachedWinnersCount: Number(result.Ok.cachedWinnersCount),
          cachedChallengesCount: Number(result.Ok.cachedChallengesCount),
          syncIntervalSeconds: Number(result.Ok.syncIntervalSeconds),
        };
      } else {
        console.error("Error fetching cache status:", result.Err);
        return null;
      }
    } catch (error) {
      console.error("Error in getCacheStatus:", error);
      return null;
    }
  }

  /**
   * Helper to format timestamp for display
   */
  static formatTimestamp(timestamp: bigint): { date: string; time: string } {
    // IC timestamps are in nanoseconds, convert to milliseconds
    const milliseconds = Number(timestamp) / 1_000_000;
    const dateObj = new Date(milliseconds);
    
    if (isNaN(dateObj.getTime())) {
      return { date: "Invalid", time: "Date" };
    }
    
    const date = dateObj.toLocaleDateString([], {
      month: "2-digit",
      day: "2-digit",
      year: "2-digit",
    });
    
    const time = dateObj.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    
    return { date, time };
  }

  /**
   * Check if a timestamp is within a certain number of days
   */
  static isWithinDays(timestamp: bigint, days: number = 3): boolean {
    const now = Date.now();
    const itemTime = Number(timestamp) / 1_000_000; // Convert from nanoseconds to milliseconds
    const daysDiff = (now - itemTime) / (24 * 60 * 60 * 1000);
    return daysDiff <= days && daysDiff >= 0;
  }
}
