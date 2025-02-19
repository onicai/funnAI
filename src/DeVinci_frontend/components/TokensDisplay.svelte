<script lang="ts">
  export let icpBalance: number = 0;
  export let funnaiBalance: number = 0;

  $: formattedICP = icpBalance.toFixed(2);
  $: formattedFUNNAI = funnaiBalance.toFixed(2);
</script>

<div class="flex gap-4  mr-1">
  <!-- ICP Balance -->
  <div class="flex items-center gap-2 bg-slate-800/10 px-3 py-1.5 rounded-full">
    <img
      src="/icp-rounded.svg"
      alt="ICP Token"
      class="w-5 h-5 border border-pink-300 rounded-full"
    />
    <span class="font-medium text-slate-700">{formattedICP}</span>
  </div>

  <!-- FUNNAI Balance -->
  <div class="flex items-center gap-2 bg-orange-100 px-3 py-1.5 mr-2 rounded-full">
    <img
      src="/coin.webp"
      alt="FUNNAI Token"
      class="w-5 h-5"
    />
    <span class="font-medium text-orange-700">{formattedFUNNAI}</span>
  </div>
</div> 