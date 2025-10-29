// Chart Generator Service using chartjs-to-image (pure JavaScript, no native dependencies)
import ChartJsImage from 'chartjs-to-image';
import type { ChartData } from '../../types/report';

export class ChartGenerator {
  private width: number;
  private height: number;

  constructor(width: number = 600, height: number = 400) {
    this.width = width;
    this.height = height;
  }

  /**
   * Generate line chart for trends
   */
  async generateLineChart(
    labels: string[],
    datasets: Array<{
      label: string;
      data: number[];
      borderColor?: string;
      backgroundColor?: string;
    }>
  ): Promise<Buffer> {
    const chart = new ChartJsImage();
    chart.setConfig({
      type: 'line',
      data: {
        labels,
        datasets: datasets.map(ds => ({
          label: ds.label,
          data: ds.data,
          borderColor: ds.borderColor || '#3498db',
          backgroundColor: ds.backgroundColor || 'rgba(52, 152, 219, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        })),
      },
      options: {
        responsive: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
    chart.setWidth(this.width).setHeight(this.height).setBackgroundColor('white');
    return await chart.toBinary();
  }

  /**
   * Generate bar chart
   */
  async generateBarChart(
    labels: string[],
    datasets: Array<{
      label: string;
      data: number[];
      backgroundColor?: string | string[];
    }>
  ): Promise<Buffer> {
    const chart = new ChartJsImage();
    chart.setConfig({
      type: 'bar',
      data: {
        labels,
        datasets: datasets.map(ds => ({
          label: ds.label,
          data: ds.data,
          backgroundColor: ds.backgroundColor || '#3498db',
          borderWidth: 1,
        })),
      },
      options: {
        responsive: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    });
    chart.setWidth(this.width).setHeight(this.height).setBackgroundColor('white');
    return await chart.toBinary();
  }

  /**
   * Generate pie chart
   */
  async generatePieChart(
    labels: string[],
    data: number[],
    backgroundColor?: string[]
  ): Promise<Buffer> {
    const defaultColors = [
      '#e74c3c', // Critical - Red
      '#e67e22', // High - Orange
      '#f39c12', // Medium - Yellow
      '#3498db', // Low - Blue
      '#95a5a6', // Info - Gray
    ];

    const chart = new ChartJsImage();
    chart.setConfig({
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: backgroundColor || defaultColors.slice(0, data.length),
          borderWidth: 1,
          borderColor: '#ffffff',
        }],
      },
      options: {
        responsive: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
          },
        },
      },
    });
    chart.setWidth(this.width).setHeight(this.height).setBackgroundColor('white');
    return await chart.toBinary();
  }

  /**
   * Generate doughnut chart
   */
  async generateDoughnutChart(
    labels: string[],
    data: number[],
    backgroundColor?: string[]
  ): Promise<Buffer> {
    const defaultColors = [
      '#e74c3c', '#e67e22', '#f39c12', '#3498db', '#95a5a6',
      '#27ae60', '#9b59b6', '#34495e', '#16a085', '#d35400'
    ];

    const chart = new ChartJsImage();
    chart.setConfig({
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: backgroundColor || defaultColors.slice(0, data.length),
          borderWidth: 2,
          borderColor: '#ffffff',
        }],
      },
      options: {
        responsive: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
          },
        },
      },
    });
    chart.setWidth(this.width).setHeight(this.height).setBackgroundColor('white');
    return await chart.toBinary();
  }

  /**
   * Generate security score trend chart
   */
  async generateSecurityTrendChart(
    dates: string[],
    scores: number[]
  ): Promise<Buffer> {
    return await this.generateLineChart(dates, [{
      label: 'Security Score',
      data: scores,
      borderColor: '#27ae60',
      backgroundColor: 'rgba(39, 174, 96, 0.1)',
    }]);
  }

  /**
   * Generate vulnerability distribution chart
   */
  async generateVulnerabilityChart(summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  }): Promise<Buffer> {
    return await this.generatePieChart(
      ['Critical', 'High', 'Medium', 'Low', 'Info'],
      [summary.critical, summary.high, summary.medium, summary.low, summary.info],
      ['#e74c3c', '#e67e22', '#f39c12', '#3498db', '#95a5a6']
    );
  }

  /**
   * Generate performance trend chart
   */
  async generatePerformanceTrendChart(
    dates: string[],
    responseTimes: number[]
  ): Promise<Buffer> {
    return await this.generateLineChart(dates, [{
      label: 'Avg Response Time (ms)',
      data: responseTimes,
      borderColor: '#3498db',
      backgroundColor: 'rgba(52, 152, 219, 0.1)',
    }]);
  }

  /**
   * Generate multi-line trend chart
   */
  async generateMultiLineTrendChart(
    dates: string[],
    datasets: Array<{
      label: string;
      data: number[];
      color: string;
    }>
  ): Promise<Buffer> {
    return await this.generateLineChart(
      dates,
      datasets.map(ds => ({
        label: ds.label,
        data: ds.data,
        borderColor: ds.color,
        backgroundColor: `${ds.color}20`, // Add transparency
      }))
    );
  }

  /**
   * Generate stacked bar chart for severity trends
   */
  async generateSeverityTrendChart(
    dates: string[],
    criticalData: number[],
    highData: number[],
    mediumData: number[],
    lowData: number[]
  ): Promise<Buffer> {
    const chart = new ChartJsImage();
    chart.setConfig({
      type: 'bar',
      data: {
        labels: dates,
        datasets: [
          {
            label: 'Critical',
            data: criticalData,
            backgroundColor: '#e74c3c',
          },
          {
            label: 'High',
            data: highData,
            backgroundColor: '#e67e22',
          },
          {
            label: 'Medium',
            data: mediumData,
            backgroundColor: '#f39c12',
          },
          {
            label: 'Low',
            data: lowData,
            backgroundColor: '#3498db',
          },
        ],
      },
      options: {
        responsive: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
          },
        },
        scales: {
          x: {
            stacked: true,
          },
          y: {
            stacked: true,
            beginAtZero: true,
          },
        },
      },
    });
    chart.setWidth(this.width).setHeight(this.height).setBackgroundColor('white');
    return await chart.toBinary();
  }
}

// Singleton instance
let chartGeneratorInstance: ChartGenerator | null = null;

export function getChartGenerator(): ChartGenerator {
  if (!chartGeneratorInstance) {
    chartGeneratorInstance = new ChartGenerator();
  }
  return chartGeneratorInstance;
}
