import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../apiConfig';
import { Bar, Line, Pie } from 'react-chartjs-2';
import './NotebookCellsGlobal.css';

interface ChartImportModalProps {
  show: boolean;
  onClose: () => void;
  availableFiles: { filename: string; type: string }[];
  allCells: any[];
  onChartDataChange: (data: any) => void;
}

const PREVIEW_ROW_LIMIT = 200;

const ChartImportModal: React.FC<ChartImportModalProps> = ({
  show,
  onClose,
  availableFiles,
  allCells,
  onChartDataChange,
}) => {
  const [importStep, setImportStep] = useState<'select' | 'map' | 'done'>('select');
  const [importRaw, setImportRaw] = useState<any[] | null>(null);
  const [importColumns, setImportColumns] = useState<string[]>([]);
  const [labelCol, setLabelCol] = useState<string>('');
  const [valueCols, setValueCols] = useState<string[]>([]);
  const [importPreview, setImportPreview] = useState<any>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const [importChartType, setImportChartType] = useState<'bar' | 'line' | 'pie'>('bar');
  const [importColors, setImportColors] = useState<string[]>(['#1976d2', '#d2691e', '#27ae60', '#d81b60', '#fbc02d']);
  const [importLegendPos, setImportLegendPos] = useState<'top' | 'bottom' | 'left' | 'right'>('top');
  const [importTitle, setImportTitle] = useState<string>('');
  const [importStacked, setImportStacked] = useState(false);
  const [previewTruncated, setPreviewTruncated] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string>(availableFiles.length > 0 ? availableFiles[0].filename : '');
  const [selectedFileType, setSelectedFileType] = useState<string>(availableFiles.length > 0 ? availableFiles[0].type : '');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (importRaw && labelCol && valueCols.length > 0) {
      let dataRows = importRaw;
      let truncated = false;
      if (importRaw.length > PREVIEW_ROW_LIMIT) {
        dataRows = importRaw.slice(0, PREVIEW_ROW_LIMIT);
        truncated = true;
      }
      setPreviewTruncated(truncated);
      if (!dataRows[0] || !Object.prototype.hasOwnProperty.call(dataRows[0], labelCol)) {
        setImportError('Label column not found in data.');
        setImportPreview(null);
        return;
      }
      if (valueCols.length === 0) {
        setImportError('Please select at least one value column.');
        setImportPreview(null);
        return;
      }
      if (["bar", "line"].includes(importChartType)) {
        for (const col of valueCols) {
          if (!dataRows.every(row => typeof row[col] === 'number' || !isNaN(Number(row[col])))) {
            setImportError(`Column '${col}' contains non-numeric values, which are not supported for this chart type.`);
            setImportPreview(null);
            return;
          }
        }
      }
      const labelVals = dataRows.map(row => row[labelCol]);
      const labelSet = new Set(labelVals);
      if (labelVals.length !== labelSet.size) {
        setImportError('Warning: Duplicate label values detected. Chart may not render as expected.');
      }
      if (dataRows.some(row => valueCols.some(col => row[col] === undefined || row[col] === null || row[col] === ''))) {
        setImportError('Warning: Some value cells are empty or missing.');
      }
      const labelFreq: Record<string, number> = {};
      labelVals.forEach(l => { labelFreq[l] = (labelFreq[l] || 0) + 1; });
      const maxFreq = Math.max(...Object.values(labelFreq));
      if (maxFreq > dataRows.length * 0.5) {
        setImportError('Warning: One label occurs very frequently, which may distort the chart.');
      }
      const chartData = {
        labels: labelVals,
        datasets: valueCols.map((col, i) => ({
          label: col,
          data: dataRows.map(row => Number(row[col])),
          backgroundColor: importColors[i % importColors.length],
        }))
      };
      setImportPreview(chartData);
    }
  }, [importRaw, labelCol, valueCols, importChartType, importColors]);



  if (!show) return null;

  const handleClose = () => {
    setImportStep('select');
    setImportRaw(null);
    setImportPreview(null);
    setImportError(null);
    onClose();
  };

  // Helper to fetch and parse file data
  async function fetchFileData(filename: string, type: string) {
    setLoading(true);
    setImportError(null);
    try {
      const res = await fetch(getApiUrl(`files/${encodeURIComponent(filename)}`));
      if (!res.ok) {
        throw new Error('Failed to fetch file');
      }
      const text = await res.text();
      let rows: any[] = [];
      if (type === 'csv') {
        // Enhanced CSV parsing: auto-detect delimiter (tab, comma, semicolon, pipe)
        const [header, ...lines] = text.split('\n').map(l => l.trim()).filter(Boolean);
        const delimiters = ['\t', ',', ';', '|'];
        let delimiter = ',';
        let maxCount = 0;
        for (const d of delimiters) {
          const count = header.split(d).length - 1;
          if (count > maxCount) {
            maxCount = count;
            delimiter = d;
          }
        }
        const cols = header.split(delimiter);
        rows = lines.map(line => {
          const vals = line.split(delimiter);
          return Object.fromEntries(cols.map((c, i) => [c, vals[i]]));
        });
      } else if (type === 'xml') {
        // Minimal XML: not implemented, show error
        setImportError('XML import not yet implemented.');
        setLoading(false);
        return;
      }
      setImportRaw(rows);
      setImportColumns(rows.length ? Object.keys(rows[0]) : []);
      setImportStep('map');
    } catch (err: any) {
      setImportError(err.message || 'Failed to import file');
    }
    setLoading(false);
  }

  // Helper to extract data from chart cells
  function extractChartCellData(cellIdx: number) {
    setImportError(null);
    const cell = allCells?.[cellIdx];
    if (!cell || !cell.chartData) {
      setImportError('No chart data found in selected cell.');
      return;
    }
    let parsed;
    try {
      parsed = typeof cell.chartData === 'string' ? JSON.parse(cell.chartData) : cell.chartData;
    } catch {
      setImportError('Invalid chart data format in cell.');
      return;
    }
    // Convert Chart.js format to table rows
    if (!parsed.labels || !parsed.datasets) {
      setImportError('Chart data missing labels or datasets.');
      return;
    }
    const rows = parsed.labels.map((label: any, i: number) => {
      const row: any = { label };
      parsed.datasets.forEach((ds: any) => {
        row[ds.label || 'value'] = ds.data[i];
      });
      return row;
    });
    setImportRaw(rows);
    setImportColumns(rows.length ? Object.keys(rows[0]) : []);
    setImportStep('map');
  }

  // --- UI ---
  return (
    <div className="importModalBackdrop" onClick={handleClose}>
      <div className="importModal" onClick={e => e.stopPropagation()}>
        <button className="importModalClose" onClick={handleClose}>×</button>
        <h3>Import Data</h3>
        {importStep === 'select' && (
          <div style={{ minWidth: 320 }}>
            <div style={{ marginBottom: 12, fontWeight: 500 }}>Choose source:</div>
            <div style={{ marginBottom: 8 }}>
              <div style={{ fontWeight: 500, fontSize: 15, marginBottom: 6 }}>Files</div>
              {(availableFiles || []).length === 0 && <div style={{ color: '#888' }}>No files available.</div>}
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {(availableFiles || []).map(f => (
                  <li key={f.filename} style={{ marginBottom: 4 }}>
                    <button
                      className="chartImportButton"
                      style={{ background: '#16a085', fontSize: 14, padding: '3px 10px' }}
                      onClick={() => {
                        setSelectedFile(f.filename);
                        setSelectedFileType(f.type);
                        fetchFileData(f.filename, f.type);
                      }}
                      disabled={loading}
                    >
                      {f.type.toUpperCase()}: {f.filename}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
            <div style={{ marginBottom: 8 }}>
              <div style={{ fontWeight: 500, fontSize: 15, marginBottom: 6 }}>Other Chart Cells</div>
              {allCells?.filter((c, i) => c.chartData && c.chartType && c.chartData !== '' && c.chartData !== null).length === 0 && (
                <div style={{ color: '#888' }}>No chart cells with data.</div>
              )}
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {allCells?.map((c, i) => (
                  c.chartData && c.chartType && c.chartData !== '' && c.chartData !== null ? (
                    <li key={i} style={{ marginBottom: 4 }}>
                      <button
                        className="chartImportButton"
                        style={{ background: '#1976d2', fontSize: 14, padding: '3px 10px' }}
                        onClick={() => {
                          extractChartCellData(i);
                        }}
                        disabled={loading}
                      >
                        Chart Cell #{i + 1}
                      </button>
                    </li>
                  ) : null
                ))}
              </ul>
            </div>
            {importError && <div style={{ color: '#c0392b', marginTop: 10 }}>{importError}</div>}
          </div>
        )}
        {importStep === 'map' && (
          <div style={{ minWidth: 320 }}>
            <div style={{ marginBottom: 12, fontWeight: 500 }}>Map columns to chart fields:</div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ fontWeight: 500 }}>Label column:</label>
              <select
                value={labelCol}
                onChange={e => setLabelCol(e.target.value)}
                style={{ marginLeft: 8, fontSize: 15 }}
              >
                <option value="">(Choose column)</option>
                {importColumns.map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ fontWeight: 500 }}>Value columns:</label>
              <select
                multiple
                value={valueCols}
                onChange={e => {
                  const opts = Array.from(e.target.selectedOptions).map(o => o.value);
                  setValueCols(opts);
                }}
                style={{ marginLeft: 8, fontSize: 15, minHeight: 60 }}
              >
                {importColumns.filter(col => col !== labelCol).map(col => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ fontWeight: 500 }}>Chart type:</label>
              <select
                value={importChartType}
                onChange={e => setImportChartType(e.target.value as 'bar' | 'line' | 'pie')}
                style={{ marginLeft: 8, fontSize: 15 }}
              >
                <option value="bar">Bar</option>
                <option value="line">Line</option>
                <option value="pie">Pie</option>
              </select>
            </div>
            <button
              className="chartImportButton"
              style={{ background: 'var(--color-primary)', marginTop: 10, fontWeight: 600, color: 'var(--color-text-light)' }}
              disabled={!labelCol || valueCols.length === 0 || !importRaw}
              onClick={() => setImportStep('done')}
            >
              Preview Chart
            </button>
            <button
              className="chartImportButton"
              style={{ background: 'var(--color-disabled-text)', marginTop: 10, marginLeft: 8, color: 'var(--color-text-light)' }}
              onClick={() => setImportStep('select')}
            >
              Back
            </button>
            {importError && <div style={{ color: 'var(--color-error)', marginTop: 10 }}>{importError}</div>}
          </div>
        )}
        {importStep === 'done' && (
          <div style={{ minWidth: 320 }}>
            <div style={{ marginBottom: 10, fontWeight: 500 }}>Preview:</div>
            <div style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border-light)', borderRadius: 4, padding: 12, marginBottom: 12 }}>
              {importPreview ? (
                importChartType === 'bar' ? (
                  <Bar data={importPreview} />
                ) : importChartType === 'line' ? (
                  <Line data={importPreview} />
                ) : importChartType === 'pie' ? (
                  <Pie data={importPreview} />
                ) : null
              ) : <div style={{ color: 'var(--color-error)' }}>No preview available.</div>}
            </div>
            {importError && <div style={{ color: 'var(--color-error)', marginBottom: 10 }}>{importError}</div>}
            <button
              className="chartImportButton"
              style={{ background: 'var(--color-accent)', fontWeight: 600, color: 'var(--color-text-light)' }}
              disabled={!importPreview}
              onClick={() => {
                onChartDataChange && onChartDataChange(JSON.stringify(importPreview, null, 2));
                handleClose();
              }}
            >
              Import to Chart
            </button>
            <button
              className="chartImportButton"
              style={{ background: 'var(--color-disabled-text)', marginLeft: 8, color: 'var(--color-text-light)' }}
              onClick={() => setImportStep('map')}
            >
              Back
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartImportModal;
