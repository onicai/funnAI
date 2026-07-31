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

import os
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

# Shared icp-cli helpers: unlike `dfx ... --output json`, icp-cli cannot decode a Candid
# response, so decoding happens here via icp-py-core.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.resolve()
POAIW_MAINER_DIR = (SCRIPT_DIR / "../PoAIW/src/mAIner").resolve()
POAIW_DFX_JSON_PATH = (POAIW_MAINER_DIR / "dfx.json").resolve()
POAIW_CANISTER_IDS_PATH = (POAIW_MAINER_DIR / "canister_ids.json").resolve()
GAME_STATE_CANISTER_IDS_PATH = (
    SCRIPT_DIR / "../PoAIW/src/GameState/canister_ids.json"
).resolve()

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
    SKIPPED_DOES_NOT_EXIST = "skipped_not_exist" # Skipped - canister does not exist
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

# Per-canister previous cycle-state sample, for drift detection.
# Keyed by canister address. Tracks the last observed (officialCyclesBalance,
# cycleBalance) pair so sample_cycle_state() can flag when Cycles.balance()
# rose between two consecutive samples — cycles should only rise via
# addCycles() (which updates officialCyclesBalance in lockstep), so any step
# where current rises without official rising is an unattributed deposit
# worth investigating.
_prev_cycle_state: Dict[str, Dict[str, int]] = {}

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
    skipped_does_not_exist = summary.get('skipped_not_exist', 0)
    skipped_processed = skipped_already_upgraded + skipped_user + skipped_does_not_exist

    # Total that were actually looked at
    total_processed = success_count + failed_count + skipped_processed

    # Print concise summary
    log_message(f"{'='*60}", "INFO")
    log_message("UPGRADE SUMMARY", "INFO")
    log_message(f"Processed: {total_processed} mAIner(s)", "INFO")
    log_message(f"  ✓ Upgraded: {success_count}", "SUCCESS" if success_count > 0 else "INFO")
    log_message(f"  ⊘ Already up-to-date: {skipped_already_upgraded}", "INFO")
    log_message(f"  ⊘ Skipped by user: {skipped_user}", "INFO" if skipped_user == 0 else "WARNING")
    log_message(f"  ⊘ Does not exist: {skipped_does_not_exist}", "WARNING" if skipped_does_not_exist > 0 else "INFO")
    log_message(f"  ✗ Failed: {failed_count}", "ERROR" if failed_count > 0 else "INFO")

    # Show canisters that don't exist
    if skipped_does_not_exist > 0:
        log_message("\nCanisters that do not exist:", "WARNING")
        for address, data in mainer_status_tracker.items():
            if data['status'].value == 'skipped_not_exist':
                log_message(f"  {address}", "WARNING")

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
        data = icp_helpers.call_argv(["icp", "canister", "call", "game_state_canister", "getMainerAgentCanistersAdmin", "()", "-e", network])
        mainers = data.get('Ok', [])
        log_message(f"Found {len(mainers)} total mAIners (Unfiltered, still includes empty address + ShareService)", "INFO")
        return mainers
    except Exception as e:
        log_message(f"Failed to get mAIners: {e}", "ERROR")
        sys.exit(1)

def get_cycles_balance(network: str, canister_id: str) -> Optional[int]:
    """Get the cycles balance of a canister.

    Returns:
        Cycles balance as integer, or None if unable to retrieve.
    """
    try:
        result = run_command(["icp", "canister", "status", canister_id, "-e", network], retry_on_transient_errors=True, max_retries=3, retry_delay=5.0)
        for line in result.stdout.split('\n'):
            if 'Balance:' in line:
                # Parse line like "Balance: 3_000_000_000_000 Cycles"
                balance_str = line.split(':')[1].strip().split()[0]
                # Remove underscores and convert to int
                balance = int(balance_str.replace('_', ''))
                return balance
        return None
    except Exception as e:
        log_message(f"Failed to get cycles balance for {canister_id}: {e}", "WARNING")
        return None

def format_cycles(cycles: int) -> str:
    """Format cycles balance in a human-readable way (e.g., 3.5T, 500B)."""
    if cycles >= 1_000_000_000_000:
        return f"{cycles / 1_000_000_000_000:.2f}T"
    elif cycles >= 1_000_000_000:
        return f"{cycles / 1_000_000_000:.2f}B"
    elif cycles >= 1_000_000:
        return f"{cycles / 1_000_000:.2f}M"
    else:
        return str(cycles)


