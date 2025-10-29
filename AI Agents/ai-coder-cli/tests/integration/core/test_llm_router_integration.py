"""
Comprehensive integration tests for LLM Router with provider interactions.

Tests real integration between:
- LLMRouter and provider implementations (Ollama, OpenAI, LlamaCpp)
- Provider fallback mechanisms
- Query routing and provider selection
- Provider availability checking
- Error handling and retry logic

Note: These tests use mocks to avoid external dependencies while still
testing the integration logic between components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

from core.llm_router import (
    LLMRouter,
    LLMProviderError,
    BaseLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    ProviderType
)
from core.config import AppConfig


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def test_config():
    """Create a test configuration."""
    config = AppConfig()
    
    # Configure Ollama settings
    config.ollama.host = "http://localhost"
    config.ollama.port = 11434
    config.ollama.timeout = 30
    config.models.ollama_default = "llama3.2:3b"
    
    # Configure OpenAI settings (disabled by not setting api_key)
    config.openai.api_key = None  # Disabled
    config.openai.base_url = "https://api.openai.com/v1"
    config.models.openai_default = "gpt-3.5-turbo"
    
    # Configure Llama-cpp settings
    config.llamacpp.model_path = None  # Disabled
    config.models.llamacpp_default = "llama-3.2-3b"
    
    # Configure fallback and retry settings
    config.fallback.enabled = True
    config.fallback.primary_provider = "ollama"
    config.fallback.fallback_provider = "openai"
    config.fallback.secondary_fallback_provider = None
    config.retry.max_retries = 2
    
    return config


@pytest.fixture
def mock_ollama_provider():
    """Mock Ollama provider as available."""
    with patch('core.llm_router.OllamaProvider') as mock_class:
        mock_provider = Mock(spec=OllamaProvider)
        mock_provider.is_available.return_value = True
        mock_provider.get_provider_type.return_value = ProviderType.OLLAMA
        mock_provider.query.return_value = "Ollama response"
        mock_class.return_value = mock_provider
        yield mock_provider


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider as available."""
    with patch('core.llm_router.OpenAIProvider') as mock_class:
        mock_provider = Mock(spec=OpenAIProvider)
        mock_provider.is_available.return_value = True
        mock_provider.get_provider_type.return_value = ProviderType.OPENAI
        mock_provider.query.return_value = "OpenAI response"
        mock_class.return_value = mock_provider
        yield mock_provider


# =============================================================================
# LLMRouter Initialization Integration Tests
# =============================================================================

class TestLLMRouterInitializationIntegration:
    """Integration tests for LLM Router initialization with providers."""
    
    def test_router_initializes_with_ollama(self, test_config, mock_ollama_provider):
        """Test router initialization with Ollama provider."""
        # Also need to mock LlamaCpp and OpenAI to avoid initialization errors
        with patch('core.llm_router.LlamaCppProvider'), \
             patch('core.llm_router.OpenAIProvider'):
            
            router = LLMRouter(test_config)
            
            assert router.config == test_config
            assert router.providers is not None
            assert ProviderType.OLLAMA in router.providers
            mock_ollama_provider.is_available.assert_called()
    
    def test_router_initializes_with_openai(self, test_config, mock_openai_provider):
        """Test router initialization with OpenAI provider."""
        test_config.openai.api_key = "test-key"
        
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.LlamaCppProvider'):
            
            mock_ollama.return_value.is_available.return_value = False
            
            router = LLMRouter(test_config)
            
            assert router.providers is not None
            assert ProviderType.OPENAI in router.providers
    
    def test_router_initializes_with_multiple_providers(
        self, test_config, mock_ollama_provider, mock_openai_provider
    ):
        """Test router initialization with multiple providers."""
        test_config.openai.api_key = "test-key"
        
        with patch('core.llm_router.LlamaCppProvider'):
            router = LLMRouter(test_config)
        
        available = router.get_available_providers()
        assert 'ollama' in available
        assert 'openai' in available
    
    def test_router_handles_unavailable_providers(self, test_config):
        """Test router behavior when all providers are unavailable."""
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # Make all providers unavailable
            for mock_provider_class in [mock_ollama, mock_openai, mock_llamacpp]:
                mock = Mock()
                mock.is_available.return_value = False
                mock_provider_class.return_value = mock
            
            router = LLMRouter(test_config)
            
            available = router.get_available_providers()
            assert len(available) == 0
    
    def test_router_handles_provider_initialization_errors(self, test_config):
        """Test router gracefully handles provider initialization errors."""
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            # Simulate Ollama initialization error
            mock_ollama.side_effect = Exception("Connection failed")
            
            # Should not raise, just log warning
            router = LLMRouter(test_config)
            
            assert router is not None
            assert router.providers[ProviderType.OLLAMA] is None


