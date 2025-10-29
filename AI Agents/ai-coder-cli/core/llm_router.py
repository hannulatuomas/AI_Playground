
"""
LLM routing infrastructure for managing multiple LLM providers.

This module provides abstract base classes and concrete implementations for
different LLM providers (Ollama, OpenAI) with automatic fallback and retry logic.
Includes health checking and auto-start capabilities for Ollama.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum

try:
    import ollama
except ImportError:
    ollama = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from .config import AppConfig, RetryPolicy


logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Enumeration of supported LLM providers."""
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    OPENAI = "openai"


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class ConnectionError(LLMProviderError):
    """Raised when connection to provider fails."""
    pass


class AuthenticationError(LLMProviderError):
    """Raised when authentication with provider fails."""
    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded."""
    pass


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM provider implementations must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: AppConfig, retry_policy: RetryPolicy):
        """
        Initialize the LLM provider.
        
        Args:
            config: Application configuration
            retry_policy: Retry policy for failed requests
        """
        self.config = config
        self.retry_policy = retry_policy
        self._is_available = False
    
    @abstractmethod
    def query(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Send a query to the LLM and return the response.
        
        Args:
            prompt: The input prompt/query
            model: Optional model name override
            **kwargs: Additional provider-specific parameters
            
        Returns:
            The LLM's response as a string
            
        Raises:
            LLMProviderError: If the query fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and ready to accept requests.
        
        Returns:
            True if provider is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """
        Get the type of this provider.
        
        Returns:
            ProviderType enum value
        """
        pass
    
    def _retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """
        Execute a function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function return value
            
        Raises:
            LLMProviderError: If all retries fail
        """
        last_exception = None
        delay = self.retry_policy.initial_delay
        
        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.retry_policy.max_retries:
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.retry_policy.max_retries + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    delay = min(
                        delay * self.retry_policy.exponential_base,
                        self.retry_policy.max_delay
                    )
                else:
                    logger.error(f"All {self.retry_policy.max_retries + 1} attempts failed")
        
        raise LLMProviderError(f"Failed after {self.retry_policy.max_retries + 1} attempts") from last_exception


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation with health check and auto-start."""
    
    def __init__(self, config: AppConfig, retry_policy: RetryPolicy, auto_start: bool = True):
        """
        Initialize Ollama provider.
        
        Args:
            config: Application configuration
            retry_policy: Retry policy for failed requests
            auto_start: If True, attempt to start Ollama if not running
            
        Raises:
            ImportError: If ollama package is not installed
        """
        super().__init__(config, retry_policy)
        
        if ollama is None:
            raise ImportError(
                "ollama package is not installed. Install it with: pip install ollama"
            )
        
        self.client = None
        self._auto_start = auto_start
        self._ollama_manager = None
        self._initialize_client()
    
    def _get_ollama_manager(self):
        """Lazy-load Ollama manager to avoid circular imports."""
        if self._ollama_manager is None:
            try:
                from tools.ollama_manager import OllamaManager
                self._ollama_manager = OllamaManager(config=self.config.to_dict())
            except Exception as e:
                logger.warning(f"Could not initialize Ollama manager: {e}")
        return self._ollama_manager
    
    def _initialize_client(self) -> None:
        """Initialize the Ollama client with health check and auto-start."""
        try:
            # Ollama client uses environment or default host
            self.client = ollama
            
            # Perform health check
            health_result = self.health_check(auto_start=self._auto_start)
            
            if health_result['success']:
                self._is_available = True
                models = health_result.get('data', {}).get('models', [])
                logger.info(
                    f"Ollama provider initialized successfully. "
                    f"Models available: {len(models)}"
                )
            else:
                self._is_available = False
                logger.warning(
                    f"Ollama provider initialized but service is not available: "
                    f"{health_result.get('message')}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {e}")
            self._is_available = False
    
    def health_check(self, auto_start: bool = True) -> Dict[str, Any]:
        """
        Perform health check on Ollama service.
        
        Args:
            auto_start: If True, attempt to start Ollama if not running
            
        Returns:
            Dict with health check results
        """
        manager = self._get_ollama_manager()
        if manager:
            return manager.health_check(auto_start=auto_start)
        else:
            # Fallback to basic health check
            return self._basic_health_check()
    
    def _basic_health_check(self) -> Dict[str, Any]:
        """Basic health check without Ollama manager."""
        try:
            ollama.list()
            return {
                'success': True,
                'message': 'Ollama is running',
                'data': {'status': 'healthy'}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Ollama is not available: {str(e)}',
                'data': {'status': 'unhealthy', 'error': str(e)}
            }
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if Ollama is reachable, False otherwise
        """
        try:
            # Try to list models as a health check
            ollama.list()
            return True
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            # Try health check with auto-start if enabled
            if self._auto_start:
                health_result = self.health_check(auto_start=True)
                return health_result['success']
            return False
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OLLAMA
    
    def query(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Query Ollama with the given prompt.
        
        Args:
            prompt: The input prompt
            model: Optional model name (defaults to config setting)
            **kwargs: Additional parameters (temperature, etc.)
            
        Returns:
            The model's response
            
        Raises:
            ConnectionError: If connection to Ollama fails
            LLMProviderError: If query fails
        """
        if not self.is_available():
            raise ConnectionError("Ollama service is not available")
        
        model = model or self.config.models.ollama_default
        
        def _query():
            try:
                # Build options
                options = {
                    'temperature': kwargs.get('temperature', self.config.models.temperature),
                }
                
                logger.debug(f"Querying Ollama model '{model}' with prompt length {len(prompt)}")
                
                response = ollama.chat(
                    model=model,
                    messages=[
                        {'role': 'user', 'content': prompt}
                    ],
                    options=options
                )
                
                result = response['message']['content']
                logger.info(f"Ollama query successful (response length: {len(result)})")
                return result
                
            except Exception as e:
                logger.error(f"Ollama query failed: {e}")
                raise ConnectionError(f"Ollama query failed: {e}") from e
        
        return self._retry_with_backoff(_query)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, config: AppConfig, retry_policy: RetryPolicy):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Application configuration
            retry_policy: Retry policy for failed requests
            
        Raises:
            ImportError: If openai package is not installed
            AuthenticationError: If API key is not configured
        """
        super().__init__(config, retry_policy)
        
        if OpenAI is None:
            raise ImportError(
                "openai package is not installed. Install it with: pip install openai"
            )
        
        if not self.config.openai.api_key:
            raise AuthenticationError("OpenAI API key is not configured")
        
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the OpenAI client."""
        try:
            self.client = OpenAI(
                api_key=self.config.openai.api_key,
                base_url=self.config.openai.base_url,
                timeout=self.config.openai.timeout
            )
            self._is_available = True
            logger.info("OpenAI provider initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            self._is_available = False
    
    def is_available(self) -> bool:
        """
        Check if OpenAI provider is available.
        
        Returns:
            True if client is initialized with valid credentials
        """
        return self._is_available and self.client is not None
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OPENAI
    
    def query(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Query OpenAI with the given prompt.
        
        Args:
            prompt: The input prompt
            model: Optional model name (defaults to config setting)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The model's response
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            LLMProviderError: If query fails
        """
        if not self.is_available():
            raise ConnectionError("OpenAI provider is not available")
        
        model = model or self.config.models.openai_default
        
        def _query():
            try:
                # Build parameters
                params = {
                    'model': model,
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': kwargs.get('temperature', self.config.models.temperature),
                }
                
                # Add max_tokens if specified
                max_tokens = kwargs.get('max_tokens', self.config.openai.max_tokens)
                if max_tokens:
                    params['max_tokens'] = max_tokens
                
                logger.debug(f"Querying OpenAI model '{model}' with prompt length {len(prompt)}")
                
                response = self.client.chat.completions.create(**params)
                
                result = response.choices[0].message.content
                logger.info(f"OpenAI query successful (response length: {len(result)})")
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if 'api key' in error_msg or 'authentication' in error_msg or '401' in error_msg:
                    raise AuthenticationError(f"OpenAI authentication failed: {e}") from e
                elif 'rate limit' in error_msg or '429' in error_msg:
                    raise RateLimitError(f"OpenAI rate limit exceeded: {e}") from e
                else:
                    logger.error(f"OpenAI query failed: {e}")
                    raise LLMProviderError(f"OpenAI query failed: {e}") from e
        
        return self._retry_with_backoff(_query)


class LlamaCppProvider(BaseLLMProvider):
    """Llama-cpp LLM provider implementation with local model management."""
    
    def __init__(self, config: AppConfig, retry_policy: RetryPolicy):
        """
        Initialize Llama-cpp provider.
        
        Args:
            config: Application configuration
            retry_policy: Retry policy for failed requests
            
        Raises:
            ImportError: If llama-cpp-python package is not installed
        """
        super().__init__(config, retry_policy)
        
        if Llama is None:
            raise ImportError(
                "llama-cpp-python package is not installed. Install it with: pip install llama-cpp-python"
            )
        
        self.model = None
        self._llamacpp_manager = None
        self._initialize_model()
    
    def _get_llamacpp_manager(self):
        """Lazy-load Llama-cpp manager to avoid circular imports."""
        if self._llamacpp_manager is None:
            try:
                from tools.llamacpp_manager import LlamaCppManager
                self._llamacpp_manager = LlamaCppManager(config=self.config.model_dump())
            except Exception as e:
                logger.warning(f"Could not initialize Llama-cpp manager: {e}")
        return self._llamacpp_manager
    
    def _initialize_model(self) -> None:
        """Initialize the Llama-cpp model with health check."""
        try:
            manager = self._get_llamacpp_manager()
            
            if manager:
                # Perform health check
                health_result = manager.health_check()
                
                if health_result['success']:
                    self._is_available = True
                    model_info = health_result.get('data', {})
                    
                    if model_info.get('model_loaded'):
                        logger.info(
                            f"Llama-cpp provider initialized successfully. "
                            f"Model loaded: {model_info.get('loaded_model')}"
                        )
                    else:
                        logger.info(
                            "Llama-cpp provider initialized. "
                            "Model not loaded yet (will auto-load on first query)"
                        )
                else:
                    self._is_available = False
                    logger.warning(
                        f"Llama-cpp provider initialized but not fully available: "
                        f"{health_result.get('message')}"
                    )
            else:
                self._is_available = False
                logger.error("Failed to initialize Llama-cpp manager")
                
        except Exception as e:
            logger.error(f"Failed to initialize Llama-cpp provider: {e}")
            self._is_available = False
    
    def is_available(self) -> bool:
        """
        Check if Llama-cpp provider is available.
        
        Returns:
            True if provider is available, False otherwise
        """
        manager = self._get_llamacpp_manager()
        if not manager:
            return False
        
        health_result = manager.health_check()
        return health_result['success']
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.LLAMACPP
    
    def query(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        """
        Query Llama-cpp with the given prompt.
        
        Args:
            prompt: The input prompt
            model: Optional model path/name (defaults to config setting)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            The model's response
            
        Raises:
            ConnectionError: If model cannot be loaded
            LLMProviderError: If query fails
        """
        manager = self._get_llamacpp_manager()
        if not manager:
            raise ConnectionError("Llama-cpp manager is not available")
        
        def _query():
            try:
                # Check if model is loaded, if not try to load it
                status_result = manager.execute('is_model_loaded', {})
                
                if not status_result.get('data', {}).get('loaded'):
                    # Try to load the model
                    model_path = model or self.config.llamacpp.model_path
                    
                    if not model_path:
                        raise ConnectionError(
                            "No model is loaded and no model_path is configured. "
                            "Please set llamacpp.model_path in config or provide model parameter"
                        )
                    
                    load_result = manager.execute('load_model', {'model_path': model_path})
                    
                    if not load_result['success']:
                        raise ConnectionError(
                            f"Failed to load model: {load_result['message']}"
                        )
                
                # Build generation config
                gen_config = {
                    'prompt': prompt,
                    'temperature': kwargs.get('temperature', self.config.models.temperature),
                    'max_tokens': kwargs.get('max_tokens', 512),
                    'top_p': kwargs.get('top_p', 0.95),
                    'top_k': kwargs.get('top_k', 40),
                }
                
                logger.debug(f"Querying Llama-cpp with prompt length {len(prompt)}")
                
                # Generate response
                result = manager.execute('generate', gen_config)
                
                if not result['success']:
                    raise LLMProviderError(f"Generation failed: {result['message']}")
                
                generated_text = result['data']['generated_text']
                logger.info(f"Llama-cpp query successful (response length: {len(generated_text)})")
                
                return generated_text
                
            except Exception as e:
                logger.error(f"Llama-cpp query failed: {e}")
                raise ConnectionError(f"Llama-cpp query failed: {e}") from e
        
        return self._retry_with_backoff(_query)


class LLMRouter:
    """
    LLM routing system with automatic fallback and retry logic.
    
    Routes queries to the primary provider and falls back to secondary provider
    on failure if configured.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the LLM router.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.providers: Dict[ProviderType, Optional[BaseLLMProvider]] = {
            ProviderType.OLLAMA: None,
            ProviderType.LLAMACPP: None,
            ProviderType.OPENAI: None
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize available LLM providers."""
        # Initialize Ollama
        try:
            self.providers[ProviderType.OLLAMA] = OllamaProvider(
                self.config,
                self.config.retry
            )
        except Exception as e:
            logger.warning(f"Could not initialize Ollama provider: {e}")
        
        # Initialize Llama-cpp
        try:
            self.providers[ProviderType.LLAMACPP] = LlamaCppProvider(
                self.config,
                self.config.retry
            )
        except Exception as e:
            logger.warning(f"Could not initialize Llama-cpp provider: {e}")
        
        # Initialize OpenAI
        try:
            self.providers[ProviderType.OPENAI] = OpenAIProvider(
                self.config,
                self.config.retry
            )
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI provider: {e}")
        
        # Log initialized providers
        available = [
            ptype.value for ptype, provider in self.providers.items()
            if provider and provider.is_available()
        ]
        logger.info(f"Initialized LLM providers: {available}")
        
        # If no providers are available, log helpful error message
        if not available:
            logger.error(
                "No LLM providers are available! Please ensure at least one provider is configured:\n"
                "  - Ollama: Install and run Ollama server (https://ollama.ai)\n"
                "  - Llama-cpp: Install llama-cpp-python and configure model_path\n"
                "  - OpenAI: Set OPENAI_API_KEY environment variable or configure in config.yaml"
            )
    
    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a query to the appropriate LLM provider with enhanced fallback.
        
        Args:
            prompt: The input prompt
            model: Optional model name override
            provider: Optional provider override ("ollama", "llamacpp", or "openai")
            **kwargs: Additional parameters for the provider
            
        Returns:
            Dictionary containing:
                - response: The LLM response
                - provider: The provider that handled the query
                - model: The model used
                
        Raises:
            LLMProviderError: If query fails on all available providers
        """
        # Determine provider order
        if provider:
            # Explicit provider specified - no fallback
            provider_order = [ProviderType(provider.lower())]
        else:
            # Use configured preferences with fallback chain
            provider_order = [ProviderType(self.config.fallback.primary_provider)]
            
            if self.config.fallback.enabled:
                provider_order.append(ProviderType(self.config.fallback.fallback_provider))
                
                if self.config.fallback.secondary_fallback_provider:
                    provider_order.append(ProviderType(self.config.fallback.secondary_fallback_provider))
        
        last_error = None
        attempted_providers = []
        
        # Try each provider in order
        for provider_type in provider_order:
            provider_instance = self.providers.get(provider_type)
            
            if not provider_instance:
                logger.debug(f"Provider {provider_type.value} not initialized, skipping")
                continue
            
            if not provider_instance.is_available():
                logger.debug(f"Provider {provider_type.value} not available, skipping")
                continue
            
            attempted_providers.append(provider_type.value)
            
            try:
                # Log fallback if this is not the first attempt
                if len(attempted_providers) > 1:
                    logger.info(
                        f"Falling back to {provider_type.value} provider "
                        f"(previous attempts: {', '.join(attempted_providers[:-1])})"
                    )
                else:
                    logger.info(f"Querying primary provider: {provider_type.value}")
                
                response = provider_instance.query(prompt, model, **kwargs)
                
                # Determine the model used
                used_model = model
                if not used_model:
                    if provider_type == ProviderType.OLLAMA:
                        used_model = self.config.models.ollama_default
                    elif provider_type == ProviderType.LLAMACPP:
                        used_model = self.config.models.llamacpp_default
                    elif provider_type == ProviderType.OPENAI:
                        used_model = self.config.models.openai_default
                
                return {
                    'response': response,
                    'provider': provider_type.value,
                    'model': used_model
                }
                
            except LLMProviderError as e:
                last_error = e
                logger.warning(f"Provider {provider_type.value} failed: {e}")
                # Continue to next provider
                continue
        
        # All providers failed or none available
        if attempted_providers:
            raise LLMProviderError(
                f"All available providers failed ({', '.join(attempted_providers)}). "
                f"Last error: {last_error}"
            )
        else:
            # Generate helpful error message
            error_msg = self._generate_no_providers_error_message()
            raise LLMProviderError(error_msg)
    
    def _generate_no_providers_error_message(self) -> str:
        """Generate a helpful error message when no providers are available."""
        msg = "No LLM providers are available. Please configure at least one provider:\n\n"
        
        # Check status of each provider and provide specific guidance
        providers_status = []
        
        # Ollama
        ollama_provider = self.providers.get(ProviderType.OLLAMA)
        if ollama_provider:
            providers_status.append(
                "  ✗ Ollama: Initialized but not available\n"
                "    → Start Ollama server: ollama serve\n"
                "    → Or install: https://ollama.ai/download"
            )
        else:
            providers_status.append(
                "  ✗ Ollama: Not installed\n"
                "    → Install: pip install ollama\n"
                "    → Download: https://ollama.ai/download"
            )
        
        # Llama-cpp
        llamacpp_provider = self.providers.get(ProviderType.LLAMACPP)
        if llamacpp_provider:
            providers_status.append(
                "  ✗ Llama-cpp: Initialized but not available\n"
                "    → Set model_path in config.yaml under llamacpp section\n"
                "    → Or place GGUF model files in ./models/ directory\n"
                "    → Download models from: https://huggingface.co/models?library=gguf"
            )
        else:
            providers_status.append(
                "  ✗ Llama-cpp: Not installed\n"
                "    → Install: pip install llama-cpp-python\n"
                "    → Configure model_path in config.yaml"
            )
        
        # OpenAI
        openai_provider = self.providers.get(ProviderType.OPENAI)
        if openai_provider:
            providers_status.append(
                "  ✗ OpenAI: Initialized but not available\n"
                "    → Check API key configuration\n"
                "    → Set OPENAI_API_KEY environment variable\n"
                "    → Or configure api_key in config.yaml"
            )
        else:
            providers_status.append(
                "  ✗ OpenAI: Not installed\n"
                "    → Install: pip install openai\n"
                "    → Set OPENAI_API_KEY environment variable"
            )
        
        msg += "\n".join(providers_status)
        return msg
    
    def get_available_providers(self) -> list[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names that are available
        """
        return [
            ptype.value
            for ptype, provider in self.providers.items()
            if provider and provider.is_available()
        ]
    
    def is_available(self, provider: Optional[str] = None) -> bool:
        """
        Check if a provider or any provider is available.
        
        Args:
            provider: Optional provider name to check. If None, checks if any provider is available.
            
        Returns:
            True if the specified provider (or any provider) is available
        """
        if provider:
            # Check specific provider
            provider_type = ProviderType(provider.lower())
            p = self.providers.get(provider_type)
            return p is not None and p.is_available()
        else:
            # Check if any provider is available
            return len(self.get_available_providers()) > 0
    
    def get_model(self, provider: Optional[str] = None) -> str:
        """
        Get the default model for a provider.
        
        Args:
            provider: Provider name ("ollama", "llamacpp", or "openai"). If None, uses primary provider.
            
        Returns:
            Default model name for the provider
        """
        if not provider:
            provider = self.config.fallback.primary_provider
        
        provider_type = ProviderType(provider.lower())
        
        if provider_type == ProviderType.OLLAMA:
            return self.config.models.ollama_default
        elif provider_type == ProviderType.LLAMACPP:
            return self.config.models.llamacpp_default
        elif provider_type == ProviderType.OPENAI:
            return self.config.models.openai_default
        else:
            raise ValueError(f"Unknown provider: {provider}")
