# funnAI - settings in the prd network

This document summarized the settings & how to update them in the prd network

# Setup a development environment
First step is to follow the instructions of the README.md to set up a development environment.

# Controller Access
You must be a controller to be able to call the Admin endpoints of the canisters.

Follow instructions of funnAI/README-prd-upgrade-PoAIW.md

# FUNNAI reward per challenge

```bash
# From folder: funnAI
NETWORK=prd

dfx canister call game_state_canister getRewardPerChallengeAdmin --network $NETWORK

dfx canister call game_state_canister setRewardPerChallengeAdmin '100000000000' --network $NETWORK
```

# GameState Thresholds

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

# The CyclesFlow variables (Fees & Costs)

todo

# mAIner burn rates

Get & set the values with the GameState canister:

```bash
    # from folder: funnAI
    dfx canister --network $NETWORK call game_state_canister getCyclesBurnRate '( variant {Low} )'
    dfx canister --network $NETWORK call game_state_canister getCyclesBurnRate '( variant {Mid} )'
    dfx canister --network $NETWORK call game_state_canister getCyclesBurnRate '( variant {High} )'
    dfx canister --network $NETWORK call game_state_canister getCyclesBurnRate '( variant {VeryHigh} )'

    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {Low}     ; cyclesBurnRate = record { cycles = 1_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {Mid}     ; cyclesBurnRate = record { cycles = 2_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {High}    ; cyclesBurnRate = record { cycles = 3_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {VeryHigh}; cyclesBurnRate = record { cycles = 6_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
```

To test it out on a mAIner, do the following:

```bash
    # Update the AgentSettings: Low, Mid, High, VeryHigh
    dfx canister --network $NETWORK call <canister-id> updateAgentSettings '(record {cyclesBurnRate = variant {Mid}; })'

    # Check the new timer settings
    dfx canister --network $NETWORK call <canister-id> getTimerActionRegularityInSecondsAdmin 

```

# Challenger, Judge & ShareService timer delays

```bash
# From folder: funnAI
source scripts/canister_ids-prd.env

# Note: These calls will also (re-)start the timers
dfx canister --network $NETWORK call $SUBNET_0_CHALLENGER    setTimerActionRegularityInSecondsAdmin  '( 5 : nat)' 
dfx canister --network $NETWORK call $SUBNET_0_JUDGE         setTimerActionRegularityInSecondsAdmin  '( 5 : nat)'
dfx canister --network $NETWORK call $SUBNET_0_SHARE_SERVICE setTimerAction2RegularityInSecondsAdmin '( 5 : nat)'

# Get the timer regularity 
dfx canister --network $NETWORK call $SUBNET_0_CHALLENGER    getTimerActionRegularityInSecondsAdmin
dfx canister --network $NETWORK call $SUBNET_0_JUDGE         getTimerActionRegularityInSecondsAdmin
dfx canister --network $NETWORK call $SUBNET_0_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin

# Stopping the timers
dfx canister --network $NETWORK call $SUBNET_0_CHALLENGER    stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_JUDGE         stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_SHARE_SERVICE stopTimerExecutionAdmin

# (Re-)Starting the timers
dfx canister --network $NETWORK call $SUBNET_0_CHALLENGER    startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_JUDGE         startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_SHARE_SERVICE startTimerExecutionAdmin
```

# Max Number of open Challenges

todo

# Max Number of unscored resposes

todo



# Max number of mAIners

todo



