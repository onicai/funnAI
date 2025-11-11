import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from .funnai import get_funnai_principals, get_mainer_ownership_data

def update_funnai_accounts():
    """
    Pull fresh data from the funnai_backend canister and update funnai_accounts.json
    """
    print("=== Updating FunnAI Accounts Data ===")

    # Get the directory where this script is located
    SCRIPT_DIR = Path(__file__).parent

    try:
        # Get all principals from the backend
        print("Fetching all FunnAI principals from backend canister...")
        principals = get_funnai_principals()

        print(f"Retrieved {len(principals)} principals from backend")

        # Get mAIner ownership data from GameState
        print("Fetching mAIner ownership data from GameState canister...")
        mainer_ownership = get_mainer_ownership_data()

        print(f"Retrieved mAIner ownership data for {len(mainer_ownership)} principals")

        # Create enhanced account data with mAIner information
        enhanced_accounts = []
        total_mainers = 0

        for principal in principals:
            mainers = mainer_ownership.get(principal, [])
            total_mainers += len(mainers)

            account_data = {
                "principal": principal,
                "mainer_canisters": mainers,
                "mainer_count": len(mainers)
            }
            enhanced_accounts.append(account_data)

        # Create the output data structure
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_accounts": len(principals),
            "total_mainers": total_mainers,
            "accounts_with_mainers": len([acc for acc in enhanced_accounts if acc["mainer_count"] > 0]),
            "source": {
                "accounts": "funnai_backend canister getUsersAdmin",
                "mainers": "gamestate canister getMainerAgentCanistersAdmin"
            },
            "network": "ic (mainnet)",
            "accounts": enhanced_accounts
        }
        
        # Save to funnai_accounts folder
        output_dir = SCRIPT_DIR / "funnai_accounts"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "funnai_accounts.json"
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Successfully updated {output_file}")
        print(f"   Total accounts: {len(principals)}")
        print(f"   Total mAIners: {total_mainers}")
        print(f"   Accounts with mAIners: {output_data['accounts_with_mainers']}")
        print(f"   Timestamp: {output_data['timestamp']}")

        # Show first few accounts as verification
        if len(enhanced_accounts) > 0:
            print(f"\n📋 Sample accounts (first 5):")
            for i, account in enumerate(enhanced_accounts[:5]):
                mainer_info = f" ({account['mainer_count']} mAIners)" if account['mainer_count'] > 0 else " (no mAIners)"
                print(f"  {i+1}. {account['principal']}{mainer_info}")
                if account['mainer_count'] > 0:
                    for mainer in account['mainer_canisters'][:3]:  # Show first 3 mAIners
                        print(f"      └─ {mainer}")
                    if account['mainer_count'] > 3:
                        print(f"      └─ ... and {account['mainer_count'] - 3} more mAIners")

            if len(enhanced_accounts) > 5:
                print(f"  ... and {len(enhanced_accounts) - 5} more accounts")
        
    except Exception as e:
        print(f"❌ Error updating funnai accounts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_funnai_accounts()
