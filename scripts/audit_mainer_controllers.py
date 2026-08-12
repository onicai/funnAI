#!/usr/bin/env python3
"""Fleet audit of ShareAgent mAIners: controllers, module hash, and registration.

READ-ONLY. Makes no writes of any kind -- only `dfx canister info` (a public read-state
lookup, no controller rights needed) and two query calls.

Why this exists
---------------
A mAIner owner is a controller of their own canister, so they can install arbitrary wasm.
Four mAIners were tampered with and sold. This sweep answers three questions the existing
tooling cannot:

1. Which mAIners have a controller set that differs from what mAInerCreator installs?
   (`scripts/list_controllers.py` dumps raw text, serially, with no comparison.)
2. Which mAIners are running a module hash that differs from the rest of the fleet?
   The controller sweep only catches attackers who left traces; the hash sweep catches
   anyone who tampered and then tidied up.
3. Which mAIners are registered in GameState but NOT in ShareService (or vice versa)?
   `mAInerCreator.reinstallMainerctrl` ignores errors on both `setShareServiceCanisterId`
   and `addMainerShareAgentCanister`, so a mAIner can silently end up in one registry and
   not the other -- that is why the ten reverse-auction mAIners "came up inert".

Harness (threading, retry/backoff, GameState enumeration, reporting) is cloned from
`check_mAIner_status.py`, which already solved those problems at this scale.

Usage
-----
    scripts/audit_mainer_controllers.sh --network prd
    scripts/audit_mainer_controllers.sh --network prd --limit 20      # smoke test
    scripts/audit_mainer_controllers.sh --network prd --check-llms    # slower, see below
"""

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

# Deliberately no imports from the other scripts in this package.
#
# `get_mainers` pulls in `scripts.ledgers.icp`, which does `from ic.client import Client`
# (ic-py). This script needs no Python IC client at all -- every call it makes is a `dfx`
# shell-out -- so it stays dependency-free rather than dragging in ic-py. The ShareAgent
# enumeration and filtering below are the same logic as `get_mainers` /
# `check_mAIner_status.filter_share_agents`, minus that dependency.

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")

# The controller set mAInerCreator installs at creation time.
# Source of truth: PoAIW/src/mAInerCreator/src/Main.mo:679
#
# These seven are network-INDEPENDENT: they are literals in the Motoko source, so the same
# principals appear on testing and prd. The eighth controller, mAInerCreator itself, is
# `Principal.fromActor(this)` and therefore DIFFERS PER NETWORK -- it is resolved at runtime
# by resolve_mainer_creator() and must not be hardcoded here. (prd r2n3m-oqaaa-aaaaa-qanaq-cai
# vs testing 447vd-5yaaa-aaaac-qanwq-cai; hardcoding prd's flags every testing canister.)
#
# NOTE: two of these are not identified anywhere in either repo. Do not treat this list as
# a policy to enforce until they are -- see the plan, Phase 2.
# The order in Main.mo:679 is wallet/owner pairs:
#   3v5vy (patrick's wallet), fqkhp (nuno's wallet), cda4n (patrick), fsmbm (?),
#   chfec (arjaan), opcne (nuno)
EXPECTED_CONTROLLERS = {
    # Identified 2026-08-12 via `dfx canister info` + the cycles-wallet custodian rejection
    # on wallet_balance: sole controller cda4n (patrick).
    "3v5vy-2aaaa-aaaai-aapla-cai": "patrick's cycles wallet",
    # Same method: sole controller opcne (nuno).
    "fqkhp-waaaa-aaaam-qdmta-cai": "nuno's cycles wallet",
    "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe": "patrick",
    # STILL UNIDENTIFIED. Self-authenticating, so there is no canister to query; matches no
    # local dfx identity; appears nowhere in either repo, in git history on any branch, or
    # in secret/. Introduced by patnorris in PoAIW 433d745c "Add our principals as
    # controllers of mAIners for testing" (2025-06-08). Ask him before enforcing this list.
    "fsmbm-odyjn-hkwt2-3be4e-h6bg3-yi3pi-f5eny-2rosh-4u6jm-3rwa5-xae": "UNIDENTIFIED — ask patnorris",
    "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae": "arjaan",
    "opcne-svazk-6dnsy-iejci-fsm7h-miuun-ovpm4-wtsgw-5pgbz-teu3h-eqe": "nuno",
}

