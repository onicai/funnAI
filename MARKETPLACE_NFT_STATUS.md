# mAIner Marketplace - NFT Implementation Status

## Overview
The funnAI mAIner marketplace uses **ICRC7** (NFT standard) and **ICRC37** (approve/transfer standard) for buying and selling mAIners as NFTs on the Internet Computer.

## Architecture

### NFT Standards Used
- **ICRC7**: Core NFT functionality (metadata, ownership, supply tracking)
- **ICRC37**: Approve and transfer functionality (listing, canceling, buying)
- **ICRC3**: Transaction history (imported but not yet implemented)
- **ICRC10**: Supported standards declaration

### How It Works

Each mAIner listed on the marketplace is represented as an NFT where:
- **Token ID** (nat): Used for different purposes in different calls:
  - In `approve_tokens`: The price in e8s (ICP smallest unit)
  - In `transfer_from`: The ICP payment transaction block ID
- **Memo** (blob): Always contains the mAIner canister address
- **NFT Metadata**: Includes address, mainerType, listedTimestamp, listedBy, priceE8S

## Backend Implementation Status

### ✅ COMPLETED - ICRC7 Query Methods

```motoko
// Collection metadata
icrc7_symbol() -> "MAINERS"
icrc7_name() -> "funnAI mAIners"
icrc7_description() -> "mAIner AI agents listed on the funnAI marketplace."
icrc7_logo() -> "https://funnai.onicai.com/funnai.webp"

// Supply tracking
icrc7_total_supply() -> Nat
icrc7_supply_cap() -> ?Nat

// Token queries
icrc7_balance_of(accounts) -> [Nat]
icrc7_tokens(prev, take) -> [Nat]
icrc7_token_metadata(token_ids) -> [?[(Text, Value)]]
icrc7_collection_metadata() -> [(Text, Value)]

// Standards declaration
icrc10_supported_standards() -> SupportedStandards
```

### ✅ COMPLETED - ICRC37 Update Methods

#### 1. List mAIner for Sale
```motoko
icrc37_approve_tokens(args: [ApproveTokenArg]) -> [?ApproveTokenResult]
```
**Parameters:**
- `token_id`: Price in e8s (minimum 1,000,000 = 0.01 ICP)
- `approval_info.memo`: UTF-8 encoded mAIner canister address
- `approval_info.from_subaccount`: null

**Flow:**
1. Verifies caller owns the mAIner
2. Checks mAIner is not already reserved/listed
3. Creates `MainerMarketplaceListing` entry
4. Stores in `marketplaceListedMainerAgentsStorage`
5. Returns transaction ID

#### 2. Cancel Listing
```motoko
icrc37_revoke_token_approvals(args: [RevokeTokenApprovalArg]) -> [?RevokeTokenApprovalResult]
```
**Parameters:**
- `memo`: UTF-8 encoded mAIner canister address

**Flow:**
1. Verifies caller owns the mAIner
2. Confirms mAIner is currently listed
3. Removes from `marketplaceListedMainerAgentsStorage`
4. Returns transaction ID

#### 3. Buy mAIner (Transfer)
```motoko
icrc37_transfer_from(args: [TransferFromArg]) -> [?TransferFromResult]
```
**Parameters:**
- `token_id`: ICP payment transaction block ID
- `memo`: UTF-8 encoded mAIner canister address
- `from`: Seller's account
- `to`: Buyer's account

**Flow:**
1. Verifies caller has reserved the mAIner (via `reserveMarketplaceListedMainer`)
2. Verifies payment transaction (⚠️ **PARTIALLY IMPLEMENTED**)
3. Transfers mAIner ownership (⚠️ **TODO**)
4. Removes from marketplace storage
5. Returns transaction ID

### ✅ COMPLETED - Native Query Methods

```motoko
// Get all marketplace listings
getMarketplaceMainerListings() -> Result<[MainerMarketplaceListing], ApiError>

// Get user's own listings
getUserMarketplaceMainerListings() -> Result<[MainerMarketplaceListing], ApiError>

// Reserve a mAIner before buying
reserveMarketplaceListedMainer(input) -> Result<MainerMarketplaceListing, ApiError>
```

### 📦 Data Structures

```motoko
type MainerMarketplaceListing = {
    address: Text;                      // mAIner canister address
    mainerType: MainerAgentCanisterType; // #Own or #ShareAgent
    listedTimestamp: Nat64;             // When listed
    listedBy: Principal;                // Seller
    priceE8S: Nat;                      // Price in e8s
    reservedBy: ?Principal;             // Buyer (if reserved)
};
```

### 🗄️ Storage

```motoko
// Active listings
stable var marketplaceListedMainerAgentsStorage: HashMap<Text, MainerMarketplaceListing>
stable var userToMarketplaceListedMainersStorage: HashMap<Principal, List<MainerMarketplaceListing>>

// Reserved mAIners (during purchase)
stable var marketplaceReservedMainerAgentsStorage: HashMap<Text, MainerMarketplaceListing>
stable var userToMarketplaceReservedMainerStorage: HashMap<Principal, MainerMarketplaceListing>

// Transaction counter
stable var mainerMarketplaceTransactionIdCounter: Nat
```

