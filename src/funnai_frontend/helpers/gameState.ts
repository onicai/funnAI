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

export const getIsProtocolActive = async (isRetry=false) => {
  try {
    let response = storeState.gameStateCanisterActor.getPauseProtocolFlag();
    
    if ('Ok' in response) {
      let isPaused = response.Ok.flag;
      return !isPaused;
    } else if ('Err' in response) {
      console.error("Error in getPauseProtocol:", response.Err);
      if (isRetry) {
        return false; // Some issue occurred so indicate that the protocol is not active as a mesure of precaution
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
      return false; // Some issue occurred so indicate that the protocol is not active as a mesure of precaution
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
        return true; // Some issue occurred so indicate to stop as a mesure of precaution
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
      return true; // Some issue occurred so indicate to stop as a mesure of precaution
    } else {
      console.error("Trying again");
      setTimeout(() => {
        return getIsMainerCreationStopped(mainerType, true);          
      }, 2000);
    };
  };
};
