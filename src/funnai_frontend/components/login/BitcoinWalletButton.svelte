<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { store, HOST } from "../../stores/store";
  import LoadingSpinner from "../LoadingSpinner.svelte";
  import { Actor, HttpAgent } from "@dfinity/agent";
  import { 
    idlFactory as siwbProviderIdlFactory,
  } from "../../../declarations/ic_siwb_provider/ic_siwb_provider.did.js";

  export let loading;
  export let toggleModal;

  // Wallet types supported
  type WalletType = 'unisat' | 'xverse' | 'wizz' | 'okx' | 'leather';
  
  interface WalletInfo {
    name: string;
    key: WalletType;
    icon: string;
    available: boolean;
    color: string;
  }

  let wallets: WalletInfo[] = [];
  let showWalletSelector = false;
  let selectedWallet: WalletType | null = null;
  let connectingWallet: WalletType | null = null;
  let errorMessage: string | null = null;

  // SIWB Provider canister ID - set from environment or specify after deployment
  // IMPORTANT: Deploy the ic_siwb_provider canister first and update this ID
  const SIWB_PROVIDER_CANISTER_ID = process.env.CANISTER_ID_IC_SIWB_PROVIDER || "";
  
  // Check if SIWB is properly configured
  const isSiwbConfigured = !!SIWB_PROVIDER_CANISTER_ID;

  // Check for available wallets on mount
  onMount(() => {
    checkAvailableWallets();
  });

  function checkAvailableWallets() {
    const w = window as any;
    
    wallets = [
      {
        name: 'UniSat',
        key: 'unisat',
        icon: `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" rx="16" fill="#000"/><path d="M54.5 20H25.5C22.4624 20 20 22.4624 20 25.5V54.5C20 57.5376 22.4624 60 25.5 60H54.5C57.5376 60 60 57.5376 60 54.5V25.5C60 22.4624 57.5376 20 54.5 20Z" fill="#F7931A"/><path d="M47.7 35.3C47.2 32.3 44.5 31.3 41 30.9V27H39V30.8H37V27H35V30.8L30 30.8V33.4H32C33.1 33.4 33.5 34 33.5 34.7V45.3C33.5 45.8 33.2 46.6 32 46.6H30V49.2L35 49.2V53H37V49.2H39V53H41V49.1C44.8 48.8 47.5 47.6 48 44C48.3 41.3 47.1 39.8 45.1 39.1C46.6 38.3 47.4 36.9 47.7 35.3ZM43.6 43.6C43.6 46.1 39.4 45.8 38 45.8V41.3C39.4 41.3 43.6 41 43.6 43.6ZM42.6 36.1C42.6 38.4 39.1 38.1 38 38.1V34C39.1 34 42.6 33.7 42.6 36.1Z" fill="white"/></svg>`,
        available: !!w.unisat,
        color: '#F7931A'
      },
      {
        name: 'Xverse',
        key: 'xverse',
        icon: `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" rx="16" fill="#EE7A30"/><path d="M25 28L40 52L55 28H49L40 43L31 28H25Z" fill="white"/><path d="M40 52L55 28H49L40 43V52Z" fill="white" fill-opacity="0.6"/></svg>`,
        available: !!(w.XverseProviders || w.BitcoinProvider),
        color: '#EE7A30'
      },
      {
        name: 'Wizz',
        key: 'wizz',
        icon: `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" rx="16" fill="#6366F1"/><path d="M20 30L30 50L40 35L50 50L60 30H54L50 40L40 25L30 40L26 30H20Z" fill="white"/></svg>`,
        available: !!w.wizz,
        color: '#6366F1'
      },
      {
        name: 'OKX Wallet',
        key: 'okx',
        icon: `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" rx="16" fill="#000"/><rect x="24" y="24" width="14" height="14" rx="2" fill="white"/><rect x="42" y="24" width="14" height="14" rx="2" fill="white"/><rect x="24" y="42" width="14" height="14" rx="2" fill="white"/><rect x="42" y="42" width="14" height="14" rx="2" fill="white"/></svg>`,
        available: !!(w.okxwallet?.bitcoin || w.okxwallet?.bitcoinTestnet),
        color: '#000000'
      },
      {
        name: 'Leather',
        key: 'leather',
        icon: `<svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="80" height="80" rx="16" fill="#12100F"/><path d="M25 55V25H35V45H55V55H25Z" fill="#F5F1EB"/></svg>`,
        available: !!(w.LeatherProvider || w.HiroWalletProvider),
        color: '#12100F'
      }
    ];
  }

  $: availableWallets = wallets.filter(w => w.available);
  $: hasAnyWallet = availableWallets.length > 0;

  function handleMainButtonClick() {
    if (!hasAnyWallet) {
      // Show install options
      window.open('https://unisat.io/', '_blank');
      return;
    }
    
    if (availableWallets.length === 1) {
      // Only one wallet available, connect directly
      connectWithWallet(availableWallets[0].key);
    } else {
      // Show wallet selector
      showWalletSelector = true;
    }
  }

  async function connectWithWallet(walletKey: WalletType) {
    connectingWallet = walletKey;
    errorMessage = null;
    loading = "bitcoin";
    
    try {
      // Check if SIWB provider is configured
      if (!isSiwbConfigured) {
        throw new Error("Bitcoin login is not yet configured. The SIWB provider canister needs to be deployed first. Please contact the administrator.");
      }
      
      const w = window as any;
      let provider: any;
      let btcAddress: string;

      // Get wallet provider and request accounts
      switch (walletKey) {
        case 'unisat':
          provider = w.unisat;
          const unisatAccounts = await provider.requestAccounts();
          btcAddress = unisatAccounts[0];
          break;
          
        case 'xverse':
          // Xverse uses a different API
          if (w.XverseProviders?.BitcoinProvider) {
            provider = w.XverseProviders.BitcoinProvider;
          } else if (w.BitcoinProvider) {
            provider = w.BitcoinProvider;
          }
          const xverseResponse = await provider.request('getAccounts', null);
          btcAddress = xverseResponse.result[0].address;
          break;
          
        case 'wizz':
          provider = w.wizz;
          const wizzAccounts = await provider.requestAccounts();
          btcAddress = wizzAccounts[0];
          break;
          
        case 'okx':
          provider = w.okxwallet?.bitcoin || w.okxwallet?.bitcoinTestnet;
          const okxAccounts = await provider.requestAccounts();
          btcAddress = okxAccounts[0];
          break;
          
        case 'leather':
          provider = w.LeatherProvider || w.HiroWalletProvider;
          const leatherResponse = await provider.request('getAddresses');
          btcAddress = leatherResponse.result.addresses[0].address;
          break;
          
        default:
          throw new Error('Unknown wallet type');
      }

      if (!btcAddress) {
        throw new Error('No Bitcoin address returned from wallet');
      }

      console.log(`Connected to ${walletKey} with address: ${btcAddress}`);

      // Now perform SIWB authentication
      await performSiwbAuth(provider, walletKey, btcAddress);
      
      showWalletSelector = false;
      toggleModal();
      
    } catch (error) {
      console.error(`Error connecting with ${walletKey}:`, error);
      errorMessage = error instanceof Error ? error.message : 'Connection failed';
      
      if (error instanceof Error && error.message.includes('User rejected')) {
        errorMessage = 'Connection cancelled by user';
      }
    } finally {
      connectingWallet = null;
      loading = "";
    }
  }

  async function performSiwbAuth(provider: any, walletKey: WalletType, btcAddress: string) {
    // Import identity modules early - we need session key before login
    const { DelegationChain, DelegationIdentity, Ed25519KeyIdentity } = await import("@dfinity/identity");
    
    // Create session key FIRST - needed for siwb_login
    const sessionKey = Ed25519KeyIdentity.generate();
    const sessionPublicKey = sessionKey.getPublicKey().toDer();
    
    // Create anonymous agent for SIWB provider
    const agent = new HttpAgent({ host: HOST });
    
    if (process.env.DFX_NETWORK !== "ic" && process.env.NODE_ENV === "development") {
      await agent.fetchRootKey().catch(console.error);
    }

    const siwbProvider = Actor.createActor(siwbProviderIdlFactory, {
      agent,
      canisterId: SIWB_PROVIDER_CANISTER_ID,
    });

    // Step 1: Prepare login - returns a pre-formatted message string
    console.log("Preparing SIWB login...");
    const prepareResult: any = await siwbProvider.siwb_prepare_login(btcAddress);
    
    if ('Err' in prepareResult) {
      throw new Error(`Failed to prepare login: ${prepareResult.Err}`);
    }

    // The message is already formatted by the canister
    const messageToSign: string = prepareResult.Ok;
    console.log("Message to sign:", messageToSign);

    // Step 2: Sign message with wallet
    let signature: string;
    
    switch (walletKey) {
      case 'unisat':
        signature = await provider.signMessage(messageToSign, 'bip322-simple');
        break;
      case 'xverse':
        const xverseSignResult = await provider.request('signMessage', {
          message: messageToSign,
          address: btcAddress,
        });
        signature = xverseSignResult.result.signature;
        break;
      case 'wizz':
        signature = await provider.signMessage(messageToSign, 'bip322-simple');
        break;
      case 'okx':
        signature = await provider.signMessage(messageToSign, 'bip322-simple');
        break;
      case 'leather':
        const leatherSignResult = await provider.request('signMessage', {
          message: messageToSign,
          paymentType: 'p2wpkh',
        });
        signature = leatherSignResult.result.signature;
        break;
      default:
        throw new Error('Unknown wallet for signing');
    }

    console.log("Got signature:", signature.substring(0, 50) + "...");

    // Get public key from wallet for siwb_login
    let publicKeyHex: string;
    try {
      switch (walletKey) {
        case 'unisat':
          publicKeyHex = await provider.getPublicKey();
          break;
        case 'xverse':
          // Xverse returns pubkey in getAccounts response
          const xverseAccounts = await provider.request('getAccounts', null);
          publicKeyHex = xverseAccounts.result[0].publicKey || '';
          break;
        case 'wizz':
          publicKeyHex = await provider.getPublicKey();
          break;
        case 'okx':
          publicKeyHex = await provider.getPublicKey();
          break;
        case 'leather':
          // Leather includes pubkey in getAddresses
          const leatherAddresses = await provider.request('getAddresses');
          publicKeyHex = leatherAddresses.result.addresses[0].publicKey || '';
          break;
        default:
          publicKeyHex = '';
      }
    } catch (e) {
      console.warn("Could not get public key from wallet, using empty string");
      publicKeyHex = '';
    }

    console.log("Public key hex:", publicKeyHex.substring(0, 20) + "...");

    // Step 3: Login with signature
    // siwb_login takes: (SiwbSignature, Address, PublickeyHex, SessionKey, SignMessageType)
    console.log("Logging in with SIWB...");
    const loginResult: any = await siwbProvider.siwb_login(
      signature,                           // SiwbSignature (the signature as string)
      btcAddress,                          // Address
      publicKeyHex,                        // PublickeyHex (wallet's public key)
      new Uint8Array(sessionPublicKey),    // SessionKey (our session public key)
      { 'Bip322Simple': null }             // SignMessageType
    );
    
    if ('Err' in loginResult) {
      throw new Error(`Login failed: ${loginResult.Err}`);
    }

    const loginDetails = loginResult.Ok;
    console.log("Login successful, expiration:", loginDetails.expiration.toString());

    // Step 4: Get delegation
    console.log("Getting delegation...");
    const delegationResult: any = await siwbProvider.siwb_get_delegation(
      btcAddress,
      new Uint8Array(sessionPublicKey),
      loginDetails.expiration
    );

    if ('Err' in delegationResult) {
      throw new Error(`Failed to get delegation: ${delegationResult.Err}`);
    }

    // Step 5: Create identity from delegation
    const signedDelegation = delegationResult.Ok;
    
    // Convert to proper types for DelegationChain
    // Ensure expiration is BigInt
    const expiration = typeof signedDelegation.delegation.expiration === 'bigint' 
      ? signedDelegation.delegation.expiration 
      : BigInt(signedDelegation.delegation.expiration.toString());
    
    // Convert pubkey and signature to Uint8Array if they aren't already
    const delegationPubkey = signedDelegation.delegation.pubkey instanceof Uint8Array
      ? signedDelegation.delegation.pubkey
      : new Uint8Array(signedDelegation.delegation.pubkey);
    
    const delegationSignature = signedDelegation.signature instanceof Uint8Array
      ? signedDelegation.signature
      : new Uint8Array(signedDelegation.signature);
    
    const canisterPubkey = loginDetails.user_canister_pubkey instanceof Uint8Array
      ? loginDetails.user_canister_pubkey
      : new Uint8Array(loginDetails.user_canister_pubkey);

    console.log("Creating delegation chain with:", {
      expiration: expiration.toString(),
      delegationPubkeyLength: delegationPubkey.length,
      signatureLength: delegationSignature.length,
      canisterPubkeyLength: canisterPubkey.length,
      sessionPubkeyLength: sessionPublicKey.byteLength
    });

    // Import Delegation class for proper construction
    const { Delegation } = await import("@dfinity/identity");
    
    // Create the Delegation object with proper types
    // The delegation pubkey should be our session public key (the key being delegated TO)
    const delegation = new Delegation(
      sessionPublicKey,  // Use our session public key as the delegated key
      expiration,
      signedDelegation.delegation.targets?.length > 0 
        ? signedDelegation.delegation.targets 
        : undefined
    );

    // Create the signed delegation with proper ArrayBuffer types
    const signedDelegationForChain = {
      delegation,
      signature: delegationSignature.buffer.slice(
        delegationSignature.byteOffset,
        delegationSignature.byteOffset + delegationSignature.byteLength
      )
    };

    // Create delegation chain using fromDelegations
    // Use type assertion to satisfy the strict Signature type
    const delegationChain = DelegationChain.fromDelegations(
      [signedDelegationForChain] as any,
      canisterPubkey.buffer.slice(
        canisterPubkey.byteOffset,
        canisterPubkey.byteOffset + canisterPubkey.byteLength
      )
    );

    // Create delegated identity
    const identity = DelegationIdentity.fromDelegation(sessionKey, delegationChain);
    
    console.log("Created identity with principal:", identity.getPrincipal().toString());

    // Store session info - including the delegated identity for later use
    (globalThis as any).__siwb_btc_address__ = btcAddress;
    (globalThis as any).__siwb_wallet_type__ = walletKey;
    (globalThis as any).__siwb_session_key__ = sessionKey;
    (globalThis as any).__siwb_delegated_identity__ = identity;

    // Initialize store with the identity
    await store.siwbConnect(identity, btcAddress);
  }

  function hexToBytes(hex: string): Uint8Array {
    // Handle base64 encoded signatures
    if (!hex.match(/^[0-9a-fA-F]+$/)) {
      // Try base64 decode
      try {
        const binary = atob(hex);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
      } catch {
        // Fall through to hex parsing
      }
    }
    
    // Hex decode
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
      bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    return bytes;
  }

  function closeSelector() {
    showWalletSelector = false;
    errorMessage = null;
  }
