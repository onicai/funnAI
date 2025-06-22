# funnAI - settings in the prd network

This document summarized the settings & how to update them in the prd network

# Setup a development environment
First step is to follow the instructions of the README.md to set up a development environment.

# Controller Access
You must be a controller to be able to call the Admin endpoints of the canisters.

Follow instructions of funnAI/README-prd-upgrade-PoAIW.md

# FUNNAI reward per challenge:

```bash
# From folder: funnAI
NETWORK=prd

dfx canister call game_state_canister getRewardPerChallengeAdmin --network $NETWORK

dfx canister call game_state_canister setRewardPerChallengeAdmin '100000000000' --network $NETWORK
```

# The GameState Thresholds

```bash
# From folder: funnAI
NETWORK=prd

dfx canister call game_state_canister getGameStateThresholdsAdmin --output json --network $NETWORK 

dfx canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 150 : nat;
        thresholdMaxOpenChallenges= 6 : nat;
        thresholdMaxOpenSubmissions = 70 : nat;
        thresholdScoredResponsesPerChallenge = 10 : nat;
    }
)' --network $NETWORK
```

# Challenger, Judge & ShareService timer delays

```bash
# From folder: funnAI
source scripts/canister_ids-prd.env

# Note: These calls will also (re-)start the timers
dfx canister call $SUBNET_0_CHALLENGER    setTimerActionRegularityInSecondsAdmin  '( 5 : nat)' --network $NETWORK
dfx canister call $SUBNET_0_JUDGE         setTimerActionRegularityInSecondsAdmin  '( 5 : nat)' --network $NETWORK
dfx canister call $SUBNET_0_SHARE_SERVICE setTimerAction2RegularityInSecondsAdmin '( 5 : nat)' --network $NETWORK

# Get the timer regularity 
dfx canister call $SUBNET_0_CHALLENGER    getTimerActionRegularityInSecondsAdmin --network $NETWORK 
dfx canister call $SUBNET_0_JUDGE         getTimerActionRegularityInSecondsAdmin --network $NETWORK 
dfx canister call $SUBNET_0_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin --network $NETWORK 

# Stopping the timers
dfx canister call $SUBNET_0_CHALLENGER    stopTimerExecutionAdmin --network $NETWORK
dfx canister call $SUBNET_0_JUDGE         stopTimerExecutionAdmin --network $NETWORK
dfx canister call $SUBNET_0_SHARE_SERVICE stopTimerExecutionAdmin --network $NETWORK

# (Re-)Starting the timers
dfx canister call $SUBNET_0_CHALLENGER    startTimerExecutionAdmin --network $NETWORK
dfx canister call $SUBNET_0_JUDGE         startTimerExecutionAdmin --network $NETWORK
dfx canister call $SUBNET_0_SHARE_SERVICE startTimerExecutionAdmin --network $NETWORK
```

# Max Number of open Challenges

todo

# Judge timer

todo

# Max Number of unscored resposes

todo

# mAIner burn rates

todo

# Max number of mAIners

todo

# The CyclesFlow variables

todo

