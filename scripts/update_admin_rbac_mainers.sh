#!/bin/bash

# Default values
NETWORK_TYPE=""
PRINCIPAL=""
ACTION="assign"
DRY_RUN=""

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
        --principal)
            shift
            PRINCIPAL=$1
            shift
            ;;
        --action)
            shift
            if [ "$1" = "assign" ] || [ "$1" = "revoke" ]; then
                ACTION=$1
            else
                echo "Invalid action: $1. Use 'assign' or 'revoke'."
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
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --principal PRINCIPAL [--action assign|revoke] [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --network NETWORK       Required. Network to update admin RBAC on"
            echo "  --principal PRINCIPAL   Required. Principal ID to assign/revoke AdminQuery role"
            echo "  --action ACTION         Optional. Action to perform: 'assign' or 'revoke' (default: assign)"
            echo "  --dry-run               Optional. Run in dry-run mode without making changes"
            exit 1
            ;;
    esac
done

# Check if network is provided
if [ -z "$NETWORK_TYPE" ]; then
    echo "Error: --network is required"
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --principal PRINCIPAL [--action assign|revoke] [--dry-run]"
    exit 1
fi

# Check if principal is provided
if [ -z "$PRINCIPAL" ]; then
    echo "Error: --principal is required"
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --principal PRINCIPAL [--action assign|revoke] [--dry-run]"
    exit 1
fi

# Build the Python command with arguments
PYTHON_CMD="python -m scripts.update_admin_rbac_mainers --network $NETWORK_TYPE --principal $PRINCIPAL --action $ACTION"

if [ ! -z "$DRY_RUN" ]; then
    PYTHON_CMD="$PYTHON_CMD $DRY_RUN"
fi

echo "Executing: $PYTHON_CMD"
echo ""

# Execute the Python script
$PYTHON_CMD
