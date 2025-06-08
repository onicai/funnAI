#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/deploy-mainers-Own-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ] || [ "$1" = "development" ] || [ "$1" = "demo" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic' or 'testing' or 'development' or 'demo'."
                exit 1
            fi
            shift
            ;;
        --mode)
            shift
            if [ "$1" = "install" ] || [ "$1" = "reinstall" ] || [ "$1" = "upgrade" ]; then
                DEPLOY_MODE=$1
            else
                echo "Invalid mode: $1. Use 'install', 'reinstall' or 'upgrade'."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

if [ "$DEPLOY_MODE" != "install" ]; then
    echo " "
    echo "$DEPLOY_MODEl of Own mAIner is not supported."
    exit 1
fi

CANISTER_ID_GAME_STATE_CANISTER=$(dfx canister --network $NETWORK_TYPE id game_state_canister)
cd PoAIW/src/mAInerCreator
CANISTER_ID_MAINER_CREATOR_CANISTER=$(dfx canister --network $NETWORK_TYPE id mainer_creator_canister)

# go back to the funnAI folder
cd ../../../

# ================================================================
# some helper functions
extract_record_from_variant() {
    local variant_string="$1"
    python -c "
import re
s = '''$variant_string'''
match = re.search(r'Ok\s*=\s*(record\s*\{)', s)
if match:
    start = match.start(1)
    brace_level = 0
    for i, c in enumerate(s[start:], start=start):
        if c == '{':
            brace_level += 1
        elif c == '}':
            brace_level -= 1
            if brace_level == 0:
                print(s[start:i+1])
                break
"
}

#––– normalize whitespace: collapse runs → 1 space, trim ends –––
normalize() {
  sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//'
}

#––– extract the full “status = variant { … }” block on one line –––
# Usage: echo "$RECORD" | extract_status_block
extract_status_block() {
  sed -n '/status = variant/,/};/p' \
    | sed 's/status = //; s/};/}/' \
    | tr '\n' ' ' \
    | normalize
}

#––– extract just the top‑level key (e.g. LlmSetupInProgress) –––
# Usage: echo "$BLOCK" | extract_status_name
extract_status_name() {
  sed -E 's/variant[[:space:]]*\{[[:space:]]*([^[:space:]]+).*/\1/' \
    | normalize
}
# ================================================================

