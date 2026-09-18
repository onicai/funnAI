#!/usr/bin/env bash
# Compare Docker-built dist/ file hashes to the bodies served by the asset canister.
# Module hash (`dfx canister info`) is the wrong check for this canister.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
FRONTEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NETWORK="${VERIFY_NETWORK:-prd}"
MANIFEST="${FRONTEND_DIR}/out/dist.sha256"
CANISTER_IDS="${ROOT}/canister_ids.json"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "ERROR: ${MANIFEST} not found. Run: make docker-build-frontend NETWORK=${NETWORK}" >&2
  exit 1
fi

CANISTER_ID="$(python3 -c 'import json,sys; data=json.load(open(sys.argv[1])); cid=data.get("funnai_frontend",{}).get(sys.argv[2]);
assert cid, "No funnai_frontend id for network %s" % sys.argv[2]; print(cid)' "${CANISTER_IDS}" "${NETWORK}")"

HOST="https://${CANISTER_ID}.icp0.io"
echo "Verifying ${NETWORK} frontend ${CANISTER_ID}"
echo "Host: ${HOST}"
echo "Manifest: ${MANIFEST}"
echo

matched=0
mismatched=0
missing=0
skipped=0

while read -r hash file; do
  key="${file#./}"
  case "${key}" in
    .reproducible-build|.ic-assets.json|.ic-assets.json5)
      skipped=$((skipped + 1))
      continue
      ;;
  esac
  url="${HOST}/${key}"
  if ! remote_hash="$(curl -fsSL --compressed --retry 3 --retry-delay 1 "${url}" | sha256sum | awk '{print $1}')"; then
    echo "MISSING  ${key}"
    missing=$((missing + 1))
    continue
  fi
  if [[ "${remote_hash}" == "${hash}" ]]; then
    echo "MATCH    ${key}"
    matched=$((matched + 1))
  else
    echo "MISMATCH ${key}"
    echo "  docker: ${hash}"
    echo "  live:   ${remote_hash}"
    mismatched=$((mismatched + 1))
  fi
done < "${MANIFEST}"

echo
echo "matched=${matched} mismatched=${mismatched} missing=${missing} skipped=${skipped}"
if (( mismatched > 0 || missing > 0 )); then
  echo "❌ MISMATCH: Docker dist/ does NOT match the ${NETWORK} frontend canister ${CANISTER_ID}"
  exit 1
fi
echo "✅ MATCH: Docker dist/ matches the ${NETWORK} frontend canister ${CANISTER_ID}"
