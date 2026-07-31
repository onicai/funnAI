"""Shared icp-cli helpers for the funnAI ops scripts.

Replaces the ad-hoc `subprocess.run(["dfx", ...])` calls and the four near-identical
`ic_py_canister.py` copies that grew across this repo and PoAIW.

Why this module exists
----------------------
dfx is deprecated; its successor is icp-cli (`icp`). Most of the translation is a
straight command swap, but three differences bite hard enough to be worth centralising:

1. **There is no `--output json`.** dfx could decode a Candid response to JSON, and ~60
   call sites did `json.loads(dfx ... --output json)`. icp's `--json` returns a *wrapper*
   (`{response_bytes, response_text, response_candid}`), not the decoded value. So calls
   that need real Python objects go through icp-py-core instead -- see `call()`.
2. **icp does not inherit dfx's active identity.** icp's own `default` identity is a
   different principal from the `icpp-llm` that dfx used. A command that forgets
   `--identity` runs as a non-controller, and the failure can be silent. Hence
   `DEFAULT_IDENTITY` and the fact that every function here passes it.
3. **Queries are not auto-detected.** dfx worked out whether a method was a query; icp
   sends an update call unless told `--query`. On the monitoring loops -- which poll
   hundreds of canisters -- that is a 2x latency difference, so query calls say so.

Mainnet safety
--------------
Canister *lifecycle* operations against mainnet -- install, upgrade, top-up, controller
changes, wallet spends -- are refused outright. The dfx -> icp-cli migration is a tooling
change; redeploying canisters is a separate, later project.

Ordinary method calls are a different matter: several monitoring endpoints are declared as
update methods even though they only read (`recursive_dir_content_update` is the notable
one). Blocking those would break day-to-day prd monitoring, so `call`/`call_text` guard
mainnet update calls by default but accept `allow_mainnet=True` at the call site. Use it
only for methods you have checked do not mutate state, and say why in a comment.

Reads (status, balances, queries, module hashes) are never restricted.
`ICP_ALLOW_MAINNET_WRITES=1` lifts the lifecycle guard, and should be set only once the
mainnet project is deliberately underway.
"""

from __future__ import annotations

import functools
import json
import os
import subprocess
from typing import Any, Optional

from icp_core import Agent, Canister, Client, Identity

ICP = "icp"

# NOT `default`. icp-cli does not import dfx's identities or its notion of an active one:
# on this machine icp's `default` is iwcyb-... while the funnAI controller is
# chfec-...-2ae, which icp knows as `icpp-llm`.
DEFAULT_IDENTITY = os.environ.get("ICP_IDENTITY", "icpp-llm")

# The five dfx "networks" were all https://icp0.io -- separate canister-id namespaces
# rather than separate networks. Under icp-cli they are environments over network `ic`.
MAINNET_ENVIRONMENTS = frozenset({"prd", "testing", "development", "demo", "backup", "ic"})


class MainnetWriteBlocked(RuntimeError):
    """Raised when a state-changing call would target mainnet."""


def mainnet_writes_allowed() -> bool:
    return os.environ.get("ICP_ALLOW_MAINNET_WRITES") == "1"


def guard_write(env: str, what: str) -> None:
    """Refuse state-changing operations against mainnet environments."""
    if env in MAINNET_ENVIRONMENTS and not mainnet_writes_allowed():
        raise MainnetWriteBlocked(
            f"Refusing to {what} on '{env}': that is mainnet.\n"
            "The dfx -> icp-cli migration does not redeploy anything; that is a separate\n"
            "project (see WASM-HASHES.md). Use '--network local', or set\n"
            "ICP_ALLOW_MAINNET_WRITES=1 once the mainnet project is deliberately underway."
        )


# ---------------------------------------------------------------------------------------
# Running icp
# ---------------------------------------------------------------------------------------
def run_icp(args: str, quiet: bool = False, check: bool = False) -> Optional[str]:
    """Run `icp <args>` and return stripped stdout, or None on failure.

    stdin is closed: icp opens an interactive prompt when an argument is missing, which
    would hang a script forever.
    """
    try:
        out = subprocess.run(
            f"{ICP} {args}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        return out.stdout.rstrip("\n")
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"Failed icp command: '{args}'\n{e.stdout}{e.stderr}")
        if check:
            raise
        return None