#######################################################################
if [ "$NETWORK_TYPE" = "local" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Controller+LLM creation - Adding 10 TCycles to the game_state_canister canister on local"
    dfx ledger fabricate-cycles --canister game_state_canister --t 10
else
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Controller+LLM creation - Adding 10 TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER 10000000000000
fi

# ================================================================
# Type: #Own

echo " "
echo "--------------------------------------------------"
echo "Deploying a mAInerController canister of type #Own"

########################################################
GAME_STATE_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{print $2}')
GAME_STATE_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_0_T=$(echo "scale=4; $GAME_STATE_BALANCE_0 / 1000000000000" | bc)

MAINER_CREATOR_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_CREATOR_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_CREATOR_BALANCE_0_T=$(echo "scale=4; $MAINER_CREATOR_BALANCE_0 / 1000000000000" | bc)

echo " "
echo "Before createUserMainerAgent:"
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_0_T TCycles ($GAME_STATE_BALANCE_0_)"

echo " "
echo "MainerCreator ($CANISTER_ID_MAINER_CREATOR_CANISTER) "
echo "-> Balance: $MAINER_CREATOR_BALANCE_0_T TCycles ($MAINER_CREATOR_BALANCE_0_)"
########################################################

echo " "
echo "--------------------------------------------------"
echo "Clearing any previous RedeemedTransactionBlockAdmin for paymentTransactionBlockId 12"
dfx canister call game_state_canister removeRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' --network $NETWORK_TYPE

echo " "
echo "--------------------------------------------------"
echo " "
echo "Calling createUserMainerAgent"
# Note:
# (-) arguments subnetCtrl and subnetLlm are dummy values & not used by createUserMainerAgent.
#     The actual values are already set in the game_state_canister via setSubnetsAdmin
# (-) argument cyclesForMainer is a dummy value & not used by this call to createUserMainerAgent.
output=$(dfx canister call game_state_canister createUserMainerAgent '(record { paymentTransactionBlockId = 12; mainerConfig = record { mainerAgentCanisterType = variant {Own}; selectedLLM = opt variant {Qwen2_5_500M}; subnetCtrl = ""; subnetLlm = ""; cyclesForMainer = 0; }; })' --network $NETWORK_TYPE)
if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo "Call to createUserMainerAgent failed. Exiting."    
    exit 1
else
    RESULT_1=$(extract_record_from_variant "$output")
    echo "RESULT_1 (createUserMainerAgent): $RESULT_1"
fi

echo " "
echo "Calling spinUpMainerControllerCanister"
output=$(dfx canister call game_state_canister spinUpMainerControllerCanister "$RESULT_1" --network $NETWORK_TYPE)
if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo "Call to spinUpMainerControllerCanisterfailed. Exiting."    
    exit 1
else
    RESULT_2=$(extract_record_from_variant "$output")
    echo "RESULT_2 (spinUpMainerControllerCanister): $RESULT_2"

    CANISTER_ID_OWN_CONTROLLER=$(echo "$RESULT_2" | grep -o 'address = "[^"]*"' | sed 's/address = "//;s/"//')
    echo "CANISTER_ID_OWN_CONTROLLER: $CANISTER_ID_OWN_CONTROLLER"

    SUBNET_OWN=$(echo "$RESULT_2" | grep -o 'subnet = "[^"]*"' | sed 's/subnet = "//; s/"//')
    echo "SUBNET_SHARE_AGENT: $SUBNET_OWN"
fi

##############################################################
GAME_STATE_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
GAME_STATE_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_1_T=$(echo "scale=4; $GAME_STATE_BALANCE_1 / 1000000000000" | bc)
GAME_STATE_CYCLES_CHANGE_1=$(echo "$GAME_STATE_BALANCE_1 - $GAME_STATE_BALANCE_0" | bc)
GAME_STATE_CYCLES_CHANGE_1_T=$(echo "scale=4; $GAME_STATE_CYCLES_CHANGE_1 / 1000000000000" | bc)

MAINER_CREATOR_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_CREATOR_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_CREATOR_BALANCE_1_T=$(echo "scale=4; $MAINER_CREATOR_BALANCE_1 / 1000000000000" | bc)
MAINER_CREATOR_CYCLES_CHANGE_1=$(echo "$MAINER_CREATOR_BALANCE_1 - $MAINER_CREATOR_BALANCE_0" | bc)
MAINER_CREATOR_CYCLES_CHANGE_1_T=$(echo "scale=4; $MAINER_CREATOR_CYCLES_CHANGE_1 / 1000000000000" | bc)

OWN_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:"| awk '{print $2}')
OWN_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
OWN_BALANCE_1_T=$(echo "scale=4; $OWN_BALANCE_1 / 1000000000000" | bc)

# COST_TO_SPINUP_OWN_CONTROLLER=$(echo "- $GAME_STATE_CYCLES_CHANGE_1 - $MAINER_CREATOR_CYCLES_CHANGE_1 - $OWN_BALANCE_1" | bc)
# COST_TO_SPINUP_OWN_CONTROLLER_T=$(echo "scale=4; $COST_TO_SPINUP_OWN_CONTROLLER / 1000000000000" | bc)

echo " "
echo "--------------------------------------------------"

echo "After spinUpMainerControllerCanister: "
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_1_T TCycles ($GAME_STATE_BALANCE_1_)"
echo "-> Change : $GAME_STATE_CYCLES_CHANGE_1_T TCycles ($GAME_STATE_CYCLES_CHANGE_1)"

echo " "
echo "MainerCreator ($CANISTER_ID_MAINER_CREATOR_CANISTER) "
echo "-> Balance: $MAINER_CREATOR_BALANCE_1_T TCycles ($MAINER_CREATOR_BALANCE_1_)"
echo "-> Change : $MAINER_CREATOR_CYCLES_CHANGE_1_T TCycles ($MAINER_CREATOR_CYCLES_CHANGE_1)"

echo " "
echo "Own           ($CANISTER_ID_OWN_CONTROLLER) "
echo "-> Balance: $OWN_BALANCE_1_T TCycles ($OWN_BALANCE_1_)"

# echo " "
# echo "Cost to spinup Own controller: $COST_TO_SPINUP_OWN_CONTROLLER_T TCycles ($COST_TO_SPINUP_OWN_CONTROLLER)"
##############################################################

echo " "
echo "Calling setUpMainerLlmCanister"
output=$(dfx canister call game_state_canister setUpMainerLlmCanister "$RESULT_2" --network $NETWORK_TYPE)
echo $output
if [[ "$output" != *"Ok = record"* ]]; then
    echo "Call to setUpMainerLlmCanister.. Exiting."    
    exit 1
else
    RESULT_3=$(extract_record_from_variant "$output")
    echo "RESULT_3 (setUpMainerLlmCanister): $RESULT_3"
    echo " "
    CANISTER_ID_OWN_LLM=$(echo "$RESULT_3" | grep -o 'llmCanisterId = "[^"]*"' | sed 's/llmCanisterId = "//;s/"//')
    echo "CANISTER_ID_OWN_LLM: $CANISTER_ID_OWN_LLM"

    echo "Going into a loop to wait for the LLM setup to finish."
    CANISTER_STATUS_BLOCK=$(printf '%s\n' "$RESULT_3" | extract_status_block)
    CANISTER_STATUS=$(printf '%s\n' "$CANISTER_STATUS_BLOCK" | extract_status_name)
    echo "CANISTER_STATUS: $CANISTER_STATUS"
    WAIT_TIME=30
    while [[ "$CANISTER_STATUS" == "LlmSetupInProgress" ]]; do
        echo "sleep for $WAIT_TIME seconds..."
        sleep $WAIT_TIME
        output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_OWN_CONTROLLER\";})" --network $NETWORK_TYPE)
        RESULT_3A=$(extract_record_from_variant "$output")
        CANISTER_STATUS_BLOCK=$(printf '%s\n' "$RESULT_3A" | extract_status_block)
        CANISTER_STATUS=$(printf '%s\n' "$CANISTER_STATUS_BLOCK" | extract_status_name)
        echo "CANISTER_STATUS_BLOCK: $CANISTER_STATUS_BLOCK"
        # echo "CANISTER_STATUS:       $CANISTER_STATUS"
    done
