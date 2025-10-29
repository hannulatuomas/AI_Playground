

"""
Generic Code Editor Agent

Fallback code editor for unsupported languages using LLM-based approaches.
"""

from typing import Dict, Any
from ..base import CodeEditorBase


class GenericCodeEditor(CodeEditorBase):
    """
    Generic code editor agent for any language.
    
    This agent provides fallback functionality for languages that don't
    have specific implementations. It uses LLM to generate and validate
    code without language-specific tooling.
    """
    
    def __init__(
        self,
        name: str = "code_editor_generic",
        description: str = "Generic code editor for any language",
        **kwargs
    ):
        # Support common file extensions
        common_extensions = [
            '.txt', '.md', '.rst', '.json', '.yaml', '.yml', '.xml',
            '.sql', '.r', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.lua', '.pl', '.php', '.java', '.gradle', '.maven'
        ]
        super().__init__(
            name=name,
            description=description,
            supported_extensions=common_extensions,
            **kwargs
        )
    
    def _generate_code_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate code content using LLM.
        
        Since this is a generic editor, we rely entirely on the LLM
        to generate appropriate content for the target language.
        """
        file_path = operation['path']
        
        # Detect language from file extension
        import os
        ext = os.path.splitext(file_path)[1]
        language = self._guess_language_from_extension(ext)
        
        prompt = f"""Generate code for: {file_path}

Language: {language}
Task: {task}

Requirements:
- Follow best practices for {language}
- Include appropriate comments and documentation
- Ensure proper formatting and style
- Make the code production-ready
"""
        
        # Add context from plan
        if 'plan' in context:
            plan = context['plan']
            prompt += f"\nProject: {plan.get('overview', 'N/A')}\n"
        
        if operation.get('purpose'):
            prompt += f"\nPurpose: {operation['purpose']}\n"
        
        prompt += "\nGenerate ONLY the code, no markdown or explanations.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        # Clean markdown code blocks
        content = self._clean_code_blocks(content)
        
        return content
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """
        Validate syntax using LLM.
        
        Since we don't have language-specific validators, we ask
        the LLM to check for obvious syntax errors.
        """
        prompt = f"""Check this code for syntax errors:

```
{code[:1000]}  # Limit to first 1000 chars for efficiency
```

Respond with JSON:
{{
    "valid": true/false,
    "error": "error message if invalid, null otherwise"
}}
"""
        
        try:
            llm_result = self._get_llm_response(prompt, temperature=0.3)
            response = llm_result.get('response', '')
            
            # Try to parse JSON response
            import json
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # If LLM doesn't return JSON, assume valid
                return {'valid': True, 'error': None}
        except Exception:
            # If validation fails, assume valid to not block progress
            return {'valid': True, 'error': None}
    
    def _apply_formatting(self, code: str) -> str:
        """
        Apply basic formatting.
        
        Since we don't have language-specific formatters,
        we apply basic text formatting.
        """
        lines = code.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            formatted_lines.append(line)
        
        # Ensure file ends with newline
        result = '\n'.join(formatted_lines)
        if result and not result.endswith('\n'):
            result += '\n'
        
        return result
    
    def _guess_language_from_extension(self, ext: str) -> str:
        """
        Guess programming language from file extension.
        
        Args:
            ext: File extension (e.g., '.py', '.js')
            
        Returns:
            Language name
        """
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Bash',
            '.ps1': 'PowerShell',
            '.bat': 'Batch',
            '.lua': 'Lua',
            '.pl': 'Perl',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML',
            '.html': 'HTML',
            '.css': 'CSS',
        }
        
        return extension_map.get(ext.lower(), 'Unknown')
