#!/bin/bash

# Default network type is local
NETWORK_TYPE="local"
LOOP="false"
LOOP_DELAY=0
USER="all"
SKIP_POAIW_UPDATE=""
DAILY_METRICS=""
LIMIT=""
STATISTICS=""

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
        --skip-poaiw-update)
            SKIP_POAIW_UPDATE="--skip-poaiw-update"
            shift
            ;;
        --daily-metrics)
            DAILY_METRICS="--daily-metrics"
            shift
            ;;
        --limit)
            shift
            LIMIT="--limit $1"
            shift
            ;;
        --statistics)
            STATISTICS="--statistics"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --network [local|ic|testing|development|demo|prd] [--loop [delay]] [--user principal] [--skip-poaiw-update] [--daily-metrics] [--limit N] [--statistics]"
            exit 1
            ;;
    esac
done

echo "Using network type: $NETWORK_TYPE"

if [ "$LOOP" = "true" ]; then
    echo "Running in loop mode with a delay of $LOOP_DELAY seconds."
    while true; do
        python -m scripts.get_mainers --network $NETWORK_TYPE --user $USER $SKIP_POAIW_UPDATE $DAILY_METRICS $LIMIT $STATISTICS
        sleep $LOOP_DELAY
    done
fi

python -m scripts.get_mainers --network $NETWORK_TYPE --user $USER $SKIP_POAIW_UPDATE $DAILY_METRICS $LIMIT $STATISTICS

# If statistics flag is set, automatically run the analysis script
if [ -n "$STATISTICS" ]; then
    echo ""
    echo "----------------------------------------------"
    echo "Running mAIners analysis..."
    echo "----------------------------------------------"
    python -m scripts.get_mainers_analysis --network $NETWORK_TYPE
fi

