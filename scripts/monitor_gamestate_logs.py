#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values
import json

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

def get_data(canister_id, network):
    """Fetch data from gamestate using dfx."""
    try:
        output = "\n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumArchivedChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumArchivedChallengesAdmin               = {data.get('Ok')} \n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumClosedChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumClosedChallengesAdmin                 = {data.get('Ok')} \n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumScoredChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumScoredChallengesAdmin                 = {data.get('Ok')} \n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumCurrentChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumCurrentChallengesAdmin                = {data.get('Ok')} \n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumSubmissionsAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumSubmissionsAdmin                      = {data.get('Ok')} \n"

         # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumOpenSubmissionsAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumOpenSubmissionsAdmin                  = {data.get('Ok')} \n"

        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getNumOpenSubmissionsForOpenChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        output += f"- getNumOpenSubmissionsForOpenChallengesAdmin = {data.get('Ok')} \n"

        # -----------------------------------------------------
        return output.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    gamestate_name = None
    gamestate_canister_id = None
    challenger_name = None # just for color coding the output
    judge_name = None # just for color coding the output
    share_service_name = None # just for color coding the output
    for name, canister_id in CANISTERS.items():
        if "GAMESTATE" in name.upper():
            gamestate_name = name
            gamestate_canister_id = canister_id
            break
            

    if not gamestate_name:
        print(f"No GAMESTATE canister found in canisters-{network}.env")
        return
    
    # Log directory (also relative to script location)
    LOG_DIR = os.path.join(SCRIPT_DIR, f"logs-{network}")
    MONITOR_GAMESTATE_FILE = os.path.join(LOG_DIR, "monitor_gamestate_logs.log")
    PREVIOUS_LOGS = defaultdict(set)

    ensure_log_dir(LOG_DIR)

    # Clear common log file at start
    with open(MONITOR_GAMESTATE_FILE, "w"):
        pass

    print(f"\nMonitoring changes to {gamestate_name} ({gamestate_canister_id}) on '{network}' network...\n")

    timer = 0
    delay = 10  # seconds
    while True:
        new_lines = []
        log_lines = get_logs(gamestate_canister_id, network)
        for line in log_lines:
            if line not in PREVIOUS_LOGS[name]:
                PREVIOUS_LOGS[name].add(line)
                new_lines.append(line)

        if new_lines:
                individual_log_path = os.path.join(LOG_DIR, f"{name}.log")
                with open(individual_log_path, "a") as f_individual:
                    for line in new_lines:
                        f_individual.write(line + "\n")
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
    args = parser.parse_args()
    main(args.network)
