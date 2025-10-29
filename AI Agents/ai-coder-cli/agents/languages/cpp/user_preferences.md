
# C++ User Preferences

## Language Standard

### C++ Version
```yaml
# Target C++ standard
cpp_standard: cpp20

# Options:
# - cpp23: C++23 (latest, experimental)
# - cpp20: C++20 (modern)
# - cpp17: C++17 (widely supported)
# - cpp14: C++14 (mature)
# - cpp11: C++11 (legacy modern)

# Minimum supported standard
min_cpp_standard: cpp17
```

## Compiler Preferences

### Compiler
```yaml
# Preferred compiler
compiler: gcc

# Options:
# - gcc: GCC (GNU Compiler Collection)
# - clang: Clang/LLVM
# - msvc: Microsoft Visual C++
# - intel: Intel C++ Compiler

# Compiler version
compiler_version: "13.0"  # or latest

# Warning level
warning_level: wall

# Options:
# - wall: -Wall (all warnings)
# - wextra: -Wall -Wextra
# - werror: Treat warnings as errors
# - pedantic: -Wpedantic (strict standards)

# Optimization level
optimization_level: O2

# Options:
# - O0: No optimization (debug)
# - O1: Basic optimization
# - O2: Moderate optimization (recommended)
# - O3: Aggressive optimization
# - Os: Optimize for size
```

## Build System

### Build Tool
```yaml
# Build system
build_system: cmake

# Options:
# - cmake: CMake (cross-platform)
# - make: GNU Make (traditional)
# - ninja: Ninja (fast)
# - bazel: Bazel (Google)
# - meson: Meson (modern)
# - xmake: xmake (Lua-based)

# CMake version
cmake_min_version: "3.20"

# Out-of-source builds
out_of_source_build: true
```

### Package Manager
```yaml
# Dependency management
package_manager: conan

# Options:
# - conan: Conan (C/C++ package manager)
# - vcpkg: vcpkg (Microsoft)
# - cpm: CPM (CMake Package Manager)
# - hunter: Hunter
# - manual: Manual dependency management
```

## Code Style Preferences

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 4  # or 2

# Line length
max_line_length: 100

# Brace style
brace_style: allman

# Options:
# - allman: Braces on new line
#   void function()
#   {
#   }
# - kr: K&R style
#   void function() {
#   }
# - stroustrup: Stroustrup style
#   void function() {
#   } // With else on same line as }

# Pointer alignment
pointer_alignment: left

# Options:
# - left: int* ptr
# - right: int *ptr
# - middle: int * ptr

# Reference alignment (same as pointer)
reference_alignment: left
```

### Naming Conventions
```yaml
# Namespace naming
namespace_naming: snake_case

# Options:
# - snake_case: my_namespace
# - lower_case: myns
# - PascalCase: MyNamespace

# Class naming
class_naming: PascalCase

# Function naming
function_naming: camelCase

# Options:
# - camelCase: getUserData
# - PascalCase: GetUserData
# - snake_case: get_user_data

# Variable naming
variable_naming: snake_case

# Options:
# - snake_case: user_count
# - camelCase: userCount

# Member variable suffix/prefix
member_variable_style: trailing_underscore

# Options:
# - trailing_underscore: value_
# - m_prefix: m_value
# - none: value

# Constant naming
constant_naming: kPascalCase

# Options:
# - kPascalCase: kMaxSize
# - UPPER_SNAKE_CASE: MAX_SIZE
# - PascalCase: MaxSize

# Macro naming
macro_naming: UPPER_SNAKE_CASE

# Enum naming
enum_naming: PascalCase

# Template parameter naming
template_param_naming: PascalCase  # typename T, typename Value
```

### Header Guards
```yaml
# Header guard style
header_guard: pragma_once

# Options:
# - pragma_once: #pragma once
# - define_guard: #ifndef/#define/#endif
# - both: Use both for maximum compatibility

