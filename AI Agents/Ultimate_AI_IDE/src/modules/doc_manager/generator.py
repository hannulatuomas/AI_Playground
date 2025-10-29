"""
Documentation Generator

Generates various types of documentation using AI.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
from .scanner import CodeStructure, ModuleInfo, ClassInfo, FunctionInfo


@dataclass
class Documentation:
    """Generated documentation."""
    doc_type: str  # 'readme', 'api', 'docstring', 'changelog', 'user_guide'
    content: str
    file_path: Optional[str] = None


class DocGenerator:
    """Generates documentation using AI backend."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize documentation generator.
        
        Args:
            ai_backend: AI backend for generation
            project_rules: Project-specific documentation rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
    
    def generate_readme(self, project_name: str, language: str,
                       framework: Optional[str], structure: CodeStructure,
                       features: List[str]) -> Documentation:
        """
        Generate README.md for project.
        
        Args:
            project_name: Name of the project
            language: Programming language
            framework: Framework used (if any)
            structure: Code structure
            features: List of main features
            
        Returns:
            Documentation object with README content
        """
        prompt = self._build_readme_prompt(
            project_name, language, framework, structure, features
        )
        
        try:
            content = self.ai_backend.query(prompt, max_tokens=2000)
            content = self._clean_markdown(content)
            
            return Documentation(
                doc_type='readme',
                content=content,
                file_path='README.md'
            )
        except Exception as e:
            print(f"Error generating README: {e}")
            return self._generate_fallback_readme(project_name, language)
    
    def generate_api_docs(self, structure: CodeStructure, 
                         language: str) -> Documentation:
        """
        Generate API documentation.
        
        Args:
            structure: Code structure
            language: Programming language
            
        Returns:
            Documentation object with API docs
        """
        prompt = self._build_api_docs_prompt(structure, language)
        
        try:
            content = self.ai_backend.query(prompt, max_tokens=3000)
            content = self._clean_markdown(content)
            
            return Documentation(
                doc_type='api',
                content=content,
                file_path='docs/API.md'
            )
        except Exception as e:
            print(f"Error generating API docs: {e}")
            return self._generate_fallback_api_docs(structure)
    
    def generate_docstring(self, func_info: FunctionInfo, 
                          language: str) -> str:
        """
        Generate docstring for a function.
        
        Args:
            func_info: Function information
            language: Programming language
            
        Returns:
            Generated docstring
        """
        prompt = self._build_docstring_prompt(func_info, language)
        
        try:
            docstring = self.ai_backend.query(prompt, max_tokens=500)
            return self._clean_docstring(docstring, language)
        except Exception as e:
            print(f"Error generating docstring: {e}")
            return self._generate_fallback_docstring(func_info)
    
    def generate_user_guide(self, project_name: str, structure: CodeStructure,
                           features: List[str]) -> Documentation:
        """
        Generate user guide.
        
        Args:
            project_name: Project name
            structure: Code structure
            features: List of features
            
        Returns:
            Documentation object with user guide
        """
        prompt = self._build_user_guide_prompt(project_name, structure, features)
        
        try:
            content = self.ai_backend.query(prompt, max_tokens=2500)
            content = self._clean_markdown(content)
            
            return Documentation(
                doc_type='user_guide',
                content=content,
                file_path='docs/USER_GUIDE.md'
            )
        except Exception as e:
            print(f"Error generating user guide: {e}")
            return self._generate_fallback_user_guide(project_name)
    
    def generate_changelog_entry(self, version: str, changes: List[str],
                                 change_type: str = 'Added') -> str:
        """
        Generate changelog entry.
        
        Args:
            version: Version number
            changes: List of changes
            change_type: Type of changes (Added, Changed, Fixed, etc.)
            
        Returns:
            Formatted changelog entry
        """
        from datetime import datetime
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        entry = f"\n## [{version}] - {date_str}\n\n"
        entry += f"### {change_type}\n"
        
        for change in changes:
            entry += f"- {change}\n"
        
        return entry
    
    def _build_readme_prompt(self, project_name: str, language: str,
                            framework: Optional[str], structure: CodeStructure,
                            features: List[str]) -> str:
        """Build prompt for README generation."""
        rules_text = "\n".join(self.project_rules) if self.project_rules else ""
        
        prompt = f"""Generate a comprehensive README.md for this project:

Project: {project_name}
Language: {language}
Framework: {framework or 'None'}
Entry Points: {', '.join(structure.entry_points) if structure.entry_points else 'None'}
Main Features:
{chr(10).join(f'- {f}' for f in features)}

Public API Elements: {len(structure.public_api)}
Modules: {len(structure.modules)}

Include the following sections:
1. Project Title and Description
2. Features
3. Installation Instructions
4. Quick Start Guide
5. Usage Examples
6. Configuration (if applicable)
7. Project Structure
8. Contributing Guidelines
9. License

Follow markdown best practices and make it clear and professional.
{f'Additional Rules: {rules_text}' if rules_text else ''}

Generate only the README content, no additional commentary."""
        
        return prompt
    
    def _build_api_docs_prompt(self, structure: CodeStructure, 
                              language: str) -> str:
        """Build prompt for API documentation generation."""
        # Summarize public API
        api_summary = []
        for module in structure.modules:
            for cls in module.classes:
                if cls.is_public:
                    api_summary.append(f"Class {cls.name}: {cls.docstring or 'No description'}")
                    for method in cls.methods:
                        if method.is_public:
                            params = ', '.join(method.parameters)
                            api_summary.append(f"  - {method.name}({params})")
            
            for func in module.functions:
                if func.is_public:
                    params = ', '.join(func.parameters)
                    api_summary.append(f"Function {func.name}({params}): {func.docstring or 'No description'}")
        
        prompt = f"""Generate API documentation for this {language} project:

Public API Elements:
{chr(10).join(api_summary[:50])}  # Limit to first 50 items

Create comprehensive API documentation including:
1. Overview
2. Classes and their methods
3. Functions
4. Parameters and return types
5. Usage examples
6. Error handling

Format as markdown with clear sections and code examples.
Generate only the API documentation content."""
        
        return prompt
    
    def _build_docstring_prompt(self, func_info: FunctionInfo, 
                               language: str) -> str:
        """Build prompt for docstring generation."""
        params_str = ', '.join(func_info.parameters)
        
        prompt = f"""Generate a docstring for this {language} function:

Function: {func_info.name}
Parameters: {params_str}
Return Type: {func_info.return_type or 'Unknown'}
Is Method: {func_info.is_method}
{f'Class: {func_info.class_name}' if func_info.class_name else ''}

Generate a clear, concise docstring following {language} conventions.
Include:
- Brief description
- Args/Parameters section
- Returns section
- Raises section (if applicable)

Generate only the docstring content, properly formatted."""
        
        return prompt
    
    def _build_user_guide_prompt(self, project_name: str, 
                                structure: CodeStructure,
                                features: List[str]) -> str:
        """Build prompt for user guide generation."""
        prompt = f"""Generate a comprehensive user guide for {project_name}:

Features:
{chr(10).join(f'- {f}' for f in features)}

Entry Points: {', '.join(structure.entry_points) if structure.entry_points else 'CLI or API'}

Create a detailed user guide including:
1. Introduction
2. Getting Started
3. Core Concepts
4. Feature Walkthroughs (for each feature)
5. Advanced Usage
6. Troubleshooting
7. FAQ

Make it beginner-friendly with examples and screenshots placeholders.
Format as markdown.
Generate only the user guide content."""
        
        return prompt
    
    def _clean_markdown(self, content: str) -> str:
        """Clean up generated markdown content."""
        # Remove markdown code blocks if AI wrapped the content
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            content = '\n'.join(lines)
        
        return content.strip()
    
    def _clean_docstring(self, docstring: str, language: str) -> str:
        """Clean up generated docstring."""
        docstring = docstring.strip()
        
        # Remove markdown code blocks
        if docstring.startswith('```'):
            lines = docstring.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].startswith('```'):
                lines = lines[:-1]
            docstring = '\n'.join(lines)
        
        # Remove quotes if AI added them
        if docstring.startswith('"""') and docstring.endswith('"""'):
            docstring = docstring[3:-3]
        elif docstring.startswith("'''") and docstring.endswith("'''"):
            docstring = docstring[3:-3]
        
        return docstring.strip()
    
    def _generate_fallback_readme(self, project_name: str, 
                                 language: str) -> Documentation:
        """Generate basic README as fallback."""
        content = f"""# {project_name}

A {language} project.

## Installation

```bash
# Installation instructions here
```

## Usage

```{language}
# Usage examples here
```

## License

MIT License
"""
        return Documentation(
            doc_type='readme',
            content=content,
            file_path='README.md'
        )
    
    def _generate_fallback_api_docs(self, structure: CodeStructure) -> Documentation:
        """Generate basic API docs as fallback."""
        content = "# API Documentation\n\n"
        
        for module in structure.modules:
            content += f"## Module: {module.name}\n\n"
            
            if module.classes:
                content += "### Classes\n\n"
                for cls in module.classes:
                    if cls.is_public:
                        content += f"#### {cls.name}\n\n"
                        if cls.docstring:
                            content += f"{cls.docstring}\n\n"
            
            if module.functions:
                content += "### Functions\n\n"
                for func in module.functions:
                    if func.is_public:
                        params = ', '.join(func.parameters)
                        content += f"#### {func.name}({params})\n\n"
                        if func.docstring:
                            content += f"{func.docstring}\n\n"
        
        return Documentation(
            doc_type='api',
            content=content,
            file_path='docs/API.md'
        )
    
    def _generate_fallback_docstring(self, func_info: FunctionInfo) -> str:
        """Generate basic docstring as fallback."""
        params_str = ', '.join(func_info.parameters)
        
        docstring = f"{func_info.name} function.\n\n"
        
        if func_info.parameters:
            docstring += "Args:\n"
            for param in func_info.parameters:
                docstring += f"    {param}: Description\n"
        
        if func_info.return_type:
            docstring += f"\nReturns:\n    {func_info.return_type}\n"
        
        return docstring
    
    def _generate_fallback_user_guide(self, project_name: str) -> Documentation:
        """Generate basic user guide as fallback."""
        content = f"""# {project_name} User Guide

## Introduction

Welcome to {project_name}!

## Getting Started

### Installation

Follow the installation instructions in README.md

### Quick Start

Basic usage examples here.

## Features

Detailed feature descriptions here.

## Troubleshooting

Common issues and solutions.
"""
        return Documentation(
            doc_type='user_guide',
            content=content,
            file_path='docs/USER_GUIDE.md'
        )
