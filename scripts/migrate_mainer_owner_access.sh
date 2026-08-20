#!/bin/bash

# Grant mAIner owners #AdminQuery and remove them as canister controllers.
#
# Run this ONLY after the new mAIner wasm (with the updateAgentSettings ownership
# check) has been deployed to every mAIner. See README-remove-owner-as-controller.md

NETWORK_TYPE="local"
NUM=""
DRY_RUN=""
TARGET_HASH=""

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
        --num)
            shift
            NUM="--num $1"
            shift
            ;;
        --target-hash)
            shift
            TARGET_HASH="--target-hash $1"
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --target-hash 0xHASH [--num N] [--dry-run]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

python -m scripts.migrate_mainer_owner_access --network $NETWORK_TYPE $TARGET_HASH $NUM $DRY_RUN
