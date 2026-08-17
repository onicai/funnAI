#!/usr/bin/env python3
"""Stand up the whole funnAI application on a single local network.

Network lifecycle and canister deployment are separate concerns, so they are separate
commands. The deploy commands refuse to run if the network is down rather than starting it
for you -- so you always know which state you started from.

    python -m scripts.e2e.harness start        # start, reusing cached state
    python -m scripts.e2e.harness start-clean  # wipe .icp/cache, then start

    python -m scripts.e2e.harness install      # -m install   (canisters must be empty)
    python -m scripts.e2e.harness reinstall    # -m reinstall (wipes canister state)
    python -m scripts.e2e.harness upgrade      # -m upgrade   (keeps canister state)

    python -m scripts.e2e.harness status       # one-screen health summary
    python -m scripts.e2e.harness test         # backend pytest suites
    python -m scripts.e2e.harness stop         # stop the network; deletes nothing
    python -m scripts.e2e.harness clean        # stop + remove ALL disposable local state

Which deploy mode?
------------------
`install` only works on an empty canister, so it is for the first deploy onto a fresh
network. `reinstall` wipes each canister and installs fresh -- including the LLM's uploaded
model file, so the gguf has to be uploaded again. `upgrade` keeps stable state, so the gguf
survives and is not re-uploaded; pass --skip-model on install/reinstall if you do not need
inference and want to skip that slow step.

mAIners are bought, not installed
---------------------------------
Every canister in CANISTERS is deployed with `icp canister install`. ShareAgent mAIners are
not: in production a player pays for one and GameState asks mAInerCreator to create it
through the cycles-minting canister. The local network runs the real CMC and the real ICP
ledger at their mainnet ids, so that whole path works here -- and the harness uses it, which
is why a ShareAgent has no entry in e2e/icp.yaml and its id comes from GameState.

    --share-agents N    how many the player should own (default 1)

That means the three deploy modes do different things to the fleet: `install` buys them,
`upgrade` upgrades them through mAInerCreator, and `reinstall` would re-install them the
same way -- except that reinstalling game_state_canister wipes its record of every mAIner,
so there is nothing left to point at and fresh ones are bought instead.

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
import hashlib
import json
import re
import shutil
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

# The admin of the local network -- the identity this harness deploys with.
#
# Named for the project rather than called `default`, because "the default identity" would
# then mean two different things: this one, and whatever `icp identity default` reports --
# which for most developers is their MAINNET identity. Commands like
# `icp identity default default` are the kind of thing that costs an afternoon.
#
# Setting icp_helpers.DEFAULT_IDENTITY matters for the same reason: without it the helpers
# fall back to the machine default, which has no rights here and returns
# `Err = Unauthorized` -- easy to misread as "empty result".
ADMIN_IDENTITY = "funnAI-local"
icp_helpers.DEFAULT_IDENTITY = ADMIN_IDENTITY

# The variable the ic-py based uploaders read to decide whose key to sign with. It is
# icpp-pro's, and llama_cpp_canister adopted it in 0.16.1 -- so one name covers the pytest
# suites and both file uploaders.
#
# NOT to be confused with funnAI's own `ICP_IDENTITY` (scripts/lib/icp_helpers.py), which
# only means something inside funnAI's scripts. icp-cli itself reads neither.
UPLOADER_IDENTITY_ENV = "ICPP_PRO_TEST_IDENTITY"


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

    # Motoko canisters here are built with enhanced orthogonal persistence, so an upgrade
    # takes `--wasm-memory-persistence keep`. The LLM is C++ (icpp-pro), and passing that
    # flag to it is a hard error: "the target canister is not an EOP canister".
    eop: bool = True

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

    @property
    def docker_wasm(self) -> Path:
        """The Docker-built artifact -- `make docker-build-wasm` writes out/<name>.wasm.

        A vendored wasm (the LLM) is already a released binary, so there is nothing to
        build reproducibly and the override wins in both modes.
        """
        if self.wasm_override:
            return REPO / self.wasm_override
        return REPO / self.project / "out" / f"{self.source}.wasm"


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
    # ck_signer_canister is deliberately absent: it is not used by funnAI, so deploying it
    # here only lengthened the deploy and added a canister that could fail for reasons nobody
    # depends on. It keeps its own project and smoke tests in PoAIW/src/ckSigner/.
    #
    # The ShareService. The ShareAgents that talk to it are NOT listed here: they are not
    # deployed with `icp canister install` at all. In production a player buys one and
    # GameState asks mAInerCreator to create it, and this harness does exactly that -- see
    # create_share_agents(). Their ids therefore come from the CMC, not from e2e/icp.yaml.
    Canister("mainer_service_canister", "PoAIW/src/mAIner"),
    # Vendored llama_cpp wasm; nothing to build.
    Canister("llm_0", None, wasm_override="PoAIW/llms/llama_cpp_canister/build/llama_cpp.wasm",
             eop=False),
]

FRONTEND = Canister("funnai_frontend", None)

# `icp deploy` seeds a new canister with only ~0.5T cycles. Uploading a gguf and calling
# load_model traps with IC0207 (out of cycles) well before that runs out of instructions.
LLM_CYCLES = 20_000_000_000_000

GGUF = REPO / "PoAIW/llms/models/Qwen/Qwen2.5-0.5B-Instruct-GGUF/qwen2.5-0.5b-instruct-q8_0.gguf"

# --- ShareAgent creation --------------------------------------------------------------
#
# The local network runs the REAL cycles-minting canister and the REAL ICP ledger, at their
# mainnet ids, so a mAIner can be bought here exactly the way a player buys one in
# production: pay ICP to GameState, then have GameState ask mAInerCreator to create the
# canister through the CMC.
CMC = "rkp4c-7iaaa-aaaaa-aaaca-cai"

# The player who buys the mAIners. Deliberately NOT the admin identity: the buy path is
# gated on ownership, so using the admin would skip the RBAC this is meant to exercise.
PLAYER_IDENTITY = "e2e-player"

# What a ShareAgent costs. `icp token transfer` takes whole ICP, and every local identity is
# seeded with 1,000,000 ICP, so this is free in every sense that matters.
SHARE_AGENT_ICP = 10

# GameState pays for each canister the CMC creates out of its own cycles balance.
GS_CYCLES_PER_AGENT = 10_000_000_000_000

# The mAIner wasm mAInerCreator installs. `IC0.upload_chunk` caps a chunk at 1 MB, which is
# below the 2 MB the canister itself would accept -- so this, not the canister, sets it.
MAINER_WASM_CHUNK = 1_000_000

# Once bought, each ShareAgent is put up for sale, so that a human signed in through the
# browser can buy it and end up OWNING a mAIner in the UI. Without this the only owner is
# the `e2e-player` PEM key, which no browser session can ever be.
MARKETPLACE_PRICE_E8S = 100_000_000  # 1 ICP; the contract's floor is 1_000_000 (0.01 ICP)


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
    # `build` compiles locally and takes no identity; passing one is a hard error.
    if "--identity" not in args and not args.split(" ")[0] in ("identity", "network", "build"):
        args = f"{args} --identity {ADMIN_IDENTITY}"
    return run(f"icp {args}", cwd=cwd, check=check, quiet=quiet)


def banner(msg: str) -> None:
    print(f"\n{'=' * 78}\n{msg}\n{'=' * 78}")


def network_url() -> str:
    return json.loads(icp(f"network status -e {ENV} --json", quiet=True))["gateway_url"].rstrip("/")


def canister_id(name: str) -> str | None:
    out = icp(f"canister status {name} -e {ENV} --id-only", check=False, quiet=True)
    return out or None


def local_subnet() -> str:
    """The single subnet of the local network, straight from the CMC.

    Hard-coding it is not an option: it is derived from the replica's own key material and
    so changes every time `.icp/cache` is wiped. GameState ships the MAINNET subnet ids in
    its defaults, and creating a mAIner against one of those on a local network fails deep
    inside the CMC with an error that says nothing about subnets.
    """
    out = icp(f"canister call {CMC} get_default_subnets '()' -e {ENV} --query", quiet=True)
    m = re.search(r'principal\s+"([^"]+)"', out)
    if not m:
        raise SystemExit(f"could not read the local subnet from the CMC: {out!r}")
    return m.group(1)


def ok_record(out: str) -> str:
    """Pull the `record { ... }` out of a `(variant { Ok = record { ... } })` response.

    Brace-counted rather than regexed: the mAIner record nests several levels deep, and a
    non-greedy match stops at the first inner `}`.

    Used to feed the record `createUserMainerAgent` returns straight back into
    `spinUpMainerControllerCanister`, which is what the frontend does too.
    """
    i = out.find("Ok = record")
    if i < 0:
        raise SystemExit(f"expected an Ok record, got: {out!r}")
    start = out.index("record", i)
    depth, j = 0, out.index("{", start)
    for j in range(j, len(out)):
        if out[j] == "{":
            depth += 1
        elif out[j] == "}":
            depth -= 1
            if depth == 0:
                return out[start : j + 1]
    raise SystemExit(f"unbalanced record in response: {out!r}")


# ---------------------------------------------------------------------------------------
# up
# ---------------------------------------------------------------------------------------
def bootstrap_identities() -> str:
    """Create the fixed local identities. None of them is your mainnet identity.

    `--storage plaintext` is required, not cosmetic: a keyring-backed identity makes
    `icp identity export` open a password prompt and hang, and the file uploaders export the
    identity in order to sign locally.

    The machine default is NOT changed: `icp identity default <x>` is global and
    persistent, so switching here would clobber the identity you use for mainnet work.
    Every command below names its identity explicitly instead.
    """
    banner("identities")
    for ident in (ADMIN_IDENTITY, "e2e-player"):
        run(f"icp identity new {ident} --storage plaintext", check=False, quiet=True)

    def show(label: str, ident: str, note: str = "") -> None:
        principal = icp(f"identity principal --identity {ident}", quiet=True)
        print(f"  {label:<8}: {ident:<14}{principal}  {note}")

    principal = icp(f"identity principal --identity {ADMIN_IDENTITY}", quiet=True)
    show("admin", ADMIN_IDENTITY, "deploys everything, holds the admin roles")
    show("player", "e2e-player", "buys mAIners; exercises the non-admin paths")
    print(f"\n  Your machine default is '{icp('identity default', quiet=True)}' and is left")
    print("  untouched -- it is not used here and has no rights on this network.")
    return principal


def build_all(docker: bool = True, keep_base: bool = False) -> None:
    """Build each canister in its OWN project -- that is where its recipe and mops.toml are.

    Two build paths, and they do NOT produce identical bytes:

    * default -- `icp build`, the local toolchain. Fast, and what you want in a dev loop.
    * docker  -- `make docker-build-wasm`, the reproducible build. This is the CANONICAL
      artifact: it is what WASM-HASHES.md records and what `verify-wasm` checks. On
      anything other than linux/amd64 the local build differs from it (the `moc:version`
      metadata), so a hash produced locally will not match.

    Docker is the DEFAULT: measured cold, a full install is 295s with it against 133s
    without, and 162s is a cheap price for deploying the same bytes the release pipeline
    produces. `--no-cache` only busts the wasm layer -- the base image and dependency
    layers stay cached, so each canister costs ~20s rather than minutes.

    Pass --no-docker (make NO_DOCKER=1) to fall back to the local toolchain when Docker is
    unavailable or you are iterating hard and do not care about the hash.
    """
    banner("build (docker, reproducible)" if docker else "build (local toolchain)")
    if docker and run("docker info >/dev/null 2>&1 && echo up", check=False, quiet=True) != "up":
        raise SystemExit(
            "Docker is not running, and the reproducible build is the default.\n"
            "Start Docker Desktop and re-run, or use NO_DOCKER=1 to build with the local\n"
            "toolchain instead (faster, but the wasm is machine-dependent)."
        )

    # Before anything is compiled, so the toolchain the canisters build in is rebuilt from
    # the current Dockerfile rather than whatever image happens to be lying around. Each
    # project's `docker-build-wasm` notices the image is gone and rebuilds it.
    if docker and not keep_base:
        drop_base_images()

    targets = [c for c in CANISTERS if c.project]
    for i, c in enumerate(targets, 1):
        # `make docker-build-wasm` is the SAME command in every project, so printing the
        # command alone (which is what run() does) gives an unreadable column of identical
        # lines. Name the canister and its project instead, and stay quiet about the
        # command itself -- run() still dumps everything if the build fails.
        print(f"  [{i}/{len(targets)}] {c.source:<30} {c.project}")
        if docker:
            run("make docker-build-wasm", cwd=REPO / c.project, quiet=True)
        else:
            icp(f"build {c.source} -e prd", cwd=REPO / c.project, quiet=True)

        # Show the hash. With the reproducible build as the default, this is the number
        # WASM-HASHES.md records, so it is worth seeing without a separate command.
        wasm = c.docker_wasm if docker else c.wasm
        if wasm.exists():
            digest = hashlib.sha256(wasm.read_bytes()).hexdigest()
            print(f"           sha256 {digest}")
        else:
            print(f"           WARNING: expected artifact not found at {wasm}")


def base_images() -> list[str]:
    """The pinned toolchain images the canisters are built inside.

    Read from each project's docker-compose.yml rather than listed here, because that file
    already pins the tool versions the image NAME encodes
    (`poaiw-build:icp-1.2.0-moc-1.4.1`) -- a second copy would drift the moment someone
    bumps moc.
    """
    names: list[str] = []
    for c in CANISTERS:
        if not c.project:
            continue
        compose = REPO / c.project / "docker/docker-compose.yml"
        if not compose.exists():
            continue
        m = re.search(r'^\s*name: &base_name "(.+)"', compose.read_text(), re.M)
        if m and m.group(1) not in names:
            names.append(m.group(1))
    return names


def drop_base_images() -> None:
    """Delete the toolchain images so the next build has to rebuild them from Dockerfile.

    The image tag encodes the pinned tool versions, so a version bump already produces a
    new name and therefore a fresh image. What that does NOT catch is an edit to
    Dockerfile.base that leaves the versions alone -- the stale image keeps its name and is
    silently reused. Removing them every deploy closes that gap: what you build in is
    always what the Dockerfile currently says.

    Measured cost: ~150s added to a full deploy (458s -> 611s). That is for BOTH images, not
    each -- the two Dockerfile.base files are near-identical, so the second image reuses the
    first's layers almost entirely. `make e2e-* KEEP_BASE=1` skips it for a fast iteration
    loop; the canister wasm is the canonical artifact either way, because the tool versions
    are pinned regardless.
    """
    images = base_images()
    if not images:
        return
    banner("drop the toolchain base images (they will be rebuilt)")
    for img in images:
        # `docker images -q`, not `image inspect`: inspect prints "[]" on stdout for a
        # missing image, which is a truthy string, so it would report every image as having
        # been removed.
        existed = run(f"docker images -q {img}", check=False, quiet=True)
        run(f"docker image rm -f {img}", check=False, quiet=True)
        print(f"  {img:<40} {'removed' if existed else 'was not present'}")
    # The rebuild happens inside the first `make docker-build-wasm`, whose output is
    # captured, so without this the first canister just sits there for ~150s with nothing
    # on screen to say why.
    print("\n  The next canister build rebuilds them from Dockerfile.base (~150s, once).")


def start_network(clean: bool) -> None:
    # BEFORE the network starts, not after: the ledger is seeded with 1,000,000 ICP for
    # every identity that exists at that moment, and an identity created later gets nothing.
    # Since the player BUYS its mAIners with real local ICP, creating it at deploy time
    # would leave it with a zero balance on a developer's very first run.
    bootstrap_identities()

    banner("local network")
    icp("network stop", check=False, quiet=True)
    if clean:
        # There is no `--clean`. Only the cache is disposable -- NEVER remove .icp itself,
        # which in the production projects holds the mainnet id mappings.
        run("rm -rf .icp/cache", quiet=True)
    icp("network start -d")
    print(f"  gateway: {network_url()}")


def require_network() -> None:
    """Fail fast if the network is down.

    The deploy commands deliberately do NOT start it: keeping lifecycle and deployment
    separate is what makes it obvious whether you are deploying onto reused state or a
    clean replica.
    """
    # check=False: run() raises SystemExit on failure, which is a BaseException and would
    # bypass a normal except -- and it dumps the raw icp error, which is what this replaces.
    out = icp(f"network status -e {ENV} --json", check=False, quiet=True)
    if "gateway_url" not in out:
        raise SystemExit(
            "The local network is not running.\n"
            "  make e2e-start         reuse the cached state\n"
            "  make e2e-start-clean   wipe it and start fresh"
        )


def deploy_all(deployer: str, mode: str, docker: bool = True) -> None:
    """Install every canister in the given mode.

    `--wasm-memory-persistence keep` is only valid with `-m upgrade`, and is what the
    production runbook uses for the Motoko canisters (enhanced orthogonal persistence).
    """
    banner(f"deploy canisters (-m {mode})")
    for c in CANISTERS:
        persistence = " --wasm-memory-persistence keep" if mode == "upgrade" and c.eop else ""
        icp(f"canister create {c.name} -e {ENV}", check=False, quiet=True)
        cid = canister_id(c.name)
        args = c.init_args
        if c.dynamic_args == "deployer_principal":
            args = f'( principal "{deployer}" )'
        # Init args are required on EVERY mode, upgrade included: a Motoko actor class with
        # constructor parameters decodes them on upgrade too, and omitting them traps with
        # "IDL error: too few arguments".
        extra = f" --args '{args}'" if args else ""
        wasm = c.docker_wasm if docker else c.wasm
        icp(
            f"canister install {c.name} --wasm {wasm} -m {mode} -e {ENV} -y"
            f"{persistence}{extra}",
            quiet=True,
        )
        print(f"  {c.name:<30} {cid}")

    # Production runs one LLM per controller; locally there is one model, loaded once, and
    # the challenger, the judge and the ShareService all point at it. Saying so here stops
    # `llm_0` reading like the challenger's private LLM.
    print("\n  llm_0 is shared: challenger_ctrlb, judge_ctrlb and mainer_service (the")
    print("  ShareService) are all wired to this one LLM canister.")


def fund_llm() -> None:
    banner("fund the LLM canister")
    cid = canister_id("llm_0")
    icp(f"canister top-up {cid} --amount {LLM_CYCLES} -e {ENV}")
    print(f"  llm_0 topped up to ~{LLM_CYCLES / 1e12:.0f}T cycles")


def upload_gguf() -> bool:
    """Upload the gguf into the LLM canister. The slowest step by far.

    Only needed after `install` or `reinstall`: both leave the canister's file storage
    empty. An `upgrade` keeps stable memory, so the model file is still there -- which is
    what README-prd-upgrade-commands.md means by "`--mode reinstall` wipes the stable
    state; the wasm/model uploads re-populate the canister files".

    Returns False if the gguf is missing, so the caller can skip activation too.
    """
    banner("LLM model upload")
    if not GGUF.exists():
        print(f"  SKIPPED: {GGUF} not found")
        print("  The challenge/response/judging flows will not work without it.")
        return False
    cid = canister_id("llm_0")
    llama = REPO / "PoAIW/llms/llama_cpp_canister"

    # $ICPP_PRO_TEST_IDENTITY makes the uploader act as the local admin.
    #
    # scripts/ic_py_canister.py resolves the identity itself and then EXPORTS ITS PRIVATE
    # KEY, because icp-py-core signs locally. Left to its own devices it takes the machine
    # default -- for most developers the identity they use on mainnet -- so a local gguf
    # upload would pull a production key out of the OS keychain for no reason. It also has
    # no rights here, so the upload failed with `Err = Other("Access Denied")`, which reads
    # like a broken upload rather than an identity mismatch.
    #
    # llama_cpp_canister 0.16.1+ reads this variable, so this is a supported interface
    # rather than the local patch it used to be.
    #
    # ICP_PROJECT_ROOT is separate: the uploader would otherwise resolve the network from
    # ITS OWN project, which has none running.
    run(
        f"ICP_PROJECT_ROOT={E2E} {UPLOADER_IDENTITY_ENV}={ADMIN_IDENTITY} "
        f"python -m scripts.upload --network {ENV} "
        f"--canister-id {cid} --canister-filename models/model.gguf {GGUF}",
        cwd=llama,
    )
    print("  gguf uploaded")
    return True


def activate_model() -> None:
    """Load the uploaded model into working memory and cap the token counts.

    Needed after EVERY deploy, including `upgrade`: the model FILE lives in stable memory
    and survives, but the loaded model is heap state and does not. Calling this when the
    model is already loaded simply reloads it.
    """
    banner("LLM model activation")
    cid = canister_id("llm_0")
    # check=False: the canister may hold no model at all -- an environment brought up with
    # --skip-model never uploaded one. That is a legitimate state, not a failure, so say so
    # and carry on rather than aborting the whole deploy.
    out = icp(
        f"canister call {cid} load_model "
        f"'(record {{ args = vec {{\"--model\"; \"models/model.gguf\"}} }})' -e {ENV}",
        check=False,
    )
    if "status_code = 200" not in out and "Ok" not in out:
        print("  no model to load -- the canister has no models/model.gguf.")
        print("  Deploy with the gguf (omit NO_GGUF=1) if you need inference.")
        return
    icp(
        f"canister call {cid} set_max_tokens "
        f"'(record {{ max_tokens_query = 12 : nat64; max_tokens_update = 12 : nat64 }})' -e {ENV}"
    )
    print("  model loaded")


def call(target: str, method: str, arg: str = "()", identity: str | None = None) -> str:
    """Make an update call and INSIST that it succeeded.

    Several of the setters below return `#Err(#Unauthorized)` rather than trapping, and one
    (`addMainerShareAgentCanister`) swallows its own error entirely. An unchecked call
    against any of them leaves a half-wired fleet that only shows up much later as an empty
    list or a silently idle mAIner -- so nothing here is left unchecked.
    """
    ident = f" --identity {identity}" if identity else ""
    out = icp(f"canister call {target} {method} '{arg}' -e {ENV}{ident}", quiet=True)
    if "status_code = 200" not in out and "Ok" not in out:
        raise SystemExit(f"{method} on {target} returned {out!r}")
    return out


def grant_llm_access(llm: str, cid: str, note: str) -> None:
    """Give a controller access to the LLM canister and register it there.

    ORDER MATTERS: the caller must be an admin of the LLM (and one of its canister
    controllers) *before* `add_llm_canister` will accept it. The other way round leaves an
    empty llmCanisterIds and no error at all unless the response is checked --
    `checkAccessToLLMs` is the only call here that actually proves the link works.
    """
    call(
        llm,
        "assignAdminRole",
        f'(record {{ "principal" = "{cid}"; role = variant {{ AdminUpdate }}; '
        f'note = "{note}" }})',
    )
    icp(f"canister settings update {llm} --add-controller {cid} -e {ENV}", quiet=True)
    call(cid, "reset_llm_canisters")
    call(cid, "add_llm_canister", f'(record {{ canister_id = "{llm}" }})')
    call(cid, "checkAccessToLLMs")


def official_mainer_record(address: str, subnet: str, subtype: str, owner: str) -> str:
    """The `OfficialMainerAgentCanister` record GameState's registries expect.

    Only used for the ShareService, which this harness deploys by hand and therefore has to
    register by hand. A ShareAgent's record is produced by GameState itself.
    """
    return (
        f'record {{ address = "{address}"; subnet = "{subnet}"; '
        f"canisterType = variant {{ MainerAgent = variant {{ {subtype} }} }}; "
        f"creationTimestamp = 1 : nat64; "
        f'createdBy = principal "{owner}"; ownedBy = principal "{owner}"; '
        f"status = variant {{ Running }}; "
        f"mainerConfig = record {{ mainerAgentCanisterType = variant {{ {subtype} }}; "
        f"selectedLLM = opt variant {{ Qwen2_5_500M }}; cyclesForMainer = 0 : nat; "
        f'subnetCtrl = "{subnet}"; subnetLlm = "{subnet}"; }} }}'
    )


def wire_up(share_agents_wanted: int) -> None:
    """Register the canisters with each other.

    Mirrors scripts/scripts-gamestate/register-all.sh, which is the source of truth for
    what the real deploy wires together.

    Everything here is idempotent, so it runs on every deploy mode. That matters most after
    a reinstall, which wipes the state these calls write.
    """
    banner("wire canisters together")
    gs = canister_id("game_state_canister")
    mc = canister_id("mainer_creator_canister")
    ss = canister_id("mainer_service_canister")
    llm = canister_id("llm_0")
    admin = icp(f"identity principal --identity {ADMIN_IDENTITY}", quiet=True)
    subnet = local_subnet()

    for ctrlb in ("challenger_ctrlb_canister", "judge_ctrlb_canister"):
        cid = canister_id(ctrlb)
        call(cid, "setGameStateCanisterId", f'("{gs}")')
        grant_llm_access(llm, cid, ctrlb)
        print(f"  {ctrlb:<30} -> game_state + llm_0")

    # --- everything below exists so mAIners can be bought and created locally ----------

    # GameState ships the MAINNET subnet ids. Point them at the local subnet BEFORE any
    # mAIner is bought: spinUpMainerControllerCanister reads the subnet from the row that
    # createUserMainerAgent already wrote, so a row created against the wrong subnet keeps
    # it forever. setSubnetsAdmin silently ignores a value that is not a principal, hence
    # the read-back.
    call(
        gs,
        "setSubnetsAdmin",
        f'(record {{ subnetShareAgentCtrl = "{subnet}"; '
        f'subnetShareServiceCtrl = "{subnet}"; subnetShareServiceLlm = "{subnet}" }})',
    )
    if subnet not in icp(f"canister call {gs} getSubnetsAdmin '()' -e {ENV}", quiet=True):
        raise SystemExit(f"setSubnetsAdmin did not take: {subnet} is not in getSubnetsAdmin")
    print(f"  local subnet                   {subnet}")

    call(mc, "setMasterCanisterId", f'("{gs}")')
    call(
        gs,
        "addOfficialCanister",
        f'(record {{ address = "{mc}"; subnet = "{subnet}"; '
        f"canisterType = variant {{ MainerCreator }} }})",
    )
    print(f"  {'mainer_creator_canister':<30} <-> game_state")

    # The ShareService is an ordinary mAIner wasm that has to be TOLD it is the shared
    # service: mAIner/src/Main.mo defaults to #Own, and the #ShareAgent/#ShareService
    # branches never run until this is set.
    call(ss, "setMainerCanisterType", "(variant { ShareService })")
    call(ss, "setGameStateCanisterId", f'("{gs}")')

    # The ShareService is the only mAIner that runs inference; the agents just queue work on
    # it. So it reuses llm_0 rather than getting an LLM of its own -- the local network has
    # one model, loaded once.
    grant_llm_access(llm, ss, "mainer_service_canister")

    # In production mAInerCreator CREATES the ShareService and is therefore automatically
    # one of its controllers. Here the harness deployed it, so mAInerCreator has no rights
    # on it at all -- and addMainerShareAgentCanister, which registers each new agent with
    # the ShareService, is gated on #AdminUpdate. Without this the agents are created fine
    # and then never receive any work, because that registration fails SILENTLY (the
    # `return #Err` in mAInerCreator/src/Main.mo is commented out).
    icp(f"canister settings update {ss} --add-controller {mc} -e {ENV}", quiet=True)
    call(
        ss,
        "assignAdminRole",
        f'(record {{ "principal" = "{mc}"; role = variant {{ AdminUpdate }}; '
        f'note = "mainer_creator_canister" }})',
    )

    # Two separate registries, and both are read: addMainerAgentCanisterAdmin feeds the
    # mAIner bookkeeping, addOfficialCanister the protocol canister list.
    record = official_mainer_record(ss, subnet, "ShareService", admin)
    call(gs, "addMainerAgentCanisterAdmin", f"({record})")
    call(
        gs,
        "addOfficialCanister",
        f'(record {{ address = "{ss}"; subnet = "{subnet}"; '
        f"canisterType = variant {{ MainerAgent = variant {{ ShareService }} }} }})",
    )
    print(f"  {'mainer_service_canister':<30} is the ShareService -> game_state + llm_0")

    # An empty record sets no parameter, but still triggers the setCyclesFlow() recompute at
    # the end of the setter -- and it is that recompute the create/upgrade paths read. On a
    # fresh GameState the derived values are 0, so without this a mAIner is created and
    # upgraded with zero cycles attached.
    call(gs, "setCyclesFlowAdmin", "(record {})")

    # Off by default, and it blocks createUserMainerAgent outright.
    if "true" in icp(f"canister call {gs} getPauseProtocolFlag '()' -e {ENV} --query", quiet=True):
        call(gs, "togglePauseProtocolFlagAdmin")
        print("  protocol unpaused")

    call(
        gs,
        "setLimitForCreatingMainerAdmin",
        f"(record {{ mainerType = variant {{ ShareAgent }}; "
        f"newLimit = {max(share_agents_wanted, 10)} : nat }})",
    )

    # GameState pays the CMC for each canister it has created, out of its own balance.
    cycles = GS_CYCLES_PER_AGENT * max(share_agents_wanted, 1)
    icp(f"canister top-up {gs} --amount {cycles} -e {ENV}", quiet=True)
    print(
        f"  {'game_state_canister':<30} topped up with {cycles / 1e12:g}T cycles "
        f"({GS_CYCLES_PER_AGENT / 1e12:g}T x {share_agents_wanted} ShareAgent(s), to pay"
    )
    print(f"  {'':<30} the CMC for creating them)")


# ---------------------------------------------------------------------------------------
# ShareAgent mAIners -- created the way a player buys one, not with `icp canister install`
# ---------------------------------------------------------------------------------------
def upload_mainer_wasm(docker: bool = True) -> None:
    """Give mAInerCreator the wasm it installs into every mAIner it creates.

    This is the SAME artifact the harness installs as the ShareService; the two differ only
    in the canister type each is told to be.
    """
    banner("upload the mAIner wasm into mAInerCreator")
    mc = canister_id("mainer_creator_canister")
    mainer = next(c for c in CANISTERS if c.name == "mainer_service_canister")
    wasm = mainer.docker_wasm if docker else mainer.wasm
    creator = REPO / "PoAIW/src/mAInerCreator"
    candid = creator / "src/declarations/mainer_creator_canister/mainer_creator_canister.did"

    # Same variable and same reason as the gguf upload: this uploader is a copy of the same
    # ic-py machinery, so it also exports the identity's private key, and would otherwise
    # reach for the machine default -- a mainnet key -- which additionally is not a
    # controller here, so the upload endpoints (gated on Principal.isController) rejected it.
    # PoAIW owns this copy, and it was aligned to the same variable name upstream uses.
    #
    # The paths are absolute on purpose: the uploader resolves --wasm/--candid against its
    # own directory, and `files/mainer_ctrlb_canister.wasm` there is a COMMITTED artifact
    # that must not be overwritten with a local build.
    run(
        f"ICP_PROJECT_ROOT={E2E} {UPLOADER_IDENTITY_ENV}={ADMIN_IDENTITY} "
        f"python -m scripts.upload_mainer_controller_canister "
        f"--network {ENV} --canister mainer_creator_canister --canister_id {mc} "
        f"--wasm {wasm} --candid {candid} --chunksize {MAINER_WASM_CHUNK}",
        cwd=creator,
        quiet=True,
    )
    out = icp(f"canister call {mc} getSha256HashesAdmin '()' -e {ENV}", quiet=True)
    m = re.search(r'mainerControllerWasmSha256 = "([0-9a-f]+)"', out)
    local = hashlib.sha256(wasm.read_bytes()).hexdigest()
    if not m or m.group(1) != local:
        raise SystemExit(
            f"the wasm mAInerCreator stored does not match {wasm}\n"
            f"  in canister: {m.group(1) if m else '(none)'}\n"
            f"  on disk    : {local}"
        )
    print(f"  mainer wasm sha256 {local}")


def share_agents() -> list[str]:
    """The player's ShareAgents, as GameState knows them.

    GameState is the registry, so there is no state file to go stale. Note the consequence:
    `-m reinstall` wipes GameState's stable memory, and with it every mAIner it knew about.
    """
    gs = canister_id("game_state_canister")
    player = icp(f"identity principal --identity {PLAYER_IDENTITY}", quiet=True)
    out = icp(
        f'canister call {gs} getMainerAgentCanistersForUserAdmin \'("{player}")\' -e {ENV}',
        check=False,
        quiet=True,
    )
    return re.findall(r'address = "([a-z0-9-]+)"', out)


def wait_healthy(cid: str, what: str, timeout: int = 120) -> None:
    """Poll a mAIner until it answers `health`.

    GameState writes `status = #Running` OPTIMISTICALLY, before mAInerCreator has installed
    the wasm, so its status is not a completion signal. The canister answering for itself is.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        out = icp(f"canister call {cid} health '()' -e {ENV} --query", check=False, quiet=True)
        if "status_code = 200" in out:
            return
        time.sleep(2)
    raise SystemExit(f"{what} ({cid}) never became healthy within {timeout}s")


