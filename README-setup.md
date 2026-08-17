# funnAI Setup instructions

## Clone

Clone the following repos to your local disk using this folder structure:

```
|-funnAI       (https://github.com/onicai/funnAI)
  |-PoAIW      (https://github.com/onicai/PoAIW)
```

Note: The folder structure is important, because the scripts use relative paths.

## Miniconda

Create the `funnAI` conda environment. `funnAI/requirements.txt` is the single entry
point -- it pulls in the python dependencies for the vendored llama_cpp_canister tooling (icpp-pro, icp-py-core), the
PoAIW canister-test dependencies, and the admin/monitoring scripts.

```bash
# install Miniconda on your system

# create the conda environment
conda create --name funnAI python=3.13
conda activate funnAI

# from folder: funnAI   (requires PoAIW to be cloned first -- see Clone above)
pip install -r requirements.txt
```

## Install icp-cli

```bash
npm install -g @icp-sdk/icp-cli@1.2.0 @icp-sdk/ic-wasm@0.11.0 ic-mops@2.13.2
mops toolchain use moc 1.4.1

node --version   # must be >= 22
icp --version    # 1.2.0
```

## Docker

Required, not optional: every deploy target compiles each Motoko canister inside a pinned
toolchain image, so `make e2e-install` / `e2e-upgrade` / `e2e-reinstall` all fail without a
running Docker. See [The build is reproducible by default](#the-build-is-reproducible-by-default).

Install [Docker Desktop](https://docs.docker.com/desktop/) (macOS/Windows) or Docker Engine
(Linux), then **start it** — the daemon has to be up, not just installed.

```bash
# verify the daemon is actually running, not just that the CLI exists
docker info > /dev/null && echo "docker is running"

docker --version
```

Give it enough headroom in Docker Desktop → Settings → Resources. The toolchain images are a
few GB and are rebuilt on every deploy (~150 s; see
[The toolchain image is rebuilt on every deploy](#the-toolchain-image-is-rebuilt-on-every-deploy)
for why, and for `KEEP_BASE=1` to skip it while iterating).

The images are local-only and never pushed. `docker system prune -a` deletes them, which is
harmless — each project's `docker-build-wasm` notices and rebuilds rather than failing.

## Local identities

The local environment uses two icp-cli identities. **`make e2e-start` creates both for
you**, so for the normal loop there is nothing to do here — this section is what they are
and why, plus the commands if you want to create them by hand.

| identity       | role                                                                 |
| -------------- | --------------------------------------------------------------------- |
| `funnAI-local` | the local admin — deploys every canister and holds the admin roles    |
| `e2e-player`   | an ordinary player — buys mAIners, exercises the non-admin paths      |

```bash
icp identity new funnAI-local --storage plaintext
icp identity new e2e-player   --storage plaintext

# verify
icp identity list
icp identity principal --identity funnAI-local
```

Notes:

- **these identities are onlyused for setting up a local end-2-end deployment** they are
  NOT for deploying to mainnet.
- **Nothing here touches or uses your machine default.** `icp identity default` reports a
  machine-wide setting that you typically use for your identity that deploys to mainnet. 
  Every command in the scripts names its identity explicitly with `--identity`, and
  nothing ever runs `icp identity default <name>`, which is global and persistent.
- **`--storage plaintext` is required for these two identities.** The file uploaders sign locally, so
  they export the identity's key; a keyring-backed identity makes `icp identity export`
  open a password prompt and hang. These are disposable local keys with play money on a
  throwaway replica — do not use this for anything that holds value.
- **They must exist *before* the local replica starts.** The local ledger seeds 1,000,000 ICP to
  the identities that exist at that moment, and nothing afterwards. `make e2e-start` creates
  them first for exactly this reason. An identity created later has a zero balance and
  cannot buy anything.

## Download the LLMs from HuggingFace

Download the model `qwen2.5-0.5b-instruct-q8_0.gguf` from huggingface: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

Store it in: 
```
PoAIW/llms/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf
```

## Running the whole app locally

This is the everyday loop. The `e2e/` project exists to put the entire application on **one** network.

Run these from the funnAI repo root:

```bash
# network lifecycle  (e2e-start also creates the local identities, see above)
make e2e-start        # start, reusing whatever is in .icp/cache
make e2e-start-clean  # wipe .icp/cache, then start a fresh replica
make e2e-stop         # stop the network -- deletes nothing
make e2e-clean        # stop, then wipe ALL disposable local state

# deploy (the network must already be running)
make e2e-install   [NO_GGUF=1]   # first deploy onto a fresh network; gguf is uploaded by default
make e2e-reinstall [NO_GGUF=1]   # wipe canister state and deploy again; gguf is uploaded by default
make e2e-upgrade                 # keep canister state; the gguf is not re-uploaded by default
                                 # all three also take, each explained below:
                                 #   SHARE_AGENTS=N  how many mAIners to buy (default 1)
                                 #   KEEP_BASE=1     do not rebuild the toolchain images
                                 #   NO_DOCKER=1     local build; faster, non-canonical wasm

make e2e-status       # URLs, canister ids and per-canister health
make e2e-test         # run the backend pytest suites against this network

# send local ICP to a principal -- needed before a browser Internet Identity login can
# buy the listed mAIner, because an II principal starts with no ICP at all
make e2e-fund PRINCIPAL=<principal> [AMOUNT=100]
```

Starting the network and deploying canisters are separate steps on purpose. The deploy
targets **do not** start the network — if it is down they say so and stop, so you always
know whether you deployed onto reused state or a clean replica. From cold:

```bash
make e2e-start-clean && make e2e-install
```

That is all you need for the normal loop. [README-icp-cli.md](README-icp-cli.md) explains
the concepts underneath — projects, environments, where canister ids live — which you need
as soon as you run a single canister's tests or target a mainnet environment.

Operating a deployed environment — monitoring, timers, thresholds, archiving, mainnet
deploys — is in [README-operations.md](README-operations.md) (out of date, see its warning)
and [README-prd-upgrade-commands.md](README-prd-upgrade-commands.md).

### Which deploy mode?

The three deploy targets are the IC's three install modes, and the difference is what
happens to canister state:

| target          | mode        | canister state | canister ids | gguf                 | ShareAgents      |
| --------------- | ----------- | -------------- | ------------ | -------------------- | ---------------- |
| `e2e-install`   | `install`   | must be empty  | kept         | uploaded             | bought           |
| `e2e-reinstall` | `reinstall` | wiped          | kept         | uploaded (was wiped) | bought again     |
| `e2e-upgrade`   | `upgrade`   | kept           | kept         | already there        | upgraded         |

- **`e2e-install`** is the first deploy after `e2e-start-clean`. `install` mode requires an
  empty canister, so running it twice fails with `IC0514 ... canister is not empty` — use
  reinstall or upgrade instead.
- **`e2e-reinstall`** is the everyday "give me a clean app" command. It wipes each canister
  and installs fresh, but keeps the replica and the canister ids, so your browser tab and
  any ids you noted still work.
- **`e2e-upgrade`** is what the production runbook does: new code, existing state. Motoko
  canisters upgrade with `--wasm-memory-persistence keep`; the LLM is a C++ canister and
  does not take that flag.

The **gguf upload is the slow step**. `reinstall` wipes the LLM's file storage so the model
has to be uploaded again; `upgrade` keeps it, which is why upgrade never re-uploads. To skip
the upload when you do not need inference:

```bash
make e2e-install NO_GGUF=1
make e2e-reinstall NO_GGUF=1
```

Inference then returns `Model not yet loaded`, and a later `e2e-upgrade` will report that
there is no model to load — which is correct, not a failure.

Note that an upgrade clears `startTimerExecutionAdmin` and `startSendCyclesTimerAdmin` on
every canister that has them. The harness never arms those, so there is normally nothing to
restore — but if you armed either by hand, arm it again.

### mAIners are bought, not installed

Every canister listed by `make e2e-status` is deployed with `icp canister install` — except
the ShareAgents. A mAIner is not something you install; it is something a **player buys**.
In production that is: pay ICP to `game_state_canister`, which asks `mainer_creator_canister`
to create the canister through the cycles-minting canister and wire it up.

The local network runs the **real CMC and the real ICP ledger**, at their mainnet ids, so
that entire path works here — and `make e2e-install` uses it rather than shortcutting it.
The identity `e2e-player` (not the admin) pays 10 local ICP per mAIner, so the ownership
checks are genuinely exercised.

```bash
make e2e-install SHARE_AGENTS=3     # default is 1
```

Consequences worth knowing:

- A ShareAgent has **no entry in `e2e/icp.yaml`** and no id in the project's id store. The
  CMC allocated its id, and `game_state_canister` is the only place that records it —
  which is where `make e2e-status` reads them from.
- **`e2e-reinstall` cannot re-install them.** `-m reinstall` wipes `game_state_canister`'s
  stable memory, and with it every mAIner it knew about. The old agents are still on the
  replica but nothing points at them any more, so the harness says so and buys fresh ones.
  `e2e-upgrade` keeps that state, so it really does upgrade the same agents through
  `mainer_creator_canister` — the production path.
- The `e2e-player` identity has to **exist before the network starts** to be seeded with
  ICP; `make e2e-start` creates it for that reason. If you somehow end up with a player
  holding 0 ICP, `make e2e-start-clean && make e2e-install` fixes it.
- If a deploy stops with *"still `Controller Upgrade in Progress`"*, the upgrade was
  **rejected**, not slow. Nothing says so in the call response — read
  `icp canister logs $(icp canister status mainer_creator_canister -e local --id-only)`
  from `e2e/`. A mAIner whose upgrade the IC refused keeps running its old code and answers
  `health` normally, which is why the harness waits on `game_state_canister`'s status
  instead.
- The ShareAgents themselves run **no LLM**. They pull challenges from
  `game_state_canister` and queue the work on `mainer_service_canister` (the ShareService),
  which is the only mAIner that calls `llm_0`; it then calls the agent back and the agent
  submits the response.

### Owning a mAIner as a signed-in user

The harness buys its mAIners as `e2e-player`, which is a **PEM key on disk**. Signing in
through the browser with Internet Identity derives an entirely *different* principal, so a
signed-in user owns nothing and the UI shows them an empty fleet. There is no way around
that directly — the harness cannot produce an Internet Identity delegation.

So instead, every freshly bought ShareAgent is **put up for sale on the marketplace**, and
you buy it in the UI. That is the same path a real player uses to buy from another player,
so it exercises the marketplace rather than working around it.

**1. Deploy.** `make e2e-install` buys the mAIner as `e2e-player` and lists it at 1 ICP.

**2. Sign in** at the frontend URL that `make e2e-status` prints. On a fresh replica you must
**Create** the identity — see [Signing in locally](#signing-in-locally). Clicking "Sign in
with passkey" for a seed that was never created fails *silently*, which is the single most
confusing failure in this whole setup.

**3. Fund your principal.** Copy it from the UI, then:

```bash
make e2e-fund PRINCIPAL=<your II principal>     # AMOUNT=100 by default
```

> 🚨 **This step is not optional.** The local ledger hands its 1,000,000 ICP only to the
> identities that *already existed when the network started*. An Internet Identity principal
> is derived at sign-in, so it is never among them and starts at exactly zero. The purchase
> pulls the price from the buyer with `icrc2_transfer_from`, so without this the buy fails
> on payment — and nothing in the UI will tell you that an empty wallet was the reason.

**4. Buy the listed mAIner** in the marketplace. It is now genuinely yours: `ownedBy` is your
principal, you are a controller of the canister, and it appears in your fleet.

To see the listing from the CLI:

```bash
cd e2e && icp canister call game_state_canister getMarketplaceMainerListings '()' \
  -e local --query --identity funnAI-local
```

Two things worth knowing:

- **Only newly bought agents are listed.** Re-running a deploy will not re-list a mAIner you
  have already bought — by then you own it, and `e2e-player` cannot list someone else's.
- The listing call is **ICRC-37 repurposed**, which is worth knowing before you read the
  code and doubt yourself: in `icrc37_approve_tokens`, `token_id` is the **price in e8s**
  (floor `1_000_000` = 0.01 ICP) and `approval_info.memo` is the **mAIner's canister
  address** as UTF-8. Nothing in the signature hints at either.

### The toolchain image is rebuilt on every deploy

Each canister is compiled inside a pinned toolchain image — `poaiw-build:icp-1.2.0-moc-1.4.1`
for the PoAIW canisters, `funnai-build:…` for `funnai_backend` — built from
`docker/Dockerfile.base`. **Every deploy deletes those images first**, so the toolchain you
build in is always what the Dockerfile currently says.

The image tag already encodes the pinned versions, so bumping `moc` produces a new name and
therefore a new image on its own. What the deletion catches is the case the naming cannot:
an edit to `Dockerfile.base` that leaves the versions alone, where the stale image keeps its
name and would be silently reused.

Measured cost: **~150 s added to a full deploy** (458 s → 611 s). That is for *both* images
together, not each — the two `Dockerfile.base` files are near-identical, so the second image
reuses the first's layers almost entirely. For a fast iteration loop:

```bash
make e2e-upgrade KEEP_BASE=1
```

The canister wasm is the canonical artifact either way: the tool versions are pinned
regardless of whether the image was rebuilt. `KEEP_BASE=1` only trades away the guarantee
that an *un-versioned* Dockerfile edit has been picked up.

The images are also **local-only — they are never pushed anywhere**. A `docker system prune -a`
deletes them, and each project's `docker-build-wasm` notices and rebuilds automatically
rather than failing on a pull from a registry that has never had them.

### The build is reproducible by default

All three deploy targets **rebuild every Motoko canister**, and they do it through the
**reproducible Docker build**:

```
make docker-build-wasm      ->  <project>/out/<name>.wasm
```

That is the canonical artifact — the one `WASM-HASHES.md` records and `verify-wasm` checks —
so what you run locally is byte-for-byte what the release pipeline produces. **You need
Docker running**; the deploy stops with a clear message if it is not.

`NO_DOCKER=1` falls back to the local toolchain (`icp build`, into
`.icp/cache/artifacts/<name>`):

| | default | `NO_DOCKER=1` |
| ------------- | ------------------------------------ | ----------------------------- |
| build command | `make docker-build-wasm` | `icp build` |
| artifact | `out/<name>.wasm` | `.icp/cache/artifacts/<name>` |
| build time | **~290 s**, plus ~150 s for the base images | **~130 s** |
| hash | canonical — matches `WASM-HASHES.md` | machine-dependent |
| needs Docker  | yes | no |
| rebuilds the base images | yes (skip with `KEEP_BASE=1`) | n/a — does not use Docker |

Measured on an M-series Mac with `make e2e-install NO_GGUF=1` from `make e2e-clean`, so the
difference is the build alone. **The 160 s of canister build is cheaper than it looks**:
`--no-cache` only busts the wasm layer, while the dependency layers above the base image
stay cached, so each canister costs ~20 s.

The base-image rebuild is the separate ~150 s described in
[The toolchain image is rebuilt on every deploy](#the-toolchain-image-is-rebuilt-on-every-deploy)
— it is **not** a one-off first-run cost; it happens on every Docker deploy unless you pass
`KEEP_BASE=1`.

**Why reproducible is the default.** The two builds do not produce identical bytes. The
per-canister `Makefile` says so itself —

> `Wasm hash (SHA256) -- local build, differs from Docker on non-linux/amd64`

— and comparing the artifacts for all 10 canisters, **every one differs**. A local build is
therefore not evidence about a release artifact: a bug that only manifests in the Docker
wasm would not show up. At 160 s, paying for that certainty on every deploy is the better
default.

Reach for `NO_DOCKER=1` when Docker is unavailable, or when you are iterating hard on
Motoko and do not care about the hash:

```bash
make e2e-reinstall NO_DOCKER=1
```

Never quote a wasm hash produced that way. The LLM is unaffected either way — its wasm is a
vendored release binary, not built here.

### Starting completely over

`make e2e-clean` stops the network and removes **every** piece of disposable local state:
the `.icp/cache` of all 16 projects — local replica state, local canister ids *and build
artifacts* — plus `e2e/dist` and `dist`. It goes further than `e2e-start-clean`, which only
wipes the e2e project's cache and leaves compiled wasms in place.

Reach for it to prove a build works from cold, or to reclaim disk. Afterwards:

```bash
make e2e-clean
make e2e-start && make e2e-install     # ~10 min: base images, all 9 canisters, the gguf
```

Roughly: ~150 s for the toolchain base images, ~290 s for the nine canisters, and the rest
is the gguf upload. `NO_GGUF=1` removes the largest single chunk when you do not need
inference.

> 🚨 **It never touches `.icp/data`** — the committed mainnet canister ids for `prd`,
> `testing` and `development`. The command enumerates and prints each path it deletes, and
> asserts every one ends in `cache` or `dist`, precisely so it can never degrade into
> `rm -rf .icp`. It also leaves your local icp identities alone, since
> those are machine-wide.

### What the local network can and cannot test

**Real mechanics, fake assets.** The local network installs the *real* ICP ledger at
`ryjl3-tyaaa-aaaaa-aaaba-cai`, the *real* cycles minting canister at
`rkp4c-7iaaa-aaaaa-aaaca-cai` and the cycles ledger at `um5iw-rqaaa-aaaaq-qaaba-cai`, and
seeds your identity with ICP and cycles on every start. So ICP and cycles code paths execute
for real — only the value is synthetic.

| flow                                                | local | why                                                                        |
| --------------------------------------------------- | ----- | -------------------------------------------------------------------------- |
| challenge create → solve → judge → close → reward   | ✅    | including every cycles transfer                                            |
| mAIner creation and whitelist creation              | ✅    | 10 ICP for a ShareAgent, 1000 for an Own mAIner (half on the whitelist); every local identity starts with 1,000,000 |
| marketplace list / reserve / buy                    | ✅    | ICP, via `icrc2_transfer_from`                                             |
| top-ups: ICP → CMC → cycles                         | ✅    | verified: 1 ICP mints ~3.52T cycles locally                                |
| FUNNAI-denominated flows                            | ⚠️    | no FUNNAI ledger is deployed locally; it would have to be added            |
| ICPSwap (FUNNAI↔ICP, BOB and ckBTC top-ups)         | ❌    | `c5u7l-…` is bound at compile time and cannot be deployed at that id       |
| signing in with mainnet `id.ai`                     | ❌    | use the local Internet Identity at `http://id.ai.localhost:<port>/authorize` |
| anything of real value                              | ❌    | local play money throughout                                                |

Two consequences worth stating explicitly:

- **The local ICP is not your ICP.** It is a different ledger instance that happens to sit at
  the same canister id, with its own balances and its own block log. Nothing you do locally
  touches mainnet.
- **A local replica is a sealed IC.** Canisters on it cannot call mainnet canisters — the id
  is resolved in the local routing table, so a call to something that only exists on mainnet
  fails with `CanisterNotFound`. Mainnet `id.ai` cannot sign you in either: its delegations
  are canister signatures certified by mainnet's root key, which the local replica has no way
  to verify. That is what `ii: true` in `icp.yaml` is for.

### Signing in locally

`ii: true` gives the local network its own Internet Identity at
`http://id.ai.localhost:<port>/authorize` — no `dfx deps pull`, no separate deploy, nothing
to declare in `icp.yaml` beyond that one flag.

It is a **test build of II, and it does not use real passkeys**. Instead of a biometric
prompt it asks for a **seed index**: `0` is your first test user, `1` a second, and the same
index gives you the same user again for as long as the replica lives. (Mainnet `id.ai` is
genuinely passkey-based; only the local instance behaves this way.)

> ⚠️ **`e2e-start-clean` and `e2e-clean` wipe Internet Identity's state along with everything
> else in `.icp/cache`.** Every identity you created is gone, so you must **create seed 0
> again** on the new replica — and because that failure is silent (see below), it looks like
> sign-in is broken rather than like the anchor is missing. `e2e-install`, `e2e-reinstall`
> and `e2e-upgrade` do not touch the replica, so identities survive those.

**On a fresh replica you must _create_ the identity, not sign in:**

1. **Connect** → **Internet Identity** (a popup opens)
2. **Create** — under "Create new identity", *not* "Sign in with passkey"
3. **Create with passkey** → give it any name → **Create identity**
4. at the `Enter seed index` prompt, enter `0`
5. **Continue**

From then on, **Sign in with passkey** → `0` logs you straight back in.

> 🚨 **If sign-in appears to do nothing, this is why.** Clicking "Sign in with passkey" for
> a seed that was never created bounces silently back to the sign-in screen. The only clue
> is in the browser console:
> `TypeError: Cannot read properties of undefined (reading 'anchor_number')`.
> There is no on-screen error. Create the identity first.

Because the seed index is an ordinary `window.prompt` rather than an OS-level passkey
dialog, this flow is also fully scriptable — a browser-automation agent can sign itself in
without a human. That is not true of mainnet II.

### Letting Claude Code drive the browser

Combined with the seed-index sign-in above, this lets an AI agent exercise the whole app —
sign in, click through flows, read console errors — with no human at the keyboard. Setup is
one-time and takes a couple of minutes.

**The MCP server is already configured for you.** This repo ships a `.mcp.json` declaring
the `chrome-devtools` server, so cloning funnAI is enough — there is no `claude mcp add` to
run. Claude Code will ask you to approve the server the first time it starts; say yes.

That leaves one manual step, because a repo cannot launch your browser or edit your shell
config.

**A dedicated Chrome profile.** Keep this separate from your everyday browser: the
debugging port lets any local process drive it, so it should never hold real accounts.

Add to `~/.zshrc`:

```bash
chrome-claude-dev() { "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-claude-dev" >/dev/null 2>&1 & }
```

Use a **function, not an alias.** An alias re-tokenizes after expansion and splits
`Google Chrome` on its space, giving `exit 127: command not found`. A function parses once
at definition time and keeps the path quoted.

**Verify:**

```bash
chrome-claude-dev                              # launch the dedicated Chrome
curl -s http://127.0.0.1:9222/json/version     # must return JSON with a Browser field
claude mcp list                                # chrome-devtools -> ✔ Connected
```

Then point Claude at the app — `make e2e-status` prints the URL, and the port changes on
every network start, so read it back rather than reusing an old one.

**Things that bite:**

| symptom                                       | cause                                                                                  |
| --------------------------------------------- | --------------------------------------------------------------------------------------- |
| `exit 127: command not found`                 | you used an alias instead of a function                                                |
| Claude attaches to the wrong browser          | only one Chrome at a time may hold port 9222 — quit the other debug instance           |
| MCP connects but sees no pages                | the dedicated Chrome is not running; launch `chrome-claude-dev` first                  |
| the login modal's buttons are missing         | it is mounted six times in the DOM and is not in the a11y tree — click via `evaluate_script` |
| a click that opens Internet Identity "hangs"  | II opens a **popup**, i.e. a separate page — list the pages and select it              |

Reset the profile at any time with `rm -rf ~/chrome-claude-dev/`. Your normal Chrome is
unaffected and can stay open throughout.

---

## Internet Computer Resources

funnai is built and hosted on the Internet Computer. To learn more about it, see the following documentation available online:

- [Developer docs](https://internetcomputer.org/docs)
- [Motoko language guide](https://internetcomputer.org/docs/motoko/home)
- [Motoko base library](https://internetcomputer.org/docs/motoko/base)
- [icp-cli documentation](https://cli.internetcomputer.org)
- [mops, the Motoko package manager](https://mops.one/docs)

## Frontend-only local work

To run the **whole** application locally, use `make e2e-*` — see
[Running the whole app locally](#running-the-whole-app-locally). This section is the
narrower case: iterating on the Svelte frontend alone, against the repo-root project, which
owns only `funnai_frontend`.

```bash
npm install

npm run dev             # start the root project's replica + deploy the frontend
npm run erase-replica   # same, but wipe .icp/cache first
npm run build           # vite build only
```

`npm run dev` is `npm run replica && npm run deploy`, i.e.
`icp network start -d` followed by `icp deploy funnai_frontend -e local -y`.

That replica is **separate** from the one `make e2e-*` uses (icp-cli runs one network per
project), so the backend canisters are not on it. Anything that calls a backend needs the
e2e environment instead.

There is no `npm run generate`: `src/declarations/` is committed. If a canister interface
changes, regenerate with `didc bind -t js` and commit the result.


## Credits

Serving this app and hosting the data securely and in a decentralized way is made possible by the [Internet Computer](https://internetcomputer.org/)


## Appendix: how the local network works

Everything above goes through `make e2e-*`, which manages the network for you. This
section is the layer underneath — reach for it when you are working inside a single
canister's own project, or debugging the network itself.


Each project gets its own replica. Its `icp.yaml` sets `gateway.port: 0`, which means the
OS picks a free port each time the network starts — so two projects never fight over one.

Start it in the background:

```bash
icp network start -d
# ...
# Network started on port 54543
```

**That port is different every time you start the network, so never write it into a script
or a bookmark.** When you need it again — a new terminal, or later in the same session —
ask the running network:

```bash
icp network status -e local --json
```

```json
{
  "managed": true,
  "api_url": "http://localhost:54543/",
  "gateway_url": "http://localhost:54543/",
  "candid_ui_principal": "iishx-5l777-77774-qaaaa-cai",
  ...
}
```

- **`gateway_url`** is what you open in a browser. A canister is served at
  `http://<canister-id>.<host>:<port>/` — for the port above that would be
  `http://<canister-id>.localhost:54543/`. `make e2e-status` prints the resolved URLs.
- **`api_url`** is what agents and tooling call.

Note both come back **with a trailing slash**. Strip it before joining a path onto it, or
you get `//api/v3` and the replica answers 400. `scripts/lib/icp_helpers.py` already does
this for you.

To wipe local state and start clean. For the whole application prefer
`make e2e-start-clean` (or `make e2e-clean`, which also drops the build artifacts) — this is
the raw equivalent, for when you are inside a single canister's own project:

```bash
icp network stop && rm -rf .icp/cache && icp network start -d

# IMPORTANT: only ever remove .icp/cache -- NEVER .icp itself, and never .icp/data.
# .icp/cache is disposable: local replica state, local canister ids, build artifacts.
# .icp/data/mappings/<env>.ids.json holds the MAINNET canister ids for prd, testing and
# development -- the replacement for the old canister_ids.json -- and is committed.
# `rm -rf .icp` loses the ids for every environment at once, in every project you do it in.
```
