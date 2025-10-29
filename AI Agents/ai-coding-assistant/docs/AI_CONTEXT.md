\# AI Context - For AI Assistants Working on This Project



\## Project Overview



\*\*Name:\*\* AI Coding Assistant  

\*\*Version:\*\* 1.0.0  

\*\*Status:\*\* Production Ready  

\*\*Language:\*\* Python 3.12  

\*\*Architecture:\*\* Modular, layered architecture with core/features/ui separation



---



\## Purpose



This document provides context for AI assistants (like Claude, GPT, etc.) working on this codebase. It contains essential information to understand the project structure, design decisions, and implementation details.



---



\## Key Principles



1\. \*\*Lightweight \& Minimal\*\*: Keep dependencies minimal, use Python standard library

2\. \*\*Self-Improving\*\*: Learn from user feedback, avoid repeating errors

3\. \*\*Privacy-First\*\*: All processing local, no data sent externally

4\. \*\*Cross-Platform\*\*: Works on Windows, Linux, macOS

5\. \*\*Clean Code\*\*: PEP 8, type hints, docstrings, clear structure

6\. \*\*User-Friendly\*\*: Simple CLI, optional GUI, clear error messages



---



\## Project Structure Quick Reference



```

src/

├── core/           # Backend: LLM interface, prompts, learning DB

├── features/       # Features: code gen, debugging, lang support

└── ui/             # Interfaces: CLI, GUI



data/

├── config.json     # User configuration

├── models/         # GGUF model files

└── db/             # SQLite learning database



tests/              # Unit and integration tests

docs/               # Documentation

```



---



\## Core Components



\### 1. LLM Interface (src/core/llm\_interface.py)

\- \*\*Purpose:\*\* Interface to llama.cpp via subprocess

\- \*\*Key Class:\*\* `LLMInterface`

\- \*\*Important:\*\* 

&nbsp; - Uses subprocess for llama-cli execution

&nbsp; - Implements LRU caching (100 entries)

&nbsp; - Cross-platform path handling

&nbsp; - Config in dataclass `LLMConfig`



\### 2. Prompt Engine (src/core/prompt\_engine.py)

\- \*\*Purpose:\*\* Manage prompts and templates

\- \*\*Key Class:\*\* `PromptEngine`

\- \*\*Important:\*\*

&nbsp; - 15+ language-specific system prompts

&nbsp; - 5 task types: generate, debug, explain, optimize, refactor

&nbsp; - Integrates with learning DB for context

&nbsp; - Template system with `PromptTemplate` dataclass



\### 3. Learning Database (src/core/learning\_db.py)

\- \*\*Purpose:\*\* Self-improvement via SQLite

\- \*\*Key Class:\*\* `LearningDB`

\- \*\*Schema:\*\*

&nbsp; - `interactions` table: All user interactions

&nbsp; - `error\_patterns` table: Common errors and solutions

&nbsp; - `best\_practices` table: Learned best practices

\- \*\*Important:\*\*

&nbsp; - Context-aware learning retrieval

&nbsp; - Automatic cleanup of old entries (30 days)

&nbsp; - Privacy: No user-specific data (names, emails, paths)



\### 4. Code Generator (src/features/code\_gen.py)

\- \*\*Purpose:\*\* Generate code from natural language

\- \*\*Key Class:\*\* `CodeGenerator`

\- \*\*Important:\*\*

&nbsp; - Always fetches relevant learnings

&nbsp; - Parses response into code + explanation

&nbsp; - Feedback loop for self-improvement

&nbsp; - Supports all 12+ languages



\### 5. Debugger (src/features/debugger.py)

\- \*\*Purpose:\*\* Debug and fix code

\- \*\*Key Class:\*\* `Debugger`

\- \*\*Important:\*\*

&nbsp; - Classifies 12+ error types

&nbsp; - Retrieves past fixes for similar errors

&nbsp; - Tracks error patterns

&nbsp; - Suggests preventive measures



