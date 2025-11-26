<script lang="ts">
  import { tooltip as tooltipAction } from "../helpers/utils/tooltip";

  // Props defined using export let syntax
  export let tokens: FE.Token[] = [];
  export let size: number = 48;
  export let containerClass: string = "";
  export let imageWrapperClass: string = "";
  export let overlap: boolean = false;
  export let maxDisplay: number = 5;
  export let countBgColor: string = "bg-blue-600";
  export let countTextColor: string = "text-white";
  export let tooltip: { text: string; direction: "top" | "bottom" | "left" | "right" } = { text: "", direction: "top" };
  export let showSymbolFallback: boolean = true;

  const DEFAULT_IMAGE = "/tokens/not_verified.webp";

  // Map specific tokens to their image paths
  function getTokenImagePath(token: FE.Token): string {
    // Map of token symbols to their image paths
    const tokenImageMap: Record<string, string> = {
      'ICP': '/icp-rounded.svg',
      'ckBTC': '/ckbtc.webp',
      'BOB': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAATlBMVEVHcEwmIh0jHxshHRkfGxYaFxMTEQ4RDwwPDQsLCQgHBgUEAwILCwr////09PPk4+LNzMu6urmmpaSOjYx5eXhiYmFLSkk1NDMgHx8AAACPjrPaAAAADXRSTlMAECI1S2GAnLfO3+z85y7WAAAABFBJREFUeNrFm8tirCAMQEFRHjI+Ac3//+id9nbTwXaSgPYsuyiHV0wYECwa1fXaWDd84qzRfadacQtS9cbBKc7orhGX0vbWw+9YraS4BqUdoBi0EtVpegsEXN/UHXrtgYpR9cbeQMaNCm3W/K0KjYYiTCuK6D2U0gs+rYUKOMXuPlRC82bfQDVsK8goDzXpSof/7rWooTpGEDBwAVYKJNLCJbgG2b6DixgaRvv3G1i4ECdp7dfHEvdffUyN+OOfXPNhUIBiHcdxmqZ5+c/6ZEs1orL0gGJ55GyApkEsQLpAADQOsQDoArF8GbSAZS4UACXOcPcJDIgJYArwJ0FCmUACEk1RCjCVC1jECuQI8NehKRXYgYYjDcAen6QP9g/GR84BRBRlANbHW5Yt7p49BA0wBHLGeUu8ITBcgZxpO+gbQQJCAM/mqbGgRwhQmBIxHDrE549GIn0RWkTspbIDgg6diO7pSQz5QMwhfvw5Z6IkqANgCa/tJw/gEztBkeTPwHLeSBrzscGHgh7wxB+i7zGyYrMm10Lxp5W+s+bAZVGIILC8CRUBG4sUT2Da4RvHwikUeuppUPj5/weOgKamIuHnKY6cKbBZHL5ZAKRogCcQ3gnsyKRAMQUWD9/ZXpITbKncsQTyIYgjq1ru0Zsg7yZ84zUUemyJpDkCebRfmJWaEYYhkMfClXtcYYXlCzzGCJ/EiV2pOlIYyHu6nCUkK6k6GIgCCOawA5aBLIBjTkyBeunxeo/AuKbD+z2eiM0eEPgygdXDF/uSG1w/AjHboeRgMBC34fxL+bNx8lInLFtge1s/BYyA4QpM8MrBWAVWaK5AgIyFPgdG9MA7npoPyEj0ElWLjikQIOegV+m9UEyBWEegIyalY20BJUiRyI+0KdgxBbrhCSweMvZsF2AKE00SyLKh32LhiCrNOo7AeZTJTk9RxamkCPy6wjZ6KG7xBxR5E+ORhSHqEhiwv9b6LYQQw0tCNh1Z+8QZMNhDqvQ4ZUxZ0UbbhJ34xGMPRnLm6OHJESZWViixB5XrL4fjMcawjidu+INKhfgKk5k84WfsAfEJILLAe7zEHtfv5O5H2nG9RBxLEJgjoGjRP9lshL6v6MLQ4n+1Oz7ZP0gphdNeL8u6xXRwf7ezQOBMwAOVAXF5hLAkfekFP1smMB7sAfiiLRTwxTcczb0CVrzSFAlMQKQtuMKRKggYccJwo4AUJ7T3CXTiFM0XmOkTwL9JFB85IysEMHfCEULYtm39Ynkyr/wdwI3IfHrmhcqbbrobuBj7x5daB0m5Vlwf34i3NMOF7bdC/KlBK1A07o7+33+93jV/+8DAyr994qEFka52/CXTOsi4+a2ThkoYKXgoBxUYOsFGaihGy9LXhkVYJUpRFtjYTtSgYyq4rvarU37vy2n1AAS8bkVtZGc84DCdFJcgEY+vnbn4/XnbaevhHKv7VtyB/Hr974ZP3Nf7f1bP/wF/hG2iM81NVQAAAABJRU5ErkJggg==',
      // Add more tokens here as needed
    };

    // Return the mapped image path if it exists, otherwise use the token's logo_url or default
    return tokenImageMap[token.symbol] || token.logo_url || DEFAULT_IMAGE;
  }

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
    return true; // We'll always try to get an image now, either mapped or default
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
          class="w-full h-full rounded-full bg-transparent ring-2 ring-gray-900/40"
          src={getTokenImagePath(token)}
          alt={getTokenAlt(token)}
          loading="eager"
          on:error={(e) => handleImageError(e, token)}
          on:load={() => handleImageLoad(token)}
        />
      {:else if showSymbolFallback}
        <div class="w-full h-full rounded-full bg-gray-500/10 flex items-center justify-center ring-2 ring-gray-900/40">
          <span
            class="font-bold text-blue-600 truncate max-w-[80%] text-center"
            style="font-size: min(calc({size}px * 0.3), .75rem);"
          >
            {getTokenSymbol(token)}
          </span>
        </div>
      {:else}
        <img
          class="w-full h-full rounded-full bg-transparent ring-2 ring-gray-900/40"
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
    class="flex items-center justify-center rounded-full {countBgColor} {overlap ? `mr-[-${Math.floor(size * 0.3)}px]` : ''} relative border border-gray-300 shadow-md group-hover:hover:translate-y-[-2px] transition-transform duration-150"
  >
    <span class="text-[.625rem] font-bold {countTextColor}">+{remainingCount}</span>
  </div>
  {/if}
  </div>