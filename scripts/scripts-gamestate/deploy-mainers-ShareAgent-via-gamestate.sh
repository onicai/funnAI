#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"
FORCE=""

# only for upgrade
CANISTER_ID_SHARE_AGENT_CONTROLLER=""

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ] || [ "$1" = "development" ] || [ "$1" = "demo" ] || [ "$1" = "prd" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic' or 'testing' or 'development' or 'demo' or 'prd'."
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
        --force)
            # This prevents the script from asking for confirmation when reinstalling
            FORCE="--y"
            shift
            ;;
        --canister)
            shift
            CANISTER_ID_SHARE_AGENT_CONTROLLER=$1
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --mode [install|reinstall|upgrade] [--force] [--canister <CANISTER_ID_SHARE_AGENT_CONTROLLER>]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"
echo "We are going to   : $DEPLOY_MODE $FORCE $CANISTER_ID_SHARE_AGENT_CONTROLLER"

# Check if user wants to reinstall and confirm
if [ "$DEPLOY_MODE" = "reinstall" ] && [ "$FORCE" == "" ]; then
    echo " "
    read -p "Are you sure you want to reinstall? This will OVERWRITE all the data and code in the canister. (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Reinstall cancelled."
        exit 1
    fi
fi

if ([ "$DEPLOY_MODE" = "upgrade" ] || [ "$DEPLOY_MODE" = "reinstall" ]) && [ "$CANISTER_ID_SHARE_AGENT_CONTROLLER" = "" ]; then
    echo " "
    echo "For $DEPLOY_MODE mode, you must provide the canister ID of the ShareAgent controller."
    echo "Usage: $0 --network [local|ic|testing|development] --mode $DEPLOY_MODE --canister <CANISTER_ID_SHARE_AGENT_CONTROLLER>"
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

extract_address_of_mAIner() {
  local input="$1"
  local target_type="$2"

  python3 -c "
import re
import sys

data = '''$input'''
target_type = '''$target_type'''

records = []
start = 0

while True:
    match = re.search(r'record\s*\{', data[start:])
    if not match:
        break
    record_start = start + match.start()
    brace_level = 0
    i = record_start
    while i < len(data):
        if data[i] == '{':
            brace_level += 1
        elif data[i] == '}':
            brace_level -= 1
            if brace_level == 0:
                records.append(data[record_start:i+1])
                start = i + 1
                break
        i += 1
    else:
        break  # Unbalanced braces

for record in records:
    if f'MainerAgent = variant {{ {target_type} }}' in record:
        match = re.search(r'address\s*=\s*\"([^\"]+)\"', record)
        if match:
            print(match.group(1))
            break
"
}
# ================================================================

#######################################################################
NUMCYCLES_TO_ADD=6500000000000  # 6.5 TCycles
if [ "$DEPLOY_MODE" = "upgrade" ] || [ "$DEPLOY_MODE" = "reinstall" ]; then
    NUMCYCLES_TO_ADD=10000000000  # 10 BCycles for upgrade
fi

