<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { elasticOut } from 'svelte/easing';
  import { CELEBRATION_DURATION } from '../../helpers/config/topUpConfig';

  export let isVisible: boolean = false;
  export let amount: string = "0";
  export let token: string = "ICP";

  const dispatch = createEventDispatcher();

  let confettiContainer: HTMLDivElement;
  let mounted = false;
  let confettiInterval: ReturnType<typeof setInterval> | null = null;

  // Confetti animation variables
  let confettiPieces: Array<{
    id: number;
    x: number;
    y: number;
    rotation: number;
    color: string;
    scale: number;
    velocity: { x: number; y: number };
    rotationSpeed: number;
  }> = [];

  // Party colors for confetti
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
    '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
  ];

  function createConfetti(isInitial = false) {
    if (isInitial) {
      confettiPieces = [];
    }
    
    const newPieces = [];
    const pieceCount = isInitial ? 100 : 60; // Initial burst is bigger
    const baseId = confettiPieces.length;
    
    for (let i = 0; i < pieceCount; i++) {
      newPieces.push({
        id: baseId + i,
        x: Math.random() * window.innerWidth,
        y: -20,
        rotation: Math.random() * 360,
        color: colors[Math.floor(Math.random() * colors.length)],
        scale: 0.5 + Math.random() * 0.8,
        velocity: {
          x: (Math.random() - 0.5) * 4,
          y: Math.random() * 3 + 2
        },
        rotationSpeed: (Math.random() - 0.5) * 6
      });
    }
    
    confettiPieces = [...confettiPieces, ...newPieces];
  }

  function animateConfetti() {
    if (!isVisible) return;
    
    confettiPieces = confettiPieces.map(piece => ({
      ...piece,
      x: piece.x + piece.velocity.x,
      y: piece.y + piece.velocity.y,
      rotation: piece.rotation + piece.rotationSpeed,
      velocity: {
        x: piece.velocity.x * 0.98, // slight deceleration
        y: piece.velocity.y + 0.1 // gravity
      }
    })).filter(piece => piece.y < window.innerHeight + 50);

    if (confettiPieces.length > 0) {
      requestAnimationFrame(animateConfetti);
    }
  }

  function startCelebration() {
    if (!mounted) return;
    
    // Initial confetti burst
    createConfetti(true);
    animateConfetti();
    
    // Set up recurring confetti bursts every 8-10 seconds
    confettiInterval = setInterval(() => {
      if (isVisible) {
        createConfetti(false);
        // Restart animation if it stopped
        if (confettiPieces.length > 0) {
          animateConfetti();
        }
      }
    }, 9000); // 9 seconds
    
    // Auto-hide after configured duration
    setTimeout(() => {
      stopCelebration();
    }, CELEBRATION_DURATION);
  }

  function stopCelebration() {
    if (confettiInterval) {
      clearInterval(confettiInterval);
      confettiInterval = null;
    }
    isVisible = false;
    dispatch('close');
  }

  $: if (isVisible && mounted) {
    startCelebration();
  }

  onMount(() => {
    mounted = true;
  });
</script>

{#if isVisible}
  <!-- Full-screen overlay -->
  <div 
    class="fixed inset-0 z-200000 bg-black/70 flex items-center justify-center"
    transition:fade={{ duration: 300 }}
    on:click={stopCelebration}
    on:keydown={(e) => { if (e.key === 'Escape') { stopCelebration(); } }}
    role="button"
    tabindex="0"
  >
    <!-- Confetti container -->
    <div bind:this={confettiContainer} class="absolute inset-0 pointer-events-none overflow-hidden">
      {#each confettiPieces as piece (piece.id)}
        <div
          class="absolute w-2 h-2 rounded-xs opacity-70"
          style="
            left: {piece.x}px;
            top: {piece.y}px;
            background-color: {piece.color};
            transform: rotate({piece.rotation}deg) scale({piece.scale});
            transition: none;
          "
        />
      {/each}
    </div>

    <!-- Main celebration content -->
    <div 
      class="relative z-10 text-center p-8 max-w-md mx-4 rounded-2xl bg-agent-elevated border border-white/10 shadow-[0_0_60px_rgba(139,124,246,0.15)]"
      transition:scale={{ duration: 600, easing: elasticOut }}
      on:click|stopPropagation
      on:keydown|stopPropagation
      role="dialog"
      aria-label="Maximum top-up celebration"
    >
      <!-- Soft purple glow -->
      <div class="pointer-events-none absolute inset-0 rounded-2xl overflow-hidden">
        <div class="absolute -top-16 left-1/2 -translate-x-1/2 w-48 h-48 bg-agent-purple/20 rounded-full blur-3xl"></div>
      </div>

      <div class="relative">
        <!-- Party Parrot -->
        <div class="mb-6 flex justify-center">
          <div class="relative">
            <img 
              src="/party-parrot.gif" 
              alt="Party Parrot" 
              class="w-28 h-28 sm:w-32 sm:h-32 object-contain celebration-mascot"
            />
            <div class="absolute inset-0 bg-agent-purple/15 rounded-full blur-xl"></div>
          </div>
        </div>

        <!-- Celebration text -->
        <div class="text-gray-100">
          <h1 class="text-2xl sm:text-3xl font-semibold tracking-tight text-white mb-3">
            Maximum Top-Up
          </h1>
          <p class="text-base sm:text-lg text-gray-300 mb-2">
            You topped up the maximum amount
          </p>
          <p class="text-lg sm:text-xl font-semibold text-agent-purple">
            {amount} {token}
          </p>
          <p class="text-sm text-gray-400 mt-4">
            Top-tier mAIner status unlocked
          </p>
        </div>

        <button
          type="button"
          class="mt-6 agent-btn-ghost"
          on:click={stopCelebration}
        >
          <span>Continue</span>
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes soft-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
  }

  .celebration-mascot {
    animation: soft-float 2.4s ease-in-out infinite;
    filter: drop-shadow(0 0 18px rgba(139, 124, 246, 0.35));
  }

  @media (max-width: 640px) {
    h1 {
      font-size: 1.5rem;
    }
  }
</style>
