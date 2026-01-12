
# Set NETWORK environment variable

```bash
# The principal of funnAI Django running on aws-dev (same for all networks)
FUNNAI_DJANGO_PRINCIPAL=bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe

# One of these...
NETWORK=prd
NETWORK=testing
NETWORK=demo
NETWORK=development

echo " "
echo "Using network type: $NETWORK"

source scripts/canister_ids-$NETWORK.env
source scripts/canister_ids_mainers-$NETWORK.env

# Check status of some canisters
echo -n "SUBNET_0_1_GAMESTATE           = $SUBNET_0_1_GAMESTATE - "; dfx canister --network $NETWORK status $SUBNET_0_1_GAMESTATE | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_MAINER_CREATOR      = $SUBNET_0_1_MAINER_CREATOR - "; dfx canister --network $NETWORK status $SUBNET_0_1_MAINER_CREATOR | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_CHALLENGER          = $SUBNET_0_1_CHALLENGER - "; dfx canister --network $NETWORK status $SUBNET_0_1_CHALLENGER | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_JUDGE               = $SUBNET_0_1_JUDGE - "; dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_SHARE_SERVICE       = $SUBNET_0_1_SHARE_SERVICE - "; dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_BACKEND             = $SUBNET_0_1_BACKEND - "; dfx canister --network $NETWORK status $SUBNET_0_1_BACKEND | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_FRONTEND            = $SUBNET_0_1_FRONTEND - "; dfx canister --network $NETWORK status $SUBNET_0_1_FRONTEND | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_2_API                 = $SUBNET_0_2_API - "; dfx canister --network $NETWORK status $SUBNET_0_2_API | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_1_CHALLENGER_LLM_0    = $SUBNET_1_1_CHALLENGER_LLM_0 - "; dfx canister --network $NETWORK status $SUBNET_1_1_CHALLENGER_LLM_0 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_1_JUDGE_LLM_0         = $SUBNET_1_1_JUDGE_LLM_0 - "; dfx canister --network $NETWORK status $SUBNET_1_1_JUDGE_LLM_0 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_1_JUDGE_LLM_1         = $SUBNET_1_1_JUDGE_LLM_1 - "; dfx canister --network $NETWORK status $SUBNET_1_1_JUDGE_LLM_1 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_2_JUDGE_LLM_2         = $SUBNET_1_2_JUDGE_LLM_2 - "; dfx canister --network $NETWORK status $SUBNET_1_2_JUDGE_LLM_2 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_2_1_SHARE_SERVICE_LLM_0 = $SUBNET_2_1_SHARE_SERVICE_LLM_0 - "; dfx canister --network $NETWORK status $SUBNET_2_1_SHARE_SERVICE_LLM_0 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_2_1_SHARE_SERVICE_LLM_1 = $SUBNET_2_1_SHARE_SERVICE_LLM_1 - "; dfx canister --network $NETWORK status $SUBNET_2_1_SHARE_SERVICE_LLM_1 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0000        = $MAINER_SHARE_AGENT_0000 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0000 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0001        = $MAINER_SHARE_AGENT_0001 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0001 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
```

# stop timers of protocol canisters

In this order:

```bash
# Verify correct network !
echo $NETWORK
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    stopTimerExecutionAdmin
# wait a couple of minutes..
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE stopTimerExecutionAdmin
# wait a couple of minutes..
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         stopTimerExecutionAdmin
# wait a couple of minutes.. -> pause is next step
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

# stop protocol canisters

```bash
# Verify correct network !
echo $NETWORK
dfx canister --network $NETWORK stop $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK stop $SUBNET_0_1_CHALLENGER
dfx canister --network $NETWORK stop $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK stop $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK stop $SUBNET_0_1_MAINER_CREATOR
dfx canister --network $NETWORK stop $SUBNET_0_2_API

dfx canister --network $NETWORK status $SUBNET_0_1_GAMESTATE     | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_CHALLENGER    | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE         | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE | grep Status
dfx canister --network $NETWORK status $SUBNET_0_1_MAINER_CREATOR | grep Status
dfx canister --network $NETWORK status $SUBNET_0_2_API            | grep Status
```

# snapshot the protocol canisters

```bash
# Verify correct network !
echo $NETWORK

