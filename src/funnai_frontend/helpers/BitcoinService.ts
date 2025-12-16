import { Actor, HttpAgent, Identity } from "@dfinity/agent";
import { Principal } from "@dfinity/principal";
import { store, HOST } from "../stores/store";
import { get } from "svelte/store";
import { 
  idlFactory as ckbtcMinterIdlFactory,
  CKBTC_MINTER_CANISTER_ID,
  CKBTC_LEDGER_CANISTER_ID
} from "./idls/ckbtc_minter.idl.js";
import { ICRC2_IDL as icrc2IDL } from "./idls/icrc2.idl.js";

let storeState;
store.subscribe((value) => storeState = value);

/**
 * Get the current authenticated identity from the store
 * Supports Internet Identity, NFID, and Bitcoin (SIWB) auth types
 */
async function getAuthenticatedIdentity(): Promise<Identity | undefined> {
  const state = get(store);
  
  // For Bitcoin (SIWB) users - stored delegated identity
  if (state.isAuthed === "bitcoin") {
    const identity = (globalThis as any).__siwb_delegated_identity__;
    if (identity) {
      console.log("Using SIWB delegated identity");
      return identity;
    }
    console.warn("Bitcoin auth but no delegated identity found");
    return undefined;
  }
  
  // For NFID users
  if (state.isAuthed === "nfid") {
    // Try stored signer client first
    const storedSignerClient = (globalThis as any).__nfid_signer_client__;
    if (storedSignerClient && typeof storedSignerClient.getIdentity === 'function') {
      const identity = storedSignerClient.getIdentity();
      if (identity) {
        console.log("Using NFID identity from signer client");
        return identity;
      }
    }
    // Try identity kit
    const identityKit = (globalThis as any).__nfid_identity_kit__;
    if (identityKit?.signerClient?.getIdentity) {
      const identity = identityKit.signerClient.getIdentity();
      if (identity) {
        console.log("Using NFID identity from identity kit");
        return identity;
      }
    }
    console.warn("NFID auth but no identity found");
    return undefined;
  }
  
  // For Internet Identity users
  if (state.isAuthed === "internetidentity" || state.isAuthed === "ii") {
    try {
      const { AuthClient } = await import("@dfinity/auth-client");
      const authClient = await AuthClient.create();
      if (await authClient.isAuthenticated()) {
        const identity = await authClient.getIdentity();
        console.log("Using Internet Identity");
        return identity;
      }
    } catch (err) {
      console.error("Error getting II identity:", err);
    }
    console.warn("II auth but no identity found");
    return undefined;
  }
  
  console.warn("No authenticated identity available");
  return undefined;
}

// Types for ckBTC operations
export interface UtxoStatus {
  Minted?: {
    minted_amount: bigint;
    block_index: bigint;
    utxo: {
      height: number;
      value: bigint;
      outpoint: { txid: Uint8Array; vout: number };
    };
  };
  ValueTooSmall?: any;
  Tainted?: any;
  Checked?: any;
}

export interface PendingUtxo {
  confirmations: number;
  value: bigint;
  outpoint: { txid: Uint8Array; vout: number };
}

export interface UpdateBalanceResult {
  Ok?: UtxoStatus[];
  Err?: {
    GenericError?: { error_message: string; error_code: bigint };
    TemporarilyUnavailable?: string;
    AlreadyProcessing?: null;
    NoNewUtxos?: {
      required_confirmations: number;
      pending_utxos: PendingUtxo[] | null;
      current_confirmations: number | null;
    };
  };
}

export interface RetrieveBtcResult {
  Ok?: { block_index: bigint };
  Err?: {
    MalformedAddress?: string;
    GenericError?: { error_message: string; error_code: bigint };
    TemporarilyUnavailable?: string;
    AlreadyProcessing?: null;
    AmountTooLow?: bigint;
    InsufficientFunds?: { balance: bigint };
  };
}

