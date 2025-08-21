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

# GameState Settings for subnets

Compare to subnet allocations in this spreadsheet:
https://docs.google.com/spreadsheets/d/1KeyylEYVs3cQvYXOc9RS0q5eWd_vWIW1UVycfDEIkBk/edit?gid=0#gid=0

```bash
# From folder: funnAI
NETWORK=prd
# Verify the subnets are set correctly
dfx canister --network $NETWORK call game_state_canister getSubnetsAdmin

# Set them if not correct
source scripts/canister_ids-$NETWORK.env
SUBNETSACTRL=$SUBNET_0_1
SUBNETSSCTRL=$SUBNET_0_1
SUBNETSSLLM=$SUBNET_2_1
# Set the SubnetIds in the GameState canister
dfx canister --network $NETWORK call game_state_canister setSubnetsAdmin "(record {subnetShareAgentCtrl = \"$SUBNETSACTRL\"; subnetShareServiceCtrl = \"$SUBNETSSCTRL\"; subnetShareServiceLlm = \"$SUBNETSSLLM\" })"

```

# GameState Thresholds

```bash
# From folder: funnAI
NETWORK=prd

dfx canister call game_state_canister getGameStateThresholdsAdmin --output json --network $NETWORK 

dfx canister call game_state_canister setGameStateThresholdsAdmin '( record {
        thresholdArchiveClosedChallenges = 140 : nat;
        thresholdMaxOpenChallenges= 5 : nat;
        thresholdMaxOpenSubmissions = 140 : nat;
        thresholdScoredResponsesPerChallenge = 27 : nat;
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
    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {High}    ; cyclesBurnRate = record { cycles = 4_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
    dfx canister --network $NETWORK call game_state_canister setCyclesBurnRateAdmin '( record {cyclesBurnRateDefault = variant {VeryHigh}; cyclesBurnRate = record { cycles = 6_000_000_000_000 : nat; timeInterval = variant { Daily }; } } )'
```

To test it out on a mAIner, do the following:

```bash
    # Update the AgentSettings: Low, Mid, High, VeryHigh
    dfx canister --network $NETWORK call <canister-id> updateAgentSettings '(record {cyclesBurnRate = variant {Mid}; })'

    # Check the new timer settings
    dfx canister --network $NETWORK call <canister-id> getTimerActionRegularityInSecondsAdmin 
```

The game state setting that impacts the actual timing: `cyclesUsedPerResponse 394_591_568_000`

With this, the timers end up as:

- Low      -> 1 TCycles / day -> 43_200 seconds = Every  12 hours ==>  2 *0.4=0.8 TCycles / day
- Mid      -> 2 TCycles / day -> 17_280 seconds = Every 4.8 hours ==>  5 *0.4=2.0 TCycles / day
- High     -> 4 TCycles / day ->  8_640 seconds = Every 2.5 hours ==> 9.6*0.4=3.8 TCycles / day
- VeryHigh -> 6 TCycles / day ->  5_760 seconds = Every 1.6 hours ==> 15 *0.4=6.0 TCycles / day


# Challenger, Judge & ShareService timer delays

```bash
# From folder: funnAI
source scripts/canister_ids-prd.env

# Note: These calls will also (re-)start the timers
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    setTimerActionRegularityInSecondsAdmin  '( 300 : nat)' 
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         setTimerActionRegularityInSecondsAdmin  '( 5 : nat)'
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE setTimerAction2RegularityInSecondsAdmin '( 5 : nat)'

# Get the timer regularity 
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    getTimerActionRegularityInSecondsAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         getTimerActionRegularityInSecondsAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE getTimerActionRegularityInSecondsAdmin

# Stopping the timers
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         stopTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE stopTimerExecutionAdmin

# (Re-)Starting the timers
dfx canister --network $NETWORK call $SUBNET_0_1_CHALLENGER    startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_JUDGE         startTimerExecutionAdmin
dfx canister --network $NETWORK call $SUBNET_0_1_SHARE_SERVICE startTimerExecutionAdmin
```

# Max Number of unscored resposes

todo


# Max number of mAIners & Whitelisting

todo - finish these...

```bash
dfx canister --network $NETWORK call game_state_canister getPauseProtocolFlag
dfx canister --network $NETWORK call game_state_canister getPauseWhitelistMainerCreationFlag

dfx canister --network $NETWORK call game_state_canister togglePauseProtocolFlagAdmin
dfx canister --network $NETWORK call game_state_canister togglePauseWhitelistMainerCreationFlagAdmin

dfx canister --network $NETWORK call game_state_canister setLimitForCreatingMainerAdmin ...Types.MainerLimitInput...
```



