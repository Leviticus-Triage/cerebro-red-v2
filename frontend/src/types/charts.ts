/**
 * Chart data type definitions for Recharts visualizations.
 */

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: any;
}

export interface ScatterDataPoint {
  x: number;
  y: number;
  severity?: string;
  strategy?: string;
  title?: string;
  [key: string]: any;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  label?: string;
  [key: string]: any;
}

