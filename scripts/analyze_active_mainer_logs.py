#!/usr/bin/env python3
"""Fetch and analyze logs for all active mAIners using status data from check_mAIner_status.

Reads the latest status JSON to identify active mAIners, fetches their logs in parallel,
and produces a health analysis report.
"""

import argparse
import os
import json
import subprocess
import glob
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Expected log patterns for a healthy mAIner flow
FLOW_STEPS = [
    "Recurring action 1 was triggered",
    "pullNextChallenge - entered",
    "pullNextChallenge - calling getChallengeFromGameStateCanister",
    "calling getRandomOpenChallenge",
]

# Patterns that indicate successful progression beyond challenge pull
SUCCESS_INDICATORS = [
    "got a challenge",
    "sendToShareService",
    "ShareService",
    "submission",
    "submitResponse",
    "Inference",
    "inference",
    "response received",
    "submitToGameState",
]

# Patterns that indicate errors
ERROR_INDICATORS = [
    "ERROR",
    "Error",
    "error",
    "trap",
    "Trap",
    "reject",
    "Reject",
    "failed",
    "Failed",
    "timeout",
    "Timeout",
]


def get_logs(canister_id, network):
    """Fetch logs for a canister with retry."""
    for attempt in range(3):
        try:
            output = subprocess.check_output(
                ["icp", "canister", "logs", canister_id, "-e", network],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=30,
            )
            return output.strip().splitlines()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            if attempt == 2:
                return None
    return None


def analyze_canister_logs(canister_id, lines):
    """Analyze log lines for a single canister and return a health assessment."""
    if lines is None:
        return {
            "canister_id": canister_id,
            "verdict": "UNREACHABLE",
            "detail": "Could not fetch logs",
            "total_lines": 0,
            "recurring_triggers": 0,
            "pull_challenge_count": 0,
            "success_indicators": [],
            "error_lines": [],
            "last_activity": "",
            "timer_interval_hours": None,
        }

    total_lines = len(lines)
    recurring_count = 0
    pull_count = 0
    success_found = []
    error_lines = []
    timestamps = []

    for line in lines:
        # Extract timestamp
        if "Z]:" in line:
            try:
                ts_start = line.index(". ") + 2
                ts_end = line.index("Z]:") + 1
                ts_str = line[ts_start:ts_end]
                timestamps.append(ts_str)
            except (ValueError, IndexError):
                pass

        if "Recurring action 1 was triggered" in line:
            recurring_count += 1

        if "pullNextChallenge - entered" in line:
            pull_count += 1

        for indicator in SUCCESS_INDICATORS:
            if indicator in line:
                # Keep unique indicators only
                if indicator not in success_found:
                    success_found.append(indicator)
                break

        for indicator in ERROR_INDICATORS:
            if indicator in line:
                # Store the actual error line (truncated)
                error_lines.append(line.strip()[-150:])
                break

    # Determine last activity timestamp
    last_activity = timestamps[-1] if timestamps else ""

    # Calculate average timer interval
    timer_interval = None
    if len(timestamps) >= 2:
        try:
            first = datetime.fromisoformat(timestamps[0].replace("Z", "+00:00"))
            last = datetime.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
            span_hours = (last - first).total_seconds() / 3600
            if recurring_count > 1:
                timer_interval = round(span_hours / (recurring_count - 1), 1)
        except (ValueError, IndexError):
            pass

    # Determine verdict
    if recurring_count == 0:
        verdict = "NO_TIMERS"
        detail = "No recurring timer triggers found in logs"
    elif success_found:
        verdict = "OK"
        detail = f"Timers firing, challenge flow progressing ({', '.join(success_found)})"
    elif pull_count > 0 and not success_found:
        verdict = "STUCK_AT_CHALLENGE_PULL"
        detail = "Timers fire, pullNextChallenge runs, but no evidence of challenge completion"
    elif recurring_count > 0 and pull_count == 0:
        verdict = "TIMER_ONLY"
        detail = "Timers fire but no pullNextChallenge steps visible (possible log buffer overflow or silent failure)"
    else:
        verdict = "UNKNOWN"
        detail = "Could not determine health from logs"

    return {
        "canister_id": canister_id,
        "verdict": verdict,
        "detail": detail,
        "total_lines": total_lines,
        "recurring_triggers": recurring_count,
        "pull_challenge_count": pull_count,
        "success_indicators": success_found,
        "error_lines": error_lines[:5],  # keep top 5
        "last_activity": last_activity,
        "timer_interval_hours": timer_interval,
    }


