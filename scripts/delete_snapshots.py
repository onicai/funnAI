#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json
from collections import defaultdict
from dotenv import dotenv_values

from scripts.cleanup_llm_promptcache import cleanup_llm_promptcache

from .monitor_common import get_canisters, run_this_cmd

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))
    

def delete_snapshots(canister_name, canister_id, network):
    """Delete snapshot_ids for a given canister."""
    try:    
        print(" ")
        print(f"- Get list of snapshot_ids for {canister_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "snapshot", "list", canister_id]
        print(f"  {' '.join(cmd)}")
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        print(result)

        if "No snapshots found" in result:
            print(f"  No snapshots found for {canister_name} ({canister_id}).")
            return
        
        # Parse the result to extract snapshot_id IDs
        snapshot_ids = []
        for line in result.splitlines():
            snapshot_id = line.split(":")[0].strip()
            if snapshot_id:
             snapshot_ids.append(snapshot_id)
        
        print(f"  Found {len(snapshot_ids)} snapshot_ids:")
        for snapshot_id in snapshot_ids:
            print(" ")
            print(f"- Delete snapshot_id {snapshot_id} for {canister_name} ({canister_id})")
            cmd = ["dfx", "canister", "--network", network, "snapshot", "delete", canister_id, snapshot_id]
            run_this_cmd(cmd, FUNNAI_DIR, confirm=False)
    
        print(" ")
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR occured when calling the subprocess command.")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:\n", e.output)

def main(network, canister_id):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    for name, id in CANISTERS.items():
        if canister_id == "all" or canister_id == id:
            print(" ")
            print("=" * 100)
            print(f"Deleting snapshots for canister {name} ({id}) on network '{network}'")
            delete_snapshots(name, id, network)

            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Delete snapshot_ids.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--canister-id",
        default="all",
        help="Specify the canister ID to use",
    )
    args = parser.parse_args()
    main(args.network, args.canister_id)
