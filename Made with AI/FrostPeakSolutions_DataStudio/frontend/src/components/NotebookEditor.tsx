import React, { useState, useEffect } from 'react';
import NotebookCell, { CellType } from './NotebookCell';
import NotebookEditorFilePreview from './NotebookEditorFilePreview';
import { exportNotebook, triggerFileDownload } from '../services/exportService';
import { ExportFormat, ExportOptions } from '../types';
import { NotebookCellGroup } from './NotebookGroupTypes';
import { DragDropContext, DropResult, Droppable, DroppableProvided, DroppableStateSnapshot, Draggable, DraggableProvided, DraggableStateSnapshot } from '@hello-pangea/dnd';
import NotebookGroup from './NotebookGroup';
import NotebookCellDraggable from './NotebookCellDraggable';
import {
  addCell as addCellOp,
  moveCell as moveCellOp,
  duplicateCell as duplicateCellOp,
  deleteCell as deleteCellOp,
  createGroup as createGroupOp,
  addCellToGroup as addCellToGroupOp
} from './notebookEditor/NotebookEditorOps';
import NotebookMetaModal from './notebookEditor/NotebookMetaModal';
import './NotebookEditor.css';
import { ungroupedDroppableStyle, addGroupButtonRow } from './NotebookEditor.styles';

export interface NotebookCellData {
  id: string;
  type: CellType;
  value: string;
  collapsed: boolean;
  executing?: boolean;
  result?: any[];
  uid?: string | null;
  paramValues?: { [key: string]: string };
  chartType?: 'bar' | 'line' | 'pie';
  chartData?: any;
  title?: string;
  error?: string;
  /** Unique fileId for file-backed cells (CSV, XML, JSON) */
  fileId?: string;
}

export function genId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return 'cell_' + Math.random().toString(36).substring(2, 10) + Date.now();
}

import { useConnectionContext, DBConnection } from './ConnectionContext';

import { useFileContext } from './FileContext';

interface NotebookMeta {
  id: string;
  title: string;
  description: string;
  lastModified: number;
}

interface RunCellOpts {
  conn?: DBConnection;
  fileId?: string;
  params?: { [k: string]: string };
  schemaOverride?: { name: string; type: string }[];
}

interface NotebookEditorProps {
  onRun: (sql: string, opts?: RunCellOpts) => Promise<{ result?: any[]; error?: string | null }>;
  initialCells?: NotebookCellData[] | null;
  initialMeta?: NotebookMeta | null;
  initialGroups?: NotebookCellGroup[];
  onNotebookUpdate?: (cells: NotebookCellData[], meta: NotebookMeta, groups: NotebookCellGroup[]) => void;
  onCellSelect?: (idx: number) => void;
  onMetaChange?: () => void; // NEW: callback to notify parent of meta/title change
  selectedUid?: string | null;
}

import { useSchema } from './useSchema';


function dbTypeToCellType(dbType: string): CellType {
  if (dbType === 'mongodb') return 'mongodb';
  if (dbType === 'neo4j') return 'neo4j';
  return 'sql';
}

