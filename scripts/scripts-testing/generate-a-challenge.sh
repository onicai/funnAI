#!/bin/bash

#######################################################################
# run from funnAI folder as:
# scripts/scripts-testing/generate-a-challenge.sh --network [local|ic|development|testing|demo|prd]
#######################################################################


# Default network type is local
NETWORK_TYPE="local"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd]"
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

echo " "
echo "Calling generateNewChallenge"
output=$(dfx canister call $CANISTER_ID_CHALLENGER_CTRLB_CANISTER generateNewChallenge --network $NETWORK_TYPE)

if [[ "$output" != *"Ok = record"* ]]; then
    echo $output
    echo "Call to createUserMainerAgent failed. Exiting."
    exit 1
else
    RESULT_1=$(extract_record_from_variant "$output")
    echo "RESULT_1 (createUserMainerAgent): $RESULT_1"
    GENERATED_BY_LLM_ID=$(echo "$RESULT_1" | grep -o 'generatedByLlmId = "[^"]*"' | sed 's/generatedByLlmId = "//;s/"//')
fi