fi

echo "RESULT_3A (getMainerAgentCanisterInfo): $RESULT_3A"

##############################################################
GAME_STATE_BALANCE_2_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
GAME_STATE_BALANCE_2=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_2_T=$(echo "scale=4; $GAME_STATE_BALANCE_2 / 1000000000000" | bc)
GAME_STATE_CYCLES_CHANGE_2=$(echo "$GAME_STATE_BALANCE_2 - $GAME_STATE_BALANCE_1" | bc)
GAME_STATE_CYCLES_CHANGE_2_T=$(echo "scale=4; $GAME_STATE_CYCLES_CHANGE_2 / 1000000000000" | bc)

MAINER_CREATOR_BALANCE_2_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_CREATOR_BALANCE_2=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_MAINER_CREATOR_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_CREATOR_BALANCE_2_T=$(echo "scale=4; $MAINER_CREATOR_BALANCE_2 / 1000000000000" | bc)
MAINER_CREATOR_CYCLES_CHANGE_2=$(echo "$MAINER_CREATOR_BALANCE_2 - $MAINER_CREATOR_BALANCE_1" | bc)
MAINER_CREATOR_CYCLES_CHANGE_2_T=$(echo "scale=4; $MAINER_CREATOR_CYCLES_CHANGE_2 / 1000000000000" | bc)

OWN_LLM_BALANCE_2_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:"| awk '{print $2}')
OWN_LLM_BALANCE_2=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
OWN_LLM_BALANCE_2_T=$(echo "scale=4; $OWN_LLM_BALANCE_2 / 1000000000000" | bc)

# COST_TO_SPINUP_OWN_LLM=$(echo "- $GAME_STATE_CYCLES_CHANGE_2 - $MAINER_CREATOR_CYCLES_CHANGE_2 - $OWN_LLM_BALANCE_2" | bc)
# COST_TO_SPINUP_OWN_LLM_T=$(echo "scale=4; $COST_TO_SPINUP_OWN_LLM / 1000000000000" | bc)

echo " "
echo "--------------------------------------------------"

echo "After setUpMainerLlmCanister: "
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_2_T TCycles ($GAME_STATE_BALANCE_2_)"
echo "-> Change : $GAME_STATE_CYCLES_CHANGE_2_T TCycles ($GAME_STATE_CYCLES_CHANGE_2)"

echo " "
echo "MainerCreator ($CANISTER_ID_MAINER_CREATOR_CANISTER) "
echo "-> Balance: $MAINER_CREATOR_BALANCE_2_T TCycles ($MAINER_CREATOR_BALANCE_2_)"
echo "-> Change : $MAINER_CREATOR_CYCLES_CHANGE_2_T TCycles ($MAINER_CREATOR_CYCLES_CHANGE_2)"

echo " "
echo "Own LLM       ($CANISTER_ID_OWN_LLM) "
echo "-> Balance: $OWN_LLM_BALANCE_2_T TCycles ($OWN_LLM_BALANCE_2_)"

# echo " "
# echo "Cost to spinup Own LLM: $COST_TO_SPINUP_OWN_LLM_T TCycles ($COST_TO_SPINUP_OWN_LLM)"
##############################################################

echo " "
echo "========================================================================"
echo "To add another LLM to the Own Controller $CANISTER_ID_OWN_CONTROLLER:"
echo " "
echo "(-) First add 5 TCycles to the GameState canister:"
echo "dfx wallet send  $CANISTER_ID_GAME_STATE_CANISTER 10000000000000 --network $NETWORK_TYPE "
echo "(-) Then add the LLM to the Own Controller by calling the GameState:"
echo "dfx canister call $CANISTER_ID_GAME_STATE_CANISTER addLlmCanisterToMainer  '$RESULT_2' --network $NETWORK_TYPE"
echo " "
echo "========================================================================"
echo "The timers are running! To stop timers for Own $CANISTER_ID_OWN_CONTROLLER, call the Own controller:"
echo " "
echo "dfx canister call $CANISTER_ID_OWN_CONTROLLER stopTimerExecutionAdmin --network $NETWORK_TYPE"
echo " "
echo "========================================================================"
