import base64, json
from typing import Union, List

# from ic.client import Client
# from ic.agent import Agent
# from ic.identity import Identity
# from ic.canister import Canister
# from ic.candid import IDL
from ic.principal import Principal
from pathlib import Path
from .ic_py_canister import get_canister, run_dfx_command

# ------------------------------------------------------------------------------
# Helper functions
# ──────────────────────────────────────────────────────────────
# Textual principal  ↔  raw principal‐bytes (payload only)
# ──────────────────────────────────────────────────────────────
def _to_raw(principal_text: str) -> bytes:
    """
    Decode the canonical textual form (with dashes) to *payload* bytes.
    We strip the 4-byte CRC32 that is prepended in the text format.
    """
    b32 = principal_text.replace('-', '').upper()
    b32 += '=' * ((8 - len(b32) % 8) % 8)          # pad for base-32
    raw = base64.b32decode(b32)
    return raw[4:]                                 # drop CRC32 (first 4 bytes)


def _from_raw(raw: bytes) -> str:
    """Encode raw payload bytes back to the canonical textual form."""
    crc_prefixed = _add_crc32(raw)
    b32 = base64.b32encode(crc_prefixed).decode().lower().rstrip('=')
    return '-'.join(b32[i:i + 5] for i in range(0, len(b32), 5))


def _add_crc32(payload: bytes) -> bytes:
    import zlib
    return zlib.crc32(payload).to_bytes(4, 'big') + payload


# ──────────────────────────────────────────────────────────────
# Principal ➜ 32-byte sub-account   (ledger / ICRC convention)
# ──────────────────────────────────────────────────────────────
def principal_to_subaccount(principal: str) -> bytes:
    """
    Bioniq / ckBTC convention:
        sub = 00 00 00 || principal-payload   (right-padded with 0 to 29 B)
        ⇒ 3 + 29  = 32 bytes
    """
    body = _to_raw(principal)                      # ≤ 29 B
    if len(body) > 29:
        raise ValueError("Principal too long for sub-account derivation")
    body = body.ljust(29, b'\0')                   # pad on the right
    return b'\0\0\0' + body                        # 32-byte sub-account


# ──────────────────────────────────────────────────────────────
# One-way check: does this sub-account belong to principal ?
# Works with *any* shape ic-py may decode.
# ──────────────────────────────────────────────────────────────
OptBlob = Union[bytes, List[int], List[List[int]], List[bytes]]

def _blob_to_bytes(opt_blob: OptBlob) -> Union[bytes, None]:
    """
    • []          → None
    • [[…]]       → bytes(inner)
    • [ints]      → bytes(opt_blob)
    • bytes       → as is
    """
    if opt_blob is None or opt_blob == []:
        return None
    if isinstance(opt_blob, (bytes, bytearray)):
        return bytes(opt_blob)
    if isinstance(opt_blob, list):
        # Some(...)  => outer list has exactly one element
        inner = opt_blob[0] if opt_blob and isinstance(opt_blob[0], list) else opt_blob
        return bytes(inner)
    raise TypeError(f"Unexpected blob type: {type(opt_blob)}")


def matches_principal(sub_blob: OptBlob, principal: str) -> bool:
    """True iff `sub_blob` equals the derived sub-account of `principal`."""
    return _blob_to_bytes(sub_blob) == principal_to_subaccount(principal)


# ---------------------------------------------------------------------------
# get ic-py based Canister instance for the ckBTC index canister
canister_name = ""
candid_path = Path(__file__).parent / "ckbtc.did"
network = "ic" 
canister_id = "n5wcd-faaaa-aaaar-qaaea-cai"  # ckBTC index canister ID
canister_instance = get_canister(canister_name, candid_path, network, canister_id)

# check status (liveness)
print("--\nChecking status of canister")
response = canister_instance.status()
if "num_blocks_synced" in response[0].keys():
    print("Ok!")
else:
    print("Not OK, response is:")
    print(response)

# # Initialize the agent (no identity needed for anonymous query)
# client = Client()
# agent = Agent(Identity(), client)

# # Load the index canister interface (from its Candid .did, omitted for brevity)
# index_did = """
# service : {
#   get_account_transactions: (record { account: record { owner: principal; subaccount: opt blob }; start: opt nat; max_results: nat }) -> (variant { Ok: record { transactions: vec record { id: nat; transaction: record { transfer: opt record { from: record { owner: principal; subaccount: opt blob }; to: record { owner: principal; subaccount: opt blob }; amount: nat; fee: opt nat; memo: opt vec nat8; created_at_time: opt nat64 } }; timestamp: nat64 } }; Err: record { message: text } }) query;
# }
# """
# ckbtc_index = Canister(agent, canister_id="n5wcd-faaaa-aaaar-qaaea-cai", candid=IDL.from_text(index_did))

# Define the account: owner principal and (optional) subaccount.
# Here we assume the address is a principal and use subaccount=None.

bioniq_ckbtc_canister_id = "aclt4-uaaaa-aaaak-qb4zq-cai"

# Load the whitelist transactions from JSON file
json_path = Path(__file__).parent / "ckbtc_bioniq_whitelist_transactions.json"
with open(json_path, "r") as f:
    ckbtc_claim_transactions = json.load(f)

for ckbtc_claim_transaction in ckbtc_claim_transactions:
    from_bioniq_principal = ckbtc_claim_transaction["from_bioniq_principal"]
    to_funnai_principal = ckbtc_claim_transaction["to_funnai_principal"]
    print(f"Fetching transactions for {to_funnai_principal}...")

    # Define the ckBTC index accounts of the transaction to look up
    sub = bytes(principal_to_subaccount(from_bioniq_principal))   # or change the helper to return bytes directly
    from_bioniq_account = {
        "owner": bioniq_ckbtc_canister_id,
        "subaccount": [sub] # opt blob
    }
    to_funnai_account = {
        "owner": to_funnai_principal,
        "subaccount": [] # opt blob , null means no subaccount
    }

    arg = {
        "account": to_funnai_account,
        "start": [], # opt nat, empty means start from most recent
        "max_results": int(1000)   # adjust as needed for all history
    }
    getTransactionsResult = canister_instance.get_account_transactions(arg)
    response = getTransactionsResult[0]  # Get the first element of the tuple

    # Print timestamp, sender, amount, and transaction ID
    whitelist = False
    if "Ok" in response:
        txs = response["Ok"]["transactions"]
        for tx in txs:
            rec = tx["transaction"]
            # Check if the transfer is from the Bioniq account
            on_chain_owner = rec['transfer'][0]['from']['owner']
            on_chain_subaccount = rec['transfer'][0]['from']['subaccount']   # could be [], [[…]], …

            if (on_chain_owner.to_str()== bioniq_ckbtc_canister_id       # owner matches
                and matches_principal(on_chain_subaccount, from_bioniq_principal)):
                print("✅ found a transfer from the expected Bioniq sub-account > approve whitelist")
                whitelist = True
                break
    else:
        print("Error:", response["Err"]["message"])

    if whitelist:
        print(f"TODO - Whitelisting ok for funnAI ckBTCprincipal {to_funnai_principal}...")
       