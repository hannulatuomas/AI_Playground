import React from 'react';
import { Droppable, Draggable } from '@hello-pangea/dnd';
import { NotebookCellGroup } from './NotebookGroupTypes';
import { NotebookCellData, genId } from './NotebookEditor';
import NotebookCellDraggable from './NotebookCellDraggable';

interface NotebookGroupProps {
  group: NotebookCellGroup;
  cells: NotebookCellData[];
  allGroups: NotebookCellGroup[];
  onUpdateGroup: (group: NotebookCellGroup) => void;
  onDeleteGroup: (groupId: string) => void;
  onUngroupAll: (groupId: string) => void;
  onCellUpdate: (cell: NotebookCellData) => void;
  onCellDelete: (cellId: string) => void;
  onCellAddToGroup: (cellId: string, groupId: string | null) => void;
  onRunAllInGroup: (groupId: string) => void;
  onDuplicate: (cellId: string) => void;
  dragHandleProps?: React.HTMLAttributes<HTMLDivElement>;
  runCell: (idx: number) => void;
  onVisualizeResult: (idx: number, data: any[]) => void;
}

const NotebookGroup: React.FC<NotebookGroupProps> = ({
  group,
  cells,
  allGroups,
  onUpdateGroup,
  onDeleteGroup,
  onUngroupAll,
  onCellUpdate,
  onCellDelete,
  onCellAddToGroup,
  onRunAllInGroup,
  onDuplicate,
  dragHandleProps,
  runCell,
  onVisualizeResult
}) => {
  return (
    <Droppable droppableId={group.id} type="cell">
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.droppableProps}
          className="cellContainer"
          style={{
            border: '1.5px solid var(--color-border)',
            borderRadius: 8,
            marginBottom: 22,
            background: snapshot.isDraggingOver ? 'var(--color-primary-light)' : 'var(--color-panel)',
            boxShadow: snapshot.isDraggingOver ? '0 0 0 4px var(--color-primary-shadow)' : undefined,
            transition: 'background 0.2s',
            width: '100%',
            boxSizing: 'border-box',
            padding: 0
          }}
        >
          {/* Group Header - visually match NotebookCell header */}
          <div
            className="cellHeader"
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '8px 18px 8px 18px',
              borderBottom: '1px solid var(--color-border)',
              background: 'var(--color-panel)',
              borderTopLeftRadius: 8,
              borderTopRightRadius: 8,
              fontWeight: 600,
              fontSize: 16,
              color: 'var(--color-primary)',
              minHeight: 42
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', flex: 1 }} {...dragHandleProps}>
              <input
                value={group.title}
                onChange={e => onUpdateGroup({ ...group, title: e.target.value })}
                style={{
                  fontWeight: 600,
                  fontSize: 16,
                  border: 'none',
                  background: 'transparent',
                  outline: 'none',
                  color: 'var(--color-primary)',
                  minWidth: 60,
                  marginRight: 18,
                  flex: 1,
                  padding: 0
                }}
                onBlur={e => onUpdateGroup({ ...group, title: group.title.trim() || 'Group' })}
                maxLength={40}
              />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--color-primary)', fontWeight: 600, fontSize: 15, cursor: 'pointer', marginRight: 8 }}
                title={group.collapsed ? 'Expand group' : 'Collapse group'}
                onClick={() => onUpdateGroup({ ...group, collapsed: !group.collapsed })}
              >
                {group.collapsed ? '▼' : '▲'}
              </button>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--color-success)', fontWeight: 600, fontSize: 15, cursor: 'pointer', marginRight: 8 }}
                title="Run all cells in this group"
                onClick={() => onRunAllInGroup(group.id)}
              >
                ▶ Run All
              </button>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--color-error)', fontWeight: 600, fontSize: 15, cursor: 'pointer', marginRight: 8 }}
                title="Ungroup all cells"
                onClick={() => onUngroupAll(group.id)}
              >Ungroup</button>
              <button
                style={{ background: 'none', border: 'none', color: 'var(--color-error)', fontWeight: 600, fontSize: 15, cursor: 'pointer' }}
                title="Delete group"
                onClick={() => onDeleteGroup(group.id)}
              >✕</button>
            </div>
          </div>
          {/* Grouped Cells */}
          {!group.collapsed && (
            <div style={{ position: 'relative', padding: '0', background: 'var(--color-bg)', minHeight: 160, display: 'flex', flexDirection: 'column', justifyContent: group.cellIds.length === 0 ? 'center' : 'flex-start', alignItems: 'stretch', border: snapshot.isDraggingOver && group.cellIds.length === 0 ? '3px solid var(--color-primary)' : undefined, backgroundColor: snapshot.isDraggingOver && group.cellIds.length === 0 ? 'var(--color-primary-light)' : 'var(--color-bg)', transition: 'border 0.2s, background 0.2s' }}>
              {group.cellIds.length === 0 && (
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-primary)',
                  fontWeight: 700,
                  fontStyle: 'italic',
                  fontSize: 20,
                  border: '2.5px dashed var(--color-primary)',
                  borderRadius: 10,
                  background: 'var(--color-primary-light)',
                  margin: 16,
                  pointerEvents: 'none',
                  userSelect: 'none',
                  zIndex: 1,
                  boxShadow: snapshot.isDraggingOver ? '0 0 0 4px var(--color-primary-shadow)' : undefined
                }}>
                  Drop cells here
                </div>
              )}
              {group.cellIds.map((cellId, idx) => {
  const cell = cells.find(c => c.id === cellId);
  if (!cell) return null;
  // Find the cell's index in the global cells array for correct runCell/onVisualizeResult call
  const globalIdx = cells.findIndex(c => c.id === cellId);
  return (
    <NotebookCellDraggable
      key={cell.id}
      cell={cell}
      index={idx}
      groups={allGroups}
      onCellUpdate={onCellUpdate}
      onCellDelete={onCellDelete}
      onAddToGroup={onCellAddToGroup}
      onRun={globalIdx !== -1 ? () => runCell(globalIdx) : undefined}
      executing={cell.executing}
      onDuplicate={() => {
        if (typeof window !== 'undefined') {
          const cellIndex = cells.findIndex(c => c.id === cell.id);
          if (cellIndex !== -1) {
            onDuplicate(cell.id);
          }
        }
      }}
      onClearOutput={() => onCellUpdate({ ...cell, result: undefined, error: undefined })}
      onChartTypeChange={type => onCellUpdate({ ...cell, chartType: type })}
      onChartDataChange={data => onCellUpdate({ ...cell, chartData: data })}
      chartType={cell.chartType}
      chartData={cell.chartData}
      allCells={cells}
      onVisualizeResult={globalIdx !== -1 ? (data: any[]) => onVisualizeResult(globalIdx, data) : undefined}
    />
  );
})}
              {provided.placeholder}
            </div>
          )}
        </div>
      )}
    </Droppable>
  );
};

export default NotebookGroup;
