

"""
CPP Project Initialization Agent

This agent handles CPP project initialization with support for various
build systems and project types.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class CPPProjectInitAgent(ProjectInitBase):
    """
    CPP project initialization agent.
    
    Capabilities:
    - Initialize CPP projects
    - Support for CMake, Make, and other build systems
    - Generate proper project structure
    - Create configuration files
    """
    
    def __init__(
        self,
        name: str = "project_init_cpp",
        description: str = "CPP project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="CPP",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported CPP project types."""
        return [
            'console',      # Console application
            'library',      # Static/shared library
            'header_only',  # Header-only library
            'game',         # Game project
            'embedded',     # Embedded system
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        return {
            'directories': [
                'src',
                'include',
                'tests',
                'docs',
                'build',
                'lib',
            ],
        }
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default CPP configuration files."""
        files = {}
        project_name = config['project_name'].replace('-', '_').replace(' ', '_')
        project_type = config['project_type']
        cpp_standard = config.get('cpp_standard', '17')
        build_system = config.get('build_system', 'cmake')
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A CPP project')}

## Building

```bash
mkdir build
cd build
cmake ..
make
```

## Running

```bash
./bin/{project_name}
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        if build_system == 'cmake':
            # CMakeLists.txt
            files['CMakeLists.txt'] = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 0.1.0)

# Set CPP standard
set(CMAKE_CXX_STANDARD {cpp_standard})
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib)

# Include directories
include_directories(include)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.h" "include/*.hpp")

# Create executable or library
{self._get_cmake_target(project_type, project_name)}

# Compiler warnings
if(MSVC)
    target_compile_options({project_name} PRIVATE /W4 /WX)
else()
    target_compile_options({project_name} PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

# Testing
enable_testing()
add_subdirectory(tests)
"""
            
            # tests/CMakeLists.txt
            files['tests/CMakeLists.txt'] = f"""# Test executable
add_executable(tests_main test_main.cpp)

# Link with project library if needed
# target_link_libraries(tests_main {project_name})

# Add test
add_test(NAME tests_main COMMAND tests_main)
"""
        
        # Main source file
        if project_type == 'console':
            files['src/main.cpp'] = f"""#include <iostream>
#include "{project_name}.h"

int main(int argc, char* argv[]) {{
    std::cout << "Hello from {config['project_name']}!" << std::endl;
    return 0;
}}
"""
        
        # Header file
        files[f'include/{project_name}.h'] = f"""#ifndef {project_name.upper()}_H
#define {project_name.upper()}_H

/**
 * @file {project_name}.h
 * @brief Main header for {config['project_name']}
 * @author {config.get('author', 'Author')}
 */

namespace {project_name} {{

/**
 * @brief Get version string
 * @return Version string
 */
const char* version();

}} // namespace {project_name}

#endif // {project_name.upper()}_H
"""
        
        # Implementation file
        files[f'src/{project_name}.cpp'] = f"""#include "{project_name}.h"

namespace {project_name} {{

const char* version() {{
    return "0.1.0";
}}

}} // namespace {project_name}
"""
        
        # Test file
        files['tests/test_main.cpp'] = f"""#include <cassert>
#include <iostream>
#include "{project_name}.h"

int main() {{
    std::cout << "Running tests..." << std::endl;
    
    // Example test
    assert({project_name}::version() != nullptr);
    
    std::cout << "All tests passed!" << std::endl;
    return 0;
}}
"""
        
        # .gitignore
        files['.gitignore'] = """# Build directories
build/
bin/
lib/
*.o
*.a
*.so
*.dylib
*.dll
*.exe

# CMake
CMakeCache.txt
CMakeFiles/
cmake_install.cmake
Makefile

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        
        # .clang-format
        files['.clang-format'] = """BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 100
"""
        
        return files
    
    def _get_cmake_target(self, project_type: str, project_name: str) -> str:
        """Get CMake target definition."""
        if project_type == 'library':
            return f"""add_library({project_name} ${{SOURCES}} ${{HEADERS}})"""
        else:
            return f"""add_executable({project_name} ${{SOURCES}} ${{HEADERS}})"""
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate CPP-specific rules."""
        return f"""## CPP-Specific Rules

### CPP Standard

- **Target Standard**: CPP{config.get('cpp_standard', '17')}
- **Compiler**: GCC 9+, Clang 10+, MSVC 2019+

### Code Style

1. **Naming**:
   - snake_case for functions and variables
   - PascalCase for classes and structs
   - UPPER_SNAKE_CASE for constants and macros
   - Prefix private members with m_ or _

2. **Formatting**:
   - 4-space indentation
   - Allman or K&R brace style
   - Use clang-format for consistency

3. **Headers**:
   - Header guards or #pragma once
   - Forward declarations when possible
   - Minimize includes in headers

### Project Type: {config['project_type']}

### Best Practices

1. **Memory Management**:
   - Use smart pointers (unique_ptr, shared_ptr)
   - RAII for resource management
   - Avoid raw pointers for ownership

2. **Modern CPP**:
   - Use auto where appropriate
   - Range-based for loops
   - constexpr for compile-time constants
   - nullptr instead of NULL

3. **Standard Library**:
   - Prefer STL containers over raw arrays
   - Use std::string over C strings
   - Use std::vector for dynamic arrays

### Build System

1. **CMake**: Modern CMake (3.15+) recommended
2. **Out-of-Source**: Always build out-of-source
3. **Dependencies**: Use find_package or FetchContent
4. **Install Rules**: Provide install targets

### Error Handling

1. **Exceptions**: Use exceptions for error handling
2. **Error Codes**: Return error codes for performance-critical code
3. **Assertions**: Use assertions for preconditions
4. **Logging**: Use structured logging

### Testing

1. **Framework**: Google Test or Catch2
2. **Coverage**: Use gcov or llvm-cov
3. **CI**: Automate testing in CI/CD
4. **Mocking**: Use Google Mock for dependencies

### Documentation

1. **Doxygen**: Use Doxygen for API documentation
2. **Comments**: Document public APIs
3. **Examples**: Provide usage examples
4. **README**: Build instructions and dependencies

### Performance

1. **Profiling**: Profile before optimizing
2. **Move Semantics**: Use move semantics for large objects
3. **Const**: Use const correctness
4. **Inline**: Inline small, frequently-called functions

### Security

1. **Buffer Overflow**: Use safe string operations
2. **Integer Overflow**: Check for overflow
3. **Input Validation**: Validate all external inputs
4. **Dependencies**: Keep dependencies updated
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get CPP-specific questions."""
        return [
            {
                'key': 'cpp_standard',
                'question': 'CPP standard?',
                'type': 'choice',
                'options': ['11', '14', '17', '20', '23'],
                'default': '17',
                'required': False
            },
            {
                'key': 'build_system',
                'question': 'Build system?',
                'type': 'choice',
                'options': ['cmake', 'make', 'bazel'],
                'default': 'cmake',
                'required': False
            },
        ]


