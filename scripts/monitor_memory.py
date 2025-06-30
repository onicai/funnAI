#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir
from datetime import datetime, timezone

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_memory(canister_id, network):
    """Fetch memory using dfx for a given canister."""
    try:
        output = subprocess.check_output(
            ["dfx", "canister", "status", canister_id, "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        # Extract memory from the output
        memory = None
        for line in output.split('\n'):
            if line.startswith('Memory Size:'):
                balance_string = line.split(':')[1].strip().split()[0]  
                memory = int(balance_string)
                break
        return memory
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to fetch memory for canister {canister_id} on network {network}")
        return []

def main(network, canister_types):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    # Log directory (also relative to script location)
    LOG_DIR = os.path.join(SCRIPT_DIR, f"logs-{network}")
    MEMORY_LOG_FILE = os.path.join(LOG_DIR, "memory.log")
    PREVIOUS_LOGS = defaultdict(set)

    ensure_log_dir(LOG_DIR)

    # Clear common log file at start
    with open(MEMORY_LOG_FILE, "w"):
        pass

    print(f"Monitoring memory of {len(CANISTERS)} canisters on '{network}' network...")
    MEMORY_CHANGE_THRESHOLD = 100_000_000
    
    values = {name: None for name in CANISTERS.keys()} 
    initial_values = {name: None for name in CANISTERS.keys()} 
    max_name_length = max(len(name) for name in CANISTERS.keys())
    delay = 5 * 60  # 5 minutes
    first = True
    while True:
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        for name, canister_id in CANISTERS.items():
            memory = get_memory(canister_id, network)

            if memory is None:
                print(f"{CANISTER_COLORS[name]}[{name}]{RESET_COLOR}({canister_id}) ERROR: Unable to fetch memory")
                continue

            previous_value = values[name]
            if previous_value is not None:
                if abs(memory - previous_value) < MEMORY_CHANGE_THRESHOLD:
                    continue

            if initial_values[name] is None:
                # First time we see this canister, log its initial memory
                initial_values[name] = memory

            # Ok, we have a significant change in memory and will log it
            values[name] = memory
            with open(MEMORY_LOG_FILE, "a") as f:
                line = f" {memory:>20_} "
                if previous_value is not None:
                    change = memory - (previous_value or 0)
                    change_from_initial = memory - (initial_values[name] or 0)
                    line += f"(Δ: {change:>+20_} | total Δ: {change_from_initial:>+20_}) "
                f.write(line + "\n")
                print(f"{CANISTER_COLORS[name]}[{name:{max_name_length}}][{current_time}]: {line}{RESET_COLOR}")
        
        if first:
            first = False
            print(f"\nInitial memory check completed for {len(CANISTERS)} canisters on '{network}' network.")
            print(f"Will report changes in memory of {MEMORY_CHANGE_THRESHOLD:_} Bytes. Checking every {delay} seconds...")

        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
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
