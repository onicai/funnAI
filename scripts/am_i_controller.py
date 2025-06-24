#!/usr/bin/env python3

import sys
import subprocess
import json
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def am_i_controller(canister_id, network, my_principal):
    """List controllers using dfx for a given canister."""
    try:
        # --------------------------------
        # Get canister info
        # print(f"Getting all controllers for canister {canister_id} on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "--network", network, "info", canister_id],
            stderr=subprocess.DEVNULL,
            text=True
        )
        # Check if my principal is in the controllers list
        if my_principal in result:
            print(f"✓")
        else:
            print(f"✗ You are NOT a controller of canister {canister_id}")
            print(f"information on canister:\n{result}")
            sys.exit(1)
        
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to list controllers for canister {canister_id} on network {network}")

def main(network, canister_types):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    # --------------------------------
    # Get my principal ID
    my_identity = subprocess.check_output(
        ["dfx", "identity", "whoami"],
        text=True
    ).strip()
    my_principal = subprocess.check_output(
        ["dfx", "identity", "get-principal"],
        text=True
    ).strip()

    print(f"Your identity: {my_identity}")
    print(f"Your principal ID: {my_principal}")
    print(f"Checking if you are a controller of {len(CANISTERS)} canisters on '{network}' network...")
    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        am_i_controller(canister_id, network, my_principal)

    print("All checks completed. You are a controller for all canisters listed above.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add controllers.")
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
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types)
