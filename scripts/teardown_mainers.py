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

def teardown_mainer(canister_id, network):
    """Teardown mainer using dfx."""
    try:    
        print(f"Stopping canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "stop", canister_id],
            check=True,
            text=True
        )

        print(f"Deleting canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "delete", canister_id],
            check=True,
            text=True
        )

    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to stop canister {canister_id} on network {network}")

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "mainers")

    for name, canister_id in CANISTERS.items():
        if ("GAMESTATE" in name or "CREATOR" in name or "LLM" in name):
            continue

        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        teardown_mainer(canister_id, network)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
