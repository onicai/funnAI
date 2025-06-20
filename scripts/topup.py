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

def topup(canister_id, network, tc):
    """Top up using dfx for a given canister."""
    try:    
        print(f"Topup with {tc} T Cycles for canister {canister_id} on network {network}...")
        cycles = f"{int(tc)*1000000000000:_}"  # Convert T Cycles to Cycles (1 T Cycle = 10^12 Cycles)
        # print(f"cycles = {cycles}   (Cycles)")
        subprocess.run(
            ["dfx", "wallet", "--network", network, "send", canister_id, cycles],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to topup with {tc} T Cycles for canister {canister_id} on network {network}")

def main(network, canister_types, tc):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        topup(canister_id, network, tc)


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
    parser.add_argument(
        "--tc",
        default=2,
        help="Specify the amount of T Cycles to add (default: 2)",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types, args.tc)
