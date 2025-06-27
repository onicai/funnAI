import base64
from typing import Union, List
from .ic_py_canister import get_canister, run_dfx_command
from .ckbtc import check_ckbtc_transaction


# ------------------------------------------------------------------------------
# allocation rules
def alloc_rule_iconfucius(iconfucius_share, cap):
    alloc = 0
    if iconfucius_share < 0.10:
        print(f"Found an iconfucius share of {iconfucius_share:.2f}% which is less than 0.10% -- WHAT TO DO ????")
        if iconfucius_share > 0.05:
            print("It is > 0.05 % -- allocating 1")
            alloc = 1
        else:
            print("It is <= 0.05 % -- allocating 0")
            alloc = 0
    elif iconfucius_share == 0.10:
        alloc = 1
    elif iconfucius_share < 0.25:
        alloc = 2
    else:
        # 1 additional per  0.25 % over  0.25%
        alloc = 2 + int((iconfucius_share - 0.25) / 0.25)

    alloc = min(alloc, cap)  # cap the allocation
    return alloc

def alloc_rule_iconfucius_lp(iconfucius_lp_share, cap):
    alloc = 0
    if iconfucius_lp_share <= 0.10:
        alloc = 0
    elif iconfucius_lp_share > 0.10 and iconfucius_lp_share <= 0.25:
        alloc = 1
    elif iconfucius_lp_share < 1.00:
        alloc = 2
    elif iconfucius_lp_share < 10.00:
        alloc = 3
    else:
        # 1 additional per 10.00 % over 10.00%
        alloc = 2 + int((iconfucius_lp_share - 10.00) / 10.00)

    alloc = min(alloc, cap)  # cap the allocation
    return alloc

def alloc_rule_icpp_art(num, cap=10):
    alloc = 0
    if num == 0:
        alloc = 0
    elif num >= 1 and num < 5:
        alloc = 1
    elif num < 20:
        alloc = 2
    elif num < 100:
        alloc = 3
    else:
        # 1 additional per 25 NFTs over 100
        alloc = 2 + int((num - 100) / 25)

    alloc = min(alloc, cap)  # cap the allocation
    return alloc

def alloc_rule_charles(num, cap=15):
    alloc = 0
    if num == 0:
        alloc = 0
    elif num == 1:
        alloc = 1
    elif num < 4:
        alloc = 2
    elif num < 20:
        alloc = 3
    else:
        # 1 additional per 10 NFTs over 20
        alloc = 2 + int((num - 20) / 10)

    alloc = min(alloc, cap)  # cap the allocation
    return alloc


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
