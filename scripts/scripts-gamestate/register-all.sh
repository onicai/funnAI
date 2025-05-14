#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/register-all.sh --network [local|ic]
#######################################################################

# Default network type is local
NETWORK_TYPE="local"

# none will not use subnet parameter in deploy to ic
SUBNET="none"

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

cd PoAIW/src/mAInerCreator
CANISTER_ID_MAINER_CREATOR_CANISTER=$(dfx canister --network $NETWORK_TYPE id mainer_creator_canister)
cd ../Challenger
CANISTER_ID_CHALLENGER_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id challenger_ctrlb_canister)
cd ../Judge
CANISTER_ID_JUDGE_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id judge_ctrlb_canister)

# go back to the funnAI folder
cd ../../../

#######################################################################
echo " "
echo "--------------------------------------------------"
echo "Checking health endpoint"
output=$(dfx canister call game_state_canister health --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "game_state_canister is not healthy. Exiting."
    exit 1
else
    echo "game_state_canister is healthy."
fi

echo " "
echo "--------------------------------------------------"
echo "Registering mAInerCreator with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_MAINER_CREATOR_CANISTER\"; canisterType = variant {MainerCreator} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for mAInerCreator $CANISTER_ID_MAINER_CREATOR_CANISTER."
    exit 1
else
    echo "Successfully called mAInerCreator for mAInerCreator $CANISTER_ID_MAINER_CREATOR_CANISTER."
fi

echo " "
echo "--------------------------------------------------"
echo "Registering Challenger with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_CHALLENGER_CTRLB_CANISTER\"; canisterType = variant {Challenger} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for Challenger $CANISTER_ID_CHALLENGER_CTRLB_CANISTER."
    exit 1
else
    echo "Successfully called addOfficialCanister for Challenger $CANISTER_ID_CHALLENGER_CTRLB_CANISTER."
fi

echo " "
echo "--------------------------------------------------"
echo "Registering Judge with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_JUDGE_CTRLB_CANISTER\"; canisterType = variant {Judge} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for Judge $CANISTER_ID_JUDGE_CTRLB_CANISTER."
    exit 1
else
    echo "Successfully called addOfficialCanister for Judge $CANISTER_ID_JUDGE_CTRLB_CANISTER."
fi 