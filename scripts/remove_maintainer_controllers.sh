#!/bin/bash

# Make the mAInerCreator the sole controller of every mAIner ShareAgent: set the two
# maintainer principals as log viewers, then remove them as controllers.
#
# See the module docstring in remove_maintainer_controllers.py

NETWORK_TYPE="local"
NUM=""
MAINER=""
DRY_RUN=""
TARGET_HASH=""
CREATOR_HASH=""

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
        --mainer)
            shift
            MAINER="--mainer $1"
            shift
            ;;
        --target-hash)
            shift
            TARGET_HASH="--target-hash $1"
            shift
            ;;
        --creator-hash)
            shift
            CREATOR_HASH="--creator-hash $1"
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --target-hash 0xHASH [--creator-hash 0xHASH] [--mainer CANISTER_ID] [--num N] [--dry-run]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

python -m scripts.remove_maintainer_controllers --network $NETWORK_TYPE $TARGET_HASH $CREATOR_HASH $MAINER $NUM $DRY_RUN
