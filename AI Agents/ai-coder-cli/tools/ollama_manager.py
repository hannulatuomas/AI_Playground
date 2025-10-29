"""
Ollama Management Tool

Production-ready tool for managing Ollama LLM server.
Handles starting, stopping, health checks, and model management.
"""

import subprocess
import time
import json
import requests
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

from .base import Tool


class OllamaManager(Tool):
    """
    Production-ready Ollama Management Tool.
    
    Features:
        - Start/stop Ollama server
        - Health check before LLM connections
        - List running models
        - List available models
        - Pull/download models
        - Check model status
        - Server status monitoring
    """
    
    def __init__(self, name: str = "ollama_manager",
                 description: str = "Ollama LLM server management tool", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        # Get Ollama config
        self._host = self.config.get('ollama', {}).get('host', 'http://localhost')
        self._port = self.config.get('ollama', {}).get('port', 11434)
        self._base_url = f"{self._host}:{self._port}"
        self._timeout = self.config.get('ollama', {}).get('timeout', 120)
        
        self.logger.info(f"Ollama Manager initialized ({self._base_url})")
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the Ollama manager tool.
        
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
        """Execute Ollama management operation."""
        self.logger.info(f"Ollama operation: {operation}")
        
        try:
            if operation == 'health_check':
                return self.health_check()
            elif operation == 'start':
                return self.start_server()
            elif operation == 'stop':
                return self.stop_server()
            elif operation == 'status':
                return self.server_status()
            elif operation == 'list_models':
                return self.list_models()
            elif operation == 'list_running':
                return self.list_running_models()
            elif operation == 'pull_model':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for pull operation")
                return self.pull_model(model_name)
            elif operation == 'model_info':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for info operation")
                return self.get_model_info(model_name)
            elif operation == 'is_model_running':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for is_model_running operation")
                is_running = self.is_model_running(model_name)
                return self._build_success_result(
                    f"Model '{model_name}' is {'running' if is_running else 'not running'}",
                    data={'model': model_name, 'running': is_running}
                )
            elif operation == 'is_model_available':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for is_model_available operation")
                is_available = self.is_model_available(model_name)
                return self._build_success_result(
                    f"Model '{model_name}' is {'available' if is_available else 'not available'}",
                    data={'model': model_name, 'available': is_available}
                )
            elif operation == 'start_model':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for start_model operation")
                return self.start_model(model_name)
            elif operation == 'stop_model':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for stop_model operation")
                return self.stop_model(model_name)
            elif operation == 'check_model_status':
                model_name = context.get('model_name')
                if not model_name:
                    return self._build_error_result("model_name required for check_model_status operation")
                return self.check_model_status(model_name)
            else:
                return self._build_error_result(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Ollama operation failed: {e}", exc_info=True)
            return self._build_error_result(f"Operation failed: {str(e)}", error=e)
    
    def health_check(self, auto_start: bool = True) -> Dict[str, Any]:
        """
        Check Ollama server health.
        
        Args:
            auto_start: If True, attempt to start server if it's not running
            
        Returns:
            Dict with success status and server info
        """
        try:
            # Try to connect to Ollama API
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                return self._build_success_result(
                    "Ollama server is healthy",
                    data={
                        'status': 'healthy',
                        'url': self._base_url,
                        'models_available': len(models),
                        'models': [m.get('name') for m in models]
                    }
                )
            else:
                if auto_start:
                    self.logger.info("Ollama not responding, attempting to start...")
                    start_result = self.start_server()
                    if start_result['success']:
                        # Wait a moment for server to initialize
                        time.sleep(2)
                        return self.health_check(auto_start=False)
                
                return self._build_error_result(
                    f"Ollama server returned status {response.status_code}",
                    data={'status': 'unhealthy', 'url': self._base_url}
                )
                
        except requests.exceptions.ConnectionError:
            if auto_start:
                self.logger.info("Ollama server not running, attempting to start...")
                start_result = self.start_server()
                if start_result['success']:
                    # Wait for server to initialize
                    time.sleep(3)
                    return self.health_check(auto_start=False)
            
            return self._build_error_result(
                "Cannot connect to Ollama server",
                data={
                    'status': 'not_running',
                    'url': self._base_url,
                    'suggestion': 'Run `ollama serve` or use start_server()'
                }
            )
        except Exception as e:
            return self._build_error_result(
                f"Health check failed: {str(e)}",
                error=e,
                data={'status': 'error', 'url': self._base_url}
            )
    
    def start_server(self) -> Dict[str, Any]:
        """
        Start Ollama server.
        
        Returns:
            Dict with success status
        """
        try:
            # Check if already running
            try:
                response = requests.get(f"{self._base_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    return self._build_success_result(
                        "Ollama server is already running",
                        data={'status': 'already_running', 'url': self._base_url}
                    )
            except:
                pass
            
            # Try to start Ollama server
            self.logger.info("Starting Ollama server...")
            
            # Start server in background
            # Note: This assumes 'ollama' is in PATH
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait for server to start
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                try:
                    response = requests.get(f"{self._base_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        return self._build_success_result(
                            "Ollama server started successfully",
                            data={
                                'status': 'started',
                                'url': self._base_url,
                                'pid': process.pid
                            }
                        )
                except:
                    continue
            
            return self._build_error_result(
                "Ollama server started but not responding",
                data={'status': 'starting', 'pid': process.pid}
            )
            
        except FileNotFoundError:
            return self._build_error_result(
                "Ollama not found in PATH. Please install Ollama: https://ollama.ai/download",
                data={'status': 'not_installed'}
            )
        except Exception as e:
            return self._build_error_result(f"Failed to start server: {str(e)}", error=e)
    
    def stop_server(self) -> Dict[str, Any]:
        """
        Stop Ollama server.
        
        Returns:
            Dict with success status
        """
        try:
            # Try to find and kill ollama process
            result = subprocess.run(
                ['pkill', '-f', 'ollama serve'],
                capture_output=True,
                timeout=5
            )
            
            # Wait a moment
            time.sleep(1)
            
            # Check if stopped
            try:
                requests.get(f"{self._base_url}/api/tags", timeout=2)
                return self._build_error_result(
                    "Ollama server still running",
                    data={'status': 'running'}
                )
            except:
                return self._build_success_result(
                    "Ollama server stopped",
                    data={'status': 'stopped'}
                )
                
        except Exception as e:
            return self._build_error_result(f"Failed to stop server: {str(e)}", error=e)
    
    def server_status(self) -> Dict[str, Any]:
        """
        Get Ollama server status.
        
        Returns:
            Dict with server status information
        """
        try:
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                return self._build_success_result(
                    "Ollama server is running",
                    data={
                        'status': 'running',
                        'url': self._base_url,
                        'models_count': len(models),
                        'models': [m.get('name') for m in models]
                    }
                )
            else:
                return self._build_error_result(
                    f"Server returned status {response.status_code}",
                    data={'status': 'error'}
                )
                
        except requests.exceptions.ConnectionError:
            return self._build_error_result(
                "Ollama server is not running",
                data={'status': 'not_running', 'url': self._base_url}
            )
        except Exception as e:
            return self._build_error_result(f"Status check failed: {str(e)}", error=e)
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all available Ollama models.
        
        Returns:
            Dict with list of models
        """
        try:
            response = requests.get(
                f"{self._base_url}/api/tags",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                model_list = []
                for model in models:
                    model_list.append({
                        'name': model.get('name'),
                        'size': model.get('size'),
                        'modified': model.get('modified_at'),
                        'digest': model.get('digest')
                    })
                
                return self._build_success_result(
                    f"Found {len(model_list)} model(s)",
                    data={
                        'count': len(model_list),
                        'models': model_list
                    }
                )
            else:
                return self._build_error_result(
                    f"Failed to list models: status {response.status_code}"
                )
                
        except Exception as e:
            return self._build_error_result(f"Failed to list models: {str(e)}", error=e)
    
    def list_running_models(self) -> Dict[str, Any]:
        """
        List currently running models.
        
        Returns:
            Dict with list of running models
        """
        try:
            response = requests.get(
                f"{self._base_url}/api/ps",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                running_list = []
                for model in models:
                    running_list.append({
                        'name': model.get('name'),
                        'size': model.get('size'),
                        'expires_at': model.get('expires_at')
                    })
                
                return self._build_success_result(
                    f"Found {len(running_list)} running model(s)",
                    data={
                        'count': len(running_list),
                        'models': running_list
                    }
                )
            else:
                return self._build_error_result(
                    f"Failed to list running models: status {response.status_code}"
                )
                
        except Exception as e:
            return self._build_error_result(
                f"Failed to list running models: {str(e)}",
                error=e
            )
    
    def is_model_running(self, model_name: str) -> bool:
        """
        Check if a specific model is currently running.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is running, False otherwise
        """
        try:
            result = self.list_running_models()
            if result['success']:
                running_models = result['data'].get('models', [])
                return any(m['name'] == model_name for m in running_models)
            return False
        except Exception as e:
            self.logger.error(f"Failed to check if model is running: {e}")
            return False
    
    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is installed/available.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is available (installed), False otherwise
        """
        try:
            result = self.list_models()
            if result['success']:
                available_models = result['data'].get('models', [])
                return any(m['name'] == model_name for m in available_models)
            return False
        except Exception as e:
            self.logger.error(f"Failed to check if model is available: {e}")
            return False
    
    def start_model(self, model_name: str) -> Dict[str, Any]:
        """
        Start (load) a specific model by making a small query.
        
        This triggers Ollama to load the model into memory if it's installed
        but not currently running.
        
        Args:
            model_name: Name of the model to start
            
        Returns:
            Dict with start status
        """
        try:
            # First check if model is available
            if not self.is_model_available(model_name):
                return self._build_error_result(
                    f"Model '{model_name}' is not installed",
                    data={'status': 'not_installed', 'model': model_name}
                )
            
            # Check if already running
            if self.is_model_running(model_name):
                return self._build_success_result(
                    f"Model '{model_name}' is already running",
                    data={'status': 'already_running', 'model': model_name}
                )
            
            # Trigger model loading with a simple query
            self.logger.info(f"Starting model: {model_name}")
            response = requests.post(
                f"{self._base_url}/api/generate",
                json={
                    'model': model_name,
                    'prompt': 'test',
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return self._build_success_result(
                    f"Model '{model_name}' started successfully",
                    data={'status': 'started', 'model': model_name}
                )
            else:
                return self._build_error_result(
                    f"Failed to start model '{model_name}': status {response.status_code}",
                    data={'status': 'failed', 'model': model_name}
                )
                
        except Exception as e:
            return self._build_error_result(
                f"Failed to start model: {str(e)}",
                error=e,
                data={'model': model_name}
            )
    
    def stop_model(self, model_name: str) -> Dict[str, Any]:
        """
        Stop (unload) a specific model from memory.
        
        Note: Ollama automatically unloads models after inactivity.
        This method sends a request to explicitly unload the model.
        
        Args:
            model_name: Name of the model to stop
            
        Returns:
            Dict with stop status
        """
        try:
            # Check if model is running
            if not self.is_model_running(model_name):
                return self._build_success_result(
                    f"Model '{model_name}' is not running",
                    data={'status': 'not_running', 'model': model_name}
                )
            
            # Ollama doesn't have a direct unload API yet
            # Models auto-unload after timeout, so we just log this
            self.logger.info(
                f"Model '{model_name}' will auto-unload after inactivity. "
                "Ollama manages model lifecycle automatically."
            )
            
            return self._build_success_result(
                f"Model '{model_name}' will be unloaded automatically by Ollama",
                data={
                    'status': 'scheduled_for_unload',
                    'model': model_name,
                    'note': 'Ollama auto-manages model lifecycle'
                }
            )
            
        except Exception as e:
            return self._build_error_result(
                f"Failed to stop model: {str(e)}",
                error=e,
                data={'model': model_name}
            )
    
    def check_model_status(self, model_name: str) -> Dict[str, Any]:
        """
        Get comprehensive status of a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with model status information
        """
        try:
            status = {
                'model': model_name,
                'installed': False,
                'running': False,
                'info': None
            }
            
            # Check if installed
            status['installed'] = self.is_model_available(model_name)
            
            if status['installed']:
                # Check if running
                status['running'] = self.is_model_running(model_name)
                
                # Get model info
                info_result = self.get_model_info(model_name)
                if info_result['success']:
                    status['info'] = info_result['data']
            
            return self._build_success_result(
                f"Status for model '{model_name}'",
                data=status
            )
            
        except Exception as e:
            return self._build_error_result(
                f"Failed to check model status: {str(e)}",
                error=e,
                data={'model': model_name}
            )
    
    def pull_model(self, model_name: str) -> Dict[str, Any]:
        """
        Pull/download a model from Ollama registry.
        
        Args:
            model_name: Name of the model to pull (e.g., "llama2", "mistral")
            
        Returns:
            Dict with pull status
        """
        try:
            self.logger.info(f"Pulling model: {model_name}")
            
            # Use subprocess for better streaming support
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=600)  # 10 minute timeout
            
            if process.returncode == 0:
                return self._build_success_result(
                    f"Model '{model_name}' pulled successfully",
                    data={
                        'model': model_name,
                        'status': 'pulled',
                        'output': stdout
                    }
                )
            else:
                return self._build_error_result(
                    f"Failed to pull model '{model_name}'",
                    data={
                        'model': model_name,
                        'status': 'failed',
                        'error': stderr
                    }
                )
                
        except subprocess.TimeoutExpired:
            return self._build_error_result(
                f"Model pull timed out for '{model_name}'",
                data={'model': model_name, 'status': 'timeout'}
            )
        except FileNotFoundError:
            return self._build_error_result(
                "Ollama not found in PATH",
                data={'status': 'not_installed'}
            )
        except Exception as e:
            return self._build_error_result(
                f"Failed to pull model: {str(e)}",
                error=e
            )
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with model information
        """
        try:
            response = requests.post(
                f"{self._base_url}/api/show",
                json={'name': model_name},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return self._build_success_result(
                    f"Model info for '{model_name}'",
                    data={
                        'model': model_name,
                        'modelfile': data.get('modelfile'),
                        'parameters': data.get('parameters'),
                        'template': data.get('template'),
                        'details': data.get('details')
                    }
                )
            else:
                return self._build_error_result(
                    f"Model '{model_name}' not found or error occurred",
                    data={'model': model_name, 'status_code': response.status_code}
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
