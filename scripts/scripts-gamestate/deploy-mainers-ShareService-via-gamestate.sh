#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/deploy-mainers-ShareService-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic' or 'testing."
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
    echo "To fund Controller+LLM creation - Adding 5 TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER 10000000000000
fi

# ================================================================
# Type: #ShareService

echo " "
echo "--------------------------------------------------"
echo "Deploying a mAInerController canister of type #ShareService"

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
echo "Calling createUserMainerAgent"
output=$(dfx canister call game_state_canister createUserMainerAgent '(record { paymentTransactionBlockId = 0; mainerConfig = record { mainerAgentCanisterType = variant {ShareService}; selectedLLM = opt variant {Qwen2_5_500M}; }; })' --network $NETWORK_TYPE)
echo $output
if [[ "$output" != *"Ok = record"* ]]; then
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

    CANISTER_ID_SHARE_SERVICE_CONTROLLER=$(echo "$RESULT_2" | grep -o 'address = "[^"]*"' | sed 's/address = "//;s/"//')
    echo "CANISTER_ID_SHARE_SERVICE_CONTROLLER: $CANISTER_ID_SHARE_SERVICE_CONTROLLER"

    echo " "
    echo "Going into a loop to wait for the ShareService Controller setup to finish."
    CANISTER_STATUS=$(echo "$RESULT_2" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
    echo "CANISTER_STATUS: $CANISTER_STATUS"
    WAIT_TIME=5
    while [[ "$CANISTER_STATUS" == "ControllerCreationInProgress" ]]; do
        echo "sleep for $WAIT_TIME seconds..."
        sleep $WAIT_TIME
        output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\";})" --network $NETWORK_TYPE)
        RESULT_2A=$(extract_record_from_variant "$output")
        CANISTER_STATUS=$(echo "$RESULT_2A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
        echo "CANISTER_STATUS: $CANISTER_STATUS"
    done
fi

echo "RESULT_2A (getMainerAgentCanisterInfo): $RESULT_2A"

echo " "
echo "--------------------------------------------------"
echo "Registering ShareService mAIner canister with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\"; canisterType = variant {MainerAgent = variant {ShareService}} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for ShareService mAIner canister $CANISTER_ID_SHARE_SERVICE_CONTROLLER."
    exit 1
else
    echo "Successfully called addOfficialCanister for ShareService mAIner canister $CANISTER_ID_SHARE_SERVICE_CONTROLLER."
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

SHARE_SERVICE_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_SHARE_SERVICE_CONTROLLER 2>&1 | grep "Balance:"| awk '{print $2}')
SHARE_SERVICE_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_SHARE_SERVICE_CONTROLLER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
SHARE_SERVICE_BALANCE_1_T=$(echo "scale=4; $SHARE_SERVICE_BALANCE_1 / 1000000000000" | bc)

COST_TO_SPINUP_SHARE_SERVICE_CONTROLLER=$(echo "- $GAME_STATE_CYCLES_CHANGE_1 - $MAINER_CREATOR_CYCLES_CHANGE_1 - $SHARE_SERVICE_BALANCE_1" | bc)
COST_TO_SPINUP_SHARE_SERVICE_CONTROLLER_T=$(echo "scale=4; $COST_TO_SPINUP_SHARE_SERVICE_CONTROLLER / 1000000000000" | bc)

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
echo "ShareService  ($CANISTER_ID_SHARE_SERVICE_CONTROLLER) "
echo "-> Balance: $SHARE_SERVICE_BALANCE_1_T TCycles ($SHARE_SERVICE_BALANCE_1_)"

echo " "
echo "Cost to spinup ShareService controller: $COST_TO_SPINUP_SHARE_SERVICE_CONTROLLER_T TCycles ($COST_TO_SPINUP_SHARE_SERVICE_CONTROLLER)"
##############################################################

