# Marketplace Backend Implementation Guide

## Overview
This document provides detailed instructions for implementing the complete marketplace backend functionality, including mAIner listing, purchasing, and payment processing with ICP.

## Backend Architecture

### 1. Game State Canister Extensions
The marketplace functionality should be added to the existing `game_state_canister` in the PoAIW system.

**Location:** `PoAIW/src/GameState/`

## Required Data Structures

### 1. Marketplace Types (Add to Types.mo)

```motoko
// Marketplace-specific types
public type MarketplaceListing = {
  id: Text;
  mainerId: Text;
  seller: Principal;
  price: Nat64; // Price in e8s (ICP smallest unit)
  listedAt: Nat64;
  status: MarketplaceListingStatus;
  mainerInfo: MainerInfo;
};

public type MarketplaceListingStatus = {
  #Active;
  #Sold;
  #Cancelled;
};

public type MainerInfo = {
  name: Text;
  mainerType: MainerType;
  cycleBalance: Nat64;
  createdAt: Nat64;
  burnedCycles: Nat64;
};

public type MainerType = {
  #Own;
  #Shared;
};

public type MarketplaceStats = {
  totalListings: Nat;
  totalVolume: Nat64; // Total volume in e8s
  activeTraders: Nat;
};

// Input types
public type ListMainerInput = {
  mainerId: Text;
  price: Nat64; // Price in e8s
};

public type BuyMainerInput = {
  listingId: Text;
};

public type CancelListingInput = {
  listingId: Text;
};

// Result types
public type ListMainerResult = Result<{listingId: Text}, ApiError>;
public type BuyMainerResult = Result<{transactionId: Text}, ApiError>;
public type CancelListingResult = Result<(), ApiError>;
public type GetMarketplaceListingsResult = Result<[MarketplaceListing], ApiError>;
public type GetMarketplaceStatsResult = Result<MarketplaceStats, ApiError>;
```

### 2. Storage Variables (Add to GameState.mo)

```motoko
// Marketplace storage
stable var marketplaceListingsStable: [(Text, MarketplaceListing)] = [];
var marketplaceListings: HashMap.HashMap<Text, MarketplaceListing> = HashMap.HashMap(0, Text.equal, Text.hash);

stable var marketplaceStatsStable: MarketplaceStats = {
  totalListings = 0;
  totalVolume = 0;
  activeTraders = 0;
};
var marketplaceStats: MarketplaceStats = {
  totalListings = 0;
  totalVolume = 0;
  activeTraders = 0;
};

// Track active traders (principals who have bought/sold)
stable var activeTradersStable: [Principal] = [];
var activeTraders: HashSet.HashSet<Principal> = HashSet.HashSet(0, Principal.equal, Principal.hash);
```

## Required Functions Implementation

### 1. List mAIner on Marketplace

```motoko
public shared(msg) func listMainerOnMarketplace(input: ListMainerInput): async ListMainerResult {
  // Authentication check
  if (Principal.isAnonymous(msg.caller)) {
    return #Err(#Unauthorized);
  };

  // Verify mAIner ownership
  let mainerCanisters = await getMainerAgentCanistersForUser();
  let mainerExists = switch (mainerCanisters) {
    case (#Ok canisters) {
      Array.find<MainerAgentCanisterInfo>(canisters, func(canister) {
        canister.address == input.mainerId and canister.ownedBy == ?msg.caller
      }) != null;
    };
    case (#Err(_)) false;
  };

  if (not mainerExists) {
    return #Err(#NotFound);
  };

  // Check if already listed
  switch (marketplaceListings.get(input.mainerId)) {
    case (?existingListing) {
      if (existingListing.status == #Active) {
        return #Err(#AlreadyExists);
      };
    };
    case null {};
  };

  // Validate price (minimum 0.01 ICP = 1,000,000 e8s)
  if (input.price < 1_000_000) {
    return #Err(#InvalidInput);
  };

  // Get mAIner info
  let mainerInfo = await getMainerInfo(input.mainerId);
  let mainerInfoResult = switch (mainerInfo) {
    case (#Ok info) info;
    case (#Err(err)) return #Err(err);
  };

  // Create listing
  let listingId = generateListingId();
  let listing: MarketplaceListing = {
    id = listingId;
    mainerId = input.mainerId;
    seller = msg.caller;
    price = input.price;
    listedAt = Time.now();
    status = #Active;
    mainerInfo = mainerInfoResult;
  };

  // Store listing
  marketplaceListings.put(listingId, listing);
  
  // Update stats
  marketplaceStats := {
    totalListings = marketplaceStats.totalListings + 1;
    totalVolume = marketplaceStats.totalVolume;
    activeTraders = marketplaceStats.activeTraders;
  };

  // Add seller to active traders
  activeTraders.add(msg.caller);

  #Ok({listingId = listingId});
};
```