dfx canister --network $NETWORK snapshot create $SUBNET_0_1_CHALLENGER    
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_JUDGE         
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_MAINER_CREATOR 
dfx canister --network $NETWORK snapshot create $SUBNET_0_2_API
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_TREASURY 
```

# upgrade the GameState

```bash
# Verify correct network !
echo $NETWORK

# from folder: funnAI
dfx canister --network $NETWORK stop $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_GAMESTATE
#
dfx deploy --network $NETWORK game_state_canister --mode upgrade --wasm-memory-persistence keep

# start the GameState canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK status $SUBNET_0_1_GAMESTATE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE health

# verify that it is still paused
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# Update the wasm-hash, using the Admin owned test mAIner ShareAgent
echo $MAINER_SHARE_AGENT_0001
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE deriveNewMainerAgentCanisterWasmHashAdmin "(record {address=\"$MAINER_SHARE_AGENT_0001\"; textNote=\"Protocol upgrade\"})"

# If needed, initialize the openSubmissionsQueue. 
# -> Tyically not needed. Was created during introduction of new openSubmissionsQueue
# -> Needed if getNumOpenSubmissionsAdmin > 0 , while getNumOpenSubmissionsForOpenChallengesAdmin = 0
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE initializeOpenSubmissionsQueueAdmin

dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getNumOpenSubmissionsAdmin
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsAdmin

dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getNumOpenSubmissionsForOpenChallengesAdmin
dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsForOpenChallengesAdmin

dfx canister --network $NETWORK call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsQueueSizeAdmin

# Update the protocol thresholds, if needed.
dfx canister --network $NETWORK call game_state_canister getGameStateThresholdsAdmin

dfx canister --network $NETWORK call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 140 : nat;
        thresholdMaxOpenChallenges = 7 : nat;
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
    }
)'

# Update the CyclesFlow variables if needed: 
# - dailySubmissionsAllShare = 6 * 24 = 144  (6 per hour)
# - dailySubmissionsAllShare = dailyChallenges * thresholdScoredResponsesPerChallenge
#                            = 144 * 33 = 4,752
# - dailySubmissionsAllOwn = (TODO for PowerMainer)

# verify current settings
dfx canister --network $NETWORK call game_state_canister getCyclesFlowAdmin | grep dailySubmissionsAllShare

# set the values, which will trigger a recalculation
dfx canister --network $NETWORK call game_state_canister setCyclesFlowAdmin '( record { dailySubmissionsAllShare = opt (4752 : nat);})'
```

## Update Admin RBAC for GameState

```bash
# verify funnAI_django principal has #AdminQuery permissions
dfx canister --network $NETWORK call game_state_canister getAdminRoles
dfx canister --network $NETWORK call game_state_canister assignAdminRole '( record { "principal" = "'$FUNNAI_DJANGO_PRINCIPAL'"; role = variant { AdminQuery }; note = "Grant AdminQuery access for funnai-django" } )'
# if needed, this is how you revoke permissions for the previous principal
dfx canister --network $NETWORK call game_state_canister revokeAdminRole '( "'$FUNNAI_DJANGO_PRINCIPAL'")'
```

# upgrade the Challenger

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Challenger
dfx deploy --network $NETWORK challenger_ctrlb_canister --mode upgrade --wasm-memory-persistence keep

# start the Challenger canister back up
# Important
# The IS_GENERATING_CHALLENGE flag is not reset during a stop/start of the canister
# Make sure to call resetIsGeneratingChallengeFlag after start
#
dfx canister --network $NETWORK start  $SUBNET_0_1_CHALLENGER
dfx canister --network $NETWORK call   $SUBNET_0_1_CHALLENGER resetIsGeneratingChallengeFlag
dfx canister --network $NETWORK status $SUBNET_0_1_CHALLENGER     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_CHALLENGER health
dfx canister --network $NETWORK call   $SUBNET_0_1_CHALLENGER getIsGeneratingChallengeFlag

# fill the LLM data storage - No longer needed. Is in stable storage
# -> Run it in case a reinstall is needed
# scripts/register-llms.sh --network $NETWORK

# Verify registered LLMs
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters

# Verify timer setting
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER getTimerActionRegularityInSecondsAdmin
```

