#!/usr/bin/env python3
"""Print the canister ids for an environment, gathered from every project in the repo.

icp-cli keeps one id store per project, so funnAI's ids are spread over 16 files:

    <project>/.icp/data/mappings/<env>.ids.json    committed mainnet ids
    <project>/.icp/cache/mappings/local.ids.json   local, disposable

That is the right layout -- one owner per canister, no duplicate stores to drift -- but it
makes "what is the api_canister id on prd?" tedious to answer by hand. This script gives
that back as a single table WITHOUT reintroducing a second source of truth: it derives
everything from the mapping files, so it cannot go stale.

Usage:
    python scripts/show_ids.py                    # prd, all canisters
    python scripts/show_ids.py --network testing  # another environment
    python scripts/show_ids.py api                # only names containing "api"
    python scripts/show_ids.py api_canister -q    # just the id, for scripting
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# `local` lives in the disposable cache; everything else is committed under data/.
CACHE_ENVIRONMENTS = frozenset({"local"})


def mapping_files(network: str) -> list[Path]:
    store = "cache" if network in CACHE_ENVIRONMENTS else "data"
    pattern = f"**/.icp/{store}/mappings/{network}.ids.json"
    return sorted(p for p in REPO.glob(pattern) if "node_modules" not in p.parts)


def is_declared(network: str) -> bool:
    """True if any icp.yaml declares this environment (or it is the implicit `ic`)."""
    if network == "ic":
        return True
    needle = f"name: {network}"
    for path in REPO.glob("**/icp.yaml"):
        if "node_modules" in path.parts or ".mops" in path.parts:
            continue
        try:
            if needle in path.read_text():
                return True
        except OSError:
            continue
    return False


def collect(network: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for path in mapping_files(network):
        # <project>/.icp/<store>/mappings/<env>.ids.json -> <project>
        project = path.parent.parent.parent.parent
        label = "<root>" if project == REPO else str(project.relative_to(REPO))
        try:
            ids = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"warning: could not read {path}: {exc}", file=sys.stderr)
            continue
        for name, canister_id in ids.items():
            if canister_id:  # skip empty placeholders
                rows.append((name, canister_id, label))
    return sorted(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("filter", nargs="?", help="only show canisters whose name contains this")
    parser.add_argument(
        "--network",
        default="prd",
        help="environment name as declared in icp.yaml (default: prd). Use `prd` for "
        "production, never `ic`.",
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="print ids only, one per line")
    args = parser.parse_args()

    rows = collect(args.network)
    if args.filter:
        rows = [r for r in rows if args.filter.lower() in r[0].lower()]

    if not rows:
        where = f" matching '{args.filter}'" if args.filter else ""
        print(f"No canister ids found for environment '{args.network}'{where}.", file=sys.stderr)
        if not mapping_files(args.network):
            print(
                f"No {args.network}.ids.json mapping files exist. Is that a declared "
                f"environment? Check a project's icp.yaml.",
                file=sys.stderr,
            )
        return 1

    if args.quiet:
        for _, canister_id, _ in rows:
            print(canister_id)
        return 0

    name_w = max([len(r[0]) for r in rows] + [len("canister")])
    id_w = max([len(r[1]) for r in rows] + [len("id")])
    proj_w = max([len(r[2]) for r in rows] + [len("project")])
    print(f"{'canister'.ljust(name_w)}  {'id'.ljust(id_w)}  project")
    print(f"{'-' * name_w}  {'-' * id_w}  {'-' * proj_w}")
    for name, canister_id, project in rows:
        print(f"{name.ljust(name_w)}  {canister_id.ljust(id_w)}  {project}")
    print(f"\n{len(rows)} canisters on {args.network}")
    if not is_declared(args.network):
        print(
            f"\nNOTE: '{args.network}' is not declared as an environment in any icp.yaml.\n"
            f"      These ids are from a leftover mapping file -- icp-cli will not resolve\n"
            f"      them, and `-e {args.network}` will fail.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
