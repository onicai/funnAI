# Deployed wasm hashes

The record of **which build is deployed on prd** for every canister the funnAI SNS
controls, so anyone — team or community — can permissionlessly verify a canister is
running the code this repo builds.

Read any deployed hash with no special rights (`dfx` prints it with a `0x` prefix; the
tables below use bare hex to match `shasum` / the reproducible build output):

```bash
dfx canister --network ic info <canister-id>   # prints "Module hash: 0x..."
```

All hashes in this file were **read live on 2026-09-17**. Re-read them with the loop in
[Read every deployed hash at once](#read-every-deployed-hash-at-once) rather than trusting
a copy — this file has been wrong before from stale copying.

## What the SNS controls

The `onicai` SNS (`onicai_sns/onicai_sns_init.yaml`) decentralizes funnAI by taking
control of **21 `dapp_canisters`** — 12 protocol/app + 9 LLM — listed below in groups A–E.

The **~754 ShareAgent mAIner canisters are not individually in `dapp_canisters`**, yet
they are strictly SNS-controlled: their controller is **mAInerCreator**
(`r2n3m-oqaaa-aaaaa-qanaq-cai`), which *is* an SNS dapp_canister. The SNS therefore governs
the whole fleet indirectly through mAInerCreator, which mints and upgrades every agent and
holds the promoted controller wasm they all run. They are documented in group B.

## Deployed hashes

Grouped by how the wasm is built and verified. The **source** column is repo-aware: a
PoAIW commit for groups A/B, the `llama_cpp_onicai_fork` commit / release for group C, the
DFINITY release tag for group D, and the outer `funnAI` repo for group E. `(to confirm)`
means the deployed hash is authoritative but its exact source commit/date isn't on record
yet — reproduce it with the group's verify procedure to establish it.

### Group A — Motoko protocol canisters (PoAIW, shared Docker build)

| role          | canister-id                   | source (PoAIW) | deployed     | deployed module hash                                             |
| ------------- | ----------------------------- | -------------- | ------------ | ---------------------------------------------------------------- |
| GameState     | `r5m5y-diaaa-aaaaa-qanaa-cai` | `(to confirm)` | (to confirm) | e26a6419dbcfc98e1eff40c02cd10916cead203dff25814a779421efabf55d71 |
| Challenger    | `rtoqq-yyaaa-aaaaa-qanba-cai` | `(to confirm)` | (to confirm) | 47f386b76144ef1a0fccd20608c099de7c83480a9a7e87a8ae1fa64b10f97db1 |
| Judge         | `qmgdh-3aaaa-aaaaa-qanfq-cai` | `(to confirm)` | (to confirm) | 24ade07da97f8e6026c15b150f81e6486360025fc846cf2eefa74bb195f7edd6 |
| mAInerCreator | `r2n3m-oqaaa-aaaaa-qanaq-cai` | `968cc3a`      | 2026-08-25   | 6441d67f73af48d06e06106db1ce6f23eaf7d7c7782f352accead7a9a622d52d |
| Treasury      | `qbhxa-ziaaa-aaaaa-qbqza-cai` | `(to confirm)` | (to confirm) | df75427673a8a49c4cd03befdaf0c9b189e5e31e3e9f3481097ea8f5eaa006e7 |
| Archive       | `yiobo-hyaaa-aaaaf-qdjnq-cai` | `(to confirm)` | (to confirm) | 1220f961d72159c8ddbee7eb6f89ac71a1a054781e4db7ca90add749c37061b7 |
| API           | `bgm6p-5aaaa-aaaaf-qbzda-cai` | `(to confirm)` | (to confirm) | 13ef2f45052b5b914cb867a02b281440307ab6ce861ef489d34ab71a1ede5513 |

Note: GameState's hash `e26a6419…` differs from the `66e0da2a…` (`968cc3a`, 2026-08-25)
this file recorded before — it was upgraded since (e.g. the marketplace / 60% bonus
release), so its source commit is `(to confirm)`.

### Group B — mAIner controller wasm (PoAIW; ShareService + the ShareAgent fleet)

One Motoko source (`PoAIW/src/mAIner`) produces the role-neutral `mainer_canister.wasm`,
run by both the ShareService controller and every ShareAgent. mAInerCreator deliberately
promotes a pinned build to the fleet, which can lag the ShareService's own deploy, so the
two hashes can differ.

| role                    | canister-id                   | source (PoAIW) | deployed     | deployed module hash                                             |
| ----------------------- | ----------------------------- | -------------- | ------------ | ---------------------------------------------------------------- |
| ShareService controller | `rilmv-caaaa-aaaaa-qandq-cai` | `(unrecorded)` | (to confirm) | 7e149b675f982bb948055326a22358508da2cbd472e7949aad1e2e40b0f3db6e |
| ShareAgent fleet (754)  | *(all 754 mAIner canisters)*  | `968cc3a`      | 2026-08-26   | ce262a7b1167a86204d4f80273b05b7b299df852a99e6c3134e1f22dd41199d7 |

The fleet hash equals mAInerCreator's promoted `mainerControllerWasmSha256` and a sampled
agent's live module hash (both `ce262a7b…`, verified 2026-09-17);
`scripts/audit_mainer_controllers.sh --network prd` confirms all 754 agree.

### Group C — LLM canisters (llama_cpp_canister)

All **9 LLM canisters run the identical wasm**, llama_cpp_canister release **v0.16.8**:

- deployed module hash `3db909db346b6851ae1761de45b1fbc13b882ac0dbc3c44069f6944667e55066`
- source: `onicai/llama_cpp_onicai_fork` commit `6bd774370579b0c48b8ad3f56df468907d033fe9`
  (vendored at `PoAIW/llms/llama_cpp_canister`; see `BUILD-PROVENANCE.txt` +
  `build/llama_cpp.wasm.sha256`)
- deployed 2026-09-17

| role               | canister-id                   |
| ------------------ | ----------------------------- |
| Challenger LLM     | `psgg4-iqaaa-aaaac-qgtza-cai` |
| Judge LLM 0        | `pvhai-fiaaa-aaaac-qgtzq-cai` |
| Judge LLM 1        | `tem27-5yaaa-aaaam-ajawq-cai` |
| Judge LLM 2        | `ftzot-hiaaa-aaaah-avtja-cai` |
| Judge LLM 3        | `lk5m5-hqaaa-aaaad-agqwa-cai` |
| ShareService LLM 0 | `q6xar-uyaaa-aaaag-ayxxq-cai` |
| ShareService LLM 1 | `k26rl-vqaaa-aaaai-rakcq-cai` |
| ShareService LLM 2 | `tb4fe-6qaaa-aaaac-be5tq-cai` |
| ShareService LLM 3 | `6tx5a-raaaa-aaaan-q6hfa-cai` |

### Group D — Token Ledger & Index (DFINITY ICRC release)

Standard DFINITY ICRC-1 canisters (`type: custom`), wasm downloaded from DFINITY release
**`ledger-suite-icrc-2025-01-07`** — see `PoAIW/src/TokenLedger`/`TokenIndex` `dfx.json` +
`download_latest_icrc1_*.sh`. Not built from funnAI/PoAIW source.

| role                  | canister-id                   | source (DFINITY release asset @ ledger-suite-icrc-2025-01-07) | deployed module hash                                             |
| --------------------- | ----------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- |
| Token Ledger (FUNNAI) | `vpyot-zqaaa-aaaaa-qavaq-cai` | `ic-icrc1-ledger.wasm.gz`                                     | 3b03d1bb1145edbcd11101ab2788517bc0f427c3bd7b342b9e3e7f42e29d5822 |
| Token Index           | `mziuv-biaaa-aaaaa-qccrq-cai` | `ic-icrc1-index-ng.wasm.gz`                                   | e155db9d06b6147ece4f9defe599844f132a7db21693265671aa6ac60912935f |

### Group E — Frontend & Backend (outer funnAI repo)

Built in the **outer `funnAI` repo** (not PoAIW) and — unlike every other group —
**without a reproducible Docker build**. Deployed hashes are recorded; reproducibility is
a known gap (see the group-E verify note below).

| role     | canister-id                   | source (funnAI)              | deployed     | deployed module hash                                             |
| -------- | ----------------------------- | ---------------------------- | ------------ | ---------------------------------------------------------------- |
| Frontend | `vizih-uiaaa-aaaaa-qavaa-cai` | `funnai_frontend` `(to confirm)` | (to confirm) | 423f20ee4e5daf8f76d6bb2b4a87440227f15b26cf874c132fd75d83e252c8f6 |
| Backend  | `6wp2z-paaaa-aaaaa-qau7q-cai` | `funnai_backend` `(to confirm)`  | (to confirm) | 9fca8da6b78fe5c4aa0957596c28c32ebe90bdb16573c64880809577aca688cb |

## Reproducible build & verification

Building from source is the trust layer. Reading a deployed hash, or comparing it against
an on-chain stored hash, only proves consistency — it says nothing about whether that
artifact is the source in this repo. Trust starts where someone reads the source and
builds it themselves.

### A. Motoko protocol canisters (shared Docker build)

Every group-A canister carries an identical build kit (`Makefile`, `docker/`,
`scripts/build.sh`, `mops.toml`) under `PoAIW/src/<Canister>/`. Reproducibility is pinned
by the shared base image `poaiw-build:dfx-0.29.2` (dfx 0.29.2 + mops 2.0.0; see
`PoAIW/src/docker/Dockerfile.base`).

```bash
cd PoAIW && git checkout <commit>          # the source commit for the row
cd src/GameState                           # or Challenger, Judge, mAInerCreator, Treasury, ArchiveChallenges, Api
make docker-build-base                     # once; shared toolchain image, reused by all canisters
make docker-build-wasm                     # -> out/<canister>.wasm, prints its sha256 (must equal the table)
make docker-verify-wasm VERIFY_NETWORK=prd # rebuilds and auto-compares to `dfx canister info`; prints MATCH/MISMATCH
```

### B. mAIner controller (ShareService + the ShareAgent fleet)

One source, one role-neutral artifact `out/mainer_canister.wasm`. The full trust chain for
a ShareAgent — each link must be checked:

```bash
# 1. SOURCE -> BUILD (the trust anchor: you build the recorded commit yourself)
cd PoAIW && git checkout 968cc3a
cd src/mAIner && make docker-build-wasm        # must print ce262a7b1167a862...

# 2. BUILD -> PROMOTED (the hash mAInerCreator hands out must be that build)
dfx canister --network prd call --query r2n3m-oqaaa-aaaaa-qanaq-cai getSha256HashesAdmin
#   -> mainerControllerWasmSha256 must equal the hash from step 1

# 3. PROMOTED -> DEPLOYED (every ShareAgent must actually run it)
dfx canister --network prd info <any-ShareAgent-canister-id>   # Module hash must equal it
scripts/audit_mainer_controllers.sh --network prd              # fleet-wide: one line if all 754 agree
```

For the **ShareService controller**, verify directly (it has no on-chain expected hash):
`make docker-verify-wasm VERIFY_NETWORK=prd VERIFY_CANISTER=rilmv-caaaa-aaaaa-qandq-cai`.

### C. LLM canisters

Permissionless: read a deployed LLM's module hash and compare to the release sha256.

```bash
dfx canister --network ic info psgg4-iqaaa-aaaac-qgtza-cai   # any of the 9; must be 0x3db909db...
```

Full reproduce: build the release from `onicai/llama_cpp_canister` at the fork commit
`6bd7743…` (`make docker-build-base` + `make docker-verify-wasm`); the vendored copy at
`PoAIW/llms/llama_cpp_canister` ships only the pre-built artifact + `BUILD-PROVENANCE.txt`.

### D. Token Ledger & Index

Not built here — verify the deployed hash against the DFINITY release asset:

```bash
curl -sL https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-01-07/ic-icrc1-ledger.wasm.gz | gunzip | shasum -a 256
#   -> must equal the deployed Token Ledger module hash (index: ic-icrc1-index-ng.wasm.gz)
```

### E. Frontend & Backend — reproducibility gap

These have **no reproducible Docker build** yet. Frontend is a certified-assets asset
canister (`funnai_frontend`, `npm run build` + `dfx deploy`; its module hash is the
asset-storage wasm, app content is uploaded assets not part of the wasm). Backend is
`funnai_backend` (`type: motoko`, plain `dfx build`). Their deployed hashes are recorded
above so a change is at least detectable, but they cannot yet be independently reproduced
from a pinned source. **TODO (later pass): add a Docker reproducible-build kit for both**,
matching the group-A pattern, so all 21 SNS canisters are reproducibly verifiable.

## Read every deployed hash at once

```bash
source scripts/canister_ids-prd.env
for v in $(grep -oE '^SUBNET_[A-Z0-9_]+' scripts/canister_ids-prd.env | sort -u); do
  id=${!v}; [ -n "$id" ] || continue
  printf '%-34s %s  ' "$v" "$id"
  dfx canister --network prd info "$id" 2>&1 | grep -oE '0x[0-9a-f]+' || echo "(no module hash)"
done
```