# Define guard format (if used)
define_guard_format: PROJECT_PATH_FILENAME_H_

# Options:
# - PROJECT_PATH_FILENAME_H_: MYLIB_UTILS_STRING_H_
# - FILENAME_H_: STRING_H_
```

### Include Order
```yaml
# Include organization
include_order:
  - related_header    # Corresponding .h for .cpp
  - c_system         # <stdio.h>
  - cpp_system       # <iostream>
  - other_library    # <boost/...>
  - project          # "myproject/..."

# Separate groups with blank line
separate_include_groups: true

# Sort alphabetically within groups
sort_includes: true
```

### Const Correctness
```yaml
# Const preference
const_preference: const_correct

# Options:
# - const_correct: Use const wherever possible
# - minimal: Only when necessary
# - east_const: East const (int const)
# - west_const: West const (const int)

# Const position
const_position: west

# Options:
# - west: const int
# - east: int const
```

## Memory Management

### Smart Pointers
```yaml
# Prefer smart pointers
prefer_smart_pointers: true

# Smart pointer preference
smart_pointer_preference: unique_ptr

# Options:
# - unique_ptr: std::unique_ptr (default)
# - shared_ptr: std::shared_ptr (when sharing needed)
# - mixed: Use appropriate type

# Avoid raw pointers
avoid_raw_pointers: true

# Options:
# - true: Only use for non-owning pointers
# - false: Allow raw pointers

# Use make_unique/make_shared
use_make_functions: true
```

### RAII
```yaml
# Enforce RAII
enforce_raii: true

# Custom resource wrappers
custom_resource_wrappers: true

# File handling
file_handling: raii

# Options:
# - raii: Custom RAII wrapper or use std::fstream
# - standard: Standard library (fstream)
# - manual: Manual resource management (avoid)
```

### Rule of Zero/Five
```yaml
# Follow Rule of Zero/Five
follow_rule: rule_of_zero

# Options:
# - rule_of_zero: Prefer compiler-generated
# - rule_of_five: Explicitly define all five
# - rule_of_three: C++98/03 style (legacy)

# Delete copy operations by default
default_copy_delete: false

# Delete move operations by default
default_move_delete: false
```

## Standard Library Usage

### Containers
```yaml
# Preferred container for dynamic arrays
dynamic_array_container: vector

# Options:
# - vector: std::vector (default)
# - deque: std::deque (double-ended)

# Use std::array for fixed size
use_std_array: true

# Prefer range-based for loops
prefer_range_for: true
```

### Algorithms
```yaml
# Use STL algorithms
use_stl_algorithms: prefer

# Options:
# - prefer: Prefer STL algorithms
# - mixed: Use when appropriate
# - minimal: Hand-written loops

# Use ranges (C++20)
use_ranges: true
```

### Strings
```yaml
# String type preference
string_type: std_string

# Options:
# - std_string: std::string
# - std_string_view: std::string_view (C++17)
# - custom: Custom string class

# String parameter passing
string_parameter: string_view

# Options:
# - string_view: const std::string_view&
# - const_ref: const std::string&
# - value: std::string (for ownership)
```

## Error Handling

### Exception Strategy
```yaml
# Use exceptions
use_exceptions: true

# Options:
# - true: Use exceptions
# - false: Error codes/optional
# - mixed: Context-dependent

# Exception types
exception_types: standard_exceptions

# Options:
# - standard_exceptions: std::exception derived
# - custom_exceptions: Custom exception hierarchy
# - mixed: Both

# noexcept specification
use_noexcept: true

# Exception safety guarantee
exception_safety: strong

# Options:
# - strong: Strong guarantee
# - basic: Basic guarantee
# - nothrow: No-throw guarantee
```

### Alternative Error Handling
```yaml
# Use std::optional (C++17)
use_optional: true

# Use std::expected (C++23)
use_expected: true  # When available

# Error codes
error_code_style: std_error_code

