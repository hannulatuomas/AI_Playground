# Project Context Awareness Guide

## Overview

This document describes the project context awareness feature added in v2.1, which enables all agents to understand project goals, architecture, and coding standards automatically.

## Quick Start

### For New Projects

1. **Initialize your project:**
   ```bash
   ai-console "Initialize a Python web API project"
   ```

2. **The project_init agent will:**
   - Ask clarifying questions about your project
   - Create the complete `.project_ai` structure
   - Set up project-specific rules and guidelines

3. **Customize your project preferences:**
   ```bash
   # Edit project-specific coding rules
   nano .project_ai/rules/project_preferences.md
   
   # Update project goals
   nano .project_ai/goals.md
   
   # Maintain your todo list
   nano .project_ai/todo.md
   ```

### For Existing Projects

1. **Add context awareness to an existing project:**
   ```bash
   cd /path/to/your/project
   ai-console "Initialize project context for this codebase"
   ```

2. **Fill in the context files:**
   - Add your project goals to `goals.md`
   - Document your architecture in `initial_plan.md`
   - Set project-specific rules in `rules/project_preferences.md`
   - Track tasks in `todo.md`

## .project_ai Structure

```
your-project/
├── .codebase_root                    # Project root marker
├── .project_ai/
│   ├── codebase_structure.md         # Project structure documentation
│   ├── rules/
│   │   └── project_preferences.md    # Project-specific rules (HIGHEST PRIORITY)
│   ├── initial_plan.md               # Architecture and design decisions
│   ├── goals.md                      # Project objectives and success criteria
│   └── todo.md                       # Task list and progress tracking
├── src/
│   └── ... (your code)
└── ... (other project files)
```

## 3-Level Rules Hierarchy

All agents follow a clear priority order for coding standards:

### Level 1: Project Preferences (Highest Priority)
- **File:** `<project>/.project_ai/rules/project_preferences.md`
- **Scope:** This specific project only
- **Use:** Project-specific rules that override all others
- **Example:** "Use 2-space indentation for this project"

### Level 2: User Preferences
- **File:** `agents/languages/<lang>/user_preferences.md`
- **Scope:** All your projects in this language
- **Use:** Your personal coding preferences
- **Example:** "I prefer 4-space indentation generally"

### Level 3: Best Practices (Baseline)
- **File:** `agents/languages/<lang>/best_practices.md`
- **Scope:** Language-level defaults
- **Use:** Community standards and conventions
- **Example:** "PEP 8 recommends 4-space indentation for Python"

**Resolution:** If your project requires 2 spaces, user prefers 4 spaces, and PEP 8 recommends 4 spaces, the agent will use **2 spaces** (project preference wins).

## Context Files Explained

### 1. .codebase_root
- Empty marker file at project root
- Helps agents quickly locate project root
- Works across nested directory structures

### 2. codebase_structure.md
- Documents project structure and organization
- Automatically maintained by agents
- Helps new agents understand the codebase layout

### 3. rules/project_preferences.md ⭐
- **This is your project's coding rulebook**
- Highest priority - overrides all other rules
- Customize for project-specific standards
- Examples:
  - Indentation and formatting
  - Naming conventions
  - Architecture patterns
  - Testing requirements
  - Documentation standards

### 4. initial_plan.md
- Initial project plan and architecture
- Technology stack decisions
- Key architectural choices
- Development phases
- Update as major decisions are made

### 5. goals.md
- What you want to achieve with this project
- Success criteria and measures
- Long-term vision
- Helps agents align their work with objectives

### 6. todo.md
- High/medium/low priority tasks
- Backlog items
- Completed tasks
- Helps agents understand current priorities

## How Agents Use Context

### 1. Automatic Context Loading

When any code-related agent executes:
```python
# Agent automatically:
1. Locates project root via .codebase_root
2. Loads all .project_ai files
3. Enriches LLM prompts with context
4. Follows project-specific rules
```

### 2. Context-Aware Code Generation

```python
# Agent generates code considering:
- Project goals (from goals.md)
- Architecture decisions (from initial_plan.md)
- Current priorities (from todo.md)
- Project structure (from codebase_structure.md)
- Project-specific rules (from rules/project_preferences.md)
```

### 3. Proactive Clarification

Agents ask questions when:
- Requirements are ambiguous
- Multiple approaches are possible
- Context is missing
- Project goals are unclear

## Benefits

### 1. Contextual Code Generation
Code aligns with your project's goals and architecture automatically.

