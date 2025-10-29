"""
Agent Capabilities Module

Provides comprehensive capability classes for agents to use:
- Prompts (dynamic prompt construction and templating)
- Rules (rule-based decision making and constraints)
- Memories (short-term and long-term memory access)
- Files (file reading, writing, and manipulation)
- Codebase (code analysis and interaction)
- Console (input/output with structured data extraction)

These capabilities are designed to be modular and reusable across all agent types.
"""

import logging
import re
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


logger = logging.getLogger(__name__)


# ==============================================================================
# Prompt Capabilities
# ==============================================================================

class PromptManager:
    """
    Manages dynamic prompt construction and templating for agents.
    
    Features:
    - Template-based prompts with variable substitution
    - Prompt composition from multiple sections
    - Context-aware prompt generation
    - Token counting and optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the prompt manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.templates: Dict[str, str] = {}
        self.logger = logging.getLogger(f"{__name__}.PromptManager")
    
    def register_template(self, name: str, template: str) -> None:
        """
        Register a prompt template.
        
        Args:
            name: Template name
            template: Template string with {variables}
        """
        self.templates[name] = template
        self.logger.debug(f"Registered template: {name}")
    
    def build_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        sections: Optional[List[Tuple[str, str]]] = None
    ) -> str:
        """
        Build a prompt from a template with variables and sections.
        
        Args:
            template_name: Name of the template to use
            variables: Variables to substitute in the template
            sections: Optional additional sections as (title, content) tuples
            
        Returns:
            Constructed prompt string
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Substitute variables
        try:
            prompt = template.format(**variables)
        except KeyError as e:
            self.logger.error(f"Missing variable in template {template_name}: {e}")
            raise ValueError(f"Missing variable: {e}") from e
        
        # Add sections if provided
        if sections:
            prompt += "\n\n"
            for title, content in sections:
                prompt += f"\n### {title}\n{content}\n"
        
        self.logger.debug(f"Built prompt from template {template_name}: {len(prompt)} chars")
        return prompt
    
    def compose_prompt(self, *parts: str, separator: str = "\n\n") -> str:
        """
        Compose a prompt from multiple parts.
        
        Args:
            *parts: Prompt parts to combine
            separator: Separator between parts
            
        Returns:
            Composed prompt
        """
        return separator.join(part for part in parts if part)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text (rough approximation).
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        return len(text) // 4
    
    def optimize_prompt(self, prompt: str, max_tokens: int) -> str:
        """
        Optimize prompt to fit within token limit.
        
        Args:
            prompt: Original prompt
            max_tokens: Maximum token limit
            
        Returns:
            Optimized prompt
        """
        estimated_tokens = self.estimate_tokens(prompt)
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Truncate to fit (simple strategy)
        target_chars = max_tokens * 4
        truncated = prompt[:target_chars]
        self.logger.warning(f"Prompt truncated from {estimated_tokens} to ~{max_tokens} tokens")
        
        return truncated + "\n\n[...truncated for length...]"


# ==============================================================================
# Rule Capabilities
# ==============================================================================

class RuleEngine:
    """
    Manages rule-based decision making and constraints for agents.
    
    Features:
    - Rule definition and registration
    - Rule evaluation with context
    - Constraint validation
    - Priority-based rule ordering
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the rule engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.rules: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.RuleEngine")
    
    def add_rule(
        self,
        name: str,
        condition: str,
        action: str,
        priority: int = 0,
        description: str = ""
    ) -> None:
        """
        Add a rule to the engine.
        
        Args:
            name: Rule name
            condition: Condition expression (Python expression)
            action: Action to take if condition is true
            priority: Rule priority (higher = evaluated first)
            description: Rule description
        """
        rule = {
            'name': name,
            'condition': condition,
            'action': action,
            'priority': priority,
            'description': description
        }
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r['priority'], reverse=True)
        self.logger.debug(f"Added rule: {name} (priority: {priority})")
    
    def evaluate_rules(self, context: Dict[str, Any]) -> List[str]:
        """
        Evaluate all rules against the context.
        
        Args:
            context: Context dictionary for rule evaluation
            
        Returns:
            List of actions from matching rules
        """
        actions = []
        
        for rule in self.rules:
            try:
                # Evaluate condition safely
                if eval(rule['condition'], {"__builtins__": {}}, context):
                    actions.append(rule['action'])
                    self.logger.debug(f"Rule triggered: {rule['name']}")
            except Exception as e:
                self.logger.warning(f"Error evaluating rule {rule['name']}: {e}")
        
        return actions
    
    def validate_constraint(self, constraint: str, value: Any) -> bool:
        """
        Validate a value against a constraint.
        
        Args:
            constraint: Constraint expression
            value: Value to validate
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        try:
            return eval(constraint, {"__builtins__": {}, "value": value})
        except Exception as e:
            self.logger.warning(f"Error validating constraint: {e}")
            return False