## ⚠️ INCOMPLETE BACKEND IMPLEMENTATIONS

### 1. Payment Verification in `icrc37_transfer_from`
**Location:** `Main.mo` line ~8601

**Current Status:** Commented out with TODO

**Needed:**
```motoko
// Verify payment transaction
let verificationResponse = await verifyIncomingPayment(transactionEntry);
// Check amount paid matches listing price
// Ensure payment goes to correct seller
```

### 2. Ownership Transfer in `icrc37_transfer_from`
**Location:** `Main.mo` line ~8629

**Current Status:** Commented out with TODO

**Needed:**
```motoko
// Transfer mAIner ownership from seller to buyer
let transferResult = await transferMainerOwnershipToNewOwner({
    address = mainerAddress;
    previousOwner = seller;
    newOwner = buyer;
});
```

### 3. Reservation Timeout Timer
**Location:** `Main.mo` line ~8800

**Current Status:** TODO comment

**Needed:**
- Set timer when mAIner is reserved
- If purchase not completed in X minutes, cancel reservation
- Return mAIner to listings

### 4. Marketplace Statistics
**Not implemented yet**

**Needed:**
```motoko
type MarketplaceStats = {
    totalListings: Nat;
    totalVolume: Nat64;  // Total e8s traded
    activeTraders: Nat;
};

public query func getMarketplaceStats() -> Result<MarketplaceStats, ApiError>
```

## Frontend Implementation Status

### ✅ COMPLETED - UI Components

1. **Marketplace.svelte** - Main page with tabs and stats
2. **MyMainersForSale.svelte** - Selection UI for listing mAIners
3. **MarketplaceListings.svelte** - Browse and buy interface
4. **marketplace.ts** - TypeScript type definitions
5. **mainerIdentity.ts** - Visual identity system

### ❌ NOT IMPLEMENTED - Backend Integration

**Current Status:** All frontend components use mock data with TODO comments

**Location:** `src/funnai_frontend/pages/Marketplace.svelte` lines 44-102

**Needed Implementations:**

#### 1. List mAIner to Marketplace
```typescript
async function handleListToMarketplace(mainerIds: string[], prices: Record<string, number>) {
    for (const mainerId of mainerIds) {
        const priceE8s = BigInt(Math.floor(prices[mainerId] * 100_000_000));
        const mainerAddressBlob = new TextEncoder().encode(mainerId);
        
        const result = await gameStateActor.icrc37_approve_tokens([{
            token_id: priceE8s,
            approval_info: {
                spender: { owner: gameStatePrincipal, subaccount: [] },
                from_subaccount: [],
                expires_at: [],
                memo: [mainerAddressBlob],
                created_at_time: BigInt(Date.now() * 1_000_000)
            }
        }]);
        
        // Handle result
    }
}
```

#### 2. Cancel Listing
```typescript
async function handleCancelListing(listingId: string, mainerId: string) {
    const mainerAddressBlob = new TextEncoder().encode(mainerId);
    
    const result = await gameStateActor.icrc37_revoke_token_approvals([{
        spender: [],
        from_subaccount: [],
        token_id: 0n, // Not used for cancellation
        memo: [mainerAddressBlob],
        created_at_time: []
    }]);
    
    // Handle result
}
```

#### 3. Buy mAIner
```typescript
async function handleBuyMainer(listing: MarketplaceListing) {
    // Step 1: Reserve the mAIner
    const reserveResult = await gameStateActor.reserveMarketplaceListedMainer({
        address: listing.mainerId
    });
    
    if ('Err' in reserveResult) throw new Error('Failed to reserve');
    
    // Step 2: Pay the seller with ICP
    const priceE8s = BigInt(listing.priceE8S);
    const transferResult = await icpLedger.icrc1_transfer({
        to: { owner: Principal.fromText(listing.seller), subaccount: [] },
        amount: priceE8s,
        fee: [],
        memo: [],
        from_subaccount: [],
        created_at_time: []
    });
    
    if ('Err' in transferResult) throw new Error('Payment failed');
    
    // Step 3: Complete the NFT transfer
    const blockId = transferResult.Ok;
    const mainerAddressBlob = new TextEncoder().encode(listing.mainerId);
    
    const nftResult = await gameStateActor.icrc37_transfer_from([{
        spender_subaccount: [],
        from: { owner: Principal.fromText(listing.seller), subaccount: [] },
        to: { owner: $store.principal, subaccount: [] },
        token_id: blockId,
        memo: [mainerAddressBlob],
        created_at_time: []
    }]);
    
    // Handle result
}
```