def create_share_agents(n: int) -> list[str]:
    """Buy n ShareAgents as the player, exactly the way the frontend does.

    Two calls, not one, and that split is the production flow rather than an artefact:
    `createUserMainerAgent` verifies the ICP payment and writes a `#Paid` row, and
    `spinUpMainerControllerCanister` then asks mAInerCreator to create the canister. The
    record the first returns is fed straight into the second.
    """
    banner(f"create {n} ShareAgent mAIner(s) via mAInerCreator")
    gs = canister_id("game_state_canister")
    created = []

    # The ledger seeds only the identities that existed when the network started. If this
    # network was started before `e2e-player` was created, the buy fails at the transfer
    # with a bare "insufficient funds", which says nothing about why.
    balance = icp(f"token balance -e {ENV} --identity {PLAYER_IDENTITY}", quiet=True)
    if float(re.search(r"([\d.]+)", balance).group(1)) < SHARE_AGENT_ICP * n:
        raise SystemExit(
            f"{PLAYER_IDENTITY} holds {balance}, which is not enough for {n} mAIner(s) at "
            f"{SHARE_AGENT_ICP} ICP each.\n"
            "The local ledger seeds only the identities that existed when the network\n"
            "started, so this identity missed the hand-out. Restart the network to seed it:\n"
            "  make e2e-start-clean && make e2e-install"
        )

    for i in range(1, n + 1):
        # Pay GameState in real (local) ICP. The ledger credits the default subaccount of
        # the GameState principal, which is the account createUserMainerAgent checks.
        block = icp(
            f"token transfer {SHARE_AGENT_ICP} {gs} -e {ENV} -q "
            f"--identity {PLAYER_IDENTITY}",
            quiet=True,
        )
        paid = call(
            gs,
            "createUserMainerAgent",
            f"(record {{ paymentTransactionBlockId = {block} : nat64; "
            f"mainerConfig = record {{ mainerAgentCanisterType = variant {{ ShareAgent }}; "
            f"selectedLLM = opt variant {{ Qwen2_5_500M }}; cyclesForMainer = 0 : nat; "
            f'subnetCtrl = ""; subnetLlm = ""; }}; }})',
            identity=PLAYER_IDENTITY,
        )
        # The record has to be wrapped in parens to become a candid argument list.
        out = call(
            gs,
            "spinUpMainerControllerCanister",
            f"({ok_record(paid)})",
            identity=PLAYER_IDENTITY,
        )
        cid = re.search(r'address = "([a-z0-9-]+)"', out).group(1)
        wait_healthy(cid, f"ShareAgent {i}")
        verify_share_agent(cid)
        created.append(cid)
        print(f"  [{i}/{n}] {cid}  paid in block {block}")

    # GameState refuses a submission whose module hash it does not recognise
    # (GameState.mo, submitChallengeResponse). One call covers every agent on this wasm.
    if created:
        call(
            gs,
            "deriveNewMainerAgentCanisterWasmHashAdmin",
            f'(record {{ address = "{created[0]}"; textNote = "e2e" }})',
        )
        print("  registered the mAIner wasm hash with game_state")
    return created


