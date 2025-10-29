import React from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { NotebookCellData } from './NotebookEditor';
import { NotebookCellGroup } from './NotebookGroupTypes';
import NotebookCell from './NotebookCell';

interface NotebookCellDraggableProps {
  cell: NotebookCellData;
  index: number;
  groups: NotebookCellGroup[];
  onCellUpdate: (cell: NotebookCellData) => void;
  onCellDelete: (cellId: string) => void;
  onAddToGroup: (cellId: string, groupId: string | null) => void;
  onDuplicate: () => void;
  onClearOutput: () => void;
  onChartTypeChange?: (type: 'bar' | 'line' | 'pie') => void;
  onChartDataChange?: (data: any) => void;
  chartType?: 'bar' | 'line' | 'pie';
  chartData?: any;
  allCells?: NotebookCellData[];
  isUngrouped?: boolean;
  onRun?: () => void;
  executing?: boolean;
  onVisualizeResult?: (data: any[]) => void;
  fileId?: string;
  // --- Updated for uid ---
  // No connUid or onConnChange

}

const NotebookCellDraggable: React.FC<NotebookCellDraggableProps> = ({
  cell,
  index,
  groups,
  onCellUpdate,
  onCellDelete,
  onAddToGroup,
  onDuplicate,
  onClearOutput,
  onChartTypeChange,
  onChartDataChange,
  chartType,
  chartData,
  allCells,
  isUngrouped = false,
  onRun,
  executing,
  onVisualizeResult,
  fileId
}) => {
  return (
    <Draggable draggableId={cell.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={{
            marginBottom: 16,
            background: snapshot.isDragging ? 'var(--color-primary-light)' : undefined,
            display: 'flex',
            alignItems: 'center',
            ...provided.draggableProps.style
          }}
        >
          <div style={{ flex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <NotebookCell
              cellId={cell.id}
              type={cell.type}
              value={cell.value}
              onChange={val => onCellUpdate({ ...cell, value: val })}
              onRun={onRun}
              onDelete={() => onCellDelete(cell.id)}
              collapsed={cell.collapsed}
              onToggleCollapse={() => onCellUpdate({ ...cell, collapsed: !cell.collapsed })}
              executing={executing}
              result={cell.result}
              error={cell.error}
              uid={cell.uid ?? null}
              onUidChange={uid => onCellUpdate({ ...cell, uid })}
              chartType={chartType}
              chartData={chartData}
              onChartTypeChange={onChartTypeChange}
              onChartDataChange={onChartDataChange}
              title={cell.title}
              onTitleChange={title => onCellUpdate({ ...cell, title })}
              addToGroupDropdown={isUngrouped && groups.length > 0 ? (
                <select
                  style={{ marginLeft: 8, padding: '2px 8px', borderRadius: 4, border: '1px solid var(--color-border-accent)', background: 'var(--color-primary-light)', color: 'var(--color-primary)', fontWeight: 600, fontSize: 14, cursor: 'pointer', height: 28 }} // already using CSS variables
                  defaultValue=""
                  title="Add to group"
                  onChange={e => {
                    const groupId = e.target.value;
                    if (!groupId) return;
                    onAddToGroup(cell.id, groupId);
                  }}
                >
                  <option value="" disabled>Add to group…</option>
                  {groups.map((g: NotebookCellGroup) => <option key={g.id} value={g.id}>{g.title || 'Group'}</option>)}
                </select>
              ) : undefined}
              removeFromGroupButtonInToolbar={
                !isUngrouped ? (
                  <button
                    title="Remove from group"
                    onClick={() => onAddToGroup(cell.id, null)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--color-error)',
                      cursor: 'pointer',
                      fontSize: 22,
                      fontWeight: 700,
                      marginRight: 6,
                      padding: '2px 8px',
                      borderRadius: 5,
                      transition: 'background 0.2s',
                      alignSelf: 'center',
                    }} // already using CSS variables
                    aria-label="Remove from group"
                  >⎋</button>
                ) : undefined
              }
              onDuplicate={onDuplicate}
              onClearOutput={onClearOutput}
              paramValues={cell.paramValues}
              onParamValuesChange={onCellUpdate ? v => onCellUpdate({ ...cell, paramValues: v }) : undefined}
              onFocus={undefined}
              onVisualizeResult={onVisualizeResult}
              allCells={allCells}
              fileId={fileId ?? cell.fileId}
            />
          </div>
        </div>
      )}
    </Draggable>
  );
};

export default NotebookCellDraggable;
