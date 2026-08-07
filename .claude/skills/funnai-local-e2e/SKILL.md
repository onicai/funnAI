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

- `e2e/icp.yaml` declares **only** a `local` environment — `-e prd`, `-e testing` and
  `-e development` all fail here.
- `scripts/lib/icp_helpers.py` **refuses** mainnet installs, upgrades, top-ups, controller
  changes and wallet spends, raising `MainnetWriteBlocked`.
- One caveat: icp-cli always provides an implicit `ic` environment. It has no id mappings
  in this project, so `-e ic` would not touch an existing funnAI canister — it would
  *create new ones on mainnet and spend real cycles*. **Never pass `-e ic` from `e2e/`.**

Redeploying anything to mainnet is a separate, deliberate project — see `WASM-HASHES.md`.

## Commands

```bash
# network lifecycle
make e2e-start        # start, reusing .icp/cache
make e2e-start-clean  # wipe .icp/cache, then start a fresh replica
make e2e-stop         # stop the network -- deletes nothing
make e2e-clean        # stop + wipe ALL local state incl. build artifacts (never .icp/data)

# deploy -- the network must already be running, these will NOT start it
make e2e-install      # first deploy onto a fresh network (canisters must be empty)
make e2e-reinstall    # wipe canister state and deploy again
make e2e-upgrade      # keep canister state; gguf is not re-uploaded

make e2e-status       # URLs + per-canister health
make e2e-test         # system-level checks (deployed / healthy / wired / serving)
```

From cold: `make e2e-start-clean && make e2e-install`.

All three deploy targets take `SHARE_AGENTS=N` (default 1) — see "mAIners are bought"
below.

Add `NO_GGUF=1` to `e2e-install` / `e2e-reinstall` to skip the gguf upload — that is the
slow step (~10+ min with it, ~2 min without). Use it whenever the task is not inference.
`e2e-upgrade` never uploads the gguf: an upgrade keeps stable memory, so the model file is
still there.

Deploys rebuild through the **reproducible Docker build** by default, so the wasm matches
`WASM-HASHES.md`. **Docker must be running** — if it is not, ask the user to start it
rather than working around it. `NO_DOCKER=1` falls back to the local `icp build` (~130s vs
~290s cold), but its output is machine-dependent and all 10 canisters differ between the
two, so never quote a wasm hash from a `NO_DOCKER=1` run. Never claim a wasm hash from a default local run.

`e2e-install` only works on empty canisters, so a second run fails with
`IC0514 ... canister is not empty` — reach for `e2e-reinstall` to get a clean app while
keeping the replica and the canister ids.

## Why there is a separate `e2e/` project

icp-cli runs **one local network per project root**. In production every canister has its
own project (`src/funnai_backend/`, `PoAIW/src/*/`), so deploying them the obvious way
gives each its own isolated replica — canisters that are individually healthy and unable
to call each other. Worse, each replica allocates ids from the same sequence, so two
canisters end up with the *same* id in their respective stores.

`e2e/icp.yaml` exists to own **one** network and **one** id store. It builds nothing: every
canister is `pre-built`, pointing at the artifact its own project produced. The harness
builds those first, then installs them all here with an explicit `--wasm` path.

## mAIners are bought, not installed

Every canister in `e2e/icp.yaml` is deployed with `icp canister install` — **except the
ShareAgents**. A mAIner is bought: the player pays ICP to `game_state_canister`, which asks
`mainer_creator_canister` to create the canister through the CMC and wire it up. The local
network runs the real CMC and the real ICP ledger, so the harness uses that path rather than
shortcutting it, and `e2e-player` (not the admin) does the buying.

```bash
make e2e-install SHARE_AGENTS=3
```

- ShareAgents have **no id in the project's id store** — the CMC allocated it, and
  `game_state_canister` is the only record. `make e2e-status` lists them as `share_agent_N`.
- **`e2e-reinstall` cannot re-install them**: `-m reinstall` wipes `game_state_canister`'s
  memory of every mAIner, so the harness buys fresh ones and orphans the old. `e2e-upgrade`
  keeps that state and really does upgrade the same agents via `mainer_creator_canister`.
- After a create or re-install, `mainer_creator_canister` configures the agent
  **asynchronously** — it answers `health` well before `getMainerCanisterType` stops saying
  `#Own`. Poll, do not check once.
