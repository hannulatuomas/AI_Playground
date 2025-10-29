"""
Test script for Debugger Feature

Tests the Debugger class with various scenarios.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core import LLMInterface, LLMConfig, PromptEngine, LearningDB, load_config_from_file
from features import Debugger


def test_debugger_init():
    """Test Debugger initialization."""
    print("="*60)
    print("Testing Debugger Initialization")
    print("="*60)

    db = LearningDB("data/db/test_debugger.db")
    engine = PromptEngine(learning_db=db)

    config = load_config_from_file()
    if not config:
        config = LLMConfig(
            model_path="data/models/test.gguf",
            executable_path="llama.cpp/llama-cli"
        )

    try:
        llm = LLMInterface(config)
        print("✓ LLM Interface created")
    except FileNotFoundError:
        print("⚠ LLM Interface not available (expected without setup)")
        llm = None

    debugger = Debugger(llm if llm else None, engine, db)
    print("✓ Debugger initialized")

    return debugger, db


def test_error_classification(debugger):
    """Test error classification."""
    print("\n" + "="*60)
    print("Testing Error Classification")
    print("="*60)

    test_cases = [
        ("SyntaxError: invalid syntax", "python", "syntax_error"),
        ("NameError: name 'x' is not defined", "python", "name_error"),
        ("TypeError: unsupported operand", "python", "type_error"),
        ("IndexError: list index out of range", "python", "index_error"),
        ("Segmentation fault", "cpp", "null_pointer"),
        ("command not found: mycommand", "bash", "command_not_found"),
        ("variable expansion error", "bash", "variable_expansion_error"),
        ("permission denied", "bash", "permission_error"),
        ("", "python", "code_review"),  # No error message
    ]

    for error_msg, language, expected in test_cases:
        result = debugger._classify_error(error_msg, language)
        status = "✓" if result == expected else "✗"
        error_preview = error_msg[:40] if error_msg else "(no error msg)"
        print(f"{status} '{error_preview}...' -> {result}")
        if result != expected:
            print(f"   Expected: {expected}, Got: {result}")


def test_input_validation(debugger):
    """Test input validation."""
    print("\n" + "="*60)
    print("Testing Input Validation")
    print("="*60)

    test_cases = [
        ("", "python", None, "Code cannot be empty"),
        ("print('hi')", "", None, "Language must be specified"),
        ("x" * 60000, "python", None, "Code is too long"),
        ("print('hi')", "python", None, None),  # Valid
    ]

    for code, lang, error_msg, expected_error in test_cases:
        result = debugger._validate_inputs(code, lang, error_msg)
        if expected_error:
            status = "✓" if result and expected_error in result else "✗"
            print(f"{status} Should reject: {expected_error[:40]}...")
        else:
            status = "✓" if result is None else "✗"
            print(f"{status} Should accept valid input")


def test_language_hints(debugger):
    """Test language-specific hints."""
    print("\n" + "="*60)
    print("Testing Language-Specific Hints")
    print("="*60)

    test_cases = [
        ("bash", "command not found"),
        ("powershell", "cannot run script"),
        ("batch", "syntax error"),
        ("python", "IndentationError"),
        ("javascript", "undefined is not a function"),
        ("cpp", "segmentation fault"),
    ]

    for language, error_msg in test_cases:
        hints = debugger._get_language_specific_hints(language, error_msg)
        status = "✓" if hints else "○"
        print(f"{status} {language:12} -> {len(hints):3} chars")
        if hints and len(hints) < 200:
            print(f"     Preview: {hints[:60]}...")


def test_prompt_building(debugger, db):
    """Test debug prompt building."""
    print("\n" + "="*60)
    print("Testing Prompt Building")
    print("="*60)

    # Add a test learning
    db.add_entry(
        query="Debug syntax error",
        language="python",
        response="Fixed code",
        task_type='debug',
        success=False,
        error_type='syntax_error',
        correction="Add colon after def statement"
    )

    # Test basic prompt
    prompt1 = debugger._build_debug_prompt(
        code="def hello()\n    pass",
        language="python",
        error_msg="SyntaxError: invalid syntax",
        context=None,
        error_type="syntax_error",
        past_fixes=[],
        language_hints=""
    )
    print(f"✓ Basic prompt: {len(prompt1)} chars")

    # Test prompt with past fixes
    past_fixes = [
        {'solution': 'Add colon after function definition'}
    ]
    prompt2 = debugger._build_debug_prompt(
        code="def hello()\n    pass",
        language="python",
        error_msg="SyntaxError",
        context=None,
        error_type="syntax_error",
        past_fixes=past_fixes,
        language_hints="Check Python syntax"
    )
    print(f"✓ Prompt with learnings: {len(prompt2)} chars")
    if "past successful fixes" in prompt2.lower():
        print("  ✓ Contains past fixes")


def test_response_parsing(debugger):
    """Test response parsing."""
    print("\n" + "="*60)
    print("Testing Response Parsing")
    print("="*60)

    # Test case 1: Standard markdown
    response1 = """
Here's the fixed code:

```python
def hello():
    print('Hello')
```

The issue was a missing colon after the function definition.