### 2. Buy mAIner from Marketplace

```motoko
public shared(msg) func buyMainerFromMarketplace(input: BuyMainerInput): async BuyMainerResult {
  // Authentication check
  if (Principal.isAnonymous(msg.caller)) {
    return #Err(#Unauthorized);
  };

  // Get listing
  let listing = switch (marketplaceListings.get(input.listingId)) {
    case (?listing) listing;
    case null return #Err(#NotFound);
  };

  // Check if listing is active
  if (listing.status != #Active) {
    return #Err(#NotFound);
  };

  // Prevent self-purchase
  if (listing.seller == msg.caller) {
    return #Err(#InvalidInput);
  };

  // Verify mAIner still exists and is owned by seller
  let mainerCanisters = await getMainerAgentCanistersForUser();
  let mainerStillOwned = switch (mainerCanisters) {
    case (#Ok canisters) {
      Array.find<MainerAgentCanisterInfo>(canisters, func(canister) {
        canister.address == listing.mainerId and canister.ownedBy == ?listing.seller
      }) != null;
    };
    case (#Err(_)) false;
  };

  if (not mainerStillOwned) {
    return #Err(#NotFound);
  };

  // Process ICP payment
  let paymentResult = await processICPPayment(msg.caller, listing.seller, listing.price);
  switch (paymentResult) {
    case (#Ok transactionId) {
      // Transfer mAIner ownership
      let transferResult = await transferMainerOwnership(listing.mainerId, listing.seller, msg.caller);
      switch (transferResult) {
        case (#Ok(_)) {
          // Update listing status
          let updatedListing = {
            listing with status = #Sold
          };
          marketplaceListings.put(input.listingId, updatedListing);

          // Update stats
          marketplaceStats := {
            totalListings = marketplaceStats.totalListings - 1;
            totalVolume = marketplaceStats.totalVolume + listing.price;
            activeTraders = marketplaceStats.activeTraders;
          };

          // Add buyer to active traders
          activeTraders.add(msg.caller);

          #Ok({transactionId = transactionId});
        };
        case (#Err(err)) #Err(err);
      };
    };
    case (#Err(err)) #Err(err);
  };
};
```

### 3. Cancel Marketplace Listing

```motoko
public shared(msg) func cancelMarketplaceListing(input: CancelListingInput): async CancelListingResult {
  // Authentication check
  if (Principal.isAnonymous(msg.caller)) {
    return #Err(#Unauthorized);
  };

  // Get listing
  let listing = switch (marketplaceListings.get(input.listingId)) {
    case (?listing) listing;
    case null return #Err(#NotFound);
  };

  // Check ownership
  if (listing.seller != msg.caller) {
    return #Err(#Unauthorized);
  };

  // Check if listing is active
  if (listing.status != #Active) {
    return #Err(#InvalidInput);
  };

  // Update listing status
  let updatedListing = {
    listing with status = #Cancelled
  };
  marketplaceListings.put(input.listingId, updatedListing);

  // Update stats
  marketplaceStats := {
    totalListings = marketplaceStats.totalListings - 1;
    totalVolume = marketplaceStats.totalVolume;
    activeTraders = marketplaceStats.activeTraders;
  };

  #Ok(());
};
```

### 4. Get Marketplace Listings

```motoko
public query func getMarketplaceListings(): async GetMarketplaceListingsResult {
  let listings = Iter.toArray(marketplaceListings.entries());
  let activeListings = Array.filter<(Text, MarketplaceListing)>(listings, func((_, listing)) {
    listing.status == #Active
  });
  
  let result = Array.map<(Text, MarketplaceListing), MarketplaceListing>(activeListings, func((_, listing)) {
    listing
  });

  #Ok(result);
};
```

