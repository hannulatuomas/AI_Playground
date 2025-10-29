import './NotebookCellsGlobal.css';
import React, { useState } from 'react';
import { exportChartData, triggerFileDownload } from '../services/exportService';
import { ExportFormat, ExportOptions } from '../types';
import { Bar, Line, Pie } from 'react-chartjs-2';
// Uses global class names for all layout and visual elements, matching NotebookCell and other cells.

import type { ChartData, ChartOptions } from 'chart.js';

interface ChartCellProps {
  chartType: 'bar' | 'line' | 'pie';
  chartData: ChartData<'bar' | 'line' | 'pie'> | string;
  chartOptions?: ChartOptions<'bar' | 'line' | 'pie'>;
  onChartTypeChange?: (type: 'bar' | 'line' | 'pie') => void;
  onChartDataChange?: (data: ChartData<'bar' | 'line' | 'pie'> | string) => void;
  setShowImportModal: (show: boolean) => void;
}

const ChartCell: React.FC<ChartCellProps> = ({
  chartType,
  chartData,
  chartOptions,
  onChartTypeChange,
  onChartDataChange,
  setShowImportModal
}) => {
  // Export state
  const [exportFormat, setExportFormat] = useState<ExportFormat>(ExportFormat.JSON);
  const [exporting, setExporting] = useState(false);

  // Helper to convert chart data to QueryResult-like structure for export
  function chartDataToQueryResult(): any {
    try {
      const parsed = typeof chartData === 'string' ? JSON.parse(chartData) : chartData;
      if (!parsed || !parsed.labels || !parsed.datasets) return null;
      const columns = [parsed.labels ? 'Label' : '', ...parsed.datasets.map((ds: any) => ds.label || 'Dataset')];
      const rows = (parsed.labels || []).map((label: string, i: number) => [label, ...parsed.datasets.map((ds: any) => ds.data[i])]);
      return {
        columns: columns.map(name => ({ name, type: 'number', nullable: true })),
        rows,
        rowCount: rows.length,
      };
    } catch {
      return null;
    }
  }

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = chartDataToQueryResult();
      if (!result) throw new Error('Invalid chart data');
      const options: ExportOptions = {
        format: exportFormat,
        includeHeaders: true,
        prettyPrint: exportFormat === ExportFormat.JSON,
      };
      const blob = await exportChartData(result, options);
      const filename = `chart-data.${exportFormat}`;
      triggerFileDownload(blob, filename);
    } catch (err) {
      alert('Failed to export chart data: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="cellContainer">
      <div className="chartToolbar">
        <label className="chartLabel">Chart Type:</label>
        <select
          value={typeof chartType === 'string' ? chartType : 'bar'}
          onChange={e => onChartTypeChange && onChartTypeChange(e.target.value as 'bar' | 'line' | 'pie')}
          className="chartSelect"
          aria-label="Select chart type"
        >
          <option value="bar">Bar</option>
          <option value="line">Line</option>
          <option value="pie">Pie</option>
        </select>
        <div id="chart-type-desc" style={{ fontSize: 12, color: 'var(--color-disabled-text)', marginTop: 2 }}>
          Select the type of chart to display
        </div>
        <button
          className="chartImportButton"
          onClick={() => setShowImportModal(true)}
          type="button"
          aria-label="Import chart data"
        >
          Import Data
        </button>
        <select
          value={exportFormat}
          onChange={e => setExportFormat(e.target.value as ExportFormat)}
          style={{ marginLeft: 12, marginRight: 8, padding: '2px 8px', borderRadius: 4, border: '1px solid var(--color-border-accent)', fontSize: 14 }}
          aria-label="Select export format"
          aria-describedby="export-format-desc"
        >
          <option value={ExportFormat.JSON}>JSON</option>
          <option value={ExportFormat.CSV}>CSV</option>
          <option value={ExportFormat.XML}>XML</option>
        </select>
        <button
          onClick={handleExport}
          disabled={exporting || !chartDataToQueryResult()}
          style={{ background: 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '2px 12px', cursor: 'pointer', fontSize: 15 }}
          title="Export chart data"
          aria-label="Export chart data"
        >
          {exporting ? 'Exporting…' : 'Export'}
        </button>
      </div>
      <div style={{ marginBottom: 10 }}>
        <label className="chartLabel">Chart Data (JSON):</label>
        <textarea
          value={typeof chartData === 'string' ? chartData : (chartData ? JSON.stringify(chartData, null, 2) : '')}
          onChange={e => onChartDataChange && onChartDataChange(e.target.value)}
          rows={6}
          className="chartDataTextarea"
          placeholder='{"labels": ["A", "B"], "datasets": [{"label": "My Data", "data": [10, 20]}]}'
          aria-label="Chart data (JSON)"
          aria-describedby="chart-data-desc"
        />
        <div id="chart-data-desc" style={{ fontSize: 12, color: 'var(--color-disabled-text)', marginTop: 2 }}>
          Enter Chart.js compatible JSON. Example: {`{"labels": ["A", "B"], "datasets": [{"label": "My Data", "data": [10, 20]}]}`}
        </div>
      </div>
      <div className="chartDataContainer" role="region" aria-label="Chart preview area">
        {(() => {
          let parsed: any = null;
          try {
            parsed = typeof chartData === 'string' ? JSON.parse(chartData) : chartData;
          } catch (e) {
            return <div className="invalidJson" style={{ color: 'var(--color-error)' }}>Invalid JSON</div>;
          }
          if (!parsed || !parsed.labels || !parsed.datasets) {
            return <div className="invalidJson" style={{ color: 'var(--color-error)' }}>Provide valid Chart.js data structure</div>;
          }
          if (chartType === 'bar') {
            return <Bar data={parsed} options={chartOptions as ChartOptions<'bar'>} />;
          } else if (chartType === 'line') {
            return <Line data={parsed} options={chartOptions as ChartOptions<'line'>} />;
          } else if (chartType === 'pie') {
            return <Pie data={parsed} options={chartOptions as ChartOptions<'pie'>} />;
          } else {
            return <div style={{ color: 'var(--color-error)' }}>Unsupported chart type</div>;
          }
        })()}
      </div>
    </div>
  );
};

export default ChartCell;
