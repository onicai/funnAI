<script lang="ts">
  import { onMount } from 'svelte';

  import InternetIdentityButton from "./InternetIdentityButton.svelte";
  import NfidButton from "./NfidButton.svelte";

  export let toggleModal;

  let loading = ""; // this allows us to disable all buttons if one of them is clicked

  // Main function to initialize modal functionality
  const initializeModal = () => {
    const modal = document.getElementById('crypto-modal');
    // Add event listener to close the modal when clicking outside of it
    window.addEventListener('click', (event) => {
      if (event.target === modal) {
        toggleModal();
      };
    });
  };

  onMount(() => {
    initializeModal();
  });
</script>

<!-- Pirate-themed Modal with Background Effects -->
<div id="crypto-modal" tabindex="-1" aria-hidden="true" class="pirate-modal-backdrop fixed top-0 right-0 left-0 z-[9999] justify-center items-center w-full md:inset-0 h-[calc(100%)] max-h-full overflow-hidden">
  
  <!-- Animated Background with Distortion Effects -->
  <div class="pirate-bg-layer absolute inset-0 w-full h-full">
    <!-- Ocean waves effect -->
    <div class="ocean-waves absolute inset-0"></div>
    
    <!-- Floating treasure and particles -->
    <div class="treasure-particles absolute inset-0">
      <div class="floating-coin coin-1">⚱️</div>
      <div class="floating-coin coin-2">🪙</div>
      <div class="floating-coin coin-3">💰</div>
      <div class="floating-coin coin-4">⚓</div>
      <div class="floating-coin coin-5">🏴‍☠️</div>
      <div class="floating-coin coin-6">💎</div>
    </div>
    
    <!-- Fog/mist overlay -->
    <div class="fog-overlay absolute inset-0"></div>
  </div>

  <!-- Modal Content Container -->
  <div class="relative p-6 w-full mx-auto flex items-center content-center max-w-md max-h-full h-full z-10">
    <!-- Modal content with pirate theme -->
    <div class="pirate-modal-content relative w-full">
      
  
      
      <!-- Main modal card -->
      <div class="relative bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-100 dark:from-slate-900 dark:via-gray-900 dark:to-slate-800 rounded-2xl shadow-2xl border-2 border-amber-400/50 dark:border-amber-600/30 backdrop-blur-sm overflow-hidden">
        
        <!-- Treasure chest glow effect -->
        <div class="absolute inset-0 bg-gradient-to-t from-amber-200/20 via-transparent to-blue-300/10 dark:from-amber-900/20 dark:via-transparent dark:to-blue-900/10 pointer-events-none"></div>
        
        <!-- Modal header with pirate styling -->
        <div class="flex items-center justify-between p-6 pb-2 rounded-t relative">
          <div class="absolute top-2 left-2 text-amber-600/70 dark:text-amber-400/60 text-sm">⚔️</div>
          
          <button type="button" on:click={() => {toggleModal()}} class="close-modal-button absolute top-4 right-4 bg-red-600/80 hover:bg-red-500 dark:bg-red-800/80 dark:hover:bg-red-700 inline-flex justify-center items-center text-white dark:text-amber-200 rounded-full focus:ring-2 focus:ring-red-400 p-2 transition-all duration-300 hover:scale-110 border border-red-500/50 dark:border-red-600/50 shadow-lg" data-modal-toggle="crypto-modal">
            <svg class="w-4 h-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
            </svg>
            <span class="sr-only">Close modal</span>
          </button>
        </div>
        
        <!-- Modal body with pirate theme -->
        <div class="px-6 pb-6 pt-2">
          
          <!-- Pirate treasure chest icon with parrot -->
          <div class="flex justify-center mb-6 relative">
            <div class="treasure-glow relative">
              <div class="absolute inset-0 bg-amber-400/30 rounded-full blur-xl animate-pulse"></div>
              <div class="relative">
                <img src="/coin.webp" alt="Pirate Parrot" class="w-20 h-20 filter drop-shadow-lg" />
              </div>
            </div>
          </div>
          
          <!-- Pirate-themed heading -->
          <div class="text-center mb-6">
            <h3 class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-800 via-amber-700 to-amber-900 dark:from-amber-200 dark:via-amber-100 dark:to-amber-300 mb-2 font-serif tracking-wide">
              Ahoy, Matey! 
            </h3>
            <div class="flex items-center justify-center gap-2 mb-3">
              <div class="w-8 h-0.5 bg-gradient-to-r from-transparent via-amber-600 dark:via-amber-500 to-transparent"></div>
              <span class="text-amber-600 dark:text-amber-400">⚓</span>
              <div class="w-8 h-0.5 bg-gradient-to-r from-transparent via-amber-600 dark:via-amber-500 to-transparent"></div>
            </div>
            <p class="text-amber-800/90 dark:text-amber-200/90 text-sm leading-relaxed font-medium">
              Set sail into the <span class="text-amber-700 dark:text-amber-300 font-semibold">funnAI seas</span>! Connect your wallet to join our flock.
            </p>
          </div>
          
          <!-- Navigation buttons with pirate styling -->
          <div class="space-y-4">
            <InternetIdentityButton bind:loading {toggleModal} />
            <NfidButton bind:loading {toggleModal} />
          </div>
          
          <!-- Decorative elements -->
          <div class="flex justify-center items-center mt-6 gap-4 opacity-60">
            <span class="text-amber-600/70 dark:text-amber-400/70 text-xs">🗝️</span>
            <div class="text-amber-700/60 dark:text-amber-300/50 text-xs font-medium tracking-wider">SECURE • DECENTRALIZED • PRIVATE</div>
            <span class="text-amber-600/70 dark:text-amber-400/70 text-xs">🗝️</span>
          </div>
        </div>
        
        <!-- Bottom decorative border -->
        <div class="h-1 bg-gradient-to-r from-amber-600 via-amber-500 to-amber-600 dark:from-amber-800 dark:via-amber-600 dark:to-amber-800"></div>
      </div>
    </div>
  </div>
