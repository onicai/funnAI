import { Principal } from '@dfinity/principal';
import { createAnonymousActorHelper } from './utils/actorUtils';

// Token Index canister ID
const TOKEN_INDEX_CANISTER_ID = "mziuv-biaaa-aaaaa-qccrq-cai";

// Transaction data interfaces based on the API response
export interface TransactionMint {
  amount: string;
  created_at_time: [];
  memo: [];
  to: {
    owner: string;
    subaccount: [];
  };
}

export interface TransactionTransfer {
  amount: string;
  created_at_time: [];
  fee: [];
  from: {
    owner: string;
    subaccount: [];
  };
  memo: [];
  to: {
    owner: string;
    subaccount: [];
  };
}

export interface TransactionBurn {
  amount: string;
  created_at_time: [];
  from: {
    owner: string;
    subaccount: [];
  };
  memo: [];
}

export interface TransactionApprove {
  amount: string;
  created_at_time: [];
  expected_allowance: [];
  expires_at: [];
  fee: [];
  from: {
    owner: string;
    subaccount: [];
  };
  memo: [];
  spender: {
    owner: string;
    subaccount: [];
  };
}

export interface Transaction {
  id: string;
  transaction: {
    approve: TransactionApprove[];
    burn: TransactionBurn[];
    kind: "mint" | "transfer" | "burn" | "approve";
    mint: TransactionMint[];
    timestamp: string;
    transfer: TransactionTransfer[];
  };
}

export interface GetAccountTransactionsRequest {
  max_results: number; // Required nat (not optional)
  start: []; // Optional nat (empty array = none)
  account: {
    owner: Principal;
    subaccount: []; // Optional blob (empty array = none)
  };
}

// Processed transaction for UI display
export interface ProcessedTransaction {
  id: string;
  type: "mint" | "transfer" | "burn" | "approve";
  amount: bigint;
  timestamp: Date;
  from?: string;
  to?: string;
  spender?: string;
  fee?: bigint;
  memo?: string;
}

// IDL from Internet Computer dashboard for token index canister
const tokenIndexIDL = ({ IDL }: any) => {
  const Value = IDL.Rec();
  const UpgradeArg = IDL.Record({
    'ledger_id' : IDL.Opt(IDL.Principal),
    'retrieve_blocks_from_ledger_interval_seconds' : IDL.Opt(IDL.Nat64),
  });
  const InitArg = IDL.Record({
    'ledger_id' : IDL.Principal,
    'retrieve_blocks_from_ledger_interval_seconds' : IDL.Opt(IDL.Nat64),
  });
  const IndexArg = IDL.Variant({ 'Upgrade' : UpgradeArg, 'Init' : InitArg });
  const BlockIndex = IDL.Nat;
  const SubAccount = IDL.Vec(IDL.Nat8);
  const Account = IDL.Record({
    'owner' : IDL.Principal,
    'subaccount' : IDL.Opt(SubAccount),
  });
  const GetAccountTransactionsArgs = IDL.Record({
    'max_results' : IDL.Nat,
    'start' : IDL.Opt(BlockIndex),
    'account' : Account,
  });
  const Tokens = IDL.Nat;
  const Burn = IDL.Record({
    'from' : Account,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'amount' : IDL.Nat,
    'spender' : IDL.Opt(Account),
  });
  const Mint = IDL.Record({
    'to' : Account,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'amount' : IDL.Nat,
  });
  const Approve = IDL.Record({
    'fee' : IDL.Opt(IDL.Nat),
    'from' : Account,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'amount' : IDL.Nat,
    'expected_allowance' : IDL.Opt(IDL.Nat),
    'expires_at' : IDL.Opt(IDL.Nat64),
    'spender' : Account,
  });
  const Transfer = IDL.Record({
    'to' : Account,
    'fee' : IDL.Opt(IDL.Nat),
    'from' : Account,
    'memo' : IDL.Opt(IDL.Vec(IDL.Nat8)),
    'created_at_time' : IDL.Opt(IDL.Nat64),
    'amount' : IDL.Nat,
    'spender' : IDL.Opt(Account),
  });
  const Transaction = IDL.Record({
    'burn' : IDL.Opt(Burn),
    'kind' : IDL.Text,
    'mint' : IDL.Opt(Mint),
    'approve' : IDL.Opt(Approve),
    'timestamp' : IDL.Nat64,
    'transfer' : IDL.Opt(Transfer),
  });
  const TransactionWithId = IDL.Record({
    'id' : BlockIndex,
    'transaction' : Transaction,
  });
  const GetTransactions = IDL.Record({
    'balance' : Tokens,
    'transactions' : IDL.Vec(TransactionWithId),
    'oldest_tx_id' : IDL.Opt(BlockIndex),
  });
  const GetTransactionsErr = IDL.Record({ 'message' : IDL.Text });
  const GetTransactionsResult = IDL.Variant({
    'Ok' : GetTransactions,
    'Err' : GetTransactionsErr,
  });
  const GetBlocksRequest = IDL.Record({
    'start' : IDL.Nat,
    'length' : IDL.Nat,
  });
  const Map = IDL.Vec(IDL.Tuple(IDL.Text, Value));
  Value.fill(
    IDL.Variant({
      'Int' : IDL.Int,
      'Map' : Map,
      'Nat' : IDL.Nat,
      'Nat64' : IDL.Nat64,
      'Blob' : IDL.Vec(IDL.Nat8),
      'Text' : IDL.Text,
      'Array' : IDL.Vec(Value),
    })
  );
  const Block = Value;
  const GetBlocksResponse = IDL.Record({
    'blocks' : IDL.Vec(Block),
    'chain_length' : IDL.Nat64,
  });
  const FeeCollectorRanges = IDL.Record({
    'ranges' : IDL.Vec(
      IDL.Tuple(Account, IDL.Vec(IDL.Tuple(BlockIndex, BlockIndex)))
    ),
  });
  const ListSubaccountsArgs = IDL.Record({
    'owner' : IDL.Principal,
    'start' : IDL.Opt(SubAccount),
  });
  const Status = IDL.Record({ 'num_blocks_synced' : BlockIndex });
  return IDL.Service({
    'get_account_transactions' : IDL.Func(
        [GetAccountTransactionsArgs],
        [GetTransactionsResult],
        ['query'],
      ),
    'get_blocks' : IDL.Func([GetBlocksRequest], [GetBlocksResponse], ['query']),
    'get_fee_collectors_ranges' : IDL.Func([], [FeeCollectorRanges], ['query']),
    'icrc1_balance_of' : IDL.Func([Account], [Tokens], ['query']),
    'ledger_id' : IDL.Func([], [IDL.Principal], ['query']),
    'list_subaccounts' : IDL.Func(
        [ListSubaccountsArgs],
        [IDL.Vec(SubAccount)],
        ['query'],
      ),
    'status' : IDL.Func([], [Status], ['query']),
  });
};

