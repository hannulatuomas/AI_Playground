// Logic for notebook group and cell operations extracted from NotebookEditor.tsx
import { NotebookCellData } from '../NotebookEditor';
import { NotebookCellGroup } from '../NotebookGroupTypes';

export function addCell(cells: NotebookCellData[], type: NotebookCellData['type'], idx?: number): NotebookCellData[] {
  const newCell: NotebookCellData = { id: genId(), type, value: '', collapsed: false };
  const arr = [...cells];
  arr.splice(idx !== undefined ? idx + 1 : arr.length, 0, newCell);
  return arr;
}

export function moveCell(cells: NotebookCellData[], from: number, to: number): NotebookCellData[] {
  const arr = [...cells];
  const [removed] = arr.splice(from, 1);
  arr.splice(to, 0, removed);
  return arr;
}

export function duplicateCell(cells: NotebookCellData[], idx: number): NotebookCellData[] {
  const arr = [...cells];
  const originalCell = arr[idx];
  const copy = {
    ...originalCell,
    id: genId(),
    executing: false,
    result: undefined,
    error: undefined,
    title: originalCell.title ? `${originalCell.title} (Copy)` : undefined
  };
  arr.splice(idx + 1, 0, copy);
  return arr;
}

export function deleteCell(cells: NotebookCellData[], idx: number): NotebookCellData[] {
  if (cells.length === 1) return cells;
  return cells.filter((_, i) => i !== idx);
}

export function createGroup(groups: NotebookCellGroup[], title = 'Group'): NotebookCellGroup[] {
  const id = 'group_' + Math.random().toString(36).slice(2, 10);
  return [...groups, { id, title, collapsed: false, cellIds: [] }];
}

export function addCellToGroup(groups: NotebookCellGroup[], cellId: string, groupId: string): NotebookCellGroup[] {
  return groups.map(g => g.id === groupId ? { ...g, cellIds: [...g.cellIds, cellId] } : g);
}

// Helper: Generate unique cell IDs
function genId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return 'cell_' + Math.random().toString(36).substring(2, 10) + Date.now();
}
