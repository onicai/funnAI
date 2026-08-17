#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/deploy-mainers-ShareService-LLMs-via-gamestate.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

CANISTER_ID_GAME_STATE_CANISTER=$(icp canister status game_state_canister -e $NETWORK_TYPE --id-only)
cd PoAIW/src/mAInerCreator
CANISTER_ID_MAINER_CREATOR_CANISTER=$(icp canister status mainer_creator_canister -e $NETWORK_TYPE --id-only)

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

if [ "$NETWORK_TYPE" = "local" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "To fund LLM creation - Adding 5 TCycles to the game_state_canister canister on local"
    icp canister top-up game_state_canister --amount $((5 * 1000000000000)) -e local
else
    echo " "
    echo "--------------------------------------------------"
    echo "To fund LLM creation - Adding 5 TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    icp canister call jh35u-eqaaa-aaaag-abf3a-cai wallet_send "(record { canister = principal \"$CANISTER_ID_GAME_STATE_CANISTER\"; amount = 5000000000000 : nat64 })" -e $NETWORK_TYPE
fi

echo " "
echo "--------------------------------------------------"
output=$(icp canister call $CANISTER_ID_GAME_STATE_CANISTER getSharedServiceCanistersAdmin '()' -e $NETWORK_TYPE)
if [[ "$output" != *"Ok = vec"* ]]; then
    echo $output
    echo " "
    echo "Call to getSharedServiceCanistersAdmin failed. Exiting."    
    exit 1
else
    CANISTER_ID_SHARE_SERVICE_CONTROLLER=$(extract_address_of_mAIner "$output" "ShareService")
fi

echo "CANISTER_ID_SHARE_SERVICE_CONTROLLER: $CANISTER_ID_SHARE_SERVICE_CONTROLLER"

echo " "
echo "--------------------------------------------------"
echo "Checking health endpoint of ShareService canister ($CANISTER_ID_SHARE_SERVICE_CONTROLLER)"
output=$(icp canister call $CANISTER_ID_SHARE_SERVICE_CONTROLLER health '()' -e $NETWORK_TYPE --query)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo $output
    echo "ShareService Canister is not healthy. Exiting."
    exit 1
else
    echo "ShareService Canister is healthy."
fi

echo " "
echo "--------------------------------------------------"
output=$(icp canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\";})" -e $NETWORK_TYPE)
RESULT_2A=$(extract_record_from_variant "$output")
CANISTER_STATUS=$(echo "$RESULT_2A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
echo "CANISTER_STATUS: $CANISTER_STATUS"

echo "RESULT_2A (getMainerAgentCanisterInfo): $RESULT_2A"

echo " "
echo "Calling setUpMainerLlmCanister to add an LLM to the ShareService"
output=$(icp canister call game_state_canister setUpMainerLlmCanister "$RESULT_2A" -e $NETWORK_TYPE)

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
    echo " "

    echo "Going into a loop to wait for the LLM setup to finish."
    CANISTER_STATUS_BLOCK=$(printf '%s\n' "$RESULT_3" | extract_status_block)
    CANISTER_STATUS=$(printf '%s\n' "$CANISTER_STATUS_BLOCK" | extract_status_name)
    echo "CANISTER_STATUS: $CANISTER_STATUS"
    WAIT_TIME=30
    while [[ "$CANISTER_STATUS" == "LlmSetupInProgress" ]]; do
        echo "sleep for $WAIT_TIME seconds..."
        sleep $WAIT_TIME
        output=$(icp canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\";})" -e $NETWORK_TYPE)
        RESULT_3A=$(extract_record_from_variant "$output")
        CANISTER_STATUS_BLOCK=$(printf '%s\n' "$RESULT_3A" | extract_status_block)
        CANISTER_STATUS=$(printf '%s\n' "$CANISTER_STATUS_BLOCK" | extract_status_name)
        echo "CANISTER_STATUS_BLOCK: $CANISTER_STATUS_BLOCK"
        # echo "CANISTER_STATUS:       $CANISTER_STATUS"
    done
fi

output=$(icp canister call game_state_canister getMainerAgentCanisterInfo "(record { address = \"$CANISTER_ID_SHARE_SERVICE_CONTROLLER\";})" -e $NETWORK_TYPE)
RESULT_3A=$(extract_record_from_variant "$output")
CANISTER_STATUS=$(echo "$RESULT_3A" | grep -o 'status = variant { [^}]* }' | sed 's/status = variant { //; s/ }//')
echo "CANISTER_STATUS: $CANISTER_STATUS"

echo " "
echo "RESULT_3A (getMainerAgentCanisterInfo) summary from ShareService Controller: $RESULT_3A"

echo " "
echo "Succesfully completed setup of ShareService LLM: $CANISTER_ID_SHARE_SERVICE_LLM"
echo " "