export class TransactionService {
  private static cache = new Map<string, { data: ProcessedTransaction[]; timestamp: number; totalCount?: number }>();
  private static readonly CACHE_DURATION = 2 * 60 * 1000; // 2 minutes cache
  private static readonly MAX_CACHE_SIZE = 10; // Maximum number of cached entries
  private static actor: any = null;

  /**
   * Get the token index canister actor
   */
  private static getActor() {
    if (!this.actor) {
      this.actor = createAnonymousActorHelper(TOKEN_INDEX_CANISTER_ID, tokenIndexIDL);
    }
    return this.actor;
  }

  /**
   * Convert nanoseconds timestamp to Date
   */
  private static timestampToDate(timestampNs: string | number | bigint): Date {
    let ns: number;
    if (typeof timestampNs === 'bigint') {
      ns = Number(timestampNs);
    } else if (typeof timestampNs === 'number') {
      ns = timestampNs;
    } else {
      ns = parseInt(timestampNs);
    }
    
    // Convert nanoseconds to milliseconds
    const timestampMs = ns / 1_000_000;
    return new Date(timestampMs);
  }

  /**
   * Convert amount string to bigint (amounts are in e8s format)
   */
  private static parseAmount(amount: string | number | bigint): bigint {
    if (typeof amount === 'bigint') return amount;
    if (typeof amount === 'number') return BigInt(amount);
    if (typeof amount === 'string') {
      return BigInt(amount.replace(/_/g, ''));
    }
    return 0n;
  }

