"""
CPP Documentation Agent

This agent specializes in maintaining documentation for CPP projects.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ...base.documentation_agent import DocumentationAgentBase


logger = logging.getLogger(__name__)


class CPPDocumentationAgent(DocumentationAgentBase):
    """
    Documentation agent specialized for CPP projects.
    
    Features:
    - CPP-specific docstring/comment formats
    - Project structure awareness
    - Doxygen documentation generation
    - Best practices for CPP documentation
    """
    
    def __init__(
        self,
        name: str = "documentation_cpp",
        description: str = "CPP-specific documentation agent",
        **kwargs
    ):
        """
        Initialize CPP documentation agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional arguments passed to base class
        """
        super().__init__(
            name=name,
            description=description,
            language="cpp",
            **kwargs
        )
        
        self.logger.info("CppDocumentationAgent initialized")
    
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
        Generate CPP-specific code documentation.
        
        Args:
            code_content: Source code content
            file_path: Path to source file
            context: Execution context
            
        Returns:
            Documented code content
        """
        # Build prompt for LLM with language-specific requirements
        prompt = f"""Add comprehensive Doxygen documentation to this CPP code.

File: {file_path}

Original Code:
```cpp
{code_content}
```

Instructions:
1. Use Doxygen format for documentation
2. Follow CPP documentation conventions from documentation_preferences.md
3. Document all classes, functions, methods, and templates
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
        Get CPP-specific documentation format specifications.
        
        Returns:
            Dictionary with documentation format specifications
        """
        return {
            'style': 'Doxygen',
            'code_doc_style': 'Doxygen',
            'readme_format': 'markdown',
            'changelog_format': 'keep-a-changelog',
            'doxygen_format': True,
            'template_support': True
        }
    
    def _validate_documentation(self, doc_content: str) -> Dict[str, Any]:
        """
        Validate CPP-specific documentation.
        
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
        
        # CPP-specific validation
        # Check for Doxygen
        if '/**' in doc_content or '@brief' in doc_content or '@param' in doc_content:
            warnings.append('Uses Doxygen format (good for CPP)')
        
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
__all__ = ['CppDocumentationAgent']
