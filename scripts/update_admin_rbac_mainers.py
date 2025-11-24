"""
Admin RBAC Update Script for mAIners

This script updates Admin RBAC roles for all mAIner canisters by granting AdminQuery access.

To run:
    # from the folder: funnAI
    conda activate llama_cpp_canister

    # Assign AdminQuery role for principal:
    PRINCIPAL=...
    scripts/update_admin_rbac_mainers.sh --network $NETWORK --principal $PRINCIPAL [--action assign] [--dry-run]

    # Revoke admin role for principal:
    scripts/update_admin_rbac_mainers.sh --network $NETWORK --principal $PRINCIPAL --action revoke [--dry-run]

To run unit tests:
    # from the root of the repository
    conda activate llama_cpp_canister
    pytest scripts/test/test_update_admin_rbac_mainers.py -v
"""

import subprocess
import time
import argparse
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional
import signal
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = Path(__file__).parent.resolve()

# Log file path
LOG_FILE_PATH = SCRIPT_DIR / "logs-admin-rbac" / "update_admin_rbac_mainers.logs"

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
mainer_status_tracker: Dict[str, Dict] = {}

def update_mainer_status(address: str, status: str, error_msg: Optional[str] = None):
    """
    Update the status of a mAIner in the global tracker.

    Args:
        address: Canister address
        status: Status string (success, failed, skipped, already_granted)
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
        status = data['status']
        summary[status] = summary.get(status, 0) + 1
    return summary

def print_status_report():
    """Print a concise status report of all mAIners."""
    if not mainer_status_tracker:
        log_message("No mAIners tracked", "INFO")
        return

    # Get summary counts
    summary = get_status_summary()

    success_count = summary.get('success', 0)
    already_granted_count = summary.get('already_granted', 0)
    already_revoked_count = summary.get('already_revoked', 0)
    failed_count = summary.get('failed', 0)
    skipped_count = summary.get('skipped', 0)

    total_processed = success_count + already_granted_count + already_revoked_count + failed_count + skipped_count

    # Print concise summary
    log_message(f"{'='*60}", "INFO")
    log_message("ADMIN RBAC UPDATE SUMMARY", "INFO")
    log_message(f"Processed: {total_processed} mAIner(s)", "INFO")
    log_message(f"  ✓ Updated: {success_count}", "SUCCESS" if success_count > 0 else "INFO")
    log_message(f"  ⊘ Already granted: {already_granted_count}", "INFO")
    log_message(f"  ⊘ Already revoked: {already_revoked_count}", "INFO")
    log_message(f"  ⊘ Skipped: {skipped_count}", "INFO")
    log_message(f"  ✗ Failed: {failed_count}", "ERROR" if failed_count > 0 else "INFO")

    # Show failed mAIners with details if any
    if failed_count > 0:
        log_message("\nFailed mAIners:", "ERROR")
        for address, data in mainer_status_tracker.items():
            if data['status'] == 'failed':
                error_msg = f" - {data['error']}" if data.get('error') else ""
                log_message(f"  {address}{error_msg}", "ERROR")

    log_message(f"\nDetailed log saved to: {LOG_FILE_PATH}", "INFO")
    log_message(f"{'='*60}", "INFO")

def signal_handler(sig, frame):  # noqa: ARG001
    """Handle Ctrl+C interruption gracefully."""
    global interrupted, log_file_handle
    interrupted = True
    print(f"\n{RED}Process interrupted! Current canister may need manual inspection.{NC}")

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
    retry_on_transient_errors: bool = False,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> subprocess.CompletedProcess:
    """Run a command and return the result.

    Args:
        command: Command to run as list of strings
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise on non-zero exit code
        retry_on_transient_errors: If True, retry on transient errors like timeouts, IC0508, etc.
        max_retries: Maximum number of retry attempts (only used if retry_on_transient_errors=True)
        retry_delay: Base delay between retries in seconds (exponential backoff applied)
    """
    # Log the command being executed
    cmd_str = ' '.join(command)
    capture_info = " (capturing output)" if capture_output else " (not capturing output)"
    log_message(f"Executing: {cmd_str}{capture_info}", "INFO")

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
            "timed out",
            "Operation timed out",
            "tcp connect error",
            "connection refused",
            "Connection refused",
            "temporarily unavailable",
            "error sending request",
            "client error (Connect)"
        ]
        return any(indicator in stderr for indicator in transient_indicators)

    attempt = 0
    while True:
        try:
            if capture_output:
                result = subprocess.run(command, capture_output=True, text=True, check=check)
                return result
            else:
                result = subprocess.run(command, check=check)
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
        ], retry_on_transient_errors=True, max_retries=5, retry_delay=3.0)
        data = json.loads(result.stdout)
        mainers = data.get('Ok', [])
        log_message(f"Found {len(mainers)} total mAIners", "INFO")
        return mainers
    except Exception as e:
        log_message(f"Failed to get mAIners: {e}", "ERROR")
        sys.exit(1)

def get_admin_roles(network: str, canister_id: str, dry_run: bool = False) -> Optional[List[Dict]]:
    """Get the admin roles for a canister.

    Returns:
        List of admin role assignments, or None if the call fails
    """
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "getAdminRoles", "--output", "json"
    ]

    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return []

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)
        data = json.loads(result.stdout)

        if 'Ok' in data:
            return data['Ok']
        else:
            log_message(f"Unexpected response format: {data}", "WARNING")
            return None
    except subprocess.CalledProcessError as e:
        # Check if the error is because the method doesn't exist (old canister)
        if e.stderr and ("has no query method 'getAdminRoles'" in e.stderr or "IC0536" in e.stderr):
            log_message(f"Canister {canister_id} does not have getAdminRoles method (old version)", "WARNING")
            return None
        log_message(f"Failed to get admin roles for {canister_id}: {e}", "ERROR")
        return None
    except Exception as e:
        log_message(f"Failed to get admin roles for {canister_id}: {e}", "ERROR")
        return None

def assign_admin_role(network: str, canister_id: str, principal: str, note: str, dry_run: bool = False) -> bool:
    """Assign AdminQuery role to a principal.

    Returns:
        True if successful, False otherwise
    """
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "assignAdminRole",
        f'( record {{ "principal" = "{principal}"; role = variant {{ AdminQuery }}; note = "{note}" }} )'
    ]

    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)

        # Check for successful assignment (should contain Ok variant)
        if ('variant' in result.stdout) and ('Ok' in result.stdout or '17_724' in result.stdout):
            log_message(f"Successfully assigned AdminQuery role to {principal}", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when assigning role: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to assign admin role: {e}", "ERROR")
        return False

def revoke_admin_role(network: str, canister_id: str, principal: str, dry_run: bool = False) -> bool:
    """Revoke admin role from a principal.

    Returns:
        True if successful, False otherwise
    """
    command = [
        "dfx", "canister", "--network", network, "call",
        canister_id, "revokeAdminRole",
        f'( "{principal}")'
    ]

    if dry_run:
        log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True

    try:
        result = run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)

        # Check for successful revocation (should contain Ok variant)
        if ('variant' in result.stdout) and ('Ok' in result.stdout or '17_724' in result.stdout):
            log_message(f"Successfully revoked admin role from {principal}", "SUCCESS")
            return True
        else:
            log_message(f"Unexpected response when revoking role: {result.stdout}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Failed to revoke admin role: {e}", "ERROR")
        return False

def principal_has_role(admin_roles: List[Dict], principal: str) -> bool:
    """Check if a principal already has an admin role assigned.

    Args:
        admin_roles: List of admin role assignments
        principal: Principal ID to check

    Returns:
        True if principal already has a role, False otherwise
    """
    if not admin_roles:
        return False

    for role_assignment in admin_roles:
        if role_assignment.get('principal') == principal:
            return True

    return False

def update_mainer_rbac(network: str, mainer: Dict, principal: str, action: str, note: str, dry_run: bool = False) -> bool:
    """Update Admin RBAC for a single mAIner.

    Args:
        network: Network name
        mainer: mAIner dict with address and other info
        principal: Principal ID to assign/revoke role
        action: 'assign' or 'revoke'
        note: Note for assignment (not used for revoke)
        dry_run: If True, simulates actions without making changes

    Returns:
        True if successful or already in desired state, False otherwise
    """
    address = mainer.get('address', '')

    log_message(f"{'='*60}", "INFO")
    log_message(f"Processing mAIner: {address}", "INFO")

    # Step 1: Get current admin roles
    log_message(f"Step 1: Getting current admin roles...", "INFO")
    admin_roles = get_admin_roles(network, address, dry_run)

    if admin_roles is None:
        log_message(f"Skipping {address} - method not available or error occurred", "WARNING")
        update_mainer_status(address, 'skipped', "getAdminRoles method not available")
        return True  # Don't fail the whole process for old canisters

    has_role = principal_has_role(admin_roles, principal)

    if action == 'assign':
        # Check if principal already has a role
        if has_role:
            log_message(f"Principal {principal} already has admin role - skipping", "INFO")
            update_mainer_status(address, 'already_granted')
            return True

        # Step 2: Assign the role
        log_message(f"Step 2: Assigning AdminQuery role to {principal}...", "INFO")
        if not assign_admin_role(network, address, principal, note, dry_run):
            log_message(f"Failed to assign role", "ERROR")
            update_mainer_status(address, 'failed', "Could not assign role")
            return False

        # Step 3: Verify the role was assigned (if not dry run)
        if not dry_run:
            log_message(f"Step 3: Verifying role assignment...", "INFO")
            time.sleep(2)  # Give canister a moment to process

            admin_roles_after = get_admin_roles(network, address, dry_run)

            if admin_roles_after is None:
                log_message(f"Failed to verify role assignment - could not get admin roles", "ERROR")
                update_mainer_status(address, 'failed', "Could not verify role assignment")
                return False

            if principal_has_role(admin_roles_after, principal):
                log_message(f"Role assignment verified successfully", "SUCCESS")
                update_mainer_status(address, 'success')
                return True
            else:
                log_message(f"Role assignment verification failed - principal not found in admin roles", "ERROR")
                update_mainer_status(address, 'failed', "Role not found after assignment")
                return False
        else:
            update_mainer_status(address, 'success')
            return True

    elif action == 'revoke':
        # Check if principal doesn't have a role
        if not has_role:
            log_message(f"Principal {principal} does not have admin role - skipping", "INFO")
            update_mainer_status(address, 'already_revoked')
            return True

        # Step 2: Revoke the role
        log_message(f"Step 2: Revoking admin role from {principal}...", "INFO")
        if not revoke_admin_role(network, address, principal, dry_run):
            log_message(f"Failed to revoke role", "ERROR")
            update_mainer_status(address, 'failed', "Could not revoke role")
            return False

        # Step 3: Verify the role was revoked (if not dry run)
        if not dry_run:
            log_message(f"Step 3: Verifying role revocation...", "INFO")
            time.sleep(2)  # Give canister a moment to process

            admin_roles_after = get_admin_roles(network, address, dry_run)

            if admin_roles_after is None:
                log_message(f"Failed to verify role revocation - could not get admin roles", "ERROR")
                update_mainer_status(address, 'failed', "Could not verify role revocation")
                return False

            if not principal_has_role(admin_roles_after, principal):
                log_message(f"Role revocation verified successfully", "SUCCESS")
                update_mainer_status(address, 'success')
                return True
            else:
                log_message(f"Role revocation verification failed - principal still found in admin roles", "ERROR")
                update_mainer_status(address, 'failed', "Role still present after revocation")
                return False
        else:
            update_mainer_status(address, 'success')
            return True

    return False

def main():
    parser = argparse.ArgumentParser(
        description="Update Admin RBAC roles for mAIner canisters"
    )
    parser.add_argument(
        "--network",
        required=True,
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        help="Network to update admin RBAC on"
    )
    parser.add_argument(
        "--principal",
        required=True,
        help="Principal ID to assign/revoke AdminQuery role"
    )
    parser.add_argument(
        "--action",
        choices=["assign", "revoke"],
        default="assign",
        help="Action to perform: 'assign' or 'revoke' (default: assign)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode without making actual changes"
    )

    args = parser.parse_args()

    # The note (only used for assign)
    note = "Grant AdminQuery access for funnai-django"

    # Open log file
    global log_file_handle
    try:
        # Ensure the logs directory exists
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        log_file_handle = open(LOG_FILE_PATH, 'w')
    except Exception as e:
        print(f"{RED}Warning: Could not open log file {LOG_FILE_PATH}: {e}{NC}")
        log_file_handle = None

    try:
        log_message(f"{'='*60}", "INFO")
        log_message(f"Admin RBAC Update Script for mAIners", "INFO")
        log_message(f"Log file: {LOG_FILE_PATH}", "INFO")
        log_message(f"Network: {args.network}", "INFO")
        log_message(f"Principal: {args.principal}", "INFO")
        log_message(f"Action: {args.action}", "INFO")
        if args.action == 'assign':
            log_message(f"Note: {note}", "INFO")
        log_message(f"Dry Run: {args.dry_run}", "INFO")
        log_message(f"{'='*60}", "INFO")

        if args.dry_run:
            log_message("RUNNING IN DRY-RUN MODE - NO ACTUAL CHANGES WILL BE MADE", "WARNING")
        else:
            log_message("THIS IS A LIVE RUN - CHANGES WILL BE MADE TO CANISTERS", "WARNING")
            confirm = input("Type 'yes' to continue: ")
            if confirm.lower() != 'yes':
                log_message("Update cancelled", "INFO")
                sys.exit(0)

        # Get all mAIners
        mainers = get_mainers(args.network)

        # Filter to only ShareAgent mAIners with non-empty addresses
        share_agent_mainers = []
        for mainer in mainers:
            address = mainer.get('address', '')
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

            # Skip if not ShareAgent type or empty address
            if canister_type != "ShareAgent" or address == "":
                continue

            share_agent_mainers.append(mainer)

        total_mainers = len(share_agent_mainers)

        if total_mainers == 0:
            log_message("No ShareAgent mAIners found to update", "WARNING")
            sys.exit(0)

        log_message(f"Will process {total_mainers} ShareAgent mAIners", "SUCCESS")

        # Set global progress tracking for logging
        global current_mainer_index, total_mainers_to_process
        total_mainers_to_process = total_mainers

        # Process mAIners
        for i, mainer in enumerate(share_agent_mainers):
            current_mainer_index = i

            if interrupted:
                log_message("Process interrupted by user", "WARNING")
                break

            try:
                if not update_mainer_rbac(args.network, mainer, args.principal, args.action, note, args.dry_run):
                    log_message(f"Failed to update RBAC for mAIner {i}. Stopping process.", "ERROR")
                    break
            except Exception as e:
                address = mainer.get('address', '')
                log_message(f"Unexpected error updating mAIner {i}: {e}", "ERROR")
                update_mainer_status(address, 'failed', f"Unexpected error: {str(e)}")
                break

        # Reset progress tracking
        current_mainer_index = None
        total_mainers_to_process = None

        # Print status report
        print_status_report()

        # Check if any failed
        summary = get_status_summary()
        if summary.get('failed', 0) > 0:
            sys.exit(1)
    finally:
        # Always close log file
        if log_file_handle:
            log_file_handle.close()

if __name__ == "__main__":
    main()
