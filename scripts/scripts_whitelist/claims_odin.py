import json
from pathlib import Path
from .claims_common import alloc_rule_iconfucius, alloc_rule_iconfucius_lp

def claims_odin(claims: list, wl_allocs: dict, total_wl_allocs: dict):
    """
    Main function to process the whitelist claims based on the specified category.
    """

    # ------------------------------------------------------------------------------
    # Read the iconfucius_odin_holders snapshot from file
    json_path = Path(__file__).parent / "snapshots" / "iconfucius_odin_holders.json"
    with open(json_path, "r") as f:
        iconfucius_odin_holders_json = json.load(f)
    iconfucius_odin_holders = iconfucius_odin_holders_json['data']
    total_iconfucius = 21000000 # Total ICONFUCIUS supply is 21M

    # Read the iconfucius_odin_lp snapshot from file
    json_path = Path(__file__).parent / "snapshots" / "iconfucius_odin_lp.json"
    with open(json_path, "r") as f:
        iconfucius_odin_lp_json = json.load(f)
    iconfucius_odin_lp = iconfucius_odin_lp_json['data']
    total_iconfucius_lp = 0
    for lp in iconfucius_odin_lp:
        balance = lp.get('balance', 0)
        if balance:
            total_iconfucius_lp += balance
    print(f"Total lp tokens in iconfucius_odin_lp: {total_iconfucius_lp} ICONFUCIUS")

    # ------------------------------------------------------------------------------
    # PROCESS ODIN CLAIMS
    print(f"-------------------------------------------------------")
    for claim in claims:
        funnai_principal = claim.get("funnai_principal")
        odin_user_id = claim.get("odin_user_id")
        odin_username_block = funnai_principal[:23]
        
        found_odin_holder = False
        iconfucius_share = 0.0 # %
        for odin_holder in iconfucius_odin_holders:
            if odin_username_block in odin_holder['user_username'].lower():
                print(f"Found odin_holder username {odin_holder['user_username']} for {funnai_principal}")
                found_odin_holder = True
                odin_holder_balance = odin_holder.get('balance', 0)
                iconfucius_share = odin_holder_balance / total_iconfucius / 1000000000 # convert to %-age share of total token supply
                break

        found_odin_lp = False
        iconfucius_lp_share = 0.0 # %
        for odin_lp in iconfucius_odin_lp:
            if odin_username_block in odin_lp['user_username'].lower():
                print(f"Found odin_lp username {odin_lp['user_username']} for {funnai_principal}")
                found_odin_lp = True
                odin_lp_balance = odin_lp.get('balance', 0)
                iconfucius_lp_share = odin_lp_balance / total_iconfucius_lp  * 100 # convert to %-age share of total token supply
                break
               
        if not found_odin_holder and not found_odin_lp:
            if odin_user_id != '':
                print(f"ERROR: Could not find an odin username in either odin_holders or odin_lp for {funnai_principal} with odin_user_id {odin_user_id}")
                print(f"funnai_principal: {funnai_principal}, odin_user_id: {odin_user_id}")
                print("SKIPPING -- INVESTIGATE THIS CLAIM MANUALLY")
                print(f"-------------------------------------------------------")
            continue  # No odin holder or lp found, skip this claim


        alloc_iconfucius = alloc_rule_iconfucius(iconfucius_share, cap=15)
        
        alloc_iconfucius_lp = alloc_rule_iconfucius_lp(iconfucius_lp_share, cap=5)

        print(f"Odin based WL allocations: {alloc_iconfucius} ({iconfucius_share:.2f}%), {alloc_iconfucius_lp} ({iconfucius_lp_share:.2f}%))")

        wl_allocs[funnai_principal]["odin"] = alloc_iconfucius
        wl_allocs[funnai_principal]["odin_lp"] = alloc_iconfucius_lp    
        wl_allocs[funnai_principal]["total"] += alloc_iconfucius + alloc_iconfucius_lp
        total_wl_allocs["odin"] += alloc_iconfucius
        total_wl_allocs["odin_lp"] += alloc_iconfucius_lp
        total_wl_allocs["total"] += alloc_iconfucius + alloc_iconfucius_lp
        print(f"-------------------------------------------------------")