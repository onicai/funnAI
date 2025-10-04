#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
USER_PRINCIPAL=""

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
        --user)
            shift
            USER_PRINCIPAL=$1
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --user [PRINCIPAL_ID]"
            exit 1
            ;;
    esac
done

if [ -z "$USER_PRINCIPAL" ]; then
    echo "Error: --user parameter is required"
    echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --user [PRINCIPAL_ID]"
    exit 1
fi

echo "Using network type: $NETWORK_TYPE"
echo "Using user principal: $USER_PRINCIPAL"

python -m scripts.check_failed_topups --network $NETWORK_TYPE --user $USER_PRINCIPAL