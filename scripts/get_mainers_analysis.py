#!/usr/bin/env python3

import argparse
import os
import json
import sys
from datetime import datetime, timedelta

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Import ICP ledger functions
from .ledgers.icp import get_cycles_per_icp_from_cmc, get_icp_to_usd_rate_from_coinbase, get_icp_transactions, principal_to_account_id

# GameState canister treasury account ID
GAMESTATE_TREASURY_ACCOUNT_ID = "300d6f0058417bb5131c7313a3fe7f7b90510ca2f413ab863d39b1e35eceebad"

# CycleOps canister IDs to check for as controllers
CYCLEOPS_CANISTER_IDS = [
    "cpbhu-5iaaa-aaaad-aalta-cai",
    "2daxo-giaaa-aaaap-anvca-cai"
]


def load_mainers_data(network):
    """Load the mainers by principal JSON file for the given network."""
    json_file_path = os.path.join(SCRIPT_DIR, f"get_mainers_by_principal-{network}.json")

    if not os.path.exists(json_file_path):
        print(f"ERROR: JSON file not found: {json_file_path}")
        print(f"Please run: ./scripts/get_mainers.sh --network {network} --statistics")
        sys.exit(1)

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    return data


def calculate_icp_and_usd_for_burn_rate(burn_rate_tcycles, cycles_per_icp, usd_per_icp):
    """
    Calculate ICP and USD needed for a given burn rate in trillion cycles/day.

    Args:
        burn_rate_tcycles: Burn rate in trillion cycles per day
        cycles_per_icp: Current cycles per ICP rate
        usd_per_icp: Current USD per ICP rate

    Returns:
        Tuple of (icp_per_day, usd_per_day)
    """
    # Convert trillion cycles to cycles
    total_cycles = burn_rate_tcycles * 1_000_000_000_000

    # Calculate ICP needed
    icp_per_day = total_cycles / cycles_per_icp

    # Calculate USD value
    usd_per_day = icp_per_day * usd_per_icp

    return icp_per_day, usd_per_day


def check_mainer_controllers(network, canister_id):
    """
    Check if a mainer has CycleOps canisters as controllers.

    Args:
        network: The network to query
        canister_id: The mainer canister ID to check

    Returns:
        List of CycleOps canister IDs that are controllers, or empty list
    """
    try:
        cmd = ["dfx", "canister", "--network", network, "info", canister_id]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return []

        output = result.stdout

        # Parse the controllers from the output
        # Looking for lines like "Controllers: canister1 canister2 ..."
        cycleops_controllers = []

        for line in output.split('\n'):
            if 'Controllers:' in line or 'Controller' in line:
                # Check if any of the CycleOps canister IDs are in this line
                for cycleops_id in CYCLEOPS_CANISTER_IDS:
                    if cycleops_id in line:
                        cycleops_controllers.append(cycleops_id)

        return cycleops_controllers

    except Exception as e:
        return []


