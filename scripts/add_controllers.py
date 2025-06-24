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

CONTROLLERS = [
    {
        "name" : "patrick",
        "principal" : "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"
    },
    {
        "name" : "arjaan",
        "principal" : "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"
    } 
]

def add_controllers(canister_id, network):
    """Add controllers using dfx for a given canister."""
    for controller in CONTROLLERS:
        try:    
            print(f"Adding controller {controller} to canister {canister_id} on network {network}...")
            subprocess.run(
                ["dfx", "canister", "--network", network, "update-settings", canister_id, "--add-controller", controller["principal"]],
                check=True,
                text=True
            )
        except subprocess.CalledProcessError:
            print(f"ERROR: Unable to add controller {controller} for canister {canister_id} on network {network}")

def main(network, canister_types):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    print(f"Updating controllers of {len(CANISTERS)} canisters on '{network}' network...")
    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        add_controllers(canister_id, network)

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
