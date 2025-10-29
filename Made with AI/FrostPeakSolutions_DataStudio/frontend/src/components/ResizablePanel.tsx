import React, { useRef, useState, useEffect, ReactNode } from 'react';

interface ResizablePanelProps {
  direction: 'horizontal' | 'vertical';
  minSize?: number;
  maxSize?: number;
  initialSize?: number;
  storageKey?: string;
  children: ReactNode;
}

const ResizablePanel: React.FC<ResizablePanelProps> = ({
  direction,
  minSize = 180,
  maxSize = 500,
  initialSize = 240,
  storageKey,
  children,
}) => {
  const isHorizontal = direction === 'horizontal';
  const sizeProp = isHorizontal ? 'width' : 'height';
  const [size, setSize] = useState<number>(() => {
    if (storageKey) {
      const stored = localStorage.getItem(storageKey);
      if (stored) return parseInt(stored, 10);
    }
    return initialSize;
  });
  const panelRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  useEffect(() => {
    if (storageKey) localStorage.setItem(storageKey, String(size));
  }, [size, storageKey]);

  const onDrag = (delta: number) => {
    setSize((prev) => {
      let next = prev + delta;
      if (minSize) next = Math.max(next, minSize);
      if (maxSize) next = Math.min(next, maxSize);
      return next;
    });
  };

  const onMouseDown = (e: React.MouseEvent) => {
    dragging.current = true;
    let prev = isHorizontal ? e.clientX : e.clientY;
    const moveHandler = (moveEvent: MouseEvent) => {
      if (!dragging.current) return;
      const curr = isHorizontal ? moveEvent.clientX : moveEvent.clientY;
      onDrag(curr - prev);
      prev = curr;
    };
    const upHandler = () => {
      dragging.current = false;
      window.removeEventListener('mousemove', moveHandler);
      window.removeEventListener('mouseup', upHandler);
    };
    window.addEventListener('mousemove', moveHandler);
    window.addEventListener('mouseup', upHandler);
  };

  // Keyboard accessibility
  const onKeyDown = (e: React.KeyboardEvent) => {
    let delta = 0;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') delta = -16;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') delta = 16;
    if (delta !== 0) {
      onDrag(delta);
      e.preventDefault();
    }
  };

  return (
    <div
      ref={panelRef}
      style={{
        display: 'flex',
        flexDirection: isHorizontal ? 'row' : 'column',
        [sizeProp]: size,
        minWidth: isHorizontal ? minSize : undefined,
        minHeight: !isHorizontal ? minSize : undefined,
        maxWidth: isHorizontal ? maxSize : undefined,
        maxHeight: !isHorizontal ? maxSize : undefined,
        position: 'relative',
        overflow: 'visible',
      }}
    >
      <div style={{ flex: 1, minWidth: 0, minHeight: 0 }}>{children}</div>
      {/* Resize handle - always visible as a flex child on desktop */}
      <div
        role="separator"
        aria-orientation={isHorizontal ? 'vertical' : 'horizontal'}
        aria-valuenow={size}
        aria-valuemin={minSize}
        aria-valuemax={maxSize}
        tabIndex={0}
        className="resizablePanelHandle"
        style={{
          cursor: isHorizontal ? 'col-resize' : 'row-resize',
          background: 'var(--color-border-accent)',
          width: isHorizontal ? 5 : '100%',
          height: !isHorizontal ? 14 : '100%',
          minHeight: 48,
          outline: 'none',
          zIndex: 12,
          userSelect: 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRight: isHorizontal ? '2px solid var(--color-border)' : undefined,
          boxShadow: isHorizontal ? '2px 0 4px 0 rgba(0,0,0,0.04)' : undefined,
          backgroundClip: 'padding-box',
        }}
        onMouseDown={onMouseDown}
        onKeyDown={onKeyDown}
        title="Resize panel"
        aria-label="Resize panel"
      >
        {/* Grabber dots for visual affordance */}
        <div style={{
          width: isHorizontal ? 4 : 20,
          height: isHorizontal ? 20 : 4,
          borderRadius: 3,
          background: 'var(--color-border-dark)',
          opacity: 0.7,
          margin: isHorizontal ? '0 auto' : 'auto 0',
          display: 'flex',
          flexDirection: isHorizontal ? 'column' : 'row',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          {/* 3 vertical dots */}
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: 'var(--color-border-dark)',
            margin: '2px 0',
            display: 'block',
          }} />
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: 'var(--color-border-dark)',
            margin: '2px 0',
            display: 'block',
          }} />
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: 'var(--color-border-dark)',
            margin: '2px 0',
            display: 'block',
          }} />
        </div>
      </div>
    </div>
  );
};

export default ResizablePanel;