def analyze_principal_topups(principal_id):
    """
    Analyze ICP top-ups sent by a principal to the GameState treasury.

    Args:
        principal_id: The principal ID to analyze

    Returns:
        Dict with top-up analysis or None if error
    """
    try:
        # Get the principal's account ID
        principal_account_id = principal_to_account_id(principal_id)

        # Get ICP transactions for this principal
        transactions_data = get_icp_transactions(principal_id, max_results=1000)

        if not transactions_data:
            return {
                "error": "No transaction data available",
                "total_last_3_months": 0,
                "total_last_month": 0,
                "avg_per_day_last_month": 0,
                "transaction_count_3_months": 0,
                "transaction_count_1_month": 0
            }

        # Get current time
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)
        one_month_ago = now - timedelta(days=30)

        # Convert to nanoseconds since epoch
        three_months_ago_nanos = int(three_months_ago.timestamp() * 1_000_000_000)
        one_month_ago_nanos = int(one_month_ago.timestamp() * 1_000_000_000)

        # Analyze transactions
        total_3_months = 0
        total_1_month = 0
        count_3_months = 0
        count_1_month = 0

        transactions = transactions_data.get('transactions', [])

        for tx in transactions:
            try:
                tx_data = tx.get('transaction', {})

                # Get timestamp
                timestamp_data = tx_data.get('timestamp', [{}])[0] if tx_data.get('timestamp') else {}
                timestamp_nanos = timestamp_data.get('timestamp_nanos', 0)

                if isinstance(timestamp_nanos, str):
                    timestamp_nanos = int(timestamp_nanos)

                # Check if it's a transfer operation
                operation = tx_data.get('operation', {})
                if 'Transfer' not in operation:
                    continue

                transfer = operation['Transfer']
                from_account = transfer.get('from', '')
                to_account = transfer.get('to', '')

                # Check if this is a transfer from our principal to GameState treasury
                if from_account == principal_account_id and to_account == GAMESTATE_TREASURY_ACCOUNT_ID:
                    amount_e8s = int(transfer.get('amount', {}).get('e8s', 0))
                    amount_icp = amount_e8s / 100_000_000

                    # Check time periods
                    if timestamp_nanos >= three_months_ago_nanos:
                        total_3_months += amount_icp
                        count_3_months += 1

                        if timestamp_nanos >= one_month_ago_nanos:
                            total_1_month += amount_icp
                            count_1_month += 1

            except Exception as e:
                # Skip problematic transactions
                continue

        # Calculate daily average for last month
        avg_per_day_last_month = total_1_month / 30 if total_1_month > 0 else 0

        return {
            "total_last_3_months": round(total_3_months, 8),
            "total_last_month": round(total_1_month, 8),
            "avg_per_day_last_month": round(avg_per_day_last_month, 8),
            "transaction_count_3_months": count_3_months,
            "transaction_count_1_month": count_1_month
        }

    except Exception as e:
        return {
            "error": str(e),
            "total_last_3_months": 0,
            "total_last_month": 0,
            "avg_per_day_last_month": 0,
            "transaction_count_3_months": 0,
            "transaction_count_1_month": 0
        }


