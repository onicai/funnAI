#!/usr/bin/env python3

import subprocess
import sys
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir, MAINTAINER_PRINCIPALS

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def add_controllers(canister_id, network, principals, dry_run):
    """Add controllers using dfx for a given canister. Returns the number of failures."""
    failures = 0
    for principal in principals:
        cmd = ["dfx", "canister", "--network", network, "update-settings", canister_id, "--add-controller", principal]
        if dry_run:
            print(f"DRY RUN: {' '.join(cmd)}")
            continue
        try:
            print(f"Adding controller {principal} to canister {canister_id} on network {network}...")
            subprocess.run(cmd, check=True, text=True)
        except subprocess.CalledProcessError:
            print(f"ERROR: Unable to add controller {principal} for canister {canister_id} on network {network}")
            failures += 1
    return failures

def main(network, canister_types, principals, dry_run):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    print(f"Adding {principals} as controllers of {len(CANISTERS)} canisters on '{network}' network...")
    failures = 0
    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        failures += add_controllers(canister_id, network, principals, dry_run)
    if failures:
        print(f"ERROR: {failures} controller addition(s) failed")
        sys.exit(1)

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
    parser.add_argument(
        "--principal",
        action="append",
        help="Controller to add; repeat for several (default: the 2 maintainer principals)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    main(args.network, args.canister_types, args.principal or MAINTAINER_PRINCIPALS, args.dry_run)
