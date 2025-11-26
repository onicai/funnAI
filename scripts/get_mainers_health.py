#!/usr/bin/env python3

import argparse
import os
import subprocess
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
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


def is_transient_error(error_text: str) -> bool:
    """Check if error message indicates a transient error worth retrying."""
    if not error_text:
        return False

    # Transient errors that should be retried
    transient_indicators = [
        "timeout",
        "Timeout",
        "timed out",
        "Operation timed out",
        "tcp connect error",
        "connection refused",
        "Connection refused",
        "temporarily unavailable",
        "error sending request",
        "client error (Connect)"
    ]
    return any(indicator in error_text for indicator in transient_indicators)


def run_command_with_retry(cmd: list, timeout: int = 10, max_retries: int = 5, retry_delay: float = 10.0):
    """
    Run a command with retry on transient errors.

    Args:
        cmd: Command to run as list of strings
        timeout: Timeout for command in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Base delay between retries in seconds (exponential backoff)

    Returns:
        subprocess.CompletedProcess if successful, None otherwise
    """
    attempt = 0
    while attempt < max_retries:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True)
            return result
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            attempt += 1

            # Collect error messages
            error_text = str(e)
            if hasattr(e, 'stderr') and e.stderr:
                error_text += " " + e.stderr
            if hasattr(e, 'stdout') and e.stdout:
                error_text += " " + e.stdout

            # Check if we should retry
            if attempt < max_retries and is_transient_error(error_text):
                delay = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                time.sleep(delay)
                continue

            # Not retrying - return None
            return None
        except Exception:
            return None

    return None


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


def get_canister_wasm_hash(network: str, canister_id: str) -> Optional[str]:
    """Get the wasm hash of a canister with retry on transient network errors."""
    cmd = [
        "dfx", "canister", "--network", network, "info", canister_id
    ]
    result = run_command_with_retry(cmd, timeout=10, max_retries=5, retry_delay=10.0)

    if not result:
        return None

    for line in result.stdout.split('\n'):
        if 'Module hash:' in line:
            return line.split(':')[1].strip()
    return None


def check_health_quiet(network: str, canister_id: str) -> bool:
    """
    Check the health of a canister without verbose logging.
    Based on check_health from upgrade_mainers.py but simplified for health checks.
    Uses retry logic for transient errors.
    """
    cmd = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "health"
    ]
    result = run_command_with_retry(cmd, timeout=10, max_retries=5, retry_delay=10.0)

    if not result:
        return False

    output = result.stdout.strip()

    # Check for successful health response
    # (Sometimes dfx fails to parse the candid and shows numeric variant)
    if "(variant { Ok = record { status_code = 200 : nat16 } })" in output or \
       "(variant { 17_724 = record { 3_475_804_314 = 200 : nat16 } })" in output:
        return True
    else:
        return False


def check_health_worker(network: str, name: str, canister_id: str, index: int, total: int, target_hash: Optional[str] = None):
    """Worker function to check health of a single canister and optionally verify hash."""
    is_healthy = check_health_quiet(network, canister_id)

    # Get hash if target hash is provided
    current_hash = None
    hash_matches = None
    if target_hash:
        current_hash = get_canister_wasm_hash(network, canister_id)
        if current_hash:
            hash_matches = (current_hash == target_hash)
        else:
            hash_matches = False  # Couldn't get hash

    # Determine overall status
    if is_healthy and (target_hash is None or hash_matches):
        log_message(f"{canister_id} is healthy" + (f" (hash OK)" if target_hash else ""), "SUCCESS", index, total)
        status = "healthy"
    elif not is_healthy:
        log_message(f"{canister_id} is unhealthy", "ERROR", index, total)
        status = "unhealthy"
    elif target_hash and not hash_matches:
        log_message(f"{canister_id} hash mismatch (expected: {target_hash[:12]}..., got: {current_hash[:12] if current_hash else 'N/A'}...)", "ERROR", index, total)
        status = "hash_mismatch"
    else:
        status = "unknown"

    result = {
        "name": name,
        "id": canister_id,
        "status": status,
        "is_healthy": is_healthy
    }

    if target_hash:
        result["current_hash"] = current_hash
        result["hash_matches"] = hash_matches

    return result


