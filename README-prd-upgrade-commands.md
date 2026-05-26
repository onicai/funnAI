
# Set NETWORK environment variable

```bash
# The principal of funnAI Django running on aws-dev (same for all networks)
FUNNAI_DJANGO_PRINCIPAL=bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe

# One of these... (note: it does not work for 'demo')
NETWORK=prd
NETWORK=testing
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
echo -n "MAINER_SHARE_AGENT_0002        = $MAINER_SHARE_AGENT_0002 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0002 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0003        = $MAINER_SHARE_AGENT_0003 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0003 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0004        = $MAINER_SHARE_AGENT_0004 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0004 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0005        = $MAINER_SHARE_AGENT_0005 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0005 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0006        = $MAINER_SHARE_AGENT_0006 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0006 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0007        = $MAINER_SHARE_AGENT_0007 - "; dfx canister --network $NETWORK status $MAINER_SHARE_AGENT_0007 | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
```

# stop timers of protocol canisters

In this order:

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_CHALLENGER
echo $SUBNET_0_1_SHARE_SERVICE
echo $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    stopTimerExecutionAdmin
# wait a couple of minutes..
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE stopTimerExecutionAdmin
# wait a couple of minutes..
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         stopTimerExecutionAdmin
# Wait until ShareService has nothing left in it's queue.
# -> pause is next step
```

# pause protocol

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_GAMESTATE
# check if it is already paused
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# then toggle it
dfx canister --network $NETWORK call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin
```

# upgrade the GameState

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_GAMESTATE

# from folder: PoAIW/src/GameState

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_GAMESTATE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_GAMESTATE

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/game_state_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_GAMESTATE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

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
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_CHALLENGER

# from folder: PoAIW/src/Challenger

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_CHALLENGER
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_CHALLENGER

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/challenger_ctrlb_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_CHALLENGER

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

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
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_SHARE_SERVICE

# from folder: PoAIW/src/mAIner

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_SHARE_SERVICE

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/mainer_service_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_SHARE_SERVICE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

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
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_SHARE_SERVICE

# from folder: PoAIW/src/mAIner
#
rm -rf .mops
mops install
#
# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_SHARE_SERVICE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_SHARE_SERVICE
#
dfx canister install --wasm out/mainer_service_canister.wasm \
    --network $NETWORK --mode reinstall --wasm-memory-persistence keep \
    $SUBNET_0_1_SHARE_SERVICE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

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
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_JUDGE

# from folder: PoAIW/src/Judge

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_JUDGE

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/judge_ctrlb_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_JUDGE

# When upgrade fails, do a reinstall
# -> WHEN REINSTALLING, THE LMMs need to be registered again! See step below
# dfx canister install --wasm out/judge_ctrlb_canister.wasm \
#   --network $NETWORK --mode reinstall --wasm-memory-persistence keep \
#    $SUBNET_0_1_JUDGE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Judge canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_JUDGE
dfx canister --network $NETWORK status $SUBNET_0_1_JUDGE     | grep Status
dfx canister --network $NETWORK call   $SUBNET_0_1_JUDGE health

# When reinstalled, issue these commands:
# re-register the LLMs, from PoAIW/src/Judge folder
# scripts/register-llms.sh --network $NETWORK

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
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_2_API

# from folder: PoAIW/src/Api

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_2_API
dfx canister --network $NETWORK snapshot create $SUBNET_0_2_API

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/api_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_2_API

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the API canister back up
dfx canister --network $NETWORK start  $SUBNET_0_2_API

# run a few tests to confirm data was preserved
dfx canister --network $NETWORK call $SUBNET_0_2_API getLatestDailyMetric --output json
dfx canister --network $NETWORK call $SUBNET_0_2_API getDailyMetrics '(opt record { start_date = opt "2025-12-21"; end_date = opt "2026-01-21"; limit = null })' --output json

# -------------------------------------------------------------------------
# Start the Activity Feed sync timer (Monitor Api canister logs to follow along)
# -------------------------------------------------------------------------
# The timer syncs winners and challenges from GameState every 300 seconds (default)

# Check current sync interval (should be 300 seconds / 5 minutes)
dfx canister --network $NETWORK call $SUBNET_0_2_API getActivityFeedSyncIntervalAdmin

# Optional: Change the sync interval (in seconds) if needed
# dfx canister --network $NETWORK call $SUBNET_0_2_API setActivityFeedSyncIntervalAdmin '(600)'

