#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/start-judge.sh --network [local|ic|development|testing|demo|prd]
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

cd PoAIW/src/Judge
CANISTER_ID_JUDGE_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id judge_ctrlb_canister)

# go back to the funnAI folder
cd ../../../

#######################################################################
echo " "
echo "--------------------------------------------------"
echo "Checking health endpoint of Chellenger ($CANISTER_ID_JUDGE_CTRLB_CANISTER)"
output=$(dfx canister call $CANISTER_ID_JUDGE_CTRLB_CANISTER health --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Judge ($CANISTER_ID_JUDGE_CTRLB_CANISTER) is not healthy. Exiting."
    exit 1
else
    echo "Judge ($CANISTER_ID_JUDGE_CTRLB_CANISTER) is healthy."
fi

echo " "
echo "--------------------------------------------------"
echo "Starting timer for Judge ($CANISTER_ID_JUDGE_CTRLB_CANISTER)"
dfx canister call $CANISTER_ID_JUDGE_CTRLB_CANISTER startTimerExecutionAdmin --network $NETWORK_TYPE