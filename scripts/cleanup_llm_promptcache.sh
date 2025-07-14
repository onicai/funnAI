#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/log.sh --network [local|ic]
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
        --canister-id)
            shift
            CANISTER_ID=$1
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--llm-type [challenger|judge|share_service]] --canister-id <canister_id>"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"
echo "Using CANISTER_ID: $CANISTER_ID"

python -m scripts.cleanup_llm_promptcache --network $NETWORK_TYPE --canister-id $CANISTER_ID
