"""Who gets control of a newly deployed funnAI canister.

This is *deployment configuration* -- which humans end up as canister controllers, admins
and log viewers -- and is deliberately separate from "which identity am I running as"
(that is `icp identity default`, or ICP_IDENTITY; see icp_helpers).

It lives in one place because the same principals were previously copy-pasted across
add_controllers.py, deploy_llm.py and upgrade_llms.py, where they drifted apart and were
easy to miss.

Override without editing code -- e.g. for a different team, or a CI deploy key:

    export FUNNAI_CONTROLLERS="name1=principal1,name2=principal2"

`maintainer_principals()` additionally includes whoever is running the command, so a
developer always retains access to what they just deployed without being listed here.
"""

from __future__ import annotations

import os
from typing import Optional

# Default controllers for newly deployed canisters.
#
# These are real people's principals, checked in because the deployment must be
# reproducible by anyone on the team. Change the team by editing this list or by setting
# FUNNAI_CONTROLLERS.
_DEFAULT_CONTROLLERS: list[dict[str, str]] = [
    {"name": "patrick", "principal": "cda4n-7jjpo-s4eus-yjvy7-o6qjc-vrueo-xd2hh-lh5v2-k7fpf-hwu5o-yqe"},
    {"name": "arjaan", "principal": "chfec-vmrjj-vsmhw-uiolc-dpldl-ujifg-k6aph-pwccq-jfwii-nezv4-2ae"},
]


def controllers() -> list[dict[str, str]]:
    """The controllers to add to a newly deployed canister."""
    raw = os.environ.get("FUNNAI_CONTROLLERS", "").strip()
    if not raw:
        return list(_DEFAULT_CONTROLLERS)
    out: list[dict[str, str]] = []
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        name, _, principal = entry.partition("=")
        out.append({"name": name.strip() or principal.strip(), "principal": principal.strip() or name.strip()})
    return out


def controller_principals() -> list[str]:
    return [c["principal"] for c in controllers()]


def maintainer_principals(me: Optional[str] = None) -> list[str]:
    """Principals to grant maintainer admin / log-viewer access.

    The team controllers, plus the principal running the command (`me`) so that whoever
    deploys keeps access to what they deployed. Duplicates are collapsed, order preserved.
    """
    principals = list(controller_principals())
    if me and me not in principals:
        principals.append(me)
    seen: set[str] = set()
    return [p for p in principals if not (p in seen or seen.add(p))]
