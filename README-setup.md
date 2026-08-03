# funnAI Setup instructions

First follow all instructions of PoAIW/README.md

Then, do the following:

```bash
# Use the funnAI conda environment (created in PoAIW/README-setup.md)
conda activate funnAI

# Set NETWORK environment variable
NETWORK=testing  # [local|ic|development|testing|demo|prd]

# NOTE: `--output json` is gone. icp-cli cannot decode a Candid response the way dfx did
# (its `--json` wraps the raw response instead), so anything that needs real JSON goes
# through scripts/lib/icp_helpers.py, which decodes with icp-py-core.

# ADMIN MONITORING & HELPER SCRIPTS
# The scripts read the canister ids from these files:
# - protocol: 'scripts/canister_ids-<network>.env'
# - mainers : 'scripts/canister_ids_mainers-<network>.env'
# Already installed by `pip install -r requirements.txt` from the funnAI folder.
# Update the file 'scripts/canister_ids_mainers-<network>.env'
scripts/get_mainers.sh --network $NETWORK --user <principal>
# Then run these
scripts/monitor_logs.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_gamestate_metrics.sh --network $NETWORK 
scripts/monitor_gamestate_logs.sh --network $NETWORK 
scripts/monitor_memory.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_balance.sh --network $NETWORK --canister-types [all|protocol|mainers]

# When running local
# `dfx deps pull` has no icp-cli equivalent, and none is needed:
# - internet-identity : the managed local network serves it itself (`ii: true` in
#                       icp.yaml), at http://id.ai.localhost:<port>/authorize
# - cycles_ledger     : a fixed mainnet principal; nothing here deploys it
#
# from folder: funnAI
# There is no `--clean`; removing .icp/cache is the equivalent.
# NEVER remove .icp itself -- .icp/data/mappings holds the mainnet canister ids.
icp network stop || true
rm -rf .icp/cache
icp network start -d

# This script deploys the core canisters:
# (-) Before doing a new install, reset all canister_ids.json files, for example:
#       "testing": ".*-cai"   -->  "testing": ""
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
# `dfx generate` has no icp-cli equivalent: src/declarations/ is committed, so nothing
# regenerates it during a build. If an interface changes, regenerate with `didc bind -t js`.
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

In case there are authentication issues: icp-cli has no wallet to pass. Check that the
identity you are deploying with is a controller of the canister
(Note that only authorized identities which are set up as canister controllers may deploy the production canisters)

```bash
icp deploy -e ic -y
```

### Backup stage

Potentially create if there's high demand on subnets and failing deployments

```bash
# icp-cli has no cycles-wallet concept. Your own cycles balance:
icp cycles balance -e prd
# icp-cli has no wallet to set: cycles come from the identity's cycles-ledger balance.
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
