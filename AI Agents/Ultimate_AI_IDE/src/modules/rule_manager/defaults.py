"""
Default Rules

Collection of default coding rules for various languages.
"""

from typing import Dict, List


class DefaultRules:
    """Default coding rules."""
    
    @staticmethod
    def get_all_defaults() -> Dict[str, Dict[str, List[str]]]:
        """Get all default rules."""
        return {
            'python': {
                'style': [
                    "Follow PEP 8 style guide",
                    "Use type hints for function signatures",
                    "Maximum line length: 100 characters",
                    "Use f-strings for string formatting",
                    "Use descriptive variable names (no single letters except i, j, k in loops)",
                    "Use snake_case for functions and variables",
                    "Use PascalCase for classes"
                ],
                'architecture': [
                    "Keep functions under 50 lines",
                    "Keep files under 500 lines",
                    "One class per file (except nested classes)",
                    "Organize imports: standard library, third-party, local",
                    "Group related functions into classes or modules",
                    "Use meaningful file and module names"
                ],
                'best_practices': [
                    "Use list comprehensions for simple transformations",
                    "Use context managers (with statement) for resources",
                    "Prefer pathlib over os.path for file operations",
                    "Use enumerate() instead of range(len())",
                    "Use dict.get() with default values",
                    "Avoid mutable default arguments"
                ],
                'quality': [
                    "Add docstrings to all public functions and classes",
                    "Handle errors explicitly (no bare except)",
                    "Avoid global variables",
                    "Use constants for magic numbers",
                    "Write self-documenting code",
                    "Add comments only for complex logic"
                ],
                'testing': [
                    "Write unit tests for all public functions",
                    "Aim for >80% code coverage",
                    "Use descriptive test names",
                    "Follow AAA pattern: Arrange, Act, Assert",
                    "Mock external dependencies",
                    "Test edge cases and error conditions"
                ],
                'documentation': [
                    "Include module-level docstring",
                    "Document all public APIs",
                    "Use Google or NumPy docstring format",
                    "Include examples in docstrings for complex functions",
                    "Keep README.md up to date",
                    "Document breaking changes in CHANGELOG"
                ],
                'security': [
                    "Never hardcode credentials or API keys",
                    "Use environment variables for secrets",
                    "Validate all user inputs",
                    "Use parameterized queries for SQL",
                    "Keep dependencies up to date",
                    "Use secure random for cryptographic operations"
                ]
            },
            
            'javascript': {
                'style': [
                    "Use const/let, never var",
                    "Use === instead of ==",
                    "Use arrow functions for callbacks",
                    "Use template literals instead of string concatenation",
                    "Use camelCase for variables and functions",
                    "Use PascalCase for classes and components"
                ],
                'architecture': [
                    "Keep functions under 50 lines",
                    "Keep files under 500 lines",
                    "One component per file",
                    "Organize imports: React, third-party, local",
                    "Use named exports for utilities",
                    "Use default exports for components"
                ],
                'best_practices': [
                    "Use async/await instead of promise chains",
                    "Use destructuring for objects and arrays",
                    "Use spread operator for copying",
                    "Use optional chaining (?.) for nested properties",
                    "Use nullish coalescing (??) for default values",
                    "Avoid nested ternary operators"
                ],
                'quality': [
                    "Add JSDoc comments for public functions",
                    "Handle promise rejections",
                    "Avoid console.log in production",
                    "Use meaningful variable names",
                    "Avoid deeply nested code",
                    "Use early returns to reduce nesting"
                ],
                'testing': [
                    "Write unit tests with Jest or Vitest",
                    "Test components with React Testing Library",
                    "Mock API calls in tests",
                    "Test user interactions",
                    "Aim for >80% coverage",
                    "Use data-testid for test selectors"
                ]
            },
            
            'typescript': {
                'style': [
                    "Use explicit types for function parameters and returns",
                    "Avoid using 'any' type",
                    "Use interfaces for object shapes",
                    "Use type aliases for unions and complex types",
                    "Enable strict mode in tsconfig.json",
                    "Use readonly for immutable properties"
                ],
                'best_practices': [
                    "Use type guards for narrowing",
                    "Use generics for reusable components",
                    "Prefer unknown over any",
                    "Use utility types (Partial, Pick, Omit, etc.)",
                    "Define types close to usage",
                    "Use enums for fixed sets of values"
                ],
                'quality': [
                    "No implicit any",
                    "No unused variables",
                    "Strict null checks enabled",
                    "No non-null assertions unless necessary",
                    "Use type inference where obvious",
                    "Document complex types"
                ]
            },
            
            'react': {
                'style': [
                    "Use functional components with hooks",
                    "Use PascalCase for component names",
                    "Use camelCase for props",
                    "One component per file",
                    "Export component as default",
                    "Keep JSX readable with proper indentation"
                ],
                'best_practices': [
                    "Use useState for local state",
                    "Use useEffect for side effects",
                    "Use useCallback for event handlers",
                    "Use useMemo for expensive computations",
                    "Use custom hooks for reusable logic",
                    "Avoid prop drilling, use Context or state management"
                ],
                'quality': [
                    "Add PropTypes or TypeScript types",
                    "Use key prop for lists",
                    "Avoid inline function definitions in JSX",
                    "Use fragments to avoid extra divs",
                    "Handle loading and error states",
                    "Implement error boundaries"
                ]
            }
        }
    
    @staticmethod
    def get_rules_for_language(language: str) -> Dict[str, List[str]]:
        """Get rules for specific language."""
        all_rules = DefaultRules.get_all_defaults()
        return all_rules.get(language, {})
    
    @staticmethod
    def get_rules_for_category(language: str, category: str) -> List[str]:
        """Get rules for specific language and category."""
        lang_rules = DefaultRules.get_rules_for_language(language)
        return lang_rules.get(category, [])
