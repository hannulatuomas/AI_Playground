// Types for cell grouping in the notebook editor

export interface NotebookCellGroup {
  id: string;
  title: string;
  collapsed: boolean;
  cellIds: string[];
}

export interface NotebookEditorGroupedState {
  groups: NotebookCellGroup[];
  cells: NotebookCellData[];
}

// Import NotebookCellData from NotebookEditor
import { NotebookCellData } from './NotebookEditor';
