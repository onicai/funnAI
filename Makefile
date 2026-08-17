SHELL := /bin/bash

MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

# The end-to-end local environment.
#
# icp-cli runs one local network per project, and canisters on different networks cannot
# call each other -- so the whole application is deployed together from e2e/, which owns a
# single network and a single id store. See e2e/icp.yaml.
#
# Everything here is LOCAL ONLY. e2e/icp.yaml declares no production environment, and the
# harness hard-codes `-e local`. Mainnet is never touched.
#
# Run from the funnAI root, in the `funnAI` conda env.

.PHONY: help
help:
	@echo "funnAI local end-to-end environment (local network only -- never mainnet):"
	@echo ""
	@echo "  network lifecycle:"
	@echo "    e2e-start        - start the network, reusing cached state"
	@echo "    e2e-start-clean  - wipe .icp/cache, then start a fresh replica"
	@echo "    e2e-stop         - stop the network (deletes nothing)"
	@echo "    e2e-clean        - stop + wipe ALL local state, incl. build artifacts"
	@echo "                       (never touches .icp/data -- the mainnet canister ids)"
	@echo ""
	@echo "  deploy (network must already be running):"
	@echo "    e2e-install      - first deploy onto a fresh network (canisters must be empty)"
	@echo "    e2e-reinstall    - wipe canister state and deploy again"
	@echo "    e2e-upgrade      - keep canister state; gguf is not re-uploaded"
	@echo "                       NO_GGUF=1  skip the slow gguf upload (install/reinstall)"
	@echo "                       NO_DOCKER=1  skip the reproducible Docker build (faster,"
	@echo "                                    non-canonical wasm; needs no Docker)"
	@echo "                       KEEP_BASE=1  reuse the Docker toolchain base images"
	@echo "                                    instead of rebuilding them (~150s a deploy);"
	@echo "                                    for a fast loop -- the wasm stays canonical"
	@echo "                       SHARE_AGENTS=N  how many ShareAgent mAIners the player"
	@echo "                                    buys (default 1). They are created through"
	@echo "                                    mAInerCreator, not installed -- see"
	@echo "                                    README-setup.md."
	@echo ""
	@echo "    e2e-status       - one-screen health summary + URLs"
	@echo "    e2e-test         - run the backend pytest suites against the local network"
	@echo ""
	@echo "    e2e-fund         - send local ICP to a principal, so a browser Internet"
	@echo "                       Identity login can buy the listed mAIner"
	@echo "                       (make e2e-fund PRINCIPAL=<p> [AMOUNT=100])"
	@echo ""
	@echo "  ids                - canister ids for one environment, gathered from all projects"
	@echo "                       (make ids, make ids NETWORK=testing, make ids FILTER=api)"

# `install` requires empty canisters, `reinstall` wipes them, `upgrade` keeps their state.
# Both install and reinstall leave the LLM's file storage empty, so the gguf is uploaded
# again unless NO_GGUF=1; an upgrade keeps it.
NO_GGUF ?=
GGUF_FLAG := $(if $(NO_GGUF),--skip-model,)

# Canisters are built with `make docker-build-wasm` -- the REPRODUCIBLE build, whose output
# is what WASM-HASHES.md records. That is the default because it costs little: a cold
# install measures 295s with Docker against 133s without.
#
# NO_DOCKER=1 falls back to the local `icp build`. Faster, but the artifact is machine
# dependent and its hash will not match the canonical one -- never quote a hash from it.
NO_DOCKER ?=
DOCKER_FLAG := $(if $(NO_DOCKER),--no-docker,)

# ShareAgent mAIners are BOUGHT, not installed: the player pays GameState 10 local ICP and
# mAInerCreator creates the canister through the CMC, which is the production path. One is
# enough to exercise the flow; raise it to exercise several players against each other.
SHARE_AGENTS ?= 1
AGENTS_FLAG := --share-agents $(SHARE_AGENTS)

# Every deploy first DELETES the Docker toolchain base images, so they are rebuilt from
# Dockerfile.base. The image tag encodes the pinned tool versions, so bumping moc already
# forces a new image -- what this catches is an edit to Dockerfile.base that leaves the
# versions alone, where the stale image keeps its name and is silently reused.
#
# Measured cost: ~150s on a full deploy (458s -> 611s), for BOTH images together -- the two
# Dockerfile.base files are near-identical, so the second reuses the first's layers.
# KEEP_BASE=1 reuses whatever is there for a fast iteration loop; the canister wasm is
# canonical either way, because the tool versions are pinned regardless.
KEEP_BASE ?=
BASE_FLAG := $(if $(KEEP_BASE),--keep-base,)

.PHONY: e2e-start
e2e-start:
	@python -m scripts.e2e.harness start

.PHONY: e2e-start-clean
e2e-start-clean:
	@python -m scripts.e2e.harness start-clean

.PHONY: e2e-install
e2e-install:
	@python -m scripts.e2e.harness install $(GGUF_FLAG) $(DOCKER_FLAG) $(BASE_FLAG) $(AGENTS_FLAG)

.PHONY: e2e-reinstall
e2e-reinstall:
	@python -m scripts.e2e.harness reinstall $(GGUF_FLAG) $(DOCKER_FLAG) $(BASE_FLAG) $(AGENTS_FLAG)

.PHONY: e2e-upgrade
e2e-upgrade:
	@python -m scripts.e2e.harness upgrade $(DOCKER_FLAG) $(BASE_FLAG) $(AGENTS_FLAG)

.PHONY: e2e-status
e2e-status:
	@python -m scripts.e2e.harness status

.PHONY: e2e-stop
e2e-stop:
	@python -m scripts.e2e.harness stop

# Wipes every .icp/cache in the repo (local network state, local ids, build artifacts) plus
# the frontend dist/ dirs. NEVER .icp/data, which holds the committed mainnet canister ids.
.PHONY: e2e-clean
e2e-clean:
	@python -m scripts.e2e.harness clean

# The per-canister suites still run against each canister's OWN project network
# (`make smoketest` there). This target runs them against the shared e2e network instead,
# which is what exercises the canisters as a wired-together system.
.PHONY: e2e-test
e2e-test:
	@python -m scripts.e2e.harness test

# Send local ICP to a principal. The local ledger seeds only the identities that existed
# when the network started, so an Internet Identity principal -- which is derived at
# sign-in -- starts with nothing and cannot buy a mAIner off the marketplace.
PRINCIPAL ?=
AMOUNT ?= 100
.PHONY: e2e-fund
e2e-fund:
	@test -n "$(PRINCIPAL)" || { echo "usage: make e2e-fund PRINCIPAL=<principal> [AMOUNT=100]"; exit 1; }
	@python -m scripts.e2e.harness fund $(PRINCIPAL) --amount $(AMOUNT)

# Canister ids live in one store per project (.icp/data/mappings/<env>.ids.json), which is
# what keeps a single owner per canister. This gathers them into one table on demand, so
# there is still no second source of truth to drift.
NETWORK ?= prd
FILTER ?=
.PHONY: ids
ids:
	@python scripts/show_ids.py --network $(NETWORK) $(FILTER)
