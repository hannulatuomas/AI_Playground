---
description: Comprehensive workflow for implementing a new feature
auto_execution_mode: 3
---

# Implement New Feature Workflow

This workflow guides you through implementing a new feature comprehensively, from analysis to testing to documentation.

## Prerequisites
- Feature request or description from user
- Access to project codebase

## Workflow Steps

### 1. Analyze Existing Codebase
**Goal:** Understand what we already have and how it's structured

- Read the project structure (CODEBASE_STRUCTURE.md if exists, or explore with list_dir/find_by_name)
- Check existing similar features or related code
- Review relevant files in src/, scripts/, tests/, docs/
- Identify patterns, conventions, and architectural decisions
- Note dependencies in requirements.txt
- Review user rules in .windsurf/rules/ for project-specific guidelines

### 2. Plan Implementation Comprehensively
**Goal:** Create a detailed, step-by-step implementation plan

- Break down the feature into main tasks
- For each main task, identify all sub-tasks
- Consider:
  - New files needed (src/, tests/, scripts/)
  - Existing files to modify
  - New dependencies required
  - Integration points with existing code
  - Edge cases and error handling
  - Testing requirements
  - Documentation updates needed
- Organize tasks in logical order (dependencies first)
- Estimate complexity for each task
- Make sure you follow project-rules.md and structure-rules.md

### 3. Document Tasks in TODO.md
**Goal:** Create a clear roadmap in TODO.md

- Open or create TODO.md in project root
- Add a new section for this feature with timestamp
- List all main tasks and sub-tasks with checkboxes
- Include brief descriptions for each task
- Mark dependencies between tasks
- Format example:
  ```markdown
  ## [Feature Name] - [Date]
  
  ### Main Task 1: [Description]
  - [ ] Sub-task 1.1: [Details]
  - [ ] Sub-task 1.2: [Details]
  
  ### Main Task 2: [Description]
  - [ ] Sub-task 2.1: [Details]
  ```

### 4. Implement Tasks One by One
**Goal:** Complete all implementation tasks systematically

// turbo
- Start with the first task in your plan
- For each task:
  - Create new files or modify existing ones
  - Follow project coding standards (check code-rules.md)
  - Keep files modular and under 500 lines when possible
  - Add proper error handling
  - Include docstrings and comments for complex logic
  - Follow existing patterns and conventions
  - Test the code mentally as you write
- Mark completed tasks in TODO.md as you finish them
- Commit logical chunks if needed (optional during development)
- Make sure you follow code-rules.md and project-rules.md

### 5. Update requirements.txt
**Goal:** Ensure all dependencies are documented

- Check if any new imports were added
- Verify each new import is in requirements.txt
- Add missing dependencies with appropriate version constraints
- Use format: `package>=min_version` or `package==exact_version`
- Sort alphabetically for maintainability
- Test that requirements.txt is complete

### 6. Create Comprehensive Tests
**Goal:** Ensure feature works correctly and prevent regressions

- Create test files in tests/ folder
- Follow naming convention: test_[feature_name].py
- Write tests for:
  - Happy path scenarios
  - Edge cases
  - Error conditions
  - Integration with existing features
- Use appropriate testing framework (pytest recommended)
- Aim for high code coverage
- Include docstrings explaining what each test validates
- Make tests independent and repeatable
- Make sure you follow structure-rules.md

### 7. Update Batch Scripts
**Goal:** Make setup, testing, and running seamless

- Always give me a scripts to easily run all the tests (with venv activated) and to easily run the program (with venv activated). Organize those in scripts/ folder and keep them up to date.

Update these scripts to include new features:

**scripts/setup.bat:**
- Ensure it installs all requirements.txt dependencies
- Add any new setup steps needed for the feature
- Test the setup process

**scripts/run_tests.bat:**
- Include commands to run new tests
- Ensure all test files are discovered
- Add any test-specific environment setup

