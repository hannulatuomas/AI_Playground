// Tests for ChartGenerator
import { ChartGenerator } from '../src/main/services/ChartGenerator';

describe('ChartGenerator', () => {
  let chartGenerator: ChartGenerator;

  beforeEach(() => {
    chartGenerator = new ChartGenerator();
  });

  describe('Initialization', () => {
    test('should create chart generator with default dimensions', () => {
      expect(chartGenerator).toBeDefined();
    });

    test('should create chart generator with custom dimensions', () => {
      const customGenerator = new ChartGenerator(800, 600);
      expect(customGenerator).toBeDefined();
    });
  });

  describe('Line Chart Generation', () => {
    test('should generate line chart', async () => {
      const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May'];
      const datasets = [{
        label: 'Sales',
        data: [10, 20, 15, 25, 30],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
      }];

      const buffer = await chartGenerator.generateLineChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should generate multi-line chart', async () => {
      const labels = ['Q1', 'Q2', 'Q3', 'Q4'];
      const datasets = [
        {
          label: 'Revenue',
          data: [100, 150, 120, 180],
          borderColor: '#27ae60',
        },
        {
          label: 'Costs',
          data: [80, 90, 85, 95],
          borderColor: '#e74c3c',
        },
      ];

      const buffer = await chartGenerator.generateLineChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Bar Chart Generation', () => {
    test('should generate bar chart', async () => {
      const labels = ['Product A', 'Product B', 'Product C'];
      const datasets = [{
        label: 'Units Sold',
        data: [50, 75, 100],
        backgroundColor: '#3498db',
      }];

      const buffer = await chartGenerator.generateBarChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should generate bar chart with multiple datasets', async () => {
      const labels = ['Jan', 'Feb', 'Mar'];
      const datasets = [
        {
          label: 'Sales',
          data: [100, 120, 150],
          backgroundColor: '#27ae60',
        },
        {
          label: 'Returns',
          data: [10, 15, 12],
          backgroundColor: '#e74c3c',
        },
      ];

      const buffer = await chartGenerator.generateBarChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Pie Chart Generation', () => {
    test('should generate pie chart', async () => {
      const labels = ['Critical', 'High', 'Medium', 'Low', 'Info'];
      const data = [2, 5, 8, 12, 20];

      const buffer = await chartGenerator.generatePieChart(labels, data);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should generate pie chart with custom colors', async () => {
      const labels = ['A', 'B', 'C'];
      const data = [30, 40, 30];
      const colors = ['#ff0000', '#00ff00', '#0000ff'];

      const buffer = await chartGenerator.generatePieChart(labels, data, colors);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Doughnut Chart Generation', () => {
    test('should generate doughnut chart', async () => {
      const labels = ['Category 1', 'Category 2', 'Category 3'];
      const data = [40, 35, 25];

      const buffer = await chartGenerator.generateDoughnutChart(labels, data);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Security Trend Chart', () => {
    test('should generate security trend chart', async () => {
      const dates = ['2024-01', '2024-02', '2024-03', '2024-04'];
      const scores = [75, 80, 85, 90];

      const buffer = await chartGenerator.generateSecurityTrendChart(dates, scores);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Vulnerability Chart', () => {
    test('should generate vulnerability distribution chart', async () => {
      const summary = {
        critical: 2,
        high: 5,
        medium: 8,
        low: 12,
        info: 20,
      };

      const buffer = await chartGenerator.generateVulnerabilityChart(summary);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should handle zero vulnerabilities', async () => {
      const summary = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        info: 0,
      };

      const buffer = await chartGenerator.generateVulnerabilityChart(summary);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Performance Trend Chart', () => {
    test('should generate performance trend chart', async () => {
      const dates = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'];
      const responseTimes = [250, 300, 275, 320, 290];

      const buffer = await chartGenerator.generatePerformanceTrendChart(dates, responseTimes);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Multi-line Trend Chart', () => {
    test('should generate multi-line trend chart', async () => {
      const dates = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
      const datasets = [
        {
          label: 'Requests',
          data: [1000, 1200, 1100, 1300],
          color: '#3498db',
        },
        {
          label: 'Errors',
          data: [50, 45, 40, 35],
          color: '#e74c3c',
        },
      ];

      const buffer = await chartGenerator.generateMultiLineTrendChart(dates, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Severity Trend Chart', () => {
    test('should generate stacked severity trend chart', async () => {
      const dates = ['Sprint 1', 'Sprint 2', 'Sprint 3'];
      const criticalData = [3, 2, 1];
      const highData = [5, 4, 3];
      const mediumData = [8, 6, 5];
      const lowData = [12, 10, 8];

      const buffer = await chartGenerator.generateSeverityTrendChart(
        dates,
        criticalData,
        highData,
        mediumData,
        lowData
      );

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should handle all zero data', async () => {
      const dates = ['Day 1', 'Day 2'];
      const criticalData = [0, 0];
      const highData = [0, 0];
      const mediumData = [0, 0];
      const lowData = [0, 0];

      const buffer = await chartGenerator.generateSeverityTrendChart(
        dates,
        criticalData,
        highData,
        mediumData,
        lowData
      );

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle empty labels', async () => {
      const labels: string[] = [];
      const datasets = [{
        label: 'Empty',
        data: [],
      }];

      const buffer = await chartGenerator.generateLineChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
    });

    test('should handle single data point', async () => {
      const labels = ['Single'];
      const datasets = [{
        label: 'Data',
        data: [100],
      }];

      const buffer = await chartGenerator.generateLineChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });

    test('should handle large datasets', async () => {
      const labels = Array.from({ length: 100 }, (_, i) => `Point ${i + 1}`);
      const datasets = [{
        label: 'Large Dataset',
        data: Array.from({ length: 100 }, () => Math.random() * 100),
      }];

      const buffer = await chartGenerator.generateLineChart(labels, datasets);

      expect(buffer).toBeInstanceOf(Buffer);
      expect(buffer.length).toBeGreaterThan(0);
    });
  });
});
