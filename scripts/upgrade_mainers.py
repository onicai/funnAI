#!/usr/bin/env python3
"""
mAIner Upgrade Script

This script safely upgrades mAIner canisters with health checks, snapshots, and rollback capability.

To run the upgrade in a safe sequence:
    # from the folder: funnAI
    conda activate llama_cpp_canister
    
    # Upgrade 1 mAIner of IConfucius on production network confirmation prompt:
    USER=xijdk-rtoet-smgxl-a4apd-ahchq-bslha-ope4a-zlpaw-ldxat-prh6f-jqe
    scripts/upgrade_mainers.sh --network prd --user $USER --num 1 --ask-before-upgrade [--dry-run]
    # -> Now you know the target hash
    TARGET_HASH=0xf2a40400e1f0cc0896c976eb2efa7a902aff68266b69b4a6be0a077b022db819

    # By providing the target hash, the script will skip upgrade for mAIners already at that hash and healthy

    # Upgrade 2 mAIner of IConfucius on production network confirmation prompt:
    scripts/upgrade_mainers.sh --network prd --user $USER --target-hash $TARGET_HASH --num 2 --ask-before-upgrade [--dry-run]

    # Upgrade ALL mAIners of IConfucius on production network confirmation prompt:
    scripts/upgrade_mainers.sh --network prd --user $USER --target-hash $TARGET_HASH --ask-before-upgrade [--dry-run]

    # Upgrade 1 mAIner on production network confirmation prompt:
    scripts/upgrade_mainers.sh --network prd --num 1 --target-hash $TARGET_HASH --ask-before-upgrade [--dry-run]

    # Upgrade 100 mainers on production network with target hash and without confirmation prompt:
    scripts/upgrade_mainers.sh --network prd --num 100 --target-hash $TARGET_HASH [--dry-run]

    # Upgrade ALL mainers on production network with target hash and without confirmation prompt:
    scripts/upgrade_mainers.sh --network prd --target-hash $TARGET_HASH [--dry-run]


To run unit tests:
    # from the root of the repository
    conda activate llama_cpp_canister
    pytest scripts/test/test_upgrade_mainers.py -v
"""

import subprocess
import time
import argparse
import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import signal
from pathlib import Path
from enum import Enum

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.resolve()
POAIW_MAINER_DIR = (SCRIPT_DIR / "../PoAIW/src/mAIner").resolve()
POAIW_DFX_JSON_PATH = (POAIW_MAINER_DIR / "dfx.json").resolve()
POAIW_CANISTER_IDS_PATH = (POAIW_MAINER_DIR / "canister_ids.json").resolve()

# Log file path
LOG_FILE_PATH = SCRIPT_DIR / "upgrade_mainers.logs"

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Global flag for interruption handling
interrupted = False

# Global log file handle
log_file_handle = None

# Global progress tracking for logging
current_mainer_index = None
total_mainers_to_process = None

# Status tracking for each mAIner
class MainerStatus(Enum):
    """Status flags for mAIner upgrade process."""
    PENDING = "pending"                          # Not yet processed
    SKIPPED_ALREADY_UPGRADED = "skipped_upgraded"  # Skipped - already at target hash and healthy
    SKIPPED_USER_REQUEST = "skipped_user"        # Skipped - user chose to skip
    SKIPPED_FILTER = "skipped_filter"            # Skipped - filtered out (not ShareAgent, empty address, etc.)
    IN_PROGRESS = "in_progress"                  # Currently being upgraded
    SUCCESS = "success"                          # Successfully upgraded
    FAILED_STOP_TIMER = "failed_stop_timer"      # Failed to stop timer
    FAILED_SNAPSHOT = "failed_snapshot"          # Failed to create snapshot
    FAILED_UPGRADE = "failed_upgrade"            # Failed during upgrade
    FAILED_START = "failed_start"                # Failed to start canister
    FAILED_HEALTH = "failed_health"              # Failed health check after upgrade
    FAILED_START_TIMER = "failed_start_timer"    # Failed to start timer
    FAILED_MAINTENANCE = "failed_maintenance"    # Failed to turn off maintenance flag
    FAILED_OTHER = "failed_other"                # Failed for other reason

# Global dictionary to track status of each mAIner
# Key: canister address, Value: dict with status, timestamp, and optional error message
mainer_status_tracker: Dict[str, Dict] = {}

def update_mainer_status(address: str, status: MainerStatus, error_msg: Optional[str] = None):
    """
    Update the status of a mAIner in the global tracker.

    Args:
        address: Canister address
        status: MainerStatus enum value
        error_msg: Optional error message for failed statuses
    """
    mainer_status_tracker[address] = {
        'status': status,
        'timestamp': datetime.now(),
        'error': error_msg
    }

def get_status_summary() -> Dict[str, int]:
    """
    Get a summary count of mAIners by status.

    Returns:
        Dictionary with status counts
    """
    summary = {}
    for data in mainer_status_tracker.values():
        status = data['status'].value
        summary[status] = summary.get(status, 0) + 1
    return summary

def write_status_to_json(filepath: str = "scripts/upgrade_mainers_status.json"):
    """
    Write the status tracker to a JSON file.

    Args:
        filepath: Path to the JSON file (default: scripts/upgrade_mainers_status.json)
    """
    if not mainer_status_tracker:
        log_message("No status data to write to JSON", "WARNING")
        return

    # Convert to JSON-serializable format
    json_data = {}
    for address, data in mainer_status_tracker.items():
        json_data[address] = {
            'status': data['status'].value,
            'timestamp': data['timestamp'].isoformat(),
            'error': data.get('error')
        }

    try:
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2)
        log_message(f"Status written to {filepath}", "SUCCESS")
    except Exception as e:
        log_message(f"Failed to write JSON status file: {e}", "ERROR")

