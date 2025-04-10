<!-- Panel.svelte -->
<script lang="ts">
  import { fade, slide, type TransitionConfig } from 'svelte/transition';

  // Props
  export let variant: "transparent" | "solid" = "transparent";
  export let type: "main" | "secondary" = "main";
  export let width: string = "auto";
  export let height: string = "auto";
  export let content: string = '';
  export let className: string = '';
  export let zIndex: number = 10;
  export let roundedBorders: boolean = true;
  export let roundness: 
    | "rounded-none" | "rounded-sm" | "rounded" | "rounded-md"
    | "rounded-lg" | "rounded-xl" | "rounded-2xl" | "rounded-3xl"
    | "rounded-full" | null = null;
  export let unpadded: boolean = false;
  export let animated: boolean = false;
  export let isSwapPanel: boolean = false;
  export let isSidebar: boolean = false;
  export let interactive: boolean = false;
  export let transition: 'fade' | 'slide' | null = null;
  export let transitionParams: TransitionConfig = {};
  export let children: () => any;

  // Default transition parameters
  const defaultSlideParams = { duration: 300, delay: 200, axis: 'x' };
  const defaultFadeParams = { duration: 200 };

  // State
  let themeRoundness: string = "rounded-lg";

  // Reactive values
  $: params = {
    ...(transition === 'slide' ? defaultSlideParams : defaultFadeParams),
    ...transitionParams
  };

  $: roundnessClass = !roundedBorders 
    ? 'rounded-none' 
    : roundness || themeRoundness;

  $: interactiveClass = interactive ? 'interactive' : '';
  
  // Function to render content
  function renderContent() {
    return children ? children() : () => content;
  }
</script>

{#if transition === 'slide'}
  <div 
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    transition:slide={params}
    on:click
    on:keydown
  >
    {#if children}
      <slot />
    {:else}
      {content}
    {/if}
  </div>
{:else if transition === 'fade'}
  <div 
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    transition:fade={params}
    on:click
    on:keydown
  >
    {#if children}
      <slot />
    {:else}
      {content}
    {/if}
  </div>
{:else}
  <div 
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    on:click
    on:keydown
  >
    {#if children}
      <slot />
    {:else}
      {content}
    {/if}
  </div>
{/if}

<style lang="postcss" scoped>
.panel {
  position: relative;
  color: var(--color-kong-text-primary); /* assuming this is a CSS variable */
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel.animated {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Base solid panel styling - uses theme variables */
.panel.solid {
  background-color: var(--color-kong-bg-dark);
  border: 1px solid var(--color-kong-border);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

/* Main panel styling - slightly different for primary panels */
.panel.solid.main {
  border-color: var(--color-kong-border);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* Sidebar panel specific style */
.panel.solid.sidebar-panel,
.panel.solid.main.sidebar-panel {
  border-color: rgba(var(--color-kong-border-rgb), 0.8); /* Simulating /80 */
  border-width: 1px;
}

/* Transparent panel styling */
.panel.transparent {
  background-color: rgba(var(--color-kong-bg-dark-rgb), 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(var(--color-kong-border-rgb), 0.5);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* Tailwind's shadow-sm approximation */
}

/* Interactive panel styles */
.panel.interactive {
  cursor: pointer;
  transition: all 0.2s ease;
}

.panel.interactive:hover {
  transform: scale(1.02);
}

.panel.interactive.solid:hover,
.panel.interactive.transparent:hover {
  border-color: rgba(var(--color-kong-primary-rgb), 0.6);
}

/* Active state for interactive panels */
.panel.interactive.active {
  border-color: var(--color-kong-primary);
  background-color: var(--color-kong-primary-hover);
  color: var(--color-kong-text-on-primary);
}

/* Hover effect for transparent panels */
.panel.transparent:hover,
.panel.transparent:has(.panel:hover) {
  border-color: rgba(var(--color-kong-border-rgb), 0.7);
  background-color: rgba(var(--color-kong-bg-dark-rgb), 0.9);
}

/* Premium edge highlight for solid variant - uses theme text color */
.panel.solid:not(.rounded-none)::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1px;
  background: linear-gradient(to bottom right,
    rgba(var(--color-kong-text-primary-rgb), 0.04),
    rgba(var(--color-kong-text-primary-rgb), 0.02),
    rgba(var(--color-kong-text-primary-rgb), 0.01)
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  border-radius: inherit;
}

/* Inner glow effect - uses theme text color */
.panel.solid::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle,
    rgba(var(--color-kong-text-primary-rgb), 0.01),
    transparent
  );
  pointer-events: none;
}

/* Special styling for swap panels */
.panel.transparent.swap-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(to right bottom, rgba(255, 255, 255, 0.03), transparent);
  pointer-events: none;
}
</style>