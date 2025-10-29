"""
Llama-cpp Management Tool

Production-ready tool for managing local LLMs using llama-cpp-python.
Handles model loading, inference, and resource management.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import Tool


class LlamaCppManager(Tool):
    """
    Production-ready Llama-cpp Management Tool.
    
    Features:
        - Load and manage GGUF models
        - Perform inference with llama-cpp-python
        - Configure context size, threads, GPU layers
        - Model status and info
        - Memory management
    """
    
    def __init__(self, name: str = "llamacpp_manager",
                 description: str = "Llama-cpp local LLM management tool", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # Check if llama-cpp-python is available
        try:
            from llama_cpp import Llama
            self._llama_cpp_available = True
            self._Llama = Llama
        except ImportError:
            self._llama_cpp_available = False
            self._Llama = None
            self.logger.warning(
                "llama-cpp-python is not installed. "
                "Install it with: pip install llama-cpp-python"
            )
        
        # Get llama-cpp config
        llamacpp_config = self.config.get('llamacpp', {})
        self._model_path = llamacpp_config.get('model_path', None)
        self._context_size = llamacpp_config.get('context_size', 2048)
        self._n_threads = llamacpp_config.get('n_threads', None)  # None = auto-detect
        self._n_gpu_layers = llamacpp_config.get('n_gpu_layers', 0)
        self._verbose = llamacpp_config.get('verbose', False)
        self._models_dir = Path(llamacpp_config.get('models_dir', './models'))
        
        # Loaded model instance
        self._model = None
        self._loaded_model_path = None
        
        self.logger.info(f"LlamaCpp Manager initialized (model: {self._model_path or 'not set'})")
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the llama-cpp manager tool.
        
        This is the main entry point for tool execution, required by the Tool interface.
        Delegates to the execute() method with operation and context.
        
        Args:
            params: Dictionary containing 'operation' and other parameters
            
        Returns:
            Dictionary with operation result
        """
        operation = params.get('operation', 'health_check')
        return self.execute(operation, params)
    
    def execute(self, operation: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute llama-cpp management operation."""
        self.logger.info(f"LlamaCpp operation: {operation}")
        
        try:
            if operation == 'health_check':
                return self.health_check()
            elif operation == 'load_model':
                model_path = context.get('model_path', self._model_path)
                if not model_path:
                    return self._build_error_result("model_path required for load operation")
                return self.load_model(model_path, context)
            elif operation == 'unload_model':
                return self.unload_model()
            elif operation == 'generate':
                prompt = context.get('prompt')
                if not prompt:
                    return self._build_error_result("prompt required for generate operation")
                return self.generate(prompt, context)
            elif operation == 'list_models':
                return self.list_models()
            elif operation == 'model_info':
                return self.get_model_info()
            elif operation == 'is_model_loaded':
                return self._build_success_result(
                    f"Model is {'loaded' if self._model else 'not loaded'}",
                    data={'loaded': self._model is not None, 'model_path': self._loaded_model_path}
                )
            else:
                return self._build_error_result(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"LlamaCpp operation failed: {e}", exc_info=True)
            return self._build_error_result(f"Operation failed: {str(e)}", error=e)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check llama-cpp health and availability.
        
        Returns:
            Dict with success status and health info
        """
        if not self._llama_cpp_available:
            return self._build_error_result(
                "llama-cpp-python is not installed",
                data={
                    'status': 'not_installed',
                    'suggestion': 'Install with: pip install llama-cpp-python'
                }
            )
        
        # Check if model is configured
        if not self._model_path and not self._models_dir.exists():
            return self._build_success_result(
                "llama-cpp-python is available but no model is configured",
                data={
                    'status': 'available',
                    'model_configured': False,
                    'model_loaded': False,
                    'suggestion': 'Set model_path in config or place models in models directory'
                }
            )
        
        # Check if model is loaded
        if self._model:
            return self._build_success_result(
                "llama-cpp is healthy and model is loaded",
                data={
                    'status': 'healthy',
                    'model_configured': True,
                    'model_loaded': True,
                    'loaded_model': self._loaded_model_path,
                    'context_size': self._context_size,
                    'n_threads': self._n_threads,
                    'n_gpu_layers': self._n_gpu_layers
                }
            )
        
        # Check if configured model exists
        if self._model_path:
            model_file = Path(self._model_path)
            if model_file.exists():
                return self._build_success_result(
                    "llama-cpp is available and model file found",
                    data={
                        'status': 'available',
                        'model_configured': True,
                        'model_loaded': False,
                        'model_path': str(model_file),
                        'suggestion': 'Use load_model operation to load the model'
                    }
                )
            else:
                return self._build_error_result(
                    f"Configured model file not found: {model_file}",
                    data={
                        'status': 'model_not_found',
                        'model_path': str(model_file),
                        'suggestion': 'Check model_path in config or download a model'
                    }
                )
        
        return self._build_success_result(
            "llama-cpp-python is available",
            data={
                'status': 'available',
                'model_configured': False,
                'model_loaded': False
            }
        )
    
    def load_model(self, model_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load a GGUF model.
        
        Args:
            model_path: Path to the GGUF model file
            config: Optional configuration overrides
            
        Returns:
            Dict with load status
        """
        if not self._llama_cpp_available:
            return self._build_error_result(
                "llama-cpp-python is not installed",
                data={'status': 'not_installed'}
            )
        
        # Check if model file exists
        model_file = Path(model_path)
        if not model_file.exists():
            # Try looking in models directory
            alt_path = self._models_dir / model_path
            if alt_path.exists():
                model_file = alt_path
            else:
                return self._build_error_result(
                    f"Model file not found: {model_path}",
                    data={
                        'status': 'not_found',
                        'model_path': str(model_path),
                        'searched_paths': [str(model_file), str(alt_path)]
                    }
                )
        
        # Unload existing model if loaded
        if self._model:
            self.logger.info(f"Unloading existing model: {self._loaded_model_path}")
            self.unload_model()
        
        try:
            self.logger.info(f"Loading model from: {model_file}")
            
            # Get configuration parameters
            config = config or {}
            context_size = config.get('context_size', self._context_size)
            n_threads = config.get('n_threads', self._n_threads)
            n_gpu_layers = config.get('n_gpu_layers', self._n_gpu_layers)
            verbose = config.get('verbose', self._verbose)
            
            # Load the model
            self._model = self._Llama(
                model_path=str(model_file),
                n_ctx=context_size,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=verbose
            )
            
            self._loaded_model_path = str(model_file)
            
            return self._build_success_result(
                f"Model loaded successfully: {model_file.name}",
                data={
                    'status': 'loaded',
                    'model_path': str(model_file),
                    'model_name': model_file.name,
                    'context_size': context_size,
                    'n_threads': n_threads,
                    'n_gpu_layers': n_gpu_layers
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}", exc_info=True)
            return self._build_error_result(
                f"Failed to load model: {str(e)}",
                error=e,
                data={'model_path': str(model_file)}
            )
    
    def unload_model(self) -> Dict[str, Any]:
        """
        Unload the currently loaded model.
        
        Returns:
            Dict with unload status
        """
        if not self._model:
            return self._build_success_result(
                "No model is currently loaded",
                data={'status': 'not_loaded'}
            )
        
        try:
            model_path = self._loaded_model_path
            self._model = None
            self._loaded_model_path = None
            
            self.logger.info(f"Model unloaded: {model_path}")
            
            return self._build_success_result(
                f"Model unloaded successfully",
                data={
                    'status': 'unloaded',
                    'previous_model': model_path
                }
            )
            
        except Exception as e:
            return self._build_error_result(
                f"Failed to unload model: {str(e)}",
                error=e
            )
    
    def generate(self, prompt: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate text using the loaded model.
        
        Args:
            prompt: Input prompt
            config: Optional generation parameters
            
        Returns:
            Dict with generated text
        """
        if not self._llama_cpp_available:
            return self._build_error_result(
                "llama-cpp-python is not installed",
                data={'status': 'not_installed'}
            )
        
        if not self._model:
            # Try to auto-load model if configured
            if self._model_path:
                load_result = self.load_model(self._model_path)
                if not load_result['success']:
                    return self._build_error_result(
                        "No model is loaded and auto-load failed",
                        data={'status': 'no_model_loaded'}
                    )
            else:
                return self._build_error_result(
                    "No model is loaded",
                    data={
                        'status': 'no_model_loaded',
                        'suggestion': 'Load a model first using load_model operation'
                    }
                )
        
        try:
            config = config or {}
            max_tokens = config.get('max_tokens', 512)
            temperature = config.get('temperature', 0.7)
            top_p = config.get('top_p', 0.95)
            top_k = config.get('top_k', 40)
            stop = config.get('stop', None)
            
            self.logger.debug(f"Generating with prompt length: {len(prompt)}")
            
            # Generate response
            output = self._model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop=stop
            )
            
            # Extract generated text
            generated_text = output['choices'][0]['text']
            
            self.logger.info(f"Generation successful (length: {len(generated_text)})")
            
            return self._build_success_result(
                "Generation successful",
                data={
                    'status': 'success',
                    'generated_text': generated_text,
                    'prompt_length': len(prompt),
                    'response_length': len(generated_text),
                    'model': self._loaded_model_path,
                    'tokens_used': output.get('usage', {})
                }
            )
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}", exc_info=True)
            return self._build_error_result(
                f"Generation failed: {str(e)}",
                error=e
            )
    
    def list_models(self) -> Dict[str, Any]:
        """
        List available models in the models directory.
        
        Returns:
            Dict with list of models
        """
        try:
            if not self._models_dir.exists():
                return self._build_success_result(
                    "Models directory does not exist",
                    data={
                        'count': 0,
                        'models': [],
                        'models_dir': str(self._models_dir),
                        'suggestion': f'Create directory and place GGUF models there'
                    }
                )
            
            # Find GGUF model files
            model_files = []
            for ext in ['*.gguf', '*.bin']:  # Support both GGUF and legacy bin formats
                model_files.extend(self._models_dir.glob(ext))
            
            models = []
            for model_file in model_files:
                models.append({
                    'name': model_file.name,
                    'path': str(model_file),
                    'size': model_file.stat().st_size,
                    'size_mb': round(model_file.stat().st_size / (1024 * 1024), 2)
                })
            
            return self._build_success_result(
                f"Found {len(models)} model(s)",
                data={
                    'count': len(models),
                    'models': models,
                    'models_dir': str(self._models_dir)
                }
            )
            
        except Exception as e:
            return self._build_error_result(
                f"Failed to list models: {str(e)}",
                error=e
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently loaded model.
        
        Returns:
            Dict with model information
        """
        if not self._model:
            return self._build_error_result(
                "No model is currently loaded",
                data={'status': 'not_loaded'}
            )
        
        try:
            info = {
                'model_path': self._loaded_model_path,
                'model_name': Path(self._loaded_model_path).name,
                'context_size': self._context_size,
                'n_threads': self._n_threads,
                'n_gpu_layers': self._n_gpu_layers
            }
            
            # Try to get additional metadata if available
            try:
                if hasattr(self._model, 'metadata'):
                    info['metadata'] = self._model.metadata
            except:
                pass
            
            return self._build_success_result(
                "Model information",
                data=info
            )
            
        except Exception as e:
            return self._build_error_result(
                f"Failed to get model info: {str(e)}",
                error=e
            )
    
    def _build_success_result(self, message: str, data: Any = None) -> Dict[str, Any]:
        """Build success result."""
        return {
            'success': True,
            'message': message,
            'data': data or {}
        }
    
    def _build_error_result(self, message: str, error: Exception = None, 
                           data: Any = None) -> Dict[str, Any]:
        """Build error result."""
        result = {
            'success': False,
            'message': message,
            'data': data or {}
        }
        if error:
            result['data']['error'] = str(error)
        return result
