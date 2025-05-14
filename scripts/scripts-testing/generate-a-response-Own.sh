#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/generate-a-challenge.sh
#######################################################################

# Default network type is local
NETWORK_TYPE="local"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

CANISTER_ID_GAME_STATE_CANISTER=$(dfx canister --network $NETWORK_TYPE id game_state_canister)

echo "CANISTER_ID_GAME_STATE_CANISTER: $CANISTER_ID_GAME_STATE_CANISTER"

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

echo "Finding the address of my first mAIner of type Own..."

# echo " "
# echo "Retrieving all my mAIner agents:"
output=$(dfx canister --network $NETWORK_TYPE call $CANISTER_ID_GAME_STATE_CANISTER getMainerAgentCanistersForUser)
if [[ "$output" != *"Ok = vec"* ]]; then
    echo $output
    echo " "
    echo "Call to getMainerAgentCanistersForUser failed. Exiting."    
    exit 1
else
    # echo "output (getMainerAgentCanistersForUser): $output"
    # echo " "
    # echo "Extracting the address of my first mAIner of type Own"
    CANISTER_ID_OWN_CONTROLLER=$(extract_address_of_mAIner "$output" "Own")
    # echo "CANISTER_ID_OWN_CONTROLLER: $CANISTER_ID_OWN_CONTROLLER"
fi

# echo " "
# echo "Get the LLM for the mAIner Agent ($CANISTER_ID_OWN_CONTROLLER):"
output=$(dfx canister --network $NETWORK_TYPE call $CANISTER_ID_OWN_CONTROLLER getLLMCanisterIds)
# echo "output (getLLMCanisterIds): $output"
if [[ "$output" != *"Ok = vec"* ]]; then
    echo $output
    echo " "
    echo "Call to getMainerAgentCanistersForUser failed. Exiting."    
    exit 1
else
    CANISTER_ID_OWN_LLM=$(echo "$output" | grep -oE '"[a-z0-9-]+"' | sed 's/"//g')
fi

# echo " "
echo "CANISTER_ID_OWN_CONTROLLER: $CANISTER_ID_OWN_CONTROLLER"
echo "CANISTER_ID_OWN_LLM: $CANISTER_ID_OWN_LLM"


#######################################################################
echo "TODO: fund mAIner with sufficient Cycles to create a response"
# if [ "$NETWORK_TYPE" = "local" ]; then
#     echo " "
#     echo "--------------------------------------------------"
#     echo "To fund Controller creation - Adding 5 TCycles to the game_state_canister canister on local"
#     dfx ledger fabricate-cycles --canister game_state_canister --t 5
# else
#     echo " "
#     echo "--------------------------------------------------"
#     echo "To fund Controller creation - Adding 5 TCycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
#     dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER 5000000000000
# fi

# ================================================================

echo " "
echo "We will first check the balances of the canisters involved in generating the response."
echo " "

echo " "
echo "--------------------------------------------------"
########################################################
GAME_STATE_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{print $2}')
GAME_STATE_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_0_T=$(echo "scale=6; $GAME_STATE_BALANCE_0 / 1000000000000" | bc)

MAINER_OWN_CTRLB_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_OWN_CTRLB_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_OWN_CTRLB_BALANCE_0_T=$(echo "scale=6; $MAINER_OWN_CTRLB_BALANCE_0 / 1000000000000" | bc)

MAINER_OWN_LLM_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_OWN_LLM_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_OWN_LLM_BALANCE_0_T=$(echo "scale=6; $MAINER_OWN_LLM_BALANCE_0 / 1000000000000" | bc)

echo " "
echo "Before generateNewChallenge:"
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_0_T TCycles ($GAME_STATE_BALANCE_0_)"

echo " "
echo "mAIner ctrlb  ($CANISTER_ID_OWN_CONTROLLER) "
echo "-> Balance: $MAINER_OWN_CTRLB_BALANCE_0_T TCycles ($MAINER_OWN_CTRLB_BALANCE_0_)"

echo " "
echo "mAIner LLM    ($CANISTER_ID_OWN_LLM) "
echo "-> Balance: $MAINER_OWN_LLM_BALANCE_0_T TCycles ($MAINER_OWN_LLM_BALANCE_0)"
########################################################

echo " "
echo "Calling triggerChallengeResponseAdmin"
output=$(dfx canister call $CANISTER_ID_OWN_CONTROLLER triggerChallengeResponseAdmin --network $NETWORK_TYPE)

if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo " "
    echo "Call to triggerChallengeResponseAdmin failed. Exiting."    
    exit 1
