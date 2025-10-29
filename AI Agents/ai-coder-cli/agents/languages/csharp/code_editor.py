
"""
CSharp/.NET/ASP.NET Code Editor Agent

This agent specializes in creating and editing CSharp code with awareness of:
- CSharp language conventions and style guidelines
- .NET framework versions
- NuGet package management
- ASP.NET Core support
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class CSharpCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for CSharp and .NET code editing.
    
    Features:
    - CSharp language conventions
    - .NET framework awareness
    - ASP.NET Core patterns
    - NuGet package references
    - Project structure awareness (.csproj)
    - Using statements organization
    - XML documentation comments
    """
    
    def __init__(
        self,
        name: str = "code_editor_csharp",
        description: str = "CSharp/.NET code editor with framework awareness",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.cs', '.csproj', '.cshtml', '.razor'],
            **kwargs
        )
        self.dotnet_versions = ['net8.0', 'net7.0', 'net6.0', 'netstandard2.1']
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CSharp code editing task."""
        self._log_action("Starting CSharp code editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse CSharp editing task")
            
            if not self._is_csharp_file(operation['path']):
                return self._build_error_result(f"Not a CSharp file: {operation['path']}")
            
            # Determine file type
            file_type = self._get_file_type(operation['path'])
            operation['file_type'] = file_type
            
            # Execute appropriate action
            if operation['action'] == 'create':
                result = self._create_csharp_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_csharp_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("CSharp code editing failed")
            return self._build_error_result(f"CSharp editing error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:c#|csharp|\.net)?\s*(?:file\s+)?([a-zA-Z0-9_/\-]+\.(?:cs|csproj|cshtml|razor))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        return None
    
    def _is_csharp_file(self, path: str) -> bool:
        """Check if path is a CSharp file."""
        return Path(path).suffix in self.supported_extensions
    
    def _get_file_type(self, path: str) -> str:
        """Determine CSharp file type."""
        suffix = Path(path).suffix.lower()
        
        if suffix == '.cs':
            path_lower = path.lower()
            if 'controller' in path_lower:
                return 'controller'
            elif 'model' in path_lower or 'entity' in path_lower:
                return 'model'
            elif 'service' in path_lower:
                return 'service'
            elif 'test' in path_lower:
                return 'test'
            else:
                return 'class'
        elif suffix == '.csproj':
            return 'project'
        elif suffix == '.cshtml':
            return 'razor_view'
        elif suffix == '.razor':
            return 'razor_component'
        
        return 'unknown'
    
    def _create_csharp_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new CSharp file."""
        try:
            if not operation.get('content'):
                content = self._generate_csharp_content(operation, task, context)
            else:
                content = operation['content']
            
            # Apply CSharp formatting
            content = self._format_csharp_code(content)
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created CSharp file", str(file_path))
            
            return self._build_success_result(
                message=f"Created CSharp file: {file_path}",
                data={
                    'path': str(file_path),
                    'file_type': operation['file_type'],
                    'lines': len(content.splitlines()),
                    'size': len(content)
                },
                next_context={'last_csharp_file': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create CSharp file: {str(e)}", e)
    
    def _modify_csharp_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing CSharp file."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            prompt = f"""Modify this CSharp code:

```csharp
{original_content}
```

Task: {task}

Generate the complete modified CSharp code.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            modified_content = self._format_csharp_code(modified_content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified CSharp file: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify CSharp file: {str(e)}", e)
    
    def _generate_csharp_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate CSharp code using LLM."""
        file_type = operation.get('file_type', 'class')
        file_path = operation['path']
        
        prompt = f"""Generate CSharp code for: {file_path}

Task: {task}
File Type: {file_type}

Requirements:
- Use modern CSharp syntax (CSharp 10+)
- Follow CSharp naming conventions (PascalCase for classes/methods)
- Add XML documentation comments (///)
- Include proper namespace declaration
- Add necessary using statements
- Use nullable reference types where appropriate
"""
        
        if file_type == 'controller':
            prompt += """
- This is an ASP.NET Core Controller
- Inherit from ControllerBase or Controller
- Use attribute routing
- Add [ApiController] if REST API
- Include action methods with HTTP verb attributes
"""
        elif file_type == 'model':
            prompt += """
- This is a data model or entity class
- Include properties with get/set
- Add data annotations if needed
- Consider constructor initialization
"""
        elif file_type == 'service':
            prompt += """
- This is a service class
- Define interface if appropriate
- Use dependency injection patterns
- Include async methods where applicable
"""
        elif file_type == 'project':
            prompt += """
- This is a .csproj project file
- Use SDK-style project format
- Include TargetFramework (net8.0 or appropriate)
- Add necessary PackageReference items
"""
        
        prompt += "\nGenerate ONLY the CSharp code, no markdown or explanations.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _format_csharp_code(self, code: str) -> str:
        """Apply basic CSharp formatting."""
        lines = code.split('\n')
        formatted_lines = [line.rstrip() for line in lines]
        
        result = '\n'.join(formatted_lines)
        if result and not result.endswith('\n'):
            result += '\n'
        
        return result
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        pattern = r'```(?:csharp|cs|c#)?\n?(.*?)\n?```'
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
        """Generate CSharp code content."""
        return self._generate_csharp_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate CSharp syntax."""
        return self._validate_csharp_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply CSharp formatting."""
        return self._apply_csharp_formatting(code)