def list_on_marketplace(agents: list[str]) -> None:
    """Put each ShareAgent up for sale, as its owner.

    This is what makes the local environment usable from the BROWSER. A mAIner bought by the
    harness is owned by the `e2e-player` PEM key, and an Internet Identity login derives an
    entirely different principal -- so a signed-in human owns nothing and the UI shows them
    an empty fleet. Listing it means they can buy it through the real marketplace flow and
    genuinely own it afterwards.

    The listing API is ICRC-37 repurposed, which is worth spelling out because nothing in
    the signature suggests it:
      * `token_id` is the PRICE in e8s, not a token id (floor: 1_000_000 = 0.01 ICP)
      * `approval_info.memo` is the mAIner's canister address as UTF-8
      * the caller must already own that mAIner
    """
    if not agents:
        return
    banner("list ShareAgent(s) on the marketplace")
    gs = canister_id("game_state_canister")
    for cid in agents:
        out = icp(
            f"canister call {gs} icrc37_approve_tokens "
            f"'(vec {{ record {{ token_id = {MARKETPLACE_PRICE_E8S} : nat; "
            f'approval_info = record {{ spender = record {{ owner = principal "{gs}"; '
            f"subaccount = null }}; from_subaccount = null; expires_at = null; "
            f'created_at_time = null; memo = opt blob "{cid}" }} }} }})\' '
            f"-e {ENV} --identity {PLAYER_IDENTITY}",
            check=False,
            quiet=True,
        )
        if "Ok" not in out:
            print(f"  {cid}  NOT listed: {out.strip()[:140]}")
            continue
        print(f"  {cid}  listed at {MARKETPLACE_PRICE_E8S / 1e8:g} ICP")

    print("\n  How to buy one in the browser is printed at the end of the deploy.")


