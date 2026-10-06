"""
Make the mAInerCreator the sole controller of every mAIner ShareAgent.

WHY
    In preparation for the SNS. Two dev principals holding controller rights on every
    mAIner is exactly the centralisation the SNS is meant to remove: a controller can
    install arbitrary code, so as long as they are controllers the DAO does not really
    own the fleet. After this script the chain is DAO -> mAInerCreator -> ShareAgent,
    with no human principal anywhere in it.

    New ShareAgents are already created this way (PoAIW/src/mAInerCreator/src/Main.mo).
    This script brings the ~754 ShareAgents that predate that change into line.

ORDER MATTERS
    Per mAIner: set the log viewers FIRST, remove the controllers SECOND.

    log_visibility defaults to #controllers, so removing the maintainers as controllers
    also removes their ability to read the canister's logs. #allowed_viewers gives that
    back - it grants fetch_canister_logs and nothing else - but setting it is itself a
    controller-only call, so it has to happen while we still are one.

WASM GUARDS
    --target-hash guards the mAIner's own wasm and is required on prd, exactly as in
    migrate_mainer_owner_access.py. --creator-hash optionally pins the mAInerCreator wasm.

    The deployed mAInerCreator (PoAIW c69ed39) does not know the `allowed_viewers`
    variant, so it would trap decoding canister_status of a mAIner with log viewers set.
    Its only canister_status callers are addControllerToMainerCanister and
    removeControllerFromMainerCanister, and nothing calls those, so this is safe.

END STATE
    Every ShareAgent has exactly one controller - the mAInerCreator - and both maintainer
    principals as allowed log viewers.

GETTING BACK IN
    Controller-only management calls (stop, start, snapshot, status) stop working against
    the ShareAgents, so upgrade_mainers.py cannot run against them. Upgrades routed
    GameState -> mAInerCreator (install_code) keep working. To make the maintainers
    controllers again, the mAInerCreator first needs an upgrade that adds an endpoint for
    it (planned post-SNS: addMaintainerControllersToMainerAdmin).

To run:
    # from the folder: funnAI
    conda activate funnAI

    TARGET_HASH=0x...    # the wasm every mAIner must be on, WITH the 0x prefix
    scripts/remove_maintainer_controllers.sh --network $NETWORK --target-hash $TARGET_HASH [--creator-hash 0x...] [--num 10] [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

# Reuse the tested helpers rather than duplicating retry/logging/status logic.
from . import update_admin_rbac_mainers as rbac
from .monitor_common import MAINTAINER_PRINCIPALS
# Same hash reader the upgrade script uses, so the comparison semantics match exactly
# (it returns `dfx canister info` output verbatim, i.e. WITH the 0x prefix).
from .upgrade_mainers import get_canister_wasm_hash

SCRIPT_DIR = Path(__file__).parent.resolve()

LOG_FILE_PATH = SCRIPT_DIR / "logs-admin-rbac" / "remove_maintainer_controllers.logs"


def mainer_creator(network: str) -> str:
    """The mAInerCreator canister id for this network - the only allowed controller."""
    env_path = SCRIPT_DIR / f"canister_ids-{network}.env"
    if not env_path.exists():
        rbac.log_message(f"Missing {env_path}", "ERROR")
        sys.exit(1)
    creator = dotenv_values(env_path).get("SUBNET_0_1_MAINER_CREATOR", "").strip('"')
    if not creator:
        rbac.log_message(f"SUBNET_0_1_MAINER_CREATOR not set in {env_path}", "ERROR")
        sys.exit(1)
    return creator


def get_info(network: str, canister_id: str):
    """
    Controllers + module hash via `dfx canister info`.

    Deliberately NOT `dfx canister status`: info is served from read_state and works for
    any caller, while status is a controller-only management call. This script removes
    its own controller rights as it goes, so status stops working on exactly the
    canisters it has already processed - which is precisely when the end state has to be
    verified.
    """
    try:
        result = rbac.run_command(
            ["dfx", "canister", "--network", network, "info", canister_id],
            retry_on_transient_errors=True, max_retries=3, retry_delay=2.0,
        )
    except subprocess.CalledProcessError:
        return None, None

    text = (result.stdout or "") + (result.stderr or "")
    controllers, module_hash = None, None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Controllers:"):
            controllers = set(line.split(":", 1)[1].split())
        elif line.startswith("Module hash:"):
            module_hash = line.split(":", 1)[1].strip()
    return controllers, module_hash


def set_log_viewers(network: str, canister_id: str, dry_run: bool) -> bool:
    """
    Make both maintainers allowed log viewers.

    --set-log-viewer, not --add-log-viewer: it states the exact end state, so it is
    idempotent whether the canister currently has #controllers, #public or a partial
    viewer list.
    """
    command = ["dfx", "canister", "--network", network, "update-settings", canister_id]
    for principal in MAINTAINER_PRINCIPALS:
        command += ["--set-log-viewer", principal]

    if dry_run:
        rbac.log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        rbac.run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)
        rbac.log_message("Set both maintainers as log viewers", "SUCCESS")
        return True
    except Exception as e:
        rbac.log_message(f"Failed to set log viewers: {e}", "ERROR")
        return False


def verify_log_viewers(network: str, canister_id: str) -> bool:
    """
    Confirm the maintainers can read the logs, BEFORE giving up the rights to check.

    Two checks, because neither is available on its own afterwards: `dfx canister status`
    reports log visibility but is controller-only, and `dfx canister logs` succeeding for
    the current (maintainer) identity is the actual acceptance criterion and keeps working
    once the controllers are gone.
    """
    try:
        result = rbac.run_command(
            ["dfx", "canister", "--network", network, "status", canister_id],
            retry_on_transient_errors=True, max_retries=3, retry_delay=2.0,
        )
        text = (result.stdout or "") + (result.stderr or "")
        for line in text.splitlines():
            if "visibility" in line.lower():
                if all(p in line for p in MAINTAINER_PRINCIPALS):
                    return True
                rbac.log_message(f"Log visibility line does not list both maintainers: {line.strip()}",
                                 "WARNING")
                break
    except Exception as e:
        rbac.log_message(f"Could not read canister status to check log visibility: {e}", "WARNING")

    # Fall back to the check that still works after the controllers are removed.
    rbac.log_message("Falling back to `dfx canister logs` to confirm log access...", "INFO")
    try:
        rbac.run_command(
            ["dfx", "canister", "--network", network, "logs", canister_id],
            retry_on_transient_errors=True, max_retries=3, retry_delay=2.0,
        )
        rbac.log_message("Log access confirmed", "SUCCESS")
        return True
    except Exception as e:
        rbac.log_message(f"Could not read the canister logs: {e}", "ERROR")
        return False


def remove_controllers(network: str, canister_id: str, to_remove: list, dry_run: bool) -> bool:
    """
    Drop every non-canonical controller in ONE call.

    One call rather than one per principal, because the identity running this script is
    itself one of the maintainers: removing it first would leave the script without the
    rights to remove the other. Removing them in a single message sidesteps the ordering
    entirely, and leaves no intermediate single-maintainer state.

    --remove-controller rather than --set-controller: the removals are computed from the
    canister's actual controller set, so a wrong SUBNET_0_1_MAINER_CREATOR value can
    never orphan a canister.

    --yes is required: dfx interactively confirms any change that costs the caller its
    own control, and would otherwise stall on every canister.
    """
    command = ["dfx", "canister", "--network", network, "update-settings", canister_id]
    for principal in to_remove:
        command += ["--remove-controller", principal]
    command.append("--yes")

    if dry_run:
        rbac.log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        rbac.run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)
        rbac.log_message(f"Removed {len(to_remove)} controller(s)", "SUCCESS")
        return True
    except Exception as e:
        rbac.log_message(f"Failed to remove controllers: {e}", "ERROR")
        return False


def process_mainer(network: str, mainer: dict, creator: str, dry_run: bool,
                   target_hash: str = None) -> bool:
    address = mainer.get("address", "")

    rbac.log_message("=" * 60, "INFO")
    rbac.log_message(f"Processing mAIner: {address}", "INFO")

    controllers, module_hash = get_info(network, address)
    if controllers is None:
        rbac.update_mainer_status(address, "failed", "could not read controllers")
        return False

    # --- Guard: only touch mAIners already on the target wasm ---
    if target_hash:
        if module_hash is None:
            rbac.log_message("Could not read the module hash - skipping", "WARNING")
            rbac.update_mainer_status(address, "skipped", "module hash unreadable")
            return True
        if module_hash != target_hash:
            rbac.log_message(
                f"Not on the target wasm yet - skipping. Has {module_hash}, needs {target_hash}",
                "WARNING")
            rbac.update_mainer_status(address, "skipped", "not on target wasm")
            return True

    # --- Guard: never strand a canister ---
    if creator not in controllers:
        rbac.log_message(
            f"mAInerCreator {creator} is not a controller of this mAIner "
            f"(has {sorted(controllers)}) - refusing to remove anything",
            "ERROR")
        rbac.update_mainer_status(address, "failed", "mAInerCreator is not a controller")
        return False

    to_remove = sorted(controllers - {creator})
    if not to_remove:
        rbac.log_message("mAInerCreator is already the sole controller", "INFO")
        rbac.update_mainer_status(address, "already_granted")
        return True

    for principal in to_remove:
        if principal not in MAINTAINER_PRINCIPALS:
            # Neither the creator nor a maintainer: the shadow-controller pattern.
            rbac.log_message(f"NOTE: {principal} is neither the mAInerCreator nor a maintainer",
                             "WARNING")

    # --- Step 1: log viewers, while we are still a controller ---
    rbac.log_message("Step 1: setting the maintainers as log viewers...", "INFO")
    if not set_log_viewers(network, address, dry_run):
        rbac.update_mainer_status(address, "failed", "could not set log viewers")
        return False

    if not dry_run:
        if not verify_log_viewers(network, address):
            rbac.log_message("Could not confirm log access - NOT removing controllers", "ERROR")
            rbac.update_mainer_status(address, "failed", "log viewers not verified")
            return False

    # --- Step 2: remove every controller except the mAInerCreator ---
    rbac.log_message(f"Step 2: removing {len(to_remove)} controller(s): {to_remove}", "INFO")
    if not remove_controllers(network, address, to_remove, dry_run):
        rbac.update_mainer_status(address, "failed", "could not remove controllers")
        return False

    # --- Step 3: assert the end state ---
    if not dry_run:
        rbac.log_message("Step 3: verifying the final controller set...", "INFO")
        final, _ = get_info(network, address)
        if final != {creator}:
            rbac.log_message(
                f"Final controller set is {sorted(final or [])}, expected {[creator]}", "ERROR")
            rbac.update_mainer_status(address, "failed", "final controller set is not the creator alone")
            return False
        rbac.log_message("mAInerCreator is the sole controller", "SUCCESS")

    rbac.update_mainer_status(address, "success")
    return True


def check_creator_wasm(network: str, creator: str, creator_hash: str) -> None:
    """
    Refuse to run against a mAInerCreator that predates the allowed_viewers type.

    See PREREQUISITE in the module docstring: an older build traps when it decodes
    canister_status of a mAIner whose log_visibility is #allowed_viewers, which is the
    state this script puts every ShareAgent into.
    """
    current = get_canister_wasm_hash(network, creator)
    if current is None:
        rbac.log_message(f"Could not read the mAInerCreator module hash for {creator}", "ERROR")
        sys.exit(1)
    if current != creator_hash:
        rbac.log_message(
            f"mAInerCreator {creator} runs {current}, expected {creator_hash}. "
            "Check --creator-hash.",
            "ERROR")
        sys.exit(1)
    rbac.log_message(f"mAInerCreator {creator} is on the expected wasm ({current})", "SUCCESS")


def main():
    parser = argparse.ArgumentParser(
        description="Remove the maintainer principals as controllers of the mAIner "
                    "ShareAgents, leaving the mAInerCreator as the sole controller."
    )
    parser.add_argument("--network", required=True,
                        choices=["local", "ic", "testing", "demo", "development", "prd"])
    parser.add_argument("--num", type=int, default=None,
                        help="Process at most this many mAIners (default: all)")
    parser.add_argument("--mainer", default=None,
                        help="Process only this mAIner canister id. Use it to do the "
                             "first one on its own before running a batch.")
    parser.add_argument("--target-hash", default=None,
                        help="Only process mAIners already on this wasm hash. "
                             "WITH the 0x prefix, as printed by `dfx canister info`. "
                             "Required on prd.")
    parser.add_argument("--creator-hash", default=None,
                        help="Optional: only run if the mAInerCreator is on this wasm hash. "
                             "WITH the 0x prefix.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # On prd both guards are not optional: these are real users' mAIners.
    if args.network == "prd" and not args.target_hash:
        parser.error("--target-hash is required on prd.")
    for name, value in (("--target-hash", args.target_hash), ("--creator-hash", args.creator_hash)):
        if value and not value.startswith("0x"):
            parser.error(f"{name} must start with 0x (got {value}). It is compared verbatim "
                         "against `dfx canister info` output.")

    # Point the reused logging at this script's log file.
    rbac.LOG_FILE_PATH = LOG_FILE_PATH
    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        rbac.log_file_handle = open(LOG_FILE_PATH, "w")
    except Exception as e:
        print(f"Warning: could not open log file {LOG_FILE_PATH}: {e}")
        rbac.log_file_handle = None

    try:
        creator = mainer_creator(args.network)

        rbac.log_message("=" * 60, "INFO")
        rbac.log_message("Remove the maintainers as controllers of the mAIner ShareAgents", "INFO")
        rbac.log_message(f"Network: {args.network}", "INFO")
        rbac.log_message(f"mAInerCreator (sole controller): {creator}", "INFO")
        rbac.log_message(f"Maintainers to remove: {MAINTAINER_PRINCIPALS}", "INFO")
        rbac.log_message(f"Target wasm hash: {args.target_hash or 'NOT SET - guard disabled'}",
                         "INFO" if args.target_hash else "WARNING")
        rbac.log_message(f"mAInerCreator wasm hash: {args.creator_hash or 'NOT SET - guard disabled'}",
                         "INFO" if args.creator_hash else "WARNING")
        rbac.log_message(f"Specific mAIner: {args.mainer or 'None - all'}", "INFO")
        rbac.log_message(f"Dry Run: {args.dry_run}", "INFO")
        rbac.log_message("=" * 60, "INFO")

        if args.creator_hash:
            check_creator_wasm(args.network, creator, args.creator_hash)

        if args.dry_run:
            rbac.log_message("DRY-RUN MODE - NO CHANGES WILL BE MADE", "WARNING")
        else:
            rbac.log_message("LIVE RUN - the maintainers will lose controller rights on "
                             "these mAIners, and with them stop/start/snapshot/status", "WARNING")
            rbac.log_message("Getting them back needs a mAInerCreator upgrade first.", "WARNING")
            if input("Type 'yes' to continue: ").lower() != "yes":
                rbac.log_message("Cancelled", "INFO")
                sys.exit(0)

        mainers = [m for m in rbac.get_mainers(args.network) if m.get("address")]

        # Only ShareAgents. GameState's registry also returns the ShareService, which
        # keeps the maintainers as controllers - it runs a different wasm and is not part
        # of the SNS-owned fleet. Matches the filter in upgrade_mainers.py.
        share_agents = []
        for m in mainers:
            subtype_dict = m.get("canisterType", {}).get("MainerAgent", {})
            subtype = list(subtype_dict.keys())[0] if subtype_dict else ""
            if subtype == "ShareAgent":
                share_agents.append(m)
            else:
                rbac.log_message(
                    f"Skipping {m['address']} - canisterType is "
                    f"{subtype or m.get('canisterType')}, not ShareAgent",
                    "INFO",
                )
        mainers = share_agents

        if args.mainer:
            # Filter before --num so the two compose predictably.
            mainers = [m for m in mainers if m["address"] == args.mainer]
            if not mainers:
                rbac.log_message(
                    f"{args.mainer} is not a ShareAgent registered with GameState on "
                    f"{args.network}. Nothing to do.",
                    "ERROR",
                )
                sys.exit(1)

        if args.num is not None:
            mainers = mainers[: args.num]

        total = len(mainers)
        if total == 0:
            rbac.log_message("No mAIners found", "WARNING")
            sys.exit(0)
        rbac.log_message(f"Will process {total} mAIner(s)", "SUCCESS")

        rbac.total_mainers_to_process = total
        for i, mainer in enumerate(mainers):
            rbac.current_mainer_index = i
            if rbac.interrupted:
                rbac.log_message("Interrupted by user", "WARNING")
                break
            try:
                if not process_mainer(args.network, mainer, creator, args.dry_run,
                                      args.target_hash):
                    rbac.log_message(f"Failed on mAIner {i}. Stopping.", "ERROR")
                    break
            except Exception as e:
                rbac.log_message(f"Unexpected error on mAIner {i}: {e}", "ERROR")
                rbac.update_mainer_status(mainer.get("address", ""), "failed", str(e))
                break
        rbac.current_mainer_index = None
        rbac.total_mainers_to_process = None

        rbac.print_status_report()
        if rbac.get_status_summary().get("failed", 0) > 0:
            sys.exit(1)
    finally:
        if rbac.log_file_handle:
            rbac.log_file_handle.close()


if __name__ == "__main__":
    main()
