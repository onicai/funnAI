<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { onMount } from "svelte";
  import { formatFunnaiAmount } from "../../helpers/utils/numberFormatUtils";
  
  export let feedItem: {
    id: string;
    timestamp: number;
    type: "challenge" | "response" | "score" | "winner" | "participation";
    mainerName: string;
    content: {
      challenge?: string;
      response?: string;
      score?: number;
      placement?: string;
      reward?: string;
    };
  };

  let showShareMenu = false;
  const dispatch = createEventDispatcher();
  let parentListItem: HTMLElement | null = null;
  let containerElement: HTMLElement | null = null;

  function generateShareText(): string {
    const baseUrl = window.location.origin;
    
    switch (feedItem.type) {
      case "challenge":
        return `🎯 New challenge for mAIners: "${feedItem.content.challenge}" - Join the AI competition at ${baseUrl} #mAIner #AI #funnAI`;
      case "response":
        return `💭 mAIner ${feedItem.mainerName} submitted: "${feedItem.content.response}" - See AI agents compete at ${baseUrl} #mAIner #AI #funnAI`;
      case "score":
        return `📊 mAIner ${feedItem.mainerName} scored ${feedItem.content.score}/5! - Watch AI agents compete at ${baseUrl} #mAIner #AI #funnAI`;
      case "winner":
        return `🏆 ${feedItem.mainerName} achieved ${feedItem.content.placement} and earned ${formatFunnaiAmount(feedItem.content.reward || '0')} funnAI! - Join the AI competition at ${baseUrl} #mAIner #AI #funnAI #Winner`;
      case "participation":
        return `🎉 ${feedItem.mainerName} earned ${formatFunnaiAmount(feedItem.content.reward || '0')} funnAI for participating! - Join the AI competition at ${baseUrl} #mAIner #AI #funnAI #Participation`;
      default:
        return `Check out this mAIner activity at ${baseUrl} #mAIner #AI #funnAI`;
    }
  }

  function getShareUrl(platform: string): string {
    const message = generateShareText();
    const encodedMessage = encodeURIComponent(message);
    const currentUrl = window.location.origin;
    const encodedUrl = encodeURIComponent(currentUrl);

    switch (platform) {
      case "twitter":
        return `https://twitter.com/intent/tweet?text=${encodedMessage}&url=${encodedUrl}`;

      case "linkedin":
        return `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`;

      case "facebook":
        return `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedMessage}`;

      case "reddit":
        return `https://www.reddit.com/submit?url=${encodedUrl}&title=${encodedMessage}`;

      case "telegram":
        return `https://t.me/share/url?url=${encodedUrl}&text=${encodedMessage}`;

      case "whatsapp":
        return `https://wa.me/?text=${encodeURIComponent(`${message} ${currentUrl}`)}`;

      case "discord":
        /*
          Discord does not support pre-filled share text via URL parameters for the regular client.
          We simply open the app/web client and rely on our clipboard helper (see handleShare)
          to put the message on the user‛s clipboard so they can paste it quickly.
        */
        return `https://discord.com/channels/@me`;

      default:
        return "";
    }
  }

  function handleShare(platform: string) {
    const shareUrl = getShareUrl(platform);

    // For platforms like Discord where we cannot pass the text, automatically copy it.
    if (platform === "discord") {
      copyToClipboard();
    }

    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
      showShareMenu = false;
      dispatch('shared', { platform, feedItem });
    }
  }

  function copyToClipboard() {
    navigator.clipboard.writeText(generateShareText()).then(() => {
      showShareMenu = false;
      dispatch('copied', { feedItem });
    });
  }

  function toggleShareMenu() {
    showShareMenu = !showShareMenu;
  }

  onMount(() => {
    // Find the closest <li> ancestor so we can elevate its z-index when the share menu is open
    const container = containerElement as HTMLElement | null;
    if (container) {
      parentListItem = container.closest("li");
    }
  });

  $: if (parentListItem) {
    if (showShareMenu) {
      // Raise the entire list item above its siblings
      parentListItem.style.zIndex = "999997";
      parentListItem.style.position = parentListItem.style.position || "relative";
    } else {
      // Reset when menu closes
      parentListItem.style.zIndex = "";
    }
  }

  // Close menu when clicking outside (handled by backdrop click)
