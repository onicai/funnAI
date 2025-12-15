import type { Principal } from '@dfinity/principal';
import type { ActorMethod } from '@dfinity/agent';
import type { IDL } from '@dfinity/candid';

export type Address = string;
export type PublickeyHex = string;
export type PublicKey = Uint8Array | number[];
export type CanisterPublicKey = PublicKey;
export type SessionKey = PublicKey;
export type SiwbMessage = string;
export type SiwbSignature = string;
export type Timestamp = bigint;

export type RuntimeFeature = { 'IncludeUriInSeed': null } |
  { 'DisableEthToPrincipalMapping': null } |
  { 'DisablePrincipalToEthMapping': null };

export type SignMessageType = { 'ECDSA': null } |
  { 'Bip322Simple': null };

export interface SettingsInput {
  'domain': string,
  'uri': string,
  'salt': string,
  'network': [] | [string],
  'scheme': [] | [string],
  'statement': [] | [string],
  'sign_in_expires_in': [] | [bigint],
  'session_expires_in': [] | [bigint],
  'targets': [] | [Array<string>],
  'runtime_features': [] | [Array<RuntimeFeature>],
}

export type GetAddressResponse = { 'Ok': Address } |
  { 'Err': string };

export interface Delegation {
  'pubkey': PublicKey,
  'expiration': Timestamp,
  'targets': [] | [Array<Principal>],
}

export interface SignedDelegation {
  'delegation': Delegation,
  'signature': Uint8Array | number[],
}

export type GetDelegationResponse = { 'Ok': SignedDelegation } |
  { 'Err': string };

export type GetPrincipalResponse = { 'Ok': Uint8Array | number[] } |
  { 'Err': string };

export interface LoginDetails {
  'expiration': Timestamp,
  'user_canister_pubkey': CanisterPublicKey,
}

export type LoginResponse = { 'Ok': LoginDetails } |
  { 'Err': string };

export type PrepareLoginResponse = { 'Ok': SiwbMessage } |
  { 'Err': string };

export interface _SERVICE {
  'get_address': ActorMethod<[Uint8Array | number[], string], GetAddressResponse>,
  'get_caller_address': ActorMethod<[[] | [string]], GetAddressResponse>,
  'get_principal': ActorMethod<[Address], GetPrincipalResponse>,
  'siwb_prepare_login': ActorMethod<[Address], PrepareLoginResponse>,
  'siwb_login': ActorMethod<
    [SiwbSignature, Address, PublickeyHex, SessionKey, SignMessageType],
    LoginResponse
  >,
  'siwb_get_delegation': ActorMethod<
    [Address, SessionKey, Timestamp],
    GetDelegationResponse
  >,
  'prune_sigs': ActorMethod<[], undefined>,
}

export declare const idlFactory: IDL.InterfaceFactory;
export declare const init: (args: { IDL: typeof IDL }) => IDL.Type[];
