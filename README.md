# funnAI

# Setup instructions

First follow all instructions of PoAIW/README.md

Then, do the following:

```bash
# Use conda environment
conda activate llama_cpp_canister

# Note: on WSL, you might first have to run
sudo sysctl -w vm.max_map_count=2097152

# from folder: funnAI

# Fresh deploy of GameState
scripts/deploy-gamestate.sh --mode install [--network ic]

# If not yet done, deploy Challenger, Judge & mAIners
scripts/deploy-all.sh --mode install [--network ic]

# This step only needed first time deploying everything
# Just to link the GameState correctly
scripts/deploy-gamestate.sh --mode reinstall [--network ic]

# Note: when redeploying changes, you can run the above commands with --mode upgrade
# to avoid reuploading the models and thus saving a lot of time

# Deploy funnai backend (used mainly for chat):
dfx deploy --argument "( principal \"$(dfx identity get-principal)\" )" funnai_backend [--ic]

# Deploy funnai frontend:
dfx deploy funnai_frontend [--ic]
```

Use the local UI: http://cbopz-duaaa-aaaaa-qaaka-cai.localhost:4943/ 

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

- Full system test with timers
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
dfx canister call funnai_backend --network development setCanisterCreationCanisterId '("wyx7t-zqaaa-aaaam-qb5ga-cai")'

dfx deploy --network development funnai_frontend
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