import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

def analyze_whitelist_criteria():
    """
    Analyze all funnai accounts against whitelist criteria.
    
    Criteria (mutually exclusive - accounts assigned to highest qualifying tier):
    - 0a: 0 mAIners + 10-19.99 ICP max balance
    - 0b: 0 mAIners + 20+ ICP max balance
    - 1b: 1 mAIner + 20-39.99 ICP max balance  
    - 1c: 1 mAIner + 40+ ICP max balance
    """
    print("=== Whitelist 2 Stealth - Criteria Analysis ===")
    
    # Path to the analysis files directory
    analysis_dir = Path("funnai_accounts")
    
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory {analysis_dir} not found!")
        return
    
    # Get all analysis files
    analysis_files = list(analysis_dir.glob("whitelist_analysis_*.json"))
    print(f"Found {len(analysis_files)} analysis files to process")
    
    # Initialize counters
    criteria_counts = {
        "0a": {"count": 0, "accounts": []},  # 0 mAIners + 10+ ICP
        "0b": {"count": 0, "accounts": []},  # 0 mAIners + 20+ ICP
        "1b": {"count": 0, "accounts": []},  # 1 mAIner + 20+ ICP
        "1c": {"count": 0, "accounts": []},  # 1 mAIner + 40+ ICP
    }
    
    # Track statistics
    stats = {
        "total_accounts": 0,
        "accounts_with_mainers": 0,
        "accounts_with_icp_history": 0,
        "mainer_distribution": defaultdict(int),
        "max_balance_distribution": defaultdict(int)
    }
    
    processed_count = 0
    
    for file_path in analysis_files:
        try:
            # Read the analysis file
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            principal = data.get('principal', '')
            analysis = data.get('analysis', {})
            mainer_analysis = data.get('mainer_analysis', {})
            
            # Extract key metrics
            mainer_count = mainer_analysis.get('mainer_count', 0)
            max_balance = analysis.get('max_balance', 0.0)
            
            # Update statistics
            stats["total_accounts"] += 1
            if mainer_count > 0:
                stats["accounts_with_mainers"] += 1
            if max_balance > 0:
                stats["accounts_with_icp_history"] += 1
            
            stats["mainer_distribution"][mainer_count] += 1
            
            # Categorize max balance for distribution analysis
            if max_balance >= 100:
                balance_category = "100+"
            elif max_balance >= 50:
                balance_category = "50-99"
            elif max_balance >= 20:
                balance_category = "20-49"
            elif max_balance >= 10:
                balance_category = "10-19"
            elif max_balance >= 5:
                balance_category = "5-9"
            elif max_balance > 0:
                balance_category = "0-4"
            else:
                balance_category = "0"
            stats["max_balance_distribution"][balance_category] += 1
            
            # Create account summary for detailed analysis
            account_info = {
                "principal": principal[:8] + "...",
                "full_principal": principal,
                "mainer_count": mainer_count,
                "max_balance": max_balance,
                "current_balance": analysis.get('current_balance', 0.0),
                "total_transactions": analysis.get('total_transactions', 0)
            }
            
            # Check whitelist criteria - assign to HIGHEST qualifying criteria only
            if mainer_count == 0:
                if max_balance >= 20.0:  # Check higher threshold first
                    criteria_counts["0b"]["count"] += 1
                    criteria_counts["0b"]["accounts"].append(account_info)
                elif max_balance >= 10.0:  # Only if doesn't qualify for 0b
                    criteria_counts["0a"]["count"] += 1
                    criteria_counts["0a"]["accounts"].append(account_info)
            
            elif mainer_count == 1:
                if max_balance >= 40.0:  # Check higher threshold first
                    criteria_counts["1c"]["count"] += 1
                    criteria_counts["1c"]["accounts"].append(account_info)
                elif max_balance >= 20.0:  # Only if doesn't qualify for 1c
                    criteria_counts["1b"]["count"] += 1
                    criteria_counts["1b"]["accounts"].append(account_info)
            
            processed_count += 1
            
            # Progress indicator
            if processed_count % 100 == 0:
                print(f"📊 Progress: {processed_count}/{len(analysis_files)} files processed...")
                
        except Exception as e:
            print(f"ERROR processing {file_path.name}: {e}")
            continue
    
    # Print results
    print("\n" + "="*80)
    print("🎉 WHITELIST CRITERIA ANALYSIS COMPLETE!")
    print("="*80)
    
    print("\n📊 OVERALL STATISTICS:")
    print(f"  Total accounts processed: {stats['total_accounts']}")
    print(f"  Accounts with mAIners: {stats['accounts_with_mainers']}")
    print(f"  Accounts with ICP history: {stats['accounts_with_icp_history']}")
    
    print("\n🔢 MAINER DISTRIBUTION:")
    for mainer_count in sorted(stats["mainer_distribution"].keys()):
        count = stats["mainer_distribution"][mainer_count]
        percentage = (count / stats["total_accounts"]) * 100
        print(f"  {mainer_count} mAIners: {count} accounts ({percentage:.1f}%)")
    
    print("\n💰 MAX BALANCE DISTRIBUTION:")
    balance_order = ["0", "0-4", "5-9", "10-19", "20-49", "50-99", "100+"]
    for balance_cat in balance_order:
        if balance_cat in stats["max_balance_distribution"]:
            count = stats["max_balance_distribution"][balance_cat]
            percentage = (count / stats["total_accounts"]) * 100
            print(f"  {balance_cat} ICP: {count} accounts ({percentage:.1f}%)")
    
    print("\n🎯 WHITELIST CRITERIA RESULTS:")
    print("=" * 50)
    
    total_eligible = 0
    for criteria_id in ["0a", "0b", "1b", "1c"]:
        count = criteria_counts[criteria_id]["count"]
        total_eligible += count
        
        # Decode criteria
        mainers = criteria_id[0]
        if criteria_id == "0a":
            icp_threshold = "10-19.99"
        elif criteria_id == "0b":
            icp_threshold = "20+"
        elif criteria_id == "1b":
            icp_threshold = "20-39.99"
        else:  # 1c
            icp_threshold = "40+"
        
        print(f"  {criteria_id}: {mainers} mAIners + {icp_threshold} ICP = {count} accounts")
    
    # Check overlap between criteria groups
    print(f"\n🔍 CRITERIA GROUP OVERLAP ANALYSIS:")
    print("=" * 50)
    
    # Compare accounts across criteria
    accounts_0a = set(acc["full_principal"] for acc in criteria_counts["0a"]["accounts"])
    accounts_0b = set(acc["full_principal"] for acc in criteria_counts["0b"]["accounts"])
    accounts_1b = set(acc["full_principal"] for acc in criteria_counts["1b"]["accounts"])
    accounts_1c = set(acc["full_principal"] for acc in criteria_counts["1c"]["accounts"])
    
    overlap_0a_0b = accounts_0a.intersection(accounts_0b)
    overlap_1b_1c = accounts_1b.intersection(accounts_1c)
    overlap_0b_1b = accounts_0b.intersection(accounts_1b)
    
    print(f"  0a (0 mAIners + 10-19.99 ICP): {len(accounts_0a)} accounts")
    print(f"  0b (0 mAIners + 20+ ICP): {len(accounts_0b)} accounts")
    print(f"  1b (1 mAIner + 20-39.99 ICP): {len(accounts_1b)} accounts")
    print(f"  1c (1 mAIner + 40+ ICP): {len(accounts_1c)} accounts")
    print(f"  ")
    print(f"  Overlap 0a ∩ 0b: {len(overlap_0a_0b)} accounts (should be 0 - mutually exclusive)")
    print(f"  Overlap 1b ∩ 1c: {len(overlap_1b_1c)} accounts (should be 0 - mutually exclusive)")
    print(f"  Overlap 0b ∩ 1b: {len(overlap_0b_1b)} accounts (should be 0 - different mAIner counts)")
    
    # Verify mutual exclusivity
    if len(overlap_0a_0b) == 0:
        print(f"  ✅ 0a and 0b are MUTUALLY EXCLUSIVE (no overlapping accounts)")
    else:
        print(f"  ❌ 0a and 0b have {len(overlap_0a_0b)} overlapping accounts - ERROR!")
        
    if len(overlap_1b_1c) == 0:
        print(f"  ✅ 1b and 1c are MUTUALLY EXCLUSIVE (no overlapping accounts)")
    else:
        print(f"  ❌ 1b and 1c have {len(overlap_1b_1c)} overlapping accounts - ERROR!")

    print(f"\n📋 SUMMARY FOR WHITELIST DECISION:")
    print(f"  Target whitelist spots: 50-100")
    print(f"  Criteria 0a (0 mAIners + 10-19.99 ICP): {criteria_counts['0a']['count']} accounts")
    print(f"  Criteria 0b (0 mAIners + 20+ ICP): {criteria_counts['0b']['count']} accounts")
    print(f"  Criteria 1b (1 mAIner + 20-39.99 ICP): {criteria_counts['1b']['count']} accounts")
    print(f"  Criteria 1c (1 mAIner + 40+ ICP): {criteria_counts['1c']['count']} accounts")
    print(f"  Combined 0b + 1b: {criteria_counts['0b']['count'] + criteria_counts['1b']['count']} accounts")
    print(f"  Combined 0b + 1c: {criteria_counts['0b']['count'] + criteria_counts['1c']['count']} accounts")
    print(f"  Combined all (0a + 0b + 1b + 1c): {criteria_counts['0a']['count'] + criteria_counts['0b']['count'] + criteria_counts['1b']['count'] + criteria_counts['1c']['count']} accounts")

if __name__ == "__main__":
    analyze_whitelist_criteria()
