#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/stop-challenger.sh --network [local|ic|development|testing]
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

cd PoAIW/src/Challenger
CANISTER_ID_CHALLENGER_CTRLB_CANISTER=$(dfx canister --network $NETWORK_TYPE id challenger_ctrlb_canister)

# go back to the funnAI folder
cd ../../../

#######################################################################
echo " "
echo "--------------------------------------------------"
echo "Checking health endpoint of Chellenger ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER)"
output=$(dfx canister call $CANISTER_ID_CHALLENGER_CTRLB_CANISTER health --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "Challenger ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER) is not healthy. Exiting."
    exit 1
else
    echo "Challenger ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER) is healthy."
fi

echo " "
echo "--------------------------------------------------"
echo "Stopping timer for Challenger ($CANISTER_ID_CHALLENGER_CTRLB_CANISTER)"
dfx canister call $CANISTER_ID_CHALLENGER_CTRLB_CANISTER stopTimerExecutionAdmin --network $NETWORK_TYPE