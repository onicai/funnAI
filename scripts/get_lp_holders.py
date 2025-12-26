#!/usr/bin/env python3
"""
Script to fetch LP (Liquidity Provider) holders from ICPSwap pools.

Uses the ICPSwap v3 SwapPool canister API to:
1. Get pool metadata (token0, token1, etc.)
2. Get all user position IDs
3. Get position details with token amounts
4. Sort by ICP held (descending)
5. Output to JSON and MD files
"""

import subprocess
import argparse
import os
import json
from datetime import datetime
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
LP_HOLDERS_DIR = os.path.join(SCRIPT_DIR, "lp_holders")

# Pool configurations
POOLS = {
    "icp_funnai": {
        "canister_id": "c5u7l-rqaaa-aaaar-qbqta-cai",
        "name": "ICP/FUNNAI",
        "token0_symbol": "ICP",
        "token0_canister": "ryjl3-tyaaa-aaaaa-aaaba-cai",
        "token1_symbol": "FUNNAI",
        "token1_canister": "vpyot-zqaaa-aaaaa-qavaq-cai",
        "token0_decimals": 8,
        "token1_decimals": 8,
    }
}

# ICPSwap LiquidityLocks canister
LIQUIDITY_LOCKS_CANISTER = "ihzcl-aiaaa-aaaah-aebvq-cai"

# Known accounts mapping: ICPSwap Account ID (AID) -> details
KNOWN_ACCOUNTS = {
    "24ae6dd2c9150906f57c9acf2e2d006716deb45cafde6393c5e6d3e511767208": {
        "PID": "tkvhh-vcdy3-44iia-rsdjd-a2tm2-6vtef-hugyr-diugf-bmxy6-fjdes-hae",
        "Name": "IConfucius login",
    },
}


def dfx_call(canister_id: str, method: str, args: str = "") -> dict:
    """Call a canister method using dfx and return JSON response."""
    cmd = [
        "dfx", "canister", "--network", "ic", "call",
        canister_id, method
    ]
    if args:
        cmd.append(args)
    cmd.extend(["--output", "json"])

    try:
        result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: dfx call failed for {method}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response for {method}: {e}")
        return None


def get_pool_metadata(canister_id: str) -> dict:
    """Get pool metadata including token info."""
    result = dfx_call(canister_id, "metadata")
    if result and "ok" in result:
        return result["ok"]
    return None


def get_liquidity_lock_aliases(token0_canister: str, token1_canister: str) -> dict:
    """
    Get liquidity lock aliases from ICPSwap LiquidityLocks canister.
    Returns a dict mapping owner address -> lock alias (e.g., "Black Hole", "Sneedlocked")
    """
    # Build the argument for getPrincipalAliasByLedgers
    args = f'(vec {{ principal "{token0_canister}"; principal "{token1_canister}" }})'
    result = dfx_call(LIQUIDITY_LOCKS_CANISTER, "getPrincipalAliasByLedgers", args)

    lock_aliases = {}
    if result and isinstance(result, list):
        for item in result:
            alias = item.get("alias", [])
            ledger_id = item.get("ledger_id")
            governance_id = item.get("governance_id", [])

            if alias and len(alias) > 0:
                alias_name = alias[0]
                # The ledger_id or governance_id becomes the "locked" principal
                # We need to convert this to the ICPSwap account format
                if alias_name and "Governance" in alias_name and governance_id:
                    lock_aliases[governance_id[0]] = alias_name
                elif ledger_id:
                    lock_aliases[ledger_id] = alias_name

    return lock_aliases


def get_positions_by_principal(canister_id: str, principal: str) -> list:
    """Get positions owned by a specific principal."""
    args = f'(principal "{principal}")'
    result = dfx_call(canister_id, "getUserPositionsByPrincipal", args)
    if result and "ok" in result:
        return result["ok"]
    return []


def get_user_position_ids(canister_id: str) -> list:
    """
    Get all user position IDs from the pool.
    Returns list of (user_address, [position_ids])
    """
    result = dfx_call(canister_id, "getUserPositionIds")
    if result and "ok" in result:
        # dfx JSON output uses "0" and "1" keys for tuple elements
        raw_data = result["ok"]
        parsed = []
        for item in raw_data:
            user_address = item.get("0", "")
            position_ids = item.get("1", [])
            # Convert position IDs from strings (with potential underscores) to integers
            position_ids = [int(str(pid).replace("_", "")) for pid in position_ids]
            parsed.append((user_address, position_ids))
        return parsed
    return []


