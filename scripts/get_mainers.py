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
POAIW_DFX_JSON_PATH = os.path.join(SCRIPT_DIR, "../PoAIW/src/mAIner/dfx.json")
POAIW_CANISTER_IDS_PATH = os.path.join(SCRIPT_DIR, "../PoAIW/src/mAIner/canister_ids.json")

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

def get_mainer_setting(network, address):
    """Get the mainer setting (Low, Medium, High, VeryHigh, Custom) for a given mainer."""
    try:
        cmd = ["dfx", "canister", "call", address, "getMainerStatisticsAdmin", "--network", network, "--output", "json"]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=10)
        data = json.loads(output)
        cycles_burn_rate = data.get('Ok', {}).get('cyclesBurnRate', {}).get('cycles', None)

        # Map cycles burn rate to human-readable setting
        if cycles_burn_rate == "1_000_000_000_000":
            return "Low"
        elif cycles_burn_rate == "2_000_000_000_000":
            return "Medium"
        elif cycles_burn_rate == "4_000_000_000_000":
            return "High"
        elif cycles_burn_rate == "6_000_000_000_000":
            return "VeryHigh"
        elif cycles_burn_rate is not None:
            return "Custom"
        else:
            return "Unknown"
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        return "Unable to query"

def get_mainer_is_active(network, address):
    """Check if a mainer is active (not paused due to low cycle balance)."""
    try:
        cmd = ["dfx", "canister", "call", address, "getIssueFlagsAdmin", "--network", network, "--output", "json"]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=10)
        data = json.loads(output)
        low_cycle_balance = data.get('Ok', {}).get('lowCycleBalance', None)

        if low_cycle_balance is None:
            return None
        return not low_cycle_balance  # Active if lowCycleBalance is False
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        return None

def get_daily_burn_rate_for_setting(setting, is_active):
    """Get the daily burn rate in trillion cycles for a given setting."""
    if not is_active:
        return 0

    if setting == "Low":
        return DAILY_BURN_RATE_LOW
    elif setting == "Medium":
        return DAILY_BURN_RATE_MEDIUM
    elif setting == "High":
        return DAILY_BURN_RATE_HIGH
    elif setting == "VeryHigh":
        return DAILY_BURN_RATE_VERY_HIGH
    else:
        return 0  # Custom, Unknown, or Unable to query

def group_mainers_by_owner(mainers):
    """Group mainers by their owner (principal ID)."""
    grouped = defaultdict(list)
    for mainer in mainers:
        address = mainer.get('address', '')
        canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
        canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

        # Only include ShareAgent mainers with valid addresses
        if canister_type == "ShareAgent" and address != "":
            owner = mainer.get('ownedBy', 'Unknown')
            grouped[owner].append(address)

    return grouped

def write_mainers_env_file(mainers, env_file_path, network):
    """Write ShareAgent mainers to .env file."""
    mainers_created = 0
    with open(env_file_path, 'w') as f:
        f.write(f"# {len(mainers)-1} mAIners - data from game_state_canister on network {network}\n")
        f.write(f"# DO NOT MANUALLY UPDATE THIS FILE, instead run: scripts/get_mainers.sh --network $NETWORK \n")

        for mainer in mainers:
            address = mainer.get('address', '')
            canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
            canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

            if canister_type == "ShareService":
                continue

            if canister_type != "ShareAgent":
                continue

            if address != "":
                line = f"MAINER_SHARE_AGENT_{mainers_created:04d}={address}\n"
                f.write(line)
                mainers_created += 1

    print(f"Updated {mainers_created} ShareAgent mainers in {os.path.abspath(env_file_path)}")
    return mainers_created

