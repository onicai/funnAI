#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/deploy-all.sh --mode [install/reinstall/upgrade] [--network ic]
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

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
        --mode)
            shift
            if [ "$1" = "install" ] || [ "$1" = "reinstall" ] || [ "$1" = "upgrade" ]; then
                DEPLOY_MODE=$1
            else
                echo "Invalid mode: $1. Use 'install', 'reinstall' or 'upgrade'."
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

echo "Using network type: $NETWORK_TYPE"
echo "We are going to   : $DEPLOY_MODE"

# Check if user wants to reinstall and confirm
if [ "$DEPLOY_MODE" = "reinstall" ]; then
    echo " "
    echo "WARNING: You are about to reinstall the canisters. You will lose all persistent data."
    echo "Are you sure you want to reinstall? (y/N)"
    read -r confirmation
    if [ "$confirmation" != "y" ] && [ "$confirmation" != "Y" ]; then
        echo "Reinstall cancelled."
        exit 1
    fi
fi

#######################################################################
# From funnAI folder
echo "scripts-gamestate deploy.sh"
scripts/scripts-gamestate/deploy.sh --network $NETWORK_TYPE --mode $DEPLOY_MODE

# Deploy the core Protocol canisters
cd PoAIW
scripts/deploy-mainer-creator.sh     --network $NETWORK_TYPE --mode $DEPLOY_MODE
scripts/deploy-challenger.sh --network $NETWORK_TYPE --mode $DEPLOY_MODE
scripts/deploy-judge.sh      --network $NETWORK_TYPE --mode $DEPLOY_MODE

# Register them with the GameState
# From folder funnAI:
cd ../
scripts/scripts-gamestate/register-all.sh --network $NETWORK_TYPE

echo " "
echo "--------------------------------------------------"
echo "Calling getCyclesFlowAdmin to get the current CyclesFlow variables"
dfx canister call game_state_canister getCyclesFlowAdmin --network $NETWORK_TYPE

# WE NO LONGER DEPLOY mAIners from this script. See README for details