**scripts/run.bat:**
- Update to include new feature functionality
- Add command-line options if needed
- Ensure all modules are accessible

### 8. Run Tests and Fix Issues
**Goal:** Achieve 100% passing tests

// turbo
- Run scripts/run_tests.bat to execute all tests
- For each failing test:
  - Read the error message carefully
  - Identify root cause (not just symptoms)
  - Fix the underlying issue
  - Re-run tests to verify fix
  - Ensure fix doesn't break other tests
- Continue until all tests pass
- If tests reveal design issues, refactor as needed
- Document any known limitations

### 9. Update All Documentation
**Goal:** Keep documentation synchronized with code
- Make sure you follow documentation-rules.md and structure-rules.md

Check and update these documents (per documentation-rules.md):

**Always update:**
- README.md - Add feature to features list, update usage if needed
- CHANGELOG.md - Add entry with date, version, and changes
- TODO.md - Mark feature tasks as complete, move to "Completed" section
- CODEBASE_STRUCTURE.md - Update structure if new directories/files added
- docs/API.md - Document any new APIs, functions, or classes
- docs/STATUS.md - Update project status and feature completion
- docs/USER_PREFERENCES.md - Add any new user-configurable options
- docs/AI_CONTEXT.md - Update context for AI about new capabilities
- docs/EXTENDING_GUIDE.md - Document how to extend the new feature
- docs/USER_GUIDE.md - Add user-facing documentation for the feature
- docs/QUICKSTART.md - Update if feature affects getting started

**Update if applicable:**
- Any feature-specific documentation
- Architecture diagrams or design docs
- Configuration examples

### 10. Create Summary Document
**Goal:** Document what was accomplished

- Create file: commits/[feature_name]_[date].md
- Include:
  - Feature overview and purpose
  - What was implemented (high-level)
  - Files created/modified (list with brief descriptions)
  - Key technical decisions made
  - Challenges encountered and solutions
  - Testing approach and results
  - Documentation updated
  - Next steps or future improvements (if any)
- Use clear markdown formatting
- Make sure you follow structure-rules.md


### 11. Generate Git Commit Script
**Goal:** Create comprehensive commit with proper message

- Create file: commits/[feature_name]_[date].bat
- Format:
  ```batch
  @echo off
  git add .
  git commit -m "[Feature] Feature Name
  
  Detailed description of what was implemented.
  
  Changes:
  - Created: [list new files]
  - Modified: [list modified files]
  - Added: [list new capabilities]
  
  Testing:
  - Added comprehensive tests in tests/
  - All tests passing
  
  Documentation:
  - Updated README.md, CHANGELOG.md, TODO.md
  - Updated all relevant docs/ files
  
  Dependencies:
  - Updated requirements.txt with [new packages if any]"
  ```
- Escape special characters properly for batch syntax
- Use proper multi-line format with ^ continuation if needed
- Make commit message detailed but concise

### 12. Final Verification
**Goal:** Ensure everything is complete and working

- Run scripts/setup.bat in a clean environment (if possible)
- Run scripts/run_tests.bat - verify all tests pass
- Run scripts/run.bat - verify feature works end-to-end
- Review all updated documentation for accuracy
- Check that commit script is syntactically correct
- Verify TODO.md reflects completion

## Success Criteria
- [ ] All planned tasks completed
- [ ] All tests passing (100%)
- [ ] requirements.txt up to date
- [ ] All batch scripts updated and working
- [ ] All documentation updated per documentation-rules.md
- [ ] Summary document created
- [ ] Git commit script created and ready to run
- [ ] Feature works as intended
- [ ] Code follows project standards and best practices

## Notes
- This workflow ensures comprehensive, production-ready feature implementation
- Don't skip steps - each is important for maintainability
- If you discover issues during implementation, update the plan and TODO.md
- Keep the user informed of progress at key milestones
- If a step fails repeatedly, ask for user guidance rather than continuing