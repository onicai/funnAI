#!/usr/bin/env python3

import subprocess
import time
import sys
import argparse
import os
import json
import re

from .monitor_common import get_canisters, run_this_cmd

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

# Model to upload (relative to PoAIW/llms/ dir)
MODEL = "models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf"

# LLM type -> (llm_cwd relative to SCRIPT_DIR, env key pattern)
LLM_TYPE_CONFIG = {
    "challenger": {
        "llm_cwd": "../PoAIW/llms/Challenger",
        "env_key": "CHALLENGER",
    },
    "judge": {
        "llm_cwd": "../PoAIW/llms/Judge",
        "env_key": "JUDGE",
    },
    "share_service": {
        "llm_cwd": "../PoAIW/llms/mAIner",
        "env_key": "SHARE_SERVICE",
    },
}


def find_next_llm_index(canister_ids_path, network):
    """Find the next available llm_N index.

    Scans canister_ids.json for the lowest N where the entry has no value
    for this network (or value is empty string). If no gaps, use max(N) + 1.
    """
    try:
        with open(canister_ids_path) as f:
            canister_ids_data = json.load(f)
    except FileNotFoundError:
        return 0, {}

    # Extract all N values from llm_N keys
    indices = []
    for key in canister_ids_data:
        match = re.match(r"^llm_(\d+)$", key)
        if match:
            indices.append(int(match.group(1)))

    if not indices:
        return 0, canister_ids_data

    indices.sort()

    # Find lowest N where entry has no value for this network or value is ""
    for n in indices:
        key = f"llm_{n}"
        networks = canister_ids_data.get(key, {})
        if network not in networks or networks[network] == "":
            return n, canister_ids_data

    # No gaps — use max + 1
    return max(indices) + 1, canister_ids_data


def ensure_dfx_json_entry(dfx_json_path, llm_name):
    """Ensure llm_N exists in dfx.json. Add it if missing."""
    with open(dfx_json_path) as f:
        dfx_data = json.load(f)

    if llm_name in dfx_data.get("canisters", {}):
        return False  # Already exists

    dfx_data["canisters"][llm_name] = {
        "type": "custom",
        "candid": "../llama_cpp_canister/build/llama_cpp.did",
        "wasm": "../llama_cpp_canister/build/llama_cpp.wasm",
    }

    with open(dfx_json_path, "w") as f:
        json.dump(dfx_data, f, indent=4)
        f.write("\n")

    return True  # Was added


def parse_subnets_from_env(env_path):
    """Parse canister_ids-{network}.env to find subnets and per-type LLM counts.

    Returns dict: {subnet_var: (subnet_id, {type_key: count})}
    where type_key is "CHALLENGER", "JUDGE", or "SHARE_SERVICE".
    """
    subnets = {}  # subnet_var -> subnet_id
    llm_counts = {}  # subnet_var -> {type_key: count}

    try:
        with open(env_path) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {}

    # Pattern for subnet definitions: SUBNET_X_Y=<id> or SUBNET_X_Y="<id>"
    subnet_pattern = re.compile(r'^(SUBNET_\d+_\d+)=[""]?([a-z0-9-]+)[""]?\s*$')
    # Pattern for any LLM entry: SUBNET_X_Y_{TYPE}_LLM_N="<id>"
    llm_pattern = re.compile(
        r'^(SUBNET_\d+_\d+)_(CHALLENGER|JUDGE|SHARE_SERVICE)_LLM_\d+='
    )

    for line in lines:
        line = line.strip()
        if line.startswith("#") or not line:
            continue

        m = subnet_pattern.match(line)
        if m:
            subnet_var = m.group(1)
            subnet_id = m.group(2)
            subnets[subnet_var] = subnet_id
            if subnet_var not in llm_counts:
                llm_counts[subnet_var] = {}
            continue

        m = llm_pattern.match(line)
        if m:
            subnet_var = m.group(1)
            type_key = m.group(2)
            if subnet_var not in llm_counts:
                llm_counts[subnet_var] = {}
            llm_counts[subnet_var][type_key] = llm_counts[subnet_var].get(type_key, 0) + 1

    result = {}
    for var, subnet_id in subnets.items():
        counts = llm_counts.get(var, {})
        result[var] = (subnet_id, counts)

    return result


