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

def get_balance(canister_id, network):
    """Fetch cycles balance using dfx for a given canister."""
    try:
        output = subprocess.check_output(
            ["dfx", "canister", "status", canister_id, "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        # Extract balance from the output
        balance = None
        for line in output.split('\n'):
            if line.startswith('Balance:'):
                balance_string = line.split(':')[1].strip().split()[0]  
                balance = int(balance_string)
                break
        return balance
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to fetch balance for canister {canister_id} on network {network}")
        return []

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network)

    # Log directory (also relative to script location)
    LOG_DIR = os.path.join(SCRIPT_DIR, f"logs-{network}")
    BALANCE_LOG_FILE = os.path.join(LOG_DIR, "balance.log")
    PREVIOUS_LOGS = defaultdict(set)

    ensure_log_dir(LOG_DIR)

    # Clear common log file at start
    with open(BALANCE_LOG_FILE, "w"):
        pass

    print(f"Monitoring balance of {len(CANISTERS)} canisters on '{network}' network...")
    BALANCE_CHANGE_THRESHOLD = 1_000_000_000
    
    balances = {name: None for name in CANISTERS.keys()} 
    initial_balances = {name: None for name in CANISTERS.keys()} 
    max_name_length = max(len(name) for name in CANISTERS.keys())
    timer = 0
    delay = 10  # seconds  
    while True:
        for name, canister_id in CANISTERS.items():
            balance = get_balance(canister_id, network)

            if balance is None:
                print(f"{CANISTER_COLORS[name]}[{name}]{RESET_COLOR}({canister_id}) ERROR: Unable to fetch balance")
                continue

            previous_balance = balances[name]
            if previous_balance is not None:
                if abs(balance - previous_balance) < BALANCE_CHANGE_THRESHOLD:
                    continue

            if initial_balances[name] is None:
                # First time we see this canister, log its initial balance
                initial_balances[name] = balance

            # Ok, we have a significant change in balance and will log it
            balances[name] = balance
            with open(BALANCE_LOG_FILE, "a") as f:
                line = f" {balance:>20_} "
                if previous_balance is not None:
                    change = balance - (previous_balance or 0)
                    change_from_initial = balance - (initial_balances[name] or 0)
                    line += f"(Δ: {change:>+20_} | total Δ: {change_from_initial:>+20_}) "
                f.write(line + "\n")
                print(f"{CANISTER_COLORS[name]}[{name:{max_name_length}}]{timer:10,}s: {line}{RESET_COLOR}")
        
        if timer == 0:
            print(f"\nInitial balance check completed for {len(CANISTERS)} canisters on '{network}' network.")
            print(f"Will report changes in balance of {BALANCE_CHANGE_THRESHOLD:_} Cycles. Checking every {delay} seconds...")

        time.sleep(delay)
        timer += delay

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
