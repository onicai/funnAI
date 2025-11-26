<script lang="ts">
  export let isVisible = true;
  export let title = "";
  export let subtitle = "";
  export let items: { icon?: string; text: string }[] = [];
  export let variant: "info" | "warning" | "success" | "announcement" = "info";
  export let onClose: (() => void) | undefined = undefined;
  
  const variantStyles = {
    info: "bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-500/10 dark:to-purple-500/10 border-blue-400 dark:border-blue-500/30",
    warning: "bg-gradient-to-r from-yellow-100 to-orange-100 dark:from-yellow-500/10 dark:to-orange-500/10 border-yellow-400 dark:border-yellow-500/30",
    success: "bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-500/10 dark:to-emerald-500/10 border-green-400 dark:border-green-500/30",
    announcement: "bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-500/10 dark:to-purple-500/10 border-pink-400 dark:border-pink-500/30"
  };
  
  const iconStyles = {
    info: "text-blue-600 dark:text-blue-400",
    warning: "text-yellow-600 dark:text-yellow-400",
    success: "text-green-600 dark:text-green-400",
    announcement: "text-pink-600 dark:text-pink-400"
  };
  
  function handleClose() {
    if (onClose) {
      onClose();
    }
  }
</script>

{#if isVisible}
  <div class="announcement-panel {variantStyles[variant]} border rounded-lg p-6 mb-6 backdrop-blur-sm relative">
    <!-- Close Button -->
    {#if onClose}
      <button
        on:click={handleClose}
        class="absolute top-3 right-3 text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors p-1 rounded-full hover:bg-gray-200/50 dark:hover:bg-white/10"
        aria-label="Close announcement"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    {/if}
    
    <div class="flex items-start gap-4">
      <!-- Icon/Visual Element -->
      <div class="flex-shrink-0">
        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-pink-500 to-purple-600 flex items-center justify-center text-2xl animate-pulse">
          🦜
        </div>
      </div>
      
      <!-- Content -->
      <div class="flex-1 pr-8">
        {#if title}
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2 {iconStyles[variant]}">{title}</h3>
        {/if}
        
        {#if subtitle}
          <p class="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">{subtitle}</p>
        {/if}
        
        {#if items.length > 0}
          <ul class="space-y-3">
            {#each items as item}
              <li class="flex items-start gap-3">
                {#if item.icon}
                  <span class="text-xl flex-shrink-0">{item.icon}</span>
                {/if}
                <span class="text-gray-800 dark:text-gray-200 leading-relaxed">{item.text}</span>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .announcement-panel {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
  }
  
  :global(.dark) .announcement-panel {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }
  
  .announcement-panel:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  }
  
  :global(.dark) .announcement-panel:hover {
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
  }
  
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.8;
      transform: scale(1.05);
    }
  }
  
  .animate-pulse {
    animation: pulse 2s ease-in-out infinite;
  }
</style>

