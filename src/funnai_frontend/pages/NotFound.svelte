<script lang="ts">
  import { link } from "svelte-spa-router";
</script>

<div class="flex min-h-full items-center justify-center px-6 py-16">
  <div class="w-full max-w-md rounded-2xl border border-white/8 bg-agent-surface/80 px-8 py-10 text-center shadow-[0_24px_48px_-28px_rgba(0,0,0,0.7)]">
    <p class="text-[11px] font-medium uppercase tracking-[0.16em] text-gray-500">404</p>
    <h1 class="mt-3 font-fredoka text-2xl font-semibold tracking-tight text-white">
      Page not found
    </h1>
    <p class="mt-2 text-sm leading-relaxed text-gray-400">
      That route doesn't exist. Head back to your mAIners.
    </p>
    <a
      use:link
      href="/"
      class="mt-6 inline-flex items-center justify-center rounded-xl border border-agent-purple/35 bg-agent-purple/15 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:border-agent-purple/55 hover:bg-agent-purple/25"
    >
      Go to mAIners
    </a>
  </div>
</div>
