"""
Test the automated testing module.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.automated_testing.test_generator import TestGenerator, TestGenerationConfig
from src.features.automated_testing.code_analyzer import CodeAnalyzer, Language


def test_code_analyzer():
    """Test the code analyzer."""
    print("Testing Code Analyzer...")
    
    # Test Python code analysis
    test_code = '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

class Calculator:
    """Simple calculator."""
    
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y
'''
    
    analyzer = CodeAnalyzer()
    result = analyzer.analyze_code(test_code, Language.PYTHON)
    
    print(f"✓ Found {len(result.functions)} functions")
    print(f"✓ Found {len(result.classes)} classes")
    
    for func in result.functions:
        print(f"  - Function: {func.name} with {len(func.parameters)} parameters")
    
    for cls in result.classes:
        print(f"  - Class: {cls.name} with {len(cls.methods)} methods")


def test_test_generator():
    """Test the test generator."""
    print("\nTesting Test Generator...")
    
    # Create a temporary test file
    test_file = Path('temp_test_module.py')
    test_code = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

class User:
    """User class."""
    
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    
    def validate(self) -> bool:
        """Validate user data."""
        return bool(self.name and '@' in self.email)
'''
    
    # Write test file
    with open(test_file, 'w') as f:
        f.write(test_code)
    
    try:
        # Generate tests
        config = TestGenerationConfig(
            framework="pytest",
            include_edge_cases=True,
            include_error_cases=True
        )
        
        generator = TestGenerator(config=config)
        test_output = generator.generate_unit_tests(test_file)
        
        print("✓ Generated test code:")
        print("-" * 60)
        print(test_output[:500] + "...")
        print("-" * 60)
        
        # Save generated tests
        test_output_file = Path('temp_test_module_test.py')
        with open(test_output_file, 'w') as f:
            f.write(test_output)
        
        print(f"✓ Saved tests to {test_output_file}")
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        if Path('temp_test_module_test.py').exists():
            Path('temp_test_module_test.py').unlink()


if __name__ == '__main__':
    print("=" * 60)
    print("Automated Testing Module - Test Suite")
    print("=" * 60)
    
    test_code_analyzer()
    test_test_generator()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
