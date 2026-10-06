#!/bin/bash

# Read-only pre-SNS audit of the protocol canisters: NNS Root controller, cycles, log viewers.
# Exits non-zero if any check fails.

python -m scripts.audit_dapp_canisters "$@"