# Known non-required controllers seen in the wild -- reported, but classified separately
# from "unknown" so they do not drown out real findings.
KNOWN_EXTRA_CONTROLLERS = {
    "cpbhu-5iaaa-aaaad-aalta-cai": "CycleOps",
    "2daxo-giaaa-aaaap-anvca-cai": "CycleOps (alt)",
    "e3mmv-5qaaa-aaaah-aadma-cai": "blackhole",
}

VERDICT_OK = "OK"
VERDICT_TAMPERED_HASH = "HASH_MISMATCH"
VERDICT_BAD_CONTROLLERS = "CONTROLLERS_UNEXPECTED"
VERDICT_UNREACHABLE = "UNREACHABLE"
VERDICT_NO_CODE = "NO_CODE_INSTALLED"
VERDICT_SCRIPT_ERROR = "SCRIPT_ERROR"  # a bug here, NOT a canister problem


def resolve_mainer_creator(network: str, override: Optional[str]) -> Optional[str]:
    """Resolve this network's mAInerCreator principal — the 8th expected controller.

    It is `Principal.fromActor(this)` in mAInerCreator/src/Main.mo:679, so it differs per
    network. Read from scripts/canister_ids-<network>.env, which is the hand-maintained
    protocol-canister id list (NOT canister_ids_mainers-*.env, which is generated and stale).
    """
    if override:
        return override
    path = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")
    if not os.path.exists(path):
        return None
    for line in open(path):
        if line.strip().startswith("SUBNET_0_1_MAINER_CREATOR"):
            return line.split("=", 1)[1].strip().strip('"')
    return None


def log_message(msg: str, level: str = "INFO") -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def get_shareagents_from_gamestate(network: str) -> list:
    """Enumerate ShareAgents from GameState -- the only source of truth.

    NOT from scripts/canister_ids_mainers-<network>.env: that file is generated and goes
    stale (it lists 744 for prd while GameState has ~755), so auditing from it would
    silently skip mAIners.
    """
    log_message(f"Enumerating mAIners from game_state_canister on '{network}'...")
    stdout, err = run_dfx([
        "dfx", "canister", "--network", network, "call",
        "game_state_canister", "getMainerAgentCanistersAdmin", "--output", "json",
    ], timeout=180)
    if stdout is None:
        log_message(f"Could not read the GameState registry: {err}", "ERROR")
        return []
    try:
        mainers = json.loads(stdout).get("Ok", [])
    except json.JSONDecodeError as exc:
        log_message(f"Could not parse the GameState registry: {exc}", "ERROR")
        return []

    share_agents = []
    for m in mainers:
        address = m.get("address", "")
        ctype = m.get("canisterType", {}).get("MainerAgent", {})
        kind = list(ctype.keys())[0] if ctype else ""
        if kind == "ShareAgent" and address:
            share_agents.append({"address": address, "owner": m.get("ownedBy", "Unknown")})
    log_message(f"{len(share_agents)} ShareAgents (of {len(mainers)} entries in the registry)")
    return share_agents


def run_dfx(args: list, timeout: int = 60, retries: int = 3) -> tuple[Optional[str], Optional[str]]:
    """Run a dfx command with retry/backoff. Returns (stdout, error)."""
    delay = 5.0
    for attempt in range(1, retries + 1):
        try:
            out = subprocess.run(args, capture_output=True, text=True,
                                 timeout=timeout, check=True)
            return (out.stdout, None)
        except subprocess.CalledProcessError as e:
            err = (e.stderr or e.stdout or "").strip()
            if attempt == retries:
                return (None, err)
        except subprocess.TimeoutExpired:
            if attempt == retries:
                return (None, "timeout")
        import time
        time.sleep(delay)
        delay *= 2
    return (None, "unreachable")


def parse_canister_info(text: str) -> tuple[list, Optional[str]]:
    """Parse `dfx canister info` output into (controllers, module_hash).

    Output shape:
        Controllers: aaaa-aa bbbb-bb cccc-cc
        Module hash: 0xdeadbeef...
    """
    controllers: list = []
    module_hash: Optional[str] = None
    for line in text.splitlines():
        if line.startswith("Controllers:"):
            controllers = line.split(":", 1)[1].split()
        elif "Module hash:" in line:
            raw = line.split(":", 1)[1].strip()
            # dfx prints the literal "None" for a canister with no code installed.
            # Keep that distinct from a real hash so it is not reported as a mismatch.
            module_hash = None if raw in ("None", "") else raw
    return (controllers, module_hash)