def generate_markdown_summary(data, network, cycles_per_icp, usd_per_icp):
    """Generate a markdown summary of the analysis."""
    from datetime import datetime

    md_lines = []
    md_lines.append("# mAIner Network Analysis")
    md_lines.append("")
    md_lines.append(f"**Network:** {network}")
    md_lines.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    md_lines.append(f"**Data Timestamp:** {data.get('timestamp', 'N/A')}")
    md_lines.append("")
    md_lines.append("## Current Rates")
    md_lines.append("")
    md_lines.append(f"- **Cycles per ICP:** {cycles_per_icp / 1_000_000_000_000:.4f} Tcycles/ICP")
    md_lines.append(f"- **ICP Price:** ${usd_per_icp:.4f} USD/ICP")
    md_lines.append("")
    md_lines.append("## Network Summary")
    md_lines.append("")
    md_lines.append(f"- **Total mAIners:** {data.get('total_mainers', 0)}")
    md_lines.append(f"- **Total Principals:** {data.get('total_principals', 0)}")

    total_burn_rate = data.get('total_network_daily_burn_rate_active', 0)
    total_icp, total_usd = calculate_icp_and_usd_for_burn_rate(total_burn_rate, cycles_per_icp, usd_per_icp)

    md_lines.append(f"- **Total Daily Burn Rate (Active):** {total_burn_rate} Tcycles/day")
    md_lines.append(f"- **Total ICP Needed/Day:** {total_icp:.2f} ICP/day")
    md_lines.append(f"- **Total USD Value/Day:** ${total_usd:.2f}/day")
    md_lines.append("")

    # Calculate monthly and yearly projections
    md_lines.append("### Projections")
    md_lines.append("")
    md_lines.append("| Period             | ICP Required      | USD Value         |")
    md_lines.append("|--------------------|-------------------|-------------------|")
    md_lines.append(f"| Daily              | {total_icp:>13.2f} ICP | ${total_usd:>15,.2f} |")
    md_lines.append(f"| Weekly             | {total_icp * 7:>13.2f} ICP | ${total_usd * 7:>15,.2f} |")
    md_lines.append(f"| Monthly (30 days)  | {total_icp * 30:>13.2f} ICP | ${total_usd * 30:>15,.2f} |")
    md_lines.append(f"| Yearly (365 days)  | {total_icp * 365:>13.2f} ICP | ${total_usd * 365:>15,.2f} |")
    md_lines.append("")

    # Top principals by burn rate
    md_lines.append("## Top Principals by Daily Burn Rate")
    md_lines.append("")

    # Check if we have topup data
    has_topup_data = any('topups' in pdata for pdata in data.get('principals', {}).values())

    if has_topup_data:
        md_lines.append("| Rank | Principal            | Active mAIners | CycleOps | Daily Burn (Tcycles) | ICP/day    | USD/day    | Avg/Day ICP Top-up (Last Month) |")
        md_lines.append("|-----:|:---------------------|---------------:|---------:|---------------------:|-----------:|-----------:|--------------------------------:|")
    else:
        md_lines.append("| Rank | Principal            | Active mAIners | CycleOps | Daily Burn (Tcycles) | ICP/day    | USD/day    |")
        md_lines.append("|-----:|:---------------------|---------------:|---------:|---------------------:|-----------:|-----------:|")

    principals = data.get('principals', {})
    # Get principals with burn rate > 0 and sort by burn rate
    active_principals = [(pid, pdata) for pid, pdata in principals.items()
                         if pdata.get('total_daily_burn_rate_active', 0) > 0]
    # Already sorted in JSON, just take top 20

    for rank, (principal_id, principal_data) in enumerate(list(active_principals)[:20], 1):
        burn_rate = principal_data.get('total_daily_burn_rate_active', 0)
        icp_per_day, usd_per_day = calculate_icp_and_usd_for_burn_rate(burn_rate, cycles_per_icp, usd_per_icp)
        active_count = principal_data.get('active_mainers', 0)
        cycleops_count = principal_data.get('mainers_with_cycleops', 0)

        # Truncate principal for readability
        principal_short = f"{principal_id[:8]}...{principal_id[-3:]}"

        if has_topup_data:
            avg_topup = principal_data.get('topups', {}).get('avg_per_day_last_month', 0)
            md_lines.append(f"| {rank:>4} | `{principal_short:<18}` | {active_count:>14} | {cycleops_count:>8} | {burn_rate:>20} | {icp_per_day:>10.2f} | ${usd_per_day:>9.2f} | {avg_topup:>31.4f} |")
        else:
            md_lines.append(f"| {rank:>4} | `{principal_short:<18}` | {active_count:>14} | {cycleops_count:>8} | {burn_rate:>20} | {icp_per_day:>10.2f} | ${usd_per_day:>9.2f} |")

    md_lines.append("")
    md_lines.append("## All Principals Summary")
    md_lines.append("")

    if has_topup_data:
        md_lines.append("| Principal            | Total mAIners | Active | Paused | CycleOps | Daily Burn (Tcycles) | ICP/day    | USD/day    | Avg/Day ICP Top-up (Last Month) |")
        md_lines.append("|:---------------------|----------------|--------|--------|:--------:|---------------------:|-----------:|-----------:|--------------------------------:|")
    else:
        md_lines.append("| Principal            | Total mAIners | Active | Paused | CycleOps | Daily Burn (Tcycles) | ICP/day    | USD/day    |")
        md_lines.append("|:---------------------|----------------|--------|--------|:--------:|---------------------:|-----------:|-----------:|")

    # Sort by daily burn rate (descending) - same as other tables
    all_principals_sorted = sorted(principals.items(), key=lambda x: x[1].get('total_daily_burn_rate_active', 0), reverse=True)

    for principal_id, principal_data in all_principals_sorted:
        burn_rate = principal_data.get('total_daily_burn_rate_active', 0)
        icp_per_day, usd_per_day = calculate_icp_and_usd_for_burn_rate(burn_rate, cycles_per_icp, usd_per_icp)

        total_mainers = principal_data.get('total_mainers', 0)
        active_count = principal_data.get('active_mainers', 0)
        paused_count = principal_data.get('paused_mainers', 0)
        cycleops_count = principal_data.get('mainers_with_cycleops', 0)

        # Truncate principal for readability
        principal_short = f"{principal_id[:8]}...{principal_id[-3:]}"

        if has_topup_data:
            avg_topup = principal_data.get('topups', {}).get('avg_per_day_last_month', 0)
            md_lines.append(f"| `{principal_short:<18}` | {total_mainers:>14} | {active_count:>6} | {paused_count:>6} | {cycleops_count:>8} | {burn_rate:>20} | {icp_per_day:>10.2f} | ${usd_per_day:>9.2f} | {avg_topup:>31.4f} |")
        else:
            md_lines.append(f"| `{principal_short:<18}` | {total_mainers:>14} | {active_count:>6} | {paused_count:>6} | {cycleops_count:>8} | {burn_rate:>20} | {icp_per_day:>10.2f} | ${usd_per_day:>9.2f} |")

    # Add top-up analysis section if data is available
    if has_topup_data:
        md_lines.append("")
        md_lines.append("## ICP Top-Ups to GameState Treasury")
        md_lines.append("")
        md_lines.append("Analysis of ICP sent to the GameState treasury account for cycle top-ups. Required amounts shown in brackets.")
        md_lines.append("")
        md_lines.append("| Principal            | Last Month (Required)        | Avg/Day Last Month (Required) |")
        md_lines.append("|:---------------------|-----------------------------:|------------------------------:|")

        # Sort by daily burn rate (descending) - same as other tables
        principals_with_topups = [
            (pid, pdata) for pid, pdata in principals.items()
            if pdata.get('total_daily_burn_rate_active', 0) > 0
        ]
        # Already sorted by burn rate in the JSON

        for principal_id, principal_data in principals_with_topups:
            topup_data = principal_data.get('topups', {})
            principal_short = f"{principal_id[:8]}...{principal_id[-3:]}"

            # Get actual top-up amounts
            total_1m = topup_data.get('total_last_month', 0)
            avg_day = topup_data.get('avg_per_day_last_month', 0)

            # Calculate required amounts
            burn_rate = principal_data.get('total_daily_burn_rate_active', 0)
            required_icp_per_day, _ = calculate_icp_and_usd_for_burn_rate(burn_rate, cycles_per_icp, usd_per_icp)
            required_1m = required_icp_per_day * 30

            # Calculate percentages
            pct_1m = (total_1m / required_1m * 100) if required_1m > 0 else 0
            pct_day = (avg_day / required_icp_per_day * 100) if required_icp_per_day > 0 else 0

            # Format: actual (required) (percentage%)
            last_month_str = f"{total_1m:>10.2f} ({required_1m:>10.2f}) ({pct_1m:>5.1f}%)"
            avg_day_str = f"{avg_day:>10.4f} ({required_icp_per_day:>10.2f}) ({pct_day:>5.1f}%)"

            md_lines.append(f"| `{principal_short:<18}` | {last_month_str:>28} | {avg_day_str:>29} |")

        md_lines.append("")
        md_lines.append("**Note:** Values shown as Actual (Required) (%). GameState Treasury Account ID: `300d6f0058417bb5131c7313a3fe7f7b90510ca2f413ab863d39b1e35eceebad`")
        md_lines.append("")

    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append(f"*Generated by get_mainers_analysis.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*")
    md_lines.append("")

    return "\n".join(md_lines)