# Start the timer (will sync 5 seconds after starting, then every syncInterval seconds)
dfx canister --network $NETWORK call $SUBNET_0_2_API startActivityFeedTimerAdmin

# Wait ~10 seconds for first sync, then verify cache is populated
dfx canister --network $NETWORK call $SUBNET_0_2_API getActivityFeedCacheStatus --output json

# -------------------------------------------------------------------------
# Test the Activity Feed endpoints
# -------------------------------------------------------------------------

# Get activity feed with default pagination (20 winners, 20 challenges)
dfx canister --network $NETWORK call $SUBNET_0_2_API getActivityFeed '(record { winnersLimit = null; winnersOffset = null; challengesLimit = null; challengesOffset = null; sinceTimestamp = null })' --output json

# Get activity feed with custom pagination
dfx canister --network $NETWORK call $SUBNET_0_2_API getActivityFeed '(record { winnersLimit = opt 5; winnersOffset = opt 0; challengesLimit = opt 3; challengesOffset = opt 0; sinceTimestamp = null })' --output json

# Get open challenges from cache
dfx canister --network $NETWORK call $SUBNET_0_2_API getOpenChallengesFromCache --output json
```

## Update Admin RBAC for API canister

```bash
# verify funnAI_django principal has #AdminUpdate permissions
dfx canister --network $NETWORK call $SUBNET_0_2_API getAdminRoles
dfx canister --network $NETWORK call $SUBNET_0_2_API assignAdminRole '( record { "principal" = "'$FUNNAI_DJANGO_PRINCIPAL'"; role = variant { AdminUpdate }; note = "Grant AdminUpdate access for funnai-django" } )'
# if needed, this is how you revoke permissions for the previous principal
dfx canister --network $NETWORK call SUBNET_0_2_API revokeAdminRole '( "'$FUNNAI_DJANGO_PRINCIPAL'")'
```

# upgrade the ArchiveChallenges canister

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_2_ARCHIVE

# from folder: PoAIW/src/ArchiveChallenges

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_2_ARCHIVE
dfx canister --network $NETWORK snapshot create $SUBNET_0_2_ARCHIVE

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/archive_challenges_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_2_ARCHIVE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Archive canister back up
dfx canister --network $NETWORK start  $SUBNET_0_2_ARCHIVE
```

# upgrade the Treasury canister

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_TREASURY

# from folder: PoAIW/src/Treasury

# mops.toml was updated in latest PR
rm -rf .mops
mops install

dfx generate funnai_treasury_canister

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_TREASURY
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_TREASURY

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/funnai_treasury_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_TREASURY

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Treasury canister back up
dfx canister --network $NETWORK start  $SUBNET_0_1_TREASURY
```

# upgrade the ckSigner canister

The ckSigner canister requires a Schnorr key name in addition to the network.

Schnorr Key Names

| Schnorr Key Name | dfx network                 | Signing Cost | Subnet used for signing    |
| ---------------- | --------------------------- | ------------ | -------------------------- |
| `key_1`          | IC mainnet (prd)            | ~26B cycles  | 34-node fiduciary subnet   |
| `test_key_1`     | IC mainnet (testing)        | ~10B cycles  | 13-node application subnet |
| `dfx_test_key`   | Local replica (`dfx start`) | Free         | Local test subnet          |

```bash
# Set SCHNORR_KEY_NAME to match your NETWORK
# NETWORK=prd         -> SCHNORR_KEY_NAME="key_1"
# NETWORK=testing     -> SCHNORR_KEY_NAME="test_key_1"
# NETWORK=local       -> SCHNORR_KEY_NAME="dfx_test_key"
SCHNORR_KEY_NAME="key_1"

# Verify correct network & signing key!
echo "NETWORK=$NETWORK"
echo "SCHNORR_KEY_NAME=$SCHNORR_KEY_NAME"

# from folder: PoAIW/src/ckSigner

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop ck_signer_canister
dfx canister --network $NETWORK snapshot create ck_signer_canister

# ---------------------------------------------
# To upgrade
dfx canister install ck_signer_canister \
    --mode upgrade \
    --network $NETWORK \
    --wasm out/ck_signer_canister.wasm \
    --argument "(\"$SCHNORR_KEY_NAME\")" \
    --wasm-memory-persistence keep

