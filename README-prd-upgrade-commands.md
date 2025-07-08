
# Set NETWORK environment variable

```bash
# One of these...
NETWORK=prd       # CAREFUL - CAREFUL - CAREFUL
NETWORK=testing

echo " "
echo "Using network type: $NETWORK"

source scripts/canister_ids-$NETWORK.env

echo " "
echo "SUBNET_0_1_GAMESTATE          : $SUBNET_0_1_GAMESTATE"

echo " "
echo "SUBNET_0_1_CHALLENGER         : $SUBNET_0_1_CHALLENGER"
echo "SUBNET_1_1_CHALLENGER_LLM_0   : $SUBNET_1_1_CHALLENGER_LLM_0"

echo " "
echo "Judge        canister ID      : $SUBNET_0_1_JUDGE"
echo "SUBNET_1_1_JUDGE_LLM_0        : $SUBNET_1_1_JUDGE_LLM_0"

echo " "
echo "ShareService canister ID      : $SUBNET_0_1_SHARE_SERVICE"
echo "SUBNET_2_1_SHARE_SERVICE_LLM_0: $SUBNET_2_1_SHARE_SERVICE_LLM_0"

echo " "
source scripts/canister_ids_mainers-$NETWORK.env
echo "MAINER_SHARE_AGENT_0000       : $MAINER_SHARE_AGENT_0000"
```

# pause protocol

```bash
# Verify correct network !
echo $NETWORK
# check if it is already paused
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# then toggle it
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin
```

# stop timers of protocol canisters

```bash
# Verify correct network !
echo $NETWORK
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE stopTimerExecutionAdmin
```

# stop protocol canisters

```bash
# Verify correct network !
echo $NETWORK
dfx canister --network $NETWORK stop $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK stop $SUBNET_0_1_CHALLENGER
dfx canister --network $NETWORK stop $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK stop $SUBNET_0_1_SHARE_SERVICE

dfx canister --network $NETWORK status $SUBNET_0_1_GAMESTATE     | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_CHALLENGER    | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE         | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE | grep Status
```

# snapshot the protocol canisters

```bash
# Verify correct network !
echo $NETWORK
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_CHALLENGER    
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_JUDGE         
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_SHARE_SERVICE 
```

# upgrade the GameState

```bash
# Verify correct network !
echo $NETWORK

# from folder: funnAI
dfx deploy --network $NETWORK game_state_canister --mode upgrade

# start the GameState canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK status $SUBNET_0_1_GAMESTATE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE health

# verify that it is still paused
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# Update the wasm-hash, using the Admin owned test mAIner ShareAgent
echo $MAINER_SHARE_AGENT_0000
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE deriveNewMainerAgentCanisterWasmHashAdmin "(record {address=\"$MAINER_SHARE_AGENT_0000\"; textNote=\"First protocol upgrade\"})"

# Update the protocol thresholds, if needed.
dfx canister --network $NETWORK call game_state_canister getGameStateThresholdsAdmin

dfx canister --network $NETWORK call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdMaxOpenChallenges= 4 : nat;
        thresholdArchiveClosedChallenges = 150 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
    }
)'
```

# upgrade the Challenger

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Challenger
dfx deploy --network $NETWORK challenger_ctrlb_canister --mode upgrade

# start the Challenger canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_CHALLENGER
dfx canister --network $NETWORK status $SUBNET_0_1_CHALLENGER     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_CHALLENGER health

# fill the LLM data storage - This is needed for this upgrade, NOT next time because it will be in stable storage
scripts/register-llms.sh --network $NETWORK

# Test the new endpoints to manage the deployed LLMs
# Get the LLMs currently in use > Remove > check > Add > check
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
echo "SUBNET_1_1_CHALLENGER_LLM_0 : $SUBNET_1_1_CHALLENGER_LLM_0"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$SUBNET_1_1_CHALLENGER_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    add_llm_canister    "(record {canister_id = \"$SUBNET_1_1_CHALLENGER_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
```

# upgrade the Judge

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Judge
dfx deploy --network $NETWORK judge_ctrlb_canister --mode upgrade

# start the Judge canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_JUDGE health

# fill the LLM data storage - This is needed for this upgrade, NOT next time because it will be in stable storage
scripts/register-llms.sh --network $NETWORK

# Test the new endpoints to manage the deployed LLMs
# Get the LLMs currently in use > Remove > check > Add > check
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
echo "SUBNET_1_1_JUDGE_LLM_0: $SUBNET_1_1_JUDGE_LLM_0"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    remove_llm_canister "(record {canister_id = \"$SUBNET_1_1_JUDGE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    add_llm_canister    "(record {canister_id = \"$SUBNET_1_1_JUDGE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters

# These are registered, but remove them for now. We will do the expansion one by one on Wednesday.
echo "SUBNET_1_6_JUDGE_LLM_13: $SUBNET_1_6_JUDGE_LLM_13"
echo "SUBNET_1_6_JUDGE_LLM_14: $SUBNET_1_6_JUDGE_LLM_14"
echo "SUBNET_1_6_JUDGE_LLM_15: $SUBNET_1_6_JUDGE_LLM_15"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    remove_llm_canister "(record {canister_id = \"$SUBNET_1_6_JUDGE_LLM_13\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    remove_llm_canister "(record {canister_id = \"$SUBNET_1_6_JUDGE_LLM_14\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    remove_llm_canister "(record {canister_id = \"$SUBNET_1_6_JUDGE_LLM_15\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
```

# upgrade the ShareService

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/mAIner
dfx deploy --network $NETWORK mainer_service_canister --mode upgrade

# start the ShareService canister back up
echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
dfx canister --network $NETWORK start  $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_SHARE_SERVICE health

# Test the new endpoints to manage the deployed LLMs
# Get the LLMs currently in use > Remove > check > Add > check
echo "SUBNET_2_1_SHARE_SERVICE_LLM_0: $SUBNET_2_1_SHARE_SERVICE_LLM_0"
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    remove_llm_canister "(record {canister_id = \"$SUBNET_2_1_SHARE_SERVICE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    add_llm_canister    "(record {canister_id = \"$SUBNET_2_1_SHARE_SERVICE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters
```

# start timers of protocol canisters

```bash
# From folder: funnAI
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE startTimerExecutionAdmin
```

# un-pause protocol
```bash
# From folder: funnAI

# Toggle it
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin

# verify
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag
```


# HOW TO ROLL BACK IN CASE OF ISSUES

Use the snapshots to roll back everything

```bash
# pause > stop timers > stop canisters , as described above

# list & load the snapshots
dfx canister --network $NETWORK snapshot list $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_GAMESTATE     <snapshot-id>

dfx canister --network $NETWORK snapshot list $SUBNET_0_1_CHALLENGER    
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_CHALLENGER    <snapshot-id>

dfx canister --network $NETWORK snapshot list $SUBNET_0_1_JUDGE         
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_JUDGE         <snapshot-id> 

dfx canister --network $NETWORK snapshot list $SUBNET_0_1_SHARE_SERVICE 
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_SHARE_SERVICE <snapshot-id>

# start canisters > start timers > unpause, as described above
```
