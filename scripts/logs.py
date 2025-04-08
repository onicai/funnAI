#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Load CANISTER_NAME=ID pairs from .env file located in the script's directory
ENV_PATH = os.path.join(SCRIPT_DIR, "canister_ids.env")
env_config = dotenv_values(ENV_PATH)
CANISTERS = {key: value.strip('"') for key, value in env_config.items() if value}

# Log directory (also relative to script location)
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
COMMON_LOG_FILE = os.path.join(LOG_DIR, "combined_logs.log")
PREVIOUS_LOGS = defaultdict(set)

def ensure_log_dir():
    """Ensure the logs directory exists."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created log directory: {LOG_DIR}")

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

def main(network):
    ensure_log_dir()

    # Clear common log file at start
    with open(COMMON_LOG_FILE, "w"):
        pass

    print(f"Monitoring {len(CANISTERS)} canisters on '{network}' network...")
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
                        print(line)

        time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
