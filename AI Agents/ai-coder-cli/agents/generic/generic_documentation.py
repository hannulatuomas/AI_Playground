"""
Generic Documentation Agent

Language-agnostic documentation agent that provides fallback functionality
for maintaining project documentation across all languages.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..base.documentation_agent import DocumentationAgentBase


logger = logging.getLogger(__name__)


class GenericDocumentationAgent(DocumentationAgentBase):
    """
    Generic documentation agent for any language.
    
    This agent provides fallback documentation functionality for projects
    without language-specific documentation agents. It can:
    - Update README, TODO, and STATUS files
    - Generate basic code documentation
    - Maintain codebase structure documentation
    - Handle API documentation
    
    Uses LLM-based approaches without language-specific tooling.
    """
    
    def __init__(
        self,
        name: str = "documentation_generic",
        description: str = "Generic documentation agent for any language",
        **kwargs
    ):
        """
        Initialize generic documentation agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(
            name=name,
            description=description,
            language=None,  # Generic - no specific language
            **kwargs
        )
        
        self.logger.info("GenericDocumentationAgent initialized")
    
    # ========================================================================
    # Implementation of Abstract Methods
    # ========================================================================
    
    def _generate_code_documentation(
        self,
        code_content: str,
        file_path: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate generic code documentation using LLM.
        
        Args:
            code_content: Source code content
            file_path: Path to source file
            context: Execution context
            
        Returns:
            Documented code content
        """
        # Detect language from file extension
        language = self._detect_language_from_file(file_path)
        
        # Build prompt for LLM
        prompt = f"""Add comprehensive documentation to this {language} code.

File: {file_path}

Original Code:
```
{code_content}
```

Instructions:
1. Add appropriate docstrings/comments based on the language
2. Document all functions, classes, and complex logic
3. Include parameter descriptions and return types where applicable
4. Add inline comments for non-obvious code
5. Follow {language} documentation conventions
6. Preserve all existing functionality

Output ONLY the documented code, no explanations or markdown.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.5)
                documented_code = response.get('content', code_content)
                
                # Clean up any markdown code blocks
                documented_code = self._clean_code_blocks(documented_code)
                
                return documented_code
            else:
                # Fallback: return original code
                self.logger.warning("No LLM router available, returning original code")
                return code_content
                
        except Exception as e:
            self.logger.error(f"Failed to generate code documentation: {e}")
            return code_content
    
    def _get_documentation_format(self) -> Dict[str, Any]:
        """
        Get generic documentation format specifications.
        
        Returns:
            Dictionary with documentation format specifications
        """
        return {
            'style': 'markdown',
            'readme_sections': [
                'Title',
                'Description',
                'Installation',
                'Usage',
                'Configuration',
                'API Reference',
                'Contributing',
                'License'
            ],
            'code_doc_style': 'language-appropriate',
            'changelog_format': 'keep-a-changelog',
            'api_doc_format': 'rest',
            'versioning': 'semver'
        }
    
    def _validate_documentation(self, doc_content: str) -> Dict[str, Any]:
        """
        Validate generic documentation.
        
        Args:
            doc_content: Documentation content
            
        Returns:
            Validation result dictionary with 'valid' bool and optional 'errors'
        """
        errors = []
        warnings = []
        
        # Basic validation checks
        if not doc_content or not doc_content.strip():
            errors.append("Documentation is empty")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Check for common markdown issues
        lines = doc_content.split('\n')
        
        # Check for title
        has_title = any(line.strip().startswith('#') for line in lines[:10])
        if not has_title:
            warnings.append("No title found in documentation")
        
        # Check for very short documentation
        if len(doc_content) < 100:
            warnings.append("Documentation seems very short")
        
        # Check for broken markdown links
        import re
        broken_links = re.findall(r'\[([^\]]+)\]\(\)', doc_content)
        if broken_links:
            warnings.append(f"Found {len(broken_links)} broken markdown links")
        
        # Check for unbalanced code blocks
        code_block_count = doc_content.count('```')
        if code_block_count % 2 != 0:
            errors.append("Unbalanced code blocks (odd number of ```)")
        
        is_valid = len(errors) == 0
        
        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }
    
    # ========================================================================
    # Enhanced Documentation Generation Methods
    # ========================================================================
    
    def _generate_readme_content(
        self,
        existing_content: str,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive README content using LLM.
        
        Args:
            existing_content: Existing README content
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Updated README content
        """
        # Build comprehensive prompt
        prompt = f"""You are a technical documentation expert. Create or update a README.md file.

Current README:
```markdown
{existing_content if existing_content else '(No existing README - create new)'}
```

Context Information:
- Project Path: {self.root_folder if self.root_folder else 'N/A'}
- Files Changed: {context.get('files_changed', [])}
- Custom Instructions: {context.get('custom_instructions', 'Create comprehensive README')}
"""
        
        if vector_context:
            prompt += f"""
Codebase Context (from vector DB):
{vector_context}
"""
        
        if self.codebase_structure:
            prompt += f"""
Project Structure:
{self.codebase_structure.get('raw_content', 'N/A')[:500]}
"""
        
        prompt += """
Generate a comprehensive README.md that includes:

1. **Project Title & Description**: Clear, concise overview
2. **Features**: Key features and capabilities
3. **Installation**: Step-by-step installation instructions
4. **Usage**: Examples and usage guidelines
5. **Configuration**: Configuration options and environment variables
6. **API Documentation**: If applicable, API endpoints and usage
7. **Development**: Development setup and guidelines
8. **Testing**: How to run tests
9. **Contributing**: Contribution guidelines
10. **License**: License information
11. **Contact/Support**: How to get help

Guidelines:
- Use clear, professional language
- Include code examples where appropriate
- Use proper markdown formatting
- Add badges if applicable (build status, version, etc.)
- Keep it organized and easy to navigate
- Update sections based on existing content
- Preserve important existing information

Output ONLY the complete README.md content in markdown format.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.7)
                content = response.get('content', existing_content or self._get_default_readme_template())
                
                # Validate the generated content
                validation = self._validate_documentation(content)
                if not validation['valid']:
                    self.logger.warning(f"Generated README has issues: {validation['errors']}")
                
                return content
            else:
                return existing_content or self._get_default_readme_template()
                
        except Exception as e:
            self.logger.error(f"Failed to generate README: {e}")
            return existing_content or self._get_default_readme_template()
    
    def _generate_todo_content(
        self,
        existing_content: str,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate intelligent TODO list using LLM.
        
        Args:
            existing_content: Existing TODO content
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Updated TODO content
        """
        prompt = f"""You are a project management expert. Update the TODO.md file.

Current TODO:
```markdown
{existing_content if existing_content else '(No existing TODO - create new)'}
```

Context:
- Recent changes: {context.get('files_changed', [])}
- New tasks mentioned: {context.get('new_tasks', [])}
- Completed tasks: {context.get('completed_tasks', [])}
"""
        
        if vector_context:
            prompt += f"""
Additional Context:
{vector_context}
"""
        
        prompt += """
Create an organized TODO.md with:

1. **High Priority**: Critical tasks that block progress
2. **Medium Priority**: Important but not blocking
3. **Low Priority**: Nice to have
4. **In Progress**: Currently being worked on
5. **Completed**: Recently finished tasks (keep last 5-10)
6. **Backlog**: Future considerations

Format:
- Use checkboxes: `- [ ]` for incomplete, `- [x]` for complete
- Include brief descriptions
- Add dates where relevant
- Group related tasks
- Keep it actionable and specific

Output ONLY the complete TODO.md content.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.6)
                return response.get('content', existing_content or self._get_default_todo_template())
            else:
                return existing_content or self._get_default_todo_template()
        except Exception as e:
            self.logger.error(f"Failed to generate TODO: {e}")
            return existing_content or self._get_default_todo_template()
    
    def _generate_status_content(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate project status report using LLM.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            Status content
        """
        from datetime import datetime
        
        prompt = f"""Generate a project STATUS.md report.

Context:
- Recent Activity: {context.get('recent_activity', 'N/A')}
- Files Changed: {context.get('files_changed', [])}
- Current Phase: {context.get('project_phase', 'Development')}
"""
        
        if vector_context:
            prompt += f"""
Codebase Context:
{vector_context}
"""
        
        prompt += f"""
Create a STATUS.md with:

1. **Overview**: Current project state (1-2 sentences)
2. **Progress**: What's been accomplished recently
3. **Current Focus**: What's being worked on now
4. **Blockers**: Any issues or blockers
5. **Next Steps**: Immediate next actions
6. **Health Metrics**: Code quality, test coverage, etc. if available
7. **Timeline**: Expected milestones

Keep it concise and informative.
Output ONLY the STATUS.md content.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.6)
                return response.get('content', self._get_default_status_template())
            else:
                return self._get_default_status_template()
        except Exception as e:
            self.logger.error(f"Failed to generate STATUS: {e}")
            return self._get_default_status_template()
    
    def _generate_api_documentation_content(
        self,
        context: Dict[str, Any],
        vector_context: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive API documentation using LLM.
        
        Args:
            context: Execution context
            vector_context: Optional context from vector DB
            
        Returns:
            API documentation content
        """
        prompt = f"""Generate comprehensive API documentation.

Context:
- API Files: {context.get('api_files', [])}
- Framework: {context.get('framework', 'N/A')}
"""
        
        if vector_context:
            prompt += f"""
API Code Context:
{vector_context}
"""
        
        prompt += """
Create an API.md with:

1. **Overview**: API purpose and capabilities
2. **Base URL**: Base endpoint URL
3. **Authentication**: Authentication methods
4. **Endpoints**: For each endpoint:
   - Method and path
   - Description
   - Parameters (path, query, body)
   - Request example
   - Response example
   - Error responses
5. **Rate Limiting**: If applicable
6. **Versioning**: API version information
7. **SDK/Client Libraries**: If available
8. **Examples**: Common use cases

Use clear formatting and include code examples.
Output ONLY the API.md content.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.6)
                return response.get('content', self._get_default_api_docs_template())
            else:
                return self._get_default_api_docs_template()
        except Exception as e:
            self.logger.error(f"Failed to generate API docs: {e}")
            return self._get_default_api_docs_template()
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _detect_language_from_file(self, file_path: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected language name
        """
        ext_to_lang = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React/JSX',
            '.tsx': 'React/TSX',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++ Header',
            '.hpp': 'C++ Header',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sh': 'Bash',
            '.bash': 'Bash',
            '.zsh': 'Zsh',
            '.ps1': 'PowerShell',
            '.bat': 'Batch',
            '.cmd': 'CMD',
            '.r': 'R',
            '.R': 'R',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.sass': 'Sass',
            '.vue': 'Vue',
            '.lua': 'Lua',
            '.pl': 'Perl',
            '.md': 'Markdown',
        }
        
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        return ext_to_lang.get(ext, 'Unknown')
    
    def _clean_code_blocks(self, content: str) -> str:
        """
        Clean markdown code blocks from LLM output.
        
        Args:
            content: Content with possible markdown code blocks
            
        Returns:
            Cleaned content
        """
        import re
        
        # Remove markdown code blocks
        pattern = r'^```[\w]*\n(.*?)\n```$'
        match = re.match(pattern, content.strip(), re.DOTALL)
        
        if match:
            return match.group(1)
        
        return content
    
    def _get_default_todo_template(self) -> str:
        """Get default TODO template."""
        from datetime import datetime
        
        return f"""# TODO List

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## High Priority

- [ ] Define critical tasks

## Medium Priority

- [ ] Define important tasks

## Low Priority

- [ ] Define nice-to-have tasks

## In Progress

- Currently working on project setup

## Completed

- [x] Initial project setup ({datetime.now().strftime('%Y-%m-%d')})

## Backlog

- Future enhancements and ideas
"""
    
    def _get_default_status_template(self) -> str:
        """Get default STATUS template."""
        from datetime import datetime
        
        return f"""# Project Status

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

Project is in active development.

## Recent Progress

- Project structure initialized
- Core components being developed

## Current Focus

- Building foundational features
- Setting up development environment

## Blockers

None currently identified.

## Next Steps

1. Continue core development
2. Add comprehensive tests
3. Update documentation

## Health Metrics

- **Status**: 🟢 Healthy
- **Code Quality**: In Progress
- **Test Coverage**: TBD
- **Documentation**: In Progress

---

*This status is automatically generated and maintained by the documentation agent.*
"""
    
    def _get_default_api_docs_template(self) -> str:
        """Get default API documentation template."""
        from datetime import datetime
        
        return f"""# API Documentation

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

API overview and description.

## Base URL

```
https://api.example.com/v1
```

## Authentication

Describe authentication method here.

## Endpoints

### GET /example

**Description:** Example endpoint

**Parameters:**
- `id` (query, optional): Example parameter

**Request:**
```bash
curl -X GET "https://api.example.com/v1/example?id=123"
```

**Response:**
```json
{{
    "status": "success",
    "data": {{}}
}}
```

---

## Error Responses

Standard error response format:

```json
{{
    "status": "error",
    "message": "Error description",
    "code": "ERROR_CODE"
}}
```

---

*This API documentation is automatically generated and maintained.*
"""


# Export
__all__ = ['GenericDocumentationAgent']
