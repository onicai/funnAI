/**
 * Mainer Visual Identity Utilities
 *
 * Deterministic Pixeloids avatars keyed by mAIner canister ID.
 * @see https://github.com/nicolasleao/pixeloids
 */

import { createSvg, getMetadata } from 'pixeloids';

export interface MainerVisualIdentity {
  colors: {
    bg: string;
    bgHover: string;
    accent: string;
    icon: string;
    text: string;
    border: string;
  };
  /** Full Pixeloids SVG markup (safe to render with {@html}) */
  icon: string;
  /** Pixeloids palette name for this seed */
  palette: string;
}

/** Soft UI tint schemes (still used for card glows / chips — avatar itself is Pixeloids) */
const colorSchemes = [
  {
    bg: 'from-purple-500 to-indigo-600',
    bgHover: 'from-purple-600 to-indigo-700',
    accent: 'bg-purple-100/30',
    icon: 'text-purple-100',
    text: 'text-purple-50',
    border: 'border-purple-400/30',
  },
  {
    bg: 'from-emerald-500 to-teal-600',
    bgHover: 'from-emerald-600 to-teal-700',
    accent: 'bg-emerald-100/30',
    icon: 'text-emerald-100',
    text: 'text-emerald-50',
    border: 'border-emerald-400/30',
  },
  {
    bg: 'from-blue-500 to-cyan-600',
    bgHover: 'from-blue-600 to-cyan-700',
    accent: 'bg-blue-100/30',
    icon: 'text-blue-100',
    text: 'text-blue-50',
    border: 'border-blue-400/30',
  },
  {
    bg: 'from-rose-500 to-pink-600',
    bgHover: 'from-rose-600 to-pink-700',
    accent: 'bg-rose-100/30',
    icon: 'text-rose-100',
    text: 'text-rose-50',
    border: 'border-rose-400/30',
  },
  {
    bg: 'from-amber-500 to-orange-600',
    bgHover: 'from-amber-600 to-orange-700',
    accent: 'bg-amber-100/30',
    icon: 'text-amber-100',
    text: 'text-amber-50',
    border: 'border-amber-400/30',
  },
  {
    bg: 'from-violet-500 to-purple-600',
    bgHover: 'from-violet-600 to-purple-700',
    accent: 'bg-violet-100/30',
    icon: 'text-violet-100',
    text: 'text-violet-50',
    border: 'border-violet-400/30',
  },
  {
    bg: 'from-teal-500 to-cyan-600',
    bgHover: 'from-teal-600 to-cyan-700',
    accent: 'bg-teal-100/30',
    icon: 'text-teal-100',
    text: 'text-teal-50',
    border: 'border-teal-400/30',
  },
  {
    bg: 'from-indigo-500 to-blue-600',
    bgHover: 'from-indigo-600 to-blue-700',
    accent: 'bg-indigo-100/30',
    icon: 'text-indigo-100',
    text: 'text-indigo-50',
    border: 'border-indigo-400/30',
  },
];

function hashId(agentId: string): number {
  let hash = 0;
  for (let i = 0; i < agentId.length; i++) {
    hash = (hash << 5) - hash + agentId.charCodeAt(i);
    hash = hash & hash;
  }
  return Math.abs(hash);
}

/**
 * Generate consistent visual identity for each mAIner based on its ID.
 * Avatar SVG is a deterministic Pixeloids monster seeded by the canister ID.
 */
export function getMainerVisualIdentity(agentId: string): MainerVisualIdentity {
  const seed = agentId || 'funnai-mainer';
  const metadata = getMetadata(seed, { variant: 'monster' });
  const icon = createSvg(seed, {
    size: 128,
    variant: 'monster',
    background: true,
  });

  const colorIndex = hashId(seed) % colorSchemes.length;

  return {
    colors: colorSchemes[colorIndex],
    icon,
    palette: metadata?.palette ?? 'default',
  };
}
