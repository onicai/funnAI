<script lang="ts">
  // Token information data
  const tokenLedger = {
    title: "Token Ledger",
    canisterId: "vpyot-zqaaa-aaaaa-qavaq-cai",
    decimals: 8,
    tokenTypes: ["ICRC-1", "ICRC-2", "ICRC-3"],
    status: "active"
  };

  const tokenIndex = {
    title: "Token Index",
    canisterId: "coming soon...",
    status: "pending"
  };

  // Copy to clipboard functionality
  async function copyToClipboard(text: string, canisterType: string) {
    if (text === "coming soon...") {
      showToast("Index canister not available yet", "warning");
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      showToast(`${canisterType} canister ID copied to clipboard!`, "success");
    } catch (err) {
      console.error('Failed to copy: ', err);
      // Fallback for older browsers
      try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast(`${canisterType} canister ID copied to clipboard!`, "success");
      } catch (fallbackErr) {
        showToast("Failed to copy to clipboard", "error");
      }
    }
  }

  // Simple toast notification system
  let toastMessage = "";
  let toastType = "";
  let toastVisible = false;

  function showToast(message: string, type: "success" | "warning" | "error") {
    toastMessage = message;
    toastType = type;
    toastVisible = true;
    
    setTimeout(() => {
      toastVisible = false;
    }, 3000);
  }

  // Get toast styling based on type
  function getToastClasses(type: string): string {
    switch (type) {
      case "success":
        return "bg-green-500 text-white";
      case "warning":
        return "bg-yellow-500 text-white";
      case "error":
        return "bg-red-500 text-white";
      default:
        return "bg-gray-500 text-white";
    }
  }
</script>

<!-- Responsive Grid: 2 columns on desktop, 1 column on mobile -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Token Ledger Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <div class="p-1.5 bg-blue-100 dark:bg-blue-900/30 rounded">
              <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {tokenLedger.title}
              </h4>
            </div>
          </div>
          <div class="flex items-center space-x-1">
            <div class="w-1.5 h-1.5 rounded-full bg-green-500"></div>
            <span class="text-xs text-green-600 dark:text-green-400 font-medium">Active</span>
          </div>
        </div>

        <!-- Canister ID with Copy Button -->
        <div class="mb-3">
          <div class="flex items-center space-x-2">
            <div class="flex-1 bg-white dark:bg-gray-800 rounded px-2 py-1.5 border border-gray-300 dark:border-gray-600">
              <code class="text-xs font-mono text-gray-900 dark:text-gray-100 break-all">
                {tokenLedger.canisterId}
              </code>
            </div>
            <button
              on:click={() => copyToClipboard(tokenLedger.canisterId, "Ledger")}
              class="p-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 dark:focus:ring-offset-gray-800"
              title="Copy canister ID"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Token Details -->
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-3">
            <span class="text-gray-600 dark:text-gray-400">
              Decimals: <span class="font-medium text-gray-900 dark:text-gray-100">{tokenLedger.decimals}</span>
            </span>
          </div>
          <div class="flex gap-1">
            {#each tokenLedger.tokenTypes as tokenType}
              <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-200">
                {tokenType}
              </span>
            {/each}
          </div>
        </div>
      </div>

      <!-- Token Index Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center space-x-2">
            <div class="p-1.5 bg-yellow-100 dark:bg-yellow-900/30 rounded">
              <svg class="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white">
                {tokenIndex.title}
              </h4>
            </div>
          </div>
          <div class="flex items-center space-x-1">
            <div class="w-1.5 h-1.5 rounded-full bg-yellow-500"></div>
            <span class="text-xs text-yellow-600 dark:text-yellow-400 font-medium">Pending</span>
          </div>
        </div>

        <!-- Canister ID with Copy Button -->
        <div class="mb-3">
          <div class="flex items-center space-x-2">
            <div class="flex-1 bg-white dark:bg-gray-800 rounded px-2 py-1.5 border border-gray-300 dark:border-gray-600">
              <code class="text-xs font-mono text-gray-500 dark:text-gray-400 italic">
                {tokenIndex.canisterId}
              </code>
            </div>
            <button
              on:click={() => copyToClipboard(tokenIndex.canisterId, "Index")}
              class="p-1.5 bg-gray-400 hover:bg-gray-500 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-1 dark:focus:ring-offset-gray-800"
              title="Copy canister ID"
              disabled={tokenIndex.canisterId === "coming soon..."}
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Coming Soon Message -->
        <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded p-2">
          <div class="flex items-center space-x-2">
            <svg class="h-3 w-3 text-yellow-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <div>
              <span class="text-xs font-medium text-yellow-800 dark:text-yellow-200">Under Development</span>
              <p class="text-xs text-yellow-700 dark:text-yellow-300 mt-0.5">Index canister coming soon</p>
            </div>
          </div>
        </div>
      </div>
</div>

<!-- Toast Notification -->
{#if toastVisible}
  <div class="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right-full duration-300">
    <div class="rounded-lg px-4 py-2 shadow-lg {getToastClasses(toastType)}">
      <div class="flex items-center space-x-2">
        {#if toastType === "success"}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        {:else if toastType === "warning"}
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
        {:else}
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        {/if}
        <span class="text-sm font-medium">{toastMessage}</span>
      </div>
    </div>
  </div>
{/if}
