import React, { useState } from 'react';
import { FieldTooltip } from './FieldTooltip';
import './NotebookCellsGlobal.css';
import Editor from 'react-simple-code-editor';
const Prism = require('prismjs');
require('prismjs/components/prism-sql');
require('prismjs/themes/prism.css');
import ReactMarkdown from 'react-markdown';

interface MarkdownCellProps {
  value: string;
  onChange: (val: string) => void;
  onFocus?: () => void;
}

const MarkdownCell: React.FC<MarkdownCellProps> = ({ value, onChange, onFocus }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [showMdHelp, setShowMdHelp] = useState(false);
  return (
    <div className="cellContainer">
      <div className="markdownInputHeader" style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
        <button
          type="button"
          className="markdownCollapseBtn"
          onClick={() => setCollapsed(c => !c)}
          style={{ marginRight: 8 }}
          aria-label={collapsed ? 'Expand Markdown Editor' : 'Collapse Markdown Editor'}
        >
          {collapsed ? '▶' : '▼'}
        </button>
        <span style={{ fontWeight: 500, color: 'var(--color-accent)', fontSize: 14 }}>Markdown Input
          <FieldTooltip id="markdown-help-tooltip" text="Write markdown text. Use headings, lists, code blocks, tables, links, etc. See help for examples." />
        </span>
        <button
          type="button"
          aria-expanded={showMdHelp ? 'true' : 'false'}
          aria-controls="markdown-help-section"
          style={{ marginLeft: 8, fontSize: 13, color: 'var(--color-primary)', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
          onClick={() => setShowMdHelp(h => !h)}
        >
          {showMdHelp ? 'Hide Help' : 'Show Help'}
        </button>
        {showMdHelp && (
          <div id="markdown-help-section" style={{ background: 'var(--color-bg-alt)', borderRadius: 4, padding: 10, margin: '8px 0', fontSize: 13, color: 'var(--color-text)' }}>
            <div><b>Sample Markdown:</b></div>
            <pre style={{ background: 'var(--color-primary-light)', borderRadius: 3, padding: 6, margin: '6px 0' }}>{`# Heading\n- List item\n
**Bold** \`inline code\``}</pre>
            <div><a href="https://www.markdownguide.org/cheat-sheet/" target="_blank" rel="noopener noreferrer">Markdown Cheat Sheet</a></div>
          </div>
        )}
      </div>
      {!collapsed && (
        <div className="markdownInputArea" style={{ border: '1px solid var(--color-border-light)', borderRadius: 4, padding: 6, background: 'var(--color-panel)', marginBottom: 10 }}>
          <Editor
            value={value}
            onValueChange={onChange}
            highlight={code => code}
            padding={10}
            textareaId={`notebook-cell-markdown-${String(value).slice(0,8)}`}
            textareaClassName="editor"
            onFocus={onFocus}
            aria-label="Markdown input editor"
            aria-describedby={`notebook-cell-markdown-desc-${String(value).slice(0,8)}`}
          />
          <div id={`notebook-cell-markdown-desc-${String(value).slice(0,8)}`} style={{ fontSize: 12, color: 'var(--color-disabled-text)', marginTop: 2 }}>
            Enter markdown text. Use headings, lists, code blocks, etc. Preview is shown below.
          </div>
        </div>
      )}
      <div className="markdownPreview" style={{ border: '1px solid var(--color-border-light)', borderRadius: 4, padding: 10, background: 'var(--color-bg-tertiary)' }}
        role="region" aria-label="Markdown preview area">
        <div style={{ fontWeight: 500, color: 'var(--color-accent)', fontSize: 14, marginBottom: 6 }}>Preview</div>
        <ReactMarkdown>{value}</ReactMarkdown>
      </div>
    </div>
  );
};

export default MarkdownCell;
