"""
Whitelist 2 Stealth Script
Determines whitelist candidates by querying the funnai_backend canister and analyzing ICP transaction history.
"""

import json
import subprocess
import sys
import pprint
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from .icp import get_icp_balance, get_icp_transactions, calculate_historical_balance
from .funnai import get_funnai_principals


def main():
    """Main function to determine whitelist candidates."""
    print("=== Whitelist 2 Stealth - Historical Balance Analysis ===")

    # Get all FunnAI principals
    print("Loading FunnAI principals...")
    funnai_principals = get_funnai_principals()
    print(f"Found {len(funnai_principals)} FunnAI accounts to analyze")
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent / "funnai_accounts"
    output_dir.mkdir(exist_ok=True)
    
    # Statistics tracking
    total_accounts = len(funnai_principals)
    processed_accounts = 0
    successful_analyses = 0
    failed_analyses = 0
    tier_counts = {
        "tier_1_high_priority": 0,
        "tier_2_medium_priority": 0, 
        "tier_3_low_priority": 0,
        "tier_4_very_low_priority": 0,
        "excluded": 0
    }
    
    print(f"\nStarting analysis of {total_accounts} accounts...")
    print("=" * 80)
    
    for i, principal in enumerate(funnai_principals, 1):
        print(f"\n[{i}/{total_accounts}] Analyzing: {principal}")
        processed_accounts += 1
        
        try:
            # Get ICP transaction data
            print(f"  Fetching ICP transactions...")
            icp_transactions = get_icp_transactions(principal, max_results=1000)
            
            current_balance = int(icp_transactions.get('balance', '0')) / 100_000_000
            num_transactions = len(icp_transactions.get('transactions', []))
            
            print(f"  Current balance: {current_balance:.8f} ICP")
            print(f"  Transactions: {num_transactions}")
            
            # Calculate historical balance
            print(f"  Calculating historical balance...")
            balance_history = calculate_historical_balance(principal, icp_transactions)
            
            # Save detailed results to JSON
            output_data = {
                "principal": principal,
                "balance_history": balance_history,
                "raw_transaction_data": icp_transactions,
                "timestamp": datetime.now().isoformat()
            }
            
            output_file = output_dir / f"whitelist_analysis_{principal[:8]}.json"
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            successful_analyses += 1
            
            # Add delays to be respectful to the network
            if i % 10 == 0:
                print(f"\n  📊 Progress: {i}/{total_accounts} ({i/total_accounts*100:.1f}%) - Sleeping 5 seconds...")
                import time
                time.sleep(5)
            elif i % 5 == 0:
                print(f"  💤 Mini break (2 seconds)...")
                import time
                time.sleep(2)
            else:
                import time
                time.sleep(1)  # Small delay between requests
        
        except Exception as e:
            print(f"  ❌ Error analyzing {principal}: {e}")
            failed_analyses += 1
            
            # Save error information
            error_data = {
                "principal": principal,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
            
            output_file = output_dir / f"whitelist_analysis_{principal[:8]}.json"
            with open(output_file, 'w') as f:
                json.dump(error_data, f, indent=2)
            
            continue
    
    # Final summary
    print("\n" + "=" * 80)
    print(f"🎉 ANALYSIS COMPLETE!")
    print(f"📊 FINAL STATISTICS:")
    print(f"  Total accounts: {total_accounts}")
    print(f"  Successfully analyzed: {successful_analyses}")
    print(f"  Failed analyses: {failed_analyses}")
    print(f"  Success rate: {successful_analyses/total_accounts*100:.1f}%")
    
    print(f"\n📁 Results saved to: {output_dir}")
    print(f"   Individual analysis files: {successful_analyses + failed_analyses} JSON files")
    
if __name__ == "__main__":
    main()