else
    echo $output
    echo " "
    echo "We do not yet have a good method to automatically determine when the response generation is done."
    echo "So, please monitor the logs of the mAIner agent ($CANISTER_ID_OWN_CONTROLLER) and the LLM ($CANISTER_ID_OWN_LLM) to see when the response generation is done."
    read -p "When done, press Enter to continue..."
fi

echo " "
echo "Thank you! We will now check the balances again to see how much cycles were used to generate the response."
echo " "
##############################################################
GAME_STATE_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
GAME_STATE_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_1_T=$(echo "scale=6; $GAME_STATE_BALANCE_1 / 1000000000000" | bc)
GAME_STATE_CYCLES_CHANGE_1=$(echo "$GAME_STATE_BALANCE_1 - $GAME_STATE_BALANCE_0" | bc)
GAME_STATE_CYCLES_CHANGE_1_T=$(echo "scale=6; $GAME_STATE_CYCLES_CHANGE_1 / 1000000000000" | bc)

MAINER_OWN_CTRLB_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_OWN_CTRLB_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_CONTROLLER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_OWN_CTRLB_BALANCE_1_T=$(echo "scale=6; $MAINER_OWN_CTRLB_BALANCE_1 / 1000000000000" | bc)
MAINER_OWN_CTRLB_CYCLES_CHANGE_1=$(echo "$MAINER_OWN_CTRLB_BALANCE_1 - $MAINER_OWN_CTRLB_BALANCE_0" | bc)
MAINER_OWN_CTRLB_CYCLES_CHANGE_1_T=$(echo "scale=6; $MAINER_OWN_CTRLB_CYCLES_CHANGE_1 / 1000000000000" | bc)

MAINER_OWN_LLM_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:"| awk '{print $2}')
MAINER_OWN_LLM_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_OWN_LLM 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
MAINER_OWN_LLM_BALANCE_1_T=$(echo "scale=6; $MAINER_OWN_LLM_BALANCE_1 / 1000000000000" | bc)
MAINER_OWN_LLM_CYCLES_CHANGE_1=$(echo "$MAINER_OWN_LLM_BALANCE_1 - $MAINER_OWN_LLM_BALANCE_0" | bc)
MAINER_OWN_LLM_CYCLES_CHANGE_1_T=$(echo "scale=6; $MAINER_OWN_LLM_CYCLES_CHANGE_1 / 1000000000000" | bc)

COST_TO_GENERATE_A_RESPONSE=$(echo "- $GAME_STATE_CYCLES_CHANGE_1 - $MAINER_OWN_CTRLB_CYCLES_CHANGE_1 - $MAINER_OWN_LLM_CYCLES_CHANGE_1" | bc)
COST_TO_GENERATE_A_RESPONSE_T=$(echo "scale=6; $COST_TO_GENERATE_A_RESPONSE / 1000000000000" | bc)

echo " "
echo "--------------------------------------------------"
echo "After generation of a response: "
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_1_T TCycles ($GAME_STATE_BALANCE_1_)"
echo "-> Change : $GAME_STATE_CYCLES_CHANGE_1_T TCycles ($GAME_STATE_CYCLES_CHANGE_1)"

echo " "
echo "mAIner ctrlb  ($CANISTER_ID_OWN_CONTROLLER) "
echo "-> Balance: $MAINER_OWN_CTRLB_BALANCE_1_T TCycles ($MAINER_OWN_CTRLB_BALANCE_1_)"
echo "-> Change : $MAINER_OWN_CTRLB_CYCLES_CHANGE_1_T TCycles ($MAINER_OWN_CTRLB_CYCLES_CHANGE_1)"

echo " "
echo "mAIner LLM    ($CANISTER_ID_OWN_LLM) "
echo "-> Balance: $MAINER_OWN_LLM_BALANCE_1_T TCycles ($MAINER_OWN_LLM_BALANCE_1)"
echo "-> Change : $MAINER_OWN_LLM_CYCLES_CHANGE_1_T TCycles ($MAINER_OWN_LLM_CYCLES_CHANGE_1)"

echo " "
echo "Cost to generate a challenge: $COST_TO_GENERATE_A_RESPONSE_T TCycles ($COST_TO_GENERATE_A_RESPONSE)"

echo " "
echo "to copy into spreadsheet (corrected for the mAIner sending 0.1T cycles with the Submission...):"
echo $COST_TO_GENERATE_A_RESPONSE_T
echo $(echo "- $GAME_STATE_CYCLES_CHANGE_1_T + 0.1" | bc)
echo $(echo "- $MAINER_OWN_CTRLB_CYCLES_CHANGE_1_T - 0.1" | bc)
echo $(echo "- $MAINER_OWN_LLM_CYCLES_CHANGE_1_T" | bc)

##############################################################