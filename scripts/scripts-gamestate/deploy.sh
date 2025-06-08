#!/bin/bash

#######################################################################
# run from parent folder as:
# scripts/scripts-gamestate/deploy.sh --network [local|ic]
#######################################################################

# Default network type is local
NETWORK_TYPE="local"
DEPLOY_MODE="install"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --network)
            shift
            if [ "$1" = "local" ] || [ "$1" = "ic" ] || [ "$1" = "testing" ] || [ "$1" = "development" ] || [ "$1" = "demo" ]; then
                NETWORK_TYPE=$1
            else
                echo "Invalid network type: $1. Use 'local' or 'ic' or 'testing' or 'development' or 'demo'."
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
            echo "Usage: $0 --network [local|ic|testing]"
            exit 1
            ;;
    esac
done

# WARNING: when updating here, also update in scripts/scripts-gamestate/deploy-mainers-ShareService-LLMs-via-gamestate.sh
if [ "$NETWORK_TYPE" = "ic" ]; then
    SUBNET_GAME_STATE="csyj4-zmann-ys6ge-3kzi6-onexi-obayx-2fvak-zersm-euci4-6pslt-lae"
    SUBNET_SHARE_AGENT_CTRL="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae" # All share agents are on the same subnet
    SUBNET_SHARE_SERVICE_CTRL="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae"
    SUBNET_SHARE_SERVICE_LLM="qxesv-zoxpm-vc64m-zxguk-5sj74-35vrb-tbgwg-pcird-5gr26-62oxl-cae" # LLMs 0,1,2 - overwritten by the LLMs deployment script
elif [ "$NETWORK_TYPE" = "testing" ]; then
    SUBNET_GAME_STATE="csyj4-zmann-ys6ge-3kzi6-onexi-obayx-2fvak-zersm-euci4-6pslt-lae"
    SUBNET_SHARE_AGENT_CTRL="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae" # All share agents are on the same subnet
    SUBNET_SHARE_SERVICE_CTRL="w4asl-4nmyj-qnr7c-6cqq4-tkwmt-o26di-iupkq-vx4kt-asbrx-jzuxh-4ae"
    SUBNET_SHARE_SERVICE_LLM="qxesv-zoxpm-vc64m-zxguk-5sj74-35vrb-tbgwg-pcird-5gr26-62oxl-cae" # LLMs 0,1,2 - overwritten by the LLMs deployment script
elif [ "$NETWORK_TYPE" = "development" ]; then
    SUBNET_GAME_STATE="none"  # TODO
    SUBNET_SHARE_AGENT_CTRL="none"  # TODO
    SUBNET_SHARE_SERVICE_CTRL="none"  # TODO
    SUBNET_SHARE_SERVICE_LLM="none"  # TODO
else
    SUBNET_GAME_STATE="none"  
    SUBNET_SHARE_AGENT_CTRL="none"
    SUBNET_SHARE_SERVICE_CTRL="none"  # No specific subnet for local
    SUBNET_SHARE_SERVICE_LLM="none"  # No specific subnet for local
fi

echo "Using network type : $NETWORK_TYPE"
echo "Deploying to subnet: $SUBNET_GAME_STATE"

echo "We are going to   : $DEPLOY_MODE"

# Check if user wants to reinstall and confirm
if [ "$DEPLOY_MODE" = "reinstall" ]; then
    echo " "
    echo "WARNING: You are about to reinstall the GameState. You will lose all persistent data."
    echo "Are you really sure you want to reinstall the GameState? (y/N)"
    read -r confirmation
    if [ "$confirmation" != "y" ] && [ "$confirmation" != "Y" ]; then
        echo "Reinstall cancelled."
        exit 1
    fi
fi

#######################################################################

echo " "
echo "--------------------------------------------------"
echo "Deploying the game_state_canister"

if [ "$NETWORK_TYPE" = "ic" ] || [ "$NETWORK_TYPE" = "testing" ]; then
    if [ "$SUBNET_GAME_STATE" = "none" ]; then
        dfx deploy game_state_canister --mode $DEPLOY_MODE --yes --network $NETWORK_TYPE
    else
        dfx deploy game_state_canister --mode $DEPLOY_MODE --yes --network $NETWORK_TYPE --subnet $SUBNET_GAME_STATE
    fi
else
    dfx deploy game_state_canister --mode $DEPLOY_MODE --yes --network $NETWORK_TYPE
fi

echo " "
echo "--------------------------------------------------"
echo "Checking health endpoint"
output=$(dfx canister call game_state_canister health --network $NETWORK_TYPE)

if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
    echo "game_state_canister is not healthy. Exiting."
    exit 1
else
    echo "game_state_canister is healthy."
fi

echo " "
echo "--------------------------------------------------"
echo "Calling setSubnetsAdmin to set the mAIner subnets"
dfx canister call game_state_canister setSubnetsAdmin "(record {subnetShareAgentCtrl = \"$SUBNET_SHARE_AGENT_CTRL\"; subnetShareServiceCtrl = \"$SUBNET_SHARE_SERVICE_CTRL\"; subnetShareServiceLlm = \"$SUBNET_SHARE_SERVICE_LLM\";})" --network $NETWORK_TYPE

echo " "
echo "--------------------------------------------------"
echo "Calling getSubnetsAdmin to get the mAIner subnets"
dfx canister call game_state_canister getSubnetsAdmin  --network $NETWORK_TYPE

echo " "
echo "--------------------------------------------------"
echo "Calling setCyclesFlowAdmin to calculate the CyclesFlow variables"
dfx canister call game_state_canister setCyclesFlowAdmin '(record {})' --network $NETWORK_TYPE

if [ "$DEPLOY_MODE" != "upgrade" ]; then
    echo " "
    echo "--------------------------------------------------"
    echo "Setting initial challenge topics"
    output=$(dfx canister call game_state_canister setInitialChallengeTopics --network $NETWORK_TYPE)

    if [ "$output" != "(variant { Ok = record { status_code = 200 : nat16 } })" ]; then
        echo "setInitialChallengeTopics failed. Exiting."
        exit 1
    else
        echo "setInitialChallengeTopics successfull."
    fi
fi

echo " "
echo "--------------------------------------------------"
echo "Generating bindings for a frontend"
dfx generate game_state_canister