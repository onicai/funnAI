# Deployed wasm hashes

The record of **which build is deployed on prd** for every canister the funnAI SNS
controls, so anyone — team or community — can permissionlessly verify a canister is
running the code this repo builds.

Read any deployed hash with no special rights (`dfx` prints it with a `0x` prefix; the
tables below use bare hex to match `shasum` / the reproducible build output):

```bash
dfx canister --network ic info <canister-id>   # prints "Module hash: 0x..."
```

All hashes in this file were read live on 2026-09-17.

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
DFINITY release tag for group D, and the outer `funnAI` repo for group E.

**Verification status (2026-09-17):** all of group A (7), the group-B ShareAgent fleet,
group C (9 LLMs; re-confirmed 2026-09-18 at v0.17.0) and group D (Token Ledger + Index) were **reproduced and confirmed** — the
build/artifact hash equals the deployed module hash. Remaining gaps:
- **ShareService controller** (group B): its deployed build `7e149b67…` predates the
  reproducible-build framework (release-10); it matches no release from release-10 → `main`.
  Not reproducible — must be redeployed from `main`. See group B (⚠️).
- **Frontend** (group E): Docker kit exists (`src/funnai_frontend`); verify
  `out/dist.fingerprint` against live HTTPS assets, **not** the module hash.
  No Docker-built deploy has been recorded yet.
- **Backend** (group E): Docker kit exists (`src/funnai_backend`); the deployed
  hash has not yet been confirmed against a Docker build.

Reproducibility note: the base images for **release-10 … release-13** no longer build
as-pinned (their `Dockerfile.base` pins exact apt patch versions of curl/ca-certificates/git
that Ubuntu has since deleted); release-14 onward unpinned them. Relaxing those pins lets the
base build and does not change the wasm (apt tooling ≠ the compiler).

`(to confirm)` marks a deployed hash that is authoritative but whose source isn't pinned to
a repo commit yet.

### Group A — Motoko protocol canisters (PoAIW, shared Docker build)

All 7 verified **reproducible from PoAIW `main` @ `5e262d2`** on 2026-09-17 via
`make docker-verify-wasm VERIFY_NETWORK=prd` — each Docker build hash equalled the
deployed module hash (✅ MATCH).

| role          | canister-id                   | source (PoAIW) | verified   | deployed module hash                                             |
| ------------- | ----------------------------- | -------------- | ---------- | ---------------------------------------------------------------- |
| GameState     | `r5m5y-diaaa-aaaaa-qanaa-cai` | `5e262d2`      | 2026-09-17 | e26a6419dbcfc98e1eff40c02cd10916cead203dff25814a779421efabf55d71 |
| Challenger    | `rtoqq-yyaaa-aaaaa-qanba-cai` | `5e262d2`      | 2026-09-17 | 47f386b76144ef1a0fccd20608c099de7c83480a9a7e87a8ae1fa64b10f97db1 |
| Judge         | `qmgdh-3aaaa-aaaaa-qanfq-cai` | `5e262d2`      | 2026-09-17 | 24ade07da97f8e6026c15b150f81e6486360025fc846cf2eefa74bb195f7edd6 |
| mAInerCreator | `r2n3m-oqaaa-aaaaa-qanaq-cai` | `5e262d2`      | 2026-09-17 | 6441d67f73af48d06e06106db1ce6f23eaf7d7c7782f352accead7a9a622d52d |
| Treasury      | `qbhxa-ziaaa-aaaaa-qbqza-cai` | `5e262d2`      | 2026-09-17 | df75427673a8a49c4cd03befdaf0c9b189e5e31e3e9f3481097ea8f5eaa006e7 |
| Archive       | `yiobo-hyaaa-aaaaf-qdjnq-cai` | `5e262d2`      | 2026-09-17 | 1220f961d72159c8ddbee7eb6f89ac71a1a054781e4db7ca90add749c37061b7 |
| API           | `bgm6p-5aaaa-aaaaf-qbzda-cai` | `5e262d2`      | 2026-09-17 | 13ef2f45052b5b914cb867a02b281440307ab6ce861ef489d34ab71a1ede5513 |

`5e262d2` is `main`'s tip at verification time; the deployed protocol canisters reproduce
from it, so the code the SNS will govern is exactly what is in this repo. (GameState's
hash changed from the `66e0da2a…` this file recorded on 2026-08-25 — it was upgraded since,
e.g. the marketplace / 60% bonus release — and now reproduces at `5e262d2`.)

### Group B — mAIner controller wasm (PoAIW; ShareService + the ShareAgent fleet)

