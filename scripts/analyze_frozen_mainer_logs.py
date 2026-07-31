#!/usr/bin/env python3
"""Fetch and analyze logs for all frozen mAIners to determine why they froze.

Reads the latest status JSON to identify frozen mAIners, fetches their logs
(dfx canister logs works on frozen canisters), and analyzes for freeze causes.
"""

import argparse
import os
import json
import subprocess
import glob
import re
from datetime import datetime, timezone
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Patterns to detect in logs
TIMER_TRIGGER = "Recurring action 1 was triggered"
TIMER_2_TRIGGER = "Recurring action 2 was triggered"
PULL_CHALLENGE = "pullNextChallenge - entered"
GOT_CHALLENGE = "pullNextChallenge - challenge ="
SEND_TO_SHARE = "addChallengeToShareServiceQueue"
STORE_RESPONSE = "storeAndSubmitResponse"
SUBMIT_TO_GS = "submitChallengeResponse"
TIMER_START = "startTimerExecution"
TIMER_SET = "setTimer"
CYCLES_ADD = "Cycles.add for"
UNOFFICIAL_TOPUP = "Unofficial top ups"

# Error patterns
ERROR_PATTERNS = [
    "trap", "Trap", "ERROR", "Error", "reject", "Reject",
    "failed", "Failed", "timeout", "Timeout", "out of cycles",
    "canister_error", "IC0503", "IC0502",
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


def parse_timestamp(line):
    """Extract timestamp from a log line like '[123. 2026-03-22T23:47:22.895Z]: ...'"""
    match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', line)
    if match:
        ts_str = match.group(1)
        # Truncate nanoseconds to microseconds for parsing
        ts_str = re.sub(r'(\.\d{6})\d*Z', r'\1Z', ts_str)
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except ValueError:
            pass
    return None


def calculate_timer_intervals(timestamps):
    """Calculate timer intervals from a list of timestamps.

    Returns list of intervals in seconds.
    """
    if len(timestamps) < 2:
        return []
    intervals = []
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if delta > 0:
            intervals.append(delta)
    return intervals


def analyze_canister_logs(canister_id, lines):
    """Analyze log lines for a frozen canister and determine freeze cause."""
    if lines is None:
        return {
            "canister_id": canister_id,
            "freeze_cause": "UNREACHABLE",
            "detail": "Could not fetch logs",
            "total_lines": 0,
        }

    total_lines = len(lines)

    # Counters
    timer1_count = 0
    timer2_count = 0
    pull_count = 0
    got_challenge_count = 0
    send_share_count = 0
    store_response_count = 0
    submit_gs_count = 0
    timer_start_count = 0
    cycles_add_count = 0
    unofficial_topup_count = 0
    error_lines = []

    # Timestamps for timer interval analysis
    timer1_timestamps = []
    timer2_timestamps = []
    all_timestamps = []

    # First and last activity
    first_ts = None
    last_ts = None

    for line in lines:
        ts = parse_timestamp(line)
        if ts:
            all_timestamps.append(ts)
            if first_ts is None:
                first_ts = ts
            last_ts = ts

        if TIMER_TRIGGER in line:
            timer1_count += 1
            if ts:
                timer1_timestamps.append(ts)
        if TIMER_2_TRIGGER in line:
            timer2_count += 1
            if ts:
                timer2_timestamps.append(ts)
        if PULL_CHALLENGE in line:
            pull_count += 1
        if GOT_CHALLENGE in line:
            got_challenge_count += 1
        if SEND_TO_SHARE in line:
            send_share_count += 1
        if STORE_RESPONSE in line:
            store_response_count += 1
        if SUBMIT_TO_GS in line:
            submit_gs_count += 1
        if TIMER_START in line:
            timer_start_count += 1
        if CYCLES_ADD in line:
            cycles_add_count += 1
        if UNOFFICIAL_TOPUP in line:
            unofficial_topup_count += 1

        for pattern in ERROR_PATTERNS:
            if pattern in line and "storeAndSubmitResponse" not in line:
                error_lines.append(line.strip()[-200:])
                break

    # Calculate timer intervals
    timer1_intervals = calculate_timer_intervals(timer1_timestamps)
    timer2_intervals = calculate_timer_intervals(timer2_timestamps)

    avg_timer1_interval_h = None
    min_timer1_interval_s = None
    if timer1_intervals:
        avg_timer1_interval_h = round(sum(timer1_intervals) / len(timer1_intervals) / 3600, 2)
        min_timer1_interval_s = round(min(timer1_intervals), 1)

    avg_timer2_interval_s = None
    if timer2_intervals:
        avg_timer2_interval_s = round(sum(timer2_intervals) / len(timer2_intervals), 1)

    # Log span
    log_span_days = None
    if first_ts and last_ts:
        log_span_days = round((last_ts - first_ts).total_seconds() / 86400, 1)

    # Determine freeze cause
    freeze_cause = "UNKNOWN"
    detail = ""

    if timer2_count > 0 and avg_timer2_interval_s and avg_timer2_interval_s < 30:
        freeze_cause = "RUNAWAY_TIMER_2"
        detail = f"Timer 2 fired {timer2_count} times at ~{avg_timer2_interval_s}s interval (should not run for ShareAgent)"
    elif min_timer1_interval_s is not None and min_timer1_interval_s < 60:
        freeze_cause = "RUNAWAY_TIMER_1"
        detail = f"Timer 1 min interval was {min_timer1_interval_s}s (expected hours). Possible 5-second fallback or orphaned timers"
    elif timer1_count > 0 and got_challenge_count > 0 and store_response_count > 0:
        freeze_cause = "NORMAL_OPERATION"
        detail = f"Processed {got_challenge_count} challenges, {store_response_count} submissions. Memory growth from stored responses likely caused freeze"
    elif timer1_count > 0 and pull_count > 0 and got_challenge_count == 0:
        freeze_cause = "IDLE_WITH_TIMERS"
        detail = f"Timers firing ({timer1_count}x) and pulling challenges ({pull_count}x) but no challenges received. Idle cycle burn from timers + memory"
    elif timer1_count > 0 and pull_count == 0:
        freeze_cause = "TIMER_ONLY_NO_WORK"
        detail = f"Timers firing ({timer1_count}x) but no challenge processing visible in logs. Possible log overflow or silent failure"
    elif timer1_count == 0 and total_lines > 0:
        freeze_cause = "NO_TIMERS_IN_LOG"
        detail = f"No timer triggers found in {total_lines} log lines. Logs may predate timer start or timers never started"
    elif total_lines == 0:
        freeze_cause = "NO_LOGS"
        detail = "No log entries found"

    if error_lines:
        detail += f". {len(error_lines)} error(s) found"

    return {
        "canister_id": canister_id,
        "freeze_cause": freeze_cause,
        "detail": detail,
        "total_lines": total_lines,
        "log_span_days": log_span_days,
        "first_activity": first_ts.isoformat() if first_ts else "",
        "last_activity": last_ts.isoformat() if last_ts else "",
        "timer1_count": timer1_count,
        "timer2_count": timer2_count,
        "avg_timer1_interval_h": avg_timer1_interval_h,
        "min_timer1_interval_s": min_timer1_interval_s,
        "avg_timer2_interval_s": avg_timer2_interval_s,
        "pull_count": pull_count,
        "got_challenge_count": got_challenge_count,
        "send_share_count": send_share_count,
        "store_response_count": store_response_count,
        "submit_gs_count": submit_gs_count,
        "timer_start_count": timer_start_count,
        "cycles_add_count": cycles_add_count,
        "unofficial_topup_count": unofficial_topup_count,
        "error_count": len(error_lines),
        "error_samples": error_lines[:5],
    }


def load_status_data(network):
    """Load the latest check_mAIner_status JSON for the given network."""
    logs_dir = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")
    pattern = os.path.join(logs_dir, f"*-check_mAIner_status-{network}.json")
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)


