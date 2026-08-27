# Deployed wasm hashes

The record of **which build is deployed** on prd, so anyone — team or community — can
verify a canister is running the code this repo deploys.

The wasms are built from the **PoAIW** repo (checked out at `PoAIW/`), so the `commit`
column refers to PoAIW, not funnAI.

Read a deployed hash with no special rights:

```bash
dfx canister --network prd info <canister-id>   # prints "Module hash: 0x..."
```

Reproduce it from the recorded commit:

```bash
cd PoAIW && git checkout <commit>
cd src/mAIner && make docker-build-wasm   # or src/GameState, src/mAInerCreator
                                          # prints the sha256; must equal the table below
```

| role          | canister-id                   | deployed hash                                                      | commit         | date       |
| ------------- | ----------------------------- | ------------------------------------------------------------------ | -------------- | ---------- |
| ShareAgent    | *(754 mAIner canisters)*      | `ce262a7b1167a86204d4f80273b05b7b299df852a99e6c3134e1f22dd41199d7` | `968cc3a`      | 2026-08-26 |
| ShareService  | `rilmv-caaaa-aaaaa-qandq-cai` | `7e149b675f982bb948055326a22358508da2cbd472e7949aad1e2e40b0f3db6e` | *(unrecorded)* | ?          |
| GameState     | `r5m5y-diaaa-aaaaa-qanaa-cai` | `66e0da2a2fd68362d0be6216f212e7de03f60bd34b8e3e53e0e7e9d0bebd2926` | `968cc3a`      | 2026-08-25 |
| mAInerCreator | `r2n3m-oqaaa-aaaaa-qanaq-cai` | `6441d67f73af48d06e06106db1ce6f23eaf7d7c7782f352accead7a9a622d52d` | `968cc3a`      | 2026-08-25 |

Add a row per rollout. Record the commit you built from, not just the hash.

---

## TODO

### 1. Finish the table — cover every canister

`scripts/canister_ids-prd.env` defines ~24 canisters. This table covers four. Missing:

- **protocol**: Challenger, Judge, Api, Archive, Backend, Frontend, Index, Token, Treasury
- **LLMs**: `CHALLENGER_LLM_0`, `JUDGE_LLM_0..3`, `SHARE_SERVICE_LLM_0..3`

Read every hash **live** rather than copying from notes or older versions of this file.
The ShareService row here was wrong for exactly that reason until 2026-08-27: it
recorded `117eacbe…` while prd was actually running `7e149b67…`, and nobody had checked.

```bash
source scripts/canister_ids-prd.env
for v in $(grep -oE '^SUBNET_[A-Z0-9_]+' scripts/canister_ids-prd.env | sort -u); do
  id=${!v}; [ -n "$id" ] || continue
  printf '%-34s %s  ' "$v" "$id"
  dfx canister --network prd info "$id" 2>&1 | grep -oE '0x[0-9a-f]+' || echo "(no module hash)"
done
```

Open question: the **LLM canisters are built from `llama_cpp_canister`**, not PoAIW. The
`commit` column currently means "a PoAIW commit". Either add a `repo` column or qualify
those rows, otherwise the column is ambiguous for a third of the table.

### 2. Describe how to verify against a reproducible build

A "How to verify" section existed in the PoAIW version of this file and was dropped when
it was simplified on 2026-08-27. Recover it rather than rewriting from memory:

```bash
cd PoAIW && git show 06b81e0^:WASM-HASHES.md
```

It documented `make docker-verify-wasm VERIFY_NETWORK=prd [VERIFY_CANISTER=<id>]`.

**Building from source is the trust layer. Describe it for every role, ShareAgent
included.** Comparing a deployed hash against mAInerCreator's stored hash is circular
on its own: it proves every ShareAgent runs what mAInerCreator says it should, and
says nothing about whether that artifact is the source in this repo. Trust only
starts where someone reads the source and builds it themselves.

The full chain for a ShareAgent, and each link must be checked:

```bash
# 1. SOURCE -> BUILD. This is the trust anchor: you build the recorded commit yourself.
cd PoAIW && git checkout 968cc3a
cd src/mAIner && make docker-build-wasm        # must print ce262a7b1167a862...

# 2. BUILD -> PROMOTED. The hash mAInerCreator hands out must be the build from step 1.
dfx canister --network prd call --query r2n3m-oqaaa-aaaaa-qanaq-cai getSha256HashesAdmin
#   -> mainerControllerWasmSha256 must equal the hash from step 1

# 3. PROMOTED -> DEPLOYED. Every ShareAgent must actually be running it.
dfx canister --network prd info <any-ShareAgent-canister-id>
#   -> Module hash must equal the same value
#   fleet-wide: scripts/audit_mainer_controllers.sh --network prd
#   reports one line under "Module hashes" if all 754 agree
```

Step 1 is what makes steps 2 and 3 mean anything. Skipping it leaves you verifying
the protocol against itself.

The same applies to every other role - GameState, mAInerCreator, ShareService - except
that they have no on-chain expected hash, so it is step 1 compared directly against
`dfx canister info`. Write the equivalent recipe for each, naming the `src/` directory
to build in. A bare hash cannot be reproduced; that is what the `commit` column is for.

### 3. Link it from both READMEs — once the above is done

Add to the **bottom** of the README in both repos:

```markdown
To verify, see [WASM-HASHES.md](WASM-HASHES.md)
```

- `funnAI/README.md` — resolves to this file directly.
- `PoAIW/README.md` — resolves to `PoAIW/WASM-HASHES.md`, the pointer stub, which links
  on to this file. That is intended: the same line works in both repos, and a reader
  browsing PoAIW on GitHub still lands somewhere useful.

Note `PoAIW/README.md` currently has **no trailing newline**, so append carefully or the
new line joins the last one.

Do this last. A README that advertises verification should not point at a half-filled
table.
