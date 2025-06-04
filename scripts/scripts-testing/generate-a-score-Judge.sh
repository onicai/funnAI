#!/bin/bash

#######################################################################
# run from funnAI folder as:
# scripts/scripts-testing/generate-a-score-Judge.sh --network [local|ic|development|testing]
#######################################################################


# Default network type is local
NETWORK_TYPE="local"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

CANISTER_ID_GAME_STATE_CANISTER=$(dfx canister --network $NETWORK_TYPE id game_state_canister)
cd PoAIW/src/Judge
CANISTER_ID_JUDGE_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id judge_ctrlb_canister)
cd ../../llms/Judge
CANISTER_ID_JUDGE_LLM_0=$(dfx canister --network $NETWORK_TYPE id llm_0)
if [ "$NETWORK_TYPE" != "local" ]; then
    CANISTER_ID_JUDGE_LLM_1=$(dfx canister --network $NETWORK_TYPE id llm_1)   
    CANISTER_ID_JUDGE_LLM_2=$(dfx canister --network $NETWORK_TYPE id llm_2)
fi

# go back to the funnAI folder
cd ../../../

echo "CANISTER_ID_GAME_STATE_CANISTER: $CANISTER_ID_GAME_STATE_CANISTER"
echo "CANISTER_ID_JUDGE_CTRLB_CANISTER: $CANISTER_ID_JUDGE_CTRLB_CANISTER"
echo "CANISTER_ID_JUDGE_LLM_0: $CANISTER_ID_JUDGE_LLM_0"
if [ "$NETWORK_TYPE" != "local" ]; then
    echo "CANISTER_ID_JUDGE_LLM_1: $CANISTER_ID_JUDGE_LLM_1"
    echo "CANISTER_ID_JUDGE_LLM_2: $CANISTER_ID_JUDGE_LLM_2"
fi

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

echo " "
echo "We will first check the balances of the canisters involved in generating the score."
echo "(Be patient, this may take a few seconds.)"

echo " "
echo "--------------------------------------------------"
########################################################
GAME_STATE_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{print $2}')
GAME_STATE_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_0_T=$(echo "scale=6; $GAME_STATE_BALANCE_0 / 1000000000000" | bc)

JUDGE_CTRLB_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_CTRLB_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
JUDGE_CTRLB_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_CTRLB_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
JUDGE_CTRLB_BALANCE_0_T=$(echo "scale=6; $JUDGE_CTRLB_BALANCE_0 / 1000000000000" | bc)

JUDGE_LLM_0_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_0 2>&1 | grep "Balance:"| awk '{print $2}')
JUDGE_LLM_0_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_0 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
JUDGE_LLM_0_BALANCE_0_T=$(echo "scale=6; $JUDGE_LLM_0_BALANCE_0 / 1000000000000" | bc)

if [ "$NETWORK_TYPE" != "local" ]; then
    JUDGE_LLM_1_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_1 2>&1 | grep "Balance:"| awk '{print $2}')
    JUDGE_LLM_1_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_1 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
    JUDGE_LLM_1_BALANCE_0_T=$(echo "scale=6; $JUDGE_LLM_1_BALANCE_0 / 1000000000000" | bc)

    JUDGE_LLM_2_BALANCE_0_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_2 2>&1 | grep "Balance:"| awk '{print $2}')
    JUDGE_LLM_2_BALANCE_0=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_2 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
    JUDGE_LLM_2_BALANCE_0_T=$(echo "scale=6; $JUDGE_LLM_2_BALANCE_0 / 1000000000000" | bc)
fi

echo " "
echo "Before triggerScoreSubmissionAdmin:"
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_0_T TCycles ($GAME_STATE_BALANCE_0_)"

echo " "
echo "Judge    ($CANISTER_ID_JUDGE_CTRLB_CANISTER) "
echo "-> Balance: $JUDGE_CTRLB_BALANCE_0_T TCycles ($JUDGE_CTRLB_BALANCE_0_)"

