# How to monitor, debug & manage the deployed backend

## Set environment variables

Using `scripts/canister_ids-testing.env` as the reference,
make sure the file `scripts/canister_ids-<network>.env` is up to date.

Then set environment variables for the deployment on that network with:
```bash
# from folder funnAI
source scripts/canister_ids-testing.env  # replace with [local, ic, development, ...]

# check it worked
echo $NETWORK
echo $SUBNET_1_0
echo $SUBNET_1_0_GAMESTATE
```

## Monitor Logs

You can monitor a color-coded log of the canisters as follows:

```bash
# Continuous monitoring:
# To monitor the logs of ALL canisters, run this script from the FunnAI folder
# -> It will write to the screen & also write individual files in scripts/logs/
# -> You must be a controller or log-viewer
#    % dfx canister update-settings <canister-name> --add-log-viewer <principal-id>
#
# from folder funnAI
scripts/logs.sh --network $NETWORK

# To view logs for a specific canister
dfx canister --network $NETWORK logs <canisterId> 
```

## Start / Stop timers

```bash 
# Start/Stop by canisterId 
dfx canister --network $NETWORK call <canisterId> startTimerExecutionAdmin
dfx canister --network $NETWORK call <canisterId> stopTimerExecutionAdmin 

# Start/Stop Challenger & Judge with script
scripts/start-challenger.sh --network $NETWORK
scripts/stop-challenger.sh --network $NETWORK
scripts/start-judge.sh --network $NETWORK
scripts/stop-judge.sh --network $NETWORK
```

## Top-up a Canister

```bash
# Top up cycles by sending 1Tcycles
dfx wallet --network $NETWORK send <canisterId> 1000000000000
```

## Fix the ShareService

```bash
# Admin functions to clean up Share Service canisters in case something failed.
# Note that you still have to delete the canisters. These functions just clean up the data storage in GameState
# This is used during testing, but can also be used in production in case the mAIner creation failed, but user payment was accepted
dfx canister call game_state_canister getSharedServiceCanistersAdmin  --network $NETWORK 
dfx canister call game_state_canister removeSharedServiceCanisterAdmin '(record {canisterId = "<canisterId>" : text} )' --network $NETWORK 

# If you by accident removed the actual ShareService reference in gamestate, add it back with:
dfx canister call game_state_canister addOfficialCanister "(record { address = \"$SUBNET_2_0_SHARE_SERVICE\"; subnet = \"$SUBNET_2_0\" ; canisterType = variant {MainerAgent = variant {ShareService}} })" --network $NETWORK 

# The ShareService canister must be a controller of all it's LLMs
# Issue this command for all LLMs
dfx canister update-settings $SUBNET_2_1_SHARE_SERVICE_LLM_0 --add-controller $SUBNET_2_0_SHARE_SERVICE  --network $NETWORK

```

## Fix the Judge

```bash
# If you by accident removed the actual ShareService reference in gamestate, add it back with:
dfx canister call game_state_canister addOfficialCanister "(record { address = \"$SUBNET_1_0_JUDGE\"; subnet = \"$SUBNET_1_0\" ; canisterType = variant {MainerAgent = variant {ShareService}} })" --network $NETWORK 

# The ShareService canister must be a controller of all it's LLMs
# Repeat this command for all LLMs
dfx canister update-settings $SUBNET_1_1_JUDGE_LLM_0 --add-controller $SUBNET_1_0_JUDGE  --network $NETWORK
```

## Get canister-ids of a mAIner's registered LLMs

```bash
# For mAIners of type ShareService or Own
# Calling it in sequence will cycle through the registered LLMs
dfx canister --network $NETWORK call <mainer-canisterId> getRoundRobinCanister
```

### LLM canisters

If an LLM is not behaving, use commands from the README of the llama_cpp_canister repo
to debug it. These are some useful ones:

```bash
# Get status
dfx canister --network $NETWORK status <llm-canisterId>

# Top up cycles by sending 1Tcycles
dfx wallet --network $NETWORK send <llm-canisterId> 1000000000000

# Get current balance of cycles (Fails if cycles are below frozen canister limit !)
dfx canister --network $NETWORK status <llm-canisterId> 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}'

# Check health
dfx canister --network $NETWORK call <llm-canisterId> health
dfx canister --network $NETWORK call <llm-canisterId> ready

# If this returns 13, it means that the LLM upload & model load worked
# This call is done after that by the mAInerCreator canister
dfx canister --network $NETWORK call <llm-canisterId> get_max_tokens

# Chat with it directly
# 0. Check everything is ok
dfx canister --network $NETWORK call <llm-canisterId> ready

# 1. Create a new chat
dfx canister --network $NETWORK call <llm-canisterId> new_chat '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; 
    "--cache-type-k"; "q8_0";
    } 
})'
# 2. Repeat this call until `prompt_remaining` in the response is empty. 
# This ingest the prompt into the prompt-cache, using multiple update calls: 
# (-) Keep sending the full prompt
# (-) Use `"-n"; "1"`, so it does not generate new tokens
dfx canister --network $NETWORK call <llm-canisterId> run_update '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; 
    "--cache-type-k"; "q8_0";
    "--repeat-penalty"; "1.1";
    "--temp"; "0.6";
    "-sp"; 
    "-p"; "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\ngive me a short introduction to LLMs.<|im_end|>\n<|im_start|>assistant\n"; 
    "-n"; "1" 
    } 
})' 

# 3. Generate new tokens:
# Once `prompt_remaining` in the response is empty.
# (-) repeat this call, until `generated_eog=true`
# (-) Use an empty prompt: `"-p"; "";`
# (-) Use `"-n"; "512"`, so it will now generate new tokens 
dfx canister --network $NETWORK call <llm-canisterId> run_update '(record { 
    args = vec {
    "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; 
    "--cache-type-k"; "q8_0";
    "--repeat-penalty"; "1.1";
    "--temp"; "0.6";
    "-sp"; 
    "-p"; ""; 
    "-n"; "512" 
    } 
})' 

# Load the model (DO NOT DO THIS THOUGH, IT IS ALREADY LOADED)
dfx canister --network $NETWORK call <llm-canisterId> load_model '(record { 
    args = vec {
      "--model"; "models/model.gguf";
      "--cache-type-k"; "q8_0";
    }
  })'
```