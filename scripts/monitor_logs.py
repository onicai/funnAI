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

def get_logs(canister_id, network):
    """Fetch logs using dfx for a given canister."""
    try:
        output = subprocess.check_output(
            ["dfx", "canister", "logs", canister_id, "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        return output.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def main(network, canister_types):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    # Log directory (also relative to script location)
    LOG_DIR = os.path.join(SCRIPT_DIR, f"logs-{network}")
    COMMON_LOG_FILE = os.path.join(LOG_DIR, "combined_logs.log")
    PREVIOUS_LOGS = defaultdict(set)

    ensure_log_dir(LOG_DIR)

    # Clear common log file at start
    with open(COMMON_LOG_FILE, "w"):
        pass

    print(f"Retrieving logs for {len(CANISTERS)} canisters on '{network}' network...")
    timer = 0
    delay = 3  # seconds  
    while True:
        for name, canister_id in CANISTERS.items():
            new_lines = []
            log_lines = get_logs(canister_id, network)
            for line in log_lines:
                if line not in PREVIOUS_LOGS[name]:
                    PREVIOUS_LOGS[name].add(line)
                    new_lines.append(line)

            if new_lines:
                individual_log_path = os.path.join(LOG_DIR, f"{name}.log")
                with open(individual_log_path, "a") as f_individual, open(COMMON_LOG_FILE, "a") as f_common:
                    for line in new_lines:
                        f_individual.write(line + "\n")
                        f_common.write(line + "\n")
                        # print(line)
                        print(f"{CANISTER_COLORS[name]}[{name}]{RESET_COLOR}({canister_id}) {line}")
        
        if timer == 0:
            print(f"\nInitial log retrieval completed for {len(CANISTERS)} canisters on '{network}' network.")
            print(f"Will report changes in logs. Checking every {delay} seconds...")

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
    parser.add_argument(
        "--canister-types",
        choices=["all", "protocol", "mainers"],
        default="protocol",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types)
