<script lang="ts">
  import { theme } from "../../stores/store";
  import icLogoHex from "../../assets/ic_logo_hex.svg";
  import icLogoHexWhite from "../../assets/ic_logo_hex_white.svg";
  
  const currentYear = new Date().getFullYear();
</script>

<footer class="w-full bg-gray-200 dark:bg-gray-800 text-gray-500 dark:text-gray-200 py-4 mt-auto">
  <div class="container mx-auto px-4 flex justify-between items-center">
    <div class="flex items-center">
      {#if $theme === 'dark'}
        <img src={icLogoHexWhite} alt="IC Logo" class="w-16 h-auto">
      {:else}
        <img src={icLogoHex} alt="IC Logo" class="w-16 h-auto">
      {/if}
    </div>
    <p class="text-sm">
      {currentYear}<sup>©</sup>  onicai.com
    </p>
  </div>
</footer>
