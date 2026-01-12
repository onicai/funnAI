# funnAI

# Setup instructions

First follow all instructions of PoAIW/README.md

Then, do the following:

```bash
# Use conda environment
conda activate llama_cpp_canister

# Set NETWORK environment variable
NETWORK=testing  # [local|ic|development|testing|demo|prd]

# ADMIN MONITORING & HELPER SCRIPTS
# The scripts read the canister ids from these files:
# - protocol: 'scripts/canister_ids-<network>.env'
# - mainers : 'scripts/canister_ids_mainers-<network>.env'
pip install -r scripts/requirements.txt
# Update the file 'scripts/canister_ids_mainers-<network>.env'
scripts/get_mainers.sh --network $NETWORK --user <principal>
# Then run these
scripts/monitor_logs.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_gamestate_metrics.sh --network $NETWORK 
scripts/monitor_gamestate_logs.sh --network $NETWORK 
scripts/monitor_memory.sh --network $NETWORK --canister-types [all|protocol|mainers]
scripts/monitor_balance.sh --network $NETWORK --canister-types [all|protocol|mainers]

# When running local
# We are using dfx deps for:
# - internet-identity
# - cycles_ledger
#
# from folder: funnAI
dfx deps pull
dfx deps init
dfx start --clean
dfx deps deploy

# This script deploys the core canisters:
# (-) Before doing a new install, reset all canister_ids.json files, for example:
#       "testing": ".*-cai"   -->  "testing": ""
# (-) Deploys GameState, mAInerCreator, Challenger (1 LLM), Judge (3 LLMs)
# (-) Registers the canisters properly with each other
# (-) The timers of the Challenger & Judge are not started.
#     -> Do this manually with the command:
#          dfx canister call <canisterId> startTimerExecutionAdmin
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
# dfx canister --network $NETWORK call game_state_canister getSubnetsAdmin
# # Deploy a new ShareAgent via Admin command
# scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode install --network $NETWORK
# # Update gamestate to the latest wasmhash. <canisterId> is the address of one of the upgraded ShareAgent canisters
# dfx canister call game_state_canister deriveNewMainerAgentCanisterWasmHashAdmin '(record {address="<canisterId>"; textNote="New wasm deployed"})' --network $NETWORK

# # To increase limit of ShareAgent mAIners
# dfx canister --network prd call game_state_canister setLimitForCreatingMainerAdmin '(record {mainerType = variant { ShareAgent } ; newLimit = 450 : nat;} )'


# #########################################################################
# Admin functions to clean up redeemed payments in case the creation failed.
# This is used during testing, but can also be used in production in case the mAIner creation failed, but user payment was accepted
dfx canister call game_state_canister getRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' --network $NETWORK
dfx canister call game_state_canister removeRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' --network $NETWORK

# -----------------------------------------------
# Timers:
# (-) The timers for the mAIners are started automatically.
# (-) The timers of the Challenger & Judge are NOT started automatically.
# Start/Stop by canisterId
dfx canister --network $NETWORK call <canisterId> startTimerExecutionAdmin
dfx canister --network $NETWORK call <canisterId> stopTimerExecutionAdmin
# Start/Stop Challenger & Judge with script
scripts/start-challenger.sh --network $NETWORK
scripts/stop-challenger.sh --network $NETWORK
scripts/start-judge.sh --network $NETWORK
scripts/stop-judge.sh --network $NETWORK

# Important
# The IS_GENERATING_CHALLENGE flag is not reset during a stop/start of the canister
# Make sure to call:
dfx canister --network $NETWORK call <challenger_id> resetIsGeneratingChallengeFlag

# Once the timers are running, you can use these commands to check on the data captured by the gamestate:
# Run from folder: funnAI

# Verify Challenger challenge generations
# You can reset the challenge storage arrays with:
dfx canister call game_state_canister resetCurrentChallengesAdmin --output json --network $NETWORK

dfx canister call game_state_canister getCurrentChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumCurrentChallengesAdmin --output json --network $NETWORK


# Verify mAIner response generations
# Note: submissionStatus changes from #Submitted > #Judging > #Judged
dfx canister call game_state_canister getSubmissionsAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumSubmissionsAdmin --output json --network $NETWORK

dfx canister call game_state_canister getOpenSubmissionsAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumOpenSubmissionsAdmin --output json --network $NETWORK

dfx canister call game_state_canister getOpenSubmissionsForOpenChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin --output json --network $NETWORK

# Verify Judge score generations
dfx canister call game_state_canister getScoredChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumScoredChallengesAdmin --output json --network $NETWORK

# Verify GameState management of challenges/scores/winners
dfx canister call game_state_canister getArchivedChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumArchivedChallengesAdmin --output json --network $NETWORK

dfx canister call game_state_canister getClosedChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumClosedChallengesAdmin --output json --network $NETWORK

dfx canister call game_state_canister getRecentChallengeWinners --output json --network $NETWORK
dfx canister call game_state_canister getRecentProtocolActivity --output json --network $NETWORK

# Deploy funnai backend:
dfx generate funnai_backend
dfx deploy --argument "( principal \"$(dfx identity get-principal)\" )" funnai_backend --network $NETWORK

# Deploy funnai frontend:
## ensure you have the latest from the PoAIW repo
dfx generate game_state_canister
dfx generate mainer_ctrlb_canister
dfx generate api_canister
dfx deploy funnai_frontend --network $NETWORK
# Note: you might need to give yourself these explicit permissions:
dfx canister call funnai_frontend grant_permission '(record {permission = variant {Prepare}; to_principal = principal "<your-principal>"})'
dfx canister call funnai_frontend grant_permission '(record {permission = variant {Commit}; to_principal = principal "<your-principal>"})'


# Deploy the token ledger canister:
# from folder: PoAIW/src/TokenLedger
dfx deploy
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
dfx canister call game_state_canister resetCurrentChallengesAdmin --network $NETWORK

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
dfx canister call game_state_canister setCyclesFlowAdmin '(record {})'
dfx canister call game_state_canister getCyclesFlowAdmin
dfx canister call game_state_canister resetCyclesFlowAdmin

# setCyclesFLowAdmin allows to overwrite the default values:
#
# a) Overwrite individual parameters that go into the CyclesFlow calculations
dfx canister call game_state_canister setCyclesFlowAdmin '( record {
  dailyChallenges = opt (10 : nat);
  numJudgeLlms = opt (6 : nat);
})'
# b) Overwrite the calculated CyclesFlow variables
dfx canister call game_state_canister setCyclesFlowAdmin '( record {
  cyclesGenerateResponseSsctrlSsllm = opt (100_000_000 : nat);
})'
```

