/**
 * mAIner Health Check Service
 * 
 * This service manages health checks for mAIner canisters to enable system maintenance mode.
 * It polls mAIner health endpoints and provides maintenance status information to the UI.
 */

import { writable, derived, get } from 'svelte/store';
import type { ActorSubclass } from '@dfinity/agent';

export interface MainerHealthStatus {
  isHealthy: boolean;
  maintenanceMessage: string;
  lastChecked: Date;
  canisterId: string;
}

export interface MainerHealthCheckResult {
  Ok?: { status_code: number };
  Err?: { 
    Unauthorized?: null;
    InvalidId?: null;
    ZeroAddress?: null;
    FailedOperation?: null;
    Other?: string;
    StatusCode?: number;
    InsuffientCycles?: bigint;
  };
}

// Store for all mAIner health statuses
export const mainerHealthStatuses = writable<Map<string, MainerHealthStatus>>(new Map());

// Derived store for global maintenance mode (true if ANY mAIner is unhealthy)
export const isMaintenanceMode = derived(
  mainerHealthStatuses,
  $statuses => {
    for (const status of $statuses.values()) {
      if (!status.isHealthy) {
        return true;
      }
    }
    return false;
  }
);

// Derived store for maintenance message (returns first maintenance message found)
export const maintenanceMessage = derived(
  mainerHealthStatuses,
  $statuses => {
    for (const status of $statuses.values()) {
      if (!status.isHealthy && status.maintenanceMessage) {
        return status.maintenanceMessage;
      }
    }
    return '';
  }
);

class MainerHealthService {
  private healthCheckIntervals: Map<string, NodeJS.Timeout> = new Map();
  private readonly HEALTH_CHECK_INTERVAL_MS = 30000; // Check every 30 seconds

  /**
   * Check health of a single mAIner canister
   */
  async checkMainerHealth(
    canisterId: string,
    mainerActor: ActorSubclass<any>
  ): Promise<MainerHealthStatus> {
    try {
      // Call the health endpoint
      const result: MainerHealthCheckResult = await mainerActor.health();
      
      if ('Ok' in result) {
        // mAIner is healthy
        return {
          isHealthy: true,
          maintenanceMessage: '',
          lastChecked: new Date(),
          canisterId
        };
      } else if ('Err' in result && result.Err) {
        // Check if it's a maintenance error (#Other)
        if ('Other' in result.Err && typeof result.Err.Other === 'string') {
          // mAIner is in maintenance mode
          return {
            isHealthy: false,
            maintenanceMessage: result.Err.Other,
            lastChecked: new Date(),
            canisterId
          };
        }
        // Other error types mean unhealthy but no specific maintenance message
        return {
          isHealthy: false,
          maintenanceMessage: 'mAIner is currently unavailable',
          lastChecked: new Date(),
          canisterId
        };
      }
      
      // Unexpected response format
      return {
        isHealthy: false,
        maintenanceMessage: 'Unable to determine mAIner health status',
        lastChecked: new Date(),
        canisterId
      };
    } catch (error) {
      console.error(`Error checking health for mAIner ${canisterId}:`, error);
      return {
        isHealthy: false,
        maintenanceMessage: 'Failed to connect to mAIner',
        lastChecked: new Date(),
        canisterId
      };
    }
  }

  /**
   * Start periodic health checks for a mAIner
   */
  startHealthChecks(
    canisterId: string,
    mainerActor: ActorSubclass<any>
  ): void {
    // Clear any existing interval for this canister
    this.stopHealthChecks(canisterId);

    // Perform initial health check immediately
    this.checkMainerHealth(canisterId, mainerActor).then(status => {
      this.updateHealthStatus(canisterId, status);
    });

    // Set up periodic health checks
    const intervalId = setInterval(async () => {
      const status = await this.checkMainerHealth(canisterId, mainerActor);
      this.updateHealthStatus(canisterId, status);
    }, this.HEALTH_CHECK_INTERVAL_MS);

    this.healthCheckIntervals.set(canisterId, intervalId);
  }

  /**
   * Stop health checks for a specific mAIner
   */
  stopHealthChecks(canisterId: string): void {
    const intervalId = this.healthCheckIntervals.get(canisterId);
    if (intervalId) {
      clearInterval(intervalId);
      this.healthCheckIntervals.delete(canisterId);
    }

    // Remove health status for this canister
    mainerHealthStatuses.update(statuses => {
      statuses.delete(canisterId);
      return new Map(statuses);
    });
  }

  /**
   * Stop all health checks
   */
  stopAllHealthChecks(): void {
    for (const intervalId of this.healthCheckIntervals.values()) {
      clearInterval(intervalId);
    }
    this.healthCheckIntervals.clear();
    mainerHealthStatuses.set(new Map());
  }

  /**
   * Update health status in the store
   */
  private updateHealthStatus(canisterId: string, status: MainerHealthStatus): void {
    mainerHealthStatuses.update(statuses => {
      statuses.set(canisterId, status);
      return new Map(statuses);
    });
  }

  /**
   * Get health status for a specific mAIner
   */
  getHealthStatus(canisterId: string): MainerHealthStatus | undefined {
    const statuses = get(mainerHealthStatuses);
    return statuses.get(canisterId);
  }

  /**
   * Check if a specific mAIner is healthy
   */
  isMainerHealthy(canisterId: string): boolean {
    const status = this.getHealthStatus(canisterId);
    return status?.isHealthy ?? false; // Default to unhealthy if no status available (defensive)
  }
}

// Export singleton instance
export const mainerHealthService = new MainerHealthService();