echo " "
echo "LLM 0         ($CANISTER_ID_JUDGE_LLM_0) "
echo "-> Balance: $JUDGE_LLM_0_BALANCE_0_T TCycles ($JUDGE_LLM_0_BALANCE_0)"

if [ "$NETWORK_TYPE" != "local" ]; then
    echo " "
    echo "LLM 1         ($CANISTER_ID_JUDGE_LLM_1) "
    echo "-> Balance: $JUDGE_LLM_1_BALANCE_0_T TCycles ($JUDGE_LLM_1_BALANCE_0)"
    echo " "
    echo "LLM 2         ($CANISTER_ID_JUDGE_LLM_2) "
    echo "-> Balance: $JUDGE_LLM_2_BALANCE_0_T TCycles ($JUDGE_LLM_2_BALANCE_0)"
fi
########################################################

echo " "
echo "Calling triggerScoreSubmissionAdmin"
output=$(dfx canister call $CANISTER_ID_JUDGE_CTRLB_CANISTER triggerScoreSubmissionAdmin --network $NETWORK_TYPE)

if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo " "
    echo "Call to triggerScoreSubmissionAdmin failed. Exiting."    
    exit 1
else
    echo $output
    echo " "
    echo "We do not yet have a good method to automatically determine when the response generation is done."
    echo "So, please monitor the logs of the Judge Controller ($CANISTER_ID_JUDGE_CTRLB_CANISTER) and the LLMs ($CANISTER_ID_JUDGE_LLM_0 & $CANISTER_ID_JUDGE_LLM_1 ) to see when the response generation is done."
    read -p "When done, press Enter to continue..."
fi

echo "Thank you! We will now check the balances again to see how much cycles were used to generate the score."
echo "(Be patient, this may take a few seconds.)"

##############################################################
GAME_STATE_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
GAME_STATE_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_GAME_STATE_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
GAME_STATE_BALANCE_1_T=$(echo "scale=6; $GAME_STATE_BALANCE_1 / 1000000000000" | bc)
GAME_STATE_CYCLES_CHANGE_1=$(echo "$GAME_STATE_BALANCE_1 - $GAME_STATE_BALANCE_0" | bc)
GAME_STATE_CYCLES_CHANGE_1_T=$(echo "scale=6; $GAME_STATE_CYCLES_CHANGE_1 / 1000000000000" | bc)

JUDGE_CTRLB_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_CTRLB_CANISTER 2>&1 | grep "Balance:"| awk '{print $2}')
JUDGE_CTRLB_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_CTRLB_CANISTER 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
JUDGE_CTRLB_BALANCE_1_T=$(echo "scale=6; $JUDGE_CTRLB_BALANCE_1 / 1000000000000" | bc)
JUDGE_CTRLB_CYCLES_CHANGE_1=$(echo "$JUDGE_CTRLB_BALANCE_1 - $JUDGE_CTRLB_BALANCE_0" | bc)
JUDGE_CTRLB_CYCLES_CHANGE_1_T=$(echo "scale=6; $JUDGE_CTRLB_CYCLES_CHANGE_1 / 1000000000000" | bc)

JUDGE_LLM_0_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_0 2>&1 | grep "Balance:"| awk '{print $2}')
JUDGE_LLM_0_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_0 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
JUDGE_LLM_0_BALANCE_1_T=$(echo "scale=6; $JUDGE_LLM_0_BALANCE_1 / 1000000000000" | bc)
JUDGE_LLM_0_CYCLES_CHANGE_1=$(echo "$JUDGE_LLM_0_BALANCE_1 - $JUDGE_LLM_0_BALANCE_0" | bc)
JUDGE_LLM_0_CYCLES_CHANGE_1_T=$(echo "scale=6; $JUDGE_LLM_0_CYCLES_CHANGE_1 / 1000000000000" | bc)

