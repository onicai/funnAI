/**
 * Mainer Visual Identity Utilities
 * 
 * This file contains helper functions for generating consistent visual identities
 * for mAIners based on their IDs.
 */

export interface MainerVisualIdentity {
  colors: {
    bg: string;
    bgHover: string;
    accent: string;
    icon: string;
    text: string;
    border: string;
  };
  icon: string;
}

/**
 * Generate consistent visual identity for each mAIner based on its ID
 * @param agentId The mAIner's unique identifier
 * @returns Visual identity object with colors and icon
 */
export function getMainerVisualIdentity(agentId: string): MainerVisualIdentity {
  // Create a simple hash from the agent ID for consistent colors
  let hash = 0;
  for (let i = 0; i < agentId.length; i++) {
    const char = agentId.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Define a set of beautiful color schemes
  const colorSchemes = [
    {
      bg: 'from-purple-500 to-indigo-600',
      bgHover: 'from-purple-600 to-indigo-700',
      accent: 'bg-purple-100/30',
      icon: 'text-purple-100',
      text: 'text-purple-50',
      border: 'border-purple-400/30'
    },
    {
      bg: 'from-emerald-500 to-teal-600',
      bgHover: 'from-emerald-600 to-teal-700',
      accent: 'bg-emerald-100/30',
      icon: 'text-emerald-100',
      text: 'text-emerald-50',
      border: 'border-emerald-400/30'
    },
    {
      bg: 'from-blue-500 to-cyan-600',
      bgHover: 'from-blue-600 to-cyan-700',
      accent: 'bg-blue-100/30',
      icon: 'text-blue-100',
      text: 'text-blue-50',
      border: 'border-blue-400/30'
    },
    {
      bg: 'from-rose-500 to-pink-600',
      bgHover: 'from-rose-600 to-pink-700',
      accent: 'bg-rose-100/30',
      icon: 'text-rose-100',
      text: 'text-rose-50',
      border: 'border-rose-400/30'
    },
    {
      bg: 'from-amber-500 to-orange-600',
      bgHover: 'from-amber-600 to-orange-700',
      accent: 'bg-amber-100/30',
      icon: 'text-amber-100',
      text: 'text-amber-50',
      border: 'border-amber-400/30'
    },
    {
      bg: 'from-violet-500 to-purple-600',
      bgHover: 'from-violet-600 to-purple-700',
      accent: 'bg-violet-100/30',
      icon: 'text-violet-100',
      text: 'text-violet-50',
      border: 'border-violet-400/30'
    },
    {
      bg: 'from-teal-500 to-cyan-600',
      bgHover: 'from-teal-600 to-cyan-700',
      accent: 'bg-teal-100/30',
      icon: 'text-teal-100',
      text: 'text-teal-50',
      border: 'border-teal-400/30'
    },
    {
      bg: 'from-indigo-500 to-blue-600',
      bgHover: 'from-indigo-600 to-blue-700',
      accent: 'bg-indigo-100/30',
      icon: 'text-indigo-100',
      text: 'text-indigo-50',
      border: 'border-indigo-400/30'
    }
  ];
  
  // Define different avatar patterns/icons
  const avatarIcons = [
    // Robot variants
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M20 9V7c0-1.1-.9-2-2-2h-3c0-1.66-1.34-3-3-3S9 3.34 9 5H6c-1.1 0-2 .9-2 2v2c-1.66 0-3 1.34-3 3s1.34 3 3 3v4c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-4c1.66 0 3-1.34 3-3s-1.34-3-3-3zM9 12c0-.55-.45-1-1-1s-1 .45-1 1 .45 1 1 1 1-.45 1-1zm8 0c0-.55-.45-1-1-1s-1 .45-1 1 .45 1 1 1 1-.45 1-1zm-4 4c-1.1 0-2-.9-2-2h4c0 1.1-.9 2-2 2z"/>
    </svg>`,
    // Chip/processor
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M6 7h12v10H6V7zm-2-2v14h16V5H4zm5 3v8h6V8H9zm2 2h2v4h-2v-4z"/>
      <rect x="2" y="8" width="2" height="2"/>
      <rect x="2" y="12" width="2" height="2"/>
      <rect x="20" y="8" width="2" height="2"/>
      <rect x="20" y="12" width="2" height="2"/>
      <rect x="8" y="2" width="2" height="2"/>
      <rect x="12" y="2" width="2" height="2"/>
      <rect x="8" y="20" width="2" height="2"/>
      <rect x="12" y="20" width="2" height="2"/>
    </svg>`,
    // Neural network
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <circle cx="6" cy="6" r="2"/>
      <circle cx="18" cy="6" r="2"/>
      <circle cx="6" cy="18" r="2"/>
      <circle cx="18" cy="18" r="2"/>
      <circle cx="12" cy="12" r="3"/>
      <path d="M8 6l2.5 4.5M8 18l2.5-4.5M16 6l-2.5 4.5M16 18l-2.5-4.5"/>
    </svg>`,
    // Diamond
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M12 2l4 4-4 4-4-4 4-4zm6 6l4 4-4 4-4-4 4-4zM6 8l4 4-4 4-4-4 4-4zm6 6l4 4-4 4-4-4 4-4z"/>
    </svg>`,
    // Hexagon
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M17.5 3.5L22 12l-4.5 8.5h-11L2 12l4.5-8.5h11zm-1 2h-9L5 12l2.5 6.5h9L19 12l-2.5-6.5z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>`,
    // Star
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6-4.8-6 4.8 2.4-7.2-6-4.8h7.6z"/>
    </svg>`,
    // Lightning
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M13 2L4 14h7v7l9-11h-7V2z"/>
    </svg>`,
    // Crystal
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-full h-full">
      <path d="M12 1l8 5v12l-8 5-8-5V6l8-5zm0 2.5L6 8v8l6 3.5L18 16V8l-6-4.5zm0 3L8 10v4l4 2 4-2v-4l-4-3.5z"/>
    </svg>`
  ];
  
  // Get consistent values based on hash
  const colorIndex = Math.abs(hash) % colorSchemes.length;
  const iconIndex = Math.abs(hash >> 3) % avatarIcons.length;
  
  return {
    colors: colorSchemes[colorIndex],
    icon: avatarIcons[iconIndex]
  };
}

