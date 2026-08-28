<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { X } from '@lucide/svelte';
  import Portal from '../Portal.svelte';
  import InternetIdentityButton from "./InternetIdentityButton.svelte";
  import NfidButton from "./NfidButton.svelte";

  export let toggleModal;

  let loading = "";

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape' && !loading) {
      toggleModal();
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeydown);
  });

  onDestroy(() => {
    document.removeEventListener('keydown', handleKeydown);
  });
</script>

<Portal target="body">
  <div
    class="fixed inset-0 z-100000 flex items-center justify-center p-4 sm:p-6"
    role="dialog"
    aria-modal="true"
    aria-labelledby="login-modal-title"
  >
    <button
      type="button"
      class="absolute inset-0 bg-[#05040a]/80 backdrop-blur-md"
      aria-label="Close"
      on:click={() => { if (!loading) toggleModal(); }}
    ></button>

    <div class="relative z-10 w-full max-w-[420px] font-sans animate-modal-in">
      <div class="agent-modal relative overflow-hidden rounded-2xl border border-white/8 bg-agent-surface shadow-agent">
        <div class="pointer-events-none absolute inset-0">
          <div class="absolute -top-24 left-1/2 h-48 w-72 -translate-x-1/2 rounded-full bg-agent-purple/20 blur-3xl"></div>
          <div class="absolute inset-0 opacity-[0.35]" style="background-image: linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px); background-size: 28px 28px; mask-image: radial-gradient(ellipse at top, black 20%, transparent 70%);"></div>
        </div>

        <button
          type="button"
          on:click={() => toggleModal()}
          class="absolute top-4 right-4 z-10 inline-flex h-8 w-8 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-200"
          aria-label="Close"
        >
          <X class="w-4 h-4 stroke-[1.75]" />
        </button>

        <div class="relative px-7 pt-10 pb-7">
          <div class="mb-8">
            <p class="mb-3 text-[10px] font-medium uppercase tracking-[0.22em] text-agent-purple">
              Autonomous network
            </p>
            <h3 id="login-modal-title" class="text-[1.65rem] font-semibold leading-tight tracking-tight text-white">
              Enter the agentic world
            </h3>
            <p class="mt-3 max-w-sm text-sm font-normal leading-relaxed text-gray-400">
              Authenticate to deploy and operate your mAIners on the Proof-of-AI-Work protocol.
            </p>
          </div>

          <div class="space-y-2.5">
            <InternetIdentityButton bind:loading {toggleModal} />
            <NfidButton bind:loading {toggleModal} />
          </div>

          <p class="mt-7 text-center text-[11px] font-normal tracking-wide text-gray-600">
            End-to-end identity · No custodial keys
          </p>
        </div>
      </div>
    </div>
  </div>
</Portal>

<style>
  @keyframes modal-in {
    from {
      opacity: 0;
      transform: translateY(14px) scale(0.985);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .animate-modal-in {
    animation: modal-in 0.28s cubic-bezier(0.22, 1, 0.36, 1);
  }
</style>
