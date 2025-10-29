"""
AI Backend - llama.cpp Binary Wrapper

Provides interface to llama.cpp executable for AI inference.
Uses the llama.cpp binary directly instead of Python bindings.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import subprocess
import json
import platform

logger = logging.getLogger(__name__)


class AIBackend:
    """
    Wrapper for llama.cpp binary providing AI inference capabilities.
    
    This class handles model loading, query processing, and response
    generation using local AI models via llama.cpp executable.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI backend.
        
        Args:
            config: Configuration dictionary for AI settings
        """
        self.config = config or {}
        self.model_path: Optional[str] = None
        self.llama_binary: Optional[str] = None
        self.context_history: List[Dict[str, str]] = []
        self.is_loaded = False
        self._find_llama_binary()
        
    def _find_llama_binary(self) -> None:
        """Find llama.cpp binary in llama-cpp/ directory."""
        llama_dir = Path("llama-cpp")
        
        if not llama_dir.exists():
            logger.warning(f"llama-cpp directory not found: {llama_dir}")
            return
        
        # Determine binary name based on platform
        system = platform.system()
        if system == "Windows":
            binary_names = ["llama-cli.exe", "main.exe", "llama.exe"]
        else:
            binary_names = ["llama-cli", "main", "llama"]
        
        # Search for binary
        for binary_name in binary_names:
            binary_path = llama_dir / binary_name
            if binary_path.exists():
                self.llama_binary = str(binary_path)
                logger.info(f"Found llama.cpp binary: {self.llama_binary}")
                return
        
        logger.warning(f"No llama.cpp binary found in {llama_dir}")
        logger.warning(f"Looked for: {', '.join(binary_names)}")
    
    def load_model(self, model_path: str) -> bool:
        """
        Load AI model from file.
        
        Args:
            model_path: Path to the model file (.gguf)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.llama_binary:
            logger.error("llama.cpp binary not found. Please place llama.cpp executable in llama-cpp/ directory")
            return False
        
        if not Path(model_path).exists():
            logger.error(f"Model file not found: {model_path}")
            return False
        
        self.model_path = model_path
        self.is_loaded = True
        logger.info(f"Model configured: {model_path}")
        logger.info(f"Using binary: {self.llama_binary}")
        return True
    
    def query(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        Query the AI model with a prompt.
        
        Args:
            prompt: Input prompt for the AI
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            stream: Enable streaming output (not supported with binary)
            
        Returns:
            Generated response text
        """
        if not self.is_loaded or not self.model_path:
            logger.error("Model not loaded. Call load_model() first.")
            return ""
        
        if not self.llama_binary:
            logger.error("llama.cpp binary not found")
            return ""
        
        try:
            # Use config defaults if not specified
            max_tokens = max_tokens or self.config.get('max_tokens', 2048)
            temperature = temperature if temperature is not None else self.config.get('temperature', 0.7)
            top_p = top_p if top_p is not None else self.config.get('top_p', 0.9)
            top_k = top_k if top_k is not None else self.config.get('top_k', 40)
            n_ctx = self.config.get('context_length', 8192)
            threads = self.config.get('threads', 4)
            
            logger.debug(f"Querying model with prompt length: {len(prompt)}")
            
            # Build command
            cmd = [
                self.llama_binary,
                "-m", self.model_path,
                "-p", prompt,
                "-n", str(max_tokens),
                "--temp", str(temperature),
                "--top-p", str(top_p),
                "--top-k", str(top_k),
                "-c", str(n_ctx),
                "-t", str(threads),
                "--no-display-prompt"
            ]
            
            # Run llama.cpp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"llama.cpp error: {result.stderr}")
                return ""
            
            # Extract response (llama.cpp outputs the generated text)
            response = result.stdout.strip()
            return response
                
        except subprocess.TimeoutExpired:
            logger.error("Query timeout (5 minutes)")
            return ""
        except Exception as e:
            logger.error(f"Error during query: {e}")
            return ""
    
    def query_with_context(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Query with conversation context.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for query()
            
        Returns:
            Generated response
        """
        # Build full prompt with context
        full_prompt = ""
        
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        
        # Add conversation history
        for msg in self.context_history[-5:]:  # Keep last 5 messages
            full_prompt += f"{msg['role']}: {msg['content']}\n\n"
        
        full_prompt += f"User: {prompt}\n\nAssistant:"
        
        # Query the model
        response = self.query(full_prompt, **kwargs)
        
        # Update context history
        self.context_history.append({"role": "User", "content": prompt})
        self.context_history.append({"role": "Assistant", "content": response})
        
        return response
    
    def clear_context(self) -> None:
        """Clear conversation context history."""
        self.context_history.clear()
        logger.debug("Context history cleared")
    
    def get_context_size(self) -> int:
        """Get current context size in messages."""
        return len(self.context_history)
    
    def close(self) -> None:
        """Close the model and free resources."""
        self.model_path = None
        self.is_loaded = False
        logger.info("Model unloaded")
    
    def is_model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.is_loaded
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model."""
        return {
            'loaded': self.is_loaded,
            'model_path': self.model_path,
            'binary_path': self.llama_binary,
            'config': self.config,
            'context_size': self.get_context_size()
        }
