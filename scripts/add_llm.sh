#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
CANISTER_ID=""
LLM_TYPE=""
DRY_RUN=""

# Parse command line arguments
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
        --llm-type)
            shift
            if [ "$1" = "challenger" ] || [ "$1" = "judge" ] || [ "$1" = "share_service" ]; then
                LLM_TYPE=$1
            else
                echo "Invalid LLM type: $1. Use 'challenger' or 'judge' or 'share_service'."
                exit 1
            fi
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --canister-id CANISTER_ID --llm-type [challenger|judge|share_service] [--dry-run]"
            exit 1
            ;;
    esac
done

if [ -z "$CANISTER_ID" ]; then
    echo "ERROR: --canister-id is required."
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --canister-id CANISTER_ID --llm-type [challenger|judge|share_service] [--dry-run]"
    exit 1
fi

if [ -z "$LLM_TYPE" ]; then
    echo "ERROR: --llm-type is required."
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --canister-id CANISTER_ID --llm-type [challenger|judge|share_service] [--dry-run]"
    exit 1
fi

echo "Using network type: $NETWORK_TYPE"
echo "Using canister ID : $CANISTER_ID"
echo "Using LLM type    : $LLM_TYPE"
if [ -n "$DRY_RUN" ]; then
    echo "DRY RUN mode      : enabled"
fi

python -m scripts.add_llm --network $NETWORK_TYPE --canister-id $CANISTER_ID --llm-type $LLM_TYPE $DRY_RUN
