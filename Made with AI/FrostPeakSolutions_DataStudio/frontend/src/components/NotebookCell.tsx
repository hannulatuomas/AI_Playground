import React, { useRef, useEffect, useState } from 'react';
import { Bar, Line, Pie } from 'react-chartjs-2';
import CellResultsTable from './CellResultsTable';
import NotebookCellOutput from './NotebookCellOutput';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Title, Tooltip, Legend);
import ReactMarkdown from 'react-markdown';
import Editor from 'react-simple-code-editor';
import { FieldTooltip } from './FieldTooltip';
import SQLAutocompleteDropdown from './SQLAutocompleteDropdown';
import './NotebookCellsGlobal.css';
import NotebookCellFileSchemaPreview from './NotebookCellFileSchemaPreview';
import { cellContent, fileSelectorRow, fileSelector, fileSchemaStatus, fileSchemaPreview } from './NotebookCell.styles';
const Prism = require('prismjs');
require('prismjs/components/prism-sql');
require('prismjs/themes/prism.css');

export type CellType = 'sql' | 'markdown' | 'chart' | 'mongodb' | 'neo4j' | 'schema'; // JSON supported as data source

import NotebookCellSQL from './NotebookCellSQL';
import { MongoDBCell } from './MongoDBCell';
import { Neo4jCell } from './Neo4jCell';
import MarkdownCell from './MarkdownCell';
import ChartCell from './ChartCell';
import ChartImportModal from './ChartImportModal';
import SchemaCell from './SchemaCell';


import { DBConnection } from './ConnectionContext';
import { useSchema } from './useSchema';
import { useFileContext } from './FileContext';
import SchemaStatusBadge from './SchemaStatusBadge';

interface NotebookCellProps {
  cellId: string;
  type: CellType;
  value: string;
  onChange: (val: string) => void;
  onRun?: () => void;
  onDelete: () => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  executing?: boolean;
  result?: any[];
  error?: string | null;
  connections?: DBConnection[];
  uid?: string | null;
  onUidChange?: (uid: string | null) => void;
  onFocus?: () => void;
  chartType?: 'bar' | 'line' | 'pie';
  chartData?: any;
  chartOptions?: any;
  onChartTypeChange?: (type: 'bar' | 'line' | 'pie') => void;
  onChartDataChange?: (data: any) => void;
  title?: string;
  onTitleChange?: (title: string) => void;
  addToGroupDropdown?: React.ReactNode;
  removeFromGroupButton?: React.ReactNode;
  removeFromGroupButtonInToolbar?: React.ReactNode;
  onDuplicate?: () => void;
  onClearOutput?: () => void;
  paramValues?: { [key: string]: string };
  onParamValuesChange?: (paramValues: { [key: string]: string }) => void;
  onVisualizeResult?: (data: any[]) => void;
  allCells?: any[];
  /** Unique fileId for file-backed cells (CSV, XML, JSON) */
  fileId?: string;
}

interface ParamChangeHandler {
  (paramValues: { [key: string]: string }): void;
}

import SchemaUnconfirmedBanner from './SchemaUnconfirmedBanner';
import CellStatusIndicators from './CellStatusIndicators';

