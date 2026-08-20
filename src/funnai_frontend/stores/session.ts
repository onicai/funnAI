type AuthProvider = "nfid" | "internetidentity";

export type { AuthProvider };

export const SESSION_REFRESH_THRESHOLD = BigInt(24 * 60 * 60 * 1000 * 1000 * 1000); // 24 hours in nanoseconds
export const SESSION_CHECK_INTERVAL = 30 * 60 * 1000; // Check every 30 minutes in milliseconds

export const STORAGE_KEYS = {
  MAINER_CREATION_STATE: 'mainerCreationState',
  MAINER_CREATION_SESSION: 'mainerCreationSession',
  MAINER_UI_CACHE: 'funnai.mainerUiCache',
};

export const MAINER_UI_CACHE_KEY = STORAGE_KEYS.MAINER_UI_CACHE;

/**
 * Synchronous localStorage peek so the first paint can use the last known
 * login instead of waiting for AuthClient / NFID restore (which runs after mount).
 * Must NOT be folded into defaultState — disconnect() resets from defaultState.
 */
export const peekStoredAuth = (): AuthProvider | null => {
  if (typeof localStorage === "undefined") {
    return null;
  }

  try {
    const sessionInfoStr = localStorage.getItem("sessionInfo");
    if (sessionInfoStr) {
      const sessionInfo = JSON.parse(sessionInfoStr);
      const loginType = sessionInfo?.loginType;
      if (loginType === "nfid" || loginType === "internetidentity") {
        if (sessionInfo.expiry) {
          const expiry = BigInt(sessionInfo.expiry);
          const nowNs = BigInt(Date.now()) * 1_000_000n;
          if (expiry <= nowNs) {
            return null;
          }
        }
        return loginType;
      }
    }

    const legacy = localStorage.getItem("isAuthed");
    if (legacy === "nfid" || legacy === "internetidentity") {
      return legacy;
    }
  } catch (error) {
    console.warn("Could not peek stored auth session:", error);
  }

  return null;
};
