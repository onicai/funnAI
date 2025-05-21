#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/register-all.sh --network [local|ic]
#######################################################################

# Default network type is local
NETWORK_TYPE="local"

# When deploying local, use canister IDs from .env
source PoAIW/src/mAInerCreator/.env
source PoAIW/src/Challenger/.env
source PoAIW/src/Judge/.env

# none will not use subnet parameter in deploy to ic
SUBNET="none"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "development" ]; then
                NETWORK_TYPE=$1
                if [ "$NETWORK_TYPE" = "ic" ]; then
                    CANISTER_ID_MAINER_CREATOR_CANISTER='movk5-tyaaa-aaaaj-az64q-cai'
                    CANISTER_ID_CHALLENGER_CTRLB_CANISTER='lxb3x-jyaaa-aaaaj-azzta-cai'
                    CANISTER_ID_JUDGE_CTRLB_CANISTER='xxnvw-4yaaa-aaaaj-az4oq-cai' 
                fi
                if [ "$NETWORK_TYPE" = "development" ]; then
                    CANISTER_ID_MAINER_CREATOR_CANISTER='hh3ix-5qaaa-aaaad-qhkxq-cai'
                    CANISTER_ID_CHALLENGER_CTRLB_CANISTER='sx25d-4yaaa-aaaai-atiaq-cai'
                    CANISTER_ID_JUDGE_CTRLB_CANISTER='tjr6j-qaaaa-aaaaj-qnpaa-cai' 
                fi
            else
                echo "Invalid network type: $1. Use 'local', 'development' or 'ic'."
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