# upgrade the ShareService

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/mAIner
dfx deploy --network $NETWORK mainer_service_canister --mode upgrade --wasm-memory-persistence keep

# start the ShareService canister back up
echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
dfx canister --network $NETWORK start  $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_SHARE_SERVICE health

# Verify registered LLMs
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE get_llm_canisters

# Verify timer setting
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin
```

## reinstall the ShareService

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/mAIner
dfx deploy --network $NETWORK mainer_service_canister --mode reinstall

# start the ShareService canister back up
echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
dfx canister --network $NETWORK start  $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK status $SUBNET_0_1_SHARE_SERVICE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_SHARE_SERVICE health

# Verify timer setting
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin

# register game state
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE setGameStateCanisterId '("'$SUBNET_0_1_GAMESTATE'")'
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE getGameStateCanisterId

# register the LLMs
# from folder: PoAIW/src/mAIner
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE get_llm_canisters
# register every LLM with the ShareService with this command
CANISTER_ID_LLM=...
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE add_llm_canister '(record { canister_id = "'$CANISTER_ID_LLM'" })'

# register all the ShareAgent mAIners, by upgrading them via GameState > mAInerCreator
# -> This will take care of all proper registrations
MAINER=...
# snapshot
dfx canister --network $NETWORK stop $MAINER
dfx canister --network $NETWORK snapshot create $MAINER
dfx canister --network $NETWORK start $MAINER
# set correct type & register ShareAgent with ShareService
dfx canister call --network $NETWORK $MAINER setMainerCanisterType '(variant {ShareAgent} )'
dfx canister call --network $NETWORK $MAINER setShareServiceCanisterId '("'$SUBNET_0_1_SHARE_SERVICE'")'
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE upgradeMainerControllerAdmin "(record {canisterAddress = \"$MAINER\" })"
# Note: it will fail if maintenance flag is on. Toggle it and retry
dfx canister --network $NETWORK call $MAINER getMaintenanceFlag
dfx canister --network $NETWORK call $MAINER toggleMaintenanceFlagAdmin # it must be off !
# verify
dfx canister call --network $NETWORK $MAINER getMainerCanisterType
dfx canister --network $NETWORK call $MAINER getGameStateCanisterId 
dfx canister --network $NETWORK call $MAINER health
dfx canister --network $NETWORK call $MAINER getMaintenanceFlag
```

# upgrade the Judge

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Judge
dfx deploy --network $NETWORK judge_ctrlb_canister --mode upgrade --wasm-memory-persistence keep

# Upgrade failed, so we did a reinstall
# -> WHEN REINSTALLING, THE LMMs need to be registered again! See step below
dfx deploy --network $NETWORK judge_ctrlb_canister --mode reinstall

# start the Judge canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_JUDGE health

# THE JUDGE CURRENTLY MUST BE REINSTALLED, so issue these commands:
# re-register the LLMs, from PoAIW/src/Judge folder
scripts/register-llms.sh --network $NETWORK

# set the timer
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE getTimerActionRegularityInSecondsAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE setTimerActionRegularityInSecondsAdmin '(15)'

# reset the isProcessingSubmissions flag
dfx canister --network $NETWORK call   $SUBNET_0_1_JUDGE resetIsProcessingSubmissionsAdmin

# Verify registered LLMs
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters --output json
```

# upgrade the API canister

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/Api
dfx deploy --network $NETWORK api_canister --mode upgrade --wasm-memory-persistence keep

# start the API canister back up
dfx canister --network $NETWORK start  $SUBNET_0_2_API
```

## Update Admin RBAC for API canister

```bash
# verify funnAI_django principal has #AdminUpdate permissions
dfx canister --network $NETWORK call $SUBNET_0_2_API getAdminRoles
dfx canister --network $NETWORK call $SUBNET_0_2_API assignAdminRole '( record { "principal" = "'$FUNNAI_DJANGO_PRINCIPAL'"; role = variant { AdminUpdate }; note = "Grant AdminUpdate access for funnai-django" } )'
# if needed, this is how you revoke permissions for the previous principal
dfx canister --network $NETWORK call SUBNET_0_2_API revokeAdminRole '( "'$FUNNAI_DJANGO_PRINCIPAL'")'
```