# =============================================================================
# Provider Availability Integration Tests
# =============================================================================

class TestProviderAvailabilityIntegration:
    """Integration tests for provider availability checking."""
    
    def test_get_available_providers_ollama_only(self, test_config, mock_ollama_provider):
        """Test getting available providers with only Ollama."""
        with patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # Make other providers unavailable
            for mock_class in [mock_openai, mock_llamacpp]:
                mock = Mock()
                mock.is_available.return_value = False
                mock_class.return_value = mock
            
            router = LLMRouter(test_config)
            providers = router.get_available_providers()
        
        assert 'ollama' in providers
        assert isinstance(providers, list)
    
    def test_get_available_providers_multiple(self, test_config, mock_ollama_provider, mock_openai_provider):
        """Test getting available providers with multiple providers."""
        test_config.openai.api_key = "test-key"
        
        with patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            mock = Mock()
            mock.is_available.return_value = False
            mock_llamacpp.return_value = mock
            
            router = LLMRouter(test_config)
            providers = router.get_available_providers()
        
        # Both Ollama and OpenAI should be available
        assert 'ollama' in providers
        assert 'openai' in providers
        assert len(providers) == 2
    
    def test_get_available_providers_none(self, test_config):
        """Test getting available providers when none are available."""
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # Make all providers unavailable
            for mock_class in [mock_ollama, mock_openai, mock_llamacpp]:
                mock = Mock()
                mock.is_available.return_value = False
                mock_class.return_value = mock
            
            router = LLMRouter(test_config)
            providers = router.get_available_providers()
        
        assert len(providers) == 0
    
    def test_is_available_specific_provider(self, test_config, mock_ollama_provider):
        """Test checking availability of specific provider."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            assert router.is_available('ollama') is True
            assert router.is_available('openai') is False
    
    def test_is_available_any_provider(self, test_config, mock_ollama_provider):
        """Test checking if any provider is available."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            assert router.is_available() is True  # At least Ollama is available


# =============================================================================
# Query Routing Integration Tests
# =============================================================================

class TestQueryRoutingIntegration:
    """Integration tests for query routing to providers."""
    
    def test_query_routes_to_primary_provider(self, test_config, mock_ollama_provider):
        """Test that queries route to primary provider (Ollama) by default."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            result = router.query(prompt="What is AI?")
            
            assert result['provider'] == 'ollama'
            assert result['response'] == 'Ollama response'
            assert result['model'] == test_config.models.ollama_default
            mock_ollama_provider.query.assert_called_once()
    
    def test_query_routes_to_specified_provider(self, test_config, mock_ollama_provider, mock_openai_provider):
        """Test that queries route to explicitly specified provider."""
        test_config.openai.api_key = "test-key"
        
        with patch('core.llm_router.LlamaCppProvider'):
            router = LLMRouter(test_config)
            result = router.query(prompt="What is AI?", provider="openai")
        
        assert result['provider'] == 'openai'
        assert result['response'] == 'OpenAI response'
        mock_openai_provider.query.assert_called_once()
        # Ollama should not be called when provider is explicitly specified
        mock_ollama_provider.query.assert_not_called()
    
    def test_query_with_model_override(self, test_config, mock_ollama_provider):
        """Test querying with model override."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            result = router.query(prompt="Test", model="custom-model")
            
            # Verify model was passed to provider
            call_args = mock_ollama_provider.query.call_args
            assert call_args[0][1] == "custom-model"  # Second positional arg
            assert result['model'] == "custom-model"
    
    def test_query_with_additional_parameters(self, test_config, mock_ollama_provider):
        """Test querying with additional parameters like temperature."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            result = router.query(prompt="Test", temperature=0.7, max_tokens=100)
            
            # Verify parameters were passed to provider
            call_args = mock_ollama_provider.query.call_args
            assert 'temperature' in call_args[1]
            assert call_args[1]['temperature'] == 0.7
            assert 'max_tokens' in call_args[1]
    
    def test_query_returns_proper_format(self, test_config, mock_ollama_provider):
        """Test that query returns properly formatted result."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            result = router.query(prompt="Test query")
            
            # Verify result format
            assert isinstance(result, dict)
            assert 'response' in result
            assert 'provider' in result
            assert 'model' in result


