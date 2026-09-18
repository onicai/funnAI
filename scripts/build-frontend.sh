#!/usr/bin/env bash
# Vite 8 needs Node ^20.19 || >=22.12. dfx's npm subprocess often sees the
# login-shell default (e.g. 22.10.0) rather than nvm, so load .nvmrc here.
#
# When dist/ was produced by `make docker-build-frontend` for this commit and
# DFX_NETWORK, skip Vite so `dfx deploy` does not rebuild on the host.
set -euo pipefail
cd "$(dirname "$0")/.."

stamp="dist/.reproducible-build"
if [[ -f "${stamp}" && -f dist/index.html ]]; then
  stamp_commit=""
  stamp_network=""
  # shellcheck disable=SC1090
  source "${stamp}"
  stamp_commit="${COMMIT:-}"
  stamp_network="${NETWORK:-}"
  head_commit="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  want_network="${DFX_NETWORK:-}"
  if [[ -n "${stamp_commit}" && "${stamp_commit}" == "${head_commit}" \
     && -n "${stamp_network}" && -n "${want_network}" \
     && "${stamp_network}" == "${want_network}" ]]; then
    echo "Using Docker-prebuilt dist/ for ${stamp_network} @ ${stamp_commit}"
    exit 0
  fi
  echo "dist/.reproducible-build is stale (stamp ${stamp_network}@${stamp_commit} vs ${want_network}@${head_commit}); rebuilding"
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$NVM_DIR/nvm.sh" ]]; then
  # nvm is a function, not a binary
  # shellcheck disable=SC1091
  . "$NVM_DIR/nvm.sh"
  nvm use
fi

node -e "
const [maj, min] = process.versions.node.split('.').map(Number);
const ok = (maj === 20 && min >= 19) || maj > 22 || (maj === 22 && min >= 12);
if (!ok) {
  console.error('Need Node ^20.19 or >=22.12 (nvm use). Current: ' + process.versions.node);
  process.exit(1);
}
"

export NODE_ENV="${NODE_ENV:-production}"
exec npx vite build
