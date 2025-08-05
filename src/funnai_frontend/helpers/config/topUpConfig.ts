// Top-up configuration
export const TOP_UP_CONFIG = {
  // Minimum amount for top-up in ICP
  MIN_AMOUNT: 0.1,
  
  // Maximum amount for top-up in ICP (configurable)
  // When users top up this amount, they get a special celebration
  MAX_AMOUNT: 42, // must be a natural number (i.e. no decimals), e.g. 1, 42, 100, 187432
  
  // Minimum amount for top-up in FUNNAI
  FUNNAI_MIN_AMOUNT: 4,
  
  // Maximum amount for top-up in FUNNAI (configurable)
  // When users top up this amount, they get a special celebration
  FUNNAI_MAX_AMOUNT: 1420, // must be a natural number (i.e. no decimals)
  
  // Duration for celebration display in milliseconds
  CELEBRATION_DURATION: 120000, // 120 seconds
  
  // Enable/disable celebration feature
  CELEBRATION_ENABLED: true
} as const;

// Export individual values for convenience
export const { MIN_AMOUNT, MAX_AMOUNT, FUNNAI_MIN_AMOUNT, FUNNAI_MAX_AMOUNT, CELEBRATION_DURATION, CELEBRATION_ENABLED } = TOP_UP_CONFIG; 