def agent_status(cid: str) -> str:
    """GameState's own view of a mAIner's status, e.g. `Running`.

    GameState sets `#Other("Controller Upgrade in Progress")` before asking mAInerCreator to
    do the work and only clears it when mAInerCreator reports back, so this is the one
    signal that distinguishes "upgraded" from "the install was rejected". The canister's own
    `health` cannot: a mAIner whose upgrade the IC refused is still happily running its old
    code.
    """
    gs = canister_id("game_state_canister")
    out = icp(f"canister call {gs} getAllMainerAgentsAdmin '()' -e {ENV}", check=False, quiet=True)
    # Each record ends with its address, so the status that belongs to `cid` is the last one
    # seen before it.
    head = out.split(f'address = "{cid}"')[0]
    found = re.findall(r"status = variant \{ ([^}]+?) \}", head)
    return found[-1].strip() if found else "unknown"


def wait_agent_running(cid: str, timeout: int = 180) -> None:
    """Wait for GameState to record the mAIner as `Running` again.

    Called after a reinstall/upgrade. If this times out on
    `Other = "Controller Upgrade in Progress"`, the install was REJECTED -- check
    `icp canister logs <mainer_creator_canister>`, which carries the real reason.
    """
    deadline = time.time() + timeout
    status = ""
    while time.time() < deadline:
        status = agent_status(cid)
        if status == "Running":
            return
        time.sleep(3)
    raise SystemExit(
        f"{cid} is still {status!r} after {timeout}s -- game_state_canister never got the\n"
        "completion callback, which means mainer_creator_canister could not install the\n"
        "code. It reports why in its logs:\n"
        f"  cd e2e && icp canister logs $(icp canister status mainer_creator_canister "
        f"-e {ENV} --id-only) -e {ENV}"
    )


