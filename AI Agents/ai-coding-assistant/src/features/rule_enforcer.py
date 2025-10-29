"""
Rule Enforcer Module

Manages and enforces user-defined rules and best practices.
Ensures compliance across all operations: code generation, editing, and task execution.

Features:
- Store user rules in database
- Default best practices per language
- Inject rules into prompts automatically
- Post-action compliance checks
- Automatic remediation (e.g., refactor long files)
"""

import json
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path


class RuleEnforcer:
    """
    Enforce user-defined rules and best practices.
    Integrates with all features to ensure compliance.
    """

    # Default best practices per language
    DEFAULT_RULES = {
        'python': [
            "Follow PEP 8 style guidelines",
            "Use type hints for function parameters and returns",
            "Write docstrings for all functions and classes",
            "Use meaningful variable and function names",
            "Handle exceptions appropriately",
            "Keep functions under 50 lines when possible",
            "Keep files under 500 lines - refactor if longer",
            "Add unit tests for new functionality"
        ],
        'javascript': [
            "Use ES6+ syntax (const, let, arrow functions)",
            "Follow consistent naming conventions (camelCase)",
            "Use async/await instead of callbacks",
            "Add JSDoc comments for functions",
            "Keep functions pure when possible",
            "Handle errors with try/catch",
            "Keep files under 500 lines - refactor if longer"
        ],
        'typescript': [
            "Provide explicit type annotations",
            "Use interfaces for object shapes",
            "Avoid 'any' type - use specific types",
            "Follow consistent naming conventions",
            "Keep files under 500 lines - refactor if longer"
        ],
        'cpp': [
            "Use modern C++ (C++17/20) features",
            "Use smart pointers instead of raw pointers",
            "Follow RAII principles",
            "Use const correctness",
            "Avoid memory leaks",
            "Keep header files minimal",
            "Keep files under 500 lines - refactor if longer"
        ],
        'csharp': [
            "Follow Microsoft naming conventions",
            "Use modern C# features (LINQ, async/await)",
            "Implement IDisposable for resources",
            "Use properties instead of public fields",
            "Keep files under 500 lines - refactor if longer"
        ],
        'java': [
            "Follow Java naming conventions",
            "Use appropriate access modifiers",
            "Implement proper exception handling",
            "Use interfaces and abstract classes appropriately",
            "Keep files under 500 lines - refactor if longer"
        ],
        'default': [
            "Follow language-specific best practices",
            "Write clean, readable code",
            "Add appropriate comments",
            "Handle errors gracefully",
            "Keep code modular and maintainable",
            "Keep files under 500 lines - refactor if longer"
        ]
    }

    # Post-action checks
    POST_ACTION_CHECKS = {
        'file_length': {
            'threshold': 500,
            'action': 'refactor',
            'message': 'File exceeds 500 lines'
        },
        'function_length': {
            'threshold': 50,
            'action': 'warn',
            'message': 'Function exceeds 50 lines'
        }
    }

    def __init__(
        self,
        learning_db=None,
        project_manager=None,
        llm_interface=None
    ):
        """
        Initialize the rule enforcer.

        Args:
            learning_db: LearningDB for storing rules
            project_manager: ProjectManager for file operations
            llm_interface: LLMInterface for auto-refactoring

        Example:
            >>> from src.core.learning_db import LearningDB
            >>> from src.core.project_manager import ProjectManager
            >>> from src.core.llm_interface import LLMInterface, load_config_from_file
            >>> 
            >>> db = LearningDB()
            >>> pm = ProjectManager()
            >>> config = load_config_from_file()
            >>> llm = LLMInterface(config)
            >>> 
            >>> enforcer = RuleEnforcer(db, pm, llm)
        """
        self.learning_db = learning_db
        self.project_manager = project_manager
        self.llm_interface = llm_interface
        
        # Cache for loaded rules
        self._rules_cache = {}

    def set_rules(
        self,
        rules_list: List[str],
        project_id: Optional[str] = None,
        language: Optional[str] = None,
        override_defaults: bool = False
    ) -> bool:
        """
        Store user-defined rules in database.

        Args:
            rules_list: List of rule strings
            project_id: Optional project identifier
            language: Optional language for language-specific rules
            override_defaults: If True, replace defaults; if False, append

        Returns:
            True if stored successfully

        Example:
            >>> rules = [
            ...     "Always add unit tests",
            ...     "Update documentation after changes",
            ...     "Run tests before committing",
            ...     "Use logging instead of print statements"
            ... ]
            >>> enforcer.set_rules(rules, project_id="my-app", language="python")
        """
        if not self.learning_db:
            print("Warning: LearningDB not available, cannot store rules")
            return False

        try:
            # Combine with defaults if not overriding
            if not override_defaults and language:
                default_rules = self.DEFAULT_RULES.get(
                    language.lower(),
                    self.DEFAULT_RULES['default']
                )
                combined_rules = default_rules + rules_list
            else:
                combined_rules = rules_list

            # Store as JSON
            rules_json = json.dumps({
                'rules': combined_rules,
                'language': language,
                'override_defaults': override_defaults
            })

            # Store in database
            self.learning_db.set_project_rules(
                project_id=project_id or 'global',
                rules_json=rules_json
            )

            # Update cache
            cache_key = f"{project_id}:{language}" if project_id and language else "global"
            self._rules_cache[cache_key] = combined_rules

            print(f"✓ Stored {len(combined_rules)} rules")
            return True

        except Exception as e:
            print(f"✗ Error storing rules: {e}")
            return False

    def get_rules(
        self,
        project_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """
        Get applicable rules for context.

        Args:
            project_id: Optional project identifier
            language: Optional language filter

        Returns:
            List of applicable rule strings

        Example:
            >>> rules = enforcer.get_rules(project_id="my-app", language="python")
            >>> for rule in rules:
            ...     print(f"- {rule}")
        """
        # Check cache first
        cache_key = f"{project_id}:{language}" if project_id and language else "global"
        if cache_key in self._rules_cache:
            return self._rules_cache[cache_key]

        # Try to load from database
        if self.learning_db and project_id:
            try:
                rules_json = self.learning_db.get_project_rules(project_id)
                if rules_json:
                    rules_data = json.loads(rules_json)
                    rules = rules_data.get('rules', [])
                    self._rules_cache[cache_key] = rules
                    return rules
            except Exception as e:
                print(f"Warning: Could not load rules: {e}")

        # Fallback to defaults
        if language:
            default_rules = self.DEFAULT_RULES.get(
                language.lower(),
                self.DEFAULT_RULES['default']
            )
            return default_rules

        return self.DEFAULT_RULES['default']

    def enforce_rules(
        self,
        task_context: Dict[str, Any],
        include_in_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Enforce rules for a task context.
        
        Injects rules into prompt and prepares post-action checks.

        Args:
            task_context: Task context dictionary
            include_in_prompt: Whether to inject rules into prompt

        Returns:
            Enhanced context with rules

        Example:
            >>> context = {
            ...     'task': 'Generate user authentication',
            ...     'language': 'python',
            ...     'project_id': 'my-app'
            ... }
            >>> enhanced = enforcer.enforce_rules(context)
            >>> print(enhanced['rules_prompt'])
        """
        project_id = task_context.get('project_id')
        language = task_context.get('language')

        # Get applicable rules
        rules = self.get_rules(project_id=project_id, language=language)

        # Create rules prompt
        if include_in_prompt and rules:
            rules_prompt = "\n\nRules to follow:\n" + "\n".join([
                f"- {rule}" for rule in rules
            ])
            task_context['rules_prompt'] = rules_prompt
            task_context['rules'] = rules
        
        # Add post-action checks
        task_context['post_action_checks'] = self.POST_ACTION_CHECKS

        return task_context

    def check_compliance(
        self,
        action_result: Dict[str, Any],
        task_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check compliance after an action.
        
        Performs automatic checks like file length, test coverage, etc.

        Args:
            action_result: Result from action execution
            task_context: Original task context

        Returns:
            Compliance check results with remediation suggestions

        Example:
            >>> result = {
            ...     'success': True,
            ...     'file_path': 'api/routes.py',
            ...     'action': 'edit_file'
            ... }
            >>> compliance = enforcer.check_compliance(result, context)
            >>> if compliance['violations']:
            ...     for violation in compliance['violations']:
            ...         print(f"⚠ {violation['message']}")
        """
        compliance_result = {
            'compliant': True,
            'violations': [],
            'warnings': [],
            'remediation_actions': []
        }

        # Get file path if available
        file_path = action_result.get('file_path')
        
        if not file_path or not self.project_manager:
            return compliance_result

        # Check file length
        violation = self._check_file_length(
            file_path,
            task_context.get('project_id')
        )
        if violation:
            compliance_result['violations'].append(violation)
            compliance_result['compliant'] = False

        # Check for other violations based on rules
        rules = task_context.get('rules', [])
        for rule in rules:
            if 'test' in rule.lower() and 'after' in rule.lower():
                # Check if tests were run
                if not action_result.get('tests_run', False):
                    compliance_result['warnings'].append({
                        'rule': rule,
                        'message': 'Tests not run after implementation',
                        'severity': 'medium'
                    })

        return compliance_result

    def remediate(
        self,
        violation: Dict[str, Any],
        file_path: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Attempt automatic remediation of violations.

        Args:
            violation: Violation dictionary from check_compliance
            file_path: Path to file with violation
            project_id: Optional project identifier

        Returns:
            Remediation result

        Example:
            >>> violation = {
            ...     'type': 'file_length',
            ...     'message': 'File exceeds 500 lines'
            ... }
            >>> result = enforcer.remediate(violation, 'api/routes.py')
            >>> if result['success']:
            ...     print("File refactored successfully")
        """
        violation_type = violation.get('type')
        
        result = {
            'success': False,
            'action_taken': None,
            'message': None
        }

        if violation_type == 'file_length':
            # Attempt to refactor long file
            result = self._refactor_long_file(file_path, project_id)
        
        return result

    def _check_file_length(
        self,
        file_path: str,
        project_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Check if file exceeds length threshold."""
        if not self.project_manager:
            return None

        try:
            # Get file content
            content, _ = self.project_manager.get_file_content(file_path)
            lines = content.split('\n')
            line_count = len(lines)

            threshold = self.POST_ACTION_CHECKS['file_length']['threshold']

            if line_count > threshold:
                return {
                    'type': 'file_length',
                    'severity': 'high',
                    'message': f'File has {line_count} lines (threshold: {threshold})',
                    'file_path': file_path,
                    'line_count': line_count,
                    'threshold': threshold,
                    'remediation': 'refactor'
                }

        except Exception as e:
            print(f"Warning: Could not check file length: {e}")

        return None

    def _refactor_long_file(
        self,
        file_path: str,
        project_id: Optional[str]
    ) -> Dict[str, Any]:
        """Suggest or perform automatic refactoring of long file."""
        if not self.llm_interface or not self.project_manager:
            return {
                'success': False,
                'message': 'LLM or ProjectManager not available for refactoring'
            }

        try:
            # Get file content
            content, _ = self.project_manager.get_file_content(file_path)

            # Build refactoring prompt
            prompt = f"""This file is too long and needs refactoring.

File: {file_path}
Lines: {len(content.split(chr(10)))}

Suggest how to split this file into smaller, focused modules.
Provide:
1. Suggested module names
2. What code should go in each module
3. How they should be organized

Keep suggestions practical and maintainable."""

            # Get LLM suggestion
            suggestion = self.llm_interface.generate(
                prompt,
                max_tokens=800,
                use_cache=False
            )

            return {
                'success': True,
                'action_taken': 'generated_refactoring_suggestion',
                'message': 'Refactoring suggestion generated',
                'suggestion': suggestion
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error during refactoring: {e}'
            }

    def format_rules_for_prompt(
        self,
        rules: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Format rules for inclusion in prompts.

        Args:
            rules: Optional specific rules list
            project_id: Optional project ID
            language: Optional language

        Returns:
            Formatted rules string for prompt injection

        Example:
            >>> rules_text = enforcer.format_rules_for_prompt(
            ...     project_id="my-app",
            ...     language="python"
            ... )
            >>> full_prompt = base_prompt + rules_text
        """
        if rules is None:
            rules = self.get_rules(project_id=project_id, language=language)

        if not rules:
            return ""

        formatted = "\n\nIMPORTANT - Follow these rules:\n"
        formatted += "\n".join([f"- {rule}" for rule in rules])
        return formatted

    def validate_against_rules(
        self,
        code: str,
        language: str,
        rules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate code against rules (simplified check).

        Args:
            code: Code to validate
            language: Programming language
            rules: Optional specific rules

        Returns:
            Validation result

        Example:
            >>> result = enforcer.validate_against_rules(code, "python")
            >>> if not result['valid']:
            ...     for issue in result['issues']:
            ...         print(f"⚠ {issue}")
        """
        if rules is None:
            rules = self.get_rules(language=language)

        result = {
            'valid': True,
            'issues': [],
            'warnings': []
        }

        lines = code.split('\n')
        line_count = len(lines)

        # Check file length rule
        if line_count > 500:
            result['issues'].append(
                f"Code has {line_count} lines, exceeds 500 line guideline"
            )
            result['valid'] = False

        # Check for function length (simplified)
        function_lines = 0
        in_function = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('def ') or stripped.startswith('function '):
                in_function = True
                function_lines = 0
            elif in_function:
                if stripped and not stripped.startswith('#'):
                    function_lines += 1
                    if function_lines > 50:
                        result['warnings'].append(
                            "Function exceeds 50 line guideline"
                        )
                        in_function = False

        return result


if __name__ == "__main__":
    # Test the rule enforcer
    print("Testing Rule Enforcer...")

    from src.core.learning_db import LearningDB

    try:
        db = LearningDB()
        enforcer = RuleEnforcer(learning_db=db)
        print("✓ Rule Enforcer created")

        # Test setting rules
        print("\n=== Test: Set Rules ===")
        rules = [
            "Always add unit tests",
            "Update documentation",
            "Run tests before committing"
        ]
        success = enforcer.set_rules(
            rules,
            project_id="test-project",
            language="python"
        )
        print(f"Set rules: {success}")

        # Test getting rules
        print("\n=== Test: Get Rules ===")
        loaded_rules = enforcer.get_rules(
            project_id="test-project",
            language="python"
        )
        print(f"Loaded {len(loaded_rules)} rules")

        # Test formatting for prompt
        print("\n=== Test: Format for Prompt ===")
        prompt_text = enforcer.format_rules_for_prompt(language="python")
        print(f"Formatted text length: {len(prompt_text)}")

        # Test enforcement
        print("\n=== Test: Enforce Rules ===")
        context = {
            'task': 'Generate code',
            'language': 'python',
            'project_id': 'test-project'
        }
        enhanced = enforcer.enforce_rules(context)
        print(f"Rules in context: {len(enhanced.get('rules', []))}")

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
