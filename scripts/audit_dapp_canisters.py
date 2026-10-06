"""
Read-only pre-SNS audit of the protocol canisters in canister_ids-{network}.env.

On prd these are exactly the 21 `dapp_canisters` of onicai_sns_init.yaml. Per canister:
    NNS_ROOT     NNS Root is a controller (required before the NNS proposal is adopted)
    CYCLES       balance is at least --min-cycles (covers the ~1 month vote + swap)
    LOG_VIEWERS  log_visibility is allowed_viewers and lists both maintainers

Makes no update calls. `dfx canister status` is controller-only, so run it as a
maintainer identity while the team still controls the canisters.

Exits non-zero if any check fails.

To run:
    # from the folder: funnAI
    scripts/audit_dapp_canisters.sh --network prd
"""

import argparse
import subprocess
import sys

from .monitor_common import get_canisters, MAINTAINER_PRINCIPALS

NNS_ROOT = "r7inp-6aaaa-aaaaa-aaabq-cai"


def dfx_lines(network, *args):
    result = subprocess.run(["dfx", "canister", "--network", network, *args],
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return [line.strip() for line in (result.stdout + result.stderr).splitlines()]


def field(lines, prefix):
    for line in lines or []:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def audit(network, canister_id, min_cycles):
    controllers = field(dfx_lines(network, "info", canister_id), "Controllers:")
    status = dfx_lines(network, "status", canister_id)
    balance = field(status, "Balance:")
    visibility = field(status, "Log visibility:")

    balance = int(balance.split()[0].replace("_", "")) if balance else None
    viewers = set()
    if visibility and visibility.startswith("allowed viewers:"):
        viewers = {v.strip() for v in visibility.split(":", 1)[1].split(",") if v.strip()}

    return {
        "NNS_ROOT": controllers is not None and NNS_ROOT in controllers.split(),
        "CYCLES": balance is not None and balance >= min_cycles,
        "LOG_VIEWERS": set(MAINTAINER_PRINCIPALS) <= viewers,
        "balance": balance,
        "visibility": visibility,
        "extra_viewers": sorted(viewers - set(MAINTAINER_PRINCIPALS)),
    }


def main():
    parser = argparse.ArgumentParser(description="Read-only pre-SNS audit of the protocol canisters.")
    parser.add_argument("--network", required=True,
                        choices=["local", "ic", "testing", "demo", "development", "prd"])
    parser.add_argument("--min-cycles", type=int, default=5_000_000_000_000,
                        help="Minimum cycles balance (default: 5T)")
    args = parser.parse_args()

    canisters, _, _ = get_canisters(args.network, "protocol")
    checks = ["NNS_ROOT", "CYCLES", "LOG_VIEWERS"]
    width = max(len(name) for name in canisters)

    failures = 0
    print(f"\n{'canister':{width}}  {'id':27}  " + "  ".join(f"{c:11}" for c in checks) + "  balance")
    for name, canister_id in canisters.items():
        r = audit(args.network, canister_id, args.min_cycles)
        failures += sum(not r[c] for c in checks)
        marks = "  ".join(f"{'ok' if r[c] else 'FAIL':11}" for c in checks)
        balance = f"{r['balance'] / 1e12:.2f}T" if r["balance"] is not None else "unreadable"
        print(f"{name:{width}}  {canister_id:27}  {marks}  {balance}")
        if not r["LOG_VIEWERS"]:
            print(f"{'':{width}}    log visibility: {r['visibility']}")
        if r["extra_viewers"]:
            print(f"{'':{width}}    extra log viewers: {', '.join(r['extra_viewers'])}")

    print(f"\n{len(canisters)} canisters, {failures} failed check(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
