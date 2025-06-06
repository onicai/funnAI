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
    color: #1f2937; /* neutral-800 for light theme */
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  
  .panel.animated {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  /* Solid panel base */
  .panel.solid {
    background-color: #ffffff; /* white for light theme */
    border: 1px solid #d1d5db; /* neutral-300 for light theme */
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
  
  /* Dark theme for solid panels */
  :global(.dark) .panel.solid {
    background-color: #111827; /* neutral-900 for dark theme */
    border-color: #374151; /* neutral-700 for dark theme */
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    color: #f9fafb; /* neutral-50 for dark theme */
  }
  
  /* Main solid panel */
  .panel.solid.main {
    border-color: #d1d5db; /* neutral-300 for light theme */
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
  
  /* Dark theme for main solid panels */
  :global(.dark) .panel.solid.main {
    border-color: #374151; /* neutral-700 for dark theme */
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
  
  /* Sidebar panel */
  .panel.solid.sidebar-panel,
  .panel.solid.main.sidebar-panel {
    border-color: rgba(209, 213, 219, 0.8); /* neutral-300 @ 80% for light theme */
    border-width: 1px;
  }
  
  /* Dark theme for sidebar panels */
  :global(.dark) .panel.solid.sidebar-panel,
  :global(.dark) .panel.solid.main.sidebar-panel {
    border-color: rgba(55, 65, 81, 0.8); /* neutral-700 @ 80% for dark theme */
  }
  
  /* Transparent panel */
  .panel.transparent {
    background-color: rgba(255, 255, 255, 0.95); /* white @ 95% for light theme */
    backdrop-filter: blur(12px);
    border: 1px solid rgba(209, 213, 219, 0.5); /* neutral-300 @ 50% for light theme */
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  }
  
  /* Dark theme for transparent panels */
  :global(.dark) .panel.transparent {
    background-color: rgba(17, 24, 39, 0.85); /* neutral-900 @ 85% for dark theme */
    border-color: rgba(55, 65, 81, 0.5); /* neutral-700 @ 50% for dark theme */
    color: #f9fafb; /* neutral-50 for dark theme */
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
    border-color: rgba(156, 163, 175, 0.7); /* neutral-400 @ 70% for light theme */
    background-color: rgba(255, 255, 255, 0.98); /* white @ 98% for light theme */
  }
  
  /* Dark theme for transparent hover states */
  :global(.dark) .panel.transparent:hover,
  :global(.dark) .panel.transparent:has(.panel:hover) {
    border-color: rgba(55, 65, 81, 0.7); /* neutral-700 @ 70% for dark theme */
    background-color: rgba(17, 24, 39, 0.9); /* neutral-900 @ 90% for dark theme */
  }
  
  /* Solid edge glow - light theme */
  .panel.solid:not(.rounded-none)::before {
    content: '';
    position: absolute;
    inset: 0;
    padding: 1px;
    background: linear-gradient(to bottom right,
      rgba(156, 163, 175, 0.04),  /* neutral-400 @ 4% for light theme */
      rgba(156, 163, 175, 0.02),  /* neutral-400 @ 2% for light theme */
      rgba(156, 163, 175, 0.01)   /* neutral-400 @ 1% for light theme */
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    border-radius: inherit;
  }
  
  /* Dark theme for solid edge glow */
  :global(.dark) .panel.solid:not(.rounded-none)::before {
    background: linear-gradient(to bottom right,
      rgba(31, 41, 55, 0.04),  /* neutral-800 @ 4% for dark theme */
      rgba(31, 41, 55, 0.02),  /* neutral-800 @ 2% for dark theme */
      rgba(31, 41, 55, 0.01)   /* neutral-800 @ 1% for dark theme */
    );
  }
  
  /* Solid inner glow - light theme */
  .panel.solid::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(
      circle,
      rgba(156, 163, 175, 0.01),  /* neutral-400 @ 1% for light theme */
      transparent
    );
    pointer-events: none;
  }
  
  /* Dark theme for solid inner glow */
  :global(.dark) .panel.solid::after {
    background: radial-gradient(
      circle,
      rgba(31, 41, 55, 0.01),  /* neutral-800 @ 1% for dark theme */
      transparent
    );
  }
  
  /* Swap panel - light theme */
  .panel.transparent.swap-panel::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(to right bottom, rgba(0, 0, 0, 0.03), transparent); /* subtle dark gradient for light theme */
    pointer-events: none;
  }
  
  /* Dark theme for swap panel */
  :global(.dark) .panel.transparent.swap-panel::before {
    background: linear-gradient(to right bottom, rgba(255, 255, 255, 0.03), transparent); /* subtle light gradient for dark theme */
  }
</style>  