def audit_one(network: str, address: str, owner: str, idx: int, total: int,
              expected: dict) -> dict:
    """Read controllers + module hash for one canister. Read-only."""
    log_message(f"[{idx}/{total}] {address}")
    stdout, err = run_dfx(["dfx", "canister", "--network", network, "info", address])
    if stdout is None:
        return {
            "address": address, "owner": owner, "controllers": [], "module_hash": None,
            "verdict": VERDICT_UNREACHABLE, "error": err,
        }

    controllers, module_hash = parse_canister_info(stdout)
    ctrl_set = set(controllers)

    # Classify the controller set. The owner is expected today (that is the vulnerability,
    # not an anomaly), so it is tracked separately rather than flagged.
    missing_required = sorted(set(expected) - ctrl_set)
    owner_is_controller = owner in ctrl_set
    extras = sorted(ctrl_set - set(expected) - {owner})
    extras_known = [c for c in extras if c in KNOWN_EXTRA_CONTROLLERS]
    extras_unknown = [c for c in extras if c not in KNOWN_EXTRA_CONTROLLERS]

    return {
        "address": address,
        "owner": owner,
        "controllers": controllers,
        "module_hash": module_hash,
        "missing_required": missing_required,
        "owner_is_controller": owner_is_controller,
        "extras_known": [f"{c} ({KNOWN_EXTRA_CONTROLLERS[c]})" for c in extras_known],
        "extras_unknown": extras_unknown,
        "error": None,
    }


def get_shareservice_registry(network: str, shareservice_id: str) -> tuple[Optional[set], Optional[str]]:
    """Read the ShareService's ShareAgent registry. Query call, read-only.

    Requires #AdminQuery (or controller) on the ShareService -- see
    PoAIW/src/mAIner/src/Main.mo:435.
    """
    stdout, err = run_dfx([
        "dfx", "canister", "--network", network, "call",
        shareservice_id, "getShareAgentRegistryWithActivityAdmin", "--output", "json",
    ], timeout=120)
    if stdout is None:
        return (None, err)
    try:
        # Shape (verified against testing):
        #   {"Ok": {"registry": [{"address": ..., ...}],
        #           "activity": [{"address": ..., "lastChallengeRequestTimestamp": ...}]}}
        # Note Ok is a DICT, not a list -- iterating it directly yields its string keys and
        # silently matches nothing, which reads as "registry is empty".
        ok = json.loads(stdout).get("Ok", {})
        if not isinstance(ok, dict):
            return (None, f"unexpected shape: Ok is {type(ok).__name__}, expected dict")
        registry = {e["address"] for e in ok.get("registry", []) if "address" in e}
        activity = {e["address"]: e.get("lastChallengeRequestTimestamp")
                    for e in ok.get("activity", []) if "address" in e}
        return ({"registry": registry, "activity": activity}, None)
    except (json.JSONDecodeError, AttributeError, TypeError) as exc:
        return (None, f"could not parse registry: {exc}")


def get_llm_canisters(network: str, address: str) -> tuple[Optional[list], Optional[str]]:
    """Read a mAIner's registered LLM canisters.

    This catches the drain that leaves NO trace in either the controller list or the module
    hash: an owner is a controller, controllers auto-hold #AdminUpdate (mAIner/src/Main.mo:361),
    so any owner can `add_llm_canister` pointing at a canister they own, and the official wasm
    will deposit cycles into it. Any LLM here that is not an official protocol LLM is a live
    drain.
    """
    stdout, err = run_dfx([
        "dfx", "canister", "--network", network, "call",
        address, "get_llm_canisters", "--output", "json",
    ])
    if stdout is None:
        return (None, err)
    try:
        return (json.loads(stdout), None)
    except json.JSONDecodeError as exc:
        return (None, str(exc))


