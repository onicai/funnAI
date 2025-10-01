#!/usr/bin/env python3

import json
import subprocess
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from collections import defaultdict

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
        method,
        args
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        response_json = json.loads(result.stdout)
        return response_json
    except subprocess.CalledProcessError as e:
        print(f"Error running dfx command: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        raise


def nanoseconds_to_date(nanoseconds: int) -> str:
    """Convert nanoseconds timestamp to YYYY-MM-DD date string."""
    seconds = nanoseconds / 1_000_000_000
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return dt.strftime('%Y-%m-%d')


def parse_block_for_transaction(block: Dict, tx_type: str) -> Optional[Dict]:
    """Parse a block from get_blocks to extract transaction of specified type (burn/mint).

    Args:
        block: Block data from TokenIndex
        tx_type: Transaction type to look for ('burn' or 'mint')

    Returns:
        Dict with timestamp and amount if transaction type matches, None otherwise
    """
    try:
        if 'Map' not in block:
            return None

        timestamp = None
        tx_data = {}

        for item in block['Map']:
            key = item['0']
            value = item['1']

            if key == 'ts' and 'Nat64' in value:
                timestamp = int(value['Nat64'])
            elif key == 'tx' and 'Map' in value:
                for tx_item in value['Map']:
                    tx_key = tx_item['0']
                    tx_value = tx_item['1']

                    if tx_key == 'op' and 'Text' in tx_value:
                        tx_data['op'] = tx_value['Text']
                    elif tx_key == 'amt':
                        if 'Nat' in tx_value:
                            tx_data['amount'] = int(tx_value['Nat'])
                        elif 'Nat64' in tx_value:
                            tx_data['amount'] = int(tx_value['Nat64'])

        if tx_data.get('op') == tx_type and 'amount' in tx_data and timestamp:
            return {
                'timestamp': timestamp,
                'amount': tx_data['amount']
            }

        return None

    except Exception:
        return None


def load_cache(network: str, tx_type: str) -> Dict:
    """Load cached transaction data if it exists."""
    cache_file = Path(SCRIPT_DIR) / f"{tx_type}_tokens_cache.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                if cache.get('network') == network:
                    print(f"📦 Loaded cache: forward scan up to block {cache.get('last_block_scanned', 0)}, backward scan from block {cache.get('last_block_scanned_backward', 'N/A')}")
                    return cache
        except Exception as e:
            print(f"⚠️  Could not load cache: {e}")
    return {
        'network': network,
        'last_block_scanned': 0,  # Forward scan progress
        'last_block_scanned_backward': None,  # Backward scan progress
        f'daily_{tx_type}s': {},
        f'{tx_type}_transactions': []
    }


def save_cache(cache: Dict, tx_type: str):
    """Save cache to disk."""
    cache_file = Path(SCRIPT_DIR) / f"{tx_type}_tokens_cache.json"
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️  Could not save cache: {e}")


def process_transactions(network: str, tx_type: str = 'burn') -> Dict[str, Any]:
    """Fetch all transactions of specified type from TokenIndex and aggregate by day.

    Args:
        network: Network to query (prd, testing, etc.)
        tx_type: Transaction type to track ('burn' or 'mint')
    """

    # Get TokenIndex canister ID
    try:
        index_canister_id = get_canister_id_from_env("SUBNET_0_1_INDEX", network)
    except ValueError:
        if network == "ic" or network == "prd":
            index_canister_id = "mziuv-biaaa-aaaaa-qccrq-cai"
        elif network == "testing":
            index_canister_id = "mziuv-biaaa-aaaaa-qccrq-cai"
        else:
            raise ValueError(f"Unknown TokenIndex canister ID for network: {network}")

    print(f"Using TokenIndex canister: {index_canister_id}")

    # Load cache
    cache = load_cache(network, tx_type)
    daily_burns: Dict[str, int] = defaultdict(int, cache.get(f'daily_{tx_type}s', {}))
    total_transactions_processed = len(cache.get(f'{tx_type}_transactions', []))
    total_burn_amount = sum(daily_burns.values())

    # Get the number of blocks synced
    print(f"Getting TokenIndex status...")
    status_response = run_dfx_call(index_canister_id, "status", "()", network)
    num_blocks_synced = int(status_response.get("num_blocks_synced", 0))

    print(f"TokenIndex has synced {num_blocks_synced} blocks")

    # Scan backwards from latest block to find recent burns first
    batch_size = 1000
    forward_pos = cache.get('last_block_scanned', 0)
    backward_pos = cache.get('last_block_scanned_backward')

    # Initialize backward position if not set
    if backward_pos is None:
        backward_pos = num_blocks_synced

    # Check if we're done
    if forward_pos >= backward_pos:
        print(f"✅ Cache is up to date! All blocks scanned.")
        return {
            f'daily_{tx_type}s': dict(daily_burns),
            'total_transactions': total_transactions_processed,
            f'total_{tx_type}ed': total_burn_amount,
            'blocks_scanned': num_blocks_synced
        }

    total_blocks_to_scan = backward_pos - forward_pos
    print(f"📊 Need to scan {total_blocks_to_scan} blocks")
    print(f"   Forward position: {forward_pos}")
    print(f"   Backward position: {backward_pos}")
    print(f"   Transaction type: {tx_type}")
    print(f"   Strategy: Scan backwards from {backward_pos} (to find recent {tx_type}s first)")

    burn_transactions = cache.get(f'{tx_type}_transactions', [])

    # Scan BACKWARDS from the latest block
    while backward_pos > forward_pos:
        # Calculate batch start (move backward)
        batch_start = max(forward_pos, backward_pos - batch_size)
        fetch_length = backward_pos - batch_start

        # Calculate and display progress
        blocks_scanned = (num_blocks_synced - backward_pos) + forward_pos
        progress_pct = (blocks_scanned / num_blocks_synced) * 100
        total_funnai = total_burn_amount / 100_000_000
        action_word = "burned" if tx_type == "burn" else "minted"
        print(f"Progress: {progress_pct:.1f}% | {total_transactions_processed} {tx_type}s | {total_funnai:.2f} FUNNAI {action_word} | Blocks {batch_start}-{backward_pos - 1}", flush=True)

        try:
            args = f"(record {{ start = {batch_start}; length = {fetch_length} }})"
            response = run_dfx_call(index_canister_id, "get_blocks", args, network)

            blocks = response.get("blocks", [])

            if not blocks:
                backward_pos = batch_start
                continue

            # Process blocks
            for block in blocks:
                tx = parse_block_for_transaction(block, tx_type)
                if tx and tx['amount'] > 0:
                    date_str = nanoseconds_to_date(tx['timestamp'])
                    daily_burns[date_str] += tx['amount']
                    total_burn_amount += tx['amount']
                    total_transactions_processed += 1

                    # Store transaction details
                    burn_transactions.append({
                        'date': date_str,
                        'amount': tx['amount'],
                        'timestamp': tx['timestamp']
                    })

                    if total_transactions_processed % 100 == 0:
                        print(f"  ✓ Found {total_transactions_processed} {tx_type} transactions so far...", flush=True)

            # Move backward position
            backward_pos = batch_start

            # Save cache every 10 batches (10k blocks)
            if (num_blocks_synced - backward_pos) % 10000 < batch_size:
                cache['last_block_scanned'] = forward_pos
                cache['last_block_scanned_backward'] = backward_pos
                cache[f'daily_{tx_type}s'] = dict(daily_burns)
                cache[f'{tx_type}_transactions'] = burn_transactions
                save_cache(cache, tx_type)
                print(f"  💾 Cache saved (backward at block {backward_pos})", flush=True)

        except Exception as e:
            print(f"❌ Error fetching blocks at index {batch_start}: {e}", flush=True)
            # Save cache before continuing
            cache['last_block_scanned'] = forward_pos
            cache['last_block_scanned_backward'] = backward_pos
            cache[f'daily_{tx_type}s'] = dict(daily_burns)
            cache[f'{tx_type}_transactions'] = burn_transactions
            save_cache(cache, tx_type)
            backward_pos = batch_start
            continue

    # Final cache save
    cache['last_block_scanned'] = num_blocks_synced
    cache['last_block_scanned_backward'] = 0
    cache[f'daily_{tx_type}s'] = dict(daily_burns)
    cache[f'{tx_type}_transactions'] = burn_transactions
    save_cache(cache, tx_type)

    action_past = "burned" if tx_type == "burn" else "minted"
    print(f"\n✅ Scanned {num_blocks_synced} TokenIndex blocks")
    print(f"✅ Found {total_transactions_processed} {tx_type} transactions")
    print(f"💰 Total {action_past} amount: {total_burn_amount / 100_000_000:.8f} FUNNAI")

    return {
        f'daily_{tx_type}s': dict(daily_burns),
        'total_transactions': total_transactions_processed,
        f'total_{tx_type}ed': total_burn_amount,
        'blocks_scanned': num_blocks_synced
    }


def calculate_accumulated_burns(daily_burns: Dict[str, int], tx_type: str) -> Dict[str, Dict[str, Any]]:
    """Calculate accumulated transactions for each day.

    Args:
        daily_burns: Dictionary mapping dates to transaction amounts
        tx_type: Transaction type ('burn' or 'mint')
    """
    sorted_dates = sorted(daily_burns.keys())

    result = {}
    accumulated_total = 0

    for date in sorted_dates:
        daily_amount = daily_burns[date]
        accumulated_total += daily_amount

        result[date] = {
            f'daily_{tx_type}ed_e8s': daily_amount,
            f'daily_{tx_type}ed_funnai': daily_amount / 100_000_000,
            f'accumulated_{tx_type}ed_e8s': accumulated_total,
            f'accumulated_{tx_type}ed_funnai': accumulated_total / 100_000_000
        }

    return result


def main(network: str, tx_type: str = 'burn'):
    """Main function to calculate transactions.

    Args:
        network: Network to query (prd, testing, etc.)
        tx_type: Transaction type to analyze ('burn' or 'mint')
    """

    try:
        emoji = "🔥" if tx_type == "burn" else "🌟"
        action_past = "burned" if tx_type == "burn" else "minted"
        action_verb = "Burning" if tx_type == "burn" else "Minting"

        print(f"\n{emoji} Calculating {action_past} FUNNAI tokens for network: {network}")
        print(f"📍 Scanning TokenIndex for {tx_type} transactions")

        # Process all transactions
        print(f"\n1. Fetching and processing {tx_type} transactions from TokenIndex...")
        burn_data = process_transactions(network, tx_type)

        # Calculate daily and accumulated amounts
        print(f"\n2. Calculating daily and accumulated {tx_type}s...")
        daily_accumulated = calculate_accumulated_burns(burn_data[f'daily_{tx_type}s'], tx_type)

        # Generate output with dynamic field names based on tx_type
        daily_key = f'daily_{tx_type}s'
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "network": network,
            "transaction_type": tx_type,
            "summary": {
                f"total_{tx_type}_transactions": burn_data['total_transactions'],
                f"total_{tx_type}ed_e8s": burn_data[f'total_{tx_type}ed'],
                f"total_{tx_type}ed_funnai": burn_data[f'total_{tx_type}ed'] / 100_000_000,
                f"days_with_{tx_type}s": len(burn_data[daily_key]),
                f"first_{tx_type}_date": min(burn_data[daily_key].keys()) if burn_data[daily_key] else None,
                f"last_{tx_type}_date": max(burn_data[daily_key].keys()) if burn_data[daily_key] else None,
                "index_blocks_scanned": burn_data.get('blocks_scanned', 0)
            },
            daily_key: daily_accumulated
        }

        # Save to file in scripts directory
        output_file = Path(SCRIPT_DIR) / f"{tx_type}_tokens_{network}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        # Display summary results
        summary = output_data["summary"]
        print(f"\n✅ Analysis Complete!")
        print(f"📊 SUMMARY:")
        print(f"   {emoji} Total {action_past}: {summary[f'total_{tx_type}ed_funnai']:.8f} FUNNAI")
        print(f"   📈 {tx_type.capitalize()} transactions: {summary[f'total_{tx_type}_transactions']}")
        print(f"   📅 Days with {tx_type}s: {summary[f'days_with_{tx_type}s']}")
        print(f"   🔍 Index blocks scanned: {summary['index_blocks_scanned']}")
        if summary[f'first_{tx_type}_date'] and summary[f'last_{tx_type}_date']:
            print(f"   📆 Date range: {summary[f'first_{tx_type}_date']} to {summary[f'last_{tx_type}_date']}")

        print(f"\n💾 Detailed results saved to: {output_file}")

        # Show last 10 days of transaction data
        if daily_accumulated:
            print(f"\n📅 RECENT DAILY {tx_type.upper()}S:")
            sorted_dates = sorted(daily_accumulated.keys())[-10:]
            for date in sorted_dates:
                data = daily_accumulated[date]
                print(f"   {date}: {data[f'daily_{tx_type}ed_funnai']:.8f} FUNNAI (Accumulated: {data[f'accumulated_{tx_type}ed_funnai']:.8f})")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate FUNNAI token burns or mints by day.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--type",
        choices=["burn", "mint"],
        default="burn",
        help="Transaction type to analyze: burn or mint (default: burn)",
    )
    args = parser.parse_args()
    main(args.network, args.type)
