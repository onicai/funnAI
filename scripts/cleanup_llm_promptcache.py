#!/usr/bin/env python3

import subprocess
import sys
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values
import json

from .monitor_common import get_canisters, ensure_log_dir
from datetime import datetime, timezone

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def cleanup_llm_promptcache(gamestate_canister_id, archive_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network):
    """Cleanup prompt cache files in the LLM."""

    llm_type = ""
    if "CHALLENGER" in canister_name.upper():
        llm_type = "challenger"
    elif "JUDGE" in canister_name.upper():
        llm_type = "judge"
    elif "SHARE_SERVICE" in canister_name.upper():
        llm_type = "share_service"
    else:
        print(f"Unknown llm type for canister {canister_name}. Skipping cleanup.")
        return

    try:
        judgePromptIds = []
        mainerPromptIds = []

        if network != "prd":
            # Ok for testing on demo network - for debug purposes -> Do not do this on production network
            print(f"Cleaning up prompt cache for closed challenges on network {network}...")
            # Get promptIds for the closed challenges
            result = subprocess.check_output(
                ["dfx", "canister", "call", gamestate_canister_id, "getClosedChallengesAdmin", "--output", "json", "--network", network],
                stderr=subprocess.DEVNULL,
                text=True
            )
            data = json.loads(result)
            for challenge in data.get('Ok', []):
                if challenge.get('judgePromptId'):
                    judgePromptIds.append(challenge['judgePromptId'])
                if challenge.get('mainerPromptId'):
                    mainerPromptIds.append(challenge['mainerPromptId'])
        else:
            print(f"Skipping cleanup of closed challenges on production network {network} for canister {canister_name} ({canister_id}).")

        print("----------------------------------------------------")
        print(f"Getting the promptIds for archived challenges from the GameState canister on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "call", gamestate_canister_id, "getArchivedChallengesAdmin", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        print(f"Found {len(data.get('Ok', []))} archived challenges in GameState canister {gamestate_canister_id} on network {network}.")
        for challenge in data.get('Ok', []):
            if challenge.get('judgePromptId'):
                judgePromptIds.append(challenge['judgePromptId'])
            if challenge.get('mainerPromptId'):
                mainerPromptIds.append(challenge['mainerPromptId'])

        print("----------------------------------------------------")
        print(f"Getting the promptIds for migrated archived challenges from the Archive canister on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "call", archive_canister_id, "getChallenges", "--output", "json", "--network", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        print(f"Found {len(data.get('Ok', []))} migrated archived challenges in Archive canister {archive_canister_id} on network {network}.")
        for challenge in data.get('Ok', []):
            if challenge.get('judgePromptId'):
                judgePromptIds.append(challenge['judgePromptId'])
            if challenge.get('mainerPromptId'):
                mainerPromptIds.append(challenge['mainerPromptId'])

        print("----------------------------------------------------")
        if not judgePromptIds and not mainerPromptIds:
            print(f"No closed or archived promptIds found for {llm_type} canister {canister_name} ({canister_id}) on network {network}. Nothing to clean up.")
            return
        
        # NOTE: we do not have a clean remove_promptcache, because only the Judge Controller can remove it
        #       a patch is to upload a zero byte file to the prompt cache, which will overwrite the existing cache file
        if llm_type == "judge" or llm_type == "all":
            # sample Judge: .canister_cache/qmgdh-3aaaa-aaaaa-qanfq-cai/sessions/bc0e24ac-7ef4-4d19-a061-ec5324a9ca74.cache
            for i, judgePromptId in enumerate(judgePromptIds):
                full_prompt_cache_filename = f".canister_cache/{judge_canister_id}/sessions/{judgePromptId}.cache"
                print(f"{canister_name}: {i+1}/{len(judgePromptIds)}: {full_prompt_cache_filename}")
                subprocess.run(
                    ["dfx", "canister", "call", canister_id, "file_upload_chunk", 
                    f"(record {{filename = \"{full_prompt_cache_filename}\"; chunk = blob \"\"; chunksize = 0 : nat64; offset = 0 : nat64; }})", 
                    "--network", network],
                    check=True,
                    text=True
                )
                # delay to avoid rate limiting
                time.sleep(1)

        if llm_type == "share_service" or llm_type == "all":
            # sample ShareService: .canister_cache/rilmv-caaaa-aaaaa-qandq-cai/sessions/d85d3b4f-4e91-4102-a8bb-96b5a50ec398.cache
            for i, mainerPromptId in enumerate(mainerPromptIds):
                full_prompt_cache_filename = f".canister_cache/{share_service_canister_id}/sessions/{mainerPromptId}.cache"
                print(f"{canister_name}: {i+1}/{len(mainerPromptIds)}: {full_prompt_cache_filename}")
                subprocess.run(
                    ["dfx", "canister", "call", canister_id, "file_upload_chunk", 
                    f"(record {{filename = \"{full_prompt_cache_filename}\"; chunk = blob \"\"; chunksize = 0 : nat64; offset = 0 : nat64; }})", 
                    "--network", network],
                    check=True,
                    text=True
                )
                # delay to avoid rate limiting
                time.sleep(1)
    except subprocess.CalledProcessError:
        return []

def main(network, llm_type):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    gamestate_name = None
    gamestate_canister_id = None
    archive_name = None
    archive_canister_id = None
    judge_name = None
    judge_canister_id = None
    share_service_name = None
    share_service_canister_id = None
    for name, canister_id in CANISTERS.items():
        if "LLM" in name.upper():
            continue  # Skip LLM canisters in this loop
        if "JUDGE" in name.upper():
            judge_name = name
            judge_canister_id = canister_id
        elif "SERVICE" in name.upper():
            share_service_name = name
            share_service_canister_id = canister_id
        elif "GAMESTATE" in name.upper():
            gamestate_name = name
            gamestate_canister_id = canister_id
        elif "ARCHIVE" in name.upper():
            archive_name = name
            archive_canister_id = canister_id

        if gamestate_name and archive_name and judge_name and share_service_name:
            # We found all necessary canisters, no need to continue
            print(f"Found canisters: GAMESTATE={gamestate_name}, ARCHIVE={archive_name}, JUDGE={judge_name}, SHARE_SERVICE={share_service_name}")
            break
            
    if not gamestate_canister_id:
        print(f"No GAMESTATE canister found in canisters-{network}.env")
        return
    if not archive_canister_id:
        print(f"No ARCHIVE canister found in canisters-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canisters-{network}.env")
        return
    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canisters-{network}.env")
        return

    for name, canister_id in CANISTERS.items():
        if "LLM" in name.upper() and not "CHALLENGER" in name.upper() and (llm_type == 'all' or llm_type.lower() in name.lower()):
            print(f"Cleaning up LLM prompt cache for {name} ({canister_id}) on network {network}...")
            cleanup_llm_promptcache(gamestate_canister_id, archive_canister_id, judge_canister_id, share_service_canister_id, name, canister_id, network)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor DFINITY canister logs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--llm-type",
        choices=["all", "judge", "share_service"],
        default="all",
        help="Specify the cache type to use (default: all)",
    )
    args = parser.parse_args()
    main(args.network, args.llm_type)
