import { Actor, HttpAgent } from "@dfinity/agent";

// Imports and re-exports candid interface
import { idlFactory } from "./game_state_canister.did.js";
export { idlFactory } from "./game_state_canister.did.js";

/* CANISTER_ID is replaced by webpack based on node environment
 * Note: canister environment variable will be standardized as
 * process.env.CANISTER_ID_<CANISTER_NAME_UPPERCASE>
 * beginning in dfx 0.15.0
 */

// Fallback canister IDs based on network
const CANISTER_IDS = {
  ic: "xzpy6-hiaaa-aaaaj-az4pq-cai",
  prd: "r5m5y-diaaa-aaaaa-qanaa-cai",
  demo: "4tr6r-mqaaa-aaaae-qfcta-cai",
  testing: "vpa37-giaaa-aaaam-qdxeq-cai",
  development: "ciqqv-4iaaa-aaaag-auara-cai",
  local: ""
};

// Determine network - check NODE_ENV and DFX_NETWORK
const network = process.env.DFX_NETWORK || (process.env.NODE_ENV === "production" ? "ic" : "local");
const fallbackId = CANISTER_IDS[network] || CANISTER_IDS.ic;

export const canisterId =
  process.env.CANISTER_ID_GAME_STATE_CANISTER || fallbackId;

export const createActor = (canisterId, options = {}) => {
  const agent = options.agent || new HttpAgent({ ...options.agentOptions });

  if (options.agent && options.agentOptions) {
    console.warn(
      "Detected both agent and agentOptions passed to createActor. Ignoring agentOptions and proceeding with the provided agent."
    );
  }

  // Fetch root key for certificate validation during development
  if (process.env.DFX_NETWORK !== "ic") {
    agent.fetchRootKey().catch((err) => {
      console.warn(
        "Unable to fetch root key. Check to ensure that your local replica is running"
      );
      console.error(err);
    });
  }

  // Creates an actor with using the candid interface and the HttpAgent
  return Actor.createActor(idlFactory, {
    agent,
    canisterId,
    ...options.actorOptions,
  });
};

export const game_state_canister = canisterId ? createActor(canisterId) : undefined;
