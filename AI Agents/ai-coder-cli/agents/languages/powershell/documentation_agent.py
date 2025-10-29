"""
PowerShell Documentation Agent

This agent specializes in maintaining documentation for PowerShell projects.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ...base.documentation_agent import DocumentationAgentBase


logger = logging.getLogger(__name__)


class PowerShellDocumentationAgent(DocumentationAgentBase):
    """
    Documentation agent specialized for PowerShell projects.
    
    Features:
    - PowerShell-specific docstring/comment formats
    - Project structure awareness
    - comment-based help documentation generation
    - Best practices for PowerShell documentation
    """
    
    def __init__(
        self,
        name: str = "documentation_powershell",
        description: str = "PowerShell-specific documentation agent",
        **kwargs
    ):
        """
        Initialize PowerShell documentation agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(
            name=name,
            description=description,
            language="powershell",
            **kwargs
        )
        
        self.logger.info("PowerShellDocumentationAgent initialized")
    
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
        Generate PowerShell-specific code documentation.
        
        Args:
            code_content: Source code content
            file_path: Path to source file
            context: Execution context
            
        Returns:
            Documented code content
        """
        # Build prompt for LLM with language-specific requirements
        prompt = f"""Add comprehensive comment-based help documentation to this PowerShell code.

File: {file_path}

Original Code:
```powershell
{code_content}
```

Instructions:
1. Use comment-based help format for documentation
2. Follow PowerShell documentation conventions from documentation_preferences.md
3. Document all functions, parameters, and cmdlets
4. Include parameter descriptions and return types where applicable
5. Add inline comments for complex logic
6. Preserve all existing functionality

"""
        
        if self.documentation_preferences:
            prompt += f"""
Documentation Preferences:
{self.documentation_preferences}
"""
        
        prompt += """
Output ONLY the documented code, no explanations or markdown blocks.
"""
        
        try:
            if self.llm_router:
                response = self._get_llm_response(prompt, temperature=0.5)
                documented_code = response.get('content', code_content)
                
                # Clean up any markdown code blocks
                documented_code = self._clean_code_blocks(documented_code)
                
                return documented_code
            else:
                self.logger.warning("No LLM router available, returning original code")
                return code_content
                
        except Exception as e:
            self.logger.error(f"Failed to generate code documentation: {e}")
            return code_content
    
    def _get_documentation_format(self) -> Dict[str, Any]:
        """
        Get PowerShell-specific documentation format specifications.
        
        Returns:
            Dictionary with documentation format specifications
        """
        return {
            'style': 'comment-based help',
            'code_doc_style': 'comment-based help',
            'readme_format': 'markdown',
            'changelog_format': 'keep-a-changelog',
            'comment_help': True,
            'parameter_docs': True
        }
    
    def _validate_documentation(self, doc_content: str) -> Dict[str, Any]:
        """
        Validate PowerShell-specific documentation.
        
        Args:
            doc_content: Documentation content
            
        Returns:
            Validation result dictionary with 'valid' bool and optional 'errors'
        """
        errors = []
        warnings = []
        
        # Basic validation
        if not doc_content or not doc_content.strip():
            errors.append("Documentation is empty")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # PowerShell-specific validation
        # Check for comment-based help
        if '<#' in doc_content or '.SYNOPSIS' in doc_content:
            warnings.append('Uses comment-based help (good for PowerShell)')
        
        is_valid = len(errors) == 0
        
        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings
        }
    
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


# Export
__all__ = ['PowerShellDocumentationAgent']
