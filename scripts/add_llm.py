#!/usr/bin/env python3

import subprocess
import sys
import argparse
import os
import json
import re

from .monitor_common import get_canisters, run_this_cmd

# Shared icp-cli helpers: unlike `dfx ... --output json`, icp-cli cannot decode a Candid
# response, so decoding happens here via icp-py-core.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

# LLM type -> setCyclesFlowAdmin field name
GAMESTATE_FIELD = {
    "challenger": "numChallengerLlms",
    "judge": "numJudgeLlms",
    "share_service": "numShareServiceLlms",
}

# LLM type -> (working directory relative to SCRIPT_DIR, env key)
LLM_TYPE_CONFIG = {
    "challenger": {
        "llm_cwd": "../PoAIW/llms/Challenger",
        "env_key": "CHALLENGER",
    },
    "judge": {
        "llm_cwd": "../PoAIW/llms/Judge",
        "env_key": "JUDGE",
    },
    "share_service": {
        "llm_cwd": "../PoAIW/llms/mAIner",
        "env_key": "SHARE_SERVICE",
    },
}


def parse_llm_count(data):
    """Parse the LLM count from a decoded get_llm_canisters response.

    Takes the DECODED response ({"Ok": {"llmCanisterIds": [...], ...}}) rather than a JSON
    string: icp-cli cannot emit JSON the way `dfx ... --output json` did, so the decoding
    now happens in icp_helpers.call() and this function receives real Python objects.
    Returns (count, canister_ids_list).
    """
    try:
        if isinstance(data, dict) and "Ok" in data:
            ids = data["Ok"].get("llmCanisterIds", [])
            return len(ids), ids
    except (AttributeError, TypeError):
        pass
    return None, []


def find_env_entry(env_path, canister_id):
    """Check if canister_id already exists in the env file."""
    try:
        with open(env_path) as f:
            for line in f:
                if canister_id in line and "=" in line:
                    return line.strip()
    except FileNotFoundError:
        pass
    return None


def find_canister_in_ids_json(canister_ids_path, canister_id, network):
    """Find the llm_N name for a canister ID in canister_ids.json."""
    try:
        with open(canister_ids_path) as f:
            data = json.load(f)
        for key, networks in data.items():
            if networks.get(network) == canister_id:
                return key
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def find_subnet_var_for_canister(env_path, canister_id):
    """Find the SUBNET_X_Y variable under which this canister is deployed.

    Scans the env file for the canister_id and extracts the SUBNET_X_Y prefix.
    Returns (subnet_var, env_key, llm_index) or (None, None, None).
    """
    # Pattern: SUBNET_X_Y_{TYPE}_LLM_N="<id>"
    pattern = re.compile(
        r'^(SUBNET_\d+_\d+)_(CHALLENGER|JUDGE|SHARE_SERVICE)_LLM_(\d+)='
    )
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if canister_id not in line:
                    continue
                m = pattern.match(line)
                if m:
                    return m.group(1), m.group(2), int(m.group(3))
    except FileNotFoundError:
        pass
    return None, None, None


def determine_env_line(env_path, canister_id, llm_type, llm_cwd, network):
    """Determine the env line to add for this canister.

    Looks up the llm_N index from canister_ids.json and finds the subnet
    from the env file. Returns the line to append or None.
    """
    env_key = LLM_TYPE_CONFIG[llm_type]["env_key"]
    canister_ids_path = os.path.join(llm_cwd, "canister_ids.json")

    # Find llm_N name from canister_ids.json
    llm_name = find_canister_in_ids_json(canister_ids_path, canister_id, network)
    if not llm_name:
        print(f"  WARNING: Canister {canister_id} not found in {canister_ids_path} for network {network}")
        return None

    # Extract N from llm_N
    m = re.match(r"^llm_(\d+)$", llm_name)
    if not m:
        print(f"  WARNING: Unexpected canister name format: {llm_name}")
        return None
    llm_index = m.group(1)

    # Find which subnet this canister is on by checking existing LLM entries
    # of the same type and picking the subnet of the last one, or prompting
    subnet_pattern = re.compile(r'^(SUBNET_\d+_\d+)_' + re.escape(env_key) + r'_LLM_\d+=')
    last_subnet_var = None
    try:
        with open(env_path) as f:
            for line in f:
                m2 = subnet_pattern.match(line.strip())
                if m2:
                    last_subnet_var = m2.group(1)
    except FileNotFoundError:
        pass

    if not last_subnet_var:
        print(f"  WARNING: No existing {env_key} LLM entries found in {env_path}")
        last_subnet_var = input(f"  Enter the subnet variable (e.g. SUBNET_1_2): ").strip()
        if not last_subnet_var:
            return None

    return f'{last_subnet_var}_{env_key}_LLM_{llm_index}="{canister_id}"'


