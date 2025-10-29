import { useState } from 'react';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ArrowLeft, Plus, Play, Trash2, Save, PlayCircle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function NotebookEditor({ notebook, connections, onClose, onUpdate }) {
  const [cells, setCells] = useState(notebook.cells || []);
  const [saving, setSaving] = useState(false);
  const [selectedConnection, setSelectedConnection] = useState(connections[0]?.id);

  const addCell = (type) => {
    const newCell = {
      id: Date.now().toString(),
      type: type, // 'sql', 'markdown', 'python'
      content: type === 'markdown' ? '# New Cell\n\nWrite your markdown here...' : '-- Write your code here',
      output: null
    };
    setCells([...cells, newCell]);
  };

  const updateCell = (cellId, content) => {
    setCells(cells.map(cell => 
      cell.id === cellId ? { ...cell, content } : cell
    ));
  };

  const deleteCell = (cellId) => {
    setCells(cells.filter(cell => cell.id !== cellId));
  };

  const executeCell = async (cellId) => {
    const cell = cells.find(c => c.id === cellId);
    if (!cell) return;

    try {
      if (cell.type === 'sql') {
        if (!selectedConnection) {
          toast.error('Please select a connection');
          return;
        }
        
        const connection = connections.find(c => c.id === selectedConnection);
        const response = await axios.post(`${API}/query/execute`, {
          connection_id: connection.id,
          query: cell.content
        });

        setCells(cells.map(c => 
          c.id === cellId ? { 
            ...c, 
            output: response.data.status === 'success' 
              ? { type: 'table', data: response.data } 
              : { type: 'error', message: response.data.message }
          } : c
        ));

        if (response.data.status === 'success') {
          toast.success('Query executed successfully');
        } else {
          toast.error('Query failed');
        }
      } else if (cell.type === 'python') {
        const response = await axios.post(`${API}/notebooks/execute-python`, {
          code: cell.content
        });

        setCells(cells.map(c => 
          c.id === cellId ? { 
            ...c, 
            output: response.data.status === 'success' 
              ? { type: 'text', data: response.data.output } 
              : { type: 'error', message: response.data.error, traceback: response.data.traceback }
          } : c
        ));

        if (response.data.status === 'success') {
          toast.success('Python code executed');
        } else {
          toast.error('Python execution failed');
        }
      }
    } catch (error) {
      toast.error('Execution failed');
      setCells(cells.map(c => 
        c.id === cellId ? { 
          ...c, 
          output: { type: 'error', message: error.message }
        } : c
      ));
    }
  };

  const executeAllCells = async () => {
    for (const cell of cells) {
      if (cell.type !== 'markdown') {
        await executeCell(cell.id);
      }
    }
    toast.success('All cells executed');
  };

  const saveNotebook = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/notebooks/${notebook.id}`, { cells });
      onUpdate();
      toast.success('Notebook saved');
    } catch (error) {
      toast.error('Failed to save notebook');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={onClose}
            className="border-slate-300 dark:border-slate-600"
            data-testid="close-notebook-button"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white">{notebook.name}</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Interactive Notebook</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={selectedConnection} onValueChange={setSelectedConnection}>
            <SelectTrigger className="w-56 bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-slate-900 dark:text-white" data-testid="notebook-connection-select">
              <SelectValue placeholder="Select connection" />
            </SelectTrigger>
            <SelectContent className="bg-white dark:bg-slate-700 border-slate-300 dark:border-slate-600">
              {connections.map(conn => (
                <SelectItem key={conn.id} value={conn.id}>
                  {conn.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            onClick={executeAllCells}
            variant="outline"
            className="border-slate-300 dark:border-slate-600"
            data-testid="run-all-cells-button"
          >
            <PlayCircle className="w-4 h-4 mr-2" />
            Run All
          </Button>
          <Button
            onClick={saveNotebook}
            disabled={saving}
            className="bg-cyan-600 hover:bg-cyan-700"
            data-testid="save-notebook-button"
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>

      {/* Add Cell Buttons */}
      <div className="flex space-x-3">
        <Button
          size="sm"
          onClick={() => addCell('sql')}
          className="bg-slate-700 hover:bg-slate-600"
          data-testid="add-sql-cell-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          SQL Cell
        </Button>
        <Button
          size="sm"
          onClick={() => addCell('markdown')}
          className="bg-slate-700 hover:bg-slate-600"
          data-testid="add-markdown-cell-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          Markdown Cell
        </Button>
        <Button
          size="sm"
          onClick={() => addCell('python')}
          className="bg-slate-700 hover:bg-slate-600"
          data-testid="add-python-cell-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          Python Cell
        </Button>
      </div>

      {/* Cells */}
      <div className="space-y-4">
        {cells.length === 0 ? (
          <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
            <CardContent className="py-12 text-center">
              <p className="text-slate-600 dark:text-slate-400 text-lg">No cells yet. Add your first cell!</p>
            </CardContent>
          </Card>
        ) : (
          cells.map((cell, idx) => (
            <Card key={cell.id} className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 notebook-cell" data-testid="notebook-cell">
              <CardContent className="p-4">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-mono text-slate-500">
                      [{idx + 1}] {cell.type.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    {cell.type !== 'markdown' && (
                      <Button
                        size="sm"
                        onClick={() => executeCell(cell.id)}
                        className="bg-cyan-600 hover:bg-cyan-700"
                        data-testid="run-cell-button"
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Run
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deleteCell(cell.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
                      data-testid="delete-cell-button"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                {/* Cell Editor */}
                {cell.type === 'markdown' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="monaco-editor-container">
                      <Editor
                        height="200px"
                        defaultLanguage="markdown"
                        theme="vs-dark"
                        value={cell.content}
                        onChange={(value) => updateCell(cell.id, value || '')}
                        options={{
                          minimap: { enabled: false },
                          fontSize: 13,
                          lineNumbers: 'off',
                          scrollBeyondLastLine: false,
                          wordWrap: 'on',
                        }}
                      />
                    </div>
                    <div className="bg-slate-900/50 rounded p-4 prose prose-invert max-w-none overflow-y-auto" style={{ maxHeight: '200px' }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {cell.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <div className="monaco-editor-container">
                    <Editor
                      height="200px"
                      defaultLanguage={cell.type === 'sql' ? 'sql' : 'python'}
                      theme="vs-dark"
                      value={cell.content}
                      onChange={(value) => updateCell(cell.id, value || '')}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineNumbers: 'on',
                        scrollBeyondLastLine: false,
                      }}
                    />
                  </div>
                )}

                {/* Cell Output */}
                {cell.output && (
                  <div className="mt-4 border-t border-slate-600 pt-4">
                    {cell.output.type === 'error' ? (
                      <div className="bg-red-900/20 border border-red-700 rounded p-3">
                        <p className="text-red-400 font-semibold text-sm mb-1">Error:</p>
                        <p className="text-red-300 text-sm">{cell.output.message}</p>
                        {cell.output.traceback && (
                          <pre className="text-red-300 text-xs mt-2 overflow-x-auto">
                            {cell.output.traceback}
                          </pre>
                        )}
                      </div>
                    ) : cell.output.type === 'text' ? (
                      <pre className="bg-slate-900/50 rounded p-3 text-slate-300 text-sm overflow-x-auto">
                        {cell.output.data}
                      </pre>
                    ) : cell.output.type === 'table' && cell.output.data.results ? (
                      <div className="overflow-x-auto">
                        <table className="results-table">
                          <thead>
                            <tr>
                              {cell.output.data.columns.map((col, idx) => (
                                <th key={idx}>{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {cell.output.data.results.slice(0, 100).map((row, rowIdx) => (
                              <tr key={rowIdx}>
                                {cell.output.data.columns.map((col, colIdx) => (
                                  <td key={colIdx} className="text-slate-300">
                                    {row[col] !== null && row[col] !== undefined 
                                      ? String(row[col]) 
                                      : <span className="text-slate-500 italic">NULL</span>
                                    }
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        <p className="text-slate-500 text-sm mt-2">
                          {cell.output.data.row_count} rows returned
                          {cell.output.data.results.length > 100 && ' (showing first 100)'}
                        </p>
                      </div>
                    ) : null}
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