# upgrade the mAInerCreator

```bash
# Verify correct network !
echo $NETWORK

# from folder: PoAIW/src/mAInerCreator
# Generate the bindings for the upload scripts and the frontend
dfx generate mainer_creator_canister
dfx deploy --network $NETWORK mainer_creator_canister --mode upgrade --wasm-memory-persistence keep

# start the mAInerCreator canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_MAINER_CREATOR
dfx canister --network $NETWORK status $SUBNET_0_1_MAINER_CREATOR     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_MAINER_CREATOR health

# ensure the correct wasm & did files are in this folder 
# -> PoAIW/src/mAInerCreator/files
#
# If you just did a mAIner upgrade, you can do this:
# From folder: PoAIW/src/mAIner
shasum -a 256 .dfx/$NETWORK/canisters/mainer_ctrlb_canister_0/mainer_ctrlb_canister_0.wasm # confirm it is the TARGET_HASH
cp .dfx/$NETWORK/canisters/mainer_ctrlb_canister_0/mainer_ctrlb_canister_0.did ../mAInerCreator/files/mainer_ctrlb_canister.did
cp .dfx/$NETWORK/canisters/mainer_ctrlb_canister_0/mainer_ctrlb_canister_0.wasm ../mAInerCreator/files/mainer_ctrlb_canister.wasm
#
# -> More details in PoAIW/src/mAInerCreator/README.md
#
# from folder: PoAIW/src/mAInerCreator
#
# (if changed) Upload the mainer controller canister wasm
shasum -a 256 files/mainer_ctrlb_canister.wasm # verify
python -m scripts.upload_mainer_controller_canister --network $NETWORK --canister mainer_creator_canister --wasm files/mainer_ctrlb_canister.wasm --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator
#
# (if changed) Upload the mainer LLM canister wasm
shasum -a 256 files/llama_cpp.wasm # verify
python -m scripts.upload_mainer_llm_canister_wasm --network $NETWORK --canister mainer_creator_canister --wasm files/llama_cpp.wasm --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator

# (if changed) Upload the mainer LLM model file (gguf)
shasum -a 256 files/qwen2.5-0.5b-instruct-q8_0.gguf # verify
python -m scripts.upload_mainer_llm_canister_modelfile --network $NETWORK --canister mainer_creator_canister --chunksize 2000000 --wasm files/qwen2.5-0.5b-instruct-q8_0.gguf --hf-sha256 "ca59ca7f13d0e15a8cfa77bd17e65d24f6844b554a7b6c12e07a5f89ff76844e" --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator

# Verify the sha256 hashes of all uploaded files
# Warning: do not run this while upload is in process. Wait till it is fully completed.
#          It uses a lazy evaluation logic.
dfx canister --network $NETWORK call mainer_creator_canister getSha256HashesAdmin
```

## Testing the mAInerCreator

Final test must be done by creating a mAIner via the UI, but initial test you can do with dfx.

Call the `spinUpMainerControllerCanisterForUserAdmin` endpoint as described in PoAIW/src/GameState/README.md 

# un-pause protocol
```bash
# From folder: funnAI

# Toggle it
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin

# verify
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag
```

# start timers of protocol canisters

In this order:

```bash
# From folder: funnAI
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    startTimerExecutionAdmin

# If you changed the Challenger timer interval, note it is a stble var.
# You will need to call setTimerActionRegularityInSecondsAdmin, as in:
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER setTimerActionRegularityInSecondsAdmin '(420)'
```

# Add a `release-#` tag to PoAIW git repo

Once deployed and confirmed it is OK, apply a tag:

