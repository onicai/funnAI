"""
Audit the controllers, module hashes and admin roles of all mAIner canisters.

STRICTLY READ-ONLY
    This script makes NO update calls to any funnAI/PoAIW canister. Every call to
    GameState or a mAIner is forced with `--query`, so dfx cannot silently promote
    it to an update call. The only other calls are `dfx canister info`, which reads
    controllers and the module hash from the state tree (read_state).

    Note this is why the read helpers here are local rather than reused from
    update_admin_rbac_mainers: those omit `--query`.

WHAT IT CHECKS, per mAIner
    1. Controllers  - are exactly the canonical three present, is the owner still
                      one of them, and is there anything else (a shadow controller
                      is the pattern behind the 2026-08 marketplace incident).
    2. Module hash  - all mAIners of a type should share one hash. An outlier is
                      either un-upgraded or tampered.
    3. Admin roles  - does the owner hold #AdminQuery, and does anyone hold
                      #AdminUpdate, which must never be granted on a ctrlb canister.

VERDICTS
    PRE_MIGRATION  canonical + owner as controller, owner has no role yet
    MIGRATED       canonical only, owner holds #AdminQuery
    ANOMALY        shadow controller, missing canonical, #AdminUpdate granted,
                   or a module-hash outlier

Exits non-zero if any mAIner is an ANOMALY, so it can be used as a drift detector.

To run:
    # from the folder: funnAI
    conda activate funnAI

    scripts/audit_mainer_controllers.sh --network $NETWORK [--all] [--json out.json]
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from pathlib import Path

from dotenv import dotenv_values

# Reuse the tested logging/retry machinery. NOT the read helpers - they omit --query.
from . import update_admin_rbac_mainers as rbac

SCRIPT_DIR = Path(__file__).parent.resolve()

LOG_FILE_PATH = SCRIPT_DIR / "logs-admin-rbac" / "audit_mainer_controllers.logs"

# Each mAIner needs two calls (`dfx canister info` + a --query getAdminRoles), ~1.8s
# sequentially, i.e. ~23 minutes over 754. Both are read-only, so run them concurrently.
AUDIT_WORKERS = 8
AUDIT_PROGRESS_EVERY = 25

# Must match MAINTAINER_PRINCIPAL_1 / _2 in PoAIW/src/mAInerCreator/src/Main.mo
MAINTAINER_PRINCIPALS = [
    "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe",  # MAINTAINER_PRINCIPAL_1
    "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae",  # MAINTAINER_PRINCIPAL_2
]


def canonical_controllers(network: str) -> set:
    """mAInerCreator for this network plus the two maintainer principals."""
    env_path = SCRIPT_DIR / f"canister_ids-{network}.env"
    if not env_path.exists():
        rbac.log_message(f"Missing {env_path}", "ERROR")
        sys.exit(1)
    creator = dotenv_values(env_path).get("SUBNET_0_1_MAINER_CREATOR", "").strip('"')
    if not creator:
        rbac.log_message(f"SUBNET_0_1_MAINER_CREATOR not set in {env_path}", "ERROR")
        sys.exit(1)
    return {creator, *MAINTAINER_PRINCIPALS}


def get_mainers_readonly(network: str) -> list:
    """Enumerate mAIners from GameState. Forced query - never an update call."""
    rbac.log_message(f"Reading mAIner registry from game_state_canister on {network}...")
    try:
        result = rbac.run_command([
            "dfx", "canister", "--network", network, "call", "--query",
            "game_state_canister", "getMainerAgentCanistersAdmin", "--output", "json",
        ], retry_on_transient_errors=True, max_retries=5, retry_delay=3.0)
        mainers = json.loads(result.stdout).get("Ok", [])
        rbac.log_message(f"Found {len(mainers)} mAIner entries", "INFO")
        return mainers
    except Exception as e:
        rbac.log_message(f"Failed to read the mAIner registry: {e}", "ERROR")
        sys.exit(1)


def get_info(network: str, canister_id: str):
    """Controllers + module hash via `dfx canister info` (read_state, no update call)."""
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


def get_admin_roles_readonly(network: str, canister_id: str):
    """Admin roles on a mAIner. Forced query - never an update call."""
    try:
        result = rbac.run_command([
            "dfx", "canister", "--network", network, "call", "--query",
            canister_id, "getAdminRoles", "--output", "json",
        ], retry_on_transient_errors=True, max_retries=3, retry_delay=2.0)
        return json.loads(result.stdout).get("Ok")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "getAdminRoles" in stderr or "IC0536" in stderr:
            return None  # older wasm without the method
        rbac.log_message(f"Failed to read admin roles for {canister_id}: {e}", "WARNING")
        return None
    except Exception as e:
        rbac.log_message(f"Failed to read admin roles for {canister_id}: {e}", "WARNING")
        return None


def mainer_type(mainer: dict) -> str:
    t = mainer.get("canisterType", {}).get("MainerAgent", {})
    return list(t.keys())[0] if t else "?"


def audit_one(network: str, mainer: dict, canonical: set) -> dict:
    address = mainer.get("address", "")
    owner = mainer.get("ownedBy", "")

    controllers, module_hash = get_info(network, address)
    roles = get_admin_roles_readonly(network, address)

    findings = []
    if controllers is None:
        findings.append("could not read controllers")
        return {
            "address": address, "owner": owner, "type": mainer_type(mainer),
            "controllers": None, "module_hash": module_hash, "roles": roles,
            "verdict": "ANOMALY", "findings": findings,
        }

    missing = canonical - controllers
    owner_is_controller = bool(owner) and owner in controllers
    extra = controllers - canonical - ({owner} if owner else set())

    if missing:
        findings.append(f"missing canonical controller(s): {sorted(missing)}")
    if extra:
        findings.append(f"SHADOW controller(s): {sorted(extra)}")

    owner_role = None
    if roles:
        for r in roles:
            if r.get("principal") == owner:
                owner_role = list(r.get("role", {}).keys())[0] if isinstance(r.get("role"), dict) else r.get("role")
            role_name = list(r.get("role", {}).keys())[0] if isinstance(r.get("role"), dict) else r.get("role")
            if role_name == "AdminUpdate":
                findings.append(f"#AdminUpdate granted to {r.get('principal')} - must never be set on a ctrlb canister")

    if findings:
        verdict = "ANOMALY"
    elif owner_is_controller:
        verdict = "PRE_MIGRATION"
    elif owner_role == "AdminQuery":
        verdict = "MIGRATED"
    else:
        verdict = "ANOMALY"
        findings.append("owner is neither a controller nor holds #AdminQuery - locked out")

    return {
        "address": address, "owner": owner, "type": mainer_type(mainer),
        "controllers": sorted(controllers), "owner_is_controller": owner_is_controller,
        "module_hash": module_hash, "owner_role": owner_role,
        "roles": roles, "verdict": verdict, "findings": findings,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only audit of mAIner controllers, module hashes and admin roles."
    )
    parser.add_argument("--network", required=True,
                        choices=["local", "ic", "testing", "demo", "development", "prd"])
    parser.add_argument("--all", action="store_true",
                        help="Audit every mAIner type, not just ShareAgent")
    parser.add_argument("--num", type=int, default=None, help="Audit at most this many")
    parser.add_argument("--json", dest="json_out", default=None,
                        help="Also write the full findings to this JSON file")
    args = parser.parse_args()

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
        rbac.log_message("mAIner controller audit - READ ONLY, no update calls", "INFO")
        rbac.log_message(f"Network: {args.network}", "INFO")
        rbac.log_message(f"Canonical controllers ({len(canonical)}): {sorted(canonical)}", "INFO")
        rbac.log_message("=" * 60, "INFO")

        mainers = [m for m in get_mainers_readonly(args.network) if m.get("address")]
        if not args.all:
            mainers = [m for m in mainers if mainer_type(m) == "ShareAgent"]
        if args.num is not None:
            mainers = mainers[: args.num]

        if not mainers:
            rbac.log_message("No mAIners to audit", "WARNING")
            sys.exit(0)

        # Audit concurrently. The per-mAIner index in log_message is meaningless once
        # the order is non-deterministic, so leave it unset and report a progress bar
        # from the completion count instead.
        total = len(mainers)
        by_address, done, started = {}, 0, time.time()
        with ThreadPoolExecutor(max_workers=AUDIT_WORKERS) as pool:
            futures = {pool.submit(audit_one, args.network, m, canonical): m for m in mainers}
            for fut in as_completed(futures):
                m = futures[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    r = {"address": m.get("address", ""), "owner": m.get("owner", ""),
                         "type": mainer_type(m), "controllers": None, "module_hash": None,
                         "roles": None, "verdict": "ANOMALY",
                         "findings": [f"audit raised {e}"]}
                by_address[r["address"]] = r
                done += 1
                if done % AUDIT_PROGRESS_EVERY == 0 or done == total:
                    elapsed = time.time() - started
                    eta = (total - done) * (elapsed / done)
                    filled = int(30 * done / total)
                    rbac.log_message(
                        f"[{'#' * filled}{'-' * (30 - filled)}] {done}/{total} "
                        f"({done * 100 // total}%) ~{eta:,.0f}s left",
                        "INFO",
                    )

        # Keep registry order so the report and the JSON are stable across runs.
        results = [by_address[m["address"]] for m in mainers if m["address"] in by_address]

        # ---- module hash outliers (un-upgraded or tampered) ----
        by_hash = defaultdict(list)
        for r in results:
            if r.get("module_hash"):
                by_hash[r["module_hash"]].append(r["address"])
        if len(by_hash) > 1:
            majority = max(by_hash, key=lambda h: len(by_hash[h]))
            for h, addrs in by_hash.items():
                if h == majority:
                    continue
                for r in results:
                    if r["address"] in addrs:
                        r["findings"].append(f"module hash differs from the majority ({h} vs {majority})")
                        r["verdict"] = "ANOMALY"

        # ---- report ----
        print()
        print(f"{'mAIner':29} {'ctrls':>5} {'owner-ctrl':>10} {'owner-role':>11}  verdict")
        print("-" * 88)
        for r in results:
            print(f"{r['address']:29} {len(r['controllers'] or []):>5} "
                  f"{('yes' if r.get('owner_is_controller') else 'no'):>10} "
                  f"{(r.get('owner_role') or '-'):>11}  {r['verdict']}")
            for f in r["findings"]:
                print(f"{'':29} !! {f}")

        counts = Counter(r["verdict"] for r in results)
        print()
        rbac.log_message(f"Audited {len(results)} mAIner(s) on '{args.network}'", "INFO")
        for v in ("PRE_MIGRATION", "MIGRATED", "ANOMALY"):
            if counts.get(v):
                rbac.log_message(f"  {v}: {counts[v]}", "ERROR" if v == "ANOMALY" else "SUCCESS")
        print()
        print("Module hashes:")
        for h, addrs in sorted(by_hash.items(), key=lambda kv: -len(kv[1])):
            print(f"  {h}  x{len(addrs)}")

        if args.json_out:
            Path(args.json_out).write_text(json.dumps(
                {"network": args.network, "canonical": sorted(canonical), "results": results}, indent=2))
            rbac.log_message(f"Findings written to {args.json_out}", "INFO")

        sys.exit(1 if counts.get("ANOMALY") else 0)
    finally:
        if rbac.log_file_handle:
            rbac.log_file_handle.close()


if __name__ == "__main__":
    main()
