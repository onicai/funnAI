<script lang="ts">
  import { onMount } from 'svelte';
  import Toast from './Toast.svelte';

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;
  let spinning = false;
  let currentAngle = 0;
  let spinAngleStart = 0;
  let spinTime = 0;
  let spinTimeTotal = 0;
  let audio: HTMLAudioElement;
  let lastTickPosition = 0;
  let hasWon = false;
  let email = '';
  let showToast = false;
  let toastMessage = '';
  let toastType: 'success' | 'error' = 'success';

  const segments = [
    { fillStyle: '#ff223e', text: 'win' },
    { fillStyle: '#fcac2e', text: 'lose' },
    { fillStyle: '#29ccfd', text: 'win' },
    { fillStyle: '#448f13', text: 'lose' },
    { fillStyle: '#ff223e', text: 'win' },
    { fillStyle: '#fcac2e', text: 'lose', textFillStyle: '#ffffff' },
    { fillStyle: '#448f13', text: 'win' },
    { fillStyle: '#68c317', text: 'lose' },
    { fillStyle: '#fcac2e', text: 'win' },
    { fillStyle: '#e44902', text: 'lose' },
    { fillStyle: '#ff223e', text: 'win' },
    { fillStyle: '#448f13', text: 'lose' },
  ];

  onMount(() => {
    ctx = canvas.getContext('2d');
    drawWheel();
    
    // Initialize audio
    audio = new Audio('/wheel/tick.mp3');
    audio.volume = 0.5;
    audio.preload = 'auto';
  });

  function showToastMessage(message: string, type: 'success' | 'error' = 'success') {
    toastMessage = message;
    toastType = type;
    showToast = true;
  }

  function handleToastClose() {
    showToast = false;
  }

  function handleSubmit() {
    // Here you would typically send the email to your backend
    console.log('Submitting email:', email);
    showToastMessage('Your email has been submitted successfully!', 'success');
    // Reset the form
    email = '';
    hasWon = false;
  }

  function drawWheel() {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const outerRadius = canvas.width / 2 - 10;
    const textRadius = outerRadius - 15;
    const innerRadius = 40;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw wheel segments
    const segmentAngle = 2 * Math.PI / segments.length;
    
    for (let i = 0; i < segments.length; i++) {
      const angle = currentAngle + i * segmentAngle;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, outerRadius, angle, angle + segmentAngle);
      ctx.lineTo(centerX, centerY);
      ctx.closePath();
      
      ctx.fillStyle = segments[i].fillStyle;
      ctx.fill();
      
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw text
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(angle + segmentAngle / 2);
      
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = segments[i].textFillStyle || '#fff';
      ctx.font = 'bold 14px Arial';
      
      ctx.fillText(segments[i].text, textRadius, 0);
      ctx.restore();
    }
    
    // Draw center circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.fillStyle = '#fff';
    ctx.fill();
    
    // Draw outer circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, outerRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Draw arrow on the RIGHT side but pointing INWARD (rotated 180 degrees)
    ctx.beginPath();
    // Start at the outer edge of the wheel on the right
    ctx.moveTo(centerX + outerRadius - 10, centerY);
    // Draw the triangle pointing inward
    ctx.lineTo(centerX + outerRadius + 10, centerY - 10);
    ctx.lineTo(centerX + outerRadius + 10, centerY + 10);
    ctx.closePath();
    ctx.fillStyle = 'gold';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  function playTickSound() {
    if (!audio) return;
    
    // Reset the audio
    audio.pause();
    audio.currentTime = 0;
    
    // Play the audio
    audio.play().catch(error => {
      console.error("Error playing tick sound:", error);
    });
  }

  function spin() {
    if (spinning) return;
    
    spinning = true;
    spinAngleStart = Math.random() * 10 + 10;
    spinTime = 0;
    spinTimeTotal = Math.random() * 2 + 6 * 1000;
    lastTickPosition = 0;
    rotateWheel();
  }

  function rotateWheel() {
    spinTime += 30;
    if (spinTime >= spinTimeTotal) {
      stopRotateWheel();
      return;
    }
    
    const spinFactor = spinAngleStart - easeOut(spinTime, 0, spinAngleStart, spinTimeTotal);
    currentAngle += (spinFactor * Math.PI / 180);
    
    // Play tick sound based on segment position
    const segmentAngle = 2 * Math.PI / segments.length;
    const currentPosition = Math.floor(currentAngle / segmentAngle) % segments.length;
    
    if (currentPosition !== lastTickPosition) {
      playTickSound();
      lastTickPosition = currentPosition;
    }
    
    drawWheel();
    window.requestAnimationFrame(rotateWheel);
  }

  function stopRotateWheel() {
    spinning = false;
    
    const degrees = currentAngle * 180 / Math.PI % 360;
    const segmentIndex = Math.floor(segments.length - (degrees / (360 / segments.length)) % segments.length);
    const winner = segments[segmentIndex];
    
    setTimeout(() => {
      if (winner.text === 'lose') {
        showToastMessage('Try again!', 'error');
      } else {
        hasWon = true;
        showToastMessage('Congratulations! You won the chance to enter the raffle!', 'success');
      }
    }, 500);
  }

  function easeOut(t, b, c, d) {
    const ts = (t /= d) * t;
    const tc = ts * t;
    return b + c * (tc + -3 * ts + 3 * t);
  }
</script>

<div class="w-full bg-gray-800 rounded-lg p-6 mb-6">
  <div class="flex flex-col md:flex-row items-center justify-between gap-6">
    <!-- Wheel Column -->
    <div class="relative">
      <canvas bind:this={canvas} width="217" height="217"></canvas>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <img src="/coin.webp" alt="Wheel of Fortune" class="w-16 h-16">
      </div>
    </div>

    <!-- Text/Form Column -->
    <div class="text-center md:text-left flex-1">
      {#if hasWon}
        <div class="animate-fade-in">
          <h2 class="text-2xl font-bold text-white mb-4">You won the chance, please input your raffle email</h2>
          <form on:submit|preventDefault={handleSubmit} class="w-full">
            <input
              type="email"
              bind:value={email}
              placeholder="Enter your email"
              class="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              autofocus
              required
            />
          </form>
        </div>
      {:else}
        <h2 class="text-2xl font-bold text-white mb-4">Unlock exclusive access to funnAI!</h2>
        <p class="text-gray-300">
          Spin the wheel to unlock your shot at joining the exclusive funnAI early access raffle — a limited opportunity reserved for the lucky few who dare to take a chance!
        </p>
      {/if}
    </div>

    <!-- Button Column -->
    <div class="flex items-center">
      {#if hasWon}
        <button
          style="margin-top:44px;"
          class="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-md font-semibold"
          on:click={handleSubmit}
          disabled={!email}>
          Send your raffle email
        </button>
      {:else}
        <button
          class="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-md font-semibold"
          on:click={spin}
          disabled={spinning}>
          I'm feeling lucky!
        </button>
      {/if}
    </div>
  </div>
</div>

{#if showToast}
  <Toast
    message={toastMessage}
    type={toastType}
    onClose={handleToastClose}
  />
{/if}

<style>
  .animate-fade-in {
    animation: fadeIn 0.5s ease-in-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style> 