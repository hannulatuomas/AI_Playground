"""
Codebase Awareness Utilities

This module provides utility functions and mixins for agents to be aware of:
- Project root folder (via .codebase_root marker)
- Codebase structure (via codebase_structure.md)

These utilities are used by code_editor, build_agent, debug_agent, and
documentation agents to maintain consistency across the codebase.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


logger = logging.getLogger(__name__)


class CodebaseAwarenessMixin:
    """
    Mixin class that provides codebase awareness functionality to agents.
    
    Adds methods for:
    - Finding project root via .codebase_root marker
    - Loading codebase structure from codebase_structure.md
    - Updating codebase structure when changes occur
    
    Usage:
        class MyAgent(Agent, CodebaseAwarenessMixin):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.init_codebase_awareness()
    """
    
    def init_codebase_awareness(self) -> None:
        """
        Initialize codebase awareness.
        
        Sets up:
        - self.root_folder: Path to project root
        - self.codebase_structure: Loaded structure data
        """
        self.root_folder: Optional[Path] = None
        self.codebase_structure: Optional[Dict[str, Any]] = None
        
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def find_project_root(
        self,
        hint_path: Optional[str] = None,
        create_if_missing: bool = False
    ) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Find the project root folder by looking for .codebase_root marker.
        
        Args:
            hint_path: Optional hint path to start searching from
            create_if_missing: If True, create marker if not found
            
        Returns:
            Tuple of (success, root_path, error_message)
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
                    self.root_folder = current_path
                    self.logger.info(f"Found project root: {current_path}")
                    return True, current_path, None
                
                # Move up one directory
                parent = current_path.parent
                if parent == current_path:  # Reached filesystem root
                    break
                
                current_path = parent
                depth += 1
            
            # If no marker found
            if create_if_missing:
                # Create marker at the hint path
                fallback_path = start_path if hint_path else Path.cwd()
                marker_file = fallback_path / '.codebase_root'
                
                try:
                    marker_file.write_text(
                        f"# Codebase Root Marker\n"
                        f"# Created automatically\n"
                        f"# Do not delete this file\n"
                    )
                    self.root_folder = fallback_path
                    self.logger.info(f"Created .codebase_root at: {fallback_path}")
                    return True, fallback_path, None
                except Exception as e:
                    error = f"Failed to create .codebase_root: {e}"
                    self.logger.error(error)
                    return False, None, error
            else:
                # Use fallback without marker
                fallback_path = start_path if hint_path else Path.cwd()
                self.root_folder = fallback_path
                warning = f".codebase_root marker not found, using: {fallback_path}"
                self.logger.warning(warning)
                return True, fallback_path, warning
                
        except Exception as e:
            error = f"Failed to find project root: {e}"
            self.logger.error(error)
            return False, None, error
    
    def load_codebase_structure(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Load codebase structure from codebase_structure.md file.
        
        Returns:
            Tuple of (success, structure_data, error_message)
        """
        try:
            if not self.root_folder:
                error = "Root folder not set. Call find_project_root() first."
                self.logger.error(error)
                return False, None, error
            
            structure_file = self.root_folder / 'codebase_structure.md'
            
            if not structure_file.exists():
                warning = f"codebase_structure.md not found at {structure_file}"
                self.logger.warning(warning)
                return False, None, warning
            
            # Read structure file
            content = structure_file.read_text(encoding='utf-8')
            
            # Parse structure (basic parsing)
            structure = {
                'raw_content': content,
                'file_path': str(structure_file),
                'last_updated': structure_file.stat().st_mtime,
                'directories': [],
                'key_files': []
            }
            
            # Extract key information from markdown
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- `') and '`' in line[3:]:
                    # Extract directory or file paths
                    path_match = line.split('`')[1] if '`' in line else None
                    if path_match:
                        if path_match.endswith('/'):
                            structure['directories'].append(path_match)
                        else:
                            structure['key_files'].append(path_match)
            
            self.codebase_structure = structure
            self.logger.info("Loaded codebase structure")
            return True, structure, None
            
        except Exception as e:
            error = f"Failed to load codebase structure: {e}"
            self.logger.error(error)
            return False, None, error
    
    def get_relative_path(self, absolute_path: str) -> str:
        """
        Get path relative to project root.
        
        Args:
            absolute_path: Absolute file path
            
        Returns:
            Relative path from project root
        """
        if not self.root_folder:
            return absolute_path
        
        try:
            path = Path(absolute_path).resolve()
            return str(path.relative_to(self.root_folder))
        except ValueError:
            # Path is not relative to root
            return absolute_path
    
    def resolve_path(self, path: str) -> Path:
        """
        Resolve a path relative to project root.
        
        Args:
            path: Relative or absolute path
            
        Returns:
            Resolved absolute Path object
        """
        path_obj = Path(path)
        
        # If already absolute, return as-is
        if path_obj.is_absolute():
            return path_obj
        
        # Otherwise, resolve relative to root
        if self.root_folder:
            return (self.root_folder / path_obj).resolve()
        else:
            return path_obj.resolve()
    
    def get_codebase_context_for_prompt(self) -> str:
        """
        Get formatted codebase structure context for inclusion in LLM prompts.
        
        Returns:
            Formatted context string
        """
        if not self.codebase_structure:
            return ""
        
        context = f"""## Codebase Context

**Project Root:** `{self.root_folder}`

**Key Directories:**
"""
        
        for directory in self.codebase_structure.get('directories', [])[:10]:
            context += f"- `{directory}`\n"
        
        context += """
**Key Files:**
"""
        
        for file_path in self.codebase_structure.get('key_files', [])[:15]:
            context += f"- `{file_path}`\n"
        
        return context
    
    def load_project_context(self) -> Dict[str, Optional[str]]:
        """
        Load all project context files from .project_ai folder.
        
        Returns:
            Dictionary with context file contents:
            - goals: Project goals
            - initial_plan: Initial project plan
            - todo: Project todo list
            - project_preferences: Project-level preferences
            - codebase_structure: Codebase structure (already loaded)
        """
        if not self.root_folder:
            self.logger.warning("Root folder not set, cannot load project context")
            return {}
        
        context = {
            'goals': load_project_goals(self.root_folder),
            'initial_plan': load_initial_plan(self.root_folder),
            'todo': load_project_todo(self.root_folder),
            'project_preferences': load_project_preferences(self.root_folder),
            'codebase_structure': self.codebase_structure.get('raw_content') if self.codebase_structure else None
        }
        
        return context
    
    def get_project_context_for_prompt(
        self,
        include_goals: bool = True,
        include_plan: bool = True,
        include_todo: bool = True,
        include_preferences: bool = True
    ) -> str:
        """
        Get formatted project context for inclusion in LLM prompts.
        
        Args:
            include_goals: Include project goals
            include_plan: Include initial plan
            include_todo: Include todo list
            include_preferences: Include project preferences
            
        Returns:
            Formatted project context string
        """
        if not self.root_folder:
            return ""
        
        context = "## Project Context\n\n"
        has_content = False
        
        # Load all context
        project_context = self.load_project_context()
        
        # Add goals
        if include_goals and project_context.get('goals'):
            context += "### Project Goals\n\n"
            context += project_context['goals'] + "\n\n"
            has_content = True
        
        # Add initial plan (summary only, not full content)
        if include_plan and project_context.get('initial_plan'):
            context += "### Initial Plan\n\n"
            # Extract just the overview section
            plan_lines = project_context['initial_plan'].split('\n')
            in_overview = False
            overview_lines = []
            for line in plan_lines:
                if '## Project Overview' in line:
                    in_overview = True
                    continue
                elif in_overview and line.startswith('##'):
                    break
                elif in_overview:
                    overview_lines.append(line)
            
            if overview_lines:
                context += '\n'.join(overview_lines).strip() + "\n\n"
                context += "*See `.project_ai/initial_plan.md` for full plan.*\n\n"
            has_content = True
        
        # Add todo (high priority items only)
        if include_todo and project_context.get('todo'):
            context += "### Current Tasks (High Priority)\n\n"
            # Extract high priority tasks
            todo_lines = project_context['todo'].split('\n')
            in_high_priority = False
            task_lines = []
            for line in todo_lines:
                if '### High Priority' in line:
                    in_high_priority = True
                    continue
                elif in_high_priority and line.startswith('###'):
                    break
                elif in_high_priority and line.strip().startswith('- ['):
                    task_lines.append(line)
            
            if task_lines:
                context += '\n'.join(task_lines) + "\n\n"
                context += "*See `.project_ai/todo.md` for full task list.*\n\n"
            has_content = True
        
        # Add preferences note (not full content to keep prompt size reasonable)
        if include_preferences and project_context.get('project_preferences'):
            context += "### Project Preferences\n\n"
            context += "Project-specific coding standards and preferences are defined in "
            context += "`.project_ai/rules/project_preferences.md`. These take **highest priority** "
            context += "over user_preferences.md and best_practices.md.\n\n"
            has_content = True
        
        return context if has_content else ""
    
    def ensure_codebase_awareness_initialized(
        self,
        context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Ensure codebase awareness is initialized.
        
        This is a helper method to be called at the start of agent execution
        to ensure root folder and structure are loaded.
        
        Args:
            context: Execution context (may contain 'project_path')
            
        Returns:
            Tuple of (success, error_message)
        """
        # Find root folder if not already set
        if not self.root_folder:
            hint_path = context.get('project_path') or context.get('path')
            success, root, error = self.find_project_root(hint_path)
            
            if not success:
                return False, error
        
        # Load structure if not already loaded
        if not self.codebase_structure:
            success, structure, error = self.load_codebase_structure()
            # Don't fail if structure doesn't exist, just log warning
            if not success and error:
                self.logger.warning(f"Could not load codebase structure: {error}")
        
        return True, None


# Standalone utility functions (for non-class usage)

def find_codebase_root(hint_path: Optional[str] = None) -> Optional[Path]:
    """
    Find project root by searching for .codebase_root marker.
    
    Args:
        hint_path: Optional hint path to start searching from
        
    Returns:
        Path to project root, or None if not found
    """
    try:
        start_path = Path(hint_path).resolve() if hint_path else Path.cwd()
        
        if start_path.is_file():
            start_path = start_path.parent
        
        current_path = start_path
        max_depth = 10
        depth = 0
        
        while depth < max_depth:
            marker_file = current_path / '.codebase_root'
            
            if marker_file.exists():
                return current_path
            
            parent = current_path.parent
            if parent == current_path:
                break
            
            current_path = parent
            depth += 1
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to find codebase root: {e}")
        return None


def create_codebase_root_marker(path: Path) -> bool:
    """
    Create .codebase_root marker file at specified path.
    
    Args:
        path: Directory path where marker should be created
        
    Returns:
        True if created successfully
    """
    try:
        marker_file = path / '.codebase_root'
        
        if marker_file.exists():
            logger.info(f".codebase_root already exists at {path}")
            return True
        
        marker_file.write_text(
            "# Codebase Root Marker\n"
            "#\n"
            "# This file marks the root of the codebase for AI agents.\n"
            "# It helps agents understand project structure and maintain\n"
            "# consistent awareness of the codebase layout.\n"
            "#\n"
            "# DO NOT DELETE THIS FILE\n"
        )
        
        logger.info(f"Created .codebase_root at {path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create .codebase_root: {e}")
        return False


def create_codebase_structure_md(
    root_path: Path,
    project_name: str = "Project",
    project_type: str = "Unknown"
) -> bool:
    """
    Create initial codebase_structure.md file.
    
    Args:
        root_path: Project root directory
        project_name: Name of the project
        project_type: Type of project
        
    Returns:
        True if created successfully
    """
    try:
        from datetime import datetime
        
        structure_file = root_path / 'codebase_structure.md'
        
        content = f"""# Codebase Structure

**Project:** {project_name}  
**Type:** {project_type}  
**Root:** `{root_path}`  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Overview

This file documents the structure and organization of the codebase.
It is automatically maintained by AI agents and helps provide context
for code generation, debugging, and documentation tasks.

---

## Directory Structure

```
{root_path.name}/
├── (Structure will be populated by agents)
```

---

## Key Directories

(To be populated by agents based on actual project structure)

---

## Key Files

(To be populated by agents based on actual project structure)

---

## Notes

- This file is automatically updated by documentation agents
- Keep this synchronized with actual project changes
- Update directory descriptions as the project evolves

---

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        structure_file.write_text(content, encoding='utf-8')
        logger.info(f"Created codebase_structure.md at {root_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create codebase_structure.md: {e}")
        return False


def load_project_context_file(
    root_path: Path,
    filename: str
) -> Optional[str]:
    """
    Load a project context file from .project_ai folder.
    
    Args:
        root_path: Project root directory
        filename: Name of file to load (e.g., 'goals.md', 'todo.md')
        
    Returns:
        File content as string, or None if not found
    """
    try:
        context_file = root_path / '.project_ai' / filename
        
        if not context_file.exists():
            logger.debug(f"Project context file not found: {filename}")
            return None
        
        content = context_file.read_text(encoding='utf-8')
        logger.debug(f"Loaded project context file: {filename}")
        return content
        
    except Exception as e:
        logger.error(f"Failed to load project context file {filename}: {e}")
        return None


def load_project_preferences(root_path: Path) -> Optional[str]:
    """
    Load project-level preferences from .project_ai/rules/project_preferences.md.
    
    Args:
        root_path: Project root directory
        
    Returns:
        Project preferences content, or None if not found
    """
    return load_project_context_file(root_path, 'rules/project_preferences.md')


def load_project_goals(root_path: Path) -> Optional[str]:
    """
    Load project goals from .project_ai/goals.md.
    
    Args:
        root_path: Project root directory
        
    Returns:
        Project goals content, or None if not found
    """
    return load_project_context_file(root_path, 'goals.md')


def load_initial_plan(root_path: Path) -> Optional[str]:
    """
    Load initial project plan from .project_ai/initial_plan.md.
    
    Args:
        root_path: Project root directory
        
    Returns:
        Initial plan content, or None if not found
    """
    return load_project_context_file(root_path, 'initial_plan.md')


def load_project_todo(root_path: Path) -> Optional[str]:
    """
    Load project todo list from .project_ai/todo.md.
    
    Args:
        root_path: Project root directory
        
    Returns:
        Todo list content, or None if not found
    """
    return load_project_context_file(root_path, 'todo.md')


def get_rules_hierarchy_context(
    language: str,
    language_dir: Path,
    root_path: Optional[Path] = None
) -> str:
    """
    Get formatted rules hierarchy context for inclusion in prompts.
    
    This shows the 3-level hierarchy:
    1. best_practices.md (language-level)
    2. user_preferences.md (language-level)
    3. project_preferences.md (project-level) - OVERRIDES the above
    
    Args:
        language: Programming language name
        language_dir: Path to language-specific agent directory
        root_path: Project root directory (optional)
        
    Returns:
        Formatted rules hierarchy context string
    """
    context = f"""## Rules Hierarchy for {language.title()}

**Priority Order (highest to lowest):**
1. **Project Preferences** (in project's `.project_ai/rules/project_preferences.md`) ← HIGHEST PRIORITY
2. **User Preferences** (in `agents/languages/{language}/user_preferences.md`)
3. **Best Practices** (in `agents/languages/{language}/best_practices.md`) ← Baseline

**Important:** If there are conflicts between these files, always follow the higher priority rules.

"""
    
    # Try to load each level
    best_practices_path = language_dir / 'best_practices.md'
    user_prefs_path = language_dir / 'user_preferences.md'
    
    if best_practices_path.exists():
        context += f"✓ Best practices available at: `{best_practices_path}`\n"
    else:
        context += f"✗ Best practices not found at: `{best_practices_path}`\n"
    
    if user_prefs_path.exists():
        context += f"✓ User preferences available at: `{user_prefs_path}`\n"
    else:
        context += f"✗ User preferences not found at: `{user_prefs_path}`\n"
    
    if root_path:
        project_prefs_path = root_path / '.project_ai' / 'rules' / 'project_preferences.md'
        if project_prefs_path.exists():
            context += f"✓ Project preferences available at: `{project_prefs_path}`\n"
        else:
            context += f"✗ Project preferences not found at: `{project_prefs_path}`\n"
    
    return context


def create_project_ai_structure(
    root_path: Path,
    project_name: str,
    project_type: str,
    description: str = "",
    goals: Optional[List[str]] = None,
    initial_plan: str = "",
    author: str = ""
) -> bool:
    """
    Create complete .project_ai structure with all required files.
    
    Creates:
    - .project_ai/codebase_structure.md
    - .project_ai/rules/project_preferences.md
    - .project_ai/initial_plan.md
    - .project_ai/goals.md
    - .project_ai/todo.md
    
    Args:
        root_path: Project root directory
        project_name: Name of the project
        project_type: Type of project
        description: Project description
        goals: List of project goals
        initial_plan: Initial project plan
        author: Project author
        
    Returns:
        True if created successfully
    """
    try:
        from datetime import datetime
        
        project_ai_path = root_path / '.project_ai'
        rules_path = project_ai_path / 'rules'
        
        # Create directories
        project_ai_path.mkdir(parents=True, exist_ok=True)
        rules_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Create codebase_structure.md
        if not (project_ai_path / 'codebase_structure.md').exists():
            create_codebase_structure_md(root_path, project_name, project_type)
        
        # 2. Create rules/project_preferences.md
        prefs_file = rules_path / 'project_preferences.md'
        if not prefs_file.exists():
            prefs_content = f"""# Project Preferences - {project_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project Type:** {project_type}

---

## ⚠️ CRITICAL: Rules Hierarchy

This file is part of a 3-level rules hierarchy:

1. **best_practices.md** (Language-level baseline) ← Located in `agents/languages/*/best_practices.md`
2. **user_preferences.md** (User-level preferences) ← Located in `agents/languages/*/user_preferences.md`
3. **project_preferences.md (THIS FILE)** (Project-specific rules) ← **HIGHEST PRIORITY**

**When conflicts arise, this file (project_preferences.md) ALWAYS takes precedence.**

---

## Project-Specific Guidelines

### Coding Standards

(Add your project-specific coding standards here)

Example:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Follow PEP 8 for Python code
- Use meaningful variable names

### Architecture Patterns

(Add your architecture patterns and design decisions here)

Example:
- Use MVC pattern for web components
- Implement dependency injection
- Follow SOLID principles

### Testing Requirements

(Add your testing requirements here)

Example:
- Maintain minimum 80% code coverage
- Write unit tests for all public APIs
- Include integration tests for critical paths

### Documentation Requirements

(Add your documentation requirements here)

Example:
- Document all public APIs with docstrings
- Include usage examples in README
- Keep CHANGELOG.md updated

### Dependencies and Libraries

(Add your dependency management rules here)

Example:
- Pin all dependency versions
- Avoid deprecated libraries
- Review security advisories before adding new dependencies

---

## Notes

1. Update this file as project requirements evolve
2. All AI agents working on this project must follow these rules first
3. These rules override both user_preferences.md and best_practices.md
4. Keep this synchronized with actual project needs

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            prefs_file.write_text(prefs_content, encoding='utf-8')
            logger.info(f"Created project_preferences.md at {rules_path}")
        
        # 3. Create initial_plan.md
        plan_file = project_ai_path / 'initial_plan.md'
        if not plan_file.exists():
            plan_content = f"""# Initial Project Plan - {project_name}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project Type:** {project_type}  
**Author:** {author or 'N/A'}

---

## Project Overview

{description or 'This project was initialized using AI Agent Console.'}

---

## Initial Architecture

### High-Level Design

{initial_plan or '(To be defined based on project requirements)'}

### Technology Stack

- **Language:** (To be determined)
- **Framework:** (To be determined)
- **Database:** (To be determined)
- **Deployment:** (To be determined)

---

## Development Phases

### Phase 1: Foundation
- [ ] Set up project structure
- [ ] Configure development environment
- [ ] Implement core functionality

### Phase 2: Feature Development
- [ ] Implement main features
- [ ] Add tests
- [ ] Write documentation

### Phase 3: Polish and Deploy
- [ ] Performance optimization
- [ ] Security review
- [ ] Deployment setup

---

## Key Decisions

1. **(Add key architectural decisions here)**
2. **(Add technology choices and justifications)**
3. **(Add any constraints or requirements)**

---

## Notes

- This is the initial plan created at project initialization
- Update this document as the project evolves
- Major changes should be documented here with dates

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            plan_file.write_text(plan_content, encoding='utf-8')
            logger.info(f"Created initial_plan.md at {project_ai_path}")
        
        # 4. Create goals.md
        goals_file = project_ai_path / 'goals.md'
        if not goals_file.exists():
            goals_list = goals or [
                "Implement core functionality",
                "Achieve high code quality and test coverage",
                "Maintain comprehensive documentation",
                "Ensure security and performance"
            ]
            
            goals_content = f"""# Project Goals - {project_name}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project Type:** {project_type}

---

## Main Goals

"""
            for i, goal in enumerate(goals_list, 1):
                goals_content += f"{i}. **{goal}**\n"
            
            goals_content += f"""

---

## Measures of Success

### Functionality
- [ ] All core features implemented
- [ ] Features work as specified
- [ ] Edge cases handled properly

### Quality
- [ ] Code follows project preferences and best practices
- [ ] Test coverage >= 80%
- [ ] No critical bugs or security issues

### Documentation
- [ ] README.md is comprehensive
- [ ] API documentation is complete
- [ ] Code is well-commented

### Performance
- [ ] Meets performance requirements
- [ ] Optimized for target use cases
- [ ] Resource usage is reasonable

### Maintainability
- [ ] Code is modular and organized
- [ ] Dependencies are manageable
- [ ] Easy to extend and modify

---

## Long-Term Vision

(Add your long-term vision and roadmap here)

---

## Notes

- Review and update these goals regularly
- Align all development work with these goals
- Use these as criteria for code reviews

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            goals_file.write_text(goals_content, encoding='utf-8')
            logger.info(f"Created goals.md at {project_ai_path}")
        
        # 5. Create todo.md
        todo_file = project_ai_path / 'todo.md'
        if not todo_file.exists():
            todo_content = f"""# Project Todo List - {project_name}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project Type:** {project_type}

---

## Current Sprint

### High Priority
- [ ] Set up development environment
- [ ] Review project structure and organization
- [ ] Implement initial features

### Medium Priority
- [ ] Write unit tests
- [ ] Add documentation
- [ ] Set up CI/CD pipeline

### Low Priority
- [ ] Performance optimization
- [ ] Additional features
- [ ] UI/UX improvements

---

## Backlog

- [ ] (Add future tasks here)

---

## Completed

- [x] Project initialization
- [x] Created .project_ai structure
- [x] Set up basic project files

---

## Notes

- Update this file as you complete tasks
- Use this to track progress and plan work
- Coordinate with `goals.md` and `initial_plan.md`

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            todo_file.write_text(todo_content, encoding='utf-8')
            logger.info(f"Created todo.md at {project_ai_path}")
        
        logger.info(f"Successfully created .project_ai structure at {root_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create .project_ai structure: {e}")
        return False


def analyze_codebase_structure(path: str) -> Dict[str, Any]:
    """
    Analyze codebase structure at the given path.
    
    Args:
        path: Path to analyze
        
    Returns:
        Dictionary with structure information
    """
    try:
        root_path = Path(path)
        
        if not root_path.exists():
            return {'error': 'Path does not exist'}
        
        structure = {
            'root': str(root_path),
            'directories': [],
            'files': [],
            'languages': set(),
            'total_files': 0,
            'total_size': 0
        }
        
        # Walk through directory
        for item in root_path.rglob('*'):
            if item.is_file():
                structure['files'].append(str(item.relative_to(root_path)))
                structure['total_files'] += 1
                structure['total_size'] += item.stat().st_size
                
                # Detect language
                suffix = item.suffix.lower()
                lang_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.cpp': 'cpp',
                    '.c': 'c',
                    '.cs': 'csharp',
                    '.java': 'java',
                    '.go': 'go',
                    '.rs': 'rust',
                    '.rb': 'ruby',
                    '.php': 'php'
                }
                if suffix in lang_map:
                    structure['languages'].add(lang_map[suffix])
                    
            elif item.is_dir():
                structure['directories'].append(str(item.relative_to(root_path)))
        
        structure['languages'] = list(structure['languages'])
        
        return structure
        
    except Exception as e:
        logger.error(f"Failed to analyze codebase structure: {e}")
        return {'error': str(e)}