```bash
# From folder: PoAIW

# Check out main branch

# get all the current tags, with their commit sha & description
git fetch --tags
git tag -l --format='%(refname:short) -> %(if)%(*objectname)%(then)%(*objectname:short)%(else)%(objectname:short)%(end) %(contents:subject)'

# add the tag, as in this example
RELEASE_TAG=release-4    # increment
RELEASE_SHA=dd7792e      # get with `git log --oneline -5`
RELEASE_MESSAGE="Release 4: Admin RBAC for GameState, Api & mAIners"
git tag -a $RELEASE_TAG $RELEASE_SHA -m "$RELEASE_MESSAGE"

# push it to github
git push origin $RELEASE_TAG
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

# Load a snapshot to ROLL BACK

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

# Deploy or Upgrade LLMs

## IMPORTANT: Also upload wasm to mAInerCreator

Even though we are not using the mAInerCreator to upgrade mAIners, it
is important to keep the wasm file up to date.

## Description

Deploying or upgrading LLMs is done without pausing the protocol.

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

## Add new LLM to the protocol

### For Challenger
```bash
    LLM="<canister-id>"
    # Add it to the Challenger ctrlb canister
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters --output json
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    add_llm_canister "(record {canister_id = \"$LLM\"})"
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    get_llm_canisters --output json

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
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    add_llm_canister "(record {canister_id = \"$LLM\"})"
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE    get_llm_canisters --output json

    # update GameState cycle cost calculations
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numJudgeLlms
    NUM_LLMS_DEPLOYED=...
    dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numJudgeLlms = opt ($NUM_LLMS_DEPLOYED : nat);})" 
```

## Upgrade an existing LLM

```bash
    # Takes the LLM offline, upgrades it, tests it, and puts it back online
    # Script will pause to ask for confirmation a couple of times
    scripts/upgrade_llms.sh --network $NETWORK [--canister-id <canister-id>]
```

# Cleaning LLMs (prompt cache files)

## Using a daily task

The cleaning of the LLMs is now done automatically via a periodic task in funnAI_django.

## Manually, while the LLM is still online

This approach is deprecated.

```bash
    sscripts/cleanup_llm_promptcache_live.sh --network $NETWORK [--canister-id <canister-id>]
```

## Manually, while the LLM is offline

This approach is deprecated.

This script is used by `scripts/upgrade_llms.sh` which takes the LLM offline first:

```bash
    sscripts/cleanup_llm_promptcache.sh --network $NETWORK [--canister-id <canister-id>]
```


---

If you want to do it all manually, follow these steps:

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
    #
    # or:
    llm=llm_15
    LLM=$SUBNET_1_6_JUDGE_LLM_15
    echo "llm = $llm"
    echo "LLM = $LLM"

    # Follow the logs
    dfx canister --network $NETWORK logs $LLM --follow

    # Remove the LLM from the protocol
    # for Challenger
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for ShareService
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for Judge
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         remove_llm_canister "(record {canister_id = \"$LLM\"})"

    # then upgrade
    # from folder: PoAIW/llms/xxx
    dfx canister --network $NETWORK status $llm | grep "Memory Size"
    dfx canister --network $NETWORK stop $llm
    dfx canister --network $NETWORK snapshot create $llm
    dfx deploy   --network $NETWORK $llm --mode upgrade
    dfx canister --network $NETWORK start $llm

    # Cleanup the prompt cache files
    # from folder: funnAI
    scripts/cleanup_llm_promptcache.sh --network $NETWORK --canister-id $LLM

    # Configure the LLM
    # from folder: PoAIW/llms/xxx
    dfx canister --network $NETWORK call $llm health
    dfx canister --network $NETWORK call $llm load_model '(record { args = vec {"--model"; "models/model.gguf"} })'
    dfx canister --network $NETWORK call $llm set_max_tokens '(record { max_tokens_query = 13 : nat64; max_tokens_update = 13 : nat64 })'
    dfx canister --network $NETWORK call $llm get_max_tokens
    dfx canister --network $NETWORK call $llm log_pause
    dfx canister --network $NETWORK call $llm chats_pause

    # Test operations manually (Copy/Paste all commands at once...)
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
    dfx canister --network $NETWORK call $llm recursive_dir_content_query  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json
    dfx canister --network $NETWORK call $llm remove_prompt_cache '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache"
        }
        })'
    dfx canister --network $NETWORK call $llm recursive_dir_content_update  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json
    dfx canister --network $NETWORK call $llm filesystem_remove '(record {filename = ".canister_cache/chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae/sessions"})'
    dfx canister --network $NETWORK call $llm filesystem_remove '(record {filename = ".canister_cache/chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"})'
    dfx canister --network $NETWORK call $llm filesystem_remove '(record {filename = ".canister_cache"})'
    dfx canister --network $NETWORK call $llm recursive_dir_content_query  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json

```


