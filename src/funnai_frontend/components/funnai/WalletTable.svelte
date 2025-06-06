<script lang="ts">
  import { IcrcService } from '../../helpers/IcrcService';
  import { store } from '../../stores/store';
  import { fetchTokens } from '../../helpers/token_helpers';
  
  // Remove the default transactions and only accept them as a prop
  export let transactions: {
    coin: string;
    symbol: string;
    amount: string;
    icon: string;
  }[];

  // Add state for both modals
  let isSendModalOpen = false;
  let isReceiveModalOpen = false;
  let selectedTransaction: typeof transactions[0] | null = null;
  
  // Add form state variables for the send modal
  let sendForm = {
    recipient: '',
    account: '',
    amount: 0
  };
  
  // Add loading and error states
  let isProcessingTransaction = false;
  let transactionError = '';
  let transactionSuccess = false;
  
  // Store token data for blockchain operations
  let tokenDataMap = new Map();
  let isLoadingTokenData = false;
  
  // Load token data for blockchain operations
  async function loadTokenData() {
    if (isLoadingTokenData) return;
    isLoadingTokenData = true;
    
    try {
      const result = await fetchTokens({});
      tokenDataMap.clear();
      result.tokens.forEach(token => {
        tokenDataMap.set(token.symbol, token);
      });
    } catch (error) {
      console.error('Error loading token data:', error);
    } finally {
      isLoadingTokenData = false;
    }
  }
  
  // Generate a random ICP-like principal ID
  const generatePrincipalId = () => {
    const characters = '23456789abcdefghijkmnpqrstuvwxyz'; // base32 alphabet without 1, l, o, 0
    const length = 63; // typical length for principal IDs
    let result = '';
    
    // Generate segments with hyphens
    const segments = [10, 5, 5, 5, 5, 5, 5, 5, 8]; // typical segmentation
    
    segments.forEach((segmentLength, index) => {
      for (let i = 0; i < segmentLength; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
      }
      if (index < segments.length - 1) {
        result += '-';
      }
    });
    
    return result;
  };

  // Generate a random ICP account ID (hex format)
  const generateAccountId = () => {
    const length = 64; // 32 bytes represented in hex
    const hex = '0123456789abcdef';
    return Array.from({length}, () => hex[Math.floor(Math.random() * hex.length)]).join('');
  };
  
  let receivePrincipalId = generatePrincipalId();
  let receiveAccountId = generateAccountId();

  // Update modal functions
  function openSendModal(transaction: typeof transactions[0]) {
    selectedTransaction = transaction;
    isSendModalOpen = true;
    // Reset form state
    sendForm = {
      recipient: '',
      account: '',
      amount: 0
    };
    transactionError = '';
    transactionSuccess = false;
    
    // Load token data if not already loaded
    if (tokenDataMap.size === 0) {
      loadTokenData();
    }
  }

  function openReceiveModal(transaction: typeof transactions[0]) {
    selectedTransaction = transaction;
    isReceiveModalOpen = true;
    // Use the user's actual principal ID if available, otherwise generate random ones
    if ($store.principal) {
      receivePrincipalId = $store.principal.toString();
    } else {
      receivePrincipalId = generatePrincipalId();
    }
    receiveAccountId = generateAccountId();
  }

  function closeModals() {
    isSendModalOpen = false;
    isReceiveModalOpen = false;
    selectedTransaction = null;
    isProcessingTransaction = false;
    transactionError = '';
    transactionSuccess = false;
  }
  
  // Add form validation
  function validateSendForm(): boolean {
    if (!sendForm.recipient.trim()) {
      transactionError = 'Principal ID is required';
      return false;
    }
    
    if (sendForm.amount <= 0) {
      transactionError = 'Amount must be greater than 0';
      return false;
    }
    
    const availableAmount = parseFloat(selectedTransaction?.amount || '0');
    if (sendForm.amount > availableAmount) {
      transactionError = 'Insufficient balance';
      return false;
    }
    
    // Basic principal ID format validation (simplified)
    const principalPattern = /^[a-z0-9]{5}-[a-z0-9]{5}-[a-z0-9]{5}/;
    if (!principalPattern.test(sendForm.recipient)) {
      transactionError = 'Invalid Principal ID format';
      return false;
    }
    
    return true;
  }
  
  // Add real transaction processing function using IcrcService
  async function processSendTransaction() {
    if (!validateSendForm()) {
      return;
    }
    
    isProcessingTransaction = true;
    transactionError = '';
    
    try {
      // Check authentication
      if (!$store.principal) {
        throw new Error('Please connect your wallet first');
      }
      
      // Get token data for blockchain operations
      const tokenData = tokenDataMap.get(selectedTransaction?.symbol);
      if (!tokenData) {
        throw new Error('Token data not found. Please try again.');
      }
      
      console.log('Processing transaction:', {
        from: $store.principal.toString(),
        to: sendForm.recipient,
        amount: sendForm.amount,
        currency: selectedTransaction?.symbol,
        accountId: sendForm.account || undefined,
        tokenData: tokenData
      });
      
      // Convert amount to BigInt with proper decimals
      const amountBigInt = BigInt(Math.floor(sendForm.amount * Math.pow(10, tokenData.decimals)));
      
      // Perform the actual blockchain transfer
      const result = await IcrcService.transfer(
        tokenData,
        sendForm.recipient, // Principal ID as string
        amountBigInt,
        {
          fee: BigInt(tokenData.fee_fixed),
          // Include account ID in memo if provided
          memo: sendForm.account ? Array.from(new TextEncoder().encode(sendForm.account)) : undefined
        }
      );
      
      console.log('Transaction result:', result);
      
      if (result && typeof result === 'object' && 'Ok' in result) {
        const txId = result.Ok?.toString();
        console.log('Transaction successful. TX ID:', txId);
        transactionSuccess = true;
        
        // Update the transaction list locally (in real app, this would come from backend refresh)
        const updatedAmount = (parseFloat(selectedTransaction?.amount || '0') - sendForm.amount).toFixed(8);
        const transactionIndex = transactions.findIndex(t => t.symbol === selectedTransaction?.symbol);
        if (transactionIndex !== -1) {
          transactions[transactionIndex].amount = updatedAmount;
        }
        
        // Auto-close modal after success
        setTimeout(() => {
          closeModals();
        }, 2000);
        
      } else if (result && typeof result === 'object' && 'Err' in result) {
        // Handle blockchain-specific errors
        const error = result.Err;
        if (typeof error === 'object' && error !== null) {
          if ('InsufficientFunds' in error) {
            transactionError = 'Insufficient funds for this transaction';
          } else if ('BadFee' in error) {
            const badFeeError = error.BadFee as any;
            transactionError = `Invalid fee. Expected: ${badFeeError?.expected_fee || 'unknown'}`;
          } else if ('TxTooOld' in error) {
            transactionError = 'Transaction request too old. Please try again.';
          } else if ('TxCreatedInFuture' in error) {
            transactionError = 'Transaction created in future. Please try again.';
          } else if ('Duplicate' in error) {
            transactionError = 'Duplicate transaction detected.';
          } else {
            const errorKey = Object.keys(error)[0];
            transactionError = `Transaction failed: ${errorKey}`;
          }
        } else {
          transactionError = `Transaction failed: ${String(error)}`;
        }
        console.error('Transfer error details:', error);
      } else {
        transactionError = 'Unknown transaction error occurred';
      }
    } catch (error) {
      console.error('Transaction error:', error);
      if (error.message.includes('Refused to connect')) {
        transactionError = 'Connection refused. Please check your wallet connection.';
      } else if (error.message.includes('network')) {
        transactionError = 'Network error. Please check your connection and try again.';
      } else {
        transactionError = error.message || 'Transaction failed. Please try again.';
      }
    } finally {
      isProcessingTransaction = false;
    }
  }
  
  // Add form submit handler
  function handleSendFormSubmit(event: Event) {
    event.preventDefault();
    processSendTransaction();
  }
