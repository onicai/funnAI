#!/usr/bin/env python3

import argparse
import os
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .monitor_common import get_canisters

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Color codes for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Thread lock for synchronized printing
print_lock = threading.Lock()


def log_message(message: str, level: str = "INFO", current: int = None, total: int = None):
    """Log messages with timestamps and progress indicator (thread-safe)."""
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

    with print_lock:
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


def check_health_worker(network: str, name: str, canister_id: str, index: int, total: int):
    """Worker function to check health of a single canister."""
    is_healthy = check_health_quiet(network, canister_id)

    if is_healthy:
        log_message(f"{canister_id} is healthy", "SUCCESS", index, total)
    else:
        log_message(f"{canister_id} is unhealthy", "ERROR", index, total)

    return {
        "name": name,
        "id": canister_id,
        "status": "healthy" if is_healthy else "unhealthy",
        "is_healthy": is_healthy
    }


def main(network, workers=10):
    log_message("=" * 100)
    log_message(f"Checking health of all mAIners on network '{network}'")
    log_message(f"Using {workers} parallel workers")
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

    # Process health checks in parallel
    processed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all health check tasks
        future_to_canister = {
            executor.submit(check_health_worker, network, name, canister_id, idx + 1, total_mainers): (name, canister_id)
            for idx, (name, canister_id) in enumerate(CANISTERS.items())
        }

        # Process results as they complete
        for future in as_completed(future_to_canister):
            processed += 1
            try:
                result = future.result()
                if result["is_healthy"]:
                    healthy_mainers.append(result)
                else:
                    unhealthy_mainers.append(result)
            except Exception as e:
                name, canister_id = future_to_canister[future]
                log_message(f"Exception checking {canister_id}: {e}", "ERROR", processed, total_mainers)
                unhealthy_mainers.append({
                    "name": name,
                    "id": canister_id,
                    "status": "error",
                    "is_healthy": False
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
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers for health checks (default: 10)",
    )
    args = parser.parse_args()
    main(args.network, args.workers)
