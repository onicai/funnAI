export const idlFactory = ({ IDL }) => {
  const Address = IDL.Text;
  const PublickeyHex = IDL.Text;
  const PublicKey = IDL.Vec(IDL.Nat8);
  const CanisterPublicKey = PublicKey;
  const Principal = IDL.Vec(IDL.Nat8);
  const SessionKey = PublicKey;
  const SiwbMessage = IDL.Text;
  const SiwbSignature = IDL.Text;
  const Timestamp = IDL.Nat64;
  const String = IDL.Text;

  const RuntimeFeature = IDL.Variant({
    'IncludeUriInSeed': IDL.Null,
    'DisableEthToPrincipalMapping': IDL.Null,
    'DisablePrincipalToEthMapping': IDL.Null,
  });

  const SignMessageType = IDL.Variant({
    'ECDSA': IDL.Null,
    'Bip322Simple': IDL.Null,
  });

  const SettingsInput = IDL.Record({
    'domain': IDL.Text,
    'uri': IDL.Text,
    'salt': IDL.Text,
    'network': IDL.Opt(IDL.Text),
    'scheme': IDL.Opt(IDL.Text),
    'statement': IDL.Opt(IDL.Text),
    'sign_in_expires_in': IDL.Opt(IDL.Nat64),
    'session_expires_in': IDL.Opt(IDL.Nat64),
    'targets': IDL.Opt(IDL.Vec(IDL.Text)),
    'runtime_features': IDL.Opt(IDL.Vec(RuntimeFeature)),
  });

  const GetAddressResponse = IDL.Variant({
    'Ok': Address,
    'Err': IDL.Text,
  });

  const Delegation = IDL.Record({
    'pubkey': PublicKey,
    'expiration': Timestamp,
    'targets': IDL.Opt(IDL.Vec(IDL.Principal)),
  });

  const SignedDelegation = IDL.Record({
    'delegation': Delegation,
    'signature': IDL.Vec(IDL.Nat8),
  });

  const GetDelegationResponse = IDL.Variant({
    'Ok': SignedDelegation,
    'Err': IDL.Text,
  });

  const GetPrincipalResponse = IDL.Variant({
    'Ok': Principal,
    'Err': IDL.Text,
  });

  const LoginDetails = IDL.Record({
    'expiration': Timestamp,
    'user_canister_pubkey': CanisterPublicKey,
  });

  const LoginResponse = IDL.Variant({
    'Ok': LoginDetails,
    'Err': IDL.Text,
  });

  const PrepareLoginResponse = IDL.Variant({
    'Ok': SiwbMessage,
    'Err': IDL.Text,
  });

  return IDL.Service({
    'get_address': IDL.Func([Principal, String], [GetAddressResponse], ['query']),
    'get_caller_address': IDL.Func([IDL.Opt(String)], [GetAddressResponse], ['query']),
    'get_principal': IDL.Func([Address], [GetPrincipalResponse], ['query']),
    'siwb_prepare_login': IDL.Func([Address], [PrepareLoginResponse], []),
    'siwb_login': IDL.Func(
      [SiwbSignature, Address, PublickeyHex, SessionKey, SignMessageType],
      [LoginResponse],
      []
    ),
    'siwb_get_delegation': IDL.Func(
      [Address, SessionKey, Timestamp],
      [GetDelegationResponse],
      ['query']
    ),
    'prune_sigs': IDL.Func([], [], []),
  });
};

export const init = ({ IDL }) => {
  const RuntimeFeature = IDL.Variant({
    'IncludeUriInSeed': IDL.Null,
    'DisableEthToPrincipalMapping': IDL.Null,
    'DisablePrincipalToEthMapping': IDL.Null,
  });

  const SettingsInput = IDL.Record({
    'domain': IDL.Text,
    'uri': IDL.Text,
    'salt': IDL.Text,
    'network': IDL.Opt(IDL.Text),
    'scheme': IDL.Opt(IDL.Text),
    'statement': IDL.Opt(IDL.Text),
    'sign_in_expires_in': IDL.Opt(IDL.Nat64),
    'session_expires_in': IDL.Opt(IDL.Nat64),
    'targets': IDL.Opt(IDL.Vec(IDL.Text)),
    'runtime_features': IDL.Opt(IDL.Vec(RuntimeFeature)),
  });

  return [SettingsInput];
};