\### 6. Language Support (src/features/lang\_support.py)

\- \*\*Purpose:\*\* Language-specific functionality

\- \*\*Key Class:\*\* `LanguageSupport`

\- \*\*Supported Languages:\*\*

&nbsp; - Python, C++, C#, JavaScript, TypeScript

&nbsp; - HTML, CSS, PowerShell, Bash, Zsh, Sh, Batch

\- \*\*Framework Detection:\*\*

&nbsp; - React, Node.js, Django, Flask, Express, Next.js, Axios



---



\## Design Patterns



1\. \*\*Dependency Injection:\*\* Components receive dependencies via constructor

2\. \*\*Strategy Pattern:\*\* Different prompts for different languages

3\. \*\*Repository Pattern:\*\* LearningDB abstracts database operations

4\. \*\*Factory Pattern:\*\* Config objects creation

5\. \*\*Observer Pattern:\*\* Feedback system updates learning DB



---



\## Important Implementation Details



\### Self-Improvement Mechanism



The system learns in this cycle:



```

1\. User provides task

2\. Fetch past learnings from DB (ALWAYS)

3\. Build enhanced prompt with learnings

4\. Generate response via LLM

5\. Show to user

6\. Collect feedback (success/failure)

7\. Store in DB with classification

8\. Next iteration uses this learning (back to step 2)

```



\*\*Key Point:\*\* Learnings are ALWAYS fetched and injected, not optional.



\### Privacy Guarantee



\*\*What is stored:\*\*

\- Error patterns (e.g., "Using mutable default arguments")

\- Solutions (e.g., "Use None and initialize in function body")

\- Language, task type, error type, timestamp



\*\*What is NOT stored:\*\*

\- User names, emails

\- File paths, directory structures

\- API keys, secrets

\- Any personally identifiable information



\### Response Caching



\- LRU cache with 100 entries

\- Cache key: (prompt, max\_tokens)

\- Avoids redundant LLM calls

\- Implemented in `LLMInterface`



\### Error Handling Philosophy



\- Comprehensive try-except blocks

\- Graceful degradation (continue with reduced functionality)

\- Clear, user-friendly error messages

\- No crashes on invalid input

\- All errors logged to learning DB



---



\## Code Style Guidelines



\### Python Style

\- \*\*PEP 8 compliant\*\*

\- \*\*Type hints everywhere:\*\* Use `from typing import \*`

\- \*\*Docstrings:\*\* Google style for all classes/functions

\- \*\*Line length:\*\* 100 characters max

\- \*\*Imports:\*\* Standard lib → Third party → Local



\### Example Function

```python

def generate\_code(

&nbsp;   self,

&nbsp;   task: str,

&nbsp;   language: str,

&nbsp;   max\_tokens: int = 2048

) -> Dict\[str, Any]:

&nbsp;   """

&nbsp;   Generate code for a given task.

&nbsp;   

&nbsp;   Args:

&nbsp;       task: Description of the code to generate

&nbsp;       language: Target programming language

&nbsp;       max\_tokens: Maximum tokens to generate

&nbsp;       

&nbsp;   Returns:

&nbsp;       Dictionary with 'code', 'explanation', 'interaction\_id'

&nbsp;       

&nbsp;   Raises:

&nbsp;       ValueError: If language not supported

&nbsp;       RuntimeError: If LLM generation fails

&nbsp;   """

&nbsp;   # Implementation

```



\### Naming Conventions

\- \*\*Classes:\*\* PascalCase (e.g., `CodeGenerator`)

\- \*\*Functions/Methods:\*\* snake\_case (e.g., `generate\_code`)

\- \*\*Constants:\*\* UPPER\_SNAKE\_CASE (e.g., `MAX\_RETRIES`)

\- \*\*Private members:\*\* Leading underscore (e.g., `\_parse\_response`)



---



\## Common Tasks for AI Assistants



\### Adding a New Language



1\. Edit `src/features/lang\_support.py`:

