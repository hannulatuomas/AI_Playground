"""
Tests for Configuration Manager
"""

import pytest
import json
from pathlib import Path
import tempfile
import os

from src.config.config import Config


def test_config_initialization():
    """Test config initialization."""
    config = Config()
    assert config.config_path == "config.json"
    assert isinstance(config.config_data, dict)


def test_config_load_defaults():
    """Test loading default configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.json")
        config = Config(config_path)
        
        # Should load defaults when file doesn't exist
        assert config.load()
        assert config.get('ai.temperature') == 0.7
        assert config.get('database.path') == 'data/uaide.db'


def test_config_get_set():
    """Test getting and setting configuration values."""
    config = Config()
    config.load()
    
    # Test get
    assert config.get('ai.temperature') is not None
    assert config.get('nonexistent.key', 'default') == 'default'
    
    # Test set
    config.set('test.value', 123)
    assert config.get('test.value') == 123
    
    config.set('nested.deep.value', 'test')
    assert config.get('nested.deep.value') == 'test'


def test_config_save_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "test_config.json")
        
        # Create and save config
        config1 = Config(config_path)
        config1.load()
        config1.set('test.value', 'hello')
        assert config1.save()
        
        # Load in new instance
        config2 = Config(config_path)
        assert config2.load()
        assert config2.get('test.value') == 'hello'


def test_config_reset():
    """Test resetting configuration to defaults."""
    config = Config()
    config.load()
    
    config.set('custom.value', 'test')
    assert config.get('custom.value') == 'test'
    
    config.reset()
    assert config.get('custom.value') is None
    assert config.get('ai.temperature') == 0.7


def test_config_get_all():
    """Test getting all configuration."""
    config = Config()
    config.load()
    
    all_config = config.get_all()
    assert isinstance(all_config, dict)
    assert 'ai' in all_config
    assert 'database' in all_config
