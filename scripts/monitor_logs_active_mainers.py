#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
import json
from collections import defaultdict
from datetime import datetime

from .get_mainers import get_mainers, get_mainer_is_active, get_mainer_setting
from .monitor_common import ensure_log_dir

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

BURN_RATE_GROUPS = ["Low", "Medium", "High", "VeryHigh"]

# Color codes for burn rate groups
BURN_RATE_COLORS = {
    "Low": "\033[38;5;82m",       # green
    "Medium": "\033[38;5;226m",   # yellow
    "High": "\033[38;5;208m",     # orange
    "VeryHigh": "\033[38;5;196m", # red
}
RESET_COLOR = "\033[0m"


def get_logs(canister_id, network):
    """Fetch logs using dfx for a given canister."""
    try:
        output = subprocess.check_output(
            ["icp", "canister", "logs", canister_id, "-e", network],
            stderr=subprocess.DEVNULL,
            text=True
        )
        return output.strip().splitlines()
    except subprocess.CalledProcessError:
        return []


def filter_share_agents(mainers):
    """Filter mAIner list to only ShareAgent type with non-empty addresses."""
    share_agents = []
    for mainer in mainers:
        address = mainer.get('address', '')
        canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
        canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''
        if canister_type == "ShareAgent" and address != "":
            share_agents.append(address)
    return share_agents


def discover_active_mainers(network, limit=None):
    """Fetch all ShareAgent mAIners and return only active ones grouped by burn rate."""
    print(f"Fetching all mAIners from GameState on network '{network}'...")
    mainers = get_mainers(network)
    if not mainers:
        print("ERROR: No mainers found.")
        return {}

    share_agents = filter_share_agents(mainers)
    print(f"Found {len(share_agents)} ShareAgent mAIners.")

    if limit is not None and limit > 0:
        share_agents = share_agents[:limit]
        print(f"Limiting to first {limit} mAIners (for testing).")

    print(f"Checking active status and burn rate for {len(share_agents)} mAIners...")
    grouped = {br: [] for br in BURN_RATE_GROUPS}
    active_count = 0
    paused_count = 0
    skipped_count = 0

    for idx, address in enumerate(share_agents, 1):
        is_active = get_mainer_is_active(network, address)
        if is_active is not True:
            if is_active is False:
                paused_count += 1
            else:
                skipped_count += 1
            continue

        active_count += 1
        setting = get_mainer_setting(network, address)
        if setting in grouped:
            grouped[setting].append(address)
        else:
            # Custom/Unknown/Unable to query — skip
            skipped_count += 1

        if idx % 50 == 0:
            print(f"  Checked {idx}/{len(share_agents)} mAIners...")

    print(f"\nDiscovery complete:")
    print(f"  Active: {active_count}, Paused: {paused_count}, Skipped: {skipped_count}")
    for br in BURN_RATE_GROUPS:
        print(f"  {br}: {len(grouped[br])} active mAIners")

    return grouped


def main(network, delay=3, limit=None):
    # Step 1: Discover active mAIners grouped by burn rate
    grouped = discover_active_mainers(network, limit)

    total_active = sum(len(ids) for ids in grouped.values())
    if total_active == 0:
        print("\nNo active mAIners found. Nothing to monitor.")
        return

    # Step 2: Set up log directories and files
    log_dir = os.path.join(SCRIPT_DIR, f"logs-active-mainers-{network}")
    ensure_log_dir(log_dir)

    log_files = {}
    for br in BURN_RATE_GROUPS:
        if grouped[br]:
            log_path = os.path.join(log_dir, f"burn_rate_{br.lower()}.log")
            # Clear at start
            with open(log_path, "w"):
                pass
            log_files[br] = log_path

    combined_log_path = os.path.join(log_dir, "combined_active.log")
    with open(combined_log_path, "w"):
        pass

    # Write a manifest of which canisters are in each group
    manifest_path = os.path.join(log_dir, "manifest.json")
    manifest = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "network": network,
        "total_active": total_active,
        "groups": {br: grouped[br] for br in BURN_RATE_GROUPS},
    }
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nMonitoring {total_active} active mAIners on '{network}'.")
    print(f"Log directory: {os.path.abspath(log_dir)}")
    print(f"  Combined log: combined_active.log")
    for br in BURN_RATE_GROUPS:
        if grouped[br]:
            print(f"  {br} ({len(grouped[br])} mAIners): burn_rate_{br.lower()}.log")
    print(f"\nChecking every {delay} seconds. Press Ctrl+C to stop.\n")

    # Step 3: Monitor loop
    previous_logs = defaultdict(set)
    first = True

    while True:
        for br in BURN_RATE_GROUPS:
            for canister_id in grouped[br]:
                log_lines = get_logs(canister_id, network)
                new_lines = []
                for line in log_lines:
                    if line not in previous_logs[canister_id]:
                        previous_logs[canister_id].add(line)
                        new_lines.append(line)

                if new_lines:
                    color = BURN_RATE_COLORS.get(br, "")
                    br_log_path = log_files.get(br)

                    with open(combined_log_path, "a") as f_combined:
                        br_file = open(br_log_path, "a") if br_log_path else None
                        try:
                            for line in new_lines:
                                tagged_line = f"[{br}][{canister_id}] {line}"
                                f_combined.write(tagged_line + "\n")
                                if br_file:
                                    br_file.write(f"[{canister_id}] {line}\n")
                                print(f"{color}[{br}]{RESET_COLOR}({canister_id}) {line}")
                        finally:
                            if br_file:
                                br_file.close()

        if first:
            first = False
            print(f"\nInitial log retrieval completed for {total_active} active mAIners.")
            print(f"Will report changes in logs. Checking every {delay} seconds...")

        time.sleep(delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor logs for active ShareAgent mAIners, grouped by burn rate."
    )
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Seconds between log checks (default: 3)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of mainers to check (for testing)",
    )
    args = parser.parse_args()
    main(args.network, args.delay, args.limit)
