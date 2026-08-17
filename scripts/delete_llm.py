#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json

from .monitor_common import get_canisters, run_this_cmd, get_balance

# Shared icp-cli helpers: unlike `dfx ... --output json`, icp-cli cannot decode a Candid
# response, so decoding happens here via icp-py-core.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

# LLM type -> setCyclesFlowAdmin field name (mirrors scripts/add_llm.py)
GAMESTATE_FIELD = {
    "challenger": "numChallengerLlms",
    "judge": "numJudgeLlms",
    "share_service": "numShareServiceLlms",
}


def parse_llm_count(data):
    """Parse the LLM count from a decoded get_llm_canisters response.

    Takes the DECODED response ({"Ok": {"llmCanisterIds": [...], ...}}) rather than a JSON
    string: icp-cli cannot emit JSON the way `dfx ... --output json` did, so decoding now
    happens in icp_helpers and this function receives real Python objects.
    Returns (count, canister_ids_list) or (None, []) on parse failure.
    """
    try:
        if isinstance(data, dict) and "Ok" in data:
            ids = data["Ok"].get("llmCanisterIds", [])
            return len(ids), ids
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return None, []


def delete_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, gamestate_canister_id, canister_name, canister_id, network, dry_run=False):
    """Delete an LLM canister from the protocol and reclaim its cycles."""
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
            print(f"Unknown llm type for canister {canister_name}. Aborting.")
            return

        field_name = GAMESTATE_FIELD[llm_type]

        if dry_run:
            print(" ")
            print("=" * 80)
            print("DRY RUN — no changes will be made")
            print("=" * 80)

        # Step 1: Show current cycles balance
        print(" ")
        print(f"- Checking cycles balance for {canister_name} ({canister_id})")
        balance = get_balance(canister_id, network)
        if balance is not None:
            print(f"  Current balance: {balance:,} cycles")

        # Step 2: Verify LLMs registered in controller
        print(" ")
        print(f"- Verifying LLMs registered in controller canister ({ctrlb_canister_id})")
        cmd = ["icp", "canister", "call", ctrlb_canister_id, "get_llm_canisters", "()", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 3: Load canister_ids.json and identify entry to clean up
        canister_ids_path = os.path.join(llm_cwd, "canister_ids.json")
        canister_ids_data = None
        json_key_to_remove = None
        try:
            with open(canister_ids_path) as f:
                canister_ids_data = json.load(f)
            for key, networks in canister_ids_data.items():
                if networks.get(network) == canister_id:
                    json_key_to_remove = key
                    break
        except FileNotFoundError:
            pass

        # Step 4: Identify what would be cleaned up in canister_ids-{network}.env
        env_path = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")
        env_line_to_remove = None
        try:
            with open(env_path) as f:
                for line in f:
                    if canister_id in line and "=" in line:
                        env_line_to_remove = line.strip()
                        break
        except FileNotFoundError:
            pass

        if dry_run:
            print(" ")
            print("-" * 80)
            print("Actions that WOULD be performed:")
            print(f"  1. Remove LLM from controller canister ({ctrlb_canister_id})")
            print(f"  2. Update GameState: {field_name} = (controller count after remove)")
            print(f"  3. Wait 180s grace period for in-flight requests")
            print(f"  4. Delete canister {canister_id} (cycles returned to wallet)")
            if json_key_to_remove:
                print(f"  5. Remove '{json_key_to_remove}' ({network}) from {canister_ids_path}")
            else:
                print(f"  5. canister_ids.json: no matching entry found")
            if env_line_to_remove:
                print(f"  6. Remove from {env_path}: {env_line_to_remove}")
            else:
                print(f"  6. canister_ids-{network}.env: no matching entry found")
            print("-" * 80)
            print("DRY RUN complete — nothing was changed.")
            return

        # Step 5: Confirm with user
        print(" ")
        confirm = input(f"Delete {canister_name} ({canister_id}) on '{network}'? This is irreversible. (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Deletion cancelled.")
            return

        # Step 6: Remove LLM from controller
        print(" ")
        print(f"- Removing LLM from controller canister ({ctrlb_canister_id})")
        cmd = ["icp", "canister", "call", ctrlb_canister_id, "remove_llm_canister", f"(record {{canister_id = \"{canister_id}\"}})", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 7: Capture controller's current count for GameState reconciliation
        print(" ")
        print(f"- Verifying LLMs registered in controller canister ({ctrlb_canister_id})")
        cmd = ["icp", "canister", "call", ctrlb_canister_id, "get_llm_canisters", "()", "-e", network]
        print(f"  {' '.join(cmd)} \n  -> from directory: {llm_cwd}")
        result = icp_helpers.call_argv(cmd)
        print(result)

        new_count, _verified_ids = parse_llm_count(result)
        if new_count is None:
            print(f"  WARNING: Could not parse LLM count — skipping GameState update")
        else:
            # Step 8: Reconcile GameState with controller's actual count.
            # This also self-heals any pre-existing drift (e.g. from past
            # deletes that didn't update GameState). If remove_llm_canister
            # was a no-op (404, canister already gone from controller),
            # GameState is still set to whatever the controller actually has.
            print(" ")
            print(f"- Updating GameState: {field_name} = {new_count}")
            cmd = ["icp", "canister", "call", gamestate_canister_id, "setCyclesFlowAdmin", f"(record {{{field_name} = opt ({new_count} : nat);}})", "-e", network]
            run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 9: Wait for in-flight requests
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

        # Step 10: Delete the canister (cycles returned to wallet)
        print(" ")
        print(f"- Deleting canister {canister_name} ({canister_id})")
        cmd = ["icp", "canister", "delete", canister_id, "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 11: Remove entry from canister_ids.json
        print(" ")
        print(f"- Removing entry from canister_ids.json")
        if json_key_to_remove and canister_ids_data:
            del canister_ids_data[json_key_to_remove][network]
            if not canister_ids_data[json_key_to_remove]:
                del canister_ids_data[json_key_to_remove]
            with open(canister_ids_path, "w") as f:
                json.dump(canister_ids_data, f, indent=2)
                f.write("\n")
            print(f"  Removed '{json_key_to_remove}' ({network}) from {canister_ids_path}")
        else:
            print(f"  WARNING: Canister {canister_id} not found in {canister_ids_path}")

        # Step 12: Remove entry from canister_ids-{network}.env
        print(" ")
        print(f"- Removing entry from canister_ids-{network}.env")
        try:
            with open(env_path) as f:
                lines = f.readlines()

            new_lines = []
            removed_line = None
            for line in lines:
                if canister_id in line and "=" in line:
                    removed_line = line.strip()
                    continue
                new_lines.append(line)

            if removed_line:
                with open(env_path, "w") as f:
                    f.writelines(new_lines)
                print(f"  Removed: {removed_line}")
            else:
                print(f"  WARNING: Canister {canister_id} not found in {env_path}")
        except FileNotFoundError:
            print(f"  WARNING: {env_path} not found")

        # Step 13: Summary
        print(" ")
        print("=" * 80)
        print(f"Successfully deleted {canister_name} ({canister_id}) on '{network}'.")
        if balance is not None:
            print(f"Cycles balance at time of deletion: {balance:,}")
        print("Remaining cycles have been returned to the cycles wallet.")
        print("=" * 80)

    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to delete LLM canister {canister_id} on network {network}")


def main(network, canister_id_, dry_run=False):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    challenger_name = None
    challenger_canister_id = None
    judge_name = None
    judge_canister_id = None
    share_service_name = None
    share_service_canister_id = None
    gamestate_canister_id = None
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
        elif "GAMESTATE" in name.upper():
            gamestate_canister_id = id

    if not challenger_canister_id:
        print(f"No CHALLENGER canister found in canisters-{network}.env")
        return
    if not judge_canister_id:
        print(f"No JUDGE canister found in canisters-{network}.env")
        return
    if not share_service_canister_id:
        print(f"No SHARE_SERVICE canister found in canisters-{network}.env")
        return
    if not gamestate_canister_id:
        print(f"No GAMESTATE canister found in canister_ids-{network}.env")
        return

    # Find the target canister
    target_name = None
    target_id = None
    for name, id in CANISTERS.items():
        if "LLM" not in name.upper():
            continue
        if id == canister_id_:
            target_name = name
            target_id = id
            break

    if not target_id:
        print(f"ERROR: Canister {canister_id_} not found in canister_ids-{network}.env")
        return

    print(" ")
    print("=" * 80)
    print(f"Target: {target_name} ({target_id}) on network '{network}'")
    print("=" * 80)

    delete_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, gamestate_canister_id, target_name, target_id, network, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete an LLM canister.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        required=True,
        help="Specify the canister ID to delete",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id, dry_run=args.dry_run)