# =============================================================================
# Provider Fallback Integration Tests
# =============================================================================

class TestProviderFallbackIntegration:
    """Integration tests for provider fallback mechanisms."""
    
    def test_fallback_to_openai_when_ollama_fails(self, test_config):
        """Test fallback to OpenAI when Ollama fails."""
        test_config.openai.api_key = "test-key"
        test_config.fallback.enabled = True
        
        with patch('core.llm_router.OllamaProvider') as mock_ollama_class, \
             patch('core.llm_router.OpenAIProvider') as mock_openai_class, \
             patch('core.llm_router.LlamaCppProvider'):
            
            # Ollama is available but query fails
            mock_ollama = Mock()
            mock_ollama.is_available.return_value = True
            mock_ollama.get_provider_type.return_value = ProviderType.OLLAMA
            mock_ollama.query.side_effect = LLMProviderError("Ollama connection error")
            mock_ollama_class.return_value = mock_ollama
            
            # OpenAI is available and works
            mock_openai = Mock()
            mock_openai.is_available.return_value = True
            mock_openai.get_provider_type.return_value = ProviderType.OPENAI
            mock_openai.query.return_value = "OpenAI fallback response"
            mock_openai_class.return_value = mock_openai
            
            router = LLMRouter(test_config)
            result = router.query(prompt="Test query")
        
        # Should fallback to OpenAI
        assert result['provider'] == 'openai'
        assert result['response'] == 'OpenAI fallback response'
        mock_ollama.query.assert_called_once()
        mock_openai.query.assert_called_once()
    
    def test_fallback_chain_with_secondary(self, test_config):
        """Test fallback chain with secondary fallback provider."""
        test_config.openai.api_key = "test-key"
        test_config.llamacpp.model_path = "/path/to/model.gguf"
        test_config.fallback.enabled = True
        test_config.fallback.primary_provider = "ollama"
        test_config.fallback.fallback_provider = "openai"
        test_config.fallback.secondary_fallback_provider = "llamacpp"
        
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # Ollama fails
            ollama = Mock()
            ollama.is_available.return_value = True
            ollama.query.side_effect = LLMProviderError("Ollama error")
            mock_ollama.return_value = ollama
            
            # OpenAI fails
            openai = Mock()
            openai.is_available.return_value = True
            openai.query.side_effect = LLMProviderError("OpenAI error")
            mock_openai.return_value = openai
            
            # LlamaCpp succeeds
            llamacpp = Mock()
            llamacpp.is_available.return_value = True
            llamacpp.query.return_value = "LlamaCpp response"
            mock_llamacpp.return_value = llamacpp
            
            router = LLMRouter(test_config)
            result = router.query(prompt="Test")
        
        # Should fallback through chain to LlamaCpp
        assert result['provider'] == 'llamacpp'
        assert result['response'] == 'LlamaCpp response'
    
    def test_no_fallback_when_disabled(self, test_config):
        """Test that fallback doesn't occur when disabled."""
        test_config.fallback.enabled = False
        
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            mock_provider = Mock()
            mock_provider.is_available.return_value = True
            mock_provider.query.side_effect = LLMProviderError("Ollama error")
            mock_ollama.return_value = mock_provider
            
            router = LLMRouter(test_config)
            
            with pytest.raises(LLMProviderError):
                router.query(prompt="Test")
    
    def test_no_fallback_with_explicit_provider(self, test_config):
        """Test that fallback doesn't occur when provider is explicitly specified."""
        test_config.openai.api_key = "test-key"
        test_config.fallback.enabled = True
        
        with patch('core.llm_router.OllamaProvider'), \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider'):
            
            # OpenAI is specified but fails
            openai = Mock()
            openai.is_available.return_value = True
            openai.query.side_effect = LLMProviderError("OpenAI error")
            mock_openai.return_value = openai
            
            router = LLMRouter(test_config)
            
            # Should not fallback when provider is explicit
            with pytest.raises(LLMProviderError):
                router.query(prompt="Test", provider="openai")


