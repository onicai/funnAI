#!/bin/bash

# Top up a mAIner through the protocol's OFFICIAL ICP flow.
#
# Unlike `dfx wallet send` (IC0.deposit_cycles), this credits officialCyclesBalance,
# so it does NOT trigger the 90% unofficial-topup penalty on the mAIner's next
# submission. See scripts/official_topup.py for the full explanation.

NETWORK_TYPE="local"
MAINER=""
ICP=""
TARGET=""
IDENTITY=""
DRY_RUN=""

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
        --mainer)
            shift
            MAINER="--mainer $1"
            shift
            ;;
        --icp)
            shift
            ICP="--icp $1"
            shift
            ;;
        --target-spendable)
            shift
            TARGET="--target-spendable $1"
            shift
            ;;
        --identity)
            shift
            IDENTITY="--identity $1"
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --mainer <canister-id> [--icp N] [--target-spendable N] [--identity NAME] [--dry-run]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

python -m scripts.official_topup --network $NETWORK_TYPE $MAINER $ICP $TARGET $IDENTITY $DRY_RUN
