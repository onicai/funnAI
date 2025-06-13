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
