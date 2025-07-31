import os
import json
import subprocess
import time
from pathlib import Path

def get_mainers_for_principal(principal, mainers_data):
    """Count how many mAIners a principal owns."""
    count = 0
    mainer_details = []
    
    for mainer in mainers_data:
        # Only count mAIners that have an owner
        owned_by = mainer.get('ownedBy', '')
        if not owned_by:
            continue  # Skip mAIners with no owner
            
        # Only count mAIners that have a non-empty address (as per get_mainers.py logic)
        address = mainer.get('address', '')
        if not address:
            continue  # Skip mAIners with empty address
            
        if owned_by == principal:
            # Skip ShareService canisters as per get_mainers.py logic
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''
            
            if canister_type == "ShareService":
                continue
                
            if canister_type != "ShareAgent":
                continue
                
            count += 1
            mainer_details.append({
                "address": address,  # Use the already retrieved address
                "status": mainer.get('status', {}),
                "subnet": mainer.get('subnet', ''),
                "creationTimestamp": mainer.get('creationTimestamp', '')
            })
    
    return count, mainer_details

def get_all_mainers():
    """Get all mAIners from the game_state_canister.""" 
    print("Fetching mAIners from game_state_canister...")
    try:
        # Change to the funnAI root directory where dfx.json is located
        funnai_root = "/Users/arjaan/github/repos/funnAI"
        result = subprocess.check_output(
            ["dfx", "canister", "--network", "prd", "call", "game_state_canister", "getMainerAgentCanistersAdmin", "--output", "json"],
            cwd=funnai_root,
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        mainers = data.get('Ok', [])
        print(f"Found {len(mainers)} total mAIner entries")
        return mainers
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Unable to get mAIners from game_state_canister: {e}")
        return []

def main():
    print("=== Whitelist 2 Stealth Prep 2 - Adding mAIner Count Analysis ===")
    
    # Get all mAIners data
    mainers_data = get_all_mainers()
    if not mainers_data:
        print("ERROR: Could not fetch mAIners data. Exiting.")
        return
    
    # Path to the analysis files directory
    analysis_dir = Path("funnai_accounts")
    
    if not analysis_dir.exists():
        print(f"ERROR: Analysis directory {analysis_dir} not found!")
        return
    
    # Get all analysis files
    analysis_files = list(analysis_dir.glob("whitelist_analysis_*.json"))
    print(f"Found {len(analysis_files)} analysis files to update")
    
    updated_count = 0
    total_mainers_found = 0
    
    for file_path in analysis_files:
        try:
            # Read the existing analysis file
            with open(file_path, 'r') as f:
                analysis_data = json.load(f)
            
            principal = analysis_data.get('principal')
            if not principal:
                print(f"WARNING: No principal found in {file_path.name}")
                continue
            
            # Get mAIner count for this principal
            mainer_count, mainer_details = get_mainers_for_principal(principal, mainers_data)
            
            # Add mAIner information to the analysis
            analysis_data['mainer_analysis'] = {
                "mainer_count": mainer_count,
                "mainer_details": mainer_details,
                "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            # Write the updated analysis back to the file
            with open(file_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            if mainer_count > 0:
                print(f"✅ {file_path.name}: {mainer_count} mAIners found for {principal[:8]}...")
                total_mainers_found += mainer_count
            else:
                print(f"   {file_path.name}: 0 mAIners for {principal[:8]}...")
            
            updated_count += 1
            
            # Small delay to be respectful
            if updated_count % 50 == 0:
                print(f"📊 Progress: {updated_count}/{len(analysis_files)} files updated...")
                time.sleep(1)
            
        except Exception as e:
            print(f"ERROR processing {file_path.name}: {e}")
            continue
    
    print("\n" + "="*80)
    print("🎉 MAINER ANALYSIS COMPLETE!")
    print(f"📊 FINAL STATISTICS:")
    print(f"  Files processed: {updated_count}/{len(analysis_files)}")
    print(f"  Total mAIners found: {total_mainers_found}")
    print(f"  Average mAIners per account: {total_mainers_found/updated_count:.2f}")
    print("="*80)

if __name__ == "__main__":
    main()
