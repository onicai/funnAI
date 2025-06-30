#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
LOOP="false"
LOOP_DELAY=0
USER="all"

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
        --loop)
            LOOP="true"
            shift
            LOOP_DELAY=$1  # Default loop delay
            shift
            ;;
        --user)
            shift
            USER=$1  # "all" or a specific principal"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--loop [delay]] [--user principal]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

if [ "$LOOP" = "true" ]; then
    echo "Running in loop mode with a delay of $LOOP_DELAY seconds."
    while true; do
        echo "Fetching mainers on network: $NETWORK_TYPE for user: $USER"
        python -m scripts.get_mainers --network $NETWORK_TYPE --user $USER
        sleep $LOOP_DELAY
    done
fi

echo "Fetching mainers on network: $NETWORK_TYPE for user: $USER"USER
python -m scripts.get_mainers --network $NETWORK_TYPE --user $USER

