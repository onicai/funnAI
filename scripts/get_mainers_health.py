#!/usr/bin/env python3

import argparse
import os
import subprocess
from datetime import datetime

from .monitor_common import get_canisters

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Color codes for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log_message(message: str, level: str = "INFO", current: int = None, total: int = None):
    """Log messages with timestamps and progress indicator."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if level == "ERROR":
        color = RED
    elif level == "SUCCESS":
        color = GREEN
    else:
        color = BLUE

    # Add progress indicator if provided
    progress = ""
    if current is not None and total is not None:
        progress = f" ({current}/{total})"

    print(f"{color}[{timestamp}]{progress} {level}: {message}{NC}")


def check_health_quiet(network: str, canister_id: str) -> bool:
    """
    Check the health of a canister without verbose logging.
    Based on check_health from upgrade_mainers.py but simplified for health checks.
    """
    try:
        cmd = [
            "dfx", "canister", "--network", network, "call",
            canister_id, "health"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=True)
        output = result.stdout.strip()

        # Check for successful health response
        # (Sometimes dfx fails to parse the candid and shows numeric variant)
        if "(variant { Ok = record { status_code = 200 : nat16 } })" in output or \
           "(variant { 17_724 = record { 3_475_804_314 = 200 : nat16 } })" in output:
            return True
        else:
            return False
    except Exception:
        return False


def main(network):
    log_message("=" * 100)
    log_message(f"Checking health of all mAIners on network '{network}'")
    log_message("=" * 100)

    # Get all mainers using the existing infrastructure
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "mainers")

    if not CANISTERS:
        log_message(f"No mainers found for network '{network}'", "ERROR")
        log_message(f"Make sure to run: scripts/get_mainers.sh --network {network}", "INFO")
        return

    total_mainers = len(CANISTERS)
    healthy_mainers = []
    unhealthy_mainers = []

    log_message(f"Starting health check for {total_mainers} mAIners...")

    processed = 0
    for name, canister_id in CANISTERS.items():
        processed += 1

        is_healthy = check_health_quiet(network, canister_id)

        if is_healthy:
            log_message(f"{canister_id} is healthy", "SUCCESS", processed, total_mainers)
            healthy_mainers.append({
                "name": name,
                "id": canister_id,
                "status": "healthy"
            })
        else:
            log_message(f"{canister_id} is unhealthy", "ERROR", processed, total_mainers)
            unhealthy_mainers.append({
                "name": name,
                "id": canister_id,
                "status": "unhealthy"
            })

    # Print summary
    log_message("")
    log_message("=" * 100)
    log_message("HEALTH CHECK SUMMARY")
    log_message("=" * 100)
    log_message(f"Total mAIners checked : {total_mainers}")
    log_message(f"Healthy mAIners       : {len(healthy_mainers)}", "SUCCESS" if len(unhealthy_mainers) == 0 else "INFO")
    log_message(f"Unhealthy mAIners     : {len(unhealthy_mainers)}", "ERROR" if len(unhealthy_mainers) > 0 else "INFO")
    log_message("")

    # Print details of unhealthy mainers
    if unhealthy_mainers:
        log_message("=" * 100)
        log_message("UNHEALTHY MAINERS DETAILS", "ERROR")
        log_message("=" * 100)
        for mainer in unhealthy_mainers:
            log_message(f"{mainer['name']} ({mainer['id']})", "ERROR")
        log_message("")
    else:
        log_message("All mAIners are healthy!", "SUCCESS")
        log_message("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check health status of all mAIners.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    args = parser.parse_args()
    main(args.network)