# =============================================================================
# Error Handling Integration Tests
# =============================================================================

class TestErrorHandlingIntegration:
    """Integration tests for error handling."""
    
    def test_router_handles_provider_errors(self, test_config, mock_ollama_provider):
        """Test that router handles provider errors gracefully."""
        mock_ollama_provider.query.side_effect = LLMProviderError("Provider connection error")
        
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            with pytest.raises(LLMProviderError):
                router.query(prompt="Test")
    
    def test_router_raises_error_when_no_providers_available(self, test_config):
        """Test that router raises error when no providers are available."""
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # All providers unavailable
            for mock_class in [mock_ollama, mock_openai, mock_llamacpp]:
                mock = Mock()
                mock.is_available.return_value = False
                mock_class.return_value = mock
            
            router = LLMRouter(test_config)
            
            with pytest.raises(LLMProviderError) as exc_info:
                router.query(prompt="Test")
            
            error_msg = str(exc_info.value).lower()
            assert "no llm providers are available" in error_msg or "provider" in error_msg
    
    def test_router_handles_invalid_provider_name(self, test_config, mock_ollama_provider):
        """Test handling of invalid provider name."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            with pytest.raises((LLMProviderError, ValueError)) as exc_info:
                router.query(prompt="Test", provider="invalid_provider")
            
            # Should raise error for invalid provider
            assert exc_info.value is not None
    
    def test_error_message_provides_helpful_guidance(self, test_config):
        """Test that error messages provide helpful guidance."""
        with patch('core.llm_router.OllamaProvider') as mock_ollama, \
             patch('core.llm_router.OpenAIProvider') as mock_openai, \
             patch('core.llm_router.LlamaCppProvider') as mock_llamacpp:
            
            # All providers unavailable
            for mock_class in [mock_ollama, mock_openai, mock_llamacpp]:
                mock = Mock()
                mock.is_available.return_value = False
                mock_class.return_value = mock
            
            router = LLMRouter(test_config)
            
            with pytest.raises(LLMProviderError) as exc_info:
                router.query(prompt="Test")
            
            error_msg = str(exc_info.value)
            # Should contain helpful information about how to configure providers
            assert len(error_msg) > 50  # Error message should be informative


# =============================================================================
# Model Management Integration Tests
# =============================================================================

class TestModelManagementIntegration:
    """Integration tests for model management."""
    
    def test_get_default_model_for_provider(self, test_config, mock_ollama_provider):
        """Test getting default model for a provider."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            model = router.get_model(provider="ollama")
            
            assert model == test_config.models.ollama_default
    
    def test_get_default_model_for_openai(self, test_config, mock_openai_provider):
        """Test getting default model for OpenAI."""
        test_config.openai.api_key = "test-key"
        
        with patch('core.llm_router.OllamaProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            model = router.get_model(provider="openai")
            
            assert model == test_config.models.openai_default
    
    def test_get_default_model_without_provider_uses_primary(self, test_config, mock_ollama_provider):
        """Test that get_model without provider uses primary provider."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            model = router.get_model()
            
            # Should return primary provider's default model
            assert model == test_config.models.ollama_default
    
    def test_invalid_provider_raises_error(self, test_config, mock_ollama_provider):
        """Test that invalid provider raises error."""
        with patch('core.llm_router.OpenAIProvider'), \
             patch('core.llm_router.LlamaCppProvider'):
            
            router = LLMRouter(test_config)
            
            with pytest.raises(ValueError):
                router.get_model(provider="invalid")
