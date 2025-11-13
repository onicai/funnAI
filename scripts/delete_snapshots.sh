#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
CANISTER_ID="all"
CANISTER_TYPES="protocol"
DRY_RUN=""
WORKERS=""

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
        --canister-types)
            shift
            if [ "$1" = "all" ] || [ "$1" = "protocol" ] || [ "$1" = "mainers" ]; then
                CANISTER_TYPES=$1
            else
                echo "Invalid canister types: $1. Use 'all' or 'protocol' or 'mainers'."
                exit 1
            fi
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --workers)
            shift
            WORKERS="--workers $1"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --canister-id [CANISTER_ID/all] --canister-types [all|protocol|mainers] [--dry-run] [--workers N]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"
echo "Using canister ID : $CANISTER_ID"

python -m scripts.delete_snapshots --network $NETWORK_TYPE --canister-id $CANISTER_ID --canister-types $CANISTER_TYPES $DRY_RUN $WORKERS
