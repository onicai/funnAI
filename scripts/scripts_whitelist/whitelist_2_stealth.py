"""
Whitelist 2 Stealth Script
Determines whitelist candidates by querying the funnai_backend canister.
"""

import json
import subprocess
import sys
import pprint
from pathlib import Path
from typing import Dict, Any
from .icp import get_icp_balance, get_icp_transactions
from .funnai import get_funnai_principals




def main():
    """Main function to determine whitelist candidates."""
    print("=== Whitelist 2 Stealth - Candidate Determination ===")

    funnai_principals = get_funnai_principals()

    for funnai_principal in funnai_principals:
       icp_transactions = get_icp_transactions(funnai_principal, max_results=1000)
       pprint.pprint(f"Principal: {funnai_principal}, Transactions: {icp_transactions}")



if __name__ == "__main__":
    main()