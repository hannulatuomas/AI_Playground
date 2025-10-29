import React, { useRef, useEffect, useState } from 'react';

interface SQLAutocompleteProps {
  value: string;
  onChange: (val: string) => void;
  suggestions: string[];
  onSelect: (suggestion: string) => void;
  disabled?: boolean;
}

export default function SQLAutocomplete({ value, onChange, suggestions, onSelect, disabled }: SQLAutocompleteProps) {
  const [show, setShow] = useState(false);
  const [filtered, setFiltered] = useState<string[]>([]);
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (!show) return;
    setFiltered(
      suggestions.filter(s =>
        s.toLowerCase().includes(value.split(/\s|,|\(|\)/).pop()?.toLowerCase() || '')
      )
    );
    setActive(0);
  }, [value, suggestions, show]);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!show || filtered.length === 0) return;
    if (e.key === 'ArrowDown') {
      setActive(a => Math.min(a + 1, filtered.length - 1));
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      setActive(a => Math.max(a - 1, 0));
      e.preventDefault();
    } else if (e.key === 'Enter' && filtered[active]) {
      onSelect(filtered[active]);
      setShow(false);
      e.preventDefault();
    } else if (e.key === 'Escape') {
      setShow(false);
      e.preventDefault();
    }
  }

  function handleInput(e: React.ChangeEvent<HTMLTextAreaElement>) {
    onChange(e.target.value);
    setShow(true);
  }

  function handleSuggestionClick(s: string) {
    onSelect(s);
    setShow(false);
    inputRef.current?.focus();
  }

  return (
    <div style={{ position: 'relative' }}>
      <textarea
        ref={inputRef}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKeyDown}
        onFocus={() => setShow(true)}
        onBlur={() => setTimeout(() => setShow(false), 120)}
        disabled={disabled}
        style={{
          width: '100%',
          minHeight: 70,
          fontFamily: 'monospace',
          fontSize: 15,
          border: '1px solid var(--color-border)',
          borderRadius: 4,
          background: 'var(--color-bg-alt)',
          padding: '8px 12px',
          boxSizing: 'border-box',
          resize: 'vertical',
        }}
      />
      {show && filtered.length > 0 && (
        <ul
          ref={listRef}
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: '100%',
            zIndex: 20,
            background: 'var(--color-panel)',
            border: '1px solid var(--color-border-accent)',
            borderRadius: 5,
            margin: 0,
            padding: '2px 0',
            listStyle: 'none',
            maxHeight: 160,
            overflowY: 'auto',
            boxShadow: '0 2px 12px var(--color-shadow)',
          }}
        >
          {filtered.map((s, i) => (
            <li
              key={s}
              onMouseDown={() => handleSuggestionClick(s)}
              style={{
                padding: '6px 16px',
                background: i === active ? 'var(--color-primary-light)' : undefined,
                color: i === active ? 'var(--color-primary)' : undefined,
                cursor: 'pointer',
                fontWeight: i === active ? 600 : 400,
                fontSize: 15,
              }}
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
