# Phase 2: Basic Features - Detailed Implementation Plan

**Timeline**: Weeks 3-5  
**Status**: Not Started  
**Priority**: High - Core functionality  
**Dependencies**: Phase 1 Complete

---

## Overview

Phase 2 builds the primary features that users will interact with: project management, code generation, and testing. These modules form the core workflow of the IDE.

---

## Goals

1. ✅ Enable automatic project scaffolding
2. ✅ Implement AI-powered code generation
3. ✅ Create automated testing and bug fixing
4. ✅ Support multiple languages and frameworks

---

## Task Breakdown

### 2.1 Project Management Module (4-5 days)

**Files to Create**:
- `src/modules/project_manager/__init__.py`
- `src/modules/project_manager/manager.py`
- `src/modules/project_manager/detector.py`
- `src/modules/project_manager/scaffolder.py`
- `src/modules/project_manager/templates/`
  - `python/` (Django, Flask, FastAPI, basic)
  - `javascript/` (React, Next.js, Express, basic)
  - `typescript/` (React, Next.js, Express)
  - `csharp/`
  - `cpp/`
  - `shell/`
- `tests/test_project_manager.py`

**Features to Implement**:

1. **Project Detection**
   ```python
   detect_project_type(path: str) -> ProjectInfo
   - Detect language (by file extensions)
   - Detect framework (by config files)
   - Detect dependencies
   - Detect project structure
   ```

2. **Project Scaffolding**
   ```python
   create_project(name: str, language: str, framework: str, path: str) -> Project
   - Generate folder structure
   - Create configuration files
   - Initialize version control
   - Set up dependencies
   - Create README and docs
   ```

3. **Project Maintenance**
   ```python
   maintain_project(project: Project) -> MaintenanceReport
   - Check for outdated dependencies
   - Validate structure
   - Suggest improvements
   - Fix common issues
   ```

**Template Examples**:

Python FastAPI:
```
project_name/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── models/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   └── test_api.py
├── requirements.txt
├── .gitignore
├── README.md
└── pyproject.toml
```

React + TypeScript:
```
project_name/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── utils/
│   ├── App.tsx
│   └── index.tsx
├── public/
├── tests/
├── package.json
├── tsconfig.json
├── .gitignore
└── README.md
```

**AI Prompts**:
```
Create templates for {language}/{framework} project.
Include:
- Standard folder structure
- Configuration files
- Sample code
- README template
- Best practices for {framework}

Follow modular design principles.
```

---

### 2.2 Code Generation Module (5-6 days)

**Files to Create**:
- `src/modules/code_generator/__init__.py`
- `src/modules/code_generator/generator.py`
- `src/modules/code_generator/analyzer.py`
- `src/modules/code_generator/editor.py`
- `src/modules/code_generator/validator.py`
- `tests/test_code_generator.py`

**Features to Implement**:

1. **Feature Request Analysis**
   ```python
   analyze_request(description: str, context: Context) -> FeaturePlan
   - Parse user request
   - Identify affected files
   - Check for existing code
   - Generate implementation plan
   ```

2. **Code Generation**
   ```python
   generate_code(plan: FeaturePlan) -> CodeArtifacts
   - Generate new classes/functions
   - Create necessary imports
   - Follow project style
   - Ensure modularity (<500 lines)
   - Add docstrings and comments
   ```

3. **Code Insertion**
   ```python
   insert_code(file: str, code: str, location: Location) -> bool
   - Determine insertion point
   - Maintain proper indentation
   - Update imports
   - Preserve existing code
   ```

4. **Duplicate Detection**
   ```python
   check_duplicates(code: str, project: Project) -> List[Match]
   - Search for similar code
   - Identify potential conflicts
   - Suggest refactoring
   ```

5. **Code Validation**
   ```python
   validate_code(code: str, language: str) -> ValidationResult
   - Syntax checking
   - Style validation
   - Best practices check
   ```

**Workflow**:
```
User Request → Analyze → Check Existing → Generate → Validate → Insert → Test
```

**AI Prompts**:
```
Analyze this feature request: "{description}"
Project context: {project_info}
Existing code: {relevant_code}

Generate a modular implementation plan including:
1. Files to create/modify
2. Classes/functions needed
3. Dependencies required
4. Test cases

Follow these rules: {project_rules}
```

