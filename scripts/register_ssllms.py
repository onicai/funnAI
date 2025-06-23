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

def reset_llm_canisters(ssctrl_canister_id, network):
    """Reset the LLM canisters for the Ssctrl."""
    try:    
        print(f"Resetting the LLM canisters for Ssctrl {ssctrl_canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "call", ssctrl_canister_id, "reset_llm_canisters" ],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable rResetting the LLM canisters for Ssctrl {ssctrl_canister_id} on network {network}...")

def register_ssllm(ssctrl_canister_id, network, canister_id):
    """Register an Ssllm with the Ssctrl."""
    try:    
        print(f"Registering Ssllm canister {canister_id} with Ssctrl {ssctrl_canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "call", ssctrl_canister_id, "add_llm_canister", f"( record {{ canister_id = \"{canister_id}\"; }})" ],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable registering Ssllm canister {canister_id} with Ssctrl {ssctrl_canister_id} on network {network}...")

def main(network):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    SSCTRL_CANISTER_ID = ""
    for name, canister_id in CANISTERS.items():
        if ("LLM" in name):
            continue
        if ("SHARE_SERVICE" in name):
            SSCTRL_CANISTER_ID = canister_id
            print(f"Found Ssctrl canister: {name} ({canister_id})")
            reset_llm_canisters(SSCTRL_CANISTER_ID, network)
            break

    for name, canister_id in CANISTERS.items():
        if ("SHARE_SERVICE_LLM" in name):
            print("-------------------------------")
            print(f"Canister {name} ({canister_id})")

            register_ssllm(SSCTRL_CANISTER_ID, network, canister_id)


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
