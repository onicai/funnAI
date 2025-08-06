import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def analyze_whitelist_criteria():
    """
    Analyze all funnai accounts to find accounts with no mainers and more than 10 ICP balance.
    
    Target criteria:
    - 0 mAIners (mainer_analysis.mainer_count == 0)
    - More than 10 ICP maximum balance (max balance_icp from balance_history > 10)
    """
    print("=== Finding Accounts with 0 Mainers and >10 ICP Balance ===")
    
    # Path to the analysis files directory
    analysis_dir = Path("funnai_accounts")
    
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory {analysis_dir} not found!")
        return
    
    # Get all analysis files
    analysis_files = list(analysis_dir.glob("whitelist_analysis_*.json"))
    print(f"Found {len(analysis_files)} analysis files to process")
    
    # Initialize results storage
    qualifying_accounts = []
    
    # Initialize counters for statistics
    stats = {
        "total_accounts": 0,
        "accounts_with_no_mainers": 0,
        "accounts_with_10plus_icp": 0,
        "qualifying_accounts": 0,
        "current_balance_over_10": 0
    }
    
    processed_count = 0
    
    for file_path in analysis_files:
        try:
            # Read the analysis file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            principal = data.get('principal', '')
            balance_history = data.get('balance_history', [])
            mainer_analysis = data.get('mainer_analysis', {})
            
            # Extract key metrics
            mainer_count = mainer_analysis.get('mainer_count', 0)
            
            # Find maximum balance from balance_history and related dates
            max_balance_icp = 0.0
            max_balance_icp_date = None
            first_balance_icp_over_10_date = None
            current_icp_balance = 0.0
            
            if balance_history:
                # Sort balance history by timestamp to process chronologically
                sorted_history = sorted(balance_history, key=lambda x: x.get('timestamp', ''))
                
                # Find maximum balance and its date
                max_entry = max(balance_history, key=lambda x: x.get('balance_icp', 0.0))
                max_balance_icp = max_entry.get('balance_icp', 0.0)
                max_balance_icp_date = max_entry.get('timestamp', None)
                
                # Get current balance (most recent entry)
                if sorted_history:
                    current_icp_balance = sorted_history[-1].get('balance_icp', 0.0)
                
                # Find first time balance exceeded 10 ICP
                for entry in sorted_history:
                    balance = entry.get('balance_icp', 0.0)
                    if balance > 10.0:
                        first_balance_icp_over_10_date = entry.get('timestamp', None)
                        break
            
            # Update statistics
            stats["total_accounts"] += 1
            
            if mainer_count == 0:
                stats["accounts_with_no_mainers"] += 1
            
            if max_balance_icp > 10.0:
                stats["accounts_with_10plus_icp"] += 1
            
            # Check if account meets our criteria
            if mainer_count == 0 and max_balance_icp > 10.0:
                stats["qualifying_accounts"] += 1
                
                # Check if current balance is still over 10 ICP
                if current_icp_balance > 10.0:
                    stats["current_balance_over_10"] += 1
                
                # Create account summary
                account_info = {
                    "principal": principal,
                    "principal_short": principal[:8] + "..." if len(principal) > 8 else principal,
                    "mainer_count": mainer_count,
                    "max_balance_icp": max_balance_icp,
                    "max_balance_icp_date": max_balance_icp_date,
                    "first_balance_icp_over_10_date": first_balance_icp_over_10_date,
                    "current_icp_balance": current_icp_balance,
                    "balance_history_entries": len(balance_history)
                }
                
                qualifying_accounts.append(account_info)
            
            processed_count += 1
            
            # Progress indicator
            if processed_count % 100 == 0:
                print(f"📊 Progress: {processed_count}/{len(analysis_files)} files processed...")
                
        except Exception as e:
            print(f"ERROR processing {file_path.name}: {e}")
            continue
    
    # Print results
    print("\n" + "="*80)
    print("🎉 ANALYSIS COMPLETE!")
    print("="*80)
    
    print("\n📊 OVERALL STATISTICS:")
    print(f"  Total accounts processed: {stats['total_accounts']}")
    print(f"  Accounts with 0 mAIners: {stats['accounts_with_no_mainers']}")
    print(f"  Accounts with >10 ICP balance: {stats['accounts_with_10plus_icp']}")
    print(f"  Accounts meeting BOTH criteria: {stats['qualifying_accounts']}")
    print(f"  Qualifying accounts with current balance >10 ICP: {stats['current_balance_over_10']}")
    print(f"  Qualifying accounts with current balance ≤10 ICP: {stats['qualifying_accounts'] - stats['current_balance_over_10']}")
    
    print("\n🎯 QUALIFYING ACCOUNTS (0 mAIners + >10 ICP):")
    print("=" * 50)
    
    if not qualifying_accounts:
        print("  No accounts found matching the criteria.")
    else:
        # Sort by first time balance exceeded 10 ICP (earliest first)
        qualifying_accounts.sort(key=lambda x: x['first_balance_icp_over_10_date'] or '9999-12-31')
        
        print(f"  Found {len(qualifying_accounts)} qualifying accounts:")
        print()
        
        # Print column headers
        print(f"  {'#':>3} | {'Principal ID':<65} | {'Max Balance':>12} | {'Current Balance':>15} | {'First >10 Date':<12}")
        print(f"  {'-'*3}-+-{'-'*65}-+-{'-'*12}-+-{'-'*15}-+-{'-'*12}")
        
        for i, account in enumerate(qualifying_accounts, 1):
            current_status = "✅" if account['current_icp_balance'] > 10.0 else "❌"
            print(f"  {i:3d} | {account['principal']:<65} | "
                  f"{account['max_balance_icp']:>8.4f} ICP | "
                  f"{account['current_icp_balance']:>8.4f} ICP {current_status} | "
                  f"{account['first_balance_icp_over_10_date'][:10] if account['first_balance_icp_over_10_date'] else 'N/A':<12}")
        
        print(f"\n📋 SUMMARY:")
        print(f"  • Total qualifying accounts: {len(qualifying_accounts)}")
        print(f"  • Accounts with current balance >10 ICP: {stats['current_balance_over_10']}")
        print(f"  • Accounts with current balance ≤10 ICP: {len(qualifying_accounts) - stats['current_balance_over_10']}")
        print(f"  • Highest max balance: {max(acc['max_balance_icp'] for acc in qualifying_accounts):.4f} ICP")
        print(f"  • Lowest max balance: {min(acc['max_balance_icp'] for acc in qualifying_accounts):.4f} ICP")
        print(f"  • Average max balance: {sum(acc['max_balance_icp'] for acc in qualifying_accounts) / len(qualifying_accounts):.4f} ICP")
        print(f"  • Average current balance: {sum(acc['current_icp_balance'] for acc in qualifying_accounts) / len(qualifying_accounts):.4f} ICP")
        
        # Export to file
        output_file = "qualifying_accounts_0_mainers_10plus_icp.json"
        with open(output_file, 'w') as f:
            json.dump({
                "criteria": "0 mAIners and >10 ICP maximum balance",
                "timestamp": "2025-08-05",
                "total_qualifying": len(qualifying_accounts),
                "accounts": qualifying_accounts
            }, f, indent=2)
        
        print(f"\n💾 Results exported to: {output_file}")
    
    return qualifying_accounts

if __name__ == "__main__":
    analyze_whitelist_criteria()
