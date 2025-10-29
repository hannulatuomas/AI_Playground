"""
Default Prompts

Collection of default prompts for common tasks.
"""

from typing import Dict


class DefaultPrompts:
    """Default prompts for common tasks."""
    
    @staticmethod
    def get_all_defaults() -> Dict[str, Dict[str, str]]:
        """Get all default prompts."""
        return {
            # Code Generation
            'generate_function': {
                'template': '''Generate a {language} function that {description}.

Requirements:
- Function name: {function_name}
- Parameters: {parameters}
- Return type: {return_type}
- Include docstring
- Add type hints
- Follow best practices

Generate only the function code.''',
                'category': 'code_generation',
                'description': 'Generate a function'
            },
            
            'generate_class': {
                'template': '''Generate a {language} class for {purpose}.

Requirements:
- Class name: {class_name}
- Attributes: {attributes}
- Methods: {methods}
- Include docstrings
- Follow OOP best practices

Generate only the class code.''',
                'category': 'code_generation',
                'description': 'Generate a class'
            },
            
            # Testing
            'generate_tests': {
                'template': '''Generate unit tests for this {language} code:

```{language}
{code}
```

Requirements:
- Test framework: {test_framework}
- Cover main functionality
- Include edge cases
- Test error handling
- Follow testing best practices

Generate only the test code.''',
                'category': 'testing',
                'description': 'Generate unit tests'
            },
            
            # Documentation
            'generate_docstring': {
                'template': '''Generate a docstring for this {language} function:

```{language}
{code}
```

Include:
- Brief description
- Parameters with types
- Return value with type
- Raises (if applicable)
- Example usage (if helpful)

Follow {language} documentation conventions.''',
                'category': 'documentation',
                'description': 'Generate docstring'
            },
            
            'generate_readme': {
                'template': '''Generate a README.md for this project:

Project: {project_name}
Language: {language}
Description: {description}
Features: {features}

Include:
1. Project title and description
2. Installation instructions
3. Usage examples
4. Configuration
5. Contributing guidelines
6. License

Make it professional and clear.''',
                'category': 'documentation',
                'description': 'Generate README'
            },
            
            # Refactoring
            'refactor_code': {
                'template': '''Refactor this {language} code:

```{language}
{code}
```

Improvements needed:
{improvements}

Requirements:
- Maintain functionality
- Improve readability
- Reduce complexity
- Add type hints
- Follow best practices

Generate only the refactored code.''',
                'category': 'refactoring',
                'description': 'Refactor code'
            },
            
            # Debugging
            'debug_error': {
                'template': '''Debug this {language} error:

Code:
```{language}
{code}
```

Error:
{error}

Provide:
1. What caused the error
2. How to fix it
3. Corrected code

Be specific and clear.''',
                'category': 'debugging',
                'description': 'Debug error'
            },
            
            # API Development
            'generate_api_endpoint': {
                'template': '''Generate a {framework} API endpoint:

Method: {method}
Path: {path}
Description: {description}
Request body: {request_body}
Response: {response}

Include:
- Route handler
- Request validation
- Error handling
- Documentation

Generate only the endpoint code.''',
                'category': 'api',
                'description': 'Generate API endpoint'
            },
            
            # Database
            'generate_schema': {
                'template': '''Generate a {db_type} schema for:

Entities: {entities}
Relationships: {relationships}

Include:
- Table definitions
- Indexes
- Constraints
- Foreign keys

Follow {db_type} best practices.''',
                'category': 'database',
                'description': 'Generate database schema'
            },
            
            # Code Review
            'review_code': {
                'template': '''Review this {language} code:

```{language}
{code}
```

Provide:
1. Code quality assessment
2. Potential issues
3. Improvement suggestions
4. Best practice violations

Be constructive and specific.''',
                'category': 'review',
                'description': 'Review code'
            },
            
            # Optimization
            'optimize_code': {
                'template': '''Optimize this {language} code for {optimization_goal}:

```{language}
{code}
```

Focus on:
- {optimization_goal}
- Maintain correctness
- Improve efficiency
- Keep readable

Generate optimized code with explanation.''',
                'category': 'optimization',
                'description': 'Optimize code'
            }
        }
    
    @staticmethod
    def get_prompt(name: str) -> Dict[str, str]:
        """Get a specific default prompt."""
        prompts = DefaultPrompts.get_all_defaults()
        return prompts.get(name, {})
    
    @staticmethod
    def get_by_category(category: str) -> Dict[str, Dict[str, str]]:
        """Get all prompts in a category."""
        all_prompts = DefaultPrompts.get_all_defaults()
        return {
            name: prompt 
            for name, prompt in all_prompts.items() 
            if prompt.get('category') == category
        }
