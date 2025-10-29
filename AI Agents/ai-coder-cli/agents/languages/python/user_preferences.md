
# Python User Preferences

## Framework and Library Preferences

### Web Framework
```yaml
# Preferred web framework
web_framework: fastapi

# Options:
# - fastapi: FastAPI (modern, async, type hints)
# - django: Django (batteries-included)
# - flask: Flask (lightweight, flexible)
# - sanic: Sanic (async)
# - tornado: Tornado (async, long polling)
# - pyramid: Pyramid (flexible)
```

### ORM/Database
```yaml
# Database ORM/toolkit
orm: sqlalchemy

# Options:
# - sqlalchemy: SQLAlchemy (powerful, flexible)
# - django_orm: Django ORM (Django only)
# - peewee: Peewee (simple, lightweight)
# - tortoise_orm: Tortoise ORM (async)
# - pony: Pony ORM (pythonic)

# Async database driver
async_db: asyncpg  # for PostgreSQL

# Options:
# - asyncpg: asyncpg (PostgreSQL)
# - aiomysql: aiomysql (MySQL)
# - aiosqlite: aiosqlite (SQLite)
# - motor: Motor (MongoDB)
```

### Testing Framework
```yaml
# Test framework
test_framework: pytest

# Options:
# - pytest: pytest (modern, fixtures)
# - unittest: unittest (built-in)
# - nose2: nose2 (unittest extension)

# Test runner
test_runner: pytest

# Options:
# - pytest: pytest
# - tox: tox (multi-environment)
# - nox: nox (flexible)
```

### API Documentation
```yaml
# API documentation
api_docs: swagger

# Options:
# - swagger: Swagger/OpenAPI (FastAPI built-in)
# - redoc: ReDoc
# - sphinx: Sphinx (comprehensive docs)
# - mkdocs: MkDocs (markdown-based)
```

### Serialization
```yaml
# Data validation/serialization
serialization: pydantic

# Options:
# - pydantic: Pydantic (type-based validation)
# - marshmallow: Marshmallow (schema-based)
# - attrs: attrs + cattrs
# - dataclasses: Built-in dataclasses
```

## Code Style Preferences

### Python Version
```yaml
# Target Python version
python_version: "3.11"

# Minimum supported version
min_python_version: "3.9"

# Options:
# - "3.12": Latest features
# - "3.11": Modern, stable
# - "3.10": Pattern matching support
# - "3.9": Type hint improvements
# - "3.8": Walrus operator, positional-only params
```

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 4  # PEP 8 standard

# Line length
max_line_length: 88  # Black default

# Options:
# - 79: PEP 8 strict
# - 88: Black default
# - 100: Relaxed
# - 120: Very relaxed

# String quotes
string_quotes: double

# Options:
# - double: "string"
# - single: 'string'
```

### Import Organization
```yaml
# Import sorting
import_sorting: isort

# Import order (PEP 8)
import_order:
  - standard_library  # import os, sys
  - third_party       # import requests
  - first_party       # from myapp import module
  - local             # from . import local

# One import per line
one_import_per_line: true
```

### Type Hints
```yaml
# Use type hints
use_type_hints: true

# Type checking level
type_checking: strict

# Options:
# - strict: Strict type checking (mypy strict mode)
# - standard: Standard type checking
# - minimal: Basic type hints only
# - none: No type hints

# Runtime type validation
runtime_validation: true  # Using pydantic or similar
```

### Naming Conventions
```yaml
# Follow PEP 8 naming conventions

# Module names: lowercase_with_underscores
module_naming: snake_case

# Class names: PascalCase
class_naming: PascalCase

# Function names: lowercase_with_underscores
function_naming: snake_case

# Variable names: lowercase_with_underscores
variable_naming: snake_case

# Constant names: UPPER_CASE_WITH_UNDERSCORES
constant_naming: UPPER_SNAKE_CASE

# Private attributes: _leading_underscore
private_prefix: single_underscore

# Options:
# - single_underscore: _private
# - double_underscore: __private (name mangling)
```

### String Formatting
```yaml
# String formatting preference
string_formatting: f_strings

# Options:
# - f_strings: f"Hello {name}" (Python 3.6+)
# - format: "Hello {}".format(name)
# - percent: "Hello %s" % name
# - template: Template strings
```

### Docstring Style
```yaml
# Docstring format
docstring_style: google

