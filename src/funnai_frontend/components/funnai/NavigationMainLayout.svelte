<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import { link, location } from 'svelte-spa-router';
  import LoginModal from '../login/LoginModal.svelte';
  import {
    ShoppingCart,
    LogIn,
    Bot,
    LayoutDashboard,
    Wallet,
    LayoutGrid,
    Menu,
    ChevronDown,
    LogOut,
  } from 'lucide-svelte';

  let navigationDropdownOpen = false;

  let modalIsOpen = false;

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  const toggleNavigationDropdown = (event: Event) => {
    event.stopPropagation();
    navigationDropdownOpen = !navigationDropdownOpen;
  };

  const closeNavigationDropdown = () => {
    navigationDropdownOpen = false;
  };

  async function disconnect() {
    await store.disconnect();
  }

  const navItems = [
    { href: '/', label: 'mAIners', icon: Bot },
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/wallet', label: 'Wallet', icon: Wallet },
    { href: '/marketplace', label: 'Marketplace', icon: ShoppingCart },
    { href: '/store', label: 'App Store', icon: LayoutGrid },
  ];

  $: currentPath = $location;

  const initializeDropdown = () => {
    document.body.addEventListener('click', function (event) {
      const target = event.target as Node;
      const navDropdown = document.getElementById('navigationDropdown');
      const navDropdownButton = document.getElementById('navigationDropdownButton');

      if (
        navDropdown &&
        navDropdownButton &&
        !navDropdown.contains(target) &&
        !navDropdownButton.contains(target)
      ) {
        closeNavigationDropdown();
      }
    });
  };

  onMount(() => {
    initializeDropdown();
  });
</script>

<div class="flex items-center justify-center w-full relative font-sans">
  <div class="ml-auto flex items-center gap-2.5">
    <a
      use:link
      href="/marketplace"
      class="nav-pill group flex items-center gap-2 h-9 px-3.5 rounded-full border border-white/10 bg-white/[0.04] text-gray-200 text-[13px] font-medium tracking-tight no-underline transition-all duration-200 hover:border-agent-purple/40 hover:bg-agent-purple/10 hover:text-white"
    >
      <ShoppingCart class="w-3.5 h-3.5 stroke-[1.75] text-gray-400 transition-colors duration-200 group-hover:text-agent-purple" />
      <span>Buy mAIner</span>
    </a>

    {#if $store.isAuthed}
      <div class="relative z-[80]">
        <button
          id="navigationDropdownButton"
          type="button"
          aria-haspopup="menu"
          aria-expanded={navigationDropdownOpen}
          on:click={toggleNavigationDropdown}
          class="nav-pill flex items-center gap-2 h-9 px-3.5 rounded-full border text-[13px] font-medium tracking-tight transition-all duration-200
            {navigationDropdownOpen
              ? 'border-agent-purple/50 bg-agent-purple/15 text-white'
              : 'border-white/10 bg-white/[0.04] text-gray-200 hover:border-agent-purple/40 hover:bg-agent-purple/10 hover:text-white'}"
        >
          <Menu class="w-3.5 h-3.5 stroke-[1.75] {navigationDropdownOpen ? 'text-agent-purple' : 'text-gray-400'}" />
          <span class="hidden sm:inline">Menu</span>
          <ChevronDown
            class="w-3.5 h-3.5 stroke-[1.75] text-gray-500 transition-transform duration-200 {navigationDropdownOpen ? 'rotate-180 text-agent-purple' : ''}"
          />
        </button>

        {#if navigationDropdownOpen}
          <!-- Backdrop keeps page interactions blocked and ensures overlay stacking -->
          <button
            type="button"
            class="fixed inset-0 z-[90] cursor-default bg-black/20"
            aria-label="Close menu"
            on:click={closeNavigationDropdown}
          ></button>

          <div
            id="navigationDropdown"
            role="menu"
            class="absolute right-0 top-full mt-2 w-60 z-[100] overflow-hidden rounded-2xl border border-white/10 bg-[#15141B] shadow-[0_20px_50px_rgba(0,0,0,0.55)] animate-slideDown"
          >
            <div class="border-b border-white/[0.06] px-4 py-3">
              <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Navigate</p>
            </div>

            <div class="p-1.5">
              {#each navItems as item}
                <a
                  use:link
                  href={item.href}
                  role="menuitem"
                  on:click={closeNavigationDropdown}
                  class="group flex items-center gap-3 rounded-xl px-3 py-2.5 no-underline transition-colors duration-150
                    {currentPath === item.href
                      ? 'bg-white/[0.07] text-white'
                      : 'text-gray-400 hover:bg-white/[0.05] hover:text-gray-100'}"
                >
                  <svelte:component
                    this={item.icon}
                    class="w-4 h-4 stroke-[1.75] shrink-0 {currentPath === item.href
                      ? 'text-agent-purple'
                      : 'text-gray-500 group-hover:text-agent-purple'}"
                  />
                  <span class="text-[13px] font-medium tracking-tight">{item.label}</span>
                  {#if currentPath === item.href}
                    <span class="ml-auto h-1.5 w-1.5 rounded-full bg-agent-purple"></span>
                  {/if}
                </a>
              {/each}
            </div>

            <div class="border-t border-white/[0.06] p-1.5">
              <button
                type="button"
                role="menuitem"
                on:click={() => {
                  disconnect();
                  closeNavigationDropdown();
                }}
                class="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-red-400 transition-colors duration-150 hover:bg-red-500/10"
              >
                <LogOut class="w-4 h-4 stroke-[1.75] text-red-400/80 group-hover:text-red-300" />
                <span class="text-[13px] font-medium tracking-tight">Logout</span>
              </button>
            </div>
          </div>
        {/if}
      </div>
    {/if}

    {#if !$store.isAuthed}
      <button
        type="button"
        on:click={toggleModal}
        class="nav-pill group flex items-center gap-2 h-9 px-4 rounded-full bg-agent-purple text-white text-[13px] font-semibold tracking-tight shadow-agent-cta transition-all duration-200 hover:bg-[#5a37b5] active:scale-[0.98]"
      >
        <LogIn class="w-3.5 h-3.5 stroke-[1.75]" />
        <span>Connect</span>
      </button>
    {/if}
  </div>
</div>

<div class={modalIsOpen ? "" : "hidden"}>
  <LoginModal {toggleModal} />
</div>

<style>
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-8px) scale(0.98);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .animate-slideDown {
    animation: slideDown 0.18s ease-out;
  }

  @media (max-width: 640px) {
    .nav-pill {
      min-height: 36px;
    }
  }
</style>