if [ "$NETWORK_TYPE" = "local" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Controller $DEPLOY_MODE - Adding $NUMCYCLES_TO_ADD TCycles to the game_state_canister canister on local"
    dfx ledger fabricate-cycles --canister game_state_canister --t $NUMCYCLES_TO_ADD
else
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Controller $DEPLOY_MODE - Adding $NUMCYCLES_TO_ADD TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER $NUMCYCLES_TO_ADD
fi

# ================================================================
# Type: #ShareAgent

echo " "
echo "--------------------------------------------------"
echo "$DEPLOY_MODE a mAInerController canister of type #ShareAgent"

if [ "$DEPLOY_MODE" = "upgrade" ] || [ "$DEPLOY_MODE" = "reinstall" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "Checking health endpoint of ShareAgent canister ($CANISTER_ID_SHARE_AGENT_CONTROLLER)"
    output=$(dfx canister call $CANISTER_ID_SHARE_AGENT_CONTROLLER health --network $NETWORK_TYPE)

    if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
        echo $output
        echo "ShareAgent Canister is not healthy. Exiting."
        exit 1
    else
        echo "ShareAgent Canister is healthy."
    fi
fi

if [ "$DEPLOY_MODE" = "upgrade" ]; then
    echo " "
    echo "Calling upgradeMainerControllerAdmin"
    output=$(dfx canister call game_state_canister upgradeMainerControllerAdmin "(record {canisterAddress = \"$CANISTER_ID_SHARE_AGENT_CONTROLLER\" })" --network $NETWORK_TYPE)
    if [[ "$output" != *"Ok = record"* ]]; then
        echo $output
        echo "Call to upgradeMainerControllerAdmin. Exiting."    
        exit 1
    else
        RESULT_2=$(extract_record_from_variant "$output")
        echo "RESULT_2 (upgradeMainerControllerAdmin): $RESULT_2"

        echo " "
        echo "Going into a loop to wait for the ShareAgent Controller upgrade to finish."
        CANISTER_STATUS=$(echo "$RESULT_2" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
        echo "CANISTER_STATUS: $CANISTER_STATUS"
        WAIT_TIME=5
        while [[ "$CANISTER_STATUS" != "Running" ]]; do
            echo "sleep for $WAIT_TIME seconds..."
            sleep $WAIT_TIME
            output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_AGENT_CONTROLLER\";})" --network $NETWORK_TYPE)
            RESULT_2A=$(extract_record_from_variant "$output")
            CANISTER_STATUS=$(echo "$RESULT_2A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
            echo "CANISTER_STATUS: $CANISTER_STATUS"
        done
    fi

    echo "RESULT_2A (upgradeMainerControllerAdmin): $RESULT_2A"
elif [ "$DEPLOY_MODE" = "reinstall" ]; then
    echo " "
    echo "Calling reinstallMainerControllerAdmin"
    output=$(dfx canister call game_state_canister reinstallMainerControllerAdmin "(record {canisterAddress = \"$CANISTER_ID_SHARE_AGENT_CONTROLLER\" })" --network $NETWORK_TYPE)
    if [[ "$output" != *"Ok = record"* ]]; then
        echo $output
        echo "Call to reinstallMainerControllerAdmin. Exiting."    
        exit 1
    else
        RESULT_2=$(extract_record_from_variant "$output")
        echo "RESULT_2 (reinstallMainerControllerAdmin): $RESULT_2"

        echo " "
        echo "Going into a loop to wait for the ShareAgent Controller reinstall to finish."
        CANISTER_STATUS=$(echo "$RESULT_2" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
        echo "CANISTER_STATUS: $CANISTER_STATUS"
        WAIT_TIME=5
        while [[ "$CANISTER_STATUS" != "Running" ]]; do
            echo "sleep for $WAIT_TIME seconds..."
            sleep $WAIT_TIME
            output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_AGENT_CONTROLLER\";})" --network $NETWORK_TYPE)
            RESULT_2A=$(extract_record_from_variant "$output")
            CANISTER_STATUS=$(echo "$RESULT_2A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
            echo "CANISTER_STATUS: $CANISTER_STATUS"
        done
    fi

    echo "RESULT_2A (reinstallMainerControllerAdmin): $RESULT_2A"
else
    echo " "
    echo "--------------------------------------------------"
    echo "Clearing any previous RedeemedTransactionBlockAdmin for paymentTransactionBlockId 12"
    dfx canister call game_state_canister removeRedeemedTransactionBlockAdmin '(record {paymentTransactionBlockId = 12 : nat64} )' --network $NETWORK_TYPE

    echo " "
    echo "--------------------------------------------------"
    echo "Calling createUserMainerAgent"
    # Note:
    # (-) arguments subnetCtrl and subnetLlm are dummy values & not used by createUserMainerAgent.
    #     The actual values are already set in the game_state_canister via setSubnetsAdmin
    # (-) argument cyclesForMainer is a dummy value & not used by this call to createUserMainerAgent.
    output=$(dfx canister call game_state_canister createUserMainerAgent '(record { paymentTransactionBlockId = 12; mainerConfig = record { mainerAgentCanisterType = variant {ShareAgent}; selectedLLM = opt variant {Qwen2_5_500M}; subnetCtrl = ""; subnetLlm = ""; cyclesForMainer = 0; }; })' --network $NETWORK_TYPE)
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

        CANISTER_ID_SHARE_AGENT_CONTROLLER=$(echo "$RESULT_2" | grep -o 'address = "[^"]*"' | sed 's/address = "//;s/"//')
        echo "CANISTER_ID_SHARE_AGENT_CONTROLLER: $CANISTER_ID_SHARE_AGENT_CONTROLLER"

        SUBNET_SHARE_AGENT=$(echo "$RESULT_2" | grep -o 'subnet = "[^"]*"' | sed 's/subnet = "//; s/"//')
        echo "SUBNET_SHARE_AGENT: $SUBNET_SHARE_AGENT"
    fi
fi