<script lang="ts">
  export let agent: any;
</script>

<div class="rounded-xl bg-white/3 px-3 py-2.5">
  <div class="flex items-center justify-between gap-3">
    <div class="min-w-0">
      <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Controller</p>
      <p class="mt-0.5 font-mono text-[11px] text-gray-300 truncate" title={agent.id}>{agent.id}</p>
    </div>
    <a
      href="https://dashboard.internetcomputer.org/canister/{agent.id}"
      target="_blank"
      rel="noopener noreferrer"
      class="shrink-0 inline-flex items-center gap-1.5 h-8 px-2.5 rounded-lg border border-white/10 bg-white/4 text-[11px] font-medium text-gray-200 hover:border-agent-purple/40 hover:bg-agent-purple/15 hover:text-white transition-colors"
    >
      Dashboard
      <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
      </svg>
    </a>
  </div>
</div>
