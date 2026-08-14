<script lang="ts">
  import { onMount } from 'svelte';
  import { store } from "../../stores/store";
  import { link } from 'svelte-spa-router';
  import LoginModal from '../login/LoginModal.svelte';
  import {
    ShoppingCart,
    ChevronDown,
    LogOut,
    User,
  } from 'lucide-svelte';

  let accountDropdownOpen = false;
  let modalIsOpen = false;

  const toggleModal = () => {
    modalIsOpen = !modalIsOpen;
  };

  const toggleAccountDropdown = (event: Event) => {
    event.stopPropagation();
    accountDropdownOpen = !accountDropdownOpen;
  };

  const closeAccountDropdown = () => {
    accountDropdownOpen = false;
  };

  async function disconnect() {
    await store.disconnect();
  }

  $: principalShort = $store.principal
    ? `${$store.principal.toText().slice(0, 5)}…${$store.principal.toText().slice(-3)}`
    : 'Account';

  onMount(() => {
    document.body.addEventListener('click', function (event) {
      const target = event.target as Node;
      const dropdown = document.getElementById('accountDropdown');
      const button = document.getElementById('accountDropdownButton');

      if (
        dropdown &&
        button &&
        !dropdown.contains(target) &&
        !button.contains(target)
      ) {
        closeAccountDropdown();
      }
    });
  });
</script>

<div class="flex items-center justify-center w-full relative font-sans">
  <div class="ml-auto flex items-center gap-2.5">
    <a
      use:link
      href="/marketplace"
      class="agent-btn-primary no-underline"
    >
      <ShoppingCart class="w-3.5 h-3.5 stroke-[1.75]" />
      <span>Buy mAIner</span>
    </a>

    {#if $store.isAuthed}
      <div class="relative z-[80]">
        <button
          id="accountDropdownButton"
          type="button"
          aria-haspopup="menu"
          aria-expanded={accountDropdownOpen}
          on:click={toggleAccountDropdown}
          class="agent-btn-ghost sm:min-w-[9.5rem]"
        >
          <User class="w-3.5 h-3.5 stroke-[1.75] text-gray-400 shrink-0" />
          <span class="hidden sm:inline w-[5.5rem] truncate text-left">{principalShort}</span>
          <ChevronDown
            class="w-3.5 h-3.5 stroke-[1.75] text-gray-500 shrink-0 transition-transform duration-200 {accountDropdownOpen ? 'rotate-180' : ''}"
          />
        </button>

        {#if accountDropdownOpen}
          <button
            type="button"
            class="fixed inset-0 z-[90] cursor-default bg-black/20"
            aria-label="Close account menu"
            on:click={closeAccountDropdown}
          ></button>

          <div
            id="accountDropdown"
            role="menu"
            class="absolute right-0 top-full mt-2 w-52 z-[100] overflow-hidden rounded-2xl border border-white/10 bg-[#15141B] shadow-[0_20px_50px_rgba(0,0,0,0.55)] animate-slideDown"
          >
            <div class="border-b border-white/[0.06] px-4 py-3">
              <p class="text-[10px] font-medium uppercase tracking-[0.14em] text-gray-500">Account</p>
              {#if $store.principal}
                <p class="mt-1.5 font-mono text-[11px] text-gray-400 truncate" title={$store.principal.toText()}>
                  {$store.principal.toText()}
                </p>
              {/if}
            </div>

            <div class="p-1.5">
              <button
                type="button"
                role="menuitem"
                on:click={() => {
                  disconnect();
                  closeAccountDropdown();
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
        class="inline-flex items-center justify-center gap-2 h-9 px-4 rounded-xl border border-white/12 bg-white/[0.04] text-[13px] font-medium tracking-tight text-white shadow-[0_1px_0_0_rgba(255,255,255,0.06)_inset] transition-colors hover:border-white/20 hover:bg-white/[0.07]"
      >
        <span>Connect</span>
      </button>
    {/if}
  </div>
</div>

{#if modalIsOpen}
  <LoginModal {toggleModal} />
{/if}

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
</style>
