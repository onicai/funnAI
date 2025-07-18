<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  // Props
  export let targetDate: Date | string;
  export let format: 'detailed' | 'compact' | 'simple' = 'detailed';
  export let showLabels: boolean = true;
  export let className: string = '';
  export let onComplete: (() => void) | null = null;

  // State
  let timeRemaining = 0;
  let isCompleted = false;
  let timer: NodeJS.Timeout | null = null;

  // Time units
  let days = 0;
  let hours = 0;
  let minutes = 0;
  let seconds = 0;

  // Convert target date to Date object if it's a string
  $: target = typeof targetDate === 'string' ? new Date(targetDate + 'T23:59:59') : targetDate;

  // Calculate time remaining
  function calculateTimeRemaining() {
    const now = new Date().getTime();
    const targetTime = target.getTime();
    timeRemaining = Math.max(0, targetTime - now);

    if (timeRemaining <= 0) {
      isCompleted = true;
      if (onComplete) {
        onComplete();
      }
      stopTimer();
      return;
    }

    // Calculate time units
    days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
    hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
    seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
  }

  // Format time for different display modes
  function formatTime(): string {
    if (isCompleted) {
      return 'Completed!';
    }

    switch (format) {
      case 'compact':
        if (days > 0) return `${days}d ${hours}h ${minutes}m`;
        if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
        return `${minutes}m ${seconds}s`;
        
      case 'simple':
        if (days > 0) return `${days} days`;
        if (hours > 0) return `${hours} hours`;
        return `${minutes} minutes`;
        
      case 'detailed':
      default:
        const parts = [];
        if (days > 0) parts.push(`${days} day${days !== 1 ? 's' : ''}`);
        if (hours > 0) parts.push(`${hours} hour${hours !== 1 ? 's' : ''}`);
        if (minutes > 0) parts.push(`${minutes} minute${minutes !== 1 ? 's' : ''}`);
        if (seconds > 0) parts.push(`${seconds} second${seconds !== 1 ? 's' : ''}`);
        
        if (parts.length === 0) return 'Less than a minute';
        if (parts.length === 1) return parts[0];
        return parts.slice(0, -1).join(', ') + ' and ' + parts[parts.length - 1];
    }
  }

  // Start the countdown timer
  function startTimer() {
    calculateTimeRemaining();
    timer = setInterval(calculateTimeRemaining, 1000);
  }

  // Stop the countdown timer
  function stopTimer() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  // Lifecycle
  onMount(() => {
    startTimer();
  });

  onDestroy(() => {
    stopTimer();
  });

  // Reactive formatting
  $: formattedTime = formatTime();
</script>

<div class="countdown {className}" class:completed={isCompleted}>
  {#if format === 'detailed' && !isCompleted}
    <div class="countdown-detailed">
      {#if days > 0}
        <div class="time-unit">
          <span class="time-value">{days}</span>
          {#if showLabels}<span class="time-label">day{days !== 1 ? 's' : ''}</span>{/if}
        </div>
      {/if}
      
      {#if hours > 0 || days > 0}
        <div class="time-unit">
          <span class="time-value">{hours}</span>
          {#if showLabels}<span class="time-label">hour{hours !== 1 ? 's' : ''}</span>{/if}
        </div>
      {/if}
      
      {#if minutes > 0 || hours > 0 || days > 0}
        <div class="time-unit">
          <span class="time-value">{minutes}</span>
          {#if showLabels}<span class="time-label">minute{minutes !== 1 ? 's' : ''}</span>{/if}
        </div>
      {/if}
      
      <div class="time-unit">
        <span class="time-value">{seconds}</span>
        {#if showLabels}<span class="time-label">second{seconds !== 1 ? 's' : ''}</span>{/if}
      </div>
    </div>
  {:else}
    <span class="countdown-text" class:completed-text={isCompleted}>
      {formattedTime}
    </span>
  {/if}
</div>

<style>
  .countdown {
    display: flex;
    align-items: center;
    font-family: 'ui-monospace', 'SFMono-Regular', 'Consolas', monospace;
  }

  .countdown-detailed {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
  }

  .time-unit {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 3rem;
  }

  .time-value {
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1;
  }

  .time-label {
    font-size: 0.75rem;
    font-weight: 500;
    opacity: 0.7;
    margin-top: 0.125rem;
  }

  .countdown-text {
    font-weight: 600;
  }

  .completed .time-value,
  .completed-text {
    color: #059669; /* emerald-600 */
  }

  .completed .time-label {
    color: #065f46; /* emerald-800 */
    opacity: 0.8;
  }

  /* Dark mode support */
  :global(.dark) .completed .time-value,
  :global(.dark) .completed-text {
    color: #10b981; /* emerald-500 */
  }

  :global(.dark) .completed .time-label {
    color: #6ee7b7; /* emerald-300 */
  }
</style> 