import { Actor, HttpAgent } from "@dfinity/agent";

// In-memory cache for anonymous actors
const actorCache = new Map<string, any>();

export const createAnonymousActorHelper = (canisterId: string, idl: any) => {
  const cacheKey = `${canisterId}-${idl.name || "anonymous"}`;
  if (actorCache.has(cacheKey)) {
    return actorCache.get(cacheKey);
  }

  // IC_HOST is injected by vite.config.ts. Locally it points at the icp-cli managed
  // network, whose gateway port is ephemeral and so cannot be hardcoded.
  const agent = new HttpAgent({
    host:
      process.env.DFX_NETWORK === "local"
        ? process.env.IC_HOST
        : "https://icp0.io",
  });

  if (process.env.DFX_NETWORK === "local") {
    agent.fetchRootKey();
  }

  const actor = Actor.createActor(idl as any, {
    agent,
    canisterId,
  });

  actorCache.set(cacheKey, actor);
  return actor;
};
