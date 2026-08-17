#!/usr/bin/env python3
"""One-off migration of dfx `canister_ids.json` -> icp-cli `.icp/data/mappings/<env>.ids.json`.

Background
----------
dfx stored every canister id for every network in a single `canister_ids.json`, shaped
`{canister_name: {network: principal}}`. icp-cli instead keeps one flat file per
environment, `.icp/data/mappings/<env>.ids.json`, shaped `{canister_name: principal}`.

Only canisters that are declared in the project's `icp.yaml` belong in a mapping file.
funnAI has two large families that deliberately are NOT declared there -- the ~744
`mainer_ctrlb_canister_N` and the `llm_N` slots -- because they are addressed by principal
(`icp canister call <principal> ... -n ic`), which needs no icp.yaml entry. Those are
written to a plain ops registry instead, keeping the original nested shape.

Usage
-----
    # show what would happen, touch nothing
    python3 scripts/migrate_canister_ids.py --check PoAIW/src/Challenger

    # write the mapping files (and the registry, if --registry is given)
    python3 scripts/migrate_canister_ids.py --write PoAIW/src/Challenger

    # a family whose extra names go to an ops registry rather than to icp.yaml
    python3 scripts/migrate_canister_ids.py --write --registry mainer_ids.json PoAIW/src/mAIner

Nothing here contacts a network, and `canister_ids.json` is never deleted -- verify with
`--verify` first, then remove it in a separate, deliberate step.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def icp_yaml_names(project: Path) -> set[str]:
    """Canister names declared in the project's icp.yaml."""
    icp_yaml = project / "icp.yaml"
    if not icp_yaml.is_file():
        sys.exit(f"{project}: no icp.yaml -- write it before migrating the ids")
    doc = yaml.safe_load(icp_yaml.read_text()) or {}
    return {c["name"] for c in (doc.get("canisters") or [])}


def load_old(project: Path) -> dict[str, dict[str, str]]:
    old = project / "canister_ids.json"
    if not old.is_file():
        sys.exit(f"{project}: no canister_ids.json to migrate")
    return json.loads(old.read_text())


def split(
    old: dict[str, dict[str, str]], declared: set[str]
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Split into (mappings by env for declared names, registry for the rest).

    Empty principals are dropped: dfx wrote `""` placeholders for networks that were
    never deployed to (notably `backup`), and icp-cli has no use for them.
    """
    by_env: dict[str, dict[str, str]] = {}
    registry: dict[str, dict[str, str]] = {}
    for name, envs in old.items():
        live = {e: c for e, c in envs.items() if c}
        if not live:
            continue
        if name in declared:
            for env, cid in live.items():
                by_env.setdefault(env, {})[name] = cid
        else:
            registry[name] = live
    return by_env, registry


def triples(nested: dict[str, dict[str, str]]) -> set[tuple[str, str, str]]:
    return {(n, e, c) for n, envs in nested.items() for e, c in envs.items() if c}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projects", nargs="+", type=Path, help="project dirs holding an icp.yaml")
    ap.add_argument("--write", action="store_true", help="write the mapping/registry files")
    ap.add_argument("--check", action="store_true", help="report only (default)")
    ap.add_argument(
        "--registry",
        metavar="FILENAME",
        help="write names absent from icp.yaml to this file (e.g. mainer_ids.json). "
        "Without it, such names are reported and left in canister_ids.json.",
    )
    args = ap.parse_args()
    write = args.write and not args.check

    failures = 0
    for project in args.projects:
        declared = icp_yaml_names(project)
        old = load_old(project)
        by_env, registry = split(old, declared)

        print(f"\n=== {project} ===")
        print(f"  declared in icp.yaml : {', '.join(sorted(declared)) or '(none)'}")
        for env in sorted(by_env):
            print(f"  {env:<12} -> .icp/data/mappings/{env}.ids.json  ({len(by_env[env])} id(s))")
        if registry:
            dest = args.registry or "(NOT WRITTEN -- pass --registry)"
            print(f"  not in icp.yaml      : {len(registry)} name(s) -> {dest}")

        # Nothing may be lost: every (name, env, id) triple must land somewhere.
        want = triples(old)
        got = {(n, e, c) for e, m in by_env.items() for n, c in m.items()} | triples(registry)
        lost = want - got
        if lost:
            failures += 1
            print(f"  LOST {len(lost)} triple(s): {sorted(lost)[:5]}")
        else:
            print(f"  id check             : OK, all {len(want)} id(s) accounted for")

        if registry and not args.registry:
            failures += 1
            print("  REFUSING to write: names absent from icp.yaml need --registry")
            continue

        if write:
            out = project / ".icp" / "data" / "mappings"
            out.mkdir(parents=True, exist_ok=True)
            for env, mapping in by_env.items():
                path = out / f"{env}.ids.json"
                path.write_text(json.dumps(dict(sorted(mapping.items())), indent=2) + "\n")
            if registry:
                (project / args.registry).write_text(
                    json.dumps(dict(sorted(registry.items())), indent=2) + "\n"
                )
            print("  written.")

    if not write:
        print("\n(dry run -- pass --write to create the files)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
