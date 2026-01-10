#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json
from collections import defaultdict
from dotenv import dotenv_values

from scripts.cleanup_llm_promptcache import cleanup_llm_promptcache

from .monitor_common import get_canisters, run_this_cmd

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
    

def upgrade_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network):
    """Upgrade LLM"""
    try:    
        ctrlb_canister_id = None
        llm_type = None
        llm_cwd = None
        if "CHALLENGER" in canister_name.upper():
            ctrlb_canister_id = challenger_canister_id
            llm_type = "challenger"
            llm_cwd = os.path.join(SCRIPT_DIR, "../PoAIW/llms/Challenger")
        elif "JUDGE" in canister_name.upper():
            ctrlb_canister_id = judge_canister_id
            llm_type = "judge"
            llm_cwd = os.path.join(SCRIPT_DIR, "../PoAIW/llms/Judge")
        elif "SHARE_SERVICE" in canister_name.upper():
            ctrlb_canister_id = share_service_canister_id
            llm_type = "share_service"
            llm_cwd = os.path.join(SCRIPT_DIR, "../PoAIW/llms/mAIner")
        else:
            print(f"Unknown llm type for canister {canister_name}. Skipping cleanup.")
            return

        # get canister name from canister_ids.json, for dfx deploy command
        llm_name_dfx_json = None
        with open(os.path.join(llm_cwd, "canister_ids.json")) as f:
            canister_ids = json.load(f)
            for key, networks in canister_ids.items():
                if networks.get(network) == canister_id:
                    llm_name_dfx_json = key
                    break
        if not llm_name_dfx_json:
            print(f"ERROR: Canister name for {llm_type} not found in canister_ids.json for network {network}.")
            return
        
        print(" ")
        print(f"- Verifying LLMs registered in controller canister {canister_name} ({ctrlb_canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "get_llm_canisters", "--output", "json"]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Removing LLM from controller canister {canister_name} ({ctrlb_canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "remove_llm_canister", f"(record {{canister_id = \"{canister_id}\"}})"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
    
        DELAY = 180
        print(" ")
        print(f"- Waiting for {DELAY} seconds to allow protocol to finish possible use of the LLM canister...")
        confirm = input(f"Skip the delay? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("---> Starting delay.")
            time.sleep(DELAY)
        else:
            confirm = input(f"Are you sure to skip the delay? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("---> Starting delay.")
                time.sleep(DELAY)
        
        print(" ")
        print(f"- Stopping LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "stop", canister_id]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Creating snapshot for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "snapshot", "create", canister_id]
        run_this_cmd(cmd, llm_cwd, confirm=True)
        
        print(" ")
        print(f"- Upgrading LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "deploy", "--network", network, llm_name_dfx_json, "--mode", "upgrade"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Starting LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "start", canister_id]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Cleaning prompt caches in LLM {canister_name} ({canister_id})")
        cmd = ["scripts/cleanup_llm_promptcache.sh", "--network", network, "--canister-id", canister_id]
        run_this_cmd(cmd, FUNNAI_DIR, confirm=False)
        
        print(" ")
        print(f"- Checking health for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "health"]
        print(f"Command: {' '.join(cmd)} \n-> from directory: {llm_cwd}")
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Loading model for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "load_model", '(record { args = vec {"--model"; "models/model.gguf"} })']
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Setting max_tokens for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "set_max_tokens", '(record { max_tokens_query = 12 : nat64; max_tokens_update = 12 : nat64 })']
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Pausing logs for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "log_pause"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Pausing db_chats for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "chats_pause"]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Assigning admin role to controller canister for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "assignAdminRole", f'(record {{ "principal" = "{ctrlb_canister_id}"; role = variant {{ AdminUpdate }}; note = "{llm_type.capitalize()} controller canister" }})']
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Assigning admin role to funnai-django-aws-dev for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "assignAdminRole", '(record { "principal" = "bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe"; role = variant { AdminUpdate }; note = "funnai-django-aws-dev" })']
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Assigning admin role to maintainer for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "assignAdminRole", '(record { "principal" = "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"; role = variant { AdminUpdate }; note = "maintainer" })']
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Assigning admin role to maintainer for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "assignAdminRole", '(record { "principal" = "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"; role = variant { AdminUpdate }; note = "maintainer" })']
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Removing controller canister as controller for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "update-settings", canister_id, "--remove-controller", ctrlb_canister_id, "--network", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Adding log viewers for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "update-settings", canister_id,
               "--add-log-viewer", "bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe",
               "--add-log-viewer", "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae",
               "--add-log-viewer", "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe",
               "--network", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Adding NNS Root Canister as controller for LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "sns", "prepare-canisters", "--network", "ic", "add-nns-root", canister_id]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Testing LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "new_chat", '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--cache-type-k"; "q8_0"; }})']
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Testing LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "run_update", '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; "--cache-type-k"; "q8_0"; "--repeat-penalty"; "1.1"; "--temp"; "0.6"; "-sp"; "-p"; "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\ngive me a short introduction to LLMs.<|im_end|>\n<|im_start|>assistant\n"; "-n"; "1" }})']
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Testing LLM {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "remove_prompt_cache", '(record { args = vec { "--prompt-cache"; "prompt.cache" }})']
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        print(f"- Adding LLM to controller canister {canister_name} ({ctrlb_canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "add_llm_canister", f"(record {{canister_id = \"{canister_id}\"}})"]
        run_this_cmd(cmd, llm_cwd, confirm=True)
        
        print(" ")
        print(f"- Verifying LLMs registered in controller canister {canister_name} ({ctrlb_canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "get_llm_canisters", "--output", "json"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        
        print(" ")
        
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to upgrade LLM for canister {canister_id} on network {network}")

def main(network, canister_id_):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    challenger_name = None
    challenger_canister_id = None
    judge_name = None
    judge_canister_id = None
    share_service_name = None
    share_service_canister_id = None
    for name, id in CANISTERS.items():
        if "LLM" in name.upper():
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

        if challenger_name and judge_name and share_service_name:
            # We found all necessary canisters, no need to continue
            break

    if not challenger_canister_id:
        print(f"No CHALLENGER canister found in canisters-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canisters-{network}.env")
        return
    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canisters-{network}.env")
        return

    for name, id in reversed(list(CANISTERS.items())):
        if "LLM" not in name.upper():
            continue
        if canister_id_ == "all" or canister_id_ == id:
            canister_id = id
            canister_name = name

            # Ask user for confirmation to proceed with the upgrade
            print(" ")
            print("=" * 100)
            confirm = input(f"Upgrade {canister_name} ({canister_id}) on network '{network}'? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Upgrade cancelled.")
                continue

            upgrade_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network)

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgrade LLMs.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        default="all",
        help="Specify the canister ID to use",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id)
