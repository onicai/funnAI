# funnAI frontend — reproducible build

This directory is the build kit for `funnai_frontend`. The app is a Vite 8 +
Svelte 5 UI deployed as a dfx **assets** canister.

The official build is Docker on `linux/amd64`. Independent parties can rebuild
from a git commit and check that the files served on-chain match that build
bit-for-bit.

## Why this is not a wasm hash

`funnai_backend` and the PoAIW Motoko canisters are one wasm. For those,
`sha256(out/<canister>.wasm)` equals `dfx canister info`'s module hash.

`funnai_frontend` is `type: assets` in the repo-root `dfx.json`. `dfx deploy`
does two separate things:

1. Installs dfx's **stock certified-assets wasm** (from the dfx cache). That
   module hash is the same for every project on the same dfx version. Updating
   HTML/JS/CSS **does not change it**.
2. Uploads **`dist/`** (the Vite output) through the asset API. That is the UI.

So `dfx canister info funnai_frontend` only proves "this is dfx's asset
canister runtime." It says nothing about whether the live site is this repo.

The trust artifact is therefore **`dist/`**, content-addressed as:

| file | meaning |
| --- | --- |
| `out/dist.sha256` | `sha256` of every served file, paths sorted (`LC_ALL=C`) |
| `out/dist.fingerprint` | `sha256` of that manifest — the single hash to record |
| `out/assets.tar.xz` | same files packed with GNU tar reproducible-archive flags |
| `out/versions.txt` | node/npm, network, commit, `SOURCE_DATE_EPOCH`, fingerprint |

`make docker-verify-frontend` hashes live HTTPS bodies at
`https://<canister-id>.icp0.io/...` against `out/dist.sha256`. That is the
frontend equivalent of `make docker-verify-wasm`.

## Relation to nns-dapp

