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

def cleanup_llm_promptcache(challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network):
    """Cleanup prompt cache files in the LLM."""

    llm_type = None
    if "CHALLENGER" in canister_name.upper():
        llm_type = "challenger"
    elif "JUDGE" in canister_name.upper():
        llm_type = "judge"
    elif "SHARE_SERVICE" in canister_name.upper():
        llm_type = "share_service"
    else:
        print(f"Unknown llm type for canister {canister_name}. Skipping cleanup.")
        return

    print("----------------------------------------------------")            
    entries = get_prompt_cache_entries(canister_name, canister_id, network)
    if not entries:
        print(f"No entries found in .canister_cache for LLM canister {canister_name} ({canister_id}) on network {network}. Nothing to clean up.")
        return
    
    ftype = "file"
    age_minutes_threshold = 24 * 60  # Only delete files older than this threshold
    print(f"Deleting .canister_cache '{ftype}' paths older than {age_minutes_threshold} minutes, while LLM is still online.")
    try:
        count = 0
        count_deleted = 0
        for entry in reversed(entries):
            count += 1
            filename = entry.get('filename')
            filetype = entry.get('filetype')
            if filetype != ftype:
                # print(f"({count}/{len(entries)}) Skipping {filename} of type {filetype}, as it is not a '{ftype}' file.")
                continue

            # get age of the file
            # print(f"({count}/{len(entries)}) Checking age of {filename}...")
            cmd = ["dfx", "canister", "--network", network, "call", canister_id, "get_creation_timestamp_ns", 
                f"(record {{filename = \"{filename}\"; }})", "--output", "json"]
            # print(f"  {' '.join(cmd)}")
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
            # print(result)
            data = json.loads(result)
            if 'Err' in data:
                print(f"  Error getting age for {filename}: {data['Err']}")
                continue
            age_seconds = int(data['Ok'].get('age_seconds', 0))
            age_minutes = age_seconds / 60

            if age_minutes < age_minutes_threshold:
                print(f"({count}/{len(entries)}) Skipping {filename} of age {age_minutes} minutes, as it is too recent.")
                time.sleep(1.0)
                continue

            age_days = age_minutes // (60 * 24)
            age_hours = (age_minutes % (60 * 24)) // 60
            print(f"({count}/{len(entries)}) Deleting {filename} of age {age_minutes} minutes ({age_days} days and {age_hours} hours).")
            count_deleted += 1
            # print("====PATCH-PATCH-PATCH=====SKIPPING ACTUAL DELETE===DRY-RUN=====")
            # time.sleep(3)
            # continue            
            subprocess.run(
                ["dfx", "canister", "call", canister_id, "filesystem_remove", 
                f"(record {{filename = \"{filename}\"; }})", 
                "--network", network],
                check=True,
                text=True
            )
            # delay to avoid protocol interference
            time.sleep(1.0)
        print(f"Deleted {count_deleted} .canister_cache '{ftype}' paths in LLM canister {canister_name} ({canister_id}) on network {network}.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR occured when calling the subprocess command.")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:\n", e.output)
        return      

    print(f"Cleanup of prompt cache for {llm_type} canister {canister_name} ({canister_id}) on network {network} completed successfully.")

def main(network, canister_id):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    canister_name = None
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

        if canister_name and challenger_name and judge_name and share_service_name:
            # We found all necessary canisters, no need to continue
            break

    if not canister_name:
        print(f"No LLM canister found in canisters-{network}.env")
        return
    if not challenger_canister_id:
        print(f"No CHALLENGER canister found in canisters-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canisters-{network}.env")
        return
    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canisters-{network}.env")
        return

    cleanup_llm_promptcache(challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network)

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