def add_llm(ctrlb_canister_id, gamestate_canister_id, llm_type, canister_id, network, dry_run=False):
    """Add a deployed LLM canister to the protocol."""
    llm_cwd = os.path.join(SCRIPT_DIR, LLM_TYPE_CONFIG[llm_type]["llm_cwd"])
    env_key = LLM_TYPE_CONFIG[llm_type]["env_key"]
    field_name = GAMESTATE_FIELD[llm_type]
    env_path = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")

    # Step 1: Show current LLMs in controller
    print(f"\n- Current LLMs in controller canister ({ctrlb_canister_id})")
    cmd = ["icp", "canister", "call", ctrlb_canister_id, "get_llm_canisters", "()", "-e", network]
    print(f"  {' '.join(cmd)} \n  -> from directory: {llm_cwd}")
    result = icp_helpers.call_argv(cmd)
    print(result)

    current_count, current_ids = parse_llm_count(result)
    if current_count is None:
        print("  WARNING: Could not parse LLM count from response")
        current_count = 0
        current_ids = []
    print(f"  Current LLM count: {current_count}")

    # Check if canister is already registered
    if canister_id in current_ids:
        print(f"\n  ERROR: Canister {canister_id} is already registered in the controller.")
        return

    # Determine the env line to add
    env_line = determine_env_line(env_path, canister_id, llm_type, llm_cwd, network)
    existing_env = find_env_entry(env_path, canister_id)

    # Step 2: Dry-run summary
    new_count = current_count + 1
    if dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN — no changes will be made")
        print("=" * 80)
        print(f"  Canister    : {canister_id}")
        print(f"  LLM type    : {llm_type}")
        print(f"  Controller  : {ctrlb_canister_id}")
        print(f"  GameState   : {gamestate_canister_id}")
        print("-" * 80)
        print("Actions that WOULD be performed:")
        print(f"  1. Add LLM to controller: add_llm_canister")
        print(f"  2. Verify LLM count: {current_count} -> {new_count}")
        print(f"  3. Update GameState: {field_name} = {new_count}")
        if existing_env:
            print(f"  4. canister_ids-{network}.env: already present ({existing_env})")
        elif env_line:
            print(f"  4. Append to canister_ids-{network}.env: {env_line}")
        else:
            print(f"  4. canister_ids-{network}.env: could not determine line to add")
        print("-" * 80)
        print("DRY RUN complete — nothing was changed.")
        return

    # Step 3: Confirm with user
    print(f"\nAbout to add {canister_id} ({llm_type}) to controller on '{network}'")
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Add LLM cancelled.")
        return

    # Step 4: Add LLM to controller
    print(f"\n- Adding LLM to controller canister ({ctrlb_canister_id})")
    cmd = ["icp", "canister", "call", ctrlb_canister_id, "add_llm_canister", f'(record {{canister_id = "{canister_id}"}})', "-e", network]
    run_this_cmd(cmd, llm_cwd, confirm=False)

    # Step 5: Verify addition
    print(f"\n- Verifying LLMs registered in controller canister ({ctrlb_canister_id})")
    cmd = ["icp", "canister", "call", ctrlb_canister_id, "get_llm_canisters", "()", "-e", network]
    print(f"  {' '.join(cmd)} \n  -> from directory: {llm_cwd}")
    result = icp_helpers.call_argv(cmd)
    print(result)

    verified_count, verified_ids = parse_llm_count(result)
    if verified_count is not None:
        new_count = verified_count
    if new_count == current_count + 1:
        print(f"  LLM count verified: {current_count} -> {new_count}")
    else:
        print(f"  WARNING: Expected {current_count + 1} LLMs, got {new_count}")

    # Verify canister is in the list
    if canister_id in verified_ids:
        print(f"  Canister {canister_id} confirmed in controller")
    else:
        print(f"  WARNING: Canister {canister_id} NOT found in controller after add!")

    # Step 6: Get current GameState cycle config
    print(f"\n- Getting current GameState cycle config")
    cmd = ["icp", "canister", "call", gamestate_canister_id, "getCyclesFlowAdmin", "()", "-e", network]
    run_this_cmd(cmd, llm_cwd, confirm=False)

    # Step 7: Update GameState LLM count
    print(f"\n- Updating GameState: {field_name} = {new_count}")
    cmd = ["icp", "canister", "call", gamestate_canister_id, "setCyclesFlowAdmin", f"(record {{{field_name} = opt ({new_count} : nat);}})", "-e", network]
    run_this_cmd(cmd, llm_cwd, confirm=False)

    # Step 8: Update canister_ids-{network}.env
    if existing_env:
        print(f"\n- canister_ids-{network}.env: already present ({existing_env})")
    elif env_line:
        print(f"\n- Updating canister_ids-{network}.env")
        with open(env_path, "a") as f:
            f.write(f"{env_line}\n")
        print(f"  Appended: {env_line}")
    else:
        print(f"\n- WARNING: Could not determine env line. Please update canister_ids-{network}.env manually.")

    # Step 9: Print summary
    print("\n" + "=" * 80)
    print(f"Successfully added {canister_id} to {llm_type} controller")
    print(f"  Controller LLM count: {new_count}")
    print(f"  GameState {field_name}: {new_count}")
    print("=" * 80)
    print("\nManual step required:")
    print(f"  Register the new LLM canister with CycleOps")
    print(f"  (adds controller 2daxo-giaaa-aaaap-anvca-cai).")
    print("\nVerify on-chain prompt-cache cleanup is active:")
    print(f"  dfx canister --network {network} call {canister_id} get_cache_cleanup_stats '()'")
    print(f"  Look for is_running = true, and runs > 0 after one period (default 600s).")


