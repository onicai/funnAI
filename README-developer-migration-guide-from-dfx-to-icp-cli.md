# Developer guide: moving funnAI from dfx to icp-cli

Audience: the onicai team. This is what you need to do to your local machine, and what
changes in day-to-day work, now that funnAI and PoAIW run on **icp-cli** instead of dfx.

`dfx` is deprecated. Its successor is `icp` (icp-cli). Everything in both repos —
`icp.yaml`, canister ids, builds, tests, the ops scripts — has moved over.

Three things will surprise you most:

1. **The local network is per-project and on a random port.** There is no single shared
   replica any more, and no fixed `4943`.
2. **`--network prd` now names an icp.yaml *environment*.** The names you already use
   (`local`, `prd`, `testing`, `development`, `demo`) are unchanged — they just mean
   something slightly different underneath.
3. **icp does not create a `default` identity for you, and does not know about dfx's.**
   This is the step people get wrong.

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

Python side (unchanged conda env, newer icpp-pro):

```bash
conda activate llama_cpp_canister
python --version                      # must be >= 3.11
pip install -r PoAIW/requirements.txt # now icpp-pro>=5.6.0
```

### Identity migration — do not skip this

icp-cli keeps its **own** identity store. It does not import dfx's, and its own `default`
identity is a *different principal* from the one you have been using with dfx. A command
that runs as the wrong principal is not a controller, and the failure is sometimes silent.

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

Nothing in this repo hardcodes an identity name. The scripts and Makefiles use whatever
`icp identity default` is set to, i.e. yours.

### Make your identity stick — use `icp identity default`, not `~/.zshrc`

Set it once, and every icp command uses it from then on:

```bash
icp identity default "$MY_ID"
icp identity default            # prints it back
```

**Do not export `ICP_IDENTITY` in `~/.zshrc` instead.** icp-cli has no identity environment
variable — `--identity` is the only way to select one, and the only env vars it reads are
`ICP_ENVIRONMENT`, `ICP_NETWORK` and `ICP_PROJECT_ROOT`. `ICP_IDENTITY` is a convention of
*this repo's* Python helpers only, so exporting it globally gives you a split brain:

| | honours `ICP_IDENTITY` | honours `icp identity default` |
| --------------------------------- | :---: | :---: |
| `scripts/*.py` (via `icp_helpers`) | yes   | yes (as the fallback) |
| an `icp` command you type yourself | no    | yes |
| the Makefiles (they use `IDENTITY`)| no    | yes |
| icpp-pro's pytest smoketests       | no    | yes |
| the vendored llama_cpp uploader    | no    | yes |

Everything honours `icp identity default`; only one row honours the env var. Setting it in
your shell profile means your scripts act as one principal while your hand-typed commands
act as another — and that failure usually shows up as a silent empty result rather than an
error.

Keep `ICP_IDENTITY` / `IDENTITY` for what they are good at: a deliberate, one-off override.

```bash
ICP_IDENTITY=my-deploy-key ./scripts/monitor_balance.sh --network prd   # python scripts
make docker-verify-wasm IDENTITY=my-deploy-key                          # Makefiles
```

Nothing in this repo changes your default identity behind your back. The local smoketests
and `make e2e-up` need a `default` identity to *exist*, so they create one — but they name
it explicitly on each command rather than calling `icp identity default`, which is global
and persistent and would otherwise leave you running as a non-controller afterwards.

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

