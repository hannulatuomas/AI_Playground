
"""
Unit tests for LLM Router.

Tests the LLM routing system for managing multiple LLM providers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestLLMRouter:
    """Test suite for LLM Router."""
    
    @pytest.fixture
    def mock_ollama(self):
        """Mock Ollama module and its functions."""
        with patch('core.llm_router.ollama') as mock_ollama:
            # Mock ollama.list() for health checks
            mock_ollama.list.return_value = {
                'models': [
                    {'name': 'llama3.2:3b'},
                    {'name': 'codellama:7b'}
                ]
            }
            
            # Mock ollama.chat() for queries
            mock_ollama.chat.return_value = {
                'message': {'content': 'Mock Ollama response'},
                'done': True
            }
            
            yield mock_ollama
    
    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI module and client."""
        with patch('core.llm_router.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='Mock OpenAI response'))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            
            yield mock_openai_class
    
    @pytest.fixture
    def llm_router(self, app_config, mock_ollama, mock_openai):
        """Create an LLM router for testing with mocked providers."""
        from core.llm_router import LLMRouter
        
        # Patch the OllamaManager to avoid circular import issues
        with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
            router = LLMRouter(config=app_config)
            return router
    
    def test_initialization(self, llm_router):
        """Test LLM router initialization."""
        assert llm_router is not None
        assert llm_router.config is not None
        assert llm_router.providers is not None
    
    def test_query_success(self, llm_router, mock_ollama):
        """Test successful LLM query."""
        result = llm_router.query(
            prompt="Test prompt",
            model="llama3.2:3b"
        )
        
        assert result is not None
        assert 'response' in result
        assert result['response'] == 'Mock Ollama response'
        assert 'provider' in result
        assert 'model' in result
    
    def test_query_with_temperature(self, llm_router, mock_ollama):
        """Test query with custom temperature."""
        result = llm_router.query(
            prompt="Test prompt",
            temperature=0.9
        )
        
        assert result is not None
        assert 'response' in result
        
        # Verify temperature was passed to ollama.chat
        mock_ollama.chat.assert_called()
        call_kwargs = mock_ollama.chat.call_args[1]
        assert call_kwargs['options']['temperature'] == 0.9
    
    def test_query_with_max_tokens(self, llm_router, mock_ollama):
        """Test query with max tokens limit."""
        result = llm_router.query(
            prompt="Test prompt",
            max_tokens=1000
        )
        
        assert result is not None
        assert 'response' in result
    
    def test_is_available(self, llm_router, mock_ollama):
        """Test checking if LLM is available."""
        result = llm_router.is_available()
        
        assert isinstance(result, bool)
        assert result is True  # Should be True because mock_ollama.list() succeeds
    
    def test_get_model(self, llm_router):
        """Test getting current model."""
        model = llm_router.get_model()
        
        assert model is not None
        assert isinstance(model, str)
        assert model == 'llama3.2:3b'  # From app_config fixture
    
    def test_fallback_to_openai(self, app_config, mock_openai):
        """Test fallback to OpenAI when Ollama unavailable."""
        from core.llm_router import LLMRouter
        
        # Mock ollama to fail
        with patch('core.llm_router.ollama') as mock_ollama:
            mock_ollama.list.side_effect = Exception("Ollama not available")
            mock_ollama.chat.side_effect = Exception("Ollama not available")
            
            with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
                router = LLMRouter(config=app_config)
                
                # Query should fallback to OpenAI
                result = router.query("Test prompt")
                
                # Should succeed with OpenAI
                assert result is not None
                assert 'response' in result
                assert result['response'] == 'Mock OpenAI response'
                assert result['provider'] == 'openai'


@pytest.mark.unit
class TestLLMRouterModelSelection:
    """Test suite for LLM Router model selection."""
    
    @pytest.fixture
    def mock_ollama(self):
        """Mock Ollama module."""
        with patch('core.llm_router.ollama') as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.2:3b'}]}
            mock_ollama.chat.return_value = {
                'message': {'content': 'Mock response'},
                'done': True
            }
            yield mock_ollama
    
    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI module."""
        with patch('core.llm_router.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='Mock response'))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            yield mock_openai_class
    
    @pytest.fixture
    def router_with_models(self, app_config, mock_ollama, mock_openai):
        """Create router with multiple models configured."""
        from core.llm_router import LLMRouter
        
        with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
            return LLMRouter(config=app_config)
    
    def test_select_model_by_task(self, router_with_models):
        """Test selecting model based on task type."""
        # This tests the model selection logic
        model = router_with_models.get_model()
        
        assert model is not None
        assert isinstance(model, str)
        assert model == 'llama3.2:3b'  # From app_config


@pytest.mark.unit
class TestLLMRouterErrorHandling:
    """Test suite for LLM Router error handling."""
    
    @pytest.fixture
    def mock_ollama(self):
        """Mock Ollama module."""
        with patch('core.llm_router.ollama') as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.2:3b'}]}
            mock_ollama.chat.return_value = {
                'message': {'content': 'Mock response'},
                'done': True
            }
            yield mock_ollama
    
    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI module."""
        with patch('core.llm_router.OpenAI') as mock_openai_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='Mock fallback response'))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_class.return_value = mock_client
            yield mock_openai_class
    
    @pytest.fixture
    def router(self, app_config, mock_ollama, mock_openai):
        """Create router for error testing."""
        from core.llm_router import LLMRouter
        
        with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
            return LLMRouter(config=app_config)
    
    def test_query_with_invalid_model(self, app_config, mock_openai):
        """Test query with invalid model."""
        from core.llm_router import LLMRouter
        from core.llm_router import ConnectionError
        
        # Mock ollama to fail with invalid model
        with patch('core.llm_router.ollama') as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.2:3b'}]}
            mock_ollama.chat.side_effect = Exception("Model not found")
            
            with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
                router = LLMRouter(config=app_config)
                
                # Query with invalid model should fallback to OpenAI
                result = router.query(
                    prompt="Test",
                    model="nonexistent_model"
                )
                
                # Should handle error by falling back to OpenAI
                assert result is not None
                assert 'response' in result
                assert result['provider'] == 'openai'
    
    def test_query_timeout(self, app_config, mock_openai):
        """Test query with timeout."""
        from core.llm_router import LLMRouter
        
        # Mock ollama to timeout
        with patch('core.llm_router.ollama') as mock_ollama:
            mock_ollama.list.return_value = {'models': [{'name': 'llama3.2:3b'}]}
            mock_ollama.chat.side_effect = TimeoutError("Timeout")
            
            with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
                router = LLMRouter(config=app_config)
                
                # Query with timeout should fallback to OpenAI
                result = router.query(
                    prompt="Test",
                    timeout=1
                )
                
                # Should handle timeout by falling back
                assert result is not None
                assert 'response' in result
                assert result['provider'] == 'openai'


