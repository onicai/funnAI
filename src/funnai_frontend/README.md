# Build, Deploy and Verify

The frontend is a dfx **assets** canister. Unlike Motoko wasms, `dfx canister info`
prints the stock certified-assets runtime hash, which does **not** include the UI.
The trust artifact is therefore `dist/` — content-addressed as `out/dist.fingerprint`
(sha256 of the sorted per-file manifest `out/dist.sha256`).

```bash
# from this directory
make docker-build-frontend NETWORK=prd

# Deploy the Docker-built dist/. scripts/build-frontend.sh skips Vite when the
# stamp in dist/.reproducible-build matches this commit and DFX_NETWORK.
dfx deploy funnai_frontend --network $NETWORK

# Compare live HTTPS bodies to the Docker dist/
make docker-verify-frontend VERIFY_NETWORK=$NETWORK
```

The bundle is network-specific: canister IDs from `canister_ids.json` are inlined
at build time. Rebuild with `NETWORK=testing` (or `development`) for those networks.

```bash
make help
```
