# funnAI

# Setup instructions

We are using dfx deps for:
- internet-identity
- cycles_ledger

Use dfx deps & dfx start from the funnAI root folder:

```bash
# from folder: funnAI
dfx deps pull
dfx deps init

dfx start --clean

dfx deploy
```

Then, follow all instructions of PoAIW/README.md

Then, do the following:

```bash
# Use conda environment
conda activate llama_cpp_canister

# Note: on WSL, you might first have to run
sudo sysctl -w vm.max_map_count=2097152

# from folder: funnAI

# To monitor the logs on mainnet, run this script
# -> it reads the canister IDs from the file: "scripts/canister_ids.env"
# -> It will write to the screen & also write individual files in scripts/logs/
# -> You must be a controller or log-viewer
#    % dfx canister update-settings <canister-name> --add-log-viewer <principal-id>
scripts/logs.sh --network ic

# This script deploys the core canisters:
# (-) Deploys GameState, mAInerCreator, Challenger, Judge
# (-) Registers the canisters properly with each other
# (-) The timers of the Challenger & Judge are not started.
#     -> Do this manually in the next step
scripts/deploy-all.sh --mode install [--network ic]

# Notes: 
# (-) when redeploying changes, you can run the above command with --mode upgrade
#     to avoid reuploading the models and thus saving a lot of time
# (-) to reset the gamestate, run `scripts/deploy-gamestate.sh --mode reinstall`, 
#     followed by                 `scripts/deploy-all.sh --mode upgrade`
#     -> This will erase all data: canisters/challenges/responses/etc.

# -----------------------------------------------------------------------------------
# Deploy mAIners
#
# Always deploy a mAIner of type #ShareService, since this is a protocol canister
scripts/scripts-gamestate/deploy-mainers-ShareService-via-gamestate.sh --mode install [--network ic]

# Optionally, deploy mAIners of type #Own or #ShareAgent
# This is optional for test purposes, because these mAIners will be created by users of the frontend
#
# (-) Deploy a mAIner of type #Own
scripts/scripts-gamestate/deploy-mainers-Own-via-gamestate.sh --mode install [--network ic]
# (-) Deploy a mAIner of type #ShareAgent
scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode install [--network ic]
#
# Notes: 
# (-) You (should) run the script for type #ShareService only once. It has not been verified what happens if you run it again.
# (-) You can run the scripts for type #Own and #ShareAgent multiple times. It will deploy another mAIner.
# (-) The #Own & #ShareService mAIners are deployed with 1 LLM. To add more LLMs, use the function: addLlmCanisterToMainer (*)
# (-) The timers of the mAIners are NOT started automatically. (*)
#
# => The exact dfx commands to add LLMs & to start the timers are printed by the scripts
#

# Deploy funnai backend (used mainly for chat):
dfx deploy --argument "( principal \"$(dfx identity get-principal)\" )" funnai_backend [--ic]

# Deploy funnai frontend:
dfx deploy funnai_frontend [--ic]

# Deploy the token ledger canister:
# from folder: PoAIW/src/TokenLedger
dfx deploy
# follow the manual steps in PoAIW/src/TokenLedger/README to set canister ids and test the token ledger setup
```

Use the local UI: http://cbopz-duaaa-aaaaa-qaaka-cai.localhost:4943/:
- The feed will allways show the Protocol updates, namely Challenges & Winners
- The feed will show mAIner related items (Submissions & Scores) for the logged in user (!)
  - You can login using NFID with your Google account.

# The GameState Thresholds

The Thresholds are stored in stable memory.

The following endpoints allow to set & get the values:

```bash
# From folder: funnAI
dfx canister call game_state_canister getGameStateThresholdsAdmin --output json [--ic] 

dfx canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 30 : nat;
        thresholdMaxOpenChallenges= 2 : nat;
        thresholdMaxOpenSubmissions = 5 : nat;
        thresholdScoredResponsesPerChallenge = 3 : nat;
    }
)' [--ic]
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