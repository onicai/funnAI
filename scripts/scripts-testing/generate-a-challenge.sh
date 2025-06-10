#!/bin/bash

#######################################################################
# run from funnAI folder as:
# scripts/scripts-testing/generate-a-challenge.sh --network [local|ic|development|testing]
#######################################################################


# Default network type is local
NETWORK_TYPE="local"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

CANISTER_ID_GAME_STATE_CANISTER=$(dfx canister --network $NETWORK_TYPE id game_state_canister)
cd PoAIW/src/Challenger
CANISTER_ID_CHALLENGER_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id challenger_ctrlb_canister)
cd ../../llms/Challenger
CANISTER_ID_CHALLENGER_LLM_0=$(dfx canister --network $NETWORK_TYPE id llm_0)
# Switching to only 1 LLM for Challenger
# if [ "$NETWORK_TYPE" != "local" ]; then
#     CANISTER_ID_CHALLENGER_LLM_1=$(dfx canister --network $NETWORK_TYPE id llm_1)   
# fi

# go back to the funnAI folder
cd ../../../

echo "CANISTER_ID_GAME_STATE_CANISTER: $CANISTER_ID_GAME_STATE_CANISTER"
echo "CANISTER_ID_CHALLENGER_CTRLB_CANISTER: $CANISTER_ID_CHALLENGER_CTRLB_CANISTER"
echo "CANISTER_ID_CHALLENGER_LLM_0: $CANISTER_ID_CHALLENGER_LLM_0"

# Switching to only 1 LLM for Challenger
# if [ "$NETWORK_TYPE" != "local" ]; then
#     echo "CANISTER_ID_CHALLENGER_LLM_1: $CANISTER_ID_CHALLENGER_LLM_1"
# fi

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
    echo "To fund Challenger - Adding 5 TCycles to the game_state_canister canister on local"
    dfx ledger fabricate-cycles --canister game_state_canister --t 1
else
    echo " "
    echo "--------------------------------------------------"
    echo "To fund Challenger - Adding 400_000_000_000 Cycles to the game_state_canister ($CANISTER_ID_GAME_STATE_CANISTER) canister on $NETWORK_TYPE"
    dfx wallet send --network $NETWORK_TYPE $CANISTER_ID_GAME_STATE_CANISTER 400_000_000_000
fi

# ================================================================

echo " "
echo "We will first check the balances of the canisters involved in generating the Challenge."
echo "(Be patient, this may take a few seconds.)"

echo " "
echo "--------------------------------------------------"
########################################################
GAME_STATE_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{print $2}')
GAME_STATE_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_0_T=$(echo "scale=6; $GAME_STATE_BALANCE_0 / 1000000000000" | bc)

CHALLENGER_CTRLB_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_CTRLB_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
CHALLENGER_CTRLB_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_CTRLB_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
CHALLENGER_CTRLB_BALANCE_0_T=$(echo "scale=6; $CHALLENGER_CTRLB_BALANCE_0 / 1000000000000" | bc)

CHALLENGER_LLM_0_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_0 2>&1 | grep "Balance:"| awk '{print $2}')
CHALLENGER_LLM_0_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_0 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
CHALLENGER_LLM_0_BALANCE_0_T=$(echo "scale=6; $CHALLENGER_LLM_0_BALANCE_0 / 1000000000000" | bc)

# if [ "$NETWORK_TYPE" != "local" ]; then
#     CHALLENGER_LLM_1_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_1 2>&1 | grep "Balance:"| awk '{print $2}')
#     CHALLENGER_LLM_1_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_1 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
#     CHALLENGER_LLM_1_BALANCE_0_T=$(echo "scale=6; $CHALLENGER_LLM_1_BALANCE_0 / 1000000000000" | bc)
# fi

echo " "
echo "Before generateNewChallenge:"
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_0_T TCycles ($GAME_STATE_BALANCE_0_)"

echo " "
echo "Challenger    ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER) "
echo "-> Balance: $CHALLENGER_CTRLB_BALANCE_0_T TCycles ($CHALLENGER_CTRLB_BALANCE_0_)"