&nbsp;  ```python

&nbsp;  'newlang': {

&nbsp;      'extensions': \['.ext'],

&nbsp;      'comment': '#',

&nbsp;      'common\_keywords': \['keyword1', 'keyword2'],

&nbsp;      'frameworks': \[]

&nbsp;  }

&nbsp;  ```



2\. Edit `src/core/prompt\_engine.py`:

&nbsp;  ```python

&nbsp;  'newlang': """You are a NewLang expert. Follow best practices..."""

&nbsp;  ```



3\. Update tests in `tests/test\_lang\_support.py`



\### Adding a New Feature



1\. Create `src/features/new\_feature.py`

2\. Import core components:

&nbsp;  ```python

&nbsp;  from core import LLMInterface, PromptEngine, LearningDB

&nbsp;  ```

3\. Implement feature class

4\. Add to CLI in `src/ui/cli.py`

5\. Add to GUI in `src/ui/gui.py`

6\. Write tests in `tests/test\_new\_feature.py`

7\. Update documentation



\### Fixing a Bug



1\. \*\*Identify:\*\* Check error message and stack trace

2\. \*\*Locate:\*\* Find the relevant module

3\. \*\*Fix:\*\* Implement fix with proper error handling

4\. \*\*Test:\*\* Run existing tests, add new test case

5\. \*\*Document:\*\* Update docstring if behavior changed



\### Improving Prompts



1\. Open `src/core/prompt\_engine.py`

2\. Find the language or task in respective dictionary

3\. Edit the prompt string

4\. Test with various inputs

5\. Commit changes with clear message



---



\## Testing Guidelines



\### Running Tests

```bash

python tests/tests.py

```



\### Writing New Tests

```python

import unittest

from unittest.mock import Mock, patch



class TestNewFeature(unittest.TestCase):

&nbsp;   def setUp(self):

&nbsp;       """Set up test fixtures."""

&nbsp;       self.mock\_llm = Mock()

&nbsp;       self.feature = NewFeature(self.mock\_llm)

&nbsp;   

&nbsp;   def test\_basic\_functionality(self):

&nbsp;       """Test basic feature functionality."""

&nbsp;       result = self.feature.do\_something()

&nbsp;       self.assertEqual(result, expected\_value)

```



\### Test Coverage Goals

\- All public methods tested

\- Edge cases covered

\- Error conditions tested

\- Integration points verified



---



\## Database Schema Quick Reference



\### interactions table

```sql

id, query, language, task\_type, response, 

feedback, success, error\_type, correction, timestamp

```



\### error\_patterns table

```sql

id, language, error\_type, pattern, solution, 

occurrence\_count, last\_seen

```



\### best\_practices table

```sql

id, language, practice, context, 

confidence\_score, usage\_count, timestamp

```



---



\## Configuration Quick Reference



\### Default Values

```python

context\_size = 4096

temperature = 0.7

top\_p = 0.9

top\_k = 40

repeat\_penalty = 1.1

threads = 4

gpu\_layers = 0

max\_tokens = 2048

timeout = 120  # seconds

```



\### File Locations

\- Config: `data/config.json`

\- Database: `data/db/learning.db`

\- Models: `data/models/\*.gguf`

\- Logs: `logs/` (auto-created)



---



\## Dependencies



\### Required (Minimal!)

\- Python 3.8+ (3.12 recommended)

\- SQLite3 (built-in)

\- subprocess (built-in)

\- json (built-in)

\- pathlib (built-in)



\### Optional

\- colorama: Colored CLI output

\- regex: Enhanced text parsing



\### External

\- llama.cpp: LLM inference engine (separate installation)



---



\## Common Pitfalls and Solutions



\### 1. Path Issues

\*\*Problem:\*\* Paths don't work cross-platform  

\*\*Solution:\*\* Always use `pathlib.Path` and forward slashes



\### 2. Subprocess Timeout

\*\*Problem:\*\* llama.cpp hangs  

\*\*Solution:\*\* Increase timeout in config, check model compatibility



