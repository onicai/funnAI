import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  LineController,
  BarController,
  DoughnutController
} from 'chart.js';

let isRegistered = false;

/**
 * Register Chart.js components globally
 * This should be called once at app startup
 */
export function initializeChartJS() {
  if (isRegistered) {
    return;
  }

  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    Filler,
    LineController,
    BarController,
    DoughnutController
  );

  isRegistered = true;
  console.log('Chart.js components registered successfully');
}

/**
 * Check if Chart.js is properly initialized
 */
export function isChartJSInitialized(): boolean {
  return isRegistered;
}