</script>

<div class="relative overflow-x-auto shadow-md sm:rounded-lg">
  
  <table class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400">
    <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
      <tr>
        <th scope="col" class="px-6 py-3">
          Coin
        </th>
        <th scope="col" class="px-6 py-3">
          Amount
        </th>
        <th scope="col" class="px-6 py-3">
          Action
        </th>
      </tr>
    </thead>
    <tbody>
      {#each transactions as transaction, i}
        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600">
         
          <th scope="row" class="flex items-center px-6 py-4 text-gray-900 whitespace-nowrap dark:text-white">
            <img class="w-8 h-8 rounded-full" src={transaction.icon} alt="{transaction.coin} icon">
            <div class="ps-3">
              <div class="text-base font-semibold">{transaction.coin}</div>
              <div class="font-normal text-gray-500">{transaction.symbol}</div>
            </div>  
          </th>
          <td class="px-6 py-4">
            {transaction.amount}
          </td>
          <td class="px-6 py-4">
            <!-- Modal toggle -->
            <button 
              type="button" 
              on:click={() => openSendModal(transaction)}
              class="text-white bg-gradient-to-r from-purple-500 via-purple-600 to-purple-700 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-purple-300 dark:focus:ring-purple-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2"
            >
              Send
            </button>
            <button 
              type="button"
              on:click={() => openReceiveModal(transaction)}
              class="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden text-sm font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-purple-500 to-pink-500 group-hover:from-purple-500 group-hover:to-pink-500 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800"
            >
              <span class="relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                Receive
              </span>
            </button>
        </td>
        </tr>
      {/each}
    </tbody>
  </table>
  
  <!-- Transaction details modal -->
  <div 
    class="fixed top-0 left-0 right-0 z-50 items-center justify-center w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-[calc(100%-1rem)] max-h-full {isSendModalOpen ? 'flex' : 'hidden'}"
  >
    <div 
      class="fixed inset-0 bg-black bg-opacity-50"
      on:click={closeModals}
    ></div>
    <div class="relative w-full max-w-2xl max-h-full z-10">
      <!-- Modal content -->
      <div class="relative bg-white rounded-lg shadow-sm dark:bg-gray-700">
        <!-- Modal header -->
        <div class="flex items-start justify-between p-4 border-b rounded-t dark:border-gray-600 border-gray-200">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
            Send {selectedTransaction?.coin ?? ''}
          </h3>
          <button 
            type="button" 
            class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" 
            on:click={closeModals}
          >
            <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
            </svg>
            <span class="sr-only">Close modal</span>
          </button>
        </div>
        <!-- Modal body -->
        <div class="p-6 space-y-6">
          <form class="space-y-4" on:submit={handleSendFormSubmit}>
            <!-- Error message display -->
            {#if transactionError}
              <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400" role="alert">
                <span class="font-medium">Error:</span> {transactionError}
              </div>
            {/if}
            
            <!-- Success message display -->
            {#if transactionSuccess}
              <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400" role="alert">
                <span class="font-medium">Success!</span> Transaction completed successfully.
              </div>
            {/if}
            
            <div>
              <label for="recipient" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Principal ID</label>
              <input 
                type="text" 
                id="recipient" 
                bind:value={sendForm.recipient}
                disabled={isProcessingTransaction}
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white font-mono disabled:opacity-50" 
                placeholder="aaaaa-bbbbb-ccccc-..." 
                required
              >
            </div>
            <div>
              <label for="account" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Account ID (Optional)</label>
              <input 
                type="text" 
                id="account" 
                bind:value={sendForm.account}
                disabled={isProcessingTransaction}
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white font-mono disabled:opacity-50" 
                placeholder="Enter account ID..."
              >
            </div>
            <div>
              <label for="amount" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Amount</label>
              <div class="flex">
                <input 
                  type="number" 
                  id="amount" 
                  bind:value={sendForm.amount}
                  disabled={isProcessingTransaction}
                  step="0.00000001"
                  min="0"
                  max={selectedTransaction?.amount}
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-l-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white disabled:opacity-50" 
                  placeholder="0.00" 
                  required
                >
                <span class="inline-flex items-center px-3 text-sm text-gray-900 bg-gray-200 border border-l-0 border-gray-300 rounded-r-lg dark:bg-gray-600 dark:text-gray-400 dark:border-gray-500">
                  {selectedTransaction?.symbol ?? ''}
                </span>
              </div>
              <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Available: {selectedTransaction?.amount ?? '0'} {selectedTransaction?.symbol ?? ''}
              </p>
            </div>
          </form>
        </div>
        <!-- Modal footer -->
        <div class="flex items-center p-6 space-x-3 rtl:space-x-reverse border-t border-gray-200 rounded-b dark:border-gray-600">
          <button 
            type="submit" 
            disabled={isProcessingTransaction || transactionSuccess}
            on:click={handleSendFormSubmit}
            class="text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {#if isProcessingTransaction}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            {:else if transactionSuccess}
              ✓ Sent
            {:else}
              Send {selectedTransaction?.symbol ?? ''}
            {/if}
          </button>
          <button 
            type="button" 
            disabled={isProcessingTransaction}
            class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" 
            on:click={closeModals}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Add the receive modal -->
  <div 
    class="fixed top-0 left-0 right-0 z-60 items-center justify-center w-full p-4 overflow-x-hidden overflow-y-auto md:inset-0 h-[calc(100%-1rem)] max-h-full {isReceiveModalOpen ? 'flex' : 'hidden'}"
  >
    <div 
      class="fixed inset-0 bg-black bg-opacity-50"
      on:click={closeModals}
    ></div>
    <div class="relative w-full max-w-2xl max-h-full z-10">
      <!-- Modal content -->
      <div class="relative bg-white rounded-lg shadow-sm dark:bg-gray-700">
        <!-- Modal header -->
        <div class="flex items-start justify-between p-4 border-b rounded-t dark:border-gray-600 border-gray-200">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
            Receive {selectedTransaction?.coin ?? ''}
          </h3>
          <button 
            type="button" 
            class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white" 
            on:click={closeModals}
          >
            <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
            </svg>
            <span class="sr-only">Close modal</span>
          </button>
        </div>
        <!-- Modal body -->
        <div class="p-6 space-y-6">
          <div class="flex flex-col items-center space-y-6">
            <!-- QR Code -->
            <div class="bg-white p-4 rounded-lg">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${receivePrincipalId}`}
                alt="QR Code"
                class="w-48 h-48"
              />
            </div>
            <!-- Principal ID -->
            <div class="w-full">
              <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Principal ID
              </label>
              <div class="flex">
                <input 
                  type="text" 
                  readonly 
                  value={receivePrincipalId}
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white font-mono"
                >
                <button 
                  type="button"
                  class="ms-2 text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800"
                  on:click={() => navigator.clipboard.writeText(receivePrincipalId)}
                >
                  Copy
                </button>
              </div>
            </div>
            <!-- Account ID -->
            <div class="w-full">
              <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Account ID
              </label>
              <div class="flex">
                <input 
                  type="text" 
                  readonly 
                  value={receiveAccountId}
                  class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-purple-500 focus:border-purple-500 block w-full p-2.5 dark:bg-gray-600 dark:border-gray-500 dark:placeholder-gray-400 dark:text-white font-mono"
                >
                <button 
                  type="button"
                  class="ms-2 text-white bg-purple-700 hover:bg-purple-800 focus:ring-4 focus:outline-none focus:ring-purple-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-purple-600 dark:hover:bg-purple-700 dark:focus:ring-purple-800"
                  on:click={() => navigator.clipboard.writeText(receiveAccountId)}
                >
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- Modal footer -->
        <div class="flex items-center p-6 space-x-3 rtl:space-x-reverse border-t border-gray-200 rounded-b dark:border-gray-600">
          <button 
            type="button" 
            class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600" 
            on:click={closeModals}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</div> 