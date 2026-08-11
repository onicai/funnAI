<script lang="ts">
  import icLogoHexWhite from "../../assets/ic_logo_hex_white.svg";
</script>

<footer class="w-full border-t border-white/[0.06] bg-agent-bg text-gray-500 py-4 mt-auto font-sans">
  <div class="container mx-auto px-4 flex justify-center items-center">
    <div class="flex items-center text-xs font-normal tracking-wide">
      <span>powered by</span>
      <a 
        href="https://onicai.com" 
        target="_blank" 
        rel="noopener noreferrer"
        class="mx-2 text-sm font-medium text-agent-purple hover:text-[#7a55d4] transition-colors"
      >
        onicai
      </a>
      <span class="text-white/20">·</span>
      <span class="ml-2">built on</span>
      <img src={icLogoHexWhite} alt="Internet Computer" class="w-9 h-auto ml-2 opacity-60">
    </div>
  </div>
</footer>
