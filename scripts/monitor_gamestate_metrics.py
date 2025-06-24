#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values
import json

from .monitor_common import get_canisters, ensure_log_dir
from datetime import datetime, timezone

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_data(canister_id, network):
    """Fetch data from gamestate using dfx, only output changed values."""
    if not hasattr(get_data, "previous_values"):
        get_data.previous_values = {}

    previous_values = get_data.previous_values
    current_values = {}
    output = "\n"

    def should_include(key, value):
        prev = previous_values.get(key)
        current_values[key] = value
        return prev != value

    try:
        # -----------------------------------------------------
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "getScoredChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        numJudgedResponses = 0
        max_depth = 100
        for challenge in data.get('Ok', []):
            l1 = challenge["1"]
            depth = 0
            while len(l1) > 0 and depth < max_depth:
                depth += 1
                l1_0 = l1[0]
                l1_0_0 = l1_0.get('0', {})
                submissionStatus = l1_0_0.get('submissionStatus', {})
                if submissionStatus == {'Judged': None}:
                    numJudgedResponses += 1
                else:
                    print(f"Unexpected submissionStatus: {submissionStatus}")
                l1 = l1_0.get('1', {})

                if depth > 50:
                    print(f"Warning: depth = {depth} : exceeded 50 for challenge {challenge['0']}. Possible infinite loop detected.")

        if should_include("numJudgedResponses", numJudgedResponses):
            output += f"- numJudgedResponses = {numJudgedResponses} \n"

        # -----------------------------------------------------
        methods = [
            ("getNumArchivedChallengesAdmin", "ArchivedChallenges"),
            ("getNumClosedChallengesAdmin", "ClosedChallenges"),
            ("getNumScoredChallengesAdmin", "ScoredChallenges"),
            ("getNumCurrentChallengesAdmin", "CurrentChallenges"),
            ("getNumSubmissionsAdmin", "Submissions"),
            ("getNumOpenSubmissionsAdmin", "OpenSubmissions"),
            ("getNumOpenSubmissionsForOpenChallengesAdmin", "OpenSubsForOpenChallenges"),
        ]

        for method, label in methods:
            result = subprocess.check_output(
                ["dfx", "canister", "call", canister_id, method, "--output", "json", "--network", network],
                stderr=subprocess.DEVNULL,
                text=True
            )
            data = json.loads(result)
            val = data.get('Ok')
            if should_include(label, val):
                output += f"- {method:<45} = {val} \n"

        get_data.previous_values = current_values
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

    delay = 2  # seconds

    print(f"\nEvery {delay} seconds, monitoring changes to stats for {gamestate_name} ({gamestate_canister_id}) on '{network}' network...\n")
    while True:
        new_lines = []
        log_lines = get_data(gamestate_canister_id, network)
        CURRENT_LOGS = defaultdict(set)
        for line in log_lines:
            if line not in PREVIOUS_LOGS[gamestate_name]:
                CURRENT_LOGS[gamestate_name].add(line)
                new_lines.append(line)

        PREVIOUS_LOGS = CURRENT_LOGS
        
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
                    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                    print(f"{color_line}[{current_time}]-{line}")
        time.sleep(delay)

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