</script>

<!-- Capture the container element reference -->
<div bind:this={containerElement} class="share-menu-container relative">
  <button
    on:click={toggleShareMenu}
    class="relative p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 {showShareMenu ? 'pointer-events-none' : ''}"
    title="Share this activity"
    aria-label="Share this activity"
    style="z-index: 1;"
  >
    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
    </svg>
  </button>

  {#if showShareMenu}
    <!-- Portal to body to avoid overflow issues -->
    <div class="fixed inset-0" role="button" tabindex="0" on:click={() => showShareMenu = false} on:keydown={(e) => e.key === 'Escape' && (showShareMenu = false)} aria-label="Close share menu" style="z-index: 999998;"></div>
    <div 
      class="absolute right-0 top-8 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-500 rounded-lg shadow-xl py-2 min-w-[180px]" 
      on:click|stopPropagation 
      on:keydown|stopPropagation 
      style="z-index: 999999; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);"
    >
      <div class="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700 mb-1">
        Share on
      </div>
      
      <button
        on:click={() => handleShare('twitter')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-blue-400" fill="currentColor" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
        X
      </button>

      <button
        on:click={() => handleShare('linkedin')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-700 dark:hover:text-blue-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        LinkedIn
      </button>

      <button
        on:click={() => handleShare('facebook')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-700 dark:hover:text-blue-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
        Facebook
      </button>

      <button
        on:click={() => handleShare('reddit')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-orange-50 dark:hover:bg-gray-700 hover:text-orange-600 dark:hover:text-orange-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
        </svg>
        Reddit
      </button>

      <button
        on:click={() => handleShare('telegram')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.365.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
        </svg>
        Telegram
      </button>

      <button
        on:click={() => handleShare('whatsapp')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-green-50 dark:hover:bg-gray-700 hover:text-green-600 dark:hover:text-green-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
        </svg>
        WhatsApp
      </button>

      <button
        on:click={() => handleShare('discord')}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-indigo-50 dark:hover:bg-gray-700 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-[#5865F2]" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.317 4.3698a19.7913 19.7913 0 0 0-4.8851-1.5152.0741.0741 0 0 0-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.393-.4058-.8742-.6177-1.2495-.0176-.0282-.0546-.0403-.087-.0338a19.7363 19.7363 0 0 0-4.8852 1.515.062.062 0 0 0-.028.0213C.5334 9.0458-.319 13.5799.0994 18.0578c.0103.1214.0841.2293.1908.2879a19.961 19.961 0 0 0 5.993 2.99.0777.0777 0 0 0 .0842-.0277c.4616-.63.8731-1.2952 1.226-1.9942a.076.076 0 0 0-.0416-.1057 13.3862 13.3862 0 0 1-1.918-.9.077.077 0 0 1-.008-.1277c.1306-.0988.2618-.2012.382-.304.0256-.0213.0552-.0322.0868-.0281 3.9278 2.8478 8.18 2.8478 12.0614 0 .031-.0039.0614.0068.0859.0281.121.1028.2524.2053.383.304a.077.077 0 0 1-.006.1277 12.2986 12.2986 0 0 1-1.92.901.0766.0766 0 0 0-.0409.1057c.3604.698.7718 1.3623 1.225 1.9923.0172.0249.049.0359.0782.0276a19.9344 19.9344 0 0 0 6.0013-2.989.077.077 0 0 0 .1907-.2867c.5004-5.177-.8382-9.6739-3.5485-13.666a.061.061 0 0 0-.028-.0213Z"/>
        </svg>
        Discord
      </button>

      <div class="border-t border-gray-100 dark:border-gray-700 my-1"></div>

      <button
        on:click={copyToClipboard}
        class="w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-300 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
        Copy text
      </button>
    </div>
  {/if}
</div>

<style>
  .share-menu-container {
    /* Ensure the dropdown doesn't get clipped and appears above all feed content */
    position: relative;
    z-index: 1;
  }
  
  /* Ensure the dropdown menu appears above everything */
  .share-menu-container :global(.share-dropdown) {
    position: absolute !important;
    z-index: 99999 !important;
  }
</style> 