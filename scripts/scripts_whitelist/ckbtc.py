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
# Read the NFT collection snapshots from file
json_path = Path(__file__).parent / "snapshots" / "charles.json"
with open(json_path, "r") as f:
    charles = json.load(f)

json_path = Path(__file__).parent / "snapshots" / "icpp_art.json"
with open(json_path, "r") as f:
    icpp_art = json.load(f)

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
candid_path = Path(__file__).parent / "ckbtc_index_canister.did"
network = "ic" 
canister_id = "n5wcd-faaaa-aaaar-qaaea-cai"  # ckBTC index canister ID
ckbtc_index_canister = get_canister(canister_name, candid_path, network, canister_id)

# check status (liveness)
print("--\nChecking status of ckbtc index canister")
response = ckbtc_index_canister.status()
if "num_blocks_synced" in response[0].keys():
    print("Ok!")
else:
    print("Not OK, response is:")
    print(response)

# ---------------------------------------------------------------------------
# get ic-py based Canister instance for the ckBTC ledger canister
canister_name = ""
candid_path = Path(__file__).parent / "ckbtc_ledger_canister.did"
network = "ic" 
canister_id = "mxzaz-hqaaa-aaaar-qaada-cai"  # ckBTC ledger canister ID
ckbtc_ledger_canister = get_canister(canister_name, candid_path, network, canister_id)

# check status (liveness)
print("--\nChecking readiness of ckbtc ledgercanister")
response = ckbtc_ledger_canister.is_ledger_ready()
if response[0]:
    print("Ok!")
else:
    print("Not OK, response is:")
    print(response)

# ---------------------------------------------------------------------------
# get ic-py based Canister instance for the ckBTC minter canister
canister_name = ""
candid_path = Path(__file__).parent / "ckbtc_minter_canister.did"
network = "ic" 
canister_id = "mqygn-kiaaa-aaaar-qaadq-cai"  # ckBTC minter canister ID
ckbtc_minter_canister = get_canister(canister_name, candid_path, network, canister_id)

# check status (liveness)
print("--\nChecking readiness of ckbtc minter canister")
response = ckbtc_minter_canister.get_canister_status()
if response[0].get("status") == {'running': None}:
    print("Ok!")
else:
    print("Not OK, response is:")
    print(response)
        
# ---------------------------------------------------------------------------
bioniq_ckbtc_canister_id = "aclt4-uaaaa-aaaak-qb4zq-cai"



# Load the whitelist transactions from JSON file
json_path = Path(__file__).parent / "bioniq_claims_form_output.json"
with open(json_path, "r") as f:
    ckbtc_claim_transactions = json.load(f)

for ckbtc_claim_transaction in ckbtc_claim_transactions:
    bioniq_ckbtc_address = ckbtc_claim_transaction["bioniq_ckbtc_address"]
    bioniq_btc_address = ckbtc_claim_transaction["bioniq_btc_address"]
    funnai_principal = ckbtc_claim_transaction["funnai_principal"]
    print(f"Fetching transactions for {funnai_principal}...")

    # Define the ckBTC index accounts of the transaction to look up
    sub = bytes(principal_to_subaccount(bioniq_ckbtc_address))   # or change the helper to return bytes directly
    from_bioniq_account = {
        "owner": bioniq_ckbtc_canister_id,
        "subaccount": [sub] # opt blob
    }
    to_funnai_account = {
        "owner": funnai_principal,
        "subaccount": [] # opt blob , null means no subaccount
    }

    arg = {
        "account": to_funnai_account,
        "start": [], # opt nat, empty means start from most recent
        "max_results": int(1000)   # adjust as needed for all history
    }
    getTransactionsResult = ckbtc_index_canister.get_account_transactions(arg)
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

            print(f"on_chain_owner: {on_chain_owner}, on_chain_subaccount: {on_chain_subaccount}")

            if (on_chain_owner.to_str()== bioniq_ckbtc_canister_id       # owner matches
                and matches_principal(on_chain_subaccount, bioniq_ckbtc_address)):
                print("✅ found a transfer from the expected Bioniq sub-account > approve whitelist")
                whitelist = True
                break
    else:
        print("Error:", response["Err"]["message"])

    if whitelist:
        # Get the BTC address for this bioniq ckBTC address
        sub = bytes(principal_to_subaccount(bioniq_ckbtc_address)) 
        arg = {
            "owner": [bioniq_ckbtc_canister_id], # opt principal
            "subaccount": [sub] # opt blob
        }
        response = ckbtc_minter_canister.get_btc_address(arg)
        bioniq_btc_address = response[0]
        
        print("------------------------------------------------------------------")
        print(f"Whitelisting ok")
        print(f"  FunnAI principal    : {funnai_principal}")
        print(f"  Bioniq ckBTC address: {bioniq_ckbtc_address}")
        print(f"  Bioniq BTC address  : {bioniq_btc_address}")

        # OOPS --- WE NOW FOUND OUT THAT THE BIONIQ BTC ADDRESS IS NOT A CKBTC MANAGED ADDRESS... 
        #          RE-EVALUATING THE APPROACH TO ACCOUNT OWNERSHIP VERIFICATION...
        
        # Check how many Charles NFTs this user owns
        # TODO...

       