def main(network: str, workers: int, limit: Optional[int], check_llms: bool,
         shareservice_id: Optional[str], reference_hash: Optional[str],
         mainer_creator: Optional[str]) -> None:
    log_message("=" * 80)
    log_message(f"ShareAgent controller + integrity audit  (network={network})")
    log_message("READ-ONLY: no writes are performed")
    log_message("=" * 80)

    creator = resolve_mainer_creator(network, mainer_creator)
    expected = dict(EXPECTED_CONTROLLERS)
    if creator:
        expected[creator] = f"mAInerCreator ({network})"
        log_message(f"mAInerCreator for '{network}': {creator}")
    else:
        log_message(f"Could not resolve the mAInerCreator for '{network}'. It will be "
                    f"reported as an unknown extra controller on every mAIner. Pass "
                    f"--mainer-creator <principal>.", "WARN")

    share_agents = get_shareagents_from_gamestate(network)
    if not share_agents:
        log_message(f"No ShareAgents found on '{network}'", "ERROR")
        return
    if limit:
        share_agents = share_agents[:limit]
        log_message(f"Limited to first {limit}")

    total = len(share_agents)
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(audit_one, network, a["address"], a["owner"], i + 1, total,
                        expected): a
            for i, a in enumerate(share_agents)
        }
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as exc:  # noqa: BLE001 - never lose a canister to one failure
                # Distinguish a bug in THIS script from a canister we could not reach.
                # Collapsing both into UNREACHABLE once hid a TypeError as "9 unreachable
                # canisters", which at fleet scale would read as a network problem and
                # quietly invalidate the whole report.
                a = futures[fut]
                verdict = (VERDICT_SCRIPT_ERROR
                           if isinstance(exc, (TypeError, AttributeError, KeyError, NameError))
                           else VERDICT_UNREACHABLE)
                if verdict == VERDICT_SCRIPT_ERROR:
                    log_message(f"BUG in audit script on {a['address']}: "
                                f"{type(exc).__name__}: {exc}", "ERROR")
                results.append({"address": a["address"], "owner": a["owner"],
                                "verdict": verdict,
                                "error": f"{type(exc).__name__}: {exc}",
                                "controllers": [], "module_hash": None})

    # .get(): successful results have no "verdict" yet -- it is assigned below.
    script_errors = [r for r in results if r.get("verdict") == VERDICT_SCRIPT_ERROR]
    if script_errors:
        log_message(f"ABORTING: {len(script_errors)} canister(s) failed due to a bug in "
                    f"this script, not the network. The report would be misleading.",
                    "ERROR")
        raise SystemExit(1)

    # --- module hash: compare against the reference, else the fleet majority -------------
    counts = Counter(r["module_hash"] for r in results if r.get("module_hash"))
    majority_hash, majority_n = (counts.most_common(1)[0] if counts else (None, 0))
    canonical = reference_hash or majority_hash
    if reference_hash:
        log_message(f"Comparing against supplied reference hash {reference_hash}")
    else:
        log_message(f"No --reference-hash given; using fleet majority {majority_hash} "
                    f"({majority_n}/{total}). This is a heuristic -- if tampering were "
                    f"widespread the majority would be wrong.", "WARN")

    # --- ShareService registry cross-check ----------------------------------------------
    ss_registry = None
    ss_activity = {}
    if shareservice_id:
        ss_data, ss_err = get_shareservice_registry(network, shareservice_id)
        if ss_data is None:
            log_message(f"Could not read ShareService registry: {ss_err}", "WARN")
        else:
            ss_registry = ss_data["registry"]
            ss_activity = ss_data["activity"]
            log_message(f"ShareService registry holds {len(ss_registry)} ShareAgents, "
                        f"{len(ss_activity)} with activity records")

    gamestate_addresses = {a["address"] for a in share_agents}

    for r in results:
        if r.get("verdict") == VERDICT_UNREACHABLE:
            continue
        r["in_gamestate"] = r["address"] in gamestate_addresses
        r["in_shareservice"] = (r["address"] in ss_registry) if ss_registry is not None else None
        r["last_activity"] = ss_activity.get(r["address"])
        hash_bad = (canonical is not None and r["module_hash"] is not None
                    and r["module_hash"] != canonical)
        ctrl_bad = bool(r["missing_required"]) or bool(r["extras_unknown"])
        if r["module_hash"] is None:
            r["verdict"] = VERDICT_NO_CODE
        elif hash_bad:
            r["verdict"] = VERDICT_TAMPERED_HASH
        elif ctrl_bad:
            r["verdict"] = VERDICT_BAD_CONTROLLERS
        else:
            r["verdict"] = VERDICT_OK

    if check_llms:
        log_message("Reading registered LLM canisters per mAIner (slow)...")
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(get_llm_canisters, network, r["address"]): r
                       for r in results if r.get("verdict") != VERDICT_UNREACHABLE}
            for fut in as_completed(futures):
                r = futures[fut]
                llms, err = fut.result()
                r["llm_canisters"] = llms
                r["llm_error"] = err

    # --- report --------------------------------------------------------------------------
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    base = os.path.join(REPORT_DIR, f"{stamp}-audit_mainer_controllers-{network}")

    summary = {
        "network": network,
        "generated_utc": stamp,
        "total_shareagents": total,
        "canonical_hash": canonical,
        "canonical_source": "supplied" if reference_hash else "fleet majority",
        "hash_distribution": counts.most_common(),
        "verdicts": Counter(r["verdict"] for r in results).most_common(),
    }
    with open(f"{base}.json", "w") as fh:
        json.dump({"summary": summary, "results": sorted(results, key=lambda r: r["address"])},
                  fh, indent=2)

    findings = [r for r in results if r["verdict"] != VERDICT_OK]
    with open(f"{base}.md", "w") as fh:
        fh.write(f"# ShareAgent controller + integrity audit — {network}\n\n")
        fh.write(f"Generated {stamp} UTC. **Read-only sweep; nothing was modified.**\n\n")
        fh.write(f"- ShareAgents in GameState: **{total}**\n")
        fh.write(f"- Canonical module hash: `{canonical}` ({summary['canonical_source']})\n")
        if ss_registry is not None:
            fh.write(f"- ShareService registry: **{len(ss_registry)}** entries\n")
        fh.write(f"- Findings: **{len(findings)}**\n\n")

        # ---- controllers: the point of this audit, so it leads ----------------------
        seen = [r for r in results if r.get("controllers")]
        principal_counts: Counter = Counter()
        shape_counts: Counter = Counter()
        owner_is_ctrl = 0
        for r in seen:
            for c in r["controllers"]:
                principal_counts[c] += 1
            if r.get("owner_is_controller"):
                owner_is_ctrl += 1
            # shape = the controller set with the owner factored out, so mAIners differing
            # only by which user owns them collapse into one row.
            #
            # Only strip the owner if they are NOT also an expected controller. A team
            # member who owns a mAIner is both; stripping them unconditionally made that
            # one mAIner look like it was "missing" a required controller (it was not --
            # the principal was present, just removed by this very line).
            owner_p = r.get("owner")
            strip = {owner_p} if owner_p not in expected else set()
            shape_counts[tuple(sorted(set(r["controllers"]) - strip))] += 1

        def label(p: str) -> str:
            if p == creator:
                return f"mAInerCreator ({network})"
            if p in EXPECTED_CONTROLLERS:
                return EXPECTED_CONTROLLERS[p]
            if p in KNOWN_EXTRA_CONTROLLERS:
                return KNOWN_EXTRA_CONTROLLERS[p]
            return "**UNKNOWN**"

        fh.write("## Controllers\n\n")
        fh.write(f"- mAIners inspected: **{len(seen)}**\n")
        fh.write(f"- Owner is a controller of their own mAIner: **{owner_is_ctrl}** / {len(seen)}"
                 f"  ← this is the vulnerability, expected until it is fixed at the source\n")
        fh.write(f"- Distinct controller-set shapes (owner excluded): **{len(shape_counts)}**\n\n")

        # A principal that owns some mAIner AND controls a DIFFERENT one is exactly the
        # "seller keeps control after the sale" shape. Separate those from ordinary owners.
        # Expected controllers are on EVERY mAIner by design. If a team member also happens
        # to own one, they would otherwise appear to be "controlling mAIners they do not
        # own" across the entire fleet -- 755 rows of pure noise that would bury the real
        # signal. Only a NON-expected principal doing this is suspicious.
        owners = {r.get("owner") for r in seen}
        foreign_control: dict = {}
        for r in seen:
            for c in r["controllers"]:
                if c in expected:
                    continue
                if c in owners and c != r.get("owner"):
                    foreign_control.setdefault(c, []).append(r["address"])

        fh.write("### Every controller principal seen across the fleet\n\n")
        fh.write("Owner principals controlling only their own mAIner are summarised above "
                 "rather than listed individually.\n\n")
        fh.write("| principal | who | # mAIners | expected? |\n| --- | --- | ---: | --- |\n")
        for p, n in principal_counts.most_common():
            # Hide ordinary owners (a user controlling only the mAIner they own) -- there is
            # one per mAIner and they carry no signal. But never hide an EXPECTED controller
            # just because they also happen to own one: they belong in this fleet-wide table.
            if p not in expected and p in owners and p not in foreign_control:
                continue
            exp = "yes" if (p in EXPECTED_CONTROLLERS or p == creator) else "**NO**"
            fh.write(f"| `{p}` | {label(p)} | {n} | {exp} |\n")

        if foreign_control:
            fh.write(f"\n### ⚠️ Principals controlling a mAIner they do not own "
                     f"({len(foreign_control)})\n\n")
            fh.write("This is the shape left behind when a seller keeps control after a "
                     "marketplace sale — `icrc37_transfer_from` never prunes extra controllers "
                     "the seller planted.\n\n")
            fh.write("| principal | controls (not owned) |\n| --- | --- |\n")
            for p, addrs in sorted(foreign_control.items(), key=lambda kv: -len(kv[1])):
                fh.write(f"| `{p}` | {', '.join(f'`{a}`' for a in sorted(addrs))} |\n")

        fh.write("\n### Controller-set shapes (owner excluded)\n\n")
        fh.write("| # mAIners | missing required | unexpected extras |\n| ---: | --- | --- |\n")
        for shape, n in shape_counts.most_common():
            s = set(shape)
            missing = sorted(set(expected) - s)
            extra = sorted(s - set(expected))
            fh.write(f"| {n} | "
                     f"{', '.join(f'`{m}` ({label(m)})' for m in missing) or '— none'} | "
                     f"{', '.join(f'`{e}` ({label(e)})' for e in extra) or '— none'} |\n")

        missing_any = [r for r in seen if r.get("missing_required")]
        if missing_any:
            fh.write(f"\n### mAIners missing a required controller ({len(missing_any)})\n\n")
            fh.write("A mAIner missing **mAInerCreator** cannot be reinstalled through "
                     "`reinstallMainerControllerAdmin`, and one missing every required "
                     "controller is unreachable by the team entirely.\n\n")
            fh.write("| mAIner | missing |\n| --- | --- |\n")
            for r in sorted(missing_any, key=lambda r: r["address"]):
                fh.write(f"| `{r['address']}` | "
                         f"{', '.join(f'`{m}` ({label(m)})' for m in r['missing_required'])} |\n")

        fh.write("\n## Module hash distribution\n\n| hash | count |\n| --- | ---: |\n")
        for h, n in counts.most_common():
            marker = "  ← canonical" if h == canonical else ""
            fh.write(f"| `{h}` | {n}{marker} |\n")

        fh.write("\n## Findings\n\n")
        if not findings:
            fh.write("None — every ShareAgent matches the canonical hash and the expected "
                     "controller set.\n")
        else:
            fh.write("| mAIner | owner | verdict | missing required | unknown extras | "
                     "in GS | in SS |\n| --- | --- | --- | --- | --- | --- | --- |\n")
            for r in sorted(findings, key=lambda r: r["address"]):
                fh.write(
                    f"| `{r['address']}` | `{r.get('owner','?')}` | {r['verdict']} | "
                    f"{len(r.get('missing_required') or [])} | "
                    f"{', '.join(r.get('extras_unknown') or []) or '—'} | "
                    f"{r.get('in_gamestate')} | {r.get('in_shareservice')} |\n")

        registry_gaps = [r for r in results if r.get("in_shareservice") is False]
        if registry_gaps:
            fh.write(f"\n## Registered in GameState but NOT in ShareService "
                     f"({len(registry_gaps)})\n\n")
            fh.write("These are inert: they will not be given work.\n\n")
            for r in sorted(registry_gaps, key=lambda r: r["address"]):
                fh.write(f"- `{r['address']}` (owner `{r.get('owner','?')}`)\n")

    log_message("=" * 80)
    log_message(f"{len(findings)} findings of {total} ShareAgents")
    for verdict, n in summary["verdicts"]:
        log_message(f"  {verdict}: {n}")
    log_message(f"JSON: {base}.json")
    log_message(f"MD:   {base}.md")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Read-only ShareAgent controller/integrity audit")
    p.add_argument("--network", default="local",
                   choices=["local", "ic", "testing", "demo", "development", "prd"])
    p.add_argument("--workers", type=int, default=10)
    p.add_argument("--limit", type=int, default=None, help="only the first N (smoke test)")
    p.add_argument("--check-llms", action="store_true",
                   help="also read get_llm_canisters per mAIner (catches the add_llm_canister drain)")
    p.add_argument("--shareservice", default=None,
                   help="ShareService canister id, to cross-check its ShareAgent registry")
    p.add_argument("--mainer-creator", default=None,
                   help="mAInerCreator principal for this network; default reads "
                        "scripts/canister_ids-<network>.env")
    p.add_argument("--reference-hash", default=None,
                   help="canonical module hash; omit to use the fleet majority (heuristic)")
    args = p.parse_args()
    main(args.network, args.workers, args.limit, args.check_llms,
         args.shareservice, args.reference_hash, args.mainer_creator)