echo " "
echo "LLM 0         ($CANISTER_ID_CHALLENGER_LLM_0) "
echo "-> Balance: $CHALLENGER_LLM_0_BALANCE_0_T TCycles ($CHALLENGER_LLM_0_BALANCE_0)"

# if [ "$NETWORK_TYPE" != "local" ]; then
#     echo " "
#     echo "LLM 1         ($CANISTER_ID_CHALLENGER_LLM_1) "
#     echo "-> Balance: $CHALLENGER_LLM_1_BALANCE_0_T TCycles ($CHALLENGER_LLM_1_BALANCE_0)"
# fi
########################################################

echo " "
echo "Calling generateNewChallenge"
output=$(dfx canister call $CANISTER_ID_CHALLENGER_CTRLB_CANISTER generateNewChallenge --network $NETWORK_TYPE)

if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo " "
    echo "If there are already sufficient open challenges, you can reset them with a call the GameState:"
    echo "dfx canister --network $NETWORK_TYPE call $CANISTER_ID_GAME_STATE_CANISTER resetCurrentChallengesAdmin"
    echo " "
    echo "Check the currently open Challenges by calling the GameState:"
    echo "dfx canister --network $NETWORK_TYPE call $CANISTER_ID_GAME_STATE_CANISTER getNumCurrentChallengesAdmin"
    echo "dfx canister --network $NETWORK_TYPE call $CANISTER_ID_GAME_STATE_CANISTER getCurrentChallengesAdmin"
    echo " "
    echo "Call to createUserMainerAgent failed. Exiting."    
    exit 1
else
    RESULT_1=$(extract_record_from_variant "$output")
    echo "RESULT_1 (createUserMainerAgent): $RESULT_1"
    GENERATED_BY_LLM_ID=$(echo "$RESULT_1" | grep -o 'generatedByLlmId = "[^"]*"' | sed 's/generatedByLlmId = "//;s/"//')
fi

# echo " "
# echo "The Challenger used LLM with ID: $GENERATED_BY_LLM_ID"
# echo "...but... it likely used the other LLM for prompt.cache generation. Will include both LLMs in the cost calculation."

echo " "
echo "We will now check the balances again to see how much cycles were used to generate the Challenge."
echo "(Be patient, this may take a few seconds.)"

##############################################################
GAME_STATE_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
GAME_STATE_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_1_T=$(echo "scale=6; $GAME_STATE_BALANCE_1 / 1000000000000" | bc)
GAME_STATE_CYCLES_CHANGE_1=$(echo "$GAME_STATE_BALANCE_1 - $GAME_STATE_BALANCE_0" | bc)
GAME_STATE_CYCLES_CHANGE_1_T=$(echo "scale=6; $GAME_STATE_CYCLES_CHANGE_1 / 1000000000000" | bc)

CHALLENGER_CTRLB_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_CTRLB_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
CHALLENGER_CTRLB_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_CTRLB_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
CHALLENGER_CTRLB_BALANCE_1_T=$(echo "scale=6; $CHALLENGER_CTRLB_BALANCE_1 / 1000000000000" | bc)
CHALLENGER_CTRLB_CYCLES_CHANGE_1=$(echo "$CHALLENGER_CTRLB_BALANCE_1 - $CHALLENGER_CTRLB_BALANCE_0" | bc)
CHALLENGER_CTRLB_CYCLES_CHANGE_1_T=$(echo "scale=6; $CHALLENGER_CTRLB_CYCLES_CHANGE_1 / 1000000000000" | bc)

CHALLENGER_LLM_0_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_0 2>&1 | grep "Balance:"| awk '{print $2}')
CHALLENGER_LLM_0_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_0 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
CHALLENGER_LLM_0_BALANCE_1_T=$(echo "scale=6; $CHALLENGER_LLM_0_BALANCE_1 / 1000000000000" | bc)
CHALLENGER_LLM_0_CYCLES_CHANGE_1=$(echo "$CHALLENGER_LLM_0_BALANCE_1 - $CHALLENGER_LLM_0_BALANCE_0" | bc)
CHALLENGER_LLM_0_CYCLES_CHANGE_1_T=$(echo "scale=6; $CHALLENGER_LLM_0_CYCLES_CHANGE_1 / 1000000000000" | bc)

