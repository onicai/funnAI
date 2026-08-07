# How icp-cli works

funnAI is built, tested and deployed with **[icp-cli](https://cli.internetcomputer.org)**
(the `icp` command), not dfx.

The `make e2e-*` targets in [README-setup.md](README-setup.md#running-the-whole-app-locally)
hide most of this, and for the normal loop you do not need it. But the moment you step
outside them — running one canister's tests, calling a canister by hand, deploying to a
mainnet environment — these concepts decide whether the command works. Nearly every setup
mistake traces back to standing in the wrong folder or naming the wrong environment.

Migrating from dfx? See
[README-developer-migration-guide-from-dfx-to-icp-cli.md](README-developer-migration-guide-from-dfx-to-icp-cli.md).

## Projects

> **A project is a folder containing an `icp.yaml`.**

`icp` finds it by walking up from your current directory, and a project owns three things:

1. **which canisters exist by name** — the `canisters:` block in its `icp.yaml`
2. **its canister ids** — under `.icp/`
3. **its own local replica** — icp-cli runs one local network *per project*

**funnAI has 16 projects, not one.** The repo root, `e2e/`, `src/funnai_backend/`, each of
the nine canisters in `PoAIW/src/*/`, and the four `PoAIW/llms/*/` folders each have their
own `icp.yaml`. That is why instructions say "from folder X" — `cd`-ing to the right
project is a real step, and outside one you get `failed to locate project directory`.

**One of those 16 is not like the others: `e2e/`.** Fifteen of them own a canister — its
source, its build recipe, its ids. `e2e/` owns **no source and builds nothing**. It exists
only to provide one network and one id store that the *whole* application can be deployed
onto together, because canisters on separate networks cannot call each other. Every canister
in its `icp.yaml` is declared `pre-built`, pointing at the artifact one of the other fifteen
produced.

That is the project you will spend most of your time using, through `make e2e-*` — see
[Running the whole app locally](README-setup.md#running-the-whole-app-locally). The per-canister projects
matter when you are building or unit-testing one canister on its own.

To see what a project declares, read its `icp.yaml`. That file is short and is the source of
truth; it is where you change things.

## Environments and networks

These are two different things, and every command has to be told which it is using.

- A **network** is a replica to talk to. There are two: `local` (a throwaway replica
  declared in `icp.yaml`) and `ic` (mainnet).
- An **environment** is a *named set of canister ids* on one of those networks. Several
  environments can share one network, differing only in which ids they point at.

funnAI has six environments; five of them run on `ic`:

```
environment          network      canister ids live in
-----------          -------      --------------------
local          -->   local        .icp/cache/mappings/local.ids.json   (throwaway)
prd            -->   ic     \
testing        -->   ic      |    .icp/data/mappings/<env>.ids.json    (committed)
development    -->   ic     /
```

`prd` is the production environment — the canisters serving https://funnai.onicai.com/.

There is a seventh, **`ic`**, which icp-cli always provides implicitly — you will not find it
in any `icp.yaml` here. It has no canister ids, so `-e ic` will not reach an existing funnAI
canister — it would *create new ones on mainnet and spend real cycles*. Use `-e prd` for
production; never `-e ic`.

Select an environment with `-e`, or a network with `-n`:

| you are targeting   | flag                | requires                                                       |
| ------------------- | ------------------- | -------------------------------------------------------------- |
| a canister **name** | `-e <env>` ONLY     | being inside that project (it reads its `icp.yaml` + id store) |
| a **principal**     | `-e <env>`          | being inside a project                                         |
| a **principal**     | `-n ic`             | nothing — works from any folder                                |
| a **principal**     | `-n local`          | being inside a project (`local` is declared there)             |
| a **principal**     | `-n <url> -k fetch` | nothing, but `--root-key` is mandatory for a URL               |

**Rule of thumb: use `-e <env>` for everything while inside a project.** It is the only
thing that works with names, and it works with principals too. Reach for `-n ic` only when
you have a bare principal and no project.

## Where canister ids live

| path                                | holds                                 | committed? |
| ----------------------------------- | ------------------------------------- | ---------- |
| `.icp/data/mappings/<env>.ids.json` | the **mainnet** canister ids          | yes        |
| `.icp/cache/`                       | build artifacts + local network state | no         |

> 🚨 **Never `rm -rf .icp` — only ever `.icp/cache`.** `.icp/data/` holds the mainnet
> canister ids for every environment. Deleting it loses them all.

There is one store per project, so the ids are spread over 16 files. That is deliberate —
one owner per canister, no duplicate stores to drift — but it makes a single id tedious to
look up by hand. To get them all in one table:

```bash
make ids                          # every canister on prd
make ids NETWORK=testing          # another environment
make ids FILTER=api               # just the ones matching "api"
python scripts/show_ids.py api_canister -q   # the bare id, for scripting
```

This reads the mapping files directly, so it is a *view*, not a second source of truth.

Most canisters are declared by name in their project's `icp.yaml`, with ids in
`.icp/data/mappings/`. Two families are not — they are addressed by principal instead, and
their ids live in a plain registry file:

| family                             | registry                           | why                                          |
| ---------------------------------- | ---------------------------------- | -------------------------------------------- |
| the ~744 `mainer_ctrlb_canister_N` | `PoAIW/src/mAIner/mainer_ids.json` | a 744-entry `icp.yaml` would be unmanageable |
| the ICRC token ledger + index      | `PoAIW/src/Token*/token_ids.json`  | downloaded wasms; nothing here rebuilds them |

`icp canister install <principal> --wasm ...` works with no project and no declaration,
which is what makes that possible.
