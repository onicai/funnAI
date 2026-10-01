"""
Re-take controllership of every mAIner ShareAgent, for a maintenance window.

WHY
    A ShareAgent's sole controller is the mAInerCreator, so the maintainers cannot stop,
    start, snapshot or status one, and the upgrade pipeline cannot run. This script is the
    way back in: it drives the mAInerCreator's addMaintainerControllersToMainerAdmin
    endpoint once per ShareAgent, which adds both maintainer principals to that agent's
    controller set.

    The inverse is scripts/remove_maintainer_controllers.py. Run this before an upgrade
    campaign and that one after it.

    Note the asymmetry: getting IN needs the mAInerCreator's help, because it is the sole
    controller. Getting OUT does not - once the maintainers are controllers they remove
    themselves with a plain `dfx canister update-settings --remove-controller --yes`.

PREREQUISITE: BE A CONTROLLER OF THE mAInerCreator
    addMaintainerControllersToMainerAdmin is isController-gated. Pre-SNS that is just the
    dev identities. Post-SNS the only controller is SNS root, so the DAO must first open a
    maintenance window with a DeregisterDappCanisters proposal that KEEPS SNS root in
    new_controllers - see "Maintenance window" in README-prd-upgrade-commands.md. Close it
    the same way when done.

PREREQUISITE, ENFORCED
    The mAInerCreator must run the build that has the endpoint, and that knows about the
    allowed_viewers log_visibility variant. Pass --creator-hash to enforce it.

NO --target-hash, DELIBERATELY
    remove_maintainer_controllers.py has one; this script does not, and that asymmetry is
    intentional. This is the recovery path. Refusing to restore access to a mAIner because
    it is on an unexpected wasm is exactly backwards - an unexpected wasm is a reason to
    want access, not to withhold it.

END STATE
    Every ShareAgent has the mAInerCreator plus both maintainer principals as controllers.

To run:
    # from the folder: funnAI
    conda activate funnAI

    CREATOR_HASH=0x...   # the mAInerCreator wasm that has the endpoint
    scripts/add_maintainer_controllers.sh --network $NETWORK --creator-hash $CREATOR_HASH [--num 10] [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

# Reuse the tested helpers rather than duplicating retry/logging/status logic.
from . import update_admin_rbac_mainers as rbac
# Same hash reader the upgrade script uses, so the comparison semantics match exactly
# (it returns `dfx canister info` output verbatim, i.e. WITH the 0x prefix).
from .upgrade_mainers import get_canister_wasm_hash

SCRIPT_DIR = Path(__file__).parent.resolve()

LOG_FILE_PATH = SCRIPT_DIR / "logs-admin-rbac" / "add_maintainer_controllers.logs"

# Must match MAINTAINER_PRINCIPAL_1 / _2 in PoAIW/src/mAInerCreator/src/Main.mo.
# The endpoint adds exactly these two; they are not passed as arguments.
MAINTAINER_PRINCIPALS = [
    "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe",  # MAINTAINER_PRINCIPAL_1
    "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae",  # MAINTAINER_PRINCIPAL_2
]


def mainer_creator(network: str) -> str:
    """The mAInerCreator canister id for this network."""
    env_path = SCRIPT_DIR / f"canister_ids-{network}.env"
    if not env_path.exists():
        rbac.log_message(f"Missing {env_path}", "ERROR")
        sys.exit(1)
    creator = dotenv_values(env_path).get("SUBNET_0_1_MAINER_CREATOR", "").strip('"')
    if not creator:
        rbac.log_message(f"SUBNET_0_1_MAINER_CREATOR not set in {env_path}", "ERROR")
        sys.exit(1)
    return creator


def get_controllers(network: str, canister_id: str):
    """
    Controllers via `dfx canister info`.

    Deliberately NOT `dfx canister status`: info is served from read_state and works for
    any caller, while status is controller-only - and the whole point of this script is
    that we are NOT yet a controller of the ShareAgent.
    """
    try:
        result = rbac.run_command(
            ["dfx", "canister", "--network", network, "info", canister_id],
            retry_on_transient_errors=True, max_retries=3, retry_delay=2.0,
        )
    except subprocess.CalledProcessError:
        return None

    text = (result.stdout or "") + (result.stderr or "")
    for line in text.splitlines():
        if line.strip().startswith("Controllers:"):
            return set(line.split(":", 1)[1].split())
    rbac.log_message(f"Could not parse controllers for {canister_id}", "ERROR")
    return None


def add_controllers(network: str, creator: str, canister_id: str, dry_run: bool) -> bool:
    """Ask the mAInerCreator to add both maintainers to this ShareAgent."""
    command = [
        "dfx", "canister", "--network", network, "call", creator,
        "addMaintainerControllersToMainerAdmin", f'(principal "{canister_id}")',
    ]
    if dry_run:
        rbac.log_message(f"DRY RUN: Would execute: {' '.join(command)}", "INFO")
        return True
    try:
        result = rbac.run_command(command, retry_on_transient_errors=True,
                                  max_retries=3, retry_delay=2.0)
        out = (result.stdout or "") + (result.stderr or "")
        if "Err" in out:
            rbac.log_message(f"Endpoint returned an error: {out.strip()}", "ERROR")
            return False
        rbac.log_message(out.strip(), "SUCCESS")
        return True
    except Exception as e:
        rbac.log_message(f"Failed to call addMaintainerControllersToMainerAdmin: {e}", "ERROR")
        return False


def process_mainer(network: str, mainer: dict, creator: str, dry_run: bool) -> bool:
    address = mainer.get("address", "")

    rbac.log_message("=" * 60, "INFO")
    rbac.log_message(f"Processing mAIner: {address}", "INFO")

    controllers = get_controllers(network, address)
    if controllers is None:
        rbac.update_mainer_status(address, "failed", "could not read controllers")
        return False

    # --- Guard: the endpoint can only work where the mAInerCreator is a controller ---
    if creator not in controllers:
        rbac.log_message(
            f"mAInerCreator {creator} is not a controller of this mAIner "
            f"(has {sorted(controllers)}) - the endpoint cannot help here",
            "ERROR")
        rbac.update_mainer_status(address, "failed", "mAInerCreator is not a controller")
        return False

    # --- Idempotence short-circuit: skip the update call entirely when already done ---
    if set(MAINTAINER_PRINCIPALS) <= controllers:
        rbac.log_message("Both maintainers are already controllers", "INFO")
        rbac.update_mainer_status(address, "already_granted")
        return True

    if not add_controllers(network, creator, address, dry_run):
        rbac.update_mainer_status(address, "failed", "could not add controllers")
        return False

    # --- Verify the end state ---
    if not dry_run:
        final = get_controllers(network, address)
        if final is None:
            rbac.update_mainer_status(address, "failed", "could not re-read controllers")
            return False
        missing = set(MAINTAINER_PRINCIPALS) - final
        if missing:
            rbac.log_message(f"Maintainers still missing after the call: {sorted(missing)}", "ERROR")
            rbac.update_mainer_status(address, "failed", "maintainers not added")
            return False
        # The union must never drop the creator - that would orphan the canister.
        if creator not in final:
            rbac.log_message(f"mAInerCreator {creator} is no longer a controller!", "ERROR")
            rbac.update_mainer_status(address, "failed", "mAInerCreator lost controllership")
            return False
        rbac.log_message("Both maintainers are controllers, mAInerCreator retained", "SUCCESS")

    rbac.update_mainer_status(address, "success")
    return True


def check_creator_wasm(network: str, creator: str, creator_hash: str) -> None:
    """Refuse to run against a mAInerCreator that does not have the endpoint."""
    current = get_canister_wasm_hash(network, creator)
    if current is None:
        rbac.log_message(f"Could not read the mAInerCreator module hash for {creator}", "ERROR")
        sys.exit(1)
    if current != creator_hash:
        rbac.log_message(
            f"mAInerCreator {creator} runs {current}, expected {creator_hash}. "
            "Deploy the build with addMaintainerControllersToMainerAdmin first.",
            "ERROR")
        sys.exit(1)
    rbac.log_message(f"mAInerCreator {creator} is on the expected wasm ({current})", "SUCCESS")


def main():
    parser = argparse.ArgumentParser(
        description="Add the maintainer principals as controllers of the mAIner "
                    "ShareAgents, via the mAInerCreator."
    )
    parser.add_argument("--network", required=True,
                        choices=["local", "ic", "testing", "demo", "development", "prd"])
    parser.add_argument("--num", type=int, default=None,
                        help="Process at most this many mAIners (default: all)")
    parser.add_argument("--mainer", default=None,
                        help="Process only this mAIner canister id. Use it to do the "
                             "first one on its own before running a batch.")
    parser.add_argument("--creator-hash", default=None,
                        help="The mAInerCreator wasm hash that has the endpoint. "
                             "WITH the 0x prefix. Required on prd.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.network == "prd" and not args.creator_hash:
        parser.error("--creator-hash is required on prd. Without it this script could run "
                     "against a mAInerCreator that does not have the endpoint.")
    if args.creator_hash and not args.creator_hash.startswith("0x"):
        parser.error(f"--creator-hash must start with 0x (got {args.creator_hash}). It is "
                     "compared verbatim against `dfx canister info` output.")

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
        rbac.log_message("Add the maintainers as controllers of the mAIner ShareAgents", "INFO")
        rbac.log_message(f"Network: {args.network}", "INFO")
        rbac.log_message(f"mAInerCreator: {creator}", "INFO")
        rbac.log_message(f"Maintainers to add: {MAINTAINER_PRINCIPALS}", "INFO")
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
            rbac.log_message("LIVE RUN - the maintainers will REGAIN controller rights on "
                             "these mAIners, and with them the ability to install code", "WARNING")
            rbac.log_message("Run scripts/remove_maintainer_controllers.sh to tighten back "
                             "down as soon as the maintenance is done.", "WARNING")
            if input("Type 'yes' to continue: ").lower() != "yes":
                rbac.log_message("Cancelled", "INFO")
                sys.exit(0)

        mainers = [m for m in rbac.get_mainers(args.network) if m.get("address")]

        # Only ShareAgents. GameState's registry also returns the ShareService, which is
        # not managed through the mAInerCreator. Matches the filter in upgrade_mainers.py.
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
                if not process_mainer(args.network, mainer, creator, args.dry_run):
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
