<script lang="ts">
  export let rows: number = 3;
</script>

<div class="space-y-2">
  {#each Array(rows) as _, i}
    <div class="rounded-xl border border-white/[0.07] bg-white/2.5 p-3.5 sm:px-4 sm:py-3.5">
      <div class="flex items-center gap-3">
        <div class="h-11 w-11 shrink-0 rounded-xl bg-white/6 animate-pulse"></div>
        <div class="flex-1 min-w-0 space-y-1.5">
          <div class="h-3.5 w-16 bg-white/6 rounded-sm animate-pulse"></div>
          <div class="h-3 w-24 bg-white/4 rounded-sm animate-pulse"></div>
        </div>
        <div class="hidden sm:block h-3.5 w-20 bg-white/6 rounded-sm animate-pulse"></div>
        <div class="flex gap-2">
          <div class="h-8 w-16 bg-white/6 rounded-full animate-pulse"></div>
          <div class="h-8 w-12 bg-white/6 rounded-full animate-pulse"></div>
        </div>
      </div>
    </div>
  {/each}
</div>