# ==============================================================================
# Memory Capabilities (Enhanced)
# ==============================================================================

class MemoryCapability:
    """
    Enhanced memory capability for agents with short-term and long-term access.
    
    Features:
    - Short-term memory (working memory for current task)
    - Long-term memory (persistent across sessions)
    - Memory search and retrieval
    - Context-aware memory management
    """
    
    def __init__(self, memory_manager: Optional[Any] = None):
        """
        Initialize memory capability.
        
        Args:
            memory_manager: Memory manager instance
        """
        self.memory_manager = memory_manager
        self.short_term_memory: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.MemoryCapability")
    
    def store_short_term(self, key: str, value: Any) -> None:
        """
        Store data in short-term memory.
        
        Args:
            key: Memory key
            value: Value to store
        """
        self.short_term_memory[key] = value
        self.logger.debug(f"Stored in short-term memory: {key}")
    
    def retrieve_short_term(self, key: str, default: Any = None) -> Any:
        """
        Retrieve data from short-term memory.
        
        Args:
            key: Memory key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.short_term_memory.get(key, default)
    
    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self.short_term_memory.clear()
        self.logger.debug("Cleared short-term memory")
    
    def store_long_term(self, session_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store data in long-term memory.
        
        Args:
            session_id: Session ID
            content: Content to store
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        if not self.memory_manager:
            self.logger.warning("No memory manager available for long-term storage")
            return False
        
        try:
            self.memory_manager.add_agent_message(
                session_id=session_id,
                content=content,
                agent_name="memory_capability",
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to store long-term memory: {e}")
            return False
    
    def retrieve_long_term(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve data from long-term memory.
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages
        """
        if not self.memory_manager:
            self.logger.warning("No memory manager available for long-term retrieval")
            return []
        
        try:
            return self.memory_manager.get_messages(session_id, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to retrieve long-term memory: {e}")
            return []


# ==============================================================================
# File Capabilities
# ==============================================================================

class FileCapability:
    """
    File operations capability for agents.
    
    Features:
    - Read/write files
    - File search and manipulation
    - Safe file operations with validation
    - Batch file operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize file capability.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.FileCapability")
    
    def read_file(self, path: Path, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read a file.
        
        Args:
            path: File path
            encoding: File encoding
            
        Returns:
            File content or None if error
        """
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            self.logger.debug(f"Read file: {path}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read file {path}: {e}")
            return None
    
    def write_file(self, path: Path, content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> bool:
        """
        Write content to a file.
        
        Args:
            path: File path
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if needed
            
        Returns:
            True if successful
        """
        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            self.logger.debug(f"Wrote file: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {e}")
            return False
    
    def search_files(self, directory: Path, pattern: str, recursive: bool = True) -> List[Path]:
        """
        Search for files matching a pattern.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "*.py")
            recursive: Search recursively
            
        Returns:
            List of matching file paths
        """
        try:
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))
            
            self.logger.debug(f"Found {len(files)} files matching {pattern}")
            return files
        except Exception as e:
            self.logger.error(f"Failed to search files: {e}")
            return []


# ==============================================================================
# Codebase Capabilities
# ==============================================================================