def verify_share_agent(cid: str, timeout: int = 120) -> None:
    """Wait until an agent is a wired-up ShareAgent, not merely alive.

    The failure this catches is silent: a mAIner defaults to `#Own` pointing at a canister
    id baked into its source, and one that came back from a reinstall without its
    configuration answers `health` perfectly well while never doing any work.

    POLLED, because mAInerCreator applies that configuration asynchronously -- the agent
    starts answering `health` a good while before the setters land, so a single check right
    after the install reads the pre-configuration state and looks like a real failure.

    Called as the OWNER. These getters are gated on an admin role, and mAInerCreator makes
    the owner a controller of the canister, which is what grants it. The harness admin has
    no rights here at all (mAInerCreator created the canister, so it and the owner are its
    controllers), and calling as it returns Unauthorized -- which reads like a broken agent.
    """
    ss = canister_id("mainer_service_canister")
    deadline = time.time() + timeout
    kind = pointer = ""
    while time.time() < deadline:
        kind = icp(
            f"canister call {cid} getMainerCanisterType '()' -e {ENV} "
            f"--identity {PLAYER_IDENTITY}",
            check=False,
            quiet=True,
        )
        pointer = icp(
            f"canister call {cid} getShareServiceCanisterId '()' -e {ENV} "
            f"--identity {PLAYER_IDENTITY}",
            check=False,
            quiet=True,
        )
        if "ShareAgent" in kind and ss in pointer:
            return
        time.sleep(2)
    raise SystemExit(
        f"{cid} was not configured as a ShareAgent within {timeout}s\n"
        f"  getMainerCanisterType    : {kind!r}\n"
        f"  getShareServiceCanisterId: {pointer!r} (expected {ss})"
    )


