<script lang="ts">
  export let isVisible = true;
  export let title = "";
  export let subtitle = "";
  export let items: { icon?: string; text: string }[] = [];
  export let variant: "info" | "warning" | "success" | "announcement" = "info";
  export let onClose: (() => void) | undefined = undefined;
  
  const variantStyles = {
    info: "border-white/10 bg-white/[0.03]",
    warning: "border-amber-500/30 bg-amber-500/5",
    success: "border-emerald-500/30 bg-emerald-500/5",
    announcement: "border-agent-purple/30 bg-agent-purple/5"
  };
  
  const iconStyles = {
    info: "text-agent-purple",
    warning: "text-amber-400",
    success: "text-emerald-400",
    announcement: "text-agent-purple"
  };

  const iconBgStyles = {
    info: "border-white/10 bg-white/[0.03]",
    warning: "border-amber-500/30 bg-amber-500/10",
    success: "border-emerald-500/30 bg-emerald-500/10",
    announcement: "border-agent-purple/20 bg-agent-purple/15"
  };
  
  function handleClose() {
    if (onClose) {
      onClose();
    }
  }
</script>

{#if isVisible}
  <div class="agent-card {variantStyles[variant]} p-5 sm:p-6 mb-6 relative">
    <!-- Close Button -->
    {#if onClose}
      <button
        on:click={handleClose}
        class="absolute top-3 right-3 text-gray-500 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/[0.06]"
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
        <div class="w-10 h-10 rounded-xl border {iconBgStyles[variant]} flex items-center justify-center">
          {#if variant === "warning"}
            <svg class="w-5 h-5 {iconStyles[variant]}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          {:else if variant === "success"}
            <svg class="w-5 h-5 {iconStyles[variant]}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          {:else if variant === "announcement"}
            <svg class="w-5 h-5 {iconStyles[variant]}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
            </svg>
          {:else}
            <svg class="w-5 h-5 {iconStyles[variant]}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          {/if}
        </div>
      </div>
      
      <!-- Content -->
      <div class="flex-1 {onClose ? 'pr-8' : ''}">
        {#if title}
          <h3 class="text-lg font-semibold text-white mb-2">{title}</h3>
        {/if}
        
        {#if subtitle}
          <p class="text-gray-400 mb-4 leading-relaxed text-sm">{subtitle}</p>
        {/if}
        
        {#if items.length > 0}
          <ul class="space-y-3">
            {#each items as item}
              <li class="flex items-start gap-3">
                {#if item.icon}
                  <span class="text-sm flex-shrink-0 text-gray-500">{item.icon}</span>
                {/if}
                <span class="text-gray-300 leading-relaxed text-sm">{item.text}</span>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  </div>
{/if}