def update_poaiw_files(mainers, network):
    """Update dfx.json and canister_ids.json with ShareAgent mainers."""
    share_agent_mainers = []

    # Filter for ShareAgent type mainers only
    for mainer in mainers:
        address = mainer.get('address', '')
        canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
        canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

        if canister_type == "ShareAgent" and address != "":
            share_agent_mainers.append(address)

    # Update dfx.json
    with open(POAIW_DFX_JSON_PATH, 'r') as f:
        dfx_config = json.load(f)

    # Add or update ShareAgent mainers in dfx.json (preserve all existing entries)
    for i, address in enumerate(share_agent_mainers):
        canister_name = f"mainer_ctrlb_canister_{i}"
        if canister_name not in dfx_config['canisters']:
            dfx_config['canisters'][canister_name] = {
                "main": "src/Main.mo",
                "type": "motoko",
                "args": "--enhanced-orthogonal-persistence"
            }

    with open(POAIW_DFX_JSON_PATH, 'w') as f:
        json.dump(dfx_config, f, indent=2)

    # Update canister_ids.json
    with open(POAIW_CANISTER_IDS_PATH, 'r') as f:
        canister_ids = json.load(f)

    # Add or update ShareAgent mainers with their addresses for the specified network (preserve all existing entries)
    for i, address in enumerate(share_agent_mainers):
        canister_name = f"mainer_ctrlb_canister_{i}"
        if canister_name not in canister_ids:
            canister_ids[canister_name] = {}
        canister_ids[canister_name][network] = address

    with open(POAIW_CANISTER_IDS_PATH, 'w') as f:
        json.dump(canister_ids, f, indent=2)

    print(f"Updated {len(share_agent_mainers)} ShareAgent mainers in {os.path.abspath(POAIW_DFX_JSON_PATH)}")
    print(f"Updated {len(share_agent_mainers)} ShareAgent mainers in {os.path.abspath(POAIW_CANISTER_IDS_PATH)}")

def get_mainer_info_parallel(network, address):
    """Get both setting and active status for a mainer in a single call (for parallel processing)."""
    setting = get_mainer_setting(network, address)
    is_active = get_mainer_is_active(network, address)
    return {
        "address": address,
        "setting": setting,
        "is_active": is_active
    }

