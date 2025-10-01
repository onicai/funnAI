#!/bin/bash

# Default values
NETWORK_TYPE="local"
TX_TYPE="burn"

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
        --type)
            shift
            if [ "$1" = "burn" ] || [ "$1" = "mint" ]; then
                TX_TYPE=$1
            else
                echo "Invalid transaction type: $1. Use 'burn' or 'mint'."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --type [burn|mint]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"
echo "Transaction type: $TX_TYPE"

python -m scripts.calculate_token_transactions --network $NETWORK_TYPE --type $TX_TYPE