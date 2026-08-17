# funnAI operations

> # ⚠️ THIS FILE IS SIGNIFICANTLY OUT OF DATE
>
> It was split out of `README-setup.md` largely unchanged, and most of it predates the move
> from dfx to icp-cli and the `e2e/` local environment. Treat every command here as a
> **starting point to verify, not an instruction to follow**:
>
> - Some commands were written for a single shared `dfx start` replica. icp-cli runs one
>   network per project, so "from folder funnAI" no longer means what it used to.
> - Canister ids, thresholds, prices and limits quoted inline may be stale.
> - `demo` and `backup` are no longer environments; only `local`, `development`, `testing`
>   and `prd` exist.
>
> **It needs a pass by someone who runs these flows.** Until then, check a command against
> the canister's current Candid interface before running it against anything that matters.

For **mainnet** build, deploy, upgrade and verification procedures, use
[README-prd-upgrade-commands.md](README-prd-upgrade-commands.md) — that runbook is
maintained and is the authority for anything touching production. This file covers the
surrounding day-to-day operational commands.

For first-time setup and the local environment, see [README-setup.md](README-setup.md).

---

## funnAI-specific steps

Then, do the following:

```bash
# Use the funnAI conda environment (created in PoAIW/README-setup.md)
conda activate funnAI

# Set NETWORK environment variable
# `local` here is the REPO-ROOT project's network, not the e2e one. Most commands below
# target a deployed environment; switch deliberately.
NETWORK=local  # [local|development|testing|prd]  -- use prd for production, never ic

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
icp canister call <canisterId> startTimerExecutionAdmin '()' -e $NETWORK
icp canister call <canisterId> stopTimerExecutionAdmin '()' -e $NETWORK
# Start/Stop Challenger & Judge with script
scripts/start-challenger.sh --network $NETWORK
scripts/stop-challenger.sh --network $NETWORK
scripts/start-judge.sh --network $NETWORK
scripts/stop-judge.sh --network $NETWORK

# Important
# The IS_GENERATING_CHALLENGE flag is not reset during a stop/start of the canister
# Make sure to call:
icp canister call <challenger_id> resetIsGeneratingChallengeFlag '()' -e $NETWORK

# Once the timers are running, you can use these commands to check on the data captured by the gamestate:
# Run from folder: funnAI

# Verify Challenger challenge generations
# You can reset the challenge storage arrays with:
icp canister call game_state_canister resetCurrentChallengesAdmin '()' -e $NETWORK

icp canister call game_state_canister getCurrentChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumCurrentChallengesAdmin '()' -e $NETWORK

# Verify mAIner response generations
# Note: submissionStatus changes from #Submitted > #Judging > #Judged
icp canister call game_state_canister getSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumSubmissionsAdmin '()' -e $NETWORK

icp canister call game_state_canister getOpenSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsAdmin '()' -e $NETWORK

icp canister call game_state_canister getOpenSubmissionsForOpenChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin '()' -e $NETWORK

# Verify Judge score generations
icp canister call game_state_canister getScoredChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumScoredChallengesAdmin '()' -e $NETWORK

# Verify GameState management of challenges/scores/winners
icp canister call game_state_canister getArchivedChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumArchivedChallengesAdmin '()' -e $NETWORK

icp canister call game_state_canister getClosedChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumClosedChallengesAdmin '()' -e $NETWORK

icp canister call game_state_canister getRecentChallengeWinners '()' -e $NETWORK
icp canister call game_state_canister getRecentProtocolActivity '()' -e $NETWORK

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

# The FUNNAI token ledger is NOT available locally.
# PoAIW/src/TokenLedger/ has no icp.yaml -- it was never migrated to icp-cli -- so
# `icp deploy` there fails with "failed to locate project directory". Its README and
# token_ids.json cover the mainnet environments only. FUNNAI-denominated flows therefore
# cannot be exercised on the local network; see "What the local network can and cannot test".
```

Open the local UI. The gateway port is assigned at start time, so read it back rather than
guessing:

```bash
cd e2e && icp network status -e local --json    # .gateway_url
# the frontend is served at http://funnai_frontend.local.<host>:<port>/
```

- The feed will allways show the Protocol updates, namely Challenges & Winners
- The feed will show mAIner related items (Submissions & Scores) for the logged in user (!)
  - Log in with the **local** Internet Identity — see [Signing in
    locally](README-setup.md#signing-in-locally) above, and remember to **Create** the identity before
    trying to sign in with it. Mainnet sign-in — `id.ai` or NFID/Google — does not work
    against a local replica: those delegations are canister signatures certified by
    mainnet's root key, which the local replica cannot verify.

## Testing each component & their cycle burn

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

## The CyclesFlow variables

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

## Adjust reward per challenge

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

## The GameState Thresholds

The Thresholds are stored in stable memory.

The following endpoints allow to set & get the values:

```bash
# From folder: funnAI
icp canister call game_state_canister getGameStateThresholdsAdmin '()' -e $NETWORK

icp canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 140 : nat;
        thresholdMaxOpenChallenges = 7 : nat;
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
    }
)' -e $NETWORK
```

## Manually migrate data to the Archive canister
```bash
# Archived challenges
icp canister call game_state_canister migrateArchivedChallengesAdmin '()' -e $NETWORK
# Submissions
icp canister call game_state_canister getNumSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumArchivedSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister archiveSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister cleanSubmissionsAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumSubmissionsToMigrateAdmin '()' -e $NETWORK
# 3000 is the max, due to the message size limit
icp canister call game_state_canister setNumSubmissionsToMigrateAdmin '100' -e $NETWORK
icp canister call game_state_canister migrateSubmissionsAdmin '()' -e $NETWORK
# Winner declarations
icp canister call game_state_canister migrateWinnerDeclarationsAdmin 'vec { "challengeIdsToMigrate"; "" }' -e $NETWORK
# Scored responses
icp canister call game_state_canister getScoredChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister getNumScoredChallengesAdmin '()' -e $NETWORK
icp canister call game_state_canister migrateScoredResponsesForChallengeAdmin '"challengeIdToMigrate"' -e $NETWORK
```

## Manually backup mAIners to the Archive canister
```bash
icp canister call game_state_canister backupMainersAdmin '()' -e $NETWORK
```

## Start & Stop the Game

The mAIner timers start automatically; the Challenger and Judge timers do not. Start and
stop them with the scripts under [funnAI-specific steps](#funnai-specific-steps)
(`scripts/start-challenger.sh`, `scripts/start-judge.sh`, and their `stop-` counterparts),
and exercise single components with the scripts under
[Testing each component](#testing-each-component--their-cycle-burn).

---


## Deployment to the Internet Computer mainnet

Deploy the code as canisters to the live IC where it's accessible via regular Web browsers.

### Development Stage

```bash
# funnai_backend takes the deploying principal as its init argument.
# `--argument` is `--args` in icp-cli, and `icp identity principal` takes no environment.
icp deploy funnai_backend --args "( principal \"$(icp identity principal)\" )" -e development -y

icp deploy funnai_frontend -e development -y
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


## Other

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


---
