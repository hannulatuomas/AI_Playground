import React, { useRef, useEffect, useState } from 'react';
import Editor from 'react-simple-code-editor';
import SQLAutocompleteDropdown from './SQLAutocompleteDropdown';
import NotebookCellOutput from './NotebookCellOutput';
import { useFileContext } from './FileContext';
import { useSchema } from './useSchema';
import { validateSql, getCurrentWord, getSuggestions } from './notebookCellUtils';
import Prism from 'prismjs';

interface NotebookCellSQLProps {
  cellId: string;
  value: string;
  onChange: (val: string) => void;
  onRun?: () => void;
  executing?: boolean;
  error?: string | null;
  result?: any[];
  onFocus?: () => void;
  onVisualizeResult?: (data: any[]) => void;
  schemaTables?: any[];
}

const NotebookCellSQL: React.FC<NotebookCellSQLProps> = ({
  cellId,
  value,
  onChange,
  onRun,
  executing,
  error,
  result,
  onFocus,
  onVisualizeResult,
  schemaTables
}) => {
  const [sqlValidationError, setSqlValidationError] = useState<string | null>(null);
  const [showSqlHelp, setShowSqlHelp] = useState(false);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [activeSuggestion, setActiveSuggestion] = useState(0);
  const suggestionRefs = useRef<(HTMLLIElement | null)[]>([]);

  useEffect(() => {
    setSqlValidationError(null);
  }, [value]);

  function handleRunWithValidation() {
    const err = validateSql(value);
    setSqlValidationError(err);
    if (!err && onRun) onRun();
  }

  function handleEditorKeyDownWithValidation(e: React.KeyboardEvent) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleRunWithValidation();
    } else {
      handleEditorKeyDown(e);
    }
  }

  function handleEditorChange(val: string) {
    onChange(val);
    const textarea = getSqlTextarea();
    const cursor = textarea ? textarea.selectionStart : val.length;
    const word = getCurrentWord(val, cursor);
    if (word.length > 0) {
      const all = getSuggestions(schemaTables);
      const filtered = all.filter(s => s.toLowerCase().includes(word.toLowerCase()));
      setFilteredSuggestions(filtered);
      setShowAutocomplete(filtered.length > 0);
      setActiveSuggestion(0);
    } else {
      setShowAutocomplete(false);
      setFilteredSuggestions([]);
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
      const textarea = getSqlTextarea();
      if (textarea) {
        textarea.selectionStart = textarea.selectionEnd = before.length + s.length + 1;
        textarea.focus();
      }
    }, 0);
  }

  function getSqlTextarea(): HTMLTextAreaElement | null {
    return document.getElementById(`notebook-cell-sql-${cellId}`) as HTMLTextAreaElement | null;
  }

  return (
    <div className="cellContainer">
      <div style={{ marginBottom: 4 }}>
        <button className="secondaryButton" onClick={() => setShowSqlHelp(h => !h)}>
          SQL Help
        </button>
        {showSqlHelp && (
          <div style={{ background: 'var(--color-bg-tertiary)', padding: 8, border: '1px solid var(--color-border-light)', borderRadius: 4, marginTop: 4 }}>
            <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--color-text-primary)' }}>SQL Syntax Help</div>
            <div style={{ fontSize: 14, color: 'var(--color-text-secondary)' }}>
              SELECT ... FROM ...<br />INSERT INTO ... VALUES ...<br />UPDATE ... SET ...<br />DELETE FROM ...<br />CREATE TABLE ...<br />DROP TABLE ...
            </div>
            <div style={{ marginTop: 4, color: 'var(--color-text-link)' }}><a href="https://www.sqltutorial.org/sql-cheat-sheet/" target="_blank" rel="noopener noreferrer">SQL Cheat Sheet</a></div>
          </div>
        )}
      </div>
      <Editor
        value={value}
        onValueChange={handleEditorChange}
        highlight={code => Prism.highlight(code, Prism.languages.sql, 'sql')}
        padding={10}
        textareaId={`notebook-cell-sql-${cellId}`}
        textareaClassName="editor-textarea"
        style={{ fontFamily: 'monospace', fontSize: 15, minHeight: 70, background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border-light)', borderRadius: 4, outline: 'none', width: '100%', resize: 'vertical' }}
        placeholder="Enter SQL query..."
        onFocus={onFocus}
        onKeyDown={handleEditorKeyDownWithValidation}
      />
      {sqlValidationError && (
        <div style={{ color: 'var(--color-error)', fontSize: 14, marginTop: 4 }}>{sqlValidationError}</div>
      )}
      {showAutocomplete && filteredSuggestions.length > 0 && (
        <SQLAutocompleteDropdown
          suggestions={filteredSuggestions}
          activeIndex={activeSuggestion}
          onSuggestionClick={s => {
            handleSuggestionClick(s);
          }}
          suggestionRefs={suggestionRefs}
          onSuggestionKeyDown={(e, s) => {
            if (e.key === 'Enter') handleSuggestionClick(s);
          }}
          position={(() => {
            const textarea = getSqlTextarea();
            if (!textarea) return null;
            const rect = textarea.getBoundingClientRect();
            return {
              top: rect.bottom + window.scrollY,
              left: rect.left + window.scrollX,
              width: rect.width
            };
          })()}
        />
      )}
      <NotebookCellOutput executing={executing} error={error} result={result} onVisualize={onVisualizeResult} />
    </div>
  );
};

export default NotebookCellSQL;
