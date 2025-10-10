#!/bin/bash

# Default values
NETWORK_TYPE=""
TARGET_HASH=""
NUM_MAINERS=""
SPECIFIC_MAINER=""
USER_PRINCIPAL=""
DRY_RUN=""
SKIP_PREPARATION=""
ASK_BEFORE_UPGRADE=""
REVERSE=""

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ] || [ "$1" = "development" ] || [ "$1" = "demo" ] || [ "$1" = "prd" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local', 'ic', 'testing', 'development', 'demo', or 'prd'."
                exit 1
            fi
            shift
            ;;
        --target-hash)
            shift
            TARGET_HASH=$1
            shift
            ;;
        --num)
            shift
            NUM_MAINERS=$1
            shift
            ;;
        --mainer)
            shift
            SPECIFIC_MAINER=$1
            shift
            ;;
        --user)
            shift
            USER_PRINCIPAL=$1
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --skip-preparation)
            SKIP_PREPARATION="--skip-preparation"
            shift
            ;;
        --ask-before-upgrade)
            ASK_BEFORE_UPGRADE="--ask-before-upgrade"
            shift
            ;;
        --reverse)
            REVERSE="--reverse"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--target-hash HASH] [--num NUM] [--mainer CANISTER_ID] [--user PRINCIPAL] [--dry-run] [--skip-preparation] [--ask-before-upgrade] [--reverse]"
            echo ""
            echo "Options:"
            echo "  --network NETWORK       Required. Network to upgrade mainers on"
            echo "  --target-hash HASH      Optional. Target wasm hash to upgrade to (from 'dfx canister info <canister_id>')"
            echo "  --num NUM               Optional. Number of mAIners to upgrade"
            echo "  --mainer CANISTER_ID    Optional. Specific mAIner canister to upgrade"
            echo "  --user PRINCIPAL        Optional. Principal ID of user whose mAIners to upgrade"
            echo "  --dry-run               Optional. Run in dry-run mode without making changes"
            echo "  --skip-preparation      Optional. Skip Step 1 preparation"
            echo "  --ask-before-upgrade    Optional. Ask for confirmation before upgrading each canister"
            echo "  --reverse               Optional. Process mainers in reverse order"
            exit 1
            ;;
    esac
done

# Check if network is provided
if [ -z "$NETWORK_TYPE" ]; then
    echo "Error: --network is required"
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [options]"
    exit 1
fi

# Build the Python command with arguments
PYTHON_CMD="python -m scripts.upgrade_mainers --network $NETWORK_TYPE"

if [ ! -z "$TARGET_HASH" ]; then
    PYTHON_CMD="$PYTHON_CMD --target-hash $TARGET_HASH"
fi

if [ ! -z "$NUM_MAINERS" ]; then
    PYTHON_CMD="$PYTHON_CMD --num $NUM_MAINERS"
fi

if [ ! -z "$SPECIFIC_MAINER" ]; then
    PYTHON_CMD="$PYTHON_CMD --mainer $SPECIFIC_MAINER"
fi

if [ ! -z "$USER_PRINCIPAL" ]; then
    PYTHON_CMD="$PYTHON_CMD --user $USER_PRINCIPAL"
fi

if [ ! -z "$DRY_RUN" ]; then
    PYTHON_CMD="$PYTHON_CMD $DRY_RUN"
fi

if [ ! -z "$SKIP_PREPARATION" ]; then
    PYTHON_CMD="$PYTHON_CMD $SKIP_PREPARATION"
fi

if [ ! -z "$ASK_BEFORE_UPGRADE" ]; then
    PYTHON_CMD="$PYTHON_CMD $ASK_BEFORE_UPGRADE"
fi

if [ ! -z "$REVERSE" ]; then
    PYTHON_CMD="$PYTHON_CMD $REVERSE"
fi

echo "Executing: $PYTHON_CMD"
echo ""

# Execute the Python script
$PYTHON_CMD