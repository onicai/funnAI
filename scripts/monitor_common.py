#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def ensure_log_dir(log_dir):
    """Ensure the logs directory exists."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created log directory: {log_dir}")

def get_canisters(network):
    
    # Load CANISTER_NAME=ID pairs from .env file located in the script's directory
    ENV_PATH = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")
    env_config = dotenv_values(ENV_PATH)
    CANISTERS = {key: value.strip('"') for key, value in env_config.items() if value and value.endswith("-cai") and not key=="NETWORK"}

    # Pick visually distinct 256-color codes (avoid 0-15 for standard colors, go higher for vivid ones)
    COLOR_CODES_256 = [
        27, 82, 196, 129, 226,  # distinct colors (blue, green, red, purple, yellow)
        33, 39, 45, 51,         # blues, cyans
        118, 154, 190,          # greens
        202, 208, 214,          # reds/oranges
        135, 141, 177,          # purples/pinks
        220, 190                # yellows
    ]

    def make_ansi_color(code):
        return f"\033[38;5;{code}m"

    RESET_COLOR = "\033[0m"

    CANISTER_COLORS = {
        name: make_ansi_color(COLOR_CODES_256[i % len(COLOR_CODES_256)])
        for i, name in enumerate(sorted(CANISTERS.keys()))
    }

    print(f"get_canisters: canister_ids-{network}.env lists {len(CANISTERS)} canisters on '{network}' network...")
    for name, canister_id in CANISTERS.items():
        print(f"{CANISTER_COLORS[name]}[{name}]{RESET_COLOR}({canister_id})")

    return (CANISTERS, CANISTER_COLORS, RESET_COLOR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(args.network)
