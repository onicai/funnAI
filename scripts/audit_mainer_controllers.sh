#!/bin/bash

# Read-only fleet audit of ShareAgent mAIners: controllers, module hash, registration.
# Makes NO writes -- only `dfx canister info` (public read-state) and query calls.

NETWORK_TYPE="local"
WORKERS=""
LIMIT=""
CHECK_LLMS=""
SHARESERVICE=""
REFERENCE_HASH=""

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
        --workers)
            shift
            WORKERS="--workers $1"
            shift
            ;;
        --limit)
            shift
            LIMIT="--limit $1"
            shift
            ;;
        --check-llms)
            CHECK_LLMS="--check-llms"
            shift
            ;;
        --shareservice)
            shift
            SHARESERVICE="--shareservice $1"
            shift
            ;;
        --reference-hash)
            shift
            REFERENCE_HASH="--reference-hash $1"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--workers N] [--limit N] [--check-llms] [--shareservice CANISTER_ID] [--reference-hash HASH]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

python -m scripts.audit_mainer_controllers --network $NETWORK_TYPE $WORKERS $LIMIT $CHECK_LLMS $SHARESERVICE $REFERENCE_HASH
