"""
Tests for Rule Manager Module
"""

import pytest
import tempfile
from pathlib import Path
from src.modules.rule_manager import (
    RuleManager, RuleScope, RuleCategory,
    RuleValidator, RuleParser, DefaultRules
)


@pytest.fixture
def temp_rules_file():
    """Create temporary rules file."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


def test_rule_manager_add_rule(temp_rules_file):
    """Test adding a rule."""
    manager = RuleManager(temp_rules_file)
    
    rule = manager.add_rule(
        scope=RuleScope.GLOBAL,
        category=RuleCategory.STYLE,
        rule_text="Use consistent naming",
        priority=5
    )
    
    assert rule.id > 0
    assert rule.rule_text == "Use consistent naming"


def test_rule_manager_get_rules(temp_rules_file):
    """Test getting rules."""
    manager = RuleManager(temp_rules_file)
    
    manager.add_rule(RuleScope.GLOBAL, RuleCategory.STYLE, "Rule 1", 5)
    manager.add_rule(RuleScope.LANGUAGE, RuleCategory.QUALITY, "Rule 2", 7, language='python')
    
    all_rules = manager.get_rules()
    assert len(all_rules) >= 2
    
    python_rules = manager.get_rules(language='python')
    assert len(python_rules) >= 1


def test_rule_manager_applicable_rules(temp_rules_file):
    """Test getting applicable rules."""
    manager = RuleManager(temp_rules_file)
    
    manager.add_rule(RuleScope.GLOBAL, RuleCategory.STYLE, "Global rule", 5)
    manager.add_rule(RuleScope.LANGUAGE, RuleCategory.STYLE, "Python rule", 7, language='python')
    
    rules = manager.get_applicable_rules('python')
    
    assert len(rules) >= 2


def test_rule_manager_format_rules(temp_rules_file):
    """Test formatting rules for prompt."""
    manager = RuleManager(temp_rules_file)
    
    manager.add_rule(RuleScope.GLOBAL, RuleCategory.STYLE, "Rule 1", 5)
    
    rules = manager.get_rules()
    formatted = manager.format_rules_for_prompt(rules)
    
    assert "Rule 1" in formatted
    assert "Style:" in formatted


def test_rule_validator():
    """Test rule validator."""
    validator = RuleValidator()
    
    code = "x = 1\ny = 2"
    rules = []
    
    result = validator.validate_code(code, rules, 'python')
    
    assert result.passed is True
    assert result.score >= 0


def test_rule_parser():
    """Test rule parser."""
    parser = RuleParser()
    
    text = "- Rule 1\n- Rule 2\n- Rule 3"
    rules = parser.parse_from_text(text, RuleScope.GLOBAL, RuleCategory.STYLE)
    
    assert len(rules) == 3
    assert rules[0].rule_text == "Rule 1"


def test_default_rules():
    """Test default rules."""
    defaults = DefaultRules.get_all_defaults()
    
    assert 'python' in defaults
    assert 'javascript' in defaults
    assert 'style' in defaults['python']


def test_default_rules_for_language():
    """Test getting rules for specific language."""
    python_rules = DefaultRules.get_rules_for_language('python')
    
    assert 'style' in python_rules
    assert 'quality' in python_rules
    assert len(python_rules['style']) > 0
