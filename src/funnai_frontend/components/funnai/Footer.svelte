<script lang="ts">
  import { theme } from "../../stores/store";
  import icLogoHex from "../../assets/ic_logo_hex.svg";
  import icLogoHexWhite from "../../assets/ic_logo_hex_white.svg";
  
  const currentYear = new Date().getFullYear();
</script>

<footer class="w-full bg-gradient-to-r from-gray-100 via-gray-200 to-gray-300 dark:bg-gradient-to-r dark:from-gray-900 dark:via-gray-800 dark:to-gray-700 text-gray-500 dark:text-gray-400 py-3 mt-auto">
  <div class="container mx-auto px-4 flex justify-center items-center">
    <div class="flex items-center text-xs">
      <span>powered by</span>
      <a 
        href="https://onicai.com" 
        target="_blank" 
        rel="noopener noreferrer"
        class="mx-2 ml-1 text-sm font-medium text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 transition-colors"
        style="text-shadow: 0 0 6px rgba(147, 51, 234, 0.4); animation: glow-pulse 2.5s ease-in-out infinite;"
      >
        onicai
      </a>
      <span>•</span>
      <span class="ml-2">built on</span>
      {#if $theme === 'dark'}
        <img src={icLogoHexWhite} alt="Internet Computer" class="w-10 h-auto ml-2 opacity-75">
      {:else}
        <img src={icLogoHex} alt="Internet Computer" class="w-10 h-auto ml-2 opacity-75">
      {/if}
    </div>
  </div>
</footer>

<style>
  @keyframes glow-pulse {
    0%, 100% {
      text-shadow: 0 0 6px rgba(147, 51, 234, 0.4);
      opacity: 0.9;
    }
    50% {
      text-shadow: 0 0 10px rgba(147, 51, 234, 0.6), 0 0 16px rgba(147, 51, 234, 0.2);
      opacity: 1;
    }
  }
</style>
