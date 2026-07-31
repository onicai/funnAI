#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
import sys
from collections import defaultdict
from dotenv import dotenv_values
import json
import pandas as pd

from .monitor_common import get_canisters, ensure_log_dir, get_balance
from .get_mainers import get_mainers_for_user
from .ledgers.icp import get_usd_per_computed_xdr_from_cmc, icp_xdr_summary, get_cycle_burn_rate_from_ic_api

# Shared icp-cli helpers: unlike `dfx ... --output json`, icp-cli cannot decode a Candid
# response, so decoding happens here via icp-py-core.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

TARGET_CYCLES_BALANCE = 100_000_000_000_000

def main(network, user):
    print("----------------------------------------------")
    mainers = get_mainers_for_user(network, user)
    if not mainers or len(mainers) == 0:
        print(f"No mainers found for {user} on the specified network {network}.")
        return
    
    # Initialize counters
    total_cycles = 0
    total_paused = 0
    total_active = 0
    total_cycles_needed = 0
    
    try:
        for mainer in mainers:
            # Sanity check that it is a ShareAgent
            address = mainer.get('address', '')
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

            if address == "":
                print(f"Skipping canister, because the address is empty.")
                continue

            if canister_type == "ShareService":
                print(f"Skipping ShareService canister, because this is part of the protocol canisters: {address}")
                continue

            if canister_type != "ShareAgent":
                print(f"Skipping canister, because the canister_type is unknown : {canister_type}")
                continue

            # check if the canister is paused or active
            active = False
            cmd = ["icp", "canister", "call", address, "getIssueFlagsAdmin", "()", "-e", network]
            data = icp_helpers.call_argv(cmd)
            low_cycle_balance = data.get('Ok', {}).get('lowCycleBalance', None)
            if low_cycle_balance is None:
                print(f"ERROR 1: Unable to get issue flags for canister {address} on network {network}")
                print(f"  {' '.join(cmd)}")
                print(output)
                continue
            elif low_cycle_balance == False:
                active = True
                total_active += 1
                # print(f"Canister {address} is active")
            elif low_cycle_balance == True:
                total_paused += 1        
                # print(f"Canister {address} is paused")

            # get cycleBalance from getMainerStatisticsAdmin endpoint
            cmd = ["icp", "canister", "call", address, "getMainerStatisticsAdmin", "()", "-e", network]
            data = icp_helpers.call_argv(cmd)

            cycle_balance = int(data.get('Ok', {}).get('cycleBalance', 0))
            if cycle_balance > 0:
                total_cycles += cycle_balance
            else:
                print(f"ERROR: Unable to get cycleBalance for canister {address} on network {network}")
                print(f"  {' '.join(cmd)}")
                print(output)
                continue

            cycles_to_send = TARGET_CYCLES_BALANCE - cycle_balance

            if cycles_to_send > 0:
                total_cycles_needed += cycles_to_send
                # get cycleBalance from getMainerStatisticsAdmin endpoint
                cmd = ["icp", "canister", "call", icp_helpers.CYCLES_WALLET, "wallet_send",
                 f'(record {{ canister = principal "{address}"; amount = {str(f"{cycles_to_send}").replace("_","")} : nat64 }})',
                 "-e", network]
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                if output == "":
                    print(f"Successfully sent {cycles_to_send:_} cycles to canister {address}.")
                else:
                    print(f"ERROR: Unable to send cycles to canister {address} on network {network}")
                    print(f"  {' '.join(cmd)}")
                    print(output)
            else:
                print(f"Canister {address} has sufficient cycles ({cycle_balance:_} >= {TARGET_CYCLES_BALANCE:_}).")

    except subprocess.CalledProcessError as e:
        print(f"ERROR occured when calling the subprocess command.")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:\n", e.output)
        sys.exit(1)
    
    # Print summary
    print("\n----------------------------------------------")
    print(f"Summary for user {user} on network {network}:")
    print(f"Total mainers: {len(mainers)}")
    print(f"Active mainers: {total_active}")
    print(f"Paused mainers: {total_paused}")
    print(f"Total cycles across all mainers: {total_cycles:_}")
    print(f"Total cycles needed to reach target: {total_cycles_needed:_}")
    print(f"Target balance per mainer: {TARGET_CYCLES_BALANCE:_}")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--user",
        default="all",
        help="Specify the user for which to get mainers (default: 'all')",
    )
    args = parser.parse_args()
    main(args.network, args.user)
