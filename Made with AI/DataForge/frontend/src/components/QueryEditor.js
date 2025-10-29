import { useState, useEffect } from 'react';
import axios from 'axios';
import Editor from '@monaco-editor/react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Play, Download, Database, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function QueryEditor({ connections, selectedConnection, onConnectionChange }) {
  const [query, setQuery] = useState('-- Write your SQL query here\nSELECT * FROM users LIMIT 10;');
  const [results, setResults] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [schema, setSchema] = useState([]);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [editorError, setEditorError] = useState(null);

  useEffect(() => {
    if (selectedConnection && selectedConnection.id) {
      loadSchema();
    } else {
      setSchema([]);
    }
  }, [selectedConnection]);

  const loadSchema = async () => {
    if (!selectedConnection || !selectedConnection.id) return;
    
    setLoadingSchema(true);
    try {
      const response = await axios.get(`${API}/schema/${selectedConnection.id}`);
      setSchema(response.data.schema || []);
    } catch (error) {
      console.error('Failed to load schema:', error);
      setSchema([]);
    } finally {
      setLoadingSchema(false);
    }
  };

  const executeQuery = async () => {
    if (!selectedConnection) {
      toast.error('Please select a connection');
      return;
    }

    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setExecuting(true);
    try {
      const response = await axios.post(`${API}/query/execute`, {
        connection_id: selectedConnection.id,
        query: query
      });

      if (response.data.status === 'success') {
        setResults(response.data);
        toast.success(`Query executed successfully! ${response.data.row_count} rows returned.`);
      } else {
        toast.error(response.data.message || 'Query execution failed');
        setResults({ status: 'error', message: response.data.message, traceback: response.data.traceback });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Query execution failed');
      setResults({ status: 'error', message: error.message });
    } finally {
      setExecuting(false);
    }
  };

  const exportResults = (format) => {
    if (!results || !results.results) return;

    let content = '';
    let filename = '';
    let mimeType = '';

    if (format === 'json') {
      content = JSON.stringify(results.results, null, 2);
      filename = 'query_results.json';
      mimeType = 'application/json';
    } else if (format === 'csv') {
      const headers = results.columns.join(',');
      const rows = results.results.map(row => 
        results.columns.map(col => JSON.stringify(row[col] || '')).join(',')
      );
      content = [headers, ...rows].join('\n');
      filename = 'query_results.csv';
      mimeType = 'text/csv';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    toast.success(`Results exported as ${format.toUpperCase()}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Query Editor</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Execute SQL queries with Monaco Editor</p>
        </div>
        <div className="flex items-center space-x-4 mt-2">
          {connections.length === 0 ? (
            <div className="bg-slate-100 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2">
              <p className="text-slate-600 dark:text-slate-400 text-sm">No connections available</p>
              <p className="text-slate-500 dark:text-slate-500 text-xs mt-1">Add a connection to start querying</p>
            </div>
          ) : (
            <Select 
              value={selectedConnection?.id || ""} 
              onValueChange={(id) => {
                const conn = connections.find(c => c.id === id);
                if (conn) onConnectionChange(conn);
              }}
            >
              <SelectTrigger className="w-64 bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-slate-900 dark:text-white" data-testid="connection-select">
                <SelectValue placeholder="Select connection" />
              </SelectTrigger>
              <SelectContent className="bg-white dark:bg-slate-700 border-slate-300 dark:border-slate-600">
                {connections.map(conn => (
                  <SelectItem key={conn.id} value={conn.id}>
                    {conn.name} ({conn.db_type})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </div>

      {connections.length === 0 ? (
        <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
          <CardContent className="py-12 text-center">
            <Database className="w-16 h-16 text-slate-400 dark:text-slate-600 mx-auto mb-4" />
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-4">No database connections available</p>
            <p className="text-slate-500 dark:text-slate-500 text-sm mb-6">Create a connection to start executing queries</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-12 gap-6">
          {/* Schema Explorer */}
          <Card className="col-span-3 bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 max-h-[600px] overflow-y-auto">
          <CardHeader>
            <CardTitle className="text-slate-900 dark:text-white flex items-center text-lg">
              <Database className="w-5 h-5 mr-2" />
              Schema
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingSchema ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
              </div>
            ) : !selectedConnection ? (
              <div className="text-slate-600 dark:text-slate-400 text-sm space-y-2">
                <p>No connection selected</p>
                <p className="text-xs">Select a connection to view schema</p>
              </div>
            ) : schema.length === 0 ? (
              <p className="text-slate-600 dark:text-slate-400 text-sm">No schema available</p>
            ) : (
              <div className="space-y-3">
                {schema.map((table, idx) => (
                  <div key={idx} className="border-l-2 border-slate-300 dark:border-slate-600 pl-3">
                    <p className="text-cyan-600 dark:text-cyan-400 font-semibold text-sm">{table.table}</p>
                    <div className="mt-2 space-y-1">
                      {table.columns.map((col, colIdx) => (
                        <p key={colIdx} className="text-slate-700 dark:text-slate-300 text-xs">
                          {col.name} <span className="text-slate-500 dark:text-slate-500">({col.type})</span>
                        </p>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Query Editor & Results */}
        <div className="col-span-9 space-y-6">
          {/* Editor */}
          <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-slate-900 dark:text-white">SQL Query</CardTitle>
              <Button
                onClick={executeQuery}
                disabled={executing || !selectedConnection}
                className="bg-cyan-600 hover:bg-cyan-700"
                data-testid="execute-query-button"
              >
                {executing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Execute (Ctrl+Enter)
                  </>
                )}
              </Button>
            </CardHeader>
            <CardContent>
              {editorError ? (
                <div className="bg-red-900/20 border border-red-700 rounded p-4">
                  <p className="text-red-400">Failed to load editor. Please refresh the page.</p>
                  <p className="text-red-300 text-sm mt-2">{editorError}</p>
                </div>
              ) : (
                <div className="monaco-editor-container">
                  <Editor
                    height="300px"
                    defaultLanguage="sql"
                    theme="vs-dark"
                    value={query}
                    onChange={(value) => setQuery(value || '')}
                    loading={<div className="flex items-center justify-center h-full"><Loader2 className="w-6 h-6 animate-spin text-cyan-400" /></div>}
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      lineNumbers: 'on',
                      scrollBeyondLastLine: false,
                      automaticLayout: true,
                    }}
                    onMount={(editor, monaco) => {
                      try {
                        if (monaco && editor) {
                          editor.addCommand(
                            monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
                            () => {
                              if (selectedConnection) {
                                executeQuery();
                              } else {
                                toast.error('Please select a connection first');
                              }
                            }
                          );
                        }
                      } catch (err) {
                        console.error('Monaco mount error:', err);
                        if (err && err.message) {
                          setEditorError(err.message);
                        }
                      }
                    }}
                    onValidate={(markers) => {
                      // Ignore validation errors, they're just warnings
                    }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Results */}
          {results && (
            <Card className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700" data-testid="query-results">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-slate-900 dark:text-white">
                  {results.status === 'success' ? 'Query Results' : 'Error'}
                </CardTitle>
                {results.status === 'success' && (
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => exportResults('json')}
                      className="border-slate-300 dark:border-slate-600"
                      data-testid="export-json-button"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      JSON
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => exportResults('csv')}
                      className="border-slate-300 dark:border-slate-600"
                      data-testid="export-csv-button"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      CSV
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {results.status === 'error' ? (
                  <div className="bg-red-900/20 border border-red-700 rounded p-4">
                    <p className="text-red-400 font-semibold mb-2">Error:</p>
                    <p className="text-red-300 text-sm">{results.message}</p>
                    {results.traceback && (
                      <pre className="text-red-300 text-xs mt-3 overflow-x-auto">
                        {results.traceback}
                      </pre>
                    )}
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="results-table">
                      <thead>
                        <tr>
                          {results.columns.map((col, idx) => (
                            <th key={idx}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {results.results.map((row, rowIdx) => (
                          <tr key={rowIdx}>
                            {results.columns.map((col, colIdx) => (
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
                    {results.results.length === 0 && (
                      <p className="text-slate-400 text-center py-8">No results</p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
        </div>
      )}
    </div>
  );
}
