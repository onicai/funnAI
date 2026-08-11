
# Set NETWORK environment variable

```bash
# Maintainer development principals (same for all networks). Needed for admin
# access post-SNS, when the controller (isController) route belongs only to
# NNS/SNS root and AdminRBAC is the remaining maintenance path.
# Your own principal, so this runbook works for whoever is running it.
MAINTAINER=$(icp identity principal)
PATRICK=cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe

# One of these...
NETWORK=prd
NETWORK=testing
NETWORK=development

echo " "
echo "Using network type: $NETWORK"

source scripts/canister_ids-$NETWORK.env
source scripts/canister_ids_mainers-$NETWORK.env

# Check status of some canisters
echo -n "SUBNET_0_1_GAMESTATE           = $SUBNET_0_1_GAMESTATE - "; icp canister status $SUBNET_0_1_GAMESTATE -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_MAINER_CREATOR      = $SUBNET_0_1_MAINER_CREATOR - "; icp canister status $SUBNET_0_1_MAINER_CREATOR -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_CHALLENGER          = $SUBNET_0_1_CHALLENGER - "; icp canister status $SUBNET_0_1_CHALLENGER -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_JUDGE               = $SUBNET_0_1_JUDGE - "; icp canister status $SUBNET_0_1_JUDGE -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_SHARE_SERVICE       = $SUBNET_0_1_SHARE_SERVICE - "; icp canister status $SUBNET_0_1_SHARE_SERVICE -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_BACKEND             = $SUBNET_0_1_BACKEND - "; icp canister status $SUBNET_0_1_BACKEND -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_1_FRONTEND            = $SUBNET_0_1_FRONTEND - "; icp canister status $SUBNET_0_1_FRONTEND -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_0_2_API                 = $SUBNET_0_2_API - "; icp canister status $SUBNET_0_2_API -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_1_CHALLENGER_LLM_0    = $SUBNET_1_1_CHALLENGER_LLM_0 - "; icp canister status $SUBNET_1_1_CHALLENGER_LLM_0 -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_1_1_JUDGE_LLM_0         = $SUBNET_1_1_JUDGE_LLM_0 - "; icp canister status $SUBNET_1_1_JUDGE_LLM_0 -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "SUBNET_2_1_SHARE_SERVICE_LLM_0 = $SUBNET_2_1_SHARE_SERVICE_LLM_0 - "; icp canister status $SUBNET_2_1_SHARE_SERVICE_LLM_0 -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0000        = $MAINER_SHARE_AGENT_0000 - "; icp canister status $MAINER_SHARE_AGENT_0000 -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
echo -n "MAINER_SHARE_AGENT_0001        = $MAINER_SHARE_AGENT_0001 - "; icp canister status $MAINER_SHARE_AGENT_0001 -e $NETWORK | grep -E "(Status|Balance)" | tr '\n' ' ' | sed 's/  */ /g'; echo
```

# stop timers of protocol canisters

In this order:

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_CHALLENGER
echo $SUBNET_0_1_SHARE_SERVICE
echo $SUBNET_0_1_JUDGE
icp canister call $SUBNET_0_1_CHALLENGER    stopTimerExecutionAdmin
# wait a couple of minutes..
icp canister call $SUBNET_0_1_SHARE_SERVICE stopTimerExecutionAdmin
# wait a couple of minutes..
icp canister call $SUBNET_0_1_JUDGE         stopTimerExecutionAdmin
# Wait until ShareService has nothing left in it's queue.
# -> pause is next step
```

# pause protocol

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_GAMESTATE
# check if it is already paused
icp canister call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# then toggle it
icp canister call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin
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

icp canister stop $SUBNET_0_1_GAMESTATE -e $NETWORK
icp canister snapshot create $SUBNET_0_1_GAMESTATE -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_GAMESTATE --wasm out/game_state_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the GameState canister back up
icp canister start $SUBNET_0_1_GAMESTATE -e $NETWORK
icp canister status $SUBNET_0_1_GAMESTATE -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_GAMESTATE health

# verify that it is still paused
icp canister call   $SUBNET_0_1_GAMESTATE getPauseProtocolFlag

# Update the wasm-hash, using the Admin owned test mAIner ShareAgent
echo $MAINER_SHARE_AGENT_0001
icp canister call   $SUBNET_0_1_GAMESTATE deriveNewMainerAgentCanisterWasmHashAdmin "(record {address=\"$MAINER_SHARE_AGENT_0001\"; textNote=\"Protocol upgrade\"})"

# If needed, initialize the openSubmissionsQueue. 
# -> Tyically not needed. Was created during introduction of new openSubmissionsQueue
# -> Needed if getNumOpenSubmissionsAdmin > 0 , while getNumOpenSubmissionsForOpenChallengesAdmin = 0
icp canister call   $SUBNET_0_1_GAMESTATE initializeOpenSubmissionsQueueAdmin

icp canister call   $SUBNET_0_1_GAMESTATE getNumOpenSubmissionsAdmin
icp canister call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsAdmin

icp canister call   $SUBNET_0_1_GAMESTATE getNumOpenSubmissionsForOpenChallengesAdmin
icp canister call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsForOpenChallengesAdmin

icp canister call   $SUBNET_0_1_GAMESTATE getOpenSubmissionsQueueSizeAdmin

# Update the protocol thresholds, if needed.
icp canister call game_state_canister getGameStateThresholdsAdmin

icp canister call game_state_canister setGameStateThresholdsAdmin '( record {
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
icp canister call game_state_canister getCyclesFlowAdmin | grep dailySubmissionsAllShare

# set the values, which will trigger a recalculation
icp canister call game_state_canister setCyclesFlowAdmin '( record { dailySubmissionsAllShare = opt (4752 : nat);})'
```

## Update Admin RBAC for GameState

Grant the maintainer principals `#AdminUpdate` so they keep admin access post-SNS.

```bash
# verify which principals already have admin roles
icp canister call game_state_canister getAdminRoles
# grant #AdminUpdate to the maintainer principals (arjaan, patrick)
icp canister call game_state_canister assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call game_state_canister assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'
# if needed, this is how you revoke permissions for a principal
# icp canister call game_state_canister revokeAdminRole '( "'$MAINTAINER'")'
```

# upgrade the Challenger

> **After upgrade, re-arm both transient timers** (both are cleared by every
> upgrade): `startTimerExecutionAdmin` (recurring action) and
> `startSendCyclesTimerAdmin` (send-cycles drain). In a full-protocol upgrade
> these are started in the batch sections near the end of this doc — see
> `# start timers of protocol canisters` and
> `# Cycle capping: start the send-cycles drain timers`.

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

icp canister stop $SUBNET_0_1_CHALLENGER -e $NETWORK
icp canister snapshot create $SUBNET_0_1_CHALLENGER -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_CHALLENGER --wasm out/challenger_ctrlb_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Challenger canister back up
# Important
# The IS_GENERATING_CHALLENGE flag is not reset during a stop/start of the canister
# Make sure to call resetIsGeneratingChallengeFlag after start
#
icp canister start $SUBNET_0_1_CHALLENGER -e $NETWORK
icp canister call   $SUBNET_0_1_CHALLENGER resetIsGeneratingChallengeFlag
icp canister status $SUBNET_0_1_CHALLENGER -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_CHALLENGER health
icp canister call   $SUBNET_0_1_CHALLENGER getIsGeneratingChallengeFlag

# fill the LLM data storage - No longer needed. Is in stable storage
# -> Run it in case a reinstall is needed
# scripts/register-llms.sh -e $NETWORK

# Verify registered LLMs
icp canister call $SUBNET_0_1_CHALLENGER    get_llm_canisters

# Verify timer setting
icp canister call $SUBNET_0_1_CHALLENGER getTimerActionRegularityInSecondsAdmin
```

## Update Admin RBAC for Challenger

Grant the maintainer principals `#AdminUpdate` so they retain admin access
post-SNS (after decentralization the `isController` path belongs only to
NNS/SNS root). One-time per network — the role assignment persists across upgrades.

