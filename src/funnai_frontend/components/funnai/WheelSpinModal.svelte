<script lang="ts">
  import { onMount } from 'svelte';
  import Modal from "../CommonModal.svelte";
  import { store } from "../../stores/store";
  import { IcrcService } from "../../helpers/IcrcService";
  import { formatBalance } from "../../helpers/utils/numberFormatUtils";
  import { fetchTokens, protocolConfig, FUNNAI_CANISTER_ID } from "../../helpers/token_helpers";
  import { WHEEL_CONFIG, getSegmentIndexForOutcome, type WheelOutcome } from "../../helpers/config/wheelConfig";
  import { Info, Gift, Zap, Coins, AlertCircle, CheckCircle, ChevronDown, ChevronUp, HelpCircle, Shield } from 'lucide-svelte';

  export let isOpen: boolean = false;
  
  // Info panel state
  let showInfo: boolean = false;
  let showFairness: boolean = false;
  export let onClose: () => void = () => {};

  // State
  let isLoading: boolean = true;
  let isSpinning: boolean = false;
  let isBurning: boolean = false;
  let isProcessing: boolean = false;
  let statusMessage: string = "";
  let errorMessage: string = "";
  let successMessage: string = "";
  
  // User data
  let funnaiBalance: bigint = BigInt(0);
  let funnaiToken: any = null;
  let canSpin: boolean = false;
  let canSpinReason: string = "";
  let requiredFunnai: bigint = WHEEL_CONFIG.FUNNAI_COST;
  let nextSpinAvailableAt: Date | null = null;
  
  // Wheel state
  let wheelPhase: 'info' | 'spinning' | 'result' = 'info';
  let spinResult: WheelOutcome | null = null;
  
  // Canvas for wheel
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D;
  let currentAngle: number = 0;
  let targetAngle: number = 0;
  let isAnimating: boolean = false;
  let audio: HTMLAudioElement;
  let lastTickPosition: number = 0;
  
  const segments = WHEEL_CONFIG.SEGMENTS;
  
  // Computed
  $: hasEnoughBalance = funnaiBalance >= requiredFunnai;
  $: canSubmit = hasEnoughBalance && canSpin && !isSpinning && !isBurning && !isProcessing;
  $: formattedBalance = funnaiToken ? formatBalance(funnaiBalance.toString(), funnaiToken.decimals) : '0';
  $: formattedRequired = funnaiToken ? formatBalance(requiredFunnai.toString(), funnaiToken.decimals) : '0';
  
  onMount(async () => {
    await loadData();
    
    // Initialize audio
    audio = new Audio('/wheel/tick.mp3');
    audio.volume = 0.5;
    audio.preload = 'auto';
    
    // Initialize wheel drawing after DOM is ready
    setTimeout(() => {
      if (canvas) {
        ctx = canvas.getContext('2d')!;
        drawWheel();
      }
    }, 100);
  });
  
  // Re-draw wheel when canvas becomes available or when loading finishes
  $: if (canvas && !isLoading) {
    // Ensure context is set and wheel is drawn
    setTimeout(() => {
      if (canvas) {
        ctx = canvas.getContext('2d')!;
        drawWheel();
      }
    }, 50);
  }
  
  async function loadData() {
    isLoading = true;
    errorMessage = "";
    
    try {
      // Load FUNNAI token data
      const result = await fetchTokens({});
      funnaiToken = result.tokens.find(t => t.symbol === "FUNNAI");
      
      if (!funnaiToken) {
        throw new Error("FUNNAI token not found");
      }
      
      // Load user's FUNNAI balance
      if ($store.principal) {
        funnaiBalance = await IcrcService.getIcrc1Balance(
          funnaiToken,
          $store.principal
        ) as bigint;
      }
      
      // Check if user can spin
      await checkCanSpin();
      
    } catch (error) {
      console.error("Error loading wheel data:", error);
      errorMessage = "Failed to load data. Please try again.";
    } finally {
      isLoading = false;
    }
  }
  
  async function checkCanSpin() {
    try {
      if (!$store.gameStateCanisterActor) {
        canSpin = false;
        canSpinReason = "Game state not available";
        return;
      }
      
      const result = await $store.gameStateCanisterActor.canUserSpinWheel();
      
      if (result && 'Ok' in result) {
        canSpin = result.Ok.canSpin;
        canSpinReason = result.Ok.reason?.[0] || "";
        requiredFunnai = BigInt(result.Ok.requiredFunnai);
        
        if (result.Ok.nextSpinAvailableAt?.[0]) {
          // Convert nanoseconds to milliseconds
          const nextSpinNs = BigInt(result.Ok.nextSpinAvailableAt[0]);
          nextSpinAvailableAt = new Date(Number(nextSpinNs / BigInt(1000000)));
        }
      } else {
        canSpin = false;
        const errorResult = result as { Err?: unknown };
        canSpinReason = errorResult?.Err ? JSON.stringify(errorResult.Err) : "Unable to check spin eligibility";
      }
    } catch (error) {
      console.error("Error checking spin eligibility:", error);
      canSpin = false;
      canSpinReason = "Failed to check eligibility";
    }
  }
  
  // Helper to add timeout to promises
  function withTimeout<T>(promise: Promise<T>, ms: number, errorMsg: string): Promise<T> {
    return Promise.race([
      promise,
      new Promise<T>((_, reject) => 
        setTimeout(() => reject(new Error(errorMsg)), ms)
      )
    ]);
  }

  async function handleSpin() {
    if (!canSubmit || !funnaiToken) return;
    
    errorMessage = "";
    statusMessage = "Processing payment...";
    isBurning = true;
    isProcessing = true;
    
    try {
      // Step 1: Burn FUNNAI by transferring to protocol
      const tokenFee = funnaiToken.fee_fixed ? BigInt(funnaiToken.fee_fixed) : BigInt(0);
      const transferResult = await withTimeout(
        IcrcService.transfer(
          funnaiToken,
          protocolConfig.address,
          requiredFunnai,
          {
            fee: tokenFee,
            memo: WHEEL_CONFIG.MEMO
          }
        ),
        30000,
        "Transfer timed out. Please try again."
      );
      
      if (!transferResult || typeof transferResult !== 'object' || !('Ok' in transferResult)) {
        const errorResult = transferResult as { Err?: Record<string, unknown> } | undefined;
        const errMsg = errorResult?.Err 
          ? (typeof errorResult.Err === 'object' 
              ? Object.keys(errorResult.Err)[0] 
              : String(errorResult.Err))
          : "Transfer failed";
        throw new Error(`Failed to burn FUNNAI: ${errMsg}`);
      }
      
      const txId = transferResult.Ok;
      console.log("Burn transaction successful, txId:", txId);
      
      isBurning = false;
      statusMessage = "Verifying payment...";
      
      // Step 2: Call backend to spin the wheel - get result first
      if (!$store.gameStateCanisterActor) {
        throw new Error("Game state canister not available");
      }
      
      const spinResultResponse = await withTimeout(
        $store.gameStateCanisterActor.spinWheel({ 
          paymentTransactionBlockId: BigInt(txId as bigint) 
        }),
        45000,
        "Spin request timed out. Your FUNNAI was burned but the spin didn't complete. Please contact support."
      );
      
      if (!spinResultResponse || !('Ok' in spinResultResponse)) {
        const errorResult = spinResultResponse as { Err?: Record<string, unknown> };
        let errMsg = "Spin failed";
        if (errorResult?.Err && typeof errorResult.Err === 'object') {
          const errKey = Object.keys(errorResult.Err)[0];
          const errValue = errorResult.Err[errKey];
          errMsg = typeof errValue === 'string' ? errValue : errKey;
        }
        throw new Error(errMsg);
      }
      
      // Parse the outcome - we have the result!
      const outcome = spinResultResponse.Ok.outcome;
      spinResult = parseOutcome(outcome);
      
      // NOW start the spin animation with the known outcome
      isProcessing = false;
      isSpinning = true;
      wheelPhase = 'spinning';
      statusMessage = "";
      
      // Calculate target angle and spin to it
      const segmentIndex = getSegmentIndexForOutcome(spinResult);
      spinToSegment(segmentIndex);
      
    } catch (error) {
      console.error("Spin error:", error);
      errorMessage = error instanceof Error ? error.message : "Spin failed";
      isBurning = false;
      isSpinning = false;
      isProcessing = false;
      isAnimating = false;
      statusMessage = "";
      wheelPhase = 'info';
      if (ctx) drawWheel();
    }
  }
  
  // New function: spin directly to a segment (result already known)
  function spinToSegment(segmentIndex: number) {
    const segmentAngle = 2 * Math.PI / segments.length;
    const minRotations = WHEEL_CONFIG.MIN_ROTATIONS;
    
    // Target the center of the segment, accounting for the pointer being on the right
    const segmentCenterAngle = segmentIndex * segmentAngle + segmentAngle / 2;
    targetAngle = currentAngle + (minRotations * 2 * Math.PI) + (2 * Math.PI - segmentCenterAngle);
    
    animateToTarget();
  }
  
  function parseOutcome(outcome: any): WheelOutcome {
    if ('Nothing' in outcome) {
      return { type: 'nothing' };
    }
    if ('Cycles' in outcome) {
      const cycles = outcome.Cycles;
      const amount = formatCyclesAmount(BigInt(cycles.amount));
      return { 
        type: 'cycles', 
        amount,
        mainerAddress: cycles.mainerAddress 
      };
    }
    if ('Funnai' in outcome) {
      const funnai = outcome.Funnai;
      // Convert from smallest unit (8 decimals) to display amount
      const displayAmount = Number(BigInt(funnai.amount) / BigInt(100000000));
      return { 
        type: 'funnai', 
        amount: displayAmount.toString() 
      };
    }
    return { type: 'nothing' };
  }
  
  function formatCyclesAmount(cycles: bigint): string {
    const trillion = BigInt(1000000000000);
    if (cycles >= trillion * BigInt(100)) return '100T';
    if (cycles >= trillion * BigInt(10)) return '10T';
    if (cycles >= trillion) return '1T';
    return cycles.toString();
  }
  
  // Wheel drawing functions
  function drawWheel() {
    if (!ctx || !canvas) return;
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const outerRadius = canvas.width / 2 - 15;
    const textRadius = outerRadius - 12; // Position text closer to the outer edge
    const innerRadius = 35;
    
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
      
      ctx.fillStyle = segments[i].color;
      ctx.fill();
      
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw text
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(angle + segmentAngle / 2);
      
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = segments[i].textColor;
      ctx.font = 'bold 13px Arial';
      
      // Add text shadow for better readability
      ctx.shadowColor = 'rgba(0,0,0,0.5)';
      ctx.shadowBlur = 3;
      ctx.shadowOffsetX = 1;
      ctx.shadowOffsetY = 1;
      
      ctx.fillText(segments[i].label, textRadius, 0);
      ctx.shadowColor = 'transparent';
      ctx.restore();
    }
    
    // Draw outer ring
    ctx.beginPath();
    ctx.arc(centerX, centerY, outerRadius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 4;
    ctx.stroke();
    
    // Draw center circle background
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Draw arrow/pointer on the right side
    ctx.beginPath();
    ctx.moveTo(centerX + outerRadius - 5, centerY);
    ctx.lineTo(centerX + outerRadius + 20, centerY - 15);
    ctx.lineTo(centerX + outerRadius + 20, centerY + 15);
    ctx.closePath();
    ctx.fillStyle = '#a855f7';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 3;
    ctx.stroke();
    
    // Add pointer inner highlight
    ctx.beginPath();
    ctx.moveTo(centerX + outerRadius + 5, centerY);
    ctx.lineTo(centerX + outerRadius + 15, centerY - 8);
    ctx.lineTo(centerX + outerRadius + 15, centerY + 8);
    ctx.closePath();
    ctx.fillStyle = '#c084fc';
    ctx.fill();
  }
  
  function playTickSound() {
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    audio.play().catch(() => {});
  }
  
  function startSpinAnimation() {
    isAnimating = true;
    lastTickPosition = 0;
    animateSpin();
  }
  
  function animateSpin() {
    if (!isAnimating) return;
    
    // Fast spinning while waiting for result
    currentAngle += 0.3;
    
    // Play tick sound on segment change
    const segmentAngle = 2 * Math.PI / segments.length;
    const currentPosition = Math.floor(currentAngle / segmentAngle) % segments.length;
    if (currentPosition !== lastTickPosition) {
      playTickSound();
      lastTickPosition = currentPosition;
    }
    
    drawWheel();
    requestAnimationFrame(animateSpin);
  }
  
  function stopSpinAtSegment(segmentIndex: number) {
    isAnimating = false;
    
    // Calculate target angle to land on the segment
    const segmentAngle = 2 * Math.PI / segments.length;
    const minRotations = WHEEL_CONFIG.MIN_ROTATIONS;
    
    // Target the center of the segment, accounting for the pointer being on the right
    const segmentCenterAngle = segmentIndex * segmentAngle + segmentAngle / 2;
    targetAngle = currentAngle + (minRotations * 2 * Math.PI) + (2 * Math.PI - segmentCenterAngle);
    
    animateToTarget();
  }
  
  function animateToTarget() {
    const duration = WHEEL_CONFIG.SPIN_DURATION_MS;
    const startAngle = currentAngle;
    const startTime = Date.now();
    
    function easeOut(t: number): number {
      return 1 - Math.pow(1 - t, 3);
    }
    
    function animate() {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOut(progress);
      
      currentAngle = startAngle + (targetAngle - startAngle) * easedProgress;
      
      // Play tick sound on segment change
      const segmentAngle = 2 * Math.PI / segments.length;
      const currentPosition = Math.floor(currentAngle / segmentAngle) % segments.length;
      if (currentPosition !== lastTickPosition) {
        playTickSound();
        lastTickPosition = currentPosition;
      }
      
      drawWheel();
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        // Animation complete - show result
        isSpinning = false;
        wheelPhase = 'result';
      }
    }
    
    animate();
  }
  
  function handleClose() {
    // Reset state
    wheelPhase = 'info';
    spinResult = null;
    isSpinning = false;
    isBurning = false;
    isProcessing = false;
    statusMessage = "";
    errorMessage = "";
    successMessage = "";
    showInfo = false;
    showFairness = false;
    onClose();
  }
  
  function handleSpinAgain() {
    wheelPhase = 'info';
    spinResult = null;
    isProcessing = false;
    isSpinning = false;
    isAnimating = false;
    statusMessage = "";
    errorMessage = "";
    currentAngle = 0; // Reset wheel position
    loadData().then(() => {
      // Re-initialize canvas after data loads
      setTimeout(() => {
        if (canvas) {
          ctx = canvas.getContext('2d')!;
          drawWheel();
        }
      }, 100);
    });
  }
  
  function getResultMessage(): string {
    if (!spinResult) return "";
    
    if (spinResult.type === 'nothing') {
      return "Better luck next time!";
    }
    if (spinResult.type === 'cycles') {
      return `You won ${spinResult.amount} Cycles${spinResult.mainerAddress ? ` for your mAIner!` : '!'}`;
    }
    if (spinResult.type === 'funnai') {
      return `You won ${spinResult.amount} FUNNAI!`;
    }
    return "";
  }
  
  function formatTimeUntilSpin(): string {
    if (!nextSpinAvailableAt) return "";
    
    const now = new Date();
    const diff = nextSpinAvailableAt.getTime() - now.getTime();
    
    if (diff <= 0) return "Available now!";
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }
</script>

