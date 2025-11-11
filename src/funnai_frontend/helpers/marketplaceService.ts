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
      // Use string multiplication to avoid floating point precision issues
      const priceE8s = BigInt(Math.round(priceICP * 100_000_000));
      
      console.log('💰 Price Conversion:', {
        inputICP: priceICP,
        calculatedE8s: priceICP * 100_000_000,
        roundedE8s: Math.round(priceICP * 100_000_000),
        finalE8s: priceE8s.toString(),
        backToICP: Number(priceE8s) / 100_000_000
      });
      
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
   * Check if user has an active reservation
   */
  static async getUserReservation(): Promise<{ success: boolean; reservation?: any; error?: string }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      if (!$store.isAuthed) {
        return { success: true, reservation: null };
      }
      
      const reservation = await $store.gameStateCanisterActor.getUserMarketplaceReservation();
      
      // The backend returns ?MainerMarketplaceListing
      // Candid optional types come as empty array [] when null, or [value] when present
      let actualReservation = null;
      
      if (Array.isArray(reservation)) {
        if (reservation.length > 0) {
          // Extract the first element from the array
          actualReservation = reservation[0];
        }
        // else: empty array means no reservation
      } else if (reservation) {
        // Direct object (shouldn't happen but handle it)
        actualReservation = reservation;
      }
      
      return {
        success: true,
        reservation: actualReservation
      };
      
    } catch (error) {
      console.error('Error checking user reservation:', error);
      return {
        success: false,
        error: error.message || 'Failed to check reservation'
      };
    }
  }

  /**
   * Clear any stale reservation the user might have (call on page load)
   */
  static async clearStaleReservation(): Promise<{ success: boolean; hadReservation: boolean; error?: string }> {
    try {
      console.log('🔍 Checking for existing reservation...');
      const reservationResult = await this.getUserReservation();
      
      console.log('📋 Reservation check result:', reservationResult);
      
      if (!reservationResult.success) {
        console.error('❌ Failed to check reservation:', reservationResult.error);
        return { success: false, hadReservation: false, error: reservationResult.error };
      }
      
      // Check if reservation exists (handle both null and empty array from Candid optional)
      const hasReservation = reservationResult.reservation && 
                            !(Array.isArray(reservationResult.reservation) && reservationResult.reservation.length === 0);
      
      if (!hasReservation) {
        console.log('✅ No reservation found');
        return { success: true, hadReservation: false };
      }
      
      // Extract the actual reservation object (might be wrapped in array)
      const reservation = Array.isArray(reservationResult.reservation) && reservationResult.reservation.length > 0
        ? reservationResult.reservation[0]
        : reservationResult.reservation;
      
      console.log('🔧 Found stale reservation, clearing:', {
        address: reservation.address,
        priceE8S: reservation.priceE8S,
        listedBy: reservation.listedBy?.toString?.() || reservation.listedBy
      });
      
      // Cancel the stale reservation
      const cancelResult = await this.cancelReservation(reservation.address);
      
      console.log('🔧 Cancel result:', cancelResult);
      
      if (cancelResult.success) {
        console.log('✅ Successfully cleared stale reservation and returned mAIner to marketplace');
        return { success: true, hadReservation: true };
      } else {
        console.error('❌ Failed to cancel reservation:', cancelResult.error);
        return {
          success: false,
          hadReservation: true,
          error: cancelResult.error
        };
      }
      
    } catch (error) {
      console.error('❌ Error in clearStaleReservation:', error);
      return {
        success: false,
        hadReservation: false,
        error: error.message || 'Failed to clear stale reservation'
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
      
      console.log('🔄 Attempting to reserve mAIner:', mainerAddress);
      
      // First, verify the mAIner is actually listed
      const allListingsResult = await this.getAllListings();
      if (allListingsResult.success && allListingsResult.listings) {
        const isListed = allListingsResult.listings.some(l => l.address === mainerAddress);
        console.log('🔍 Is mAIner in listings?', isListed);
        if (!isListed) {
          console.error('❌ mAIner not found in listings!');
          throw new Error('mAIner is not currently available for purchase');
        }
        
        const listing = allListingsResult.listings.find(l => l.address === mainerAddress);
        console.log('📋 Listing details:', listing);
      }
      
      // Check if mAIner is stuck in reserved storage (diagnostic)
      try {
        const isInReservedStorage = await $store.gameStateCanisterActor.isMainerInReservedStorage(mainerAddress);
        console.log('🔍 Is mAIner in reserved storage?', isInReservedStorage);
        if (isInReservedStorage) {
          console.error('❌ mAIner is stuck in reserved storage! This should not happen.');
          throw new Error('mAIner has a stale reservation. Please try again in 2 minutes or contact support.');
        }
      } catch (err) {
        console.log('⚠️ Could not check reserved storage (might be old backend):', err.message);
      }
      
      const result = await $store.gameStateCanisterActor.reserveMarketplaceListedMainer({
        address: mainerAddress
      });
      
      console.log('🔄 Reserve result:', result);
      
      if ('Ok' in result) {
        console.log('✅ Reservation successful!');
        return {
          success: true,
          listing: result.Ok
        };
      } else if ('Err' in result) {
        console.error('❌ Reservation failed:', result.Err);
        throw new Error(`Reservation failed: ${JSON.stringify(result.Err)}`);
      } else {
        throw new Error('Unknown response format');
      }
      
    } catch (error) {
      console.error('❌ Error reserving mAIner:', error);
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
    stats?: { totalListings: number; totalSales: number; totalVolume: string; activeTraders: number };
    error?: string;
  }> {
    try {
      const $store = get(store);
      
      if (!$store.gameStateCanisterActor) {
        throw new Error('Game State canister not initialized');
      }
      
      // Get actual sales statistics from backend
      const salesStats = await $store.gameStateCanisterActor.getMarketplaceSalesStats();
      
      // Get current number of listings
      const totalListings = await $store.gameStateCanisterActor.icrc7_total_supply();
      
      // Convert total volume from e8s to ICP
      const totalVolumeICP = (Number(salesStats.totalVolumeE8S) / 100_000_000).toFixed(2);
      
      // Calculate total active traders (buyers + sellers, deduplicated)
      const totalTraders = Number(salesStats.uniqueBuyers) + Number(salesStats.uniqueSellers);
      
      return {
        success: true,
        stats: {
          totalListings: Number(totalListings),
          totalSales: Number(salesStats.totalSales),
          totalVolume: totalVolumeICP,
          activeTraders: totalTraders
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

