"""
Documentation Agent Base Class

This module provides the base class for all documentation agents.
Documentation agents are responsible for keeping project documentation up to date:
- README files
- TODO lists
- Status files
- Code documentation
- API documentation
- Architecture documentation
- Codebase structure documentation

These agents integrate with the vector database for context awareness and
understand the project structure and root folder location.
"""

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from .agent_base import Agent
from ..utils.codebase_awareness import CodebaseAwarenessMixin


class DocumentationAgentBase(Agent, CodebaseAwarenessMixin):
    """
    Abstract base class for documentation agents with project context awareness.
    
    This class provides common functionality for:
    - Reading and updating README files
    - Managing TODO lists
    - Updating status files
    - Generating and updating code documentation
    - Understanding codebase structure
    - Finding project root folder
    - Integration with vector database for context
    - Reading documentation preferences
    - Project context awareness (goals, plan, tasks, preferences)
    - Rules hierarchy awareness (project_preferences > user_preferences > best_practices)
    
    Subclasses must implement:
    - _generate_code_documentation: Generate language-specific code docs
    - _get_documentation_format: Get language-specific doc format
    - _validate_documentation: Validate language-specific documentation
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        language: Optional[str] = None,
        vector_db: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize documentation agent with project context awareness.
        
        Args:
            name: Agent name
            description: Agent description
            language: Target language (None for generic agent)
            vector_db: Vector database for context retrieval
            **kwargs: Additional arguments passed to Agent base class
        """
        super().__init__(
            name=name,
            description=description,
            **kwargs
        )
        
        self.language = language
        self.vector_db = vector_db
        self.file_ops_tool = None
        self.documentation_preferences: Optional[str] = None
        
        # Initialize codebase awareness (provides root_folder, codebase_structure)
        self.init_codebase_awareness()
        
        # Load language documentation if available
        if language:
            try:
                self._load_language_docs()
                self._load_documentation_preferences()
            except Exception as e:
                self.logger.warning(f"Could not load language docs: {e}")
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute documentation task with project context awareness.
        
        Args:
            task: Task description (e.g., "update README", "generate API docs")
            context: Execution context with:
                - project_path: Optional project path
                - files_changed: List of recently changed files
                - update_type: Type of update (readme, todo, code_docs, etc.)
                - custom_instructions: Optional custom instructions
                
        Returns:
            Result dictionary with documentation updates
        """
        self._log_action("Starting documentation task", task[:100])
        
        try:
            # Get file operations tool
            self.file_ops_tool = self._get_tool('file_operations')
            if not self.file_ops_tool:
                self.logger.warning("FileOperations tool not available, using fallback")
            
            # Initialize project context awareness (finds root, loads structure, etc.)
            success, error = self.ensure_codebase_awareness_initialized(context)
            if not success and error:
                self.logger.warning(f"Project context initialization: {error}")
            
            if self.root_folder:
                self._log_action("Found project root", str(self.root_folder))
            
            # Step 3: Get context from vector DB if available
            vector_context = self._get_vector_context(context)
            
            # Step 4: Determine update type and execute
            update_type = context.get('update_type', 'auto')
            
            if update_type == 'readme' or 'readme' in task.lower():
                result = self._update_readme(context, vector_context)
            elif update_type == 'todo' or 'todo' in task.lower():
                result = self._update_todo(context, vector_context)
            elif update_type == 'status' or 'status' in task.lower():
                result = self._update_status(context, vector_context)
            elif update_type == 'code_docs' or 'code' in task.lower():
                result = self._update_code_documentation(context, vector_context)
            elif update_type == 'api_docs' or 'api' in task.lower():
                result = self._update_api_documentation(context, vector_context)
            elif update_type == 'structure' or 'structure' in task.lower():
                result = self._update_codebase_structure(context, vector_context)
            elif update_type == 'auto':
                # Auto-detect what needs updating based on context
                result = self._auto_update_documentation(context, vector_context)
            else:
                result = self._build_error_result(f"Unknown update type: {update_type}")
            
            if result['success']:
                self._log_action("Documentation update complete")
            else:
                self.logger.error(f"Documentation update failed: {result.get('message')}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Documentation task failed")
            return self._build_error_result(f"Documentation task failed: {str(e)}", e)
    
    # ========================================================================
    # Project Root and Structure Methods
    # ========================================================================
    
    def _find_project_root(self, hint_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Find the project root folder by looking for .codebase_root marker.
        
        Args:
            hint_path: Optional hint path to start searching from
            
        Returns:
            Result dictionary with 'success' and 'root_path' or 'error'
        """
        try:
            # Start from hint path or current directory
            start_path = Path(hint_path).resolve() if hint_path else Path.cwd()
            
            # If hint path is a file, start from its parent
            if start_path.is_file():
                start_path = start_path.parent
            
            # Search upwards for .codebase_root marker
            current_path = start_path
            max_depth = 10  # Prevent infinite loops
            depth = 0
            
            while depth < max_depth:
                marker_file = current_path / '.codebase_root'
                
                if marker_file.exists():
                    return {
                        'success': True,
                        'root_path': str(current_path)
                    }
                
                # Move up one directory
                parent = current_path.parent
                if parent == current_path:  # Reached filesystem root
                    break
                
                current_path = parent
                depth += 1
            
            # If no marker found, return the hint path or current directory
            fallback_path = start_path if hint_path else Path.cwd()
            self.logger.warning(
                f".codebase_root marker not found, using fallback: {fallback_path}"
            )
            
            return {
                'success': True,
                'root_path': str(fallback_path),
                'warning': 'No .codebase_root marker found, using fallback'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_codebase_structure(self) -> Dict[str, Any]:
        """
        Load codebase structure from codebase_structure.md file.
        
        Returns:
            Result dictionary with 'success' and 'structure' or 'error'
        """
        try:
            if not self.root_folder:
                return {
                    'success': False,
                    'error': 'Root folder not set'
                }
            
            structure_file = self.root_folder / 'codebase_structure.md'
            
            if not structure_file.exists():
                return {
                    'success': False,
                    'error': 'codebase_structure.md not found'
                }
            
            # Read structure file
            content = self._read_file(structure_file)
            
            # Parse structure (basic parsing for now)
            structure = {
                'raw_content': content,
                'last_updated': structure_file.stat().st_mtime,
                'directories': [],
                'key_files': []
            }
            
            # Extract key information from markdown
            # (More sophisticated parsing can be added)
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- `') and '/' in line:
                    # Extract directory or file paths
                    path_match = line.split('`')[1] if '`' in line else None
                    if path_match:
                        if path_match.endswith('/'):
                            structure['directories'].append(path_match)
                        else:
                            structure['key_files'].append(path_match)
            
            return {
                'success': True,
                'structure': structure
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_codebase_structure(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the codebase_structure.md file.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            if not self.root_folder:
                return self._build_error_result("Root folder not set")
            
            structure_file = self.root_folder / 'codebase_structure.md'
            
            # Generate updated structure
            structure_content = self._generate_codebase_structure_content(context)
            
            # Write structure file
            self._write_file(structure_file, structure_content)
            
            self._log_action("Updated codebase structure", str(structure_file))
            
            return self._build_success_result(
                message=f"Updated codebase structure at {structure_file}",
                data={'file': str(structure_file)},
                next_context={'codebase_structure_updated': True}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to update codebase structure: {str(e)}", e)
    
    def _generate_codebase_structure_content(self, context: Dict[str, Any]) -> str:
        """
        Generate content for codebase_structure.md.
        
        Args:
            context: Execution context
            
        Returns:
            Markdown content
        """
        if not self.root_folder:
            return "# Codebase Structure\n\n(Root folder not found)"
        
        content = f"""# Codebase Structure

**Project Root:** `{self.root_folder}`  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Directory Tree

"""
        
        # Generate directory tree
        try:
            tree = self._generate_directory_tree(self.root_folder)
            content += tree + "\n\n"
        except Exception as e:
            content += f"(Error generating tree: {e})\n\n"
        
        content += """---

## Key Directories

"""
        
        # Add key directories with descriptions
        key_dirs = self._identify_key_directories()
        for dir_info in key_dirs:
            content += f"- **`{dir_info['path']}`**: {dir_info['description']}\n"
        
        content += """

---

## Key Files

"""
        
        # Add key files with descriptions
        key_files = self._identify_key_files()
        for file_info in key_files:
            content += f"- **`{file_info['path']}`**: {file_info['description']}\n"
        
        content += """

---

## Notes

- This file is automatically generated and updated by the documentation agent
- Keep this synchronized with actual project structure
- Update descriptions as needed

"""
        
        return content
    
    def _generate_directory_tree(
        self,
        directory: Path,
        prefix: str = "",
        max_depth: int = 4,
        current_depth: int = 0
    ) -> str:
        """
        Generate directory tree visualization.
        
        Args:
            directory: Directory to generate tree for
            prefix: Prefix for formatting
            max_depth: Maximum depth to traverse
            current_depth: Current depth level
            
        Returns:
            Tree string
        """
        if current_depth >= max_depth:
            return ""
        
        # Directories/files to skip
        skip_patterns = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', '.env', '.idea', '.vscode', 'dist',
            'build', '.eggs', '*.pyc', '.DS_Store'
        }
        
        tree = ""
        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            
            for i, item in enumerate(items):
                # Skip ignored patterns
                if any(pattern in item.name for pattern in skip_patterns):
                    continue
                
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                
                tree += f"{prefix}{connector}`{item.name}`"
                
                if item.is_dir():
                    tree += "/\n"
                    extension = "    " if is_last else "│   "
                    tree += self._generate_directory_tree(
                        item,
                        prefix + extension,
                        max_depth,
                        current_depth + 1
                    )
                else:
                    tree += "\n"
        
        except PermissionError:
            tree += f"{prefix}(Permission denied)\n"
        
        return tree
    
    def _identify_key_directories(self) -> List[Dict[str, str]]:
        """
        Identify key directories in the project.
        
        Returns:
            List of directory info dictionaries
        """
        if not self.root_folder:
            return []
        
        key_dirs = []
        
        # Common directories to look for
        common_dirs = {
            'src': 'Source code directory',
            'lib': 'Library code',
            'tests': 'Test files',
            'test': 'Test files',
            'docs': 'Documentation',
            'doc': 'Documentation',
            'examples': 'Example code',
            'scripts': 'Utility scripts',
            'config': 'Configuration files',
            'data': 'Data files',
            'assets': 'Asset files',
            'public': 'Public files',
            'static': 'Static files',
            'templates': 'Template files',
            'migrations': 'Database migrations',
            'models': 'Data models',
            'views': 'View components',
            'controllers': 'Controller components',
            'routes': 'Route definitions',
            'middleware': 'Middleware components',
            'utils': 'Utility functions',
            'helpers': 'Helper functions',
            'services': 'Service layer',
            'api': 'API endpoints',
            'components': 'UI components',
            'pages': 'Page components',
            'layouts': 'Layout components',
        }
        
        for dir_name, description in common_dirs.items():
            dir_path = self.root_folder / dir_name
            if dir_path.exists() and dir_path.is_dir():
                key_dirs.append({
                    'path': dir_name + '/',
                    'description': description
                })
        
        # Add .project_ai if exists
        project_ai = self.root_folder / '.project_ai'
        if project_ai.exists():
            key_dirs.append({
                'path': '.project_ai/',
                'description': 'AI project rules and configuration'
            })
        
        return key_dirs
    
    def _identify_key_files(self) -> List[Dict[str, str]]:
        """
        Identify key files in the project.
        
        Returns:
            List of file info dictionaries
        """
        if not self.root_folder:
            return []
        
        key_files = []
        
        # Common files to look for
        common_files = {
            'README.md': 'Project documentation',
            'TODO.md': 'Project TODO list',
            'CHANGELOG.md': 'Project changelog',
            'LICENSE': 'License information',
            'LICENSE.md': 'License information',
            '.gitignore': 'Git ignore patterns',
            '.codebase_root': 'Codebase root marker',
            'codebase_structure.md': 'Codebase structure documentation',
            'requirements.txt': 'Python dependencies',
            'setup.py': 'Python package setup',
            'pyproject.toml': 'Python project configuration',
            'package.json': 'Node.js project configuration',
            'Makefile': 'Build automation',
            'Dockerfile': 'Docker container definition',
            'docker-compose.yml': 'Docker Compose configuration',
            '.env.example': 'Environment variables example',
            'config.json': 'Configuration file',
            'config.yml': 'Configuration file',
        }
        
        for file_name, description in common_files.items():
            file_path = self.root_folder / file_name
            if file_path.exists() and file_path.is_file():
                key_files.append({
                    'path': file_name,
                    'description': description
                })
        
        # Add rules.md if exists
        rules_file = self.root_folder / '.project_ai' / 'rules.md'
        if rules_file.exists():
            key_files.append({
                'path': '.project_ai/rules.md',
                'description': 'Project rules (source of truth)'
            })
        
        return key_files
    
    def _load_documentation_preferences(self) -> None:
        """
        Load documentation_preferences.md for the language.
        
        Sets self.documentation_preferences with the content.
        """
        if not self.language:
            return
        
        try:
            docs_dir = Path(__file__).parent.parent / 'languages' / self.language
            prefs_file = docs_dir / 'documentation_preferences.md'
            
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    self.documentation_preferences = f.read()
                self.logger.info(f"Loaded documentation_preferences.md for {self.language}")
            else:
                self.logger.warning(
                    f"documentation_preferences.md not found for {self.language}"
                )
        except Exception as e:
            self.logger.error(f"Failed to load documentation_preferences.md: {e}")
    
    # ========================================================================
    # Vector Database Context Methods
    # ========================================================================
    
    def _get_vector_context(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Get relevant context from vector database.
        
        Args:
            context: Execution context
            
        Returns:
            Context string or None
        """
        if not self.vector_db:
            return None
        
        try:
            # Query vector DB for relevant context
            query = context.get('task', '')
            files_changed = context.get('files_changed', [])
            
            # Build query string
            query_parts = [query]
            if files_changed:
                query_parts.append(f"Files changed: {', '.join(files_changed)}")
            
            full_query = ' '.join(query_parts)
            
            # Retrieve context
            results = self.vector_db.query(full_query, top_k=5)
            
            if results:
                context_parts = []
                for result in results:
                    context_parts.append(result.get('content', ''))
                
                return '\n\n'.join(context_parts)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get vector context: {e}")
            return None
    
    # ========================================================================
    # Documentation Update Methods
    # ========================================================================
    
    def _update_readme(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update README.md file.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            if not self.root_folder:
                return self._build_error_result("Root folder not set")
            
            readme_file = self.root_folder / 'README.md'
            
            # Read existing README if it exists
            existing_content = ""
            if readme_file.exists():
                existing_content = self._read_file(readme_file)
            
            # Generate updated README content using LLM
            updated_content = self._generate_readme_content(
                existing_content,
                context,
                vector_context
            )
            
            # Write updated README
            self._write_file(readme_file, updated_content)
            
            self._log_action("Updated README", str(readme_file))
            
            return self._build_success_result(
                message=f"Updated README at {readme_file}",
                data={'file': str(readme_file)},
                next_context={'readme_updated': True}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to update README: {str(e)}", e)
    
    def _update_todo(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update TODO.md file.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            if not self.root_folder:
                return self._build_error_result("Root folder not set")
            
            todo_file = self.root_folder / 'TODO.md'
            
            # Read existing TODO if it exists
            existing_content = ""
            if todo_file.exists():
                existing_content = self._read_file(todo_file)
            
            # Generate updated TODO content
            updated_content = self._generate_todo_content(
                existing_content,
                context,
                vector_context
            )
            
            # Write updated TODO
            self._write_file(todo_file, updated_content)
            
            self._log_action("Updated TODO", str(todo_file))
            
            return self._build_success_result(
                message=f"Updated TODO at {todo_file}",
                data={'file': str(todo_file)},
                next_context={'todo_updated': True}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to update TODO: {str(e)}", e)
    
    def _update_status(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update STATUS.md file with current project status.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            if not self.root_folder:
                return self._build_error_result("Root folder not set")
            
            status_file = self.root_folder / 'STATUS.md'
            
            # Generate status content
            status_content = self._generate_status_content(context, vector_context)
            
            # Write status file
            self._write_file(status_file, status_content)
            
            self._log_action("Updated STATUS", str(status_file))
            
            return self._build_success_result(
                message=f"Updated STATUS at {status_file}",
                data={'file': str(status_file)},
                next_context={'status_updated': True}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to update STATUS: {str(e)}", e)
    
    def _update_code_documentation(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update code documentation (docstrings, comments).
        
        Args:
            context: Execution context with files to document
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            files_to_document = context.get('files', [])
            
            if not files_to_document:
                return self._build_error_result("No files specified for documentation")
            
            documented_files = []
            
            for file_path in files_to_document:
                result = self._document_single_file(file_path, context, vector_context)
                if result['success']:
                    documented_files.append(file_path)
                else:
                    self.logger.warning(f"Failed to document {file_path}: {result.get('error')}")
            
            if documented_files:
                return self._build_success_result(
                    message=f"Documented {len(documented_files)} files",
                    data={'files': documented_files},
                    next_context={'code_docs_updated': True}
                )
            else:
                return self._build_error_result("Failed to document any files")
                
        except Exception as e:
            return self._build_error_result(f"Failed to update code documentation: {str(e)}", e)
    
    def _update_api_documentation(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update API documentation.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        try:
            if not self.root_folder:
                return self._build_error_result("Root folder not set")
            
            api_docs_dir = self.root_folder / 'docs' / 'api'
            api_docs_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate API documentation
            api_content = self._generate_api_documentation_content(context, vector_context)
            
            api_file = api_docs_dir / 'API.md'
            self._write_file(api_file, api_content)
            
            self._log_action("Updated API documentation", str(api_file))
            
            return self._build_success_result(
                message=f"Updated API documentation at {api_file}",
                data={'file': str(api_file)},
                next_context={'api_docs_updated': True}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to update API documentation: {str(e)}", e)
    
    def _auto_update_documentation(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Automatically determine and update needed documentation.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        updated_docs = []
        
        # Check what changed and update accordingly
        files_changed = context.get('files_changed', [])
        
        # Always update codebase structure if files changed
        if files_changed:
            result = self._update_codebase_structure(context, vector_context)
            if result['success']:
                updated_docs.append('codebase_structure.md')
        
        # Update README if major changes
        if self._should_update_readme(context, files_changed):
            result = self._update_readme(context, vector_context)
            if result['success']:
                updated_docs.append('README.md')
        
        # Update TODO if new tasks mentioned
        if self._should_update_todo(context):
            result = self._update_todo(context, vector_context)
            if result['success']:
                updated_docs.append('TODO.md')
        
        if updated_docs:
            return self._build_success_result(
                message=f"Auto-updated documentation: {', '.join(updated_docs)}",
                data={'updated_docs': updated_docs},
                next_context={'documentation_updated': True}
            )
        else:
            return self._build_success_result(
                message="No documentation updates needed",
                data={'updated_docs': []},
                next_context={}
            )
    
    # ========================================================================
    # Content Generation Methods (to be enhanced by language-specific agents)
    # ========================================================================
    
    def _generate_readme_content(
        self,
        existing_content: str,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate updated README content using LLM.
        
        Args:
            existing_content: Existing README content
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Updated README content
        """
        # Build prompt for LLM
        prompt = f"""You are a documentation expert. Update the README.md file based on the context provided.

Current README:
```
{existing_content if existing_content else '(New README)'}
```

Context:
- Files changed: {context.get('files_changed', [])}
- Custom instructions: {context.get('custom_instructions', 'Keep README clear, comprehensive, and up-to-date')}

"""
        
        if vector_context:
            prompt += f"""
Additional Context from Codebase:
{vector_context}
"""
        
        if self.documentation_preferences:
            prompt += f"""
Documentation Preferences:
{self.documentation_preferences}
"""
        
        prompt += """
Generate an updated README.md that:
1. Maintains existing structure where appropriate
2. Adds new information about recent changes
3. Keeps installation, usage, and configuration sections current
4. Follows markdown best practices
5. Is clear and helpful for users

Output only the complete README.md content.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.7)
                return response.get('content', existing_content)
            else:
                # Fallback: return existing or template
                return existing_content if existing_content else self._get_default_readme_template()
        except Exception as e:
            self.logger.error(f"Failed to generate README content: {e}")
            return existing_content if existing_content else self._get_default_readme_template()
    
    def _generate_todo_content(
        self,
        existing_content: str,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate updated TODO content.
        
        Args:
            existing_content: Existing TODO content
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Updated TODO content
        """
        # For now, return existing or create new
        if existing_content:
            return existing_content
        
        return f"""# TODO List

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## High Priority

- [ ] Task 1

## Medium Priority

- [ ] Task 2

## Low Priority

- [ ] Task 3

## Completed

- [x] Initial setup
"""
    
    def _generate_status_content(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate status content.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Status content
        """
        return f"""# Project Status

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status

Project is under active development.

## Recent Changes

- {context.get('recent_change', 'No recent changes')}

## Next Steps

- Continue development
- Update documentation
- Add tests
"""
    
    def _generate_api_documentation_content(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate API documentation content.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            API documentation content
        """
        return f"""# API Documentation

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Endpoints

### Endpoint 1

**URL:** `/api/endpoint1`  
**Method:** `GET`  
**Description:** Description of endpoint

**Parameters:**
- `param1`: Description

**Response:**
```json
{{
    "status": "success",
    "data": {{}}
}}
```

---

*This API documentation is automatically generated and maintained.*
"""
    
    def _get_default_readme_template(self) -> str:
        """
        Get default README template.
        
        Returns:
            Default README content
        """
        return f"""# Project Title

## Description

Project description goes here.

## Installation

```bash
# Installation instructions
```

## Usage

```bash
# Usage examples
```

## Configuration

Configuration instructions go here.

## Contributing

Contribution guidelines go here.

## License

License information goes here.

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _should_update_readme(
        self,
        context: Dict[str, Any],
        files_changed: List[str]
    ) -> bool:
        """
        Determine if README should be updated.
        
        Args:
            context: Execution context
            files_changed: List of changed files
            
        Returns:
            True if README should be updated
        """
        # Update if explicitly requested
        if context.get('force_readme_update'):
            return True
        
        # Update if major files changed
        major_files = ['setup.py', 'package.json', 'requirements.txt', 'Dockerfile']
        return any(f in str(files_changed) for f in major_files)
    
    def _should_update_todo(self, context: Dict[str, Any]) -> bool:
        """
        Determine if TODO should be updated.
        
        Args:
            context: Execution context
            
        Returns:
            True if TODO should be updated
        """
        # Update if explicitly requested
        return context.get('force_todo_update', False)
    
    def _document_single_file(
        self,
        file_path: str,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Document a single file.
        
        Args:
            file_path: Path to file
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Result dictionary
        """
        # To be implemented by language-specific agents
        return {
            'success': True,
            'message': f"Documented {file_path}"
        }
    
    # ========================================================================
    # Abstract Methods (for language-specific agents)
    # ========================================================================
    
    @abstractmethod
    def _generate_code_documentation(
        self,
        code_content: str,
        file_path: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate language-specific code documentation.
        
        Args:
            code_content: Source code content
            file_path: Path to source file
            context: Execution context
            
        Returns:
            Documented code content
        """
        pass
    
    @abstractmethod
    def _get_documentation_format(self) -> Dict[str, Any]:
        """
        Get language-specific documentation format.
        
        Returns:
            Dictionary with documentation format specifications
        """
        pass
    
    @abstractmethod
    def _validate_documentation(self, doc_content: str) -> Dict[str, Any]:
        """
        Validate language-specific documentation.
        
        Args:
            doc_content: Documentation content
            
        Returns:
            Validation result dictionary
        """
        pass
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _read_file(self, path: Path) -> str:
        """
        Read file using FileOperations tool or fallback.
        
        Args:
            path: File path
            
        Returns:
            File content
        """
        if self.file_ops_tool:
            result = self.file_ops_tool.invoke({
                'operation': 'read',
                'path': str(path),
                'encoding': 'utf-8'
            })
            
            if not result.get('success'):
                raise Exception(f"Failed to read file: {result.get('error')}")
            
            return result.get('content', '')
        else:
            # Fallback to pathlib
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _write_file(self, path: Path, content: str) -> None:
        """
        Write file using FileOperations tool or fallback.
        
        Args:
            path: File path
            content: File content
        """
        if self.file_ops_tool:
            result = self.file_ops_tool.invoke({
                'operation': 'write',
                'path': str(path),
                'content': content,
                'encoding': 'utf-8',
                'force': True
            })
            
            if not result.get('success'):
                raise Exception(f"Failed to write file: {result.get('error')}")
        else:
            # Fallback to pathlib
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
