# funnAI Setup instructions

First follow all instructions of [PoAIW/README-setup.md](PoAIW/README-setup.md) — it
covers the clone layout, the `funnAI` conda environment, mops, and the gguf download.

## How icp-cli works

funnAI is built, tested and deployed with **[icp-cli](https://cli.internetcomputer.org)**
(the `icp` command). A few of its concepts shape how this repo is laid out; skim these
before running the commands further down, because most setup mistakes trace back to
standing in the wrong folder or naming the wrong environment.

### Projects

> **A project is a folder containing an `icp.yaml`.**

`icp` finds it by walking up from your current directory, and a project owns three things:

1. **which canisters exist by name** — the `canisters:` block in its `icp.yaml`
2. **its canister ids** — under `.icp/`
3. **its own local replica** — icp-cli runs one local network *per project*

**funnAI has 16 projects, not one.** The repo root, `e2e/`, `src/funnai_backend/`, each of
the nine canisters in `PoAIW/src/*/`, and the four `PoAIW/llms/*/` folders each have their
own `icp.yaml`. That is why instructions say "from folder X" — `cd`-ing to the right
project is a real step, and outside one you get `failed to locate project directory`.

```bash
icp project show          # what the project you are standing in declares
icp environment list      # its environments
```

### Environments and networks

These are two different things, and every command has to be told which it is using.

- A **network** is a replica to talk to. There are two: `local` (a throwaway replica
  declared in `icp.yaml`) and `ic` (mainnet).
- An **environment** is a *named set of canister ids* on one of those networks. Several
  environments can share one network, differing only in which ids they point at.

funnAI has six environments; five of them run on `ic`:

```
environment          network      canister ids live in
-----------          -------      --------------------
local          -->   local        .icp/cache/mappings/local.ids.json   (throwaway)
prd            -->   ic     \
testing        -->   ic      |    .icp/data/mappings/<env>.ids.json    (committed)
development    -->   ic      |
demo           -->   ic      |
backup         -->   ic     /
```

`prd` is the production environment — the canisters serving https://funnai.onicai.com/.

`icp environment list` shows a seventh, **`ic`**, which icp-cli always provides implicitly.
It is not declared in any `icp.yaml` here and has no canister ids, so `-e ic` will not reach
an existing funnAI canister — it would *create new ones on mainnet and spend real cycles*.
Use `-e prd` for production; never `-e ic`.

Select an environment with `-e`, or a network with `-n`:

| you are targeting   | flag                | requires                                                       |
| ------------------- | ------------------- | -------------------------------------------------------------- |
| a canister **name** | `-e <env>` ONLY     | being inside that project (it reads its `icp.yaml` + id store) |
| a **principal**     | `-e <env>`          | being inside a project                                         |
| a **principal**     | `-n ic`             | nothing — works from any folder                                |
| a **principal**     | `-n local`          | being inside a project (`local` is declared there)             |
| a **principal**     | `-n <url> -k fetch` | nothing, but `--root-key` is mandatory for a URL               |

Two things that catch people out:

```bash
# `-n` takes a NETWORK name. An environment name is not a network:
icp canister status <principal> -n prd
#   Error: project does not contain a network named 'prd'

# `-n` cannot be combined with a canister NAME at all, not even a valid network:
icp canister status game_state_canister -n local
#   Error: Specifying a network is not supported if you are targeting a canister by
#          name, specify an environment instead
```

**Rule of thumb: use `-e <env>` for everything while inside a project.** It is the only
thing that works with names, and it works with principals too. Reach for `-n ic` only when
you have a bare principal and no project — which is how the ops scripts drive the ~745
mAIner canisters and the LLM canisters without listing any of them in an `icp.yaml`.

### The local network

Each project gets its own replica, on a port the OS picks at start time
(`gateway.port: 0`). **The port changes every time you start it, so never hardcode it** —
read it back:

```bash
icp network start -d                  # prints e.g. "Network started on port 63840"
icp network status -e local --json    # .gateway_url / .api_url
```

To wipe local state and start clean:

```bash
icp network stop && rm -rf .icp/cache && icp network start -d
```

Because each project has its own replica, canisters in different projects cannot call each
other locally. To run the **whole application** — every canister, the LLM and the frontend
on one local network — use the end-to-end environment from the repo root:

```bash
make e2e-up          # build + deploy everything locally
make e2e-status      # URLs and per-canister health
make e2e-test        # system-level checks
make e2e-down
```

### Where canister ids live

| path                                | holds                                 | committed? |
| ----------------------------------- | ------------------------------------- | ---------- |
| `.icp/data/mappings/<env>.ids.json` | the **mainnet** canister ids          | yes        |
| `.icp/cache/`                       | build artifacts + local network state | no         |

> 🚨 **Never `rm -rf .icp` — only ever `.icp/cache`.** `.icp/data/` holds the mainnet
> canister ids for every environment. Deleting it loses them all.

Most canisters are declared by name in their project's `icp.yaml`, with ids in
`.icp/data/mappings/`. Two families are not — they are addressed by principal instead, and
their ids live in a plain registry file:

| family                             | registry                           | why                                          |
| ---------------------------------- | ---------------------------------- | -------------------------------------------- |
| the ~744 `mainer_ctrlb_canister_N` | `PoAIW/src/mAIner/mainer_ids.json` | a 744-entry `icp.yaml` would be unmanageable |
| the ICRC token ledger + index      | `PoAIW/src/Token*/token_ids.json`  | downloaded wasms; nothing here rebuilds them |

`icp canister install <principal> --wasm ...` works with no project and no declaration,
which is what makes that possible.

---

## funnAI-specific steps

Then, do the following:

```bash
# Use the funnAI conda environment (created in PoAIW/README-setup.md)
conda activate funnAI

# Set NETWORK environment variable
NETWORK=testing  # [local|development|testing|demo|prd]  -- use prd for production, never ic

# ADMIN MONITORING & HELPER SCRIPTS
# The scripts read the canister ids from these files:
# - protocol: 'scripts/canister_ids-<network>.env'
# - mainers : 'scripts/canister_ids_mainers-<network>.env'
# Update the file 'scripts/canister_ids_mainers-<network>.env'
scripts/get_mainers.sh --network $NETWORK --user <principal>
# Then run these
scripts/monitor_logs.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_gamestate_metrics.sh --network $NETWORK 
scripts/monitor_gamestate_logs.sh --network $NETWORK 
scripts/monitor_memory.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_balance.sh --network $NETWORK --canister-types [all|protocol|mainers]

# When running local
# Nothing needs to be pulled first:
# - internet-identity : the managed local network serves it itself (`ii: true` in
#                       icp.yaml), at http://id.ai.localhost:<port>/authorize
# - cycles_ledger     : a fixed mainnet principal; nothing here deploys it
#
# from folder: funnAI
# Removing .icp/cache resets the local network.
# NEVER remove .icp itself -- .icp/data/mappings holds the mainnet canister ids.
icp network stop || true
rm -rf .icp/cache
icp network start -d

# This script deploys the core canisters:
# (-) Before doing a new install, clear the ids for that environment, i.e. remove the
#     canister's entry from '.icp/data/mappings/<network>.ids.json' in each project
# (-) Deploys GameState, mAInerCreator, Challenger (1 LLM), Judge (3 LLMs)
# (-) Registers the canisters properly with each other
# (-) The timers of the Challenger & Judge are not started.
#     -> Do this manually with the command:
#          icp canister call <canisterId> startTimerExecutionAdmin '()' -e $NETWORK
# Note: on WSL, you might first have to run
sudo sysctl -w vm.max_map_count=2097152
# from folder: funnAI
scripts/deploy-all.sh --mode install --network $NETWORK
# When redeploying changes, you can run the above command with --mode upgrade
#      to avoid reuploading the models and thus saving a lot of time

# -----------------------------------------------------------------------------------
# Deploy mAIner of type #ShareService
#
# IMPORTANT: Record the canister ids in scripts/canister_ids-<network>.env
#            for canister monitoring, management & logging purposes
#
# Follow instructions of README-prd-upgrade-commands.md

# -----------------------------------------
# Deploy mAIners of type #ShareAgent
#
# This is still possible, but there are other options now.
#
# # Verify that 'subnetShareAgentCtrl' is set correctly in GameState
# icp canister call game_state_canister getSubnetsAdmin '()' -e $NETWORK
# # Deploy a new ShareAgent via Admin command
# scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode install --network $NETWORK
# # Update gamestate to the latest wasmhash. <canisterId> is the address of one of the upgraded ShareAgent canisters
# icp canister call game_state_canister deriveNewMainerAgentCanisterWasmHashAdmin '(record {address="<canisterId>"; textNote="New wasm deployed"})' -e $NETWORK

# # To increase limit of ShareAgent mAIners
# icp canister call game_state_canister setLimitForCreatingMainerAdmin '(record {mainerType = variant { ShareAgent } ; newLimit = 450 : nat;} )' -e prd

# #########################################################################
# Admin functions to clean up redeemed payments in case the creation failed.
# This is used during testing, but can also be used in production in case the mAIner creation failed, but user payment was accepted
icp canister call game_state_canister getRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' -e $NETWORK
icp canister call game_state_canister removeRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' -e $NETWORK

# -----------------------------------------------
# Timers:
# (-) The timers for the mAIners are started automatically.
# (-) The timers of the Challenger & Judge are NOT started automatically.
# Start/Stop by canisterId
icp canister call <canisterId -e $NETWORK > startTimerExecutionAdmin
icp canister call <canisterId -e $NETWORK > stopTimerExecutionAdmin
# Start/Stop Challenger & Judge with script
scripts/start-challenger.sh --network $NETWORK
scripts/stop-challenger.sh --network $NETWORK
scripts/start-judge.sh --network $NETWORK
scripts/stop-judge.sh --network $NETWORK

# Important
# The IS_GENERATING_CHALLENGE flag is not reset during a stop/start of the canister
# Make sure to call:
icp canister call <challenger_id -e $NETWORK > resetIsGeneratingChallengeFlag

# Once the timers are running, you can use these commands to check on the data captured by the gamestate:
# Run from folder: funnAI

# Verify Challenger challenge generations
# You can reset the challenge storage arrays with:
icp canister call game_state_canister resetCurrentChallengesAdmin -e $NETWORK

icp canister call game_state_canister getCurrentChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumCurrentChallengesAdmin -e $NETWORK

# Verify mAIner response generations
# Note: submissionStatus changes from #Submitted > #Judging > #Judged
icp canister call game_state_canister getSubmissionsAdmin -e $NETWORK
icp canister call game_state_canister getNumSubmissionsAdmin -e $NETWORK

icp canister call game_state_canister getOpenSubmissionsAdmin -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsAdmin -e $NETWORK

icp canister call game_state_canister getOpenSubmissionsForOpenChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin -e $NETWORK

# Verify Judge score generations
icp canister call game_state_canister getScoredChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumScoredChallengesAdmin -e $NETWORK

# Verify GameState management of challenges/scores/winners
icp canister call game_state_canister getArchivedChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumArchivedChallengesAdmin -e $NETWORK

icp canister call game_state_canister getClosedChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumClosedChallengesAdmin -e $NETWORK

icp canister call game_state_canister getRecentChallengeWinners -e $NETWORK
icp canister call game_state_canister getRecentProtocolActivity -e $NETWORK

# Deploy funnai backend (reproducible build):
# See README-prd-upgrade-commands.md for build, deploy and verify instructions

# Deploy funnai frontend:
## ensure you have the latest from the PoAIW repo
# src/declarations/ is committed, so nothing regenerates it during a build.
# If a canister interface changes, regenerate with `didc bind -t js` and commit the result.
icp deploy funnai_frontend -e $NETWORK -y
# Note: you might need to give yourself these explicit permissions:
icp canister call funnai_frontend grant_permission '(record {permission = variant {Prepare}; to_principal = principal "<your-principal>"})' -e $NETWORK
icp canister call funnai_frontend grant_permission '(record {permission = variant {Commit}; to_principal = principal "<your-principal>"})' -e $NETWORK

# Deploy the token ledger canister:
# from folder: PoAIW/src/TokenLedger
icp deploy -e local -y
# follow the manual steps in PoAIW/src/TokenLedger/README to set canister ids and test the token ledger setup
```

Use the local UI: http://cbopz-duaaa-aaaaa-qaaka-cai.localhost:4943/:

- The feed will allways show the Protocol updates, namely Challenges & Winners
- The feed will show mAIner related items (Submissions & Scores) for the logged in user (!)
  - You can login using NFID with your Google account.

# Testing each component & their cycle burn

Scripts are provided to verify that each component works correctly, and to determine the exact cycle burn.

For accurate cycle burn calculation, turn off ALL the timers (Challenger, mAIners, Judge).

```bash
# To start with a clean slate, remove all current challenges
icp canister call game_state_canister resetCurrentChallengesAdmin '()' -e $NETWORK

# test a single Challenge Generation by the Challenger
scripts/scripts-testing/generate-a-challenge.sh --network $NETWORK

# test a single Score Generation by the Judge
scripts/scripts-testing/generate-a-score-Judge.sh --network $NETWORK
```

# The CyclesFlow variables

The CyclesFlow variables are defined in GameState and then selectively passed on to the other canisters.

- public type `CyclesFlow`
- GameState does the following:
  - Defines `let DEFAULT_COST_XXX_YYY`
  - Assigns `DEFAULT_COST_XXX_YYY` to `stable var costXxxxYyyy`
  - Provides endpoint to calculate the cycles flow variables `stable var cyclesZzz`

The following Admin endpoints are available:

```bash
icp canister call game_state_canister setCyclesFlowAdmin '(record {})' -e $NETWORK
icp canister call game_state_canister getCyclesFlowAdmin '()' -e $NETWORK
icp canister call game_state_canister resetCyclesFlowAdmin '()' -e $NETWORK

# setCyclesFLowAdmin allows to overwrite the default values:
#
# a) Overwrite individual parameters that go into the CyclesFlow calculations
icp canister call game_state_canister setCyclesFlowAdmin '( record {
  dailyChallenges = opt (10 : nat);
  numJudgeLlms = opt (6 : nat);
})' -e $NETWORK
# b) Overwrite the calculated CyclesFlow variables
icp canister call game_state_canister setCyclesFlowAdmin '( record {
  cyclesGenerateResponseSsctrlSsllm = opt (100_000_000 : nat);
})' -e $NETWORK
```

# Adjust reward per challenge:

```bash
# e.g. to 1000 FUNNAI
icp canister call game_state_canister setRewardPerChallengeAdmin '100000000000' -e $NETWORK
```

## Adjust cycles security buffer
This determines the threshold of conversion to ICP. If the Game State's cycle balance is underneath the buffer, it converts incoming ICP payments to cycles. If the cycle balance is above the threshold it doesn't convert ICP to cycles but uses the cycles from its balance.
```bash
icp canister call game_state_canister getProtocolCyclesBalanceBuffer '()' -e $NETWORK
# parameter is in trillion cycles, e.g. to 400 means 400T cycles
icp canister call game_state_canister setProtocolCyclesBalanceBuffer '400' -e $NETWORK
```

## Adjust mAIner creation buffer
This determines the threshold of allowing more mAIners to be created and is a security measurement against concurrent creation requests from users (to avoid that they pay but then are blocked from the creation).
```bash
icp canister call game_state_canister getBufferMainerCreation '()' -e $NETWORK
icp canister call game_state_canister setBufferMainerCreation '10' -e $NETWORK
```

# The GameState Thresholds

The Thresholds are stored in stable memory.

The following endpoints allow to set & get the values:

```bash
# From folder: funnAI
icp canister call game_state_canister getGameStateThresholdsAdmin -e $NETWORK

icp canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 140 : nat;
        thresholdMaxOpenChallenges = 7 : nat;
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
    }
)' -e $NETWORK
```

# Manually migrate data to the Archive canister
```bash
# Archived challenges
icp canister call game_state_canister migrateArchivedChallengesAdmin '()' -e $NETWORK
# Submissions
icp canister call game_state_canister getNumSubmissionsAdmin -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsAdmin -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumArchivedSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister archiveSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister cleanSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumSubmissionsToMigrateAdmin '()' -e $NETWORK
icp canister call game_state_canister setNumSubmissionsToMigrateAdmin '100' # 3000 is the max (due to message size limit -e $NETWORK)
icp canister call game_state_canister migrateSubmissionsAdmin '()' -e $NETWORK
# Winner declarations
icp canister call game_state_canister migrateWinnerDeclarationsAdmin 'vec { "challengeIdsToMigrate"; "" }' -e $NETWORK
# Scored responses
icp canister call game_state_canister getScoredChallengesAdmin -e $NETWORK
icp canister call game_state_canister getNumScoredChallengesAdmin -e $NETWORK
icp canister call game_state_canister migrateScoredResponsesForChallengeAdmin '"challengeIdToMigrate"' -e $NETWORK
```

# Manually backup mAIners to the Archive canister
```bash
icp canister call game_state_canister backupMainersAdmin '()' -e $NETWORK
```

# Start & Stop the Game

See instructions in PoAIW/README.md, the sections:

- Full system test with timers (Note that mAIner timers are already active...)
- Test components individually

---

## Internet Computer Resources

funnai is built and hosted on the Internet Computer. To learn more about it, see the following documentation available online:

- [Quick Start](https://sdk.dfinity.org/docs/quickstart/quickstart-intro.html)
- [SDK Developer Tools](https://sdk.dfinity.org/docs/developers-guide/sdk-guide.html)
- [Motoko Programming Language Guide](https://sdk.dfinity.org/docs/language-guide/motoko.html)
- [Motoko Language Quick Reference](https://sdk.dfinity.org/docs/language-guide/language-manual.html)
- [JavaScript API Reference](https://erxue-5aaaa-aaaab-qaagq-cai.raw.ic0.app)

## Running the project locally

If you want to run this project locally, you can use the following commands:

### 1. Install dependencies

```bash
npm install
```

### 2. Install Vessel which is a dependency

https://github.com/dfinity/vessel

### 3. Start a local replica

```bash
npm run dev
```

Note: this starts a local replica of the Internet Computer (IC) which includes the canisters state stored from previous sessions.
If you want to start a clean local IC replica (i.e. all canister state is erased) run instead:

```bash
npm run erase-replica
```

### 4. Deploy your canisters to the replica

See instructions above.

## Deployment to the Internet Computer mainnet

Deploy the code as canisters to the live IC where it's accessible via regular Web browsers.

### Development Stage

```bash
# funnai_backend takes the deploying principal as its init argument.
# `--argument` is `--args` in icp-cli, and `icp identity principal` takes no environment.
icp deploy funnai_backend --args "( principal \"$(icp identity principal)\" )" -e development -y

icp deploy funnai_frontend -e development -y

# demo
icp deploy funnai_frontend -e demo -y
```

For setting up stages, see [Notes on Stages](./notes/NotesOnStages.md)

### Production Deployment

```bash
npm install

icp network start -d
```

Deploy to Mainnet (live IC):
Ensure that all changes needed for Mainnet deployment have been made (e.g. define HOST in store.ts)

```bash
icp deploy funnai_backend --args "( principal \"$(icp identity principal)\" )" -e prd -y
icp deploy funnai_frontend -e prd -y
```

In case there are authentication issues, check that the identity you are deploying with is
a controller of the canister
(Note that only authorized identities which are set up as canister controllers may deploy the production canisters)

```bash
icp deploy -e ic -y
```

### Backup stage

Potentially create if there's high demand on subnets and failing deployments

```bash
# Your own cycles balance:
icp cycles balance -e prd
# Cycles come from the identity's cycles-ledger balance.
icp deploy funnai_backend --args "( principal \"$(icp identity principal)\" )" \
  --subnet qdvhd-os4o2-zzrdw-xrcv4-gljou-eztdp-bj326-e6jgr-tkhuc-ql6v2-yqe -e backup -y
icp deploy funnai_frontend --subnet qdvhd-os4o2-zzrdw-xrcv4-gljou-eztdp-bj326-e6jgr-tkhuc-ql6v2-yqe --with-cycles 1000000000000 -e backup -y
```

# Credits

Serving this app and hosting the data securely and in a decentralized way is made possible by the [Internet Computer](https://internetcomputer.org/)

# Other

## Get and delete Email Subscribers

The project has email subscription functionality included. The following commands are helpful for managing subscriptions.

```bash
icp canister call funnai_backend get_email_subscribers '()' -e $NETWORK
icp canister call funnai_backend delete_email_subscriber 'j@g.com'

icp canister call funnai_backend get_email_subscribers --network development -e $NETWORK
icp canister call funnai_backend delete_email_subscriber 'j@g.com' --network development -e $NETWORK

icp canister call funnai_backend get_email_subscribers --network ic -e $NETWORK
icp canister call funnai_backend delete_email_subscriber 'j@g.com' -e ic -e $NETWORK
```

## Cycles for Production Canisters

Due to the IC's reverse gas model, developers charge their canisters with cycles to pay for any used computational resources. The following can help with managing these cycles.

Fund wallet with cycles (from ICP): https://medium.com/dfinity/internet-computer-basics-part-3-funding-a-cycles-wallet-a724efebd111

Top up cycles:

```bash
icp cycles balance -e ic
icp canister call jh35u-eqaaa-aaaag-abf3a-cai wallet_balance '()' -e ic --query
icp canister status funnai_backend -e ic
icp canister status funnai_frontend -e ic
icp canister top-up funnai_backend --amount 3000000000000 -e ic
icp canister top-up funnai_frontend --amount 300000000000 -e ic
```
