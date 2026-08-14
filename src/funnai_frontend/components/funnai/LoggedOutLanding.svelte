<script lang="ts">
  import { onMount } from "svelte";
  import InternetIdentityButton from "../login/InternetIdentityButton.svelte";
  import NfidButton from "../login/NfidButton.svelte";
  import { DailyMetricsService } from "../../helpers/DailyMetricsService";

  let loading = "";
  let metricsLoading = true;
  let activeMainers: number | null = null;
  let funnaiIndex: number | null = null;
  let auraEl: HTMLImageElement | null = null;
  let auraReady = false;

  const toggleModal = () => {};

  function revealAura(img: HTMLImageElement) {
    if (auraReady) return;
    const show = () => {
      auraReady = true;
    };
    if (typeof img.decode === "function") {
      img.decode().then(show).catch(show);
    } else {
      show();
    }
  }

  function handleAuraLoad(event: Event) {
    revealAura(event.currentTarget as HTMLImageElement);
  }

  onMount(async () => {
    if (auraEl && auraEl.complete && auraEl.naturalWidth > 0) {
      revealAura(auraEl);
    }

    try {
      const latest = await DailyMetricsService.getLatestMetrics();
      if (latest) {
        activeMainers = latest.mainers.totals.active;
        funnaiIndex = latest.system_metrics.funnai_index * 100;
      }
    } catch (err) {
      console.warn("Logged-out landing metrics unavailable:", err);
    } finally {
      metricsLoading = false;
    }
  });
</script>

<section class="relative mx-auto w-full max-w-5xl px-2 sm:px-0 pt-6 sm:pt-10 pb-16 sm:pb-24 min-h-[28rem] sm:min-h-[34rem]">
  <div class="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
    <img
      bind:this={auraEl}
      src="/landing-aura.jpg"
      alt=""
      width="1024"
      height="635"
      decoding="async"
      on:load={handleAuraLoad}
      class="landing-aura absolute left-1/2 bottom-0 w-[160%] max-w-none -translate-x-1/2 translate-y-[4%] mix-blend-screen select-none {auraReady ? 'is-ready' : ''}"
    />
    <img
      src="/landing-stars.png"
      alt=""
      class="absolute -top-6 left-[4%] w-40 sm:w-52 mix-blend-screen opacity-80 select-none"
    />
    <img
      src="/landing-stars.png"
      alt=""
      class="absolute top-[8%] right-[2%] w-36 sm:w-48 mix-blend-screen opacity-70 select-none rotate-12"
    />
    <img
      src="/landing-stars.png"
      alt=""
      class="absolute bottom-[28%] left-[8%] w-28 sm:w-36 mix-blend-screen opacity-55 select-none -rotate-6"
    />
    <img
      src="/landing-stars.png"
      alt=""
      class="absolute bottom-[12%] right-[10%] w-32 sm:w-40 mix-blend-screen opacity-65 select-none rotate-[-12deg]"
    />
  </div>

  <div class="relative text-center max-w-3xl mx-auto">
    <p class="agent-eyebrow mb-4">Autonomous network</p>
    <h1 class="text-[1.85rem] sm:text-4xl lg:text-[2.75rem] font-semibold tracking-tight text-white leading-[1.15]">
      Own your
      <span class="bg-gradient-to-r from-[#ddd6fe] via-[#c4b5fd] to-[#653FC5] bg-clip-text text-transparent">autonomous agents</span>
      on the Proof-of-AI-Work protocol
    </h1>
    <p class="mt-4 sm:mt-5 text-sm sm:text-base font-normal leading-relaxed text-gray-400 max-w-xl mx-auto">
      Deploy mAIners, compete in on-chain challenges, and earn FUNNAI — with Internet Identity or NFID, no custodial keys.
    </p>
  </div>

  <div class="relative mt-10 sm:mt-14 grid grid-cols-1 xl:grid-cols-[11rem_minmax(0,28rem)_11rem] xl:justify-center gap-3 xl:gap-5 items-start">
    <!-- Floating metric -->
    <div class="order-2 xl:order-1 w-full rounded-2xl border border-white/[0.08] bg-[#0c0b12]/80 backdrop-blur-xl p-4 shadow-[0_18px_40px_-24px_rgba(101,63,197,0.45)] xl:mt-6">
      <div class="flex items-center gap-1.5 mb-3">
        <span class="h-1.5 w-1.5 rounded-full bg-[#a78bfa] animate-pulse"></span>
        <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-400">Live network</p>
      </div>
      <p class="text-[11px] text-gray-500">Active mAIners</p>
      <p class="mt-1 text-3xl font-semibold tracking-tight text-white tabular-nums leading-8 min-h-8">
        {#if metricsLoading}
          <span class="agent-metric-pulse w-[4ch]" aria-hidden="true"></span>
        {:else}
          {(activeMainers ?? 0).toLocaleString()}
        {/if}
      </p>
    </div>

    <!-- Connect module — identity options on-page, not in a dropdown -->
    <div class="order-1 xl:order-2 relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#0c0b12]/85 backdrop-blur-xl shadow-[0_24px_64px_-28px_rgba(101,63,197,0.4)]">
      <div class="pointer-events-none absolute inset-0">
        <div class="absolute -top-16 left-1/2 h-32 w-56 -translate-x-1/2 rounded-full bg-[#653FC5]/20 blur-3xl"></div>
      </div>

      <div class="relative p-4 sm:p-5">
        <p class="agent-eyebrow mb-3">Connect</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          <InternetIdentityButton bind:loading {toggleModal} />
          <NfidButton bind:loading {toggleModal} />
        </div>
      </div>

      <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-t border-white/[0.06] px-4 sm:px-5 py-3.5">
        <p class="text-sm font-medium text-[#c4b5fd]">
          ✓ Ready to deploy mAIners
        </p>
        <p class="text-[11px] text-gray-500">
          End-to-end identity · no custodial keys
        </p>
      </div>
    </div>

    <!-- Floating chips -->
    <div class="order-3 flex flex-wrap xl:flex-col gap-2 justify-center xl:items-end xl:mt-10">
      <span class="inline-flex items-center rounded-xl border border-white/[0.08] bg-[#0c0b12]/80 backdrop-blur-xl px-3.5 py-2 text-[12px] font-medium text-gray-200 shadow-[0_12px_28px_-18px_rgba(0,0,0,0.65)]">
        Proof-of-AI-Work
      </span>
      <span class="inline-flex items-center rounded-xl border border-white/[0.08] bg-[#0c0b12]/80 backdrop-blur-xl px-3.5 py-2 text-[12px] font-medium text-gray-200 xl:translate-x-2">
        On-chain identity
      </span>
      <span class="inline-flex items-center rounded-xl border border-white/[0.08] bg-[#0c0b12]/80 backdrop-blur-xl px-3.5 py-2 text-[12px] font-medium text-gray-200">
        {#if metricsLoading}
          Internet Computer
        {:else if funnaiIndex !== null}
          FunnAI Index {funnaiIndex.toFixed(1)}%
        {:else}
          Internet Computer
        {/if}
      </span>
    </div>
  </div>
</section>

<style>
  .landing-aura {
    opacity: 0;
    transition: opacity 0.85s ease-out;
  }

  .landing-aura.is-ready {
    opacity: 1;
  }
</style>
