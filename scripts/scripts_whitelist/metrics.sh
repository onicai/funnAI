#!/bin/bash

TOKEN="icp"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --token)
            shift
            if [ "$1" = "all" ] || [ "$1" = "icp" ] || [ "$1" = "funnai" ] || [ "$1" = "ckbtc" ] || [ "$1" = "iconfucius" ] ; then
                TOKEN=$1
            else
                echo "Invalid token type: $1. Use 'all' or 'icp' or 'funnai' or 'ckbtc' or 'iconfucius'."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --token [all|icp|funnai|ckbtc|iconfucius]"
            exit 1
            ;;
    esac
done

echo "Using token: $TOKEN"

while true; do
    echo "=========================="
    echo "Running metrics script for token: $TOKEN"
    python -m scripts.scripts_whitelist.metrics --token $TOKEN
    sleep 600
done
