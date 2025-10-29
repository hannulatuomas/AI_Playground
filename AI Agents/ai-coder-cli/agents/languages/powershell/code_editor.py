
"""
PowerShell Script Editor Agent

This agent specializes in creating and editing PowerShell scripts with awareness of:
- PowerShell syntax and cmdlets
- Module awareness
- Windows-specific features
- PowerShell Core cross-platform support
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class PowerShellCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for PowerShell script editing.
    
    Features:
    - PowerShell syntax awareness
    - Cmdlet recognition
    - Module and function patterns
    - Windows PowerShell vs PowerShell Core
    - Comment-based help
    - Parameter validation
    """
    
    def __init__(
        self,
        name: str = "code_editor_powershell",
        description: str = "PowerShell script editor with module awareness",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.ps1', '.psm1', '.psd1'],
            **kwargs
        )
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute PowerShell script editing task."""
        self._log_action("Starting PowerShell script editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse PowerShell task")
            
            if not self._is_powershell_file(operation['path']):
                return self._build_error_result(f"Not a PowerShell file: {operation['path']}")
            
            # Determine file type
            file_type = self._get_file_type(operation['path'])
            operation['file_type'] = file_type
            
            if operation['action'] == 'create':
                result = self._create_powershell_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_powershell_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("PowerShell script editing failed")
            return self._build_error_result(f"PowerShell error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:powershell|ps1)?\s*(?:script\s+)?([a-zA-Z0-9_/\-]+\.(?:ps1|psm1|psd1))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        return None
    
    def _is_powershell_file(self, path: str) -> bool:
        """Check if path is a PowerShell file."""
        return Path(path).suffix in self.supported_extensions
    
    def _get_file_type(self, path: str) -> str:
        """Determine PowerShell file type."""
        suffix = Path(path).suffix.lower()
        
        if suffix == '.ps1':
            return 'script'
        elif suffix == '.psm1':
            return 'module'
        elif suffix == '.psd1':
            return 'manifest'
        
        return 'script'
    
    def _create_powershell_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new PowerShell file."""
        try:
            if not operation.get('content'):
                content = self._generate_powershell_content(operation, task, context)
            else:
                content = operation['content']
            
            # Write file (PowerShell uses UTF-8 with BOM typically, but UTF-8 without BOM is fine)
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created PowerShell file", str(file_path))
            
            return self._build_success_result(
                message=f"Created PowerShell {operation['file_type']}: {file_path}",
                data={
                    'path': str(file_path),
                    'file_type': operation['file_type'],
                    'lines': len(content.splitlines())
                },
                next_context={'last_powershell_file': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create PowerShell file: {str(e)}", e)
    
    def _modify_powershell_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing PowerShell file."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            prompt = f"""Modify this PowerShell script:

```powershell
{original_content}
```

Task: {task}

Generate the complete modified PowerShell code.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified PowerShell file: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify PowerShell file: {str(e)}", e)
    
    def _generate_powershell_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate PowerShell code using LLM."""
        file_type = operation.get('file_type', 'script')
        
        prompt = f"""Generate PowerShell {file_type} for: {operation['path']}

Task: {task}

Requirements:
- Use approved PowerShell verbs (Get-, Set-, New-, etc.)
- Add comment-based help at the top
- Use [CmdletBinding()] for advanced functions
- Define parameters with [Parameter()] attributes
- Use proper error handling (try/catch, -ErrorAction)
- Add Write-Verbose for debugging
- Follow PowerShell naming conventions (Verb-Noun)
"""
        
        if file_type == 'script':
            prompt += """
- This is a PowerShell script (.ps1)
- Can contain functions and script-level code
- Add #Requires statements if needed
"""
        elif file_type == 'module':
            prompt += """
- This is a PowerShell module (.psm1)
- Export functions with Export-ModuleMember
- Organize functions logically
"""
        elif file_type == 'manifest':
            prompt += """
- This is a module manifest (.psd1)
- Include ModuleVersion, Author, Description
- List exported functions in FunctionsToExport
"""
        
        prompt += "\nGenerate ONLY the PowerShell code, no markdown.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        pattern = r'```(?:powershell|ps1)?\n?(.*?)\n?```'
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
        """Generate PowerShell code content."""
        return self._generate_powershell_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate PowerShell syntax."""
        return self._validate_powershell_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply PowerShell formatting."""
        return self._apply_powershell_formatting(code)