@pytest.mark.unit
class TestLlamaCppProvider:
    """Test suite for Llama-cpp provider."""
    
    @pytest.fixture
    def mock_llamacpp(self):
        """Mock Llama-cpp module and its classes."""
        with patch('core.llm_router.Llama') as mock_llama_class:
            mock_model = Mock()
            
            # Mock model generation
            mock_model.return_value = {
                'choices': [
                    {'text': 'Mock Llama-cpp response'}
                ],
                'usage': {'total_tokens': 50}
            }
            
            # Mock metadata
            mock_model.metadata = {'model_name': 'test_model.gguf'}
            
            mock_llama_class.return_value = mock_model
            
            yield mock_llama_class
    
    @pytest.fixture
    def mock_llamacpp_manager(self):
        """Mock LlamaCpp manager."""
        with patch('core.llm_router.LlamaCppProvider._get_llamacpp_manager') as mock_manager_getter:
            mock_manager = Mock()
            
            # Mock health check
            mock_manager.health_check.return_value = {
                'success': True,
                'message': 'Llama-cpp is available',
                'data': {
                    'status': 'available',
                    'model_configured': True,
                    'model_loaded': False
                }
            }
            
            # Mock is_model_loaded
            mock_manager.execute.side_effect = lambda op, ctx: {
                'is_model_loaded': {
                    'success': True,
                    'data': {'loaded': True, 'model_path': '/models/test.gguf'}
                },
                'generate': {
                    'success': True,
                    'message': 'Generation successful',
                    'data': {
                        'status': 'success',
                        'generated_text': 'Mock Llama-cpp response',
                        'prompt_length': len(ctx.get('prompt', '')),
                        'response_length': 27
                    }
                }
            }.get(op, {'success': False})
            
            mock_manager_getter.return_value = mock_manager
            
            yield mock_manager
    
    @pytest.fixture
    def llamacpp_router(self, app_config, mock_llamacpp, mock_llamacpp_manager):
        """Create an LLM router with llama-cpp provider for testing."""
        from core.llm_router import LLMRouter
        
        # Configure to use llama-cpp as primary
        app_config.fallback.primary_provider = "llamacpp"
        app_config.llamacpp.model_path = "/models/test.gguf"
        
        # Disable other providers to test llama-cpp specifically
        with patch('core.llm_router.ollama', None), \
             patch('core.llm_router.OpenAI', None):
            router = LLMRouter(config=app_config)
            return router
    
    def test_llamacpp_initialization(self, llamacpp_router):
        """Test Llama-cpp provider initialization."""
        assert llamacpp_router is not None
        assert llamacpp_router.config is not None
        assert llamacpp_router.providers is not None
    
    def test_llamacpp_query_success(self, llamacpp_router):
        """Test successful Llama-cpp query."""
        result = llamacpp_router.query(
            prompt="Test prompt",
            model="test.gguf"
        )
        
        assert result is not None
        assert 'response' in result
        assert result['response'] == 'Mock Llama-cpp response'
        assert 'provider' in result
        assert result['provider'] == 'llamacpp'
        assert 'model' in result
    
    def test_llamacpp_with_custom_params(self, llamacpp_router):
        """Test Llama-cpp query with custom parameters."""
        result = llamacpp_router.query(
            prompt="Test prompt",
            temperature=0.8,
            max_tokens=1024
        )
        
        assert result is not None
        assert 'response' in result
    
    def test_llamacpp_fallback_to_ollama(self, app_config, mock_llamacpp):
        """Test fallback from Llama-cpp to Ollama."""
        from core.llm_router import LLMRouter
        
        # Configure llama-cpp as primary, ollama as fallback
        app_config.fallback.primary_provider = "llamacpp"
        app_config.fallback.fallback_provider = "ollama"
        
        # Mock llama-cpp to fail
        with patch('core.llm_router.LlamaCppProvider._get_llamacpp_manager') as mock_manager:
            mock_manager.return_value = None  # Simulate manager failure
            
            # Mock ollama to succeed
            with patch('core.llm_router.ollama') as mock_ollama:
                mock_ollama.list.return_value = {'models': [{'name': 'llama3.2:3b'}]}
                mock_ollama.chat.return_value = {
                    'message': {'content': 'Mock Ollama fallback response'},
                    'done': True
                }
                
                with patch('core.llm_router.OllamaProvider._get_ollama_manager', return_value=None):
                    router = LLMRouter(config=app_config)
                    
                    # Query should fallback to Ollama
                    result = router.query("Test prompt")
                    
                    # Should succeed with Ollama
                    assert result is not None
                    assert 'response' in result
                    assert result['response'] == 'Mock Ollama fallback response'
                    assert result['provider'] == 'ollama'