</script>

<!-- Main Button -->
<button
  type="button"
  class="flex items-center p-3 text-base font-bold text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow w-full text-left disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none"
  class:opacity-60={loading === "bitcoin"}
  disabled={!isSiwbConfigured}
  on:click={handleMainButtonClick}
>
  {#if loading === "bitcoin" && !showWalletSelector}
    <LoadingSpinner size="h-6 w-6" />
  {:else}
    <!-- Bitcoin Logo -->
    <svg class="h-5 w-5" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <g fill="none" fill-rule="evenodd">
        <circle cx="16" cy="16" r="16" fill="#F7931A"/>
        <path fill="#FFF" fill-rule="nonzero" d="M23.189 14.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69 2.765c-.454-.113-.92-.22-1.385-.326l.695-2.783-1.728-.431-.709 2.84c-.376-.086-.744-.17-1.101-.259l.002-.01-2.384-.595-.46 1.847s1.283.294 1.256.312c.7.175.827.638.806 1.006l-.807 3.238c.048.012.11.03.18.057l-.183-.046-1.132 4.538c-.086.213-.303.533-.793.412.018.025-1.256-.313-1.256-.313l-.858 1.978 2.25.561c.418.105.828.215 1.231.318l-.715 2.872 1.727.43.709-2.84c.472.127.93.245 1.378.357l-.706 2.828 1.728.43.715-2.866c2.948.558 5.164.333 6.097-2.333.752-2.146-.037-3.385-1.588-4.192 1.13-.26 1.98-1.003 2.207-2.538zm-3.95 5.538c-.533 2.147-4.148.986-5.32.695l.95-3.805c1.172.293 4.929.872 4.37 3.11zm.535-5.569c-.487 1.953-3.495.96-4.47.717l.86-3.45c.975.243 4.118.696 3.61 2.733z"/>
      </g>
    </svg>
    <span class="flex-1 ms-3 whitespace-nowrap">
      {#if !isSiwbConfigured}
        Bitcoin Wallet
        <span class="text-xs text-amber-600 block">(Coming Soon)</span>
      {:else if hasAnyWallet}
        Bitcoin Wallet
        {#if availableWallets.length > 0}
          <span class="text-xs text-gray-500 block">
            {availableWallets.map(w => w.name).join(', ')}
          </span>
        {/if}
      {:else}
        Bitcoin Wallet
        <span class="text-xs text-gray-500 block">(Install UniSat/Xverse)</span>
      {/if}
    </span>
  {/if}
</button>

<!-- Wallet Selector Modal -->
{#if showWalletSelector}
  <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
  <div 
    class="fixed inset-0 bg-black/50 z-[10000] flex items-center justify-center p-4"
    role="dialog"
    aria-modal="true"
    aria-labelledby="wallet-selector-title"
    on:click={closeSelector}
    on:keydown={(e) => e.key === 'Escape' && closeSelector()}
  >
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div 
      class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-sm w-full shadow-2xl"
      on:click|stopPropagation
    >
      <div class="flex items-center justify-between mb-4">
        <h3 id="wallet-selector-title" class="text-lg font-semibold text-gray-900 dark:text-white">Select Bitcoin Wallet</h3>
        <button 
          on:click={closeSelector}
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      {#if errorMessage}
        <div class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-sm text-red-700 dark:text-red-400">{errorMessage}</p>
        </div>
      {/if}

      <div class="space-y-2">
        {#each wallets as wallet}
          <button
            type="button"
            disabled={!wallet.available || connectingWallet !== null}
            class="w-full flex items-center gap-3 p-3 rounded-lg border transition-all
              {wallet.available 
                ? 'border-gray-200 dark:border-gray-600 hover:border-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 cursor-pointer' 
                : 'border-gray-100 dark:border-gray-700 opacity-50 cursor-not-allowed'}"
            on:click={() => wallet.available && connectWithWallet(wallet.key)}
          >
            <div class="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0">
              {@html wallet.icon}
            </div>
            <div class="flex-1 text-left">
              <div class="font-medium text-gray-900 dark:text-white">{wallet.name}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {wallet.available ? 'Available' : 'Not installed'}
              </div>
            </div>
            {#if connectingWallet === wallet.key}
              <LoadingSpinner size="h-5 w-5" />
            {:else if !wallet.available}
              <a 
                href={wallet.key === 'unisat' ? 'https://unisat.io/' : 
                      wallet.key === 'xverse' ? 'https://www.xverse.app/' :
                      wallet.key === 'leather' ? 'https://leather.io/' :
                      wallet.key === 'okx' ? 'https://www.okx.com/web3' :
                      'https://wizzwallet.io/'}
                target="_blank"
                rel="noopener noreferrer"
                class="text-xs text-blue-600 hover:underline"
                on:click|stopPropagation
              >
                Install
              </a>
            {/if}
          </button>
        {/each}
      </div>

      <p class="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
        Sign in with your Bitcoin wallet to get an ICP identity
      </p>
    </div>
  </div>
{/if}