def main(network, user, skip_poaiw_update=False, daily_metrics=False, limit=None, statistics=False):
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
            setting = get_mainer_setting(network, address)
            print(f"  - {address} ({setting})")
        env_file_path = os.path.join(SCRIPT_DIR, f"canister_ids_mainers-{network}-{user}.env")

    if not mainers or len(mainers) == 0:
        print(f"No mainers found for the specified network {network}.")
        return

    # Apply limit if specified
    original_count = len(mainers)
    if limit is not None and limit > 0:
        mainers = mainers[:limit]
        print(f"Limiting to first {limit} mainers (out of {original_count} total)")
        print("----------------------------------------------")

    # Update PoAIW files unless skipped (only when processing all mainers)
    if not skip_poaiw_update and (user == "all" or user is None):
        update_poaiw_files(mainers, network)

    # Write mainers to .env file
    mainers_created = write_mainers_env_file(mainers, env_file_path, network)

    # Display mainers grouped by principal ID with settings (only for "all" users and when --statistics flag is set)
    if statistics and (user == "all" or user is None):
        print("----------------------------------------------")
        print("mAIners grouped by Principal ID with settings:")
        print("----------------------------------------------")

        grouped_mainers = group_mainers_by_owner(mainers)

        # Sort by number of mainers (descending) then by principal ID
        sorted_owners = sorted(grouped_mainers.items(), key=lambda x: (-len(x[1]), x[0]))

        # Prepare data for JSON output
        principals_data = {}
        total_network_daily_burn = 0

        # Use ThreadPoolExecutor for parallel processing
        from concurrent.futures import ThreadPoolExecutor, as_completed

        for owner, addresses in sorted_owners:
            print(f"\nPrincipal: {owner}")
            print(f"  Total mainers: {len(addresses)}")
            print(f"  Fetching statistics for {len(addresses)} mainers in parallel...")

            # Get settings and calculate daily burn rate for each mainer in parallel
            settings_count = defaultdict(int)
            total_daily_burn_rate = 0
            active_count = 0
            paused_count = 0
            mainer_details = []

            # Fetch all mainer info in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_address = {
                    executor.submit(get_mainer_info_parallel, network, address): address
                    for address in addresses
                }

                for future in as_completed(future_to_address):
                    try:
                        info = future.result()
                        address = info["address"]
                        setting = info["setting"]
                        is_active = info["is_active"]

                        settings_count[setting] += 1

                        if is_active is True:
                            active_count += 1
                            daily_burn = get_daily_burn_rate_for_setting(setting, is_active)
                            total_daily_burn_rate += daily_burn
                        elif is_active is False:
                            paused_count += 1

                        mainer_details.append({
                            "address": address,
                            "setting": setting,
                            "is_active": is_active
                        })
                    except Exception as e:
                        address = future_to_address[future]
                        print(f"  Error fetching info for {address}: {e}")
                        mainer_details.append({
                            "address": address,
                            "setting": "Unable to query",
                            "is_active": None
                        })

            total_network_daily_burn += total_daily_burn_rate

            # Display settings summary
            print(f"  Settings breakdown:")
            for setting in ["Low", "Medium", "High", "VeryHigh", "Custom", "Unknown", "Unable to query"]:
                if settings_count[setting] > 0:
                    print(f"    - {setting}: {settings_count[setting]}")

            print(f"  Active mainers: {active_count}")
            print(f"  Paused mainers: {paused_count}")
            print(f"  Total daily burn rate (active): {total_daily_burn_rate} trillion cycles/day")

            # Store data for JSON output
            principals_data[owner] = {
                "total_mainers": len(addresses),
                "active_mainers": active_count,
                "paused_mainers": paused_count,
                "addresses": addresses,
                "mainer_details": mainer_details,
                "settings": dict(settings_count),
                "total_daily_burn_rate_active": total_daily_burn_rate
            }

        print(f"\nTotal network daily burn rate (active): {total_network_daily_burn} trillion cycles/day")
        print("\n----------------------------------------------")

        # Write JSON summary file
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        json_file_path = os.path.join(SCRIPT_DIR, f"get_mainers_by_principal-{network}.json")

        # Sort principals by burn rate (descending)
        sorted_principals_data = dict(
            sorted(principals_data.items(), key=lambda x: x[1]["total_daily_burn_rate_active"], reverse=True)
        )

        json_output = {
            "network": network,
            "timestamp": timestamp,
            "total_mainers": len(mainers),
            "total_principals": len(principals_data),
            "total_network_daily_burn_rate_active": total_network_daily_burn,
            "principals": sorted_principals_data
        }

        with open(json_file_path, 'w') as f:
            json.dump(json_output, f, indent=2)

        print(f"Written principal ownership summary to {os.path.abspath(json_file_path)}")
        print("----------------------------------------------")

    # Calculate daily metrics if requested
    if daily_metrics and (user == "all" or user is None):
        print("----------------------------------------------")
        # Print the summary of ICP to XDR conversion
        icp_xdr_summary()

        print("----------------------------------------------")
        print(f"Calculating daily metrics for {mainers_created} mainers...")

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

        try:
            processed = 0
            for mainer in mainers:
                address = mainer.get('address', '')
                canister_type_dict = mainer.get('canisterType', {}).get("MainerAgent", {})
                canister_type = list(canister_type_dict.keys())[0] if canister_type_dict else ''

                if canister_type != "ShareAgent" or address == "":
                    continue

                processed += 1

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
                if processed % 25 == 0:
                    print(f"Processed {processed} mainers")

        except subprocess.CalledProcessError as e:
            print(f"ERROR occured when calling the subprocess command.")
            print("Command:", e.cmd)
            print("Return code:", e.returncode)
            print("Output:\n", e.output)
            sys.exit(1)

    if daily_metrics:
        total_cycles = total_cycles // 1_000_000_000_000 # Convert to trillion cycles
        total_cycles_usd = total_cycles * CMC_USD_PER_COMPUTED_XDR  # Convert to USD

        daily_burn_rate = total_active_low * DAILY_BURN_RATE_LOW+ total_active_medium * DAILY_BURN_RATE_MEDIUM + total_active_high * DAILY_BURN_RATE_HIGH + total_active_very_high * DAILY_BURN_RATE_VERY_HIGH
        daily_burn_rate_usd = daily_burn_rate * CMC_USD_PER_COMPUTED_XDR  # Convert to USD

        funnai_index = 0.9 * daily_burn_rate / IC_API_TCYCLE_BURN_RATE_PER_DAY if IC_API_TCYCLE_BURN_RATE_PER_DAY > 0 else 0

        print(f"FUNNAI Index                            : {funnai_index:.2f}")
        print(f"Total daily burn rate                   : {daily_burn_rate} trillion cycles /day (${daily_burn_rate_usd:.2f} USD/day)")
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

    if daily_metrics and (user == "all" or user is None):
        # Write counts to a timestamped CSV file only if there's a change
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        csv_file_path = os.path.join(SCRIPT_DIR, f"get_mainers-{network}.csv")

        df = pd.DataFrame()
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
    parser.add_argument(
        "--skip-poaiw-update",
        action="store_true",
        help="Skip updating PoAIW dfx.json and canister_ids.json files",
    )
    parser.add_argument(
        "--daily-metrics",
        action="store_true",
        help="Calculate daily metrics including cycle burn rates and active/paused status",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of mainers to process (for testing purposes)",
    )
    parser.add_argument(
        "--statistics",
        action="store_true",
        help="Calculate per-principal statistics including settings and daily burn rates",
    )
    args = parser.parse_args()
    main(args.network, args.user, args.skip_poaiw_update, args.daily_metrics, args.limit, args.statistics)
