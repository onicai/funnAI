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

def list_controllers(canister_id, network):
    """List controllers using dfx for a given canister."""
    try:    
        print(f"Listing all controllers for canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "info", canister_id],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to list controllers for canister {canister_id} on network {network}")

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network)

    print(f"Listing controllers of {len(CANISTERS)} canisters on '{network}' network...")
    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        list_controllers(canister_id, network)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add controllers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