One Motoko source (`PoAIW/src/mAIner`) produces the role-neutral `mainer_canister.wasm`,
run by both the ShareService controller and every ShareAgent. The two hashes differ today
because the ShareService controller was left behind: the fleet was upgraded (via
mAInerCreator) to the current build, but the ShareService controller canister was not.

| role                    | canister-id                   | source (PoAIW)     | verified   | deployed module hash                                             |
| ----------------------- | ----------------------------- | ------------------ | ---------- | ---------------------------------------------------------------- |
| ShareAgent fleet (754)  | *(all 754 mAIner canisters)*  | `5e262d2`          | 2026-09-17 | ce262a7b1167a86204d4f80273b05b7b299df852a99e6c3134e1f22dd41199d7 |
| ShareService controller | `rilmv-caaaa-aaaaa-qandq-cai` | `(to confirm)` ⚠️  | —          | 7e149b675f982bb948055326a22358508da2cbd472e7949aad1e2e40b0f3db6e |

**ShareAgent fleet** (`ce262a7b…`): reproducible from `main` @ `5e262d2` — a
`make docker-verify-wasm` build of `PoAIW/src/mAIner` produced exactly `ce262a7b…` on
2026-09-17. It also equals mAInerCreator's promoted `mainerControllerWasmSha256` and a
sampled agent's live hash; `scripts/audit_mainer_controllers.sh --network prd` confirms
all 754 agree.

**⚠️ ShareService controller** (`7e149b67…`): **its build predates the reproducible-build
framework — it cannot be reproduced from any release.** `PoAIW/src/mAIner` was built at
every release from release-10 (the first reproducible release, 2026-01-31) through
release-16 / `main`, each with its own correct per-release base image (apt version pins
relaxed only where Ubuntu has since removed those exact patch versions — those pins are
build tooling, not the Motoko compiler, so the wasm is unaffected):

| release                                    | mAIner wasm hash |
| ------------------------------------------ | ---------------- |
| release-10                                 | `62704fe6…`      |
| release-11, release-12                     | `eec87d02…`      |
| release-13                                 | `ea4b480b…`      |
| release-14, release-15, release-16, `main` | `ce262a7b…` (fleet) |

**None equals ShareService's `7e149b67…`.** So the ShareService controller was last
deployed **before release-10** — before any reproducible-build machinery existed, when the
wasm came from an unpinned local `dfx build`. It therefore **cannot be reproduced today**.
It was never redeployed as the fleet advanced (releases upgrade the fleet via mAInerCreator,
not the standalone ShareService controller canister `rilmv`).
**Fix before SNS launch:** redeploy the ShareService controller from a current `main`
build — `make docker-verify-wasm VERIFY_NETWORK=prd VERIFY_CANISTER=rilmv-caaaa-aaaaa-qandq-cai`
would then MATCH `ce262a7b…`, making it reproducible and aligned with the fleet and `main`.

### Group C — LLM canisters (llama_cpp_canister)

All **9 LLM canisters run the identical wasm**, llama_cpp_canister release **v0.17.0**:

- deployed module hash `4f89aa1564470574acc5ae78e5b5f49f78d4f188c252760fa399e726e72d8820`
  (confirmed live on all 9 canisters via `dfx canister info`; matches the vendored
  release `build/llama_cpp.wasm.sha256`)
- source: `onicai/llama_cpp_onicai_fork` commit `91c63a2284ff99c5761a27c3865b312fb8eca148`
  (vendored at `PoAIW/llms/llama_cpp_canister`; see `BUILD-PROVENANCE.txt` +
  `build/llama_cpp.wasm.sha256`)
- deployed 2026-09-18 (upgraded from v0.16.8 `3db909db…` to fix the IC0502
  heap-out-of-bounds traps; see `TMP-HANDOVER-llama_cpp_canister-v0.17.0.md`)

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

Both **verified 2026-09-17**: `shasum -a 256` of each release `.gz` asset equals the
deployed module hash. Note the IC stores the **gzip-compressed** module, so the module
hash is the sha256 of the `.gz` file **as-is** — do NOT gunzip it first (see the group-D
verify command below).

### Group E — Frontend & Backend (outer funnAI repo)

Built in the **outer `funnAI` repo** (not PoAIW).

**Frontend** is a dfx `type: assets` canister. Its **module hash is dfx's stock
certified-assets wasm** and does not include the UI. The reproducible artifact is
`out/dist.fingerprint` (sha256 of the sorted per-file manifest). Compare that to
live HTTPS bodies with `make docker-verify-frontend`, not `dfx canister info`.