- **`health` cannot tell you an upgrade worked.** A mAIner whose upgrade the IC rejected
  keeps running its old code and answers health perfectly. The signal is
  `game_state_canister`'s status for that agent: it is set to
  `#Other("Controller Upgrade in Progress")` up front and only cleared when
  `mainer_creator_canister` reports back. **Stuck there = the install was rejected**, and
  `icp canister logs <mainer_creator_canister>` says why. Nothing surfaces in the call
  response.
- Those getters are gated on being a **controller** of the agent, and the controllers are
  `mainer_creator_canister` and the owner — *not* the admin. Query them as `e2e-player`.
- The agents run **no LLM**: they pull challenges from `game_state_canister` and queue work
  on `mainer_service_canister` (the ShareService), which is the only mAIner that calls
  `llm_0`, then calls the agent back so it can submit.

### A signed-in user cannot own a harness-bought mAIner

`e2e-player` is a PEM key; an Internet Identity login derives a different principal, so a
signed-in user's fleet is empty. The harness therefore **lists each new ShareAgent on the
marketplace** so a human can buy it in the UI and genuinely own it.

The listing call is ICRC-37 repurposed — `token_id` is the **price in e8s** and
`approval_info.memo` is the **mAIner address** as UTF-8. Nothing in the signature says so.

The buyer needs local ICP, and an II principal has none (only identities present at network
start were seeded), so this step is required before the purchase can go through:

```bash
make e2e-fund PRINCIPAL=<their II principal>   # AMOUNT=100 by default
```

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

| identity       | role                                                          |
| -------------- | ------------------------------------------------------------- |
| `funnAI-local` | the local admin — deploys everything, holds all admin roles   |
| `e2e-player`   | an ordinary player, buys mAIners, exercises non-admin paths   |

**`funnAI-local` is the admin here — not your mainnet identity, and not the machine
default.** `icp identity default` reports a machine-wide setting that for most developers is
their MAINNET identity; it has no rights on this throwaway network, and calling as it returns
`Err = Unauthorized`, which is easy to misread as "empty result". The harness names its
identity explicitly on every call and sets `icp_helpers.DEFAULT_IDENTITY` to `funnAI-local`.
It never runs `icp identity default <name>`, which is global and persistent.

`make smoketest` in a canister's own project uses the same identity: each Makefile exports
`ICPP_PRO_TEST_IDENTITY = funnAI-local`, which icpp-pro >= 6.0.0 turns into `--identity` on
every icp command. Deployer and tester must match — the controller is whoever installed the
canister, so a mismatch flips every `is_controller` assertion.

If a local call returns an empty list or `Unauthorized`, check which identity you used
before assuming a bug.

## Driving the UI

The frontend is served at `http://funnai_frontend.local.localhost:<port>/`.

The repo ships a `.mcp.json` declaring the `chrome-devtools` MCP server, so it is available
in any clone with no `claude mcp add`. It attaches to a Chrome started with
`--remote-debugging-port=9222` — if `curl -s http://127.0.0.1:9222/json/version` returns
nothing, ask the user to run `chrome-claude-dev`. Setup is in `README-setup.md`, under
"Letting Claude Code drive the browser".

**You can sign in yourself — no human needed.** The local Internet Identity that `ii: true`
provisions is a *test build*: it does not use real passkeys. Instead it asks for a **seed
index** via a plain `window.prompt`, which `mcp__chrome-devtools__handle_dialog` answers
directly. Seed index N always yields the same principal, so `0` is "user A", `1` is
"user B", stable across restarts.

(Mainnet `id.ai` *is* passkey-gated and cannot be driven this way. Only the local instance
behaves like this.)

### The click path — first time on a fresh network

The identity must be **created** before it can be signed in with. This is the step that
trips people up:

1. On the app, click **Connect**, then **Internet Identity**. A popup opens — it is a
   separate page, so `list_pages` + `select_page`.
2. Click **Create** (under "Create new identity"). **Not** "Sign in with passkey".
3. **Create with passkey** → type any name → **Create identity**.
4. Answer the `Enter seed index` prompt with `0`:
   `handle_dialog(action="accept", promptText="0")`.
5. Click **Continue**.

Afterwards, `localStorage.isAuthed === "internetidentity"` on the app page, and the nav
shows **Menu** instead of **Connect**.

On later sign-ins with an already-created seed, **Sign in with passkey** → `0` works.

