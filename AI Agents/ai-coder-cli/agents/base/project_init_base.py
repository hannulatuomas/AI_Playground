
"""
Project Initialization Base Class

This module provides the base class for all project initialization agents.
It handles common initialization logic including:
- Directory creation
- .project_ai folder generation with complete structure:
  - .codebase_root marker (for project root detection)
  - codebase_structure.md (project structure documentation)
  - rules/project_preferences.md (project-specific coding rules)
  - initial_plan.md (initial project plan and architecture)
  - goals.md (project goals and success measures)
  - todo.md (project task list)
- User interaction for gathering project requirements
- Clarification questions to understand user needs

The .project_ai structure provides comprehensive context for AI agents working
on the project and implements a 3-level rules hierarchy:
1. best_practices.md (language-level baseline)
2. user_preferences.md (user-level preferences)
3. project_preferences.md (project-specific rules) ← HIGHEST PRIORITY
"""

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .agent_base import Agent
from ..utils.codebase_awareness import (
    create_codebase_root_marker,
    create_project_ai_structure
)

# Import important files manager
try:
    from ...utils.important_files_manager import get_manager as get_important_files_manager
    IMPORTANT_FILES_AVAILABLE = True
except ImportError:
    IMPORTANT_FILES_AVAILABLE = False


class ProjectInitBase(Agent):
    """
    Abstract base class for project initialization agents.
    
    This class provides common functionality for initializing projects:
    - Creating directory structures
    - Generating comprehensive .project_ai folder with:
      * .codebase_root marker (for project root detection)
      * codebase_structure.md (project structure documentation)
      * rules/project_preferences.md (project-specific coding rules)
      * initial_plan.md (initial project plan)
      * goals.md (project goals and success criteria)
      * todo.md (project task list)
    - Asking clarifying questions to users
    - Validating user inputs
    - Integrating with FileOperations tool
    
    The rules/project_preferences.md file is the ultimate source of truth 
    for project-specific rules, overriding both user_preferences.md and 
    best_practices.md in case of conflicts.
    
    Language-specific agents should inherit from this class and implement:
    - _get_project_types(): Return list of supported project types
    - _get_project_structure(): Return directory structure for project type
    - _get_default_files(): Return default configuration files
    - _generate_language_rules(): Generate language-specific rules
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        language: str,
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        """
        Initialize the project initialization agent.
        
        Args:
            name: Agent name
            description: Agent description
            language: Target language/framework
            llm_router: LLM router for AI queries
            tool_registry: Tool registry for file operations
            config: Configuration dictionary
            memory_manager: Memory manager for context
        """
        super().__init__(
            name=name,
            description=description,
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
        
        self.language = language
        self.file_ops_tool = None
        
        # Load language documentation if available
        try:
            self._load_language_docs()
        except Exception as e:
            self.logger.warning(f"Could not load language docs: {e}")
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute project initialization.
        
        Args:
            task: Task description
            context: Execution context with user preferences
            
        Returns:
            Result dictionary with initialization status
        """
        self._log_action("Starting project initialization", task[:100])
        
        try:
            # Get file operations tool
            self.file_ops_tool = self._get_tool('file_operations')
            if not self.file_ops_tool:
                self.logger.warning("FileOperations tool not available, using fallback")
            
            # Step 1: Ask clarifying questions
            project_config = self._gather_project_requirements(context)
            if not project_config:
                return self._build_error_result("Failed to gather project requirements")
            
            # Step 2: Validate inputs
            validation_result = self._validate_project_config(project_config)
            if not validation_result['valid']:
                return self._build_error_result(
                    f"Invalid project configuration: {validation_result['error']}"
                )
            
            # Step 3: Create directory structure
            project_path = Path(project_config.get('project_path', './'))
            structure_result = self._create_directory_structure(project_path, project_config)
            if not structure_result['success']:
                return self._build_error_result(
                    f"Failed to create directory structure: {structure_result['error']}"
                )
            
            # Step 4: Create .codebase_root marker (for codebase awareness)
            self._log_action("Creating .codebase_root marker")
            if not create_codebase_root_marker(project_path):
                self.logger.warning("Failed to create .codebase_root marker (non-critical)")
            
            # Step 5: Create complete .project_ai structure
            self._log_action("Creating comprehensive .project_ai structure")
            if not create_project_ai_structure(
                root_path=project_path,
                project_name=project_config.get('project_name', 'Project'),
                project_type=project_config.get('project_type', 'Unknown'),
                description=project_config.get('description', ''),
                goals=project_config.get('goals', []),
                initial_plan=project_config.get('initial_plan', ''),
                author=project_config.get('author', '')
            ):
                self.logger.warning("Failed to create complete .project_ai structure (non-critical)")
            
            # Step 5.5: Generate additional project-specific rules
            rules_result = self._generate_additional_rules(project_path, project_config)
            if not rules_result['success']:
                self.logger.warning(f"Failed to add language-specific rules: {rules_result.get('error')}")
            
            # Step 6: Create default configuration files
            config_result = self._create_config_files(project_path, project_config)
            if not config_result['success']:
                self.logger.warning(f"Some config files failed: {config_result.get('error')}")
            
            # Step 7: Create important documentation files
            self._log_action("Creating important documentation files")
            doc_result = self._create_important_documentation_files(project_path, project_config)
            if not doc_result['success']:
                self.logger.warning(f"Some documentation files failed: {doc_result.get('error')}")
            
            self._log_action("Project initialization complete", str(project_path))
            
            # Generate explanation of .project_ai structure
            explanation = self._get_project_ai_explanation()
            
            return self._build_success_result(
                message=f"Project initialized successfully at {project_path}\n\n{explanation}",
                data={
                    'project_path': str(project_path),
                    'project_type': project_config.get('project_type'),
                    'language': self.language,
                    'files_created': structure_result.get('files_created', []),
                    'config': project_config,
                    'explanation': explanation
                },
                next_context={
                    'project_initialized': True,
                    'project_path': str(project_path),
                    'project_config': project_config
                }
            )
            
        except Exception as e:
            self.logger.exception("Project initialization failed")
            return self._build_error_result(f"Project initialization failed: {str(e)}", e)
    
    def _gather_project_requirements(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Gather project requirements from user via clarifying questions.
        
        This method asks the user about:
        - Project name
        - Project type (e.g., console app, web API, etc.)
        - Project goals
        - Initial plan
        - Tech stack preferences
        - Styling guide preferences
        - Directory structure preferences
        - Additional options
        
        Args:
            context: Execution context (may contain pre-filled answers)
            
        Returns:
            Dictionary with project configuration or None if failed
        """
        self._log_action("Gathering project requirements")
        
        # Check if context already has answers
        if context.get('project_config'):
            return context['project_config']
        
        try:
            questions = self._get_clarifying_questions()
            answers = {}
            
            # If in interactive mode, ask questions
            # For now, use defaults or context values
            for question in questions:
                key = question['key']
                
                # Check if answer in context
                if key in context:
                    answers[key] = context[key]
                # Use default if available
                elif 'default' in question:
                    answers[key] = question['default']
                # Required without default - use a sensible fallback
                else:
                    if key == 'project_name':
                        answers[key] = f"new_{self.language}_project"
                    elif key == 'project_type':
                        types = self._get_project_types()
                        answers[key] = types[0] if types else 'default'
                    elif key == 'project_path':
                        answers[key] = f"./{answers.get('project_name', 'new_project')}"
                    else:
                        answers[key] = question.get('default', '')
            
            # Parse goals if provided as comma-separated string
            if 'goals' in answers and isinstance(answers['goals'], str) and answers['goals']:
                goals_list = [g.strip() for g in answers['goals'].split(',') if g.strip()]
                answers['goals'] = goals_list if goals_list else []
            elif 'goals' not in answers or not answers['goals']:
                answers['goals'] = []
            
            return answers
            
        except Exception as e:
            self.logger.error(f"Failed to gather requirements: {e}")
            return None
    
    def _get_clarifying_questions(self) -> List[Dict[str, Any]]:
        """
        Get list of clarifying questions for project initialization.
        
        Language-specific agents can override this to add custom questions.
        
        Returns:
            List of question dictionaries with keys:
                - key: Configuration key
                - question: Question text
                - type: Answer type (text, choice, bool)
                - options: Available options for choice type
                - default: Default value
                - required: Whether answer is required
        """
        project_types = self._get_project_types()
        
        base_questions = [
            {
                'key': 'project_name',
                'question': 'What is your project name?',
                'type': 'text',
                'required': True
            },
            {
                'key': 'project_type',
                'question': f'What type of {self.language} project?',
                'type': 'choice',
                'options': project_types,
                'default': project_types[0] if project_types else 'default',
                'required': True
            },
            {
                'key': 'project_path',
                'question': 'Where should the project be created?',
                'type': 'text',
                'default': './{project_name}',
                'required': True
            },
            {
                'key': 'description',
                'question': 'Project description (optional)?',
                'type': 'text',
                'default': '',
                'required': False
            },
            {
                'key': 'author',
                'question': 'Author name (optional)?',
                'type': 'text',
                'default': '',
                'required': False
            },
            {
                'key': 'git_init',
                'question': 'Initialize git repository?',
                'type': 'bool',
                'default': True,
                'required': False
            },
            {
                'key': 'goals',
                'question': 'What are the main goals of this project? (comma-separated)',
                'type': 'text',
                'default': '',
                'required': False,
                'help': 'Example: Build a REST API, Create a dashboard, Automate workflow'
            },
            {
                'key': 'initial_plan',
                'question': 'Brief initial plan or architecture overview (optional)?',
                'type': 'text',
                'default': '',
                'required': False,
                'help': 'High-level description of how you plan to build this'
            }
        ]
        
        # Add language-specific questions
        language_questions = self._get_language_specific_questions()
        
        return base_questions + language_questions
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """
        Get language-specific clarifying questions.
        
        Override in language-specific agents to add custom questions.
        
        Returns:
            List of question dictionaries
        """
        return []
    
    def _validate_project_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project configuration.
        
        Args:
            config: Project configuration
            
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        # Check required fields
        required_fields = ['project_name', 'project_type', 'project_path']
        
        for field in required_fields:
            if field not in config or not config[field]:
                return {
                    'valid': False,
                    'error': f"Missing required field: {field}"
                }
        
        # Validate project name (no spaces, special chars except - and _)
        project_name = config['project_name']
        if not project_name.replace('-', '').replace('_', '').isalnum():
            return {
                'valid': False,
                'error': "Project name can only contain letters, numbers, hyphens, and underscores"
            }
        
        # Validate project type
        valid_types = self._get_project_types()
        if config['project_type'] not in valid_types:
            return {
                'valid': False,
                'error': f"Invalid project type. Must be one of: {', '.join(valid_types)}"
            }
        
        # Additional language-specific validation
        lang_validation = self._validate_language_specific(config)
        if not lang_validation['valid']:
            return lang_validation
        
        return {'valid': True}
    
    def _validate_language_specific(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform language-specific validation.
        
        Override in language-specific agents for custom validation.
        
        Args:
            config: Project configuration
            
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        return {'valid': True}
    
    def _create_directory_structure(
        self,
        project_path: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create project directory structure.
        
        Args:
            project_path: Root project path
            config: Project configuration
            
        Returns:
            Result dictionary with created directories
        """
        try:
            # Get structure for project type
            structure = self._get_project_structure(config['project_type'])
            
            created_dirs = []
            
            # Create root directory
            self._create_directory(project_path)
            created_dirs.append(str(project_path))
            
            # Create subdirectories
            for dir_path in structure.get('directories', []):
                full_path = project_path / dir_path
                self._create_directory(full_path)
                created_dirs.append(str(full_path))
            
            return {
                'success': True,
                'files_created': created_dirs
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_additional_rules(
        self,
        project_path: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate additional language-specific rules and append to project_preferences.md.
        
        This method adds language-specific content to the project preferences file
        that was already created by create_project_ai_structure().
        
        Args:
            project_path: Root project path
            config: Project configuration
            
        Returns:
            Result dictionary
        """
        try:
            prefs_path = project_path / '.project_ai' / 'rules' / 'project_preferences.md'
            
            if not prefs_path.exists():
                return {
                    'success': False,
                    'error': 'project_preferences.md not found'
                }
            
            # Generate language-specific rules
            language_rules = self._generate_language_rules(config)
            
            # Read existing content
            existing_content = self._read_file(prefs_path)
            
            # Append language-specific rules before the "Notes" section
            if '## Notes' in existing_content:
                # Insert before Notes section
                parts = existing_content.split('## Notes')
                updated_content = parts[0] + f"""
## Language-Specific Rules ({self.language.title()})

{language_rules}

---

## Notes""" + parts[1]
            else:
                # Append at end
                updated_content = existing_content + f"""

---

## Language-Specific Rules ({self.language.title()})

{language_rules}
"""
            
            # Write updated content
            self._write_file(prefs_path, updated_content)
            
            return {
                'success': True,
                'path': str(prefs_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_config_files(
        self,
        project_path: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create default configuration files for the project.
        
        Args:
            project_path: Root project path
            config: Project configuration
            
        Returns:
            Result dictionary
        """
        try:
            files = self._get_default_files(config)
            created_files = []
            
            for file_path, content in files.items():
                full_path = project_path / file_path
                
                # Create parent directories if needed
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file
                self._write_file(full_path, content)
                created_files.append(str(full_path))
            
            return {
                'success': True,
                'files_created': created_files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_important_documentation_files(
        self,
        project_path: Path,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create important documentation files from the important files configuration.
        
        This method uses the ImportantFilesManager to determine which files should
        be created during project initialization and creates them with appropriate
        templates.
        
        Args:
            project_path: Root project path
            config: Project configuration
            
        Returns:
            Result dictionary with success status and created files
        """
        try:
            if not IMPORTANT_FILES_AVAILABLE:
                self.logger.warning("ImportantFilesManager not available, skipping documentation files")
                return {'success': False, 'error': 'ImportantFilesManager not available'}
            
            manager = get_important_files_manager()
            files_to_create = manager.get_files_to_create_on_init()
            
            created_files = []
            skipped_files = []
            
            # Prepare template variables
            template_vars = {
                'project_name': config.get('project_name', 'Project'),
                'project_description': config.get('description', 'A project managed by AI Agent Console'),
                'author': config.get('author', 'N/A'),
                'license': config.get('license', 'MIT'),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'language': self.language
            }
            
            for filename in files_to_create:
                try:
                    # Get file info
                    file_info = manager.get_file_info(filename)
                    if not file_info:
                        self.logger.debug(f"No info found for {filename}, skipping")
                        skipped_files.append(filename)
                        continue
                    
                    # Determine file location
                    location = file_info.get('location', 'root')
                    if location == 'root':
                        file_path = project_path / filename
                    elif location == 'docs':
                        file_path = project_path / 'docs' / filename
                    elif location == '.project_ai':
                        file_path = project_path / '.project_ai' / filename
                    else:
                        file_path = project_path / location / filename
                    
                    # Skip if file already exists
                    if file_path.exists():
                        self.logger.debug(f"File {filename} already exists, skipping")
                        skipped_files.append(filename)
                        continue
                    
                    # Get template content
                    content = manager.get_file_template(filename, **template_vars)
                    
                    # If no template, create minimal content
                    if content is None:
                        content = self._generate_minimal_content(filename, config)
                    
                    # Create parent directories
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    self._write_file(file_path, content)
                    created_files.append(str(file_path))
                    self.logger.info(f"Created important file: {filename}")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to create {filename}: {e}")
                    skipped_files.append(filename)
            
            return {
                'success': True,
                'files_created': created_files,
                'files_skipped': skipped_files,
                'message': f"Created {len(created_files)} important documentation files"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create important documentation files: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_minimal_content(self, filename: str, config: Dict[str, Any]) -> str:
        """Generate minimal content for files without templates."""
        project_name = config.get('project_name', 'Project')
        
        minimal_contents = {
            'STRUCTURE.md': f"""# {project_name} - Project Structure

## Directory Structure

```
{project_name}/
├── src/          # Source code
├── tests/        # Test files
├── docs/         # Documentation
└── README.md     # Main documentation
```

## Key Directories

- **src/**: Contains the main application source code
- **tests/**: Contains test files and test data
- **docs/**: Contains project documentation

## Configuration Files

- **README.md**: Main project documentation
- **VERSION**: Current version number
""",
            
            'Project_Goals.md': f"""# {project_name} - Project Goals

## Primary Objectives

1. {config.get('goals', ['Define project objectives'])[0] if config.get('goals') else 'Define project objectives'}

## Success Criteria

- Functional requirements met
- Code quality standards maintained
- Documentation complete
- Tests passing

## Timeline

- **Start Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Target Completion**: TBD
""",
            
            'Getting_Started.md': f"""# Getting Started with {project_name}

## Prerequisites

- {self.language} development environment
- Required dependencies (see README.md)

## Installation

1. Clone the repository
2. Install dependencies
3. Configure settings
4. Run the application

## Quick Start

```bash
# Add quick start commands here
```

## Next Steps

- Review the [User Guide](User_Guide.md)
- Check the [Documentation](../README.md)
- Explore the [Examples](../examples/)
""",
        }
        
        return minimal_contents.get(filename, f"# {filename}\n\n*Documentation pending*\n")
    
    # ========================================================================
    # Abstract Methods - Must be implemented by language-specific agents
    # ========================================================================
    
    @abstractmethod
    def _get_project_types(self) -> List[str]:
        """
        Get list of supported project types for this language.
        
        Returns:
            List of project type identifiers
        """
        pass
    
    @abstractmethod
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """
        Get directory structure for project type.
        
        Args:
            project_type: Type of project
            
        Returns:
            Dictionary with 'directories' list and optional 'files' dict
        """
        pass
    
    @abstractmethod
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get default configuration files for project.
        
        Args:
            config: Project configuration
            
        Returns:
            Dictionary mapping file paths to content
        """
        pass
    
    @abstractmethod
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """
        Generate language-specific rules for rules.md.
        
        Args:
            config: Project configuration
            
        Returns:
            Markdown content with language-specific rules
        """
        pass
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _get_project_ai_explanation(self) -> str:
        """
        Get explanation of .project_ai structure for user.
        
        Returns:
            Formatted explanation string
        """
        return """
### 📁 Project AI Structure Created

Your project now includes a `.project_ai/` folder with the following files:

1. **`.codebase_root`** - Marker file that helps AI agents locate your project root

2. **`codebase_structure.md`** - Documents your project structure and organization
   - Automatically maintained by AI agents
   - Provides context for code generation and debugging

3. **`rules/project_preferences.md`** - Your project-specific coding rules (HIGHEST PRIORITY)
   - Overrides user_preferences.md and best_practices.md
   - Customize this for project-specific guidelines

4. **`initial_plan.md`** - Your initial project plan and architecture
   - Documents key decisions and technology choices
   - Update as your project evolves

5. **`goals.md`** - Your project goals and success criteria
   - Defines what success looks like
   - Helps align all development work

6. **`todo.md`** - Your project task list
   - Track progress and plan work
   - Coordinate with goals and plan

### 📋 Rules Hierarchy (for AI Agents)

When AI agents work on your project, they follow this priority order:
1. **project_preferences.md** (THIS PROJECT) ← Highest priority
2. **user_preferences.md** (YOUR SETTINGS)
3. **best_practices.md** (LANGUAGE DEFAULTS) ← Baseline

**Tip:** Customize `rules/project_preferences.md` to set project-specific standards!
"""
    
    def _create_directory(self, path: Path) -> None:
        """
        Create a directory using FileOperations tool or fallback.
        
        Args:
            path: Directory path
        """
        if self.file_ops_tool:
            result = self.file_ops_tool.invoke({
                'operation': 'mkdir',
                'path': str(path),
                'parents': True,
                'exist_ok': True
            })
            
            if not result.get('success'):
                raise Exception(f"Failed to create directory: {result.get('error')}")
        else:
            # Fallback to pathlib
            path.mkdir(parents=True, exist_ok=True)
    
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
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    
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