def manage_share_agents(mode: str, n: int) -> None:
    """Bring the ShareAgent fleet to n agents, using `mode` on any that already exist.

    `install` has nothing to re-install: on a fresh network there are no agents yet.
    `upgrade` keeps GameState's memory, so the agents it created are still there and get
    upgraded through mAInerCreator -- which is the production path.
    """
    existing = share_agents()

    if existing and mode in ("reinstall", "upgrade"):
        banner(f"{mode} {len(existing)} ShareAgent(s) via mAInerCreator")
        gs = canister_id("game_state_canister")
        method = "reinstallMainerControllerAdmin" if mode == "reinstall" else "upgradeMainerControllerAdmin"
        done = "re-installed" if mode == "reinstall" else "upgraded"
        for cid in existing:
            call(gs, method, f'(record {{ canisterAddress = "{cid}" }})')
            wait_healthy(cid, f"ShareAgent {cid}")

            # `health` is NOT sufficient here. A mAIner whose upgrade the IC rejected keeps
            # running its old code and answers health perfectly -- so waiting on GameState's
            # status is the only way to tell an upgrade from a no-op.
            wait_agent_running(cid)

            # A reinstall wipes the agent's stable state, so it comes back as `#Own` with no
            # ShareService. mAInerCreator re-applies all of that itself, and this proves it
            # did. The harness could not do it instead even if it wanted to: only the
            # canister's controllers may call those setters, and those are mAInerCreator and
            # the owner -- not the harness admin.
            verify_share_agent(cid)
            print(f"  {cid}  {done}")

    elif existing and mode == "install":
        print(f"\n  {len(existing)} ShareAgent(s) already exist; leaving them alone.")

    missing = n - len(existing)
    if missing > 0:
        if mode == "reinstall" and not existing:
            # Worth saying out loud -- this is not the harness losing track of them.
            print(
                "\n  -m reinstall wiped game_state_canister's stable memory, and with it\n"
                "  every mAIner it knew about. Any agent from a previous run is still on\n"
                "  the replica but is now unreachable, so fresh ones are bought instead."
            )
        # Only newly bought agents are listed. An agent that already existed may have been
        # sold to a browser user already, and re-listing someone else's mAIner would fail.
        list_on_marketplace(create_share_agents(missing))