def main(network, analyze_topups=False, limit=None):
    print("----------------------------------------------")
    print(f"Loading mAIners data for network: {network}")
    if analyze_topups:
        print("Top-up analysis: ENABLED (this will be slow)")
    if limit:
        print(f"Limit: Processing only first {limit} principals")
    print("----------------------------------------------")

    # Load the JSON data
    data = load_mainers_data(network)

    # Print basic info to confirm it loaded
    print(f"Network: {data['network']}")
    print(f"Timestamp: {data['timestamp']}")
    print(f"Total mainers: {data['total_mainers']}")
    print(f"Total principals: {data['total_principals']}")
    print(f"Total network daily burn rate (active): {data['total_network_daily_burn_rate_active']} trillion cycles/day")
    print("----------------------------------------------")

    # Get current rates
    print("Fetching current ICP and cycles rates...")
    cycles_per_icp = get_cycles_per_icp_from_cmc()
    usd_per_icp = get_icp_to_usd_rate_from_coinbase()

    print(f"Current rate: {cycles_per_icp / 1_000_000_000_000:.4f} Tcycles/ICP")
    print(f"Current rate: ${usd_per_icp:.4f} USD/ICP")
    print("----------------------------------------------")

    # Update JSON with ICP and USD calculations
    print("Updating JSON with ICP and USD calculations...")

    principals = data.get('principals', {})

    for principal_id, principal_data in principals.items():
        burn_rate = principal_data.get('total_daily_burn_rate_active', 0)
        icp_per_day, usd_per_day = calculate_icp_and_usd_for_burn_rate(
            burn_rate, cycles_per_icp, usd_per_icp
        )

        # Add ICP and USD calculations to principal data
        principal_data['icp_per_day'] = round(icp_per_day, 8)
        principal_data['usd_per_day'] = round(usd_per_day, 2)

    # Add rates to top-level data
    data['cycles_per_icp'] = cycles_per_icp
    data['usd_per_icp'] = round(usd_per_icp, 4)

    # Calculate total network ICP and USD
    total_burn_rate = data.get('total_network_daily_burn_rate_active', 0)
    total_icp, total_usd = calculate_icp_and_usd_for_burn_rate(
        total_burn_rate, cycles_per_icp, usd_per_icp
    )
    data['total_network_icp_per_day'] = round(total_icp, 8)
    data['total_network_usd_per_day'] = round(total_usd, 2)

    # Check CycleOps controllers for all mainers
    print("----------------------------------------------")
    print("Checking for CycleOps controllers on mainers...")
    print("----------------------------------------------")

    first_cycleops_found = False

    for principal_id, principal_data in principals.items():
        addresses = principal_data.get('addresses', [])
        cycleops_count = 0

        for address in addresses:
            cycleops_controllers = check_mainer_controllers(network, address)
            if cycleops_controllers:
                cycleops_count += 1

                # Debug: Print the first time we find a CycleOps controller
                if not first_cycleops_found:
                    print(f"DEBUG: Found CycleOps controller(s) on mainer {address}")
                    print(f"       Controllers found: {', '.join(cycleops_controllers)}")
                    print(f"       Principal: {principal_id[:20]}...")
                    first_cycleops_found = True

        principal_data['mainers_with_cycleops'] = cycleops_count

    print("CycleOps controller check complete!")
    print("----------------------------------------------")

    # Analyze ICP top-ups if requested
    if analyze_topups:
        print("----------------------------------------------")
        print("Analyzing ICP top-ups to GameState treasury...")
        print("This may take a while as it queries transaction history for each principal...")
        print("----------------------------------------------")

        # Get list of principal IDs to process
        principal_ids = list(principals.keys())
        if limit and limit > 0:
            principal_ids = principal_ids[:limit]
            print(f"Limited to first {limit} principals")

        total_principals = len(principal_ids)
        processed = 0

        for principal_id in principal_ids:
            principal_data = principals[principal_id]
            processed += 1
            print(f"[{processed}/{total_principals}] Analyzing {principal_id[:20]}...")

            topup_data = analyze_principal_topups(principal_id)
            principal_data['topups'] = topup_data

        print("----------------------------------------------")
        print("Top-up analysis complete!")
        print("----------------------------------------------")

    # Save updated JSON
    json_file_path = os.path.join(SCRIPT_DIR, f"get_mainers_by_principal-{network}.json")
    with open(json_file_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Updated JSON file: {os.path.abspath(json_file_path)}")
    print("----------------------------------------------")

    # Generate markdown summary
    print("Generating markdown summary...")
    md_content = generate_markdown_summary(data, network, cycles_per_icp, usd_per_icp)

    md_file_path = os.path.join(SCRIPT_DIR, f"get_mainers_analysis-{network}.md")
    with open(md_file_path, 'w') as f:
        f.write(md_content)

    print(f"Generated markdown summary: {os.path.abspath(md_file_path)}")
    print("----------------------------------------------")

    # Print summary to console
    print("\nSUMMARY:")
    print("=" * 100)
    print(f"Total daily burn rate: {total_burn_rate} Tcycles/day")
    print(f"Total ICP needed/day: {total_icp:.2f} ICP")
    print(f"Total USD value/day: ${total_usd:.2f}")
    print(f"Monthly projection: {total_icp * 30:.2f} ICP (${total_usd * 30:.2f})")
    print(f"Yearly projection: {total_icp * 365:.2f} ICP (${total_usd * 365:.2f})")
    print("=" * 100)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze mAIners by principal data.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to analyze (default: local)",
    )
    parser.add_argument(
        "--topups",
        action="store_true",
        help="Analyze ICP top-ups sent to GameState treasury (slow, queries transaction history)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of principals to analyze (for testing purposes)",
    )
    args = parser.parse_args()
    main(args.network, args.topups, args.limit)