def net_flag(env: str) -> str:
    """Network selector for a target addressed by PRINCIPAL.

    Calling by *name* needs `-e <env>` so icp can resolve the id from the project's
    store. Calling by *principal* needs no project at all, so mainnet environments
    collapse to `-n ic`.
    """
    return "-e local" if env == "local" else "-n ic"


# ---------------------------------------------------------------------------------------
# Reads
# ---------------------------------------------------------------------------------------
def canister_id(name: str, env: str) -> Optional[str]:
    """Resolve a canister name to its principal via icp's id store.

    Reads .icp/data/mappings/<env>.ids.json (or the local cache); no network call, so it
    works with the local network stopped. Replaces `dfx canister id NAME --network N`.
    """
    return run_icp(f"canister status {name} -e {env} --id-only", quiet=True)


@functools.lru_cache(maxsize=None)
def api_url(env: str) -> str:
    """Replica URL for an environment.

    The local network's port is ephemeral (icp.yaml sets gateway.port: 0) so it must be
    read back on every run. The trailing slash icp reports must be stripped: icp-py-core
    appends "/api/v3/...", and "//api/v3" is rejected by the replica with a 400.
    """
    if env != "local":
        return "https://icp0.io"
    status = run_icp("network status -e local --json")
    if status is None:
        raise RuntimeError("local network is not running -- start it with `icp network start -d`")
    return json.loads(status)["api_url"].rstrip("/")


def status_json(target: str, env: str, identity: str = DEFAULT_IDENTITY) -> Optional[dict]:
    """Full `icp canister status --json` for a canister id. Requires being a controller."""
    out = run_icp(f"canister status {target} {net_flag(env)} --identity {identity} --json")
    return json.loads(out) if out else None


def public_status(target: str) -> Optional[dict]:
    """Public state-tree status: works WITHOUT being a controller (mainnet only).

    This is the replacement for `dfx canister info`.
    """
    out = run_icp(f"canister status {target} -n ic -p --json")
    return json.loads(out) if out else None


def _to_int(value: Any) -> Optional[int]:
    """icp reports numbers as strings with `_` thousand separators."""
    if value is None:
        return None
    return int(str(value).replace("_", ""))


def balance(target: str, env: str, identity: str = DEFAULT_IDENTITY) -> Optional[int]:
    """Cycles balance of a canister. Replaces parsing dfx status' `Balance:` line."""
    st = status_json(target, env, identity)
    return _to_int(st.get("cycles")) if st else None


def module_hash(target: str) -> Optional[str]:
    """Deployed module hash, without the 0x prefix. No controller rights needed."""
    st = public_status(target)
    if not st or not st.get("module_hash"):
        return None
    return str(st["module_hash"]).removeprefix("0x")


def controllers(target: str, env: str, identity: str = DEFAULT_IDENTITY) -> list[str]:
    st = status_json(target, env, identity)
    return list(st.get("settings", {}).get("controllers", [])) if st else []


# ---------------------------------------------------------------------------------------
# Candid calls
# ---------------------------------------------------------------------------------------
@functools.lru_cache(maxsize=None)
def _agent(env: str, identity: str) -> Agent:
    pem = run_icp(f"identity export {identity}")
    if pem is None:
        raise RuntimeError(
            f"could not export identity '{identity}'. It must exist and be stored in "
            "plaintext: a keyring-backed identity prompts for a password and hangs."
        )
    return Agent(Identity.from_pem(pem), Client(url=api_url(env)))


@functools.lru_cache(maxsize=None)
def candid_of(target: str, env: str) -> str:
    """Fetch a canister's Candid interface from its own metadata -- no .did file needed."""
    did = run_icp(f"canister metadata {target} candid:service {net_flag(env)}")
    if did is None:
        raise RuntimeError(f"could not read candid:service metadata from {target}")
    return did


def extract_value(response: list[Any]) -> Any:
    """Normalise icp-py-core's `[{'type': ..., 'value': X}]` to X."""
    item = response[0]
    if isinstance(item, dict) and "value" in item:
        return item["value"]
    return item