**Backend** is Motoko; verify like group A via `make docker-verify-wasm`.

| role     | canister-id                   | source (funnAI)   | verified                         | deployed module hash                                             |
| -------- | ----------------------------- | ----------------- | -------------------------------- | ---------------------------------------------------------------- |
| Frontend | `vizih-uiaaa-aaaaa-qavaa-cai` | `funnai_frontend` | kit added; fingerprint unrecorded | 423f20ee4e5daf8f76d6bb2b4a87440227f15b26cf874c132fd75d83e252c8f6 |
| Backend  | `6wp2z-paaaa-aaaaa-qau7q-cai` | `funnai_backend`  | kit exists; not yet confirmed    | 9fca8da6b78fe5c4aa0957596c28c32ebe90bdb16573c64880809577aca688cb |

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
cd PoAIW && git checkout 5e262d2
cd src/mAIner && make docker-build-wasm        # must print ce262a7b1167a862... (verified 2026-09-17)

# 2. BUILD -> PROMOTED (the hash mAInerCreator hands out must be that build)
dfx canister --network prd call --query r2n3m-oqaaa-aaaaa-qanaq-cai getSha256HashesAdmin
#   -> mainerControllerWasmSha256 must equal the hash from step 1

# 3. PROMOTED -> DEPLOYED (every ShareAgent must actually run it)
dfx canister --network prd info <any-ShareAgent-canister-id>   # Module hash must equal it
scripts/audit_mainer_controllers.sh --network prd              # fleet-wide: one line if all 754 agree
```

For the **ShareService controller**, verify directly (it has no on-chain expected hash):
`make docker-verify-wasm VERIFY_NETWORK=prd VERIFY_CANISTER=rilmv-caaaa-aaaaa-qandq-cai`.
As of 2026-09-17 this reports **MISMATCH** — the `main` build yields `ce262a7b…` (the
fleet) while ShareService still runs the older `7e149b67…` (see the group-B table note). It
becomes verifiable once ShareService is redeployed from a `main` build.

### C. LLM canisters

Permissionless: read a deployed LLM's module hash and compare to the release sha256.

```bash
dfx canister --network ic info psgg4-iqaaa-aaaac-qgtza-cai   # any of the 9; must be 0x4f89aa15...
```

Full reproduce: build the release from `onicai/llama_cpp_canister` at the fork commit
`91c63a2…` (`make docker-build-base` + `make docker-verify-wasm`); the vendored copy at
`PoAIW/llms/llama_cpp_canister` ships only the pre-built artifact + `BUILD-PROVENANCE.txt`.

### D. Token Ledger & Index

Not built here — verify the deployed hash against the DFINITY release asset:

```bash
curl -sL https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-01-07/ic-icrc1-ledger.wasm.gz | shasum -a 256
#   -> must equal the deployed Token Ledger module hash 3b03d1bb...  (verified 2026-09-17)
#   The IC stores the gzip-compressed module, so hash the .gz AS-IS — do NOT gunzip.
#   Index: same with ic-icrc1-index-ng.wasm.gz -> must equal e155db9d...
```

### E. Frontend & Backend (outer funnAI repo)

**Frontend** — assets canister. The module hash is the stock asset runtime; the UI is
`dist/`. The bundle inlines `canister_ids.json`, so the artifact is per-network.

```bash
cd src/funnai_frontend
make docker-build-frontend NETWORK=prd     # prints out/dist.fingerprint
make docker-verify-frontend VERIFY_NETWORK=prd
# MATCH means every file in dist/ is served bit-for-bit at
# https://vizih-uiaaa-aaaaa-qavaa-cai.icp0.io/...
```

Record `out/dist.fingerprint` (and the commit) in the group-E table after the first
Docker-built deploy. Do not treat the module hash as a UI check.

**Backend** — Motoko, same pattern as group A:

```bash
cd src/funnai_backend
make docker-build-base
make docker-build-wasm                     # prints sha256 of out/funnai_backend.wasm
make docker-verify-wasm VERIFY_NETWORK=prd
```

## Read every deployed hash at once

```bash
source scripts/canister_ids-prd.env
for v in $(grep -oE '^SUBNET_[A-Z0-9_]+' scripts/canister_ids-prd.env | sort -u); do
  id=${!v}; [ -n "$id" ] || continue
  printf '%-34s %s  ' "$v" "$id"
  dfx canister --network prd info "$id" 2>&1 | grep -oE '0x[0-9a-f]+' || echo "(no module hash)"
done
```
