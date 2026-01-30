ARG IMAGE
FROM --platform=linux/amd64 ${IMAGE}

WORKDIR /app/funnai_backend

# Copy project files
COPY funnai_backend/mops.toml ./
COPY funnai_backend/dfx.json ./
COPY funnai_backend/canister_ids.json ./

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