| task | dfx | icp |
| ------------------------- | ------------------------------------------- | ------------------------------------------------- |
| start / stop local network | `dfx start --background` / `dfx stop`      | `icp network start -d` / `icp network stop`       |
| clean restart             | `dfx start --clean`                         | `icp network stop && rm -rf .icp/cache && icp network start -d` |
| deploy                    | `dfx deploy X --network prd`                | `icp deploy X -e prd -y`                          |
| call                      | `dfx canister call X m '(...)' --network prd` | `icp canister call X m '(...)' -e prd`          |
| call a query              | (auto-detected)                             | `... --query`                                     |
| canister id               | `dfx canister id X --network prd`           | `icp canister status X -e prd --id-only`          |
| status                    | `dfx canister status X --network prd`       | `icp canister status X -e prd`                    |
| module hash (not a controller) | `dfx canister info X --network ic`     | `icp canister status X -n ic -p`                  |
| logs                      | `dfx canister logs X --network prd`         | `icp canister logs X -e prd`                      |
| controllers               | `dfx canister update-settings X --add-controller P` | `icp canister settings update X --add-controller P` |
| cycles balance            | `dfx wallet balance`                        | `icp cycles balance -e prd`                       |
| identity                  | `dfx identity whoami` / `get-principal`     | `icp identity default` / `icp identity principal` |

Three gotchas worth internalising:

- **`--query` is not auto-detected.** dfx worked out whether a method was a query; icp sends
  an update call unless you say `--query`. On the monitoring loops that poll hundreds of
  canisters this is roughly a 2x difference. But check first: `health` is a query on our
  canisters, **`ready` is not**.
- **A call with no argument needs an explicit `'()'`.** dfx defaulted to it. icp instead
  opens an interactive argument builder, which will hang a script.
- **`-e <env>` for names, `-n ic` for bare principals outside a project.** Resolving a
  *name* needs the project's icp.yaml; a principal does not, but then icp needs to be told
  the network another way.

---

## 3. The local network

icp-cli runs **one local network per project**, keyed by the project root — so
`src/funnai_backend/`, each `PoAIW/src/*/`, and the funnAI root each get their own replica.
Separate git worktrees get their own too.

Every `icp.yaml` here sets `gateway.port: 0`, so the OS picks a free port and **the port
changes on every start**. Never hardcode it:

```bash
icp network start -d                       # prints e.g. "Network started on port 63840"
icp network status -e local --json         # .gateway_url / .api_url
```

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

---

## 4. Where everything moved

| dfx | icp-cli |
| --------------------------------- | ------------------------------------------------------- |
| `dfx.json`                        | `icp.yaml` |
| `canister_ids.json`               | `.icp/data/mappings/<env>.ids.json` (committed) |
| `networks` in dfx.json            | `environments` in icp.yaml |
| `.dfx/<net>/canisters/<n>/<n>.wasm` | `.icp/cache/artifacts/<n>` |
| `.env` (`output_env_file`)        | gone — vite reads the mappings directly |
| dfx's bundled `moc`               | `[toolchain] moc` in `mops.toml` |
| `dfx deps pull`                   | nothing — fixed principals, plus `ii: true` for local II |

`PoAIW/llms/llama_cpp_canister/` is vendored at **v0.16.0**. The prd canisters still run
v0.11.0 — upgrading them is a mainnet operation, done separately. The three fleet projects
(`PoAIW/llms/{Challenger,Judge,mAIner}/`) now carry `icp.yaml` + `.icp/data/mappings/`, and
declare only the `llm_N` slots that actually have ids rather than all 55 dfx placeholders.

Two families of canisters deliberately have **no** `icp.yaml` entry and are addressed by
principal instead:

- the 744 `mainer_ctrlb_canister_N` → `PoAIW/src/mAIner/mainer_ids.json`
- the `llm_N` slots → `PoAIW/llms/*/llm_ids.json`

`icp canister install <principal> --wasm ... ` works with no project and no declaration,
which is what makes that possible — and it keeps a 745-entry config file from existing.

---

## 5. Building, and the wasm-hash change

```bash
make build-wasm          # local, fast
make docker-build-wasm   # the reproducible build
make docker-verify-wasm  # compare against what is deployed
```

The build chain changed: `dfx build` → `icp build` → the `@dfinity/motoko` recipe →
`mops build` + `ic-wasm shrink`. That is a different compiler and a different pipeline, so
**every Motoko wasm hash changed**. `docker-verify-wasm` will report MISMATCH for every
canister until it is redeployed. That is expected, and redeploying is a **separate project**
— see `WASM-HASHES.md`, which tracks the old hash, the new hash, and what has been
redeployed.

