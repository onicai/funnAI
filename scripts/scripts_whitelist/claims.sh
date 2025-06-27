#!/bin/bash

CATEGORY="all"

# Parse command line arguments for network type
while [ $# -gt 0 ]; do
    case "$1" in
        --category)
            shift
            if [ "$1" = "all" ] || [ "$1" = "kongswap" ] || [ "$1" = "bioniq" ] || [ "$1" = "odin" ] ; then
                CATEGORY=$1
            else
                echo "Invalid category type: $1. Use 'all' or 'kongswap' or 'bioniq' or 'odin'."
                exit 1
            fi
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 --category [all|kongswap|bioniq|odin]"
            exit 1
            ;;
    esac
done

echo "Using category: $CATEGORY"

python -m scripts.scripts_whitelist.claims --category $CATEGORY
