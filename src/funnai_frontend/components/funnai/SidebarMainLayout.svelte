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
// import funnailogoWhite from "../../assets/funnai_white.svg";
// import logoClickSound from "../../assets/wheel/1.mp3";

// function playLogoSound() {
//   const audio = new Audio(logoClickSound);
//   audio.volume = 0.5;
//   audio.play().catch(err => {
//     console.log('Error playing sound:', err);
//   });
// }

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

<div class="sidebar-header font-sans flex flex-col h-full bg-transparent">
    <!-- Logotype (temporarily hidden)
    <div class="flex flex-col items-start px-4 py-5">
      <h1 class="text-2xl font-semibold flex items-center gap-2">
        <a use:link href="/" on:dblclick={playLogoSound}>
          <div class="w-28 h-6 relative ml-3">
            <img src={funnailogoWhite} alt="funnAI logo" class="absolute inset-0 w-full h-full object-contain object-left" width="112" height="24" />
          </div>
        </a>
      </h1>
    </div>
    -->

    <!-- Manage navigation (redesigned) -->
    <nav class="flex-1 px-3 pt-5 pb-3 overflow-y-auto">
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

    <!-- Connect module -->
    <div class="px-3 pb-4 pt-3 border-t border-white/[0.06]">
      <div class="rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent p-3">
        <div class="px-1 mb-3">
          <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Connect</p>
          <p class="mt-1 text-[12px] leading-snug text-gray-500">Community & support from onicai</p>
        </div>

        <a
          href="https://oc.app/community/mepna-eqaaa-aaaar-bclua-cai/channel/2881126157/?ref=mwte3-ciaaa-aaaaf-ad7aq-cai"
          target="_blank"
          rel="noopener noreferrer"
          class="group flex items-center gap-3 rounded-xl border border-[#653FC5]/25 bg-[#653FC5]/12 px-3 py-2.5 transition-all duration-200 hover:border-[#653FC5]/45 hover:bg-[#653FC5]/18"
          aria-label="Open support community"
          on:click={closeSidebar}
        >
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.06] text-[#c4b5fd]">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </span>
          <span class="min-w-0 flex-1">
            <span class="block text-[13px] font-medium tracking-tight text-white leading-none">Support</span>
            <span class="mt-1 block text-[11px] text-gray-400 leading-none">OpenChat community</span>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0 text-gray-500 transition-transform duration-200 group-hover:translate-x-0.5 group-hover:text-[#c4b5fd]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </a>

        <div class="mt-2.5 grid grid-cols-2 gap-2">
          <a
            href="https://www.onicai.com/#/funnai"
            target="_blank"
            rel="noopener noreferrer"
            class="group flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-2.5 py-2 text-gray-400 transition-colors hover:border-[#653FC5]/35 hover:bg-[#653FC5]/10 hover:text-gray-200"
            aria-label="onicai website"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0 text-gray-500 group-hover:text-[#a78bfa] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <circle cx="12" cy="12" r="9" stroke-width="1.75"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12h18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c-2.5 3-2.5 9 0 18"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 3c2.5 3 2.5 9 0 18"/>
            </svg>
            <span class="text-[11px] font-medium leading-none tracking-tight">Website</span>
          </a>
          <a
            href="https://x.com/onicaiHQ"
            target="_blank"
            rel="noopener noreferrer"
            class="group flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-2.5 py-2 text-gray-400 transition-colors hover:border-[#653FC5]/35 hover:bg-[#653FC5]/10 hover:text-gray-200"
            aria-label="onicai on X"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 shrink-0 text-gray-500 group-hover:text-[#a78bfa] transition-colors" fill="currentColor" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
            <span class="text-[11px] font-medium leading-none tracking-tight">X / Twitter</span>
          </a>
        </div>
      </div>
    </div>
</div>
