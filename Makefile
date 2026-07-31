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
# Run from the funnAI root, in the `llama_cpp_canister` conda env.

.PHONY: help
help:
	@echo "funnAI local end-to-end environment (local network only -- never mainnet):"
	@echo "  e2e-up          - build + deploy the whole app onto one local network"
	@echo "  e2e-up-fast     - same, but skip the slow gguf upload (no inference)"
	@echo "  e2e-reset       - wipe the local network state and start over"
	@echo "  e2e-status      - one-screen health summary + URLs"
	@echo "  e2e-down        - stop the local network"
	@echo "  e2e-test        - run the backend pytest suites against the local network"

.PHONY: e2e-up
e2e-up:
	@python -m scripts.e2e.harness up

.PHONY: e2e-up-fast
e2e-up-fast:
	@python -m scripts.e2e.harness up --skip-model

.PHONY: e2e-reset
e2e-reset:
	@python -m scripts.e2e.harness reset

.PHONY: e2e-status
e2e-status:
	@python -m scripts.e2e.harness status

.PHONY: e2e-down
e2e-down:
	@python -m scripts.e2e.harness down

# The per-canister suites still run against each canister's OWN project network
# (`make smoketest` there). This target runs them against the shared e2e network instead,
# which is what exercises the canisters as a wired-together system.
.PHONY: e2e-test
e2e-test:
	@python -m scripts.e2e.harness test
