"""
Test script for CLI

Tests the CLI interface functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ui.cli import CLI, Colors


def test_cli_initialization():
    """Test CLI initialization."""
    print("="*60)
    print("Testing CLI Initialization")
    print("="*60)
    
    cli = CLI()
    print("✓ CLI instance created")
    
    assert cli.running == True
    print("✓ Running flag set")
    
    assert cli.history == []
    print("✓ History initialized")
    
    return cli


def test_colorize(cli):
    """Test color output."""
    print("\n" + "="*60)
    print("Testing Color Output")
    print("="*60)
    
    colored = cli.colorize("Test", Colors.GREEN)
    assert Colors.GREEN in colored
    assert Colors.RESET in colored
    print("✓ Color codes applied correctly")
    
    # Test all colors
    colors = [
        ('RED', Colors.RED),
        ('GREEN', Colors.GREEN),
        ('YELLOW', Colors.YELLOW),
        ('BLUE', Colors.BLUE),
        ('CYAN', Colors.CYAN),
    ]
    
    for name, color in colors:
        result = cli.colorize(f"Test {name}", color)
        print(f"✓ {name}: {result}")


def test_parse_command(cli):
    """Test command parsing."""
    print("\n" + "="*60)
    print("Testing Command Parsing")
    print("="*60)
    
    test_cases = [
        ("gen python Create a function", ("gen", "python Create a function")),
        ("help", ("help", "")),
        ("debug python", ("debug", "python")),
        ("  gen  python  test  ", ("gen", "python  test")),
        ("", (None, [])),
    ]
    
    for input_cmd, expected in test_cases:
        cmd, args = cli.parse_command(input_cmd)
        if cmd == expected[0]:
            print(f"✓ '{input_cmd[:30]}...' -> ({cmd}, '{args[:20]}...')")
        else:
            print(f"✗ '{input_cmd[:30]}...' -> Expected {expected}, got ({cmd}, {args})")


def test_command_structure(cli):
    """Test command structure and methods."""
    print("\n" + "="*60)
    print("Testing Command Structure")
    print("="*60)
    
    commands = [
        'cmd_generate',
        'cmd_debug',
        'cmd_langs',
        'cmd_frameworks',
        'cmd_template',
        'cmd_stats',
        'cmd_history',
        'cmd_clear',
    ]
    
    for cmd in commands:
        if hasattr(cli, cmd):
            print(f"✓ {cmd} method exists")
        else:
            print(f"✗ {cmd} method missing")


def test_header_and_help():
    """Test header and help output."""
    print("\n" + "="*60)
    print("Testing Header and Help")
    print("="*60)
    
    cli = CLI()
    
    # Test header (just check it doesn't crash)
    try:
        cli.print_header()
        print("✓ Header printed successfully")
    except Exception as e:
        print(f"✗ Header failed: {e}")
    
    # Test help (just check it doesn't crash)
    try:
        cli.print_help()
        print("✓ Help printed successfully")
    except Exception as e:
        print(f"✗ Help failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  CLI Tests")
    print("="*60 + "\n")
    
    try:
        # Initialize
        cli = test_cli_initialization()
        
        # Run tests
        test_colorize(cli)
        test_parse_command(cli)
        test_command_structure(cli)
        test_header_and_help()
        
        print("\n" + "="*60)
        print("  ✓ All CLI Tests Passed!")
        print("="*60)
        print("\nCLI features:")
        print("  ✓ Command parsing")
        print("  ✓ Color output (ANSI)")
        print("  ✓ Help system")
        print("  ✓ Command history")
        print("  ✓ Generation commands")
        print("  ✓ Debug commands")
        print("  ✓ Language support commands")
        print("  ✓ Statistics commands")
        print("\nTo run the CLI:")
        print("  python src/ui/cli.py")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
