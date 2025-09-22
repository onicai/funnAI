#!/usr/bin/env python3

import subprocess
import time
import argparse
import os
import sys
from collections import defaultdict
from dotenv import dotenv_values
import json
import pandas as pd

from .monitor_common import get_canisters, ensure_log_dir, get_balance
from .ledgers.icp import get_usd_per_computed_xdr_from_cmc, icp_xdr_summary, get_cycle_burn_rate_from_ic_api

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# The current value of 1 trillion cycles in USD, as computed by the CMC canister
CMC_USD_PER_COMPUTED_XDR = get_usd_per_computed_xdr_from_cmc()

# The cycle burn rate from the IC API, in cycles/second
IC_API_CYCLE_BURN_RATE = get_cycle_burn_rate_from_ic_api()
IC_API_TCYCLE_BURN_RATE_PER_DAY = IC_API_CYCLE_BURN_RATE * 60 * 60 * 24 / 1_000_000_000_000  # Tcycles/day

# Keep these values in sync with the backend (Game State: mAIner Burn Rates)
DAILY_BURN_RATE_LOW = 1
DAILY_BURN_RATE_MEDIUM = 2
DAILY_BURN_RATE_HIGH = 4
DAILY_BURN_RATE_VERY_HIGH = 6

def get_mainers(network):
    """Get mainers from gamestate using dfx."""
    try:    
        print(f"Getting all mAIners from the game_state_canister on network {network}...")
        result = subprocess.check_output(
            ["dfx", "canister", "--network", network, "call", "game_state_canister", "getMainerAgentCanistersAdmin", "--output", "json"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        data = json.loads(result)
        mainers = data.get('Ok', [])
        return mainers
    except subprocess.CalledProcessError:
        print(f"ERROR: Unable to get mAiners from game_state_canister on network {network}")

def get_mainers_for_user(network, user):
    """Get mainers for a specific user from gamestate."""
    mainers = get_mainers(network)
    if not mainers:
        return []
    
    return [mainer for mainer in mainers if (mainer.get('address','') != '' and mainer.get('ownedBy', '') == user)]

def main(network, user):
    print("----------------------------------------------")
    
    # Get mainers based on user parameter
    if user == "all" or user is None:
        mainers = get_mainers(network)
        env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}.env")
    else:
        mainers = get_mainers_for_user(network, user)
        if not mainers:
            print(f"No mainers found for user '{user}' on network '{network}'")
            return
        print(f"Found {len(mainers)} mainers for user '{user}' on network '{network}'")
        for mainer in mainers:
            address = mainer.get('address', 'N/A')
            # Get mAIner burn rate setting
            try:
                cmd = ["dfx", "canister", "call", address, "getMainerStatisticsAdmin", "--network", network, "--output", "json"]
                output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                data = json.loads(output)
                cycles_burn_rate = data.get('Ok', {}).get('cyclesBurnRate', {}).get('cycles', None)

                # Map cycles burn rate to human-readable setting
                setting = "Unknown"
                if cycles_burn_rate == "1_000_000_000_000":
                    setting = "Low"
                elif cycles_burn_rate == "2_000_000_000_000":
                    setting = "Medium"
                elif cycles_burn_rate == "4_000_000_000_000":
                    setting = "High"
                elif cycles_burn_rate == "6_000_000_000_000":
                    setting = "VeryHigh"
                else:
                    setting = "Custom"

                print(f"  - {address} ({setting})")
            except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
                print(f"  - {address} (Unable to query setting)")
        env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}-{user}.env")
    
    if not mainers or len(mainers) == 0:
        print(f"No mainers found for the specified network {network}.")
        return
    
    print("----------------------------------------------")
    # Print the summary of ICP to XDR conversion
    icp_xdr_summary()

    print("----------------------------------------------")
    print(f"Writing mainers to {env_file_path}")

    # get total cycle balance
    total_cycles = 0
    total_paused_low = 0
    total_paused_medium = 0
    total_paused_high = 0
    total_paused_very_high = 0
    total_active_low = 0
    total_active_medium = 0
    total_active_high = 0
    total_active_very_high = 0
    total_paused = 0
    total_active = 0
    mainers_created = 0

    with open(env_file_path, 'w') as f:
        f.write(f"# {len(mainers)-1} mAIners - data from game_state_canister on network {network}\n")
        f.write(f"# DO NOT MANUALLY UPDATE THIS FILE, instead run: scripts/get_mainers.sh --network $NETWORK \n")
    
        try:
            for mainer in mainers:
                address = mainer.get('address', '')
                canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
                canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

                if canister_type == "ShareService":
                    print(f"Skipping ShareService canister, because this is part of the protocol canisters: {address}")
                    continue

                if canister_type != "ShareAgent":
                    print(f"Skipping canister, because the canister_type is unknown : {canister_type}")
                    continue

                if address !="":
                    mainers_created += 1

                    line = f"MAINER_SHARE_AGENT_{mainers_created:04d}={address}\n"
                    f.write(line)

                    if user == "all" or user is None:
                        # check if the canister is paused or active
                        active = False
                        cmd = ["dfx", "canister", "call", address, "getIssueFlagsAdmin", "--network", network, "--output", "json"]
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                        data = json.loads(output)
                        low_cycle_balance = data.get('Ok', {}).get('lowCycleBalance', None)
                        if low_cycle_balance is None:
                            print(f"ERROR 1: Unable to get issue flags for canister {address} on network {network}")
                            print(f"  {' '.join(cmd)}")
                            print(output)
                            continue
                        elif low_cycle_balance == False:
                            active = True
                            total_active += 1
                        elif low_cycle_balance == True:
                            total_paused += 1        

                        # This used 'dfx status', which is slow...
                        # balance = get_balance(address, network)
                        # total_cycles += balance if balance is not None else 0

                        # get cycleBalance & cyclesBurnRate from getMainerStatisticsAdmin endpoint
                        cmd = ["dfx", "canister", "call", address, "getMainerStatisticsAdmin", "--network", network, "--output", "json"]
                        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
                        data = json.loads(output)

                        cycle_balance = int(data.get('Ok', {}).get('cycleBalance', 0))
                        if cycle_balance > 0:
                            total_cycles += cycle_balance
                        else:
                            print(f"ERROR: Unable to get cycleBalance for canister {address} on network {network}")
                            print(f"  {' '.join(cmd)}")
                            print(output)
                            continue

                        cycles_burn_rate = data.get('Ok', {}).get('cyclesBurnRate', {}).get('cycles', None)
                        if cycles_burn_rate is not None:
                            # These ranges need to be kept up to date with the backend (Game State: mAIner Burn Rates)
                            if cycles_burn_rate == "1_000_000_000_000":
                                if active:
                                    total_active_low += 1
                                else:
                                    total_paused_low += 1
                            elif cycles_burn_rate == "2_000_000_000_000":
                                if active:
                                    total_active_medium += 1
                                else:
                                    total_paused_medium += 1
                            elif cycles_burn_rate == "4_000_000_000_000":
                                if active:
                                    total_active_high += 1
                                else:
                                    total_paused_high += 1
                            elif cycles_burn_rate == "6_000_000_000_000":
                                if active:
                                    total_active_very_high += 1
                                else:
                                    total_paused_very_high += 1
                            else:
                                print(f"ERROR: Unknown cyclesBurnRate {cycles_burn_rate} for canister {address} on network {network}")
                                print(f"  {' '.join(cmd)}")
                                print(output)
                                continue
                        else:
                            print(f"ERROR: Unable to get cyclesBurnRate for canister {address} on network {network}")
                            print(f"  {' '.join(cmd)}")
                            print(output)
                            continue

                        # print progress every 25 mainers
                        if mainers_created % 25 == 0:
                            print(f"Processed {mainers_created} mainers:")
                            
        except subprocess.CalledProcessError as e:
            print(f"ERROR occured when calling the subprocess command.")
            print("Command:", e.cmd)
            print("Return code:", e.returncode)
            print("Output:\n", e.output)
            sys.exit(1)

    total_cycles = total_cycles // 1_000_000_000_000 # Convert to trillion cycles
    total_cycles_usd = total_cycles * CMC_USD_PER_COMPUTED_XDR  # Convert to USD

    daily_burn_rate = total_active_low * DAILY_BURN_RATE_LOW+ total_active_medium * DAILY_BURN_RATE_MEDIUM + total_active_high * DAILY_BURN_RATE_HIGH + total_active_very_high * DAILY_BURN_RATE_VERY_HIGH
    daily_burn_rate_usd = daily_burn_rate * CMC_USD_PER_COMPUTED_XDR  # Convert to USD
    
    funnai_index = 0.9 * daily_burn_rate / IC_API_TCYCLE_BURN_RATE_PER_DAY if IC_API_TCYCLE_BURN_RATE_PER_DAY > 0 else 0

    print(f"FUNNAI Index                            : {funnai_index:.2f}")
    print(f"Total daily burn rate                   : {daily_burn_rate} trillion cycles /day (${daily_burn_rate_usd:.2f} USD/day)")
    print(f"Total mainers created                   : {mainers_created}")
    print(f"Total cycles across all mainers         : {total_cycles} trillion cycles")
    print(f"Total paused mainers                    : {total_paused}")
    print(f"Total active mainers                    : {total_active}")
    print(f"Total active low burn rate mainers      : {total_active_low}")
    print(f"Total active medium burn rate mainers   : {total_active_medium}")
    print(f"Total active high burn rate mainers     : {total_active_high}")
    print(f"Total active very high burn rate mainers: {total_active_very_high}")
    print(f"Total paused low burn rate mainers      : {total_paused_low}")
    print(f"Total paused medium burn rate mainers   : {total_paused_medium}")
    print(f"Total paused high burn rate mainers     : {total_paused_high}")
    print(f"Total paused very high burn rate mainers: {total_paused_very_high}")

    if user == "all" or user is None:
        # Write counts to a timestamped CSV file only if there's a change
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        csv_file_path = os.path.join(SCRIPT_DIR, f"get_mainers-{network}.csv")
            
        if os.path.exists(csv_file_path) and os.stat(csv_file_path).st_size > 0:
            # Read the contents of the CSV file and store it in a pandas dataframe. It has a header line
            df = pd.read_csv(csv_file_path)

        if not df.empty:
            # Adding new data as a new row
            new_row = {
                'timestamp': timestamp, 
                'network': network, 
                'mainers_created': mainers_created, 
                'total_cycles': total_cycles,
                'total_paused': total_paused,
                'total_active': total_active,
                'total_active_low': total_active_low,
                'total_active_medium': total_active_medium,
                'total_active_high': total_active_high,
                'total_active_very_high': total_active_very_high,
                'total_paused_low': total_paused_low,
                'total_paused_medium': total_paused_medium,
                'total_paused_high': total_paused_high,
                'total_paused_very_high': total_paused_very_high
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Patch to calculate estimate of total cycles
            # add a new column: total_cycles
            # df['total_cycles'] = df['mainers_created'].apply(lambda x: x * 15 if x <= 217 else x * 30)

            # write the df back to the csv file
            print(f"Writing mainer metrics to {csv_file_path}")
            df.to_csv(csv_file_path, index=False)

        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start timers.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--user",
        default="all",
        help="Specify the user for which to get mainers (default: 'all')",
    )
    args = parser.parse_args()
    main(args.network, args.user)