if [ "$NETWORK_TYPE" != "local" ]; then
    JUDGE_LLM_1_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_1 2>&1 | grep "Balance:"| awk '{print $2}')
    JUDGE_LLM_1_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_1 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
    JUDGE_LLM_1_BALANCE_1_T=$(echo "scale=6; $JUDGE_LLM_1_BALANCE_1 / 1000000000000" | bc)
    JUDGE_LLM_1_CYCLES_CHANGE_1=$(echo "$JUDGE_LLM_1_BALANCE_1 - $JUDGE_LLM_0_BALANCE_0" | bc)
    JUDGE_LLM_1_CYCLES_CHANGE_1_T=$(echo "scale=6; $JUDGE_LLM_1_CYCLES_CHANGE_1 / 1000000000000" | bc)

    JUDGE_LLM_2_BALANCE_1_=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_2 2>&1 | grep "Balance:"| awk '{print $2}')
    JUDGE_LLM_2_BALANCE_1=$(dfx canister --network $NETWORK_TYPE status $CANISTER_ID_JUDGE_LLM_2 2>&1 | grep "Balance:" | awk '{gsub("_", ""); print $2}')
    JUDGE_LLM_2_BALANCE_1_T=$(echo "scale=6; $JUDGE_LLM_2_BALANCE_1 / 1000000000000" | bc)
    JUDGE_LLM_2_CYCLES_CHANGE_1=$(echo "$JUDGE_LLM_2_BALANCE_1 - $JUDGE_LLM_0_BALANCE_0" | bc)
    JUDGE_LLM_2_CYCLES_CHANGE_1_T=$(echo "scale=6; $JUDGE_LLM_2_CYCLES_CHANGE_1 / 1000000000000" | bc)
fi

echo " "
echo "--------------------------------------------------"
echo "After score generation: "
echo "GameState     ($CANISTER_ID_GAME_STATE_CANISTER) "
echo "-> Balance: $GAME_STATE_BALANCE_1_T TCycles ($GAME_STATE_BALANCE_1_)"
echo "-> Change : $GAME_STATE_CYCLES_CHANGE_1_T TCycles ($GAME_STATE_CYCLES_CHANGE_1)"

echo " "
echo "Judge    ($CANISTER_ID_JUDGE_CTRLB_CANISTER) "
echo "-> Balance: $JUDGE_CTRLB_BALANCE_1_T TCycles ($JUDGE_CTRLB_BALANCE_1_)"
echo "-> Change : $JUDGE_CTRLB_CYCLES_CHANGE_1_T TCycles ($JUDGE_CTRLB_CYCLES_CHANGE_1)"

echo " "
echo "LLM 0         ($CANISTER_ID_JUDGE_LLM_0) "
echo "-> Balance: $JUDGE_LLM_0_BALANCE_0_T TCycles ($JUDGE_LLM_0_BALANCE_0)"
echo "-> Change : $JUDGE_LLM_0_CYCLES_CHANGE_1_T TCycles ($JUDGE_LLM_0_CYCLES_CHANGE_1)"

if [ "$NETWORK_TYPE" != "local" ]; then
    echo " "
    echo "LLM 1         ($CANISTER_ID_JUDGE_LLM_1) "
    echo "-> Balance: $JUDGE_LLM_1_BALANCE_0_T TCycles ($JUDGE_LLM_1_BALANCE_0)"
    echo "-> Change : $JUDGE_LLM_1_CYCLES_CHANGE_1_T TCycles ($JUDGE_LLM_1_CYCLES_CHANGE_1)"
    echo " "
    echo "LLM 2         ($CANISTER_ID_JUDGE_LLM_2) "
    echo "-> Balance: $JUDGE_LLM_2_BALANCE_0_T TCycles ($JUDGE_LLM_2_BALANCE_0)"
    echo "-> Change : $JUDGE_LLM_2_CYCLES_CHANGE_1_T TCycles ($JUDGE_LLM_2_CYCLES_CHANGE_1)"
fi