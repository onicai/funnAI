#!/usr/bin/env bash
# Vite 8 needs Node ^20.19 || >=22.12. dfx's npm subprocess often sees the
# login-shell default (e.g. 22.10.0) rather than nvm, so load .nvmrc here.
set -euo pipefail
cd "$(dirname "$0")/.."

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

exec npx vite build