# Adjust reward per challenge:

```bash
# e.g. to 1000 FUNNAI
dfx canister call game_state_canister setRewardPerChallengeAdmin '100000000000' --network $NETWORK
```

## Adjust cycles security buffer
This determines the threshold of conversion to ICP. If the Game State's cycle balance is underneath the buffer, it converts incoming ICP payments to cycles. If the cycle balance is above the threshold it doesn't convert ICP to cycles but uses the cycles from its balance.
```bash
dfx canister call game_state_canister getProtocolCyclesBalanceBuffer --network $NETWORK
# parameter is in trillion cycles, e.g. to 400 means 400T cycles
dfx canister call game_state_canister setProtocolCyclesBalanceBuffer '400' --network $NETWORK
```

## Adjust mAIner creation buffer
This determines the threshold of allowing more mAIners to be created and is a security measurement against concurrent creation requests from users (to avoid that they pay but then are blocked from the creation).
```bash
dfx canister call game_state_canister getBufferMainerCreation --network $NETWORK
dfx canister call game_state_canister setBufferMainerCreation '10' --network $NETWORK
```

# The GameState Thresholds

The Thresholds are stored in stable memory.

The following endpoints allow to set & get the values:

```bash
# From folder: funnAI
dfx canister call game_state_canister getGameStateThresholdsAdmin --output json --network $NETWORK

dfx canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 140 : nat;
        thresholdMaxOpenChallenges = 7 : nat;
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
    }
)' --network $NETWORK
```

