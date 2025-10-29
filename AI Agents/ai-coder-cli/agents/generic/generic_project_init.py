
"""
General Project Initialization Agent

This agent handles generic project initialization for any language or framework.
It provides a fallback when no language-specific initialization agent is available.
"""

from typing import Dict, Any, List, Optional
from ..base import ProjectInitBase


class GenericProjectInitAgent(ProjectInitBase):
    """
    General project initialization agent for any language/framework.
    
    This agent provides generic project initialization capabilities and serves
    as a fallback when language-specific agents are not available.
    
    Capabilities:
    - Initialize basic project structure
    - Create .project_ai folder with rules
    - Support multiple project types (basic, library, app, cli)
    - Generic configuration file creation
    - Git initialization
    """
    
    def __init__(
        self,
        name: str = "project_init",
        description: str = "General project initialization for any language",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        """
        Initialize the general project init agent.
        
        Args:
            name: Agent name
            description: Agent description
            llm_router: LLM router
            tool_registry: Tool registry
            config: Configuration
            memory_manager: Memory manager
        """
        super().__init__(
            name=name,
            description=description,
            language="generic",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """
        Get supported project types for generic initialization.
        
        Returns:
            List of project types
        """
        return [
            'basic',      # Basic project structure
            'library',    # Library/package project
            'application', # Application project
            'cli',        # Command-line tool
            'service',    # Service/daemon
            'microservice', # Microservice
            'monorepo',   # Monorepo structure
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """
        Get directory structure for project type.
        
        Args:
            project_type: Type of project
            
        Returns:
            Dictionary with directories and files
        """
        structures = {
            'basic': {
                'directories': [
                    'src',
                    'docs',
                    'tests',
                ],
            },
            'library': {
                'directories': [
                    'src',
                    'tests',
                    'docs',
                    'examples',
                ],
            },
            'application': {
                'directories': [
                    'src',
                    'src/core',
                    'src/utils',
                    'tests',
                    'docs',
                    'config',
                ],
            },
            'cli': {
                'directories': [
                    'src',
                    'src/commands',
                    'src/utils',
                    'tests',
                    'docs',
                ],
            },
            'service': {
                'directories': [
                    'src',
                    'src/api',
                    'src/core',
                    'src/utils',
                    'tests',
                    'config',
                    'docs',
                ],
            },
            'microservice': {
                'directories': [
                    'src',
                    'src/api',
                    'src/services',
                    'src/models',
                    'src/utils',
                    'tests',
                    'config',
                    'docs',
                    'deployments',
                ],
            },
            'monorepo': {
                'directories': [
                    'packages',
                    'apps',
                    'libs',
                    'tools',
                    'docs',
                ],
            },
        }
        
        return structures.get(project_type, structures['basic'])
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """
        Get default configuration files.
        
        Args:
            config: Project configuration
            
        Returns:
            Dictionary mapping file paths to content
        """
        files = {}
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A new project')}

## Overview

This project was initialized using AI Agent Console.

## Getting Started

1. Review the project structure
2. Check `.project_ai/rules.md` for project-specific guidelines
3. Start building!

## Project Structure

```
{config['project_name']}/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
└── .project_ai/   # AI agent project rules
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # .gitignore
        if config.get('git_init', True):
            files['.gitignore'] = """# General
.DS_Store
*.log
*.tmp
*~

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local

# Build outputs
dist/
build/
*.out
*.exe

# Dependencies (adjust based on your stack)
node_modules/
vendor/
venv/
__pycache__/
*.pyc
"""
        
        # CHANGELOG.md
        files['CHANGELOG.md'] = f"""# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial project setup
- Basic project structure

"""
        
        # LICENSE (MIT by default)
        if config.get('license', 'MIT') == 'MIT':
            files['LICENSE'] = f"""MIT License

Copyright (c) {config.get('author', 'Project Author')}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        return files
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """
        Generate language-specific rules.
        
        For the general agent, these are generic best practices.
        
        Args:
            config: Project configuration
            
        Returns:
            Markdown content with rules
        """
        return f"""## General Project Rules

### Code Organization

1. **Directory Structure**: Follow the standard structure for {config['project_type']} projects
2. **File Naming**: Use clear, descriptive names for files and directories
3. **Module Organization**: Keep related functionality together
4. **Separation of Concerns**: Separate business logic, data access, and presentation

### Code Quality

1. **Consistency**: Maintain consistent coding style throughout the project
2. **Documentation**: Document complex logic and public APIs
3. **Testing**: Write tests for critical functionality
4. **Error Handling**: Handle errors gracefully with appropriate messages
5. **Logging**: Use structured logging for debugging and monitoring

### Version Control

1. **Commits**: Write clear, descriptive commit messages
2. **Branching**: Use feature branches for new development
3. **Pull Requests**: Review code before merging
4. **Tags**: Use semantic versioning for releases

### Dependencies

1. **Management**: Use a dependency manager appropriate for your language
2. **Versions**: Pin dependency versions for reproducibility
3. **Security**: Keep dependencies up to date
4. **Auditing**: Regularly audit dependencies for vulnerabilities

### Documentation

1. **README**: Keep README.md up to date with setup instructions
2. **CHANGELOG**: Document changes in CHANGELOG.md
3. **API Docs**: Document public APIs and interfaces
4. **Architecture**: Document major architectural decisions

### Security

1. **Secrets**: Never commit secrets, API keys, or passwords
2. **Input Validation**: Validate all user inputs
3. **Dependencies**: Regularly update and audit dependencies
4. **Permissions**: Follow principle of least privilege

### Performance

1. **Optimization**: Optimize after profiling, not before
2. **Caching**: Use caching for expensive operations
3. **Resources**: Clean up resources properly
4. **Monitoring**: Monitor application performance

### Project-Specific Guidelines

Language: {config.get('language', 'generic')}
Framework: {config.get('framework', 'N/A')}
Project Type: {config['project_type']}

(Add your project-specific guidelines here as the project evolves)
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """
        Get language-specific questions.
        
        Returns:
            List of questions
        """
        return [
            {
                'key': 'language',
                'question': 'Primary programming language?',
                'type': 'text',
                'default': 'unknown',
                'required': False
            },
            {
                'key': 'framework',
                'question': 'Framework (if any)?',
                'type': 'text',
                'default': '',
                'required': False
            },
            {
                'key': 'license',
                'question': 'License type?',
                'type': 'choice',
                'options': ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'None'],
                'default': 'MIT',
                'required': False
            },
        ]