# Delete snapshots

```bash
    # We have a script to delete ALL snapshots for either ALL protocol canisters or a specified canister-id
    scripts/delete_snapshots.sh --network $NETWORK --canister-types [all/protocol/mainers] [--canister-id <canister-id>] [--dry-run] [--workers N]

    # You can do it manually with:
    LLM="<canister-id>"
    # list & delete the snapshot
    dfx canister --network $NETWORK snapshot list   $LLM
    dfx canister --network $NETWORK snapshot delete $LLM     <snapshot-id>
    # verify memory
    dfx canister --network $NETWORK status $llm | grep "Memory Size"
```

# Upgrade the mAIners

## IMPORTANT: Also upload wasm to mAInerCreator

## Using script

The following script is used to upgrade ALL or selected mAIners.

It puts the mAIner in MAINTENANCE mode and safely upgrades it.
A snapshot of the stopped canister before upgrade will be taken.
If something goes wrong with a canister, it will exit.
Just restore the canister from the snapshot, and run the script again.

The only errors seen so far is when the IC timed out. 
The script has been made robust against this using retry logic.

```bash
scripts/upgrade_mainers.sh --network [local|ic|testing|development|demo|prd] [--target-hash HASH] [--num NUM] [--mainer CANISTER_ID] [--user PRINCIPAL] [--dry-run] [--skip-preparation] [--ask-before-upgrade] [--reverse]

Options:
  --network NETWORK       Required. Network to upgrade mainers on
  --target-hash HASH      Optional. Target wasm hash to upgrade to (from 'dfx canister info <canister_id>')
  --num NUM               Optional. Number of mAIners to upgrade
  --mainer CANISTER_ID    Optional. Specific mAIner canister to upgrade
  --user PRINCIPAL        Optional. Principal ID of user whose mAIners to upgrade
  --dry-run               Optional. Run in dry-run mode without making changes
  --skip-preparation      Optional. Skip Step 1 preparation
  --ask-before-upgrade    Optional. Ask for confirmation before upgrading each canister
  --reverse               Optional. Process mainers in reverse order
  --deploy-with-yes       Optional. Will use: dfx deploy ... --yes

# from the folder: funnAI
conda activate llama_cpp_canister

# Option 1: Upgrade a specific mAIner of IConfucius
# -> eg: nkftb-zqaaa-aaaaa-qbbxa-cai is running at VeryHigh
MAINER=nkftb-zqaaa-aaaaa-qbbxa-cai
scripts/upgrade_mainers.sh --network $NETWORK --mainer $MAINER --ask-before-upgrade [--dry-run]
# -> It will print new wasm hash, which you set as the target hash for rest of deployment
TARGET_HASH=0xe7304d5490b6ad190bbebe14a1da8988e7a6e064afc697bdee90ffce902e67bc  # Nov 22, 2025 (release-4)
TARGET_HASH=0xad2c4545d533e4a01f81e9ec57c9bd16e1c5c358208ef8f9122f9c0e43ed547f  # Oct 25, 2025 (release-3)
TARGET_HASH=0x55ab6af1cdaf08ddd34776e7404aecd3eacba3b86ba03eb9196ddfd8113d50c2  # Oct 23, 2025 (release-2)
TARGET_HASH=0xf2a40400e1f0cc0896c976eb2efa7a902aff68266b69b4a6be0a077b022db819  # Oct 10, 2025 (release-1)
# By providing the target hash, the script will skip upgrade for mAIners already at that hash and healthy

# Upgrade 1 more mAIner of IConfucius on production network with confirmation prompt:
USER=xijdk-rtoet-smgxl-a4apd-ahchq-bslha-ope4a-zlpaw-ldxat-prh6f-jqe
scripts/upgrade_mainers.sh --network $NETWORK --user $USER --target-hash $TARGET_HASH --num 1 --ask-before-upgrade [--dry-run]

# Upgrade 2 more mAIners of IConfucius on production network, without confirmation prompt:
scripts/upgrade_mainers.sh --network $NETWORK --user $USER --target-hash $TARGET_HASH --num 2 [--dry-run]

# Upgrade ALL mAIners of IConfucius on production network without confirmation prompt:
scripts/upgrade_mainers.sh --network $NETWORK --user $USER --target-hash $TARGET_HASH [--dry-run]

# Upgrade 1 other mAIner on production network, with confirmation prompt:
scripts/upgrade_mainers.sh --network $NETWORK --num 1 --target-hash $TARGET_HASH [--dry-run]

# Upgrade 100 mainers on production network with target hash and without confirmation prompt:
scripts/upgrade_mainers.sh --network $NETWORK --num 100 --target-hash $TARGET_HASH [--dry-run]

# Upgrade ALL mainers on production network with target hash and without confirmation prompt:
scripts/upgrade_mainers.sh --network $NETWORK --target-hash $TARGET_HASH [--dry-run]
```

