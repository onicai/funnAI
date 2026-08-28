<script lang="ts">
  /**
   * Badge component for displaying status indicators, tags, or labels
   * 
   * Usage:
   * <Badge>Default</Badge>
   * <Badge variant="blue">Blue</Badge>
   * <Badge variant="green">Green</Badge>
   * <Badge variant="red">Red</Badge>
   * <Badge variant="yellow">Yellow</Badge>
   * <Badge variant="purple">Purple</Badge>
   * <Badge variant="gray">Gray</Badge>
   * <Badge icon="🐋">Whale</Badge>
   * <Badge tooltip="This is a tooltip">With tooltip</Badge>
   */
  import { tooltip } from "../helpers/utils/tooltip";

  export let variant: "blue" | "green" | "red" | "yellow" | "purple" | "gray" = "blue";
  export let size: "xs" | "sm" | "md" | "lg" = "sm";
  export let icon: string | null = null;
  export let pill: boolean = true;
  export let tooltipText: string | null = null;
  export let tooltipDirection: "top" | "bottom" | "left" | "right" = "top";
  export let className: string = "";

  // Computed styles based on variant
  const variantStyles = {
    blue: "bg-blue-900/30 text-blue-300",
    green: "bg-green-900/30 text-green-300",
    red: "bg-red-900/30 text-red-300",
    yellow: "bg-yellow-900/30 text-yellow-300",
    purple: "bg-purple-900/30 text-purple-300",
    gray: "bg-gray-800 text-gray-300"
  };

  // Size styles
  const sizeStyles = {
    xs: "text-xs px-1 py-0.5 px-2",
    sm: "text-xs px-1.5 py-0.5 px-2",
    md: "text-sm px-2 py-1 px-2",
    lg: "text-sm px-2.5 py-1.5 px-2"
  };

  // Computed classes
  $: badgeClasses = `
    inline-flex items-center gap-1 
    ${variantStyles[variant] || variantStyles.blue} 
    ${sizeStyles[size] || sizeStyles.sm} 
    ${pill ? 'rounded-full' : 'rounded-sm'} 
    font-medium
    ${tooltipText ? 'cursor-help' : ''}
    ${className}
  `;
</script>

<span 
  class={badgeClasses}
  use:tooltip={tooltipText ? { text: tooltipText, direction: tooltipDirection } : undefined}
>
  {#if icon}<span class="inline-block">{icon}</span>{/if}
  <slot />
</span>