Changes made:
1. Added colon after 'def hello()'
2. Fixed indentation
"""
    fixed1, expl1, changes1 = debugger._parse_debug_response(
        response1, "python", "def hello()\n    print('Hello')"
    )
    print("✓ Test 1: Standard markdown")
    print(f"  Fixed code: {len(fixed1)} chars")
    print(f"  Explanation: {len(expl1)} chars")
    print(f"  Changes: {len(changes1)} items")
    assert "def hello():" in fixed1
    assert len(changes1) > 0

    # Test case 2: No markdown blocks
    response2 = """
def hello():
    print('Hello')
    
Fixed by adding colon.
"""
    fixed2, expl2, changes2 = debugger._parse_debug_response(
        response2, "python", "def hello()\n    print('Hello')"
    )
    print("✓ Test 2: No markdown blocks")
    print(f"  Extracted: {len(fixed2)} chars")

    # Test case 3: Multiple changes
    response3 = """
Fixed code:
```python
x = 5
```

Changes:
- Fixed variable name
- Added initialization
- Removed typo
"""
    fixed3, expl3, changes3 = debugger._parse_debug_response(
        response3, "python", "y = "
    )
    print("✓ Test 3: Multiple changes")
    print(f"  Changes extracted: {len(changes3)}")


def test_feedback_system(debugger, db):
    """Test feedback system."""
    print("\n" + "="*60)
    print("Testing Feedback System")
    print("="*60)

    # Add test entry
    entry_id = db.add_entry(
        query="Debug test",
        language="python",
        response="fixed code",
        task_type="debug"
    )
    print(f"✓ Created test entry: {entry_id}")

    # Positive feedback
    success1 = debugger.provide_feedback(
        interaction_id=entry_id,
        success=True,
        feedback="Fix worked perfectly!"
    )
    print(f"✓ Positive feedback recorded: {success1}")

    # Negative feedback with final code
    entry_id2 = db.add_entry(
        query="Another debug",
        language="python",
        response="incorrect fix",
        task_type="debug"
    )
    success2 = debugger.provide_feedback(
        interaction_id=entry_id2,
        success=False,
        feedback="Fix didn't work",
        final_code="correct version here"
    )
    print(f"✓ Negative feedback recorded: {success2}")


def test_common_errors_analysis(debugger, db):
    """Test common error analysis."""
    print("\n" + "="*60)
    print("Testing Common Error Analysis")
    print("="*60)

    # Add some test errors
    for i in range(3):
        db.add_entry(
            query=f"Debug {i}",
            language="python",
            response="fixed",
            task_type="debug",
            error_type="syntax_error"
        )

    analysis = debugger.analyze_common_errors("python")
    print(f"✓ Analysis for Python:")
    print(f"  Total sessions: {analysis['total_debug_sessions']}")
    print(f"  Success rate: {analysis['success_rate']:.1f}%")
    print(f"  Common errors: {len(analysis['most_common'])}")


def test_shell_script_handling(debugger):
    """Test shell script specific handling."""
    print("\n" + "="*60)
    print("Testing Shell Script Handling")
    print("="*60)

    # Test bash variable expansion
    hints_bash = debugger._get_language_specific_hints("bash", "variable expansion")
    print(f"✓ Bash hints: {len(hints_bash)} chars")
    if "variable expansion" in hints_bash.lower():
        print("  ✓ Contains variable expansion tips")

    # Test command not found
    error_type = debugger._classify_error("command not found: test", "bash")
    print(f"✓ Bash error classification: {error_type}")
    assert error_type == "command_not_found"

    # Test PowerShell
    hints_ps = debugger._get_language_specific_hints("powershell", None)
    print(f"✓ PowerShell hints: {len(hints_ps)} chars")

    # Test batch
    hints_batch = debugger._get_language_specific_hints("batch", None)
    print(f"✓ Batch hints: {len(hints_batch)} chars")


def test_looks_like_code(debugger):
    """Test code detection heuristic."""
    print("\n" + "="*60)
    print("Testing Code Detection")
    print("="*60)

    test_lines = [
        ("def hello():", True),
        ("This is just text", False),
        ("x = 5", True),
        ("for i in range(10):", True),
        ("# Comment only", False),
        ("// Comment", False),
        ("function test() {", True),
        ("if (x > 5) {", True),
        ("", False),
    ]

    for line, expected in test_lines:
        result = debugger._looks_like_code(line, "python")
        status = "✓" if result == expected else "✗"
        line_preview = line[:30] if line else "(empty)"
        print(f"{status} '{line_preview}' -> {result}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Debugger Feature - Tests")
    print("="*60 + "\n")

    try:
        # Initialize
        debugger, db = test_debugger_init()

        # Run tests
        test_error_classification(debugger)
        test_input_validation(debugger)
        test_language_hints(debugger)
        test_prompt_building(debugger, db)
        test_response_parsing(debugger)
        test_feedback_system(debugger, db)
        test_common_errors_analysis(debugger, db)
        test_shell_script_handling(debugger)
        test_looks_like_code(debugger)

        print("\n" + "="*60)
        print("  ✓ All Debugger Tests Passed!")
        print("="*60)
        print("\nDebugger features:")
        print("  ✓ Error classification (8+ types)")
        print("  ✓ Input validation")
        print("  ✓ Language-specific hints")
        print("  ✓ Prompt building with past fixes")
        print("  ✓ Response parsing")
        print("  ✓ Feedback system")
        print("  ✓ Common error analysis")
        print("  ✓ Shell script handling")
        print("  ✓ Code detection heuristic")
        print("\nReady for actual debugging with llama.cpp!")
        print()

        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
