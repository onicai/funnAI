# Reproducible frontend build (nns-dapp-style Docker sandbox).
#
# The trust artifact is dist/ (content-addressed via dist.sha256 / dist.fingerprint),
# NOT the asset-canister module hash. funnai_frontend is dfx type=assets: the wasm is
# dfx's stock certified-assets runtime and does not include the UI.
#
# Use:
#   make -C src/funnai_frontend docker-build-frontend
ARG PLATFORM=linux/amd64
# node:22.21.1-bookworm-slim — matches .nvmrc. Pin by digest, not the floating tag.
FROM --platform=${PLATFORM} node:22.21.1-bookworm-slim@sha256:25b3eb23a00590b7499f2a2ce939322727fcce1b15fdd69754fcd09536a3ae2c

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# git: pixeloids is fetched from GitHub. xz-utils: reproducible assets.tar.xz.
# Deliberately unpinned apt patch versions — same reason as src/docker/Dockerfile.base:
# Ubuntu deletes superseded packages, and these tools do not emit the JS bundle.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        xz-utils \
        findutils \
    && rm -rf /var/lib/apt/lists/*

# Docker has no GitHub SSH keys. The lockfile may record git+ssh://; rewrite to https.
# The commit is still pinned by package-lock.json.
RUN git config --global url."https://github.com/".insteadOf "ssh://git@github.com/" \
    && git config --global url."https://github.com/".insteadOf "git@github.com:"

WORKDIR /build

# Install dependencies before copying sources so this layer caches.
# NODE_ENV must NOT be production here: vite/svelte/tailwind live in devDependencies.
COPY package.json package-lock.json ./
RUN npm ci

# Sources required by Vite. Do not copy .env, .dfx, node_modules, dist, or PoAIW
# (.dockerignore enforces this; the .env check below is a belt-and-suspenders fail).
COPY dfx.json canister_ids.json vite.config.ts svelte.config.js tsconfig.json postcss.config.cjs index.html ./
COPY src/funnai_frontend ./src/funnai_frontend
COPY src/declarations ./src/declarations
COPY src/funnai_frontend/scripts/build.sh ./scripts/build.sh

RUN if test -e /build/.env ; then echo "ERROR: There should be no .env in docker!" ; exit 1 ; fi

ARG DFX_NETWORK=prd
ARG SOURCE_DATE_EPOCH=0
ARG COMMIT=unknown
ENV DFX_NETWORK=${DFX_NETWORK} \
    SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH} \
    COMMIT=${COMMIT}

RUN bash scripts/build.sh