Two things you will trip over:

- **A local `icp build` on macOS never matches the Docker build.** Motoko codegen *is*
  deterministic across platforms — every wasm section is byte-identical — except the
  90-byte `moc:version` metadata section, which the recipe stamps with `moc --version`, and
  moc reports a platform-specific build hash. The Docker linux/amd64 build is canonical.
- **`ic-wasm` version changes the hash.** Its `shrink` pass rewrites the element section;
  0.9.11 vs 0.11.0 differ by 1288 bytes from identical source. Hence the pin.

---

## 6. Running the tests

```bash
conda activate llama_cpp_canister
cd PoAIW/src/Challenger
make smoketest                                    # full cycle, fresh network
pytest -vv --network local test/test_challenger_canister.py
```

`--network` now names an **icp.yaml environment**, not a dfx network. `conftest.py` did not
change.

If a new assertion fails on whitespace, that is `candid_compat`: icp's Candid printer wraps
records over several lines, prints the top level as `( <v> , )`, and omits dfx's trailing
`;` before `}`. Every test dir has a `candid_compat.py` whose `norm()` flattens both forms:

```python
from .candid_compat import call_canister_api, norm
assert response == norm(expected_response)
```

Responses come back already normalized, so substring assertions need no change.

---

## 7. Frontend

```bash
npm run replica     # icp network start -d
npm run build       # ICP_ENV=local|prd|testing|development
npm run deploy      # icp deploy funnai_frontend -e local -y
```

`vite.config.ts` no longer imports `dfx.json`. It reads canister ids from each owning
project's `.icp/data/mappings/<env>.ids.json` and the local replica URL from
`icp network status`, then injects them as the same `process.env.CANISTER_ID_*` names the
committed `src/declarations/` already expect.

**`dfx generate` is gone and has no equivalent.** `src/declarations/` is committed, so
nothing needs it during a normal build. If a canister interface changes, regenerate with
`didc bind -t js` (or adopt `@icp-sdk/bindgen`) and commit the result.

Locally, Internet Identity is served by the managed network itself (`ii: true` in
`icp.yaml`) at `http://id.ai.localhost:<port>/authorize`.

---

## 8. Ops scripts

The scripts keep their existing interface — `--network local|ic|testing|development|demo|prd`
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

| symptom | cause and fix |
| ------------------------------------------------- | ------------------------------------------------------ |
| `port 8000 is in use by the local network of ...`  | another project's replica. Ours all use `gateway.port: 0`; check the project's icp.yaml. |
| a script hangs with no output                      | an `icp canister call` with no `'()'` argument opened the interactive builder. Add `'()'`. |
| `The replica returned ... 400` on an upload        | trailing slash: `icp network status` reports `.../`, and appending `/api/v3` gives `//api/v3`. `.rstrip("/")` it. |
| `could not find ID for canister`                   | the canister is not in `.icp/data/mappings/<env>.ids.json`, or you are in the wrong project dir. |
| `Caller ... is not allowed to read the canister status` | you are running as an identity that is not a controller — usually icp's `default` rather than your imported one. Check `icp identity default`, or pass `ICP_IDENTITY=<your-identity>`. |
| a password prompt when exporting an identity       | it is keyring-backed. Recreate with `--storage plaintext`. |
| CI: `403 rate limit exceeded` from api.github.com  | `icp network start` downloads the network-launcher; set `ICP_CLI_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`. |
| `libdbus-1.so.3: cannot open shared object file`   | Linux/CI only: `apt-get install -y libdbus-1-3 libssl3`. |
| `mops build` fails: *No Motoko canisters found*    | `[canisters.<name>]` in `mops.toml` must exactly match the `name` in `icp.yaml`. |
| `docker-verify-wasm` says MISMATCH                 | expected until that canister is redeployed — see `WASM-HASHES.md`. |