---

### 2.3 Testing and Bug Fixing Module (5-6 days)

**Files to Create**:
- `src/modules/tester/__init__.py`
- `src/modules/tester/test_generator.py`
- `src/modules/tester/test_runner.py`
- `src/modules/tester/bug_fixer.py`
- `src/modules/tester/coverage_analyzer.py`
- `tests/test_tester.py`

**Features to Implement**:

1. **Test Generation**
   ```python
   generate_tests(file: str, functions: List[Function]) -> TestFile
   - Analyze function signatures
   - Generate unit tests
   - Create test fixtures
   - Add edge cases
   - Mock dependencies
   ```

2. **Test Execution**
   ```python
   run_tests(project: Project, test_files: List[str]) -> TestResults
   - Detect test framework
   - Execute tests
   - Collect results
   - Generate coverage report
   ```

3. **Bug Diagnosis**
   ```python
   diagnose_bug(error: Error, context: Context) -> Diagnosis
   - Analyze error message
   - Identify root cause
   - Search for similar issues
   - Generate hypothesis
   ```

4. **Bug Fixing**
   ```python
   fix_bug(diagnosis: Diagnosis) -> Fix
   - Generate fix
   - Apply changes
   - Re-run tests
   - Verify fix
   ```

**Test Framework Support**:
- Python: pytest, unittest
- JavaScript: Jest, Mocha
- TypeScript: Jest
- C#: xUnit, NUnit
- C++: Google Test

**AI Prompts for Test Generation**:
```
Generate comprehensive unit tests for this function:

{function_code}

Requirements:
- Test normal cases
- Test edge cases
- Test error conditions
- Use appropriate fixtures
- Mock external dependencies
- Aim for 100% coverage

Framework: {test_framework}
```

**AI Prompts for Bug Fixing**:
```
Debug this error:

Error: {error_message}
Stack trace: {stack_trace}
Code context: {relevant_code}

Steps:
1. Identify root cause
2. Explain the issue
3. Suggest fix
4. Consider side effects
5. Recommend tests to prevent regression
```

---

## Integration Points

### With Phase 1 Components:

1. **AI Backend**: All modules use AI for generation/analysis
2. **Database**: Store projects, code summaries, test results
3. **Config**: Language-specific settings
4. **CLI**: Commands for each module

### Module Interactions:

```
ProjectManager → creates structure
CodeGenerator → adds features
Tester → validates code
   ↓
All feed back to SelfImprover (Phase 4)
```

---

## Testing Strategy

1. **Unit Tests**:
   - Test each module independently
   - Mock AI backend responses
   - Test edge cases

2. **Integration Tests**:
   - Create sample projects
   - Generate code
   - Run tests
   - Verify results

3. **End-to-End Tests**:
   - Full workflow: new project → add feature → test → fix
   - Multiple languages
   - Complex scenarios

---

## Deliverables

- [ ] Project Manager with templates for all supported languages
- [ ] Code Generator that creates modular, valid code
- [ ] Test Generator supporting multiple frameworks
- [ ] Test Runner with coverage reports
- [ ] Bug Fixer with high success rate
- [ ] Integration with Phase 1 components
- [ ] Comprehensive tests (>80% coverage)
- [ ] Documentation and examples

---

## Success Criteria

✅ Can scaffold new projects in all supported languages  
✅ Generated code compiles/runs without errors  
✅ Generated tests achieve >80% coverage  
✅ Bug fixer successfully resolves common errors  
✅ All files stay under 500 lines  
✅ Code follows project rules  
✅ Integration tests pass

---

## Known Challenges

1. **Language-Specific Complexity**: Each language has unique patterns
   - Solution: Modular handlers, extensive templates

2. **Context Management**: Large codebases require context
   - Solution: Use Phase 4's Context Manager (simplified version for now)

3. **Test Quality**: AI-generated tests may miss edge cases
   - Solution: Human review, iterative improvement

---

## Next Steps

After Phase 2, proceed to Phase 3: Advanced Features
- Documentation Management
- Code Refactoring
- API/Database tools
