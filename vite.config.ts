import { svelte } from "@sveltejs/vite-plugin-svelte";
import { defineConfig, loadEnv } from "vite";
import { execFileSync } from "child_process";
import path from "path";
import fs from "fs";
// PWA plugin removed to solve caching issues

// Load environment variables from .env file
const mode = process.env.NODE_ENV || "development";
const env = loadEnv(mode, process.cwd(), "");

// Which icp.yaml environment to build for: local | prd | testing | development | demo.
// ICP_ENV is the icp-cli name for it; DFX_NETWORK is still accepted so existing shell
// aliases and CI invocations keep working.
const icpEnv =
  env.ICP_ENV || process.env.ICP_ENV || env.DFX_NETWORK || process.env.DFX_NETWORK || "local";
const isDev = icpEnv === "local";

// ---------------------------------------------------------------------------
// Canister ids
//
// Under dfx these came from ./canister_ids.json (or .dfx/local/canister_ids.json), keyed
// {canister: {network: id}}. icp-cli instead keeps one flat {canister: id} file per
// environment, and each canister belongs to the project that owns it:
//
//   .icp/data/mappings/<env>.ids.json   committed mainnet ids
//   .icp/cache/mappings/<env>.ids.json  local ids (disposable, recreated per network)
//
// The root project owns only funnai_frontend, so the backend ids are read from their own
// projects. That keeps a single source of truth -- the old duplicate root store had already
// drifted (it disagreed with PoAIW/src/Api about api_canister on `development`).
// ---------------------------------------------------------------------------
const ID_SOURCES: Record<string, string> = {
  funnai_frontend: ".",
  funnai_backend: "src/funnai_backend",
  api_canister: "PoAIW/src/Api",
  game_state_canister: "PoAIW/src/GameState",
};

// Fixed mainnet system canisters. Previously pulled with `dfx deps pull`, which icp-cli
// has no equivalent for -- and needs none, since these ids never change.
const SYSTEM_CANISTER_IDS: Record<string, string> = {
  internet_identity: "rdmx6-jaaaa-aaaaa-aaadq-cai",
  cycles_ledger: "um5iw-rqaaa-aaaaq-qaaba-cai",
  icp_ledger_canister: "ryjl3-tyaaa-aaaaa-aaaba-cai",
};

function readCanisterId(project: string, canister: string): string | undefined {
  // Locally, ALL ids come from this project's own network.
  //
  // icp-cli runs one local network per project, so src/funnai_backend/ and PoAIW/src/*/
  // each have their OWN replica with their own id space -- ids that are meaningless here
  // and even collide with each other (two projects both get the first id their replica
  // hands out). The frontend can only talk to canisters on the network it is served from,
  // so for local we look exclusively in the root project's own mapping. Deploying the
  // backends into this one network is what `make e2e-up` does.
  //
  // A managed network keeps its ids in the disposable cache, not in data/.
  const candidates = isDev
    ? // The whole app is deployed onto ONE local network by `make e2e-up`, whose project
      // is e2e/. Fall back to this project's own store for a frontend-only local deploy.
      ["e2e/.icp/cache/mappings/local.ids.json", ".icp/cache/mappings/local.ids.json"]
    : [`${project}/.icp/data/mappings/${icpEnv}.ids.json`];
  for (const rel of candidates) {
    try {
      const ids = JSON.parse(fs.readFileSync(path.join(__dirname, rel)).toString());
      if (ids[canister]) return ids[canister];
    } catch {
      /* try the next candidate */
    }
  }
  return undefined;
}

const canisterIds: Record<string, string> = { ...SYSTEM_CANISTER_IDS };
for (const [canister, project] of Object.entries(ID_SOURCES)) {
  const id = readCanisterId(project, canister);
  if (id) canisterIds[canister] = id;
  else console.warn(`⚠️  No canister ID found for '${canister}' on environment '${icpEnv}'`);
}
console.log(`🌐 Environment: ${icpEnv}`);
console.log(`📋 Canister IDs: ${JSON.stringify(canisterIds, null, 2)}`);

