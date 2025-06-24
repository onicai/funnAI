// Top-up configuration
export const TOP_UP_CONFIG = {
  // Minimum amount for top-up in ICP
  MIN_AMOUNT: 0.1,
  
  // Maximum amount for top-up in ICP (configurable)
  // When users top up this amount, they get a special celebration
  MAX_AMOUNT: 100, // must be a natural number
  
  // Duration for celebration display in milliseconds
  CELEBRATION_DURATION: 5500,
  
  // Enable/disable celebration feature
  CELEBRATION_ENABLED: true
} as const;

// Export individual values for convenience
export const { MIN_AMOUNT, MAX_AMOUNT, CELEBRATION_DURATION, CELEBRATION_ENABLED } = TOP_UP_CONFIG; 