> ⚠️ Clicking **Sign in with passkey** on a seed that was never created fails silently: the
> popup bounces back to the sign-in screen, and the only clue is
> `TypeError: Cannot read properties of undefined (reading 'anchor_number')` in the console.
> If sign-in "does nothing", this is why — create the identity first.

The login modal is mounted six times in the DOM and is not exposed in the a11y snapshot, so
`take_snapshot` will not show its buttons. Click them with `evaluate_script`, filtering to
the visible one:

```js
[...document.querySelectorAll('a,button')]
  .filter(e => /Internet Identity/i.test(e.textContent) && e.getClientRects().length)[0].click()
```

Hand off to `browser-mcp` for the browser driving itself rather than duplicating it here.

## What to check after a change

- backend logic → `make e2e-test`, plus the canister's own `make smoketest`
- canister-to-canister wiring → `make e2e-test` (it verifies registration, not just health)
- inference → deploy WITHOUT `NO_GGUF=1`, then exercise challenge/response/judging
- frontend → rebuild into `e2e/dist` and redeploy: the harness does this, or
  `ICP_ENV=local npx vite build --outDir e2e/dist --emptyOutDir && cd e2e && icp deploy funnai_frontend -e local -y`

## Known failure modes

| symptom                                             | cause                                                                                                                                                                |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `IC0207` / "out of cycles" on `load_model`          | `icp deploy` seeds only ~0.5T. The harness tops the LLM up to 20T; if you deployed by hand, do the same.                                                             |
| `Err = Unauthorized` where you expected data        | wrong identity — use `funnAI-local` locally (see above).                                                                                                                  |
| `llmCanisterIds` empty after wiring                 | a controller must be an admin **and** a canister-controller of the LLM *before* `add_llm_canister`; the reverse order fails silently unless the response is checked. |
| `Model not yet loaded`                              | you deployed with `NO_GGUF=1`. Redeploy without it.                                                                                                                  |
| a script hangs with no output                       | an `icp canister call` with no `'()'` argument opened the interactive builder.                                                                                       |
| `plugin dir '../dist' is not a safe relative path`  | the asset-canister recipe rejects `..`; build into `e2e/dist`.                                                                                                       |
| `the local network for this project is not running` | you are in the wrong project dir. The app's network belongs to `e2e/`; `icp_helpers.use_project()` handles this in Python.                                           |
| a mAIner stuck at `"Controller Upgrade in Progress"` | `mainer_creator_canister` could not install the code -- read its `icp canister logs`. The known cause, an EOP upgrade sent without `wasm_memory_persistence`, is fixed; anything else is new. |
| `failed to prepare extraction snapshot ... parent snapshot ... does not exist` | Docker BuildKit corruption, not your code. Seen twice, at different canisters, on both a full and a nearly-empty Docker. Run `docker buildx prune -f`, then re-run `make e2e-install` -- the network stays up, so only the deploy repeats. |

## Limits worth stating out loud

The local network is not mainnet, but it is less limited than it looks: it installs the **real
ICP ledger** at `ryjl3-tyaaa-aaaaa-aaaba-cai` and the **real CMC** at
`rkp4c-7iaaa-aaaaa-aaaca-cai`, and seeds your identity with ICP and cycles at every start. So
ICP and cycles paths run for real — only the value is synthetic. mAIner creation, marketplace
purchases and ICP→CMC→cycles top-ups are all exercisable locally (verified: 1 ICP mints ~3.52T
cycles).

What genuinely cannot be exercised here:

- **FUNNAI flows** — no FUNNAI ledger is deployed locally.
- **ICPSwap** (`c5u7l-…`, so FUNNAI↔ICP and BOB/ckBTC top-ups) — bound at compile time in
  `PoAIW/src/common/Types.mo`, and icp-cli has no `--specified-id`, so it cannot be deployed
  at that id. Calls fail with `CanisterNotFound`; they are caught, not trapped.
- **Mainnet sign-in** — `id.ai` delegations are canister signatures certified by mainnet's root
  key, which a local replica cannot verify. Use the local II at `id.ai.localhost:<port>`.
- **HTTPS outcalls** to Coinbase / ic-api / api.icpswap.com, so dashboard market data and the
  Api pricing timer's off-chain legs.
- Cycle economics and subnet behaviour still differ, and inference is the same wasm on a far
  smaller machine.

If something cannot be exercised here, say so plainly rather than reporting a green run — and
add it to the handover list for the mainnet project.