# Module-level previous wallet sample. The wallet is per-identity, not
# per-canister, so we track it as a single global value across the run.
_prev_wallet_balance_cycles: Optional[int] = None


def get_wallet_balance(network: str) -> Optional[int]:
    """Query `dfx wallet --network <network> balance` and return the amount in cycles.

    Output format examples:
        "25,427.884 TC (trillion cycles)."
        "1,234.56 BC (billion cycles)."
        "999,999 MC (million cycles)."

    Returns None on failure or unrecognized unit.
    """
    try:
        result = run_command(
            ["dfx", "wallet", "--network", network, "balance"],
            retry_on_transient_errors=True,
            max_retries=3,
            retry_delay=5.0,
        )
        line = result.stdout.strip().split("\n")[0].strip()
        parts = line.split()
        if len(parts) < 2:
            log_message(f"Unexpected wallet balance output (too few tokens): {line!r}", "WARNING")
            return None
        amount_str = parts[0].replace(",", "")
        unit = parts[1].upper()
        amount = float(amount_str)
        unit_multipliers = {
            "C":  1,
            "KC": 10 ** 3,
            "MC": 10 ** 6,
            "BC": 10 ** 9,
            "TC": 10 ** 12,
        }
        multiplier = unit_multipliers.get(unit)
        if multiplier is None:
            log_message(f"Unrecognized wallet balance unit: {unit!r}", "WARNING")
            return None
        return int(amount * multiplier)
    except Exception as e:
        log_message(f"Failed to fetch wallet balance: {e}", "WARNING")
        return None


