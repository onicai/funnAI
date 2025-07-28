// Session Manager Helper
// Provides utilities for managing user authentication sessions with enhanced debugging

export interface SessionInfo {
  loginType: string;
  expiry: bigint;
  timestamp: number;
  version?: string;
}

export class SessionManager {
  private static readonly SESSION_WARNING_THRESHOLD = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
  private static readonly EXTENDED_SESSION_KEY = 'extendedSessionPreference';
  private static readonly DEBUG_MODE = true; // Enable debugging for session issues

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
   * Get detailed session status for debugging
   */
  static getSessionStatus(): {
    hasSession: boolean;
    loginType?: string;
    timeRemaining?: string;
    expiryDate?: string;
    isExpiringSoon?: boolean;
    lastActivity?: string;
    debugInfo?: any;
  } {
    try {
      const sessionInfoStr = localStorage.getItem('sessionInfo');
      const lastActivity = localStorage.getItem('lastActivity');
      
      if (!sessionInfoStr) {
        return {
          hasSession: false,
          debugInfo: {
            sessionStorage: null,
            lastActivity: lastActivity ? new Date(parseInt(lastActivity)).toLocaleString() : null
          }
        };
      }

      const sessionInfo = JSON.parse(sessionInfoStr);
      const expiry = BigInt(sessionInfo.expiry);
      const now = BigInt(Date.now()) * BigInt(1000000);
      
      return {
        hasSession: true,
        loginType: sessionInfo.loginType,
        timeRemaining: SessionManager.getTimeUntilExpiry(expiry),
        expiryDate: SessionManager.formatExpiryDate(expiry),
        isExpiringSoon: SessionManager.isSessionExpiringSoon(expiry),
        lastActivity: lastActivity ? new Date(parseInt(lastActivity)).toLocaleString() : 'Unknown',
        debugInfo: {
          sessionTimestamp: new Date(sessionInfo.timestamp).toLocaleString(),
          currentTime: new Date().toLocaleString(),
          timeLeftNs: (expiry - now).toString(),
          version: sessionInfo.version || '1.0'
        }
      };
    } catch (error) {
      return {
        hasSession: false,
        debugInfo: {
          error: error.message,
          storageContent: localStorage.getItem('sessionInfo')
        }
      };
    }
  }

  /**
   * Log session status to console (for debugging)
   */
  static logSessionStatus(): void {
    if (!SessionManager.DEBUG_MODE) return;
    
    const status = SessionManager.getSessionStatus();
    console.group('🔐 Session Status');
    console.log('Has Session:', status.hasSession);
    
    if (status.hasSession) {
      console.log('Login Type:', status.loginType);
      console.log('Time Remaining:', status.timeRemaining);
      console.log('Expires:', status.expiryDate);
      console.log('Expiring Soon:', status.isExpiringSoon);
      console.log('Last Activity:', status.lastActivity);
      
      if (status.debugInfo) {
        console.log('Debug Info:', status.debugInfo);
      }
    } else {
      console.log('No active session found');
      if (status.debugInfo) {
        console.log('Debug Info:', status.debugInfo);
      }
    }
    
    console.groupEnd();
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
          localStorage.removeItem('sessionInfoBackup');
          localStorage.removeItem('isAuthed');
          localStorage.removeItem('lastActivity');
          console.log('🧹 Cleaned up expired session data');
        }
      }
    } catch (error) {
      console.error('Error cleaning up session data:', error);
    }
  }

  /**
   * Monitor session health and log warnings
   */
  static monitorSessionHealth(): void {
    if (!SessionManager.DEBUG_MODE) return;
    
    setInterval(() => {
      const status = SessionManager.getSessionStatus();
      
      if (status.hasSession && status.isExpiringSoon) {
        console.warn('⚠️ Session expiring soon:', status.timeRemaining);
      }
    }, 5 * 60 * 1000); // Check every 5 minutes
  }

  /**
   * Initialize session monitoring
   */
  static initialize(): void {
    if (SessionManager.DEBUG_MODE) {
      console.log('🔐 SessionManager initialized with debugging enabled');
      SessionManager.logSessionStatus();
      SessionManager.monitorSessionHealth();
    }
    
    SessionManager.cleanupExpiredSessions();
  }
} 