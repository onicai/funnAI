import { Actor, HttpAgent } from "@dfinity/agent";

// Imports and re-exports candid interface
import { idlFactory } from "./funnai_backend.did.js";
export { idlFactory } from "./funnai_backend.did.js";

/* CANISTER_ID is replaced by webpack based on node environment
 * Note: canister environment variable will be standardized as
 * process.env.CANISTER_ID_<CANISTER_NAME_UPPERCASE>
 * beginning in dfx 0.15.0
 */

// Fallback canister IDs based on network
const CANISTER_IDS = {
  ic: "yekds-uqaaa-aaaaj-az5la-cai",
  prd: "6wp2z-paaaa-aaaaa-qau7q-cai",
  demo: "dtxtp-ciaaa-aaaah-are5a-cai",
  testing: "62vhh-cyaaa-aaaam-qd2wq-cai",
  development: "bom4f-cyaaa-aaaah-qqa2a-cai",
  local: ""
};

// Determine network - check NODE_ENV and DFX_NETWORK
const network = process.env.DFX_NETWORK || (process.env.NODE_ENV === "production" ? "ic" : "local");
const fallbackId = CANISTER_IDS[network] || CANISTER_IDS.ic;

export const canisterId =
  process.env.CANISTER_ID_FUNNAI_BACKEND || fallbackId;

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

export const funnai_backend = canisterId ? createActor(canisterId) : undefined;
