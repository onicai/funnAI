#!/usr/bin/env python3

import sys
import subprocess
import time
import argparse
import os
from collections import defaultdict
from dotenv import dotenv_values

from .monitor_common import get_canisters, ensure_log_dir

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def topup(canister_id, network, tc):
    """Send cycles to a canister from the funnAI cycles wallet.

    icp-cli has no `dfx wallet` equivalent -- no wallet concept at all -- so this calls
    the wallet canister's own `wallet_send` endpoint. Behaviour and funds are unchanged.
    Refused against mainnet unless ICP_ALLOW_MAINNET_WRITES=1.
    """
    try:
        print(f"Topup with {tc} T Cycles for canister {canister_id} on network {network}...")
        cycles = int(tc) * 1000000000000  # 1 T Cycle = 10^12 Cycles
        icp_helpers.wallet_send(canister_id, cycles, env=network)
    except icp_helpers.MainnetWriteBlocked:
        raise
    except Exception:
        print(f"ERROR: Unable to topup with {tc} T Cycles for canister {canister_id} on network {network}")

def main(network, canister_types, tc):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, canister_types)

    for name, canister_id in CANISTERS.items():
        print("-------------------------------")
        print(f"Canister {name} ({canister_id})")
        topup(canister_id, network, tc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-types",
        choices=["all", "protocol", "mainers"],
        default="protocol",
        help="Specify the canister type (default: protocol)",
    )
    parser.add_argument(
        "--tc",
        default=2,
        help="Specify the amount of T Cycles to add (default: 2)",
    )
    args = parser.parse_args()
    main(args.network, args.canister_types, args.tc)
