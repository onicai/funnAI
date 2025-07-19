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
    class="fixed inset-0 z-[200000] bg-black/20 backdrop-blur-sm flex items-center justify-center"
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
          class="absolute w-3 h-3 rounded-sm opacity-90"
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
      class="relative z-10 text-center p-8 max-w-md mx-4"
      transition:scale={{ duration: 600, easing: elasticOut }}
    >
      <!-- Party Parrot -->
      <div class="mb-6 flex justify-center">
        <div class="relative">
          <img 
            src="/party-parrot.gif" 
            alt="Party Parrot" 
            class="w-32 h-32 sm:w-40 sm:h-40 object-contain drop-shadow-2xl animate-bounce"
          />
          <!-- Glow effect -->
          <div class="absolute inset-0 bg-gradient-to-r from-yellow-400/20 via-pink-400/20 to-purple-400/20 rounded-full blur-xl animate-pulse"></div>
        </div>
      </div>

      <!-- Celebration text -->
      <div class="text-white drop-shadow-lg">
        <h1 class="text-4xl sm:text-6xl font-bold mb-4 animate-pulse">
          🎉 MAXIMUM TOP-UP! 🎉
        </h1>
        <p class="text-xl sm:text-2xl font-semibold mb-2 text-yellow-300">
          Incredible! You topped up the maximum amount!
        </p>
        <p class="text-lg sm:text-xl text-blue-200">
          {amount} {token} = ULTIMATE POWER! 💪
        </p>
        <p class="text-sm sm:text-base text-gray-300 mt-4 opacity-80">
          You're officially a top-tier mAIner legend! 🏆
        </p>
      </div>

      <!-- Additional party elements -->
      <div class="mt-8 flex justify-center space-x-4 text-4xl animate-bounce">
        <span style="animation-delay: 0.1s">🚀</span>
        <span style="animation-delay: 0.2s">⭐</span>
        <span style="animation-delay: 0.3s">🔥</span>
        <span style="animation-delay: 0.4s">💎</span>
        <span style="animation-delay: 0.5s">🎊</span>
      </div>
    </div>
  </div>
{/if}

<style>
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }

  .animate-float {
    animation: float 2s ease-in-out infinite;
  }

  /* Enhanced glow effect */
  @keyframes glow {
    0%, 100% { 
      filter: drop-shadow(0 0 20px rgba(255, 215, 0, 0.8)) 
              drop-shadow(0 0 40px rgba(255, 20, 147, 0.6)); 
    }
    50% { 
      filter: drop-shadow(0 0 30px rgba(255, 215, 0, 1)) 
              drop-shadow(0 0 60px rgba(255, 20, 147, 0.8)); 
    }
  }

  img {
    animation: glow 1.5s ease-in-out infinite;
  }

  /* Responsive adjustments */
  @media (max-width: 640px) {
    h1 {
      font-size: 2.5rem;
    }
  }
</style> 