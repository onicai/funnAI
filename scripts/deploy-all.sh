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
            if [ "$1" = "local" ] || [ "$1" = "ic" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic'."
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
            echo "Usage: $0 --network [local|ic]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

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

# WE NO LONGER DEPLOY mAIners from this script. See README for details