```bash
# verify which principals already have admin roles
icp canister call $SUBNET_0_1_CHALLENGER getAdminRoles
# grant #AdminUpdate to the maintainer principals (arjaan, patrick)
icp canister call $SUBNET_0_1_CHALLENGER assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call $SUBNET_0_1_CHALLENGER assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'
# verify
icp canister call $SUBNET_0_1_CHALLENGER getAdminRoles
# if needed, revoke
# icp canister call $SUBNET_0_1_CHALLENGER revokeAdminRole '( "'$MAINTAINER'")'
```

# upgrade the ShareService

> **After upgrade, re-arm both transient timers** (both are cleared by every
> upgrade): `startTimerExecutionAdmin` (recurring action) and
> `startSendCyclesTimerAdmin` (send-cycles drain). In a full-protocol upgrade
> these are started in the batch sections near the end of this doc — see
> `# start timers of protocol canisters` and
> `# Cycle capping: start the send-cycles drain timers`.

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

icp canister stop $SUBNET_0_1_SHARE_SERVICE -e $NETWORK
icp canister snapshot create $SUBNET_0_1_SHARE_SERVICE -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_SHARE_SERVICE --wasm out/mainer_service_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the ShareService canister back up
echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
icp canister start $SUBNET_0_1_SHARE_SERVICE -e $NETWORK
icp canister status $SUBNET_0_1_SHARE_SERVICE -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_SHARE_SERVICE health

# Verify registered LLMs
icp canister call $SUBNET_0_1_SHARE_SERVICE get_llm_canisters

# Verify timer setting
icp canister call $SUBNET_0_1_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin
```

## Update Admin RBAC for ShareService

Grant the Api canister `#AdminQuery` so it can pull the ShareAgent
registry+activity snapshot via `getShareAgentRegistryWithActivityAdmin`.
Required for the on-chain daily-metrics aggregation. One-time per network —
role assignments survive an **upgrade**.

> 🚨 **They do NOT survive a `--mode reinstall`.** A reinstall wipes stable state, and the
> admin roles go with it. Re-run **every** assignment in this section afterwards, including
> the mAInerCreator one below — and then actually read back `getAdminRoles` to confirm.
> A missing role here fails **silently**: the callers that need it swallow the
> `#Err(#Unauthorized)`, so everything reports success while doing nothing.

```bash
# verify which principals already have admin roles
icp canister call $SUBNET_0_1_SHARE_SERVICE getAdminRoles

# grant #AdminQuery to the Api canister
echo "$SUBNET_0_2_API"
icp canister call $SUBNET_0_1_SHARE_SERVICE assignAdminRole '( record { "principal" = "'$SUBNET_0_2_API'"; role = variant { AdminQuery }; note = "Daily metrics pull from Api canister" } )'

# grant #AdminUpdate to the maintainer principals (arjaan, patrick) for maintenance (post-SNS)
icp canister call $SUBNET_0_1_SHARE_SERVICE assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call $SUBNET_0_1_SHARE_SERVICE assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'

# 🚨 REQUIRED, AND EASY TO MISS: grant #AdminUpdate to the mAInerCreator canister.
#
# Every ShareAgent it creates or reinstalls is registered with the ShareService via
# addMainerShareAgentCanister, which is gated on hasAdminRole(caller, #AdminUpdate).
# Without this role the call returns #Err(#Unauthorized) -- and mAInerCreator SWALLOWS
# that error (the `return #Err` is commented out), so the creation reports success while
# the agent is silently absent from the registry and is never given any work.
#
# This bit us in prd on 2026-08-10: the role was missing (presumably lost in an earlier
# ShareService reinstall and never re-added), and every auction mAIner came up inert.
# Verify with getShareAgentRegistryWithActivityAdmin that a newly created mAIner actually
# appears in the registry -- that is the only reliable check, since the error is swallowed.
#
# Assign the ROLE, not controllership -- the role is what the code checks and is narrower.
echo "$SUBNET_0_1_MAINER_CREATOR"
icp canister call $SUBNET_0_1_SHARE_SERVICE assignAdminRole '( record { "principal" = "'$SUBNET_0_1_MAINER_CREATOR'"; role = variant { AdminUpdate }; note = "mAInerCreator: register new ShareAgents" } )'

# verify -- mAInerCreator MUST appear in this list with AdminUpdate
icp canister call $SUBNET_0_1_SHARE_SERVICE getAdminRoles

# if needed, revoke
# icp canister call $SUBNET_0_1_SHARE_SERVICE revokeAdminRole '( "'$SUBNET_0_2_API'")'
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

icp canister stop $SUBNET_0_1_SHARE_SERVICE -e $NETWORK
icp canister snapshot create $SUBNET_0_1_SHARE_SERVICE -e $NETWORK
#
icp canister install $SUBNET_0_1_SHARE_SERVICE --wasm out/mainer_service_canister.wasm \
    -e $NETWORK --mode reinstall --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the ShareService canister back up
echo "SUBNET_0_1_SHARE_SERVICE: $SUBNET_0_1_SHARE_SERVICE"
icp canister start $SUBNET_0_1_SHARE_SERVICE -e $NETWORK
icp canister status $SUBNET_0_1_SHARE_SERVICE -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_SHARE_SERVICE health

# Verify timer setting
icp canister call $SUBNET_0_1_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin

# register game state
icp canister call $SUBNET_0_1_SHARE_SERVICE setGameStateCanisterId '("'$SUBNET_0_1_GAMESTATE'")'
icp canister call $SUBNET_0_1_SHARE_SERVICE getGameStateCanisterId

# register the LLMs
# from folder: PoAIW/src/mAIner
icp canister call $SUBNET_0_1_SHARE_SERVICE get_llm_canisters
# register every LLM with the ShareService with this command
CANISTER_ID_LLM=...
icp canister call $SUBNET_0_1_SHARE_SERVICE add_llm_canister '(record { canister_id = "'$CANISTER_ID_LLM'" })'

# register all the ShareAgent mAIners, by upgrading them via GameState > mAInerCreator
# -> This will take care of all proper registrations
MAINER=...
# snapshot
icp canister stop $MAINER -e $NETWORK
icp canister snapshot create $MAINER -e $NETWORK
icp canister start $MAINER -e $NETWORK
# set correct type & register ShareAgent with ShareService
icp canister call -e $NETWORK $MAINER setMainerCanisterType '(variant {ShareAgent} )'
icp canister call -e $NETWORK $MAINER setShareServiceCanisterId '("'$SUBNET_0_1_SHARE_SERVICE'")'
icp canister call $SUBNET_0_1_GAMESTATE upgradeMainerControllerAdmin "(record {canisterAddress = \"$MAINER\" })"
# Note: it will fail if maintenance flag is on. Toggle it and retry
icp canister call $MAINER getMaintenanceFlag
icp canister call $MAINER toggleMaintenanceFlagAdmin # it must be off !
# verify
icp canister call -e $NETWORK $MAINER getMainerCanisterType
icp canister call $MAINER getGameStateCanisterId 
icp canister call $MAINER health
icp canister call $MAINER getMaintenanceFlag
```

# upgrade the Judge

> **After upgrade, re-arm both transient timers** (both are cleared by every
> upgrade): `startTimerExecutionAdmin` (recurring action) and
> `startSendCyclesTimerAdmin` (send-cycles drain). In a full-protocol upgrade
> these are started in the batch sections near the end of this doc — see
> `# start timers of protocol canisters` and
> `# Cycle capping: start the send-cycles drain timers`.

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

