
"""
CPP Code Editor Agent

This agent specializes in creating and editing CPP code with awareness of:
- CPP standards (CPP11/14/17/20/23)
- Header/source file separation
- CMake and Makefile support
- Modern CPP features
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class CPPCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for CPP code editing.
    
    Features:
    - CPP standards awareness (CPP11 through CPP23)
    - Header (.h, .hpp) and source (.cpp) file patterns
    - CMake and Makefile generation
    - Modern CPP features (auto, smart pointers, lambdas)
    - Include guard generation
    - Namespace organization
    """
    
    def __init__(
        self,
        name: str = "code_editor_cpp",
        description: str = "CPP code editor with standards awareness",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.cpp', '.cxx', '.cc', '.c', '.h', '.hpp', '.hxx'],
            **kwargs
        )
        self.build_files = ['CMakeLists.txt', 'Makefile']
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CPP code editing task."""
        self._log_action("Starting CPP code editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse CPP task")
            
            if not self._is_cpp_file(operation['path']):
                return self._build_error_result(f"Not a CPP file: {operation['path']}")
            
            # Determine file type
            file_info = self._analyze_cpp_file(operation['path'])
            operation.update(file_info)
            
            if operation['action'] == 'create':
                result = self._create_cpp_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_cpp_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("CPP code editing failed")
            return self._build_error_result(f"CPP error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:c\+\+|cpp)?\s*(?:file\s+)?([a-zA-Z0-9_/\-]+\.(?:cpp|cxx|cc|c|h|hpp|hxx))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        # Check for CMakeLists.txt or Makefile
        if 'cmake' in task.lower() or 'cmakelists' in task.lower():
            return {
                'action': 'create',
                'path': 'CMakeLists.txt',
                'content': None
            }
        elif 'makefile' in task.lower():
            return {
                'action': 'create',
                'path': 'Makefile',
                'content': None
            }
        
        return None
    
    def _is_cpp_file(self, path: str) -> bool:
        """Check if path is a CPP file or build file."""
        return (
            Path(path).suffix in self.supported_extensions or
            Path(path).name in self.build_files
        )
    
    def _analyze_cpp_file(self, path: str) -> Dict[str, Any]:
        """Analyze CPP file to determine type."""
        suffix = Path(path).suffix.lower()
        name = Path(path).name
        
        if name == 'CMakeLists.txt':
            return {'file_type': 'cmake', 'is_header': False}
        elif name == 'Makefile':
            return {'file_type': 'makefile', 'is_header': False}
        elif suffix in ['.h', '.hpp', '.hxx']:
            return {'file_type': 'header', 'is_header': True}
        elif suffix in ['.cpp', '.cxx', '.cc', '.c']:
            return {'file_type': 'source', 'is_header': False}
        
        return {'file_type': 'source', 'is_header': False}
    
    def _create_cpp_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new CPP file."""
        try:
            if not operation.get('content'):
                content = self._generate_cpp_content(operation, task, context)
            else:
                content = operation['content']
            
            # Add include guards for header files
            if operation.get('is_header', False):
                content = self._add_include_guards(content, operation['path'])
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created CPP file", str(file_path))
            
            return self._build_success_result(
                message=f"Created CPP {operation['file_type']}: {file_path}",
                data={
                    'path': str(file_path),
                    'file_type': operation['file_type'],
                    'is_header': operation.get('is_header', False),
                    'lines': len(content.splitlines())
                },
                next_context={'last_cpp_file': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create CPP file: {str(e)}", e)
    
    def _modify_cpp_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing CPP file."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            file_type = operation.get('file_type', 'CPP')
            prompt = f"""Modify this {file_type} code:

```cpp
{original_content}
```

Task: {task}

Generate the complete modified code.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified CPP file: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify CPP file: {str(e)}", e)
    
    def _generate_cpp_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate CPP code using LLM."""
        file_type = operation.get('file_type', 'source')
        
        prompt = f"""Generate CPP {file_type} for: {operation['path']}

Task: {task}

"""
        
        if file_type == 'header':
            prompt += """Requirements:
- Use #pragma once or include guards
- Declare classes, functions, or constants
- Add Doxygen-style comments
- Use namespace appropriately
- Forward declare when possible
"""
        elif file_type == 'source':
            prompt += """Requirements:
- Include necessary headers
- Use modern CPP features (CPP17 or later)
- Use smart pointers (unique_ptr, shared_ptr) over raw pointers
- Add implementation comments
- Use auto for type inference when clear
- Implement RAII principles
"""
        elif file_type == 'cmake':
            prompt += """Requirements:
- Specify minimum CMake version
- Set project name and version
- Set CPP standard (17, 20, or 23)
- Add executable or library targets
- Link necessary libraries
- Include install directives if needed
"""
        elif file_type == 'makefile':
            prompt += """Requirements:
- Define compiler (CXX = g++ or clang++)
- Set CPP standard flag (-std=c++17)
- Define compilation flags (CXXFLAGS)
- Create targets (all, clean)
- Define dependencies
"""
        
        prompt += "\nGenerate ONLY the code, no markdown or explanations.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _add_include_guards(self, content: str, file_path: str) -> str:
        """Add include guards to header file if not present."""
        # Check if already has #pragma once or include guards
        if '#pragma once' in content or '#ifndef' in content:
            return content
        
        # Generate include guard name from file path
        guard_name = Path(file_path).stem.upper() + '_H'
        guard_name = re.sub(r'[^A-Z0-9_]', '_', guard_name)
        
        guarded_content = f"""#ifndef {guard_name}
#define {guard_name}

{content}

#endif // {guard_name}
"""
        
        return guarded_content
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        patterns = [
            r'```(?:cpp|c\+\+|c)?\n?(.*?)\n?```',
            r'```cmake\n?(.*?)\n?```',
            r'```makefile\n?(.*?)\n?```'
        ]
        
        for pattern in patterns:
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
        """Generate CPP code content."""
        return self._generate_cpp_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate CPP syntax."""
        return self._validate_cpp_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply CPP formatting."""
        return self._apply_cpp_formatting(code)

