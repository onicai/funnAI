import json, csv, sys
import pprint
import argparse

from pathlib import Path
from .icp import get_icp_balance
from time import sleep
from datetime import datetime

def main (token: str):
    """
    Main function to check on WL wallet balances.
    """
    # Read the ../../secret/whitelist/wl_allocs.json from file
    json_path = Path(__file__).parent / "../../secret/whitelist/wl_allocs.json"
    with open(json_path, "r") as f:
        wl_allocs_json = json.load(f)


    total_icp_wl_needed = 0
    total_icp_in_wallets = 0
    count = 0
    total = len(wl_allocs_json)
    for funnai_principal, alloc in wl_allocs_json.items():
       total_icp_wl_needed += alloc.get('total', 0) * 5
       balance = get_icp_balance(funnai_principal)
       total_icp_in_wallets += balance
       alloc['icp_balance'] = balance
       count += 1
    #    print(f"{count:.2f}/{total:.2f} total_icp_wl_needed = {total_icp_wl_needed:.2f}, total_icp_in_wallets = {total_icp_in_wallets:.2f} ({(total_icp_in_wallets/total_icp_wl_needed*100 if total_icp_wl_needed > 0 else 0):.2f}%)")
       # throttle the requests to avoid rate limiting
       sleep(0.5)
        
    print(f"Total ICP needed for WL claims: {total_icp_wl_needed}")
    print(f"Total ICP in funnAI wallets   : {total_icp_in_wallets:.2f} ({(total_icp_in_wallets/total_icp_wl_needed*100 if total_icp_wl_needed > 0 else 0):.2f}%)")

    # append this with a timestamp to a CSV file
    csv_path = Path(__file__).parent / "metrics.csv"
    with open(csv_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # write header if file is empty
        if csvfile.tell() == 0:
            writer.writerow(["timestamp", "total_icp_wl_needed", "total_icp_in_wallets", "percentage"])
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, total_icp_wl_needed, total_icp_in_wallets, (total_icp_in_wallets / total_icp_wl_needed * 100 if total_icp_wl_needed > 0 else 0)])
    
    # export metrics to JSON file
    json_path = Path(__file__).parent / "metrics.json"
    with open(json_path, "w") as jsonfile:
        json.dump(wl_allocs_json, jsonfile, indent=4)
    print(f"Exported metrics to {json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate funnAI metrics.")
    parser.add_argument(
        "--token",
        choices=["all", "icp", "funnai", "ckbtc", "iconfucius"],
        default="icp",
        help="Specify the token to calculate metrics for (default: icp)",
    )
    args = parser.parse_args()
    main(args.token)