# Manually migrate data to the Archive canister
```bash
# Archived challenges
dfx canister call game_state_canister migrateArchivedChallengesAdmin --network $NETWORK
# Submissions
dfx canister call game_state_canister getNumSubmissionsAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumOpenSubmissionsAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumOpenSubmissionsForOpenChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumArchivedSubmissionsAdmin --network $NETWORK
dfx canister call game_state_canister archiveSubmissionsAdmin --network $NETWORK
dfx canister call game_state_canister cleanSubmissionsAdmin --network $NETWORK
dfx canister call game_state_canister getNumSubmissionsToMigrateAdmin --network $NETWORK
dfx canister call game_state_canister setNumSubmissionsToMigrateAdmin '100' --network $NETWORK # 3000 is the max (due to message size limit)
dfx canister call game_state_canister migrateSubmissionsAdmin --network $NETWORK
# Winner declarations
dfx canister call game_state_canister migrateWinnerDeclarationsAdmin 'vec { "challengeIdsToMigrate"; "" }' --network $NETWORK
# Scored responses
dfx canister call game_state_canister getScoredChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister getNumScoredChallengesAdmin --output json --network $NETWORK
dfx canister call game_state_canister migrateScoredResponsesForChallengeAdmin '"challengeIdToMigrate"' --output json --network $NETWORK
```

# Manually backup mAIners to the Archive canister
```bash
dfx canister call game_state_canister backupMainersAdmin --network $NETWORK
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
dfx deploy --network development --argument "( principal\"$(dfx identity get-principal)\" )" funnai_backend

dfx deploy --network development funnai_frontend

or

dfx deploy funnai_frontend --network development --wallet "$(dfx identity --network development get-wallet)"

demo

dfx deploy funnai_frontend --network demo --wallet "$(dfx identity --network demo get-wallet)"
```


For setting up stages, see [Notes on Stages](./notes/NotesOnStages.md)

### Production Deployment

```bash
npm install

dfx start --background
```

Deploy to Mainnet (live IC):
Ensure that all changes needed for Mainnet deployment have been made (e.g. define HOST in store.ts)

```bash
dfx deploy --network ic --argument "( principal\"$(dfx identity get-principal)\" )" funnai_backend
dfx deploy --network ic funnai_frontend
```

In case there are authentication issues, you could try this command
(Note that only authorized identities which are set up as canister controllers may deploy the production canisters)

```bash
dfx deploy --network ic --wallet "$(dfx identity --network ic get-wallet)"
```

### Backup stage

Potentially create if there's high demand on subnets and failing deployments

```bash
dfx identity get-wallet --ic
dfx identity --network backup set-wallet 3v5vy-2aaaa-aaaai-aapla-cai
dfx deploy --network backup --argument "( principal\"$(dfx identity get-principal)\" )" funnai_backend --subnet qdvhd-os4o2-zzrdw-xrcv4-gljou-eztdp-bj326-e6jgr-tkhuc-ql6v2-yqe --with-cycles 1000000000000
dfx deploy --network backup funnai_frontend --subnet qdvhd-os4o2-zzrdw-xrcv4-gljou-eztdp-bj326-e6jgr-tkhuc-ql6v2-yqe --with-cycles 1000000000000
```

# Credits

Serving this app and hosting the data securely and in a decentralized way is made possible by the [Internet Computer](https://internetcomputer.org/)

# Other

## Get and delete Email Subscribers

The project has email subscription functionality included. The following commands are helpful for managing subscriptions.

```bash
dfx canister call funnai_backend get_email_subscribers
dfx canister call funnai_backend delete_email_subscriber 'j@g.com'

dfx canister call funnai_backend get_email_subscribers --network development
dfx canister call funnai_backend delete_email_subscriber 'j@g.com' --network development

dfx canister call funnai_backend get_email_subscribers --network ic
dfx canister call funnai_backend delete_email_subscriber 'j@g.com' --network ic
```

## Cycles for Production Canisters

Due to the IC's reverse gas model, developers charge their canisters with cycles to pay for any used computational resources. The following can help with managing these cycles.

Fund wallet with cycles (from ICP): https://medium.com/dfinity/internet-computer-basics-part-3-funding-a-cycles-wallet-a724efebd111

Top up cycles:

```bash
dfx identity --network=ic get-wallet
dfx wallet --network ic balance
dfx canister --network ic status funnai_backend
dfx canister --network ic status funnai_frontend
dfx canister --network ic --wallet 3v5vy-2aaaa-aaaai-aapla-cai deposit-cycles 3000000000000 funnai_backend
dfx canister --network ic --wallet 3v5vy-2aaaa-aaaai-aapla-cai deposit-cycles 300000000000 funnai_frontend
```
