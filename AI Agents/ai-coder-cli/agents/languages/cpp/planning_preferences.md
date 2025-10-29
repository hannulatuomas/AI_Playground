# C++ Planning Preferences

## Overview

This document defines project planning preferences and guidelines for C++ projects.

## Project Structure

### Standard Directory Layout

```
project/
├── src/              # Source code
├── tests/            # Test files
├── docs/             # Documentation
├── config/           # Configuration files
├── scripts/          # Build and utility scripts
└── README.md         # Project documentation
```

## Technology Stack Selection

### Core Considerations

1. **Project Requirements**: Match technology to project needs
2. **Team Expertise**: Consider team familiarity
3. **Community Support**: Choose well-supported libraries
4. **Maintenance**: Consider long-term maintainability
5. **Performance**: Meet performance requirements

### Recommended Tools

- **CMake**: For project management and dependencies
- **Make**: For project management and dependencies
- **vcpkg**: For project management and dependencies

## Architecture Patterns

### Design Principles

- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It

### Common Patterns

- **MVC/MVVM**: For UI applications
- **Repository Pattern**: For data access
- **Factory Pattern**: For object creation
- **Strategy Pattern**: For interchangeable algorithms
- **Observer Pattern**: For event handling

## Project Phases

### Phase 1: Requirements Analysis

- Define project goals and objectives
- Identify stakeholders and users
- Document functional requirements
- Document non-functional requirements
- Define success criteria

### Phase 2: Design

- Create high-level architecture
- Define module boundaries
- Design data models
- Plan API interfaces
- Create wireframes/mockups (if applicable)

### Phase 3: Implementation Planning

- Break down into user stories/tasks
- Estimate effort and timelines
- Identify dependencies
- Plan sprints/iterations
- Assign responsibilities

### Phase 4: Development

- Follow coding standards (Google C++ Style Guide)
- Write tests alongside code
- Conduct code reviews
- Document as you go
- Integrate continuously

### Phase 5: Testing

- Execute test plan
- Fix defects
- Verify requirements met
- Performance testing
- Security testing

### Phase 6: Deployment

- Prepare deployment environment
- Create deployment scripts
- Plan rollback strategy
- Document deployment process
- Monitor after deployment

## Dependency Management

### Guidelines

- Minimize dependencies
- Use well-maintained libraries
- Pin dependency versions
- Regular security updates
- Document dependency choices

## Documentation Requirements

### Code Documentation

- Module/class docstrings
- Function/method documentation
- Complex algorithm explanations
- API documentation

### Project Documentation

- README with setup instructions
- Architecture overview
- Deployment guide
- User guide (if applicable)
- API reference

## Version Control Strategy

### Branching Model

- **main/master**: Production-ready code
- **develop**: Integration branch
- **feature/**: Feature branches
- **bugfix/**: Bug fix branches
- **hotfix/**: Emergency fixes

### Commit Practices

- Atomic commits
- Clear commit messages
- Reference issues/tickets
- Keep history clean

## Quality Assurance

### Code Quality

- Follow Google C++ Style Guide
- Use linters and formatters
- Maintain consistent style
- Regular refactoring

### Review Process

- Mandatory code reviews
- Automated checks before merge
- Documentation review
- Test coverage verification

## Risk Management

### Common Risks

- Scope creep
- Technical debt accumulation
- Dependency vulnerabilities
- Performance bottlenecks
- Team knowledge gaps

### Mitigation Strategies

- Regular risk assessments
- Incremental development
- Continuous integration
- Knowledge sharing
- Code reviews

## Best Practices

1. Plan for testability from the start
2. Design for maintainability
3. Document architectural decisions
4. Regular architecture reviews
5. Keep dependencies up-to-date
6. Plan for scalability
7. Security by design
8. Monitor and measure

---

**Last Updated**: 1760295524.931