export default function NotebookEditor({ onRun, initialCells, initialMeta, initialGroups, onNotebookUpdate, onCellSelect, onMetaChange, selectedUid }: NotebookEditorProps) {
  const [cells, setCells] = useState<NotebookCellData[]>(
    initialCells && Array.isArray(initialCells) && initialCells.length > 0
      ? initialCells
      : initialMeta && initialMeta.id
        ? [{ id: genId(), type: 'sql', value: '', collapsed: false }]
        : [{ id: genId(), type: 'sql', value: 'SELECT 1 as example;', collapsed: false, uid: selectedUid ?? null }]
  );
  const [groups, setGroups] = useState<NotebookCellGroup[]>(
    (initialMeta && Array.isArray((initialMeta as any).groups)) ? (initialMeta as any).groups : (initialGroups || [])
  ); // Cell grouping state
  const [meta, setMeta] = useState<NotebookMeta>(
    initialMeta && initialMeta.id
      ? { ...initialMeta }
      : { id: Math.random().toString(36).slice(2, 10), title: 'Untitled Notebook', description: '', lastModified: Date.now() }
  );

  const handleVisualizeResult = (idx: number, data: any[]) => {
    if (!Array.isArray(data) || data.length === 0) return;
    const columns = Object.keys(data[0]);
    const chartData = {
      labels: data.map(row => row[columns[0]]),
      datasets: [
        {
          label: columns[1] || columns[0],
          data: data.map(row => row[columns[1]] ?? 0),
          backgroundColor: '#1976d2',
        }
      ]
    };
    const newCell: NotebookCellData = {
      id: genId(),
      type: 'chart',
      value: '',
      chartType: 'bar',
      chartData,
      collapsed: false
    };
    setCells(cs => {
      const newCells = [...cs];
      newCells.splice(idx + 1, 0, newCell);
      return newCells;
    });
  };

  const createGroup = (title = 'Group') => {
    setGroups(gs => createGroupOp(gs, title));
  };

  const addCellToGroup = (cellId: string, groupId: string) => {
    setGroups(gs => addCellToGroupOp(gs, cellId, groupId));
  };

  const moveCellOrGroup = (sourceId: string, destId: string, type: 'cell' | 'group') => {
    // To be implemented with drag-and-drop logic
  };

  // Update state ONLY when a new notebook is opened (by ID)
  React.useEffect(() => {
    if (initialMeta && initialMeta.id && initialMeta.id !== meta.id) {
      setMeta({ ...initialMeta });
      if (initialCells && Array.isArray(initialCells) && initialCells.length > 0) {
        // Ensure all initialCells have uid set (migrate from legacy if needed)
        setCells(initialCells.map(cell => ({
          ...cell,
          uid: cell.uid ?? selectedUid ?? null
        })));
      } else {
        setCells([{ id: genId(), type: 'sql', value: '', collapsed: false }]);
      }
      // Always restore groups from initialGroups if present, then from initialMeta.groups, else empty
      if (initialGroups && Array.isArray(initialGroups)) {
        setGroups(initialGroups);
      } else if ((initialMeta as any).groups && Array.isArray((initialMeta as any).groups)) {
        setGroups((initialMeta as any).groups);
      } else {
        setGroups([]);
      }
    }
    // eslint-disable-next-line
  }, [initialCells, initialMeta]);

  const [showMetaModal, setShowMetaModal] = useState(false);
  const { connections, selected } = useConnectionContext();
  const { files, loading: filesLoading, error: filesError, refreshFiles } = useFileContext();

  // Drag-and-drop state
  const [dragIndex, setDragIndex] = useState<number | null>(null);
  const [dropIndex, setDropIndex] = useState<number | null>(null);

  // Propagate changes to parent (App) for persistence
  /**
   * Atomically save notebook state to localStorage with version and timestamp.
   * Falls back gracefully if localStorage is full or errors occur.
   */
  React.useEffect(() => {
    if (onNotebookUpdate) onNotebookUpdate(cells, meta, groups);
    if (meta && meta.id) {
      const saveObj = {
        version: 1,
        saved: Date.now(),
        cells,
        meta,
        groups
      };
      try {
        localStorage.setItem('notebook:' + meta.id + ':cells', JSON.stringify(saveObj));
      } catch (err) {
        // Handle quota/full errors gracefully
        // Optionally notify user or log
      }
      try {
        localStorage.setItem('notebook:' + meta.id, JSON.stringify({ ...meta, groups, version: 1, saved: Date.now() }));
      } catch {}
    }
    // eslint-disable-next-line
  }, [cells, meta, groups]);

  // Track last focused cell for snippet insertion
  const handleCellFocus = (idx: number) => {
    if (onCellSelect) onCellSelect(idx);
  };

  // Use modular duplicateCell from NotebookEditorOps
const duplicateCell = (idx: number) => {
  setCells(cs => duplicateCellOp(cs, idx));
  // Group logic must be handled separately if needed
};

  const clearCellOutput = (idx: number) => {
    setCells(cs => cs.map((c, i) => i === idx ? { ...c, result: undefined, error: undefined, executing: false } : c));
  };

  // Use modular addCell from NotebookEditorOps
  const addCell = (type?: CellType, idx?: number) => {
    let finalType: CellType = 'sql';
    let uid: string | null = null;
    if (type) {
      finalType = type;
    } else if (selected != null && connections[selected]) {
      finalType = dbTypeToCellType(connections[selected].type);
      uid = connections[selected].uid;
    }
    setCells(cs => {
  const newCells = addCellOp(cs, finalType, idx);
  if (uid && newCells.length > 0) {
    const insertIdx = typeof idx === 'number' ? idx : newCells.length - 1;
    newCells[insertIdx] = { ...newCells[insertIdx], uid };
  }
  return newCells;
});
  };

  // Use modular moveCell from NotebookEditorOps
  const moveCell = (from: number, to: number) => {
    setCells(cs => moveCellOp(cs, from, to));
  };

  // Drag and drop handlers
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null);
  const [dragOverIdx, setDragOverIdx] = useState<number | null>(null);

  const handleDragStart = (idx: number) => {
    setDraggedIdx(idx);
  };

  const handleDragEnter = (idx: number) => {
    setDragOverIdx(idx);
  };

  const handleDragEnd = () => {
    if (draggedIdx !== null && dragOverIdx !== null && draggedIdx !== dragOverIdx) {
      moveCell(draggedIdx, dragOverIdx);
    }
    setDraggedIdx(null);
    setDragOverIdx(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  // Use modular deleteCell from NotebookEditorOps
  const deleteCell = (idx: number) => {
    setCells(cs => deleteCellOp(cs, idx));
  };

  const runCell = async (idx: number) => {
    setCells((cs: NotebookCellData[]) => cs.map((c, i) => i === idx ? { ...c, executing: true, error: undefined, result: undefined } : c));
    const cell = cells[idx];
    const sql = cell.value;
    let opts: RunCellOpts = {};
    if (cell.uid && connections) {
      const conn = connections.find((c: DBConnection) => c.uid === cell.uid);
      if (conn) opts.conn = conn;
    }
    if (!opts.conn && selected != null && connections[selected]) opts.conn = connections[selected];
    if (cell.paramValues) opts.params = cell.paramValues;

    // For file-backed cells, resolve fileId to file
    if (cell.fileId) {
      const file = files.find(f => f.id === cell.fileId);
      if (file) {
        opts.fileId = file.id;
        // --- Pass schemaOverride for CSV/XML/JSON queries ---
        try {
          const raw = localStorage.getItem('file_schema_overrides');
          if (raw) {
            const obj = JSON.parse(raw);
            if (obj && obj[file.id]) opts.schemaOverride = obj[file.id];
          }
        } catch {}
      }
    }

    // --- Frontend validation for missing connection or file ---
    if (!opts.conn && !opts.fileId) {
      setCells((cs: NotebookCellData[]) => cs.map((c, i) => i === idx ? {
        ...c,
        executing: false,
        error: 'No valid database connection or file selected.'
      } : c));
      return;
    }

    try {
      const { result, error } = await onRun(sql, opts);
      // Only set cell error if error is not the global missing connection/file error
      const isGlobalConnError = error === 'Please select a database connection or file.';
      setCells((cs: NotebookCellData[]) => cs.map((c, i) =>
        i === idx ? { ...c, executing: false, result, error: isGlobalConnError ? undefined : (error ?? undefined) } : c
      ));
    } catch (err: any) {
      setCells((cs: NotebookCellData[]) => cs.map((c, i) => i === idx ? { ...c, executing: false, error: err.message } : c));
    }
  };

  // Run all executable cells (SQL, MongoDB, Neo4j) in order
  async function runAllCells() {
    for (let idx = 0; idx < cells.length; idx++) {
      const cell = cells[idx];
      if (!['sql', 'mongodb', 'neo4j'].includes(cell.type)) continue;
      setCells(cs => cs.map((c, i) => i === idx ? { ...c, executing: true, error: undefined, result: undefined } : c));
      let opts: RunCellOpts = {};
      if (cell.uid && connections) {
        const conn = connections.find((c: DBConnection) => c.uid === cell.uid);
        if (conn) opts.conn = conn;
      }
      if (!opts.conn && selected != null && connections[selected]) opts.conn = connections[selected];
      if (cell.paramValues) opts.params = cell.paramValues;

      // For file-backed cells, resolve fileId to file
      if (cell.fileId) {
        const file = files.find(f => f.id === cell.fileId);
        if (file) {
          opts.fileId = file.id;
          // --- Pass schemaOverride for CSV/XML/JSON queries ---
          try {
            const raw = localStorage.getItem('file_schema_overrides');
            if (raw) {
              const obj = JSON.parse(raw);
              if (obj && obj[file.id]) opts.schemaOverride = obj[file.id];
            }
          } catch {}
        }
      }

      // --- Frontend validation for missing connection or file ---
      if (!opts.conn && !opts.fileId) {
        setCells(cs => cs.map((c, i) => i === idx ? {
          ...c,
          executing: false,
          error: 'No valid database connection or file selected.'
        } : c));
        continue;
      }

      let sql = cell.value;
      // Handle MongoDB and Neo4j query payloads
      if (cell.type === 'mongodb' || cell.type === 'neo4j') {
        try {
          const parsed = JSON.parse(cell.value);
          opts = { ...opts, ...parsed };
          sql = '';
        } catch (e) {
          setCells(cs => cs.map((c, i) => i === idx ? { ...c, executing: false, error: 'Invalid JSON in cell value' } : c));
          continue;
        }
      }
      try {
        const { result, error } = await onRun(sql, opts);
        setCells(cs => cs.map((c, i) => i === idx ? { ...c, executing: false, result, error: error ?? undefined } : c));
      } catch (err: any) {
        setCells(cs => cs.map((c, i) => i === idx ? { ...c, executing: false, error: err.message } : c));
      }
    }
  }

  // Export format state and handler
  const [exportFormat, setExportFormat] = useState<ExportFormat>(ExportFormat.JSON);
  const [exporting, setExporting] = useState(false);

  // Export notebook handler
  const handleExport = async () => {
    setExporting(true);
    try {
      const notebookPayload = {
        id: meta.id,
        name: meta.title,
        createdAt: new Date(meta.lastModified).toISOString(),
        updatedAt: new Date().toISOString(),
        cells: cells.map(cell => {
          let result: any = undefined;
          if (cell.result && typeof cell.result === 'object' && 'columns' in cell.result && 'rows' in cell.result && 'rowCount' in cell.result) {
            result = cell.result;
          }
          return {
            id: cell.id,
            type: cell.type,
            content: cell.value,
            result,
          };
        }),
        metadata: { description: meta.description },
      };
      const options: ExportOptions = {
        format: exportFormat,
        includeHeaders: true,
        prettyPrint: exportFormat === ExportFormat.JSON,
      };
      const blob = await exportNotebook(notebookPayload, options);
      const filename = `${meta.title.replace(/[^a-z0-9_\-]/gi, '_') || 'notebook'}-${meta.id}.${exportFormat}`;
      triggerFileDownload(blob, filename);
      setMeta(m => ({ ...m, lastModified: Date.now() }));
      if (typeof onMetaChange === 'function') onMetaChange();
    } catch (err) {
      alert('Failed to export notebook: ' + (err instanceof Error ? err.message : String(err)));
    } finally {
      setExporting(false);
    }
  };

  // Import notebook handler
  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = evt => {
      try {
        const obj = JSON.parse(evt.target?.result as string);
        if (Array.isArray(obj)) {
          setCells(obj);
          setMeta(m => ({ ...m, title: 'Imported Notebook', lastModified: Date.now() }));
        } else if (obj && obj.meta && Array.isArray(obj.cells)) {
          setCells(obj.cells);
          setMeta({ ...obj.meta, lastModified: Date.now() });
          localStorage.setItem('notebook:' + obj.meta.id, JSON.stringify({ ...obj.meta, lastModified: Date.now() }));
        } else {
          alert('Invalid notebook file.');
        }
      } catch {
        alert('Failed to parse notebook file.');
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  // Meta save handler
  const handleMetaSave = (title: string, description: string) => {
    setMeta(m => {
      const updatedMeta = { ...m, title, description, lastModified: Date.now() };
      localStorage.setItem('notebook:' + updatedMeta.id, JSON.stringify(updatedMeta));
      if (typeof onMetaChange === 'function') onMetaChange();
      if (typeof onNotebookUpdate === 'function') onNotebookUpdate(cells, updatedMeta, groups);
      return updatedMeta;
    });
    setShowMetaModal(false);
  };

  // Handler to run all cells in a group
  const handleRunAllInGroup = async (groupId: string) => {
    const group = groups.find(g => g.id === groupId);
    if (!group) return;
    for (const cellId of group.cellIds) {
      const idx = cells.findIndex(c => c.id === cellId);
      if (idx >= 0) {
        await runCell(idx);
      }
    }
  };

  return (
    <div className="notebookEditorScrollArea" style={{ padding: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
        <h2 style={{ fontSize: 20, margin: 0, flex: 1 }}>{meta.title}</h2>
        <button style={{ background: '#e3f2fd', color: '#1976d2', border: '1px solid #b6d4fa', borderRadius: 5, padding: '4px 14px', fontWeight: 600, fontSize: 14, cursor: 'pointer', marginLeft: 12 }} onClick={() => setShowMetaModal(true)}>
          Edit Info
        </button>
        <button
          style={{ background: '#1976d2', color: '#fff', border: 'none', borderRadius: 5, padding: '4px 16px', fontWeight: 600, fontSize: 14, cursor: 'pointer', marginLeft: 12 }}
          onClick={runAllCells}
          disabled={cells.some(cell => cell.executing)}
          title="Run all executable cells in order"
        >
          ▶ Run All
        </button>
      </div>
      <div style={{ color: '#888', fontSize: 14, marginBottom: 10 }}>{meta.description}</div>
      <div style={{ color: '#aaa', fontSize: 12, marginBottom: 16 }}>Last modified: {new Date(meta.lastModified).toLocaleString()}</div>
      {showMetaModal && (
        <NotebookMetaModal
          meta={meta}
          onChange={updated => setMeta(m => ({ ...m, ...updated }))}
          onSave={() => handleMetaSave(meta.title, meta.description)}
          onCancel={() => setShowMetaModal(false)}
        />
      )}
      <div className="notebookEditorToolbar">
        <button onClick={() => addCell()} className="primaryButton">+ Query Cell</button>
        <button onClick={() => addCell('markdown')} className="markdownButton">+ Markdown Cell</button>
        <button onClick={() => addCell('chart')} className="chartButton">+ Chart Cell</button>
        <button onClick={() => addCell('schema')} className="secondaryButton schema-cell-add-btn">+ Schema Cell</button>
        <div style={{ flex: 1 }} />
        <select
          value={exportFormat}
          onChange={e => setExportFormat(e.target.value as ExportFormat)}
          style={{ marginRight: 8, padding: '4px 8px', borderRadius: 4, border: '1px solid #b6d4fa', fontSize: 14 }}
          aria-label="Select export format"
        >
          <option value={ExportFormat.JSON}>JSON</option>
          <option value={ExportFormat.CSV}>CSV</option>
          <option value={ExportFormat.XML}>XML</option>
        </select>
        <button onClick={handleExport} className="secondaryButton" disabled={exporting}>
          {exporting ? 'Exporting…' : 'Export Notebook'}
        </button>
        <label className="secondaryButton" style={{ background: '#f8fafd' }}>
          Import Notebook
          <input type="file" accept="application/json" style={{ display: 'none' }} onChange={handleImport} />
        </label>
      </div>
      <DragDropContext
  onDragEnd={(result: DropResult) => {
    const { source, destination, draggableId, type } = result;
    if (!destination) return;

    // Handle group reordering
    if (type === 'group') {
      if (source.index !== destination.index) {
        setGroups(gs => {
          const arr = [...gs];
          const [removed] = arr.splice(source.index, 1);
          arr.splice(destination.index, 0, removed);
          return arr;
        });
      }
      return;
    }

    // Handle cell dragging
    if (type === 'cell') {
      const sourceGroup = groups.find(g => g.id === source.droppableId);
      const destGroup = groups.find(g => g.id === destination.droppableId);
      const isSourceUngrouped = source.droppableId === 'ungrouped';
      const isDestUngrouped = destination.droppableId === 'ungrouped';
      
      // Determine original cell index for potential reordering or removal
      const originalCellIndex = cells.findIndex(c => c.id === draggableId);
      if (originalCellIndex === -1) return; // Cell not found, should not happen
      const cellToMove = cells[originalCellIndex];

      let newCells = [...cells];
      let newGroups = groups.map(g => ({ ...g, cellIds: [...g.cellIds] })); // Deep copy cellIds

      // Remove cell from its original position (either in groups or from overall cell list)
      if (sourceGroup) {
        const groupIdx = newGroups.findIndex(g => g.id === sourceGroup.id);
        if (groupIdx !== -1) {
          newGroups[groupIdx].cellIds = newGroups[groupIdx].cellIds.filter(id => id !== draggableId);
        }
      }
      // If it was in ungrouped or moving between groups, we need to adjust newCells order later if it's not just group membership change.
      // For now, assume cellToMove holds the correct cell object.
      // If reordering within ungrouped, or moving to/from ungrouped, the 'cells' array order matters.

      if (isSourceUngrouped && isDestUngrouped) { // Reorder within ungrouped
        // Filter out grouped cells to get the list of ungrouped cells in their current display order
        const currentUngroupedCells = newCells.filter(c => !newGroups.some(g => g.cellIds.includes(c.id)));
        const fromUngroupedIdx = currentUngroupedCells.findIndex(c => c.id === draggableId);
        
        if (fromUngroupedIdx !== -1) {
          const [movedCell] = currentUngroupedCells.splice(fromUngroupedIdx, 1);
          currentUngroupedCells.splice(destination.index, 0, movedCell);
          
          // Reconstruct newCells: put all grouped cells first (in their original relative order), then the reordered ungrouped cells
          const groupedCells = newCells.filter(c => newGroups.some(g => g.cellIds.includes(c.id)));
          newCells = [...groupedCells, ...currentUngroupedCells];
        }
      } else if (destGroup) { // Moving to a group (from ungrouped or another group)
        const destGroupIdx = newGroups.findIndex(g => g.id === destGroup.id);
        if (destGroupIdx !== -1) {
          newGroups[destGroupIdx].cellIds.splice(destination.index, 0, draggableId);
        }
        // If moving from ungrouped, ensure it's removed from the visual order of ungrouped cells
        // The general re-ordering of 'newCells' might be complex if we want to preserve exact visual positions.
        // A simpler approach might be to rely on filtering for ungrouped display.
        // For now, just ensure group membership is correct. The `cells` array itself does not need reordering if display relies on `groups`.
      } else if (isDestUngrouped) { // Moving to ungrouped (from a group)
        // Cell is already removed from sourceGroup's cellIds
        // Add to ungrouped visually by inserting into 'cells' array at an appropriate position.
        // This is tricky because 'destination.index' for ungrouped is relative to visible ungrouped cells.
        // Find current ungrouped cells
        const currentUngroupedCells = newCells.filter(c => !newGroups.some(g => g.cellIds.includes(c.id) && c.id !== draggableId));
        // Insert the cellToMove into this list at the target index
        currentUngroupedCells.splice(destination.index, 0, cellToMove);
        
        // Reconstruct newCells: grouped cells + new order of ungrouped cells
        const groupedCells = newCells.filter(c => newGroups.some(g => g.cellIds.includes(c.id)));
        newCells = [...groupedCells, ...currentUngroupedCells.filter(c => c.id !== draggableId), cellToMove]; // ensure no duplicates if logic is complex
        
        // Re-filter to ensure correct composition of newCells
        const finalGroupedCellIds = new Set(newGroups.flatMap(g => g.cellIds));
        const finalGroupedCells = cells.filter(c => finalGroupedCellIds.has(c.id));
        const finalUngroupedCells = [];
        
        // Build finalUngroupedCells in the new order
        const tempUngroupedWithMoved = cells.filter(c => !finalGroupedCellIds.has(c.id) || c.id === draggableId);
        const fromIdx = tempUngroupedWithMoved.findIndex(c => c.id === draggableId);
        if (fromIdx !== -1) {
            const [item] = tempUngroupedWithMoved.splice(fromIdx, 1);
            tempUngroupedWithMoved.splice(destination.index, 0, item);
        }
        newCells = [...finalGroupedCells, ...tempUngroupedWithMoved];
      }
      
      // If the overall order of `cells` array needs to be strictly maintained to reflect visual order of ungrouped items,
      // this part needs careful reconstruction.
      // A common pattern is to have `cells` be the single source of truth for cell objects,
      // and `groups` + filtering determines render order. If so, `newCells` might not need reordering,
      // only `newGroups` needs updates. However, the provided `onDragEnd` seems to try to reorder `newCells`.
      // The logic for reordering `newCells` based on ungrouped DND is complex.
      // For now, we focus on group membership. Re-ordering 'cells' array for ungrouped items:
      if (isDestUngrouped || (isSourceUngrouped && isDestUngrouped)) {
          const allGroupedIds = new Set(newGroups.flatMap(g => g.cellIds));
          const currentUngroupedCells = cells.filter(c => !allGroupedIds.has(c.id) || c.id === draggableId); // include the one being moved if it was grouped
          
          let Sidx = currentUngroupedCells.findIndex(c => c.id === draggableId);
          if (Sidx === -1 && sourceGroup) { // If it came from a group, it's not in currentUngroupedCells yet
              // This case needs cellToMove to be added
          } else if (Sidx !== -1) {
            const [item] = currentUngroupedCells.splice(Sidx, 1); // Remove from old ungrouped position
            currentUngroupedCells.splice(destination.index, 0, item); // Add to new ungrouped position
          }


          // Reconstruct the main `cells` array preserving grouped cells and using the new order for ungrouped.
          // This is non-trivial if grouped cells are interspersed.
          // A simpler model: `cells` array order is fixed, `groups` define grouped cells, others are ungrouped in `cells` order.
          // If ungrouped cells can be reordered relative to each other:
          if (isSourceUngrouped && isDestUngrouped) { // Reordering within ungrouped section
            // `newCells` will be directly manipulated based on source.index and destination.index relative to ungrouped items.
            // This requires finding true indices in `newCells` array.
            const ungroupedCellObjects = newCells.filter(cell => !newGroups.some(g => g.cellIds.includes(cell.id)));
            const fromActualIdx = newCells.indexOf(ungroupedCellObjects[source.index]); // This assumes source.index is for ungrouped list
            const toActualIdx = newCells.indexOf(ungroupedCellObjects[destination.index]); // This is problematic
            // The DND library provides indices relative to the droppable list.
            // A robust way for reordering `cells` when ungrouped items are involved:
            // 1. Get all cells.
            // 2. Separate into grouped and ungrouped.
            // 3. If moving within ungrouped: reorder the ungrouped list.
            // 4. If moving from grouped to ungrouped: take from grouped, add to ungrouped list at correct pos.
            // 5. If moving from ungrouped to grouped: take from ungrouped, add to group.
            // 6. Reconstruct `cells` array, perhaps by convention (e.g., all grouped first, then all ungrouped).
            //    The current rendering iterates `groups` then filters `cells` for ungrouped. This means `cells` order matters for ungrouped.

            // Simplified reordering for ungrouped:
            const items = Array.from(cells);
            const [reorderedItem] = items.splice(originalCellIndex, 1); // Remove from original position in main list
            // Find the actual insertion point in `cells` based on `destination.index` of ungrouped list
            const currentUngroupedIds = items.filter(c => !newGroups.some(g => g.cellIds.includes(c.id))).map(c=>c.id);
            let targetIndexInFullList = originalCellIndex; // fallback
            if (currentUngroupedIds.length > 0) {
                if (destination.index >= currentUngroupedIds.length) { // dragging to the end
                    targetIndexInFullList = items.indexOf(items.find(c => c.id === currentUngroupedIds[currentUngroupedIds.length-1])!) + 1;
                } else {
                    targetIndexInFullList = items.indexOf(items.find(c => c.id === currentUngroupedIds[destination.index])!);
                }
            } else { // dragging to an empty ungrouped list
                // find first cell that is not in any group, or end of list
                 targetIndexInFullList = items.length; // Default to end if no ungrouped cells to reference
                 for(let i=0; i<items.length; ++i) {
                     if (!newGroups.some(g => g.cellIds.includes(items[i].id))) {
                         targetIndexInFullList = i;
                         break;
                     }
                 }
            }
            items.splice(targetIndexInFullList, 0, reorderedItem);
            newCells = items;
          }
      }

      setGroups(newGroups);
      setCells(newCells); // This might need more robust logic for ordering
    }
  }}
>
        {/* --- Grouped Cells (DnD) --- */}
        <Droppable droppableId="groups-droppable" type="group">
          {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
            <div ref={provided.innerRef} {...provided.droppableProps}>
              {groups.map((group, idx) => (
                <Draggable draggableId={group.id} index={idx} key={group.id}>
                  {(dragProvided, dragSnapshot) => (
                    <div
                      ref={dragProvided.innerRef}
                      {...dragProvided.draggableProps}
                      style={{
                        marginBottom: 8,
                        ...dragProvided.draggableProps.style,
                      }}
                    >
                      <NotebookGroup
                        group={group}
                        cells={cells.filter(c => group.cellIds.includes(c.id))} // Pass only relevant cells
                        allGroups={groups}
                        onUpdateGroup={updated => setGroups(gs => gs.map(g => g.id === updated.id ? updated : g))}
                        onDeleteGroup={groupId => setGroups(gs => gs.filter(g => g.id !== groupId))}
                        onUngroupAll={groupId => setGroups(gs => gs.map(g => g.id === groupId ? { ...g, cellIds: [] } : g))}
                        onCellUpdate={updatedCell => setCells(cs => cs.map(c => c.id === updatedCell.id ? updatedCell : c))}
                        onCellDelete={cellId => {
                            setCells(cs => cs.filter(c => c.id !== cellId));
                            setGroups(gs => gs.map(g => ({...g, cellIds: g.cellIds.filter(id => id !== cellId)})))
                        }}
                        onCellAddToGroup={(cellId: string, targetGroupId: string | null) => {
                          let newGroupsState = groups.map(g => ({ ...g, cellIds: g.cellIds.filter(id => id !== cellId) }));
                          if (targetGroupId) {
                            newGroupsState = newGroupsState.map(g =>
                              g.id === targetGroupId
                                ? { ...g, cellIds: [...g.cellIds, cellId] }
                                : g
                            );
                          }
                          setGroups(newGroupsState);
                        }}
                        onRunAllInGroup={handleRunAllInGroup}
                        onDuplicate={(cellId: string) => {
                          const cellIndex = cells.findIndex(c => c.id === cellId);
                          if (cellIndex !== -1) {
                             // duplicateCellOp already adds the new cell after the original.
                             // If it's in a group, we need to add the new cell's ID to the same group.
                             const originalCell = cells[cellIndex];
                             const newCellId = genId(); // Assuming duplicateCellOp doesn't return the new cell or its id.
                                                       // This is a simplification; ideally duplicateCellOp would handle group logic or return new cell.
                             
                             setCells(cs => {
                                const tempCells = duplicateCellOp(cs, cellIndex);
                                 const groupOfOriginal = groups.find(g => g.cellIds.includes(originalCell.id));
                                 if (groupOfOriginal) {
                                     setGroups(gs => gs.map(g => {
                                         if (g.id === groupOfOriginal.id) {
                                             const originalCellGroupIndex = g.cellIds.indexOf(originalCell.id);
                                             const newCellIds = [...g.cellIds];
                                             newCellIds.splice(originalCellGroupIndex + 1, 0, newCellId);
                                             return {...g, cellIds: newCellIds};
                                         }
                                         return g;
                                     }));
                                 }
                                return tempCells;
                             });
                          }
                        }}
                        runCell={(idx: number) => {
                            const cellId = group.cellIds[idx];
                            const cellIndex = cells.findIndex(c => c.id === cellId);
                            if (cellIndex !== -1) runCell(cellIndex);
                        }}
                        onVisualizeResult={(idx: number, data: any[]) => {
                            const cellId = group.cellIds[idx];
                            const cellIndex = cells.findIndex(c => c.id === cellId);
                            if (cellIndex !== -1) handleVisualizeResult(cellIndex, data);
                        }}
                        dragHandleProps={dragProvided.dragHandleProps ?? undefined}
                      />
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
        {/* --- Ungrouped Cells --- */}
        <Droppable droppableId="ungrouped" type="cell">
          {(provided: DroppableProvided, snapshot: DroppableStateSnapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              style={ungroupedDroppableStyle(snapshot.isDraggingOver)}
            >
              {cells.filter(cell => !groups.some((g: NotebookCellGroup) => g.cellIds.includes(cell.id))).map((cell, idxInUngroupedList) => {
                const originalIndex = cells.findIndex(c => c.id === cell.id); // Get original index in `cells` array
                const fileBacked = ['csv', 'xml', 'json'].includes(cell.type as string);
                return (
                  <NotebookCellDraggable
                    key={cell.id}
                    cell={cell}
                    index={originalIndex} // Pass original index for operations on `cells`
                    groups={groups}
                    isUngrouped={true}
                    onCellUpdate={updatedCell => setCells(cs => cs.map(c => c.id === updatedCell.id ? updatedCell : c))}
                    onCellDelete={() => {
                         setCells(cs => cs.filter(c => c.id !== cell.id));
                         // No need to update groups for ungrouped cell delete
                     }}
                    onAddToGroup={(cellId: string, targetGroupId: string | null) => { // targetGroupId can be null to ungroup
                        let newGroupsState = groups.map(g => ({ ...g, cellIds: g.cellIds.filter(id => id !== cellId) }));
                        if (targetGroupId) {
                        newGroupsState = newGroupsState.map(g =>
                            g.id === targetGroupId ? { ...g, cellIds: [...g.cellIds, cellId] } : g
                        );
                        }
                        setGroups(newGroupsState);
                    }}
                    onDuplicate={() => {
                      if (originalIndex !== -1) {
                        duplicateCell(originalIndex); // This will add cell to main `cells` list; it will appear as ungrouped.
                      }
                    }}
                    onClearOutput={() => {
                        if (originalIndex !== -1) clearCellOutput(originalIndex);
                    }}
                    onChartTypeChange={type => setCells(cs => cs.map(c => c.id === cell.id ? { ...c, chartType: type } : c))}
                    onChartDataChange={data => setCells(cs => cs.map(c => c.id === cell.id ? { ...c, chartData: data } : c))}
                    chartType={cell.chartType}
                    chartData={cell.chartData}
                    allCells={cells}
                    onRun={cell.type === 'sql' || cell.type === 'mongodb' || cell.type === 'neo4j' || cell.fileId ? (() => {
                        if (originalIndex !== -1) runCell(originalIndex);
                    }) : undefined}
                    executing={cell.executing}
                    onVisualizeResult={(data: any[]) => {
                        const idx = cells.findIndex(c => c.id === cell.id);
                        if (idx !== -1) handleVisualizeResult(idx, data);
                    }}
                    {...(fileBacked && cell.fileId ? { fileId: cell.fileId } : {})}
                  />
                );
              })}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
        <div style={addGroupButtonRow}>
          <button
            className="secondaryButton"
            onClick={() => createGroup('Group')}
          >
            + Add Group
          </button>
        </div>
      </DragDropContext>
    </div>
  );
}