def write_markdown_report(analysis_results, network, md_path):
    """Write analysis report as markdown."""
    lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"# Frozen mAIner Log Analysis — {network} — {timestamp}")
    lines.append("")

    # Group by freeze cause
    by_cause = defaultdict(list)
    for r in analysis_results:
        by_cause[r["freeze_cause"]].append(r)

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Freeze Cause           | Count |")
    lines.append("|------------------------|-------|")
    cause_order = [
        "RUNAWAY_TIMER_2", "RUNAWAY_TIMER_1", "NORMAL_OPERATION",
        "IDLE_WITH_TIMERS", "TIMER_ONLY_NO_WORK", "NO_TIMERS_IN_LOG",
        "NO_LOGS", "UNREACHABLE", "UNKNOWN",
    ]
    for cause in cause_order:
        count = len(by_cause.get(cause, []))
        if count > 0:
            lines.append(f"| {cause:<22} | {count:>5} |")
    lines.append(f"| **Total**              | **{len(analysis_results):>3}** |")
    lines.append("")

    # Legend
    lines.append("### Freeze Cause Legend")
    lines.append("")
    lines.append("- **RUNAWAY_TIMER_2**: Timer 2 firing at ~5s interval (should not run for ShareAgent) — rapid cycle drain")
    lines.append("- **RUNAWAY_TIMER_1**: Timer 1 firing at sub-minute intervals instead of hours — possible 5s fallback")
    lines.append("- **NORMAL_OPERATION**: Was processing challenges normally — froze from memory growth + idle cost")
    lines.append("- **IDLE_WITH_TIMERS**: Timers firing, pulling challenges, but no challenges received — idle cycle burn")
    lines.append("- **TIMER_ONLY_NO_WORK**: Timers firing but no challenge steps visible (log buffer overflow)")
    lines.append("- **NO_TIMERS_IN_LOG**: No timer triggers in log — timers may have never started")
    lines.append("- **NO_LOGS**: No log entries at all")
    lines.append("- **UNREACHABLE**: Could not fetch logs")
    lines.append("")

    # Detail table
    cid_width = 27
    cause_width = 22
    lines.append("## All Frozen mAIners")
    lines.append("")
    lines.append(
        f"| {'#':<4} "
        f"| {'Canister ID':<{cid_width}} "
        f"| {'Freeze Cause':<{cause_width}} "
        f"| {'T1':>4} "
        f"| {'T2':>4} "
        f"| {'T1 Avg':>7} "
        f"| {'T1 Min':>7} "
        f"| {'Pulls':>5} "
        f"| {'Got':>4} "
        f"| {'Submit':>6} "
        f"| {'Errs':>4} "
        f"| {'Span':>6} "
        f"| {'Last Activity':<25} |"
    )
    lines.append(
        f"|{'-' * 6}"
        f"|{'-' * (cid_width + 2)}"
        f"|{'-' * (cause_width + 2)}"
        f"|{'-' * 6}"
        f"|{'-' * 6}"
        f"|{'-' * 9}"
        f"|{'-' * 9}"
        f"|{'-' * 7}"
        f"|{'-' * 6}"
        f"|{'-' * 8}"
        f"|{'-' * 6}"
        f"|{'-' * 8}"
        f"|{'-' * 27}|"
    )

    # Sort by cause (runaway first)
    cause_sort = {c: i for i, c in enumerate(cause_order)}
    sorted_results = sorted(analysis_results, key=lambda r: cause_sort.get(r["freeze_cause"], 99))

    for idx, r in enumerate(sorted_results, 1):
        t1_avg = f"{r['avg_timer1_interval_h']}h" if r["avg_timer1_interval_h"] else ""
        t1_min = f"{r['min_timer1_interval_s']}s" if r["min_timer1_interval_s"] else ""
        span = f"{r['log_span_days']}d" if r["log_span_days"] else ""
        last = r.get("last_activity", "")[:25]
        lines.append(
            f"| {idx:<4} "
            f"| {r['canister_id']:<{cid_width}} "
            f"| {r['freeze_cause']:<{cause_width}} "
            f"| {r['timer1_count']:>4} "
            f"| {r['timer2_count']:>4} "
            f"| {t1_avg:>7} "
            f"| {t1_min:>7} "
            f"| {r['pull_count']:>5} "
            f"| {r['got_challenge_count']:>4} "
            f"| {r['submit_gs_count']:>6} "
            f"| {r['error_count']:>4} "
            f"| {span:>6} "
            f"| {last:<25} |"
        )
    lines.append("")

    # Detailed sections per cause
    for cause in cause_order:
        group = by_cause.get(cause, [])
        if not group:
            continue
        lines.append(f"## {cause} ({len(group)} mAIners)")
        lines.append("")
        for r in group:
            lines.append(f"### `{r['canister_id']}`")
            lines.append("")
            lines.append(f"- **Detail**: {r['detail']}")
            lines.append(f"- **Log span**: {r['log_span_days']}d, {r['total_lines']} lines")
            lines.append(f"- **Last activity**: {r.get('last_activity', 'N/A')}")
            lines.append(f"- **Timer 1**: {r['timer1_count']}x, avg {r['avg_timer1_interval_h']}h, min {r['min_timer1_interval_s']}s")
            if r["timer2_count"] > 0:
                lines.append(f"- **Timer 2**: {r['timer2_count']}x, avg {r['avg_timer2_interval_s']}s")
            lines.append(f"- **Flow**: pulls={r['pull_count']}, got={r['got_challenge_count']}, share={r['send_share_count']}, submit={r['submit_gs_count']}")
            if r["error_samples"]:
                lines.append(f"- **Errors**:")
                for err in r["error_samples"]:
                    lines.append(f"  - `{err}`")
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

    # Step 2: Extract frozen mAIners
    frozen_mainers = [m["canister_id"] for m in status_data["mainers"] if m["status"] == "Frozen"]

    if not frozen_mainers:
        print("No frozen mAIners found in status data.")
        return

    print(f"Found {len(frozen_mainers)} frozen mAIners to analyze.")

    # Step 3: Fetch logs in parallel
    print(f"Fetching logs with {workers} parallel workers...")
    logs_map = {}

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_id = {
            executor.submit(get_logs, cid, network): cid
            for cid in frozen_mainers
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
                print(f"  Fetched {done}/{len(frozen_mainers)} logs...")

    print(f"  Fetched all {len(frozen_mainers)} logs.")

    # Step 4: Analyze each canister
    print("Analyzing logs...")
    analysis_results = []
    for cid in frozen_mainers:
        result = analyze_canister_logs(cid, logs_map.get(cid))
        analysis_results.append(result)

    # Step 5: Print summary
    by_cause = defaultdict(int)
    for r in analysis_results:
        by_cause[r["freeze_cause"]] += 1

    print(f"\n{'='*60}")
    print("FROZEN MAINER LOG ANALYSIS SUMMARY")
    print(f"{'='*60}")
    for cause in ["RUNAWAY_TIMER_2", "RUNAWAY_TIMER_1", "NORMAL_OPERATION",
                   "IDLE_WITH_TIMERS", "TIMER_ONLY_NO_WORK", "NO_TIMERS_IN_LOG",
                   "NO_LOGS", "UNREACHABLE", "UNKNOWN"]:
        count = by_cause.get(cause, 0)
        if count > 0:
            print(f"  {cause:<25}: {count}")
    print(f"  {'Total':<25}: {len(analysis_results)}")
    print()

    # Step 6: Write output files
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    logs_dir = os.path.join(SCRIPT_DIR, "logs-mainer-analysis")
    os.makedirs(logs_dir, exist_ok=True)

    json_path = os.path.join(logs_dir, f"{date_prefix}-analyze_frozen_mainer_logs-{network}.json")
    with open(json_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "network": network,
            "total_frozen": len(frozen_mainers),
            "summary": dict(by_cause),
            "results": analysis_results,
        }, f, indent=2)
    print(f"JSON report: {os.path.abspath(json_path)}")

    md_path = os.path.join(logs_dir, f"{date_prefix}-analyze_frozen_mainer_logs-{network}.md")
    write_markdown_report(analysis_results, network, md_path)
    print(f"Markdown report: {os.path.abspath(md_path)}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and analyze logs for all frozen mAIners to determine freeze cause."
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
