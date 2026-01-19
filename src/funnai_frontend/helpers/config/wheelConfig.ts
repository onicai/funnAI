// Wheel of Fortune configuration

export const WHEEL_CONFIG = {
  // Required FUNNAI amount to spin (in smallest unit - 8 decimals)
  // 1 FUNNAI = 100_000_000 (10^8)
  // 0.1 FUNNAI = 10_000_000
  FUNNAI_COST: BigInt(10_000_000), // 0.1 FUNNAI
  
  // Cooldown period in milliseconds (24 hours)
  COOLDOWN_MS: 24 * 60 * 60 * 1000,
  
  // Memo for wheel spin transactions (ASCII for "WHEEL")
  MEMO: [87, 72, 69, 69, 76] as number[],
  
  // Prize segments for the visual wheel (display only - backend determines actual outcome)
  SEGMENTS: [
    { label: '1T Cycles', color: '#22c55e', textColor: '#ffffff', type: 'cycles', amount: '1T' },
    { label: 'Try Again', color: '#475569', textColor: '#ffffff', type: 'nothing', amount: '0' },
    { label: '10 FUNNAI', color: '#0ea5e9', textColor: '#ffffff', type: 'funnai', amount: '10' },
    { label: 'Try Again', color: '#64748b', textColor: '#ffffff', type: 'nothing', amount: '0' },
    { label: '10T Cycles', color: '#f59e0b', textColor: '#ffffff', type: 'cycles', amount: '10T' },
    { label: 'Try Again', color: '#334155', textColor: '#ffffff', type: 'nothing', amount: '0' },
    { label: '100 FUNNAI', color: '#14b8a6', textColor: '#ffffff', type: 'funnai', amount: '100' },
    { label: 'Try Again', color: '#475569', textColor: '#ffffff', type: 'nothing', amount: '0' },
    { label: '100T Cycles', color: '#f97316', textColor: '#ffffff', type: 'cycles', amount: '100T' },
    { label: 'Try Again', color: '#1e293b', textColor: '#ffffff', type: 'nothing', amount: '0' },
    { label: '1000 FUNNAI', color: '#06b6d4', textColor: '#ffffff', type: 'funnai', amount: '1000' },
    { label: 'Try Again', color: '#64748b', textColor: '#ffffff', type: 'nothing', amount: '0' },
  ] as const,
  
  // Animation settings
  SPIN_DURATION_MS: 6000, // How long the wheel spins
  MIN_ROTATIONS: 5, // Minimum full rotations before stopping
} as const;

// Export individual values for convenience
export const { 
  FUNNAI_COST, 
  COOLDOWN_MS, 
  MEMO,
  SEGMENTS,
  SPIN_DURATION_MS,
  MIN_ROTATIONS 
} = WHEEL_CONFIG;

// Type exports
export type WheelSegment = typeof WHEEL_CONFIG.SEGMENTS[number];
export type WheelOutcomeType = 'cycles' | 'funnai' | 'nothing';

// Outcome interface that matches backend response
export interface WheelOutcome {
  type: WheelOutcomeType;
  amount?: string;
  mainerAddress?: string;
}

// Helper to find segment index for a given outcome
export function getSegmentIndexForOutcome(outcome: WheelOutcome): number {
  const segments = WHEEL_CONFIG.SEGMENTS;
  
  if (outcome.type === 'nothing') {
    // Return first "Try Again" segment
    return segments.findIndex(s => s.type === 'nothing');
  }
  
  if (outcome.type === 'cycles') {
    // Find matching cycles segment
    const idx = segments.findIndex(s => s.type === 'cycles' && s.amount === outcome.amount);
    return idx >= 0 ? idx : segments.findIndex(s => s.type === 'nothing');
  }
  
  if (outcome.type === 'funnai') {
    // Find matching FUNNAI segment
    const idx = segments.findIndex(s => s.type === 'funnai' && s.amount === outcome.amount);
    return idx >= 0 ? idx : segments.findIndex(s => s.type === 'nothing');
  }
  
  return 0;
}
