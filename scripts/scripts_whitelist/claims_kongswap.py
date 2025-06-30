import csv, sys

from pathlib import Path
from .ckbtc import check_ckbtc_transaction
from .claims_common import alloc_rule_iconfucius, alloc_rule_iconfucius_lp

def claims_kongswap(claims: list, wl_allocs: dict, total_wl_allocs: dict):
    """
    Main function to process the whitelist claims based on the specified category.
    """
   
    # ------------------------------------------------------------------------------
    # HELPER TO MANUALLY TAKE THE SNAPSHOT FROM KONGSWAP WALLETS - 
    # Print the kongswap principals & URL to their kongswap wallet
    # This is a manual step to take the snapshot of the kongswap wallets
    # print("-------------------------------------------------------")
    # print("funnai_principal: kongswap_principal")
    # count_kongswap = 0
    # for claim in claims:
    #     funnai_principal = claim.get("funnai_principal")
    #     bioniq_ckbtc_address = claim.get("bioniq_ckbtc_address")
    #     bioniq_btc_address = claim.get("bioniq_btc_address")
    #     kongswap_principal = claim.get("kongswap_principal")
    #     if kongswap_principal:
    #         count_kongswap += 1
    #         print(f"{count_kongswap} {funnai_principal}, {kongswap_principal},  -> https://www.kongswap.io/wallets/{kongswap_principal}") 

    # ------------------------------------------------------------------------------
    # Read the kongswap snapshot from file
    kongswap = {}
    csv_path = Path(__file__).parent / "../../secret/whitelist/snapshots/kongswap.csv"
    with open(csv_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = row.get("funnai_principal")
            kongswap[key] = row

    # # calculate the total of iconfucius claimed 
    # total_iconfucius_kongswap_claimed = 0.0
    # for claim in kongswap.values():
    #     amount_str = claim.get("iconfucius", "0").strip()
    #     if amount_str:
    #         try:
    #             total_iconfucius_kongswap_claimed += float(amount_str)
    #         except ValueError:
    #             pass

    # print("-------------------------------------------------------")
    # print(f"Total ICONFUCIUS claimed: {total_iconfucius_kongswap_claimed}")
    # print("-------------------------------------------------------")
    # ------------------------------------------------------------------------------
    # Calculate the total ICONFUCIUS ever transferred via OMNITY
    # From: https://explorer.omnity.network/chain/ICP?tokenId=Bitcoin-runes-ICONFUCIUS%E2%80%A2ID%E2%80%A2RVMN%E2%80%A2ODIN&action=Transfer&page=1

    iconfucius_via_omnity = [
        82000,
        5250,
        20000,
        80070,
        32701.85688528,
        1000,
        1000,
        1000,
        5000,
        3383.67825949,
        # 21000000  # This was the original creation by Odin
    ]
    iconfucius_on_icp_total = sum(iconfucius_via_omnity)
    print("-------------------------------------------------------")
    print(f"Total ICONFUCIUS transferred via OMNITY: {iconfucius_on_icp_total}")
    print("-------------------------------------------------------")

    # ------------------------------------------------------------------------------
    for claim in claims:
        funnai_principal = claim.get("funnai_principal")
        kongswap_principal = claim.get("kongswap_principal")

        if kongswap_principal == '':
            continue

        print(f"-------------------------------------------------------")
        print(f"Processing kongswap claim for {funnai_principal} with kongswap principal {kongswap_principal}")

        # Verify that a ckBTC amount was sent to the funnai principal
        if not check_ckbtc_transaction(kongswap_principal, funnai_principal):
            print(f"NO ckBTC transaction from kongswap '{kongswap_principal} to funnAI {funnai_principal} - SKIPPING")
            continue
        # --------------------------------------------------------------
        if kongswap.get(funnai_principal) is None:
            print(f"ERROR: kongswap principal {kongswap_principal} not found in the snapshot of kongswap wallets")
            print(f"funnai_principal: {funnai_principal}, kongswap_principal: {kongswap_principal}")
            sys.exit(1)
            continue

        ks = kongswap[funnai_principal]

        iconfucius = float(ks.get("iconfucius", "0").strip() or 0)
        iconfucius_share = iconfucius / iconfucius_on_icp_total * 100

        iconfucius_icp_lp_share = float(ks.get("iconfucius_icp_lp_share", "0").strip() or 0)
        iconfucius_ckusdt_lp_share = float(ks.get("iconfucius_ckusdt_lp_share", "0").strip() or 0)

        alloc_iconfucius = alloc_rule_iconfucius(iconfucius_share, cap=5)
        
        alloc_iconfucius_icp_lp = alloc_rule_iconfucius_lp(iconfucius_icp_lp_share, cap=5)
        alloc_iconfucius_ckusdt_lp = alloc_rule_iconfucius_lp(iconfucius_ckusdt_lp_share, cap=5)
        alloc_iconfucius_lp = alloc_iconfucius_icp_lp + alloc_iconfucius_ckusdt_lp

        print(f"KongSwap based WL allocations: {alloc_iconfucius}, {alloc_iconfucius_lp }")

        wl_allocs[funnai_principal]["kongswap"] = alloc_iconfucius
        wl_allocs[funnai_principal]["kongswap_lp"] = alloc_iconfucius_lp    
        wl_allocs[funnai_principal]["total"] += alloc_iconfucius + alloc_iconfucius_lp
        total_wl_allocs["kongswap"] += alloc_iconfucius
        total_wl_allocs["kongswap_lp"] += alloc_iconfucius_lp
        total_wl_allocs["total"] += alloc_iconfucius + alloc_iconfucius_lp