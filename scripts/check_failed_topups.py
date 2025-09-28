#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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


def run_dfx_call(canister_id: str, method: str, args: str, network: str) -> Any:
    """Run a dfx canister call and return the parsed JSON response."""
    cmd = [
        "dfx", "canister", "call",
        "--network", network,
        "--output", "json",
        canister_id,
        method
    ]

    if args:
        cmd.append(args)

    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_json = json.loads(result.stdout)

        if 'Ok' in response_json:
            return response_json['Ok']
        elif 'Err' in response_json:
            raise Exception(f"Canister error: {response_json['Err']}")
        else:
            return response_json
    except subprocess.CalledProcessError as e:
        print(f"Error running dfx command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        raise


def get_user_icp_transactions(user_principal: str, network: str, max_results: int = 1000) -> Dict:
    """Get user's ICP transaction history."""
    icp_index_canister = "qhbym-qaaaa-aaaaa-aaafq-cai"  # ICP Index Canister

    args = f'(record{{account=record {{owner = principal "{user_principal}"}}; max_results={max_results}:nat}})'

    result = run_dfx_call(icp_index_canister, "get_account_transactions", args, "ic")
    return result


def get_gamestate_redeemed_blocks(network: str) -> List[Dict]:
    """Get all redeemed transaction blocks from GameState."""
    gamestate_id = get_canister_id_from_env("SUBNET_0_1_GAMESTATE", network)
    return run_dfx_call(gamestate_id, "getRedeemedTransactionBlocksAdmin", "", network)


def check_transaction_processed(transaction_id: str, network: str) -> Optional[Dict]:
    """Check if a specific transaction was processed by GameState."""
    gamestate_id = get_canister_id_from_env("SUBNET_0_1_GAMESTATE", network)
    args = f'(record{{paymentTransactionBlockId={transaction_id}:nat64}})'

    try:
        result = run_dfx_call(gamestate_id, "getRedeemedTransactionBlockAdmin", args, network)
        return result
    except Exception as e:
        if "entry not found" in str(e):
            return None
        raise


def get_gamestate_account_address() -> str:
    """Get the GameState canister's ICP account address."""
    return "300d6f0058417bb5131c7313a3fe7f7b90510ca2f413ab863d39b1e35eceebad"


def convert_timestamp_to_readable(timestamp_nanos: int) -> str:
    """Convert nanoseconds timestamp to readable format."""
    timestamp_seconds = timestamp_nanos / 1_000_000_000
    dt = datetime.fromtimestamp(timestamp_seconds)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def analyze_user_topups(user_principal: str, network: str) -> Dict:
    """Analyze user's top-up transactions and identify failures."""

    print(f"\n🔍 Analyzing top-up transactions for user: {user_principal}")

    # Get user's ICP transaction history
    print("1. Fetching user's ICP transaction history...")
    user_transactions = get_user_icp_transactions(user_principal, network)

    if not user_transactions or 'transactions' not in user_transactions:
        return {
            "error": "Could not fetch user transactions",
            "user_principal": user_principal,
            "network": network
        }

    transactions = user_transactions.get('transactions', [])
    current_balance = user_transactions.get('balance', '0')

    print(f"   Found {len(transactions)} total transactions")
    print(f"   Current ICP balance: {int(current_balance) / 100_000_000:.8f} ICP")

    # Filter for top-up transactions (memo [173] to GameState)
    gamestate_address = get_gamestate_account_address()
    topup_transactions = []

    for tx in transactions:
        tx_data = tx.get('transaction', {})
        operation = tx_data.get('operation', {})

        if 'Transfer' in operation:
            transfer = operation['Transfer']
            memo = tx_data.get('icrc1_memo', [])
            to_address = transfer.get('to', '')

            # Check if it's a top-up: memo [173] and sent to GameState
            if memo == [[173]] and to_address == gamestate_address:
                topup_transactions.append({
                    'id': tx.get('id'),
                    'amount_e8s': int(transfer.get('amount', {}).get('e8s', '0')),
                    'amount_icp': int(transfer.get('amount', {}).get('e8s', '0')) / 100_000_000,
                    'timestamp_nanos': int(tx_data.get('timestamp', [{}])[0].get('timestamp_nanos', '0')),
                    'timestamp_readable': convert_timestamp_to_readable(int(tx_data.get('timestamp', [{}])[0].get('timestamp_nanos', '0')))
                })

    print(f"2. Found {len(topup_transactions)} top-up transactions (memo [173] to GameState)")

    # Check each top-up transaction for processing status
    print("3. Checking processing status for each top-up...")

    results = {
        "user_principal": user_principal,
        "network": network,
        "current_icp_balance": float(current_balance) / 100_000_000,
        "total_transactions": len(transactions),
        "total_topup_transactions": len(topup_transactions),
        "processed_topups": [],
        "failed_topups": [],
        "summary": {
            "total_processed": 0,
            "total_failed": 0,
            "total_failed_amount_icp": 0.0,
            "total_processed_amount_icp": 0.0
        }
    }

    for i, topup in enumerate(topup_transactions, 1):
        print(f"   Checking {i}/{len(topup_transactions)}: Transaction {topup['id']} ({topup['amount_icp']} ICP)")

        processed_block = check_transaction_processed(topup['id'], network)

        if processed_block is not None:
            # Successfully processed
            topup['processed'] = True
            topup['processed_details'] = processed_block
            results['processed_topups'].append(topup)
            results['summary']['total_processed'] += 1
            results['summary']['total_processed_amount_icp'] += topup['amount_icp']
            print(f"      ✅ PROCESSED")
        else:
            # Failed to process
            topup['processed'] = False
            results['failed_topups'].append(topup)
            results['summary']['total_failed'] += 1
            results['summary']['total_failed_amount_icp'] += topup['amount_icp']
            print(f"      ❌ FAILED - No redeemed transaction block found")

    return results


def main(network: str, user_principal: str):
    """Main function to analyze failed top-ups."""

    try:
        print(f"\n=== Analyzing Failed Top-ups for User on network {network} ===")
        print(f"User Principal: {user_principal}")

        # Analyze user's top-ups
        analysis_results = analyze_user_topups(user_principal, network)

        if "error" in analysis_results:
            print(f"\n❌ Error: {analysis_results['error']}")
            return

        # Generate output
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "network": network,
            "analysis_type": "failed_topups",
            "results": analysis_results
        }

        # Save to file
        safe_principal = user_principal.replace("-", "_")
        output_file = Path(f"failed_topups_{network}_{safe_principal[:20]}.json")
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        # Display summary results
        summary = analysis_results["summary"]
        print(f"\n✅ Analysis Complete!")
        print(f"📊 SUMMARY:")
        print(f"   💰 Current ICP Balance: {analysis_results['current_icp_balance']:.8f} ICP")
        print(f"   📝 Total Transactions: {analysis_results['total_transactions']}")
        print(f"   🎯 Total Top-up Transactions: {analysis_results['total_topup_transactions']}")
        print(f"   ✅ Successfully Processed: {summary['total_processed']} ({summary['total_processed_amount_icp']:.8f} ICP)")
        print(f"   ❌ Failed to Process: {summary['total_failed']} ({summary['total_failed_amount_icp']:.8f} ICP)")

        if summary['total_failed'] > 0:
            print(f"\n🚨 FAILED TOP-UPS FOUND:")
            for i, failed_topup in enumerate(analysis_results['failed_topups'], 1):
                print(f"   {i}. Transaction ID: {failed_topup['id']}")
                print(f"      Amount: {failed_topup['amount_icp']:.8f} ICP")
                print(f"      Time: {failed_topup['timestamp_readable']}")

            print(f"\n💡 RECOMMENDATION:")
            print(f"   User is owed {summary['total_failed_amount_icp']:.8f} ICP worth of cycles")
            print(f"   These transactions reached GameState but were never processed into cycles")

        print(f"\n💾 Detailed results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for failed ICP top-up transactions")
    parser.add_argument("--network", required=True,
                       choices=["local", "ic", "testing", "development", "demo", "prd"],
                       help="Network to query")
    parser.add_argument("--user", required=True,
                       help="User principal ID to analyze")

    args = parser.parse_args()

    # Convert network shortcuts
    network = "ic" if args.network == "prd" else args.network

    main(network, args.user)