icp canister stop $SUBNET_0_1_JUDGE -e $NETWORK
icp canister snapshot create $SUBNET_0_1_JUDGE -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_JUDGE --wasm out/judge_ctrlb_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# When upgrade fails, do a reinstall
# -> WHEN REINSTALLING, THE LMMs need to be registered again! See step below
# icp canister install --wasm out/judge_ctrlb_canister.wasm \
#   -e $NETWORK --mode reinstall --wasm-memory-persistence keep \
#    $SUBNET_0_1_JUDGE

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Judge canister back up
icp canister start $SUBNET_0_1_JUDGE -e $NETWORK
icp canister status $SUBNET_0_1_JUDGE -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_JUDGE health

# When reinstalled, issue these commands:
# re-register the LLMs, from PoAIW/src/Judge folder
# scripts/register-llms.sh -e $NETWORK

# set the timer
icp canister call $SUBNET_0_1_JUDGE getTimerActionRegularityInSecondsAdmin
icp canister call $SUBNET_0_1_JUDGE setTimerActionRegularityInSecondsAdmin '(15)'

# reset the isProcessingSubmissions flag
icp canister call   $SUBNET_0_1_JUDGE resetIsProcessingSubmissionsAdmin

# Verify registered LLMs
icp canister call $SUBNET_0_1_JUDGE    get_llm_canisters --output json
```

## Update Admin RBAC for Judge

Grant the maintainer principals `#AdminUpdate` so they retain admin access
post-SNS (after decentralization the `isController` path belongs only to
NNS/SNS root). One-time per network — the role assignment persists across upgrades.

```bash
# verify which principals already have admin roles
icp canister call $SUBNET_0_1_JUDGE getAdminRoles
# grant #AdminUpdate to the maintainer principals (arjaan, patrick)
icp canister call $SUBNET_0_1_JUDGE assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call $SUBNET_0_1_JUDGE assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'
# verify
icp canister call $SUBNET_0_1_JUDGE getAdminRoles
# if needed, revoke
# icp canister call $SUBNET_0_1_JUDGE revokeAdminRole '( "'$MAINTAINER'")'
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

icp canister stop $SUBNET_0_2_API -e $NETWORK
icp canister snapshot create $SUBNET_0_2_API -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_2_API --wasm out/api_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the API canister back up
icp canister start $SUBNET_0_2_API -e $NETWORK

# run a few tests to confirm data was preserved
icp canister call $SUBNET_0_2_API getLatestDailyMetric --output json
icp canister call $SUBNET_0_2_API getDailyMetrics '(opt record { start_date = opt "2025-12-21"; end_date = opt "2026-01-21"; limit = null })' --output json

# -------------------------------------------------------------------------
# Start the Activity Feed sync timer (Monitor Api canister logs to follow along)
# -------------------------------------------------------------------------
# The timer syncs winners and challenges from GameState every 300 seconds (default)

# Check current sync interval (should be 300 seconds / 5 minutes)
icp canister call $SUBNET_0_2_API getActivityFeedSyncIntervalAdmin

# Optional: Change the sync interval (in seconds) if needed
# icp canister call $SUBNET_0_2_API setActivityFeedSyncIntervalAdmin '(600)'

# Start the timer (will sync 5 seconds after starting, then every syncInterval seconds)
icp canister call $SUBNET_0_2_API startActivityFeedTimerAdmin

# Wait ~10 seconds for first sync, then verify cache is populated
icp canister call $SUBNET_0_2_API getActivityFeedCacheStatus --output json

# -------------------------------------------------------------------------
# Test the Activity Feed endpoints
# -------------------------------------------------------------------------

# Get activity feed with default pagination (20 winners, 20 challenges)
icp canister call $SUBNET_0_2_API getActivityFeed '(record { winnersLimit = null; winnersOffset = null; challengesLimit = null; challengesOffset = null; sinceTimestamp = null })' --output json

# Get activity feed with custom pagination
icp canister call $SUBNET_0_2_API getActivityFeed '(record { winnersLimit = opt 5; winnersOffset = opt 0; challengesLimit = opt 3; challengesOffset = opt 0; sinceTimestamp = null })' --output json

# Get open challenges from cache
icp canister call $SUBNET_0_2_API getOpenChallengesFromCache --output json
```

## Update Admin RBAC for API canister

```bash
# verify which principals already have admin roles
icp canister call $SUBNET_0_2_API getAdminRoles
# grant #AdminUpdate to the maintainer principals (arjaan, patrick)
icp canister call $SUBNET_0_2_API assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call $SUBNET_0_2_API assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'
# if needed, this is how you revoke permissions for a principal
# icp canister call $SUBNET_0_2_API revokeAdminRole '( "'$MAINTAINER'")'
```

## On-chain Daily Metrics setup for the API canister

After every API canister upgrade, point it at this network's ShareService
(`SHARE_SERVICE_CANISTER_ID` defaults to the prd canister id), then start the
pricing timer. Both timers (pricing + daily-metrics) are `transient` — they
do **not** auto-restart on upgrade.

```bash
# Verify the current ShareService canister id on the API canister
icp canister call $SUBNET_0_2_API getShareServiceCanisterIdAdmin

# Set it to this network's ShareService (idempotent — safe to run on prd too)
icp canister call $SUBNET_0_2_API setShareServiceCanisterIdAdmin '("'$SUBNET_0_1_SHARE_SERVICE'")'

# Start the pricing timer (HTTPS outcalls Coinbase + IC API every hour; refreshes immediately on start)
icp canister call $SUBNET_0_2_API startPricingTimerAdmin

# Verify the pricing cache populated with real upstream values
icp canister call $SUBNET_0_2_API getPricingCacheAdmin
```

## Daily Metrics admin smoke tests for the API canister

Verifies the inter-canister read of the ShareService snapshot, the
aggregation path, and the pricing enrichment — **without writing** anything
into the canister's `dailyMetrics` storage. Safe to run any time, including
during the rollout window when Django is still the authoritative writer.

```bash
# Cross-canister read of ShareService (requires the #AdminQuery grant — see ShareService section)
icp canister call $SUBNET_0_2_API pullShareServiceSnapshotAdmin

# Run-status: expect timerActive = false right after upgrade
icp canister call $SUBNET_0_2_API getDailyMetricsRunStatusAdmin

# Compute the metric for yesterday WITHOUT storing it. Inspect the returned
# record to verify the aggregation, pricing, and date look right.
icp canister call $SUBNET_0_2_API previewDailyMetricsAggregationAdmin
```

> When you are ready to start writing the row to canister storage, use
> `triggerDailyMetricsAggregationAdmin` instead — that one writes via
> `storeDailyMetric` (last-writer-wins against any Django write for the same
> date).

## Start the Daily Metrics recurring timer

> ⚠️ Only start AFTER all ShareAgent mAIners have been upgraded AND the
> activity registry has had at least 25 hours to warm up. Before that, the
> recurring timer would write wrong numbers over Django's authoritative row
> every 24 h.

```bash
# Verify the warm-up: activity list should be close to registry size (≥80%)
icp canister call $SUBNET_0_2_API pullShareServiceSnapshotAdmin

# Start the daily-metrics timer (anchored to 00:00 UTC; recurring every 24h)
icp canister call $SUBNET_0_2_API startDailyMetricsTimerAdmin

# Verify
icp canister call $SUBNET_0_2_API getDailyMetricsRunStatusAdmin
```

To stop the daily-metrics timer (e.g. rolling back to the Django writer):

```bash
icp canister call $SUBNET_0_2_API stopDailyMetricsTimerAdmin
```

## Burn-scan setup for the API canister

The burn-scan timer walks the FUNNAI `TokenIndex` canister (ICRC-3 blocks)
and accumulates the running total of burned tokens into `totalBurnedE8s`.
Like every other timer on the Api canister, it does **not** auto-restart
across upgrades and must be started explicitly after every upgrade.

On the first start after upgrading from a build that didn't have this
feature, the scanner starts at block 0 and self-schedules 5-second
follow-ups until it catches up to the head of `TokenIndex`. Expect ~6
hours of catch-up time and non-trivial cycle consumption (each batch
fetches ~250 KB of inter-canister data). After catch-up, the recurring
hourly tick just processes whatever new blocks accumulated in the last
hour.