  /**
   * Process raw transaction data into UI-friendly format
   */
  private static processTransaction(rawTx: any): ProcessedTransaction {
    try {
      console.log("Processing transaction with proper IDL:", rawTx);
      
      // With proper IDL, we should have clean property names
      const id = rawTx.id || String(Math.random());
      const transaction = rawTx.transaction || rawTx;
      
      const kind = transaction.kind || "unknown";
      const timestamp = transaction.timestamp || Date.now().toString();
      
      console.log("Transaction details:", { id, kind, timestamp });
      
      let processed: ProcessedTransaction = {
        id: String(id),
        type: kind as any,
        amount: 0n,
        timestamp: this.timestampToDate(timestamp)
      };

      // Process different transaction types with Candid optional pattern
      // In Candid, optional fields are represented as [] (none) or [value] (some)
      const mint = transaction.mint;
      const transfer = transaction.transfer;
      const burn = transaction.burn;
      const approve = transaction.approve;
      
      // Check which transaction type is present
      
      switch (kind) {
        case "mint":
          // mint is [] | [Mint], so check if it's an array with a value
          if (Array.isArray(mint) && mint.length > 0) {
            const mintTx = mint[0];
            // Process mint transaction
            processed.amount = this.parseAmount(mintTx.amount || 0);
            processed.to = mintTx.to?.owner?.toString();
          } else if (mint && !Array.isArray(mint)) {
            // Fallback for direct object (shouldn't happen with proper IDL)
            // Process mint transaction (direct fallback)
            processed.amount = this.parseAmount(mint.amount || 0);
            processed.to = mint.to?.owner?.toString();
          }
          break;

        case "transfer":
          // transfer is [] | [Transfer]
          if (Array.isArray(transfer) && transfer.length > 0) {
            const transferTx = transfer[0];
            // Process transfer transaction
            
            processed.amount = this.parseAmount(transferTx.amount || 0);
            processed.from = transferTx.from?.owner?.toString();
            processed.to = transferTx.to?.owner?.toString();
            
            // Handle optional fee: [] | [bigint]
            if (Array.isArray(transferTx.fee) && transferTx.fee.length > 0) {
              processed.fee = this.parseAmount(transferTx.fee[0]);
            }
          } else if (transfer && !Array.isArray(transfer)) {
            // Fallback for direct object
            // Process transfer transaction (direct fallback)
            processed.amount = this.parseAmount(transfer.amount || 0);
            processed.from = transfer.from?.owner?.toString();
            processed.to = transfer.to?.owner?.toString();
            
            if (Array.isArray(transfer.fee) && transfer.fee.length > 0) {
              processed.fee = this.parseAmount(transfer.fee[0]);
            }
          }
          break;

        case "burn":
          // burn is [] | [Burn]
          if (Array.isArray(burn) && burn.length > 0) {
            const burnTx = burn[0];
            // Process burn transaction
            processed.amount = this.parseAmount(burnTx.amount || 0);
            processed.from = burnTx.from?.owner?.toString();
          } else if (burn && !Array.isArray(burn)) {
            // Process burn transaction (direct fallback)
            processed.amount = this.parseAmount(burn.amount || 0);
            processed.from = burn.from?.owner?.toString();
          }
          break;

        case "approve":
          // approve is [] | [Approve]
          if (Array.isArray(approve) && approve.length > 0) {
            const approveTx = approve[0];
            // Process approve transaction
            processed.amount = this.parseAmount(approveTx.amount || 0);
            processed.from = approveTx.from?.owner?.toString();
            processed.spender = approveTx.spender?.owner?.toString();
            
            if (Array.isArray(approveTx.fee) && approveTx.fee.length > 0) {
              processed.fee = this.parseAmount(approveTx.fee[0]);
            }
          } else if (approve && !Array.isArray(approve)) {
            // Process approve transaction (direct fallback)
            processed.amount = this.parseAmount(approve.amount || 0);
            processed.from = approve.from?.owner?.toString();
            processed.spender = approve.spender?.owner?.toString();
            
            if (Array.isArray(approve.fee) && approve.fee.length > 0) {
              processed.fee = this.parseAmount(approve.fee[0]);
            }
          }
          break;
      }

      return processed;
    } catch (error) {
      console.error("Error processing transaction:", error, rawTx);
      // Return a minimal transaction object as fallback
      return {
        id: String(Math.random()),
        type: "unknown" as any,
        amount: 0n,
        timestamp: new Date()
      };
    }
  }

  /**
   * Fetch transactions for a user account with pagination support
   */
  public static async fetchUserTransactions(
    principalId: string, 
    maxResults: number = 50,
    startFrom?: number
  ): Promise<ProcessedTransaction[]> {
    const cacheKey = `${principalId}-${maxResults}${startFrom ? `-${startFrom}` : ''}`;
    
    // Check cache first
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      console.log(`Using cached transaction data for ${principalId}`);
      return cached.data;
    }

