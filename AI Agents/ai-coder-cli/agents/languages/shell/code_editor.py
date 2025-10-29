
"""
Shell Script Editor Agent (Bash/Sh/Zsh)

This agent specializes in creating and editing shell scripts with awareness of:
- Bash/Sh/Zsh syntax
- Shebang handling
- Cross-shell compatibility
- Shell script best practices
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class ShellCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for shell script editing.
    
    Features:
    - Bash/Sh/Zsh support
    - Shebang line handling
    - Script validation
    - Cross-shell compatibility awareness
    - Error handling patterns
    - Executable permissions
    """
    
    def __init__(
        self,
        name: str = "code_editor_shell",
        description: str = "Shell script editor with full bash/zsh/sh compatibility",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=['.sh', '.bash', '.zsh', '.ksh', '.dash'],
            **kwargs
        )
        self.shebangs = {
            'bash': '#!/bin/bash',
            'sh': '#!/bin/sh',
            'zsh': '#!/bin/zsh',
            'env_bash': '#!/usr/bin/env bash',
            'env_sh': '#!/usr/bin/env sh',
            'env_zsh': '#!/usr/bin/env zsh',
            'dash': '#!/bin/dash',
            'ksh': '#!/bin/ksh'
        }
        # Shell-specific features
        self.shell_features = {
            'bash': ['arrays', 'associative_arrays', 'process_substitution', '[[ ]]', 'local'],
            'zsh': ['arrays', 'associative_arrays', 'glob_qualifiers', 'parameter_expansion', 'local'],
            'sh': ['basic_posix'],  # Minimal POSIX features only
            'dash': ['basic_posix'],  # POSIX-compliant
            'ksh': ['arrays', 'associative_arrays', 'coprocesses', 'local']
        }
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell script editing task."""
        self._log_action("Starting shell script editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse shell script task")
            
            if not self._is_shell_file(operation['path']):
                return self._build_error_result(f"Not a shell script: {operation['path']}")
            
            # Detect shell type
            shell_type = self._detect_shell_type(operation['path'], task)
            operation['shell_type'] = shell_type
            
            if operation['action'] == 'create':
                result = self._create_shell_script(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_shell_script(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Shell script editing failed")
            return self._build_error_result(f"Shell script error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:shell|bash|sh|zsh)?\s*(?:script\s+)?([a-zA-Z0-9_/\-]+\.(?:sh|bash|zsh))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        return None
    
    def _is_shell_file(self, path: str) -> bool:
        """Check if path is a shell script."""
        return Path(path).suffix in self.supported_extensions
    
    def _detect_shell_type(self, path: str, task: str) -> str:
        """
        Detect shell type from path, task, or file content.
        
        Priority:
        1. File shebang (if file exists)
        2. File extension
        3. Task keywords
        4. Default to bash
        """
        # Check file extension
        path_lower = path.lower()
        task_lower = task.lower()
        
        # Try to read shebang from existing file
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#!'):
                        if 'bash' in first_line:
                            return 'bash'
                        elif 'zsh' in first_line:
                            return 'zsh'
                        elif 'dash' in first_line:
                            return 'dash'
                        elif 'ksh' in first_line:
                            return 'ksh'
                        elif '/sh' in first_line or first_line.endswith('sh'):
                            return 'sh'
            except Exception:
                pass
        
        # Check file extension
        if '.bash' in path_lower or path_lower.endswith('.bash'):
            return 'bash'
        elif '.zsh' in path_lower or path_lower.endswith('.zsh'):
            return 'zsh'
        elif '.dash' in path_lower:
            return 'dash'
        elif '.ksh' in path_lower:
            return 'ksh'
        elif '.sh' in path_lower or path_lower.endswith('.sh'):
            # .sh could be any shell, check task for hints
            if 'posix' in task_lower or 'portable' in task_lower or 'compatible' in task_lower:
                return 'sh'
            elif 'bash' in task_lower:
                return 'bash'
            elif 'zsh' in task_lower:
                return 'zsh'
            else:
                return 'sh'  # Default .sh to POSIX sh for maximum compatibility
        
        # Check task keywords
        if 'zsh' in task_lower:
            return 'zsh'
        elif 'bash' in task_lower:
            return 'bash'
        elif 'posix' in task_lower or 'sh ' in task_lower or task_lower.startswith('sh '):
            return 'sh'
        elif 'dash' in task_lower:
            return 'dash'
        elif 'ksh' in task_lower:
            return 'ksh'
        
        return 'bash'  # Default to bash as most common
    
    def _create_shell_script(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new shell script."""
        try:
            if not operation.get('content'):
                content = self._generate_shell_content(operation, task, context)
            else:
                content = operation['content']
            
            # Ensure shebang is present
            content = self._ensure_shebang(content, operation['shell_type'])
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            # Make executable (Unix-like systems)
            try:
                import stat
                file_path.chmod(file_path.stat().st_mode | stat.S_IEXEC)
                self.logger.info(f"Made script executable: {file_path}")
            except Exception as e:
                self.logger.warning(f"Could not make script executable: {e}")
            
            self._log_action("Created shell script", str(file_path))
            
            return self._build_success_result(
                message=f"Created shell script: {file_path}",
                data={
                    'path': str(file_path),
                    'shell_type': operation['shell_type'],
                    'executable': True,
                    'lines': len(content.splitlines())
                },
                next_context={'last_shell_script': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create shell script: {str(e)}", e)
    
    def _modify_shell_script(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing shell script."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            prompt = f"""Modify this shell script:

```bash
{original_content}
```

Task: {task}

Maintain the shebang line and shell type.
Generate the complete modified script.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            modified_content = self._ensure_shebang(modified_content, operation['shell_type'])
            
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified shell script: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify shell script: {str(e)}", e)
    
    def _generate_shell_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate shell script using LLM with shell-specific guidance."""
        shell_type = operation.get('shell_type', 'bash')
        
        prompt = f"""Generate a {shell_type} shell script.

Task: {task}
File: {operation['path']}

General Requirements:
- Start with appropriate shebang for {shell_type}
- Use proper error handling (set -e, set -u, set -o pipefail)
- Add comments explaining each section
- Use functions for reusable code
- Quote variables to prevent word splitting
- Check command success with || or &&
- Use meaningful variable names (UPPER_CASE for constants, lowercase for variables)
- Include help/usage function
- Handle signals with trap
"""
        
        # Shell-specific guidance
        if shell_type == 'sh' or shell_type == 'dash':
            prompt += """
Shell-Specific (POSIX sh):
- Use POSIX-compliant syntax ONLY
- NO bash-specific features: arrays, [[ ]], process substitution, etc.
- Use [ ] for tests, NOT [[ ]]
- Use simple command substitution: $(command) or `command`
- NO local keyword - use global variables carefully
- Use printf instead of echo for portability
- Test compatibility: #!/bin/sh
"""
        elif shell_type == 'bash':
            prompt += """
Shell-Specific (Bash):
- Use bash-specific features as appropriate: arrays, [[ ]], etc.
- Use local variables in functions
- Use [[ ]] for advanced conditional tests
- Arrays: declare -a for indexed, declare -A for associative
- Process substitution: <(command) when useful
- Use printf for formatted output
- Bash 4.0+ features available
"""
        elif shell_type == 'zsh':
            prompt += """
Shell-Specific (Zsh):
- Use zsh-specific features: glob qualifiers, advanced parameter expansion
- Use local variables in functions
- Arrays start at index 1 (not 0 like bash)
- Use [[ ]] for conditional tests
- Extended globbing: setopt extended_glob
- Use printf for formatted output
- Zsh 5.0+ features available
"""
        elif shell_type == 'ksh':
            prompt += """
Shell-Specific (KornShell):
- Use ksh-specific features: coprocesses, associative arrays
- Use local keyword typeset for function variables
- Arrays available
- Use [[ ]] for conditional tests
- Advanced parameter expansion available
"""
        
        prompt += """
Error Handling Pattern:
set -euo pipefail
trap 'echo "Error at line $LINENO"; exit 1' ERR

Generate ONLY the shell script code, no markdown blocks or explanations.
"""
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _ensure_shebang(self, content: str, shell_type: str) -> str:
        """Ensure script has proper shebang line."""
        lines = content.split('\n')
        
        # Check if shebang exists
        if lines and lines[0].startswith('#!'):
            return content
        
        # Add shebang
        shebang = self.shebangs.get(shell_type, '#!/bin/bash')
        return f"{shebang}\n\n{content}"
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        pattern = r'```(?:bash|sh|shell)?\n?(.*?)\n?```'
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
        """Generate Shell code content."""
        return self._generate_shell_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate Shell syntax."""
        return self._validate_shell_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply Shell formatting."""
        return self._apply_shell_formatting(code)