```bash
# Verify the TokenIndex canister id the Api canister will scan.
# Default points at prd; non-prd networks must override (next command).
icp canister call $SUBNET_0_2_API getTokenIndexCanisterIdAdmin

# Set it for this network (idempotent — safe to run on prd too)
TOKEN_INDEX="<this-network's-token-index-canister-id>"
icp canister call $SUBNET_0_2_API setTokenIndexCanisterIdAdmin "(\"$TOKEN_INDEX\")"

# Start the burn-scan timer (runs one scan immediately, then every hour)
icp canister call $SUBNET_0_2_API startBurnScanTimerAdmin

# Read the current running total + scan cursor
icp canister call --query $SUBNET_0_2_API getTotalBurned
```

To stop the timer (e.g. before a planned upgrade or for ops investigation):

```bash
icp canister call $SUBNET_0_2_API stopBurnScanTimerAdmin
```

To force a one-shot scan without touching the recurring timer:

```bash
icp canister call $SUBNET_0_2_API triggerBurnScanAdmin
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

icp canister stop $SUBNET_0_2_ARCHIVE -e $NETWORK
icp canister snapshot create $SUBNET_0_2_ARCHIVE -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_2_ARCHIVE --wasm out/archive_challenges_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Archive canister back up
icp canister start $SUBNET_0_2_ARCHIVE -e $NETWORK
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

# (no `icp` equivalent to `dfx generate` -- src/declarations/ is committed)

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

icp canister stop $SUBNET_0_1_TREASURY -e $NETWORK
icp canister snapshot create $SUBNET_0_1_TREASURY -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_TREASURY --wasm out/funnai_treasury_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the Treasury canister back up
icp canister start $SUBNET_0_1_TREASURY -e $NETWORK
```

# upgrade the ckSigner canister

The ckSigner canister requires a Schnorr key name in addition to the network.

Schnorr Key Names

| Schnorr Key Name | network                     | Signing Cost | Subnet used for signing    |
| ---------------- | --------------------------- | ------------ | -------------------------- |
| `key_1`          | IC mainnet (prd)            | ~26B cycles  | 34-node fiduciary subnet   |
| `test_key_1`     | IC mainnet (testing)        | ~10B cycles  | 13-node application subnet |
| `dfx_test_key`   | Local replica (`icp network start`) | Free         | Local test subnet          |

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

icp canister stop ck_signer_canister -e $NETWORK
icp canister snapshot create ck_signer_canister -e $NETWORK

# ---------------------------------------------
# To upgrade
icp canister install ck_signer_canister \
    --mode upgrade \
    -e $NETWORK \
    --wasm out/ck_signer_canister.wasm \
    --argument "(\"$SCHNORR_KEY_NAME\")" \
    --wasm-memory-persistence keep

# To reinstall
# When reinstalling, make sure the redo the steps of the section:
# "Configure fee tokens"
#
icp canister install ck_signer_canister \
    --mode reinstall \
    -e $NETWORK \
    --wasm out/ck_signer_canister.wasm \
    --argument "(\"$SCHNORR_KEY_NAME\")"

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# Start the canister back up
icp canister start ck_signer_canister -e $NETWORK
icp canister status ck_signer_canister -e $NETWORK | grep Status
icp canister call ck_signer_canister health

# Verify Treasury -> go to Configure Treasury section if wrong
icp canister call ck_signer_canister getTreasury

# Verify fee token configuration
icp canister call ck_signer_canister getFeeTokens

# If "Accepted tokens" is empty (e.g. after reinstall), add ckBTC:
#
# | Token | Ledger Canister ID          | Fee        |
# | ----- | --------------------------- | ---------- |
# | ckBTC | mxzaz-hqaaa-aaaar-qaada-cai | 100 (sats) |
#
icp canister call ck_signer_canister addFeeToken \
    '(record { tokenName = "ckBTC"; tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai"; fee = 100 : nat })'
icp canister call ck_signer_canister getFeeTokens
```

## Configure ckSigner treasury

The treasury is where all signing fees are sent. Default: funnAI Treasury Canister (prd).
After a reinstall, verify the treasury is correct. For testing, set it to the testing treasury.

```bash
echo "Using network: $NETWORK"

# Check current treasury
icp canister call ck_signer_canister getTreasury

# Set treasury (only needed if default is wrong, e.g. for testing network)
# icp canister call ck_signer_canister setTreasury  '(record { treasuryName = "<description>"; treasuryPrincipal = principal "<principal>" })'
```

## Configure ckSigner fee tokens

After upgrade, configure the accepted ICRC-2 fee tokens.

```bash
echo "Using network: $NETWORK"

# Check current fee token configuration
icp canister call ck_signer_canister getFeeTokens

## Fee Token Configuration
#
# | Token | Ledger Canister ID          | Fee        |
# | ----- | --------------------------- | ---------- |
# | ckBTC | mxzaz-hqaaa-aaaar-qaada-cai | 100 (sats) |

icp canister call ck_signer_canister addFeeToken \
    '(record { tokenName = "ckBTC"; tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai"; fee = 100 : nat })'

# Verify fee tokens are configured
icp canister call ck_signer_canister getFeeTokens

# Verify sign rejects without payment (should return "Fee payment required" error)
icp canister call ck_signer_canister sign \
    '(record { botName = "testbot"; message = blob "\00\01\02\03\04\05\06\07\08\09\0a\0b\0c\0d\0e\0f\10\11\12\13\14\15\16\17\18\19\1a\1b\1c\1d\1e\1f"; payment = null })'

# To remove a fee token (if needed):
# icp canister call ck_signer_canister removeFeeToken \
#     '(record { tokenLedger = principal "mxzaz-hqaaa-aaaar-qaada-cai" })'
```

# upgrade the mAInerCreator

```bash
# Verify correct network & canister settings !
echo $NETWORK
echo $SUBNET_0_1_MAINER_CREATOR

# from folder: PoAIW/src/mAInerCreator
# Generate the bindings for the upload scripts and the frontend
# (no `icp` equivalent to `dfx generate` -- src/declarations/ is committed)

# mops.toml was updated in latest PR
rm -rf .mops
mops install

# Build wasm with Docker (reproducible build)
make docker-build-base # Optional. Once built for one PoAIW canister, no rebuild needed for others.
make docker-build-wasm

icp canister stop $SUBNET_0_1_MAINER_CREATOR -e $NETWORK
icp canister snapshot create $SUBNET_0_1_MAINER_CREATOR -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install $SUBNET_0_1_MAINER_CREATOR --wasm out/mainer_creator_canister.wasm \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep -y

# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

# start the mAInerCreator canister back up
icp canister start $SUBNET_0_1_MAINER_CREATOR -e $NETWORK
icp canister status $SUBNET_0_1_MAINER_CREATOR -e $NETWORK     | grep Status
icp canister call   $SUBNET_0_1_MAINER_CREATOR health

# ensure the correct wasm & did files are in this folder 
# -> PoAIW/src/mAInerCreator/files
#
# If you just did a mAIner upgrade, you can do this:
# From folder: PoAIW/src/mAIner
shasum -a 256 PoAIW/src/mAIner/out/mainer_ctrlb_canister_0.wasm # confirm it is the TARGET_HASH
cp PoAIW/src/mAIner/out/mainer_ctrlb_canister_0.did ../mAInerCreator/files/mainer_ctrlb_canister.did
cp PoAIW/src/mAIner/out/mainer_ctrlb_canister_0.wasm ../mAInerCreator/files/mainer_ctrlb_canister.wasm
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
python -m scripts.upload_mainer_controller_canister -e $NETWORK --canister mainer_creator_canister --wasm files/mainer_ctrlb_canister.wasm --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator
#
# (if changed) Upload the mainer LLM canister wasm
shasum -a 256 files/llama_cpp.wasm # verify
python -m scripts.upload_mainer_llm_canister_wasm -e $NETWORK --canister mainer_creator_canister --wasm files/llama_cpp.wasm --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator

# (if changed) Upload the mainer LLM model file (gguf)
shasum -a 256 files/qwen2.5-0.5b-instruct-q8_0.gguf # verify
python -m scripts.upload_mainer_llm_canister_modelfile -e $NETWORK --canister mainer_creator_canister --chunksize 2000000 --wasm files/qwen2.5-0.5b-instruct-q8_0.gguf --hf-sha256 "ca59ca7f13d0e15a8cfa77bd17e65d24f6844b554a7b6c12e07a5f89ff76844e" --candid src/declarations/mainer_creator_canister/mainer_creator_canister.did
# -> Repeat for all networks, used to test mAInerCreator

# Verify the sha256 hashes of all uploaded files
# Warning: do not run this while upload is in process. Wait till it is fully completed.
#          It uses a lazy evaluation logic.
icp canister call mainer_creator_canister getSha256HashesAdmin
```

## Post-reinstall configuration (mAInerCreator)

`--mode reinstall` wipes the mAInerCreator's stable state. The wasm/model
uploads above re-populate the canister files, but `MASTER_CANISTER_ID`
resets to its hard-coded **prd** default (`r5m5y-diaaa-aaaaa-qanaa-cai`).
That default is wrong on every other network and **will silently break
mAIner marketplace purchases** — `addControllerToMainerCanister` checks
that the caller equals `MASTER_CANISTER_ID`, so calls from a non-prd
GameState are rejected as `#Unauthorized`. The buyer's ICP is refunded
and the user sees:

```
Purchase completion failed: {"GenericError":{"message":"Controller update failed, ICP refunded","error_code":2}}
```

Set the master canister id to the current network's GameState after every
reinstall (no-op on prd, since the default already matches):

```bash
# verify current value
icp canister call $SUBNET_0_1_MAINER_CREATOR getMasterCanisterIdAdmin

# set it to this network's GameState
icp canister call $SUBNET_0_1_MAINER_CREATOR setMasterCanisterId '("'$SUBNET_0_1_GAMESTATE'")'

# verify
icp canister call $SUBNET_0_1_MAINER_CREATOR getMasterCanisterIdAdmin
```

Regular `--mode upgrade` preserves stable state and does not need this step.

## Testing the mAInerCreator

Final test must be done by creating a mAIner via the UI, but initial test you can do from the command line.

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

# (no `icp` equivalent to `dfx generate` -- src/declarations/ is committed)
icp canister stop funnai_backend -e $NETWORK
icp canister snapshot create funnai_backend -e $NETWORK

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
# The wasm will be uploaded to the SNS and a deploy proposal will be created
# for the community to vote on. Once the proposal passes, the SNS automatically
# upgrades the canister.
icp canister install --wasm out/funnai_backend.wasm \
    --argument "( principal \"$(icp identity principal)\" )" \
    -e $NETWORK --mode upgrade --wasm-memory-persistence keep \
    funnai_backend


# Verify wasm hash
make docker-verify-wasm VERIFY_NETWORK=$NETWORK

icp canister start funnai_backend -e $NETWORK
```

# un-pause protocol
```bash
# From folder: funnAI

# Toggle it
icp canister call $SUBNET_0_1_GAMESTATE togglePauseProtocolFlagAdmin

# verify
icp canister call $SUBNET_0_1_GAMESTATE getPauseProtocolFlag
```

# start timers of protocol canisters

In this order:

```bash
# From folder: funnAI
icp canister call $SUBNET_0_1_JUDGE         startTimerExecutionAdmin
icp canister call $SUBNET_0_1_SHARE_SERVICE startTimerExecutionAdmin
icp canister call $SUBNET_0_1_CHALLENGER    startTimerExecutionAdmin

# If you changed the Challenger timer interval, note it is a stble var.
# You will need to call setTimerActionRegularityInSecondsAdmin, as in:
icp canister call $SUBNET_0_1_CHALLENGER setTimerActionRegularityInSecondsAdmin '(420)'
```

# Cycle capping: start the send-cycles drain timers

Each controller (Challenger, ShareService, Judge) has a recurring **send-cycles
timer** that drains excess cycles down to GameState via the existing fixed-chunk
`sendCyclesToGameStateCanister` logic. The timer is **transient (in-memory) and
does NOT survive an upgrade** — re-arm it after every controller upgrade.

```bash
# From folder: funnAI  (run after upgrading each controller)
icp canister call $SUBNET_0_1_CHALLENGER    startSendCyclesTimerAdmin
icp canister call $SUBNET_0_1_SHARE_SERVICE startSendCyclesTimerAdmin
icp canister call $SUBNET_0_1_JUDGE         startSendCyclesTimerAdmin

# Period defaults to 3600s (1 hour). To change (per controller):
# icp canister call $SUBNET_0_1_CHALLENGER setSendCyclesPeriodInSecondsAdmin '(3600)'
icp canister call $SUBNET_0_1_CHALLENGER    getSendCyclesPeriodInSecondsAdmin

# To stop a drain timer:
# icp canister call $SUBNET_0_1_CHALLENGER stopSendCyclesTimerAdmin
```

The drain keeps `MIN_CYCLES_BALANCE` (30T default) and sends the fixed
`CYCLES_AMOUNT_TO_GAME_STATE_CANISTER` (10T default) per tick when the balance
allows. Both are admin-tunable via the existing
`setMinCyclesBalanceAdmin` / `setCyclesToSendToGameStateAdmin` (now also on the
ShareService/mAIner canister).

## Cycle capping: verify the drain thresholds

The drain only fires when `balance >= CYCLES_AMOUNT_TO_GAME_STATE_CANISTER +
MIN_CYCLES_BALANCE` (send chunk + keep floor). The intended prd values are the
code defaults: **30T floor / 10T chunk** (drains when balance >= 40T). If they
are set higher than the controller's steady-state balance, the drain will never
fire and the log shows `#Ok({added = false; amount = 0})` on every tick.

Verify (all three controllers):

```bash
# From folder: funnAI  (prd)
icp canister call $SUBNET_0_1_CHALLENGER    getMinCyclesBalanceAdmin
icp canister call $SUBNET_0_1_CHALLENGER    getCyclesToSendToGameStateAdmin
icp canister call $SUBNET_0_1_SHARE_SERVICE getMinCyclesBalanceAdmin
icp canister call $SUBNET_0_1_SHARE_SERVICE getCyclesToSendToGameStateAdmin
icp canister call $SUBNET_0_1_JUDGE         getMinCyclesBalanceAdmin
icp canister call $SUBNET_0_1_JUDGE         getCyclesToSendToGameStateAdmin
```

Each `getMinCyclesBalanceAdmin` should return `30_000_000_000_000` and each
`getCyclesToSendToGameStateAdmin` should return `10_000_000_000_000`. Fix any
that differ:

```bash
icp canister call $SUBNET_0_1_CHALLENGER    setMinCyclesBalanceAdmin        '(30_000_000_000_000)'
icp canister call $SUBNET_0_1_CHALLENGER    setCyclesToSendToGameStateAdmin '(10_000_000_000_000)'
icp canister call $SUBNET_0_1_SHARE_SERVICE setMinCyclesBalanceAdmin        '(30_000_000_000_000)'
icp canister call $SUBNET_0_1_SHARE_SERVICE setCyclesToSendToGameStateAdmin '(10_000_000_000_000)'
icp canister call $SUBNET_0_1_JUDGE         setMinCyclesBalanceAdmin        '(30_000_000_000_000)'
icp canister call $SUBNET_0_1_JUDGE         setCyclesToSendToGameStateAdmin '(10_000_000_000_000)'
```

Note: `MIN_CYCLES_BALANCE` also sets the LLM funding cap (LLMs are topped up only
when below this threshold), so keep it at 30T for both purposes. These are stable
vars and survive upgrades — only re-check them if you suspect they were changed.

