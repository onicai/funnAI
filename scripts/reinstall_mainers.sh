#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"

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
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] --burnrate [Low|Mid|High|VeryHigh]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

echo " "
read -p "Are you sure you want to reinstall all the mAIners? This will OVERWRITE all the data and code in the canisters. (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reinstall cancelled."
    exit 1
fi

python -m scripts.reinstall_mainers --network $NETWORK_TYPE
