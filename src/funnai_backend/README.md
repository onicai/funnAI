# Build, Deploy and Verify

```bash
# Build wasm with Docker (reproducible build)
# The base image is shared across all canisters of the funnAI repo.
# Once built, it can be reused. (The PoAIW repo has its own, separate base image.)
make docker-build-base
make docker-build-wasm

# Deploy the pre-built wasm
# Note: Post-SNS, this step is replaced with SNS governed deployment.
dfx generate funnai_backend
dfx canister --network $NETWORK stop funnai_backend
dfx canister --network $NETWORK snapshot create funnai_backend
dfx canister install --wasm out/funnai_backend.wasm \
    --argument "( principal \"$(dfx identity get-principal)\" )" \
    --network $NETWORK --mode upgrade --wasm-memory-persistence keep \
    funnai_backend
dfx canister --network $NETWORK start funnai_backend

# Verify the deployed wasm matches the Docker build
make docker-verify-wasm VERIFY_NETWORK=$NETWORK
```

# Available Makefile targets

```bash
make help
```
