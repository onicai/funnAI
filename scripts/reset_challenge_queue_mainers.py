#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
import json
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

resetcounter = 0
mainersWithQueueCounter = 0

def reset_challenge_queue(canister_id, network):
    """Reset challenge queue for mAIner."""
    global mainersWithQueueCounter
    global resetcounter

    try:
        print(f"Getting challengeQueue for the mAIner {canister_id} on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "--network", network, "call", canister_id, "getChallengeQueueAdmin", "--output", "json"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        challenge_queue = data.get('Ok', [])

        if len(challenge_queue) > 0:
            if len(challenge_queue) >= 4:
                print(f"  Resetting the challenge queue for {canister_id}.")

                cmd = ["dfx", "canister", "call", canister_id, "resetChallengeQueueAdmin", "--network", network]    
                subprocess.run(
                    cmd,
                    check=True,
                    text=True
                )

                resetcounter += 1
            elif len(challenge_queue) > 1:
                print(f"  {canister_id} has {len(challenge_queue)} challenges in the queue.")
                mainersWithQueueCounter += 1

    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to reset challenge queue for mAIner for canister {canister_id} on network {network}")

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "mainers")

    for name, canister_id in CANISTERS.items():
        if ("MAINER_SHARE_AGENT" not in name):
            print(f"Skipping canister {name} ({canister_id}) as it is not a mAIner.")
            continue

        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        reset_challenge_queue(canister_id, network)
    
    print(f"  Reset {resetcounter} mAIners.")
    print(f"  {mainersWithQueueCounter} mAIners have challenges in their queues.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset challenge queue for mAIners.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()

    main(args.network)
