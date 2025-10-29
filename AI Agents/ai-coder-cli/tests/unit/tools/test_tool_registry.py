
"""
Unit tests for Tool Registry.

Tests the tool registration and retrieval system.
"""

import pytest
from unittest.mock import Mock
from tools.registry import ToolRegistry
from tools.base import Tool


class MockTool(Tool):
    """Mock tool for testing."""
    
    def invoke(self, params):
        """Mock invoke method."""
        return {'success': True, 'result': 'Mock result'}


class AnotherMockTool(Tool):
    """Another mock tool for testing."""
    
    def invoke(self, params):
        """Mock invoke method."""
        return {'success': True}


@pytest.mark.unit
class TestToolRegistry:
    """Test suite for ToolRegistry class."""
    
    def test_singleton_pattern(self):
        """Test that ToolRegistry implements singleton pattern."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        
        assert registry1 is registry2, "ToolRegistry should be a singleton"
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = MockTool('test_tool', 'Test tool description')
        
        registry.register(tool)
        
        assert registry.get('test_tool') is tool
        assert 'test_tool' in registry.list_tools()
    
    def test_register_tool_with_custom_name(self):
        """Test registering a tool with custom name."""
        registry = ToolRegistry()
        tool = MockTool('original_name', 'Test tool')
        
        registry.register(tool, name='custom_name')
        
        assert registry.get('custom_name') is tool
        assert 'custom_name' in registry.list_tools()
    
    def test_register_tool_without_name_attribute(self):
        """Test that registering tool without name raises ValueError."""
        registry = ToolRegistry()
        
        # Create a mock object without name attribute
        invalid_tool = Mock(spec=[])
        
        with pytest.raises(ValueError, match="name"):
            registry.register(invalid_tool)
    
    def test_register_duplicate_warning(self, caplog):
        """Test that registering duplicate tool name logs warning."""
        registry = ToolRegistry()
        tool1 = MockTool('duplicate', 'Tool 1')
        tool2 = AnotherMockTool('duplicate', 'Tool 2')
        
        registry.register(tool1)
        registry.register(tool2)
        
        assert 'already registered' in caplog.text.lower()
        # Second tool should overwrite first
        assert registry.get('duplicate') is tool2
    
    def test_get_nonexistent_tool(self):
        """Test getting a non-existent tool returns None."""
        registry = ToolRegistry()
        
        result = registry.get('nonexistent_tool')
        
        assert result is None
    
    def test_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()
        registry.clear()  # Clear any existing tools
        
        tool1 = MockTool('tool1', 'Tool 1')
        tool2 = AnotherMockTool('tool2', 'Tool 2')
        
        registry.register(tool1)
        registry.register(tool2)
        
        tools = registry.list_tools()
        
        assert 'tool1' in tools
        assert 'tool2' in tools
        assert len(tools) >= 2
    
    def test_list_all_with_metadata(self):
        """Test listing all tools with metadata."""
        registry = ToolRegistry()
        registry.clear()
        
        tool = MockTool('meta_tool', 'Tool with metadata')
        registry.register(tool)
        
        all_tools = registry.list_all()
        
        assert 'meta_tool' in all_tools
        assert 'class_name' in all_tools['meta_tool']
        assert 'description' in all_tools['meta_tool']
        assert all_tools['meta_tool']['description'] == 'Tool with metadata'
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = MockTool('unregister_test', 'Test tool')
        
        registry.register(tool)
        assert registry.get('unregister_test') is not None
        
        result = registry.unregister('unregister_test')
        
        assert result is True
        assert registry.get('unregister_test') is None
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering non-existent tool returns False."""
        registry = ToolRegistry()
        
        result = registry.unregister('nonexistent')
        
        assert result is False
    
    def test_clear(self):
        """Test clearing all registered tools."""
        registry = ToolRegistry()
        tool1 = MockTool('clear1', 'Tool 1')
        tool2 = MockTool('clear2', 'Tool 2')
        
        registry.register(tool1)
        registry.register(tool2)
        
        initial_count = len(registry)
        registry.clear()
        
        assert len(registry) == 0
        assert initial_count > 0
    
    def test_len(self):
        """Test __len__ method returns correct count."""
        registry = ToolRegistry()
        registry.clear()
        
        tool = MockTool('len_test', 'Test')
        registry.register(tool)
        
        assert len(registry) == 1
    
    def test_repr(self):
        """Test __repr__ method."""
        registry = ToolRegistry()
        
        repr_str = repr(registry)
        
        assert 'ToolRegistry' in repr_str
        assert 'tools=' in repr_str
