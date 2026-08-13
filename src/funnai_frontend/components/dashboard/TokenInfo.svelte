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
    canisterId: "mziuv-biaaa-aaaaa-qccrq-cai",
    status: "active"
  };

  // Copy to clipboard functionality
  async function copyToClipboard(text: string, canisterType: string) {
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

<!-- Token canisters -->
<div class="agent-card !bg-agent-surface p-5 sm:p-6">
  <div class="relative z-[1] mb-5">
    <p class="agent-eyebrow">Canisters</p>
    <h3 class="mt-1 text-base font-semibold tracking-tight text-white">Token infrastructure</h3>
    <p class="mt-0.5 text-sm text-gray-500">Ledger and index principals for FUNNAI</p>
  </div>

  <div class="relative z-[1] grid grid-cols-1 lg:grid-cols-2 gap-3">
    <div class="rounded-xl bg-white/[0.03] p-4">
      <div class="flex items-center justify-between gap-2 mb-3">
        <div>
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Ledger</p>
          <h4 class="mt-0.5 text-sm font-semibold tracking-tight text-white">{tokenLedger.title}</h4>
        </div>
        <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
          <span class="h-1 w-1 rounded-full bg-emerald-400"></span>
          Active
        </span>
      </div>
      <div class="flex items-center gap-2">
        <code class="flex-1 min-w-0 text-xs font-mono text-gray-300 break-all rounded-lg bg-white/[0.03] px-2.5 py-2 border border-white/[0.06]">
          {tokenLedger.canisterId}
        </code>
        <button
          type="button"
          on:click={() => copyToClipboard(tokenLedger.canisterId, "Ledger")}
          class="agent-btn-ghost !h-8 !px-2.5 flex-shrink-0"
          title="Copy canister ID"
        >
          Copy
        </button>
      </div>
      <div class="mt-3 flex flex-wrap items-center gap-1.5">
        <span class="text-xs text-gray-500">Decimals {tokenLedger.decimals}</span>
        {#each tokenLedger.tokenTypes as tokenType}
          <span class="inline-flex items-center rounded-full bg-[#653FC5]/15 px-2 py-0.5 text-[10px] font-medium text-[#c4b5fd]">
            {tokenType}
          </span>
        {/each}
      </div>
    </div>

    <div class="rounded-xl bg-white/[0.03] p-4">
      <div class="flex items-center justify-between gap-2 mb-3">
        <div>
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Index</p>
          <h4 class="mt-0.5 text-sm font-semibold tracking-tight text-white">{tokenIndex.title}</h4>
        </div>
        <span class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-300">
          <span class="h-1 w-1 rounded-full bg-emerald-400"></span>
          Active
        </span>
      </div>
      <div class="flex items-center gap-2">
        <code class="flex-1 min-w-0 text-xs font-mono text-gray-300 break-all rounded-lg bg-white/[0.03] px-2.5 py-2 border border-white/[0.06]">
          {tokenIndex.canisterId}
        </code>
        <button
          type="button"
          on:click={() => copyToClipboard(tokenIndex.canisterId, "Index")}
          class="agent-btn-ghost !h-8 !px-2.5 flex-shrink-0"
          title="Copy canister ID"
        >
          Copy
        </button>
      </div>
      <p class="mt-3 text-xs text-gray-500">Index canister is active and ready</p>
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
