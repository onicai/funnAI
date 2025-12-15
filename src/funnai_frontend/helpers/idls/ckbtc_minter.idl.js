// ckBTC Minter IDL
// Canister ID: mqygn-kiaaa-aaaar-qaadq-cai (mainnet)

export const idlFactory = ({ IDL }) => {
  const Network = IDL.Variant({
    'mainnet' : IDL.Null,
    'testnet' : IDL.Null,
  });

  const Mode = IDL.Variant({
    'RestrictedTo' : IDL.Vec(IDL.Principal),
    'DepositsRestrictedTo' : IDL.Vec(IDL.Principal),
    'ReadOnly' : IDL.Null,
    'GeneralAvailability' : IDL.Null,
  });

  const UpgradeArgs = IDL.Record({
    'kyt_principal' : IDL.Opt(IDL.Principal),
    'mode' : IDL.Opt(Mode),
    'retrieve_btc_min_amount' : IDL.Opt(IDL.Nat64),
    'max_time_in_queue_nanos' : IDL.Opt(IDL.Nat64),
    'min_confirmations' : IDL.Opt(IDL.Nat32),
    'kyt_fee' : IDL.Opt(IDL.Nat64),
  });

  const InitArgs = IDL.Record({
    'kyt_principal' : IDL.Opt(IDL.Principal),
    'ecdsa_key_name' : IDL.Text,
    'mode' : Mode,
    'retrieve_btc_min_amount' : IDL.Nat64,
    'ledger_id' : IDL.Principal,
    'max_time_in_queue_nanos' : IDL.Nat64,
    'btc_network' : Network,
    'min_confirmations' : IDL.Opt(IDL.Nat32),
    'kyt_fee' : IDL.Opt(IDL.Nat64),
  });

  const MinterArg = IDL.Variant({
    'Upgrade' : IDL.Opt(UpgradeArgs),
    'Init' : InitArgs,
  });

  const Account = IDL.Record({
    'owner' : IDL.Principal,
    'subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
  });

  const EstimateWithdrawalFeeArg = IDL.Record({
    'amount' : IDL.Opt(IDL.Nat64),
  });

  const EstimateWithdrawalFeeResponse = IDL.Record({
    'minter_fee' : IDL.Nat64,
    'bitcoin_fee' : IDL.Nat64,
  });

  const BitcoinAddress = IDL.Text;

  const GetBtcAddressArgs = IDL.Record({
    'owner' : IDL.Opt(IDL.Principal),
    'subaccount' : IDL.Opt(IDL.Vec(IDL.Nat8)),
  });

  const Utxo = IDL.Record({
    'height' : IDL.Nat32,
    'value' : IDL.Nat64,
    'outpoint' : IDL.Record({
      'txid' : IDL.Vec(IDL.Nat8),
      'vout' : IDL.Nat32,
    }),
  });

  const UtxoStatus = IDL.Variant({
    'ValueTooSmall' : Utxo,
    'Tainted' : Utxo,
    'Minted' : IDL.Record({
      'minted_amount' : IDL.Nat64,
      'block_index' : IDL.Nat64,
      'utxo' : Utxo,
    }),
    'Checked' : Utxo,
  });

  const PendingUtxo = IDL.Record({
    'confirmations' : IDL.Nat32,
    'value' : IDL.Nat64,
    'outpoint' : IDL.Record({
      'txid' : IDL.Vec(IDL.Nat8),
      'vout' : IDL.Nat32,
    }),
  });

  const UpdateBalanceError = IDL.Variant({
    'GenericError' : IDL.Record({
      'error_message' : IDL.Text,
      'error_code' : IDL.Nat64,
    }),
    'TemporarilyUnavailable' : IDL.Text,
    'AlreadyProcessing' : IDL.Null,
    'NoNewUtxos' : IDL.Record({
      'required_confirmations' : IDL.Nat32,
      'pending_utxos' : IDL.Opt(IDL.Vec(PendingUtxo)),
      'current_confirmations' : IDL.Opt(IDL.Nat32),
    }),
  });

  const UpdateBalanceResult = IDL.Variant({
    'Ok' : IDL.Vec(UtxoStatus),
    'Err' : UpdateBalanceError,
  });

  const RetrieveBtcArgs = IDL.Record({
    'address' : BitcoinAddress,
    'amount' : IDL.Nat64,
  });

  const RetrieveBtcError = IDL.Variant({
    'MalformedAddress' : IDL.Text,
    'GenericError' : IDL.Record({
      'error_message' : IDL.Text,
      'error_code' : IDL.Nat64,
    }),
    'TemporarilyUnavailable' : IDL.Text,
    'AlreadyProcessing' : IDL.Null,
    'AmountTooLow' : IDL.Nat64,
    'InsufficientFunds' : IDL.Record({ 'balance' : IDL.Nat64 }),
  });

  const RetrieveBtcOk = IDL.Record({
    'block_index' : IDL.Nat64,
  });

  const RetrieveBtcResult = IDL.Variant({
    'Ok' : RetrieveBtcOk,
    'Err' : RetrieveBtcError,
  });

  const RetrieveBtcStatus = IDL.Variant({
    'Signing' : IDL.Null,
    'Confirmed' : IDL.Record({ 'txid' : IDL.Vec(IDL.Nat8) }),
    'Sending' : IDL.Record({ 'txid' : IDL.Vec(IDL.Nat8) }),
    'AmountTooLow' : IDL.Null,
    'Unknown' : IDL.Null,
    'Submitted' : IDL.Record({ 'txid' : IDL.Vec(IDL.Nat8) }),
    'Pending' : IDL.Null,
  });

  const RetrieveBtcStatusRequest = IDL.Record({
    'block_index' : IDL.Nat64,
  });

  const MinterInfo = IDL.Record({
    'retrieve_btc_min_amount' : IDL.Nat64,
    'min_confirmations' : IDL.Nat32,
    'kyt_fee' : IDL.Nat64,
  });

  return IDL.Service({
    'estimate_withdrawal_fee' : IDL.Func(
      [EstimateWithdrawalFeeArg],
      [IDL.Opt(EstimateWithdrawalFeeResponse)],
      ['query'],
    ),
    'get_btc_address' : IDL.Func(
      [GetBtcAddressArgs],
      [BitcoinAddress],
      [],
    ),
    'get_deposit_fee' : IDL.Func([], [IDL.Nat64], ['query']),
    'get_minter_info' : IDL.Func([], [MinterInfo], ['query']),
    'get_withdrawal_account' : IDL.Func([], [Account], []),
    'retrieve_btc' : IDL.Func(
      [RetrieveBtcArgs],
      [RetrieveBtcResult],
      [],
    ),
    'retrieve_btc_status' : IDL.Func(
      [RetrieveBtcStatusRequest],
      [RetrieveBtcStatus],
      ['query'],
    ),
    'update_balance' : IDL.Func(
      [GetBtcAddressArgs],
      [UpdateBalanceResult],
      [],
    ),
  });
};