def call(
    target: str,
    method: str,
    *args: Any,
    env: str = "local",
    identity: str = DEFAULT_IDENTITY,
    is_query: bool = False,
    allow_mainnet: bool = False,
) -> Any:
    """Call a canister method and return DECODED Python objects.

    This is the replacement for `dfx canister call ... --output json` + `json.loads`,
    which icp-cli has no equivalent for. Decoding happens client-side via icp-py-core.

    Pass `allow_mainnet=True` for an update method that only reads (see module docstring).
    """
    if not is_query and not allow_mainnet:
        guard_write(env, f"call update method '{method}' on {target}")
    canister = Canister(agent=_agent(env, identity), canister_id=target, candid=candid_of(target, env))
    return extract_value(getattr(canister, method)(*args))


def call_text(
    target: str,
    method: str,
    arg: str = "()",
    *,
    env: str = "local",
    query: bool = False,
    identity: str = DEFAULT_IDENTITY,
    allow_mainnet: bool = False,
) -> Optional[str]:
    """Call a canister method and return the raw Candid TEXT response.

    For the many places that only log or substring-match the response. Pass
    `query=True` for query methods: unlike dfx, icp does not auto-detect them, and an
    update call is markedly slower.

    Pass `allow_mainnet=True` for an update method that only reads (see module docstring).
    """
    if not query and not allow_mainnet:
        guard_write(env, f"call update method '{method}' on {target}")
    q = "--query" if query else ""
    return run_icp(
        f"canister call {target} {method} '{arg}' {net_flag(env)} --identity {identity} {q}"
    )


# ---------------------------------------------------------------------------------------
# Writes (all guarded)
# ---------------------------------------------------------------------------------------
def install(
    target: str,
    wasm: str,
    mode: str = "upgrade",
    env: str = "local",
    identity: str = DEFAULT_IDENTITY,
    args: Optional[str] = None,
) -> Optional[str]:
    """Install/upgrade a wasm BY PRINCIPAL -- needs no icp.yaml entry for the canister.

    This is what lets the 744 mainer_ctrlb_canister_N and the llm_N slots stay out of
    icp.yaml entirely: they are addressed by principal, never by name.
    """
    guard_write(env, f"install ({mode}) onto {target}")
    extra = f" --args '{args}'" if args else ""
    return run_icp(
        f"canister install {target} --wasm {wasm} -m {mode} {net_flag(env)} "
        f"--identity {identity} -y{extra}"
    )


def top_up(target: str, amount: int, env: str = "local", identity: str = DEFAULT_IDENTITY) -> Optional[str]:
    """Add cycles from the identity's cycles-ledger balance."""
    guard_write(env, f"top up {target}")
    return run_icp(f"canister top-up {target} --amount {amount} {net_flag(env)} --identity {identity}")


def add_controller(target: str, principal: str, env: str = "local", identity: str = DEFAULT_IDENTITY):
    guard_write(env, f"add a controller to {target}")
    return run_icp(
        f"canister settings update {target} --add-controller {principal} "
        f"{net_flag(env)} --identity {identity}"
    )


# The funnAI cycles wallet. icp-cli has no wallet concept, so instead of `dfx wallet send`
# we call the wallet canister's own endpoint directly. Deliberately unchanged behaviour:
# migrating the 72.7 TC held here to the cycles ledger is a separate decision.
CYCLES_WALLET = "jh35u-eqaaa-aaaag-abf3a-cai"


def wallet_send(target: str, amount: int, env: str = "local", identity: str = DEFAULT_IDENTITY):
    """Replacement for `dfx wallet send <canister> <cycles>`."""
    guard_write(env, f"send {amount} cycles to {target}")
    arg = f'(record {{ canister = principal "{target}"; amount = {amount} : nat64 }})'
    # allow_mainnet: the guard_write above already made the decision for this operation.
    return call_text(CYCLES_WALLET, "wallet_send", arg, env=env, identity=identity, allow_mainnet=True)


def wallet_balance(env: str = "local", identity: str = DEFAULT_IDENTITY) -> Optional[str]:
    """Replacement for `dfx wallet balance` (a query, so it is not guarded)."""
    return call_text(CYCLES_WALLET, "wallet_balance", "()", env=env, query=True, identity=identity)
