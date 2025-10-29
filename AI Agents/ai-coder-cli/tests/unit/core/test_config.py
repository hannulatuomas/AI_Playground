
"""
Unit tests for Configuration System.

Tests the configuration loading and management.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import yaml


@pytest.mark.unit
class TestConfigLoader:
    """Test suite for Configuration Loader."""
    
    @pytest.fixture
    def config_loader(self):
        """Create a config loader for testing."""
        from core.config import ConfigLoader
        
        return ConfigLoader()
    
    def test_load_yaml_config(self, config_loader, temp_dir):
        """Test loading YAML configuration."""
        # Create a test config file
        config_file = temp_dir / "config.yaml"
        test_config = {
            'models': {'ollama_default': 'test-model'},
            'agents': {'max_concurrent': 5}
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(test_config, f)
        
        loaded_config = config_loader.load(str(config_file))
        
        assert loaded_config is not None
        assert loaded_config['models']['ollama_default'] == 'test-model'
    
    def test_load_nonexistent_file(self, config_loader):
        """Test loading non-existent config file."""
        result = config_loader.load('/nonexistent/config.yaml')
        
        # Should return default config or handle gracefully
        assert result is not None
    
    def test_get_config_value(self, config_loader):
        """Test getting specific config value."""
        # Assuming config is loaded
        value = config_loader.get('llm.default_model', default='llama3.2')
        
        assert value is not None
    
    def test_validate_config(self, config_loader, mock_config):
        """Test config validation."""
        is_valid = config_loader.validate(mock_config)
        
        assert isinstance(is_valid, bool)


@pytest.mark.unit
class TestConfigMerging:
    """Test suite for configuration merging."""
    
    @pytest.fixture
    def config_loader(self):
        """Create config loader for merge testing."""
        from core.config import ConfigLoader
        
        return ConfigLoader()
    
    def test_merge_configs(self, config_loader):
        """Test merging multiple configurations."""
        base_config = {'llm': {'model': 'base-model'}, 'agents': {}}
        override_config = {'llm': {'temperature': 0.8}}
        
        merged = config_loader.merge(base_config, override_config)
        
        assert merged['llm']['model'] == 'base-model'
        assert merged['llm']['temperature'] == 0.8
    
    def test_deep_merge(self, config_loader):
        """Test deep merging of nested configurations."""
        config1 = {'a': {'b': {'c': 1, 'd': 2}}}
        config2 = {'a': {'b': {'c': 3, 'e': 4}}}
        
        merged = config_loader.merge(config1, config2)
        
        assert merged['a']['b']['c'] == 3  # Overridden
        assert merged['a']['b']['d'] == 2  # Preserved
        assert merged['a']['b']['e'] == 4  # Added