def auto_select_subnet(env_path, env_key):
    """Auto-select a subnet with < 3 LLMs of this type and no other types.

    Returns (subnet_var, subnet_id) or (None, None) if none available.
    """
    subnet_map = parse_subnets_from_env(env_path)

    for var, (subnet_id, counts) in sorted(subnet_map.items()):
        own_count = counts.get(env_key, 0)
        other_types = {k for k in counts if k != env_key and counts[k] > 0}
        # Skip subnets that have LLMs of a different type
        if other_types:
            continue
        # Pick subnets that already have our type and have room
        if own_count > 0 and own_count < 3:
            return var, subnet_id

    # If no existing subnet has room, return None
    return None, None


def deploy_llm(ctrlb_canister_id, llm_type, llm_cwd, network, subnet, dry_run=False):
    """Deploy a new LLM canister and configure it."""
    env_key = LLM_TYPE_CONFIG[llm_type]["env_key"]
    canister_ids_path = os.path.join(llm_cwd, "canister_ids.json")
    dfx_json_path = os.path.join(llm_cwd, "dfx.json")
    env_path = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")

    # Step 1: Determine next llm_N index
    llm_index, canister_ids_data = find_next_llm_index(canister_ids_path, network)
    llm_name = f"llm_{llm_index}"
    print(f"\n- Next available LLM index: {llm_name}")

    # Step 2: Verify/add llm_N in dfx.json
    added = ensure_dfx_json_entry(dfx_json_path, llm_name)
    if added:
        print(f"  Added {llm_name} to {dfx_json_path}")
    else:
        print(f"  Ok! {llm_name} exists in {dfx_json_path} — we know how to deploy")

    # Step 3: Auto-select subnet if not provided
    subnet_var = None
    if not subnet:
        subnet_var, subnet = auto_select_subnet(env_path, env_key)
        if subnet:
            print(f"\n- Auto-selected subnet: {subnet_var} ({subnet}) — has room for more LLMs")
        else:
            print(f"\n- No subnet with room found for {env_key} LLMs.")
            subnet = input("  Enter a subnet ID to use: ").strip()
            if not subnet:
                print("  No subnet provided. Aborting.")
                return
            subnet_var = input("  Enter the subnet variable name (e.g. SUBNET_1_7): ").strip()
    else:
        # Find the subnet_var for the provided subnet
        subnet_map = parse_subnets_from_env(env_path)
        for var, (sid, _counts) in subnet_map.items():
            if sid == subnet:
                subnet_var = var
                break
        if not subnet_var:
            print(f"\n- Subnet {subnet} not found in {env_path}")
            subnet_var = input("  Enter the subnet variable name (e.g. SUBNET_1_7): ").strip()

    # Step 4: Dry-run summary
    if dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN — no changes will be made")
        print("=" * 80)
        print(f"  LLM name   : {llm_name}")
        print(f"  LLM type   : {llm_type}")
        print(f"  Network    : {network}")
        print(f"  Subnet     : {subnet_var} ({subnet})")
        print(f"  Controller : {ctrlb_canister_id}")
        print(f"  Working dir: {llm_cwd}")
        print("-" * 80)
        print("Actions that WOULD be performed:")
        print(f"   1. Deploy {llm_name} to subnet {subnet}")
        print(f"   2. Health check (3 retries)")
        print(f"   3. Verify correct subnet")
        print(f"   4. Add admin controllers (Patrick, Arjaan)")
        print(f"   5. Upload model: {MODEL}")
        print(f"   6. Load model")
        print(f"   7. Set max_tokens (12/12)")
        print(f"   8. Pause logs and chats")
        print(f"   9. Assign admin roles (4 principals)")
        print(f"  10. Add log viewers (3 principals)")
        print(f"  11. Test LLM (new_chat, run_update, remove_prompt_cache)")
        print(f"  12. Update canister_ids.json")
        print("-" * 80)
        print("DRY RUN complete — nothing was changed.")
        return

    # Step 5: Confirm with user
    print(f"\nAbout to deploy {llm_name} ({llm_type}) on '{network}' to subnet {subnet}")
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Deployment cancelled.")
        return

    # Track completed steps for error reporting
    completed_steps = []
    canister_id = None

    try:
        # Step 6: Deploy canister
        print(f"\n- Deploying {llm_name} to subnet {subnet}")
        cmd = [
            "dfx", "deploy", "--network", network,
            llm_name, "--subnet", subnet, "--mode", "install",
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Deploy canister")

        # Step 7: Wait 30s + health check (3 retries)
        print(f"\n- Waiting 30 seconds for canister to initialize...")
        time.sleep(30)

        # Step 8: Get canister ID
        print(f"\n- Getting canister ID for {llm_name}")
        cmd = ["dfx", "canister", "id", llm_name, "--network", network]
        print(f"  {' '.join(cmd)} \n  -> from directory: {llm_cwd}")
        result = subprocess.check_output(cmd, text=True, cwd=llm_cwd)
        canister_id = result.strip()
        print(f"  Canister ID: {canister_id}")
        completed_steps.append(f"Get canister ID: {canister_id}")

        # Health check with retries
        print(f"\n- Checking health for {llm_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "health"]
        max_retries = 3
        retry_delay = 10
        for attempt in range(1, max_retries + 1):
            try:
                run_this_cmd(cmd, llm_cwd, confirm=False)
                break
            except subprocess.CalledProcessError:
                if attempt < max_retries:
                    print(f"  Health check failed (attempt {attempt}/{max_retries}). Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"  Health check failed after {max_retries} attempts")
                    raise
        completed_steps.append("Health check")

        # Verify correct subnet (API may need a retry if canister is newly indexed)
        if network in ["ic", "prd", "testing", "development", "demo"]:
            print(f"\n- Verifying canister is on correct subnet")
            curl_cmd = [
                "curl", "-s",
                f"https://ic-api.internetcomputer.org/api/v3/canisters/{canister_id}",
            ]
            print(f"  {' '.join(curl_cmd)}")
            for attempt in range(1, 4):
                result = subprocess.check_output(curl_cmd, text=True)
                try:
                    data = json.loads(result)
                    actual_subnet = data.get("subnet_id")
                except json.JSONDecodeError:
                    actual_subnet = None

                if actual_subnet == subnet:
                    print(f"  Subnet verified: {actual_subnet}")
                    break
                elif actual_subnet and actual_subnet != subnet:
                    print(f"  WARNING: Expected subnet {subnet}, got {actual_subnet}")
                    break
                else:
                    if attempt < 3:
                        print(f"  Subnet not yet indexed (attempt {attempt}/3). Retrying in 10s...")
                        time.sleep(10)
                    else:
                        print(f"  WARNING: Could not verify subnet after 3 attempts")
            completed_steps.append("Verify subnet")

        # Add admin controllers
        PATRICK = "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"
        ARJAAN = "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"

        print(f"\n- Adding Patrick as dfx controller")
        cmd = [
            "dfx", "canister", "update-settings", llm_name,
            "--add-controller", PATRICK,
            "--network", network,
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Adding Arjaan as dfx controller")
        cmd = [
            "dfx", "canister", "update-settings", llm_name,
            "--add-controller", ARJAAN,
            "--network", network,
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Add admin controllers (Patrick, Arjaan)")

        # Upload model
        # The upload script (llama_cpp_canister/scripts/upload.py) uses
        # ROOT_PATH = Path(__file__).parent.parent (= llama_cpp_canister/)
        # for dfx.json, candid, and resolving the model path.
        # So we must: run from llama_cpp_canister/, pass canister ID directly,
        # and use a model path relative to llama_cpp_canister/.
        # We use --network ic because llama_cpp_canister/dfx.json only knows
        # "local" and "ic". Networks like testing/prd/demo all resolve to ic.
        print(f"\n- Uploading model to {llm_name} ({canister_id})")
        llama_cpp_canister_path = os.path.join(llm_cwd, "../llama_cpp_canister")
        llama_cpp_canister_path = os.path.realpath(llama_cpp_canister_path)
        model_path_relative = os.path.join("..", MODEL)

        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        if existing_pythonpath:
            env["PYTHONPATH"] = f"{existing_pythonpath}:{llama_cpp_canister_path}"
        else:
            env["PYTHONPATH"] = llama_cpp_canister_path

        upload_network = "ic" if network != "local" else "local"
        cmd = [
            sys.executable, "-m", "scripts.upload",
            "--network", upload_network,
            "--canister", canister_id,
            "--canister-filename", "models/model.gguf",
            model_path_relative,
        ]
        print(f"  {' '.join(cmd)} \n  -> from directory: {llama_cpp_canister_path}")
        print(f"  PYTHONPATH includes: {llama_cpp_canister_path}")
        subprocess.run(cmd, check=True, text=True, cwd=llama_cpp_canister_path, env=env)
        completed_steps.append("Upload model")

        # Step 13: Load model
        print(f"\n- Loading model for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "load_model", '(record { args = vec {"--model"; "models/model.gguf"} })',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Load model")

        # Step 14: Set max_tokens
        print(f"\n- Setting max_tokens for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "set_max_tokens",
            "(record { max_tokens_query = 12 : nat64; max_tokens_update = 12 : nat64 })",
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Set max_tokens")

        # Step 15: Pause logs
        print(f"\n- Pausing logs for {llm_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "log_pause"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Pause logs")

        # Step 16: Pause chats
        print(f"\n- Pausing chats for {llm_name} ({canister_id})")
        cmd = ["dfx", "canister", "--network", network, "call", canister_id, "chats_pause"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Pause chats")

        # Step 17: Assign admin roles
        print(f"\n- Assigning admin role to controller canister for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "assignAdminRole",
            f'(record {{ "principal" = "{ctrlb_canister_id}"; role = variant {{ AdminUpdate }}; note = "{llm_type.capitalize()} controller canister" }})',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Assigning admin role to funnai-django-aws-dev for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "assignAdminRole",
            '(record { "principal" = "bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe"; role = variant { AdminUpdate }; note = "funnai-django-aws-dev" })',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Assigning admin role to maintainer (Arjaan) for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "assignAdminRole",
            '(record { "principal" = "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"; role = variant { AdminUpdate }; note = "maintainer" })',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Assigning admin role to maintainer (Patrick) for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "assignAdminRole",
            '(record { "principal" = "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"; role = variant { AdminUpdate }; note = "maintainer" })',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Assign admin roles")

        # Add log viewers
        print(f"\n- Adding log viewers for {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "update-settings", canister_id,
            "--add-log-viewer", "bzqba-mwz5i-rq3oz-iie6i-gf7bi-kqr2x-tjuq4-nblmh-ephou-n27tl-xqe",
            "--add-log-viewer", "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae",
            "--add-log-viewer", "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe",
            "--network", network,
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Add log viewers")

        # Step 20: Test LLM
        print(f"\n- Testing LLM {llm_name} ({canister_id})")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "new_chat",
            '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--cache-type-k"; "q8_0"; }})',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Testing LLM {llm_name} ({canister_id}) — run_update")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "run_update",
            '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; "--cache-type-k"; "q8_0"; "--repeat-penalty"; "1.1"; "--temp"; "0.6"; "-sp"; "-p"; "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\ngive me a short introduction to LLMs.<|im_end|>\n<|im_start|>assistant\n"; "-n"; "1" }})',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Testing LLM {llm_name} ({canister_id}) — remove_prompt_cache")
        cmd = [
            "dfx", "canister", "--network", network, "call", canister_id,
            "remove_prompt_cache",
            '(record { args = vec { "--prompt-cache"; "prompt.cache" }})',
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Test LLM")

        # Update canister_ids.json
        print(f"\n- Updating canister_ids.json")
        if llm_name in canister_ids_data:
            canister_ids_data[llm_name][network] = canister_id
        else:
            canister_ids_data[llm_name] = {network: canister_id}
        with open(canister_ids_path, "w") as f:
            json.dump(canister_ids_data, f, indent=2)
            f.write("\n")
        print(f"  Updated {llm_name}.{network} = {canister_id}")
        completed_steps.append("Update canister_ids.json")

        # Print summary
        print("\n" + "=" * 80)
        print(f"Successfully deployed {llm_name} ({canister_id})")
        print(f"  LLM type : {llm_type}")
        print(f"  Network  : {network}")
        print(f"  Subnet   : {subnet_var} ({subnet})")
        print(f"  Controller: {ctrlb_canister_id}")
        print("=" * 80)
        print("\nNext steps:")
        print(f"  1. Register canister with CycleOps (manual)")
        print(f"  2. Add LLM to protocol: ./scripts/add_llm.sh --network {network} --canister-id {canister_id} --llm-type {llm_type}")

    except subprocess.CalledProcessError as e:
        print("\n" + "!" * 80)
        print("ERROR: Deployment failed!")
        print("!" * 80)
        print(f"  LLM name     : {llm_name}")
        if canister_id:
            print(f"  Canister ID  : {canister_id}")
        print(f"  Subnet       : {subnet_var} ({subnet})")
        print(f"  Network      : {network}")
        print(f"\n  Completed steps:")
        for i, step in enumerate(completed_steps, 1):
            print(f"    {i}. {step}")
        print(f"\n  Failed at step {len(completed_steps) + 1}")
        if hasattr(e, "cmd"):
            print(f"  Command: {e.cmd}")
        if hasattr(e, "returncode"):
            print(f"  Return code: {e.returncode}")
        if canister_id:
            env_updated = "Update canister_ids-" in " ".join(completed_steps)
            print(f"\n  To clean up the failed canister:")
            if env_updated:
                print(f"    ./scripts/delete_llm.sh --network {network} --canister-id {canister_id}")
            else:
                print(f"    # The canister was not yet added to canister_ids-{network}.env,")
                print(f"    # so delete_llm.sh cannot be used. Run from {llm_cwd}:")
                print(f"    dfx canister --network {network} delete {llm_name}")
        print("!" * 80)


def main(network, llm_type, subnet=None, dry_run=False):
    (CANISTERS, CANISTER_COLORS, RESET_COLOR) = get_canisters(network, "protocol")

    # Extract controller canister IDs
    challenger_canister_id = None
    judge_canister_id = None
    share_service_canister_id = None
    for name, id in CANISTERS.items():
        if "LLM" in name.upper():
            continue
        elif "CHALLENGER" in name.upper():
            challenger_canister_id = id
        elif "JUDGE" in name.upper():
            judge_canister_id = id
        elif "SERVICE" in name.upper():
            share_service_canister_id = id

        if challenger_canister_id and judge_canister_id and share_service_canister_id:
            break

    # Pick the controller matching llm_type
    ctrlb_canister_id = None
    if llm_type == "challenger":
        ctrlb_canister_id = challenger_canister_id
    elif llm_type == "judge":
        ctrlb_canister_id = judge_canister_id
    elif llm_type == "share_service":
        ctrlb_canister_id = share_service_canister_id

    if not ctrlb_canister_id:
        print(f"ERROR: No {llm_type.upper()} controller canister found in canister_ids-{network}.env")
        return

    llm_cwd = os.path.join(SCRIPT_DIR, LLM_TYPE_CONFIG[llm_type]["llm_cwd"])

    print("\n" + "=" * 80)
    print(f"Deploy new {llm_type} LLM on network '{network}'")
    print(f"  Controller: {ctrlb_canister_id}")
    print(f"  Working dir: {llm_cwd}")
    print("=" * 80)

    deploy_llm(ctrlb_canister_id, llm_type, llm_cwd, network, subnet, dry_run=dry_run)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy a new LLM canister.")
    parser.add_argument(
        "--network",
        choices=["local", "ic", "testing", "demo", "development", "prd"],
        default="local",
        help="Specify the network to use (default: local)",
    )
    parser.add_argument(
        "--llm-type",
        choices=["challenger", "judge", "share_service"],
        required=True,
        help="Specify the LLM type to deploy",
    )
    parser.add_argument(
        "--subnet",
        default=None,
        help="Specify the subnet ID (auto-selected if not provided)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )
    args = parser.parse_args()
    main(args.network, args.llm_type, subnet=args.subnet, dry_run=args.dry_run)