def build_frontend() -> None:
    """Build the Svelte app straight into e2e/dist.

    Not ../dist: the asset-canister sync plugin refuses a `dir` containing '..'.
    """
    banner("frontend")
    run("ICP_ENV=local npx vite build --outDir e2e/dist --emptyOutDir", cwd=REPO)
    icp(f"deploy {FRONTEND.name} -e {ENV} -y")


def print_next_steps() -> None:
    """What to actually DO with the environment that was just deployed.

    Printed last, on purpose. Everything here was discoverable already -- in the status
    block, in a line 30 rows up, or only in README-setup.md -- and that is exactly why it
    kept being missed. The two steps that have no on-screen error when you get them wrong
    (creating the identity, funding the principal) are the ones worth spelling out.
    """
    url = network_url()
    port = url.rsplit(":", 1)[-1]
    gs = canister_id("game_state_canister")
    listings = icp(
        f"canister call {gs} getMarketplaceMainerListings '()' -e {ENV} --query",
        check=False,
        quiet=True,
    )
    for_sale = re.findall(r'address = "([a-z0-9-]+)"', listings)

    banner("next steps")
    print(f"  1. Open the app     http://{FRONTEND.name}.local.localhost:{port}/")
    print(f"     Not {url} -- that is the API gateway, and")
    print("     it redirects to the IC dashboard because it has no canister to resolve.\n")

    print("  2. Sign in          Connect -> Internet Identity")
    print("     On a fresh replica you must CREATE the identity first:")
    print("       Create (under 'Create new identity') -> Create with passkey ->")
    print("       any name -> Create identity -> seed index 0 -> Continue")
    print("     Clicking 'Sign in with passkey' for a seed that was never created fails")
    print("     SILENTLY -- it just returns to the sign-in screen. Once seed 0 exists,")
    print("     'Sign in with passkey' -> 0 works, until the next e2e-start-clean.\n")

    if for_sale:
        print("  3. Fund yourself    make e2e-fund PRINCIPAL=<your principal from the UI>")
        print("     An Internet Identity principal holds 0 ICP: the local ledger seeds only")
        print("     the identities that existed when the network started. Without this the")
        print("     purchase fails on payment, and the UI will not say why.\n")
        print("  4. Get a mAIner     two routes, both worth exercising:\n")
        print(f"     4a. Buy from the marketplace  ({len(for_sale)} listed, "
              f"{MARKETPLACE_PRICE_E8S / 1e8:g} ICP each)")
        for cid in for_sale:
            print(f"           {cid}")
        print("         Owned by e2e-player until you buy it. This is the resale path --")
        print("         one player buying another player's mAIner.\n")
        print("     4b. Create new mAIner         in the UI")
        print("         The mint path: you pay the protocol and mainer_creator_canister")
        print("         creates a brand-new canister for you, rather than transferring an")
        print(f"         existing one. Costs {SHARE_AGENT_ICP} ICP, so fund accordingly.")
    else:
        print("  3. No mAIner is listed for sale. You can still use 'Create new mAIner' in")
        print(f"     the UI to mint one ({SHARE_AGENT_ICP} ICP) -- fund your principal first:")
        print("       make e2e-fund PRINCIPAL=<your principal from the UI>")
        print("     Deploy with SHARE_AGENTS=N to also have one listed for resale.")


def cmd_start(args: argparse.Namespace) -> None:
    """Start the network, reusing whatever is in .icp/cache."""
    start_network(clean=False)


def cmd_start_clean(args: argparse.Namespace) -> None:
    """Wipe .icp/cache and start a brand-new replica."""
    start_network(clean=True)


def _deploy(args: argparse.Namespace, mode: str) -> None:
    """Shared body of install / reinstall / upgrade."""
    t0 = time.time()
    require_network()
    deployer = bootstrap_identities()
    docker = not args.no_docker
    build_all(docker, keep_base=args.keep_base)
    deploy_all(deployer, mode, docker)
    fund_llm()

    # The registration setters are idempotent, so this is safe in every mode. It is also
    # necessary after an upgrade: the values live in canister state, and re-running costs
    # nothing but guarantees the fleet is wired however the current code expects.
    wire_up(args.share_agents)

    if mode == "upgrade":
        # The model FILE survives an upgrade; only the loaded model needs restoring.
        activate_model()
        # The harness never arms the timers (see README-setup.md), so there is nothing to
        # restore here -- but an upgrade clears them, so anything armed by hand is gone.
        print(
            "\nNote: every upgrade clears startTimerExecutionAdmin and "
            "startSendCyclesTimerAdmin.\n"
            "      If you armed either by hand, arm it again."
        )
    elif not args.skip_model:
        # install/reinstall leave the canister's file storage empty.
        if upload_gguf():
            activate_model()

    # mAInerCreator needs the wasm before it can create or re-install anything, and the
    # upload is cheap (one 855 KB chunk), so it is not worth conditioning on the mode.
    upload_mainer_wasm(docker)
    manage_share_agents(mode, args.share_agents)

    if not args.skip_frontend:
        build_frontend()
    cmd_status(args)
    print(f"\ne2e environment ready in {time.time() - t0:.0f}s")
    print_next_steps()


def cmd_install(args: argparse.Namespace) -> None:
    _deploy(args, "install")


def cmd_reinstall(args: argparse.Namespace) -> None:
    _deploy(args, "reinstall")


def cmd_upgrade(args: argparse.Namespace) -> None:
    _deploy(args, "upgrade")


