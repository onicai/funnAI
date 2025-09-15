# Dashboard Chart Components

This directory contains the new chart-based dashboard components for displaying daily metrics data from the funnAI canister.

## Overview

The dashboard provides real-time visualization of mAIner activity, system metrics, and tier distribution using Chart.js with Svelte integration. All components are theme-aware and support both light and dark modes.

## Components

### Core Components

1. **MetricsDashboard.svelte** - Main dashboard component that orchestrates all charts
2. **MainerMetricsChart.svelte** - Line chart showing mAIner activity over time
3. **TierDistributionChart.svelte** - Doughnut chart showing current tier distribution
4. **SystemMetricsChart.svelte** - Bar/line combo chart for system performance metrics
5. **TimeFilterSelector.svelte** - Time filter controls (15 days, 1 month, all time)

### Helper Services

1. **DailyMetricsService.ts** - Service for fetching and caching daily metrics data
2. **chartUtils.ts** - Utilities for theme-aware chart styling and formatting

## Data Structure

The components consume data from the `getDailyMetrics` canister method with the following structure:

```typescript
interface DailyMetricsData {
  metadata: {
    updated_at: string;
    date: string;
    created_at: string;
  };
  mainers: {
    totals: {
      created: number;
      active: number;
      total_cycles: number;
      paused: number;
    };
    breakdown_by_tier: {
      active: { low: number; high: number; very_high: number; medium: number; };
      paused: { low: number; high: number; very_high: number; medium: number; };
    };
  };
  derived_metrics: {
    avg_cycles_per_mainer: number;
    paused_percentage: number;
    tier_distribution: {
      low: number; high: number; very_high: number; medium: number;
    };
    burn_rate_per_active_mainer: number;
    active_percentage: number;
  };
  system_metrics: {
    funnai_index: number;
    daily_burn_rate: {
      usd: number;
      cycles: number;
    };
  };
}
```

## Features

### Performance Optimizations

- **Caching**: 5-minute cache for API responses to reduce canister calls
- **Lazy Loading**: Charts load data independently and asynchronously
- **Efficient Updates**: Components only re-fetch when time filters change
- **Background Refresh**: Auto-refresh every 5 minutes for real-time data

### Time Filters

- **15 Days**: Last 15 days of data
- **1 Month**: Last 30 days of data
- **All Time**: All available historical data

### Theme Support

- **Automatic Theme Detection**: Charts adapt to light/dark theme changes
- **Theme-Aware Colors**: Consistent color palette across themes
- **Responsive Design**: Works on desktop and mobile devices

### Chart Types

1. **Line Charts**: Time series data for mAIner activity trends
2. **Doughnut Charts**: Proportional data for tier distribution
3. **Bar Charts**: Comparative metrics like burn rates and system performance
4. **Combo Charts**: Mixed bar/line charts for multi-scale data

## Usage

### Basic Integration

```svelte
<script>
  import MetricsDashboard from '../components/dashboard/MetricsDashboard.svelte';
</script>

<MetricsDashboard title="Daily Metrics Dashboard" />
```

### Individual Components

```svelte
<script>
  import MainerMetricsChart from '../components/dashboard/MainerMetricsChart.svelte';
  import TierDistributionChart from '../components/dashboard/TierDistributionChart.svelte';
</script>

<MainerMetricsChart timeFilter="1month" />
<TierDistributionChart showLatestOnly={true} />
```

## API Integration

The components call the canister method:

```bash
dfx canister --ic call p6pu7-5aaaa-aaaap-qqdfa-cai getDailyMetrics '(opt record {
  start_date=opt "2025-09-01"; 
  end_date=opt "2025-09-13";
  limit=null
})'
```

### Query Parameters

- `start_date`: Optional start date in YYYY-MM-DD format
- `end_date`: Optional end date in YYYY-MM-DD format  
- `limit`: Optional limit on number of records returned

## Error Handling

- **Network Errors**: Graceful fallback with error messages
- **Data Validation**: Type-safe data transformation
- **Loading States**: Skeleton loaders during data fetching
- **Cache Management**: Automatic cache invalidation and refresh

## Styling

All components use Tailwind CSS classes and are fully responsive:

- **Mobile First**: Optimized for mobile devices
- **Flexible Grid**: Responsive grid layouts
- **Dark Mode**: Full dark mode support
- **Accessibility**: ARIA labels and keyboard navigation

## Dependencies

- `chart.js`: Core charting library
- `svelte-chartjs`: Svelte wrapper for Chart.js
- `tailwindcss`: Utility-first CSS framework

## Browser Compatibility

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Development Notes

### TypeScript Warnings

The components may show TypeScript warnings related to svelte-chartjs type definitions. These are cosmetic and don't affect functionality. The build process completes successfully.

### Performance Considerations

- Charts are rendered client-side using Canvas
- Large datasets (>100 data points) may impact performance
- Consider implementing data pagination for very large time ranges

### Future Enhancements

- Export chart data to CSV/JSON
- More granular time filters (hourly, weekly)
- Real-time WebSocket updates
- Custom chart color themes
- Interactive drill-down capabilities
