import json
import subprocess
from pathlib import Path
from ic.client import Client
from ic.agent import Agent
from ic.identity import Identity
from ic.common.ledger import Ledger
from ic.principal import Principal

from .ic_py_canister import get_canister, run_dfx_command

import hashlib
import binascii

def get_icp_balance(principal_str: str) -> float:
    """
    Return the ICP balance (as float) for the given principal string.
    """
    # 1. Initialize an anonymous agent on mainnet
    identity = Identity()             # random (anonymous) identity
    client   = Client(url="https://ic0.app")
    agent    = Agent(identity, client)
    ledger   = Ledger(agent)          # ledger canister interface:contentReference[oaicite:2]{index=2}

    # 2. Convert principal string to bytes (no signing needed for query)
    principal = Principal.from_str(principal_str)
    principal_bytes = principal.bytes  # raw principal bytes (no CRC)

    # 3. Compute the ICRC-1 account identifier (default subaccount = 32 zero bytes)
    subaccount = bytes(32)             # default subaccount = 32 zero bytes
    # Prepend the domain separator for account identifiers
    prefix = b"\x0Aaccount-id"        
    h = hashlib.sha224(prefix + principal_bytes + subaccount).digest()
    checksum = binascii.crc32(h) & 0xFFFFFFFF
    account_id = checksum.to_bytes(4, "big") + h

    # 4. Query the ledger canister for balance
    result = ledger.account_balance({"account": list(account_id)})  # type: ignore
    # The result is a list of records; extract the first record’s e8s field
    e8s = result[0]["e8s"]             # balance in 10^-8 ICP:contentReference[oaicite:3]{index=3}

    # 5. Convert to ICP (float)
    return e8s / 1e8

def get_icp_transactions(principal_str: str, max_results: int = 1000) -> dict:
    """
    Returns all the ICP transactions for the given principal string.
    """
    icp_index_canister_id = "qhbym-qaaaa-aaaaa-aaafq-cai" 

    # Run the dfx canister call command
    cmd = [
        "dfx", "canister", "call", 
        "--network", "ic",
        "--output", "json",
        icp_index_canister_id,
        "get_account_transactions",
        f'(record{{account=record {{owner = principal "{principal_str}"}}; max_results={max_results}:nat}})'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    # Parse the JSON response
    response_json = json.loads(result.stdout)

    return response_json.get('Ok', {})