def load_status_data(network):
    """Load the latest check_mAIner_status JSON for the given network."""
    logs_dir = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")
    pattern = os.path.join(logs_dir, f"*-check_mAIner_status-{network}.json")
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    # Use the latest file
    with open(files[-1]) as f:
        return json.load(f)


def write_markdown_report(analysis_results, network, md_path):
    """Write analysis report as markdown."""
    lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"# Active mAIner Log Analysis — {network} — {timestamp}")
    lines.append("")

    # Group by verdict
    by_verdict = defaultdict(list)
    for r in analysis_results:
        by_verdict[r["verdict"]].append(r)

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Verdict                 | Count |")
    lines.append("|-------------------------|-------|")
    for verdict in ["OK", "STUCK_AT_CHALLENGE_PULL", "TIMER_ONLY", "NO_TIMERS", "UNREACHABLE", "UNKNOWN"]:
        count = len(by_verdict.get(verdict, []))
        if count > 0 or verdict in ["OK", "STUCK_AT_CHALLENGE_PULL", "TIMER_ONLY"]:
            lines.append(f"| {verdict:<23} | {count:>5} |")
    lines.append(f"| **Total**               | **{len(analysis_results):>3}** |")
    lines.append("")

    # Verdict explanations
    lines.append("### Verdict Legend")
    lines.append("")
    lines.append("- **OK**: Timers firing and evidence of challenge processing beyond `getRandomOpenChallenge`")
    lines.append("- **STUCK_AT_CHALLENGE_PULL**: Timers fire, `pullNextChallenge` runs, but no evidence of receiving a challenge or completing inference")
    lines.append("- **TIMER_ONLY**: Timers fire but `pullNextChallenge` steps not visible in log buffer (may be log overflow)")
    lines.append("- **NO_TIMERS**: No recurring timer triggers found")
    lines.append("- **UNREACHABLE**: Could not fetch logs from canister")
    lines.append("")

    # Detail table
    cid_width = 27
    verdict_width = 23
    lines.append("## All Active mAIners")
    lines.append("")
    lines.append(f"| {'#':<4} | {'Canister ID':<{cid_width}} | {'Burn Rate':<9} | {'Verdict':<{verdict_width}} | {'Triggers':<8} | {'Pulls':<5} | {'Interval':<8} | {'Days Left':<9} | {'Last Activity':<25} |")
    lines.append(f"|{'-'*6}|{'-'*(cid_width+2)}|{'-'*11}|{'-'*(verdict_width+2)}|{'-'*10}|{'-'*7}|{'-'*10}|{'-'*11}|{'-'*27}|")

    # Sort: problems first, then by days_until_freeze ascending
    verdict_order = {"UNREACHABLE": 0, "NO_TIMERS": 1, "STUCK_AT_CHALLENGE_PULL": 2, "TIMER_ONLY": 3, "UNKNOWN": 4, "OK": 5}
    sorted_results = sorted(analysis_results, key=lambda r: (verdict_order.get(r["verdict"], 99), r.get("days_until_freeze") if r.get("days_until_freeze") is not None else 9999))

    for idx, r in enumerate(sorted_results, 1):
        interval = f"{r['timer_interval_hours']}h" if r["timer_interval_hours"] else ""
        days_left = f"{r['days_until_freeze']:.1f}" if r.get("days_until_freeze") is not None else ""
        lines.append(
            f"| {idx:<4} "
            f"| {r['canister_id']:<{cid_width}} "
            f"| {r.get('burn_rate', ''):<9} "
            f"| {r['verdict']:<{verdict_width}} "
            f"| {r['recurring_triggers']:<8} "
            f"| {r['pull_challenge_count']:<5} "
            f"| {interval:<8} "
            f"| {days_left:>9} "
            f"| {r['last_activity']:<25} |"
        )
    lines.append("")

    # Problem canisters detail
    problems = [r for r in sorted_results if r["verdict"] != "OK"]
    if problems:
        lines.append("## Problem mAIners — Details")
        lines.append("")
        for r in problems:
            lines.append(f"### `{r['canister_id']}` — {r['verdict']}")
            lines.append("")
            lines.append(f"- **Detail**: {r['detail']}")
            lines.append(f"- **Log lines**: {r['total_lines']}, Triggers: {r['recurring_triggers']}, Pulls: {r['pull_challenge_count']}")
            if r["error_lines"]:
                lines.append(f"- **Errors found**:")
                for err in r["error_lines"]:
                    lines.append(f"  - `{err}`")
            lines.append("")

    # OK canisters with success indicators
    ok_results = by_verdict.get("OK", [])
    if ok_results:
        lines.append("## OK mAIners — Success Indicators")
        lines.append("")
        for r in ok_results:
            indicators = ", ".join(r["success_indicators"]) if r["success_indicators"] else "none"
            lines.append(f"- `{r['canister_id']}`: {indicators}")
        lines.append("")

    with open(md_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main(network, workers=10):
    # Step 1: Load status data
    status_data = load_status_data(network)
    if not status_data:
        print(f"ERROR: No check_mAIner_status JSON found for network '{network}'.")
        print(f"Run check_mAIner_status.sh --network {network} first.")
        return

    print(f"Loaded status data from {status_data['timestamp']} ({status_data['summary']['total_share_agents']} total mAIners)")

    # Step 2: Extract active mAIners with burn rates and freeze prediction
    active_mainers = []
    for m in status_data["mainers"]:
        if m.get("active") is True and m.get("burn_rate", ""):
            active_mainers.append({
                "canister_id": m["canister_id"],
                "burn_rate": m["burn_rate"],
                "days_until_freeze": m.get("days_until_freeze"),
            })

    if not active_mainers:
        print("No active mAIners found in status data.")
        return

    print(f"Found {len(active_mainers)} active mAIners to analyze.")

    # Step 3: Fetch logs in parallel
    print(f"Fetching logs with {workers} parallel workers...")
    logs_map = {}  # canister_id -> lines

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {
            executor.submit(get_logs, m["canister_id"], network): m["canister_id"]
            for m in active_mainers
        }
        done = 0
        for future in as_completed(future_to_id):
            done += 1
            cid = future_to_id[future]
            try:
                logs_map[cid] = future.result()
            except Exception:
                logs_map[cid] = None
            if done % 25 == 0:
                print(f"  Fetched {done}/{len(active_mainers)} logs...")

    print(f"  Fetched all {len(active_mainers)} logs.")

    # Step 4: Analyze each canister
    print("Analyzing logs...")
    analysis_results = []
    for m in active_mainers:
        cid = m["canister_id"]
        result = analyze_canister_logs(cid, logs_map.get(cid))
        result["burn_rate"] = m["burn_rate"]
        result["days_until_freeze"] = m.get("days_until_freeze")
        analysis_results.append(result)

    # Step 5: Print summary
    by_verdict = defaultdict(int)
    for r in analysis_results:
        by_verdict[r["verdict"]] += 1

    print(f"\n{'='*60}")
    print("LOG ANALYSIS SUMMARY")
    print(f"{'='*60}")
    for verdict in ["OK", "STUCK_AT_CHALLENGE_PULL", "TIMER_ONLY", "NO_TIMERS", "UNREACHABLE", "UNKNOWN"]:
        count = by_verdict.get(verdict, 0)
        if count > 0:
            print(f"  {verdict:<25}: {count}")
    print(f"  {'Total':<25}: {len(analysis_results)}")
    print()

    # Step 6: Write output files
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    logs_dir = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")
    os.makedirs(logs_dir, exist_ok=True)

    json_path = os.path.join(logs_dir, f"{date_prefix}-analyze_active_mainer_logs-{network}.json")
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "network": network,
            "total_active": len(active_mainers),
            "summary": dict(by_verdict),
            "results": analysis_results,
        }, f, indent=2)
    print(f"JSON report: {os.path.abspath(json_path)}")

    md_path = os.path.join(logs_dir, f"{date_prefix}-analyze_active_mainer_logs-{network}.md")
    write_markdown_report(analysis_results, network, md_path)
    print(f"Markdown report: {os.path.abspath(md_path)}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and analyze logs for all active mAIners."
    )
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
        help="Number of parallel workers for log fetching (default: 10)",
    )
    args = parser.parse_args()
    main(args.network, args.workers)
