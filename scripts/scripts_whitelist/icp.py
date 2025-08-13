import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
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


def principal_to_account_id(principal_str: str) -> str:
    """
    Convert a principal string to an account identifier (hex string).
    Uses the same logic as the get_icp_balance function.
    """
    try:
        # Convert principal string to bytes
        principal = Principal.from_str(principal_str)
        principal_bytes = principal.bytes  # raw principal bytes (no CRC)
        
        # Use default subaccount (32 zero bytes)
        subaccount = bytes(32)
        
        # Compute the account identifier
        prefix = b"\x0Aaccount-id"
        h = hashlib.sha224(prefix + principal_bytes + subaccount).digest()
        checksum = binascii.crc32(h) & 0xFFFFFFFF
        account_id = checksum.to_bytes(4, "big") + h
        
        return account_id.hex()
        
    except Exception as e:
        print(f"Error converting principal to account ID: {e}")
        return ""


def calculate_historical_balance(principal: str, icp_transactions: dict) -> List[Dict[str, Any]]:
    """
    Calculate historical balance over time from ICP transaction data.
    
    Args:
        principal: The principal string
        icp_transactions: Dict containing 'balance', 'transactions', etc.
    
    Returns:
        List of balance points over time, sorted chronologically (oldest first)
    """
    balance_history = []
    
    try:
        # Get current balance from the transaction data
        current_balance_e8s = int(icp_transactions.get('balance', '0'))
        current_balance_icp = current_balance_e8s / 100_000_000
        
        print(f"Current balance: {current_balance_icp:.8f} ICP ({current_balance_e8s} e8s)")
        
        # Get transactions
        transactions = icp_transactions.get('transactions', [])
        print(f"Processing {len(transactions)} transactions for historical analysis...")
        
        if not transactions:
            # No transactions, just return current balance
            balance_history.append({
                "timestamp": datetime.now().isoformat(),
                "balance_e8s": current_balance_e8s,
                "balance_icp": current_balance_icp,
                "event_type": "current_only",
                "description": "No transaction history available"
            })
            return balance_history
        
        # Convert principal to account identifier for transaction matching
        account_id = principal_to_account_id(principal)
        print(f"Principal {principal} -> Account ID: {account_id}")
        
        # Process transactions to build balance history
        # We'll work backwards from current balance through transactions
        running_balance = current_balance_e8s
        transaction_points = []
        
        # Sort transactions by timestamp (newest first for processing)
        sorted_transactions = []
        for tx in transactions:
            try:
                tx_data = tx.get('transaction', {})
                timestamp_data = tx_data.get('timestamp', [{}])[0] if tx_data.get('timestamp') else {}
                timestamp_nanos = timestamp_data.get('timestamp_nanos', 0)
                
                # Convert timestamp_nanos to int if it's a string
                if isinstance(timestamp_nanos, str):
                    timestamp_nanos = int(timestamp_nanos)
                
                sorted_transactions.append({
                    'tx_id': tx.get('id', ''),
                    'timestamp_nanos': timestamp_nanos,
                    'transaction': tx_data
                })
            except Exception as e:
                print(f"Error parsing transaction: {e}")
                continue
        
        # Sort by timestamp (newest first)
        sorted_transactions.sort(key=lambda x: x['timestamp_nanos'], reverse=True)
        
        # Process each transaction to calculate balance at that point
        for i, tx_info in enumerate(sorted_transactions):
            try:
                tx_data = tx_info['transaction']
                timestamp_nanos = tx_info['timestamp_nanos']
                tx_id = tx_info['tx_id']
                
                # Convert timestamp
                if timestamp_nanos:
                    try:
                        timestamp_dt = datetime.fromtimestamp(int(timestamp_nanos) / 1_000_000_000)
                        timestamp_str = timestamp_dt.isoformat()
                    except (ValueError, OverflowError):
                        timestamp_str = f"tx_{tx_id}"
                else:
                    timestamp_str = f"tx_{tx_id}"
                
                # Analyze the transaction operation
                operation = tx_data.get('operation', {})
                balance_change = 0
                tx_type = "unknown"
                amount_e8s = 0
                fee_e8s = 0
                description = ""
                
                if 'Transfer' in operation:
                    transfer = operation['Transfer']
                    amount_e8s = int(transfer.get('amount', {}).get('e8s', 0))
                    fee_e8s = int(transfer.get('fee', {}).get('e8s', 0))
                    from_account = transfer.get('from', '')
                    to_account = transfer.get('to', '')
                    
                    # Determine if this was incoming or outgoing for our account
                    if to_account == account_id:
                        # Incoming transfer
                        balance_change = amount_e8s
                        tx_type = "incoming_transfer"
                        description = f"Received {amount_e8s / 100_000_000:.8f} ICP"
                    elif from_account == account_id:
                        # Outgoing transfer (including fee)
                        balance_change = -(amount_e8s + fee_e8s)
                        tx_type = "outgoing_transfer"
                        description = f"Sent {amount_e8s / 100_000_000:.8f} ICP (fee: {fee_e8s / 100_000_000:.8f})"
                    else:
                        # Transaction doesn't involve our account directly
                        balance_change = 0
                        tx_type = "unrelated_transfer"
                        description = f"Unrelated transfer of {amount_e8s / 100_000_000:.8f} ICP"
                
                elif 'Mint' in operation:
                    mint = operation['Mint']
                    amount_e8s = int(mint.get('amount', {}).get('e8s', 0))
                    to_account = mint.get('to', '')
                    
                    if to_account == account_id:
                        balance_change = amount_e8s
                        tx_type = "mint"
                        description = f"Minted {amount_e8s / 100_000_000:.8f} ICP"
                
                elif 'Burn' in operation:
                    burn = operation['Burn']
                    amount_e8s = int(burn.get('amount', {}).get('e8s', 0))
                    from_account = burn.get('from', '')
                    
                    if from_account == account_id:
                        balance_change = -amount_e8s
                        tx_type = "burn"
                        description = f"Burned {amount_e8s / 100_000_000:.8f} ICP"
                
                # Calculate what the balance was before this transaction
                previous_balance = running_balance - balance_change
                
                transaction_points.append({
                    "timestamp": timestamp_str,
                    "timestamp_nanos": timestamp_nanos,
                    "balance_e8s": previous_balance,
                    "balance_icp": previous_balance / 100_000_000,
                    "event_type": "transaction",
                    "transaction_type": tx_type,
                    "transaction_id": tx_id,
                    "amount_e8s": amount_e8s,
                    "amount_icp": amount_e8s / 100_000_000,
                    "fee_e8s": fee_e8s,
                    "fee_icp": fee_e8s / 100_000_000,
                    "balance_change_e8s": balance_change,
                    "balance_change_icp": balance_change / 100_000_000,
                    "description": description
                })
                
                running_balance = previous_balance
                
            except Exception as e:
                print(f"Error processing transaction {tx_info.get('tx_id', 'unknown')}: {e}")
                continue
        
        # Add current balance as the final point
        balance_history.append({
            "timestamp": datetime.now().isoformat(),
            "timestamp_nanos": int(datetime.now().timestamp() * 1_000_000_000),
            "balance_e8s": current_balance_e8s,
            "balance_icp": current_balance_icp,
            "event_type": "current",
            "description": "Current balance"
        })
        
        # Add all transaction points
        balance_history.extend(transaction_points)
        
        # Sort by timestamp (oldest first)
        balance_history.sort(key=lambda x: x.get('timestamp_nanos', 0))
        
        print(f"Created {len(balance_history)} balance history points")
        
        return balance_history
        
    except Exception as e:
        print(f"Error calculating historical balance for {principal}: {e}")
        return [{
            "timestamp": datetime.now().isoformat(),
            "balance_e8s": 0,
            "balance_icp": 0.0,
            "event_type": "error",
            "description": f"Error calculating history: {str(e)}"
        }]