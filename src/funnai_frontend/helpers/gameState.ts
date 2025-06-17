import {
  store
} from "../stores/store";

let storeState;
store.subscribe((value) => storeState = value);

export const getSharedAgentPrice = async () => {
  try {
    let response = storeState.gameStateCanisterActor.getPriceForShareAgent();
    
    if ('Ok' in response) {
      return response.Ok.price;
    } else if ('Err' in response) {
      console.error("Error in getSharedAgentPrice:", response.Err);
      return -1;
    };
  } catch (error) {
    console.error("Failed to getSharedAgentPrice:", error);
    return -1;
  };
};

export const getOwnAgentPrice = async () => {
  try {
    let response = storeState.gameStateCanisterActor.getPriceForOwnMainer();
    
    if ('Ok' in response) {
      return response.Ok.price;
    } else if ('Err' in response) {
      console.error("Error in getSharedAgentPrice:", response.Err);
      return -1;
    };
  } catch (error) {
    console.error("Failed to getSharedAgentPrice:", error);
    return -1;
  };
};

export const getWhitelistAgentPrice = async () => {
  try {
    let response = storeState.gameStateCanisterActor.getPriceForShareAgent();
    
    if ('Ok' in response) {
      return Math.floor(response.Ok.price * 0.5);
    } else if ('Err' in response) {
      console.error("Error in getWhitelistAgentPrice:", response.Err);
      return -1;
    };
  } catch (error) {
    console.error("Failed to getWhitelistAgentPrice:", error);
    return -1;
  };
};

export const getIsProtocolActive = async (isRetry=false) => {
  try {
    let response = storeState.gameStateCanisterActor.getPauseProtocolFlag();
    
    if ('Ok' in response) {
      let isPaused = response.Ok.flag;
      return !isPaused;
    } else if ('Err' in response) {
      console.error("Error in getPauseProtocol:", response.Err);
      if (isRetry) {
        return false;
      } else {
        console.error("Trying again");
        setTimeout(() => {
          return getIsProtocolActive(true);          
        }, 3000);
      };
    };
  } catch (error) {
    console.error("Failed to getPauseProtocol:", error);
    if (isRetry) {
      return false;
    } else {
      console.error("Trying again");
      setTimeout(() => {
        return getIsProtocolActive(true);          
      }, 3000);
    };
  };
};

export const getIsMainerCreationStopped = async (mainerType, isRetry=false) => {
  try {
    let input = mainerType === 'Own' ? { 'Own' : null } : { 'ShareAgent' : null };
    let response = storeState.gameStateCanisterActor.shouldCreatingMainersBeStopped(input);
    
    if ('Ok' in response) {
      return response.Ok.flag;
    } else if ('Err' in response) {
      console.error("Error in getIsMainerCreationStopped:", response.Err);
      if (isRetry) {
        return true;
      } else {
        console.error("Trying again");
        setTimeout(() => {
          return getIsMainerCreationStopped(mainerType, true);          
        }, 2000);
      };
    };
  } catch (error) {
    console.error("Failed to getIsMainerCreationStopped:", error);
    if (isRetry) {
      return true;
    } else {
      console.error("Trying again");
      setTimeout(() => {
        return getIsMainerCreationStopped(mainerType, true);          
      }, 2000);
    };
  };
};

export const getPauseWhitelistMainerCreationFlag = async (isRetry=false) => {
  try {
    return false;
  } catch (error) {
    console.error("Failed to getPauseWhitelistMainerCreationFlag:", error);
    if (isRetry) {
      return true;
    } else {
      console.error("Trying again");
      setTimeout(() => {
        return getPauseWhitelistMainerCreationFlag(true);          
      }, 2000);
    };
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
