# Deployed wasm hashes

Every canister the funnAI SNS controls, the source it is built from, and the hash it runs on
prd. Anyone can rebuild each wasm from source and check that it matches the deployed module
hash. No special rights are needed.

**Status: all 21 SNS `dapp_canisters` and the 754 ShareAgents reproduce from the commits
below (verified 2026-10-05).**

## Verify with your AI agent

You need git, Docker (builds run as `linux/amd64`; on Apple Silicon this is emulated and
slow) and [dfx](https://internetcomputer.org/docs/building-apps/getting-started/install).
Give your agent this prompt:

> Clone https://github.com/onicai/funnAI and read `WASM-HASHES.md`. For every canister in
> its tables, follow the "Build & verify" instructions: build the wasm from the listed
> commit, and read the deployed module hash with `dfx canister --network ic info
> <canister-id>`. Report one row per canister with the expected hash, your build's hash,
> the deployed hash and MATCH / MISMATCH. Do not trust any hash you did not build or read
> yourself.

`dfx` prints the module hash with a `0x` prefix. The tables use bare hex, which is how the
builds print it.

## Deployed hashes

### Protocol and app canisters

| canister                | canister-id                   | source                    | module hash                                                      |
| ----------------------- | ----------------------------- | ------------------------- | ---------------------------------------------------------------- |
| GameState               | `r5m5y-diaaa-aaaaa-qanaa-cai` | PoAIW `c69ed39` (A)       | e26a6419dbcfc98e1eff40c02cd10916cead203dff25814a779421efabf55d71 |
| Challenger              | `rtoqq-yyaaa-aaaaa-qanba-cai` | PoAIW `c69ed39` (A)       | 47f386b76144ef1a0fccd20608c099de7c83480a9a7e87a8ae1fa64b10f97db1 |
| Judge                   | `qmgdh-3aaaa-aaaaa-qanfq-cai` | PoAIW `c69ed39` (A)       | 24ade07da97f8e6026c15b150f81e6486360025fc846cf2eefa74bb195f7edd6 |
| mAInerCreator           | `r2n3m-oqaaa-aaaaa-qanaq-cai` | PoAIW `c69ed39` (A)       | 6441d67f73af48d06e06106db1ce6f23eaf7d7c7782f352accead7a9a622d52d |
| Treasury                | `qbhxa-ziaaa-aaaaa-qbqza-cai` | PoAIW `c69ed39` (A)       | df75427673a8a49c4cd03befdaf0c9b189e5e31e3e9f3481097ea8f5eaa006e7 |
| Archive                 | `yiobo-hyaaa-aaaaf-qdjnq-cai` | PoAIW `c69ed39` (A)       | 1220f961d72159c8ddbee7eb6f89ac71a1a054781e4db7ca90add749c37061b7 |
| API                     | `bgm6p-5aaaa-aaaaf-qbzda-cai` | PoAIW `c69ed39` (A)       | 13ef2f45052b5b914cb867a02b281440307ab6ce861ef489d34ab71a1ede5513 |
| ShareService controller | `rilmv-caaaa-aaaaa-qandq-cai` | PoAIW `c69ed39` (B)       | ce262a7b1167a86204d4f80273b05b7b299df852a99e6c3134e1f22dd41199d7 |
| Token Ledger (FUNNAI)   | `vpyot-zqaaa-aaaaa-qavaq-cai` | DFINITY release (D)       | 3b03d1bb1145edbcd11101ab2788517bc0f427c3bd7b342b9e3e7f42e29d5822 |
| Token Index             | `mziuv-biaaa-aaaaa-qccrq-cai` | DFINITY release (D)       | e155db9d06b6147ece4f9defe599844f132a7db21693265671aa6ac60912935f |
| Frontend                | `vizih-uiaaa-aaaaa-qavaa-cai` | funnAI `274e912` (E)      | see E: verify the assets, not the module hash                    |
| Backend                 | `6wp2z-paaaa-aaaaa-qau7q-cai` | funnAI `274e912` (E)      | 9fca8da6b78fe5c4aa0957596c28c32ebe90bdb16573c64880809577aca688cb |

### LLM canisters

All 9 run llama_cpp_canister v0.17.0, built from tag `v0.17.0-repro` (C):
`4f89aa1564470574acc5ae78e5b5f49f78d4f188c252760fa399e726e72d8820`.

| canister           | canister-id                   |
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

### ShareAgents (754 mAIner canisters)

They are not individually in the SNS `dapp_canisters`. Their only controller is
mAInerCreator, which is an SNS canister and installs the wasm they all run:
`ce262a7b1167a86204d4f80273b05b7b299df852a99e6c3134e1f22dd41199d7`, from PoAIW `c69ed39` (B).
This is the same wasm as the ShareService controller.

## Build & verify

Source repositories:

| repo                                         | commit                                     |
| -------------------------------------------- | ------------------------------------------ |
| https://github.com/onicai/PoAIW              | `c69ed39e370529ff3348f00b53d0ce6a542e0ced` |
| https://github.com/onicai/funnAI             | `274e9123d5e533f85c215b0b0f4e5dc5cc3b283c` |
| https://github.com/onicai/llama_cpp_canister | tag `v0.17.0-repro` (`2e568e5`)            |

### A. PoAIW Motoko canisters

```bash
git clone https://github.com/onicai/PoAIW.git && cd PoAIW && git checkout c69ed39
cd src/GameState            # or Challenger, Judge, mAInerCreator, Treasury, ArchiveChallenges, Api
make docker-build-base      # once; the shared toolchain image
make docker-verify-wasm VERIFY_NETWORK=prd   # builds, reads the deployed hash, prints MATCH / MISMATCH
```

### B. mAIner wasm (ShareService controller and every ShareAgent)

```bash
cd PoAIW/src/mAIner         # same checkout as A
make docker-verify-wasm VERIFY_NETWORK=prd   # compares against the ShareService controller
```

For the ShareAgents, `src/mAIner/canister_ids.json` lists every prd ShareAgent
(`mainer_ctrlb_canister_*`). Each must run `ce262a7b…`, and its only controller must be
mAInerCreator (`r2n3m-oqaaa-aaaaa-qanaq-cai`). This tallies module hash and controllers
across the whole fleet (754 public read-state calls):

```bash
python3 -c 'import json; d=json.load(open("canister_ids.json")); print("\n".join(v["prd"] for k,v in d.items() if k.startswith("mainer_ctrlb_canister_") and "prd" in v))' | while read id; do dfx canister --network ic info "$id" | tr '\n' ' ' | grep -oE 'Controllers: [^M]*|Module hash: 0x[0-9a-f]+' | tr '\n' ' '; echo; done | sort | uniq -c
```

It must print a single line, with a count of 754, showing
`Controllers: r2n3m-oqaaa-aaaaa-qanaq-cai` and `Module hash: 0xce262a7b…`.

### C. LLM canisters

```bash
git clone https://github.com/onicai/llama_cpp_canister.git && cd llama_cpp_canister && git checkout v0.17.0-repro
make docker-build-base
make docker-build-wasm      # must print 4f89aa15...; compare with `dfx canister --network ic info` for each LLM
```

`v0.17.0-repro` is the v0.17.0 source with its build image pinned completely. It adds the
exact Python package set (`docker/requirements-base.txt`) and locked crate versions for
`ic-wasi-polyfill` and `wasi2ic` (`docker/locks/`). Without these pins the image resolves
newer dependencies and the hash changes. `scripts/time_lock.py` regenerates those locks
from crates.io publish dates, so you can check that they are what the v0.17.0 release
build used:

```bash
docker run --rm --platform linux/amd64 -v "$PWD":/repo llama-cpp-canister-build:icpp-6.0.0-locked bash -c 'export RUSTUP_HOME=/root/.icpp/rust/1.93.0 CARGO_HOME=/root/.icpp/rust/1.93.0; for d in ic-wasi-polyfill wasi2ic; do cd /root/.icpp/rust/1.93.0/$d && rm -f Cargo.lock && cargo generate-lockfile -q && python /repo/scripts/time_lock.py 2026-09-18T02:55:10Z . >/dev/null && cmp Cargo.lock /repo/docker/locks/$d.Cargo.lock && echo "$d: identical"; done'
```

### D. Token Ledger and Index

These are the standard DFINITY ICRC canisters, not built from funnAI source. The IC stores
the gzipped module, so hash each `.gz` as-is, without unzipping it:

```bash
curl -sL https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-01-07/ic-icrc1-ledger.wasm.gz | shasum -a 256     # 3b03d1bb...
curl -sL https://github.com/dfinity/ic/releases/download/ledger-suite-icrc-2025-01-07/ic-icrc1-index-ng.wasm.gz | shasum -a 256   # e155db9d...
```

### E. Frontend and Backend

```bash
git clone https://github.com/onicai/funnAI.git && cd funnAI && git checkout 274e912
cd src/funnai_backend
make docker-build-base
make docker-verify-wasm VERIFY_NETWORK=prd   # MATCH / MISMATCH

cd ../funnai_frontend
make docker-verify-frontend VERIFY_NETWORK=prd
```

The frontend is an asset canister. Its module hash is DFINITY's stock asset-canister wasm
and says nothing about the UI. `docker-verify-frontend` builds `dist/` and checks that every
file is served bit for bit at https://vizih-uiaaa-aaaaa-qavaa-cai.icp0.io.
