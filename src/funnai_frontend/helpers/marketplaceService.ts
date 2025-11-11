/**
 * Marketplace Service
 * Handles all marketplace operations including listing, buying, and canceling mAIners
 */

import { get } from 'svelte/store';
import { store, canisterIds } from '../stores/store';
import type { Principal } from '@dfinity/principal';
import { Principal as PrincipalClass } from '@dfinity/principal';

export interface MarketplaceListing {
  address: string;
  mainerType: { Own?: null; ShareAgent?: null };
  listedTimestamp: bigint;
  listedBy: Principal;
  priceE8S: bigint;
  reservedBy: [] | [Principal];
}

export class MarketplaceService {
  /**
   * List a mAIner for sale on the marketplace
   * Uses ICRC37 approve_tokens with price as token_id and mAIner address as memo
   */
  static async listMainer(mainerAddress: string, priceICP: number): Promise<{ success: boolean; transactionId?: bigint; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      if (!$store.isAuthed || !$store.principal) {
        throw new Error('User not authenticated. Please connect your wallet.');
      }
      
      // Check if user owns this mAIner
      const userMainers = $store.userMainerAgentCanistersInfo || [];
      const ownsMainer = userMainers.some(m => m.address === mainerAddress);
      
      if (!ownsMainer) {
        console.error('❌ User does not own mAIner:', {
          attemptedAddress: mainerAddress,
          ownedAddresses: userMainers.map(m => m.address)
        });
        throw new Error(`You don't own this mAIner (${mainerAddress}). Please refresh the page and try again.`);
      }
      
      // Convert ICP to e8s (smallest unit)
      const priceE8s = BigInt(Math.floor(priceICP * 100_000_000));
      
      // Minimum price check (0.01 ICP = 1,000,000 e8s)
      if (priceE8s < 1_000_000n) {
        throw new Error('Price must be at least 0.01 ICP');
      }
      
      // Encode mAIner address as blob
      const mainerAddressBlob = new TextEncoder().encode(mainerAddress);
      
      // Get GameState canister principal
      const gameStatePrincipal = PrincipalClass.fromText(canisterIds.gameStateCanisterId);
      
      // Prepare approve args
      const approveArgs = [{
        token_id: priceE8s,
        approval_info: {
          spender: {
            owner: gameStatePrincipal,
            subaccount: []
          },
          from_subaccount: [],
          expires_at: [],
          memo: [mainerAddressBlob],
          created_at_time: [] // Optional field, let backend set timestamp
        }
      }];
      
      console.log('🔍 DEBUG: Listing mAIner', {
        user: $store.principal.toText(),
        address: mainerAddress,
        priceE8s: priceE8s.toString(),
        priceICP,
        isAuthed: $store.isAuthed,
        hasActor: !!$store.gameStateCanisterActor,
        ownedMainers: $store.userMainerAgentCanistersInfo?.map(m => m.address) || []
      });
      
      const result = await $store.gameStateCanisterActor.icrc37_approve_tokens(approveArgs);
      
      console.log('List result:', result);
      
      if (!result || result.length === 0) {
        throw new Error('No response from canister');
      }
      
      // Result is vec opt ApproveTokenResult, so result[0] is an optional (array)
      const firstOptional = result[0];
      
      if (!firstOptional || firstOptional.length === 0) {
        throw new Error('No result returned from approve tokens');
      }
      
      // Unwrap the optional to get the actual result
      const firstResult = firstOptional[0];
      
      if ('Ok' in firstResult) {
        return {
          success: true,
          transactionId: firstResult.Ok
        };
      } else if ('Err' in firstResult) {
        throw new Error(`Listing failed: ${JSON.stringify(firstResult.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error listing mAIner:', error);
      return {
        success: false,
        error: error.message || 'Failed to list mAIner'
      };
    }
  }
  
  /**
   * Cancel a reservation (for buyers who reserved but didn't complete purchase)
   */
  static async cancelReservation(mainerAddress: string): Promise<{ success: boolean; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      console.log('Canceling reservation for mAIner:', mainerAddress);
      
      const result = await $store.gameStateCanisterActor.cancelMarketplaceReservation({
        address: mainerAddress
      });
      
      console.log('Cancel reservation result:', result);
      
      if ('Ok' in result) {
        return { success: true };
      } else if ('Err' in result) {
        throw new Error(`Cancel reservation failed: ${JSON.stringify(result.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error canceling reservation:', error);
      return {
        success: false,
        error: error.message || 'Failed to cancel reservation'
      };
    }
  }

  /**
   * Cancel a marketplace listing
   * Uses ICRC37 revoke_token_approvals with mAIner address as memo
   */
  static async cancelListing(mainerAddress: string): Promise<{ success: boolean; transactionId?: bigint; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      // Encode mAIner address as blob
      const mainerAddressBlob = new TextEncoder().encode(mainerAddress);
      
      const revokeArgs = [{
        spender: [],
        from_subaccount: [],
        token_id: 0n, // Not used for cancellation
        memo: [mainerAddressBlob],
        created_at_time: []
      }];
      
      console.log('Canceling listing for mAIner:', mainerAddress);
      
      const result = await $store.gameStateCanisterActor.icrc37_revoke_token_approvals(revokeArgs);
      
      console.log('Cancel result:', result);
      
      if (!result || result.length === 0) {
        throw new Error('No response from canister');
      }
      
      // Result is vec opt RevokeTokenApprovalResult, so result[0] is an optional (array)
      const firstOptional = result[0];
      
      if (!firstOptional || firstOptional.length === 0) {
        throw new Error('No result returned from revoke token approvals');
      }
      
      // Unwrap the optional to get the actual result
      const firstResult = firstOptional[0];
      
      if ('Ok' in firstResult) {
        return {
          success: true,
          transactionId: firstResult.Ok
        };
      } else if ('Err' in firstResult) {
        throw new Error(`Cancel failed: ${JSON.stringify(firstResult.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error canceling listing:', error);
      return {
        success: false,
        error: error.message || 'Failed to cancel listing'
      };
    }
  }
  
  /**
   * Reserve a mAIner for purchase
   * Step 1 of the buy process
   */
  static async reserveMainer(mainerAddress: string): Promise<{ success: boolean; listing?: MarketplaceListing; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      console.log('Reserving mAIner:', mainerAddress);
      
      const result = await $store.gameStateCanisterActor.reserveMarketplaceListedMainer({
        address: mainerAddress
      });
      
      console.log('Reserve result:', result);
      
      if ('Ok' in result) {
        return {
          success: true,
          listing: result.Ok
        };
      } else if ('Err' in result) {
        throw new Error(`Reservation failed: ${JSON.stringify(result.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error reserving mAIner:', error);
      return {
        success: false,
        error: error.message || 'Failed to reserve mAIner'
      };
    }
  }
  
  /**
   * Complete the mAIner purchase
   * Step 3 of the buy process (after payment)
   * Uses ICRC37 transfer_from with payment transaction ID as token_id
   */
  static async completePurchase(
    mainerAddress: string,
    sellerPrincipal: Principal,
    paymentTxId: bigint
  ): Promise<{ success: boolean; transactionId?: bigint; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      if (!$store.principal) {
        throw new Error('User not authenticated');
      }
      
      // Encode mAIner address as blob
      const mainerAddressBlob = new TextEncoder().encode(mainerAddress);
      
      const transferArgs = [{
        spender_subaccount: [],
        from: {
          owner: sellerPrincipal,
          subaccount: []
        },
        to: {
          owner: $store.principal,
          subaccount: []
        },
        token_id: paymentTxId, // Payment transaction block ID
        memo: [mainerAddressBlob],
        created_at_time: []
      }];
      
      console.log('Completing purchase with args:', {
        mainerAddress,
        paymentTxId: paymentTxId.toString(),
        from: sellerPrincipal.toString(),
        to: $store.principal.toString()
      });
      
      const result = await $store.gameStateCanisterActor.icrc37_transfer_from(transferArgs);
      
      console.log('Complete purchase result:', result);
      
      if (!result || result.length === 0) {
        throw new Error('No response from canister');
      }
      
      // Result is vec opt TransferFromResult, so result[0] is an optional (array)
      const firstOptional = result[0];
      
      if (!firstOptional || firstOptional.length === 0) {
        throw new Error('No result returned from transfer_from');
      }
      
      // Unwrap the optional to get the actual result
      const firstResult = firstOptional[0];
      
      if ('Ok' in firstResult) {
        return {
          success: true,
          transactionId: firstResult.Ok
        };
      } else if ('Err' in firstResult) {
        throw new Error(`Purchase completion failed: ${JSON.stringify(firstResult.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error completing purchase:', error);
      return {
        success: false,
        error: error.message || 'Failed to complete purchase'
      };
    }
  }
  
  /**
   * Get all marketplace listings
   */
  static async getAllListings(): Promise<{ success: boolean; listings?: any[]; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      const result = await $store.gameStateCanisterActor.getMarketplaceMainerListings();
      
      if ('Ok' in result) {
        return {
          success: true,
          listings: result.Ok
        };
      } else if ('Err' in result) {
        throw new Error(`Failed to get listings: ${JSON.stringify(result.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error getting listings:', error);
      return {
        success: false,
        error: error.message || 'Failed to get listings'
      };
    }
  }
  
  /**
   * Get user's own marketplace listings
   */
  static async getUserListings(): Promise<{ success: boolean; listings?: any[]; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      const result = await $store.gameStateCanisterActor.getUserMarketplaceMainerListings();
      
      if ('Ok' in result) {
        return {
          success: true,
          listings: result.Ok
        };
      } else if ('Err' in result) {
        throw new Error(`Failed to get user listings: ${JSON.stringify(result.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('Error getting user listings:', error);
      return {
        success: false,
        error: error.message || 'Failed to get user listings'
      };
    }
  }
  
  /**
   * Get marketplace statistics
   */
  static async getMarketplaceStats(): Promise<{
    success: boolean;
    stats?: { totalListings: number; totalVolume: string; activeTraders: number };
    error?: string;
  }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      // Get total supply (number of listings)
      const totalListings = await $store.gameStateCanisterActor.icrc7_total_supply();
      
      // Get all listings to calculate volume
      const listingsResult = await MarketplaceService.getAllListings();
      
      if (!listingsResult.success || !listingsResult.listings) {
        throw new Error('Failed to get listings for stats');
      }
      
      // Calculate total volume (sum of all listing prices)
      const totalVolumeE8s = listingsResult.listings.reduce((sum, listing) => {
        return sum + Number(listing.priceE8S);
      }, 0);
      
      const totalVolumeICP = (totalVolumeE8s / 100_000_000).toFixed(1);
      
      // Count unique sellers as active traders
      const uniqueSellers = new Set(
        listingsResult.listings.map(l => l.listedBy.toString())
      );
      
      return {
        success: true,
        stats: {
          totalListings: Number(totalListings),
          totalVolume: totalVolumeICP,
          activeTraders: uniqueSellers.size
        }
      };
      
    } catch (error) {
      console.error('Error getting marketplace stats:', error);
      return {
        success: false,
        error: error.message || 'Failed to get marketplace stats'
      };
    }
  }
}

