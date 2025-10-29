# Saved Prompts and Snippets Guide

**Version:** 2.4.1  
**Last Updated:** October 14, 2025

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Storage System](#storage-system)
- [Getting Started](#getting-started)
- [Command Reference](#command-reference)
- [Variable Substitution](#variable-substitution)
- [Common Use Cases](#common-use-cases)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Import/Export](#importexport)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Saved Prompts and Snippets** feature allows you to save, manage, and reuse prompts and code snippets efficiently across different sessions and projects. This powerful feature helps you:

- Build a library of reusable prompts
- Share prompts across projects or keep them project-specific
- Use templates with variable substitution
- Organize prompts with tags
- Track usage statistics
- Import/export prompt collections

---

## Key Features

### 1. **Dual Storage Scopes**

- **Global Prompts**: Available across all projects, stored in `~/.ai-agent-console/prompts/`
- **Project Prompts**: Specific to a project, stored in `.project/prompts/` within the project directory

### 2. **Two Types of Content**

- **Prompts**: Full prompts for AI interactions
- **Snippets**: Reusable code or text snippets

### 3. **Rich Metadata**

- Name and description
- Tags for categorization
- Usage tracking
- Creation and modification timestamps
- Variable detection

### 4. **Variable Substitution**

Use `{{variable_name}}` syntax in your prompts for dynamic content substitution.

### 5. **Search and Filter**

Filter prompts by:
- Scope (global/project)
- Type (prompt/snippet)
- Tags
- Search terms

---

## Storage System

### Global Storage

**Location:** `~/.ai-agent-console/prompts/prompts.json`

Global prompts are accessible from any project and persist across sessions.

```
~/.ai-agent-console/
└── prompts/
    └── prompts.json
```

### Project Storage

**Location:** `<project-dir>/.project/prompts/prompts.json`

Project prompts are specific to a project and only accessible when that project is active.

```
my-project/
└── .project/
    └── prompts/
        └── prompts.json
```

### Storage Format

Prompts are stored in JSON format with the following structure:

```json
{
  "version": "1.0",
  "updated_at": "2025-10-14T10:30:00",
  "prompts": [
    {
      "prompt_id": "uuid",
      "name": "code-review",
      "description": "Template for code review",
      "content": "Review the following code...",
      "prompt_type": "prompt",
      "scope": "global",
      "tags": ["code", "review"],
      "variables": ["language", "focus_area"],
      "created_at": "2025-10-14T10:00:00",
      "updated_at": "2025-10-14T10:30:00",
      "usage_count": 5,
      "metadata": {}
    }
  ]
}
```

---

## Getting Started

### Saving Your First Prompt

```bash
# Save a simple global prompt
python main.py prompt-save "code-review" -c "Review the following code for best practices and suggest improvements."

# Save a project-scoped prompt
python main.py prompt-save "bug-fix-template" \
  -c "Analyze the bug and provide a fix" \
  --scope project \
  --tags "debugging,template"
```

### Listing Prompts

```bash
# List all prompts
python main.py prompt-list

# List global prompts only
python main.py prompt-list --scope global

# List prompts with specific tags
python main.py prompt-list --tags "python,code"
```

### Using a Prompt

```bash
# Display a prompt
python main.py prompt-use "code-review"

# Save to file
python main.py prompt-use "code-review" -o review.txt

# Copy to clipboard (requires pyperclip)
python main.py prompt-use "code-review" --copy
```

---

## Command Reference

### `prompt-save` - Save a New Prompt

Save a new prompt or snippet to the system.

**Syntax:**
```bash
python main.py prompt-save <name> [OPTIONS]
```

**Options:**
- `--content, -c <text>` - Prompt content (inline)
- `--file, -f <path>` - Read content from file
- `--description, -d <text>` - Description of the prompt
- `--type, -t <type>` - Type: 'prompt' or 'snippet' (default: prompt)
- `--scope, -s <scope>` - Scope: 'global' or 'project' (default: global)
- `--tags <tags>` - Comma-separated tags
- `--interactive, -i` - Interactive mode

**Examples:**
```bash
# Save inline content
python main.py prompt-save "code-review" -c "Review the code"

# Save from file
python main.py prompt-save "template" -f template.txt

# Save with metadata
python main.py prompt-save "debug-prompt" \
  -c "Debug the following issue" \
  -d "Template for debugging" \
  --tags "debugging,template" \
  --scope project

# Interactive mode
python main.py prompt-save "my-prompt" --interactive
```

---

### `prompt-list` - List Saved Prompts

List all saved prompts with optional filtering.

**Syntax:**
```bash
python main.py prompt-list [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Filter by scope: 'global' or 'project'
- `--type, -t <type>` - Filter by type: 'prompt' or 'snippet'
- `--tags <tags>` - Filter by tags (comma-separated)
- `--search <term>` - Search in name, description, or content
- `--verbose, -v` - Show detailed information (usage count, dates)

**Examples:**
```bash
# List all prompts
python main.py prompt-list

# List global prompts
python main.py prompt-list --scope global

# List snippets with tags
python main.py prompt-list --type snippet --tags "python,utils"

# Search prompts
python main.py prompt-list --search "code review"

# Verbose listing
python main.py prompt-list -v
```

---

### `prompt-view` - View Prompt Details

View detailed information about a specific prompt.

**Syntax:**
```bash
python main.py prompt-view <name> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Scope: 'global' or 'project'

**Examples:**
```bash
# View a global prompt
python main.py prompt-view "code-review"

# View a project prompt
python main.py prompt-view "template" --scope project
```

---

### `prompt-edit` - Edit an Existing Prompt

Edit an existing prompt's content or metadata.

**Syntax:**
```bash
python main.py prompt-edit <name> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Scope: 'global' or 'project'
- `--name <new-name>` - New name for the prompt
- `--content, -c <text>` - New content
- `--file, -f <path>` - Read new content from file
- `--description, -d <text>` - New description
- `--tags <tags>` - New tags (comma-separated)

**Examples:**
```bash
# Update description
python main.py prompt-edit "code-review" -d "Updated description"

# Update content from file
python main.py prompt-edit "template" -f new_template.txt

# Update tags
python main.py prompt-edit "my-prompt" --tags "python,code,review"

# Rename prompt
python main.py prompt-edit "old-name" --name "new-name"
```

---

### `prompt-delete` - Delete a Prompt

Delete a saved prompt.

**Syntax:**
```bash
python main.py prompt-delete <name> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Scope: 'global' or 'project'
- `--yes, -y` - Skip confirmation prompt

**Examples:**
```bash
# Delete with confirmation
python main.py prompt-delete "old-prompt"

# Delete without confirmation
python main.py prompt-delete "old-prompt" -y

# Delete project prompt
python main.py prompt-delete "template" --scope project -y
```

---

### `prompt-use` - Use a Saved Prompt

Use a saved prompt with optional variable substitution.

**Syntax:**
```bash
python main.py prompt-use <name> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Scope: 'global' or 'project'
- `--vars <variables>` - Variables in key=value format (comma-separated)
- `--output, -o <path>` - Save to file
- `--copy, -c` - Copy to clipboard (requires pyperclip)

**Examples:**
```bash
# Display prompt
python main.py prompt-use "code-review"

# With variable substitution
python main.py prompt-use "template" --vars "project_name=MyApp,version=1.0"

# Save to file
python main.py prompt-use "template" -o output.txt

# Copy to clipboard
python main.py prompt-use "code-review" --copy
```

---

### `prompt-stats` - View Statistics

Show statistics about saved prompts.

**Syntax:**
```bash
python main.py prompt-stats
```

**Output:**
- Total number of prompts
- Breakdown by scope (global/project)
- Breakdown by type (prompt/snippet)
- Available tags
- Most used prompts

**Example:**
```bash
python main.py prompt-stats
```

---

### `prompt-export` - Export Prompts

Export prompts to a JSON file.

**Syntax:**
```bash
python main.py prompt-export <output-file> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Filter by scope
- `--tags <tags>` - Filter by tags (comma-separated)

**Examples:**
```bash
# Export all prompts
python main.py prompt-export all-prompts.json

# Export only global prompts
python main.py prompt-export global-prompts.json --scope global

# Export prompts with specific tags
python main.py prompt-export python-prompts.json --tags "python"
```

---

### `prompt-import` - Import Prompts

Import prompts from a JSON file.

**Syntax:**
```bash
python main.py prompt-import <input-file> [OPTIONS]
```

**Options:**
- `--scope, -s <scope>` - Override scope for all imported prompts
- `--overwrite` - Overwrite existing prompts with same name

**Examples:**
```bash
# Import prompts
python main.py prompt-import prompts.json

# Import as global prompts
python main.py prompt-import prompts.json --scope global

# Import and overwrite existing
python main.py prompt-import prompts.json --overwrite
```

---

## Variable Substitution

### Defining Variables

Use the `{{variable_name}}` syntax in your prompt content:

```text
Review the following {{language}} code for {{focus_area}}.
Pay special attention to {{additional_concerns}}.
```

### Using Variables

When you save a prompt with variables, they are automatically detected:

```bash
python main.py prompt-save "code-review-template" \
  -c "Review the following {{language}} code for {{focus_area}}."
# Output: ℹ Variables detected: language, focus_area
```

### Substituting Variables

Provide variable values when using the prompt:

```bash
python main.py prompt-use "code-review-template" \
  --vars "language=Python,focus_area=performance"
```

**Result:**
```text
Review the following Python code for performance.
```

### Common Variable Patterns

- `{{project_name}}` - Project name
- `{{file_path}}` - File path
- `{{language}}` - Programming language
- `{{framework}}` - Framework name
- `{{version}}` - Version number
- `{{author}}` - Author name
- `{{date}}` - Date

---

## Common Use Cases

### 1. Code Review Template

```bash
# Save the template
python main.py prompt-save "code-review" \
  -c "Review the following {{language}} code:

1. Check for best practices
2. Identify potential bugs
3. Suggest performance improvements
4. Verify error handling

Focus areas: {{focus_areas}}" \
  --tags "code-review,template"

# Use the template
python main.py prompt-use "code-review" \
  --vars "language=Python,focus_areas=error handling and performance"
```

---

### 2. Bug Report Template

```bash
# Save the template
python main.py prompt-save "bug-report" \
  -c "## Bug Report

**Project:** {{project_name}}
**Component:** {{component}}
**Severity:** {{severity}}

**Description:**
{{description}}

**Steps to Reproduce:**
1. {{step1}}
2. {{step2}}
3. {{step3}}

**Expected Behavior:**
{{expected}}

**Actual Behavior:**
{{actual}}" \
  --type snippet \
  --tags "bug,template"
```

---

### 3. Documentation Prompts

```bash
# API documentation generator
python main.py prompt-save "api-docs" \
  -c "Generate API documentation for the following endpoint:
- Endpoint: {{endpoint}}
- Method: {{method}}
- Parameters: {{parameters}}
- Response format: {{response_format}}" \
  --tags "documentation,api"

# Function documentation
python main.py prompt-save "function-docs" \
  -c "Generate detailed documentation for this {{language}} function including:
- Purpose
- Parameters with types
- Return value
- Examples
- Edge cases" \
  --tags "documentation,code"
```

---

### 4. Testing Prompts

```bash
# Unit test generator
python main.py prompt-save "unit-tests" \
  -c "Generate comprehensive unit tests for the following {{language}} code:
- Test normal cases
- Test edge cases
- Test error conditions
- Use {{testing_framework}} framework" \
  --tags "testing,unit-tests"

# Test case template
python main.py prompt-save "test-case" \
  -c "## Test Case: {{test_name}}

**Objective:** {{objective}}
**Prerequisites:** {{prerequisites}}
**Test Steps:**
1. {{step1}}
2. {{step2}}
3. {{step3}}
**Expected Result:** {{expected_result}}
**Actual Result:** {{actual_result}}
**Status:** {{status}}" \
  --type snippet \
  --tags "testing,template"
```

---

### 5. Project-Specific Snippets

```bash
# Create project and save project-specific prompts
python main.py create-project "MyApp" -d "My application project"

# Save project-specific prompts
python main.py prompt-save "deploy-checklist" \
  -c "Deployment checklist for MyApp:
1. Run tests
2. Update version
3. Build artifacts
4. Deploy to staging
5. Smoke tests
6. Deploy to production" \
  --scope project \
  --tags "deployment,checklist"
```

---

### 6. Code Refactoring Prompts

```bash
python main.py prompt-save "refactor" \
  -c "Refactor the following {{language}} code:
- Apply {{design_pattern}} pattern
- Improve readability
- Reduce complexity
- Add error handling
- Follow {{style_guide}} style guide" \
  --tags "refactoring,code-quality"
```

---

## Best Practices

### 1. **Naming Conventions**

- Use descriptive, lowercase names with hyphens
- Examples: `code-review`, `bug-fix-template`, `api-docs-generator`

### 2. **Organize with Tags**

Use consistent tags for easy filtering:
- Language: `python`, `javascript`, `java`
- Purpose: `debugging`, `testing`, `documentation`
- Type: `template`, `checklist`, `example`

### 3. **Use Global vs. Project Scope Wisely**

- **Global**: Generic, reusable prompts applicable to any project
- **Project**: Project-specific prompts with project context

### 4. **Leverage Variables**

Use variables for:
- Project-specific information
- Dynamic content
- Reusable templates

### 5. **Document Your Prompts**

Add clear descriptions to help you remember the purpose and usage.

### 6. **Regular Maintenance**

- Review and update prompts periodically
- Remove unused prompts
- Check usage statistics to identify valuable prompts

### 7. **Share Prompts**

Export and share useful prompts with your team:
```bash
python main.py prompt-export team-prompts.json --tags "team-shared"
```

---

## Examples

### Example 1: Daily Standup Template

```bash
python main.py prompt-save "daily-standup" \
  -c "Daily Standup - {{date}}

**Yesterday:**
- {{yesterday_work}}

**Today:**
- {{today_plan}}

**Blockers:**
- {{blockers}}" \
  --type snippet \
  --tags "team,meeting"
```

### Example 2: Git Commit Message Template

```bash
python main.py prompt-save "commit-message" \
  -c "{{type}}: {{subject}}

{{body}}

Fixes: {{issue_number}}
Breaking changes: {{breaking_changes}}" \
  --type snippet \
  --tags "git,template"
```

### Example 3: Security Review Prompt

```bash
python main.py prompt-save "security-review" \
  -c "Perform a security review of the following code:

1. Check for SQL injection vulnerabilities
2. Verify input validation
3. Check authentication/authorization
4. Review data encryption
5. Identify security best practices violations

Focus on: {{security_focus}}" \
  --tags "security,code-review"
```

### Example 4: Performance Analysis

```bash
python main.py prompt-save "performance-analysis" \
  -c "Analyze the performance of the following {{language}} code:

1. Identify performance bottlenecks
2. Suggest optimization strategies
3. Analyze time complexity
4. Analyze space complexity
5. Recommend profiling tools

Target: {{performance_target}}" \
  --tags "performance,analysis"
```

---

## Import/Export

### Exporting Prompts

#### Export All Prompts
```bash
python main.py prompt-export all-prompts.json
```

#### Export by Scope
```bash
python main.py prompt-export global-prompts.json --scope global
python main.py prompt-export project-prompts.json --scope project
```

#### Export by Tags
```bash
python main.py prompt-export python-prompts.json --tags "python"
python main.py prompt-export templates.json --tags "template"
```

### Importing Prompts

#### Basic Import
```bash
python main.py prompt-import prompts.json
```

#### Import with Scope Override
```bash
# Import all prompts as global
python main.py prompt-import prompts.json --scope global
```

#### Import with Overwrite
```bash
# Overwrite existing prompts
python main.py prompt-import prompts.json --overwrite
```

### Sharing Prompts

1. **Export your prompts:**
   ```bash
   python main.py prompt-export my-prompts.json --tags "shared"
   ```

2. **Share the JSON file** with team members

3. **Team members import:**
   ```bash
   python main.py prompt-import my-prompts.json --scope global
   ```

---

## Troubleshooting

### Prompt Not Found

**Problem:** `Prompt 'my-prompt' not found`

**Solutions:**
- Check if the prompt exists: `python main.py prompt-list`
- Verify the scope: try adding `--scope global` or `--scope project`
- Check spelling of the prompt name

### Missing Variables Error

**Problem:** `Missing required variables: project_name, version`

**Solution:** Provide all required variables:
```bash
python main.py prompt-use "template" --vars "project_name=MyApp,version=1.0"
```

### Cannot Save Project-Scoped Prompt

**Problem:** `Cannot save project-scoped prompt: no active project`

**Solution:** Create or switch to a project first:
```bash
python main.py create-project "MyProject"
# OR
python main.py switch-project "MyProject"
```

### Prompt Already Exists

**Problem:** `Prompt with name 'code-review' already exists in global scope`

**Solutions:**
- Use a different name
- Update the existing prompt: `python main.py prompt-edit "code-review"`
- Delete the old prompt first: `python main.py prompt-delete "code-review" -y`

### Storage Issues

**Problem:** Prompts not persisting across sessions

**Solution:** Check storage directory permissions:
```bash
# Global storage
ls -la ~/.ai-agent-console/prompts/

# Project storage (when a project is active)
ls -la .project/prompts/
```

Ensure the directories are writable.

---

## Advanced Tips

### 1. Prompt Chaining

Use prompts as building blocks:
```bash
# Save base prompt
python main.py prompt-save "base-review" -c "Review the code for: {{criteria}}"

# Create specialized prompts referencing the base
python main.py prompt-use "base-review" --vars "criteria=security vulnerabilities" -o security-review.txt
```

### 2. Interactive Workflow

Use interactive mode for complex prompts:
```bash
python main.py prompt-save "complex-prompt" --interactive
```

### 3. Version Control for Prompts

Export prompts regularly and version control them:
```bash
python main.py prompt-export prompts-v1.0.json
git add prompts-v1.0.json
git commit -m "Add prompt library v1.0"
```

### 4. Prompt Templates Library

Build a library of reusable templates:
```bash
# Create templates directory
mkdir -p ~/.ai-agent-console/prompt-templates/

# Export by category
python main.py prompt-export ~/.ai-agent-console/prompt-templates/code-review.json --tags "code-review"
python main.py prompt-export ~/.ai-agent-console/prompt-templates/testing.json --tags "testing"
python main.py prompt-export ~/.ai-agent-console/prompt-templates/documentation.json --tags "documentation"
```

---

## Next Steps

1. **Create your first prompt** with the quick start guide
2. **Explore examples** to understand common patterns
3. **Build your prompt library** tailored to your workflow
4. **Share prompts** with your team
5. **Track usage** with `prompt-stats` to identify valuable prompts

---

## Related Documentation

- [User Guide](user_guide.md) - General usage guide
- [Project Management Guide](PROJECT_MANAGEMENT.md) - Project management features
- [Chat History Guide](CHAT_HISTORY.md) - Chat history features
- [Example Usage](EXAMPLE_USAGE.md) - More examples

---

## Feedback and Contributions

Have suggestions for improving the saved prompts feature? We'd love to hear from you!

- Submit issues or feature requests on GitHub
- Share your useful prompts with the community
- Contribute to the documentation

---

**Happy Prompting! 🚀**
