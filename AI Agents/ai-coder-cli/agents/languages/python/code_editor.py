
"""
Python-Specific Code Editor Agent

This agent specializes in creating and editing Python code with awareness of:
- PEP 8 style guidelines
- Python syntax validation
- Virtual environment awareness
- Support for pytest/unittest frameworks
"""

import re
import ast
from pathlib import Path
from typing import Dict, Any, Optional, List

from ...base import CodeEditorBase


class PythonCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for Python code editing and creation.
    
    Features:
    - PEP 8 compliance awareness
    - Python syntax validation using ast module
    - Import statement organization
    - Docstring generation
    - Type hints support
    - Virtual environment detection
    - Test file recognition (pytest/unittest)
    """
    
    def __init__(
        self,
        name: str = "code_editor_python",
        description: str = "Python-specific code editor with PEP8 awareness",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.py', '.pyw'],
            **kwargs
        )
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Python code editing task.
        
        Args:
            task: Description of code editing task
            context: Execution context with optional 'file_path', 'content', 'plan'
            
        Returns:
            Result dictionary with success status and file details
        """
        self._log_action("Starting Python code editing", task[:100])
        
        try:
            # Parse task to determine operation
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse Python editing task")
            
            # Validate Python file
            if not self._is_python_file(operation['path']):
                return self._build_error_result(
                    f"Not a Python file: {operation['path']}"
                )
            
            # Generate or validate content
            if operation['action'] == 'create':
                result = self._create_python_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_python_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Python code editing failed")
            return self._build_error_result(f"Python editing error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract file operation details."""
        # Check context for explicit file information
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content'),
                'test_file': self._is_test_file(context['file_path'])
            }
        
        # Extract from plan
        if 'plan' in context and 'files' in context['plan']:
            for file_info in context['plan']['files']:
                if file_info.get('path', '').endswith('.py'):
                    return {
                        'action': 'create',
                        'path': file_info['path'],
                        'content': None,
                        'test_file': self._is_test_file(file_info['path']),
                        'purpose': file_info.get('purpose', '')
                    }
        
        # Parse from task string
        pattern = r'(\w+)\s+(?:python\s+)?(?:file\s+)?([a-zA-Z0-9_/\-]+\.py)'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            path = match.group(2)
            return {
                'action': action,
                'path': path,
                'content': None,
                'test_file': self._is_test_file(path)
            }
        
        return None
    
    def _is_python_file(self, path: str) -> bool:
        """Check if path is a Python file."""
        return Path(path).suffix in self.supported_extensions
    
    def _is_test_file(self, path: str) -> bool:
        """Check if this is a test file."""
        path_lower = path.lower()
        return (
            'test_' in path_lower or
            '_test' in path_lower or
            '/tests/' in path_lower or
            '/test/' in path_lower
        )
    
    def _create_python_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new Python file."""
        try:
            # Generate content if not provided
            if not operation.get('content'):
                content = self._generate_python_content(operation, task, context)
            else:
                content = operation['content']
            
            # Validate syntax
            validation = self._validate_python_syntax(content)
            if not validation['valid']:
                self.logger.warning(f"Syntax warning: {validation['error']}")
                # Continue anyway, LLM might fix in next iteration
            
            # Apply PEP 8 formatting hints
            content = self._apply_pep8_formatting(content)
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created Python file", str(file_path))
            
            return self._build_success_result(
                message=f"Created Python file: {file_path}",
                data={
                    'path': str(file_path),
                    'lines': len(content.splitlines()),
                    'size': len(content),
                    'test_file': operation['test_file'],
                    'syntax_valid': validation['valid']
                },
                next_context={
                    'last_python_file': str(file_path),
                    'is_test': operation['test_file']
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create Python file: {str(e)}", e)
    
    def _modify_python_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing Python file."""
        try:
            file_path = Path(operation['path'])
            
            # Read existing content
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification using LLM
            modified_content = self._generate_modification(
                original_content,
                task,
                context
            )
            
            # Validate syntax
            validation = self._validate_python_syntax(modified_content)
            if not validation['valid']:
                self.logger.warning(f"Modified code has syntax issues: {validation['error']}")
            
            # Apply formatting
            modified_content = self._apply_pep8_formatting(modified_content)
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified Python file: {file_path}",
                data={
                    'path': str(file_path),
                    'lines_before': len(original_content.splitlines()),
                    'lines_after': len(modified_content.splitlines()),
                    'syntax_valid': validation['valid']
                }
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify Python file: {str(e)}", e)
    
    def _generate_python_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate Python code content using LLM."""
        prompt = self._build_python_prompt(operation, task, context)
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        # Clean markdown code blocks
        content = self._clean_code_blocks(content)
        
        return content
    
    def _build_python_prompt(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Build LLM prompt for Python code generation."""
        is_test = operation.get('test_file', False)
        file_path = operation['path']
        
        prompt = f"""Generate Python code for: {file_path}

Task: {task}

Requirements:
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Include comprehensive docstrings (Google/NumPy style)
- Organize imports: stdlib, third-party, local
- Add inline comments for complex logic
- Handle errors with try-except where appropriate
"""
        
        if is_test:
            prompt += """
- This is a TEST FILE
- Use pytest or unittest framework
- Include test cases with assertions
- Use descriptive test function names (test_*)
- Add fixtures if needed
"""
        
        # Add context from plan
        if 'plan' in context:
            plan = context['plan']
            prompt += f"\nProject: {plan.get('overview', 'N/A')}\n"
            
        if operation.get('purpose'):
            prompt += f"\nPurpose: {operation['purpose']}\n"
        
        prompt += "\nGenerate ONLY the Python code, no markdown or explanations.\n"
        
        return prompt
    
    def _generate_modification(
        self,
        original_content: str,
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate modified Python code."""
        prompt = f"""Modify the following Python code according to the task.

Original Code:
```python
{original_content}
```

Task: {task}

Requirements:
- Maintain PEP 8 compliance
- Keep existing functionality unless explicitly changed
- Update docstrings if function signatures change
- Preserve imports unless no longer needed

Generate the complete modified Python code (no markdown).
"""
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _validate_python_syntax(self, code: str) -> Dict[str, Any]:
        """
        Validate Python syntax using ast module.
        
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        try:
            ast.parse(code)
            return {'valid': True, 'error': None}
        except SyntaxError as e:
            return {
                'valid': False,
                'error': f"Line {e.lineno}: {e.msg}"
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def _apply_pep8_formatting(self, code: str) -> str:
        """
        Apply basic PEP 8 formatting rules.
        
        Note: This is a simple implementation. For production use,
        consider integrating tools like black or autopep8.
        """
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Ensure no more than 2 consecutive blank lines
            if not line:
                if len(formatted_lines) >= 2:
                    if not formatted_lines[-1] and not formatted_lines[-2]:
                        continue  # Skip third+ consecutive blank line
            
            formatted_lines.append(line)
        
        # Ensure file ends with newline
        result = '\n'.join(formatted_lines)
        if result and not result.endswith('\n'):
            result += '\n'
        
        return result
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks from LLM output."""
        # Remove ```python\n...\n```
        pattern = r'```(?:python)?\n?(.*?)\n?```'
        match = re.search(pattern, content, re.DOTALL)
        
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
        """Generate Python code content (delegates to _generate_python_content)."""
        return self._generate_python_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate Python syntax (delegates to _validate_python_syntax)."""
        return self._validate_python_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply Python formatting (delegates to _apply_pep8_formatting)."""
        return self._apply_pep8_formatting(code)

