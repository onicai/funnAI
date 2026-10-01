#!/usr/bin/env bash
# Runs inside Docker. Produces /out/{dist,dist.sha256,dist.fingerprint,assets.tar.xz}.
set -euo pipefail
cd /build

export NODE_ENV=production
export TZ=UTC
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export DFX_NETWORK="${DFX_NETWORK:-prd}"
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"
export COMMIT="${COMMIT:-unknown}"

echo "node $(node --version)"
echo "npm  $(npm --version)"
echo "DFX_NETWORK=${DFX_NETWORK}"
echo "SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}"
echo "COMMIT=${COMMIT}"

npx vite build

if find dist -name '*.map' -print -quit | grep -q .; then
  echo "ERROR: sourcemaps in dist/; they make the build non-reproducible" >&2
  exit 1
fi

# Stamp lets host `dfx deploy` skip a second Vite build. Ignored as an asset
# (see src/funnai_frontend/assets/.ic-assets.json) so it is not uploaded.
cat > dist/.reproducible-build <<EOF
COMMIT=${COMMIT}
NETWORK=${DFX_NETWORK}
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}
EOF

mkdir -p /out

# Content-addressed manifest of files the canister will serve. This is the
# frontend equivalent of sha256(wasm) — the stock asset wasm does not include
# these bytes.
(
  cd dist
  LC_ALL=C find . -type f ! -name '.reproducible-build' ! -name '.ic-assets.json' ! -name '.ic-assets.json5' -print0 \
    | LC_ALL=C sort -z \
    | xargs -0 -r sha256sum
) > /out/dist.sha256

sha256sum /out/dist.sha256 | awk '{print $1}' | tee /out/dist.fingerprint
echo "Frontend fingerprint (sha256 of dist.sha256): $(cat /out/dist.fingerprint)"

# nns-dapp-style reproducible tarball (GNU tar archive flags).
# Files are left uncompressed: dfx's asset uploader applies encodings.
tar cJf /out/assets.tar.xz \
  --mtime="@${SOURCE_DATE_EPOCH}" \
  --sort=name \
  --owner=0 \
  --group=0 \
  --numeric-owner \
  --format=gnu \
  --exclude=.reproducible-build \
  --exclude=.ic-assets.json \
  --exclude=.ic-assets.json5 \
  -C dist \
  .

sha256sum /out/assets.tar.xz

cp -a dist /out/dist

cat > /out/versions.txt <<EOF
node=$(node --version)
npm=$(npm --version)
DFX_NETWORK=${DFX_NETWORK}
COMMIT=${COMMIT}
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}
fingerprint=$(cat /out/dist.fingerprint)
EOF

echo "Wrote /out:"
ls -la /out
