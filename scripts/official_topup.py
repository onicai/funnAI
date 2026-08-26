"""
Top up a mAIner through the protocol's OFFICIAL top-up flow.

WHY THIS EXISTS
    A direct `dfx wallet send` / `IC0.deposit_cycles` reaches the canister without
    ever running its code, so `officialCyclesBalance` is NOT credited
    (mAIner/src/Main.mo:162 credits it only when msg.caller == GameState). The next
    `storeAndSubmitResponse` then sees currentCyclesBalance > officialCyclesBalance,
    reads it as an owner's unofficial top-up, and burns
        (actual - official) x (protocolOperationFeesCut x 9) / 100
    = 90% of the top-up at the live feesCut of 10.

    An upgrade normally hides this, because postupgrade re-baselines
    officialCyclesBalance afterwards. But a top-up done to RESCUE a failed upgrade
    is exactly the case where postupgrade never runs - so the penalty stands. The
    direct path is at its most dangerous precisely when it is most needed.

    This module uses the official route instead:

        icrc1_transfer  ICP -> GameState, memo = 0xAD || target_principal_bytes
               |  returns ledger block index
        GameState.topUpCyclesForAnyMainerAgent({ mainerAgentAddress; paymentTransactionBlockId })
               |  verifies payment + memo binding, applies the top-up bonus
        GameState -> Cycles.add -> mAIner.addCycles()  ->  officialCyclesBalance += amount

    No penalty, and the mAIner is credited for what was actually paid.

TWO IDENTITIES, ON PURPOSE
    GameState's verifyIncomingPayment binds the payment to the TARGET mAIner via the
    memo. It never compares the payer against msg.caller. So the ICP transfer and the
    redeem call may be made by different identities:

      - transfer: a dedicated identity whose PEM this script reads (icp-py-core needs
        the raw key). Keep only a small balance on it - it is a hot key.
      - redeem:   whatever identity dfx is currently using. No PEM needed.

    That way the maintainer identity is never exported to disk.

WHY NOT dfx FOR THE TRANSFER
    The bound memo is 11 bytes (1 marker + 10 principal bytes). `dfx ledger transfer`
    only takes an 8-byte Nat64 memo, and `dfx canister call ... icrc1_transfer` with a
    blob literal mis-parses the hex escapes and inflates it past the ledger's 32-byte
    limit. icp-py-core encodes it correctly. See PoAIW/src/GameState/scripts/pay_topup.py,
    which this generalises.

To run standalone:
    # from the folder: funnAI
    conda activate funnAI

    scripts/official_topup.sh --network prd --mainer <canister-id> [--icp 0.2] [--dry-run]

    # or let it size the payment from the canister's own shortfall:
    scripts/official_topup.sh --network prd --mainer <canister-id> --target-spendable 600
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import dotenv_values

SCRIPT_DIR = Path(__file__).parent.resolve()

ICP_LEDGER_CANISTER_ID = "ryjl3-tyaaa-aaaaa-aaaba-cai"
CMC_CANISTER_ID = "rkp4c-7iaaa-aaaaa-aaaca-cai"
MEMO_PAYMENT_MARKER = 0xAD
LEDGER_FEE_E8S = 10_000

# Default identity used ONLY for the ICP transfer. Its PEM must be readable, so it is
# deliberately NOT a maintainer identity. Create with:
#   dfx identity new funnai-topup --storage-mode plaintext
DEFAULT_TOPUP_IDENTITY = "funnai-topup"

# `install_code` needs roughly this much SPENDABLE (unreserved) balance. Derived from
# the one prd failure on 2026-08-25: qjfug-yiaaa-aaaaa-qbema-cai had 238.7 B spendable
# and the IC asked for 61.2 B more.
INSTALL_CODE_SPENDABLE_NEED = 300_000_000_000

# Default target to top up to: 2x the install requirement, so a canister is not left
# hovering on the edge for its next upgrade.
DEFAULT_TARGET_SPENDABLE = 600_000_000_000

# Idle burn grows with Memory Size. Fitted from unx3a-5aaaa-aaaaa-qbexq-cai before/after
# its snapshot (30.3 MB -> 64.7 MB, 1.639 -> 2.517 B/day) and validated against
# qjfug at 408.9 MB (predicted 11.31 vs actual 11.31 B/day).
IDLE_CYCLES_PER_MB_PER_DAY = 0.0255e9

# Round payments up to this granularity, and never send more than the cap in one go.
ICP_GRANULARITY = 0.05
MAX_ICP_PER_TOPUP = 2.0

LEDGER_DID = """
type Account = record { owner : principal; subaccount : opt blob };
type TransferArg = record {
  from_subaccount : opt blob;
  to : Account;
  amount : nat;
  fee : opt nat;
  memo : opt blob;
  created_at_time : opt nat64;
};
type TransferError = variant {
  BadFee : record { expected_fee : nat };
  BadBurn : record { min_burn_amount : nat };
  InsufficientFunds : record { balance : nat };
  TooOld;
  CreatedInFuture : record { ledger_time : nat64 };
  Duplicate : record { duplicate_of : nat };
  TemporarilyUnavailable;
  GenericError : record { error_code : nat; message : text };
};
type Result = variant { Ok : nat; Err : TransferError };
service : { icrc1_transfer : (TransferArg) -> (Result); }
"""


def _log(msg, level="INFO"):
    """Standalone logging. upgrade_mainers passes its own logger in via set_logger()."""
    print(f"[{level}] {msg}")


log_message = _log


def set_logger(fn):
    """Let a caller (upgrade_mainers) route our output into its own log file."""
    global log_message
    log_message = fn


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kw)


# --------------------------------------------------------------------------------
# Reading a canister's true spendable balance
# --------------------------------------------------------------------------------

def get_canister_cycle_state(network: str, address: str):
    """
    Parse `dfx canister status` into the numbers that decide whether an upgrade can
    be paid for. Returns None if the status cannot be read or parsed.

    `spendable` is the number that matters: the IC will not spend into the freezing
    reserve, so a canister can hold a healthy balance and still fail install_code.
    """
    try:
        r = _run(["dfx", "canister", "--network", network, "status", address])
    except subprocess.CalledProcessError as e:
        log_message(f"Could not read status of {address}: {e}", "WARNING")
        return None
    text = (r.stdout or "") + (r.stderr or "")

    def num(pattern):
        m = re.search(pattern, text)
        return int(m.group(1).replace("_", "")) if m else None

    balance = num(r"Balance:\s*([\d_]+)")
    idle = num(r"Idle cycles burned per day:\s*([\d_]+)")
    threshold = num(r"Freezing threshold:\s*([\d_]+)")
    memory = num(r"Memory Size:\s*([\d_]+)")
    if balance is None or idle is None or threshold is None:
        log_message(f"Could not parse cycle state for {address}", "WARNING")
        return None

    reserve = idle * (threshold / 86400)
    return {
        "balance": balance,
        "idle_per_day": idle,
        "threshold_s": threshold,
        "memory_bytes": memory or 0,
        "reserve": reserve,
        "spendable": balance - reserve,
    }


def predict_spendable_after_snapshot(state: dict) -> float:
    """
    Spendable AFTER the upgrade takes its snapshot.

    A snapshot is counted in Memory Size and charged in the idle burn, so taking one
    inflates the freezing reserve and REDUCES spendable. Predicting from the current
    (pre-snapshot) balance is what let qjfug-yiaaa-aaaaa-qbema-cai through the old
    check and then fail install_code: pre-snapshot it had 384.9 B spendable, post
    227.7 B, against a ~300 B requirement.

    A fresh snapshot adds roughly the canister's own memory, so model the memory-driven
    part of the idle burn as growing by the same amount again.
    """
    mem_mb = (state.get("memory_bytes") or 0) / 1e6
    idle_after = state["idle_per_day"] + IDLE_CYCLES_PER_MB_PER_DAY * mem_mb
    reserve_after = idle_after * (state["threshold_s"] / 86400)
    return state["balance"] - reserve_after


# --------------------------------------------------------------------------------
# Pricing
# --------------------------------------------------------------------------------

def get_cycles_per_icp(network: str) -> float:
    """Live conversion rate from the Cycles Minting Canister. 1 XDR == 1 T cycles."""
    r = _run(["dfx", "canister", "--network", network, "call", "--query",
              CMC_CANISTER_ID, "get_icp_xdr_conversion_rate"])
    m = re.search(r"xdr_permyriad_per_icp\s*=\s*([\d_]+)", r.stdout or "")
    if not m:
        raise RuntimeError("could not read xdr_permyriad_per_icp from the CMC")
    permyriad = int(m.group(1).replace("_", ""))
    return permyriad / 10_000 * 1e12


def get_topup_bonus_percent(network: str, gamestate: str) -> int:
    """The protocol adds a bonus on top-ups. Read it rather than assuming the default."""
    try:
        r = _run(["dfx", "canister", "--network", network, "call", "--query",
                  gamestate, "getBonusCyclesTopupInPercent"])
        m = re.search(r"Ok\s*=\s*([\d_]+)", r.stdout or "")
        if m:
            return int(m.group(1).replace("_", ""))
    except subprocess.CalledProcessError:
        pass
    log_message("Could not read the top-up bonus; assuming 0%", "WARNING")
    return 0


def get_protocol_fees_cut(network: str, gamestate: str) -> int:
    """
    Percent of an incoming ICP payment the protocol keeps for operational expenses
    before converting the remainder to cycles (GameState/src/Main.mo:4864):

        amountToKeep    = amount * protocolOperationFeesCut / 100
        amountForMainer = amount - amountToKeep

    Note getCyclesFlowAdmin is `public shared`, not a query, so this is an update call.
    """
    try:
        r = _run(["dfx", "canister", "--network", network, "call",
                  gamestate, "getCyclesFlowAdmin"])
        m = re.search(r"protocolOperationFeesCut\s*=\s*([\d_]+)", r.stdout or "")
        if m:
            return int(m.group(1).replace("_", ""))
    except subprocess.CalledProcessError:
        pass
    log_message("Could not read protocolOperationFeesCut; assuming 10%", "WARNING")
    return 10


def effective_cycles_per_icp(cycles_per_icp: float, bonus_percent: int,
                             fees_cut_percent: int) -> float:
    """
    Cycles a mAIner actually receives per ICP paid.

    The protocol takes its cut in ICP FIRST, and the top-up bonus applies to what is
    left. Verified on testing 2026-08-26: 0.05 ICP at 1.7402 T/ICP with a 50% bonus and
    a 10% cut credited 117.5 B, exactly 0.05 x 1.7402e12 x 0.9 x 1.5. Omitting the cut
    predicts 130.5 B - 10% optimistic, which would under-fund a computed top-up.
    """
    return cycles_per_icp * (1 - fees_cut_percent / 100) * (1 + bonus_percent / 100)


def icp_needed_for(cycles_shortfall: float, cycles_per_icp: float, bonus_percent: int,
                   fees_cut_percent: int = 10) -> float:
    """ICP to buy `cycles_shortfall` cycles, rounded up to ICP_GRANULARITY and capped."""
    effective = effective_cycles_per_icp(cycles_per_icp, bonus_percent, fees_cut_percent)
    raw = cycles_shortfall / effective
    rounded = math.ceil(raw / ICP_GRANULARITY) * ICP_GRANULARITY
    return min(max(rounded, ICP_GRANULARITY), MAX_ICP_PER_TOPUP)


# --------------------------------------------------------------------------------
# The official top-up itself
# --------------------------------------------------------------------------------

def _identity_pem(identity: str) -> str:
    pem = os.path.expanduser(f"~/.config/dfx/identity/{identity}/identity.pem")
    if not os.path.exists(pem):
        raise RuntimeError(
            f"no readable PEM for identity '{identity}' at {pem}.\n"
            f"Create a dedicated hot identity (do NOT export a maintainer identity):\n"
            f"  dfx identity new {identity} --storage-mode plaintext\n"
            f"then fund it:  dfx --identity {identity} ledger account-id"
        )
    return pem


def pay_icp_with_bound_memo(gamestate: str, target_mainer: str, e8s: int,
                            identity: str, ic_url: str = "https://ic0.app") -> int:
    """
    Transfer ICP to GameState with the 11-byte memo that binds it to `target_mainer`.
    Returns the ledger block index. Imports are local so that merely importing this
    module does not require icp-py-core.
    """
    from icp_agent import Agent, Client
    from icp_canister import Canister
    from icp_identity import Identity
    from icp_principal import Principal

    with open(_identity_pem(identity)) as f:
        ident = Identity.from_pem(f.read())
    agent = Agent(ident, Client(url=ic_url))
    ledger = Canister(agent, ICP_LEDGER_CANISTER_ID, LEDGER_DID)

    memo = bytes([MEMO_PAYMENT_MARKER]) + Principal.from_str(target_mainer).bytes
    result = ledger.icrc1_transfer(
        {
            "from_subaccount": None,
            "to": {"owner": Principal.from_str(gamestate), "subaccount": None},
            "amount": e8s,
            "fee": [LEDGER_FEE_E8S],
            "memo": [memo],
            "created_at_time": None,
        },
        verify_certificate=False,
    )
    value = result[0]["value"]
    if "Ok" not in value:
        raise RuntimeError(f"icrc1_transfer failed: {value.get('Err')}")
    return int(value["Ok"])


def redeem_topup(network: str, gamestate: str, target_mainer: str, block_id: int) -> dict:
    """
    Redeem a paid block against the mAIner. Runs as the CURRENT dfx identity - GameState
    binds the payment to the mAIner via the memo, not to the payer, so this needs no PEM.
    """
    arg = (f'(record {{ mainerAgentAddress = "{target_mainer}"; '
           f'paymentTransactionBlockId = {block_id} : nat64 }})')
    r = _run(["dfx", "canister", "--network", network, "call",
              gamestate, "topUpCyclesForAnyMainerAgent", arg])
    out = (r.stdout or "") + (r.stderr or "")
    if "Err" in out and "Ok" not in out:
        raise RuntimeError(f"topUpCyclesForAnyMainerAgent returned an error: {out.strip()}")
    m = re.search(r"cyclesAdded\s*=\s*([\d_]+)", out)
    return {"raw": out.strip(),
            "cycles_added": int(m.group(1).replace("_", "")) if m else None}


def official_topup(network: str, gamestate: str, target_mainer: str,
                   icp: float = None, target_spendable: int = DEFAULT_TARGET_SPENDABLE,
                   identity: str = DEFAULT_TOPUP_IDENTITY, dry_run: bool = False) -> bool:
    """
    Bring `target_mainer` up to `target_spendable` spendable cycles via the official
    flow. If `icp` is given it is used verbatim; otherwise the payment is sized from
    the canister's own post-snapshot shortfall.

    Returns True if the mAIner ends up (or already is) above the install requirement.
    """
    state = get_canister_cycle_state(network, target_mainer)
    if state is None:
        return False

    spend_now = predict_spendable_after_snapshot(state)
    log_message(
        f"{target_mainer}: balance={state['balance']/1e9:,.1f} B "
        f"reserve={state['reserve']/1e9:,.1f} B "
        f"memory={(state['memory_bytes'] or 0)/1e6:,.1f} MB | "
        f"spendable now={state['spendable']/1e9:,.1f} B, "
        f"after snapshot={spend_now/1e9:,.1f} B",
        "INFO",
    )

    # An explicit --icp means "send exactly this", so it overrides the short-circuit.
    # Without that override a healthy canister could never be used to test the flow.
    if icp is None and spend_now >= target_spendable:
        log_message(f"{target_mainer}: already above target; no top-up needed", "INFO")
        return True

    shortfall = target_spendable - spend_now
    cycles_per_icp = get_cycles_per_icp(network)
    bonus = get_topup_bonus_percent(network, gamestate)
    fees_cut = get_protocol_fees_cut(network, gamestate)
    amount_icp = icp if icp is not None else icp_needed_for(
        shortfall, cycles_per_icp, bonus, fees_cut)
    e8s = int(round(amount_icp * 1e8))
    expected = amount_icp * effective_cycles_per_icp(cycles_per_icp, bonus, fees_cut)

    log_message(
        f"{target_mainer}: short {shortfall/1e9:,.1f} B -> paying {amount_icp:.2f} ICP "
        f"({cycles_per_icp/1e12:.4f} T/ICP, -{fees_cut}% protocol cut, +{bonus}% bonus) "
        f"~= {expected/1e9:,.0f} B cycles",
        "INFO",
    )

    if dry_run:
        log_message(f"DRY RUN: would transfer {e8s} e8s with a memo bound to "
                    f"{target_mainer}, then redeem it via topUpCyclesForAnyMainerAgent",
                    "INFO")
        return True

    try:
        block = pay_icp_with_bound_memo(gamestate, target_mainer, e8s, identity)
        log_message(f"{target_mainer}: ICP transferred, ledger block {block}", "SUCCESS")
    except Exception as e:
        log_message(f"{target_mainer}: ICP transfer failed: {e}", "ERROR")
        return False

    try:
        result = redeem_topup(network, gamestate, target_mainer, block)
    except Exception as e:
        # The ICP is paid but unredeemed. The block is still valid and can be redeemed
        # later, so surface it loudly rather than losing it.
        log_message(f"{target_mainer}: PAID but redeem FAILED for block {block}: {e}", "ERROR")
        log_message(f"Retry with: dfx canister --network {network} call {gamestate} "
                    f'topUpCyclesForAnyMainerAgent \'(record {{ mainerAgentAddress = '
                    f'"{target_mainer}"; paymentTransactionBlockId = {block} : nat64 }})\'',
                    "ERROR")
        return False

    added = result.get("cycles_added")
    log_message(f"{target_mainer}: officially credited "
                f"{added/1e9:,.1f} B cycles" if added else
                f"{target_mainer}: redeemed block {block}", "SUCCESS")

    after = get_canister_cycle_state(network, target_mainer)
    if after:
        spend_after = predict_spendable_after_snapshot(after)
        log_message(f"{target_mainer}: spendable after snapshot now "
                    f"{spend_after/1e9:,.1f} B (was {spend_now/1e9:,.1f} B)", "INFO")
        if spend_after < INSTALL_CODE_SPENDABLE_NEED:
            log_message(f"{target_mainer}: STILL below the {INSTALL_CODE_SPENDABLE_NEED/1e9:,.0f} B "
                        f"install requirement", "WARNING")
            return False
    return True


def get_topup_account_balance_e8s(network: str, identity: str) -> int:
    """ICP balance of the top-up identity, in e8s. Read-only ledger query."""
    r = _run(["dfx", "--identity", identity, "identity", "get-principal"])
    principal = (r.stdout or "").strip()
    q = _run(["dfx", "canister", "--network", network, "call", "--query",
              ICP_LEDGER_CANISTER_ID, "icrc1_balance_of",
              f'(record {{ owner = principal "{principal}"; subaccount = null }})'])
    m = re.search(r"([\d_]+)\s*:\s*nat", q.stdout or "")
    if not m:
        raise RuntimeError(f"could not read the ICP balance of {identity}")
    return int(m.group(1).replace("_", ""))


def preflight_topup_budget(network: str, gamestate: str, addresses: list,
                           identity: str = DEFAULT_TOPUP_IDENTITY,
                           target_spendable: int = DEFAULT_TARGET_SPENDABLE,
                           safety_margin: float = 1.25):
    """
    Before a rollout: work out which of `addresses` cannot pay for install_code, how
    much ICP topping them all up would cost, and whether the top-up account holds it.

    Returns (ok, report). `ok` is False when the account is short - the caller should
    stop rather than discover it mid-rollout, because a canister that fails mid-flight
    is left with its timer stopped and its owner not earning.

    The margin covers ICP/XDR rate drift over a long run and the per-transfer ledger fee.
    """
    log_message(f"Pre-flight: checking top-up budget for {len(addresses)} mAIner(s)...", "INFO")
    try:
        cycles_per_icp = get_cycles_per_icp(network)
        bonus = get_topup_bonus_percent(network, gamestate)
        fees_cut = get_protocol_fees_cut(network, gamestate)
    except Exception as e:
        log_message(f"Pre-flight: could not read conversion rate/bonus: {e}", "WARNING")
        return True, {"skipped": True}

    need_topup, unreadable, total_icp = [], [], 0.0
    for i, addr in enumerate(addresses, 1):
        if i % 100 == 0:
            log_message(f"Pre-flight: scanned {i}/{len(addresses)}...", "INFO")
        state = get_canister_cycle_state(network, addr)
        if state is None:
            unreadable.append(addr)
            continue
        spend_after = predict_spendable_after_snapshot(state)
        if spend_after < INSTALL_CODE_SPENDABLE_NEED:
            icp = icp_needed_for(target_spendable - spend_after, cycles_per_icp, bonus, fees_cut)
            need_topup.append((addr, spend_after, icp))
            total_icp += icp

    required_e8s = int((total_icp * safety_margin) * 1e8) + LEDGER_FEE_E8S * len(need_topup)
    try:
        have_e8s = get_topup_account_balance_e8s(network, identity)
    except Exception as e:
        log_message(f"Pre-flight: could not read the top-up account balance: {e}", "WARNING")
        return True, {"skipped": True}

    report = {"need_topup": need_topup, "unreadable": unreadable,
              "total_icp": total_icp, "required_e8s": required_e8s,
              "have_e8s": have_e8s, "cycles_per_icp": cycles_per_icp, "bonus": bonus}

    log_message(f"Pre-flight: {len(need_topup)} of {len(addresses)} mAIner(s) cannot pay "
                f"for install_code and will need an official top-up", "INFO")
    if unreadable:
        log_message(f"Pre-flight: {len(unreadable)} mAIner(s) could not be read; "
                    f"they are NOT counted in the budget", "WARNING")
    for addr, spend, icp in need_topup:
        log_message(f"  {addr}  spendable-after-snapshot {spend/1e9:,.1f} B  -> {icp:.2f} ICP", "INFO")
    log_message(f"Pre-flight: need ~{total_icp:.2f} ICP (+{int((safety_margin-1)*100)}% margin "
                f"= {required_e8s/1e8:.2f} ICP), account '{identity}' holds "
                f"{have_e8s/1e8:.2f} ICP", "INFO")

    if have_e8s < required_e8s:
        short = (required_e8s - have_e8s) / 1e8
        log_message("=" * 70, "ERROR")
        log_message(f"NOT ENOUGH ICP for the top-ups this run needs.", "ERROR")
        log_message(f"  need   : {required_e8s/1e8:.2f} ICP", "ERROR")
        log_message(f"  have   : {have_e8s/1e8:.2f} ICP", "ERROR")
        log_message(f"  short  : {short:.2f} ICP", "ERROR")
        log_message("", "ERROR")
        log_message(f"Send at least {short:.2f} ICP to the '{identity}' account, then re-run.", "ERROR")
        log_message(f"Its account id:", "ERROR")
        log_message(f"  dfx --identity {identity} ledger account-id", "ERROR")
        log_message("", "ERROR")
        log_message(f"Stopping now rather than mid-rollout: a mAIner that fails partway is", "ERROR")
        log_message(f"left with its timer stopped and its owner not earning.", "ERROR")
        log_message(f"Re-running is safe - completed mAIners are skipped on module hash.", "ERROR")
        log_message("=" * 70, "ERROR")
        return False, report

    log_message("Pre-flight: top-up budget is sufficient", "SUCCESS")
    return True, report


def gamestate_id(network: str) -> str:
    env_path = SCRIPT_DIR / f"canister_ids-{network}.env"
    if not env_path.exists():
        raise RuntimeError(f"missing {env_path}")
    gs = dotenv_values(env_path).get("SUBNET_0_1_GAMESTATE", "").strip('"')
    if not gs:
        raise RuntimeError(f"SUBNET_0_1_GAMESTATE not set in {env_path}")
    return gs


def main():
    p = argparse.ArgumentParser(
        description="Top up a mAIner through the protocol's official ICP flow "
                    "(credits officialCyclesBalance; no 90% unofficial-topup penalty)."
    )
    p.add_argument("--network", required=True,
                   choices=["local", "ic", "testing", "demo", "development", "prd"])
    p.add_argument("--mainer", required=True, help="Target mAIner canister id")
    p.add_argument("--icp", type=float, default=None,
                   help="Exact ICP to send. Omit to size it from the shortfall.")
    p.add_argument("--target-spendable", type=float, default=DEFAULT_TARGET_SPENDABLE / 1e9,
                   help="Spendable cycles to reach, in BILLIONS (default 600)")
    p.add_argument("--identity", default=DEFAULT_TOPUP_IDENTITY,
                   help=f"dfx identity holding the ICP (default {DEFAULT_TOPUP_IDENTITY})")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    gs = gamestate_id(args.network)
    ok = official_topup(args.network, gs, args.mainer, icp=args.icp,
                        target_spendable=int(args.target_spendable * 1e9),
                        identity=args.identity, dry_run=args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
