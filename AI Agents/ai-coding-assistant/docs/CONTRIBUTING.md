# Contributing to AI Coding Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, model used)
   - Error messages or logs

### Suggesting Features

1. Check if the feature has been suggested
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions focused and small
- Use meaningful variable names
- Add comments for complex logic

Example:
```python
def process_data(input_data: str, language: str) -> Dict[str, Any]:
    """
    Process input data for the specified language.
    
    Args:
        input_data: Raw input string
        language: Programming language identifier
        
    Returns:
        Dictionary with processed results
        
    Raises:
        ValueError: If language is not supported
    """
    # Implementation here
    pass
```

### Project Structure

- Core logic in `src/core/`
- Features in `src/features/`
- UI components in `src/ui/`
- Tests in `tests/`
- Documentation in `docs/`

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting
- Aim for >80% code coverage
- Use mocks for external dependencies

Run tests:
```bash
python tests/tests.py
```

### Documentation

- Update README.md for user-facing changes
- Update API.md for API changes
- Add docstrings to new functions/classes
- Include code examples where helpful

## Adding Support for New Languages

1. Update `src/features/lang_support.py`:
```python
'newlang': {
    'extensions': ['.ext'],
    'comment': '#',
    'common_keywords': ['keyword1', 'keyword2'],
    'frameworks': []
}
```

2. Update `src/core/prompt_engine.py`:
```python
'newlang': """You are a NewLang expert..."""
```

3. Add tests for the new language
4. Update documentation

## Adding New Features

1. Create module in appropriate directory
2. Write comprehensive tests
3. Document the feature
4. Update CLI/GUI if needed
5. Add to CHANGELOG.md

## Commit Message Guidelines

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for Rust language

- Add Rust language info to lang_support.py
- Add Rust-specific prompts
- Add tests for Rust detection
- Update documentation

Closes #123
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add entry to CHANGELOG.md
4. Request review from maintainers
5. Address review feedback
6. Wait for approval and merge

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up pre-commit hooks (optional):
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install
```

5. Make your changes and test

## Areas for Contribution

### High Priority
- Additional language support
- Improved error detection
- Better framework detection
- Performance optimizations
- Test coverage improvements

### Medium Priority
- UI enhancements
- Additional features (refactoring, code review)
- Documentation improvements
- Example projects

### Low Priority
- Code style improvements
- Minor bug fixes
- Typo corrections

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues for similar questions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to make AI Coding Assistant better!