def get_user_positions_with_token_amount(canister_id: str, offset: int, limit: int) -> dict:
    """
    Get user positions with token amounts (paginated).
    Returns Page<UserPositionInfoWithTokenAmount>
    """
    args = f"({offset} : nat, {limit} : nat)"
    result = dfx_call(canister_id, "getUserPositionWithTokenAmount", args)
    if result and "ok" in result:
        return result["ok"]
    return None


def parse_nat(value) -> int:
    """Parse a Candid nat value (may be string with underscores or int)."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.replace("_", ""))
    return 0


def fetch_all_positions(canister_id: str) -> list:
    """Fetch all positions from the pool using pagination."""
    all_positions = []
    offset = 0
    limit = 100  # Fetch 100 positions at a time

    while True:
        print(f"  Fetching positions {offset} to {offset + limit}...")
        page = get_user_positions_with_token_amount(canister_id, offset, limit)

        if not page:
            break

        positions = page.get("content", [])
        all_positions.extend(positions)

        total_elements = parse_nat(page.get("totalElements", 0))
        if offset + limit >= total_elements:
            break

        offset += limit

    return all_positions


def get_position_owner(user_position_ids: list, position_id: int) -> str:
    """Find the owner of a position by its ID."""
    for user_address, position_ids in user_position_ids:
        if position_id in position_ids:
            return user_address
    return "Unknown"


def aggregate_by_owner(positions: list, user_position_ids: list, pool_config: dict) -> list:
    """
    Aggregate positions by owner and calculate total token amounts.
    Returns list of dicts sorted by token0 (ICP) amount descending.
    """
    owner_totals = {}

    for pos in positions:
        position_id = parse_nat(pos.get("id", 0))
        owner = get_position_owner(user_position_ids, position_id)

        if owner not in owner_totals:
            owner_totals[owner] = {
                "owner": owner,
                "token0_amount": 0,
                "token1_amount": 0,
                "total_liquidity": 0,
                "position_count": 0,
                "position_ids": [],
            }

        owner_totals[owner]["token0_amount"] += parse_nat(pos.get("token0Amount", 0))
        owner_totals[owner]["token1_amount"] += parse_nat(pos.get("token1Amount", 0))
        owner_totals[owner]["total_liquidity"] += parse_nat(pos.get("liquidity", 0))
        owner_totals[owner]["position_count"] += 1
        owner_totals[owner]["position_ids"].append(position_id)

    # Convert to list and sort by token0 (ICP) amount descending
    result = list(owner_totals.values())
    result.sort(key=lambda x: x["token0_amount"], reverse=True)

    return result


def format_amount(amount: int, decimals: int) -> str:
    """Format a token amount with decimals."""
    return f"{amount / (10 ** decimals):.{decimals}f}"


def write_json_output(holders: list, pool_config: dict, output_path: str):
    """Write LP holders data to JSON file."""
    output = {
        "pool": pool_config["name"],
        "canister_id": pool_config["canister_id"],
        "token0": pool_config["token0_symbol"],
        "token1": pool_config["token1_symbol"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_holders": len(holders),
        "data": holders,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written JSON output to {output_path}")


def write_md_output(holders: list, pool_config: dict, output_path: str):
    """Write LP holders summary to Markdown file."""
    token0_symbol = pool_config["token0_symbol"]
    token1_symbol = pool_config["token1_symbol"]
    token0_decimals = pool_config["token0_decimals"]
    token1_decimals = pool_config["token1_decimals"]

    # Calculate totals
    total_token0 = sum(h["token0_amount"] for h in holders)
    total_token1 = sum(h["token1_amount"] for h in holders)
    total_positions = sum(h["position_count"] for h in holders)

    # Calculate column widths for alignment
    rank_width = max(4, len(str(len(holders))))
    owner_width = max(len("Owner (AID)"), max(len(h["owner"]) for h in holders) if holders else 5)
    token0_width = max(len(token0_symbol), len(format_amount(total_token0, token0_decimals)))
    token1_width = max(len(token1_symbol), len(format_amount(total_token1, token1_decimals)))
    pos_width = max(len("Positions"), len(str(max(h["position_count"] for h in holders) if holders else 1)))
    pid_width = max(len("PID"), max(len(KNOWN_ACCOUNTS.get(h["owner"], {}).get("PID", "")) for h in holders) if holders else 3)
    name_width = max(len("Name"), max(len(KNOWN_ACCOUNTS.get(h["owner"], {}).get("Name", "")) for h in holders) if holders else 4)

    lines = [
        f"# {pool_config['name']} Liquidity Pool Holders",
        "",
        f"**Pool Canister:** `{pool_config['canister_id']}`",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        "## Summary",
        "",
        f"- **Total LP Holders:** {len(holders)}",
        f"- **Total Positions:** {total_positions}",
        f"- **Total {token0_symbol}:** {format_amount(total_token0, token0_decimals)}",
        f"- **Total {token1_symbol}:** {format_amount(total_token1, token1_decimals)}",
        "",
        "## LP Holders (sorted by ICP held)",
        "",
        f"| {'Rank':>{rank_width}} | {'Owner (AID)':<{owner_width}} | {token0_symbol:>{token0_width}} | {token1_symbol:>{token1_width}} | {'Positions':>{pos_width}} | {'PID':<{pid_width}} | {'Name':<{name_width}} |",
        f"|{'-' * (rank_width + 2)}|{'-' * (owner_width + 2)}|{'-' * (token0_width + 2)}|{'-' * (token1_width + 2)}|{'-' * (pos_width + 2)}|{'-' * (pid_width + 2)}|{'-' * (name_width + 2)}|",
    ]

    for rank, holder in enumerate(holders, 1):
        owner = holder["owner"]
        token0_fmt = format_amount(holder["token0_amount"], token0_decimals)
        token1_fmt = format_amount(holder["token1_amount"], token1_decimals)
        known = KNOWN_ACCOUNTS.get(owner, {})
        pid = known.get("PID", "")
        name = known.get("Name", "")
        lines.append(
            f"| {rank:>{rank_width}} | {owner:<{owner_width}} | {token0_fmt:>{token0_width}} | {token1_fmt:>{token1_width}} | {holder['position_count']:>{pos_width}} | {pid:<{pid_width}} | {name:<{name_width}} |"
        )

    lines.append("")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Written MD summary to {output_path}")


def main(pool_name: str):
    if pool_name not in POOLS:
        print(f"ERROR: Unknown pool '{pool_name}'. Available pools: {list(POOLS.keys())}")
        return

    pool_config = POOLS[pool_name]
    canister_id = pool_config["canister_id"]

    print(f"Fetching LP holders for {pool_config['name']} pool ({canister_id})...")
    print()

    # Step 1: Get pool metadata
    print("Step 1: Getting pool metadata...")
    metadata = get_pool_metadata(canister_id)
    if metadata:
        print(f"  Pool key: {metadata.get('key', 'N/A')}")
        print(f"  Current tick: {metadata.get('tick', 'N/A')}")
        print(f"  Total liquidity: {metadata.get('liquidity', 'N/A')}")
        print(f"  Next position ID: {metadata.get('nextPositionId', 'N/A')}")
    else:
        print("  WARNING: Could not fetch pool metadata")
    print()

    # Step 2: Get user position IDs mapping
    print("Step 2: Getting user position IDs...")
    user_position_ids = get_user_position_ids(canister_id)
    print(f"  Found {len(user_position_ids)} users with positions")
    print()

    # Step 3: Fetch all positions with token amounts
    print("Step 3: Fetching all positions with token amounts...")
    positions = fetch_all_positions(canister_id)
    print(f"  Fetched {len(positions)} positions")
    print()

    # Step 4: Aggregate by owner
    print("Step 4: Aggregating by owner...")
    holders = aggregate_by_owner(positions, user_position_ids, pool_config)
    print(f"  Aggregated into {len(holders)} unique holders")
    print()

    # Step 5: Write output files
    print("Step 5: Writing output files...")
    json_path = os.path.join(LP_HOLDERS_DIR, f"lp_icpswap_{pool_name}.json")
    md_path = os.path.join(LP_HOLDERS_DIR, f"lp_icpswap_{pool_name}.md")

    write_json_output(holders, pool_config, json_path)
    write_md_output(holders, pool_config, md_path)

    print()
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch LP holders from ICPSwap pools.")
    parser.add_argument(
        "--pool",
        choices=list(POOLS.keys()),
        default="icp_funnai",
        help="Pool to fetch LP holders for (default: icp_funnai)",
    )
    args = parser.parse_args()
    main(args.pool)
