# funnAI

# Setup instructions

First follow all instructions of PoAIW/README.md

Then, do the following:

```bash
# Use conda environment
conda activate llama_cpp_canister

# Set NETWORK environment variable
NETWORK=testing  # [local|ic|development|testing|demo|prd

# MONITORING SCRIPTS
# (-) scripts read from 'scripts/canister_ids-<network>.env'
pip install -r scripts/requirements.txt
scripts/monitor_logs.sh --network $NETWORK
scripts/monitor_gamestate.sh --network $NETWORK
scripts/monitor_balance.sh --network $NETWORK

# WHITELIST SCRIPTS
pip install -r scripts/requirements.txt
scripts/scripts_whitelist/whitelist_charles.sh

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

# Deploy a mAIner of type #ShareService, since this is a protocol canister
# Set environment variables for the subnets.
# Option 1: source the file for the environment & verify things are set
source scripts/canister_ids-$NETWORK.env
SUBNETSACTRL=$SUBNET_0
SUBNETSSCTRL=$SUBNET_0
SUBNETSSLLM=$SUBNET_2_1
# Option 2: set them manually
SUBNETSACTRL=...
SUBNETSSCTRL=...
SUBNETSSLLM=...
# Set the SubnetIds in the GameState canister
dfx canister --network $NETWORK call game_state_canister setSubnetsAdmin "(record {subnetShareAgentCtrl = \"$SUBNETSACTRL\"; subnetShareServiceCtrl = \"$SUBNETSSCTRL\"; subnetShareServiceLlm = \"$SUBNETSSLLM\" })"
# Verify the subnets are set correctly
dfx canister --network $NETWORK call game_state_canister getSubnetsAdmin
# Now install the ShareService Controller
scripts/scripts-gamestate/deploy-mainers-ShareService-Controller-via-gamestate.sh --mode install --network $NETWORK

# Install the first LLM to the correct subnet
# Verify the subnets are set correctly
dfx canister --network $NETWORK call game_state_canister getSubnetsAdmin
# If Ok, install the first Ssllm
scripts/scripts-gamestate/deploy-mainers-ShareService-FirstLLM-via-gamestate.sh --mode install --network $NETWORK

# Install the next LLMs to the correct subnet
# Set the SubnetIds in the GameState canister as explained above
# Verify the subnets are set correctly
dfx canister --network $NETWORK call game_state_canister getSubnetsAdmin
# Now install the Ssllm to the correct subnet
scripts/scripts-gamestate/deploy-mainers-ShareService-AddLLM-via-gamestate.sh --mode install --network $NETWORK

# -----------------------------------------
# Deploy mAIners of type #ShareAgent
scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode install --network $NETWORK

# -----------------------------------------
# Deploy mAIners of type #Own
# TODO - fix the script
# scripts/scripts-gamestate/deploy-mainers-Own-via-gamestate.sh --mode install --network $NETWORK

# #########################################################################
# Adding controllers
# If you maintain a file 'scripts/canister_ids-$NETWORK.env' , you can add
# the pre-defined controllers (patrick & arjaan) to all canisters at once.
#
# If you need others, just update the script 'scripts/add_controllers.py'
#
scripts/add_controllers.sh --network $NETWORK
scripts/list_controllers.sh --network $NETWORK

# #########################################################################
# Upgrading for new GameState code
# NEVER, EVER reinstall the GameState. Always upgrade...
scripts/deploy-gamestate.sh --mode upgrade --network $NETWORK
scripts/scripts-gamestate/register-all.sh --network $NETWORK
# Be careful, but you might need to do these to apply new settings and values for stable memory:
dfx canister call game_state_canister resetCyclesFlowAdmin --network $NETWORK

# #########################################################################
# Upgrading for new mAIner code
#
# Store the new mAIner did & wasm in mAinerCreator/files, then issue these commands to upgrade the system
cd PoAIW
scripts/deploy-mainer-creator.sh  --network $NETWORK --mode upgrade
#
# go back to funnAI folder
cd ..
#
# Upgrade the #ShareService with the new mAIner code
scripts/scripts-gamestate/deploy-mainers-ShareService-Controller-via-gamestate.sh --mode upgrade --network $NETWORK
# Add a previous ShareService if need be, e.g.
dfx canister call game_state_canister addOfficialCanister '(record { address = "ecpt4-ayaaa-aaaad-qhk4a-cai"; subnet = ""; canisterType = variant { MainerAgent = variant { ShareService } } })' --network $NETWORK
# Verify with
dfx canister call game_state_canister getOfficialCanistersAdmin --network $NETWORK
#
# Upgrade the #ShareAgent canisters with new mAIner code, by repeating this call for all of them
# Get user's mAIners
dfx canister call game_state_canister getNumberMainerAgentsAdmin --output json --network $NETWORK
dfx canister call game_state_canister getMainerAgentCanistersAdmin --output json --network $NETWORK
# TODO: write a script that automates these calls over all ShareAgent canisters
scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode upgrade --canister <canisterId> --network $NETWORK
#
# Update gamestate to the latest wasmhash. <canisterId> is the address of one of the upgraded ShareAgent canisters
dfx canister call game_state_canister deriveNewMainerAgentCanisterWasmHashAdmin '(record {address="<canisterId>"; textNote="New wasm deployed"})' --network $NETWORK

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

# Deploy funnai backend (used mainly for chat):
dfx deploy --argument "( principal \"$(dfx identity get-principal)\" )" funnai_backend --network $NETWORK

# Deploy funnai frontend:
dfx deploy funnai_frontend --network $NETWORK

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

# test a single Response Generation by your first mAIner of type #ShareAgent
scripts/scripts-testing/generate-a-response-ShareAgent.sh --network $NETWORK

# test a single Response Generation by your first mAIner of type #Own
# TODO UPDATE SCRIPT scripts/scripts-testing/generate-a-response-Own.sh --network $NETWORK

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

Adjust reward per challenge:

```bash
# e.g. to 1000 FUNNAI
dfx canister call game_state_canister setRewardPerChallengeAdmin '100000000000' --network $NETWORK
```

# The GameState Thresholds

The Thresholds are stored in stable memory.

The following endpoints allow to set & get the values:

```bash
# From folder: funnAI
dfx canister call game_state_canister getGameStateThresholdsAdmin --output json --network $NETWORK

dfx canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 30 : nat;
        thresholdMaxOpenChallenges= 2 : nat;
        thresholdMaxOpenSubmissions = 5 : nat;
        thresholdScoredResponsesPerChallenge = 3 : nat;
    }
)' --network $NETWORK
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
