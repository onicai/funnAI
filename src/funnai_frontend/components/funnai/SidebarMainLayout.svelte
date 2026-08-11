<script lang="ts">
import { onMount } from 'svelte';
import { link } from 'svelte-spa-router';
import { downloadedModels } from "../../stores/store";
import { location } from 'svelte-spa-router';
import {
  Bot,
  LayoutDashboard,
  Wallet,
  ShoppingCart,
  LayoutGrid,
} from 'lucide-svelte';
import funnailogoWhite from "../../assets/funnai_white.svg";
import logoClickSound from "../../assets/wheel/1.mp3";

function playLogoSound() {
  const audio = new Audio(logoClickSound);
  audio.volume = 0.5;
  audio.play().catch(err => {
    console.log('Error playing sound:', err);
  });
}

onMount(() => {
  const sidebarToggle = document.getElementById('mainSidebarToggle');
  const mainSidebar = document.getElementById('mainSidebar');

  function toggleSidebar(event) {
    event.stopPropagation();
    mainSidebar.classList.toggle('-translate-x-full');
  };

  function closeSidebarOutside(event) {
    if (!mainSidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
      mainSidebar.classList.add('-translate-x-full');
    };
  };

  function stopPropagation(event) {
    event.stopPropagation();
  };

  sidebarToggle.addEventListener('click', toggleSidebar);
  document.body.addEventListener('click', closeSidebarOutside);
  mainSidebar.addEventListener('click', stopPropagation);

  return () => {
    sidebarToggle.removeEventListener('click', toggleSidebar);
    document.body.removeEventListener('click', closeSidebarOutside);
    mainSidebar.removeEventListener('click', stopPropagation);
  };
});

function closeSidebar() {
  const mainSidebar = document.getElementById('mainSidebar');
  mainSidebar?.classList.add('-translate-x-full');
}

$: userHasDownloadedAtLeastOneModel = $downloadedModels.length > 0;
$: currentPath = $location;

const navItems = [
  { href: '/', label: 'mAIners', icon: Bot },
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/wallet', label: 'Wallet', icon: Wallet },
  { href: '/marketplace', label: 'Marketplace', icon: ShoppingCart },
  { href: '/store', label: 'App Store', icon: LayoutGrid },
];
</script>

<div class="sidebar-header font-sans flex flex-col h-full bg-agent-surface">
    <!-- Header Section -->
    <div class="flex flex-col items-start px-4 py-5">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <a use:link href="/" on:dblclick={playLogoSound}>
          <div class="w-28 h-6 relative ml-3">
            <img src={funnailogoWhite} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain object-left" width="112" height="24" />
          </div>
        </a>
      </h1>
    </div>

    <!-- Manage navigation (redesigned) -->
    <nav class="flex-1 px-3 pt-2 pb-3 overflow-y-auto">
      <p class="px-3 mb-3 text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">
        Manage
      </p>
      <ul class="space-y-0.5">
        {#each navItems as item}
          <li>
            <a
              use:link
              href={item.href}
              class="group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] tracking-tight transition-all duration-200
                {currentPath === item.href
                  ? 'font-medium bg-white/[0.07] text-white'
                  : 'font-normal text-gray-500 hover:bg-white/[0.05] hover:text-gray-200'}"
              on:click={closeSidebar}
            >
              {#if currentPath === item.href}
                <span
                  class="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r-full bg-agent-purple"
                  aria-hidden="true"
                ></span>
              {/if}
              <svelte:component
                this={item.icon}
                class="w-[18px] h-[18px] shrink-0 stroke-[1.6] transition-colors duration-200
                  {currentPath === item.href
                    ? 'text-agent-purple'
                    : 'text-gray-600 group-hover:text-agent-purple'}"
              />
              <span class="leading-none">{item.label}</span>
            </a>
          </li>
        {/each}
      </ul>
    </nav>

    <!-- Footer Section -->
    <div class="px-4 pb-5 border-t border-white/[0.06]">
      <div class="py-3">
        <p class="px-2 mb-2 text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">More from onicai</p>
        
        <a href="https://www.onicai.com/files/funnAI_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-1" on:click={closeSidebar}>
          <span class="w-full px-3 py-2 rounded-xl transition-colors duration-150 flex items-center gap-2 text-xs font-normal text-gray-500 hover:bg-white/[0.05] hover:text-gray-200">
            <span class="flex-1">funnAI Whitepaper</span>
          </span>
        </a>

        <a href="https://www.onicai.com/files/onicai_SNS_Whitepaper.pdf" target="_blank" rel="noopener noreferrer" class="block mb-1" on:click={closeSidebar}>
          <span class="w-full px-3 py-2 rounded-xl transition-colors duration-150 flex items-center gap-2 text-xs font-normal text-gray-500 hover:bg-white/[0.05] hover:text-gray-200">
            <span class="flex-1">onicai SNS Whitepaper</span>
          </span>
        </a>

        <a href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/?ref=mwte3-ciaaa-aaaaf-ad7aq-cai"
           target="_blank"
           rel="noopener noreferrer"
           class="block mb-3">
          <span class="w-full px-3 py-2 rounded-xl transition-colors duration-150 flex items-center gap-2 text-xs font-normal text-gray-500 hover:bg-white/[0.05] hover:text-gray-200">
            Support
          </span>
        </a>
      </div>

      <p class="px-2 mb-2 text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Connect</p>
      <div class="flex items-center gap-2 px-1">
        <a href="https://www.onicai.com/#/funnai" target="_blank" rel="noopener noreferrer" 
           class="flex-1 flex items-center justify-center p-2.5 rounded-xl bg-white/[0.03] border border-white/10 text-gray-500 transition-colors hover:text-agent-purple hover:border-agent-purple/30"
           aria-label="onicai website">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <circle cx="12" cy="12" r="9" stroke-width="1.75"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12h18"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c-2.5 3-2.5 9 0 18"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c2.5 3 2.5 9 0 18"/>
          </svg>
        </a>
        <a href="https://x.com/onicaiHQ" target="_blank" rel="noopener noreferrer"
           class="flex-1 flex items-center justify-center p-2.5 rounded-xl bg-white/[0.03] border border-white/10 text-gray-500 transition-colors hover:text-agent-purple hover:border-agent-purple/30"
           aria-label="onicai on X">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
        </a>
      </div>
    </div>
</div>