\### 3. Database Lock

\*\*Problem:\*\* SQLite database locked  

\*\*Solution:\*\* Use context managers, commit transactions



\### 4. Import Errors

\*\*Problem:\*\* Circular imports  

\*\*Solution:\*\* Follow dependency hierarchy (ui → features → core)



\### 5. Unicode Issues

\*\*Problem:\*\* Special characters break  

\*\*Solution:\*\* Use `encoding='utf-8'` everywhere



---



\## Performance Optimization Tips



1\. \*\*Caching:\*\* LLM responses are cached (LRU, 100 entries)

2\. \*\*Database:\*\* Indexes on frequently queried columns

3\. \*\*Context Size:\*\* Reduce for faster generation

4\. \*\*Threads:\*\* Match CPU core count

5\. \*\*GPU:\*\* Enable layers if GPU available



---



\## Security Considerations



1\. \*\*Input Validation:\*\* Sanitize all user input

2\. \*\*SQL Injection:\*\* Use parameterized queries ONLY

3\. \*\*Path Traversal:\*\* Validate file paths

4\. \*\*Code Execution:\*\* Never exec() generated code automatically

5\. \*\*Privacy:\*\* No data leaves the user's machine



---



\## Commit Message Format



```

<type>: <subject>



<body>



<footer>

```



\*\*Types:\*\* feat, fix, docs, style, refactor, test, chore



\*\*Example:\*\*

```

feat: Add Rust language support



\- Add Rust to lang\_support.py

\- Add Rust system prompt

\- Update tests

\- Update documentation



Closes #42

```



---



\## Documentation Standards



\### Code Documentation

\- Every class has a docstring

\- Every public method has a docstring

\- Complex logic has inline comments

\- Type hints on all functions



\### External Documentation

\- README.md: Overview and quick start

\- API.md: Complete API reference

\- QUICKSTART.md: Step-by-step guide

\- This file: Context for AI assistants



---



\## When Working on This Project



\### Before Making Changes

1\. Read relevant documentation

2\. Understand the component's role

3\. Check existing tests

4\. Consider cross-platform compatibility

5\. Think about backward compatibility



\### While Making Changes

1\. Follow code style guidelines

2\. Add type hints

3\. Write docstrings

4\. Handle errors gracefully

5\. Consider privacy implications



\### After Making Changes

1\. Run all tests

2\. Update documentation

3\. Check for regressions

4\. Write clear commit message

5\. Update CHANGELOG if needed



---



\## Project Goals (Keep in Mind)



1\. \*\*Minimal Dependencies:\*\* Avoid adding new libraries

2\. \*\*Self-Improving:\*\* Every interaction is a learning opportunity

3\. \*\*User-Friendly:\*\* Clear errors, intuitive commands

4\. \*\*Privacy-First:\*\* All processing stays local

5\. \*\*Cross-Platform:\*\* Works everywhere

6\. \*\*Maintainable:\*\* Clean, documented, tested code



---



\## Useful Commands



\### Run Application

```bash

python src/main.py            # CLI mode

python src/main.py --mode gui # GUI mode

```



\### Run Tests

```bash

python tests/tests.py

python -m unittest tests.test\_specific

```



\### Check Style

```bash

pylint src/

flake8 src/

mypy src/

```



\### Generate Documentation

```bash

pydoc -w src.core.llm\_interface

```



---



\## Quick Reference: Module Responsibilities



| Module | Responsibility | Dependencies |

|--------|---------------|--------------|

| llm\_interface | Talk to llama.cpp | None |

| prompt\_engine | Manage prompts | learning\_db |

| learning\_db | Store/retrieve learnings | None |

| code\_gen | Generate code | core.\* |

| debugger | Debug code | core.\* |

| lang\_support | Language detection | None |

| cli | CLI interface | features.\*, core.\* |

| gui | GUI interface | features.\*, core.\* |



---



\## Important Files to Always Update



When making significant changes, update these files:



1\. \*\*CHANGELOG.md\*\* - Version history

