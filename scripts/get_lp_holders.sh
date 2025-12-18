#!/bin/bash

# Default pool is ICP/FUNNAI on ICPSwap
POOL="icp_funnai"

# Parse command line arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --pool)
            shift
            if [ "$1" = "icp_funnai" ]; then
                POOL=$1
            else
                echo "Invalid pool type: $1. Currently only 'icp_funnai' is supported."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --pool [icp_funnai]"
            exit 1
            ;;
    esac
done

echo "Fetching LP holders for pool: $POOL"

python -m scripts.get_lp_holders --pool $POOL
