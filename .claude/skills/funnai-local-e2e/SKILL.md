---
name: funnai-local-e2e
description: Stand up and drive the full funnAI application on a local Internet Computer network - all Motoko canisters, the LLM, and the Svelte frontend on ONE icp-cli network - so backend and UI behaviour can be tested end to end without touching mainnet. Use when asked to run, test, debug, reproduce, or demo funnAI locally; when verifying a change to a canister or the frontend actually works; or before proposing that something is fixed. Do NOT use for mainnet operations - this environment cannot and must not reach production.
---

# funnAI local end-to-end environment

Brings the whole application up locally so you can exercise it for real instead of
reasoning about it. Run everything from the funnAI repo root in the `llama_cpp_canister`
conda env.

## 🚫 Local only

This environment never touches mainnet, and neither should you while using it.

- `e2e/icp.yaml` declares **only** a `local` environment — `-e prd`, `-e testing`,
  `-e development`, `-e demo` all fail here.
- `scripts/lib/icp_helpers.py` **refuses** mainnet installs, upgrades, top-ups, controller
  changes and wallet spends, raising `MainnetWriteBlocked`.
- One caveat: icp-cli always provides an implicit `ic` environment. It has no id mappings
  in this project, so `-e ic` would not touch an existing funnAI canister — it would
  *create new ones on mainnet and spend real cycles*. **Never pass `-e ic` from `e2e/`.**

Redeploying anything to mainnet is a separate, deliberate project — see `WASM-HASHES.md`.

## Commands

```bash
make e2e-up          # build + deploy everything, incl. the gguf upload (slow, ~10+ min)
make e2e-up-fast     # same but --skip-model: no inference, ~3 min
make e2e-status      # URLs + per-canister health
make e2e-test        # system-level checks (deployed / healthy / wired / serving)
make e2e-reset       # wipe local network state and rebuild
make e2e-down        # stop the network
```

`make e2e-up-fast` is the right default while iterating on anything that is not inference.

## Why there is a separate `e2e/` project

icp-cli runs **one local network per project root**. In production every canister has its
own project (`src/funnai_backend/`, `PoAIW/src/*/`), so deploying them the obvious way
gives each its own isolated replica — canisters that are individually healthy and unable
to call each other. Worse, each replica allocates ids from the same sequence, so two
canisters end up with the *same* id in their respective stores.

`e2e/icp.yaml` exists to own **one** network and **one** id store. It builds nothing: every
canister is `pre-built`, pointing at the artifact its own project produced. The harness
builds those first, then installs them all here with an explicit `--wasm` path.

## Reading back the environment

The gateway port is **ephemeral** (`gateway.port: 0`) and changes on every start. Never
hardcode it:

```bash
cd e2e && icp network status -e local --json     # .gateway_url / .api_url
icp canister status <name> -e local --id-only    # a canister's id
```

`make e2e-status` prints the frontend URL, the local Internet Identity URL, and every
canister id and health state in one screen.

## Identities

| identity | role |
| ------------ | ------------------------------------------------------- |
| `default`    | the local admin — deploys everything, holds all admin roles |
| `e2e-player` | an ordinary player, for exercising non-admin paths      |

**`default` is the admin locally — not your mainnet identity.** The identity you imported
for mainnet work is a controller *there*, and has no rights on this throwaway local
network; calling as it returns `Err = Unauthorized`, which is easy to misread as "empty
result". The harness sets `icp_helpers.DEFAULT_IDENTITY` to `default` for exactly this
reason. If a local call returns an empty list or an `Unauthorized` variant, check which
identity you used before assuming a bug.

## Driving the UI

The frontend is served at `http://funnai_frontend.local.localhost:<port>/`.

Internet Identity is passkey-based — mainnet `id.ai` **and** the local instance — and the
approval is a native OS dialog outside the page DOM, so it **cannot** be completed through
chrome-devtools-mcp. Use the local dev sign-in path instead; see the global `browser-mcp`
skill, which covers both the technique and how to attach to Chrome.

Hand off to `browser-mcp` for the actual browser driving rather than duplicating it here.

## What to check after a change

- backend logic → `make e2e-test`, plus the canister's own `make smoketest`
- canister-to-canister wiring → `make e2e-test` (it verifies registration, not just health)
- inference → needs `make e2e-up` (not `-fast`), then exercise challenge/response/judging
- frontend → rebuild into `e2e/dist` and redeploy: the harness does this, or
  `ICP_ENV=local npx vite build --outDir e2e/dist --emptyOutDir && cd e2e && icp deploy funnai_frontend -e local -y`

## Known failure modes

| symptom | cause |
| ------------------------------------------------ | ----------------------------------------------- |
| `IC0207` / "out of cycles" on `load_model`        | `icp deploy` seeds only ~0.5T. The harness tops the LLM up to 20T; if you deployed by hand, do the same. |
| `Err = Unauthorized` where you expected data      | wrong identity — use `default` locally (see above). |
| `llmCanisterIds` empty after wiring               | a controller must be an admin **and** a canister-controller of the LLM *before* `add_llm_canister`; the reverse order fails silently unless the response is checked. |
| `Model not yet loaded`                            | you ran `make e2e-up-fast`. Use `make e2e-up`. |
| a script hangs with no output                     | an `icp canister call` with no `'()'` argument opened the interactive builder. |
| `plugin dir '../dist' is not a safe relative path`| the asset-canister recipe rejects `..`; build into `e2e/dist`. |
| `the local network for this project is not running` | you are in the wrong project dir. The app's network belongs to `e2e/`; `icp_helpers.use_project()` handles this in Python. |

## Limits worth stating out loud

The local network is not mainnet. Cycle economics, subnet behaviour, and NNS/CMC-dependent
paths differ, and inference is the same wasm but a far smaller machine. If something cannot
be exercised here, say so plainly rather than reporting a green run — and add it to the
handover list for the mainnet project.