## LLM cycles cap

Each controller also skips funding its LLM when the LLM's cached cycle balance
(read via the v0.11.0 `get_cycle_balance` query) is above the **same
`MIN_CYCLES_BALANCE`** threshold — there is no separate LLM-cap endpoint.
Fail-open: if the balance can't be read, it funds anyway. Tune via
`setMinCyclesBalanceAdmin` (≥20T guard).

> **mAIner / ShareService note:** the LLM cap and the send-cycles drain are
> active **only on the `#ShareService` role**; `#Own`/`#ShareAgent` mAIners are
> unaffected. The ShareService admin endpoints are role-gated (`#AdminUpdate`),
> not controller-gated.

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
icp canister snapshot list $SUBNET_0_1_GAMESTATE -e $NETWORK
icp canister snapshot delete $SUBNET_0_1_GAMESTATE -e $NETWORK     <snapshot-id>

icp canister snapshot list $SUBNET_0_1_CHALLENGER -e $NETWORK    
icp canister snapshot delete $SUBNET_0_1_CHALLENGER -e $NETWORK    <snapshot-id>

icp canister snapshot list $SUBNET_0_1_SHARE_SERVICE -e $NETWORK 
icp canister snapshot delete $SUBNET_0_1_SHARE_SERVICE -e $NETWORK <snapshot-id>

icp canister snapshot list $SUBNET_0_1_JUDGE -e $NETWORK
icp canister snapshot delete $SUBNET_0_1_JUDGE -e $NETWORK         <snapshot-id>

icp canister snapshot list ck_signer_canister -e $NETWORK
icp canister snapshot delete ck_signer_canister -e $NETWORK <snapshot-id>
```

# Load a snapshot to ROLL BACK

Use the snapshots to roll back everything

```bash
# pause > stop timers > stop canisters , as described above

# list & load the snapshots
icp canister snapshot list $SUBNET_0_1_GAMESTATE -e $NETWORK
icp canister snapshot restore $SUBNET_0_1_GAMESTATE -e $NETWORK     <snapshot-id>

icp canister snapshot list $SUBNET_0_1_CHALLENGER -e $NETWORK    
icp canister snapshot restore $SUBNET_0_1_CHALLENGER -e $NETWORK    <snapshot-id>

icp canister snapshot list $SUBNET_0_1_SHARE_SERVICE -e $NETWORK 
icp canister snapshot restore $SUBNET_0_1_SHARE_SERVICE -e $NETWORK <snapshot-id>

icp canister snapshot list $SUBNET_0_1_JUDGE -e $NETWORK
icp canister snapshot restore $SUBNET_0_1_JUDGE -e $NETWORK         <snapshot-id>

icp canister stop ck_signer_canister -e $NETWORK
icp canister snapshot list ck_signer_canister -e $NETWORK
icp canister snapshot restore ck_signer_canister -e $NETWORK <snapshot-id>
icp canister start ck_signer_canister -e $NETWORK
icp canister call ck_signer_canister health

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

In these folders, the following files are used by icp-cli:
- icp.yaml : `llm_#`    -> used by `icp deploy`
- .icp/data/mappings/<env>.ids.json -> used & updated by `icp deploy`


## Deploy a new LLM

### Using script (recommended)

The `deploy_llm.sh` script automates the full deployment of a new LLM canister:
creates it on a subnet, uploads the model, configures controllers, admin roles,
log viewers, and tests the LLM.

```bash
# from folder: funnAI
# Activate the conda environment
conda activate funnAI

# Dry run first to see what will happen
scripts/deploy_llm.sh -e $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>] --dry-run

# Deploy for real
scripts/deploy_llm.sh -e $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>]
```

The script will:
1. Find the next available `llm_N` index in `canister_ids.json`
2. Ensure the entry exists in `icp.yaml`
3. Auto-select a subnet with < 3 LLMs (or use `--subnet` to override)
4. Deploy, health-check, verify subnet, configure controllers & admin roles
5. Upload and load the model, set max_tokens, pause logs/chats
6. Add log viewers, test the LLM
7. Update `canister_ids.json` and `canister_ids-{network}.env`

If deployment fails partway through, the script prints the canister ID and
a `delete_llm.sh` command to clean up.

**Next step: add the LLM to the protocol**
- See section below: "Add new LLM to the protocol"

### Manually using icp commands

- Select a new subnet, if needed, and record it in our tracking spreadsheet:
    https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0

- Add the subnet to `funnAI/scripts/canister_ids-prd.env`

- Add the llm_# entries to `PoAIW/llms/xxx/icp.yaml`

- Create the canister

    ```bash
        NETWORK=prd

        # Deploy it
        # from folder: PoAIW/llms/xxx
        icp deploy -e $NETWORK llm_<#> --subnet <subnet-id> --mode install

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
        icp canister settings update llm_<#> -e $NETWORK --add-controller $SUBNET_0_1_CHALLENGER

        # For ShareService LLM
        icp canister settings update llm_<#> -e $NETWORK --add-controller $SUBNET_0_1_SHARE_SERVICE

        # For Judge LLM
        icp canister settings update llm_<#> -e $NETWORK --add-controller $SUBNET_0_1_JUDGE

    ```

- Add Admin as controllers

    ```bash
        NETWORK=prd
        PATRICK="cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"
        MAINTAINER="$(icp identity principal)"
        icp canister settings update $llm -e $NETWORK --add-controller $PATRICK
        icp canister settings update $llm -e $NETWORK --add-controller $MAINTAINER
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
        python -m scripts.upload -e $NETWORK --canister $LLM --canister-filename models/model.gguf $MODEL
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
scripts/add_llm.sh -e $NETWORK --canister-id <canister-id> --dry-run

# Add for real
scripts/add_llm.sh -e $NETWORK --canister-id <canister-id>
```

The script will:
1. Show current LLMs registered in the controller
2. Call `add_llm_canister` on the controller
3. Verify the LLM count increased
4. Update GameState via `setCyclesFlowAdmin` (`numChallengerLlms` / `numJudgeLlms` / `numShareServiceLlms`)

**Manual step after add_llm.sh:**
- Register the canister with CycleOps (adds controller `2daxo-giaaa-aaaap-anvca-cai`)
- Record the new subnet (if new) in the tracking spreadsheet:
  https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0



### Manually using icp commands

#### For Challenger
```bash
    LLM="<canister-id>"
    # Add it to the Challenger ctrlb canister
    icp canister call $SUBNET_0_1_CHALLENGER    get_llm_canisters --output json
    icp canister call $SUBNET_0_1_CHALLENGER    add_llm_canister "(record {canister_id = \"$LLM\"})"
    icp canister call $SUBNET_0_1_CHALLENGER    get_llm_canisters --output json

    # update GameState cycle cost calculations
    icp canister call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numChallengerLlms
    NUM_LLMS_DEPLOYED=....
    icp canister call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numChallengerLlms = opt ($NUM_LLMS_DEPLOYED : nat);})"
```

#### For ShareService
```bash
    LLM="<canister-id>"
    # Add it to the ShareService ctrlb canister
    icp canister call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters --output json
    icp canister call $SUBNET_0_1_SHARE_SERVICE    add_llm_canister "(record {canister_id = \"$LLM\"})"
    icp canister call $SUBNET_0_1_SHARE_SERVICE    get_llm_canisters --output json

    # update GameState cycle cost calculations
    icp canister call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numShareServiceLlms
    NUM_LLMS_DEPLOYED=....
    icp canister call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numShareServiceLlms = opt ($NUM_LLMS_DEPLOYED : nat);})"
```