@pytest.mark.unit
class TestLlamaCppManager:
    """Test suite for LlamaCpp Manager."""
    
    @pytest.fixture
    def mock_llama(self):
        """Mock Llama class from llama-cpp-python."""
        with patch('tools.llamacpp_manager.Llama') as mock_llama_class:
            mock_model = Mock()
            
            # Mock model call (generation)
            mock_model.return_value = {
                'choices': [
                    {'text': 'Generated text from model'}
                ],
                'usage': {'total_tokens': 100}
            }
            
            mock_llama_class.return_value = mock_model
            
            yield mock_llama_class
    
    @pytest.fixture
    def llamacpp_manager(self, mock_llama):
        """Create a LlamaCpp manager for testing."""
        from tools.llamacpp_manager import LlamaCppManager
        
        config = {
            'llamacpp': {
                'model_path': '/models/test.gguf',
                'context_size': 2048,
                'n_threads': 4,
                'n_gpu_layers': 0,
                'verbose': False,
                'models_dir': '/models'
            }
        }
        
        return LlamaCppManager(config=config)
    
    def test_health_check_with_model_loaded(self, llamacpp_manager):
        """Test health check when model is loaded."""
        # Mock a loaded model
        llamacpp_manager._model = Mock()
        llamacpp_manager._loaded_model_path = '/models/test.gguf'
        
        result = llamacpp_manager.health_check()
        
        assert result['success'] is True
        assert result['data']['model_loaded'] is True
    
    def test_health_check_without_model(self, llamacpp_manager):
        """Test health check when no model is loaded."""
        result = llamacpp_manager.health_check()
        
        assert result['success'] is True
        assert result['data']['model_loaded'] is False
    
    def test_load_model_success(self, llamacpp_manager, tmp_path):
        """Test successful model loading."""
        # Create a dummy model file
        model_file = tmp_path / "test.gguf"
        model_file.write_text("dummy model content")
        
        result = llamacpp_manager.load_model(str(model_file))
        
        assert result['success'] is True
        assert llamacpp_manager._model is not None
        assert llamacpp_manager._loaded_model_path == str(model_file)
    
    def test_load_model_not_found(self, llamacpp_manager):
        """Test loading a non-existent model."""
        result = llamacpp_manager.load_model('/nonexistent/model.gguf')
        
        assert result['success'] is False
        assert 'not found' in result['message'].lower()
    
    def test_unload_model(self, llamacpp_manager):
        """Test unloading a model."""
        # Mock a loaded model
        llamacpp_manager._model = Mock()
        llamacpp_manager._loaded_model_path = '/models/test.gguf'
        
        result = llamacpp_manager.unload_model()
        
        assert result['success'] is True
        assert llamacpp_manager._model is None
        assert llamacpp_manager._loaded_model_path is None
    
    def test_generate_with_loaded_model(self, llamacpp_manager):
        """Test generation with a loaded model."""
        # Mock a loaded model
        mock_model = Mock()
        mock_model.return_value = {
            'choices': [{'text': 'Generated response'}],
            'usage': {'total_tokens': 50}
        }
        llamacpp_manager._model = mock_model
        llamacpp_manager._loaded_model_path = '/models/test.gguf'
        
        result = llamacpp_manager.generate('Test prompt')
        
        assert result['success'] is True
        assert result['data']['generated_text'] == 'Generated response'
    
    def test_generate_without_model(self, llamacpp_manager):
        """Test generation when no model is loaded."""
        # Try to generate without a loaded model
        result = llamacpp_manager.generate('Test prompt')
        
        # Should fail or attempt to auto-load
        assert 'success' in result