### 2. Consistent Standards
Project-specific rules are always followed, even across multiple agents.

### 3. Better Decision Making
Agents understand priorities and trade-offs based on project context.

### 4. No Repetition
Agents remember project structure and patterns.

### 5. Seamless Collaboration
New agents automatically understand the project context.

### 6. Proactive Clarification
Agents ask questions instead of making assumptions.

## Best Practices

### 1. Keep Context Files Updated
- Update `goals.md` when objectives change
- Maintain `todo.md` as you complete tasks
- Document major decisions in `initial_plan.md`
- Keep `rules/project_preferences.md` current

### 2. Be Specific in project_preferences.md
Instead of:
```markdown
- Use good coding practices
```

Be specific:
```markdown
- Use 2-space indentation for JavaScript/TypeScript
- Maximum line length: 100 characters
- Use async/await instead of promises .then()
- All functions must have JSDoc comments
```

### 3. Align Goals with Tasks
Make sure `todo.md` tasks support the goals in `goals.md`.

### 4. Review Context Regularly
- Weekly review of `todo.md`
- Monthly review of `goals.md` and `initial_plan.md`
- Update `rules/project_preferences.md` as standards evolve

## Examples

### Example: Web API Project

**.project_ai/goals.md:**
```markdown
# Project Goals

1. **Build a RESTful API** for managing user accounts
2. **Achieve 90% test coverage** for core functionality
3. **Deploy to production** within 6 weeks
4. **Support 10,000 concurrent users** at launch
```

**.project_ai/rules/project_preferences.md:**
```markdown
# Project Preferences

### API Standards
- Use REST best practices
- Version all endpoints (e.g., /api/v1/users)
- Return consistent error responses

### Code Standards
- Use TypeScript strict mode
- All endpoints must have OpenAPI documentation
- Write integration tests for all endpoints
```

### Example: CLI Tool Project

**.project_ai/goals.md:**
```markdown
# Project Goals

1. **Create a command-line tool** for database migrations
2. **Support multiple databases** (PostgreSQL, MySQL, SQLite)
3. **Provide clear error messages** for users
4. **Include comprehensive help documentation**
```

**.project_ai/rules/project_preferences.md:**
```markdown
# Project Preferences

### CLI Standards
- Use argparse for argument parsing
- Provide --help for all commands
- Include --verbose for debugging

### Code Standards
- Python 3.8+ only
- Use type hints for all functions
- Follow Black formatting
- Maximum line length: 88 characters
```

## Troubleshooting

### Problem: Agent doesn't seem to be using project context

**Solution:**
1. Check if `.codebase_root` exists at project root
2. Verify `.project_ai` folder structure is complete
3. Check agent logs for context loading messages

### Problem: Agent is following wrong coding rules

**Solution:**
1. Check `rules/project_preferences.md` for conflicting rules
2. Verify the file is in the correct location
3. Remember: project_preferences.md overrides all other rules

### Problem: Context files not being created

**Solution:**
1. Use a `project_init` agent to initialize the project
2. Or manually create the structure using the template above

## Advanced Usage

### Custom Context Loading

For language-specific agents, you can customize context loading:

```python
from agents.utils.codebase_awareness import CodebaseAwarenessMixin

class MyAgent(Agent, CodebaseAwarenessMixin):
    def execute(self, task, context):
        # Initialize context
        self.ensure_codebase_awareness_initialized(context)
        
        # Load specific context files
        goals = self.load_project_goals(self.root_folder)
        preferences = self.load_project_preferences(self.root_folder)
        
        # Use in your agent logic
        ...
```

### Enriching Prompts

Code editor agents can enrich prompts with context:

```python
# Base prompt
base_prompt = "Generate a REST API endpoint for user registration"

# Enriched with project context
enriched_prompt = self._get_enriched_prompt_context(
    base_prompt,
    include_codebase=True,
    include_project_context=True
)

# Now includes:
# - Project goals
# - Current architecture
# - Coding standards
# - Current tasks
```

## See Also

- [README.md](README.md) - Main documentation
- [AI_CONTEXT.md](docs/architecture/AI_CONTEXT.md) - Detailed AI context information
- [EXTENDING_GUIDE.md](docs/guides/EXTENDING_GUIDE.md) - Adding new language support
- [DESIGN_PRINCIPLES.md](../architecture/DESIGN_PRINCIPLES.md) - Design philosophy

---

**Version:** 2.1  
**Last Updated:** October 12, 2025