export interface MinterInfo {
  retrieve_btc_min_amount: bigint;
  min_confirmations: number;
  kyt_fee: bigint;
}

export interface WithdrawalFee {
  minter_fee: bigint;
  bitcoin_fee: bigint;
}

export interface RetrieveBtcStatus {
  Signing?: null;
  Confirmed?: { txid: Uint8Array };
  Sending?: { txid: Uint8Array };
  AmountTooLow?: null;
  Unknown?: null;
  Submitted?: { txid: Uint8Array };
  Pending?: null;
}

/**
 * BitcoinService - Service for ckBTC and Bitcoin-related operations
 * 
 * This service provides methods for:
 * - Getting BTC deposit addresses for minting ckBTC
 * - Updating ckBTC balance after BTC deposits
 * - Retrieving BTC (converting ckBTC back to BTC)
 * - Getting ckBTC balance
 */
export class BitcoinService {
  private static ckbtcMinterCanisterId = CKBTC_MINTER_CANISTER_ID;
  private static ckbtcLedgerCanisterId = CKBTC_LEDGER_CANISTER_ID;

  /**
   * Create an actor for the ckBTC minter canister
   * @param useAuthenticatedIdentity - If true, uses the authenticated user's identity
   */
  private static async getCkbtcMinterActor(useAuthenticatedIdentity = false) {
    const agentOptions: { host: string; identity?: Identity } = { host: HOST };
    
    if (useAuthenticatedIdentity) {
      const identity = await getAuthenticatedIdentity();
      if (identity) {
        agentOptions.identity = identity;
        console.log("Using authenticated identity for ckBTC minter");
      } else {
        console.warn("No authenticated identity found, using anonymous agent - this may fail for update_balance");
      }
    }
    
    const agent = new HttpAgent(agentOptions);
    
    // Fetch root key for local development
    if (process.env.DFX_NETWORK !== "ic" && process.env.NODE_ENV === "development") {
      await agent.fetchRootKey().catch(console.error);
    }

    return Actor.createActor(ckbtcMinterIdlFactory, {
      agent,
      canisterId: this.ckbtcMinterCanisterId,
    });
  }

  /**
   * Create an actor for the ckBTC ledger canister
   */
  private static async getCkbtcLedgerActor(useAuthenticatedIdentity = false) {
    let agent: HttpAgent;
    
    if (useAuthenticatedIdentity) {
      const identity = await getAuthenticatedIdentity();
      if (!identity) {
        throw new Error("No authenticated identity available for ledger operation");
      }
      agent = new HttpAgent({ host: HOST, identity });
      console.log("Using authenticated identity for ckBTC ledger");
    } else {
      agent = new HttpAgent({ host: HOST });
    }
    
    // Fetch root key for local development
    if (process.env.DFX_NETWORK !== "ic" && process.env.NODE_ENV === "development") {
      await agent.fetchRootKey().catch(console.error);
    }

    return Actor.createActor(icrc2IDL, {
      agent,
      canisterId: this.ckbtcLedgerCanisterId,
    });
  }

  /**
   * Get a BTC deposit address for the given principal
   * Users can send BTC to this address to receive ckBTC
   * 
   * @param principal - The ICP principal to get the deposit address for
   * @param subaccount - Optional subaccount
   * @returns The BTC deposit address
   */
  public static async getBtcDepositAddress(
    principal: Principal,
    subaccount?: Uint8Array
  ): Promise<string> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      
      const args = {
        owner: [principal],
        subaccount: subaccount ? [Array.from(subaccount)] : [],
      };
      