export const init = ({ IDL }) => {
  const Network = IDL.Variant({
    'mainnet' : IDL.Null,
    'testnet' : IDL.Null,
  });

  const Mode = IDL.Variant({
    'RestrictedTo' : IDL.Vec(IDL.Principal),
    'DepositsRestrictedTo' : IDL.Vec(IDL.Principal),
    'ReadOnly' : IDL.Null,
    'GeneralAvailability' : IDL.Null,
  });

  const InitArgs = IDL.Record({
    'kyt_principal' : IDL.Opt(IDL.Principal),
    'ecdsa_key_name' : IDL.Text,
    'mode' : Mode,
    'retrieve_btc_min_amount' : IDL.Nat64,
    'ledger_id' : IDL.Principal,
    'max_time_in_queue_nanos' : IDL.Nat64,
    'btc_network' : Network,
    'min_confirmations' : IDL.Opt(IDL.Nat32),
    'kyt_fee' : IDL.Opt(IDL.Nat64),
  });

  const UpgradeArgs = IDL.Record({
    'kyt_principal' : IDL.Opt(IDL.Principal),
    'mode' : IDL.Opt(Mode),
    'retrieve_btc_min_amount' : IDL.Opt(IDL.Nat64),
    'max_time_in_queue_nanos' : IDL.Opt(IDL.Nat64),
    'min_confirmations' : IDL.Opt(IDL.Nat32),
    'kyt_fee' : IDL.Opt(IDL.Nat64),
  });

  const MinterArg = IDL.Variant({
    'Upgrade' : IDL.Opt(UpgradeArgs),
    'Init' : InitArgs,
  });

  return [MinterArg];
};

// Export canister IDs for convenience
export const CKBTC_MINTER_CANISTER_ID = "mqygn-kiaaa-aaaar-qaadq-cai";
export const CKBTC_LEDGER_CANISTER_ID = "mxzaz-hqaaa-aaaar-qaada-cai";