def write_status_to_markdown(filepath: str = "scripts/upgrade_mainers_status.md"):
    """
    Write the status tracker to a Markdown file with a properly formatted table.

    Args:
        filepath: Path to the Markdown file (default: scripts/upgrade_mainers_status.md)
    """
    if not mainer_status_tracker:
        log_message("No status data to write to Markdown", "WARNING")
        return

    try:
        with open(filepath, 'w') as f:
            # Write header
            f.write("# mAIner Upgrade Status Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Get summary counts
            summary = get_status_summary()
            f.write("## Summary\n\n")
            for status_value in sorted(summary.keys()):
                count = summary[status_value]
                f.write(f"- **{status_value}**: {count}\n")
            f.write(f"\n**Total mAIners tracked:** {len(mainer_status_tracker)}\n\n")

            # Create detailed table
            f.write("## Detailed Status\n\n")

            # Prepare data for table
            rows = []
            max_address_len = len("Canister Address")
            max_status_len = len("Status")
            max_error_len = len("Error/Notes")

            for address, data in sorted(mainer_status_tracker.items()):
                status = data['status'].value
                timestamp = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                error = data.get('error') or '-'

                max_address_len = max(max_address_len, len(address))
                max_status_len = max(max_status_len, len(status))
                max_error_len = max(max_error_len, len(error))

                rows.append({
                    'address': address,
                    'status': status,
                    'timestamp': timestamp,
                    'error': error
                })

            # Write table header
            header = f"| {'Canister Address':{max_address_len}} | {'Status':{max_status_len}} | Timestamp           | {'Error/Notes':{max_error_len}} |"
            separator = f"|{'-' * (max_address_len + 2)}|{'-' * (max_status_len + 2)}|{'-' * 21}|{'-' * (max_error_len + 2)}|"

            f.write(header + "\n")
            f.write(separator + "\n")

            # Write table rows
            for row in rows:
                line = f"| {row['address']:{max_address_len}} | {row['status']:{max_status_len}} | {row['timestamp']} | {row['error']:{max_error_len}} |"
                f.write(line + "\n")

            # Group by status section
            f.write("\n## Grouped by Status\n\n")
            by_status = {}
            for address, data in mainer_status_tracker.items():
                status = data['status']
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append((address, data))

            for status in MainerStatus:
                if status in by_status:
                    items = by_status[status]
                    f.write(f"\n### {status.value.upper()} ({len(items)})\n\n")
                    for address, data in items:
                        error_info = f" - {data['error']}" if data.get('error') else ""
                        f.write(f"- `{address}`{error_info}\n")

        log_message(f"Status written to {filepath}", "SUCCESS")
    except Exception as e:
        log_message(f"Failed to write Markdown status file: {e}", "ERROR")

def print_status_report(processed_count: int = 0):
    """
    Print a concise status report of all mAIners.

    Args:
        processed_count: Number of mAIners that were actually processed (not filtered out)
    """
    if not mainer_status_tracker:
        log_message("No mAIners tracked", "INFO")
        return

    # Get summary counts
    summary = get_status_summary()

    # Count key categories (only for processed mAIners, not filtered ones)
    success_count = summary.get('success', 0)
    failed_count = sum(count for status, count in summary.items() if status.startswith('failed_'))

    # For skipped, only count the ones that were actually checked (not pre-filtered)
    skipped_already_upgraded = summary.get('skipped_upgraded', 0)
    skipped_user = summary.get('skipped_user', 0)
    skipped_processed = skipped_already_upgraded + skipped_user

    # Total that were actually looked at
    total_processed = success_count + failed_count + skipped_processed

    # Print concise summary
    log_message(f"{'='*60}", "INFO")
    log_message("UPGRADE SUMMARY", "INFO")
    log_message(f"Processed: {total_processed} mAIner(s)", "INFO")
    log_message(f"  ✓ Upgraded: {success_count}", "SUCCESS" if success_count > 0 else "INFO")
    log_message(f"  ⊘ Already up-to-date: {skipped_already_upgraded}", "INFO")
    log_message(f"  ⊘ Skipped by user: {skipped_user}", "INFO" if skipped_user == 0 else "WARNING")
    log_message(f"  ✗ Failed: {failed_count}", "ERROR" if failed_count > 0 else "INFO")

    # Show failed mAIners with details if any
    if failed_count > 0:
        log_message("\nFailed mAIners:", "ERROR")
        for address, data in mainer_status_tracker.items():
            if data['status'].value.startswith('failed_'):
                error_msg = f" - {data['error']}" if data.get('error') else ""
                log_message(f"  {address}: {data['status'].value}{error_msg}", "ERROR")

    log_message(f"\nDetailed status saved to:", "INFO")
    log_message(f"  - scripts/upgrade_mainers_status.json", "INFO")
    log_message(f"  - scripts/upgrade_mainers_status.md", "INFO")
    log_message(f"  - scripts/upgrade_mainers.logs", "INFO")
    log_message(f"{'='*60}", "INFO")

def signal_handler(sig, frame):
    """Handle Ctrl+C interruption gracefully."""
    global interrupted, log_file_handle
    interrupted = True
    print(f"\n{RED}Upgrade process interrupted! Current canister may need manual inspection.{NC}")

    # Close log file before exiting
    if log_file_handle:
        log_file_handle.close()

    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def log_message(message: str, level: str = "INFO"):
    """Log messages with timestamps and colors to both console and file."""
    global log_file_handle, current_mainer_index, total_mainers_to_process

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if level == "ERROR":
        color = RED
    elif level == "WARNING":
        color = YELLOW
    elif level == "SUCCESS":
        color = GREEN
    else:
        color = BLUE

    # Add progress indicator if we're in a mainer processing loop
    progress = ""
    if current_mainer_index is not None and total_mainers_to_process is not None:
        progress = f" ({current_mainer_index + 1}/{total_mainers_to_process})"

    # Print to console with color
    console_message = f"{color}[{timestamp}]{progress} {level}: {message}{NC}"
    print(console_message)

    # Write to log file without color codes
    if log_file_handle:
        file_message = f"[{timestamp}]{progress} {level}: {message}\n"
        log_file_handle.write(file_message)
        log_file_handle.flush()  # Ensure it's written immediately

def run_command(
    command: List[str],
    capture_output: bool = True,
    check: bool = True,
    cwd: Optional[str] = None,
    retry_on_transient_errors: bool = False,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    log_stdout: bool = False
) -> subprocess.CompletedProcess:
    """Run a command and return the result.

    Args:
        command: Command to run as list of strings
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise on non-zero exit code
        cwd: Working directory for command
        retry_on_transient_errors: If True, retry on transient errors like timeouts, IC0508, etc.
        max_retries: Maximum number of retry attempts (only used if retry_on_transient_errors=True)
        retry_delay: Base delay between retries in seconds (exponential backoff applied)
        log_stdout: If True, log stdout output line by line (only when capture_output=True)
    """
    # Log the command being executed with details
    cmd_str = ' '.join(command)
    cwd_info = f" (cwd: {cwd})" if cwd else " (cwd: current directory)"
    capture_info = " (capturing output)" if capture_output else " (not capturing output)"
    log_message(f"Executing: {cmd_str}{cwd_info}{capture_info}", "INFO")

    def is_transient_error(stderr: str) -> bool:
        """Check if error message indicates a transient error worth retrying."""
        if not stderr:
            return False

        # Non-transient errors that should NOT be retried
        non_transient_indicators = [
            "IC0536",  # Method not found - permanent error
            "has no update method",
            "has no query method",
        ]
        if any(indicator in stderr for indicator in non_transient_indicators):
            return False

        # Transient errors that SHOULD be retried
        transient_indicators = [
            "Failed query call",
            "CanisterError",
            "IC0508",  # Canister stopped
            "IC0503",  # Canister trapped
            "timeout",
            "Timeout",
            "timed out",  # Operation timed out
            "Operation timed out",
            "tcp connect error",
            "connection refused",
            "Connection refused",
            "temporarily unavailable",
            "error sending request",  # Network request errors
            "client error (Connect)"  # Connection errors
        ]
        return any(indicator in stderr for indicator in transient_indicators)

    attempt = 0
    while True:
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, check=check, cwd=cwd)
                # Log stdout if requested (useful for dfx deploy output)
                if log_stdout and result.stdout and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            log_message(line, "INFO")
                return result
            else:
                result = subprocess.run(command, check=check, cwd=cwd)
                return result
        except subprocess.CalledProcessError as e:
            attempt += 1

            # Collect error messages from all available sources
            error_text = ""
            if hasattr(e, 'stderr') and e.stderr:
                error_text += e.stderr
            if hasattr(e, 'stdout') and e.stdout:
                error_text += " " + e.stdout
            error_text += " " + str(e)

            # Check if we should retry
            should_retry = (
                retry_on_transient_errors
                and attempt < max_retries
                and is_transient_error(error_text)
            )

            if should_retry:
                delay = retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                log_message(f"Transient error detected (attempt {attempt}/{max_retries}). Retrying in {delay}s...", "WARNING")
                if e.stderr:
                    log_message(f"Error was: {e.stderr.strip()}", "WARNING")
                elif str(e):
                    log_message(f"Error was: {str(e)}", "WARNING")
                time.sleep(delay)
                continue

            # Not retrying - log and raise
            log_message(f"Command failed: {' '.join(command)}", "ERROR")
            if e.stderr:
                log_message(f"Error output: {e.stderr}", "ERROR")
            raise