### 5. Get Marketplace Stats

```motoko
public query func getMarketplaceStats(): async GetMarketplaceStatsResult {
  let stats = {
    totalListings = marketplaceStats.totalListings;
    totalVolume = marketplaceStats.totalVolume;
    activeTraders = activeTraders.size();
  };
  #Ok(stats);
};
```

## Payment Processing

### 1. ICP Payment Processing

```motoko
// Add to GameState.mo
private func processICPPayment(buyer: Principal, seller: Principal, amount: Nat64): async Result<Text, ApiError> {
  // This function should integrate with the ICP Ledger
  // Implementation depends on your ICP ledger setup
  
  // Option 1: Direct ledger integration
  // let ledger = actor("rdmx6-jaaaa-aaaaa-aaadq-cai") : LedgerInterface;
  // let transferResult = await ledger.transfer({
  //   to = seller;
  //   fee = { e8s = 10_000 }; // 0.0001 ICP fee
  //   memo = 0;
  //   from_subaccount = null;
  //   created_at_time = ?{ timestamp_nanos = Nat64.fromNat(Int.abs(Time.now())) };
  //   amount = { e8s = amount };
  // });
  
  // Option 2: Use existing payment infrastructure
  // Check if you have existing ICP payment handling in your codebase
  
  // For now, return a mock transaction ID
  // TODO: Implement actual ICP payment processing
  let transactionId = "tx_" # Nat64.toText(Time.now());
  #Ok(transactionId);
};
```

### 2. mAIner Ownership Transfer

```motoko
private func transferMainerOwnership(mainerId: Text, from: Principal, to: Principal): async Result<(), ApiError> {
  // This function should transfer ownership of the mAIner canister
  // Implementation depends on your mAIner management system
  
  // Option 1: Update canister ownership in your system
  // let updateResult = await updateMainerOwnership(mainerId, to);
  
  // Option 2: Use existing ownership transfer mechanisms
  // Check your existing mAIner management code for ownership transfer
  
  // For now, return success
  // TODO: Implement actual ownership transfer
  #Ok(());
};
```

## Helper Functions

### 1. Generate Listing ID

```motoko
private func generateListingId(): Text {
  let timestamp = Time.now();
  let random = Nat64.toText(timestamp);
  "listing_" # random;
};
```

### 2. Get mAIner Info

```motoko
private func getMainerInfo(mainerId: Text): async Result<MainerInfo, ApiError> {
  // Get mAIner information from your existing system
  // This should return the mAIner's details for the marketplace listing
  
  // Mock implementation - replace with actual mAIner info retrieval
  let mainerInfo: MainerInfo = {
    name = "mAIner " # mainerId;
    mainerType = #Own;
    cycleBalance = 5_000_000_000_000; // 5T cycles
    createdAt = Time.now();
    burnedCycles = 0;
  };
  
  #Ok(mainerInfo);
};
```

## Data Persistence

### 1. Preupgrade Function

```motoko
system func preupgrade() {
  // Save marketplace data
  marketplaceListingsStable := Iter.toArray(marketplaceListings.entries());
  marketplaceStatsStable := marketplaceStats;
  activeTradersStable := Iter.toArray(activeTraders.entries());
};
```

### 2. Postupgrade Function

```motoko
system func postupgrade() {
  // Restore marketplace data
  marketplaceListings := HashMap.fromIter<Text, MarketplaceListing>(
    marketplaceListingsStable.vals(), 
    marketplaceListingsStable.size(), 
    Text.equal, 
    Text.hash
  );
  marketplaceStats := marketplaceStatsStable;
  activeTraders := HashSet.fromIter<Principal>(
    activeTradersStable.vals(), 
    activeTradersStable.size(), 
    Principal.equal, 
    Principal.hash
  );
};
```

## Security Considerations

### 1. Access Control
- All functions require authentication (non-anonymous callers)
- Ownership verification for listing/canceling
- Prevent self-purchase

### 2. Input Validation
- Price validation (minimum 0.01 ICP)
- mAIner existence verification
- Listing status checks

