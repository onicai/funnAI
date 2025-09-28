#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))


def get_canister_id_from_env(env_key: str, network: str) -> str:
    """Get canister ID from canister_ids env file."""
    if network == "ic":
        env_file = Path(FUNNAI_DIR) / "scripts" / "canister_ids-prd.env"
    else:
        env_file = Path(FUNNAI_DIR) / "scripts" / f"canister_ids-{network}.env"

    if not env_file.exists():
        raise ValueError(f"Could not find {env_file}")

    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith(f'{env_key}='):
                return line.split('=')[1].strip().strip('"')

    raise ValueError(f"Could not find {env_key} in {env_file}")


def run_dfx_call(canister_id: str, method: str, network: str) -> Any:
    """Run a dfx canister call and return the parsed JSON response."""
    cmd = [
        "dfx", "canister", "call",
        "--network", network,
        "--output", "json",
        canister_id,
        method
    ]

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_json = json.loads(result.stdout)
        return response_json.get('Ok', [])
    except subprocess.CalledProcessError as e:
        print(f"Error running dfx command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        raise


def get_recent_protocol_activity(network: str) -> List[Dict]:
    """Get recent protocol activity from GameState canister (same as frontend uses)."""
    gamestate_id = get_canister_id_from_env("SUBNET_0_1_GAMESTATE", network)
    activity_data = run_dfx_call(gamestate_id, "getRecentProtocolActivity", network)

    # Extract winners from the protocol activity response
    if isinstance(activity_data, dict) and 'winners' in activity_data:
        return activity_data['winners']
    return activity_data if isinstance(activity_data, list) else []


def get_archived_winners(network: str) -> List[Dict]:
    """Get historical winner declarations from Archive canister."""
    archive_id = get_canister_id_from_env("SUBNET_0_2_ARCHIVE", network)
    return run_dfx_call(archive_id, "getWinnerDeclarationsAdmin", network)


def is_within_date_range(timestamp: int, days: int = 3) -> bool:
    """Frontend-style date filtering - only last N days (default 3)."""
    now = datetime.now().timestamp() * 1000  # Convert to milliseconds
    item_time = timestamp / 1000000  # Convert from nanoseconds to milliseconds
    days_diff = (now - item_time) / (24 * 60 * 60 * 1000)
    return days_diff <= days and days_diff >= 0


def analyze_canister_wins(target_canister: str, recent_winners: List[Dict], archived_winners: List[Dict]) -> Dict:
    """Analyze how many times the target canister won each position."""

    stats = {
        "target_canister": target_canister,
        "first_place_wins": 0,
        "second_place_wins": 0,
        "third_place_wins": 0,
        "total_wins": 0,
        "challenges_analyzed": 0,
        "first_place_wins_last_3_days": 0,
        "second_place_wins_last_3_days": 0,
        "third_place_wins_last_3_days": 0,
        "total_wins_last_3_days": 0,
        "challenges_analyzed_last_3_days": 0,
        "win_details": {
            "first_place": [],
            "second_place": [],
            "third_place": []
        }
    }

    all_winners = recent_winners + archived_winners
    stats["challenges_analyzed"] = len(all_winners)

    # Filter for 3-day analysis (frontend behavior)
    recent_winners_3_days = [w for w in all_winners if is_within_date_range(int(w.get("finalizedTimestamp", 0)), 3)]
    stats["challenges_analyzed_last_3_days"] = len(recent_winners_3_days)

    for winner_declaration in all_winners:
        challenge_id = winner_declaration.get("challengeId", "unknown")
        timestamp = winner_declaration.get("finalizedTimestamp", 0)
        is_within_3_days = is_within_date_range(int(timestamp), 3)

        # Check first place (winner)
        first_place = winner_declaration.get("winner", {})
        if first_place.get("submittedBy") == target_canister:
            stats["first_place_wins"] += 1
            stats["total_wins"] += 1
            if is_within_3_days:
                stats["first_place_wins_last_3_days"] += 1
                stats["total_wins_last_3_days"] += 1

            reward_amount = first_place.get("reward", {}).get("amount", "0")
            stats["win_details"]["first_place"].append({
                "challengeId": challenge_id,
                "timestamp": timestamp,
                "reward_amount": reward_amount,
                "submissionId": first_place.get("submissionId", ""),
                "within_3_days": is_within_3_days
            })

        # Check second place
        second_place = winner_declaration.get("secondPlace", {})
        if second_place.get("submittedBy") == target_canister:
            stats["second_place_wins"] += 1
            stats["total_wins"] += 1
            if is_within_3_days:
                stats["second_place_wins_last_3_days"] += 1
                stats["total_wins_last_3_days"] += 1

            reward_amount = second_place.get("reward", {}).get("amount", "0")
            stats["win_details"]["second_place"].append({
                "challengeId": challenge_id,
                "timestamp": timestamp,
                "reward_amount": reward_amount,
                "submissionId": second_place.get("submissionId", ""),
                "within_3_days": is_within_3_days
            })

        # Check third place
        third_place = winner_declaration.get("thirdPlace", {})
        if third_place.get("submittedBy") == target_canister:
            stats["third_place_wins"] += 1
            stats["total_wins"] += 1
            if is_within_3_days:
                stats["third_place_wins_last_3_days"] += 1
                stats["total_wins_last_3_days"] += 1

            reward_amount = third_place.get("reward", {}).get("amount", "0")
            stats["win_details"]["third_place"].append({
                "challengeId": challenge_id,
                "timestamp": timestamp,
                "reward_amount": reward_amount,
                "submissionId": third_place.get("submissionId", ""),
                "within_3_days": is_within_3_days
            })

    return stats


def get_all_mainer_canisters(frontend_winners: List[Dict], archived_winners: List[Dict]) -> List[str]:
    """Extract all unique mAIner canister IDs from winner data."""
    canister_ids = set()

    all_winners = frontend_winners + archived_winners
    for winner_declaration in all_winners:
        # Check all placement positions
        for position_key in ["winner", "secondPlace", "thirdPlace"]:
            placement = winner_declaration.get(position_key, {})
            submitted_by = placement.get("submittedBy")
            if submitted_by:
                canister_ids.add(submitted_by)

    return sorted(list(canister_ids))


def analyze_single_canister(target_canister: str, frontend_winners: List[Dict], archived_winners: List[Dict]) -> Dict:
    """Analyze wins for a single canister and return stats."""
    stats = analyze_canister_wins(target_canister, frontend_winners, archived_winners)
    return stats


def analyze_all_canisters(network: str, frontend_winners: List[Dict], archived_winners: List[Dict]) -> Dict:
    """Analyze all mAIner canisters and return aggregated results."""
    canister_ids = get_all_mainer_canisters(frontend_winners, archived_winners)

    print(f"\n🔍 Found {len(canister_ids)} unique mAIner canisters in winner data")

    all_results = {}
    summary_stats = {
        "total_canisters": len(canister_ids),
        "canisters_with_wins": 0,
        "top_performers": [],
        "network": network,
        "total_challenges_analyzed": len(frontend_winners + archived_winners)
    }

    for i, canister_id in enumerate(canister_ids, 1):
        print(f"   Analyzing {i}/{len(canister_ids)}: {canister_id[:20]}...")
        stats = analyze_single_canister(canister_id, frontend_winners, archived_winners)

        if stats["total_wins_last_3_days"] > 0:
            summary_stats["canisters_with_wins"] += 1

        all_results[canister_id] = stats

    # Create top performers list (sorted by recent wins only)
    performers = []
    for canister_id, stats in all_results.items():
        if stats["total_wins_last_3_days"] > 0:
            performers.append({
                "canister_id": canister_id,
                "recent_wins": stats["total_wins_last_3_days"],
                "first_place_recent": stats["first_place_wins_last_3_days"],
                "second_place_recent": stats["second_place_wins_last_3_days"],
                "third_place_recent": stats["third_place_wins_last_3_days"]
            })

    # Sort by: recent wins desc, then recent first place desc, then recent second place desc, then recent third place desc
    performers.sort(key=lambda x: (x["recent_wins"], x["first_place_recent"], x["second_place_recent"], x["third_place_recent"]), reverse=True)
    summary_stats["top_performers"] = performers[:100]  # Top 100

    return {
        "summary": summary_stats,
        "detailed_results": all_results
    }


def main(network: str, canister_id: str):
    """Main function to analyze mAIner wins."""

    try:
        # Fetch winner data using the same method as frontend
        print("\n1. Fetching recent protocol activity from GameState (same as frontend)...")
        frontend_winners = get_recent_protocol_activity(network)
        print(f"   Found {len(frontend_winners)} winner declarations from getRecentProtocolActivity")

        print("\n2. Fetching archived winners from Archive...")
        archived_winners = get_archived_winners(network)
        print(f"   Found {len(archived_winners)} archived winner declarations")

        if canister_id.lower() == "all":
            print(f"\n=== Analyzing wins for ALL mAIner canisters on network {network} ===")

            # Analyze all canisters
            all_results = analyze_all_canisters(network, frontend_winners, archived_winners)

            # Generate output
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "network": network,
                "query": {
                    "target": "all_canisters",
                    "data_sources": {
                        "frontend_winners_from_getRecentProtocolActivity": len(frontend_winners),
                        "archived_winners": len(archived_winners),
                        "total_challenges": len(frontend_winners + archived_winners)
                    }
                },
                "results": all_results
            }

            # Save to file
            output_file = Path(f"all_mainer_wins_{network}.json")
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            # Display summary results
            summary = all_results["summary"]
            print(f"\n✅ Analysis Complete!")
            print(f"📊 SUMMARY for {summary['total_canisters']} canisters:")
            print(f"   🎯 Canisters with wins: {summary['canisters_with_wins']}")
            print(f"   📈 Total challenges: {summary['total_challenges_analyzed']}")

            print(f"\n🏆 TOP 100 PERFORMERS (Last 3 days):")
            for i, performer in enumerate(summary["top_performers"], 1):
                canister_short = performer["canister_id"][:20] + "..." if len(performer["canister_id"]) > 20 else performer["canister_id"]
                print(f"   {i:2}. {canister_short}")
                print(f"       🥇{performer['first_place_recent']} 🥈{performer['second_place_recent']} 🥉{performer['third_place_recent']} (Recent: {performer['recent_wins']})")

            print(f"\n💾 Detailed results saved to: {output_file}")

        else:
            print(f"=== Analyzing wins for mAIner canister: {canister_id} on network {network} ===")

            # Analyze single canister
            print(f"\n3. Analyzing wins for {canister_id}...")
            stats = analyze_single_canister(canister_id, frontend_winners, archived_winners)

            # Generate output
            output_data = {
                "timestamp": datetime.now().isoformat(),
                "network": network,
                "query": {
                    "target_canister": canister_id,
                    "data_sources": {
                        "frontend_winners_from_getRecentProtocolActivity": len(frontend_winners),
                        "archived_winners": len(archived_winners),
                        "total_challenges": stats["challenges_analyzed"]
                    }
                },
                "results": stats
            }

            # Save to file
            output_file = Path(f"mainer_wins_{canister_id.replace('-', '_')}.json")
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            # Display results
            print(f"\n✅ Analysis Complete!")
            print(f"📊 LAST 3 DAYS Results for {canister_id}:")
            print(f"   🥇 First place wins:  {stats['first_place_wins_last_3_days']}")
            print(f"   🥈 Second place wins: {stats['second_place_wins_last_3_days']}")
            print(f"   🥉 Third place wins:  {stats['third_place_wins_last_3_days']}")
            print(f"   🏆 Total wins:        {stats['total_wins_last_3_days']}")
            print(f"   📈 Challenges analyzed: {stats['challenges_analyzed_last_3_days']}")

            if stats['total_wins_last_3_days'] > 0 and stats['challenges_analyzed_last_3_days'] > 0:
                win_rate_3_days = (stats['total_wins_last_3_days'] / stats['challenges_analyzed_last_3_days']) * 100
                print(f"   📊 Win rate: {win_rate_3_days:.2f}%")

            print(f"\n💾 Detailed results saved to: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check mAIner wins.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        required=True,
        help="Specify the mAIner canister ID to analyze",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id)