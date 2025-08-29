#!/usr/bin/env python3

import subprocess
import sys
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values
import json

from .monitor_common import get_canisters, get_prompt_cache_entries
from datetime import datetime, timezone

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def cleanup_llm_promptcache(gamestate_canister_id, challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network):
    """Cleanup prompt cache files in the LLM."""

    ctrlb_canister_id = None
    llm_type = None
    if "CHALLENGER" in canister_name.upper():
        ctrlb_canister_id = challenger_canister_id
        llm_type = "challenger"
    elif "JUDGE" in canister_name.upper():
        ctrlb_canister_id = judge_canister_id
        llm_type = "judge"
    elif "SHARE_SERVICE" in canister_name.upper():
        ctrlb_canister_id = share_service_canister_id
        llm_type = "share_service"
    else:
        print(f"Unknown llm type for canister {canister_name}. Skipping cleanup.")
        return

    print("----------------------------------------------------")
    # confirm that the canister is offline
    try:
        result = subprocess.check_output(
            ["dfx", "canister", "call", ctrlb_canister_id, "get_llm_canisters", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        LLMs = data.get('Ok', {}).get('llmCanisterIds', [])
        # print(f"Found {len(LLMs)} entries in LLM canister {canister_name} ({canister_id}) on network {network}.")
        # make sure the canister_id is NOT in the list of LLMs
        if canister_id in LLMs:
            print(f"Canister {canister_name} ({canister_id}) is ONLINE on network {network}.")
            print(f"Please remove the LLM canister from the '{llm_type}' controller {ctrlb_canister_id} before running this script.")
            return
        
        print(f"We confirmed that the LLM canister {canister_name} ({canister_id}) is OFFLINE on network {network}.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking if canister {canister_name} ({canister_id}) is indeed OFFLINE on network {network}: {e}")
        return
    
    
    print(f"(offline mode) Deleting all .canister_cache entries in LLM canister {canister_name} ({canister_id}) on network {network}...")

    entries = get_prompt_cache_entries(canister_name, canister_id, network)
    if not entries:
        print(f"No entries found in .canister_cache for LLM canister {canister_name} ({canister_id}) on network {network}. Nothing to clean up.")
        return
    
    for i, ftype in enumerate(["file", "directory"]):
        print(f"Loop {i}: deleting .canister_cache '{ftype}' paths in the LLM canister.")
        try:
            count = 0
            for entry in reversed(entries):
                filename = entry.get('filename')
                filetype = entry.get('filetype')
                if filetype == ftype:
                    count += 1
                    print(f"({count}/{len(entries)}) Deleting {filename} ")
                    subprocess.run(
                        ["dfx", "canister", "call", canister_id, "filesystem_remove", 
                        f"(record {{filename = \"{filename}\"; }})", 
                        "--network", network],
                        check=True,
                        text=True
                    )
                    # delay to avoid rate limiting
                    time.sleep(0.1)
            print(f"Deleted {count} .canister_cache '{ftype}' paths in LLM canister {canister_name} ({canister_id}) on network {network}.")
        except subprocess.CalledProcessError as e:
            print(f"Error deleting .canister_cache '{ftype}' paths in LLM canister {canister_name} ({canister_id}) on network {network}: {e}")
            return      

        print(f"Cleanup of prompt cache for {llm_type} canister {canister_name} ({canister_id}) on network {network} completed successfully.")

def main(network, canister_id):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    canister_name = None
    gamestate_name = None
    gamestate_canister_id = None
    # archive_name = None
    # archive_canister_id = None
    challenger_name = None
    challenger_canister_id = None
    judge_name = None
    judge_canister_id = None
    share_service_name = None
    share_service_canister_id = None
    for name, id in CANISTERS.items():
        if canister_id == id:
            canister_name = name
            print(f"Found canister {canister_name} with ID {canister_id} on network {network}.")
        elif "LLM" in name.upper():
            continue  # Skip LLM canisters in this loop
        elif "CHALLENGER" in name.upper():
            challenger_name = name
            challenger_canister_id = id
        elif "JUDGE" in name.upper():
            judge_name = name
            judge_canister_id = id
        elif "SERVICE" in name.upper():
            share_service_name = name
            share_service_canister_id = id
        elif "GAMESTATE" in name.upper():
            gamestate_name = name
            gamestate_canister_id = id
        # elif "ARCHIVE" in name.upper():
        #     archive_name = name
        #     archive_canister_id = id

        if canister_name and gamestate_name and judge_name and share_service_name:
            # We found all necessary canisters, no need to continue
            break

    if not canister_name:
        print(f"No LLM canister found in canisters-{network}.env")
        return
    if not gamestate_canister_id:
        print(f"No GAMESTATE canister found in canisters-{network}.env")
        return
    # if not archive_canister_id:
    #     print(f"No ARCHIVE canister found in canisters-{network}.env")
    #     return
    if not challenger_canister_id:
        print(f"No CHALLENGER canister found in canisters-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canisters-{network}.env")
        return

    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canisters-{network}.env")
        return

    cleanup_llm_promptcache(gamestate_canister_id, challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        help="Specify the canister ID to use",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id)