export default function NotebookCell({
  cellId,
  type, value, onChange, onRun, onDelete, collapsed, onToggleCollapse, executing, result, error,
  addToGroupDropdown,
  removeFromGroupButton,
  removeFromGroupButtonInToolbar,
  connections, uid, onUidChange, onDuplicate, onClearOutput, paramValues, onParamValuesChange, onFocus,
  chartType, chartData, chartOptions, onChartTypeChange, onChartDataChange,
  title, onTitleChange,
  addToGroupDropdown: addToGroupDropdownProp,
  removeFromGroupButton: removeFromGroupButtonProp,
  removeFromGroupButtonInToolbar: removeFromGroupButtonInToolbarProp,
  onVisualizeResult,
  allCells,
  fileId,
  onFileIdChange
}: NotebookCellProps & { onFileIdChange?: (id: string) => void }) {
  const [sqlValidationError, setSqlValidationError] = useState<string | null>(null);
  const [showSqlHelp, setShowSqlHelp] = useState(false);

  // File-backed cell logic: always use fileId for all file operations and schema preview
  const { files, schemaStatus } = useFileContext();
  const file = fileId ? files.find(f => f.id === fileId) : undefined;
  const isFileBacked = !!file && ['csv', 'xml', 'json'].includes(file.type);
  const cellSchemaStatus = isFileBacked ? (schemaStatus[fileId!] || 'unconfirmed') : undefined;

  function validateSql(sql: string): string | null {
    if (!sql.trim()) return 'SQL query cannot be empty.';
    // Basic SQL structure check (must contain SELECT/INSERT/UPDATE/DELETE/CREATE/DROP/ALTER)
    if (!/\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b/i.test(sql)) {
      return 'Query should start with a valid SQL command (SELECT, INSERT, etc).';
    }
    return null;
  }

  // Intercept Run (Ctrl+Enter, button, etc) for SQL cells
  function handleRunWithValidation() {
    if (type === 'sql') {
      const err = validateSql(value);
      setSqlValidationError(err);
      if (err) return;
    }
    if (onRun) onRun();
  }

  // Patch keydown for SQL cells to validate on Ctrl+Enter
  function handleEditorKeyDownWithValidation(e: React.KeyboardEvent) {
    if (type === 'sql' && (e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleRunWithValidation();
    } else {
      handleEditorKeyDown?.(e);
    }
  }

  // Reset error on edit
  useEffect(() => {
    if (type === 'sql') setSqlValidationError(null);
    // eslint-disable-next-line
  }, [value, type]);
  // Determine if this is a file-backed cell type
  // (Already declared above: const { schemaStatus } = useFileContext(); and const isFileBacked = !!fileId;)
  // Use 'files' from context if needed, but do not redeclare 'schemaStatus' or 'isFileBacked'.

  const currentFile = isFileBacked ? files.find(f => f.id === fileId) : undefined;
  const currentStatus = fileId && schemaStatus[fileId] ? schemaStatus[fileId] : 'unconfirmed';
  function getStatusColor(status: string) {
    switch (status) {
      case 'confirmed': return '#388e3c';
      case 'editing': return '#fbc02d';
      default: return '#b71c1c';
    }
  }
  function getStatusText(status: string) {
    switch (status) {
      case 'confirmed': return 'Schema Confirmed';
      case 'editing': return 'Editing Schema';
      default: return 'Schema Unconfirmed';
    }
  }
  // Ensure uid is defined from props
  const currentUid = uid ?? null;
  const handleDuplicate = () => {
    if (onDuplicate) {
      onDuplicate();
    }
  };
  // Suggestion refs for autocomplete dropdown
  const suggestionRefs = useRef<(HTMLLIElement | null)[]>([]);



  // --- Autocomplete logic ---

// Autocomplete state for SQL editor
const [showAutocomplete, setShowAutocomplete] = useState(false);
const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
const [activeSuggestion, setActiveSuggestion] = useState(0);

// Helper: get word before cursor
function getCurrentWord(val: string, cursor: number) {
  const left = val.slice(0, cursor);
  const match = left.match(/([\w.]+)$/);
  return match ? match[1] : '';
}

function handleEditorChange(val: string) {
  onChange(val);
  // Only show autocomplete for SQL cells
  if (type === 'sql') {
    const textarea = getSqlTextarea();
    const cursor = textarea ? textarea.selectionStart : val.length;
    const word = getCurrentWord(val, cursor);
    if (word.length > 0) {
      const all = getSuggestions();
      const filtered = all.filter(s => s.toLowerCase().includes(word.toLowerCase()));
      setFilteredSuggestions(filtered);
      setShowAutocomplete(filtered.length > 0);
      setActiveSuggestion(0);
    } else {
      setShowAutocomplete(false);
      setFilteredSuggestions([]);
    }
  }
}

function handleEditorKeyDown(e: React.KeyboardEvent) {
  if (!showAutocomplete || filteredSuggestions.length === 0) return;
  if (e.key === 'ArrowDown') {
    setActiveSuggestion(a => Math.min(a + 1, filteredSuggestions.length - 1));
    e.preventDefault();
  } else if (e.key === 'ArrowUp') {
    setActiveSuggestion(a => Math.max(a - 1, 0));
    e.preventDefault();
  } else if (e.key === 'Enter' && filteredSuggestions[activeSuggestion]) {
    handleSuggestionClick(filteredSuggestions[activeSuggestion]);
    e.preventDefault();
  } else if (e.key === 'Escape') {
    setShowAutocomplete(false);
    e.preventDefault();
  }
}

function handleSuggestionClick(s: string) {
  // Insert suggestion at cursor position
  const textarea = getSqlTextarea();
  if (!textarea) return;
  const cursor = textarea.selectionStart || value.length;
  const word = getCurrentWord(value, cursor);
  const before = value.slice(0, cursor - word.length);
  const after = value.slice(cursor);
  const newValue = before + s + ' ' + after;
  onChange(newValue);
  setShowAutocomplete(false);
  setFilteredSuggestions([]);
  setActiveSuggestion(0);
  setTimeout(() => {
    // Move cursor to after inserted suggestion
    const textarea = getSqlTextarea();
    if (textarea) {
      textarea.selectionStart = textarea.selectionEnd = before.length + s.length + 1;
      textarea.focus();
    }
  }, 0);
}


  const SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET', 'HAVING', 'DISTINCT', 'UNION', 'ALL', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'DATABASE', 'VIEW', 'INDEX', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'VALUES', 'SET', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'LIKE', 'BETWEEN', 'EXISTS', 'COUNT', 'MIN', 'MAX', 'AVG', 'SUM', 'DESC', 'ASC'
  ];
  // Fetch schema for current connection
  const { tables: schemaTables } = useSchema(currentUid);

  function getSuggestions() {
    let sugg: string[] = [...SQL_KEYWORDS];
    // Add table and column names from schema
    if (schemaTables && schemaTables.length) {
      // schemaTables: DbTableSchema[]; columns: DbColumnSchema[]
      sugg = sugg.concat(schemaTables.map((t) => t.table));
      sugg = sugg.concat(schemaTables.flatMap((t) => t.columns.map(col => typeof col === 'string' ? col : col.name)));
    }
    return Array.from(new Set(sugg));
  }
  function insertSuggestion(s: string) {
    // Insert suggestion at cursor position in textarea
    // For simplicity, replace last word
    const parts = value.split(/\s|,|\(|\)/);
    const last = parts.pop();
    const before = value.slice(0, value.length - (last?.length || 0));
    onChange(before + s + ' ');
  }
  const [focused, setFocused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  // Helper to get the SQL editor's textarea DOM node
  function getSqlTextarea(): HTMLTextAreaElement | null {
    return document.getElementById(`notebook-cell-sql-${cellId}`) as HTMLTextAreaElement | null;
  }
  const editorRef = useRef<any>(null);

  // Keyboard shortcuts for navigation and actions
  useEffect(() => {
    if (!focused) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && type === 'sql' && onRun) {
        onRun();
        e.preventDefault();
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'd' && onDuplicate) {
        handleDuplicate();
        e.preventDefault();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'l' && onClearOutput) {
        onClearOutput();
        e.preventDefault();
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'm' && onToggleCollapse) {
        onToggleCollapse();
        e.preventDefault();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [focused, type, onRun, onDuplicate, onClearOutput, onToggleCollapse, handleDuplicate]);

  return (
    <div
      style={{
        border: '1px solid var(--color-border-light)',
        borderRadius: 8,
        margin: '18px 0',
        background: focused ? 'var(--color-bg-secondary)' : 'var(--color-bg)',
        boxShadow: focused ? '0 2px 12px var(--color-shadow-focus)' : 'none',
        transition: 'box-shadow 0.2s',
        position: 'relative',
        overflow: 'visible',
        width: '100%',
        maxWidth: '100%',
      }}
      tabIndex={0}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Unified title bar and toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'var(--color-bg-tertiary)',
        borderBottom: '1px solid var(--color-border-light)',
        padding: '6px 12px',
        borderTopLeftRadius: 7,
        borderTopRightRadius: 7,
        width: '100%',
        boxSizing: 'border-box',
        minWidth: 0
      }}>
        <div style={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
          <span className={type === 'schema' ? 'schemaLabel' : undefined} style={{ fontWeight: 600, color: type === 'sql' ? 'var(--color-primary)' : type === 'chart' ? 'var(--color-accent)' : type === 'schema' ? undefined : 'var(--color-secondary)', whiteSpace: 'nowrap' }}>{type === 'sql' ? 'SQL' : type === 'chart' ? 'Chart' : type === 'schema' ? 'Schema' : 'Markdown'}</span>
          <input
            type="text"
            value={typeof title === 'string' ? title : ''}
            onChange={e => onTitleChange && onTitleChange(e.target.value)}
            placeholder="Add title..."
            style={{
              marginLeft: 14,
              fontWeight: 600,
              fontSize: 15,
              border: 'none',
              background: 'transparent',
              outline: 'none',
              color: 'var(--color-text-primary)',
              minWidth: 40,
              flex: 1
            }}
            maxLength={40}
          />
          {addToGroupDropdown}
        </div>
        {/* Toolbar, including remove from group button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          {removeFromGroupButtonInToolbar && React.cloneElement(removeFromGroupButtonInToolbar as React.ReactElement, { style: { ...((removeFromGroupButtonInToolbar as React.ReactElement).props.style || {}), height: 32, width: 32, minWidth: 32, minHeight: 32, fontSize: 22, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, color: 'var(--color-text-secondary)', background: 'var(--color-bg-tertiary)', border: '1px solid var(--color-border-light)' } })}
          {type === 'sql' && onRun && (
            <button
              title={currentStatus === 'unconfirmed' ? 'Confirm schema to enable Run' : 'Run (Ctrl+Enter)'}
              onClick={onRun}
              disabled={executing || (isFileBacked && currentStatus === 'unconfirmed')}
              aria-disabled={executing || (isFileBacked && currentStatus === 'unconfirmed')}
              style={{ background: currentStatus === 'unconfirmed' ? 'var(--color-error)' : 'var(--color-primary)', color: 'var(--color-text-light)', border: 'none', borderRadius: 5, padding: '0 12px', fontWeight: 600, fontSize: 18, cursor: executing || (isFileBacked && currentStatus === 'unconfirmed') ? 'not-allowed' : 'pointer', boxShadow: '0 1px 3px var(--color-shadow)', height: 32, minWidth: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: executing || (isFileBacked && currentStatus === 'unconfirmed') ? 0.7 : 1 }}
            >▶</button>
          )}
          {/* Banner for unconfirmed schema */}
          {isFileBacked && currentStatus === 'unconfirmed' && <SchemaUnconfirmedBanner />}
          <button title="Duplicate (Ctrl+D)" onClick={handleDuplicate} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, height: 32, minWidth: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, color: 'var(--color-secondary)' }} aria-label="Duplicate cell">⧉</button>
          {type !== 'markdown' && (
            <button
              title="Clear Output (Ctrl+L)"
              onClick={() => {
                if (type === 'chart' && onChartDataChange) {
                  onChartDataChange('');
                }
                if (onClearOutput) {
                  onClearOutput();
                }
              }}
              style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, height: 32, minWidth: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, color: 'var(--color-warning)' }}
              aria-label="Clear output"
            >🧹</button>
          )}
          <button title="Collapse/Expand (Ctrl+Shift+M)" onClick={onToggleCollapse} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 18, height: 32, minWidth: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, color: 'var(--color-primary)' }} aria-label="Collapse/expand cell">{collapsed ? '▸' : '▾'}</button>
          <button title="Delete (Ctrl+X)" onClick={onDelete} style={{ background: 'none', border: 'none', color: 'var(--color-error)', cursor: 'pointer', fontSize: 18, height: 32, minWidth: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0 }} aria-label="Delete cell">✕</button>
        </div>
      </div>
      {type === 'sql' && connections && connections.length ? (
        <div>
          <select
            value={currentUid || ''}
            onChange={e => {
              const v = e.target.value;
              onUidChange && onUidChange(v || null);
            }}
            style={{ marginLeft: 18, marginRight: 8 }}
          >
            <option value="">(default connection)</option>
            {connections.map((c) => (
              <option value={c.uid} key={c.uid}>{c.type === 'sqlite' ? `sqlite: ${c.file}` : `${c.type}://${c.user}@${c.host}:${c.port}/${c.database}`}</option>
            ))}
          </select>
          <span style={{ color: 'var(--color-text-secondary)', fontSize: 13 }}>
            {currentUid && connections ?
              (() => {
                const conn = connections.find(c => c.uid === currentUid);
                return conn ? (conn.type === 'sqlite' ? `sqlite: ${conn.file}` : `${conn.type}://${conn.user}@${conn.host}:${conn.port}/${conn.database}`) : '(default)';
              })()
              : '(default)'}
          </span>
        </div>
      ) : null}

      {!collapsed && (
        <div style={cellContent}>
          {/* File-backed cell: show file selector and schema status */}
          {isFileBacked && fileId && (
            <div style={fileSelectorRow}>
              <select
                value={fileId}
                onChange={e => onFileIdChange && onFileIdChange(e.target.value)}
                style={fileSelector}
                title="Select file for this cell"
              >
                {files.map(f => (
                  <option key={f.id} value={f.id}>{f.filename}</option>
                ))}
              </select>
              <span style={fileSchemaStatus}>
                <SchemaStatusBadge status={currentStatus} />
              </span>
            </div>
          )}
          {/* Inline schema preview for file-backed cell */}
          {/* File schema preview for file-backed cells (CSV, XML, JSON) using fileId only */}
          {isFileBacked && fileId && (
            <div style={fileSchemaPreview}>
              <NotebookCellFileSchemaPreview fileId={fileId} />
            </div>
          )}
          {type === 'sql' && (
            <NotebookCellSQL
              cellId={cellId}
              value={value}
              onChange={onChange}
              onRun={onRun}
              executing={executing}
              error={error}
              result={result}
              onFocus={onFocus}
              onVisualizeResult={onVisualizeResult}
              schemaTables={schemaTables}
            />
          )}
          {type === 'mongodb' && (
            <MongoDBCell
              value={value}
              onChange={onChange}
              onRun={onRun}
              executing={executing}
              error={error}
              result={result}
              schemaTables={schemaTables}
              onVisualize={onVisualizeResult}
            />
          )}
          {type === 'neo4j' && (
            <Neo4jCell
              value={value}
              onChange={onChange}
              onRun={onRun}
              executing={executing}
              error={error}
              result={result}
              schemaTables={schemaTables}
              onVisualize={onVisualizeResult}
            />
          )}
          {type === 'markdown' && (
            <MarkdownCell value={value} onChange={onChange} onFocus={onFocus} />
          )}
          {type === 'chart' && (
            <div className="cellContainer">
              <ChartCell
                chartType={chartType as 'bar' | 'line' | 'pie'}
                chartData={chartData}
                chartOptions={chartOptions}
                onChartTypeChange={onChartTypeChange}
                onChartDataChange={onChartDataChange}
                setShowImportModal={setShowImportModal}
              />
            </div>
          )}
          {type === 'schema' && (
            <div className="cellContainer">
              <SchemaCell uid={uid ?? null} />
            </div>
          )}
        </div>
      )}
      <ChartImportModal
        show={showImportModal}
        onClose={() => setShowImportModal(false)}
        availableFiles={useFileContext().files}
        allCells={allCells || []}
        onChartDataChange={onChartDataChange || (() => {})}
      />
    </div>
  );
}
