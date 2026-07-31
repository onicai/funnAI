ARG IMAGE
FROM --platform=linux/amd64 ${IMAGE}

WORKDIR /app/funnai_backend

# mops.lock pins the exact dependency versions, so it is part of the reproducible build.
# canister_ids.json is NOT copied: building a wasm needs no canister ids.
COPY funnai_backend/mops.toml ./
COPY funnai_backend/mops.lock ./
COPY funnai_backend/icp.yaml ./

# Install mops dependencies
RUN mops install

# Copy source files
COPY funnai_backend/main.mo ./
COPY funnai_backend/Types.mo ./
COPY funnai_backend/Utils.mo ./
COPY funnai_backend/Ledger.mo ./

# Copy scripts
COPY funnai_backend/scripts ./scripts/

CMD ["/bin/bash"]
