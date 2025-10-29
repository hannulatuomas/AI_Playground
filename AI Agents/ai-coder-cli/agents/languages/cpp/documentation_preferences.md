
# C++ Documentation Preferences

This document defines documentation standards for C++ projects.
These preferences guide AI agents in maintaining consistent documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Doxygen-Style Comments** - Standard C++ documentation format
2. **Header Documentation** - Thoroughly document public interfaces
3. **Implementation Comments** - Explain complex algorithms
4. **API Documentation** - Generate reference docs from code
5. **Modern C++ Standards** - Follow C++11/14/17/20 conventions

---

## Code Documentation Standards

### Doxygen Documentation Format

**File Header:**

```cpp
/**
 * @file filename.h
 * @brief Brief description of the file's purpose
 * 
 * Detailed description of what this file contains, its role in the
 * project, and any important notes about usage or dependencies.
 * 
 * @author Author Name
 * @date YYYY-MM-DD
 * @version 1.0.0
 * 
 * @copyright Copyright (c) YYYY Company Name
 * Licensed under MIT License
 */

#ifndef FILENAME_H
#define FILENAME_H

// File contents

#endif // FILENAME_H
```

**Class Documentation:**

```cpp
/**
 * @class ClassName
 * @brief Brief one-line description of the class
 * 
 * Detailed description of the class purpose, responsibilities,
 * and usage patterns. Explain when to use this class and how
 * it fits into the larger system.
 * 
 * The class provides the following key features:
 * - Feature 1
 * - Feature 2
 * - Feature 3
 * 
 * @note This class is thread-safe / not thread-safe
 * @warning Important warnings about usage
 * 
 * @code
 * // Example usage
 * ClassName obj(param1, param2);
 * obj.method();
 * @endcode
 * 
 * @see RelatedClass
 * @see AnotherClass
 */
class ClassName {
public:
    /**
     * @brief Constructor brief description
     * 
     * Detailed description of what the constructor does and
     * any initialization performed.
     * 
     * @param param1 Description of first parameter
     * @param param2 Description of second parameter
     * @throws std::invalid_argument if param1 is invalid
     * @throws std::runtime_error if initialization fails
     */
    ClassName(int param1, const std::string& param2);
    
    /**
     * @brief Destructor
     * 
     * Cleans up resources and performs necessary cleanup.
     */
    ~ClassName();
    
    /**
     * @brief Brief description of method
     * 
     * Detailed description of what the method does, including
     * side effects, preconditions, and postconditions.
     * 
     * @param input Description of input parameter
     * @param output Description of output parameter
     * @return Description of return value
     * 
     * @pre Precondition: input must be non-null
     * @post Postcondition: output contains processed result
     * 
     * @exception std::runtime_error When operation fails
     * 
     * @code
     * ClassName obj;
     * int result = obj.method(value);
     * @endcode
     * 
     * @note Important implementation note
     * @warning Warning about usage
     */
    int method(int input, int* output);
    
private:
    int privateMethod();  ///< Brief description of private method
    
    int m_memberVar;      ///< Brief description of member variable
};
```

**Function Documentation:**

```cpp
/**
 * @brief Calculates the sum of two integers
 * 
 * This function adds two integers and returns the result.
 * It handles overflow by wrapping around.
 * 
 * @param a First integer
 * @param b Second integer
 * @return Sum of a and b
 * 
 * @warning May overflow for very large values
 * 
 * @code
 * int result = add(5, 10);  // result = 15
 * @endcode
 */
int add(int a, int b) {
    return a + b;
}

/**
 * @brief Template function brief description
 * 
 * Detailed description of the template function.
 * 
 * @tparam T Type of elements to process
 * @param container Container of elements
 * @return Processed result
 * 
 * @code
 * std::vector<int> vec = {1, 2, 3};
 * auto result = processContainer(vec);
 * @endcode
 */
template<typename T>
auto processContainer(const std::vector<T>& container) -> T {
    // Implementation
}
```

**Enum Documentation:**

```cpp
/**
 * @enum Status
 * @brief Represents operation status
 * 
 * Detailed description of the enum and when each value
 * should be used.
 */
enum class Status {
    SUCCESS,      ///< Operation completed successfully
    FAILURE,      ///< Operation failed
    PENDING,      ///< Operation is pending
    CANCELLED     ///< Operation was cancelled
};
```

**Struct Documentation:**

```cpp
/**
 * @struct DataStruct
 * @brief Brief description of the struct
 * 
 * Detailed description of the struct's purpose and usage.
 */
struct DataStruct {
    int id;              ///< Unique identifier
    std::string name;    ///< Name field
    double value;        ///< Value field
    
    /**
     * @brief Default constructor
     */
    DataStruct() : id(0), value(0.0) {}
};
```

**Namespace Documentation:**

```cpp
/**
 * @namespace Utils
 * @brief Utility functions namespace
 * 
 * Contains general-purpose utility functions used throughout
 * the application.
 */
namespace Utils {
    /**
     * @brief Utility function description
     */
    void utilityFunction();
}
```

