import {
  canisterId as backendCanisterId,
  idlFactory as backendIdlFactory,
} from "../../declarations/funnai_backend";

import {
  canisterId as gameStateCanisterId,
  idlFactory as gameStateIdlFactory,
} from "../../declarations/game_state_canister";

import {
  canisterId as apiCanisterId,
} from "../../declarations/api_canister";

import { ICRC2_IDL as icrc2IDL } from "../helpers/idls/icrc2.idl.js";
import { idlFactory as icpIDL } from "../helpers/idls/icp.idl.js";
import { idlFactory as swapPoolIDL } from "../helpers/idls/swappool.idl.js";
import { idlFactory as cmcIDL } from "../helpers/idls/cmc.idl.js";

export const canisterIds = {
  backendCanisterId,
  gameStateCanisterId,
  apiCanisterId
};

export const canisterIDLs = {
  backendIdlFactory,
  gameStateIdlFactory,
  icrc1: icrc2IDL,
  icrc2: icrc2IDL,
  ICP: icpIDL,
  swapPool: swapPoolIDL,
  cmc: cmcIDL,
};

export const HOST =
  process.env.NODE_ENV !== "development"
    ? "https://ic0.app"
    : "http://localhost:4943";

/** Memo prefix used by mAIner payment / top-up / burn-rate flows. */
export const MEMO_PAYMENT_PROTOCOL: number[] = [173];