def get_mainers(network: str) -> List[Dict]:
    """Get all mainers from game state canister."""
    log_message(f"Getting all mAIners from game_state_canister on network {network}...")
    try:
        result = run_command([
            "dfx", "canister", "--network", network, "call",
            "game_state_canister", "getMainerAgentCanistersAdmin",
            "--output", "json"
        ])
        data = json.loads(result.stdout)
        mainers = data.get('Ok', [])
        log_message(f"Found {len(mainers)} total mAIners (Unfiltered, still includes empty address + ShareService)", "INFO")
        return mainers
    except Exception as e:
        log_message(f"Failed to get mAIners: {e}", "ERROR")
        sys.exit(1)

def get_canister_status(network: str, canister_id: str) -> Optional[str]:
    """Get the status of a canister (Running, Stopping, or Stopped) with retry on transient network errors.

    Handles out-of-cycles errors by automatically topping up the canister with cycles.
    """
    def is_out_of_cycles_error(error_text: str) -> bool:
        """Check if error indicates canister is out of cycles."""
        return "is out of cycles" in error_text and "IC0207" in error_text

    max_attempts = 2  # Initial attempt + 1 retry after topping up

    for attempt in range(1, max_attempts + 1):
        try:
            result = run_command([
                "dfx", "canister", "--network", network, "status", canister_id
            ], retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
            for line in result.stdout.split('\n'):
                if line.startswith('Status:'):
                    return line.split(':')[1].strip()
            return None
        except subprocess.CalledProcessError as e:
            error_text = ""
            if hasattr(e, 'stderr') and e.stderr:
                error_text = e.stderr
            if hasattr(e, 'stdout') and e.stdout:
                error_text += " " + e.stdout
            error_text += " " + str(e)

            # Check if this is an out-of-cycles error
            if is_out_of_cycles_error(error_text) and attempt < max_attempts:
                log_message(f"Canister {canister_id} is out of cycles", "WARNING")
                log_message(f"Sending 500,000,000,000 cycles to canister...", "INFO")

                try:
                    # Send cycles using dfx wallet
                    send_result = run_command([
                        "dfx", "wallet", "--network", network, "send", canister_id, "500_000_000_000"
                    ])
                    log_message(f"Successfully sent cycles to {canister_id}", "SUCCESS")

                    # Wait 10 seconds before retrying
                    log_message(f"Waiting 10 seconds before retrying status check...", "INFO")
                    time.sleep(10)

                    # Loop will continue to retry
                    continue
                except Exception as send_error:
                    log_message(f"Failed to send cycles to {canister_id}: {send_error}", "ERROR")
                    return None
            else:
                # Not an out-of-cycles error, or we've exhausted retries
                log_message(f"Failed to get status for {canister_id}: {e}", "WARNING")
                return None
        except Exception as e:
            log_message(f"Failed to get status for {canister_id}: {e}", "WARNING")
            return None

    # If we get here, all attempts failed
    log_message(f"Failed to get status for {canister_id} after {max_attempts} attempts", "ERROR")
    return None

def get_canister_wasm_hash(network: str, canister_id: str) -> Optional[str]:
    """Get the wasm hash of a canister with retry on transient network errors."""
    try:
        result = run_command([
            "dfx", "canister", "--network", network, "info", canister_id
        ], retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        for line in result.stdout.split('\n'):
            if 'Module hash:' in line:
                return line.split(':')[1].strip()
        return None
    except Exception as e:
        log_message(f"Failed to get wasm hash for {canister_id}: {e}", "WARNING")
        return None

def stop_timer(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Stop the timer execution for a canister with retry on transient network errors."""
    log_message(f"Stopping timer for {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "stopTimerExecutionAdmin"
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # Check if the response indicates success (Ok variant)
        # Valid responses include:
        # - "You stopped the timers: ..."
        # - "No timers were running"
        if 'variant { Ok' in result.stdout or  'variant { 17_724' in result.stdout:
            log_message(f"Timer stopped for {canister_id}", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when stopping timer: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to stop timer for {canister_id}: {e}", "ERROR")
        return False

def start_timer(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Start the timer execution for a canister with retry on transient network errors."""
    log_message(f"Starting timer for {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "startTimerExecutionAdmin"
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # Check for the exact expected response
        expected_response = '(variant { Ok = record { auth = "You started the timers:  1, " } })'
        if expected_response in result.stdout:
            log_message(f"Timer started for {canister_id}", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when starting timer: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to start timer for {canister_id}: {e}", "ERROR")
        return False

def check_queue(network: str, canister_id: str) -> Tuple[bool, Optional[datetime]]:
    """Check the queue for a canister and return status and last entry time."""
    log_message(f"Checking challenge queue for {canister_id}...")
    try:
        result = run_command([
            "dfx", "canister", "--network", network, "call",
            canister_id, "getChallengeQueueAdmin", "--output", "json"
        ], retry_on_transient_errors=True)
        data = json.loads(result.stdout)
        queue = data.get('Ok', [])

        if not queue:
            log_message("Challenge queue is empty", "SUCCESS")
            return False, None

        # Find the entry with the most recent (highest) challengeQueuedTimestamp
        # The queue can contain up to 5 items and they may not be in timestamp order
        most_recent_timestamp = 0
        most_recent_entry = None

        for entry in queue:
            timestamp_str = entry.get('challengeQueuedTimestamp', '0')
            # Remove underscores from timestamp string if present
            timestamp_str = timestamp_str.replace('_', '')
            timestamp_ns = int(timestamp_str)

            if timestamp_ns > most_recent_timestamp:
                most_recent_timestamp = timestamp_ns
                most_recent_entry = entry

        if most_recent_timestamp == 0:
            log_message("Could not find valid timestamp in queue", "ERROR")
            return False, None

        timestamp = datetime.fromtimestamp(most_recent_timestamp / 1_000_000_000)
        age = datetime.now() - timestamp
        log_message(f"Most recent queue entry age: {age.total_seconds() / 60:.1f} minutes")

        return True, timestamp
    except Exception as e:
        log_message(f"Failed to check queue for {canister_id}: {e}", "WARNING")
        # Assume empty queue if we can't check
        return False, None

def clear_queue(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Clear the challenge queue for a canister with retry on transient network errors."""
    log_message(f"Clearing challenge queue for {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "resetChallengeQueueAdmin"
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # Check if the result contains Ok with status_code = 200
        if "Ok" in result.stdout and "status_code = 200" in result.stdout:
            log_message(f"Challenge queue cleared for {canister_id}", "SUCCESS")
            return True
        else:
            log_message(f"Failed to clear challenge queue for {canister_id}: {result.stdout}", "ERROR")
            sys.exit(1)
    except Exception as e:
        log_message(f"Failed to clear challenge queue for {canister_id}: {e}", "ERROR")
        sys.exit(1)

def stop_canister(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Stop a canister with retry on transient network errors."""
    log_message(f"Stopping canister {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "stop", canister_id
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # For stop command, success means empty stdout (message goes to stderr)
        if result.stdout == '':
            log_message(f"Canister {canister_id} stopped", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when stopping canister: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to stop canister {canister_id}: {e}", "ERROR")
        return False

def start_canister(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Start a canister with retry on transient network errors."""
    log_message(f"Starting canister {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "start", canister_id
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # For start command, success means empty stdout (message goes to stderr)
        if result.stdout == '':
            log_message(f"Canister {canister_id} started", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when starting canister: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to start canister {canister_id}: {e}", "ERROR")
        return False

def create_snapshot(network: str, canister_id: str, dry_run: bool = False) -> Optional[str]:
    """Create a snapshot of a canister and return the snapshot ID with retry on transient network errors."""
    log_message(f"Creating snapshot for {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "snapshot", "create", canister_id
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return "dry-run-snapshot-id"

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # The snapshot creation output goes to stderr, not stdout
        # Expected format: "Created a new snapshot of canister xxx. Snapshot ID: yyy"
        if result.returncode == 0 and result.stdout == '':
            for line in result.stderr.split('\n'):
                if 'Snapshot ID:' in line:
                    # Extract the ID after "Snapshot ID: "
                    parts = line.split('Snapshot ID:')
                    if len(parts) >= 2:
                        snapshot_id = parts[1].strip()
                        log_message(f"Snapshot created: {snapshot_id}", "SUCCESS")
                        return snapshot_id

            # If we can't parse but command succeeded, return a marker
            log_message(f"Snapshot created but ID not parsed from stderr: {result.stderr}", "WARNING")
            return "created-but-not-parsed"
        else:
            log_message(f"Unexpected snapshot creation response: stdout={result.stdout}", "WARNING")
            return None
    except Exception as e:
        log_message(f"Failed to create snapshot for {canister_id}: {e}", "ERROR")
        return None

def upgrade_canister(network: str, canister_name: str, dry_run: bool = False, deploy_with_yes: bool = False) -> bool:
    """Upgrade a canister with retry on transient network errors.

    Handles out-of-cycles errors by automatically topping up the canister with cycles.
    """
    def is_out_of_cycles_error(error_text: str) -> bool:
        """Check if error indicates canister is out of cycles during installation."""
        return "is out of cycles" in error_text and "IC0207" in error_text

    log_message(f"Upgrading {canister_name}...")

    command = [
        "dfx", "deploy", "--network", network, canister_name, "--mode", "upgrade"
    ]
    if deploy_with_yes:
        command.append("--yes")

    if dry_run:
        log_message(f"DRY RUN: Would execute (in {POAIW_MAINER_DIR}): {' '.join(command)}", "INFO")
        return True

    # Get canister ID from canister_ids.json
    try:
        with open(POAIW_CANISTER_IDS_PATH, 'r') as f:
            canister_ids = json.load(f)
        canister_id = canister_ids.get(canister_name, {}).get(network)
        if not canister_id:
            log_message(f"Could not find canister ID for {canister_name} on network {network}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to read canister_ids.json: {e}", "ERROR")
        return False

    max_attempts = 2  # Initial attempt + 1 retry after topping up

    for attempt in range(1, max_attempts + 1):
        try:
            # Run the command WITH retry on transient errors (including network timeouts)
            # Capture output so we can detect transient errors for retry logic
            # Max 5 retries with 10 second base delay for network operations
            run_command(
                command,
                capture_output=True,
                cwd=str(POAIW_MAINER_DIR),
                retry_on_transient_errors=True,
                max_retries=5,
                retry_delay=10.0,
                log_stdout=True  # Show deployment progress
            )
            log_message(f"Canister {canister_name} upgraded", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            error_text = ""
            if hasattr(e, 'stderr') and e.stderr:
                error_text = e.stderr
            if hasattr(e, 'stdout') and e.stdout:
                error_text += " " + e.stdout
            error_text += " " + str(e)

            # Check if this is an out-of-cycles error
            if is_out_of_cycles_error(error_text) and attempt < max_attempts:
                log_message(f"Canister {canister_id} is out of cycles during installation", "WARNING")
                log_message(f"Sending 500,000,000,000 cycles to canister...", "INFO")

                try:
                    # Send cycles using dfx wallet
                    send_result = run_command([
                        "dfx", "wallet", "--network", network, "send", canister_id, "500_000_000_000"
                    ])
                    log_message(f"Successfully sent cycles to {canister_id}", "SUCCESS")

                    # Wait 10 seconds before retrying
                    log_message(f"Waiting 10 seconds before retrying upgrade...", "INFO")
                    time.sleep(10)

                    # Loop will continue to retry
                    continue
                except Exception as send_error:
                    log_message(f"Failed to send cycles to {canister_id}: {send_error}", "ERROR")
                    return False
            else:
                # Not an out-of-cycles error, or we've exhausted retries
                log_message(f"Failed to upgrade {canister_name}: {e}", "ERROR")
                return False
        except Exception as e:
            log_message(f"Failed to upgrade {canister_name}: {e}", "ERROR")
            return False

    # If we get here, all attempts failed
    log_message(f"Failed to upgrade {canister_name} after {max_attempts} attempts", "ERROR")
    return False

def check_health(network: str, canister_id: str, dry_run: bool = False) -> tuple[bool, str]:
    """Check the health of a canister.

    Returns:
        Tuple of (success: bool, output: str)
    """
    log_message(f"Checking health for {canister_id}...")
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "health"
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True, ""

    try:
        result = run_command(command, retry_on_transient_errors=True)
        output = result.stdout.strip()

        # Check for successful health response
        # (Sometimes dfx fails to parse the candid and shows numeric variant)
        if "(variant { Ok = record { status_code = 200 : nat16 } })" in output or "(variant { 17_724 = record { 3_475_804_314 = 200 : nat16 } })" in output:
                log_message(f"Health check passed for {canister_id}", "SUCCESS")
                return True, output
        else:
            log_message(f"Health check failed for {canister_id}: {output}", "ERROR")
            return False, output
    except Exception as e:
        error_msg = str(e)
        log_message(f"Health check failed for {canister_id}: {error_msg}", "ERROR")
        return False, error_msg
    

def get_maintenance_flag(network: str, canister_id: str, dry_run: bool = False) -> Optional[bool]:
    """Get the current maintenance flag status.

    Returns:
        True if flag is on
        False if flag is off
        None if method doesn't exist (old canister) - treated as success in turn_on_maintenance_flag
    """
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "getMaintenanceFlag", "--output", "json"
    ]

    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True)
        data = json.loads(result.stdout)
        return data.get('Ok', {}).get('flag', None)
    except subprocess.CalledProcessError as e:
        # Check if the error is because the method doesn't exist (old canister)
        if e.stderr and "has no update method 'getMaintenanceFlag'" in e.stderr:
            log_message(f"Canister {canister_id} does not have getMaintenanceFlag method (old version)", "INFO")
            return None
        log_message(f"Failed to get maintenance flag for {canister_id}: {e}", "ERROR")
        return None
    except Exception as e:
        log_message(f"Failed to get maintenance flag for {canister_id}: {e}", "ERROR")
        return None

def turn_on_maintenance_flag(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Turn on the maintenance flag if it's off.

    For old canisters without getMaintenanceFlag method, this returns True (success)
    since the upgrade will add the method and the flag will be on by default.
    """
    log_message(f"Checking maintenance flag for {canister_id}...")

    if dry_run:
        log_message(f"DRY RUN: Would check maintenance flag", "INFO")
        return True

    try:
        # Step 1: Check current maintenance flag status
        flag_value = get_maintenance_flag(network, canister_id)

        # Handle old canisters without the method
        if flag_value is None:
            log_message(f"Canister does not have maintenance flag method (old version) - skipping", "SUCCESS")
            return True

        # Check if flag is already true
        if flag_value is True:
            log_message(f"Maintenance flag already on for {canister_id}", "SUCCESS")
            return True
        elif flag_value is False:
            log_message(f"Maintenance flag is OFF, turning it on...")

            # Step 2: Toggle the flag
            toggle_command = [
                "dfx", "canister", "--network", network, "call",
                canister_id, "toggleMaintenanceFlagAdmin"
            ]
            toggle_result = run_command(toggle_command)

            # Step 3: Verify flag is now true (with retries)
            max_retries = 5
            retry_delay = 3.0

            for attempt in range(1, max_retries + 1):
                # Give canister a moment for the flag change to propagate
                time.sleep(retry_delay)

                new_flag_value = get_maintenance_flag(network, canister_id)

                if new_flag_value is True:
                    log_message(f"Maintenance flag turned ON for {canister_id}", "SUCCESS")
                    return True
                elif attempt < max_retries:
                    log_message(f"Flag still OFF (attempt {attempt}/{max_retries}). Waiting {retry_delay}s before next check...", "WARNING")
                else:
                    log_message(f"Failed to turn on maintenance flag for {canister_id}: flag is still {new_flag_value}", "ERROR")
                    return False

            return False
        else:
            log_message(f"Unexpected maintenance flag value: {flag_value}", "ERROR")
            return False

    except Exception as e:
        log_message(f"Failed to check/toggle maintenance flag for {canister_id}: {e}", "ERROR")
        return False

def turn_off_maintenance_flag(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Turn off the maintenance flag if it's on.

    After an upgrade, the canister might temporarily report method not found
    while initializing. This function retries to handle that case.
    """
    log_message(f"Checking maintenance flag for {canister_id}...")

    if dry_run:
        log_message(f"DRY RUN: Would check maintenance flag", "INFO")
        return True

    try:
        # Step 1: Check current maintenance flag status with retries
        # After upgrade, canister may need time to initialize
        max_initial_retries = 5
        initial_retry_delay = 3.0
        flag_value = None

        for initial_attempt in range(1, max_initial_retries + 1):
            flag_value = get_maintenance_flag(network, canister_id)

            # If we got a valid response (True or False), proceed
            if flag_value is not None:
                break

            # If None (method not found or error), retry with delay
            if initial_attempt < max_initial_retries:
                log_message(f"Could not get maintenance flag (attempt {initial_attempt}/{max_initial_retries}). Canister may be initializing. Waiting {initial_retry_delay}s...", "WARNING")
                time.sleep(initial_retry_delay)
            else:
                log_message(f"Could not get maintenance flag after {max_initial_retries} attempts. Canister may not have this method (old version) - assuming success", "WARNING")
                return True

        # Check if flag is already false
        if flag_value is False:
            log_message(f"Maintenance flag already off for {canister_id}", "SUCCESS")
            return True
        elif flag_value is True:
            log_message(f"Maintenance flag is ON, turning it off...")

            # Step 2: Toggle the flag
            toggle_command = [
                "dfx", "canister", "--network", network, "call",
                canister_id, "toggleMaintenanceFlagAdmin"
            ]
            toggle_result = run_command(toggle_command)

            # Step 3: Verify flag is now false (with retries)
            max_retries = 5
            retry_delay = 3.0

            for attempt in range(1, max_retries + 1):
                # Give canister a moment for the flag change to propagate
                time.sleep(retry_delay)

                new_flag_value = get_maintenance_flag(network, canister_id)

                if new_flag_value is False:
                    log_message(f"Maintenance flag turned OFF for {canister_id}", "SUCCESS")
                    return True
                elif attempt < max_retries:
                    log_message(f"Flag still ON (attempt {attempt}/{max_retries}). Waiting {retry_delay}s before next check...", "WARNING")
                else:
                    log_message(f"Failed to turn off maintenance flag for {canister_id}: flag is still {new_flag_value}", "ERROR")
                    return False

            return False
        else:
            log_message(f"Unexpected maintenance flag value: {flag_value}", "ERROR")
            return False

    except Exception as e:
        log_message(f"Failed to check/toggle maintenance flag for {canister_id}: {e}", "ERROR")
        return False

def prepare_for_deployment(network: str, dry_run: bool = False) -> bool:
    """Step 1: Prepare for deployment by updating files."""
    log_message("=== STEP 1: PREPARING FOR DEPLOYMENT ===", "INFO")

    # Run get_mainers.sh to update dfx.json and canister_ids.json
    log_message(f"Updating mAIner configuration files {POAIW_CANISTER_IDS_PATH} & {POAIW_DFX_JSON_PATH}...")
    get_mainers_script = (SCRIPT_DIR / "get_mainers.sh").resolve()
    command = [
        str(get_mainers_script),
        "--network", network
    ]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, capture_output=False)
        log_message("Configuration files updated", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"Failed to prepare for deployment: {e}", "ERROR")
        return False

def get_canister_name_from_address(address: str, network: str) -> Optional[str]:
    """Find the canister name from its address by looking in canister_ids.json."""
    try:
        with open(POAIW_CANISTER_IDS_PATH, 'r') as f:
            canister_ids = json.load(f)

        for canister_name, networks in canister_ids.items():
            if isinstance(networks, dict) and networks.get(network) == address:
                return canister_name

        return None
    except Exception as e:
        log_message(f"Failed to find canister name for {address}: {e}", "ERROR")
        return None

def should_skip_upgrade(network: str, address: str, target_hash: Optional[str], dry_run: bool = False) -> bool:
    """
    Determine if upgrade should be skipped.

    Skip upgrade only if:
    1. target_hash is provided AND current_hash matches target_hash
    2. AND health check passes

    Args:
        network: Network name (e.g., 'testing', 'ic')
        address: Canister address
        target_hash: Target wasm hash (optional)
        dry_run: If True, simulates checks without making actual calls

    Returns:
        True if upgrade should be skipped, False otherwise
    """
    # Get current hash
    current_hash = get_canister_wasm_hash(network, address)

    # Log current hash
    if current_hash:
        log_message(f"Current hash: {current_hash}", "INFO")
    else:
        log_message(f"Could not retrieve current hash", "WARNING")

    # If no target hash specified, don't skip
    if not target_hash:
        return False

    log_message(f"Target hash: {target_hash}", "INFO")

    # If hashes don't match, don't skip
    if current_hash != target_hash:
        log_message(f"Hash mismatch - upgrade needed", "INFO")
        return False

    # Hashes match - now check health
    log_message(f"Hash matches target - checking health before skipping", "INFO")
    health_ok, _ = check_health(network, address, dry_run)

    if health_ok:
        log_message(f"Already upgraded to target hash and health check passed - skipping", "INFO")
        return True
    else:
        log_message(f"Hash matches but health check failed - will upgrade anyway", "WARNING")
        return False

def upgrade_mainer(network: str, mainer: Dict, target_hash: Optional[str],
                  dry_run: bool = False, canister_index: int = 0, deploy_with_yes: bool = False) -> bool:
    """Upgrade a single mAIner through all steps."""
    address = mainer.get('address', '')

    log_message(f"{'='*60}", "INFO")
    log_message(f"Processing mAIner {canister_index}: {address}", "INFO")

    # Mark as in progress
    update_mainer_status(address, MainerStatus.IN_PROGRESS)

    # Find the actual canister name from canister_ids.json
    canister_name = get_canister_name_from_address(address, network)

    if not canister_name:
        log_message(f"Cannot find canister name for {address} in canister_ids.json", "ERROR")
        log_message("Make sure to run get_mainers.sh first to update the configuration files", "WARNING")
        update_mainer_status(address, MainerStatus.FAILED_OTHER, "Canister name not found in canister_ids.json")
        return False

    log_message(f"canister_ids.json key: {canister_name}", "INFO")

    # Get pre-upgrade hash for verification later
    pre_upgrade_hash = None
    if not dry_run:
        pre_upgrade_hash = get_canister_wasm_hash(network, address)
        if pre_upgrade_hash:
            log_message(f"Pre-upgrade hash: {pre_upgrade_hash}", "INFO")

    # Check canister status before proceeding
    initial_status = get_canister_status(network, address)
    log_message(f"Canister initial status: {initial_status}", "INFO")

    if initial_status == "Stopped":
        log_message("Canister is already stopped, skipping steps 2b-2e", "INFO")
    else:
        # Step 2b: Set maintenance flag
        if not turn_on_maintenance_flag(network, address, dry_run):
            log_message("Failed to turn on maintenance flag", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_MAINTENANCE, "Could not turn on maintenance flag")
            return False

        # Step 2c: Stop timer
        if not stop_timer(network, address, dry_run):
            log_message("Failed to stop timer", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_STOP_TIMER, "Could not stop timer")
            return False

        # Step 2d: Check queue
        has_entries, last_entry_time = check_queue(network, address)
        if has_entries and last_entry_time:
            age_minutes = (datetime.now() - last_entry_time).total_seconds() / 60
            if age_minutes < 10:
                wait_time = 10 - age_minutes
                log_message(f"Challenge queue has recent entries. Waiting {wait_time:.1f} minutes...", "WARNING")
                if not dry_run:
                    time.sleep(wait_time * 60)
                    # Re-check after waiting
                    has_entries, last_entry_time = check_queue(network, address)

            # Clear old entries if still present
            if has_entries:
                clear_queue(network, address, dry_run)

        # Step 2e: Stop canister
        if not stop_canister(network, address, dry_run):
            log_message("Failed to stop canister", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_OTHER, "Could not stop canister")
            return False

    # Step 2f: Create snapshot
    snapshot_id = create_snapshot(network, address, dry_run)
    if not snapshot_id:
        log_message("Failed to create snapshot", "ERROR")
        # Start canister and timer before failing
        start_canister(network, address, dry_run)
        start_timer(network, address, dry_run)
        update_mainer_status(address, MainerStatus.FAILED_SNAPSHOT, "Could not create snapshot")
        return False

    # Step 2g: Deploy upgrade
    if not upgrade_canister(network, canister_name, dry_run, deploy_with_yes):
        log_message(f"Failed to upgrade canister. Snapshot ID for rollback: {snapshot_id}", "ERROR")
        # Don't auto-rollback, let admin decide
        update_mainer_status(address, MainerStatus.FAILED_UPGRADE, f"Upgrade failed. Snapshot: {snapshot_id}")
        return False

    # Step 2h: Start canister
    if not start_canister(network, address, dry_run):
        log_message(f"Failed to start canister. Snapshot ID for rollback: {snapshot_id}", "ERROR")
        update_mainer_status(address, MainerStatus.FAILED_START, f"Could not start canister. Snapshot: {snapshot_id}")
        return False

    # Step 2i: Check maintenance flag (endpoint must now be available and return true)
    # Retry logic: canister may need time to fully initialize after upgrade
    # If flag is False, call endpoint to turn it on
    if not dry_run:
        max_retries = 10
        retry_delay = 15.0
        flag_value = None

        for attempt in range(1, max_retries + 1):
            time.sleep(retry_delay)
            flag_value = get_maintenance_flag(network, address, dry_run)

            if flag_value is True:
                log_message(f"Maintenance flag check passed (attempt {attempt}/{max_retries})", "SUCCESS")
                break
            elif flag_value is False:
                log_message(f"Maintenance flag is False (attempt {attempt}/{max_retries}), calling endpoint to turn it on...", "WARNING")
                if turn_on_maintenance_flag(network, address, dry_run):
                    log_message(f"Successfully turned on maintenance flag", "SUCCESS")
                    break
                elif attempt < max_retries:
                    log_message(f"Failed to turn on maintenance flag, will retry. Waiting {retry_delay}s...", "WARNING")
                else:
                    log_message(f"Failed to turn on maintenance flag after {max_retries} attempts. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                    update_mainer_status(address, MainerStatus.FAILED_MAINTENANCE, f"Could not turn on maintenance flag. Snapshot: {snapshot_id}")
                    return False
            elif attempt < max_retries:
                log_message(f"Maintenance flag not yet True (got: {flag_value}), attempt {attempt}/{max_retries}. Waiting {retry_delay}s...", "WARNING")
            else:
                log_message(f"Maintenance flag check failed after {max_retries} attempts. Expected True, got: {flag_value}. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_MAINTENANCE, f"Maintenance flag was {flag_value}, expected True. Snapshot: {snapshot_id}")
                return False
    else:
        flag_value = get_maintenance_flag(network, address, dry_run)

    # Step 2j: Start timer
    if not start_timer(network, address, dry_run):
        if not dry_run:
            log_message(f"Failed to start timer. Canister upgraded but timer not running!", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_START_TIMER, f"Could not start timer. Snapshot: {snapshot_id}")
            return False

    # Step 2k: Turn off maintenance flag
    if not turn_off_maintenance_flag(network, address, dry_run):
        if not dry_run:
            log_message(f"Failed to turn off maintenance flag. Canister upgraded but maintenance flag may still be ON!", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_MAINTENANCE, f"Could not turn off maintenance flag. Snapshot: {snapshot_id}")
            return False

    # Step 2i: Check health (must now return 200 OK)
    # Give canister time for maintenance flag to fully propagate
    if not dry_run:
        log_message(f"Waiting 10 seconds for maintenance flag to propagate before health check...", "INFO")
        time.sleep(10)

    # Retry health check if it fails due to maintenance flag not yet propagated
    max_health_retries = 3
    health_retry_delay = 30.0
    health_ok = False

    for health_attempt in range(1, max_health_retries + 1):
        health_ok, health_output = check_health(network, address, dry_run)

        if health_ok:
            break

        # Check if failure is due to maintenance flag still being on
        if 'mAIner is under maintenance' in health_output:
            if health_attempt < max_health_retries:
                log_message(f"Health check failed due to maintenance flag (attempt {health_attempt}/{max_health_retries}). Waiting {health_retry_delay}s before retry...", "WARNING")
                if not dry_run:
                    time.sleep(health_retry_delay)
            else:
                log_message(f"Health check still failing after {max_health_retries} attempts. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_HEALTH, f"Health check failed (maintenance flag). Snapshot: {snapshot_id}")
                return False
        else:
            # Different error - don't retry
            if not dry_run:
                log_message(f"Health check failed with unexpected error. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_HEALTH, f"Health check failed. Snapshot: {snapshot_id}")
                return False

    if not health_ok:
        if not dry_run:
            log_message(f"Health check failed. Snapshot ID for rollback: {snapshot_id}", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_HEALTH, f"Health check failed. Snapshot: {snapshot_id}")
            return False

    # Step 2l: Verify the hash after upgrade
    if not dry_run:
        log_message(f"Verifying module hash after upgrade...", "INFO")
        post_upgrade_hash = get_canister_wasm_hash(network, address)

        if not post_upgrade_hash:
            log_message(f"Could not retrieve post-upgrade hash. Snapshot ID for rollback: {snapshot_id}", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Could not verify hash after upgrade. Snapshot: {snapshot_id}")
            return False

        # Always log the new hash
        log_message(f"New hash: {post_upgrade_hash}", "INFO")

        # Verify hash based on whether target_hash was provided
        if target_hash:
            # If target hash provided, verify it matches
            if post_upgrade_hash != target_hash:
                log_message(f"Hash mismatch after upgrade! Expected: {target_hash}, Got: {post_upgrade_hash}. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Hash verification failed. Expected: {target_hash}, Got: {post_upgrade_hash}. Snapshot: {snapshot_id}")
                return False
            log_message(f"Hash verification passed: matches target hash", "SUCCESS")
        else:
            # If no target hash, verify that hash actually changed
            if pre_upgrade_hash and post_upgrade_hash == pre_upgrade_hash:
                log_message(f"Hash did not change after upgrade! Hash: {post_upgrade_hash}. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Hash unchanged after upgrade: {post_upgrade_hash}. Snapshot: {snapshot_id}")
                return False
            log_message(f"Hash verification passed: hash changed from {pre_upgrade_hash} to {post_upgrade_hash}", "SUCCESS")

    log_message(f"Successfully upgraded mAIner {canister_index}: {address}", "SUCCESS")
    update_mainer_status(address, MainerStatus.SUCCESS)
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Upgrade mAIner canisters with safety checks and rollback capability"
    )
    parser.add_argument(
        "--network",
        required=True,
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        help="Network to upgrade mainers on"
    )
    parser.add_argument(
        "--target-hash",
        help="Target wasm hash to upgrade to (optional)"
    )
    parser.add_argument(
        "--num",
        type=int,
        help="Number of mAIners to upgrade (optional)"
    )
    parser.add_argument(
        "--mainer",
        help="Specific mAIner canister ID to upgrade (optional)"
    )
    parser.add_argument(
        "--user",
        help="Principal ID of user whose mAIners to upgrade (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode without making actual changes"
    )
    parser.add_argument(
        "--skip-preparation",
        action="store_true",
        help="Skip Step 1 preparation (use if files already updated)"
    )
    parser.add_argument(
        "--ask-before-upgrade",
        action="store_true",
        help="Ask for confirmation before upgrading each canister"
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Process mainers in reverse order (start from the end)"
    )
    parser.add_argument(
        "--deploy-with-yes",
        action="store_true",
        help="Use 'dfx deploy --yes' to skip confirmation prompts"
    )

    args = parser.parse_args()

    # Open log file
    global log_file_handle
    try:
        log_file_handle = open(LOG_FILE_PATH, 'w')
    except Exception as e:
        print(f"{RED}Warning: Could not open log file {LOG_FILE_PATH}: {e}{NC}")
        log_file_handle = None

    try:
        log_message(f"{'='*60}", "INFO")
        log_message(f"mAIner Upgrade Script", "INFO")
        log_message(f"Log file: {LOG_FILE_PATH}", "INFO")
        log_message(f"Network: {args.network}", "INFO")
        log_message(f"Target Hash: {args.target_hash or 'Not specified'}", "INFO")
        log_message(f"Max mAIners: {args.num or 'All'}", "INFO")
        log_message(f"Specific mAIner: {args.mainer or 'None'}", "INFO")
        log_message(f"User: {args.user or 'All'}", "INFO")
        log_message(f"Dry Run: {args.dry_run}", "INFO")
        log_message(f"Ask Before Upgrade: {args.ask_before_upgrade}", "INFO")
        log_message(f"{'='*60}", "INFO")

        if args.dry_run:
            log_message("RUNNING IN DRY-RUN MODE - NO ACTUAL CHANGES WILL BE MADE", "WARNING")
            input("Press Enter to continue...")
        else:
            log_message("THIS IS A LIVE RUN - CHANGES WILL BE MADE TO CANISTERS", "WARNING")
            confirm = input("Type 'yes' to continue: ")
            if confirm.lower() != 'yes':
                log_message("Upgrade cancelled", "INFO")
                sys.exit(0)

        # Step 1: Prepare for deployment
        if not args.skip_preparation:
            if not prepare_for_deployment(args.network, args.dry_run):
                log_message("Failed to prepare for deployment", "ERROR")
                sys.exit(1)
        else:
            log_message("Skipping preparation step", "INFO")

        # Get all mAIners
        mainers = get_mainers(args.network)

        # Filter mAIners based on arguments
        share_agent_mainers = []
        for mainer in mainers:
            address = mainer.get('address', '')
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''
            owned_by = mainer.get('ownedBy', '')

            # Skip if not ShareAgent type
            if canister_type != "ShareAgent" or address == "":
                if address:  # Only track if we have an address
                    update_mainer_status(address, MainerStatus.SKIPPED_FILTER, f"Not ShareAgent or empty address")
                continue

            # Filter by specific mainer if provided
            if args.mainer and address != args.mainer:
                update_mainer_status(address, MainerStatus.SKIPPED_FILTER, "Not the specified mainer")
                continue

            # Filter by user if provided
            if args.user and owned_by != args.user:
                update_mainer_status(address, MainerStatus.SKIPPED_FILTER, "Not owned by specified user")
                continue

            # Mark as pending initially
            update_mainer_status(address, MainerStatus.PENDING)
            share_agent_mainers.append(mainer)

        total_mainers = len(share_agent_mainers)
        max_upgrades = min(args.num, total_mainers) if args.num else total_mainers

        if total_mainers == 0:
            log_message("No ShareAgent mAIners found to upgrade", "WARNING")
            sys.exit(0)

        # Reverse the list if --reverse flag is set
        if args.reverse:
            share_agent_mainers.reverse()
            log_message("Processing mAIners in REVERSE order", "WARNING")

        # Print clear message - highlight what will actually be processed
        if args.num and args.num < total_mainers:
            log_message(f"Found {total_mainers} ShareAgent mAIners matching filters", "INFO")
            log_message(f"Will process {max_upgrades} mAIners (--num limit)", "SUCCESS")
        else:
            log_message(f"Will process {total_mainers} ShareAgent mAIners", "SUCCESS")

        # Track results
        successful = 0
        failed = 0
        skipped = 0

        # Set global progress tracking for logging
        global current_mainer_index, total_mainers_to_process
        total_mainers_to_process = max_upgrades

        # Process mAIners
        for i, mainer in enumerate(share_agent_mainers[:max_upgrades]):
            current_mainer_index = i

            if interrupted:
                log_message("Process interrupted by user", "WARNING")
                break

            try:
                # Check if upgrade should be skipped
                address = mainer.get('address', '')

                if should_skip_upgrade(args.network, address, args.target_hash, args.dry_run):
                    update_mainer_status(address, MainerStatus.SKIPPED_ALREADY_UPGRADED, "Already at target hash and healthy")
                    skipped += 1
                    continue

                # Ask for confirmation if --ask-before-upgrade is set
                if args.ask_before_upgrade:
                    log_message(f"About to upgrade mAIner {i}: {address}", "WARNING")
                    response = input(f"Continue with upgrade? (y/n/exit) [y]: ").strip().lower()
                    if not response:
                        response = 'y'  # Default to yes

                    # Normalize responses
                    if response in ['yes', 'y']:
                        response = 'y'
                    elif response in ['no', 'n']:
                        response = 'n'
                    elif response in ['exit', 'e']:
                        response = 'exit'

                    if response == 'exit':
                        log_message(f"Exiting upgrade process by user request", "INFO")
                        update_mainer_status(address, MainerStatus.SKIPPED_USER_REQUEST, "User chose to exit")
                        break
                    elif response == 'n':
                        log_message(f"Skipping mAIner {i} by user request", "INFO")
                        update_mainer_status(address, MainerStatus.SKIPPED_USER_REQUEST, "User chose to skip")
                        skipped += 1
                        continue
                    elif response != 'y':
                        log_message(f"Invalid response. Skipping mAIner {i}", "WARNING")
                        update_mainer_status(address, MainerStatus.SKIPPED_USER_REQUEST, "Invalid response")
                        skipped += 1
                        continue

                # Proceed with upgrade
                if upgrade_mainer(args.network, mainer, args.target_hash, args.dry_run, i, args.deploy_with_yes):
                    successful += 1
                else:
                    failed += 1
                    log_message(f"Failed to upgrade mAIner {i}. Stopping process.", "ERROR")
                    break
            except Exception as e:
                failed += 1
                address = mainer.get('address', '')
                log_message(f"Unexpected error upgrading mAIner {i}: {e}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Unexpected error: {str(e)}")
                break

        # Reset progress tracking
        current_mainer_index = None
        total_mainers_to_process = None

        # Write status to files
        write_status_to_json()
        write_status_to_markdown()

        # Print concise status report (pass max_upgrades to show only what was processed)
        print_status_report(processed_count=max_upgrades)

        if failed > 0:
            sys.exit(1)
    finally:
        # Always close log file
        if log_file_handle:
            log_file_handle.close()

if __name__ == "__main__":
    main()