      const address = await minterActor.get_btc_address(args);
      console.log("BTC deposit address:", address);
      return address as string;
    } catch (error) {
      console.error("Error getting BTC deposit address:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get BTC deposit address: ${error.message}` 
          : "Failed to get BTC deposit address"
      );
    }
  }

  /**
   * Update ckBTC balance - call this after depositing BTC to mint ckBTC
   * IMPORTANT: This requires an authenticated identity as the ckBTC minter
   * doesn't allow anonymous callers
   * 
   * @param principal - The ICP principal to update balance for
   * @param subaccount - Optional subaccount
   * @returns The update balance result
   */
  public static async updateCkBtcBalance(
    principal: Principal,
    subaccount?: Uint8Array
  ): Promise<UpdateBalanceResult> {
    try {
      // Use authenticated identity - the minter requires a non-anonymous caller
      const minterActor = await this.getCkbtcMinterActor(true);
      
      const args = {
        owner: [principal],
        subaccount: subaccount ? [Array.from(subaccount)] : [],
      };
      
      const result = await minterActor.update_balance(args);
      console.log("Update balance result:", result);
      return result as UpdateBalanceResult;
    } catch (error) {
      console.error("Error updating ckBTC balance:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to update ckBTC balance: ${error.message}` 
          : "Failed to update ckBTC balance"
      );
    }
  }

  /**
   * Get ckBTC balance for a principal
   * 
   * @param principal - The ICP principal to get balance for
   * @returns The ckBTC balance in satoshis
   */
  public static async getCkBtcBalance(principal: Principal): Promise<bigint> {
    try {
      const ledgerActor = await this.getCkbtcLedgerActor();
      
      const account = {
        owner: principal,
        subaccount: [],
      };
      
      const balance = await ledgerActor.icrc1_balance_of(account);
      return balance as bigint;
    } catch (error) {
      console.error("Error getting ckBTC balance:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get ckBTC balance: ${error.message}` 
          : "Failed to get ckBTC balance"
      );
    }
  }

  /**
   * Retrieve BTC - convert ckBTC back to BTC
   * 
   * @param btcAddress - The BTC address to send to
   * @param amount - The amount in satoshis
   * @returns The retrieve BTC result
   */
  public static async retrieveBtc(
    btcAddress: string,
    amount: bigint
  ): Promise<RetrieveBtcResult> {
    try {
      // Log the identity being used for debugging
      const identity = await getAuthenticatedIdentity();
      if (identity) {
        const principal = identity.getPrincipal();
        console.log("retrieve_btc using identity with principal:", principal.toString());
      } else {
        console.warn("retrieve_btc: No authenticated identity found!");
        throw new Error("No authenticated identity - please log in again");
      }
      
      // Step 1: Get the withdrawal account from the minter
      console.log("Step 1: Getting withdrawal account...");
      const minterActor = await this.getCkbtcMinterActor(true);
      const withdrawalAccount = await minterActor.get_withdrawal_account();
      console.log("Withdrawal account:", withdrawalAccount);
      
      // Step 2: Transfer ckBTC to the withdrawal account
      console.log("Step 2: Transferring ckBTC to withdrawal account...");
      const ledgerActor = await this.getCkbtcLedgerActor(true);
      
      // ckBTC has 8 decimals, ledger fee is 10 satoshis
      const LEDGER_FEE = BigInt(10);
      
      const transferArgs = {
        to: {
          owner: withdrawalAccount.owner,
          subaccount: withdrawalAccount.subaccount,
        },
        fee: [LEDGER_FEE],
        memo: [],
        from_subaccount: [],
        created_at_time: [],
        amount: amount,
      };
      
      console.log("Transfer args:", JSON.stringify(transferArgs, (k, v) => typeof v === 'bigint' ? v.toString() : v));
      
      const transferResult = await ledgerActor.icrc1_transfer(transferArgs);
      console.log("Transfer result:", transferResult);
      
      if ('Err' in transferResult) {
        const err = transferResult.Err;
        let errorMsg = "Transfer failed: ";
        if ('InsufficientFunds' in err) {
          errorMsg += `Insufficient funds. Balance: ${err.InsufficientFunds.balance}`;
        } else if ('BadFee' in err) {
          errorMsg += `Bad fee. Expected: ${err.BadFee.expected_fee}`;
        } else {
          errorMsg += JSON.stringify(err);
        }
        throw new Error(errorMsg);
      }
      
      console.log("Transfer successful! Block index:", transferResult.Ok);
      
      // Step 3: Call retrieve_btc
      console.log("Step 3: Calling retrieve_btc...");
      const args = {
        address: btcAddress,
        amount: amount,
      };
      
      const result = await minterActor.retrieve_btc(args);
      console.log("Retrieve BTC result:", result);
      return result as RetrieveBtcResult;
    } catch (error) {
      console.error("Error retrieving BTC:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to retrieve BTC: ${error.message}` 
          : "Failed to retrieve BTC"
      );
    }
  }

  /**
   * Get the minter info including minimum amounts and fees
   */
  public static async getMinterInfo(): Promise<MinterInfo> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      const info = await minterActor.get_minter_info();
      return info as MinterInfo;
    } catch (error) {
      console.error("Error getting minter info:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get minter info: ${error.message}` 
          : "Failed to get minter info"
      );
    }
  }

  /**
   * Estimate withdrawal fee for a given amount
   * 
   * @param amount - Optional amount to estimate fee for
   */
  public static async estimateWithdrawalFee(amount?: bigint): Promise<WithdrawalFee | null> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      const result = await minterActor.estimate_withdrawal_fee({
        amount: amount ? [amount] : [],
      });
      return result?.[0] as WithdrawalFee | null;
    } catch (error) {
      console.error("Error estimating withdrawal fee:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to estimate withdrawal fee: ${error.message}` 
          : "Failed to estimate withdrawal fee"
      );
    }
  }

  /**
   * Get the withdrawal account for the current user
   * This is the account that ckBTC should be transferred to before calling retrieve_btc
   */
  public static async getWithdrawalAccount(): Promise<{ owner: Principal; subaccount: Uint8Array | null }> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      const account = await minterActor.get_withdrawal_account();
      return {
        owner: account.owner as Principal,
        subaccount: account.subaccount?.[0] ? new Uint8Array(account.subaccount[0]) : null,
      };
    } catch (error) {
      console.error("Error getting withdrawal account:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get withdrawal account: ${error.message}` 
          : "Failed to get withdrawal account"
      );
    }
  }

  /**
   * Get the deposit fee (KYT fee)
   */
  public static async getDepositFee(): Promise<bigint> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      const fee = await minterActor.get_deposit_fee();
      return fee as bigint;
    } catch (error) {
      console.error("Error getting deposit fee:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get deposit fee: ${error.message}` 
          : "Failed to get deposit fee"
      );
    }
  }

  /**
   * Get the status of a BTC retrieval (withdrawal)
   * 
   * @param blockIndex - The block index returned from retrieve_btc
   * @returns The status of the withdrawal
   */
  public static async retrieveBtcStatus(blockIndex: bigint): Promise<RetrieveBtcStatus> {
    try {
      const minterActor = await this.getCkbtcMinterActor();
      const status = await minterActor.retrieve_btc_status({ block_index: blockIndex });
      return status as RetrieveBtcStatus;
    } catch (error) {
      console.error("Error getting retrieve BTC status:", error);
      throw new Error(
        error instanceof Error 
          ? `Failed to get withdrawal status: ${error.message}` 
          : "Failed to get withdrawal status"
      );
    }
  }

  /**
   * Format satoshis to BTC for display
   */
  public static formatSatoshisToBtc(satoshis: bigint): string {
    const btc = Number(satoshis) / 100_000_000;
    return btc.toFixed(8);
  }

  /**
   * Convert BTC to satoshis
   */
  public static btcToSatoshis(btc: number): bigint {
    return BigInt(Math.floor(btc * 100_000_000));
  }
}

// Export constants
export { CKBTC_MINTER_CANISTER_ID, CKBTC_LEDGER_CANISTER_ID };

