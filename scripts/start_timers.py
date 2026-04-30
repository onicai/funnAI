#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir
from .get_mainers import get_mainers
from .check_mAIner_status import (
    is_frozen_error,
    is_transient_error,
    collect_error_text,
    HEALTH_OK_PATTERNS,
)

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def start_timer(canister_id, network):
    """Start timer using dfx for a given canister."""
    try:
        print(f"Starting timer for canister {canister_id} on network {network}...")
        subprocess.run(
            ["dfx", "canister", "--network", network, "call", canister_id, "startTimerExecutionAdmin"],
            check=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to start timer for canister {canister_id} on network {network}")


def check_health_and_start_timer(canister_id, network, index, total):
    """Check if a mAIner is responsive, then start its timer.

    Returns dict with canister_id, status ('started', 'frozen', 'unhealthy', 'error').
    """
    # Step 1: Check health
    cmd = ["dfx", "canister", "--network", network, "call", canister_id, "health"]
    max_retries = 3
    retry_delay = 5.0

    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
            output = result.stdout.strip()
            if any(pattern in output for pattern in HEALTH_OK_PATTERNS):
                break  # Healthy — proceed to start timer
            else:
                print(f"  ({index}/{total}) {canister_id} — unhealthy, skipping")
                return {"canister_id": canister_id, "status": "unhealthy"}
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            error_text = collect_error_text(e)
            if is_frozen_error(error_text):
                print(f"  ({index}/{total}) {canister_id} — FROZEN, skipping")
                return {"canister_id": canister_id, "status": "frozen"}
            if attempt < max_retries and is_transient_error(error_text):
                time.sleep(retry_delay * (2 ** (attempt - 1)))
                continue
            print(f"  ({index}/{total}) {canister_id} — error: {error_text[:100]}, skipping")
            return {"canister_id": canister_id, "status": "error"}
    else:
        print(f"  ({index}/{total}) {canister_id} — max retries exceeded, skipping")
        return {"canister_id": canister_id, "status": "error"}

    # Step 2: Start timer
    cmd = ["dfx", "canister", "--network", network, "call", canister_id, "startTimerExecutionAdmin"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
        print(f"  ({index}/{total}) {canister_id} — timer started")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        error_text = collect_error_text(e)
        print(f"  ({index}/{total}) {canister_id} — failed to start timer: {error_text[:100]}")
        return {"canister_id": canister_id, "status": "error", "logs": []}

    # Step 3: Capture logs after starting timer
    cmd = ["dfx", "canister", "logs", canister_id, "--network", network]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, timeout=30)
        log_lines = output.strip().splitlines()[-20:]  # last 20 lines
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        log_lines = ["(could not fetch logs)"]

    return {"canister_id": canister_id, "status": "started", "logs": log_lines}


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


def main(network, canister_types, workers=10, limit=None, dry_run=False):
    if dry_run:
        print("*** DRY RUN — no timers will be started ***\n")

    # Protocol canisters — use existing .env-based flow
    if canister_types == "protocol":
        (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)
        for name, canister_id in CANISTERS.items():
            if ("GAMESTATE" in name or "CREATOR" in name or "LLM" in name):
                continue
            print("-------------------------------")
            print(f"Canister {name} ({canister_id})")
            if dry_run:
                print(f"  DRY RUN: would start timer for {canister_id}")
            else:
                start_timer(canister_id, network)
        return

    # Mainers — fetch from GameState and check health before starting
    print(f"Fetching mAIners from GameState on network '{network}'...")
    mainers = get_mainers(network)
    if not mainers:
        print(f"ERROR: No mainers found on network '{network}'")
        return

    # Show canister type breakdown for verification
    type_counts = defaultdict(int)
    for mainer in mainers:
        address = mainer.get('address', '')
        canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
        canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else 'Unknown'
        if address:
            type_counts[canister_type] += 1
    print(f"Canister type breakdown:")
    for ct, count in sorted(type_counts.items()):
        selected = " <-- SELECTED" if ct == "ShareAgent" else " (skipped)"
        print(f"  {ct}: {count}{selected}")

    share_agents = filter_share_agents(mainers)
    print(f"\nFiltered to {len(share_agents)} ShareAgent mAIners.")

    if limit is not None and limit > 0:
        share_agents = share_agents[:limit]
        print(f"Limiting to first {limit} mAIners (for testing).")

    if dry_run:
        print(f"\nDRY RUN: Would check health and start timers for {len(share_agents)} ShareAgent mAIners:")
        for idx, cid in enumerate(share_agents, 1):
            print(f"  {idx}. {cid}")
        print(f"\nDRY RUN complete. Re-run without --dry-run to execute.")
        return

    total = len(share_agents)
    print(f"\nStarting timers for {total} mAIners (checking health first)...")
    print(f"Using {workers} parallel workers.\n")

    # Process in parallel
    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {
            executor.submit(
                check_health_and_start_timer, cid, network, idx + 1, total
            ): cid
            for idx, cid in enumerate(share_agents)
        }
        for future in as_completed(future_to_id):
            try:
                results.append(future.result())
            except Exception as e:
                cid = future_to_id[future]
                print(f"  {cid} — exception: {e}")
                results.append({"canister_id": cid, "status": "error", "logs": []})

    # Summary
    counts = defaultdict(int)
    for r in results:
        counts[r["status"]] += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Started : {counts['started']}")
    print(f"  Frozen  : {counts['frozen']} (skipped)")
    print(f"  Unhealthy: {counts['unhealthy']} (skipped)")
    print(f"  Errors  : {counts['error']} (skipped)")
    print(f"  Total   : {total}")
    print()

    # Write log files
    from datetime import datetime
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(SCRIPT_DIR, f"logs-start-timers-{network}")
    ensure_log_dir(log_dir)

    combined_path = os.path.join(log_dir, f"{date_prefix}-start_timers-{network}.log")
    with open(combined_path, "w") as f_combined:
        for r in sorted(results, key=lambda x: x["canister_id"]):
            cid = r["canister_id"]
            logs = r.get("logs", [])

            # Individual log file
            individual_path = os.path.join(log_dir, f"{cid}.log")
            with open(individual_path, "w") as f_ind:
                f_ind.write(f"# Status: {r['status']}\n")
                for line in logs:
                    f_ind.write(line + "\n")

            # Combined log
            f_combined.write(f"=== {cid} ({r['status']}) ===\n")
            for line in logs:
                f_combined.write(f"  {line}\n")
            f_combined.write("\n")

    print(f"Logs saved to: {os.path.abspath(log_dir)}")
    print(f"  Combined: {os.path.abspath(combined_path)}")
    print(f"  Per-canister: {len(results)} individual .log files")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-types",
        choices=["all", "protocol", "mainers"],
        default="protocol",
        help="Specify the canister type (default: protocol)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of mainers to process (for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually starting timers",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types, args.workers, args.limit, args.dry_run)