def main(network, canister_id_, llm_type, dry_run=False):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    # Extract controller and gamestate canister IDs
    challenger_canister_id = None
    judge_canister_id = None
    share_service_canister_id = None
    gamestate_canister_id = None
    for name, id in CANISTERS.items():
        if "LLM" in name.upper():
            continue
        elif "CHALLENGER" in name.upper():
            challenger_canister_id = id
        elif "JUDGE" in name.upper():
            judge_canister_id = id
        elif "SERVICE" in name.upper():
            share_service_canister_id = id
        elif "GAMESTATE" in name.upper():
            gamestate_canister_id = id

    if not challenger_canister_id:
        print(f"No CHALLENGER canister found in canister_ids-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canister_ids-{network}.env")
        return
    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canister_ids-{network}.env")
        return
    if not gamestate_canister_id:
        print(f"No GAMESTATE canister found in canister_ids-{network}.env")
        return

    # Pick the controller matching llm_type
    ctrlb_canister_id = None
    if llm_type == "challenger":
        ctrlb_canister_id = challenger_canister_id
    elif llm_type == "judge":
        ctrlb_canister_id = judge_canister_id
    elif llm_type == "share_service":
        ctrlb_canister_id = share_service_canister_id

    if not ctrlb_canister_id:
        print(f"ERROR: No {llm_type.upper()} controller canister found")
        return

    print("\n" + "=" * 80)
    print(f"Add {canister_id_} ({llm_type}) to protocol on network '{network}'")
    print(f"  Controller : {ctrlb_canister_id}")
    print(f"  GameState  : {gamestate_canister_id}")
    print("=" * 80)

    add_llm(ctrlb_canister_id, gamestate_canister_id, llm_type, canister_id_, network, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a deployed LLM canister to the protocol.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        required=True,
        help="Specify the canister ID to add to the protocol",
    )
    parser.add_argument(
        "--llm-type",
        choices=["challenger", "judge", "share_service"],
        required=True,
        help="Specify the LLM type",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id, args.llm_type, dry_run=args.dry_run)
