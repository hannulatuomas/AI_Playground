# Bash Testing Preferences

## Overview

This document defines testing preferences and guidelines for Bash projects.

## Testing Frameworks

### Recommended Frameworks

- **bats**: Preferred for Bash testing
- **shunit2**: Preferred for Bash testing

### Framework Selection

Choose testing frameworks based on:
- Project complexity and size
- Team familiarity
- Integration requirements
- Performance needs

## Test Structure

### Directory Organization

```
project/
├── src/           # Source code
├── tests/         # Test files
│   ├── unit/      # Unit tests
│   ├── integration/  # Integration tests
│   └── e2e/       # End-to-end tests
└── ...
```

### Test File Naming

- Use descriptive names: `test_<feature>.test.ext`
- Mirror source structure in test directory
- Group related tests together

## Test Quality Standards

### Code Coverage

- **Minimum**: 70% code coverage
- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage for critical business logic

### Test Types

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete user workflows

### Test Practices

- **Arrange-Act-Assert** pattern
- One assertion per test (when practical)
- Clear test names describing what's being tested
- Independent tests (no dependencies between tests)
- Fast execution (unit tests < 1s each)

## Mocking and Fixtures

- Use mocks for external dependencies
- Create reusable fixtures for common test data
- Avoid over-mocking (test real interactions when feasible)

## Continuous Integration

- Run all tests on every commit
- Fail builds on test failures
- Track test coverage trends
- Generate test reports

## Performance Testing

- Benchmark critical operations
- Set performance thresholds
- Monitor test execution time
- Optimize slow tests

## Best Practices

1. Write tests before or alongside code (TDD/BDD)
2. Keep tests simple and readable
3. Test edge cases and error conditions
4. Maintain tests like production code
5. Review test code in code reviews

## Common Pitfalls to Avoid

- ❌ Tests that depend on execution order
- ❌ Tests that rely on external state
- ❌ Flaky tests (non-deterministic)
- ❌ Tests without clear purpose
- ❌ Overly complex test setups

## Tools and Utilities

- shellcheck

## Documentation

- Document complex test scenarios
- Explain test data choices
- Note any test environment requirements

---

**Last Updated**: 1760295524.931
