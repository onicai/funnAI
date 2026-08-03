[![funnAI](https://github.com/onicai/funnAI/actions/workflows/cicd-ubuntu.yml/badge.svg)](https://github.com/onicai/funnAI/actions/workflows/cicd-ubuntu.yml)

# funnAI

The code for https://funnai.onicai.com/

<img src="brand/icons/parrot.png" alt="funnAI Parrot" width="100">

To contribute, see [README-setup.md](README-setup.md).

---

## How this repo builds and deploys

funnAI runs on the Internet Computer and is built, tested and deployed with
**[icp-cli](https://cli.internetcomputer.org)** (the `icp` command). A few of its concepts
shape how this repo is laid out, so they are worth understanding before you start.

### Projects

> **A project is a folder containing an `icp.yaml`.**

`icp` finds it by walking up from your current directory, and a project owns three things:

1. **which canisters exist by name** — the `canisters:` block in its `icp.yaml`
2. **its canister ids** — under `.icp/`
3. **its own local replica** — icp-cli runs one local network *per project*

**funnAI has 16 projects, not one.** The repo root, `e2e/`, `src/funnai_backend/`, each of
the nine canisters in `PoAIW/src/*/`, and the four `PoAIW/llms/*/` folders each have their
own `icp.yaml`. That is why instructions say "from folder X" — `cd`-ing to the right
project is a real step, and outside one you get `failed to locate project directory`.

```bash
icp project show          # what the project you are standing in declares
icp environment list      # its environments
```

### Environments and networks

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
development    -->   ic      |
demo           -->   ic      |
backup         -->   ic     /
```

`prd` is the production environment — the canisters serving https://funnai.onicai.com/.

`icp environment list` shows a seventh, **`ic`**, which icp-cli always provides implicitly.
It is not declared in any `icp.yaml` here and has no canister ids, so `-e ic` will not reach
an existing funnAI canister — it would *create new ones on mainnet and spend real cycles*.
Use `-e prd` for production; never `-e ic`.

Select an environment with `-e`, or a network with `-n`:

| you are targeting   | flag                | requires                                                       |
| ------------------- | ------------------- | -------------------------------------------------------------- |
| a canister **name** | `-e <env>` ONLY     | being inside that project (it reads its `icp.yaml` + id store) |
| a **principal**     | `-e <env>`          | being inside a project                                         |
| a **principal**     | `-n ic`             | nothing — works from any folder                                |
| a **principal**     | `-n local`          | being inside a project (`local` is declared there)             |
| a **principal**     | `-n <url> -k fetch` | nothing, but `--root-key` is mandatory for a URL               |

Two things that catch people out:

```bash
# `-n` takes a NETWORK name. An environment name is not a network:
icp canister status <principal> -n prd
#   Error: project does not contain a network named 'prd'

# `-n` cannot be combined with a canister NAME at all, not even a valid network:
icp canister status game_state_canister -n local
#   Error: Specifying a network is not supported if you are targeting a canister by
#          name, specify an environment instead
```

**Rule of thumb: use `-e <env>` for everything while inside a project.** It is the only
thing that works with names, and it works with principals too. Reach for `-n ic` only when
you have a bare principal and no project — which is how the ops scripts drive the ~745
mAIner canisters and the LLM canisters without listing any of them in an `icp.yaml`.

### The local network

Each project gets its own replica, on a port the OS picks at start time
(`gateway.port: 0`). **The port changes every time you start it, so never hardcode it** —
read it back:

```bash
icp network start -d                  # prints e.g. "Network started on port 63840"
icp network status -e local --json    # .gateway_url / .api_url
```

To wipe local state and start clean:

```bash
icp network stop && rm -rf .icp/cache && icp network start -d
```

Because each project has its own replica, canisters in different projects cannot call each
other locally. To run the **whole application** — every canister, the LLM and the frontend
on one local network — use the end-to-end environment from the repo root:

```bash
make e2e-up          # build + deploy everything locally
make e2e-status      # URLs and per-canister health
make e2e-test        # system-level checks
make e2e-down
```

### Where canister ids live

| path                                | holds                                 | committed? |
| ----------------------------------- | ------------------------------------- | ---------- |
| `.icp/data/mappings/<env>.ids.json` | the **mainnet** canister ids          | yes        |
| `.icp/cache/`                       | build artifacts + local network state | no         |

> 🚨 **Never `rm -rf .icp` — only ever `.icp/cache`.** `.icp/data/` holds the mainnet
> canister ids for every environment. Deleting it loses them all.

Most canisters are declared by name in their project's `icp.yaml`, with ids in
`.icp/data/mappings/`. Two families are not — they are addressed by principal instead, and
their ids live in a plain registry file:

| family                             | registry                           | why                                          |
| ---------------------------------- | ---------------------------------- | -------------------------------------------- |
| the ~744 `mainer_ctrlb_canister_N` | `PoAIW/src/mAIner/mainer_ids.json` | a 744-entry `icp.yaml` would be unmanageable |
| the ICRC token ledger + index      | `PoAIW/src/Token*/token_ids.json`  | downloaded wasms; nothing here rebuilds them |

`icp canister install <principal> --wasm ...` works with no project and no declaration,
which is what makes that possible.
