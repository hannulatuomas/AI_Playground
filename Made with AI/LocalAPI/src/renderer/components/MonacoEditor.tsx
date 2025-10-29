import React, { useRef } from 'react';
import Editor, { OnMount } from '@monaco-editor/react';
import { Box, useTheme } from '@mui/material';
import type { editor } from 'monaco-editor';

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  height?: string | number;
  readOnly?: boolean;
  placeholder?: string;
}

const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  onChange,
  language = 'javascript',
  height = '300px',
  readOnly = false,
  placeholder,
}) => {
  const theme = useTheme();
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure JavaScript/TypeScript language features
    monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
      noSemanticValidation: false,
      noSyntaxValidation: false,
    });

    monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ES2020,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.CommonJS,
      noEmit: true,
      esModuleInterop: true,
      allowJs: true,
    });

    // Add pm API type definitions
    monaco.languages.typescript.javascriptDefaults.addExtraLib(
      `
      declare const pm: {
        test: (name: string, fn: () => void) => void;
        expect: (value: any) => any;
        response: {
          code: number;
          status: string;
          headers: Record<string, string>;
          json: () => any;
          text: () => string;
          responseTime: number;
          responseSize: number;
        };
        variables: {
          get: (key: string) => any;
          set: (key: string, value: any) => void;
        };
        environment: {
          get: (key: string) => any;
          set: (key: string, value: any) => void;
        };
        globals: {
          get: (key: string) => any;
          set: (key: string, value: any) => void;
        };
        request: {
          url: string;
          method: string;
          headers: Record<string, string>;
          body?: any;
        };
        jsonPath: (obj: any, path: string) => any[];
        extractJson: (path: string, varName?: string) => any;
      };
      
      declare const console: {
        log: (...args: any[]) => void;
        error: (...args: any[]) => void;
        warn: (...args: any[]) => void;
      };
      `,
      'ts:pm.d.ts'
    );

    // Show placeholder if empty
    if (!value && placeholder) {
      editor.setValue(`// ${placeholder}`);
      editor.setSelection({
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 1,
        endColumn: placeholder.length + 4,
      });
    }
  };

  const handleEditorChange = (value: string | undefined) => {
    onChange(value || '');
  };

  return (
    <Box
      sx={{
        height,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        overflow: 'hidden',
        '& .monaco-editor': {
          paddingTop: '8px',
        },
      }}
    >
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        theme={theme.palette.mode === 'dark' ? 'vs-dark' : 'light'}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          lineNumbers: 'on',
          roundedSelection: true,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          wordWrap: 'on',
          wrappingIndent: 'indent',
          formatOnPaste: true,
          formatOnType: true,
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: 'on',
          quickSuggestions: {
            other: true,
            comments: false,
            strings: false,
          },
          parameterHints: {
            enabled: true,
          },
          suggest: {
            showKeywords: true,
            showSnippets: true,
          },
          folding: true,
          foldingStrategy: 'indentation',
          showFoldingControls: 'always',
          contextmenu: true,
          scrollbar: {
            vertical: 'auto',
            horizontal: 'auto',
            useShadows: false,
            verticalScrollbarSize: 10,
            horizontalScrollbarSize: 10,
          },
        }}
      />
    </Box>
  );
};

export default MonacoEditor;
