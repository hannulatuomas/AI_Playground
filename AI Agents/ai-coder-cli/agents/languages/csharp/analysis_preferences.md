# C# Code Analysis Preferences

## Overview

This document defines code analysis preferences and standards for C# projects.

## Code Quality Standards

### Style Guide

Follow **Microsoft C# Coding Conventions**:
- Consistent naming conventions
- Proper indentation and formatting
- Clear and concise code structure
- Meaningful variable and function names

### Code Metrics

#### Acceptable Ranges

- **Lines of Code per File**: < 500 lines
- **Lines of Code per Function**: < 50 lines
- **Cyclomatic Complexity**: < 10 per function
- **Code Coverage**: > 80%
- **Maintainability Index**: > 70

## Complexity Analysis

### Cyclomatic Complexity

Target cyclomatic complexity thresholds:
- **1-10**: Simple, low risk
- **11-20**: Moderate complexity, medium risk
- **21-50**: Complex, high risk
- **50+**: Very complex, very high risk - refactor required

### Cognitive Complexity

Consider:
- Nesting depth
- Control flow complexity
- Logical operator chains
- Exception handling complexity

### Recommendations

- Break down complex functions
- Extract reusable components
- Use design patterns to simplify
- Add comments for complex logic

## Security Analysis

### Critical Checks

1. **Input Validation**: Validate all user inputs
2. **SQL Injection**: Use parameterized queries
3. **XSS Prevention**: Sanitize output
4. **Authentication**: Secure authentication mechanisms
5. **Authorization**: Proper access controls
6. **Cryptography**: Use strong encryption
7. **Dependencies**: No known vulnerabilities

### Security Tools

- Use dotnet for security analysis
- Use NuGet for security analysis

### Common Vulnerabilities

- Hardcoded credentials
- SQL injection
- Cross-site scripting (XSS)
- Command injection
- Path traversal
- Insecure deserialization

## Performance Analysis

### Performance Metrics

- Response time
- Throughput
- Resource utilization
- Memory footprint
- CPU usage

### Common Performance Issues

1. **Algorithmic Complexity**: Use efficient algorithms
2. **Database Queries**: Optimize queries, use indexing
3. **Caching**: Implement appropriate caching
4. **Concurrency**: Handle concurrent operations efficiently
5. **Resource Leaks**: Properly manage resources

### Optimization Guidelines

- Profile before optimizing
- Focus on bottlenecks
- Use appropriate data structures
- Minimize I/O operations
- Implement caching strategies

## Best Practices Checklist

### Code Organization

- [ ] Clear module structure
- [ ] Logical separation of concerns
- [ ] Consistent file organization
- [ ] No circular dependencies

### Documentation

- [ ] All public APIs documented
- [ ] Complex logic explained
- [ ] README with setup instructions
- [ ] Architecture documentation

### Error Handling

- [ ] Proper exception handling
- [ ] Meaningful error messages
- [ ] Logging for debugging
- [ ] Graceful failure handling

### Testing

- [ ] Unit tests for all functions
- [ ] Integration tests for workflows
- [ ] Test coverage > 80%
- [ ] Tests are maintainable

### Code Style

- [ ] Follows Microsoft C# Coding Conventions
- [ ] Consistent naming conventions
- [ ] Proper formatting
- [ ] No code smells

## Analysis Tools

### Recommended Tools

- **dotnet**
- **NuGet**

### Static Analysis

- Run linters before committing
- Use IDE integration for real-time feedback
- Configure rules to match project standards
- Address warnings, not just errors

### Dynamic Analysis

- Profile application performance
- Monitor memory usage
- Track resource leaks
- Analyze runtime behavior

## Code Review Checklist

### Functionality

- [ ] Code meets requirements
- [ ] Edge cases handled
- [ ] Error conditions handled
- [ ] Performance acceptable

### Quality

- [ ] Follows coding standards
- [ ] Well-documented
- [ ] Tests included
- [ ] No code duplication

### Security

- [ ] Input validation present
- [ ] No security vulnerabilities
- [ ] Credentials not hardcoded
- [ ] Proper error handling

### Maintainability

- [ ] Code is readable
- [ ] Appropriate abstractions
- [ ] Reasonable complexity
- [ ] Clear intent

## Continuous Improvement

### Regular Reviews

- Weekly code quality reports
- Monthly security scans
- Quarterly architecture reviews
- Annual tool evaluation

### Metrics Tracking

- Track code quality trends
- Monitor complexity growth
- Track technical debt
- Measure test coverage

### Team Practices

- Share analysis findings
- Learn from issues found
- Update standards as needed
- Celebrate improvements

---

**Last Updated**: 1760295524.931
