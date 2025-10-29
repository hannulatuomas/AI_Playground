"""
Template Engine

Advanced template rendering with conditionals and loops.
"""

from typing import Dict, Any, List
import re


class TemplateEngine:
    """Template engine for prompt rendering."""
    
    def __init__(self):
        """Initialize template engine."""
        pass
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Render template with variables.
        
        Args:
            template: Template string
            variables: Variable values
            
        Returns:
            Rendered string
        """
        result = template
        
        # Process conditionals
        result = self._process_conditionals(result, variables)
        
        # Process loops
        result = self._process_loops(result, variables)
        
        # Process simple variable substitution
        result = self._substitute_variables(result, variables)
        
        return result
    
    def _process_conditionals(self, template: str, 
                             variables: Dict[str, Any]) -> str:
        """Process {% if condition %} blocks."""
        # Pattern: {% if variable %}...{% endif %}
        pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
        
        def replace_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            
            # Check if variable exists and is truthy
            if var_name in variables and variables[var_name]:
                return content
            return ""
        
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
    
    def _process_loops(self, template: str, 
                      variables: Dict[str, Any]) -> str:
        """Process {% for item in list %} blocks."""
        # Pattern: {% for item in list %}...{% endfor %}
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
        
        def replace_loop(match):
            item_name = match.group(1)
            list_name = match.group(2)
            content = match.group(3)
            
            if list_name not in variables:
                return ""
            
            items = variables[list_name]
            if not isinstance(items, (list, tuple)):
                return ""
            
            result = []
            for item in items:
                # Create temporary variables dict with loop item
                loop_vars = variables.copy()
                loop_vars[item_name] = item
                
                # Render content with loop variables
                rendered = self._substitute_variables(content, loop_vars)
                result.append(rendered)
            
            return ''.join(result)
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _substitute_variables(self, template: str, 
                             variables: Dict[str, Any]) -> str:
        """Substitute {variable} placeholders."""
        result = template
        
        for key, value in variables.items():
            # Handle different value types
            if isinstance(value, (list, tuple)):
                value_str = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value_str = str(value)
            else:
                value_str = str(value)
            
            # Replace {key} with value
            result = result.replace(f'{{{key}}}', value_str)
        
        return result
    
    def validate_template(self, template: str) -> tuple[bool, List[str]]:
        """
        Validate template syntax.
        
        Args:
            template: Template string
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for unmatched {% %}
        if_count = len(re.findall(r'\{%\s*if\s+', template))
        endif_count = len(re.findall(r'\{%\s*endif\s*%\}', template))
        if if_count != endif_count:
            errors.append(f"Unmatched if/endif: {if_count} if, {endif_count} endif")
        
        for_count = len(re.findall(r'\{%\s*for\s+', template))
        endfor_count = len(re.findall(r'\{%\s*endfor\s*%\}', template))
        if for_count != endfor_count:
            errors.append(f"Unmatched for/endfor: {for_count} for, {endfor_count} endfor")
        
        # Check for unmatched { }
        open_braces = template.count('{')
        close_braces = template.count('}')
        if open_braces != close_braces:
            errors.append(f"Unmatched braces: {open_braces} {{, {close_braces} }}")
        
        return (len(errors) == 0, errors)
    
    def extract_variables(self, template: str) -> List[str]:
        """
        Extract variable names from template.
        
        Args:
            template: Template string
            
        Returns:
            List of variable names
        """
        variables = set()
        
        # Extract {variable} style
        variables.update(re.findall(r'\{(\w+)\}', template))
        
        # Extract from {% if variable %}
        variables.update(re.findall(r'\{%\s*if\s+(\w+)\s*%\}', template))
        
        # Extract from {% for item in list %}
        variables.update(re.findall(r'\{%\s*for\s+\w+\s+in\s+(\w+)\s*%\}', template))
        
        return sorted(list(variables))
