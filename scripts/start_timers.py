#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def start_timer(canister_id, network):
    """Start timer using dfx for a given canister."""
    try:    
        print(f"Starting timer for canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "call", canister_id, "startTimerExecutionAdmin"],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to start timer for canister {canister_id} on network {network}")

def main(network, canister_types):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    for name, canister_id in CANISTERS.items():
        if ("GAMESTATE" in name or "CREATOR" in name or "LLM" in name):
            continue
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        start_timer(canister_id, network)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-types",
        choices=["all", "protocol", "mainers"],
        default="protocol",
        help="Specify the canister type (default: protocol)",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types)