#### 4. Load Marketplace Data
```typescript
async function loadMarketplaceStats() {
    // Get all listings
    const listingsResult = await gameStateActor.getMarketplaceMainerListings();
    
    if ('Ok' in listingsResult) {
        const listings = listingsResult.Ok;
        
        // Calculate stats
        stats = {
            totalListings: listings.length,
            totalVolume: listings.reduce((sum, l) => 
                sum + Number(l.priceE8S), 0) / 100_000_000,
            activeTraders: new Set(listings.map(l => l.listedBy)).size
        };
    }
}

async function loadListings() {
    const result = await gameStateActor.getMarketplaceMainerListings();
    
    if ('Ok' in result) {
        const userPrincipal = $store.principal?.toString();
        
        listings = result.Ok.map(listing => ({
            id: listing.address,
            mainerId: listing.address,
            mainerName: `mAIner ${listing.address.slice(0, 5)}`,
            price: Number(listing.priceE8S) / 100_000_000,
            seller: Principal.toText(listing.listedBy),
            listedAt: Number(listing.listedTimestamp) / 1_000_000,
            mainerType: listing.mainerType.Own ? 'Own' : 'Shared',
            isOwnListing: Principal.toText(listing.listedBy) === userPrincipal,
            // Need to fetch these from mAIner canister:
            cycleBalance: 0,
            createdAt: null,
            status: 'active'
        }));
    }
}
```

### 📋 Required Actor Declarations

```typescript
// In store.ts or appropriate location
import { Actor, HttpAgent } from '@dfinity/agent';
import { idlFactory as gameStateIdl } from '../declarations/game_state_canister';
import { idlFactory as icpLedgerIdl } from '../declarations/icp_ledger_canister';

// Game State Actor (for marketplace methods)
const gameStateActor = Actor.createActor(gameStateIdl, {
    agent,
    canisterId: GAME_STATE_CANISTER_ID
});

// ICP Ledger Actor (for payments)
const icpLedger = Actor.createActor(icpLedgerIdl, {
    agent,
    canisterId: 'ryjl3-tyaaa-aaaaa-aaaba-cai' // ICP Ledger
});
```

## Implementation Priority

### Phase 1: Core Marketplace (READY TO IMPLEMENT)
1. ✅ Update Candid interface with marketplace types
2. ✅ Wire frontend to call `getMarketplaceMainerListings()`
3. ✅ Implement listing flow using `icrc37_approve_tokens`
4. ✅ Implement cancel flow using `icrc37_revoke_token_approvals`
5. ⚠️ Complete payment verification in backend
6. ⚠️ Complete ownership transfer in backend
7. ✅ Implement buy flow (reserve → pay → transfer)

### Phase 2: Enhanced Features
1. ⚠️ Implement marketplace statistics endpoint
2. ⚠️ Add reservation timeout mechanism
3. ⚠️ Fetch additional mAIner metadata (cycles, creation date)
4. ⚠️ Add transaction history (ICRC3)
5. ⚠️ Add filtering and sorting
6. ⚠️ Add price history tracking

### Phase 3: Polish
1. Error handling and retry logic
2. Loading states and optimistic updates
3. Transaction notifications
4. Activity feed
5. Price suggestions based on market data

## Key Differences from Original Plan

**Original Plan (MARKETPLACE_BACKEND_IMPLEMENTATION.md):**
- Custom marketplace implementation
- Direct ICP payment handling
- Custom ownership transfer logic

**Current NFT Implementation:**
- Uses ICRC7/ICRC37 standards
- Marketplace compatible with other IC NFT tools
- Leverages existing NFT infrastructure
- Better composability with IC ecosystem

## Testing Checklist

### Backend
- [ ] List mAIner with valid price
- [ ] List mAIner with invalid price (< 0.01 ICP)
- [ ] List mAIner that's already listed
- [ ] Cancel own listing
- [ ] Cancel someone else's listing (should fail)
- [ ] Reserve available mAIner
- [ ] Reserve already reserved mAIner (should fail)
- [ ] Complete purchase with valid payment
- [ ] Complete purchase with invalid payment (should fail)
- [ ] Verify ownership transfer after purchase

### Frontend
- [ ] Display all marketplace listings
- [ ] Display user's own listings separately
- [ ] Select and price mAIners for listing
- [ ] List multiple mAIners at once
- [ ] Cancel listing
- [ ] View listing details
- [ ] Purchase mAIner
- [ ] Update stats after transactions
- [ ] Handle errors gracefully
- [ ] Show appropriate loading states

## Next Steps

Ready to start implementing! The backend NFT infrastructure is ~80% complete. Main tasks:

1. **Complete Backend TODOs:**
   - Payment verification logic
   - Ownership transfer logic
   - Statistics endpoint
   - Reservation timeouts

2. **Wire Frontend:**
   - Replace mock data with actual actor calls
   - Implement ICRC37 method calls
   - Add ICP payment flow
   - Handle errors and edge cases

3. **Update Candid:**
   - Ensure all marketplace methods are in `.did` file
   - Regenerate TypeScript declarations

Would you like me to start with any specific part of this implementation?