echo " "
echo "Calling setUpMainerLlmCanister to add an LLM to the ShareService"
output=$(dfx canister call game_state_canister setUpMainerLlmCanister "$RESULT_2A" --network $NETWORK_TYPE)

if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo "Call to setUpMainerLlmCanister.. Exiting."    
    exit 1
else
    RESULT_3=$(extract_record_from_variant "$output")
    echo "RESULT_3 (setUpMainerLlmCanister): $RESULT_3"
    echo " "
    CANISTER_ID_SHARE_SERVICE_LLM=$(echo "$RESULT_3" | grep -o 'llmCanisterId = "[^"]*"' | sed 's/llmCanisterId = "//;s/"//')
    echo "CANISTER_ID_SHARE_SERVICE_LLM: $CANISTER_ID_SHARE_SERVICE_LLM"

    echo "Going into a loop to wait for the LLM setup to finish."
    CANISTER_STATUS_BLOCK=$(printf '%s\n' "$RESULT_3" | extract_status_block)
    CANISTER_STATUS=$(printf '%s\n' "$CANISTER_STATUS_BLOCK" | extract_status_name)
    echo "CANISTER_STATUS: $CANISTER_STATUS"
    WAIT_TIME=30
    while [[ "$CANISTER_STATUS" == "LlmSetupInProgress" ]]; do
        echo "sleep for $WAIT_TIME seconds..."
        sleep $WAIT_TIME
        output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\";})" --network $NETWORK_TYPE)
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

SHARE_SERVICE_LLM_BALANCE_2_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_SHARE_SERVICE_LLM 2>&1 | grep "Balance:"| awk '{print $2}')
SHARE_SERVICE_LLM_BALANCE_2=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_SHARE_SERVICE_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
SHARE_SERVICE_LLM_BALANCE_2_T=$(echo "scale=4; $SHARE_SERVICE_LLM_BALANCE_2 / 1000000000000" | bc)

COST_TO_SPINUP_SHARE_SERVICE_LLM=$(echo "- $GAME_STATE_CYCLES_CHANGE_2 - $MAINER_CREATOR_CYCLES_CHANGE_2 - $SHARE_SERVICE_LLM_BALANCE_2" | bc)
COST_TO_SPINUP_SHARE_SERVICE_LLM_T=$(echo "scale=4; $COST_TO_SPINUP_SHARE_SERVICE_LLM / 1000000000000" | bc)

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
echo "ServiceLLM   ($CANISTER_ID_SHARE_SERVICE_LLM) "
echo "-> Balance: $SHARE_SERVICE_LLM_BALANCE_2_T TCycles ($SHARE_SERVICE_LLM_BALANCE_2_)"

echo " "
echo "Cost to spinup ShareService LLM: $COST_TO_SPINUP_SHARE_SERVICE_LLM_T TCycles ($COST_TO_SPINUP_SHARE_SERVICE_LLM)"
##############################################################

echo " "
echo "========================================================================"
echo "To add another LLM to the ShareService Controller $CANISTER_ID_SHARE_SERVICE_CONTROLLER:"
echo " "
echo "(-) First add 5 TCycles to the GameState canister:"
echo "dfx wallet send  $CANISTER_ID_GAME_STATE_CANISTER 5000000000000 --network $NETWORK_TYPE "
echo "(-) Then add the LLM to the ShareService Controller by calling the GameState:"
echo "dfx canister call $CANISTER_ID_GAME_STATE_CANISTER addLlmCanisterToMainer  '$RESULT_2A' --network $NETWORK_TYPE"
echo " "
echo "========================================================================"
echo "The timers are running! To stop timers for ShareService $CANISTER_ID_SHARE_SERVICE_CONTROLLER, call the ShareService controller:"
echo " "
echo "dfx canister call $CANISTER_ID_SHARE_SERVICE_CONTROLLER stopTimerExecutionAdmin --network $NETWORK_TYPE"
echo " "
echo "========================================================================"