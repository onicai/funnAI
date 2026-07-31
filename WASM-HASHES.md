# Wasm hash tracker — dfx → icp-cli migration

Baseline captured **2026-07-31**, before any migration change, with:

```bash
icp canister status <principal> -n ic -p --json    # .module_hash, no controller rights needed
```

## Why this file exists

The dfx → icp-cli migration replaces the build chain: `dfx build` (dfx 0.29.2, with its
bundled `moc`) becomes `icp build` → the `@dfinity/motoko` recipe → `mops build` + `ic-wasm
shrink`. That is a different compiler and a different pipeline, so **every Motoko wasm hash
changes**. This was an accepted, deliberate decision.

Consequence: `make docker-verify-wasm` and the `verify-wasm` CI workflow will report a
MISMATCH for every canister until that canister is redeployed with an icp-built wasm.

**Redeploying is NOT part of the migration project.** Nothing here writes to mainnet. The
redeploys are a separate, later project, and this file is the handover artefact for it — the
"redeployed" boxes stay unticked until that project ticks them.

## Toolchain

| | before (deployed wasms) | after (this repo builds) |
| ------------------- | ----------------------- | ----------------------------- |
| CLI                 | dfx 0.29.2              | icp-cli 1.2.0                 |
| Motoko compiler     | bundled with dfx 0.29.2 | `moc` pinned in `mops.toml`   |
| package manager     | `mops sources` via dfx  | ic-mops                       |
| post-processing     | dfx internal            | `@icp-sdk/ic-wasm` shrink     |
| llama_cpp_canister  | v0.11.0                 | v0.15.0                       |

## funnAI-owned canisters

| canister          | prd principal               | prd hash (dfx 0.29.2)                                              | new icp/mops hash | redeployed |
| ----------------- | --------------------------- | ------------------------------------------------------------------ | ----------------- | ---------- |
| `funnai_backend`  | 6wp2z-paaaa-aaaaa-qau7q-cai | `9fca8da6b78fe5c4aa0957596c28c32ebe90bdb16573c64880809577aca688cb` | TBD               | ☐          |
| `funnai_frontend` | vizih-uiaaa-aaaaa-qavaa-cai | `423f20ee4e5daf8f76d6bb2b4a87440227f15b26cf874c132fd75d83e252c8f6` | TBD               | ☐          |

`funnai_frontend` is an asset canister; its hash comes from the
`@dfinity/asset-canister` recipe, not from `moc`.

The PoAIW canisters and the LLM fleet are tracked in `PoAIW/WASM-HASHES.md`.
