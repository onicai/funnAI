#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json

from .monitor_common import get_canisters, run_this_cmd, get_balance

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))


def delete_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, canister_name, canister_id, network, dry_run=False):
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
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "get_llm_canisters", "--output", "json"]
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
            print(f"  2. Wait 180s grace period for in-flight requests")
            print(f"  3. Delete canister {canister_id} (cycles returned to wallet)")
            if json_key_to_remove:
                print(f"  4. Remove '{json_key_to_remove}' ({network}) from {canister_ids_path}")
            else:
                print(f"  4. canister_ids.json: no matching entry found")
            if env_line_to_remove:
                print(f"  5. Remove from {env_path}: {env_line_to_remove}")
            else:
                print(f"  5. canister_ids-{network}.env: no matching entry found")
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
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "remove_llm_canister", f"(record {{canister_id = \"{canister_id}\"}})"]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(" ")
        print(f"- Verifying LLMs registered in controller canister ({ctrlb_canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", ctrlb_canister_id, "get_llm_canisters", "--output", "json"]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 7: Wait for in-flight requests
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

        # Step 8: Delete the canister (cycles returned to wallet)
        print(" ")
        print(f"- Deleting canister {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "delete", canister_id]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        # Step 9: Remove entry from canister_ids.json
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

        # Step 10: Remove entry from canister_ids-{network}.env
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

        # Step 11: Summary
        print(" ")
        print("=" * 80)
        print(f"Successfully deleted {canister_name} ({canister_id}) on '{network}'.")
        if balance is not None:
            print(f"Cycles balance at time of deletion: {balance:,}")
        print("Remaining cycles have been returned to the cycles wallet.")
        print("=" * 80)
        print("\nManual step required:")
        print(f"  Remove the LLM canister from funnAI_django's CanisterRegistry.")
        print(f"  See: funnAI_django/src/apps/canisters/management/commands/import_canister_ids.py")
        print(f"  (used by funnAI_django/src/apps/celery_tasks/tasks/cache_cleanup_tasks.py)")

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

    delete_llm(challenger_canister_id, judge_canister_id, share_service_canister_id, target_name, target_id, network, dry_run=dry_run)


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
