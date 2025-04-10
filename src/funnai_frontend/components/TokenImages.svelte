<script lang="ts">
  import { tooltip as tooltipAction } from "../helpers/utils/tooltip";

  // Props defined using export let syntax
  export let tokens: FE.Token[] = [];
  export let size: number = 48;
  export let containerClass: string = "";
  export let imageWrapperClass: string = "";
  export let overlap: boolean = false;
  export let maxDisplay: number = 5;
  export let countBgColor: string = "bg-kong-primary";
  export let countTextColor: string = "text-white";
  export let tooltip: { text: string; direction: "top" | "bottom" | "left" | "right" } = { text: "", direction: "top" };
  export let showSymbolFallback: boolean = true;

  const DEFAULT_IMAGE = "/tokens/not_verified.webp";

  // Filter out invalid tokens and memoize result
  $: validTokens = tokens.filter((token): token is FE.Token => {
    return token && typeof token === "object";
  });

  // Calculate displayed tokens and remaining count
  $: displayedTokens = validTokens.slice(0, maxDisplay);
  $: remainingCount = validTokens.length > maxDisplay ? validTokens.length - maxDisplay : 0;

  // Calculate tooltip content with total count info when needed
  $: tooltipText = tooltip.text || "";
  $: tooltipContent = remainingCount > 0
    ? `${tooltipText}${tooltipText ? ' • ' : ''}${validTokens.length} tokens total`
    : tooltipText;

  // Track loading state for each token
  let imageLoadingStatus: Record<string, boolean> = {};

  // Handle image error with proper typing
  function handleImageError(e, token: FE.Token) {
    console.error(`Failed to load image: ${e.currentTarget.src}`);
    imageLoadingStatus[token.canister_id || token.symbol] = false;
  }

  // Handle image loading success
  function handleImageLoad(token: FE.Token) {
    imageLoadingStatus[token.canister_id || token.symbol] = true;
  }

  // Helper to get token alt text
  function getTokenAlt(token: FE.Token): string {
    return token.symbol ?? token.name ?? "Unknown Token";
  }

  // Helper to get token symbol for fallback
  function getTokenSymbol(token: FE.Token): string {
    return token.symbol || '?';
  }

  // Check if image exists for a token
  function hasValidImage(token: FE.Token): boolean {
    return !!(token.logo_url || DEFAULT_IMAGE);
  }
</script>

<div
  use:tooltipAction={{ ...tooltip, text: tooltipContent }}
  class="flex items-center {containerClass} p-0 m-0 group"
  style="margin-right: {overlap ? '10px' : '0'}"
>
  {#each displayedTokens as token, index}
    <div
      style="height: {size}px; width: {size}px; z-index: {displayedTokens.length - index}; transform: translateX(0); transition: transform 0.15s ease-in-out;"
      class="flex items-center rounded-full {imageWrapperClass} {overlap
        ? `mr-[-${Math.floor(size * 0.3)}px]`
        : ''} relative group-hover:hover:translate-y-[-2px]"
    >
      {#if hasValidImage(token)}
        <img
          class="w-full h-full rounded-full bg-transparent ring-2 ring-kong-bg-dark ring-opacity-40"
          src={token?.logo_url || DEFAULT_IMAGE}
          alt={getTokenAlt(token)}
          loading="eager"
          on:error={(e) => handleImageError(e, token)}
          on:load={() => handleImageLoad(token)}
        />
      {:else if showSymbolFallback}
        <div class="w-full h-full rounded-full bg-kong-text-primary/10 flex items-center justify-center ring-2 ring-kong-bg-dark ring-opacity-40">
          <span
            class="font-bold text-kong-primary truncate max-w-[80%] text-center"
            style="font-size: min(calc({size}px * 0.3), .75rem);"
          >
            {getTokenSymbol(token)}
          </span>
        </div>
      {:else}
        <img
          class="w-full h-full rounded-full bg-transparent ring-2 ring-kong-bg-dark ring-opacity-40"
          src={DEFAULT_IMAGE}
          alt={getTokenAlt(token)}
          loading="eager"
        />
      {/if}
      <div class="absolute inset-0 rounded-full ring-1 ring-white ring-opacity-10"></div>
    </div>
  {/each}

  {#if remainingCount > 0}
    <div
      style="height: {size}px; width: {size}px; z-index: 0;"
      class="flex items-center justify-center rounded-full {countBgColor} {overlap ? `mr-[-${Math.floor(size * 0.3)}px]` : ''} relative border border-kong-border shadow-md group-hover:hover:translate-y-[-2px] transition-transform duration-150"
    >
      <span class="text-[.625rem] font-bold {countTextColor}">+{remainingCount}</span>
    </div>
  {/if}
</div>