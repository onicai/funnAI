/**
 * mAIner Health Check Service
 * 
 * This service manages health checks for mAIner canisters to enable system maintenance mode.
 * It polls mAIner health endpoints and provides maintenance status information to the UI.
 */

import { writable, get } from 'svelte/store';
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

// Store for all mAIner health statuses (per-mAIner, not global)
// Each mAIner canister has its own independent health status
export const mainerHealthStatuses = writable<Map<string, MainerHealthStatus>>(new Map());

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
        const status = {
          isHealthy: true,
          maintenanceMessage: '',
          lastChecked: new Date(),
          canisterId
        };
        console.log(`Health check OK for ${canisterId}:`, status);
        return status;
      } else if ('Err' in result && result.Err) {
        // Check if it's a maintenance error (#Other)
        if ('Other' in result.Err && typeof result.Err.Other === 'string') {
          // mAIner is in maintenance mode
          const status = {
            isHealthy: false,
            maintenanceMessage: result.Err.Other,
            lastChecked: new Date(),
            canisterId
          };
          console.log(`Health check maintenance for ${canisterId}:`, status);
          return status;
        }
        // Other error types mean unhealthy but no specific maintenance message
        const status = {
          isHealthy: false,
          maintenanceMessage: 'mAIner is currently unavailable',
          lastChecked: new Date(),
          canisterId
        };
        console.log(`Health check unavailable for ${canisterId}:`, status);
        return status;
      }
      
      // Unexpected response format
      const status = {
        isHealthy: false,
        maintenanceMessage: 'Unable to determine mAIner health status',
        lastChecked: new Date(),
        canisterId
      };
      console.log(`Health check unexpected format for ${canisterId}:`, status);
      return status;
    } catch (error) {
      // Check if it's a stopped canister error
      const errorMessage = error instanceof Error ? error.message : String(error);
      let maintenanceMessage = 'Failed to connect to mAIner';
      
      if (errorMessage.includes('is stopped') || errorMessage.includes('CallContextManager')) {
        maintenanceMessage = 'mAIner is stopped';
      } else if (errorMessage.includes('does not have a') || errorMessage.includes('Canister')) {
        maintenanceMessage = 'mAIner is currently unavailable';
      }
      
      const status = {
        isHealthy: false,
        maintenanceMessage,
        lastChecked: new Date(),
        canisterId
      };
      console.error(`Error checking health for mAIner ${canisterId}:`, error);
      console.log(`Health check error status for ${canisterId}:`, status);
      return status;
    }
  }

  /**
   * Start periodic health checks for a mAIner
   */
  startHealthChecks(
    canisterId: string,
    mainerActor: ActorSubclass<any>
  ): void {
    console.log(`Starting health checks for mAIner ${canisterId}`);
    
    // Clear any existing interval for this canister
    this.stopHealthChecks(canisterId);

    // Perform initial health check immediately
    this.checkMainerHealth(canisterId, mainerActor).then(status => {
      this.updateHealthStatus(canisterId, status);
    }).catch(error => {
      console.error(`Failed to start initial health check for ${canisterId}:`, error);
    });

    // Set up periodic health checks
    const intervalId = setInterval(async () => {
      const status = await this.checkMainerHealth(canisterId, mainerActor);
      this.updateHealthStatus(canisterId, status);
    }, this.HEALTH_CHECK_INTERVAL_MS);

    this.healthCheckIntervals.set(canisterId, intervalId);
    console.log(`Health checks started for ${canisterId}, checking every ${this.HEALTH_CHECK_INTERVAL_MS}ms`);
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
    console.log(`Updating health status in store for ${canisterId}:`, status);
    mainerHealthStatuses.update(statuses => {
      statuses.set(canisterId, status);
      console.log(`Store now has ${statuses.size} mAIner statuses`);
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