// The generated code in src/declarations/* reads process.env.CANISTER_ID_<NAME>, so keep
// emitting exactly those names. This strange way of JSON.stringifying is required by vite.
const canisterDefinitions = Object.entries(canisterIds).reduce(
  (acc, [name, id]) => ({
    ...acc,
    [`process.env.${name.toUpperCase()}_CANISTER_ID`]: JSON.stringify(id),
    [`process.env.CANISTER_ID_${name.toUpperCase()}`]: JSON.stringify(id),
  }),
  {},
);

// ---------------------------------------------------------------------------
// Local replica URL
//
// dfx served a fixed port (4943). icp-cli assigns an ephemeral one (gateway.port: 0 in
// icp.yaml) that changes on every `icp network start`, so it must be read back rather than
// hardcoded anywhere.
// ---------------------------------------------------------------------------
function localReplicaUrl(): string {
  // Try the e2e project first: `make e2e-up` runs the whole app on that one network.
  // Fall back to this project's own network for a frontend-only local deploy.
  for (const cwd of [path.join(__dirname, "e2e"), __dirname]) {
    try {
      const out = execFileSync("icp", ["network", "status", "-e", "local", "--json"], {
        cwd,
        encoding: "utf-8",
        stdio: ["ignore", "pipe", "ignore"],
      });
      // icp reports the url WITH a trailing slash; strip it, or callers that append
      // "/api/v3/..." produce "//api/v3", which the replica rejects with a 400.
      return JSON.parse(out).api_url.replace(/\/$/, "");
    } catch {
      /* try the next project */
    }
  }
  console.warn("⚠️  No local network is running. Start one with `make e2e-up`.");
  return "http://127.0.0.1:8000";
}

const icHost = isDev ? localReplicaUrl() : "https://icp0.io";
// Local Internet Identity, served by the managed network because icp.yaml sets `ii: true`.
const iiUrl = isDev
  ? `${icHost.replace("//", "//id.ai.")}/authorize`
  : "https://identity.ic0.app/#authorize";

// See guide on how to configure Vite at:
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    target: "es2020",
    rollupOptions: {
      output: {
        // Default Vite hashing for cache busting
        manualChunks: {
          // Vendor chunks for large libraries
          webllm: ["@mlc-ai/web-llm"],
          dfinity: [
            "@dfinity/agent",
            "@dfinity/auth-client",
            "@dfinity/candid",
            "@dfinity/principal",
            "@dfinity/identity",
            "@dfinity/ledger-icp",
            "@dfinity/utils",
          ],
          "qr-scanner": ["html5-qrcode", "qrcode"],
          "ui-libs": ["svelte-spa-router", "lucide-svelte", "svelte-portal"],
          markdown: ["marked"],
        },
      },
    },
  },
  //publicDir: "./src/funnai_frontend/public",
  publicDir: "./src/funnai_frontend/assets",
  server: {
    host: true,
    fs: {
      allow: ["."],
    },
    //__________Local vs Mainnet Development____________
    proxy: {
      // Proxy /api to the local replica. Its port is ephemeral, so it is resolved above
      // rather than hardcoded.
      "/api": {
        target: icHost,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "/api"),
      },
    },
  },
  define: {
    // Here we can define global constants
    // This is required for now because the generated declarations rely on process.env
    ...canisterDefinitions,
    "process.env.NODE_ENV": JSON.stringify(isDev ? "development" : "production"),
    // The declarations branch on DFX_NETWORK !== "ic" to decide whether to fetch the root
    // key, so it must stay "local" locally and a mainnet name otherwise.
    "process.env.DFX_NETWORK": JSON.stringify(icpEnv),
    "process.env.ICP_ENV": JSON.stringify(icpEnv),
    // Replaces the hardcoded http://localhost:4943 / identity URLs in the app code.
    "process.env.IC_HOST": JSON.stringify(icHost),
    "process.env.II_URL": JSON.stringify(iiUrl),
    global: process.env.NODE_ENV === "development" ? "globalThis" : "global",
  },
});
