<script lang="ts">
  export let rows: number = 3;
</script>

<div class="max-h-[600px] overflow-y-auto">
  <!-- Header skeleton -->
  <div class="hidden sm:grid sm:grid-cols-[2fr,1.5fr,1fr] gap-4 px-4 py-2 border-b border-gray-200 dark:border-gray-700">
    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
    <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
  </div>

  <!-- Token rows skeleton -->
  <div class="divide-y divide-gray-200 dark:divide-gray-700">
    {#each Array(rows) as _, i}
      <div class="sm:grid sm:grid-cols-[2fr,1.5fr,1fr] sm:gap-4 sm:items-center p-4">
        <!-- Mobile skeleton -->
        <div class="flex flex-col gap-3 sm:hidden">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"></div>
              <div class="flex flex-col gap-1">
                <div class="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
                <div class="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
              </div>
            </div>
            <div class="text-right">
              <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-4">
            <div class="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
            <div class="h-8 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
          </div>
        </div>

        <!-- Desktop token column skeleton -->
        <div class="hidden sm:flex items-center gap-3">
          <div class="w-9 h-9 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"></div>
          <div class="flex flex-col gap-1">
            <div class="h-4 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
            <div class="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"></div>
          </div>
        </div>

        <!-- Desktop balance column skeleton -->
        <div class="hidden sm:block text-right">
          <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse ml-auto"></div>
        </div>

        <!-- Desktop actions column skeleton -->
        <div class="hidden sm:block text-right">
          <div class="flex justify-end gap-2">
            <div class="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
            <div class="h-8 w-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div> 