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

def upgrade_mainer(canister_id, network):
    """Upgrade mAIner using GameState > mAInerCreator."""
    try:    
        subprocess.run(
            ["scripts/scripts-gamestate/deploy-mainers-ShareAgent-via-gamestate.sh", "--network", network, "--mode", "upgrade", "--canister", canister_id],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to upgrade mAIner for canister {canister_id} on network {network}")

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "mainers")

    for name, canister_id in CANISTERS.items():
        if ("GAMESTATE" in name or "CREATOR" in name or "LLM" in name):
            continue

        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        upgrade_mainer(canister_id, network)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade mAIners.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