# Options:
# - google: Google style
# - numpy: NumPy style
# - sphinx: Sphinx/reST style
# - pep257: PEP 257 basic

# Docstring coverage
require_docstrings: public_only

# Options:
# - all: All functions/classes
# - public_only: Only public API
# - minimal: Only complex functions
# - none: No requirement
```

## Dependency Management

### Package Manager
```yaml
# Package/dependency manager
package_manager: poetry

# Options:
# - poetry: Poetry (modern, dependency resolver)
# - pipenv: Pipenv (Pipfile + virtualenv)
# - pip_tools: pip-tools (requirements.txt + compile)
# - pip: pip + requirements.txt (basic)
# - conda: Conda (scientific computing)
```

### Virtual Environment
```yaml
# Virtual environment tool
venv_tool: venv

# Options:
# - venv: Built-in venv
# - virtualenv: virtualenv (more features)
# - conda: Conda environments
# - poetry: Poetry managed (automatic)

# Auto-activate on directory change
auto_activate_venv: true
```

### Dependency Pinning
```yaml
# Pin exact versions
pin_versions: lock_file

# Options:
# - lock_file: Use lock file (poetry.lock, Pipfile.lock)
# - exact: Pin exact versions in requirements
# - compatible: Use compatible release (~=)
# - flexible: Allow minor updates
```

## Testing Preferences

### Test Structure
```yaml
# Test directory structure
test_structure: mirror

# Options:
# - mirror: Mirror source structure
# - flat: Flat test directory
# - pytest_style: tests/ with conftest.py

# Test file naming
test_file_prefix: test_

# Options:
# - test_: test_module.py
# - _test: module_test.py
```

### Test Coverage
```yaml
# Minimum coverage target
min_coverage: 80  # percentage

# Coverage tool
coverage_tool: pytest_cov

# Options:
# - pytest_cov: pytest-cov
# - coverage: coverage.py
# - codecov: Codecov integration

# Fail on coverage below threshold
fail_under: true
```

### Mocking
```yaml
# Mocking library
mocking_library: unittest_mock

# Options:
# - unittest_mock: unittest.mock (built-in)
# - pytest_mock: pytest-mock (pytest wrapper)
# - responses: responses (HTTP mocking)
# - vcrpy: VCR.py (record/replay HTTP)
```

### Test Fixtures
```yaml
# Fixture approach
fixture_approach: pytest_fixtures

# Options:
# - pytest_fixtures: pytest fixtures
# - unittest_setup: unittest setUp/tearDown
# - factory_boy: Factory Boy (test data)
# - faker: Faker (fake data generation)
```

## Tooling Preferences

### Linter
```yaml
# Code linter
linter: ruff

# Options:
# - ruff: Ruff (fast, modern, replaces many tools)
# - pylint: Pylint (comprehensive)
# - flake8: Flake8 (popular)
# - pycodestyle: pycodestyle (PEP 8 only)

# Linting strictness
linting_level: standard

# Options:
# - strict: All rules enabled
# - standard: Recommended rules
# - relaxed: Basic rules only
```

### Formatter
```yaml
# Code formatter
formatter: black

# Options:
# - black: Black (opinionated, popular)
# - autopep8: autopep8 (PEP 8 compliant)
# - yapf: YAPF (configurable)
# - ruff_format: Ruff formatter (compatible with Black)

# Format on save
format_on_save: true
```

### Import Sorter
```yaml
# Import sorting tool
import_sorter: ruff

# Options:
# - ruff: Ruff (fast)
# - isort: isort (configurable)
# - reorder_python_imports: reorder-python-imports

# Profile
isort_profile: black  # Compatible with Black
```

### Type Checker
```yaml
# Static type checker
type_checker: mypy

# Options:
# - mypy: mypy (official)
# - pyright: Pyright (fast, Microsoft)
# - pyre: Pyre (Facebook)
# - pytype: Pytype (Google)

# Type checking strictness
type_checking_strict: true

# Check on save
type_check_on_save: true
```

### Pre-commit Hooks
```yaml
# Pre-commit framework
pre_commit: enabled

# Pre-commit hooks
pre_commit_hooks:
  - black         # Code formatting
  - ruff          # Linting
  - mypy          # Type checking
  - pytest        # Run tests
  - trailing_whitespace
  - end_of_file_fixer
```

## Project Structure Preferences

### Project Layout
```yaml
# Project structure style
project_layout: src_layout

