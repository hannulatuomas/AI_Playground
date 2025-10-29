"""
Code Generation Module

Generates code using AI backend.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from .analyzer import FeaturePlan, CodeContext


@dataclass
class CodeArtifact:
    """Generated code artifact."""
    file_path: str
    content: str
    language: str
    is_new_file: bool = True


class CodeGenerator:
    """Generates code based on feature plans."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize code generator.
        
        Args:
            ai_backend: AI backend for code generation
            project_rules: Project-specific coding rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
    
    def generate_code(self, plan: FeaturePlan, 
                     context: CodeContext) -> List[CodeArtifact]:
        """
        Generate code based on feature plan.
        
        Args:
            plan: Feature implementation plan
            context: Project context
            
        Returns:
            List of code artifacts to create/modify
        """
        artifacts = []
        
        # Generate new files
        for file_path in plan.new_files:
            artifact = self._generate_new_file(file_path, plan, context)
            if artifact:
                artifacts.append(artifact)
        
        # Generate modifications for existing files
        for file_path in plan.affected_files:
            artifact = self._generate_modifications(file_path, plan, context)
            if artifact:
                artifacts.append(artifact)
        
        return artifacts
    
    def _generate_new_file(self, file_path: str, plan: FeaturePlan,
                          context: CodeContext) -> Optional[CodeArtifact]:
        """Generate a new file."""
        prompt = self._build_generation_prompt(
            file_path=file_path,
            plan=plan,
            context=context,
            is_new=True
        )
        
        try:
            code = self.ai_backend.query(prompt, max_tokens=2000)
            
            # Clean up the response (remove markdown code blocks if present)
            code = self._clean_generated_code(code, context.language)
            
            return CodeArtifact(
                file_path=file_path,
                content=code,
                language=context.language,
                is_new_file=True
            )
        except Exception as e:
            print(f"Error generating {file_path}: {e}")
            return None
    
    def _generate_modifications(self, file_path: str, plan: FeaturePlan,
                               context: CodeContext) -> Optional[CodeArtifact]:
        """Generate modifications for existing file."""
        # Read existing file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_code = f.read()
        except Exception:
            return None
        
        prompt = self._build_modification_prompt(
            file_path=file_path,
            existing_code=existing_code,
            plan=plan,
            context=context
        )
        
        try:
            modified_code = self.ai_backend.query(prompt, max_tokens=2000)
            modified_code = self._clean_generated_code(modified_code, context.language)
            
            return CodeArtifact(
                file_path=file_path,
                content=modified_code,
                language=context.language,
                is_new_file=False
            )
        except Exception as e:
            print(f"Error modifying {file_path}: {e}")
            return None
    
    def _build_generation_prompt(self, file_path: str, plan: FeaturePlan,
                                context: CodeContext, is_new: bool) -> str:
        """Build prompt for code generation."""
        rules_text = '\n'.join(f'- {rule}' for rule in self.project_rules)
        
        prompt = f"""Generate {context.language} code for: {plan.description}

File: {file_path}
Language: {context.language}
Framework: {context.framework or 'None'}

Requirements:
- Implement: {', '.join(plan.classes_to_create + plan.functions_to_create)}
- Keep file under 500 lines (modular design)
- Include proper imports
- Add docstrings and comments
- Follow best practices for {context.language}
- Use type hints (if applicable)

Project Rules:
{rules_text if rules_text else '- Follow standard best practices'}

Existing Context:
- Classes in project: {', '.join(context.existing_classes[:5])}
- Functions in project: {', '.join(context.existing_functions[:5])}

Generate clean, production-ready code. Do not include explanations, only code.
"""
        
        return prompt
    
    def _build_modification_prompt(self, file_path: str, existing_code: str,
                                  plan: FeaturePlan, context: CodeContext) -> str:
        """Build prompt for modifying existing code."""
        rules_text = '\n'.join(f'- {rule}' for rule in self.project_rules)
        
        # Truncate existing code if too long
        if len(existing_code) > 2000:
            existing_code = existing_code[:2000] + "\n... (truncated)"
        
        prompt = f"""Modify this {context.language} code to: {plan.description}

File: {file_path}

Current Code:
```
{existing_code}
```

Requirements:
- Implement the requested changes
- Maintain existing functionality
- Keep file under 500 lines
- Update imports if needed
- Preserve code style
- Add/update docstrings

Project Rules:
{rules_text if rules_text else '- Follow standard best practices'}

Output the complete modified file. Do not include explanations, only code.
"""
        
        return prompt
    
    def _clean_generated_code(self, code: str, language: str) -> str:
        """Clean up generated code (remove markdown, etc.)."""
        # Remove markdown code blocks
        if '```' in code:
            # Extract code between ```language and ```
            import re
            pattern = r'```(?:\w+)?\n(.*?)```'
            matches = re.findall(pattern, code, re.DOTALL)
            if matches:
                code = matches[0]
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Ensure proper line endings
        code = code.replace('\r\n', '\n')
        
        return code
    
    def generate_class(self, class_name: str, description: str,
                      context: CodeContext) -> str:
        """
        Generate a single class.
        
        Args:
            class_name: Name of the class
            description: What the class should do
            context: Project context
            
        Returns:
            Generated class code
        """
        prompt = f"""Generate a {context.language} class named {class_name}.

Description: {description}

Requirements:
- Include docstrings
- Add type hints (if applicable)
- Follow best practices
- Keep under 200 lines
- Include necessary imports

Output only the class code, no explanations.
"""
        
        try:
            code = self.ai_backend.query(prompt, max_tokens=1000)
            return self._clean_generated_code(code, context.language)
        except Exception:
            return f"# Error generating class {class_name}"
    
    def generate_function(self, function_name: str, description: str,
                         context: CodeContext) -> str:
        """
        Generate a single function.
        
        Args:
            function_name: Name of the function
            description: What the function should do
            context: Project context
            
        Returns:
            Generated function code
        """
        prompt = f"""Generate a {context.language} function named {function_name}.

Description: {description}

Requirements:
- Include docstring
- Add type hints (if applicable)
- Handle errors appropriately
- Follow best practices
- Keep under 50 lines

Output only the function code, no explanations.
"""
        
        try:
            code = self.ai_backend.query(prompt, max_tokens=500)
            return self._clean_generated_code(code, context.language)
        except Exception:
            return f"# Error generating function {function_name}"
    
    def add_imports(self, code: str, imports: List[str], 
                   language: str) -> str:
        """
        Add imports to code.
        
        Args:
            code: Existing code
            imports: List of imports to add
            language: Programming language
            
        Returns:
            Code with imports added
        """
        if not imports:
            return code
        
        import_lines = []
        
        if language == 'python':
            for imp in imports:
                if '.' in imp:
                    # from x import y
                    parts = imp.rsplit('.', 1)
                    import_lines.append(f"from {parts[0]} import {parts[1]}")
                else:
                    import_lines.append(f"import {imp}")
        
        elif language in ['javascript', 'typescript']:
            for imp in imports:
                import_lines.append(f"import {imp};")
        
        elif language == 'csharp':
            for imp in imports:
                import_lines.append(f"using {imp};")
        
        # Add imports at the beginning
        import_block = '\n'.join(import_lines)
        return f"{import_block}\n\n{code}"
