#!/usr/bin/env python3

import argparse
import os
from collections import defaultdict
from datetime import datetime

from .get_mainers import get_mainers

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "logs-check-mainers")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "check-mainer-duplicate-creationTimestamp.md")


def check_duplicate_timestamps(network):
    """Check for mAIners with duplicate creationTimestamp values."""
    print("----------------------------------------------")
    print(f"Checking for duplicate creationTimestamps on network: {network}")
    print("----------------------------------------------")

    mainers = get_mainers(network)

    if not mainers:
        print("No mainers found.")
        return

    print(f"Total mainers: {len(mainers)}")

    # Group mainers by creationTimestamp
    timestamp_to_mainers = defaultdict(list)

    for mainer in mainers:
        address = mainer.get('address', '')
        timestamp = mainer.get('creationTimestamp', '')
        owned_by = mainer.get('ownedBy', '')

        if address and timestamp:
            timestamp_to_mainers[timestamp].append({
                'address': address,
                'ownedBy': owned_by,
                'creationTimestamp': timestamp
            })

    # Find duplicates (timestamps with more than one mAIner)
    duplicates = {ts: mainers for ts, mainers in timestamp_to_mainers.items() if len(mainers) > 1}

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write results to markdown file
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Duplicate creationTimestamp Check\n\n")
        f.write(f"**Network:** {network}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total mAIners:** {len(mainers)}\n\n")

        if not duplicates:
            f.write("## Result\n\n")
            f.write("No duplicate creationTimestamps found.\n")
            f.write("All mAIners have unique creationTimestamps.\n")
            print("No duplicate creationTimestamps found.")
            print(f"Results written to: {OUTPUT_FILE}")
            return

        total_affected = sum(len(m) for m in duplicates.values())
        f.write(f"## Summary\n\n")
        f.write(f"- **Duplicate timestamps:** {len(duplicates)}\n")
        f.write(f"- **Affected mAIners:** {total_affected}\n\n")

        f.write("## Details\n\n")

        for timestamp, mainers_list in sorted(duplicates.items()):
            # Convert timestamp (nanoseconds) to human-readable format
            try:
                ts_seconds = int(timestamp) / 1_000_000_000
                human_time = datetime.fromtimestamp(ts_seconds).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, OSError):
                human_time = "N/A"

            f.write(f"### Timestamp: `{timestamp}` ({human_time})\n\n")
            f.write(f"**Count:** {len(mainers_list)} mAIners share this timestamp\n\n")

            # Calculate column widths for alignment (including backticks)
            addr_width = max(len(f"`{m['address']}`") for m in mainers_list)
            addr_width = max(addr_width, len("Address"))
            owner_width = max(len(f"`{m['ownedBy']}`") for m in mainers_list)
            owner_width = max(owner_width, len("Owner"))

            # Write aligned table
            f.write(f"| {'Address':<{addr_width}} | {'Owner':<{owner_width}} |\n")
            f.write(f"| {'-' * addr_width} | {'-' * owner_width} |\n")

            for mainer in mainers_list:
                addr = f"`{mainer['address']}`"
                owner = f"`{mainer['ownedBy']}`"
                f.write(f"| {addr:<{addr_width}} | {owner:<{owner_width}} |\n")

            f.write("\n")

    print(f"Found {len(duplicates)} duplicate timestamps affecting {total_affected} mAIners")
    print(f"Results written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for duplicate mAIner creationTimestamps.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    check_duplicate_timestamps(args.network)
