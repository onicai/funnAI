# Developer guide: moving funnAI from dfx to icp-cli

Audience: the onicai team. This is what you need to do to your local machine, and what
changes in day-to-day work, now that funnAI and PoAIW run on **icp-cli** instead of dfx.

`dfx` is deprecated. Its successor is `icp` (icp-cli).

| dfx                 | icp-cli                                                                                  |
| ------------------- | ---------------------------------------------------------------------------------------- |
| `dfx.json`          | `icp.yaml`                                                                               |
| `canister_ids.json` | `.icp/data/mappings/{environment}.ids.json`, environment = `prd`/`testing`/`development` |

Development & Deployment will now be done from a new conda environment: `funnAI`

### What is a "project"?

The word comes up constantly below, and it has a precise meaning in icp-cli:

> **A project is a folder containing an `icp.yaml`.**

It matters because a project owns three things, and every `icp` command resolves them from
whichever project you are standing in:

1. **which canisters exist by name** — the `canisters:` block in its `icp.yaml`
2. **its canister ids** — `.icp/data/mappings/<env>.ids.json` (mainnet, committed) and
   `.icp/cache/mappings/local.ids.json` (local, disposable)
3. **its own local network** — icp-cli runs one replica *per project*, not one shared
   replica as dfx did

`icp` finds the project by walking up from your current directory. Outside one, commands
that need any of the three fail with `failed to locate project directory`.

**funnAI is unusual: it has 16 projects, not one.** The repo root, `e2e/`,
`src/funnai_backend/`, each of the nine `PoAIW/src/*/` canisters, and the four
`PoAIW/llms/*/` folders each have their own `icp.yaml` — so each has its own id store and
its own local replica. That is why the instructions below keep saying "from folder X":
`cd`-ing to the right project is a real step, not a formality.

