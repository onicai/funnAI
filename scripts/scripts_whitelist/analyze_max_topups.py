import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

SCRIPT_DIR = Path(__file__).parent

# Whitelist challenge cutoff: August 4, 2025 midnight PT (California time)
CUTOFF_DATE = datetime(2025, 8, 4, 0, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

def is_before_cutoff(timestamp_str):
    """Check if a timestamp is before the whitelist challenge cutoff."""
    try:
        # Parse the ISO timestamp and convert to PT
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        dt_pt = dt.astimezone(ZoneInfo("America/Los_Angeles"))
        return dt_pt < CUTOFF_DATE
    except Exception:
        return False

def analyze_large_outgoing_transfers():
    """
    Analyze all whitelist analysis files to find accounts with outgoing transfers >= 42 ICP.
    """
    print("=== Analyzing Large Outgoing Transfers (42+ ICP) ===")
    
    # Path to the analysis files directory
    analysis_dir = SCRIPT_DIR / "funnai_accounts"

    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory {analysis_dir} not found!")
        return
    
    # Get all analysis files
    analysis_files = list(analysis_dir.glob("whitelist_analysis_*.json"))
    print(f"Found {len(analysis_files)} analysis files to process")
    
    # Track results
    accounts_with_large_transfers = []
    transfer_amounts = []
    stats = {
        "total_accounts": 0,
        "accounts_with_transfers": 0,
        "accounts_with_large_transfers": 0,
        "accounts_with_transfers_before_cutoff": 0,
        "transfers_before_cutoff": 0,
        "transfers_after_cutoff": 0,
        "max_transfer_amount": 0.0,
        "total_large_transfer_amount": 0.0,
        "total_amount_before_cutoff": 0.0
    }
    
    for file_path in analysis_files:
        try:
            # Read the analysis file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            principal = data.get('principal', '')
            balance_history = data.get('balance_history', [])
            
            stats["total_accounts"] += 1
            
            # Look for outgoing transfers >= 42 ICP
            large_transfers = []
            has_any_transfer = False
            
            for entry in balance_history:
                if entry.get('event_type') == 'transaction':
                    transaction_type = entry.get('transaction_type', '')
                    amount_icp = entry.get('amount_icp', 0.0)
                    
                    if transaction_type == 'outgoing_transfer':
                        has_any_transfer = True
                        if amount_icp >= 42.0:
                            # Extract destination address from raw transaction data
                            destination_address = "unknown"
                            raw_tx_data = data.get('raw_transaction_data', {})
                            transactions = raw_tx_data.get('transactions', [])
                            
                            # Find matching transaction by ID
                            tx_id = entry.get('transaction_id', '')
                            for tx in transactions:
                                if tx.get('id') == tx_id:
                                    operation = tx.get('transaction', {}).get('operation', {})
                                    if 'Transfer' in operation:
                                        destination_address = operation['Transfer'].get('to', 'unknown')
                                    break
                            
                            # Check if transfer was before cutoff
                            before_cutoff = is_before_cutoff(entry.get('timestamp', ''))
                            
                            large_transfers.append({
                                "amount": amount_icp,
                                "timestamp": entry.get('timestamp', ''),
                                "transaction_id": tx_id,
                                "fee_icp": entry.get('fee_icp', 0.0),
                                "destination_address": destination_address,
                                "date": entry.get('timestamp', '').split('T')[0] if entry.get('timestamp', '') else 'unknown',
                                "before_cutoff": before_cutoff
                            })
                            transfer_amounts.append(amount_icp)
                            stats["total_large_transfer_amount"] += amount_icp
                            
                            # Track cutoff statistics
                            if before_cutoff:
                                stats["transfers_before_cutoff"] += 1
                                stats["total_amount_before_cutoff"] += amount_icp
                            else:
                                stats["transfers_after_cutoff"] += 1
                            
                            if amount_icp > stats["max_transfer_amount"]:
                                stats["max_transfer_amount"] = amount_icp
            
            if has_any_transfer:
                stats["accounts_with_transfers"] += 1
            
            if large_transfers:
                stats["accounts_with_large_transfers"] += 1
                
                # Check if account has any transfers before cutoff
                has_transfer_before_cutoff = any(t["before_cutoff"] for t in large_transfers)
                if has_transfer_before_cutoff:
                    stats["accounts_with_transfers_before_cutoff"] += 1
                
                accounts_with_large_transfers.append({
                    "principal": principal,
                    "principal_short": principal[:8] + "...",
                    "transfers": large_transfers,
                    "total_large_transfers": len(large_transfers),
                    "max_transfer": max(t["amount"] for t in large_transfers),
                    "total_amount": sum(t["amount"] for t in large_transfers),
                    "has_transfer_before_cutoff": has_transfer_before_cutoff,
                    "transfers_before_cutoff": sum(1 for t in large_transfers if t["before_cutoff"]),
                    "amount_before_cutoff": sum(t["amount"] for t in large_transfers if t["before_cutoff"])
                })
                
        except Exception as e:
            print(f"ERROR processing {file_path.name}: {e}")
            continue
    
    # Sort accounts by max transfer amount (descending)
    accounts_with_large_transfers.sort(key=lambda x: x["max_transfer"], reverse=True)
    
    # Print results
    print("\n" + "="*80)
    print("🎯 LARGE OUTGOING TRANSFER ANALYSIS RESULTS")
    print("="*80)
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"  Total accounts analyzed: {stats['total_accounts']}")
    print(f"  Accounts with any outgoing transfers: {stats['accounts_with_transfers']}")
    print(f"  Accounts with 42+ ICP outgoing transfers: {stats['accounts_with_large_transfers']}")
    print(f"  Accounts with large transfers BEFORE cutoff: {stats['accounts_with_transfers_before_cutoff']}")
    print(f"  Percentage with large transfers: {(stats['accounts_with_large_transfers']/stats['total_accounts']*100):.2f}%")
    print(f"  Percentage qualifying for whitelist: {(stats['accounts_with_transfers_before_cutoff']/stats['total_accounts']*100):.2f}%")
    print(f"  Maximum single transfer: {stats['max_transfer_amount']:.8f} ICP")
    print(f"  Total amount in large transfers: {stats['total_large_transfer_amount']:.8f} ICP")
    print(f"  Transfers before cutoff: {stats['transfers_before_cutoff']}")
    print(f"  Transfers after cutoff: {stats['transfers_after_cutoff']}")
    print(f"  Amount before cutoff: {stats['total_amount_before_cutoff']:.8f} ICP")
    print(f"  Cutoff date: {CUTOFF_DATE.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    if accounts_with_large_transfers:
        print(f"\n🔍 ACCOUNTS WITH 42+ ICP OUTGOING TRANSFERS:")
        print("=" * 80)
        
        for i, account in enumerate(accounts_with_large_transfers, 1):
            print(f"\n[{i}] {account['principal_short']}")
            print(f"    Full principal: {account['principal']}")
            print(f"    Number of large transfers: {account['total_large_transfers']}")
            print(f"    Transfers BEFORE cutoff: {account['transfers_before_cutoff']}")
            print(f"    Amount BEFORE cutoff: {account['amount_before_cutoff']:.8f} ICP")
            print(f"    Qualifies for whitelist: {'✅ YES' if account['has_transfer_before_cutoff'] else '❌ NO'}")
            print(f"    Maximum transfer: {account['max_transfer']:.8f} ICP")
            print(f"    Total large transfer amount: {account['total_amount']:.8f} ICP")
            
            print(f"    Transfer details:")
            for j, transfer in enumerate(account['transfers'], 1):
                cutoff_status = "✅ BEFORE cutoff" if transfer['before_cutoff'] else "❌ AFTER cutoff"
                print(f"      {j}. {transfer['amount']:.8f} ICP (fee: {transfer['fee_icp']:.8f} ICP) - {cutoff_status}")
                print(f"         Date: {transfer['date']}")
                print(f"         Time: {transfer['timestamp']}")
                print(f"         Destination: {transfer['destination_address']}")
                print(f"         TX ID: {transfer['transaction_id']}")
                print()
        
        print(f"\n📈 TRANSFER AMOUNT DISTRIBUTION:")
        print("=" * 50)
        
        # Create distribution buckets
        buckets = {
            "42-49.99 ICP": 0,
            "50-99.99 ICP": 0,
            "100-499.99 ICP": 0,
            "500-999.99 ICP": 0,
            "1000+ ICP": 0
        }
        
        for amount in transfer_amounts:
            if 42 <= amount < 50:
                buckets["42-49.99 ICP"] += 1
            elif 50 <= amount < 100:
                buckets["50-99.99 ICP"] += 1
            elif 100 <= amount < 500:
                buckets["100-499.99 ICP"] += 1
            elif 500 <= amount < 1000:
                buckets["500-999.99 ICP"] += 1
            else:
                buckets["1000+ ICP"] += 1
        
        for bucket, count in buckets.items():
            if count > 0:
                percentage = (count / len(transfer_amounts)) * 100
                print(f"  {bucket}: {count} transfers ({percentage:.1f}%)")
        
        # Analyze destination addresses
        print(f"\n🎯 DESTINATION ADDRESS ANALYSIS:")
        print("=" * 50)
        
        destination_stats = defaultdict(lambda: {"count": 0, "total_amount": 0.0, "accounts": set()})
        
        for account in accounts_with_large_transfers:
            for transfer in account['transfers']:
                dest = transfer['destination_address']
                destination_stats[dest]["count"] += 1
                destination_stats[dest]["total_amount"] += transfer['amount']
                destination_stats[dest]["accounts"].add(account['principal_short'])
        
        # Sort by total amount
        sorted_destinations = sorted(destination_stats.items(), 
                                   key=lambda x: x[1]["total_amount"], reverse=True)
        
        print(f"  Found {len(sorted_destinations)} unique destination addresses:")
        print()
        
        for i, (dest, stats_data) in enumerate(sorted_destinations[:10], 1):  # Top 10
            print(f"  [{i}] {dest}")
            print(f"      Transfers: {stats_data['count']}")
            print(f"      Total amount: {stats_data['total_amount']:.8f} ICP")
            print(f"      From {len(stats_data['accounts'])} different accounts")
            if len(stats_data['accounts']) > 1:
                print(f"      Accounts: {', '.join(sorted(stats_data['accounts']))}")
            print()
    
    else:
        print(f"\n❌ No accounts found with outgoing transfers >= 42 ICP")
    
    # Save detailed results
    output_file = Path("funnai_accounts/large_transfer_analysis.json")
    output_data = {
        "analysis_timestamp": "2025-08-04",
        "criteria": "outgoing_transfer >= 42 ICP",
        "statistics": stats,
        "accounts_with_large_transfers": accounts_with_large_transfers
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Create max_topups.json for the gamestate ICP account
    gamestate_icp_account = "300d6f0058417bb5131c7313a3fe7f7b90510ca2f413ab863d39b1e35eceebad"
    
    # Find the destination data for the gamestate account
    gamestate_destination_data = None
    for dest_addr, dest_data in sorted_destinations:
        if dest_addr == gamestate_icp_account:
            gamestate_destination_data = dest_data
            break
    
    if gamestate_destination_data:
        
        max_topups_data = {
            "analysis_timestamp": "2025-08-04",
            "gamestate_icp_account": gamestate_icp_account,
            "total_number_of_max_topups": gamestate_destination_data["count"],
            "total_icp_of_max_topups": gamestate_destination_data["total_amount"],
            "total_number_of_wl_spots": 0,  # Will be calculated below
            "total_number_of_wl_accounts": 0,  # Will be calculated below
            "accounts": {}
        }
        
        # Group transfers by sender account for the gamestate ICP account
        for account in accounts_with_large_transfers:
            account_transfers_to_gamestate = []
            for transfer in account['transfers']:
                if transfer['destination_address'] == gamestate_icp_account:
                    account_transfers_to_gamestate.append({
                        "amount": transfer['amount'],
                        "timestamp": transfer['timestamp'],
                        "date": transfer['date'],
                        "transaction_id": transfer['transaction_id'],
                        "fee_icp": transfer['fee_icp'],
                        "before_cutoff": transfer['before_cutoff']
                    })
            
            if account_transfers_to_gamestate:
                number_of_max_topups = len(account_transfers_to_gamestate)
                max_topups_data["accounts"][account['principal']] = {
                    "principal_short": account['principal_short'],
                    "number_of_max_topups": number_of_max_topups,
                    "number_of_wl_spots": min(number_of_max_topups, 3),
                    "total_icp_of_max_topups": sum(t["amount"] for t in account_transfers_to_gamestate),
                    "transfers": account_transfers_to_gamestate
                }
        
        # Calculate total whitelist spots and accounts
        max_topups_data["total_number_of_wl_spots"] = sum(
            account_data["number_of_wl_spots"] 
            for account_data in max_topups_data["accounts"].values()
        )
        max_topups_data["total_number_of_wl_accounts"] = len(max_topups_data["accounts"])
        
        max_topups_file = Path("funnai_accounts/max_topups.json")
        with open(max_topups_file, 'w') as f:
            json.dump(max_topups_data, f, indent=2)
        
        print(f"\n💾 Max topups analysis saved to: {max_topups_file}")
        print(f"    Gamestate ICP account: {gamestate_icp_account}")
        print(f"    Accounts sending to this address: {len(max_topups_data['accounts'])}")
        print(f"    Total transfers: {max_topups_data['total_number_of_max_topups']}")
        print(f"    Total amount: {max_topups_data['total_icp_of_max_topups']:.8f} ICP")
        print(f"    Total whitelist accounts: {max_topups_data['total_number_of_wl_accounts']}")
        print(f"    Total whitelist spots: {max_topups_data['total_number_of_wl_spots']}")
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    analyze_large_outgoing_transfers()
