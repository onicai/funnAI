<script lang="ts">
  import { link } from "svelte-spa-router";
  import { ShoppingCart, Sparkles } from "@lucide/svelte";
  import { fly } from "svelte/transition";
</script>

<div
  in:fly={{ y: 14, duration: 480 }}
  class="empty-fleet relative overflow-hidden rounded-2xl border border-agent-purple/30 bg-agent-surface font-sans"
>
  <div class="pointer-events-none absolute inset-0" aria-hidden="true">
    <div class="empty-fleet-orb empty-fleet-orb-a absolute -top-16 -right-10 h-40 w-40 rounded-full bg-agent-purple/30 blur-3xl"></div>
    <div class="empty-fleet-orb empty-fleet-orb-b absolute -bottom-20 -left-8 h-36 w-36 rounded-full bg-fuchsia-500/15 blur-3xl"></div>
    <div class="empty-fleet-sheen absolute inset-0"></div>
  </div>

  <div class="relative flex flex-col gap-5 p-5 sm:flex-row sm:items-center sm:gap-6 sm:p-6">
    <div class="empty-fleet-icon relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-agent-purple/35 bg-agent-purple/15 shadow-[0_0_24px_rgba(101,63,197,0.35)]">
      <Sparkles class="h-6 w-6 text-[#c4b5fd]" />
      <span class="absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.9)]"></span>
    </div>

    <div class="min-w-0 flex-1">
      <p class="agent-eyebrow mb-1">Marketplace</p>
      <h2 class="text-lg font-semibold tracking-tight text-white sm:text-xl">Your fleet is empty</h2>
      <p class="mt-1 max-w-lg text-sm leading-relaxed text-gray-400">
        Buy your first mAIner on the marketplace and start mining on the network.
      </p>
    </div>

    <a
      use:link
      href="/marketplace"
      class="agent-btn-neon agent-btn-neon-pink no-underline w-full sm:w-auto sm:shrink-0"
    >
      <ShoppingCart class="h-3.5 w-3.5 stroke-[1.75]" />
      <span>Buy your first mAIner</span>
    </a>
  </div>
</div>

<style>
  .empty-fleet {
    animation: emptyFleetIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  .empty-fleet-orb-a {
    animation: emptyFleetOrb 8s ease-in-out infinite;
  }

  .empty-fleet-orb-b {
    animation: emptyFleetOrb 10s ease-in-out infinite reverse;
  }

  .empty-fleet-sheen {
    background: linear-gradient(
      110deg,
      transparent 30%,
      rgba(196, 181, 253, 0.14) 48%,
      transparent 62%
    );
    background-size: 220% 100%;
    animation: emptyFleetSheen 5.5s ease-in-out infinite;
  }

  .empty-fleet-icon {
    animation: emptyFleetPulse 2.8s ease-in-out infinite;
  }

  @keyframes emptyFleetIn {
    from {
      opacity: 0;
      transform: translateY(10px) scale(0.98);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  @keyframes emptyFleetOrb {
    0%,
    100% {
      transform: translate3d(0, 0, 0) scale(1);
      opacity: 0.55;
    }
    50% {
      transform: translate3d(-14px, 12px, 0) scale(1.12);
      opacity: 0.9;
    }
  }

  @keyframes emptyFleetSheen {
    0%,
    100% {
      background-position: 120% 0;
      opacity: 0;
    }
    35% {
      opacity: 0.85;
    }
    55% {
      background-position: -20% 0;
      opacity: 0.4;
    }
    70%,
    100% {
      opacity: 0;
    }
  }

  @keyframes emptyFleetPulse {
    0%,
    100% {
      box-shadow: 0 0 18px rgba(101, 63, 197, 0.28);
    }
    50% {
      box-shadow: 0 0 28px rgba(196, 181, 253, 0.55);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .empty-fleet,
    .empty-fleet-orb-a,
    .empty-fleet-orb-b,
    .empty-fleet-sheen,
    .empty-fleet-icon {
      animation: none;
    }
  }
</style>