# Options:
# - std_error_code: std::error_code
# - custom: Custom error codes
# - none: Don't use error codes
```

## Testing

### Testing Framework
```yaml
# Test framework
test_framework: google_test

# Options:
# - google_test: Google Test (popular)
# - catch2: Catch2 (header-only)
# - doctest: doctest (fast)
# - boost_test: Boost.Test
# - cppunit: CppUnit

# Test organization
test_organization: mirror_source

# Options:
# - mirror_source: Mirror source directory structure
# - flat: Flat test directory

# Test naming
test_file_suffix: _test

# Options:
# - _test: my_class_test.cpp
# - Test: MyClassTest.cpp
```

### Mocking
```yaml
# Mocking framework
mocking_framework: google_mock

# Options:
# - google_mock: Google Mock (gmock)
# - trompeloeil: Trompeloeil
# - hippomocks: HippoMocks
# - fakeit: FakeIt
```

### Code Coverage
```yaml
# Code coverage tool
coverage_tool: gcov

# Options:
# - gcov: gcov (GCC)
# - llvm_cov: llvm-cov (Clang)
# - codecov: Codecov (service)
# - coveralls: Coveralls (service)

# Minimum coverage
min_coverage: 80  # percentage
```

## Modern C++ Features

### Feature Adoption
```yaml
# Auto type deduction
use_auto: prefer_explicit_types

# Options:
# - prefer_auto: Use auto extensively
# - prefer_explicit_types: Explicit types where clear
# - minimal: Minimal auto usage

# Structured bindings (C++17)
use_structured_bindings: true

# Lambda expressions
lambda_usage: extensive

# Options:
# - extensive: Use liberally
# - moderate: Use when appropriate
# - minimal: Prefer named functions

# Range-based for loops
use_range_for: true

# constexpr
use_constexpr: true

# if/switch init statements (C++17)
use_init_statements: true
```

### Type Traits and Concepts
```yaml
# Use type traits
use_type_traits: true

# Use concepts (C++20)
use_concepts: true

# SFINAE vs concepts
prefer_concepts: true

# Options:
# - true: Prefer concepts over SFINAE
# - false: Use SFINAE

# Static assertions
use_static_assert: true
```

## Concurrency

### Threading
```yaml
# Threading library
threading_library: std_thread

# Options:
# - std_thread: std::thread (C++11)
# - pthread: POSIX threads
# - windows_threads: Windows threads
# - tbb: Intel TBB
# - openmp: OpenMP

# Synchronization primitives
sync_primitives: std_mutex

# Options:
# - std_mutex: std::mutex, std::lock_guard
# - custom: Custom synchronization

# Async operations
async_operations: std_async

# Options:
# - std_async: std::async
# - std_future: std::future/promise
# - custom: Custom async framework
```

### Parallelism
```yaml
# Parallel algorithms (C++17)
use_parallel_algorithms: true

# Execution policies
default_execution_policy: par

# Options:
# - seq: Sequential
# - par: Parallel
# - par_unseq: Parallel and vectorized
```

## Documentation

### Documentation Tool
```yaml
# Documentation generator
docs_tool: doxygen

# Options:
# - doxygen: Doxygen
# - breathe_sphinx: Breathe + Sphinx
# - cppcheck: Cppcheck with docs
# - standardese: Standardese

# Documentation style
doc_style: doxygen

# Options:
# - doxygen: Doxygen style (///)
# - javadoc: Javadoc style (/**)
# - qt: Qt style (/*!)

# Inline documentation
inline_docs: all_public

# Options:
# - all_public: All public APIs
# - all_members: All members
# - minimal: Only complex functions
```

### Comments
```yaml
# Comment style
comment_style: forward_slash

# Options:
# - forward_slash: // comment
# - block_comment: /* comment */

# Header comments
header_comment_style: doxygen_block

# Explain complex algorithms
explain_complexity: true
```

## Static Analysis

### Linter/Analyzer
```yaml
# Static analysis tools
static_analyzers:
  - clang_tidy
  - cppcheck
  # - cpplint
  # - pvs_studio

