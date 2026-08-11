<script lang="ts">
  export let rows: number = 3;
</script>

<div class="max-h-[600px] overflow-y-auto">
  <div class="hidden sm:grid sm:grid-cols-[2fr,1.5fr,1fr] gap-4 px-4 py-2 border-b border-white/[0.06]">
    <div class="h-3 bg-white/[0.06] rounded animate-pulse"></div>
    <div class="h-3 bg-white/[0.06] rounded animate-pulse"></div>
    <div class="h-3 bg-white/[0.06] rounded animate-pulse"></div>
  </div>

  <div class="divide-y divide-white/[0.06]">
    {#each Array(rows) as _, i}
      <div class="sm:grid sm:grid-cols-[2fr,1.5fr,1fr] sm:gap-4 sm:items-center p-4">
        <div class="flex flex-col gap-3 sm:hidden">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 bg-white/[0.06] rounded-full animate-pulse"></div>
              <div class="flex flex-col gap-1">
                <div class="h-4 w-16 bg-white/[0.06] rounded animate-pulse"></div>
                <div class="h-3 w-20 bg-white/[0.04] rounded animate-pulse"></div>
              </div>
            </div>
            <div class="h-4 w-20 bg-white/[0.06] rounded animate-pulse"></div>
          </div>
          <div class="flex justify-end gap-2 mt-2">
            <div class="h-8 w-16 bg-white/[0.06] rounded-full animate-pulse"></div>
            <div class="h-8 w-12 bg-white/[0.06] rounded-full animate-pulse"></div>
          </div>
        </div>

        <div class="hidden sm:flex items-center gap-3">
          <div class="w-9 h-9 bg-white/[0.06] rounded-full animate-pulse"></div>
          <div class="flex flex-col gap-1">
            <div class="h-4 w-16 bg-white/[0.06] rounded animate-pulse"></div>
            <div class="h-3 w-24 bg-white/[0.04] rounded animate-pulse"></div>
          </div>
        </div>

        <div class="hidden sm:block text-right">
          <div class="h-4 w-20 bg-white/[0.06] rounded animate-pulse ml-auto"></div>
        </div>

        <div class="hidden sm:block text-right">
          <div class="flex justify-end gap-2">
            <div class="h-8 w-16 bg-white/[0.06] rounded-full animate-pulse"></div>
            <div class="h-8 w-12 bg-white/[0.06] rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>
