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

def get_mainers(network):
    """Get mainers from gamestate using dfx."""
    try:    
        print(f"Getting all mAIners from the game_state_canister on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "--network", network, "call", "game_state_canister", "getMainerAgentCanistersAdmin", "--output", "json"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        mainers = data.get('Ok', [])
        return mainers
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to get mAiners from game_state_canister on network {network}")

def main(network, user):
    mainers = get_mainers(network)
    if not mainers or len(mainers) == 0:
        print("No mainers found.")
        return
    
    # Open file and write header comment
    if user == "all" or user is None:
        env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}.env")
    else:
        mainers = [mainer for mainer in mainers if mainer.get('ownedBy', '') == user]
        if not mainers:
            print(f"No mainers found for user '{user}' on network '{network}'")
            return
        env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}-{user}.env")

    print(f"Writing mainers to {env_file_path}")
    with open(env_file_path, 'w') as f:
        f.write(f"# {len(mainers)-1} mAIners - data from game_state_canister on network {network}\n")
        f.write(f"# DO NOT MANUALLY UPDATE THIS FILE, instead run: scripts/get_mainers.sh --network $NETWORK \n")
    
        count = 0
        count_created = 0
        for mainer in mainers:
            address = mainer.get('address', '')
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

            if canister_type == "ShareService":
                print(f"Skipping ShareService canister, because this is part of the protocol canisters: {address}")
                continue

            if canister_type != "ShareAgent":
                print(f"Skipping canister, because the canister_type is unknown : {canister_type}")
                continue

            line = f"MAINER_SHARE_AGENT_{count:04d}={address}\n"
            # print(line.strip())
            f.write(line)

            if address !="":
                count_created += 1
            count += 1
    
    print(f"Found {count} mainer user entries on network '{network}'") # excluding the ShareService canister
    print(f"Found {count_created} created mainers on network '{network}'") # excluding the ShareService canister

    if user == "all" or user is None:
        # Write counts to a timestamped CSV file only if there's a change
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        csv_file_path = os.path.join(SCRIPT_DIR, f"get_mainers-{network}.csv")
            
        print(f"Checking for changes before appending to {csv_file_path}")

        # Read the last two lines of the file if they exist
        last_line = None
        second_last_line = None
        last_count = None
        last_count_created = None
        second_last_count = None
        second_last_count_created = None

        if os.path.exists(csv_file_path) and os.stat(csv_file_path).st_size > 0:
            with open(csv_file_path, 'r') as csv_file:
                lines = csv_file.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    parts = last_line.split(',')
                    if len(parts) == 4:
                        last_count = int(parts[2])
                        last_count_created = int(parts[3])
                    if len(lines) > 1:
                        second_last_line = lines[-2].strip()
                        parts = second_last_line.split(',')
                        if len(parts) == 4:
                            second_last_count = int(parts[2])
                            second_last_count_created = int(parts[3])

        # Prepare the new line
        new_line = f"{timestamp},{network},{count},{count_created}"

        # Determine action based on changes
        if last_count != count or last_count_created != count_created:
            print(f"Appending counts to {csv_file_path}")
            with open(csv_file_path, 'a') as csv_file:
                if os.stat(csv_file_path).st_size == 0:  # Check if file is empty
                    csv_file.write("timestamp,network,wl_mainers_allocated,wl_mainers_created\n")
                csv_file.write(new_line + "\n")
        else:
            if second_last_count != count or second_last_count_created != count_created:
                print(f"Appending counts to {csv_file_path}")
                with open(csv_file_path, 'a') as csv_file:
                    if os.stat(csv_file_path).st_size == 0:  # Check if file is empty
                        csv_file.write("timestamp,network,wl_mainers_allocated,wl_mainers_created\n")
                    csv_file.write(new_line + "\n")
            else:
                print(f"Replacing last line in {csv_file_path}")
                with open(csv_file_path, 'w') as csv_file:
                    if os.stat(csv_file_path).st_size == 0:  # Check if file is empty
                        csv_file.write("timestamp,network,wl_mainers_allocated,wl_mainers_created\n")
                    else:
                        csv_file.write(lines[0])  # Write the header line
                    csv_file.writelines(lines[1:-1])  # Write all lines except the last one
                    csv_file.write(new_line + "\n")

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