#### For Judge
```bash
    LLM="<canister-id>"
    # Add it to the Judge ctrlb canister
    icp canister call $SUBNET_0_1_JUDGE    add_llm_canister "(record {canister_id = \"$LLM\"})"
    icp canister call $SUBNET_0_1_JUDGE    get_llm_canisters --output json

    # update GameState cycle cost calculations
    icp canister call $SUBNET_0_1_GAMESTATE getCyclesFlowAdmin | grep numJudgeLlms
    NUM_LLMS_DEPLOYED=...
    icp canister call $SUBNET_0_1_GAMESTATE setCyclesFlowAdmin "(record {numJudgeLlms = opt ($NUM_LLMS_DEPLOYED : nat);})"
```

## Delete an LLM

### Using script (recommended)

The `delete_llm.sh` script removes an LLM from the protocol, deletes the canister
(returning cycles to the wallet), and cleans up `canister_ids.json` and the env file.

```bash
# from folder: funnAI

# Dry run first
scripts/delete_llm.sh -e $NETWORK --canister-id <canister-id> --dry-run

# Delete for real
scripts/delete_llm.sh -e $NETWORK --canister-id <canister-id>
```

The script will:
1. Check cycles balance
2. Remove the LLM from the controller canister
3. Wait 180 seconds for in-flight requests to complete
4. Delete the canister (cycles returned to wallet)
5. Remove entry from `canister_ids.json`
6. Remove entry from `canister_ids-{network}.env`

### Manually using icp commands

```bash
    NETWORK=prd
    source scripts/canister_ids-$NETWORK.env
    LLM="<canister-id>"

    # Remove from controller (pick the right one for your LLM type)
    # For Challenger
    icp canister call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # For ShareService
    icp canister call $SUBNET_0_1_SHARE_SERVICE remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # For Judge
    icp canister call $SUBNET_0_1_JUDGE         remove_llm_canister "(record {canister_id = \"$LLM\"})"

    # Wait for in-flight requests (180 seconds recommended)
    sleep 180

    # Delete the canister (cycles returned to wallet)
    icp canister delete $LLM -e $NETWORK

    # Manually clean up:
    # - Remove entry from canister_ids.json in the LLM directory
    # - Remove entry from funnAI/scripts/canister_ids-{network}.env
```


## Replace an LLM (delete + deploy + add)

To replace an existing LLM (e.g. moving it to a different subnet):

```bash
# 1. Delete the old LLM
scripts/delete_llm.sh -e $NETWORK --canister-id <old-canister-id>

# 2. Deploy a new LLM
scripts/deploy_llm.sh -e $NETWORK --llm-type <challenger|judge|share_service> [--subnet <subnet-id>]

# 3. Add the new LLM to the protocol
scripts/add_llm.sh -e $NETWORK --canister-id <new-canister-id>

# 4. Manual steps:
#    - Register new canister with CycleOps
```


## Upgrade an existing LLM

```bash
    # Takes the LLM offline, upgrades it, tests it, and puts it back online
    # Script will pause to ask for confirmation a couple of times
    scripts/upgrade_llms.sh -e $NETWORK [--canister-id <canister-id>]
```

# Cleaning LLMs (prompt cache files)

## Using a daily task

The cleaning of the LLMs is now done automatically on-chain by each LLM canister's
recurring prompt-cache cleanup timer (`cache_cleanup_start_timer`, armed after every upgrade).

## Manually, while the LLM is still online

This approach is deprecated.

```bash
    sscripts/cleanup_llm_promptcache_live.sh -e $NETWORK [--canister-id <canister-id>]
```

## Manually, while the LLM is offline

This approach is deprecated.

This script is used by `scripts/upgrade_llms.sh` which takes the LLM offline first:

```bash
    sscripts/cleanup_llm_promptcache.sh -e $NETWORK [--canister-id <canister-id>]
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
    icp canister logs $LLM -e $NETWORK --follow

    # Remove the LLM from the protocol
    # for Challenger
    icp canister call $SUBNET_0_1_CHALLENGER    remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for ShareService
    icp canister call $SUBNET_0_1_SHARE_SERVICE remove_llm_canister "(record {canister_id = \"$LLM\"})"
    # for Judge
    icp canister call $SUBNET_0_1_JUDGE         remove_llm_canister "(record {canister_id = \"$LLM\"})"

    # then upgrade
    # from folder: PoAIW/llms/xxx
    icp canister status $llm -e $NETWORK | grep "Memory Size"
    icp canister stop $llm -e $NETWORK
    icp canister snapshot create $llm -e $NETWORK
    icp deploy   -e $NETWORK $llm --mode upgrade
    icp canister start $llm -e $NETWORK

    # Cleanup the prompt cache files
    # from folder: funnAI
    scripts/cleanup_llm_promptcache.sh -e $NETWORK --canister-id $LLM

    # Configure the LLM
    # from folder: PoAIW/llms/xxx
    icp canister call $llm health
    icp canister call $llm load_model '(record { args = vec {"--model"; "models/model.gguf"} })'
    icp canister call $llm set_max_tokens '(record { max_tokens_query = 13 : nat64; max_tokens_update = 13 : nat64 })'
    icp canister call $llm get_max_tokens
    icp canister call $llm log_pause
    icp canister call $llm chats_pause

    # Test operations manually (Copy/Paste all commands at once...)
    icp canister call $llm new_chat '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache";
            "--cache-type-k"; "q8_0";
        }
        })'
    icp canister call $llm run_update '(record {
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
    icp canister call $llm recursive_dir_content_query  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json
    icp canister call $llm remove_prompt_cache '(record {
        args = vec {
            "--prompt-cache"; "prompt.cache"
        }
        })'
    icp canister call $llm recursive_dir_content_update  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json
    icp canister call $llm filesystem_remove '(record {filename = ".canister_cache/$MAINTAINER/sessions"})'
    icp canister call $llm filesystem_remove '(record {filename = ".canister_cache/$MAINTAINER"})'
    icp canister call $llm filesystem_remove '(record {filename = ".canister_cache"})'
    icp canister call $llm recursive_dir_content_query  '(record {dir = ".canister_cache"; max_entries = 0 : nat64})' --output json

    # Re-arm the in-memory timers (REQUIRED after every upgrade).
    # Both timers are in-memory only and are NOT auto-armed on upgrade.
    # (The upgrade_llms.sh / deploy_llm.sh scripts do this automatically.)
    # - cache_cleanup_start_timer : recurring prompt-cache cleanup
    # - cycle_balance_start_timer : recurring cycle-balance tracking
    #   (llama_cpp_canister >= v0.11.0). Without it, get_cycle_balance errors.
    icp canister call $llm cache_cleanup_start_timer
    icp canister call $llm cycle_balance_start_timer
```


# Delete snapshots

```bash
    # We have a script to delete ALL snapshots for either ALL protocol canisters or a specified canister-id
    scripts/delete_snapshots.sh -e $NETWORK --canister-types [all/protocol/mainers] [--canister-id <canister-id>] [--dry-run] [--workers N]

    # You can do it manually with:
    LLM="<canister-id>"
    # list & delete the snapshot
    icp canister snapshot list $LLM -e $NETWORK
    icp canister snapshot delete $LLM -e $NETWORK     <snapshot-id>
    # verify memory
    icp canister status $llm -e $NETWORK | grep "Memory Size"
```

# Upgrade the mAIners

