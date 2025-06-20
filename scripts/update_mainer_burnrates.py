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

def update_mainer_burnrate(canister_id, network, burnrate):
    """Update mainer burnrate using dfx for a given canister."""
    try:    
        print(f"Updating burnrate to {burnrate} for canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "call", canister_id, "updateAgentSettings", 
             f"(record {{cyclesBurnRate = variant {{\"{burnrate}\"}}; }})"],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to set burnrate to {burnrate} for canister {canister_id} on network {network}")

def main(network, burnrate):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "mainers")

    for name, canister_id in CANISTERS.items():
        if ("GAMESTATE" in name or "CREATOR" in name or "LLM" in name):
            continue

        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        update_mainer_burnrate(canister_id, network, burnrate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--burnrate",
        choices=["Low", "Mid", "High", "VeryHigh"],
        default="Low",
        help="Specify the burnrate to use (default: Low)",
    )
    args = parser.parse_args()
    main(args.network, args.burnrate)