# Options:
# - src_layout: src/ directory (recommended)
# - flat_layout: Flat layout (legacy)

# Example src_layout:
# myproject/
#   src/
#     myproject/
#       __init__.py
#       module.py
#   tests/
#   pyproject.toml
#   README.md

# Example flat_layout:
# myproject/
#   myproject/
#     __init__.py
#     module.py
#   tests/
#   setup.py
```

### Package Configuration
```yaml
# Package configuration file
package_config: pyproject_toml

# Options:
# - pyproject_toml: pyproject.toml (PEP 518, modern)
# - setup_py: setup.py (traditional)
# - setup_cfg: setup.cfg (declarative)
```

### Module Organization
```yaml
# Module organization
module_organization: feature_based

# Options:
# - feature_based: Organize by feature/domain
# - type_based: Organize by type (models, views, etc.)
# - hybrid: Mix of both

# Example feature_based:
# myapp/
#   users/
#     models.py
#     views.py
#     services.py
#   orders/
#     models.py
#     views.py
#     services.py
```

## Design Pattern Preferences

### Architectural Pattern
```yaml
# Architecture style
architecture: clean_architecture

# Options:
# - clean_architecture: Clean Architecture
# - layered: Layered architecture
# - hexagonal: Hexagonal/Ports & Adapters
# - mvc: Model-View-Controller (Django)
# - mvt: Model-View-Template (Django)
```

### Dependency Injection
```yaml
# Dependency injection
dependency_injection: dependency_injector

# Options:
# - dependency_injector: dependency-injector library
# - injector: injector library
# - fastapi_di: FastAPI built-in DI
# - manual: Manual DI (pass dependencies)
# - none: No DI framework
```

### Configuration Management
```yaml
# Configuration approach
config_management: pydantic_settings

# Options:
# - pydantic_settings: Pydantic Settings (type-safe)
# - python_decouple: python-decouple
# - dynaconf: Dynaconf (multi-environment)
# - environ: django-environ (Django)
# - configparser: configparser (ini files)
# - env_files: .env files + os.getenv
```

## Asynchronous Programming

### Async Framework
```yaml
# Async framework preference
async_framework: asyncio

# Options:
# - asyncio: asyncio (built-in)
# - trio: Trio (structured concurrency)
# - curio: Curio (minimal)

# Use async/await
prefer_async: true  # For I/O-bound operations
```

### Concurrency
```yaml
# Concurrency approach
concurrency: asyncio

# Options:
# - asyncio: Async/await
# - threading: Threading (I/O-bound)
# - multiprocessing: Multiprocessing (CPU-bound)
# - concurrent_futures: concurrent.futures
```

## Data Processing Preferences

### Data Analysis
```yaml
# Data analysis libraries (if applicable)
data_libraries:
  - pandas     # DataFrames
  - numpy      # Numerical computing
  - polars     # Fast DataFrame library

# Visualization
visualization: matplotlib

# Options:
# - matplotlib: Matplotlib
# - plotly: Plotly (interactive)
# - seaborn: Seaborn (statistical)
# - altair: Altair (declarative)
```

### API Client
```yaml
# HTTP client library
http_client: httpx

# Options:
# - httpx: HTTPX (async support)
# - requests: Requests (popular, sync)
# - aiohttp: aiohttp (async only)
# - urllib3: urllib3 (low-level)
```

## Documentation Preferences

### Documentation Tool
```yaml
# Documentation generator
docs_tool: mkdocs

# Options:
# - mkdocs: MkDocs (Markdown)
# - sphinx: Sphinx (reST, comprehensive)
# - pdoc: pdoc (auto-generate from docstrings)
# - pydoc: pydoc (built-in, basic)

# Documentation theme
docs_theme: material

# Options (MkDocs):
# - material: Material for MkDocs
# - readthedocs: Read the Docs theme

# Options (Sphinx):
# - sphinx_rtd_theme: Read the Docs
# - alabaster: Alabaster (default)
```

### API Documentation
```yaml
# Auto-generate API docs
auto_api_docs: true

# Include examples
include_examples: true

# Type hints in docs
show_type_hints: true
```

## Logging Preferences

### Logging Framework
```yaml
# Logging library
logging_library: structlog

# Options:
# - structlog: structlog (structured logging)
# - loguru: loguru (simple, powerful)
# - logging: built-in logging module
# - python_json_logger: JSON logger

# Log format
log_format: json

