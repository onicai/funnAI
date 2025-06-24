#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
NUMBER=1

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
        --number)
            shift
            if [[ "$1" =~ ^[0-9]+$ ]]; then
                NUMBER="$1"
            else
                echo "Invalid number: $1. Must be a positive integer."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd]"
            exit 1
            ;;
    esac
done

echo "Deploying $NUMBER mAIners to network: $NETWORK_TYPE"

for ((i=1; i<=NUMBER; i++)); do
    echo "----------------------------------------"
    echo "Deploying mAIner $i of $NUMBER"
    scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh --mode install --network "$NETWORK_TYPE"
done