class CodebaseCapability:
    """
    Codebase analysis and interaction capability for agents.
    
    Features:
    - Code structure analysis
    - Find functions, classes, imports
    - Code metrics and statistics
    - Code search
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize codebase capability.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.CodebaseCapability")
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Analysis results dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract functions
            functions = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
            
            # Extract classes
            classes = re.findall(r'^class\s+(\w+)\s*[\(:]', content, re.MULTILINE)
            
            # Extract imports
            imports = re.findall(r'^(?:import|from)\s+([\w.]+)', content, re.MULTILINE)
            
            # Count lines
            lines = content.count('\n') + 1
            code_lines = len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')])
            
            analysis = {
                'file': str(file_path),
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'total_lines': lines,
                'code_lines': code_lines,
                'blank_lines': lines - code_lines
            }
            
            self.logger.debug(f"Analyzed {file_path}: {len(functions)} functions, {len(classes)} classes")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze {file_path}: {e}")
            return {}
    
    def search_code(self, directory: Path, search_term: str, file_pattern: str = "*.py") -> List[Dict[str, Any]]:
        """
        Search for a term in code files.
        
        Args:
            directory: Directory to search
            search_term: Term to search for
            file_pattern: File pattern to match
            
        Returns:
            List of search results with file, line number, and content
        """
        results = []
        
        try:
            files = list(directory.rglob(file_pattern))
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if search_term in line:
                                results.append({
                                    'file': str(file_path),
                                    'line': line_num,
                                    'content': line.strip()
                                })
                except Exception as e:
                    self.logger.warning(f"Error reading {file_path}: {e}")
            
            self.logger.debug(f"Found {len(results)} matches for '{search_term}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search code: {e}")
            return []


# ==============================================================================
# Console Capabilities
# ==============================================================================

class ConsoleCapability:
    """
    Console input/output capability with structured data extraction.
    
    Features:
    - Capture user input
    - Parse structured output
    - Extract data from console output
    - Format output for display
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize console capability.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ConsoleCapability")
    
    def capture_input(self, prompt: str = "", default: Optional[str] = None) -> str:
        """
        Capture user input from console.
        
        Args:
            prompt: Input prompt
            default: Default value if user provides no input
            
        Returns:
            User input string
        """
        try:
            user_input = input(prompt).strip()
            if not user_input and default is not None:
                return default
            return user_input
        except Exception as e:
            self.logger.error(f"Failed to capture input: {e}")
            return default or ""
    
    def execute_command(self, command: str, capture_output: bool = True) -> Dict[str, Any]:
        """
        Execute a console command and capture output.
        
        Args:
            command: Command to execute
            capture_output: Whether to capture output
            
        Returns:
            Dictionary with stdout, stderr, return_code
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out: {command}")
            return {
                'stdout': '',
                'stderr': 'Command timed out',
                'return_code': -1,
                'success': False
            }
        except Exception as e:
            self.logger.error(f"Failed to execute command: {e}")
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'success': False
            }
    
    def parse_json_output(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from console output.
        
        Args:
            output: Console output string
            
        Returns:
            Parsed JSON dictionary or None if parsing fails
        """
        try:
            # Try to find JSON in output
            json_start = output.find('{')
            json_end = output.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = output[json_start:json_end]
                return json.loads(json_str)
            
            return None
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON output: {e}")
            return None
    
    def extract_structured_data(self, output: str, patterns: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data from output using regex patterns.
        
        Args:
            output: Output string
            patterns: Dictionary of field_name: regex_pattern
            
        Returns:
            Extracted data dictionary
        """
        data = {}
        
        for field_name, pattern in patterns.items():
            try:
                match = re.search(pattern, output)
                if match:
                    data[field_name] = match.group(1) if match.groups() else match.group(0)
            except Exception as e:
                self.logger.warning(f"Error extracting {field_name}: {e}")
        
        return data


# ==============================================================================
# Capability Manager
# ==============================================================================

class CapabilityManager:
    """
    Central manager for all agent capabilities.
    
    Provides easy access to all capability modules for agents.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        """
        Initialize capability manager.
        
        Args:
            config: Configuration dictionary
            memory_manager: Memory manager instance
        """
        self.config = config or {}
        self.prompts = PromptManager(config)
        self.rules = RuleEngine(config)
        self.memory = MemoryCapability(memory_manager)
        self.files = FileCapability(config)
        self.codebase = CodebaseCapability(config)
        self.console = ConsoleCapability(config)
        
        logger.info("CapabilityManager initialized with all capabilities")
    
    def get_all_capabilities(self) -> Dict[str, Any]:
        """
        Get all capability instances.
        
        Returns:
            Dictionary of capability name to instance
        """
        return {
            'prompts': self.prompts,
            'rules': self.rules,
            'memory': self.memory,
            'files': self.files,
            'codebase': self.codebase,
            'console': self.console
        }