# Clang-tidy checks
clang_tidy_checks: modernize*,readability*,performance*

# Run on save
analyze_on_save: true
```

### Sanitizers
```yaml
# Runtime sanitizers
use_sanitizers: development

# Options:
# - development: Use in development builds
# - always: Always enabled
# - never: Never use

# Sanitizer types
sanitizers:
  - address    # AddressSanitizer
  - undefined  # UndefinedBehaviorSanitizer
  # - thread   # ThreadSanitizer
  # - memory   # MemorySanitizer
```

## Performance

### Optimization Preferences
```yaml
# Profile-guided optimization
use_pgo: false

# Link-time optimization
use_lto: release_only

# Options:
# - always: Always use LTO
# - release_only: Only in release builds
# - never: Don't use LTO
```

### Profiling
```yaml
# Profiling tool
profiling_tool: perf

# Options:
# - perf: Linux perf
# - gprof: gprof
# - valgrind: Valgrind (Callgrind)
# - vtune: Intel VTune
# - instruments: Xcode Instruments (macOS)

# Benchmark framework
benchmark_framework: google_benchmark

# Options:
# - google_benchmark: Google Benchmark
# - catch2: Catch2 benchmarks
# - custom: Custom benchmarks
```

## Project Organization

### Directory Structure
```yaml
# Project layout
project_layout: modern

# Modern layout:
# project/
#   include/
#     project/
#       *.h
#   src/
#     *.cpp
#   tests/
#   cmake/
#   CMakeLists.txt

# Options:
# - modern: Separate include/src
# - traditional: src/ with headers
# - header_only: Header-only library
```

### File Organization
```yaml
# One class per file
one_class_per_file: true

# Header and implementation
header_impl_separation: true

# Options:
# - true: Separate .h and .cpp
# - false: Header-only or inline
# - mixed: Context-dependent

# File naming matches class
file_naming_matches_class: true
```

## External Libraries

### Third-Party Libraries
```yaml
# Allowed third-party libraries
preferred_libraries:
  - boost: selective  # Use specific Boost libraries
  - abseil: true      # Abseil (Google)
  - fmt: true         # {fmt} formatting
  - spdlog: true      # spdlog logging
  - json: true        # nlohmann/json
  # - qt: false       # Qt framework
  # - wxwidgets: false
```

### Library Linking
```yaml
# Prefer header-only
prefer_header_only: true

# Static vs dynamic linking
linking_preference: static

# Options:
# - static: Static linking
# - dynamic: Dynamic linking
# - mixed: Context-dependent
```

## Platform Support

### Target Platforms
```yaml
# Supported platforms
target_platforms:
  - linux
  - windows
  - macos
  # - bsd
  # - embedded

# Cross-platform abstractions
use_platform_abstractions: true

# Conditional compilation
platform_specific_code: ifdef_guards

# Options:
# - ifdef_guards: #ifdef guards
# - separate_files: Platform-specific files
# - abstraction_layer: Abstraction layer
```

### Compiler Portability
```yaml
# Support multiple compilers
multi_compiler: true

# Test on multiple compilers
test_compilers:
  - gcc
  - clang
  - msvc
```

## CI/CD

### Continuous Integration
```yaml
# CI platform
ci_platform: github_actions

# Options:
# - github_actions: GitHub Actions
# - gitlab_ci: GitLab CI
# - jenkins: Jenkins
# - travis: Travis CI
# - circle_ci: CircleCI

# Build matrix
build_matrix: true  # Multiple compilers/platforms

# CI steps
ci_steps:
  - build
  - test
  - static_analysis
  - coverage
  - sanitizers
```

### Deployment
```yaml
# Package format
package_format: cmake_package

# Options:
# - cmake_package: CMake package
# - conan_package: Conan package
# - deb: Debian package
# - rpm: RPM package
# - installer: Platform installer
```
