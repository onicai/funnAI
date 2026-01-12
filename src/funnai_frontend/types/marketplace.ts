/**
 * Marketplace Type Definitions
 * 
 * This file contains TypeScript interfaces and types for the mAIner marketplace feature.
 */

export interface MarketplaceListing {
  id: string;
  mainerId: string;
  mainerName: string;
  price: number;
  seller: string;
  listedAt: number;
  cycleBalance: number;
  mainerType: string;
  status: MarketplaceListingStatus;
  isOwnListing: boolean;
  createdAt: number | null;
}

export type MarketplaceListingStatus = 'active' | 'sold' | 'cancelled';

export interface MarketplaceStats {
  totalListings: number;
  totalVolume: string;
  activeTraders: number;
}

export interface ListMainerInput {
  mainerId: string;
  price: number;
}

export interface BuyMainerInput {
  listingId: string;
  mainerId: string;
  price: number;
}

export interface CancelListingInput {
  listingId: string;
}

// Response types for backend calls
export type ListMainerResponse = 
  | { Ok: { listingId: string } }
  | { Err: string };

export type BuyMainerResponse = 
  | { Ok: { transactionId: string } }
  | { Err: string };

export type CancelListingResponse = 
  | { Ok: null }
  | { Err: string };

export type GetMarketplaceListingsResponse = 
  | { Ok: MarketplaceListing[] }
  | { Err: string };

export type GetMarketplaceStatsResponse = 
  | { Ok: MarketplaceStats }
  | { Err: string };

