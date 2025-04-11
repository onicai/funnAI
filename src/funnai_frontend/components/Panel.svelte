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
</script>

{#if transition === 'slide'}
  <div
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    on:click
    on:keydown
    transition:slide={params}
    >
    <slot>{content}</slot>
  </div>
{:else if transition === 'fade'}
  <div 
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    transition:fade={params}
    on:click
    on:keydown
  >
    <slot>{content}</slot>
  </div>
{:else}
  <div 
    class="panel {unpadded ? '' : 'p-4'} {variant} {type} {className} {roundnessClass} {animated ? 'animated' : ''} {isSwapPanel ? 'swap-panel' : ''} {isSidebar ? 'sidebar-panel' : ''} {interactiveClass}"
    style="width: {width}; height: {height}; z-index: {zIndex};"
    on:click
    on:keydown
  >
    <slot>{content}</slot>
  </div>
{/if}

<style lang="postcss" scoped>
  .panel {
    position: relative;
    color: #1f2937; /* neutral-800 */
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  
  .panel.animated {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  /* Solid panel base */
  .panel.solid {
    background-color: #111827; /* neutral-900 */
    border: 1px solid #374151; /* neutral-700 */
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  }
  
  /* Main solid panel */
  .panel.solid.main {
    border-color: #374151;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
  
  /* Sidebar panel */
  .panel.solid.sidebar-panel,
  .panel.solid.main.sidebar-panel {
    border-color: rgba(55, 65, 81, 0.8); /* neutral-700 @ 80% */
    border-width: 1px;
  }
  
  /* Transparent panel */
  .panel.transparent {
    background-color: rgba(17, 24, 39, 0.85); /* neutral-900 @ 85% */
    backdrop-filter: blur(12px);
    border: 1px solid rgba(55, 65, 81, 0.5); /* neutral-700 @ 50% */
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  /* Interactive states */
  .panel.interactive {
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .panel.interactive:hover {
    transform: scale(1.02);
  }
  
  .panel.interactive.solid:hover,
  .panel.interactive.transparent:hover {
    border-color: rgba(59, 130, 246, 0.6); /* blue-500 @ 60% */
  }
  
  .panel.interactive.active {
    border-color: #3b82f6; /* blue-500 */
    background-color: #2563eb; /* blue-600 */
    color: white;
  }
  
  .panel.transparent:hover,
  .panel.transparent:has(.panel:hover) {
    border-color: rgba(55, 65, 81, 0.7); /* neutral-700 @ 70% */
    background-color: rgba(17, 24, 39, 0.9); /* neutral-900 @ 90% */
  }
  
  /* Solid edge glow */
  .panel.solid:not(.rounded-none)::before {
    content: '';
    position: absolute;
    inset: 0;
    padding: 1px;
    background: linear-gradient(to bottom right,
      rgba(31, 41, 55, 0.04),  /* neutral-800 @ 4% */
      rgba(31, 41, 55, 0.02),  /* neutral-800 @ 2% */
      rgba(31, 41, 55, 0.01)   /* neutral-800 @ 1% */
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    border-radius: inherit;
  }
  
  /* Solid inner glow */
  .panel.solid::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
      circle,
      rgba(31, 41, 55, 0.01),  /* neutral-800 @ 1% */
      transparent
    );
    pointer-events: none;
  }
  
  /* Swap panel */
  .panel.transparent.swap-panel::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(to right bottom, rgba(255, 255, 255, 0.03), transparent);
    pointer-events: none;
  }
</style>  