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
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network)

    gamestate_name = None
    gamestate_canister_id = None
    challenger_name = None # just for color coding the output
    judge_name = None # just for color coding the output
    share_service_name = None # just for color coding the output
    for name, canister_id in CANISTERS.items():
        if "GAMESTATE" in name.upper():
            gamestate_name = name
            gamestate_canister_id = canister_id
        elif "CHALLENGER" in name.upper():
            challenger_name = name
        elif "JUDGE" in name.upper():
            judge_name = name
        elif "SHARE_SERVICE" in name.upper():
            share_service_name = name
        
        if gamestate_name and judge_name and share_service_name:
            break
            

    if not gamestate_name:
        print(f"No GAMESTATE canister found in canisters-{network}.env")
        return
    
    # Log directory (also relative to script location)
    LOG_DIR = os.path.join(SCRIPT_DIR, f"logs-{network}")
    MONITOR_GAMESTATE_FILE = os.path.join(LOG_DIR, "monitor_gamestate.log")
    PREVIOUS_LOGS = defaultdict(set)

    ensure_log_dir(LOG_DIR)

    # Clear common log file at start
    with open(MONITOR_GAMESTATE_FILE, "w"):
        pass

    print(f"\nMonitoring changes to stats for {gamestate_name} ({gamestate_canister_id}) on '{network}' network...\n")

    timer = 0
    delay = 10  # seconds
    while True:
        new_lines = []
        log_lines = get_data(gamestate_canister_id, network)
        for line in log_lines:
            if line not in PREVIOUS_LOGS[name]:
                PREVIOUS_LOGS[name].add(line)
                new_lines.append(line)

        if new_lines:
            with open(MONITOR_GAMESTATE_FILE, "a") as f:
                for line in new_lines:
                    color_line = CANISTER_COLORS[gamestate_name]
                    if "getNumCurrentChallengesAdmin" in line:
                        color_line = CANISTER_COLORS[challenger_name]
                    elif "getNumScoredChallengesAdmin" in line:
                        color_line = CANISTER_COLORS[judge_name]
                    elif "getNumOpenSubmissionsForOpenChallengesAdmin" in line or "getNumOpenSubmissionsAdmin" in line or "getNumSubmissionsAdmin" in line:
                        color_line = CANISTER_COLORS[share_service_name]
                    f.write(line + "\n")
                    # print(f"{CANISTER_COLORS[gamestate_name]}{timer:10,}s-[{gamestate_name}]{color_line}({gamestate_canister_id}) {line}")
                    print(f"{color_line}{timer:10,}s-{line}")
        time.sleep(delay)
        timer += delay

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