# Options:
# - json: JSON structured logs
# - text: Human-readable text
# - logfmt: Logfmt format

# Log level
log_level: INFO

# Options:
# - DEBUG: Detailed debugging
# - INFO: General information
# - WARNING: Warnings only
# - ERROR: Errors only
# - CRITICAL: Critical only
```

## Security Preferences

### Security Libraries
```yaml
# Password hashing
password_hashing: argon2

# Options:
# - argon2: Argon2 (recommended)
# - bcrypt: bcrypt (popular)
# - pbkdf2: PBKDF2 (built-in)

# Secrets management
secrets_management: environment_variables

# Options:
# - environment_variables: Environment variables
# - vault: HashiCorp Vault
# - aws_secrets: AWS Secrets Manager
# - azure_keyvault: Azure Key Vault
```

### Input Validation
```yaml
# Input validation
input_validation: pydantic

# SQL injection prevention
use_parameterized_queries: true

# XSS prevention (web apps)
escape_html: true
```

## Performance Preferences

### Profiling
```yaml
# Profiling tool
profiler: cprofile

# Options:
# - cprofile: cProfile (built-in)
# - py_spy: py-spy (sampling profiler)
# - line_profiler: line_profiler (line-by-line)
# - memory_profiler: memory_profiler (memory usage)

# Enable profiling in dev
profile_in_dev: false
```

### Optimization
```yaml
# Use compiled extensions
use_compiled_extensions: true  # e.g., Cython, numba

# Caching
caching_library: functools_lru_cache

# Options:
# - functools_lru_cache: @lru_cache (built-in)
# - cachetools: cachetools
# - redis: Redis
# - memcached: Memcached
```

## CI/CD Preferences

### CI Platform
```yaml
# CI/CD platform
ci_platform: github_actions

# Options:
# - github_actions: GitHub Actions
# - gitlab_ci: GitLab CI
# - jenkins: Jenkins
# - travis: Travis CI
# - circleci: CircleCI

# Run on commit
ci_on_commit: true

# CI steps
ci_steps:
  - lint
  - type_check
  - test
  - coverage
  - build
```

### Container
```yaml
# Use Docker
use_docker: true

# Base image
docker_base_image: python:3.11-slim

# Options:
# - python:3.11-slim: Official slim image
# - python:3.11-alpine: Alpine (smaller)
# - ubuntu:latest: Ubuntu base
```

## Deployment Preferences

### WSGI/ASGI Server
```yaml
# Production server
production_server: uvicorn

# Options (ASGI):
# - uvicorn: Uvicorn (FastAPI default)
# - hypercorn: Hypercorn (Trio/asyncio)
# - daphne: Daphne (Django Channels)

# Options (WSGI):
# - gunicorn: Gunicorn (Django, Flask)
# - uwsgi: uWSGI
# - waitress: Waitress (pure Python)

# Workers
worker_count: auto  # or specific number
```

### Hosting Platform
```yaml
# Preferred hosting
hosting: aws

# Options:
# - aws: AWS (EC2, Lambda, ECS)
# - azure: Azure
# - gcp: Google Cloud Platform
# - heroku: Heroku
# - digitalocean: DigitalOcean
# - vercel: Vercel (serverless)
# - railway: Railway
```

### Process Management
```yaml
# Process manager (production)
process_manager: supervisor

# Options:
# - supervisor: Supervisor
# - systemd: systemd
# - pm2: PM2
# - docker: Docker Compose
```

## Additional Preferences

### Code Complexity
```yaml
# Complexity checking
check_complexity: true

# Max cyclomatic complexity
max_complexity: 10

# Tool
complexity_tool: radon

# Options:
# - radon: radon
# - mccabe: mccabe (flake8 plugin)
# - xenon: xenon
```

### Security Scanning
```yaml
# Security vulnerability scanning
security_scanning: true

# Tool
security_tool: bandit

# Options:
# - bandit: bandit (code security)
# - safety: safety (dependency check)
# - pip_audit: pip-audit
```

### Changelog
```yaml
# Changelog format
changelog_format: keep_a_changelog

# Options:
# - keep_a_changelog: Keep a Changelog format
# - conventional_commits: Conventional Commits
# - towncrier: towncrier (fragment-based)

# Versioning
versioning_scheme: semver

# Options:
# - semver: Semantic Versioning (1.2.3)
# - calver: Calendar Versioning (2024.1.1)
```