    // Clean up old cache entries if we have too many
    if (this.cache.size >= this.MAX_CACHE_SIZE) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    try {
      console.log(`Fetching fresh transaction data for ${principalId}`);
      console.log(`Max results requested: ${maxResults}`);
      
      const actor = this.getActor();
      const principal = Principal.fromText(principalId);
      
      const request = {
        account: {
          owner: principal,
          subaccount: [] // Empty array for optional subaccount (means null)
        },
        start: startFrom ? [startFrom] : [], // Optional start block index (empty array = null)
        max_results: maxResults // Required nat
      };
      
      console.log("Request being sent to canister:", {
        account: {
          owner: principalId, // Log as string for readability
          subaccount: []
        },
        start: [],
        max_results: maxResults
      });

      const rawResponse = await actor.get_account_transactions(request);
      
      console.log("Raw response from canister:", rawResponse);
      console.log("Raw response JSON:", JSON.stringify(rawResponse, (key, value) => 
        typeof value === 'bigint' ? value.toString() + 'n' : value, 2));
      
      // With proper IDL, we should get a clean Result type
      let rawTransactions: any[] = [];
      
      if (rawResponse && typeof rawResponse === 'object') {
        if ('Ok' in rawResponse) {
          console.log("Found Ok result:", rawResponse.Ok);
          const okData = rawResponse.Ok;
          if (okData && 'transactions' in okData) {
            rawTransactions = okData.transactions;
            console.log("Found transactions array with length:", rawTransactions.length);
          }
        } else if ('Err' in rawResponse) {
          console.error("Canister returned error:", rawResponse.Err);
          throw new Error(`Canister error: ${rawResponse.Err}`);
        } else {
          console.error("Unexpected response format - no Ok/Err:", rawResponse);
          throw new Error("Invalid response format from canister");
        }
      } else {
        console.error("Response is not an object:", typeof rawResponse, rawResponse);
        throw new Error("Invalid response type from canister");
      }
      
      // Process transactions
      const processedTransactions = rawTransactions.map(tx => this.processTransaction(tx));
      
      // Sort by timestamp (newest first)
      processedTransactions.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

      // Cache the result
      this.cache.set(cacheKey, {
        data: processedTransactions,
        timestamp: Date.now()
      });

      console.log(`Fetched ${processedTransactions.length} transactions for ${principalId}`);
      return processedTransactions;

    } catch (error) {
      console.error('Error fetching user transactions:', error);
      throw new Error(`Failed to fetch transactions: ${error}`);
    }
  }

  /**
   * Get estimated transaction count for a user (for pagination)
   */
  public static async getTransactionCount(principalId: string): Promise<number> {
    try {
      // Fetch a small batch to estimate total count
      const sampleTransactions = await this.fetchUserTransactions(principalId, 10);
      if (sampleTransactions.length < 10) {
        return sampleTransactions.length;
      }
      
      // If we got 10 transactions, there might be more
      // This is a rough estimate - in a real implementation, you'd want a proper count endpoint
      return Math.max(50, sampleTransactions.length * 2);
    } catch (error) {
      console.error('Error getting transaction count:', error);
      return 0;
    }
  }

  /**
   * Clear cache for a specific user or all users
   */
  public static clearCache(principalId?: string) {
    if (principalId) {
      // Clear cache for specific user
      const keysToDelete = Array.from(this.cache.keys()).filter(key => key.startsWith(principalId));
      keysToDelete.forEach(key => this.cache.delete(key));
    } else {
      // Clear all cache
      this.cache.clear();
    }
  }

  /**
   * Get cache statistics for debugging
   */
  public static getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.MAX_CACHE_SIZE,
      entries: Array.from(this.cache.keys())
    };
  }

  /**
   * Format amount for display (convert from e8s to FUNNAI)
   */
  public static formatAmount(amount: bigint): string {
    const funnaiAmount = Number(amount) / 100_000_000; // Convert from e8s (8 decimals)
    return funnaiAmount.toLocaleString(undefined, { 
      minimumFractionDigits: 0,
      maximumFractionDigits: 8 
    });
  }

  /**
   * Get transaction type icon and color
   */
  public static getTransactionStyle(type: string): { icon: string; color: string; bgColor: string } {
    switch (type) {
      case "mint":
        return {
          icon: "↓",
          color: "text-green-600 dark:text-green-400",
          bgColor: "bg-green-100 dark:bg-green-900/30"
        };
      case "transfer":
        return {
          icon: "↔",
          color: "text-blue-600 dark:text-blue-400",
          bgColor: "bg-blue-100 dark:bg-blue-900/30"
        };
      case "burn":
        return {
          icon: "🔥",
          color: "text-red-600 dark:text-red-400",
          bgColor: "bg-red-100 dark:bg-red-900/30"
        };
      case "approve":
        return {
          icon: "✓",
          color: "text-purple-600 dark:text-purple-400",
          bgColor: "bg-purple-100 dark:bg-purple-900/30"
        };
      default:
        return {
          icon: "?",
          color: "text-gray-600 dark:text-gray-400",
          bgColor: "bg-gray-100 dark:bg-gray-900/30"
        };
    }
  }
}
