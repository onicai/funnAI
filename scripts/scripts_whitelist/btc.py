#!/usr/bin/env python3
"""
Find every transaction that spends from `source_addr` to `dest_addr`
using the mempool.space API.
"""

import requests
import time
from typing import List, Dict

BASE_URL = "https://mempool.space/api"          # mainnet
# For testnet/signet, change to e.g.  "https://mempool.space/testnet/api"

DEST_ADDR   = "bc1q2qwyms5ptyjq7mn09ap79u96fhmkpdjt0c8wve"      # the funnai_btc_address we’re scanning
SOURCE_ADDR = "bc1qmzhm50tgwl7k30xlnrtyffvph283y4zvx0q472"      # the bioniq_btc_address we expect in *inputs*

PAGE_SIZE = 25      # mempool.space returns 25 txs per page


def fetch_address_txs(address: str) -> List[Dict]:
    """
    Fetch **all confirmed** transactions touching `address`, handling pagination.

    Returns a list of raw tx JSON objects in **block-ascending** order
    (earliest to latest).  Each object follows Bitcoin Core’s REST format.
    """
    txs: List[Dict] = []
    last_seen = None

    while True:
        # The first call has no paging param; subsequent calls append `last_seen_txid`
        endpoint = f"{BASE_URL}/address/{address}/txs/chain"
        if last_seen:
            endpoint = f"{endpoint}/{last_seen}"

        resp = requests.get(endpoint, timeout=15)
        resp.raise_for_status()

        page = resp.json()
        if not page:                       # no more pages
            break

        txs.extend(page)
        last_seen = page[-1]["txid"]       # mempool.space uses the last txid as cursor

        if len(page) < PAGE_SIZE:
            break                          # final partial page reached

        time.sleep(1)                      # be polite – 1 request / sec
    # mempool.space gives newest→oldest; we want oldest→newest for later logic
    return list(reversed(txs))


def is_from_addr(vin: Dict, addr: str) -> bool:
    """
    True iff this input spends a UTXO whose **prevout** belongs to `addr`.
    """
    prev = vin.get("prevout", {})
    return prev.get("scriptpubkey_address") == addr


def tx_matches(tx: Dict, src_addr: str, dst_addr: str) -> bool:
    """
    Return True when *any* input comes from `src_addr` **and**
    *any* output pays to `dst_addr`.
    """
    inputs_ok  = any(is_from_addr(vin, src_addr) for vin in tx["vin"])
    outputs_ok = any(vout.get("scriptpubkey_address") == dst_addr
                     for vout in tx["vout"])
    return inputs_ok and outputs_ok


def main() -> None:
    print(f"Fetching transactions for {DEST_ADDR} …")
    all_txs = fetch_address_txs(DEST_ADDR)
    print(f"  ↳ {len(all_txs)} confirmed transactions found.")

    matches = [tx for tx in all_txs if tx_matches(tx, SOURCE_ADDR, DEST_ADDR)]
    print(f"\nTransactions sending **from {SOURCE_ADDR} → {DEST_ADDR}**:")
    if not matches:
        print("  (none found)")
        return

    for tx in matches:
        txid   = tx["txid"]
        height = tx["status"]["block_height"]
        time_s = tx["status"]["block_time"]
        print(f"• {txid}  (block {height}, unix-time {time_s})")


if __name__ == "__main__":
    main()
