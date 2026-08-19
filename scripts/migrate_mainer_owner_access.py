"""
Migrate mAIner owner access: grant #AdminQuery, then remove the owner as controller.

WHY
    A mAIner owner used to be a controller of their own mAIner canister. A controller
    can install arbitrary code, so an owner could reinstall a mAIner they had sold,
    drain its cycles, and reinstall the canonical wasm afterwards. This script removes
    owners (and anything else non-canonical) from the controller set, and grants the
    owner the read-only #AdminQuery role instead so the owner-facing UI keeps working.

    Ownership itself is NOT duplicated here - GameState remains the single source of
    truth, and updateAgentSettings verifies against it.

ORDER MATTERS
    Grant #AdminQuery BEFORE removing the controller, per mAIner, so an owner is never
    left without access mid-migration.

PREREQUISITE
    The new mAIner wasm (with the updateAgentSettings ownership check) must already be
    deployed to every mAIner. Run this only after that upgrade has completed.

END STATE
    Every mAIner has exactly three controllers - mAInerCreator plus the two
    maintainer principals - no more, no less, and the owner holds #AdminQuery.

To run:
    # from the folder: funnAI
    conda activate llama_cpp_canister

    scripts/migrate_mainer_owner_access.sh --network $NETWORK [--num 10] [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

# Reuse the tested helpers rather than duplicating retry/logging/verification logic.
from . import update_admin_rbac_mainers as rbac

SCRIPT_DIR = Path(__file__).parent.resolve()

LOG_FILE_PATH = SCRIPT_DIR / "logs-admin-rbac" / "migrate_mainer_owner_access.logs"

# Must match MAINTAINER_PRINCIPAL_1 / _2 in PoAIW/src/mAInerCreator/src/Main.mo,
# which is what new mAIners are created with. Same on all networks.
MAINTAINER_PRINCIPALS = [
    "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe",  # MAINTAINER_PRINCIPAL_1
    "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae",  # MAINTAINER_PRINCIPAL_2
]

OWNER_ROLE_NOTE = "mAIner owner"


def canonical_controllers(network: str) -> set:
    """The only principals allowed to control a mAIner: mAInerCreator + the maintainers."""
    env_path = SCRIPT_DIR / f"canister_ids-{network}.env"
    if not env_path.exists():
        rbac.log_message(f"Missing {env_path}", "ERROR")
        sys.exit(1)
    env = dotenv_values(env_path)
    mainer_creator = env.get("SUBNET_0_1_MAINER_CREATOR", "").strip('"')
    if not mainer_creator:
        rbac.log_message(f"SUBNET_0_1_MAINER_CREATOR not set in {env_path}", "ERROR")
        sys.exit(1)
    return {mainer_creator, *MAINTAINER_PRINCIPALS}


def get_controllers(network: str, canister_id: str):
    """Read the current controller set from `dfx canister status`. None on failure."""
    try:
        result = rbac.run_command(
            ["dfx", "canister", "--network", network, "status", canister_id],
            retry_on_transient_errors=True, max_retries=3, retry_delay=2.0,
        )
    except subprocess.CalledProcessError:
        return None

    # dfx writes status to stderr on some versions, stdout on others.
    text = (result.stdout or "") + (result.stderr or "")
    for line in text.splitlines():
        if line.strip().startswith("Controllers:"):
            return set(line.split(":", 1)[1].split())
    rbac.log_message(f"Could not parse controllers for {canister_id}", "ERROR")
    return None


def remove_controller(network: str, canister_id: str, principal: str, dry_run: bool) -> bool:
    command = [
        "dfx", "canister", "--network", network, "update-settings",
        canister_id, "--remove-controller", principal,
    ]
    if dry_run:
        rbac.log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        rbac.run_command(command, retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)
        rbac.log_message(f"Removed controller {principal}", "SUCCESS")
        return True
    except Exception as e:
        rbac.log_message(f"Failed to remove controller {principal}: {e}", "ERROR")
        return False


def migrate_mainer(network: str, mainer: dict, canonical: set, dry_run: bool) -> bool:
    address = mainer.get("address", "")
    owner = mainer.get("ownedBy", "")

    rbac.log_message("=" * 60, "INFO")
    rbac.log_message(f"Processing mAIner: {address} (owner {owner})", "INFO")

    if not owner:
        rbac.log_message("No ownedBy recorded - skipping", "WARNING")
        rbac.update_mainer_status(address, "skipped", "no ownedBy")
        return True

    # --- Step 1: grant #AdminQuery to the owner (BEFORE touching controllers) ---
    rbac.log_message("Step 1: ensuring owner holds #AdminQuery...", "INFO")
    admin_roles = rbac.get_admin_roles(network, address)
    if admin_roles is None:
        rbac.log_message("Could not read admin roles - skipping, mAIner may run an old wasm", "WARNING")
        rbac.update_mainer_status(address, "skipped", "getAdminRoles unavailable")
        return True

    if rbac.principal_has_role(admin_roles, owner):
        rbac.log_message("Owner already holds a role - leaving as is", "INFO")
    else:
        if not rbac.assign_admin_role(network, address, owner, OWNER_ROLE_NOTE, dry_run):
            rbac.update_mainer_status(address, "failed", "could not assign #AdminQuery")
            return False
        if not dry_run:
            roles_after = rbac.get_admin_roles(network, address)
            if roles_after is None or not rbac.principal_has_role(roles_after, owner):
                rbac.log_message("Could not verify the role landed - NOT removing controller", "ERROR")
                rbac.update_mainer_status(address, "failed", "role not verified")
                return False
            rbac.log_message("Role assignment verified", "SUCCESS")

    # --- Step 2: subtract every non-canonical controller ---
    rbac.log_message("Step 2: removing non-canonical controllers...", "INFO")
    controllers = get_controllers(network, address)
    if controllers is None:
        rbac.update_mainer_status(address, "failed", "could not read controllers")
        return False

    missing = canonical - controllers
    if missing:
        # Never remove anything if a canonical controller is absent - that would risk
        # ending up with an unreachable canister.
        rbac.log_message(f"Canonical controller(s) missing: {sorted(missing)} - refusing to remove any", "ERROR")
        rbac.update_mainer_status(address, "failed", f"canonical controllers missing: {sorted(missing)}")
        return False

    to_remove = sorted(controllers - canonical)
    if not to_remove:
        rbac.log_message("Controller set already canonical", "INFO")
        rbac.update_mainer_status(address, "already_granted")
        return True

    rbac.log_message(f"Will remove {len(to_remove)} non-canonical controller(s): {to_remove}", "INFO")
    for principal in to_remove:
        if principal != owner:
            # Not fatal, but worth shouting about: a principal that is neither the
            # owner nor canonical is exactly the shadow-controller pattern.
            rbac.log_message(f"NOTE: {principal} is neither canonical nor the owner", "WARNING")
        if not remove_controller(network, address, principal, dry_run):
            rbac.update_mainer_status(address, "failed", f"could not remove {principal}")
            return False

    # --- Step 3: assert the end state ---
    if not dry_run:
        rbac.log_message("Step 3: verifying final controller set...", "INFO")
        final = get_controllers(network, address)
        if final != canonical:
            rbac.log_message(f"Final controller set is {sorted(final or [])}, expected {sorted(canonical)}", "ERROR")
            rbac.update_mainer_status(address, "failed", "final controller set not canonical")
            return False
        rbac.log_message("Controller set is canonical: exactly 3", "SUCCESS")

    rbac.update_mainer_status(address, "success")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Grant owners #AdminQuery and remove them as controllers of their mAIner."
    )
    parser.add_argument("--network", required=True,
                        choices=["local", "ic", "testing", "demo", "development", "prd"])
    parser.add_argument("--num", type=int, default=None,
                        help="Process at most this many mAIners (default: all)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Point the reused logging at this script's log file.
    rbac.LOG_FILE_PATH = LOG_FILE_PATH
    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        rbac.log_file_handle = open(LOG_FILE_PATH, "w")
    except Exception as e:
        print(f"Warning: could not open log file {LOG_FILE_PATH}: {e}")
        rbac.log_file_handle = None

    try:
        canonical = canonical_controllers(args.network)

        rbac.log_message("=" * 60, "INFO")
        rbac.log_message("Migrate mAIner owner access", "INFO")
        rbac.log_message(f"Network: {args.network}", "INFO")
        rbac.log_message(f"Canonical controllers ({len(canonical)}): {sorted(canonical)}", "INFO")
        rbac.log_message(f"Dry Run: {args.dry_run}", "INFO")
        rbac.log_message("=" * 60, "INFO")

        if args.dry_run:
            rbac.log_message("DRY-RUN MODE - NO CHANGES WILL BE MADE", "WARNING")
        else:
            rbac.log_message("LIVE RUN - owners will be removed as controllers", "WARNING")
            rbac.log_message("Confirm the new mAIner wasm is already deployed to every mAIner.", "WARNING")
            if input("Type 'yes' to continue: ").lower() != "yes":
                rbac.log_message("Migration cancelled", "INFO")
                sys.exit(0)

        mainers = [m for m in rbac.get_mainers(args.network) if m.get("address")]
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
                if not migrate_mainer(args.network, mainer, canonical, args.dry_run):
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