# To reinstall
# When reinstalling, make sure the redo the steps of the section:
# "Configure fee tokens"
#
dfx canister install ck_signer_canister \
    --mode reinstall \
    --network $NETWORK \
    --wasm out/ck_signer_canister.wasm \
    --argument "(\"$SCHNORR_KEY_NAME\")"

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# Start the canister back up
dfx canister --network $NETWORK start ck_signer_canister
dfx canister --network $NETWORK status ck_signer_canister | grep Status
dfx canister --network $NETWORK call ck_signer_canister health

# Verify Treasury -> go to Configure Treasury section if wrong
dfx canister --network $NETWORK call ck_signer_canister getTreasury

# Verify fee token configuration
dfx canister --network $NETWORK call ck_signer_canister getFeeTokens

# If "Accepted tokens" is empty (e.g. after reinstall), add ckBTC:
#
# | Token | Ledger Canister ID          | Fee        |
# | ----- | --------------------------- | ---------- |
# | ckBTC | mxzaz-hqaaa-aaaar-qaada-cai | 100 (sats) |
#
dfx canister --network $NETWORK call ck_signer_canister addFeeToken \
    '(record { tokenName = "ckBTC"; tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai"; fee = 100 : nat })'
dfx canister --network $NETWORK call ck_signer_canister getFeeTokens
```

## Configure ckSigner treasury

The treasury is where all signing fees are sent. Default: funnAI Treasury Canister (prd).
After a reinstall, verify the treasury is correct. For testing, set it to the testing treasury.

```bash
echo "Using network: $NETWORK"

# Check current treasury
dfx canister --network $NETWORK call ck_signer_canister getTreasury

# Set treasury (only needed if default is wrong, e.g. for testing network)
# dfx canister --network $NETWORK call ck_signer_canister setTreasury  '(record { treasuryName = "<description>"; treasuryPrincipal = principal "<principal>" })'
```

## Configure ckSigner fee tokens

After upgrade, configure the accepted ICRC-2 fee tokens.

```bash
echo "Using network: $NETWORK"

# Check current fee token configuration
dfx canister --network $NETWORK call ck_signer_canister getFeeTokens

## Fee Token Configuration
#
# | Token | Ledger Canister ID          | Fee        |
# | ----- | --------------------------- | ---------- |
# | ckBTC | mxzaz-hqaaa-aaaar-qaada-cai | 100 (sats) |

dfx canister --network $NETWORK call ck_signer_canister addFeeToken \
    '(record { tokenName = "ckBTC"; tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai"; fee = 100 : nat })'

# Verify fee tokens are configured
dfx canister --network $NETWORK call ck_signer_canister getFeeTokens

# Verify sign rejects without payment (should return "Fee payment required" error)
dfx canister --network $NETWORK call ck_signer_canister sign \
    '(record { botName = "testbot"; message = blob "\00\01\02\03\04\05\06\07\08\09\0a\0b\0c\0d\0e\0f\10\11\12\13\14\15\16\17\18\19\1a\1b\1c\1d\1e\1f"; payment = null })'

# To remove a fee token (if needed):
# dfx canister --network $NETWORK call ck_signer_canister removeFeeToken \
#     '(record { tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai" })'
```

# upgrade the mAInerCreator

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_MAINER_CREATOR

# from folder: PoAIW/src/mAInerCreator
# Generate the bindings for the upload scripts and the frontend
dfx generate mainer_creator_canister

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

dfx canister --network $NETWORK stop $SUBNET_0_1_MAINER_CREATOR
dfx canister --network $NETWORK snapshot create $SUBNET_0_1_MAINER_CREATOR

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/mainer_creator_canister.wasm \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    $SUBNET_0_1_MAINER_CREATOR

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

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
# From folder: PoAIW/llms/llama_cpp_canister/build
shasum -a 256 llama_cpp.wasm # confirm it is the deployed llm wasm
cp llama_cpp.did ../../../src/mAInerCreator/files/llama_cpp.did
cp llama_cpp.wasm ../../../src/mAInerCreator/files/llama_cpp.wasm
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

# upgrade the funnai_backend

```bash
# Verify correct network & canister settings !
echo $NETWORK

# from folder: funnAI/src/funnai_backend

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
# The base image is shared across all canisters of the funnAI repo.
# Once built, it can be reused. (The PoAIW repo has its own, separate base image.)
make docker-build-base
make docker-build-wasm