# ---------------------------------------------------------------------------------------
# status / down
# ---------------------------------------------------------------------------------------
def cmd_status(_args: argparse.Namespace) -> None:
    banner("status")
    try:
        url = network_url()
    except Exception:
        print("  local network is NOT running -- `make e2e-start`")
        return
    # The bare gateway is the API endpoint, NOT the app: with no canister to resolve it
    # 307s to dashboard.internetcomputer.org, which looks like the local network is somehow
    # reaching mainnet. Canisters are addressed by SUBDOMAIN, so open the frontend URL.
    print(f"  gateway    : {url}   (API endpoint -- opening this redirects to the IC dashboard)")
    port = url.rsplit(":", 1)[-1]
    if canister_id("funnai_frontend"):
        print(f"  frontend   : http://{FRONTEND.name}.local.localhost:{port}/   <-- open this")
    print(f"  internet id: {url.replace('//', '//id.ai.')}/authorize")
    print()

    def health_of(cid: str) -> str:
        out = icp(f"canister call {cid} health '()' -e {ENV} --query", check=False, quiet=True)
        return "OK" if "status_code = 200" in out else ("-" if not out else "?")

    for c in CANISTERS + [FRONTEND]:
        cid = canister_id(c.name)
        if not cid:
            print(f"  {c.name:<30} {'-':<30} not deployed")
            continue
        print(f"  {c.name:<30} {cid:<30} {health_of(cid)}")

    # ShareAgents have no entry in icp.yaml -- they were created by the CMC on the player's
    # behalf, so GameState is the only place that knows their ids.
    for i, cid in enumerate(share_agents(), 1):
        print(f"  {f'share_agent_{i}':<30} {cid:<30} {health_of(cid)}")


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

    # The ShareAgents. Being deployed proves nothing here -- a mAIner that came up without
    # its configuration is healthy and idle, so what matters is that it knows it is a
    # ShareAgent, knows where the ShareService is, and that the ShareService will accept
    # its work. All three are read as the OWNER; the admin has no rights on these.
    ss = canister_id("mainer_service_canister")
    registry = icp(
        f"canister call {ss} getShareAgentRegistryWithActivityAdmin '()' -e {ENV}",
        check=False,
        quiet=True,
    )
    for i, agent in enumerate(share_agents(), 1):
        def wired_agent(cid=agent):
            kind = icp(
                f"canister call {cid} getMainerCanisterType '()' -e {ENV} "
                f"--identity {PLAYER_IDENTITY}",
                check=False, quiet=True,
            )
            pointer = icp(
                f"canister call {cid} getShareServiceCanisterId '()' -e {ENV} "
                f"--identity {PLAYER_IDENTITY}",
                check=False, quiet=True,
            )
            ok = "ShareAgent" in kind and ss in pointer and cid in registry
            return ok, f"type={'ShareAgent' if 'ShareAgent' in kind else kind[:20]} " \
                       f"ss={'yes' if ss in pointer else 'NO'} " \
                       f"registered={'yes' if cid in registry else 'NO'}"

        results.append(_check(f"share_agent_{i} is a wired ShareAgent", wired_agent))

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


def cmd_fund(args: argparse.Namespace) -> None:
    """Send local ICP to any principal -- meant for a browser Internet Identity login.

    The local ledger hands its 1,000,000 ICP only to the identities that exist when the
    network starts. An Internet Identity principal is derived at sign-in time and so is
    never among them: it starts at zero and cannot buy anything on the marketplace.
    """
    banner("fund a principal")
    who = args.principal
    icp(f"token transfer {args.amount} {who} -e {ENV} --identity {ADMIN_IDENTITY}", quiet=True)
    balance = icp(f"token balance --of-principal {who} -e {ENV} -q", check=False, quiet=True)
    print(f"  {who}\n  sent {args.amount} ICP -- balance now {balance or '(unreadable)'}")


def cmd_stop(_args: argparse.Namespace) -> None:
    """Stop the replica. Deletes nothing -- .icp/cache survives."""
    banner("stopping local network")
    icp("network stop", check=False)


def cmd_clean(_args: argparse.Namespace) -> None:
    """Stop the network and remove every piece of disposable local state.

    Goes further than `start-clean`, which only wipes the e2e project's cache: this also
    removes the BUILD ARTIFACTS in all 16 projects, so the next deploy recompiles from
    scratch. Use it to prove a build works from cold, or to reclaim the disk.

    It removes only paths ending in `.icp/cache` and the frontend `dist/` directories.
    `.icp/data`, which holds the MAINNET canister ids for prd/testing/development and is
    committed, is never touched -- losing it would lose the ids for every environment at
    once. That is why this enumerates and prints each path instead of doing anything
    resembling `rm -rf .icp`.
    """
    banner("clean")
    icp("network stop", check=False, quiet=True)
    print("  network stopped")

    targets = sorted(
        p for p in REPO.glob("**/.icp/cache") if "node_modules" not in p.parts
    )
    targets += [d for d in (E2E / "dist", REPO / "dist") if d.exists()]

    for path in targets:
        # Belt and braces: never delete a `.icp` directory itself, whatever the glob did.
        assert path.name in ("cache", "dist"), f"refusing to remove {path}"
        shutil.rmtree(path, ignore_errors=True)
        print(f"  removed  {path.relative_to(REPO)}")

    kept = len([p for p in REPO.glob("**/.icp/data") if "node_modules" not in p.parts])
    print(f"\n  KEPT: {kept} .icp/data directories -- the committed mainnet canister ids.")
    print("  KEPT: the `default` and `e2e-player` icp identities (they are machine-wide).")
    print("\n  Next: make e2e-start && make e2e-install")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("start", cmd_start), ("start-clean", cmd_start_clean),
                     ("install", cmd_install), ("reinstall", cmd_reinstall),
                     ("upgrade", cmd_upgrade), ("status", cmd_status),
                     ("test", cmd_test), ("stop", cmd_stop), ("clean", cmd_clean),
                     ("fund", cmd_fund)]:
        p = sub.add_parser(name)
        p.set_defaults(func=fn)
        if name == "fund":
            p.add_argument("principal", help="the principal to send local ICP to")
            p.add_argument("--amount", type=int, default=100, help="whole ICP (default 100)")
        if name in ("install", "reinstall", "upgrade"):
            # upgrade never uploads the gguf anyway; the flag is accepted so the three
            # deploy commands share one interface.
            p.add_argument("--skip-model", action="store_true", help="skip the slow gguf upload")
            p.add_argument("--skip-frontend", action="store_true")
            p.add_argument(
                "--no-docker",
                action="store_true",
                help="build with the local `icp build` instead of the reproducible Docker "
                     "build; faster, but the artifact is not the canonical one",
            )
            p.add_argument(
                "--keep-base",
                action="store_true",
                help="reuse the existing Docker toolchain base images instead of rebuilding "
                     "them; saves ~150s per image, for a fast iteration loop",
            )
            p.add_argument(
                "--share-agents",
                type=int,
                default=1,
                metavar="N",
                help="how many ShareAgent mAIners the player should own (default 1). Each "
                     "one costs 10 local ICP and is created through mAInerCreator.",
            )
    args = ap.parse_args()
    for opt in ("clean", "skip_model", "skip_frontend", "no_docker", "keep_base"):
        setattr(args, opt, getattr(args, opt, False))
    args.share_agents = getattr(args, "share_agents", 1)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
