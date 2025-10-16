#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json
from collections import defaultdict
from datetime import datetime
from dotenv import dotenv_values

from scripts.cleanup_llm_promptcache import cleanup_llm_promptcache

from .monitor_common import get_canisters, run_this_cmd

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

# Color codes for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log_message(message: str, level: str = "INFO", current: int = None, total: int = None):
    """Log messages with timestamps and progress indicator."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if level == "ERROR":
        color = RED
    elif level == "WARNING":
        color = YELLOW
    elif level == "SUCCESS":
        color = GREEN
    else:
        color = BLUE

    # Add progress indicator if provided
    progress = ""
    if current is not None and total is not None:
        progress = f" ({current}/{total})"

    print(f"{color}[{timestamp}]{progress} {level}: {message}{NC}")
    

def delete_snapshots(canister_name, canister_id, network, dry_run=False, current=None, total=None):
    """Delete snapshot_ids for a given canister."""
    try:
        log_message(f"Getting list of snapshots for {canister_name} ({canister_id})", "INFO", current, total)
        cmd = ["dfx", "canister", "--network", network, "snapshot", "list", canister_id]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)

        if "No snapshots found" in result:
            log_message(f"No snapshots found for {canister_name} ({canister_id})", "INFO", current, total)
            return 0

        # Parse the result to extract snapshot_id IDs
        snapshot_ids = []
        for line in result.splitlines():
            snapshot_id = line.split(":")[0].strip()
            if snapshot_id:
             snapshot_ids.append(snapshot_id)

        log_message(f"Found {len(snapshot_ids)} snapshot(s) for {canister_name} ({canister_id})", "INFO", current, total)

        deleted_count = 0
        for i, snapshot_id in enumerate(snapshot_ids, 1):
            if dry_run:
                log_message(f"[DRY RUN] Would delete snapshot {i}/{len(snapshot_ids)}: {snapshot_id}", "WARNING", current, total)
            else:
                log_message(f"Deleting snapshot {i}/{len(snapshot_ids)}: {snapshot_id}", "INFO", current, total)
                cmd = ["dfx", "canister", "--network", network, "snapshot", "delete", canister_id, snapshot_id]
                subprocess.run(cmd, check=True, text=True, cwd=FUNNAI_DIR, capture_output=True)
                deleted_count += 1

        if dry_run:
            log_message(f"[DRY RUN] Would have deleted {len(snapshot_ids)} snapshot(s) for {canister_name}", "SUCCESS", current, total)
        else:
            log_message(f"Deleted {deleted_count} snapshot(s) for {canister_name}", "SUCCESS", current, total)

        return deleted_count

    except subprocess.CalledProcessError as e:
        log_message(f"ERROR occurred when calling subprocess command", "ERROR", current, total)
        log_message(f"Command: {e.cmd}", "ERROR", current, total)
        log_message(f"Return code: {e.returncode}", "ERROR", current, total)
        if e.output:
            log_message(f"Output: {e.output}", "ERROR", current, total)
        return 0

def main(network, canister_id, canister_types="protocol", dry_run=False):
    log_message("=" * 100)
    log_message(f"Deleting snapshots on network '{network}' for canister types: {canister_types}")
    if dry_run:
        log_message("Running in DRY RUN mode - no snapshots will be deleted", "WARNING")
    log_message("=" * 100)

    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    # Filter canisters based on canister_id parameter
    canisters_to_process = {}
    for name, id in CANISTERS.items():
        if canister_id == "all" or canister_id == id:
            canisters_to_process[name] = id

    total_canisters = len(canisters_to_process)
    if total_canisters == 0:
        log_message(f"No canisters found matching criteria", "WARNING")
        return

    log_message(f"Processing {total_canisters} canister(s)...")

    total_deleted = 0
    processed = 0

    for name, id in canisters_to_process.items():
        processed += 1
        log_message("=" * 100)
        log_message(f"Processing canister {name} ({id})", "INFO", processed, total_canisters)
        deleted = delete_snapshots(name, id, network, dry_run, processed, total_canisters)
        total_deleted += deleted

    log_message("")
    log_message("=" * 100)
    log_message("DELETION SUMMARY", "INFO")
    log_message("=" * 100)
    log_message(f"Total canisters processed: {total_canisters}")
    if dry_run:
        log_message(f"[DRY RUN] Would have deleted {total_deleted} snapshot(s)", "SUCCESS")
    else:
        log_message(f"Total snapshots deleted: {total_deleted}", "SUCCESS")
    log_message("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete snapshot_ids.")
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
    parser.add_argument(
        "--canister-types",
        choices=["all", "protocol", "mainers"],
        default="protocol",
        help="Specify the canister types to process (default: protocol)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually deleting snapshots",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id, args.canister_types, args.dry_run)
