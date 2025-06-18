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
    // Fixed whitelist price of 0.01 ICP for debugging
    return 0.01;
  } catch (error) {
    console.error("Failed to getWhitelistAgentPrice:", error);
    return 0.01; // Fallback value in case of error
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
    
    let input = mainerType === 'Own' ? { 'Own' : null } : { 'ShareAgent' : null };
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
    return false;
  } catch (error) {
    console.error("Failed to getPauseWhitelistMainerCreationFlag:", error);
    return false;
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
