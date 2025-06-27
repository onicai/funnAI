import json, csv, sys
import pprint
import argparse

from pathlib import Path
from .claims_kongswap import claims_kongswap
from .claims_odin import claims_odin
from .claims_bioniq import claims_bioniq

def main (category: str):
    """
    Main function to process the whitelist claims based on the specified category.
    """
    # ------------------------------------------------------------------------------
    # Read the claim form responses from file
    claims = []
    csv_path = Path(__file__).parent / "snapshots/claims.csv"
    with open(csv_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            claims.append(row)

    print(f"-------------------------------------------------------")
    print("Merging duplicate claims based on funnai_principal")
    # Merge duplicate claims based on funnai_principal, keeping the first occurrence.
    unique_claims = {}
    for claim in claims:
        principal = claim.get("funnai_principal")
        if principal in unique_claims:
            existing_claim = unique_claims[principal]
            print("-------------------------------------------------------")
            print(f"Duplicate claim for {principal}':")
            print(f"  Existing claim:")
            pprint.pprint(existing_claim)
            print(f"  New claim     : ")
            pprint.pprint(claim)
            for key in claim:
                if key in ['timestamp', 'funnai_principal', 'x_post'] or claim[key] == '':
                    continue
                elif existing_claim.get(key) == '':
                    # If the existing claim has an empty value, replace it with the new claim's value.
                    existing_claim[key] = claim[key]
                elif claim[key] != existing_claim.get(key):
                    print(f"Differing detail in field '{key}':")
                    print(f"  Existing: {existing_claim.get(key)}  (keeping this value )")
                    print(f"  New: {claim[key]}")
            print(f"  Merged claim:")
            pprint.pprint(existing_claim)
        else:
            unique_claims[principal] = claim

    # Replace original claims list with the merged unique claims.
    claims[:] = list(unique_claims.values())
    

    # ---------------------------------------------------------------------------
    # Start with zero WL spots allocated for each category
    
    total_wl_allocs = {
        "icpp_art": 0,
        "charles": 0,
        "odin": 0,
        "odin_lp": 0,
        "kongswap": 0,
        "kongswap_lp": 0,
        "total": 0
    }

    wl_allocs = {}
    for claim in claims:
        funnai_principal = claim.get("funnai_principal")
        wl_allocs[funnai_principal] = {
            "icpp_art": 0,
            "charles": 0,
            "odin": 0,
            "odin_lp": 0,
            "kongswap": 0,
            "kongswap_lp": 0,
            "total": 0
        }

    print("-------------------------------------------------------")
    print("Initialized the wl_allocs dictionary with zero allocations for each funnai_principal")
    pprint.pprint(wl_allocs)

    print(f"Processing claims for category: {category}")
    
    if category == "all" or category == "kongswap":
        claims_kongswap(claims, wl_allocs, total_wl_allocs)
        print("--PROCESSED KONGSWAP CLAIMS--")    
        

    if category == "all" or category == "odin":
        claims_odin(claims, wl_allocs, total_wl_allocs)
    
    if category == "all" or category == "bioniq":
        claims_bioniq(claims, wl_allocs, total_wl_allocs)
    
    # export wl_allocs to JSON file
    json_path = Path(__file__).parent / "wl_allocs.json"
    with open(json_path, "w") as jsonfile:
        json.dump(wl_allocs, jsonfile, indent=4)
    print(f"Exported wl_allocs to {json_path}")
    # export total_wl_allocs to JSON file
    json_path = Path(__file__).parent / "total_wl_allocs.json"
    with open(json_path, "w") as jsonfile:
        json.dump(total_wl_allocs, jsonfile, indent=4)
    print(f"Exported total_wl_allocs to {json_path}")

    # Print the total WL allocations
    pprint.pprint(total_wl_allocs)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Whitelist Claims.")
    parser.add_argument(
        "--category",
        choices=["all", "kongswap", "bioniq", "odin"],
        default="all",
        help="Specify the category to use (default: all)",
    )
    args = parser.parse_args()
    main(args.category)       