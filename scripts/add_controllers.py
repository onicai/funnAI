#!/usr/bin/env python3

import sys
import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import funnai_team  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Declared once in scripts/lib/funnai_team.py, and overridable with FUNNAI_CONTROLLERS,
# so the team list is not copy-pasted across the deploy scripts.
CONTROLLERS = funnai_team.controllers()

def add_controllers(canister_id, network):
    """Add controllers to a canister."""
    for controller in CONTROLLERS:
        try:    
            print(f"Adding controller {controller} to canister {canister_id} on network {network}...")
            subprocess.run(
                ["icp", "canister", "settings", "update", canister_id, "--add-controller", controller["principal"], "-e", network],
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