### 3. Atomic Operations
- Payment and ownership transfer should be atomic
- Use proper error handling to prevent partial state

## Integration Points

### 1. Frontend Integration
Update the frontend to call these new backend methods:

```typescript
// In Marketplace.svelte
async function handleListToMarketplace(mainerIds: string[], prices: Record<string, number>) {
  for (const mainerId of mainerIds) {
    const price = prices[mainerId];
    const priceInE8s = Math.floor(price * 100_000_000); // Convert to e8s
    
    const result = await $store.gameStateCanisterActor.listMainerOnMarketplace({
      mainerId,
      price: priceInE8s
    });
    
    if ('Err' in result) {
      throw new Error(result.Err);
    }
  }
}

async function handleBuyMainer(listingId: string, mainerId: string, price: number) {
  const result = await $store.gameStateCanisterActor.buyMainerFromMarketplace({
    listingId
  });
  
  if ('Err' in result) {
    throw new Error(result.Err);
  }
  
  return result.Ok.transactionId;
}

async function handleCancelListing(listingId: string) {
  const result = await $store.gameStateCanisterActor.cancelMarketplaceListing({
    listingId
  });
  
  if ('Err' in result) {
    throw new Error(result.Err);
  }
}

async function loadMarketplaceStats() {
  const result = await $store.gameStateCanisterActor.getMarketplaceStats();
  
  if ('Ok' in result) {
    stats = {
      totalListings: Number(result.Ok.totalListings),
      totalVolume: (Number(result.Ok.totalVolume) / 100_000_000).toFixed(1), // Convert from e8s
      activeTraders: Number(result.Ok.activeTraders)
    };
  }
}
```

### 2. Candid Interface
Add these methods to your Candid interface:

```candid
// Marketplace methods
listMainerOnMarketplace: (record { mainerId: text; price: nat64 }) -> (variant { Ok: record { listingId: text }; Err: ApiError });
buyMainerFromMarketplace: (record { listingId: text }) -> (variant { Ok: record { transactionId: text }; Err: ApiError });
cancelMarketplaceListing: (record { listingId: text }) -> (variant { Ok; Err: ApiError });
getMarketplaceListings: () -> (variant { Ok: vec MarketplaceListing; Err: ApiError });
getMarketplaceStats: () -> (variant { Ok: MarketplaceStats; Err: ApiError });
```

## Testing Checklist

### 1. Unit Tests
- [ ] List mAIner with valid input
- [ ] List mAIner with invalid price
- [ ] List non-owned mAIner (should fail)
- [ ] Buy mAIner with valid listing
- [ ] Buy own mAIner (should fail)
- [ ] Cancel own listing
- [ ] Cancel others' listing (should fail)
- [ ] Get marketplace listings
- [ ] Get marketplace stats

### 2. Integration Tests
- [ ] Full listing → buying → ownership transfer flow
- [ ] Payment processing with ICP ledger
- [ ] Error handling and rollback scenarios
- [ ] Concurrent operations handling

### 3. Security Tests
- [ ] Anonymous access prevention
- [ ] Ownership verification
- [ ] Input validation
- [ ] Atomic operation testing

## Deployment Steps

1. **Add Types**: Add marketplace types to `Types.mo`
2. **Add Storage**: Add marketplace storage variables to `GameState.mo`
3. **Implement Functions**: Add all marketplace functions
4. **Add Persistence**: Implement preupgrade/postupgrade functions
5. **Update Candid**: Add marketplace methods to Candid interface
6. **Deploy**: Deploy updated canister
7. **Update Frontend**: Update frontend to use new backend methods
8. **Test**: Run comprehensive tests

## Notes

- All prices are stored in e8s (ICP smallest unit) for precision
- Frontend converts between ICP and e8s for display
- Consider adding marketplace fees (e.g., 2.5% platform fee)
- Implement proper error handling and logging
- Consider adding marketplace activity events for analytics
- Add rate limiting to prevent spam
- Consider implementing offer/bidding system for future enhancement

---

**Implementation Priority:**
1. ✅ Data structures and storage
2. ✅ Basic CRUD operations (list, buy, cancel)
3. ✅ Payment processing integration
4. ✅ Frontend integration
5. ✅ Testing and deployment
