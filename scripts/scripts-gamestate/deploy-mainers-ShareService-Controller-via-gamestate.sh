#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/deploy-mainers-ShareService-Controller-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ] || [ "$1" = "development" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic' or 'testing' or 'development'."
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
    echo "To fund Controller creation - Adding 5 TCycles to the game_state_canister canister on local"
    dfx ledger fabricate-cycles --canister game_state_canister --t 5
else
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Controller creation - Adding 5 TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER 5000000000000
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
# Note:
# (-) arguments subnetCtrl and subnetLlm are dummy values & not used by createUserMainerAgent.
#     The actual values are already set in the game_state_canister via setSubnetsAdmin
# (-) argument cyclesForMainer is a dummy value & not used by this call to createUserMainerAgent.
output=$(dfx canister call game_state_canister createUserMainerAgent '(record { paymentTransactionBlockId = 0; mainerConfig = record { mainerAgentCanisterType = variant {ShareService}; selectedLLM = opt variant {Qwen2_5_500M}; subnetCtrl = ""; subnetLlm = ""; cyclesForMainer = 0; }; })' --network $NETWORK_TYPE)
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

SUBNET_SHARE_SERVICE=$(echo "$RESULT_2A" | grep -o 'subnet = "[^"]*"' | sed 's/subnet = "//; s/"//')
echo "SUBNET_SHARE_SERVICE: $SUBNET_SHARE_SERVICE"

# This does not work right away... The ICP dashboard shows the subnet ID only after a few minutes.
# if [ "$NETWORK_TYPE" = "local" ]; then
#     SUBNET_SHARE_SERVICE="local"
# else
#     SUBNET_SHARE_SERVICE=$(curl -s "https://ic-api.internetcomputer.org/api/v3/canisters/$CANISTER_ID_SHARE_SERVICE_CONTROLLER" | jq -r '.subnet_id')
# fi
echo " "
echo "--------------------------------------------------"
echo "Registering ShareService mAIner canister ($CANISTER_ID_SHARE_SERVICE_CONTROLLER) on subnet $SUBNET_SHARE_SERVICE with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\"; subnet = \"$SUBNET_SHARE_SERVICE\"; canisterType = variant {MainerAgent = variant {ShareService}} })" --network $NETWORK_TYPE)

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

echo "========================================================================"
echo "The timers are running! To stop timers for ShareService $CANISTER_ID_SHARE_SERVICE_CONTROLLER, call the ShareService controller:"
echo " "
echo "dfx canister call $CANISTER_ID_SHARE_SERVICE_CONTROLLER stopTimerExecutionAdmin --network $NETWORK_TYPE"
echo " "
echo "========================================================================"