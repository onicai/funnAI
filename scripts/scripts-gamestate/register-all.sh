#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/register-all.sh --network [local|ic]
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

cd PoAIW/src/mAInerCreator
CANISTER_ID_MAINER_CREATOR_CANISTER=$(dfx canister --network $NETWORK_TYPE id mainer_creator_canister)
cd ../Challenger
CANISTER_ID_CHALLENGER_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id challenger_ctrlb_canister)
cd ../Judge
CANISTER_ID_JUDGE_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id judge_ctrlb_canister)

echo "CANISTER_ID_MAINER_CREATOR_CANISTER: $CANISTER_ID_MAINER_CREATOR_CANISTER"
echo "CANISTER_ID_CHALLENGER_CTRLB_CANISTER: $CANISTER_ID_CHALLENGER_CTRLB_CANISTER"
echo "CANISTER_ID_JUDGE_CTRLB_CANISTER: $CANISTER_ID_JUDGE_CTRLB_CANISTER"

if [ "$NETWORK_TYPE" = "local" ]; then
    SUBNET_MAINER_CREATOR="local"
    SUBNET_CHALLENGER="local"
    SUBNET_JUDGE="local"
else
    SUBNET_MAINER_CREATOR=$(curl -s "https://ic-api.internetcomputer.org/api/v3/canisters/$CANISTER_ID_MAINER_CREATOR_CANISTER" | jq -r '.subnet_id')
    SUBNET_CHALLENGER=$(curl -s "https://ic-api.internetcomputer.org/api/v3/canisters/$CANISTER_ID_CHALLENGER_CTRLB_CANISTER" | jq -r '.subnet_id')
    SUBNET_JUDGE=$(curl -s "https://ic-api.internetcomputer.org/api/v3/canisters/$CANISTER_ID_JUDGE_CTRLB_CANISTER" | jq -r '.subnet_id')
fi

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
echo "Registering mAInerCreator ($CANISTER_ID_MAINER_CREATOR_CANISTER) on subnet $SUBNET_MAINER_CREATOR with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_MAINER_CREATOR_CANISTER\"; subnet = \"$SUBNET_MAINER_CREATOR\"; canisterType = variant {MainerCreator} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for mAInerCreator $CANISTER_ID_MAINER_CREATOR_CANISTER."
    exit 1
else
    echo "Successfully called mAInerCreator for mAInerCreator $CANISTER_ID_MAINER_CREATOR_CANISTER."
fi

echo " "
echo "--------------------------------------------------"
echo "Registering Challenger ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER) on subnet $SUBNET_CHALLENGER with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_CHALLENGER_CTRLB_CANISTER\"; subnet = \"$SUBNET_CHALLENGER\"; canisterType = variant {Challenger} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for Challenger $CANISTER_ID_CHALLENGER_CTRLB_CANISTER."
    exit 1
else
    echo "Successfully called addOfficialCanister for Challenger $CANISTER_ID_CHALLENGER_CTRLB_CANISTER."
fi

echo " "
echo "--------------------------------------------------"
echo "Registering Judge ($CANISTER_ID_JUDGE_CTRLB_CANISTER) on subnet $SUBNET_JUDGE with the game_state_canister"
output=$(dfx canister call game_state_canister addOfficialCanister "(record { address = \"$CANISTER_ID_JUDGE_CTRLB_CANISTER\"; subnet = \"$SUBNET_JUDGE\"; canisterType = variant {Judge} })" --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Error calling addOfficialCanister for Judge $CANISTER_ID_JUDGE_CTRLB_CANISTER."
    exit 1
else
    echo "Successfully called addOfficialCanister for Judge $CANISTER_ID_JUDGE_CTRLB_CANISTER."
fi 