</div>

<style>
  /* Pirate Modal Backdrop */
  .pirate-modal-backdrop {
    display: flex;
    background: radial-gradient(circle at center, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.15) 50%, rgba(251, 191, 36, 0.1) 100%);
    backdrop-filter: blur(2px);
  }

  /* Dark mode backdrop */
  :global(.dark) .pirate-modal-backdrop {
    background: radial-gradient(circle at center, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.8) 50%, rgba(15, 23, 42, 0.7) 100%);
  }

  /* Animated Ocean Waves Background */
  .ocean-waves {
    background: 
      radial-gradient(circle at 20% 80%, rgba(251, 191, 36, 0.12) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(245, 158, 11, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(217, 119, 6, 0.06) 0%, transparent 50%);
    animation: waves 8s ease-in-out infinite;
  }

  /* Dark mode ocean waves */
  :global(.dark) .ocean-waves {
    background: 
      radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(139, 92, 246, 0.04) 0%, transparent 50%);
  }

  @keyframes waves {
    0%, 100% { 
      transform: scale(1) rotate(0deg); 
      opacity: 0.2;
    }
    50% { 
      transform: scale(1.1) rotate(2deg); 
      opacity: 0.3;
    }
  }

  /* Floating Treasure Particles */
  .floating-coin {
    position: absolute;
    font-size: 1.5rem;
    opacity: 0.6;
    pointer-events: none;
    animation: float 6s ease-in-out infinite;
    filter: drop-shadow(0 0 8px rgba(217, 119, 6, 0.4));
  }

  /* Dark mode floating coins */
  :global(.dark) .floating-coin {
    opacity: 0.4;
    filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.3));
  }

  .coin-1 {
    top: 15%;
    left: 10%;
    animation-delay: 0s;
    animation-duration: 7s;
  }

  .coin-2 {
    top: 25%;
    right: 15%;
    animation-delay: 1s;
    animation-duration: 8s;
  }

  .coin-3 {
    bottom: 30%;
    left: 15%;
    animation-delay: 2s;
    animation-duration: 6s;
  }

  .coin-4 {
    top: 60%;
    right: 10%;
    animation-delay: 3s;
    animation-duration: 9s;
  }

  .coin-5 {
    bottom: 15%;
    right: 25%;
    animation-delay: 4s;
    animation-duration: 7s;
  }

  .coin-6 {
    top: 40%;
    left: 5%;
    animation-delay: 5s;
    animation-duration: 8s;
  }

  @keyframes float {
    0%, 100% { 
      transform: translateY(0px) rotate(0deg) scale(1);
      opacity: 0.2;
    }
    25% { 
      transform: translateY(-20px) rotate(5deg) scale(1.1);
      opacity: 0.6;
    }
    50% { 
      transform: translateY(-10px) rotate(-3deg) scale(0.9);
      opacity: 0.4;
    }
    75% { 
      transform: translateY(-25px) rotate(7deg) scale(1.05);
      opacity: 0.7;
    }
  }

  /* Fog/Mist Overlay */
  .fog-overlay {
    background: 
      radial-gradient(ellipse at top, rgba(251, 191, 36, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse at bottom, rgba(245, 158, 11, 0.20) 0%, transparent 70%);
    animation: fog-drift 10s ease-in-out infinite;
  }

  /* Dark mode fog overlay */
  :global(.dark) .fog-overlay {
    background: 
      radial-gradient(ellipse at top, rgba(30, 41, 59, 0.15) 0%, transparent 70%),
      radial-gradient(ellipse at bottom, rgba(15, 23, 42, 0.2) 0%, transparent 70%);
  }

  @keyframes fog-drift {
    0%, 100% { 
      opacity: 0.2;
      transform: translateX(0px);
    }
    50% { 
      opacity: 0.4;
      transform: translateX(5px);
    }
  }

  /* Ship Wheel Border Effect */
  .ship-wheel-border {
    background: conic-gradient(from 0deg, 
      transparent 0deg, 
      rgba(251, 191, 36, 0.2) 45deg, 
      transparent 90deg,
      rgba(251, 191, 36, 0.2) 135deg,
      transparent 180deg,
      rgba(251, 191, 36, 0.2) 225deg,
      transparent 270deg,
      rgba(251, 191, 36, 0.2) 315deg,
      transparent 360deg
    );
    animation: spin-wheel 20s linear infinite;
    filter: blur(1px);
  }

  @keyframes spin-wheel {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  /* Modal Content Styling */
  .pirate-modal-content {
    animation: modal-rise 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @keyframes modal-rise {
    from {
      opacity: 0;
      transform: translateY(30px) scale(0.9);
    }
    to {
      opacity: 1;
      transform: translateY(0px) scale(1);
    }
  }

  /* Treasure Glow Animation */
  .treasure-glow {
    animation: treasure-pulse 3s ease-in-out infinite;
  }

  @keyframes treasure-pulse {
    0%, 100% { 
      transform: scale(1) rotate(0deg);
    }
    50% { 
      transform: scale(1.05) rotate(2deg);
    }
  }

  /* Enhanced hover effects for interactive elements */
  .close-modal-button {
    backdrop-filter: blur(8px);
  }

  .close-modal-button:hover {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
  }

  /* Dark mode close button hover */
  :global(.dark) .close-modal-button:hover {
    box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
  }

  /* Responsive adjustments */
  @media (max-width: 640px) {
    .floating-coin {
      font-size: 1rem;
    }
    
    .pirate-modal-content {
      margin: 1rem;
    }
  }
</style>
