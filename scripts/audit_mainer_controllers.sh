#!/bin/bash

# Read-only audit of mAIner controllers, module hashes and admin roles.
#
# Makes NO update calls to any funnAI/PoAIW canister: every GameState/mAIner call
# is forced with --query, and controllers come from `dfx canister info` (read_state).
# Safe to run against prd at any time.
#
# Exits non-zero if any mAIner is an ANOMALY, so it also works as a drift detector.

NETWORK_TYPE="local"
ALL=""
NUM=""
JSON_OUT=""

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
        --all)
            ALL="--all"
            shift
            ;;
        --num)
            shift
            NUM="--num $1"
            shift
            ;;
        --json)
            shift
            JSON_OUT="--json $1"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--all] [--num N] [--json FILE]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

python -m scripts.audit_mainer_controllers --network $NETWORK_TYPE $ALL $NUM $JSON_OUT