> **Toolchain note (historical, 2026-06-29 — predates the icp-cli migration):** the LLMs and
> ShareAgent mAIners used **dfx 0.32.0** at that time (pinned via `DFX_VERSION='0.32.0'` in each `PoAIW/llms/<x>/.env`); this is the version for the llama_cpp_canister v0.11.0 LLM upgrade. (They were previously on dfx 0.31.0 as of the 2026-04-16 mAIner upgrade/reinstall.) All other canisters (frontend, backend, and PoAIW protocol canisters) are still on **dfx 0.29.2** (pinned in `PoAIW/src/GameState/docker/docker-compose.yml`). Keep this mismatch in mind when regenerating declarations or reproducing wasm hashes — newer dfx versions emit different JS codegen (e.g. importing from `@icp-sdk/core/agent` instead of `@dfinity/agent`), which can break the frontend build if regenerated wholesale.
>
> **EOP migration block in `PoAIW/src/mAIner/src/Main.mo` — on-chain-daily-metric PR.**
> ShareAgents and ShareService share the same source file, so the migration block applies to both, but their **deployed starting points differ**:
> - ShareService was last deployed pre-#143 → needs the full migration when it was upgraded for this PR (already done).
> - ShareAgents were already reinstalled post-#143 on 2026-04-16 → their deployed memory does **not** contain `officialCycleTopUpsStorage` or `generatedResponses`, and already contains the four `let` constants added in #143.
>
> Before rebuilding the wasm for the ShareAgent rollout of this PR:
> 1. **Remove the `in var officialCycleTopUpsStorage` and `in var generatedResponses` fields from the migration input** — they're not in ShareAgents' memory and declaring them would make EOP fail to construct the input record.
> 2. **Leave the `shareServiceCanisterActor` actor-type transform in place** — ShareAgents still have the old 1-arg `addChallengeToShareServiceQueue` signature stored, and the upgrade flips it to the 2-arg version.
> 3. **Leave the new-field outputs** (`shareAgentActivityStorageStable` plus, for safety, the four `let` constants) in place. The four `let` constants are already in ShareAgents' memory; producing them in the migration output rewrites them with the same value, which is a no-op.
>
> Once **both** the ShareService and every ShareAgent on every network is on a post-this-PR build, delete the entire migration block from `Main.mo`. It's idempotent — leaving it in works but it's dead weight on subsequent upgrades.

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
scripts/upgrade_mainers.sh -e [local|ic|testing|development|prd] [--target-hash HASH] [--num NUM] [--mainer CANISTER_ID] [--user PRINCIPAL] [--dry-run] [--skip-preparation] [--ask-before-upgrade] [--reverse] [--deploy-with-yes] [--reinstall]

Options:
  -e NETWORK       Required. Network to upgrade mainers on
  --target-hash HASH      Optional. Target wasm hash to upgrade to (from 'icp canister status <canister_id>')
  --num NUM               Optional. Number of mAIners to upgrade
  --mainer CANISTER_ID    Optional. Specific mAIner canister to upgrade
  --user PRINCIPAL        Optional. Principal ID of user whose mAIners to upgrade
  --dry-run               Optional. Run in dry-run mode without making changes
  --skip-preparation      Optional. Skip Step 1 preparation
  --ask-before-upgrade    Optional. Ask for confirmation before upgrading each canister
  --reverse               Optional. Process mainers in reverse order
  --deploy-with-yes       Optional. Will use: icp deploy ... --yes
  --reinstall             Optional. Reinstall (`--mode reinstall`) instead of upgrade. WIPES all stable
                          state on each canister. Use after capping unbounded stable lists to reset
                          accumulated memory back to baseline. Mutually exclusive with `--target-hash`.

# Reinstall ONE mAIner first to verify, then roll out in batches:
scripts/upgrade_mainers.sh -e $NETWORK --reinstall --mainer $MAINER --dry-run
scripts/upgrade_mainers.sh -e $NETWORK --reinstall --mainer $MAINER
scripts/upgrade_mainers.sh -e $NETWORK --reinstall --num 10
# (Top-up of low-balance canisters happens automatically before each (re)install.)

# from the folder: funnAI
conda activate funnAI

# Option 1: Upgrade a specific mAIner of IConfucius
# -> eg: nkftb-zqaaa-aaaaa-qbbxa-cai is running at VeryHigh
MAINER=nkftb-zqaaa-aaaaa-qbbxa-cai
scripts/upgrade_mainers.sh -e $NETWORK --mainer $MAINER --ask-before-upgrade [--dry-run]
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
scripts/upgrade_mainers.sh -e $NETWORK --user $USER --target-hash $TARGET_HASH --num 1 --ask-before-upgrade [--dry-run]

# Upgrade 2 more mAIners of IConfucius on production network, without confirmation prompt:
scripts/upgrade_mainers.sh -e $NETWORK --user $USER --target-hash $TARGET_HASH --num 2 [--dry-run]

# Upgrade ALL mAIners of IConfucius on production network without confirmation prompt:
scripts/upgrade_mainers.sh -e $NETWORK --user $USER --target-hash $TARGET_HASH [--dry-run]

# Upgrade 1 other mAIner on production network, with confirmation prompt:
scripts/upgrade_mainers.sh -e $NETWORK --num 1 --target-hash $TARGET_HASH [--dry-run]

# Upgrade 100 mainers on production network with target hash and without confirmation prompt:
scripts/upgrade_mainers.sh -e $NETWORK --num 100 --target-hash $TARGET_HASH [--dry-run]

# Upgrade ALL mainers on production network with target hash and without confirmation prompt:
scripts/upgrade_mainers.sh -e $NETWORK --target-hash $TARGET_HASH [--dry-run]
```

### Update Admin RBAC for mAIners

#### Using script

```bash
# To assign permissions (run for each maintainer principal)
scripts/update_admin_rbac_mainers.sh -e $NETWORK --principal $MAINTAINER [--action assign] [--dry-run]
scripts/update_admin_rbac_mainers.sh -e $NETWORK --principal $PATRICK [--action assign] [--dry-run]

# To revoke permissions
scripts/update_admin_rbac_mainers.sh -e $NETWORK --principal $MAINTAINER --action revoke [--dry-run]
```

#### Manual

```bash
MAINER=...
# verify which principals already have admin roles
icp canister call $MAINER getAdminRoles
# grant #AdminUpdate to the maintainer principals (arjaan, patrick)
icp canister call $MAINER assignAdminRole '( record { "principal" = "'$MAINTAINER'"; role = variant { AdminUpdate }; note = "Maintainer: arjaan" } )'
icp canister call $MAINER assignAdminRole '( record { "principal" = "'$PATRICK'"; role = variant { AdminUpdate }; note = "Maintainer: patrick" } )'
# if needed, this is how you revoke permissions for a principal
# icp canister call $MAINER revokeAdminRole '( "'$MAINTAINER'")'
```

### Verify mAIners Health & Hash

After upgrade is completed, verify every mAIner is healthy and has correct module hash:

```bash
TARGET_HASH=0x...
scripts/get_mainers_health.sh -e $NETWORK --target-hash $TARGET_HASH
```

### Delete mAIners snapshots

Delete snapshot of all the mAIners:

```bash
scripts/delete_snapshots.sh -e $NETWORK --canister-types mainers [--dry-run]
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
icp canister logs $MAINER -e $NETWORK --follow

# monitor the mAInerCreator
icp canister logs $SUBNET_0_1_MAINER_CREATOR -e $NETWORK --follow

# stop the mAIner > snapshot it > start it > upgrade
# mAIner must be running during upgrade for the configuration steps
icp canister stop $MAINER -e $NETWORK
icp canister snapshot create $MAINER -e $NETWORK
icp canister start $MAINER -e $NETWORK
icp canister call game_state_canister upgradeMainerControllerAdmin "(record {canisterAddress = \"$MAINER\" })"

# verify everything looks good (timer should have been restarted)
icp canister logs $MAINER -e $NETWORK

# if it does not look good, restore the snapshot
icp canister snapshot list $MAINER -e $NETWORK
icp canister snapshot restore $MAINER -e $NETWORK <snapshot-id>

# if all good, delete the snapshot
icp canister snapshot list $MAINER -e $NETWORK
icp canister snapshot delete $MAINER -e $NETWORK <snapshot-id>
```

# Troubleshooting

## Judge calls to GameState fail with #Err(Unauthorized)

This happens if you reinstall the judge in the `testing` network.
The default GAME_STATE_CANISTER_ID is for the `prd` network. 

Verify the log file, what canister id is used.

If wrong, set it to the correct value with:

```bash
icp canister call $SUBNET_0_1_JUDGE setGameStateCanisterId "(\"$SUBNET_0_1_GAMESTATE\")"
```