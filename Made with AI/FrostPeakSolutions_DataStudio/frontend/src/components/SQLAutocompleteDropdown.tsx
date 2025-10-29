import React, { RefObject } from 'react';
import ReactDOM from 'react-dom';

interface SQLAutocompleteDropdownProps {
  suggestions: string[];
  activeIndex: number;
  onSuggestionClick: (suggestion: string) => void;
  suggestionRefs: RefObject<(HTMLLIElement | null)[]>;
  onSuggestionKeyDown: (e: React.KeyboardEvent, suggestion: string) => void;
  position: { top: number; left: number; width: number } | null;
}

import { useEffect } from 'react';

const SQLAutocompleteDropdown: React.FC<SQLAutocompleteDropdownProps> = ({
  suggestions,
  activeIndex,
  onSuggestionClick,
  suggestionRefs,
  onSuggestionKeyDown,
  position
}) => {
  useEffect(() => {
    if (suggestionRefs.current && suggestionRefs.current[activeIndex]) {
      suggestionRefs.current[activeIndex]?.scrollIntoView({ block: 'nearest' });
    }
  }, [activeIndex, suggestionRefs]);

  if (!position) return null;
  return ReactDOM.createPortal(
    <ul
      style={{
        position: 'absolute',
        top: position.top,
        left: position.left,
        width: position.width,
        zIndex: 20000,
        background: 'var(--color-panel)',
        border: '1px solid var(--color-border-accent)',
        borderRadius: 5,
        margin: 0,
        padding: '2px 0',
        listStyle: 'none',
        maxHeight: 160,
        overflowY: 'auto',
        boxShadow: '0 8px 24px var(--color-shadow)',
      }}
    >
      {suggestions.map((s, i) => (
        <li
          key={s}
          ref={el => {
            if (suggestionRefs.current) suggestionRefs.current[i] = el;
          }}
          onMouseDown={e => {
            e.preventDefault();
            onSuggestionClick(s);
          }}
          style={{
            padding: '6px 16px',
            background: i === activeIndex ? 'var(--color-primary-light)' : undefined,
            color: i === activeIndex ? 'var(--color-primary)' : undefined,
            cursor: 'pointer',
            fontWeight: i === activeIndex ? 600 : 400,
            fontSize: 15,
          }}
          tabIndex={0}
          onKeyDown={e => onSuggestionKeyDown(e, s)}
        >
          {s}
        </li>
      ))}
    </ul>,
    document.body
  );
}

export default SQLAutocompleteDropdown;
