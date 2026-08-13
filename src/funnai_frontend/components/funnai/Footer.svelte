<script lang="ts">
  import icLogoHexWhite from "../../assets/ic_logo_hex_white.svg";
</script>

<footer class="relative w-full border-t border-white/[0.06] bg-agent-bg/40 backdrop-blur-md text-gray-500 py-4 mt-auto font-sans shadow-[0_-12px_32px_-20px_rgba(101,63,197,0.18)]">
  <div class="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/18 to-transparent"></div>
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
