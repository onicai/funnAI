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

def main(network):
    mainers = get_mainers(network)
    if not mainers or len(mainers) == 0:
        print("No mainers found.")
        return
    
    # Open file and write header comment
    env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}.env")
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
            print(line.strip())
            f.write(line)

            if address !="":
                count_created += 1
            count += 1
    
    print(f"Found {count} mainer user entries on network '{network}'") # excluding the ShareService canister
    print(f"Found {count_created} created mainers on network '{network}'") # excluding the ShareService canister

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
