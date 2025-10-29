
"""
Windows Batch File Editor Agent

This agent specializes in creating and editing Windows batch files with awareness of:
- Batch file syntax
- Windows command awareness
- Environment variables
- Control flow structures
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class BatchCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for Windows batch file editing.
    
    Features:
    - Batch file syntax (.bat, .cmd)
    - Windows command awareness
    - Environment variable handling
    - Control flow (IF, FOR, GOTO)
    - Error level checking
    """
    
    def __init__(
        self,
        name: str = "code_editor_batch",
        description: str = "Windows batch file editor with CMD awareness",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.bat', '.cmd'],
            **kwargs
        )
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute batch file editing task."""
        self._log_action("Starting batch file editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse batch file task")
            
            if not self._is_batch_file(operation['path']):
                return self._build_error_result(f"Not a batch file: {operation['path']}")
            
            if operation['action'] == 'create':
                result = self._create_batch_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_batch_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Batch file editing failed")
            return self._build_error_result(f"Batch file error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:batch|cmd|bat)?\s*(?:file\s+)?([a-zA-Z0-9_/\-]+\.(?:bat|cmd))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        return None
    
    def _is_batch_file(self, path: str) -> bool:
        """Check if path is a batch file."""
        return Path(path).suffix in self.supported_extensions
    
    def _create_batch_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new batch file."""
        try:
            if not operation.get('content'):
                content = self._generate_batch_content(operation, task, context)
            else:
                content = operation['content']
            
            # Ensure @echo off at the start (common practice)
            if not content.strip().startswith('@echo off'):
                content = '@echo off\n' + content
            
            # Write file (Windows line endings)
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(content)
            
            self._log_action("Created batch file", str(file_path))
            
            return self._build_success_result(
                message=f"Created batch file: {file_path}",
                data={
                    'path': str(file_path),
                    'lines': len(content.splitlines())
                },
                next_context={'last_batch_file': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create batch file: {str(e)}", e)
    
    def _modify_batch_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing batch file."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            prompt = f"""Modify this Windows batch file:

```batch
{original_content}
```

Task: {task}

Generate the complete modified batch file.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            
            with open(file_path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified batch file: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify batch file: {str(e)}", e)
    
    def _generate_batch_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate batch file content using LLM."""
        prompt = f"""Generate Windows batch file for: {operation['path']}

Task: {task}

Requirements:
- Start with @echo off
- Use REM for comments
- Use SETLOCAL at the beginning
- Check ERRORLEVEL after critical commands
- Use %variable% syntax for variables
- Add error handling (IF ERRORLEVEL 1 ...)
- Use CALL for calling other batch files
- End with ENDLOCAL if using SETLOCAL
"""
        
        prompt += "\nGenerate ONLY the batch file code, no markdown.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        pattern = r'```(?:batch|bat|cmd)?\n?(.*?)\n?```'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return content.strip()

    # Abstract method implementations (required by CodeEditorBase)
    def _generate_code_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate Batch code content."""
        return self._generate_batch_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate Batch syntax."""
        return self._validate_batch_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply Batch formatting."""
        return self._apply_batch_formatting(code)