**`e2e/` is new, and is not like the other fifteen.** They each own a canister; `e2e/` owns
no source and builds nothing. It exists purely to give the *whole* application one network
and one id store to be deployed onto together — the thing a single shared `dfx start` replica
used to provide for free, and which one-network-per-project takes away. Every canister in its
`icp.yaml` is `pre-built`, pointing at the artifact one of the other projects produced. See
[§3 Running the whole application](#running-the-whole-application).

To see what a project declares, read its `icp.yaml`. That file is short and is the source of
truth; it is where you change things.

---

## 1. One-time machine setup

```bash
# icp-cli, the wasm post-processor, and mops.
# @icp-sdk/ic-wasm is NOT optional: the Motoko recipe shells out to it, and its version
# changes the module hash, so it is pinned.
npm install -g @icp-sdk/icp-cli@1.2.0 @icp-sdk/ic-wasm@0.11.0 ic-mops@2.13.2

node --version      # must be >= 22 (dfx only needed 20)
icp --version       # 1.2.0
```

Python side. There is now a single `funnAI` conda environment, and a single
`funnAI/requirements.txt` that pulls in everything: the vendored llama_cpp_canister tooling
(icpp-pro, icp-py-core), the PoAIW canister-test dependencies, and the admin/monitoring
script packages.

```bash
conda create --name funnAI python=3.13     # first time only
conda activate funnAI
python --version                           # must be >= 3.13

# from folder: funnAI   (requires PoAIW to be cloned inside it)
pip install -r requirements.txt
```

funnAI work previously used the `llama_cpp_canister` conda env, which needed three
separate `pip install` runs from three different folders. Use `funnAI` for funnAI from now
on. Keep the `llama_cpp_canister` env -- it is still the right environment for working in
the llama_cpp_canister repo itself.

`PoAIW/README-setup.md` remains the authoritative first-time setup (clone layout, conda,
mops, the gguf download). This guide only covers what the dfx -> icp-cli move changed.

### Identity migration — do not skip this

icp-cli keeps its **own** identity store. It does not import dfx's, and its own `default`
identity is a *different principal* from the one you have been using with dfx.

Import **your own** identity — substitute the name you use with dfx (`dfx identity list`
shows it; `dfx identity whoami` shows the active one):

```bash
MY_ID=$(dfx identity whoami)          # or type the name you want to migrate

dfx identity export "$MY_ID" > "/tmp/$MY_ID.pem"
icp identity import "$MY_ID" --from-pem "/tmp/$MY_ID.pem" && rm "/tmp/$MY_ID.pem"
icp identity default "$MY_ID"

# verify — these two must print the SAME principal
dfx identity get-principal --identity "$MY_ID"
icp identity principal --identity "$MY_ID"
```

`icp identity default` is global and persistent — set it once and every icp command uses
it from then on. Nothing in this repo hardcodes an identity, and nothing changes your
default behind your back.

Also create a plaintext `default` identity, which the test suite needs:

```bash
icp identity new default --storage plaintext
```

`--storage plaintext` is **required**, not a convenience: `icp identity export` on a
keyring-backed identity opens a password prompt and hangs the test run.

### Keep dfx installed — for exactly one command

`scripts/upgrade_llms.py` still calls `dfx sns prepare-canisters add-nns-root`. icp-cli has
no `sns` subcommand at all, so this is the single, deliberate, documented dfx dependency.
Do not uninstall dfx, and do not start using it for anything else.

---

## 2. Command translation

| task                           | dfx                                                 | icp                                                             |
| ------------------------------ | --------------------------------------------------- | --------------------------------------------------------------- |
| start / stop local network     | `dfx start --background` / `dfx stop`               | `icp network start -d` / `icp network stop`                     |
| clean restart                  | `dfx start --clean`                                 | `icp network stop && rm -rf .icp/cache && icp network start -d` |
| deploy                         | `dfx deploy X --network prd`                        | `icp deploy X -e prd -y`                                        |
| call                           | `dfx canister call X m '(...)' --network prd`       | `icp canister call X m '(...)' -e prd`                          |
| call a query                   | (auto-detected)                                     | `... --query`                                                   |
| canister id                    | `dfx canister id X --network prd`                   | `icp canister status X -e prd --id-only`                        |
| status                         | `dfx canister status X --network prd`               | `icp canister status X -e prd`                                  |
| module hash (not a controller) | `dfx canister info X --network ic`                  | `icp canister status X -n ic -p`                                |
| logs                           | `dfx canister logs X --network prd`                 | `icp canister logs X -e prd`                                    |
| controllers                    | `dfx canister update-settings X --add-controller P` | `icp canister settings update X --add-controller P`             |
| cycles balance                 | `dfx wallet balance`                                | `icp cycles balance -e prd`                                     |
| identity                       | `dfx identity whoami` / `get-principal`             | `icp identity default` / `icp identity principal`               |

Three things to internalise:

- **`--query` is not auto-detected.** dfx worked out whether a method was a query; icp sends
  an update call unless you say `--query`. On the monitoring loops that poll hundreds of
  canisters this is roughly a 2x difference. But check first: `health` is a query on our
  canisters, **`ready` is not**.
- **A call with no argument needs an explicit `'()'`.** dfx defaulted to it. icp instead
  opens an interactive argument builder, which will hang a script.
- **Environments and networks are two different things, and `-e` / `-n` select them.**
  This is the one genuinely new concept versus dfx, where `--network` meant both.

  A **network** is a replica to talk to. There are only two here:
  `local` (declared in each `icp.yaml`, a throwaway replica) and `ic` (mainnet, built in).

  An **environment** is a *named set of canister ids* on one of those networks. funnAI
  declares four — `local`, `prd`, `testing`, `development` — and the last three all run on
  the `ic` network. They differ only in which ids they point at, which is exactly what dfx's
  extra "networks" really were.

  There is a fifth, **`ic`**, which icp-cli always provides implicitly — you will not find
  it in any `icp.yaml` here. It has no canister ids, so `-e ic` would not reach an existing
  funnAI canister — it would *create new ones on mainnet*. Use `-e prd` for production.

  ```
  environment          network      canister ids live in
  -----------          -------      --------------------
  local          -->   local        .icp/cache/mappings/local.ids.json   (throwaway)
  prd            -->   ic     \
  testing        -->   ic      |    .icp/data/mappings/<env>.ids.json    (committed)
  development    -->   ic     /
  ```

  From that, the rules follow:

  | you are targeting   | flag                | requires                                                       |
  | ------------------- | ------------------- | -------------------------------------------------------------- |
  | a canister **name** | `-e <env>` ONLY     | being inside that project (it reads its `icp.yaml` + id store) |
  | a **principal**     | `-e <env>`          | being inside a project                                         |
  | a **principal**     | `-n ic`             | nothing — works from any folder                                |
  | a **principal**     | `-n local`          | being inside a project (`local` is declared there)             |
  | a **principal**     | `-n <url> -k fetch` | nothing, but `--root-key` is mandatory for a URL               |

  Rule of thumb: **use `-e <env>` for everything while you are inside a project** — it is
  the only thing that works with names, and it works with principals too. Reach for
  `-n ic` only when you have a bare principal and no project.

---

## 3. The local network

icp-cli runs **one local network per project**, keyed by the project root — so
`src/funnai_backend/`, each `PoAIW/src/*/`, and the funnAI root each get their own replica.
Separate git worktrees get their own too.

Every `icp.yaml` here sets `gateway.port: 0`, so the OS picks a free port and **the port
changes on every start**. Never hardcode it:

```bash
icp network start -d                  # prints e.g. "Network started on port 63840"
icp network status -e local --json    # ask the running network for it again
```

`network status --json` returns `gateway_url` (open this in a browser; canisters are served
at `http://<canister-id>.<host>:<port>/`) and `api_url` (what agents and tooling call). Both
come back **with a trailing slash** — strip it before joining a path on, or you get
`//api/v3` and the replica answers 400. `scripts/lib/icp_helpers.py` already does this.

There is no `--clean`. The equivalent is:

```bash
icp network stop && rm -rf .icp/cache && icp network start -d
```

### 🚨 Never `rm -rf .icp`

Only `.icp/cache/` is disposable. **`.icp/data/mappings/<env>.ids.json` holds the mainnet
canister ids** — it is the replacement for `canister_ids.json`, and it is committed. Delete
`.icp` and you lose the ids for every environment.

This exact mistake wiped the mappings during the upstream icpp-pro migration. Only ever
remove `.icp/cache`.

### Running the whole application locally

See README-setup.md how to deploy the whole application to a local replica.

## 4. Where everything moved

| dfx                                 | icp-cli                                                  |
| ----------------------------------- | -------------------------------------------------------- |
| `dfx.json`                          | `icp.yaml`                                               |
| `canister_ids.json`                 | `.icp/data/mappings/<env>.ids.json` (committed)          |
| `networks` in dfx.json              | `environments` in icp.yaml                               |
| `.dfx/<net>/canisters/<n>/<n>.wasm` | `.icp/cache/artifacts/<n>`                               |
| `.env` (`output_env_file`)          | gone — vite reads the mappings directly                  |
| dfx's bundled `moc`                 | `[toolchain] moc` in `mops.toml`                         |
| `dfx deps pull`                     | nothing — fixed principals, plus `ii: true` for local II |

`PoAIW/llms/llama_cpp_canister/` is vendored at **v0.16.0**. The prd canisters still run
v0.11.0 — upgrading them is a mainnet operation, done separately. The three fleet projects
(`PoAIW/llms/{Challenger,Judge,mAIner}/`) now carry `icp.yaml` + `.icp/data/mappings/`, and
declare only the `llm_N` slots that actually have ids rather than all 55 dfx placeholders.

Two families of canisters deliberately have **no** `icp.yaml` entry and are addressed by
principal instead:

- the ~744 `mainer_ctrlb_canister_N` → `PoAIW/src/mAIner/mainer_ids.json`
- the ICRC token ledger + index → `PoAIW/src/Token*/token_ids.json`

`icp canister install <principal> --wasm ... ` works with no project and no declaration.

---

### Letting Claude Code drive the browser

That last point is worth setting up, because it is what makes an AI agent able to verify a
frontend change instead of guessing at it: sign in, click through a flow, read the console,
screenshot the result — unattended.

The repo ships a **`.mcp.json`** declaring the `chrome-devtools` MCP server, so there is no
`claude mcp add` to run — cloning is enough, and Claude Code will ask you to approve the
server on first use. All that is left is the browser itself, which a repo cannot launch for
you:

```bash
# a DEDICATED Chrome profile -- add to ~/.zshrc
# Use a function, not an alias: an alias re-tokenizes after expansion and splits
# "Google Chrome" on its space, giving `exit 127: command not found`.
chrome-claude-dev() { "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-claude-dev" >/dev/null 2>&1 & }

# verify
chrome-claude-dev
curl -s http://127.0.0.1:9222/json/version    # JSON with a "Browser" field
claude mcp list                               # chrome-devtools -> Connected
```

Keep this profile separate from your everyday browser and do not sign into real accounts in
it: the remote-debugging port lets any local process drive that Chrome. Your normal Chrome
is unaffected and can stay open. Reset with `rm -rf ~/chrome-claude-dev/`.

Two funnAI-specific quirks worth knowing before you watch an agent fumble them: the login
modal is mounted **six times** in the DOM and does not appear in the accessibility snapshot,
so its buttons have to be clicked via `evaluate_script` filtered to the visible copy; and
Internet Identity opens in a **popup**, i.e. a separate page that has to be selected before
it can be driven.

---

## 8. Ops scripts

The scripts keep their existing interface — `--network local|ic|testing|development|prd`
still works exactly as before.

Everything now routes through **`scripts/lib/icp_helpers.py`**. If you are writing or
fixing a script, use it rather than shelling out yourself:

```python
import icp_helpers
icp_helpers.canister_id("game_state_canister", "prd")
icp_helpers.balance(cid, "prd")
icp_helpers.module_hash(cid)                       # no controller rights needed
icp_helpers.call(cid, "getAdminRoles", env="prd")  # DECODED python objects
icp_helpers.call_text(cid, "health", "()", env="prd", query=True)
```

`icp_helpers.call()` exists because **icp-cli has no `--output json`**. dfx could decode a
Candid response to JSON and ~60 call sites relied on it; icp's `--json` returns a wrapper
around the raw response instead, so the decode now happens client-side via icp-py-core.

### Mainnet write guard

`icp_helpers` **refuses** state-changing mainnet operations — install, upgrade, top-up,
controller changes, wallet sends:

```
MainnetWriteBlocked: Refusing to install (upgrade) on 'prd': that is mainnet.
```

This is deliberate: the migration is a tooling change, and redeploying is a separate
project. Reads are never restricted. When that project starts, lift the guard explicitly:

```bash
ICP_ALLOW_MAINNET_WRITES=1 ./scripts/upgrade_mainers.sh --network prd ...
```

Some monitoring endpoints are declared as update methods but only read (notably
`recursive_dir_content_update`); those call sites pass `allow_mainnet=True` with a comment
saying why.

### Cycles

icp-cli has no cycles-wallet concept. `dfx wallet send` became a direct call to the wallet
canister's own endpoint, so behaviour and funds are unchanged:

```bash
icp canister call jh35u-eqaaa-aaaag-abf3a-cai wallet_send \
  '(record { canister = principal "<target>"; amount = 500000000000 : nat64 })' -e prd
```

Moving the wallet's balance to the cycles ledger is a separate, later decision.

---

## 9. Troubleshooting

| symptom                                                 | cause and fix                                                                                                                                       |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `port 8000 is in use by the local network of ...`       | another project's replica. Ours all use `gateway.port: 0`; check the project's icp.yaml.                                                            |
| a script hangs with no output                           | an `icp canister call` with no `'()'` argument opened the interactive builder. Add `'()'`.                                                          |
| `The replica returned ... 400` on an upload             | trailing slash: `icp network status` reports `.../`, and appending `/api/v3` gives `//api/v3`. `.rstrip("/")` it.                                   |
| `could not find ID for canister`                        | the canister is not in `.icp/data/mappings/<env>.ids.json`, or you are in the wrong project dir.                                                    |
| `Caller ... is not allowed to read the canister status` | you are running as an identity that is not a controller — usually icp's `default` rather than your imported one. Check with `icp identity default`. |
| a password prompt when exporting an identity            | it is keyring-backed. Recreate with `--storage plaintext`.                                                                                          |
| CI: `403 rate limit exceeded` from api.github.com       | `icp network start` downloads the network-launcher; set `ICP_CLI_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.                                        |
| `libdbus-1.so.3: cannot open shared object file`        | Linux/CI only: `apt-get install -y libdbus-1-3 libssl3`.                                                                                            |
| `mops build` fails: *No Motoko canisters found*         | `[canisters.<name>]` in `mops.toml` must exactly match the `name` in `icp.yaml`.                                                                    |
| `docker-verify-wasm` says MISMATCH                      | expected until that canister is redeployed — see `WASM-HASHES.md`.                                                                                  |
