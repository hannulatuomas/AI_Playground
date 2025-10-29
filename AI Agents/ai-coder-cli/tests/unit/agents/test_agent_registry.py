
"""
Unit tests for Agent Registry.

Tests the agent registration, retrieval, and management system.
"""

import pytest
from unittest.mock import Mock, patch
from agents.registry import AgentRegistry
from agents.base.agent_base import Agent


class MockAgent(Agent):
    """Mock agent for testing."""
    
    def execute(self, task, context):
        """Mock execute method."""
        return {
            'success': True,
            'message': 'Mock execution',
            'data': {}
        }


class AnotherMockAgent(Agent):
    """Another mock agent for testing."""
    
    def execute(self, task, context):
        """Mock execute method."""
        return {'success': True}


@pytest.mark.unit
class TestAgentRegistry:
    """Test suite for AgentRegistry class."""
    
    def test_singleton_pattern(self):
        """Test that AgentRegistry implements singleton pattern."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()
        
        assert registry1 is registry2, "AgentRegistry should be a singleton"
    
    def test_register_agent(self):
        """Test registering an agent."""
        registry = AgentRegistry()
        registry.clear_cache()  # Clear any cached instances
        
        registry.register(MockAgent, 'test_agent')
        
        assert registry.get('test_agent') == MockAgent
        assert 'test_agent' in registry.list_agents()
    
    def test_register_agent_with_auto_name(self):
        """Test registering agent with automatic name derivation."""
        registry = AgentRegistry()
        
        # MockAgent should become 'mock'
        registry.register(MockAgent)
        
        assert registry.get('mock') is not None
    
    def test_register_duplicate_warning(self, caplog):
        """Test that registering duplicate agent name logs warning."""
        registry = AgentRegistry()
        
        registry.register(MockAgent, 'duplicate')
        registry.register(AnotherMockAgent, 'duplicate')
        
        assert 'already registered' in caplog.text.lower()
    
    def test_get_nonexistent_agent(self):
        """Test getting a non-existent agent returns None."""
        registry = AgentRegistry()
        
        result = registry.get('nonexistent_agent')
        
        assert result is None
    
    def test_get_or_create_agent(self, mock_llm_router, mock_tool_registry):
        """Test getting or creating an agent instance."""
        registry = AgentRegistry()
        registry.clear_cache()
        registry.register(MockAgent, 'test_agent')
        
        agent = registry.get_or_create_agent(
            'test_agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        assert agent is not None
        assert isinstance(agent, MockAgent)
        assert agent.name == 'test_agent'
    
    def test_get_or_create_agent_cached(self, mock_llm_router, mock_tool_registry):
        """Test that get_or_create_agent returns cached instance."""
        registry = AgentRegistry()
        registry.clear_cache()
        registry.register(MockAgent, 'cached_agent')
        
        agent1 = registry.get_or_create_agent(
            'cached_agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        agent2 = registry.get_or_create_agent(
            'cached_agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        assert agent1 is agent2, "Should return same cached instance"
    
    def test_get_or_create_agent_force_new(self, mock_llm_router, mock_tool_registry):
        """Test forcing creation of new agent instance."""
        registry = AgentRegistry()
        registry.clear_cache()
        registry.register(MockAgent, 'force_new_agent')
        
        agent1 = registry.get_or_create_agent(
            'force_new_agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        agent2 = registry.get_or_create_agent(
            'force_new_agent',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry,
            force_new=True
        )
        
        assert agent1 is not agent2, "Should create new instance with force_new=True"
    
    def test_get_or_create_nonexistent_agent(self, mock_llm_router, mock_tool_registry):
        """Test that getting non-existent agent raises ValueError."""
        registry = AgentRegistry()
        
        with pytest.raises(ValueError, match="Agent not found"):
            registry.get_or_create_agent(
                'nonexistent',
                llm_router=mock_llm_router,
                tool_registry=mock_tool_registry
            )
    
    def test_list_agents(self):
        """Test listing all registered agents."""
        registry = AgentRegistry()
        registry.clear_cache()
        
        registry.register(MockAgent, 'agent1')
        registry.register(AnotherMockAgent, 'agent2')
        
        agents = registry.list_agents()
        
        assert 'agent1' in agents
        assert 'agent2' in agents
        assert len(agents) >= 2
    
    def test_list_all_with_metadata(self):
        """Test listing all agents with metadata."""
        registry = AgentRegistry()
        registry.clear_cache()
        
        registry.register(MockAgent, 'meta_agent')
        
        all_agents = registry.list_all()
        
        assert 'meta_agent' in all_agents
        assert 'class_name' in all_agents['meta_agent']
        assert 'description' in all_agents['meta_agent']
        assert 'instance_cached' in all_agents['meta_agent']
    
    def test_clear_cache(self, mock_llm_router, mock_tool_registry):
        """Test clearing cached agent instances."""
        registry = AgentRegistry()
        registry.clear_cache()
        registry.register(MockAgent, 'cache_test')
        
        # Create instance (will be cached)
        agent1 = registry.get_or_create_agent(
            'cache_test',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        # Clear cache
        registry.clear_cache()
        
        # Create new instance
        agent2 = registry.get_or_create_agent(
            'cache_test',
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        assert agent1 is not agent2, "Should create new instance after cache clear"
    
    def test_get_for_task(self):
        """Test getting suggested agents for a task."""
        registry = AgentRegistry()
        
        # Test with code-related task
        suggestions = registry.get_for_task("Create a new Python file")
        
        assert isinstance(suggestions, list)
        # Should return at least one suggestion (or default)
        assert len(suggestions) > 0
    
    def test_len(self):
        """Test __len__ method returns correct count."""
        registry = AgentRegistry()
        initial_count = len(registry)
        
        registry.register(MockAgent, 'len_test')
        
        assert len(registry) == initial_count + 1
    
    def test_repr(self):
        """Test __repr__ method."""
        registry = AgentRegistry()
        
        repr_str = repr(registry)
        
        assert 'AgentRegistry' in repr_str
        assert 'agents=' in repr_str
        assert 'cached=' in repr_str
