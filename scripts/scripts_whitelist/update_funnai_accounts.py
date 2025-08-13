import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from funnai import get_funnai_principals

def update_funnai_accounts():
    """
    Pull fresh data from the funnai_backend canister and update funnai_accounts.json
    """
    print("=== Updating FunnAI Accounts Data ===")
    
    try:
        # Get all principals from the backend
        print("Fetching all FunnAI principals from backend canister...")
        principals = get_funnai_principals()
        
        print(f"Retrieved {len(principals)} principals from backend")
        
        # Create the output data structure
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_accounts": len(principals),
            "source": "funnai_backend canister getUsersAdmin",
            "network": "ic (mainnet)",
            "accounts": principals
        }
        
        # Save to funnai_accounts folder
        output_dir = Path("funnai_accounts")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "funnai_accounts.json"
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Successfully updated {output_file}")
        print(f"   Total accounts: {len(principals)}")
        print(f"   Timestamp: {output_data['timestamp']}")
        
        # Show first few accounts as verification
        if len(principals) > 0:
            print(f"\n📋 Sample accounts (first 5):")
            for i, principal in enumerate(principals[:5]):
                print(f"  {i+1}. {principal}")
            
            if len(principals) > 5:
                print(f"  ... and {len(principals) - 5} more")
        
    except Exception as e:
        print(f"❌ Error updating funnai accounts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_funnai_accounts()
