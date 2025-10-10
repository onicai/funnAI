import { theme } from "../stores/store";
import { get } from "svelte/store";

export interface ChartTheme {
  backgroundColor: string;
  textColor: string;
  gridColor: string;
  borderColor: string;
  primaryColor: string;
  secondaryColor: string;
  accentColors: string[];
}

/**
 * Get theme-aware colors for charts
 */
export function getChartTheme(): ChartTheme {
  const currentTheme = get(theme);
  const isDark = currentTheme === 'dark';

  return {
    backgroundColor: isDark ? '#1f2937' : '#ffffff',
    textColor: isDark ? '#f9fafb' : '#111827',
    gridColor: isDark ? '#374151' : '#e5e7eb',
    borderColor: isDark ? '#4b5563' : '#d1d5db',
    primaryColor: isDark ? '#8b5cf6' : '#7c3aed',
    secondaryColor: isDark ? '#06b6d4' : '#0891b2',
    accentColors: isDark 
      ? ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899']
      : ['#7c3aed', '#0891b2', '#059669', '#d97706', '#dc2626', '#db2777']
  };
}

/**
 * Common chart options with theme support
 */
export function getBaseChartOptions(isDark: boolean = false) {
  const chartTheme = getChartTheme();
  
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: chartTheme.textColor,
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#ffffff',
        titleColor: chartTheme.textColor,
        bodyColor: chartTheme.textColor,
        borderColor: chartTheme.borderColor,
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        mode: 'index' as const,
        intersect: false
      }
    },
    scales: {
      x: {
        ticks: {
          color: chartTheme.textColor,
          font: {
            size: 11
          }
        },
        grid: {
          color: chartTheme.gridColor,
          drawBorder: false
        }
      },
      y: {
        ticks: {
          color: chartTheme.textColor,
          font: {
            size: 11
          }
        },
        grid: {
          color: chartTheme.gridColor,
          drawBorder: false
        }
      }
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };
}

/**
 * Format number for chart display
 */
export function formatChartNumber(value: number, type: 'default' | 'percentage' | 'currency' | 'cycles' = 'default'): string {
  switch (type) {
    case 'percentage':
      return `${value.toFixed(1)}%`;
    case 'currency':
      return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    case 'cycles':
      if (value >= 1e12) return `${(value / 1e12).toFixed(1)}T`;
      if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
      if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
      if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
      return value.toString();
    default:
      return value.toLocaleString();
  }
}

/**
 * Generate gradient for chart backgrounds
 */
export function createGradient(ctx: CanvasRenderingContext2D, color: string, alpha: number = 0.2): CanvasGradient {
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, color + Math.floor(alpha * 255).toString(16).padStart(2, '0'));
  gradient.addColorStop(1, color + '00');
  return gradient;
}

/**
 * Format date for chart labels
 */
export function formatDateLabel(dateString: string, format: 'short' | 'medium' | 'long' = 'medium'): string {
  const date = new Date(dateString);
  
  switch (format) {
    case 'short':
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    case 'long':
      return date.toLocaleDateString(undefined, { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    case 'medium':
    default:
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }
}

/**
 * Generate colors for pie/doughnut charts
 */
export function generatePieColors(count: number): string[] {
  const chartTheme = getChartTheme();
  const colors = [];
  
  for (let i = 0; i < count; i++) {
    colors.push(chartTheme.accentColors[i % chartTheme.accentColors.length]);
  }
  
  return colors;
}

/**
 * Create chart dataset with theme-aware styling
 */
export function createDataset(
  label: string,
  data: number[],
  color: string,
  type: 'line' | 'bar' | 'area' = 'line'
) {
  const chartTheme = getChartTheme();
  
  const baseConfig = {
    label,
    data,
    borderColor: color,
    backgroundColor: type === 'area' ? color + '20' : color,
    borderWidth: 2,
    tension: 0.4,
    pointBackgroundColor: color,
    pointBorderColor: chartTheme.backgroundColor,
    pointBorderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
  };

  if (type === 'bar') {
    return {
      ...baseConfig,
      backgroundColor: color + '80',
      borderRadius: 4,
      tension: 0
    };
  }

  if (type === 'area') {
    return {
      ...baseConfig,
      fill: true,
      backgroundColor: color + '20',
    };
  }

  return baseConfig;
}