### Inline Comments

```cpp
// Single-line comment explaining the next line
int variable = 42;

// Multi-line comment explaining
// a more complex block of code
// across several lines
if (condition) {
    // Do something
}

/* Block comment for
   longer explanations */

// TODO: Future enhancement
// FIXME: Known bug to fix
// HACK: Temporary workaround
// NOTE: Important information
// OPTIMIZE: Performance improvement needed

// Explain complex algorithm
for (int i = 0; i < n; ++i) {
    // Algorithm step 1
    // Algorithm step 2
}
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview
2. **BUILDING.md** - Build instructions
3. **API.md** - API reference (or Doxygen-generated)
4. **CONTRIBUTING.md** - Contribution guidelines
5. **CHANGELOG.md** - Version history
6. **LICENSE** - License information
7. **docs/**
   - **ARCHITECTURE.md** - System architecture
   - **DESIGN.md** - Design decisions
   - **DEPENDENCIES.md** - Third-party dependencies

### README.md Structure

```markdown
# Project Name

Brief description of the C++ project.

[![Build Status](badge-url)](link)
[![License](badge-url)](link)
[![C++ Standard](https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/C-17_aircraft_over_over_the_Blue_Ridge_Mountains_2005.jpg/330px-C-17_aircraft_over_over_the_Blue_Ridge_Mountains_2005.jpg)

## Features

- Feature 1
- Feature 2
- Feature 3

## Requirements

- C++17 or later
- CMake 3.15+
- Compiler: GCC 9+, Clang 10+, MSVC 2019+
- Dependencies:
  - Boost 1.70+
  - Other libraries

## Building

### Linux/macOS

```bash
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Create build directory
mkdir build && cd build

# Configure
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build
cmake --build .

# Run tests
ctest
```

### Windows

```bash
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Create build directory
mkdir build
cd build

# Configure (Visual Studio 2019)
cmake -G "Visual Studio 16 2019" -A x64 ..

# Build
cmake --build . --config Release
```

## Installation

```bash
# Install to system (may require sudo)
cmake --install build --prefix /usr/local
```

## Usage

### Basic Example

```cpp
#include <projectname/header.h>

int main() {
    projectname::Class obj(param1, param2);
    auto result = obj.method();
    return 0;
}
```

### Linking

#### CMake

```cmake
find_package(ProjectName REQUIRED)
target_link_libraries(your_target ProjectName::ProjectName)
```

#### Manual

```bash
g++ -std=c++17 main.cpp -lprojectname -o program
```

## API Documentation

API documentation is generated using Doxygen.

### Generate Documentation

```bash
cd docs
doxygen Doxyfile
```

View documentation by opening `docs/html/index.html`.

Or view online at: [link]

## Project Structure

```
project/
├── include/            # Public headers
│   └── projectname/
│       ├── header1.h
│       └── header2.h
├── src/                # Source files
│   ├── file1.cpp
│   └── file2.cpp
├── tests/              # Unit tests
│   ├── test1.cpp
│   └── test2.cpp
├── examples/           # Usage examples
│   └── example1.cpp
├── docs/               # Documentation
│   ├── Doxyfile
│   └── *.md
├── CMakeLists.txt      # CMake configuration
└── README.md
```

## Testing

```bash
# Build tests
cmake -DBUILD_TESTS=ON ..
cmake --build .

# Run tests
ctest --output-on-failure

# Run with Valgrind (memory check)
ctest -T memcheck
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Licensed under MIT License - see [LICENSE](LICENSE)

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
```

### CMakeLists.txt Documentation

```cmake
# Minimum CMake version required
cmake_minimum_required(VERSION 3.15)

# Project name and version
project(ProjectName
    VERSION 1.0.0
    DESCRIPTION "Brief project description"
    LANGUAGES CXX
)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
option(BUILD_TESTS "Build tests" ON)
option(BUILD_EXAMPLES "Build examples" ON)
option(BUILD_DOCS "Build documentation" OFF)

# Find dependencies
find_package(Boost 1.70 REQUIRED COMPONENTS system filesystem)

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${Boost_INCLUDE_DIRS}
)

# Library
add_library(${PROJECT_NAME}
    src/file1.cpp
    src/file2.cpp
)

# Link libraries
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        Boost::system
        Boost::filesystem
)

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Examples
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Documentation
if(BUILD_DOCS)
    find_package(Doxygen)
    if(DOXYGEN_FOUND)
        add_custom_target(docs
            COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            COMMENT "Generating API documentation with Doxygen"
        )
    endif()
endif()

# Installation
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include
)
```

---

## Doxygen Configuration

### Doxyfile Essentials

```doxygen
# Project information
PROJECT_NAME           = "Project Name"
PROJECT_NUMBER         = 1.0.0
PROJECT_BRIEF          = "Brief description"

# Input files
INPUT                  = ../include ../src
RECURSIVE              = YES
FILE_PATTERNS          = *.h *.hpp *.cpp

# Output
OUTPUT_DIRECTORY       = .
GENERATE_HTML          = YES
GENERATE_LATEX         = NO

# Documentation style
JAVADOC_AUTOBRIEF      = YES
QT_AUTOBRIEF           = YES
EXTRACT_ALL            = YES
EXTRACT_PRIVATE        = NO
EXTRACT_STATIC         = YES

# Diagrams
HAVE_DOT               = YES
CALL_GRAPH             = YES
CALLER_GRAPH           = YES
CLASS_DIAGRAMS         = YES

# Output optimization
HTML_OUTPUT            = html
HTML_FILE_EXTENSION    = .html
HTML_COLORSTYLE_HUE    = 220
HTML_COLORSTYLE_SAT    = 100
HTML_COLORSTYLE_GAMMA  = 80
```

---

## Special Documentation Cases

### Template Classes

```cpp
/**
 * @class Vector
 * @brief Generic vector container
 * 
 * Provides a dynamic array implementation with automatic resizing.
 * 
 * @tparam T Type of elements stored in the vector
 * @tparam Allocator Allocator type for memory management
 */
template<typename T, typename Allocator = std::allocator<T>>
class Vector {
public:
    /**
     * @brief Add element to vector
     * @param value Element to add
     */
    void push_back(const T& value);
};
```

### Smart Pointers

```cpp
/**
 * @brief Creates a shared pointer to Object
 * 
 * Creates and returns a std::shared_ptr to a dynamically
 * allocated Object.
 * 
 * @param args Constructor arguments for Object
 * @return std::shared_ptr<Object> Pointer to created object
 * 
 * @code
 * auto ptr = createObject(arg1, arg2);
 * @endcode
 */
template<typename... Args>
std::shared_ptr<Object> createObject(Args&&... args) {
    return std::make_shared<Object>(std::forward<Args>(args)...);
}
```

### Operators

```cpp
/**
 * @brief Equality comparison operator
 * 
 * Compares two ClassName objects for equality.
 * 
 * @param lhs Left-hand side object
 * @param rhs Right-hand side object
 * @return true if objects are equal, false otherwise
 */
friend bool operator==(const ClassName& lhs, const ClassName& rhs);

/**
 * @brief Stream output operator
 * 
 * Outputs ClassName object to stream.
 * 
 * @param os Output stream
 * @param obj Object to output
 * @return Reference to output stream
 */
friend std::ostream& operator<<(std::ostream& os, const ClassName& obj);
```

---

## Testing Documentation

### Google Test Example

```cpp
/**
 * @file test_classname.cpp
 * @brief Unit tests for ClassName
 * 
 * Tests all functionality of ClassName including:
 * - Constructor/destructor
 * - Public methods
 * - Edge cases
 * - Error conditions
 */

#include <gtest/gtest.h>
#include "classname.h"

/**
 * @brief Test fixture for ClassName tests
 */
class ClassNameTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup code
    }
    
    void TearDown() override {
        // Teardown code
    }
    
    ClassName obj;  ///< Test object
};

/**
 * @test Constructor should initialize correctly
 */
TEST_F(ClassNameTest, ConstructorInitializesCorrectly) {
    EXPECT_EQ(obj.getValue(), 0);
}

/**
 * @test Method should handle normal input
 */
TEST_F(ClassNameTest, MethodHandlesNormalInput) {
    auto result = obj.method(10);
    EXPECT_EQ(result, 20);
}

/**
 * @test Method should throw on invalid input
 */
TEST_F(ClassNameTest, MethodThrowsOnInvalidInput) {
    EXPECT_THROW(obj.method(-1), std::invalid_argument);
}
```

---

## Documentation Maintenance

### Maintenance Checklist

- [ ] All public APIs have Doxygen comments
- [ ] All classes documented with examples
- [ ] All functions have parameter and return documentation
- [ ] Exception specifications documented
- [ ] Template parameters documented
- [ ] README.md is current
- [ ] CHANGELOG.md updated
- [ ] Doxygen generates without warnings
- [ ] Build instructions tested
- [ ] Code examples compile and run

### Generating Documentation

```bash
# Generate Doxygen documentation
cd docs
doxygen Doxyfile

# Open in browser
open html/index.html  # macOS
xdg-open html/index.html  # Linux
start html/index.html  # Windows
```

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Doxygen Format** - Use standard Doxygen tags
2. **Complete Headers** - Document all public interfaces
3. **Template Documentation** - Document all template parameters
4. **Exception Specifications** - Document all thrown exceptions
5. **Examples** - Provide working code examples
6. **Modern C++** - Follow current C++ standards (C++17/20)
7. **CMake Documentation** - Document build process
8. **API Reference** - Maintain generated documentation

**Priority Order:**
1. Public header documentation (Doxygen)
2. Class and function documentation
3. README.md and build instructions
4. API reference (generated)
5. CHANGELOG.md

---

**Last Updated:** 2025-10-12
**Version:** 1.0