[nns-dapp](https://github.com/dfinity/nns-dapp) (see their
[BUILD.md](https://github.com/dfinity/nns-dapp/blob/main/BUILD.md)) also uses a
Docker sandbox, `npm ci`, no host `.env`, and GNU tar with `--mtime` /
`--sort=name` / `--owner=0`. They then **bake `assets.tar.xz` into a Rust
canister**, so `sha256(nns-dapp.wasm.gz)` covers the UI.

This kit copies the frontend half of that workflow. It does **not** embed
assets in wasm: swapping `funnai_frontend` to a custom canister would change
controllers, custom domains, and the deploy path. Until an SNS proposal must
verify the UI via module hash alone, `dist.fingerprint` + HTTPS compare is the
correct check.

nns-dapp's own wording is "some level of reproducibility," not a fully hermetic
toolchain. Same tradeoff here: pin the compilers that emit the bundle (Node
image digest, `package-lock.json`); leave live distro `apt` indexes unpinned
because those packages do not emit JS.

## Quick start

From **this directory** (`src/funnai_frontend`):

```bash
make docker-build-frontend NETWORK=prd
```

That prints `out/dist.fingerprint`, writes artefacts under `out/`, and copies
Docker `dist/` to the repo-root `dist/` so dfx can upload it.

```bash
# from repo root (funnAI/)
dfx deploy funnai_frontend --network prd
```

`scripts/build-frontend.sh` (repo root) skips a second Vite build when
`dist/.reproducible-build` matches this git commit and `DFX_NETWORK`.

```bash
# from this directory — rebuilds, then compares live assets
make docker-verify-frontend VERIFY_NETWORK=prd
```

`MATCH` means every file in Docker `dist/` is served bit-for-bit at
`https://vizih-uiaaa-aaaaa-qavaa-cai.icp0.io/...` (prd).

```bash
make help
```

## Canister IDs (from repo-root `canister_ids.json`)

| network | canister id |
| --- | --- |
| prd | `vizih-uiaaa-aaaaa-qavaa-cai` |
| testing | `6twm3-uqaaa-aaaam-qd2xa-cai` |
| development | `zlbtt-2yaaa-aaaak-qufwa-cai` |

The Vite bundle **inlines** these IDs (and `DFX_NETWORK`) at build time. A prd
artifact is not a testing artifact. Always pass `NETWORK=` for the target.

## Makefile targets

| target | what it does |
| --- | --- |
| `docker-build-frontend` | `--no-cache` Docker Vite build; writes `out/` and repo-root `dist/` |
| `docker-verify-frontend` | runs the build, then `scripts/verify-assets.sh` against live HTTPS |
| `help` | prints targets and the trust-artifact reminder |

Variables (defaults in parentheses):

| variable | default | role |
| --- | --- | --- |
| `NETWORK` | `prd` | `DFX_NETWORK` baked into the bundle |
| `VERIFY_NETWORK` | same as `NETWORK` | which `canister_ids.json` entry to fetch |
| `COMMIT` | `git rev-parse HEAD` | written into `dist/.reproducible-build` |
| `SOURCE_DATE_EPOCH` | `git log -1 --pretty=%ct` | tar `--mtime` and any tool that honours it |

## What Docker does

Image: `node:22.21.1-bookworm-slim@sha256:25b3eb23a00590b7499f2a2ce939322727fcce1b15fdd69754fcd09536a3ae2c`
(`linux/amd64`, matches repo-root `.nvmrc`).

Inside the container:

1. Fail if a host `.env` leaked into the context.
2. Rewrite `git+ssh://github.com` to `https://` (no GitHub SSH keys in Docker).
   `pixeloids` is still pinned by commit in `package-lock.json`.
3. `npm ci` **without** `NODE_ENV=production` (Vite/Svelte/Tailwind are
   `devDependencies` and would be omitted otherwise).
4. `npx vite build` with `NODE_ENV=production` and `DFX_NETWORK`.
5. Fail if any `*.map` sourcemap appeared (`vite.config.ts` sets
   `build.sourcemap: false`).
6. Write stamp `dist/.reproducible-build` (not uploaded — ignored in
   `assets/.ic-assets.json`).
7. Emit `dist.sha256`, `dist.fingerprint`, `assets.tar.xz`, `versions.txt`.

The tarball uses the [reproducible-builds.org archive flags](https://reproducible-builds.org/docs/archives/):

```text
tar --mtime=@$SOURCE_DATE_EPOCH --sort=name --owner=0 --group=0
    --numeric-owner --format=gnu
```

Files in `dist/` are left **uncompressed**. dfx's asset uploader applies
encodings. nns-dapp gzips before packing because their Rust canister serves
gzip; that step would break dfx deploy here.

Context is the **repo root** (see `docker/docker-compose.yml`).
`.dockerignore` excludes `.env`, `.dfx`, `node_modules`, `dist`, `PoAIW`,
`src/funnai_backend`, and other paths that must not enter the image.

Copied into the image (and nothing else that affects the bundle):

- `package.json`, `package-lock.json`
- `dfx.json`, `canister_ids.json`
- `vite.config.ts`, `svelte.config.js`, `tsconfig.json`, `postcss.config.cjs`, `index.html`
- `src/funnai_frontend/`, `src/declarations/`
- `src/funnai_frontend/scripts/build.sh`

**Do not run `dfx generate` as part of this build.** The image uses the
committed `src/declarations/`. dfx 0.32 codegen imports `@icp-sdk/core/agent`
instead of `@dfinity/agent`; regenerating with a newer dfx than 0.29.2 can
break the frontend and will never match this Docker build.

## Deploy (do not rebuild on the host)

```bash
# from src/funnai_frontend
make docker-build-frontend NETWORK=$NETWORK

# from repo root
# Do not run `dfx generate` here.
dfx deploy funnai_frontend --network $NETWORK
```

`dfx.json` still has `"build": "npm run build"`. That calls
`scripts/build-frontend.sh`, which exits 0 without Vite when the stamp's
`COMMIT` equals `HEAD` and `NETWORK` equals `DFX_NETWORK`.

If the stamp is missing or stale, the host rebuilds with whatever Node is on
`$PATH` / nvm — that artifact is **not** the reproducible one. Re-run
`make docker-build-frontend` instead.

You may need asset-canister permissions:

```bash
dfx canister call funnai_frontend grant_permission '(record {permission = variant {Prepare}; to_principal = principal "<your-principal>"})'
dfx canister call funnai_frontend grant_permission '(record {permission = variant {Commit}; to_principal = principal "<your-principal>"})'
```

Post-SNS, this deploy step is replaced by an SNS proposal. The Docker
fingerprint is still the thing voters (or anyone) rebuild to check the UI.

After the first Docker-built deploy, record `out/dist.fingerprint` and the git
commit in [`WASM-HASHES.md`](../../WASM-HASHES.md) group E. The module hash
column there is the stock asset wasm; do not treat it as a UI check.

## Verify a live canister

```bash
make docker-verify-frontend VERIFY_NETWORK=prd
# or, if out/dist.sha256 is already from the commit you want:
VERIFY_NETWORK=prd bash scripts/verify-assets.sh
```

The script reads `canister_ids.json`, GETs each path with
`curl --compressed`, and compares `sha256` to the manifest. Config files
(`.reproducible-build`, `.ic-assets.json`) are skipped — they are not served.

A `MISMATCH` on today's prd is expected until the first Docker-built `dist/`
has been deployed. After that, `MATCH` is the pass criterion.

## Pins and non-determinism that were closed

| input | pin |
| --- | --- |
| Node | `22.21.1` via image digest; `.nvmrc` and `package.json` `engines` must stay in range (`^20.19` or `>=22.12`, Vite 8) |
| npm deps | `package-lock.json` + `npm ci` |
| `pixeloids` | `github:nicolasleao/pixeloids#cdb296ea82c28db5965641a8cc482493d6e40d1c`, lockfile `git+https://` |
| Network / canister IDs | `DFX_NETWORK` from the **process** environment only (`vite.config.ts`). A leftover dfx `.env` (`output_env_file`) cannot override it |
| Sourcemaps | `build.sourcemap: false`; build fails if any `*.map` appears |
| browserslist | explicit versions (`chrome >= 109`, …) instead of `last 2 … version` |
| Locale / time | `TZ=UTC`, `LANG=C.UTF-8`, `SOURCE_DATE_EPOCH` from the git commit |
| Host `.env` / `.dfx` / `node_modules` / `dist` | excluded by `.dockerignore`; image build **exits** if `.env` is present |

Apt packages (`git`, `ca-certificates`, `xz-utils`) are **not** patch-pinned.
Ubuntu deletes superseded versions; those tools fetch sources / pack tar, they
do not compile the bundle. Same reason as `src/docker/Dockerfile.base`.

This image is **not** `src/docker/Dockerfile.base` (Node 20.x unpinned, for
Motoko). Do not reuse the Motoko base for the frontend.

## Layout

```text
src/funnai_frontend/
  Makefile                 docker-build-frontend / docker-verify-frontend
  README.md                this file
  docker/
    Dockerfile             pinned Node image + npm ci + vite
    docker-compose.yml     context = repo root; copies /out -> out/
  scripts/
    build.sh               runs *inside* Docker; writes /out
    verify-assets.sh       compares out/dist.sha256 to live HTTPS
  out/                     gitignored build artefacts
  assets/.ic-assets.json   includes ignore for .reproducible-build

repo root (inputs the Docker build actually uses)
  package.json / package-lock.json / .nvmrc
  vite.config.ts / svelte.config.js / tsconfig.json / postcss.config.cjs
  index.html / dfx.json / canister_ids.json
  src/declarations/        committed dfx JS bindings — do not regenerate in Docker
  scripts/build-frontend.sh
      host wrapper: skip Vite if Docker stamp matches, else nvm + vite
  .dockerignore            frontend Docker context (repo root)
```

## CI

`.github/workflows/cicd-ubuntu.yml` job `reproducible-build funnai_frontend`
runs `make docker-build-frontend NETWORK=prd` on `ubuntu-22.04` and uploads
`dist.fingerprint`, `dist.sha256`, `assets.tar.xz`, `versions.txt`.

It does **not** call `docker-verify-frontend` (that needs the live IC). It
does **not** go through the Motoko smoketest matrix.

## What this kit does not do

- It does not change the on-chain module hash when you ship a new UI.
- It does not embed `dist/` in a custom wasm (nns-dapp style).
- It does not use `ic-wasm shrink` (that is for Motoko/Rust).
- It does not make `npm run build` on a laptop a reproducible build. Only
  Docker is.

## Recorded hashes

See [`WASM-HASHES.md`](../../WASM-HASHES.md) group E. Until a Docker-built
frontend has been deployed and `out/dist.fingerprint` recorded there, anyone
can still rebuild; they just have nothing on-chain to match yet.
