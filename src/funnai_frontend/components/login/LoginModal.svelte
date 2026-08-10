<script lang="ts">
  import { onMount } from 'svelte';
  import { X } from 'lucide-svelte';
  import InternetIdentityButton from "./InternetIdentityButton.svelte";
  import NfidButton from "./NfidButton.svelte";

  export let toggleModal;

  let loading = "";

  const initializeModal = () => {
    const modal = document.getElementById('crypto-modal');
    window.addEventListener('click', (event) => {
      if (event.target === modal) {
        toggleModal();
      }
    });
  };

  onMount(() => {
    initializeModal();
  });
</script>

<div
  id="crypto-modal"
  tabindex="-1"
  aria-hidden="true"
  class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-[#05040a]/80 backdrop-blur-md"
>
  <div class="relative w-full max-w-[420px] font-sans animate-modal-in">
    <div class="agent-modal relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c0b12] shadow-[0_24px_80px_-20px_rgba(101,63,197,0.35)]">
      <!-- Atmosphere -->
      <div class="pointer-events-none absolute inset-0">
        <div class="absolute -top-24 left-1/2 h-48 w-72 -translate-x-1/2 rounded-full bg-[#653FC5]/20 blur-3xl"></div>
        <div class="absolute inset-0 opacity-[0.35]" style="background-image: linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px); background-size: 28px 28px; mask-image: radial-gradient(ellipse at top, black 20%, transparent 70%);"></div>
      </div>

      <button
        type="button"
        on:click={() => toggleModal()}
        class="absolute top-4 right-4 z-10 inline-flex h-8 w-8 items-center justify-center rounded-full text-gray-500 transition-colors hover:bg-white/5 hover:text-gray-200"
        data-modal-toggle="crypto-modal"
        aria-label="Close"
      >
        <X class="w-4 h-4 stroke-[1.75]" />
      </button>

      <div class="relative px-7 pt-10 pb-7">
        <div class="mb-8">
          <p class="mb-3 text-[10px] font-medium uppercase tracking-[0.22em] text-[#653FC5]">
            Autonomous network
          </p>
          <h3 class="text-[1.65rem] font-semibold leading-tight tracking-tight text-white">
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
