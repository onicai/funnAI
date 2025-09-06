#!/bin/bash

# Default network type is local
NETWORK_TYPE="prd"

# Default is the principal of the IConfucius funnai account
USER="xijdk-rtoet-smgxl-a4apd-ahchq-bslha-ope4a-zlpaw-ldxat-prh6f-jqe"

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
            USER=$1  
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--user principal]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

echo "Funding all mainers on network: $NETWORK_TYPE for user: $USER"
python -m scripts.fund_mainers --network $NETWORK_TYPE --user $USER

