
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

Wait until ShareService has nothing left in it's queue.

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

# fill the LLM data storage - No longer needed. Is in stable storage
# -> Run it in case a reinstall is needed
# scripts/register-llms.sh --network $NETWORK

# Test the new endpoints to manage the deployed LLMs
# Get the LLMs currently in use > Remove > check > Add > check
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
echo "SUBNET_1_1_CHALLENGER_LLM_0 : $SUBNET_1_1_CHALLENGER_LLM_0"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$SUBNET_1_1_CHALLENGER_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    add_llm_canister    "(record {canister_id = \"$SUBNET_1_1_CHALLENGER_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters
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

# upgrade the Judge

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Judge
dfx deploy --network $NETWORK judge_ctrlb_canister --mode upgrade

# Upgrade failed, so we did a reinstall
# -> All other steps remain the same.
dfx deploy --network $NETWORK judge_ctrlb_canister --mode reinstall

# start the Judge canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_JUDGE health

# fill the LLM data storage - No longer needed. Is in stable storage
# -> Run it in case a reinstall is needed
# scripts/register-llms.sh --network $NETWORK

# Test the new endpoints to manage the deployed LLMs
# Get the LLMs currently in use > Remove > check > Add > check
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
echo "SUBNET_1_1_JUDGE_LLM_0: $SUBNET_1_1_JUDGE_LLM_0"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    remove_llm_canister "(record {canister_id = \"$SUBNET_1_1_JUDGE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    add_llm_canister    "(record {canister_id = \"$SUBNET_1_1_JUDGE_LLM_0\"})"
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters
```

# start timers of protocol canisters

```bash
# From folder: funnAI
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         startTimerExecutionAdmin
```

# un-pause protocol
```bash
# From folder: funnAI

# Toggle it
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin

# verify
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag
```

# Cleanup the snapshots

After a couple of hours, if everything looks good, remove the snapshots to save memory

```bash
# list & delete the snapshots
dfx canister --network $NETWORK snapshot list   $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK snapshot delete $SUBNET_0_1_GAMESTATE     <snapshot-id>

dfx canister --network $NETWORK snapshot list   $SUBNET_0_1_CHALLENGER    
dfx canister --network $NETWORK snapshot delete $SUBNET_0_1_CHALLENGER    <snapshot-id>

dfx canister --network $NETWORK snapshot list   $SUBNET_0_1_SHARE_SERVICE 
dfx canister --network $NETWORK snapshot delete $SUBNET_0_1_SHARE_SERVICE <snapshot-id>

dfx canister --network $NETWORK snapshot list   $SUBNET_0_1_JUDGE         
dfx canister --network $NETWORK snapshot delete $SUBNET_0_1_JUDGE         <snapshot-id> 
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

dfx canister --network $NETWORK snapshot list $SUBNET_0_1_SHARE_SERVICE 
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_SHARE_SERVICE <snapshot-id>

dfx canister --network $NETWORK snapshot list $SUBNET_0_1_JUDGE         
dfx canister --network $NETWORK snapshot load $SUBNET_0_1_JUDGE         <snapshot-id> 

# start canisters > start timers > unpause, as described above
```

--------------------------------------------------------

# Update Challenger, ShareService & Judge LLMs

LLM updates or new additions can be done without pausing the protocol.

We create, update & manage the LLMs from these folders:
- `PoAIW/llms/Challenger`
- `PoAIW/llms/Judge`
- `PoAIW/llms/mAIner` 

In these folders, the following files are used by dfx:
- dfx.json : `llm_#`    -> used by `dfx deploy`
- canister_ids.json     -> used & updated by `dfx deploy`


## Deploy a new LLM

- Select a new subnet, if needed, and record it in our tracking spreadsheet:
    https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0

- Add the subnet to `funnAI/scripts/canister_ids-prd.env`

- Add the llm_# entries to `PoAIW/llms/xxx/dfx.json`

- Create the canister

    ```bash
        NETWORK=prd

        # Deploy it
        # from folder: PoAIW/llms/xxx
        dfx deploy --network $NETWORK llm_<#> --subnet <subnet-id> --mode install

        # -> Update the file: `funnAI/scripts/canister_ids-prd.env`

        # Verify that the LLM ended up on the correct subnet
        # (Need to call it twice if it returns 'null' the first time)
        LLM="<canister-id>"
        curl -s "https://ic-api.internetcomputer.org/api/v3/canisters/$LLM" | jq -r '.subnet_id'
    ```

- Add ctrlb_canister as a controller

    ```bash        
        NETWORK=prd

        # from folder: funnAI
        source scripts/canister_ids-$NETWORK.env

        # verify
        echo "Using network type: $NETWORK"
        echo "SUBNET_0_1_CHALLENGER   : $SUBNET_0_1_CHALLENGER"
        echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
        echo "SUBNET_0_1_JUDGE        : $SUBNET_0_1_JUDGE"
        
        # from folder: PoAIW/llms/xxx

        # For Challenger LLM
        dfx canister --network $NETWORK update-settings llm_<#> --add-controller $SUBNET_0_1_CHALLENGER 

        # For ShareService LLM
        dfx canister --network $NETWORK update-settings llm_<#> --add-controller $SUBNET_0_1_SHARE_SERVICE 

        # For Judge LLM
        dfx canister --network $NETWORK update-settings llm_<#> --add-controller $SUBNET_0_1_JUDGE 

    ```

- Add Admin as controllers

    ```bash
        NETWORK=prd
        PATRICK="cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"
        ARJAAN="chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"
        dfx canister --network $NETWORK update-settings $llm --add-controller $PATRICK 
        dfx canister --network $NETWORK update-settings $llm --add-controller $ARJAAN 
    ```

- Register the canister with CycleOps

    This adds controller: 2daxo-giaaa-aaaap-anvca-cai

- Upload the model

    ```bash
        # from folder: PoAIW/llms/xxx
        NETWORK=prd
        LLAMA_CPP_CANISTER_PATH="../../../../llama_cpp_canister"
        export PYTHONPATH="${PYTHONPATH}:$(realpath $LLAMA_CPP_CANISTER_PATH)"
        MODEL="models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf"
        LLM="<canister-id>"
        python -m scripts.upload --network $NETWORK --canister $LLM --canister-filename models/model.gguf $MODEL
    ```

- Update the scripts that automate deployment:

    Note: We do not use these scripts for prd right now.
          We do maintain them, in case we need to do a wholesale upgrade later on.
          For example when we are upgrading to a new LLM model.

    - Update script `PoAIW/llms/xxx/2-deploy.sh` to reflect the changed LLM configuration

        ```bash
        # eg. for Challenger: `PoAIW/llms/Challenger/scripts/2-deploy.sh`
        elif [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=2
            # Deploy 2 LLMs across two subnets, for failover and redundancy
            # https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0
            # SUBNET_1_1
            SUBNET_LLM_0="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae"
            ...etc...
        ```

    - Update the other scripts for the LLMs:

        - `PoAIW/llms/xxx/scripts/3-upload-model.sh`
        - `PoAIW/llms/xxx/scripts/4-load-model.sh`
        - `PoAIW/llms/xxx/scripts/5-set-max-tokens.sh`
        - `PoAIW/llms/xxx/scripts/6-register-ctrlb-canister.sh`
        - `PoAIW/llms/xxx/scripts/7-log-pause.sh`
        - `PoAIW/llms/xxx/scripts/7-log-resume.sh`
        - `PoAIW/llms/xxx/scripts/balance.sh`
        - `PoAIW/llms/xxx/scripts/memory.sh`
        - `PoAIW/llms/xxx/scripts/ready-check.sh`
        - `PoAIW/llms/xxx/scripts/status.sh`
        - `PoAIW/llms/xxx/scripts/top-off.sh`

        ```bash
        if [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=...
        fi
        ```

    - Update `PoAIW/src/xxx/scripts/register-llms.sh` for the Controller:
    
        ```bash
        if [ "$NETWORK_TYPE" = "prd" ]; then
            NUM_LLMS_DEPLOYED=...
            NUM_LLMS_ROUND_ROBIN=...
        fi
        ```
        
## Upgrade an LLM

An upgrade of the llama_cpp_canister code is simple. Just issue these commands:

```bash
    NETWORK=prd

    # remove the LLM from the protocol
    LLM="<canister-id>"
    # for Challenger
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for ShareService
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for Judge
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         remove_llm_canister "(record {canister_id = \"$LLM\"})"

    # then upgrade
    # from folder: PoAIW/llms/xxx
    dfx deploy   --network $NETWORK llm_<#> --mode upgrade
```

## Configure & test the LLM

Issue these commands, while the LLM is still removed from the protocol:

```bash
    # set proper environment variables
    # Set & verify environment variables
    # from folder: funnAI
    NETWORK=prd
    source scripts/canister_ids-$NETWORK.env

    # verify
    echo "Using network type: $NETWORK"
    echo "SUBNET_0_1_GAMESTATE    : $SUBNET_0_1_GAMESTATE"
    echo "SUBNET_0_1_CHALLENGER   : $SUBNET_0_1_CHALLENGER"
    echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
    echo "SUBNET_0_1_JUDGE        : $SUBNET_0_1_JUDGE"

    # set the variables for the LLM you want to update
    llm=llm_<#>
    LLM="<canister-id>"
    # For Example:
    llm=llm_11
    LLM=$SUBNET_2_4_SHARE_SERVICE_LLM_11

    echo "llm = $llm"
    echo "LLM = $LLM"

    # from folder: PoAIW/llms/xxx
    dfx canister --network $NETWORK logs $llm --follow
    dfx canister --network $NETWORK call $llm health
    dfx canister --network $NETWORK call $llm load_model '(record { args = vec {"--model"; "models/model.gguf"} })'
    dfx canister --network $NETWORK call $llm set_max_tokens '(record { max_tokens_query = 13 : nat64; max_tokens_update = 13 : nat64 })'
    dfx canister --network $NETWORK call $llm get_max_tokens
    dfx canister --network $NETWORK call $llm log_pause
    dfx canister --network $NETWORK call $llm chats_pause

    # Status check: 
    # Controllers: cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe (Patrick)
    #              chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae (Arjaan)
    #              jh35u-eqaaa-aaaag-abf3a-cai    (Wallet)
    #              qmgdh-3aaaa-aaaaa-qanfq-cai    (Judge Controller)
    #              2daxo-giaaa-aaaap-anvca-cai    (cycleops)
    # Balance > 3T
    dfx canister --network $NETWORK status $llm
    dfx wallet   --network $NETWORK send   $LLM 2_000_000_000_000

    # Test operations manually
    dfx canister --network $NETWORK call $llm new_chat '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache";
            "--cache-type-k"; "q8_0";
        }
        })'

    # Repeat until `prompt_remaining` is empty (3 calls)
    dfx canister --network $NETWORK call $llm run_update '(record {
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

    # Repeat twice (just cut it off before eog is reached)
    dfx canister --network $NETWORK call $llm run_update '(record {
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

    # Explore file system
    dfx canister --network $NETWORK call $llm recursive_dir_content '(record {dir = ".canister_cache"})'
    dfx canister --network $NETWORK call $llm filesystem_remove     '(record {filename = ".canister_cache/chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae/sessions/prompt.cache"})'
    dfx canister --network $NETWORK call $llm recursive_dir_content '(record {dir = ".canister_cache"})'

    # Repeat prompt.cache creation, now cleanup with remove_prompt_cache function
    dfx canister --network $NETWORK call $llm new_chat '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache";
            "--cache-type-k"; "q8_0";
        }
        })'
    dfx canister --network $NETWORK call $llm run_update '(record {
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
    dfx canister --network $NETWORK call $llm recursive_dir_content '(record {dir = ".canister_cache"})'
    dfx canister --network $NETWORK call $llm remove_prompt_cache '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache"
        }
        })'
    dfx canister --network $NETWORK call $llm recursive_dir_content '(record {dir = ".canister_cache"})'
```

## Add LLM to the protocol

### For Challenger
```bash
    LLM="<canister-id>"
    # Add it to the Challenger ctrlb canister
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters --output json
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    add_llm_canister "(record {canister_id = \"$LLM\"})"

    # update GameState cycle cost calculations
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numChallengerLlms
    NUM_LLMS_DEPLOYED=....
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numChallengerLlms = opt ($NUM_LLMS_DEPLOYED : nat);})" 
```

### For ShareService
```bash
    LLM="<canister-id>"
    # Add it to the ShareService ctrlb canister
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters --output json
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    add_llm_canister "(record {canister_id = \"$LLM\"})"
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters --output json

    # update GameState cycle cost calculations
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numShareServiceLlms
    NUM_LLMS_DEPLOYED=....
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numShareServiceLlms = opt ($NUM_LLMS_DEPLOYED : nat);})" 
```

### For Judge
```bash
    LLM="<canister-id>"
    # Add it to the Judge ctrlb canister
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters --output json
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    add_llm_canister "(record {canister_id = \"$LLM\"})"

    # update GameState cycle cost calculations
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numJudgeLlms
    NUM_LLMS_DEPLOYED=...
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numJudgeLlms = opt ($NUM_LLMS_DEPLOYED : nat);})" 
```