# Phase 11.1 Quick Reference

## 🚀 Quick Start

```python
from src.features.automated_testing import TestGenerator, TestGenerationConfig
from pathlib import Path

# Generate tests with pytest
config = TestGenerationConfig(framework="pytest")
generator = TestGenerator(config=config)
tests = generator.generate_unit_tests(Path("mymodule.py"))
print(tests)
```

## 📋 Supported Languages & Frameworks

| Language | Frameworks |
|----------|-----------|
| Python | pytest, unittest |
| JavaScript/TypeScript | jest, mocha |
| C# | xUnit, NUnit, MSTest |
| C++ | Google Test, Catch2 |

## 🎯 Configuration Options

```python
TestGenerationConfig(
    framework="pytest",           # Testing framework
    include_mocks=True,           # Generate mocks
    include_edge_cases=True,      # Generate edge cases
    include_error_cases=True,     # Generate error tests
    include_integration=False,    # Generate integration tests
    max_tests_per_function=10     # Max tests per function
)
```

## 📊 Methods

### TestGenerator
- `generate_unit_tests(file_path, target=None, output_path=None)` - Generate unit tests
- `generate_class_tests(file_path, class_name, output_path=None)` - Generate class tests
- `generate_integration_tests(module_path, output_path=None)` - Generate integration tests
- `generate_edge_cases(code_analysis)` - Get edge case descriptions
- `generate_mocks(dependencies)` - Generate mock objects

### CodeAnalyzer
- `analyze_file(file_path)` - Analyze a source file
- `analyze_code(code, language)` - Analyze code string
- `detect_edge_cases(parameters)` - Detect edge cases

## 🧪 Example: Generate Tests for a File

```python
from pathlib import Path
from src.features.automated_testing import TestGenerator

generator = TestGenerator()

# Generate and save tests
generator.generate_unit_tests(
    file_path=Path("calculator.py"),
    output_path=Path("tests/test_calculator.py")
)
```

## 🎨 Example: Analyze Code Structure

```python
from src.features.automated_testing.code_analyzer import CodeAnalyzer, Language

analyzer = CodeAnalyzer()
result = analyzer.analyze_file(Path("mymodule.py"))

print(f"Functions: {len(result.functions)}")
print(f"Classes: {len(result.classes)}")

for func in result.functions:
    print(f"  - {func.name}: {len(func.parameters)} params")
```

## 🔧 Framework-Specific Examples

### Python (pytest)
```python
config = TestGenerationConfig(framework="pytest")
generator = TestGenerator(config=config)
tests = generator.generate_unit_tests(Path("mymodule.py"))
```

### JavaScript (jest)
```python
config = TestGenerationConfig(framework="jest")
generator = TestGenerator(config=config)
tests = generator.generate_unit_tests(Path("mymodule.js"))
```

### C# (xUnit)
```python
config = TestGenerationConfig(framework="xunit")
generator = TestGenerator(config=config)
tests = generator.generate_unit_tests(Path("MyClass.cs"))
```

## 📁 File Structure

```
src/features/automated_testing/
├── __init__.py              # Exports
├── code_analyzer.py         # Code analysis
├── test_generator.py        # Main interface
└── generators/              # Language-specific
    ├── python_generator.py
    ├── javascript_generator.py
    ├── csharp_generator.py
    └── cpp_generator.py
```

## 🧪 Testing

```bash
python test_automated_testing.py
```

## 📚 Documentation

- `docs/PHASE_11_1_TEST_GENERATION.md` - Complete guide
- `PHASE_11_1_SUMMARY.md` - Implementation summary
- `README.md` - Updated with Phase 11.1

## ✅ Checklist

- [x] Install dependencies: `pip install -r requirements.txt`
- [x] Run test suite: `python test_automated_testing.py`
- [x] Read documentation: `docs/PHASE_11_1_TEST_GENERATION.md`
- [x] Try examples above
- [x] Generate tests for your code
- [x] Customize generated tests
- [x] Run generated tests

## 🎯 Common Use Cases

### 1. Test New Function
```python
# Generate tests for specific function
tests = generator.generate_unit_tests(
    Path("utils.py"),
    target="calculate_sum"
)
```

### 2. Test Entire Class
```python
# Generate tests for specific class
tests = generator.generate_class_tests(
    Path("models.py"),
    class_name="User"
)
```

### 3. Batch Generate Tests
```python
from pathlib import Path

generator = TestGenerator()
for py_file in Path("src").glob("**/*.py"):
    output = Path("tests") / f"test_{py_file.name}"
    generator.generate_unit_tests(py_file, output_path=output)
```

## 🐛 Troubleshooting

**Issue**: Import errors in generated tests  
**Solution**: Check module paths and adjust imports manually

**Issue**: Tests too generic  
**Solution**: Add specific assertions based on your requirements

**Issue**: Edge cases not relevant  
**Solution**: Review and customize edge case tests

## 📞 Support

- Documentation: `docs/PHASE_11_1_TEST_GENERATION.md`
- Examples: `test_automated_testing.py`
- Source: `src/features/automated_testing/`

---

**Version**: 2.1.0  
**Phase**: 11.1 - Automated Test Generation  
**Status**: ✅ Complete