def main(network, workers=10, target_hash=None):
    log_message("=" * 100)
    log_message(f"Checking health of all mAIners on network '{network}'")
    log_message(f"Using {workers} parallel workers")
    if target_hash:
        log_message(f"Target hash: {target_hash}")
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
    hash_mismatch_mainers = []

    log_message(f"Starting health check for {total_mainers} mAIners...")

    # Process health checks in parallel
    processed = 0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all health check tasks
        future_to_canister = {
            executor.submit(check_health_worker, network, name, canister_id, idx + 1, total_mainers, target_hash): (name, canister_id)
            for idx, (name, canister_id) in enumerate(CANISTERS.items())
        }

        # Process results as they complete
        for future in as_completed(future_to_canister):
            processed += 1
            try:
                result = future.result()
                if result["status"] == "hash_mismatch":
                    hash_mismatch_mainers.append(result)
                elif result["is_healthy"]:
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
    log_message(f"Healthy mAIners       : {len(healthy_mainers)}", "SUCCESS" if len(unhealthy_mainers) == 0 and len(hash_mismatch_mainers) == 0 else "INFO")
    log_message(f"Unhealthy mAIners     : {len(unhealthy_mainers)}", "ERROR" if len(unhealthy_mainers) > 0 else "INFO")
    if target_hash:
        log_message(f"Hash mismatch mAIners : {len(hash_mismatch_mainers)}", "ERROR" if len(hash_mismatch_mainers) > 0 else "INFO")
    log_message("")

    # Print details of unhealthy mainers
    if unhealthy_mainers:
        log_message("=" * 100)
        log_message("UNHEALTHY MAINERS DETAILS", "ERROR")
        log_message("=" * 100)
        for mainer in unhealthy_mainers:
            log_message(f"{mainer['name']} ({mainer['id']})", "ERROR")
        log_message("")

    # Print details of hash mismatch mainers
    if hash_mismatch_mainers:
        log_message("=" * 100)
        log_message("HASH MISMATCH MAINERS DETAILS", "ERROR")
        log_message("=" * 100)
        for mainer in hash_mismatch_mainers:
            current_hash_short = mainer.get('current_hash', 'N/A')[:12] if mainer.get('current_hash') else 'N/A'
            log_message(f"{mainer['id']} ({mainer['name']}) - Current hash: {current_hash_short}...", "ERROR")
        log_message("")

    # Final message
    if not unhealthy_mainers and not hash_mismatch_mainers:
        log_message("All mAIners are healthy" + (" and have the correct hash!" if target_hash else "!"), "SUCCESS")
        log_message("")

    # Save results to JSON file with date prefix
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    logs_dir = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")
    os.makedirs(logs_dir, exist_ok=True)

    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "network": network,
        "target_hash": target_hash,
        "total_mainers": total_mainers,
        "healthy_count": len(healthy_mainers),
        "unhealthy_count": len(unhealthy_mainers),
        "hash_mismatch_count": len(hash_mismatch_mainers),
        "healthy_mainers": healthy_mainers,
        "unhealthy_mainers": unhealthy_mainers,
        "hash_mismatch_mainers": hash_mismatch_mainers
    }

    json_file_path = os.path.join(logs_dir, f"{date_prefix}-get_mainers_health-{network}.json")
    with open(json_file_path, 'w') as f:
        json.dump(results, f, indent=2)

    log_message(f"Results saved to: {os.path.abspath(json_file_path)}", "INFO")
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
    parser.add_argument(
        "--target-hash",
        type=str,
        default=None,
        help="Target wasm hash to verify all mAIners against",
    )
    args = parser.parse_args()
    main(args.network, args.workers, args.target_hash)