dfx generate funnai_backend
dfx canister --network $NETWORK stop funnai_backend
dfx canister --network $NETWORK snapshot create funnai_backend

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
dfx canister install --wasm out/funnai_backend.wasm \
    --argument "( principal \"$(dfx identity get-principal)\" )" \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    funnai_backend


# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

dfx canister --network $NETWORK start funnai_backend
```

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

dfx canister --network $NETWORK snapshot list   ck_signer_canister
dfx canister --network $NETWORK snapshot delete  ck_signer_canister <snapshot-id>
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

dfx canister --network $NETWORK stop ck_signer_canister
dfx canister --network $NETWORK snapshot list ck_signer_canister
dfx canister --network $NETWORK snapshot load ck_signer_canister <snapshot-id>
dfx canister --network $NETWORK start ck_signer_canister
dfx canister --network $NETWORK call ck_signer_canister health

# start canisters > start timers > unpause, as described above
```

--------------------------------------------------------

# Deploy or Upgrade LLMs

## IMPORTANT: Also upload wasm to mAInerCreator

Even though we are not using the mAInerCreator to upgrade mAIners, it
is important to keep the wasm file up to date.

## Get latest llama_cpp_canister release

Store latest release in the folder PoAIW/llms/llama_cpp_canister
Follow instructions of PoAIW/llms/llama_cpp_canister/README-instructions.md

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

### Using script (recommended)

The `deploy_llm.sh` script automates the full deployment of a new LLM canister:
creates it on a subnet, uploads the model, configures controllers, admin roles,
log viewers, and tests the LLM.

```bash
# from folder: funnAI
# Activate the conda environment
conda activate llama_cpp_canister

# Dry run first to see what will happen
scripts/deploy_llm.sh --network $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>] --dry-run

# Deploy for real
scripts/deploy_llm.sh --network $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>]
```

The script will:
1. Find the next available `llm_N` index in `canister_ids.json`
2. Ensure the entry exists in `dfx.json`
3. Auto-select a subnet with < 3 LLMs (or use `--subnet` to override)
4. Deploy, health-check, verify subnet, configure controllers & admin roles
5. Upload and load the model, set max_tokens, pause logs/chats
6. Add log viewers, test the LLM
7. Update `canister_ids.json` and `canister_ids-{network}.env`

If deployment fails partway through, the script prints the canister ID and
a `delete_llm.sh` command to clean up.

**Next step: add the LLM to the protocol**
- See section below: "Add new LLM to the protocol"

### Manually using dfx commands

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

### Using script (recommended)

The `add_llm.sh` script adds a deployed LLM to the protocol by registering it
with the controller canister and updating the GameState LLM count.

```bash
# from folder: funnAI

# Dry run first
scripts/add_llm.sh --network $NETWORK --canister-id <canister-id> --dry-run

# Add for real
scripts/add_llm.sh --network $NETWORK --canister-id <canister-id>
```

The script will:
1. Show current LLMs registered in the controller
2. Call `add_llm_canister` on the controller
3. Verify the LLM count increased
4. Update GameState via `setCyclesFlowAdmin` (`numChallengerLlms` / `numJudgeLlms` / `numShareServiceLlms`)

**Manual step after add_llm.sh:**
- Register the new canister in funnAI_django's `CanisterRegistry`
  Required for cache cleanup tasks to include the new LLM.
- Register the canister with CycleOps (adds controller `2daxo-giaaa-aaaap-anvca-cai`)
- Record the new subnet (if new) in the tracking spreadsheet:
  https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0



### Manually using dfx commands

#### For Challenger
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

#### For ShareService
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

#### For Judge
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

**Manual step after adding:**
- Register the new canister in funnAI_django's `CanisterRegistry`
  (see `funnAI_django/src/apps/canisters/management/commands/import_canister_ids.py`).
  Required for cache cleanup tasks to include the new LLM.


## Delete an LLM

### Using script (recommended)

The `delete_llm.sh` script removes an LLM from the protocol, deletes the canister
(returning cycles to the wallet), and cleans up `canister_ids.json` and the env file.

```bash
# from folder: funnAI

# Dry run first
scripts/delete_llm.sh --network $NETWORK --canister-id <canister-id> --dry-run

# Delete for real
scripts/delete_llm.sh --network $NETWORK --canister-id <canister-id>
```