def get_file_dependencies(file_path: str) -> List[str]:
    """
    Extract file dependencies (imports) from a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        List of imported modules/files
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return []
        
        content = path.read_text(encoding='utf-8')
        dependencies = []
        
        # Python imports
        if path.suffix == '.py':
            import re
            # Match import statements
            import_pattern = r'^(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)'
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    if match.group(1):  # from ... import
                        dependencies.append(match.group(1))
                    else:  # import ...
                        imports = match.group(2).split(',')
                        dependencies.extend([imp.strip() for imp in imports])
        
        # JavaScript/TypeScript imports
        elif path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            import re
            import_pattern = r'import\s+.*\s+from\s+[\'"](.+)[\'"]'
            for line in content.split('\n'):
                match = re.search(import_pattern, line)
                if match:
                    dependencies.append(match.group(1))
        
        return dependencies
        
    except Exception as e:
        logger.error(f"Failed to get file dependencies: {e}")
        return []


def identify_language(file_path: str) -> str:
    """
    Identify the programming language of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name as string
    """
    try:
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.sh': 'shell',
            '.bash': 'shell',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml'
        }
        
        return lang_map.get(suffix, 'unknown')
        
    except Exception as e:
        logger.error(f"Failed to identify language: {e}")
        return 'unknown'


def get_codebase_summary(path: str) -> Dict[str, Any]:
    """
    Generate a comprehensive codebase summary.
    
    Args:
        path: Path to codebase root
        
    Returns:
        Summary dictionary or formatted string
    """
    try:
        structure = analyze_codebase_structure(path)
        
        if 'error' in structure:
            return structure
        
        summary = {
            'root': structure['root'],
            'statistics': {
                'total_files': structure['total_files'],
                'total_directories': len(structure['directories']),
                'total_size_bytes': structure['total_size'],
                'languages': structure['languages']
            },
            'key_directories': structure['directories'][:10],
            'key_files': structure['files'][:20]
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get codebase summary: {e}")
        return {'error': str(e)}


def find_entry_points(path: str) -> List[str]:
    """
    Find entry points (main files) in a codebase.
    
    Args:
        path: Path to codebase root
        
    Returns:
        List of entry point file paths
    """
    try:
        root_path = Path(path)
        entry_points = []
        
        # Common entry point patterns
        entry_patterns = [
            'main.py',
            'app.py',
            '__main__.py',
            'index.js',
            'app.js',
            'server.js',
            'main.go',
            'main.rs',
            'Main.java',
            'Program.cs'
        ]
        
        # Search for entry point files
        for pattern in entry_patterns:
            for file_path in root_path.rglob(pattern):
                entry_points.append(str(file_path.relative_to(root_path)))
        
        # Also search for files with if __name__ == '__main__'
        for py_file in root_path.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                if '__name__' in content and '__main__' in content:
                    rel_path = str(py_file.relative_to(root_path))
                    if rel_path not in entry_points:
                        entry_points.append(rel_path)
            except:
                pass
        
        return entry_points
        
    except Exception as e:
        logger.error(f"Failed to find entry points: {e}")
        return []


def get_project_metadata(path: str) -> Dict[str, Any]:
    """
    Extract project metadata from various configuration files.
    
    Args:
        path: Path to project root
        
    Returns:
        Dictionary with project metadata
    """
    try:
        root_path = Path(path)
        metadata = {
            'name': root_path.name,
            'path': str(root_path),
            'type': 'unknown',
            'version': None,
            'description': None,
            'dependencies': []
        }
        
        # Check for various project files
        project_files = {
            'setup.py': 'python',
            'pyproject.toml': 'python',
            'requirements.txt': 'python',
            'package.json': 'javascript',
            'pom.xml': 'java',
            'build.gradle': 'java',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            '*.csproj': 'csharp'
        }
        
        for file_pattern, proj_type in project_files.items():
            if '*' in file_pattern:
                files = list(root_path.glob(file_pattern))
                if files:
                    metadata['type'] = proj_type
                    break
            else:
                file_path = root_path / file_pattern
                if file_path.exists():
                    metadata['type'] = proj_type
                    
                    # Try to extract more info
                    if file_pattern == 'setup.py':
                        try:
                            content = file_path.read_text()
                            if 'name=' in content:
                                # Very basic extraction
                                import re
                                match = re.search(r"name=['\"]([^'\"]+)['\"]", content)
                                if match:
                                    metadata['name'] = match.group(1)
                        except:
                            pass
                    
                    elif file_pattern == 'package.json':
                        try:
                            import json
                            data = json.loads(file_path.read_text())
                            metadata['name'] = data.get('name', metadata['name'])
                            metadata['version'] = data.get('version')
                            metadata['description'] = data.get('description')
                        except:
                            pass
                    
                    break
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to get project metadata: {e}")
        return {'error': str(e)}


# Export all
__all__ = [
    'CodebaseAwarenessMixin',
    'find_codebase_root',
    'create_codebase_root_marker',
    'create_codebase_structure_md',
    'load_project_context_file',
    'load_project_preferences',
    'load_project_goals',
    'load_initial_plan',
    'load_project_todo',
    'get_rules_hierarchy_context',
    'create_project_ai_structure',
    'analyze_codebase_structure',
    'get_file_dependencies',
    'identify_language',
    'get_codebase_summary',
    'find_entry_points',
    'get_project_metadata'
]
