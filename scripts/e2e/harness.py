#!/usr/bin/env python3
"""Stand up the whole funnAI application on a single local network.

    python -m scripts.e2e.harness up      # cold machine -> working app
    python -m scripts.e2e.harness seed    # deterministic fixture data
    python -m scripts.e2e.harness status  # one-screen health summary
    python -m scripts.e2e.harness down    # stop the network
    python -m scripts.e2e.harness reset   # down + wipe cache + up

Why this exists
---------------
icp-cli runs one local network per project root, and canisters on different networks cannot
call each other. The production layout gives every canister its own project, so a naive
"deploy everything locally" leaves you with a dozen isolated replicas -- and, because each
replica allocates ids from the same sequence, with several canisters sharing an id.

So: each canister is built in its own project (that is where its mops.toml and recipe live),
and then all the artifacts are deployed together from `e2e/`, which is a project whose only
job is to own one network and one id store.

Mainnet is never touched. `e2e/icp.yaml` declares only a `local` environment, and every
command below hard-codes `-e local`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
E2E = REPO / "e2e"
ENV = "local"  # never anything else, from this harness

sys.path.insert(0, str(REPO / "scripts" / "lib"))
import icp_helpers  # noqa: E402

# Every icp_helpers call must act on the e2e project: that is where the shared network and
# its id store live. Without this the helpers resolve the project from the CWD (the repo
# root), whose own network is not the one the app is deployed on.
icp_helpers.use_project(E2E)

# On the local network the admin is `default` -- the identity this harness deploys with.
# icp_helpers otherwise uses the machine's default identity, which for most developers is
# their MAINNET identity: it has no rights here, and calling as it returns
# `Err = Unauthorized`, which is easy to misread as "empty".
ADMIN_IDENTITY = "default"
icp_helpers.DEFAULT_IDENTITY = ADMIN_IDENTITY


@dataclass
class Canister:
    """A canister to build in its own project and deploy into the shared e2e network."""

    name: str
    project: str | None  # project dir to build in; None = nothing to build (asset canister)
    build_name: str | None = None  # canister name inside that project, if it differs
    init_args: str | None = None
    dynamic_args: str | None = None  # "deployer_principal" -> filled at install time
    depends_on: list[str] = field(default_factory=list)

    wasm_override: str | None = None  # for canisters with nothing to build

    @property
    def source(self) -> str:
        return self.build_name or self.name

    @property
    def wasm(self) -> Path:
        """The artifact to install.

        Passed to `icp canister install --wasm` explicitly rather than relying on the
        e2e project to stage it: the artifact is produced by the canister's OWN project,
        and pointing at it directly keeps the two steps independent.
        """
        if self.wasm_override:
            return REPO / self.wasm_override
        return REPO / self.project / ".icp/cache/artifacts" / self.source


# Deployment order matters: game_state and the controllers reference each other, and the
# registration step below wires them up once they all exist.
CANISTERS = [
    Canister("funnai_backend", "src/funnai_backend", dynamic_args="deployer_principal"),
    Canister("game_state_canister", "PoAIW/src/GameState"),
    Canister("api_canister", "PoAIW/src/Api"),
    Canister("challenger_ctrlb_canister", "PoAIW/src/Challenger"),
    Canister("judge_ctrlb_canister", "PoAIW/src/Judge"),
    Canister("mainer_creator_canister", "PoAIW/src/mAInerCreator"),
    Canister("funnai_treasury_canister", "PoAIW/src/Treasury"),
    Canister("archive_challenges_canister", "PoAIW/src/ArchiveChallenges"),
    # The threshold-ECDSA key name the icp-cli managed network provides. Verified: the
    # local replica exposes the same `dfx_test_key` the dfx replica did.
    Canister("ck_signer_canister", "PoAIW/src/ckSigner", init_args='("dfx_test_key")'),
    Canister("mainer_service_canister", "PoAIW/src/mAIner"),
    Canister("mainer_ctrlb_canister_0", "PoAIW/src/mAIner", build_name="mainer_service_canister"),
    # Vendored llama_cpp wasm; nothing to build.
    Canister("llm_0", None, wasm_override="PoAIW/llms/llama_cpp_canister/build/llama_cpp.wasm"),
]

FRONTEND = Canister("funnai_frontend", None)

# `icp deploy` seeds a new canister with only ~0.5T cycles. Uploading a gguf and calling
# load_model traps with IC0207 (out of cycles) well before that runs out of instructions.
LLM_CYCLES = 20_000_000_000_000

GGUF = REPO / "PoAIW/llms/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf"


# ---------------------------------------------------------------------------------------
# shell helpers
# ---------------------------------------------------------------------------------------
def run(cmd: str, cwd: Path = E2E, check: bool = True, quiet: bool = False) -> str:
    """Run a command with stdin closed (icp prompts interactively when args are missing)."""
    if not quiet:
        print(f"  $ {cmd}")
    p = subprocess.run(
        cmd, shell=True, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL
    )
    if check and p.returncode != 0:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise SystemExit(f"command failed: {cmd}")
    return p.stdout.strip()


def icp(args: str, cwd: Path = E2E, check: bool = True, quiet: bool = False) -> str:
    """Run an `icp` command as the local admin.

    The identity is named explicitly rather than made the machine default: switching the
    default is global and persistent, and would clobber the identity used for mainnet work.
    """
    if "--identity" not in args and not args.split(" ")[0] in ("identity", "network"):
        args = f"{args} --identity {ADMIN_IDENTITY}"
    return run(f"icp {args}", cwd=cwd, check=check, quiet=quiet)


def banner(msg: str) -> None:
    print(f"\n{'=' * 78}\n{msg}\n{'=' * 78}")


def network_url() -> str:
    return json.loads(icp(f"network status -e {ENV} --json", quiet=True))["gateway_url"].rstrip("/")


def canister_id(name: str) -> str | None:
    out = icp(f"canister status {name} -e {ENV} --id-only", check=False, quiet=True)
    return out or None


# ---------------------------------------------------------------------------------------
# up
# ---------------------------------------------------------------------------------------
def bootstrap_identities() -> str:
    """Create the fixed test identities.

    icp-cli does not create a `default` identity the way dfx did, and icpp-pro's pytest
    fixtures need one to EXIST. `--storage plaintext` is required, not cosmetic: a
    keyring-backed identity makes `icp identity export` open a password prompt and hang.

    The identities are created but the machine default is NOT changed: `icp identity
    default <x>` is global and persistent, so switching here would clobber the identity you
    use for mainnet work. Local commands name the admin explicitly instead.
    """
    banner("identities")
    for ident in (ADMIN_IDENTITY, "e2e-player"):
        run(f"icp identity new {ident} --storage plaintext", check=False, quiet=True)
    principal = icp(f"identity principal --identity {ADMIN_IDENTITY}", quiet=True)
    print(f"  admin  : {ADMIN_IDENTITY:<12}{principal}")
    print(f"  player : e2e-player  {icp('identity principal --identity e2e-player', quiet=True)}")
    return principal


def build_all() -> None:
    """Build each canister in its OWN project -- that is where its recipe and mops.toml are."""
    banner("build (each canister in its own project)")
    built: set[tuple[str, str]] = set()
    for c in CANISTERS:
        if not c.project or (c.project, c.source) in built:
            continue
        icp(f"build {c.source} -e prd", cwd=REPO / c.project)
        built.add((c.project, c.source))


def start_network(clean: bool) -> None:
    banner("local network")
    icp("network stop", check=False, quiet=True)
    if clean:
        # There is no `--clean`. Only the cache is disposable -- NEVER remove .icp itself,
        # which in the production projects holds the mainnet id mappings.
        run("rm -rf .icp/cache", quiet=True)
    icp("network start -d")
    print(f"  gateway: {network_url()}")


def deploy_all(deployer: str) -> None:
    banner("deploy canisters")
    for c in CANISTERS:
        icp(f"canister create {c.name} -e {ENV}", check=False, quiet=True)
        cid = canister_id(c.name)
        args = c.init_args
        if c.dynamic_args == "deployer_principal":
            args = f'( principal "{deployer}" )'
        extra = f" --args '{args}'" if args else ""
        icp(
            f"canister install {c.name} --wasm {c.wasm} -m install -e {ENV} -y{extra}",
            quiet=True,
        )
        print(f"  {c.name:<30} {cid}")


def fund_llm() -> None:
    banner("fund the LLM canister")
    cid = canister_id("llm_0")
    icp(f"canister top-up {cid} --amount {LLM_CYCLES} -e {ENV}")
    print(f"  llm_0 topped up to ~{LLM_CYCLES / 1e12:.0f}T cycles")


def load_model() -> None:
    """Upload the gguf and load it. This is the slowest step by far."""
    banner("LLM model")
    if not GGUF.exists():
        print(f"  SKIPPED: {GGUF} not found")
        print("  The challenge/response/judging flows will not work without it.")
        return
    cid = canister_id("llm_0")
    llama = REPO / "PoAIW/llms/llama_cpp_canister"
    # The vendored uploader is icp-native (v0.16.0+), but it resolves the network from ITS
    # OWN project -- which has no running network. ICP_PROJECT_ROOT points icp at the e2e
    # project, where the app actually lives.
    run(
        f"ICP_PROJECT_ROOT={E2E} python -m scripts.upload --network {ENV} "
        f"--canister-id {cid} --canister-filename models/model.gguf {GGUF}",
        cwd=llama,
    )
    icp(
        f"canister call {cid} load_model "
        f"'(record {{ args = vec {{\"--model\"; \"models/model.gguf\"}} }})' -e {ENV}"
    )
    icp(
        f"canister call {cid} set_max_tokens "
        f"'(record {{ max_tokens_query = 12 : nat64; max_tokens_update = 12 : nat64 }})' -e {ENV}"
    )
    print("  model loaded")


def wire_up() -> None:
    """Register the canisters with each other.

    Mirrors scripts/scripts-gamestate/register-all.sh, which is the source of truth for
    what the real deploy wires together.

    ORDER MATTERS: a controller must be an admin of the LLM (and one of its canister
    controllers) *before* `add_llm_canister` will accept it. Doing it the other way round
    leaves an empty llmCanisterIds and no error unless you check the response -- which is
    why every call below is checked.
    """
    banner("wire canisters together")
    gs = canister_id("game_state_canister")
    llm = canister_id("llm_0")

    def call(target: str, method: str, arg: str = "()") -> None:
        out = icp(f"canister call {target} {method} '{arg}' -e {ENV}", quiet=True)
        if "status_code = 200" not in out and "Ok" not in out:
            raise SystemExit(f"wiring failed: {method} on {target} returned {out!r}")

    for ctrlb in ("challenger_ctrlb_canister", "judge_ctrlb_canister"):
        cid = canister_id(ctrlb)
        call(cid, "setGameStateCanisterId", f'("{gs}")')

        # 1. give the controller access to the LLM ...
        call(
            llm,
            "assignAdminRole",
            f'(record {{ "principal" = "{cid}"; role = variant {{ AdminUpdate }}; '
            f'note = "{ctrlb}" }})',
        )
        icp(f"canister settings update {llm} --add-controller {cid} -e {ENV}", quiet=True)

        # 2. ... and only then register it, which verifies that access.
        call(cid, "reset_llm_canisters")
        call(cid, "add_llm_canister", f'(record {{ canister_id = "{llm}" }})')
        call(cid, "checkAccessToLLMs")
        print(f"  {ctrlb:<30} -> game_state + llm_0")


def build_frontend() -> None:
    """Build the Svelte app straight into e2e/dist.

    Not ../dist: the asset-canister sync plugin refuses a `dir` containing '..'.
    """
    banner("frontend")
    run("ICP_ENV=local npx vite build --outDir e2e/dist --emptyOutDir", cwd=REPO)
    icp(f"deploy {FRONTEND.name} -e {ENV} -y")


def cmd_up(args: argparse.Namespace) -> None:
    t0 = time.time()
    start_network(clean=args.clean)
    deployer = bootstrap_identities()
    build_all()
    deploy_all(deployer)
    fund_llm()
    wire_up()
    if not args.skip_model:
        load_model()
    if not args.skip_frontend:
        build_frontend()
    cmd_status(args)
    print(f"\ne2e environment ready in {time.time() - t0:.0f}s")


# ---------------------------------------------------------------------------------------
# status / down
# ---------------------------------------------------------------------------------------
def cmd_status(_args: argparse.Namespace) -> None:
    banner("status")
    try:
        url = network_url()
    except Exception:
        print("  local network is NOT running -- `make e2e-up`")
        return
    print(f"  gateway    : {url}")
    print(f"  internet id: {url.replace('//', '//id.ai.')}/authorize")
    fid = canister_id("funnai_frontend")
    if fid:
        port = url.rsplit(":", 1)[-1]
        print(f"  frontend   : http://{FRONTEND.name}.local.localhost:{port}/")
    print()
    for c in CANISTERS + [FRONTEND]:
        cid = canister_id(c.name)
        if not cid:
            print(f"  {c.name:<30} {'-':<30} not deployed")
            continue
        health = icp(
            f"canister call {cid} health '()' -e {ENV} --query", check=False, quiet=True
        )
        ok = "OK" if "status_code = 200" in health else ("-" if not health else "?")
        print(f"  {c.name:<30} {cid:<30} {ok}")


# ---------------------------------------------------------------------------------------
# test
# ---------------------------------------------------------------------------------------
def _check(name: str, fn) -> bool:
    try:
        ok, detail = fn()
    except Exception as e:  # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:<48} {detail}")
    return ok


def cmd_test(_args: argparse.Namespace) -> None:
    """System-level checks: the canisters as a wired-together application.

    The per-canister unit suites are `make smoketest` in each project; they prove a
    canister works in isolation. These prove the parts found each other.
    """
    banner("end-to-end checks")
    results = []

    for c in CANISTERS:
        cid = canister_id(c.name)
        results.append(_check(f"{c.name} is deployed", lambda cid=cid: (bool(cid), cid or "missing")))

    gs = canister_id("game_state_canister")
    llm = canister_id("llm_0")

    def health(cid):
        r = icp_helpers.call_text(cid, "health", "()", env=ENV, query=True)
        return ("status_code = 200" in (r or "")), (r or "no response")[:60]

    for name in ("game_state_canister", "challenger_ctrlb_canister", "judge_ctrlb_canister", "llm_0"):
        results.append(_check(f"{name} health", lambda n=name: health(canister_id(n))))

    def wired(ctrlb):
        data = icp_helpers.call(canister_id(ctrlb), "get_llm_canisters", env=ENV)
        # Surface an Err rather than letting `.get("Ok", {})` turn it into an empty list:
        # an Unauthorized response would otherwise look identical to "nothing registered".
        if "Ok" not in data:
            return False, f"unexpected response: {data}"
        ids = data["Ok"].get("llmCanisterIds", [])
        return (llm in ids), f"llmCanisterIds={ids}"

    for ctrlb in ("challenger_ctrlb_canister", "judge_ctrlb_canister"):
        results.append(_check(f"{ctrlb} knows llm_0", lambda c=ctrlb: wired(c)))

    def model_loaded():
        r = icp_helpers.call_text(llm, "ready", "()", env=ENV)
        return ("status_code = 200" in (r or "")), (r or "no response")[:60]

    results.append(_check("llm_0 has a model loaded (ready)", model_loaded))

    def frontend_serves():
        port = network_url().rsplit(":", 1)[-1]
        url = f"http://funnai_frontend.local.localhost:{port}/"
        code = run(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", quiet=True)
        return (code == "200"), f"{url} -> {code}"

    results.append(_check("frontend serves index.html", frontend_serves))

    passed = sum(1 for r in results if r)
    print(f"\n  {passed}/{len(results)} checks passed")
    if passed != len(results):
        raise SystemExit(1)


def cmd_down(_args: argparse.Namespace) -> None:
    banner("stopping local network")
    icp("network stop", check=False)


def cmd_reset(args: argparse.Namespace) -> None:
    args.clean = True
    cmd_up(args)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("up", cmd_up), ("status", cmd_status), ("down", cmd_down),
                     ("reset", cmd_reset), ("test", cmd_test)]:
        p = sub.add_parser(name)
        p.set_defaults(func=fn)
        if name in ("up", "reset"):
            p.add_argument("--clean", action="store_true", help="wipe .icp/cache first")
            p.add_argument("--skip-model", action="store_true", help="skip the slow gguf upload")
            p.add_argument("--skip-frontend", action="store_true")
    args = ap.parse_args()
    for opt in ("clean", "skip_model", "skip_frontend"):
        setattr(args, opt, getattr(args, opt, False))
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
