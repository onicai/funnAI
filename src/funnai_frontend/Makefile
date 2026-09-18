SHELL := /bin/bash

MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-builtin-variables

NETWORK        ?= prd
VERIFY_NETWORK ?= $(NETWORK)
COMMIT         ?= $(shell git -C ../.. rev-parse HEAD)
SOURCE_DATE_EPOCH ?= $(shell git -C ../.. log -1 --pretty=%ct)
REPO_ROOT      := $(abspath ../..)

.PHONY: help docker-build-frontend docker-verify-frontend

help:
	@echo "Makefile targets:"
	@echo "  docker-build-frontend  - Vite build in Docker; writes out/ and repo dist/"
	@echo "  docker-verify-frontend - rebuilds, then compares dist/ hashes to live HTTPS assets"
	@echo "  help                   - Show this help message"
	@echo ""
	@echo "Variables: NETWORK=$(NETWORK) VERIFY_NETWORK=$(VERIFY_NETWORK)"
	@echo "The trust artifact is out/dist.fingerprint (sha256 of out/dist.sha256)."
	@echo "dfx canister info module hash is the stock asset-canister wasm, not the UI."

docker-build-frontend:
	rm -rf out
	mkdir -p out
	cd docker && \
	  DFX_NETWORK="$(NETWORK)" \
	  SOURCE_DATE_EPOCH="$(SOURCE_DATE_EPOCH)" \
	  COMMIT="$(COMMIT)" \
	  docker compose build --no-cache frontend && \
	  DFX_NETWORK="$(NETWORK)" docker compose run --rm frontend
	@test -f out/dist.fingerprint
	@echo "Frontend fingerprint (Docker build): $$(cat out/dist.fingerprint)"
	@echo "Network: $(NETWORK)  commit: $(COMMIT)  SOURCE_DATE_EPOCH: $(SOURCE_DATE_EPOCH)"
	rm -rf "$(REPO_ROOT)/dist"
	cp -a out/dist "$(REPO_ROOT)/dist"
	@echo "Copied Docker dist/ to $(REPO_ROOT)/dist for dfx deploy"

docker-verify-frontend: docker-build-frontend
	VERIFY_NETWORK="$(VERIFY_NETWORK)" bash scripts/verify-assets.sh
