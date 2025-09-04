#!/usr/bin/env python3

import subprocess
import sys
import argparse
import os
import json
from collections import defaultdict
from dotenv import dotenv_values

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_balance(canister_id, network):
    """Fetch cycles balance using dfx for a given canister."""
    try:
        cmd = ["dfx", "canister", "status", canister_id, "--network", network]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        
        # Extract balance from the output
        balance = None
        for line in output.split('\n'):
            if line.startswith('Balance:'):
                balance_string = line.split(':')[1].strip().split()[0]  
                balance = int(balance_string)
                break
        
        if balance is None:
            print(f"ERROR: Unable to find balance for canister {canister_id} on network {network}")
            print(f"  {' '.join(cmd)}")
            print(output)

        return balance
    except subprocess.CalledProcessError as e:
        print(f"ERROR occured when calling the subprocess command.")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:\n", e.output)
        return None

def run_this_cmd(cmd, cwd, confirm=False):
    print(f"  {' '.join(cmd)} \n  -> from directory: {cwd}")
    if not confirm:
        subprocess.run(cmd, check=True,text=True, cwd=cwd)
    else:
        confirm = input(f"  Do you want to run this command? (y/n/quit): ").strip().lower()
        if confirm in ['y', 'yes']:
            subprocess.run(cmd, check=True,text=True, cwd=cwd)
        elif confirm in ['q', 'quit']:
            print("Upgrade cancelled.")
            sys.exit(0)
        else:
            print("  Command skipped.")

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

def get_prompt_cache_entries(canister_name, canister_id, network):
    print(" ")
    print(f"Getting the content of the .canister_cache folder in the LLM canister {canister_name} ({canister_id}) on network {network}...")
    try:
        result = subprocess.check_output(
            ["dfx", "canister", "call", canister_id, "recursive_dir_content_update", 
            '(record {dir = ".canister_cache"; max_entries = 0 : nat64})', 
            "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        entries = data.get('Ok', [])
        print(f"Found {len(entries)} entries in LLM canister {canister_name} ({canister_id}) on network {network}.")
        return entries
    except subprocess.CalledProcessError as e:
        print(f"Error getting content of .canister_cache in LLM canister {canister_name} ({canister_id}) on network {network}: {e}")
        return []
    
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