# CHALLENGER_LLM_1_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_1 2>&1 | grep "Balance:"| awk '{print $2}')
# CHALLENGER_LLM_1_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_CHALLENGER_LLM_1 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
# CHALLENGER_LLM_1_BALANCE_1_T=$(echo "scale=6; $CHALLENGER_LLM_1_BALANCE_1 / 1000000000000" | bc)
# CHALLENGER_LLM_1_CYCLES_CHANGE_1=$(echo "$CHALLENGER_LLM_1_BALANCE_1 - $CHALLENGER_LLM_1_BALANCE_0" | bc)
# CHALLENGER_LLM_1_CYCLES_CHANGE_1_T=$(echo "scale=6; $CHALLENGER_LLM_1_CYCLES_CHANGE_1 / 1000000000000" | bc)

# This is no longer correct, because we fund the Challenger & LLM
# COST_TO_GENERATE_A_CHALLENGE=$(echo "- $GAME_STATE_CYCLES_CHANGE_1 - $CHALLENGER_CTRLB_CYCLES_CHANGE_1 - $CHALLENGER_LLM_0_CYCLES_CHANGE_1 - $CHALLENGER_LLM_1_CYCLES_CHANGE_1" | bc)
# COST_TO_GENERATE_A_CHALLENGE_T=$(echo "scale=6; $COST_TO_GENERATE_A_CHALLENGE / 1000000000000" | bc)

echo " "
echo "--------------------------------------------------"
echo "After generateNewChallenge: "
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_1_T TCycles ($GAME_STATE_BALANCE_1_)"
echo "-> Change : $GAME_STATE_CYCLES_CHANGE_1_T TCycles ($GAME_STATE_CYCLES_CHANGE_1)"

echo " "
echo "Challenger    ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER) "
echo "-> Balance: $CHALLENGER_CTRLB_BALANCE_1_T TCycles ($CHALLENGER_CTRLB_BALANCE_1_)"
echo "-> Change : $CHALLENGER_CTRLB_CYCLES_CHANGE_1_T TCycles ($CHALLENGER_CTRLB_CYCLES_CHANGE_1)"

echo " "
echo "LLM 0         ($CANISTER_ID_CHALLENGER_LLM_0) "
echo "-> Balance: $CHALLENGER_LLM_0_BALANCE_1_T TCycles ($CHALLENGER_LLM_0_BALANCE_1_)"
echo "-> Change : $CHALLENGER_LLM_0_CYCLES_CHANGE_1_T TCycles ($CHALLENGER_LLM_0_CYCLES_CHANGE_1)"

# echo " "
# echo "LLM 1         ($CANISTER_ID_CHALLENGER_LLM_1) "
# echo "-> Balance: $CHALLENGER_LLM_1_BALANCE_1_T TCycles ($CHALLENGER_LLM_1_BALANCE_1_)"
# echo "-> Change : $CHALLENGER_LLM_1_CYCLES_CHANGE_1_T TCycles ($CHALLENGER_LLM_1_CYCLES_CHANGE_1)"

# echo " "
# echo "Cost to generate a challenge: $COST_TO_GENERATE_A_CHALLENGE_T TCycles ($COST_TO_GENERATE_A_CHALLENGE)"

# echo " "
# echo "to copy into spreadsheet:"
# echo $COST_TO_GENERATE_A_CHALLENGE_T
# echo $(echo "- $GAME_STATE_CYCLES_CHANGE_1_T" | bc)
# echo $(echo "- $CHALLENGER_CTRLB_CYCLES_CHANGE_1_T" | bc)
# echo $(echo "- $CHALLENGER_LLM_0_CYCLES_CHANGE_1_T - $CHALLENGER_LLM_1_CYCLES_CHANGE_1_T" | bc)

##############################################################