<Modal
  {isOpen}
  onClose={handleClose}
  title="Aira's Wheel of Fortune"
  width="min(500px, calc(100vw - 2rem))"
  variant="transparent"
  height="auto"
  className="wheel-spin-modal"
  closeOnEscape={!isSpinning}
  closeOnClickOutside={!isSpinning}
  isPadded={true}
>
  <div class="px-2 sm:px-4 py-4 flex flex-col gap-4">
    {#if isLoading}
      <!-- Loading skeleton -->
      <div class="flex flex-col items-center gap-4">
        <!-- Wheel placeholder -->
        <div class="relative w-[300px] h-[300px] rounded-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse flex items-center justify-center">
          <div class="w-16 h-16 rounded-full bg-white dark:bg-gray-600"></div>
        </div>
        <!-- Info placeholder -->
        <div class="w-full space-y-3">
          <div class="h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
          <div class="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"></div>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">Loading wheel data...</p>
      </div>
    {:else}
      <!-- Wheel is always visible -->
      <div class="flex flex-col items-center gap-4">
        <!-- Wheel Display -->
        <div class="relative">
          <canvas bind:this={canvas} width="300" height="300"></canvas>
          <!-- Center coin overlay -->
          <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <img src="/coin.webp" alt="FUNNAI" class="w-14 h-14 rounded-full coin-image" />
          </div>
        </div>
        
        {#if wheelPhase === 'spinning'}
          <div class="text-center space-y-2">
            <p class="text-lg font-semibold text-amber-600 dark:text-amber-400 animate-pulse">
              Spinning...
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Good luck!
            </p>
          </div>
        {:else if wheelPhase === 'result' && spinResult}
          <!-- Result Display -->
          <div class="w-full p-4 rounded-lg {spinResult.type === 'nothing' 
            ? 'bg-gray-100 dark:bg-gray-800' 
            : 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20'} 
            border {spinResult.type === 'nothing' 
              ? 'border-gray-300 dark:border-gray-600' 
              : 'border-green-200 dark:border-green-800/30'}">
            <div class="flex items-center justify-center gap-3">
              {#if spinResult.type === 'nothing'}
                <AlertCircle class="w-8 h-8 text-gray-500" />
              {:else}
                <CheckCircle class="w-8 h-8 text-green-600" />
              {/if}
              <span class="text-lg font-semibold {spinResult.type === 'nothing' 
                ? 'text-gray-700 dark:text-gray-300' 
                : 'text-green-800 dark:text-green-200'}">
                {getResultMessage()}
              </span>
            </div>
            {#if spinResult.type === 'cycles' && spinResult.mainerAddress}
              <p class="text-sm text-center text-green-600 dark:text-green-400 mt-2">
                Sent to: {spinResult.mainerAddress.slice(0, 10)}...
              </p>
            {/if}
          </div>
          
          <div class="flex gap-3 w-full">
            <button
              type="button"
              on:click={handleSpinAgain}
              class="flex-1 py-2 px-4 rounded-lg font-medium text-amber-700 dark:text-amber-300 bg-amber-100 dark:bg-amber-900/30 hover:bg-amber-200 dark:hover:bg-amber-900/50 transition-colors"
            >
              Spin Again
            </button>
            <button
              type="button"
              on:click={handleClose}
              class="flex-1 py-2 px-4 rounded-lg font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              Close
            </button>
          </div>
        {:else}
          <!-- Info Phase (wheel visible above) -->
          <div class="w-full flex flex-col gap-3">
            <!-- How to Play Toggle -->
            <button
              type="button"
              on:click={() => showInfo = !showInfo}
              class="w-full flex items-center justify-between p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800/30 text-purple-700 dark:text-purple-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
            >
              <span class="flex items-center gap-2 text-sm font-medium">
                <HelpCircle class="w-4 h-4" />
                How to Play & Prizes
              </span>
              {#if showInfo}
                <ChevronUp class="w-4 h-4" />
              {:else}
                <ChevronDown class="w-4 h-4" />
              {/if}
            </button>
            
            {#if showInfo}
              <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/30 border border-gray-200 dark:border-gray-700 text-sm space-y-3">
                <!-- How to Play -->
                <div>
                  <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-1.5 flex items-center gap-1.5">
                    <Gift class="w-4 h-4 text-amber-500" />
                    How to Play
                  </h4>
                  <ol class="list-decimal list-inside text-gray-600 dark:text-gray-400 space-y-1 text-xs">
                    <li>Make sure you have enough FUNNAI tokens</li>
                    <li>Click "Spin the Wheel" to pay and spin</li>
                    <li>Watch the wheel spin and land on your prize!</li>
                    <li>Cycle prizes are sent directly to your mAIner</li>
                  </ol>
                </div>
                
                <!-- Prizes -->
                <div>
                  <h4 class="font-semibold text-gray-800 dark:text-gray-200 mb-1.5 flex items-center gap-1.5">
                    <Coins class="w-4 h-4 text-yellow-500" />
                    Prizes
                  </h4>
                  <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                      <span class="text-gray-600 dark:text-gray-400">1T Cycles</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-green-600"></span>
                      <span class="text-gray-600 dark:text-gray-400">10T Cycles</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-teal-500"></span>
                      <span class="text-gray-600 dark:text-gray-400">100T Cycles</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                      <span class="text-gray-600 dark:text-gray-400">10 FUNNAI</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                      <span class="text-gray-600 dark:text-gray-400">100 FUNNAI</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
                      <span class="text-gray-600 dark:text-gray-400">1000 FUNNAI</span>
                    </div>
                  </div>
                </div>
                
                <!-- Note -->
                <p class="text-xs text-gray-500 dark:text-gray-500 italic">
                  Randomness is secured by the Internet Computer's cryptographic random beacon.
                </p>
              </div>
            {/if}
            
            <!-- Provably Fair Toggle -->
            <button
              type="button"
              on:click={() => showFairness = !showFairness}
              class="w-full flex items-center justify-between p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
            >
              <span class="flex items-center gap-2 text-sm font-medium">
                <Shield class="w-4 h-4" />
                Provably Fair 🎰
              </span>
              {#if showFairness}
                <ChevronUp class="w-4 h-4" />
              {:else}
                <ChevronDown class="w-4 h-4" />
              {/if}
            </button>
            
            {#if showFairness}
              <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/30 border border-gray-200 dark:border-gray-700 text-sm space-y-3">
                <p class="text-gray-700 dark:text-gray-300">
                  🎡 <strong>Aira's Wheel of Fortune</strong> runs on <a href="https://internetcomputer.org" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-400 hover:underline">DFINITY's Internet Computer</a> - where randomness isn't just "random", it's cryptographically <strong>GUARANTEED</strong> fair.
                </p>
                
                <div class="bg-blue-50 dark:bg-blue-900/20 p-2.5 rounded-lg border border-blue-100 dark:border-blue-800/30">
                  <p class="text-gray-700 dark:text-gray-300 font-medium mb-1.5">How does it work?</p>
                  <p class="text-gray-600 dark:text-gray-400 text-xs">
                    The IC uses <strong>threshold BLS signatures</strong>: multiple nodes each contribute a piece, and <strong>NO ONE</strong> knows the outcome until they're combined.
                  </p>
                </div>
                
                <p class="text-gray-600 dark:text-gray-400 text-center font-medium">
                  No single party can predict or manipulate the spin. Ever. 🎰✨
                </p>
              </div>
            {/if}
            
            <!-- Cost & Balance Info -->
            <div class="p-3 rounded-lg bg-gray-100 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">Spin Cost:</span>
                <span class="font-semibold text-amber-600 dark:text-amber-400">{formattedRequired} FUNNAI</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Your Balance:</span>
                <span class="font-semibold {hasEnoughBalance ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
                  {formattedBalance} FUNNAI
                </span>
              </div>
            </div>
            
            <!-- Eligibility Status -->
            {#if !canSpin && canSpinReason}
              <div class="p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800/30">
                <div class="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
                  <AlertCircle class="w-5 h-5 flex-shrink-0" />
                  <span class="text-sm">{canSpinReason}</span>
                </div>
                {#if nextSpinAvailableAt}
                  <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-1 ml-7">
                    Next spin available in: {formatTimeUntilSpin()}
                  </p>
                {/if}
              </div>
            {/if}
            
            {#if !hasEnoughBalance}
              <div class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30">
                <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
                  <AlertCircle class="w-5 h-5 flex-shrink-0" />
                  <span class="text-sm">Insufficient FUNNAI balance</span>
                </div>
              </div>
            {/if}
            
            {#if errorMessage}
              <div class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/30">
                <div class="flex items-center gap-2 text-red-800 dark:text-red-200">
                  <AlertCircle class="w-5 h-5 flex-shrink-0" />
                  <span class="text-sm">{errorMessage}</span>
                </div>
              </div>
            {/if}
            
            <!-- Spin Button -->
            <button
              type="button"
              on:click={handleSpin}
              disabled={!canSubmit}
              class="w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200 flex items-center justify-center gap-2
                     {canSubmit 
                       ? 'bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 shadow-lg hover:shadow-xl' 
                       : 'bg-gray-400 dark:bg-gray-700 cursor-not-allowed'}"
            >
              {#if isProcessing}
                <span class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                {statusMessage || 'Processing...'}
              {:else}
                <Gift class="w-5 h-5" />
                Spin the Wheel ({formattedRequired} FUNNAI)
              {/if}
            </button>
            
            <p class="text-xs text-center text-gray-500 dark:text-gray-400">
              Spin for a chance to win Cycles or FUNNAI!
            </p>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</Modal>

<style>
  :global(.wheel-spin-modal) {
    max-width: min(500px, calc(100vw - 2rem));
  }
  
  .coin-image {
    object-fit: cover;
  }
  
  .coin-image:not([src]), .coin-image[src=""] {
    display: none;
  }
</style>