The script will:
1. Check cycles balance
2. Remove the LLM from the controller canister
3. Wait 180 seconds for in-flight requests to complete
4. Delete the canister (cycles returned to wallet)
5. Remove entry from `canister_ids.json`
6. Remove entry from `canister_ids-{network}.env`

**Manual step after delete_llm.sh:**
- Remove the LLM canister from funnAI_django's `CanisterRegistry`
  (see `funnAI_django/src/apps/canisters/management/commands/import_canister_ids.py`).
  Required so cache cleanup tasks stop referencing the deleted canister.

### Manually using dfx commands

```bash
    NETWORK=prd
    source scripts/canister_ids-$NETWORK.env
    LLM="<canister-id>"

    # Remove from controller (pick the right one for your LLM type)
    # For Challenger
    dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # For ShareService
    dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # For Judge
    dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         remove_llm_canister "(record {canister_id = \"$LLM\"})"

    # Wait for in-flight requests (180 seconds recommended)
    sleep 180

    # Delete the canister (cycles returned to wallet)
    dfx canister --network $NETWORK delete $LLM

    # Manually clean up:
    # - Remove entry from canister_ids.json in the LLM directory
    # - Remove entry from funnAI/scripts/canister_ids-{network}.env
    # - Remove from funnAI_django CanisterRegistry
```


## Replace an LLM (delete + deploy + add)

To replace an existing LLM (e.g. moving it to a different subnet):

```bash
# 1. Delete the old LLM
scripts/delete_llm.sh --network $NETWORK --canister-id <old-canister-id>

# 2. Deploy a new LLM
scripts/deploy_llm.sh --network $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>]

# 3. Add the new LLM to the protocol
scripts/add_llm.sh --network $NETWORK --canister-id <new-canister-id>

# 4. Manual steps:
#    - Remove old canister from funnAI_django CanisterRegistry
#    - Register new canister in funnAI_django CanisterRegistry
#    - Register new canister with CycleOps
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

> **dfx version note (2026-04-16):** the ShareAgent mAIners were last upgraded/reinstalled on 2026-04-16 with **dfx 0.31.0**. All other canisters (frontend, backend, and PoAIW protocol canisters) are still on **dfx 0.29.2** (pinned in `PoAIW/src/GameState/docker/docker-compose.yml`). Keep this mismatch in mind when regenerating declarations or reproducing wasm hashes — newer dfx versions emit different JS codegen (e.g. importing from `@icp-sdk/core/agent` instead of `@dfinity/agent`), which can break the frontend build if regenerated wholesale.

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
scripts/upgrade_mainers.sh --network [local|ic|testing|development|demo|prd] [--target-hash HASH] [--num NUM] [--mainer CANISTER_ID] [--user PRINCIPAL] [--dry-run] [--skip-preparation] [--ask-before-upgrade] [--reverse] [--deploy-with-yes] [--reinstall]

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
  --reinstall             Optional. Reinstall (`--mode reinstall`) instead of upgrade. WIPES all stable
                          state on each canister. Use after capping unbounded stable lists to reset
                          accumulated memory back to baseline. Mutually exclusive with `--target-hash`.

# Reinstall ONE mAIner first to verify, then roll out in batches:
scripts/upgrade_mainers.sh --network $NETWORK --reinstall --mainer $MAINER --dry-run
scripts/upgrade_mainers.sh --network $NETWORK --reinstall --mainer $MAINER
scripts/upgrade_mainers.sh --network $NETWORK --reinstall --num 10
# (Top-up of low-balance canisters happens automatically before each (re)install.)

# from the folder: funnAI
conda activate llama_cpp_canister

# Option 1: Upgrade a specific mAIner of IConfucius
# -> eg: nkftb-zqaaa-aaaaa-qbbxa-cai is running at VeryHigh
MAINER=nkftb-zqaaa-aaaaa-qbbxa-cai
scripts/upgrade_mainers.sh --network $NETWORK --mainer $MAINER --ask-before-upgrade [--dry-run]
# -> It will print new wasm hash, which you set as the target hash for rest of deployment
TARGET_HASH=0x2dbae383acd69e45ee48c35d71c1af87ac8261876daa458beb62e46547ed587d  # Mar 22, 2026 (AdminRBAC for ChallengeQueue endpoints)
TARGET_HASH=0xf20306cea7159e1fe5a023e2a3b3b1b4acb795341b5a6f0cd3de0526866f649e  # Jan 15, 2026 (release-8; SNS)
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