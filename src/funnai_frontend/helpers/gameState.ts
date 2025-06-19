import {
  store
} from "../stores/store";

let storeState;
store.subscribe((value) => storeState = value);

export const getSharedAgentPrice = async () => {
  try {
    let response = await storeState.gameStateCanisterActor.getPriceForShareAgent();
    
    if ('Ok' in response) {
      return response.Ok.price;
    } else if ('Err' in response) {
      console.error("Error in getSharedAgentPrice:", response.Err);
      return 1000; // Fallback value in case of error
    };
  } catch (error) {
    console.error("Failed to getSharedAgentPrice:", error);
    return 1000; // Fallback value in case of error
  };
};

export const getOwnAgentPrice = async () => {
  try {
    let response = await storeState.gameStateCanisterActor.getPriceForOwnMainer();
    
    if ('Ok' in response) {
      return response.Ok.price;
    } else if ('Err' in response) {
      console.error("Error in getOwnAgentPrice:", response.Err);
      return 1500; // Fallback value in case of error
    };
  } catch (error) {
    console.error("Failed to getOwnAgentPrice:", error);
    return 1500; // Fallback value in case of error
  };
};

export const getWhitelistAgentPrice = async () => {
  try {
    console.log("🔵 getWhitelistAgentPrice called");
    
    // Check if the method exists before calling it
    if (!storeState.gameStateCanisterActor.getWhitelistPriceForShareAgent) {
      console.warn("🟠 getWhitelistPriceForShareAgent method not available, using fallback price");
      return 5;
    }
    
    console.log("🔵 Calling getWhitelistPriceForShareAgent...");
    let response = await storeState.gameStateCanisterActor.getWhitelistPriceForShareAgent();
    console.log("🔵 getWhitelistPriceForShareAgent response:", response);
    
    if ('Ok' in response) {
      const price = response.Ok.price;
      console.log("✅ Whitelist price obtained:", price);
      
      // If backend returns 0, use fallback value (backend not configured yet)
      if (price <= 0) {
        console.warn("🟠 Backend returned 0 or negative price, using fallback value");
        return 5;
      }
      
      return price;
    } else if ('Err' in response) {
      console.error("❌ Error in getWhitelistAgentPrice:", response.Err);
      return 5; // Fallback value in case of error
    };
  } catch (error) {
    console.error("❌ Failed to getWhitelistAgentPrice:", error);
    return 5; // Fallback value in case of error
  };
};

export const getIsProtocolActive = async () => {
  try {
    // Check if the method exists before calling it
    if (!storeState.gameStateCanisterActor.getPauseProtocolFlag) {
      console.warn("getPauseProtocolFlag method not available, defaulting to active");
      return true;
    }
    
    let response = await storeState.gameStateCanisterActor.getPauseProtocolFlag();
    
    if ('Ok' in response) {
      let isPaused = response.Ok.flag;
      return !isPaused;
    } else if ('Err' in response) {
      console.error("Error in getPauseProtocol:", response.Err);
      return true; // Default to active if we can't determine
    };
  } catch (error) {
    console.error("Failed to getPauseProtocol:", error);
    return true; // Default to active if we can't determine
  };
};

export const getIsMainerCreationStopped = async (mainerType) => {
  try {
    // Check if the method exists before calling it
    if (!storeState.gameStateCanisterActor.shouldCreatingMainersBeStopped) {
      console.warn("shouldCreatingMainersBeStopped method not available, defaulting to not stopped");
      return false;
    }
    
    let input = { 'mainerType' : mainerType === 'Own' ? { 'Own': null } : { 'ShareAgent': null } }
    let response = await storeState.gameStateCanisterActor.shouldCreatingMainersBeStopped(input);
    
    // Handle both response types - the backend might return just a boolean or a Result type
    if (typeof response === 'boolean') {
      return response;
    } else if ('Ok' in response) {
      return response.Ok.flag;
    } else if ('Err' in response) {
      console.error("Error in getIsMainerCreationStopped:", response.Err);
      return false; // Default to not stopped if we can't determine
    };
    
    return false; // Default fallback
  } catch (error) {
    console.error("Failed to getIsMainerCreationStopped:", error);
    return false; // Default to not stopped if we can't determine
  };
};

export const getPauseWhitelistMainerCreationFlag = async () => {
  try {
    // Check if the method exists before calling it
    if (!storeState.gameStateCanisterActor.getPauseWhitelistMainerCreationFlag) {
      console.warn("getPauseWhitelistMainerCreationFlag method not available, defaulting to not paused");
      return false;
    }
    
    let response = await storeState.gameStateCanisterActor.getPauseWhitelistMainerCreationFlag();
    
    if ('Ok' in response) {
      return response.Ok.flag;
    } else if ('Err' in response) {
      console.error("Error in getPauseWhitelistMainerCreationFlag:", response.Err);
      return false; // Default to not paused if we can't determine
    };
  } catch (error) {
    console.error("Failed to getPauseWhitelistMainerCreationFlag:", error);
    return false; // Default to not paused if we can't determine
  };
};

export const getIsWhitelistPhaseActive = async (isRetry=false) => {
  try {
    // For testing: manually enable/disable whitelist phase
    return true;  // 👈 Change this to true/false to enable/disable whitelist phase
    
    /*
    // For production: uncomment this when backend function is available
    let response = await storeState.gameStateCanisterActor.getIsWhitelistPhaseActive();
    
    if ('Ok' in response) {
      return response.Ok.flag;
    } else if ('Err' in response) {
      console.error("Error in getIsWhitelistPhaseActive:", response.Err);
      if (isRetry) {
        return false; // Some issue occurred so indicate no whitelist phase as a measure of precaution
      } else {
        console.error("Trying again");
        setTimeout(() => {
          return getIsWhitelistPhaseActive(true);          
        }, 2000);
      };
    };
    */
  } catch (error) {
    console.error("Failed to getIsWhitelistPhaseActive:", error);
    if (isRetry) {
      return false; // Some issue occurred so indicate no whitelist phase as a measure of precaution
    } else {
      console.error("Trying again");
      setTimeout(() => {
        return getIsWhitelistPhaseActive(true);          
      }, 2000);
    };
  };
};