2\. \*\*README.md\*\* - If user-facing changes

3\. \*\*docs/API.md\*\* - If API changes

4\. \*\*TODO.md\*\* - Mark tasks complete

5\. \*\*STATUS.md\*\* - Update status

6\. \*\*This file\*\* - If architecture changes



---



\## Emergency Procedures



\### If Tests Fail

1\. Run single test to isolate: `python -m unittest tests.test\_module.TestClass.test\_method`

2\. Check recent changes

3\. Verify dependencies installed

4\. Check Python version compatibility



\### If Application Crashes

1\. Check error log/stack trace

2\. Verify config.json is valid JSON

3\. Check llama.cpp path and model path

4\. Test llama.cpp independently

5\. Check database file permissions



\### If Performance Degrades

1\. Check context\_size in config (reduce if high)

2\. Check cache size (increase if needed)

3\. Profile with cProfile

4\. Check database size (cleanup old entries)

5\. Monitor memory usage



---



\## Best Practices Summary



\### Code

✅ Use type hints  

✅ Write docstrings  

✅ Handle errors gracefully  

✅ Follow PEP 8  

✅ Keep functions small (<50 lines)  



\### Testing

✅ Test public APIs  

✅ Mock external dependencies  

✅ Test error conditions  

✅ Aim for high coverage  



\### Documentation

✅ Update README for user changes  

✅ Update API docs for code changes  

✅ Add inline comments for complex logic  

✅ Keep CHANGELOG current  



\### Git

✅ Clear commit messages  

✅ One feature per commit  

✅ Test before committing  

✅ Update docs in same commit  



---



\## Extending the Assistant



\### Common Extensions



1\. \*\*New Language:\*\*

&nbsp;  - Edit lang\_support.py

&nbsp;  - Edit prompt\_engine.py

&nbsp;  - Add tests

&nbsp;  - Update docs



2\. \*\*New Task Type:\*\*

&nbsp;  - Add to prompt\_engine.py task\_templates

&nbsp;  - Add method to code\_gen.py or create new feature

&nbsp;  - Add CLI command

&nbsp;  - Add GUI option



3\. \*\*New UI Mode:\*\*

&nbsp;  - Create new file in src/ui/

&nbsp;  - Import features and core

&nbsp;  - Add to main.py argument parser

&nbsp;  - Document usage



4\. \*\*Database Schema Change:\*\*

&nbsp;  - Add migration in learning\_db.py

&nbsp;  - Update queries

&nbsp;  - Test with existing data

&nbsp;  - Document schema change



---



\## Version History Quick Reference



\- \*\*v1.0.0\*\* (Jan 15, 2025): Initial release, all features complete

\- \*\*v0.5.0\*\* (Jan 14, 2025): Phases 1-4 complete (internal)

\- \*\*v0.1.0\*\* (Jan 1, 2025): Project started (internal)



---



\## Contact and Support



\- \*\*Issues:\*\* GitHub Issues

\- \*\*Discussions:\*\* GitHub Discussions

\- \*\*Documentation:\*\* See docs/ folder

\- \*\*Source Code:\*\* Well-commented, read the code!



---



\## Final Notes for AI Assistants



When working on this project:



1\. \*\*Preserve the design:\*\* Modular, minimal, self-improving

2\. \*\*Maintain quality:\*\* Tests, docs, type hints

3\. \*\*Keep it simple:\*\* No unnecessary complexity

4\. \*\*Think about users:\*\* Clear errors, intuitive design

5\. \*\*Respect privacy:\*\* No data leaves the machine

6\. \*\*Be consistent:\*\* Follow existing patterns

7\. \*\*Document everything:\*\* Code, commits, changes



This is a well-designed, production-ready codebase. Treat it with care!



---



\*\*Last Updated:\*\* October 16, 2025  

\*\*Version:\*\* 1.0.0  

\*\*Status:\*\* Complete and Production-Ready



For more details, explore the well-commented source code in src/.



