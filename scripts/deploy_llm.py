#!/usr/bin/env python3

from pathlib import Path
import subprocess
import time
import sys
import argparse
import os
import json
import re

from .monitor_common import get_canisters, run_this_cmd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import funnai_team  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"))
import icp_helpers  # noqa: E402

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
FUNNAI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../"))

# Model to upload (relative to PoAIW/llms/ dir)
MODEL = "models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf"

# Cycles to deposit into a freshly-deployed LLM canister so it can grow its
# wasm heap to fit the model (~670 MB) and have operating headroom before
# CycleOps takes over the lifecycle.
INITIAL_TOPUP_CYCLES = 3_000_000_000_000  # 3 T cycles

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


def ensure_icp_yaml_entry(icp_yaml_path, llm_name):
    """Ensure llm_N is declared in icp.yaml. Add it if missing.

    Replaces the old dfx.json mutation -- dfx.json no longer exists. The slot is a
    `pre-built` step pointing at the vendored llama_cpp wasm; there is nothing to compile.
    Appended as text rather than round-tripped through a YAML parser, so the file keeps
    its comments.
    """
    path = Path(icp_yaml_path)
    text = path.read_text()
    if re.search(rf"^  - name: {re.escape(llm_name)}$", text, re.MULTILINE):
        return False  # already declared

    block = (
        f"  - name: {llm_name}\n"
        f"    build:\n"
        f"      steps:\n"
        f"        - type: pre-built\n"
        f"          path: ../llama_cpp_canister/build/llama_cpp.wasm\n"
    )
    marker = "\nnetworks:"
    if marker not in text:
        raise SystemExit(f"{icp_yaml_path}: no `networks:` section to insert before")
    path.write_text(text.replace(marker, f"\n{block}{marker}", 1))
    return True  # was added


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
    icp_yaml_path = os.path.join(llm_cwd, "icp.yaml")
    env_path = os.path.join(SCRIPT_DIR, f"canister_ids-{network}.env")

    # Step 1: Determine next llm_N index
    llm_index, canister_ids_data = find_next_llm_index(canister_ids_path, network)
    llm_name = f"llm_{llm_index}"
    print(f"\n- Next available LLM index: {llm_name}")

    # Step 2: Verify/add llm_N in dfx.json
    added = ensure_icp_yaml_entry(icp_yaml_path, llm_name)
    if added:
        print(f"  Added {llm_name} to {icp_yaml_path}")
    else:
        print(f"  Ok! {llm_name} exists in {icp_yaml_path} — we know how to deploy")

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
        print(f"   5. Deposit {INITIAL_TOPUP_CYCLES // 10**12} T cycles into canister")
        print(f"   6. Upload model: {MODEL}")
        print(f"   7. Load model")
        print(f"   8. Set max_tokens (12/12)")
        print(f"   9. Pause logs and chats")
        print(f"  10. Assign admin roles (3 principals)")
        print(f"  11. Add log viewers (2 principals)")
        print(f"  12. Test LLM (new_chat, run_update, remove_prompt_cache)")
        print(f"  13. Start prompt-cache cleanup timer")
        print(f"  14. Start cycle-balance tracking timer")
        print(f"  15. Update canister_ids.json")
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
        cmd = ["icp", "deploy", llm_name, "--subnet", subnet, "--mode", "install", "-e", network, "-y"]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Deploy canister")

        # Step 7: Wait 30s + health check (3 retries)
        print(f"\n- Waiting 30 seconds for canister to initialize...")
        time.sleep(30)

        # Step 8: Get canister ID
        print(f"\n- Getting canister ID for {llm_name}")
        cmd = ["icp", "canister", "status", llm_name, "-e", network, "--id-only"]
        print(f"  {' '.join(cmd)} \n  -> from directory: {llm_cwd}")
        result = subprocess.check_output(cmd, text=True, cwd=llm_cwd)
        canister_id = result.strip()
        print(f"  Canister ID: {canister_id}")
        completed_steps.append(f"Get canister ID: {canister_id}")

        # Health check with retries
        print(f"\n- Checking health for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "health", "()", "--query", "-e", network]
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
        # The team controllers, from scripts/lib/funnai_team.py (override with
        # FUNNAI_CONTROLLERS), rather than principals pasted into this file.
        for _c in funnai_team.controllers():
            print(f"\n- Adding {_c['name']} as canister controller")
            run_this_cmd(
                ["icp", "canister", "settings", "update", llm_name,
                 "--add-controller", _c["principal"], "-e", network],
                llm_cwd, confirm=False,
            )
        completed_steps.append(
            "Add admin controllers ("
            + ", ".join(c["name"] for c in funnai_team.controllers())
            + ")"
        )

        # Deposit cycles before the model is loaded into the wasm heap.
        # load_model needs to grow the heap by ~670 MB, which requires ~135 B
        # cycles for the memory allocation alone, on top of operating costs.
        # The canister is not registered with CycleOps yet at this point.
        topup_tc = INITIAL_TOPUP_CYCLES // 10**12
        print(f"\n- Depositing {topup_tc} T cycles into {llm_name} ({canister_id})")
        # `dfx canister deposit-cycles` -> `icp canister top-up`. Note the argument order
        # is reversed: icp takes the canister first and the amount as a flag.
        cmd = [
            "icp", "canister", "top-up", canister_id,
            "--amount", str(INITIAL_TOPUP_CYCLES), "-e", network,
        ]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append(f"Deposit {topup_tc} T cycles")

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
        cmd = ["icp", "canister", "call", canister_id, "load_model", '(record { args = vec {"--model"; "models/model.gguf"} })', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Load model")

        # Step 14: Set max_tokens
        print(f"\n- Setting max_tokens for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "set_max_tokens", "(record { max_tokens_query = 12 : nat64; max_tokens_update = 12 : nat64 })", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Set max_tokens")

        # Step 15: Pause logs
        print(f"\n- Pausing logs for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "log_pause", "()", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Pause logs")

        # Step 16: Pause chats
        print(f"\n- Pausing chats for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "chats_pause", "()", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Pause chats")

        # Step 17: Assign admin roles
        print(f"\n- Assigning admin role to controller canister for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "assignAdminRole", f'(record {{ "principal" = "{ctrlb_canister_id}"; role = variant {{ AdminUpdate }}; note = "{llm_type.capitalize()} controller canister" }})', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Assigning admin role to maintainer (Arjaan) for {llm_name} ({canister_id})")
        # Maintainer admin goes to the team plus whoever is running this, so a
        # developer keeps access to what they just deployed.
        for _p in funnai_team.maintainer_principals(icp_helpers.principal()):
            cmd = ["icp", "canister", "call", canister_id, "assignAdminRole",
                   f'(record {{ "principal" = "{_p}"; role = variant {{ AdminUpdate }}; note = "maintainer" }})',
                   "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Assigning admin role to maintainer (Patrick) for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "assignAdminRole", '(record { "principal" = "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"; role = variant { AdminUpdate }; note = "maintainer" })', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Assign admin roles")

        # Add log viewers
        print(f"\n- Adding log viewers for {llm_name} ({canister_id})")
        _viewers = []
        for _p in funnai_team.maintainer_principals(icp_helpers.principal()):
            _viewers += ["--add-log-viewer", _p]
        cmd = ["icp", "canister", "settings", "update", canister_id, *_viewers, "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Add log viewers")

        # Step 20: Test LLM
        print(f"\n- Testing LLM {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "new_chat", '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--cache-type-k"; "q8_0"; }})', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Testing LLM {llm_name} ({canister_id}) — run_update")
        cmd = ["icp", "canister", "call", canister_id, "run_update", '(record { args = vec { "--prompt-cache"; "prompt.cache"; "--prompt-cache-all"; "--cache-type-k"; "q8_0"; "--repeat-penalty"; "1.1"; "--temp"; "0.6"; "-sp"; "-p"; "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\ngive me a short introduction to LLMs.<|im_end|>\n<|im_start|>assistant\n"; "-n"; "1" }})', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)

        print(f"\n- Testing LLM {llm_name} ({canister_id}) — remove_prompt_cache")
        cmd = ["icp", "canister", "call", canister_id, "remove_prompt_cache", '(record { args = vec { "--prompt-cache"; "prompt.cache" }})', "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Test LLM")

        # Start prompt-cache cleanup timer
        # Timer is in-memory only and is NOT auto-armed on install/upgrade,
        # so it must be explicitly started here.
        print(f"\n- Starting prompt-cache cleanup timer for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "cache_cleanup_start_timer", "()", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Start prompt-cache cleanup timer")

        # Cycle-balance tracking timer (llama_cpp_canister >= v0.11.0).
        # In-memory only and NOT auto-armed on install/upgrade, so it must be
        # started explicitly. Without it, get_cycle_balance returns an error
        # instead of a cached balance.
        print(f"\n- Starting cycle-balance tracking timer for {llm_name} ({canister_id})")
        cmd = ["icp", "canister", "call", canister_id, "cycle_balance_start_timer", "()", "-e", network]
        run_this_cmd(cmd, llm_cwd, confirm=False)
        completed_steps.append("Start cycle-balance tracking timer")

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
                print(f"    icp canister delete {llm_name} -e {network}")
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
