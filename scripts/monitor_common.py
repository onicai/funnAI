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

def get_canisters(network, canister_types):
    
    # Load CANISTER_NAME=ID pairs from .env files located in the script's directory

    CANISTERS = {}

    # protocol canisters
    if canister_types == "protocol" or canister_types == "all":
        ENV_PATH = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")
        env_config = dotenv_values(ENV_PATH)
        CANISTERS = {key: value.strip('"') for key, value in env_config.items() if value and value.endswith("-cai") and not key=="NETWORK"}

    # mainer canisters
    if canister_types == "mainers" or canister_types == "all":
        ENV_PATH = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}.env")
        env_config = dotenv_values(ENV_PATH)
        CANISTERS.update({key: value.strip('"') for key, value in env_config.items() if value and value.endswith("-cai") and not key=="NETWORK"})

    # Pick visually distinct 256-color codes (avoid 0-15 for standard colors, go higher for vivid ones)
    COLOR_CODES_256 = [
        27, 82, 196, 129, 226,  # distinct colors (blue, green, red, purple, yellow)
        33, 39, 45, 51,         # blues, cyans
        118, 154, 190,          # greens
        202, 208, 214,          # reds/oranges
        135, 141, 177,          # purples/pinks
        220, 190, 228, 185,     # yellows/light colors
        21, 57, 93, 99,         # more blues
        35, 71, 107, 143,       # more cyans
        22, 28, 34, 40,         # darker blues
        46, 76, 106, 112,       # teals
        124, 160, 167, 173,     # more greens
        198, 204, 210, 216,     # more reds
        126, 132, 138, 144,     # more purples
        150, 156, 162, 168,     # grays/other distinct colors
        # Additional 100 colors
        17, 18, 19, 20, 23, 24, 25, 26, 29, 30, 31, 32, 36, 37, 38, 41, 42, 43, 44, 47, 48, 49, 50, 52, 53, 54, 55, 56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 77, 78, 79, 80, 81, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 108, 109, 110, 111, 113, 114, 115, 116, 117, 119, 120, 121, 122, 123, 125, 127, 128, 130, 131, 133, 134, 136, 137, 139, 140, 142, 145, 146, 147, 148, 149
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
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(args.network)
