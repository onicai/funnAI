#!/usr/bin/env python3
"""One-off migration of icpp-pro smoke tests from the dfx era to icp-cli.

What changes, and why
---------------------
1. ``dfx_json_path=`` -> ``icp_yaml_path=``     -- icpp-pro >= 5.5.0 reads icp.yaml.
2. ``DFX_JSON_PATH``   -> ``ICP_YAML_PATH``     -- and the path it points at.
3. ``from icpp.smoketest import ...``           -- routed through the local
   ``candid_compat`` shim, which normalizes icp-cli's Candid pretty-printer so the
   existing expected values keep comparing equal.
4. exact-match assertions get their expected value wrapped in ``norm(...)``.
   Substring assertions (``"..." in response``) and ``startswith`` need no change,
   because ``candid_compat.call_canister_api`` returns already-normalized text.
5. the module docstring's ``dfx start`` / ``dfx deploy`` recipe.

Assertions this script deliberately does NOT rewrite are reported at the end so they
can be handled by hand -- notably ``assert x in [ ... ]`` over a multi-line list.

Usage
-----
    python3 scripts/migrate_tests_to_icp.py --check PoAIW/src/Challenger/test/test_*.py
    python3 scripts/migrate_tests_to_icp.py --write PoAIW/src/Challenger/test/test_*.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# `assert <name> == <expected>` where <expected> is a bare identifier or a string
# literal -- the two shapes that carry a Candid value in these suites.
ASSERT_IDENT = re.compile(r"^(\s*assert\s+\w+\s*==\s*)(expected_\w+)(\s*)$")
ASSERT_LITERAL = re.compile(
    r"""^(\s*assert\s+\w+\s*==\s*)          # assert response ==
         ((?:'[^']*'|"[^"]*"))              # a single- or double-quoted literal
         (\s*)$""",
    re.VERBOSE,
)


def migrate(text: str) -> tuple[str, list[str]]:
    """Return (new_text, notes-about-things-left-for-a-human)."""
    notes: list[str] = []

    # --- 1/2/3: paths and imports -------------------------------------------------
    text = text.replace(
        'DFX_JSON_PATH = Path(__file__).parent / "../dfx.json"',
        'ICP_YAML_PATH = Path(__file__).parent / "../icp.yaml"',
    )
    text = text.replace("dfx_json_path=DFX_JSON_PATH", "icp_yaml_path=ICP_YAML_PATH")
    text = text.replace("# Path to the dfx.json file", "# Path to the icp.yaml file")
    text = text.replace(
        "# Canister in the dfx.json file we want to test",
        "# Canister in the icp.yaml file we want to test",
    )

    def _import(m: re.Match[str]) -> str:
        names = [n.strip() for n in m.group(1).split(",")]
        if "norm" not in names:
            names.append("norm")
        return f"from .candid_compat import {', '.join(names)}"

    text = re.sub(r"^from icpp\.smoketest import ([^\n]+)$", _import, text, flags=re.MULTILINE)

    # --- 5: the docstring recipe --------------------------------------------------
    text = text.replace("$ dfx start --clean --background", "$ icp network start -d")
    text = re.sub(
        r"\$ dfx deploy --network (\S+) (\S+)", r"$ icp deploy \2 -e \1 -y", text
    )

    # --- 4: exact-match assertions ------------------------------------------------
    out: list[str] = []
    for lineno, line in enumerate(text.splitlines(keepends=True), 1):
        stripped = line.rstrip("\n")
        m = ASSERT_IDENT.match(stripped)
        if m:
            out.append(f"{m.group(1)}norm({m.group(2)}){m.group(3)}\n")
            continue
        m = ASSERT_LITERAL.match(stripped)
        if m:
            out.append(f"{m.group(1)}norm({m.group(2)}){m.group(3)}\n")
            continue
        # Flag comparison shapes we are not confident to rewrite mechanically.
        if re.match(r"^\s*assert\s+\w+\s+in\s+\[\s*$", stripped):
            notes.append(f"line {lineno}: `{stripped.strip()}` -- wrap each list item in norm()")
        elif re.search(r"assert\s+\w+\s*==", stripped) and "norm(" not in stripped:
            notes.append(f"line {lineno}: `{stripped.strip()}` -- unrecognised, check by hand")
        out.append(line)

    return "".join(out), notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--write", action="store_true", help="apply the changes in place")
    args = ap.parse_args()

    leftovers = 0
    for path in args.files:
        original = path.read_text()
        new, notes = migrate(original)
        changed = new != original
        print(f"\n=== {path} ===")
        print(f"  changed: {'yes' if changed else 'no'}")
        print(f"  icp_yaml_path= : {new.count('icp_yaml_path=ICP_YAML_PATH')}")
        print(f"  norm(...)      : {new.count('norm(')}")
        for n in notes:
            leftovers += 1
            print(f"  MANUAL {n}")
        if args.write and changed:
            path.write_text(new)
            print("  written.")

    if not args.write:
        print("\n(dry run -- pass --write to apply)")
    if leftovers:
        print(f"\n{leftovers} assertion(s) need a manual look (see MANUAL above).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
