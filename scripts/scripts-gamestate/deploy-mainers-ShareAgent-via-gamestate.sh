#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/deploy-mainers-ShareAgent-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic'."
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
            echo "Usage: $0 --network [local|ic]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

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

#######################################################################
if [ "$NETWORK_TYPE" = "local" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "Adding 20 TCycles to the game_state_canister canister"
    dfx ledger fabricate-cycles --canister game_state_canister --t 20
fi

# ================================================================
# Type: #ShareAgent

echo " "
echo "--------------------------------------------------"
echo "Deploying a mAInerController canister of type #ShareAgent"

echo " "
echo "Calling createUserMainerAgent"
output=$(dfx canister call game_state_canister createUserMainerAgent '(record { paymentTransactionBlockId = 12; mainerConfig = record { mainerAgentCanisterType = variant {ShareAgent}; selectedLLM = opt variant {Qwen2_5_500M}; }; })' --network $NETWORK_TYPE)
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
# echo $output
if [[ "$output" != *"Ok = record"* ]]; then
    echo "Call to spinUpMainerControllerCanisterfailed. Exiting."    
    exit 1
else
    RESULT_2=$(extract_record_from_variant "$output")
    echo "RESULT_2 (spinUpMainerControllerCanister): $RESULT_2"

    NEW_MAINER_SHARE_AGENT_CANISTER=$(echo "$RESULT_2" | grep -o 'address = "[^"]*"' | sed 's/address = "//;s/"//')
    echo "NEW_MAINER_SHARE_AGENT_CANISTER: $NEW_MAINER_SHARE_AGENT_CANISTER"

    echo " "
    echo "Going into a loop to wait for the ShareAgent Controller setup to finish."
    CANISTER_STATUS=$(echo "$RESULT_2" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
    echo "CANISTER_STATUS: $CANISTER_STATUS"
    WAIT_TIME=5
    while [[ "$CANISTER_STATUS" == "ControllerCreationInProgress" ]]; do
        echo "sleep for $WAIT_TIME seconds..."
        sleep $WAIT_TIME
        output=$(dfx canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$NEW_MAINER_SHARE_AGENT_CANISTER\";})" --network $NETWORK_TYPE)
        RESULT_2A=$(extract_record_from_variant "$output")
        CANISTER_STATUS=$(echo "$RESULT_2A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
        echo "CANISTER_STATUS: $CANISTER_STATUS"
    done
fi

echo "RESULT_2A (getMainerAgentCanisterInfo): $RESULT_2A"

echo "========================================================================"
echo "The timers are running! To stop for the mAInerController $NEW_MAINER_SHARE_AGENT_CANISTER of type #ShareAgent, issue this command:"
echo " "
echo "dfx canister call $NEW_MAINER_SHARE_AGENT_CANISTER startTimerExecutionAdmin --network $NETWORK_TYPE"
echo " "
echo "========================================================================"