def sample_cycle_state(
    network: str,
    canister_id: str,
    label: str,
    dry_run: bool = False,
) -> Optional[Tuple[int, int]]:
    """Query officialCyclesBalance + Cycles.balance() via getOfficialCyclesBalanceAdmin
    and log a status line. If Cycles.balance() rose vs the previous sample for
    this canister (which should only happen via addCycles()), log a WARNING
    (yellow) pointing at the step that caused the rise.

    Returns (official, current) or None on failure / dry_run.
    """
    if dry_run:
        log_message(f"[CYCLES][{label}] DRY RUN: skipping cycle state sample for {canister_id}", "INFO")
        return None

    # Single query returns both fields atomically (consistent snapshot).
    try:
        payload = icp_helpers.call_argv(
            ["icp", "canister", "call", canister_id, "getOfficialCyclesBalanceAdmin", "()", "-e", network]
        )
        if "Ok" not in payload:
            log_message(
                f"[CYCLES][{label}] getOfficialCyclesBalanceAdmin returned non-Ok: {payload}",
                "WARNING",
            )
            return None
        ok = payload["Ok"]
        official = int(ok["officialCyclesBalance"])
        current = int(ok["cycleBalance"])
    except Exception as e:
        log_message(f"[CYCLES][{label}] Failed to fetch cycle state for {canister_id}: {e}", "ERROR")
        return None

    diff = current - official
    prev = _prev_cycle_state.get(canister_id)
    rose = prev is not None and current > prev["current"]

    line = (
        f"[CYCLES][{label}] official={official:,} current={current:,} "
        f"diff(current-official)={diff:+,}"
    )
    if prev is not None:
        delta_current = current - prev["current"]
        delta_official = official - prev["official"]
        line += f" | since prev: Δcurrent={delta_current:+,} Δofficial={delta_official:+,}"

    log_message(line, "WARNING" if rose else "INFO")
    if rose:
        delta_current = current - prev["current"]
        log_message(
            f"[CYCLES][{label}] WARNING: Cycles.balance() ROSE by {delta_current:,} "
            f"since previous sample. Cycles should only rise via addCycles(). "
            f"Investigate: is this a late refund, auto-topup, or other unattributed deposit?",
            "WARNING",
        )

    _prev_cycle_state[canister_id] = {"official": official, "current": current}

    # Sample wallet balance too. If wallet drops while the canister's current
    # rises (or even stays flat after install/snapshot operations), it means
    # dfx is silently funding the canister via wallet → that is the
    # most likely source of the +N B "extra" cycles we keep observing
    # post-reinstall.
    global _prev_wallet_balance_cycles
    wallet = get_wallet_balance(network)
    if wallet is not None:
        wallet_line = f"[WALLET][{label}] balance={wallet:,}"
        wallet_dropped_significantly = False
        if _prev_wallet_balance_cycles is not None:
            delta_wallet = wallet - _prev_wallet_balance_cycles
            wallet_line += f" Δwallet={delta_wallet:+,}"
            # >100M cycles drop in one step is significant (normal query/update
            # cost is single digits of millions); flag it so we can correlate
            # with the canister's current-balance change at the same step.
            if delta_wallet < -100_000_000:
                wallet_dropped_significantly = True
        log_message(wallet_line, "WARNING" if wallet_dropped_significantly else "INFO")
        if wallet_dropped_significantly:
            log_message(
                f"[WALLET][{label}] WARNING: wallet dropped by {-delta_wallet:,} cycles "
                f"between samples (>100M). dfx may have silently sent cycles to the "
                f"canister or another IC entity during this step.",
                "WARNING",
            )
        _prev_wallet_balance_cycles = wallet

    return (official, current)

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
            result = run_command(["icp", "canister", "status", canister_id, "-e", network], retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
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

class CanisterDoesNotExistError(Exception):
    """Exception raised when a canister does not exist."""
    pass

def get_canister_wasm_hash(network: str, canister_id: str) -> Optional[str]:
    """Get the wasm hash of a canister with retry on transient network errors.

    Raises:
        CanisterDoesNotExistError: If the canister does not exist
    """
    try:
        result = run_command(["icp", "canister", "status", canister_id, "-e", network, "-p"], retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        for line in result.stdout.split('\n'):
            if 'Module hash:' in line:
                return line.split(':')[1].strip()
        return None
    except subprocess.CalledProcessError as e:
        # Check if the error is because canister does not exist
        error_text = ""
        if hasattr(e, 'stderr') and e.stderr:
            error_text = e.stderr

        if "does not exist" in error_text:
            raise CanisterDoesNotExistError(f"Canister {canister_id} does not exist")

        log_message(f"Failed to get wasm hash for {canister_id}: {e}", "WARNING")
        return None
    except Exception as e:
        log_message(f"Failed to get wasm hash for {canister_id}: {e}", "WARNING")
        return None

def stop_timer(network: str, canister_id: str, dry_run: bool = False) -> bool:
    """Stop the timer execution for a canister with retry on transient network errors."""
    log_message(f"Stopping timer for {canister_id}...")
    command = ["icp", "canister", "call", canister_id, "stopTimerExecutionAdmin", "()", "-e", network]
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
    command = ["icp", "canister", "call", canister_id, "startTimerExecutionAdmin", "()", "-e", network]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        # Check if the response indicates success (Ok variant)
        # dfx sometimes returns hash keys (17_724 for Ok, 1_081_532_264 for auth)
        if 'variant { Ok' in result.stdout or 'variant { 17_724' in result.stdout:
            log_message(f"Timer started for {canister_id}", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when starting timer: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to start timer for {canister_id}: {e}", "ERROR")
        return False

def get_game_state_id(network: str) -> str:
    """Read the game_state_canister principal for `network` directly from
    PoAIW/src/GameState/canister_ids.json. Same source dfx uses to resolve
    the `game_state_canister` alias. Raises KeyError if the network entry
    is missing — we cannot re-configure a mAIner without it.
    """
    with open(GAME_STATE_CANISTER_IDS_PATH, 'r') as f:
        ids = json.load(f)
    return ids["game_state_canister"][network]


def get_share_service_id(network: str) -> str:
    """Read the mainer_service_canister principal for `network` directly from
    PoAIW/src/mAIner/canister_ids.json. Raises KeyError if the network entry
    is missing and ValueError if the entry is empty — we cannot re-link a
    reinstalled ShareAgent without it.
    """
    with open(POAIW_CANISTER_IDS_PATH, 'r') as f:
        ids = json.load(f)
    value = ids["mainer_service_canister"][network]
    if not value:
        raise ValueError(
            f"mainer_service_canister['{network}'] is empty in {POAIW_CANISTER_IDS_PATH}"
        )
    return value


def set_game_state_canister_id(network: str, canister_id: str, gs_principal: str, dry_run: bool = False) -> bool:
    """Re-apply setGameStateCanisterId on a freshly-reinstalled mAIner."""
    log_message(f"Setting GameState canister id on {canister_id} -> {gs_principal}...")
    command = ["icp", "canister", "call", canister_id, "setGameStateCanisterId", f'("{gs_principal}")', "-e", network]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        if 'variant { Ok' in result.stdout or 'variant { 17_724' in result.stdout:
            log_message(f"GameState canister id set on {canister_id}", "SUCCESS")
            return True
        log_message(f"Unexpected response from setGameStateCanisterId: {result.stdout}", "ERROR")
        return False
    except Exception as e:
        log_message(f"Failed to set GameState canister id on {canister_id}: {e}", "ERROR")
        return False


def set_mainer_canister_type(network: str, canister_id: str, subtype: str, dry_run: bool = False) -> bool:
    """Re-apply setMainerCanisterType on a freshly-reinstalled mAIner.

    subtype must be one of: "Own", "ShareAgent", "ShareService", "NA".
    """
    VALID_SUBTYPES = {"Own", "ShareAgent", "ShareService", "NA"}
    if subtype not in VALID_SUBTYPES:
        log_message(f"Invalid mAIner subtype '{subtype}' (expected one of {VALID_SUBTYPES})", "ERROR")
        return False
    log_message(f"Setting mAIner canister type on {canister_id} -> variant {{ {subtype} }}...")
    command = ["icp", "canister", "call", canister_id, "setMainerCanisterType", f"(variant {{ {subtype} }})", "-e", network]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        if 'variant { Ok' in result.stdout or 'variant { 17_724' in result.stdout:
            log_message(f"mAIner canister type set on {canister_id}", "SUCCESS")
            return True
        log_message(f"Unexpected response from setMainerCanisterType: {result.stdout}", "ERROR")
        return False
    except Exception as e:
        log_message(f"Failed to set mAIner canister type on {canister_id}: {e}", "ERROR")
        return False


def get_burn_rate_setting(network: str, canister_id: str) -> Optional[str]:
    """Query the mAIner's current burn-rate setting. Returns the setter
    variant name ("Low" | "Mid" | "High" | "VeryHigh") or None if the
    endpoint fails, the canister is stopped, or the tier is non-standard.

    Note: the mAIner type uses variant `#Mid` where the UI shows "Medium".
    """
    log_message(f"Capturing burn-rate setting from {canister_id}...")
    try:
        data = icp_helpers.call_argv(
            ["icp", "canister", "call", canister_id, "getMainerStatisticsAdmin", "()", "-e", network]
        )
        cycles_burn_rate = data.get("Ok", {}).get("cyclesBurnRate", {}).get("cycles")
        mapping = {
            "1_000_000_000_000": "Low",
            "2_000_000_000_000": "Mid",
            "4_000_000_000_000": "High",
            "6_000_000_000_000": "VeryHigh",
        }
        variant = mapping.get(cycles_burn_rate)
        if variant is None:
            log_message(
                f"Burn-rate cycles '{cycles_burn_rate}' does not map to a standard "
                f"tier; will not re-apply (canister will default after reinstall).",
                "WARNING",
            )
            return None
        log_message(f"Captured burn-rate setting: {variant}", "SUCCESS")
        return variant
    except Exception as e:
        log_message(f"Failed to read burn-rate setting from {canister_id}: {e}", "WARNING")
        return None


def set_burn_rate_setting(network: str, canister_id: str, variant: str, dry_run: bool = False) -> bool:
    """Re-apply the burn-rate setting via updateAgentSettings.

    updateAgentSettings stops and restarts the mAIner's timers internally,
    so call this AFTER the explicit start_timer step. On a freshly-reinstalled
    canister the 24h cooldown is inactive (no previous settings), so the call
    always succeeds on the first attempt.
    """
    VALID = {"Low", "Mid", "High", "VeryHigh"}
    if variant not in VALID:
        log_message(f"Invalid burn-rate variant '{variant}' (expected one of {VALID})", "ERROR")
        return False
    log_message(f"Re-applying burn-rate setting on {canister_id} -> variant {{ {variant} }}...")
    command = ["icp", "canister", "call", canister_id, "updateAgentSettings", f"(record {{ cyclesBurnRate = variant {{ {variant} }} }})", "-e", network]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        if 'variant { Ok' in result.stdout or 'variant { 17_724' in result.stdout:
            log_message(f"Burn-rate setting applied on {canister_id}", "SUCCESS")
            return True
        log_message(f"Unexpected response from updateAgentSettings: {result.stdout}", "ERROR")
        return False
    except Exception as e:
        log_message(f"Failed to set burn-rate on {canister_id}: {e}", "ERROR")
        return False


def set_share_service_canister_id(network: str, canister_id: str, ss_principal: str, dry_run: bool = False) -> bool:
    """Re-apply setShareServiceCanisterId on a freshly-reinstalled ShareAgent mAIner."""
    log_message(f"Setting ShareService canister id on {canister_id} -> {ss_principal}...")
    command = ["icp", "canister", "call", canister_id, "setShareServiceCanisterId", f'("{ss_principal}")', "-e", network]
    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=5, retry_delay=10.0)
        if 'variant { Ok' in result.stdout or 'variant { 17_724' in result.stdout:
            log_message(f"ShareService canister id set on {canister_id}", "SUCCESS")
            return True
        log_message(f"Unexpected response from setShareServiceCanisterId: {result.stdout}", "ERROR")
        return False
    except Exception as e:
        log_message(f"Failed to set ShareService canister id on {canister_id}: {e}", "ERROR")
        return False


def reapply_post_reinstall_config(network: str, mainer: Dict, dry_run: bool = False) -> bool:
    """Re-apply the 3 mAIner-local setters that mAInerCreator.reinstallMainerctrl
    performs after a reinstall wipes stable state. Idempotent; safe to call twice.
    Mirrors PoAIW/src/mAInerCreator/src/Main.mo:1687-1738 (minimum-viable subset).
    """
    address = mainer["address"]
    try:
        subtype = list(mainer["canisterType"]["MainerAgent"].keys())[0]
    except (KeyError, IndexError, TypeError):
        log_message(f"{address}: could not determine MainerAgent subtype from mainer record", "ERROR")
        return False

    try:
        gs_principal = get_game_state_id(network)
    except (KeyError, FileNotFoundError, json.JSONDecodeError) as e:
        log_message(f"Could not resolve GameState principal for network '{network}': {e}", "ERROR")
        return False

    if not set_game_state_canister_id(network, address, gs_principal, dry_run):
        return False
    if not set_mainer_canister_type(network, address, subtype, dry_run):
        return False

    if subtype == "ShareAgent":
        try:
            ss_principal = get_share_service_id(network)
        except (KeyError, ValueError, FileNotFoundError, json.JSONDecodeError) as e:
            log_message(f"Could not resolve ShareService principal for network '{network}': {e}", "ERROR")
            return False
        if not set_share_service_canister_id(network, address, ss_principal, dry_run):
            return False

    return True


def check_queue(network: str, canister_id: str) -> Tuple[bool, Optional[datetime]]:
    """Check the queue for a canister and return status and last entry time."""
    log_message(f"Checking challenge queue for {canister_id}...")
    try:
        data = icp_helpers.call_argv(["icp", "canister", "call", canister_id, "getChallengeQueueAdmin", "()", "-e", network])
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
    command = ["icp", "canister", "call", canister_id, "resetChallengeQueueAdmin", "()", "-e", network]
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
    command = ["icp", "canister", "stop", canister_id, "-e", network]
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
    command = ["icp", "canister", "start", canister_id, "-e", network]
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
        # Expected format: "Created a new snapshot of canister xxx. Snapshot ID: yyy"
        # Older dfx wrote this to stderr; dfx 0.30+ writes it to stdout. Scan both.
        if result.returncode == 0:
            combined = (result.stdout or "") + "\n" + (result.stderr or "")
            for line in combined.split("\n"):
                if "Snapshot ID:" in line:
                    parts = line.split("Snapshot ID:")
                    if len(parts) >= 2:
                        snapshot_id = parts[1].strip()
                        log_message(f"Snapshot created: {snapshot_id}", "SUCCESS")
                        return snapshot_id

            log_message(
                f"Snapshot created but ID not parsed. stdout={result.stdout!r} stderr={result.stderr!r}",
                "WARNING",
            )
            return "created-but-not-parsed"
        else:
            log_message(
                f"Snapshot command failed (returncode={result.returncode}). stdout={result.stdout!r} stderr={result.stderr!r}",
                "ERROR",
            )
            return None
    except Exception as e:
        log_message(f"Failed to create snapshot for {canister_id}: {e}", "ERROR")
        return None

def upgrade_canister(network: str, canister_name: str, dry_run: bool = False, deploy_with_yes: bool = False, reinstall: bool = False) -> bool:
    """Upgrade (or reinstall) a canister with retry on transient network errors.

    Handles out-of-cycles errors by automatically topping up the canister with cycles.

    When reinstall=True, the canister is reinstalled (--mode reinstall), wiping all
    stable state. Use only when the goal is to reset accumulated memory.
    """
    def is_out_of_cycles_error(error_text: str) -> bool:
        """Check if error indicates canister is out of cycles during installation."""
        return "is out of cycles" in error_text and "IC0207" in error_text

    install_mode = "reinstall" if reinstall else "upgrade"
    log_message(f"{'Reinstalling' if reinstall else 'Upgrading'} {canister_name} (--mode {install_mode})...")

    command = ["icp", "deploy", canister_name, "--mode", install_mode, "-e", network, "-y"]
    # --wasm-memory-persistence is only valid with mode 'upgrade' or 'auto'
    if not reinstall:
        command.extend(["--wasm-memory-persistence", "keep"])
    # dfx reinstall prompts interactively ("YOU WILL LOSE ALL DATA...") which
    # would hang the non-interactive subprocess. The user has already confirmed
    # the reinstall at the top of this script, so always pass --yes for reinstall.
    if deploy_with_yes or reinstall:
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
    command = ["icp", "canister", "call", canister_id, "health", "()", "--query", "-e", network]
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
    command = ["icp", "canister", "call", canister_id, "getMaintenanceFlag", "()", "-e", network]

    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        data = icp_helpers.call_argv(command)
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
            toggle_command = ["icp", "canister", "call", canister_id, "toggleMaintenanceFlagAdmin", "()", "-e", network]
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
            toggle_command = ["icp", "canister", "call", canister_id, "toggleMaintenanceFlagAdmin", "()", "-e", network]
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

def should_skip_upgrade(network: str, address: str, target_hash: Optional[str], dry_run: bool = False, reinstall: bool = False) -> tuple[bool, Optional[str]]:
    """
    Determine if upgrade (or reinstall) should be skipped.

    Skip only if:
    1. target_hash is provided AND current_hash matches target_hash
    2. AND health check passes

    This applies to both --upgrade and --reinstall: if the canister is already
    running the target hash and is healthy, there is no reason to redeploy and
    disturb its state — the caller can drop --target-hash to force a reinstall
    for its state-wipe side effect alone. Canister-does-not-exist still skips.

    Args:
        network: Network name (e.g., 'testing', 'ic')
        address: Canister address
        target_hash: Target wasm hash (optional)
        dry_run: If True, simulates checks without making actual calls
        reinstall: Unused for skip-decision purposes; kept for signature parity

    Returns:
        Tuple of (should_skip: bool, skip_reason: Optional[str])
        skip_reason is "does_not_exist" if canister doesn't exist, None otherwise
    """
    # Get current hash
    try:
        current_hash = get_canister_wasm_hash(network, address)
    except CanisterDoesNotExistError:
        log_message(f"Canister {address} does not exist - skipping", "WARNING")
        return True, "does_not_exist"

    # Log current hash
    if current_hash:
        log_message(f"Current hash: {current_hash}", "INFO")
    else:
        log_message(f"Could not retrieve current hash", "WARNING")

    # If no target hash specified, don't skip
    if not target_hash:
        return False, None

    log_message(f"Target hash: {target_hash}", "INFO")

    # If hashes don't match, don't skip
    if current_hash != target_hash:
        log_message(f"Hash mismatch - upgrade needed", "INFO")
        return False, None

    # Hashes match - now check health
    log_message(f"Hash matches target - checking health before skipping", "INFO")
    health_ok, _ = check_health(network, address, dry_run)

    if health_ok:
        log_message(f"Already upgraded to target hash and health check passed - skipping", "INFO")
        return True, None
    else:
        log_message(f"Hash matches but health check failed - will upgrade anyway", "WARNING")
        return False, None

def upgrade_mainer(network: str, mainer: Dict, target_hash: Optional[str],
                  dry_run: bool = False, canister_index: int = 0, deploy_with_yes: bool = False,
                  reinstall: bool = False) -> bool:
    """Upgrade (or reinstall) a single mAIner through all steps.

    When reinstall=True, the canister is reinstalled instead of upgraded. Stable
    state is wiped, the post-deploy "hash unchanged" sanity check is skipped (a
    same-wasm reinstall produces the same hash), and the hash-match guard against
    target_hash is also skipped.
    """
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

    # Check cycles balance before upgrade
    cycles_balance = get_cycles_balance(network, address)
    if cycles_balance is not None:
        log_message(f"Canister cycles balance: {format_cycles(cycles_balance)}", "INFO")
    else:
        log_message(f"Canister cycles balance: Unable to retrieve", "WARNING")

    # Cycle-state baseline: query both Cycles.balance() and officialCyclesBalance
    # via getOfficialCyclesBalanceAdmin. Each subsequent sample compares against
    # the previous one and warns (yellow) if Cycles.balance() rose without an
    # addCycles() in between — the signature of an unattributed deposit.
    sample_cycle_state(network, address, "entry", dry_run)

    # Proactively top up if balance is low. Covers both IC0406 on self-calls
    # (upgrade path) and the freezing-threshold + install-code cost of reinstall.
    MIN_CYCLES_BALANCE = 500_000_000_000  # 500B
    TOPUP_CYCLES_AMOUNT = "500_000_000_000"  # 500B
    if cycles_balance is not None and cycles_balance < MIN_CYCLES_BALANCE:
        log_message(f"Cycles balance ({format_cycles(cycles_balance)}) is below {format_cycles(MIN_CYCLES_BALANCE)} threshold", "WARNING")
        log_message(f"Sending {TOPUP_CYCLES_AMOUNT} cycles to canister...", "INFO")
        if not dry_run:
            try:
                run_command([
                    "dfx", "wallet", "--network", network, "send", address, TOPUP_CYCLES_AMOUNT
                ])
                log_message(f"Successfully sent cycles to {address}", "SUCCESS")
                time.sleep(10)
                sample_cycle_state(network, address, "after pre-topup", dry_run)
            except Exception as e:
                log_message(f"Failed to send cycles to {address}: {e}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, "Could not top up cycles")
                return False

    # If we're reinstalling and the canister is currently Stopped, start it
    # first so pre-reinstall capture queries (burn rate) can succeed. Queries
    # against a stopped canister return IC0508. The normal flow will stop the
    # canister again at Step 2e before the actual reinstall.
    if reinstall and not dry_run and initial_status == "Stopped":
        log_message(
            f"Canister is Stopped but reinstall needs to read its state first; "
            f"starting it for pre-reinstall capture...",
            "WARNING",
        )
        if not start_canister(network, address, dry_run):
            log_message(f"Failed to start stopped canister for pre-reinstall capture", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_OTHER, "Could not start stopped canister for capture")
            return False
        time.sleep(30)  # give the state transition and timer warm-up a moment
        initial_status = get_canister_status(network, address)
        log_message(f"Canister status after start: {initial_status}", "INFO")

    # Capture user-configured settings BEFORE reinstall wipes stable state.
    # Can only succeed while the canister is Running; queries against a stopped
    # canister return IC0508. If capture fails, we let the mAIner fall back to
    # its default burn rate after reinstall.
    pre_reinstall_burn_rate = None
    if reinstall and not dry_run and initial_status != "Stopped":
        pre_reinstall_burn_rate = get_burn_rate_setting(network, address)

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

    # Step 2g: Deploy upgrade (or reinstall)
    if not upgrade_canister(network, canister_name, dry_run, deploy_with_yes, reinstall):
        log_message(f"Failed to {'reinstall' if reinstall else 'upgrade'} canister. Snapshot ID for rollback: {snapshot_id}", "ERROR")
        # Don't auto-rollback, let admin decide
        update_mainer_status(address, MainerStatus.FAILED_UPGRADE, f"{'Reinstall' if reinstall else 'Upgrade'} failed. Snapshot: {snapshot_id}")
        return False

    # Step 2h: Start canister
    if not start_canister(network, address, dry_run):
        log_message(f"Failed to start canister. Snapshot ID for rollback: {snapshot_id}", "ERROR")
        update_mainer_status(address, MainerStatus.FAILED_START, f"Could not start canister. Snapshot: {snapshot_id}")
        return False

    # First sample after the canister is Running again (post stop+snapshot+reinstall).
    # The Δcurrent here is dominated by the install_code prepay/refund (~300 B
    # added) plus snapshot create refund (~130 B added) — see Main.mo
    # INSTALL_CODE_REFUND_BUFFER comment.
    sample_cycle_state(network, address, "after dfx start (post-reinstall)", dry_run)

    # Step 2h.1: Immediately ensure the maintenance flag is ON. After --mode
    # reinstall, stable state is wiped and the flag defaults to OFF — without
    # this the mAIner could accept/process challenges during the brief window
    # before we re-apply configuration. After --mode upgrade the flag should
    # already be ON from Step 2b; turn_on_maintenance_flag is idempotent
    # (checks current state, toggles only when OFF) so it's a no-op then.
    if not turn_on_maintenance_flag(network, address, dry_run):
        log_message(
            f"Failed to turn on maintenance flag immediately after restart. Snapshot: {snapshot_id}",
            "ERROR",
        )
        update_mainer_status(
            address,
            MainerStatus.FAILED_MAINTENANCE,
            f"Could not turn on maintenance flag after restart. Snapshot: {snapshot_id}",
        )
        return False

    # Step 2h.5: Re-apply configuration that --mode reinstall wiped.
    # Mirrors the minimum-viable subset of mAInerCreator.reinstallMainerctrl
    # (setGameStateCanisterId, setMainerCanisterType, setShareServiceCanisterId).
    # No-op for plain upgrades (stable state persists).
    if reinstall and not dry_run:
        if not reapply_post_reinstall_config(network, mainer, dry_run):
            log_message(
                f"Failed to re-apply post-reinstall configuration. Snapshot: {snapshot_id}",
                "ERROR",
            )
            update_mainer_status(
                address,
                MainerStatus.FAILED_OTHER,
                f"Post-reinstall config failed. Snapshot: {snapshot_id}",
            )
            return False
        sample_cycle_state(network, address, "after reapply_post_reinstall_config", dry_run)

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
    sample_cycle_state(network, address, "after start_timer", dry_run)

    # Step 2j.5: Restore pre-reinstall burn-rate setting (reinstall only).
    # updateAgentSettings internally stops and restarts the timers so the new
    # setting takes effect. Non-fatal on failure — the canister just runs at
    # the default tier instead of the captured one.
    if reinstall and not dry_run and pre_reinstall_burn_rate:
        if not set_burn_rate_setting(network, address, pre_reinstall_burn_rate, dry_run):
            log_message(
                f"Could not restore burn-rate '{pre_reinstall_burn_rate}'; "
                f"canister will run at default tier. Snapshot: {snapshot_id}",
                "WARNING",
            )
        sample_cycle_state(network, address, "after set_burn_rate_setting (updateAgentSettings)", dry_run)

    # Step 2k: Turn off maintenance flag
    if not turn_off_maintenance_flag(network, address, dry_run):
        if not dry_run:
            log_message(f"Failed to turn off maintenance flag. Canister upgraded but maintenance flag may still be ON!", "ERROR")
            update_mainer_status(address, MainerStatus.FAILED_MAINTENANCE, f"Could not turn off maintenance flag. Snapshot: {snapshot_id}")
            return False
    sample_cycle_state(network, address, "after turn_off_maintenance_flag", dry_run)

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

    sample_cycle_state(network, address, "after health check (final)", dry_run)

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
                log_message(f"Hash mismatch after deploy! Expected: {target_hash}, Got: {post_upgrade_hash}. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Hash verification failed. Expected: {target_hash}, Got: {post_upgrade_hash}. Snapshot: {snapshot_id}")
                return False
            log_message(f"Hash verification passed: matches target hash", "SUCCESS")
        elif not reinstall:
            # If no target hash, verify that hash actually changed (upgrade only;
            # a same-wasm reinstall legitimately leaves the hash unchanged).
            if pre_upgrade_hash and post_upgrade_hash == pre_upgrade_hash:
                log_message(f"Hash did not change after upgrade! Hash: {post_upgrade_hash}. Snapshot ID for rollback: {snapshot_id}", "ERROR")
                update_mainer_status(address, MainerStatus.FAILED_OTHER, f"Hash unchanged after upgrade: {post_upgrade_hash}. Snapshot: {snapshot_id}")
                return False
            log_message(f"Hash verification passed: hash changed from {pre_upgrade_hash} to {post_upgrade_hash}", "SUCCESS")

    log_message(f"Successfully {'reinstalled' if reinstall else 'upgraded'} mAIner {canister_index}: {address}", "SUCCESS")
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
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="Reinstall instead of upgrade. WIPES all stable state on each canister. "
             "Use to reset accumulated memory after capping unbounded stable lists."
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
        log_message(f"Mode: {'REINSTALL (wipes stable state)' if args.reinstall else 'upgrade'}", "INFO")
        log_message(f"{'='*60}", "INFO")

        if args.dry_run:
            log_message("RUNNING IN DRY-RUN MODE - NO ACTUAL CHANGES WILL BE MADE", "WARNING")
            input("Press Enter to continue...")
        else:
            if args.reinstall:
                log_message("REINSTALL MODE: every selected canister will have its STABLE STATE WIPED", "WARNING")
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

                should_skip, skip_reason = should_skip_upgrade(args.network, address, args.target_hash, args.dry_run, args.reinstall)
                if should_skip:
                    if skip_reason == "does_not_exist":
                        update_mainer_status(address, MainerStatus.SKIPPED_DOES_NOT_EXIST, "Canister does not exist")
                    else:
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
                if upgrade_mainer(args.network, mainer, args.target_hash, args.dry_run, i, args.deploy_with_yes, args.reinstall):
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