### Update Admin RBAC for mAIners

#### Using script

```bash
# To assign permissions
scripts/update_admin_rbac_mainers.sh --network $NETWORK --principal $FUNNAI_DJANGO_PRINCIPAL [--action assign] [--dry-run]

# To revoke permissions
scripts/update_admin_rbac_mainers.sh --network $NETWORK --principal $FUNNAI_DJANGO_PRINCIPAL --action revoke [--dry-run]
```

#### Manual

```bash
MAINER=...
# verify funnAI_django principal has #AdminQuery permissions
dfx canister --network $NETWORK call $MAINER getAdminRoles
dfx canister --network $NETWORK call $MAINER assignAdminRole '( record { "principal" = "'$FUNNAI_DJANGO_PRINCIPAL'"; role = variant { AdminQuery }; note = "Grant AdminQuery access for funnai-django" } )'
# if needed, this is how you revoke permissions for the previous principal
dfx canister --network $MAINER revokeAdminRole '( "'$FUNNAI_DJANGO_PRINCIPAL'")'
```

### Verify mAIners Health & Hash

After upgrade is completed, verify every mAIner is healthy and has correct module hash:

```bash
TARGET_HASH=0x...
scripts/get_mainers_health.sh --network $NETWORK --target-hash $TARGET_HASH
```

### Delete mAIners snapshots

Delete snapshot of all the mAIners:

```bash
scripts/delete_snapshots.sh --network $NETWORK --canister-types mainers [--dry-run]
```

## Old approach

An individual mAIner agent can be upgraded with the following commands:

```bash
NETWORK=prd
source scripts/canister_ids-$NETWORK.env
MAINER="<canister-id>"

echo NETWORK = $NETWORK
echo SUBNET_0_1_MAINER_CREATOR = $SUBNET_0_1_MAINER_CREATOR
echo MAINER  = $MAINER

# first check the logs, and make sure the mAIner is not doing anything
dfx canister --network $NETWORK logs $MAINER --follow

# monitor the mAInerCreator
dfx canister --network $NETWORK logs $SUBNET_0_1_MAINER_CREATOR --follow

# stop the mAIner > snapshot it > start it > upgrade
# mAIner must be running during upgrade for the configuration steps
dfx canister --network $NETWORK stop $MAINER
dfx canister --network $NETWORK snapshot create $MAINER
dfx canister --network $NETWORK start $MAINER
dfx canister --network $NETWORK call game_state_canister upgradeMainerControllerAdmin "(record {canisterAddress = \"$MAINER\" })"

# verify everything looks good (timer should have been restarted)
dfx canister --network $NETWORK logs $MAINER

# if it does not look good, restore the snapshot
dfx canister --network $NETWORK snapshot list $MAINER
dfx canister --network $NETWORK snapshot load $MAINER <snapshot-id>

# if all good, delete the snapshot
dfx canister --network $NETWORK snapshot list   $MAINER
dfx canister --network $NETWORK snapshot delete $MAINER <snapshot-id>
```

# Troubleshooting

## Judge calls to GameState fail with #Err(Unauthorized)

This happens if you reinstall the judge in the `testing` or `demo` network.
The default GAME_STATE_CANISTER_ID is for the `prd` network. 

Verify the log file, what canister id is used.

If wrong, set it to the correct value with:

```bash
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE setGameStateCanisterId "(\"$SUBNET_0_1_GAMESTATE\")"
```