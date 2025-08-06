// Session Manager Helper
// Provides utilities for managing user authentication sessions

export interface SessionInfo {
  loginType: string;
  expiry: bigint;
  timestamp: number;
}

export class SessionManager {
  private static readonly SESSION_WARNING_THRESHOLD = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
  private static readonly EXTENDED_SESSION_KEY = 'extendedSessionPreference';

  /**
   * Check if the user prefers extended sessions
   */
  static getExtendedSessionPreference(): boolean {
    return localStorage.getItem(SessionManager.EXTENDED_SESSION_KEY) === 'true';
  }

  /**
   * Set the user's extended session preference
   */
  static setExtendedSessionPreference(enabled: boolean): void {
    localStorage.setItem(SessionManager.EXTENDED_SESSION_KEY, enabled.toString());
  }

  /**
   * Get time remaining until session expires in human-readable format
   */
  static getTimeUntilExpiry(expiry: bigint): string {
    const now = BigInt(Date.now()) * BigInt(1000000); // Convert to nanoseconds
    const timeLeft = expiry - now;
    
    if (timeLeft <= 0n) {
      return "Session expired";
    }

    // Convert back to milliseconds
    const timeLeftMs = Number(timeLeft / BigInt(1000000));
    
    const days = Math.floor(timeLeftMs / (24 * 60 * 60 * 1000));
    const hours = Math.floor((timeLeftMs % (24 * 60 * 60 * 1000)) / (60 * 60 * 1000));
    const minutes = Math.floor((timeLeftMs % (60 * 60 * 1000)) / (60 * 1000));

    if (days > 0) {
      return `${days} day${days !== 1 ? 's' : ''}, ${hours} hour${hours !== 1 ? 's' : ''}`;
    } else if (hours > 0) {
      return `${hours} hour${hours !== 1 ? 's' : ''}, ${minutes} minute${minutes !== 1 ? 's' : ''}`;
    } else {
      return `${minutes} minute${minutes !== 1 ? 's' : ''}`;
    }
  }

  /**
   * Check if the session is expiring soon (within warning threshold)
   */
  static isSessionExpiringSoon(expiry: bigint): boolean {
    const now = BigInt(Date.now()) * BigInt(1000000); // Convert to nanoseconds
    const timeLeft = expiry - now;
    const warningThresholdNs = BigInt(SessionManager.SESSION_WARNING_THRESHOLD) * BigInt(1000000);
    
    return timeLeft <= warningThresholdNs && timeLeft > 0n;
  }

  /**
   * Get session progress (0-1, where 1 is fully expired)
   */
  static getSessionProgress(expiry: bigint, sessionDurationNs: bigint): number {
    const now = BigInt(Date.now()) * BigInt(1000000);
    const sessionStart = expiry - sessionDurationNs;
    const elapsed = now - sessionStart;
    
    if (elapsed <= 0n) return 0;
    if (elapsed >= sessionDurationNs) return 1;
    
    return Number(elapsed) / Number(sessionDurationNs);
  }

  /**
   * Format session expiry as a readable date
   */
  static formatExpiryDate(expiry: bigint): string {
    const expiryMs = Number(expiry / BigInt(1000000));
    const date = new Date(expiryMs);
    return date.toLocaleString();
  }

  /**
   * Clean up expired session data
   */
  static cleanupExpiredSessions(): void {
    try {
      const sessionInfoStr = localStorage.getItem('sessionInfo');
      if (sessionInfoStr) {
        const sessionInfo = JSON.parse(sessionInfoStr);
        const expiry = BigInt(sessionInfo.expiry);
        const now = BigInt(Date.now()) * BigInt(1000000);
        
        if (expiry <= now) {
          localStorage.removeItem('sessionInfo');
          localStorage.removeItem('isAuthed');
          console.log('Cleaned up expired session data');
        }
      }
    } catch (error) {
      console.error('Error cleaning up session data:', error);
    }
  }
} 