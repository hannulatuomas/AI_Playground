"""
LLM Interface Module

Handles integration with llama.cpp for running local language models.
Provides methods to run queries via subprocess, handle errors, and cache responses.
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class LLMConfig:
    """Configuration for the LLM."""
    model_path: str
    executable_path: str
    context_size: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    threads: int = 4
    gpu_layers: int = 0


class LLMInterface:
    """
    Interface for interacting with llama.cpp via subprocess.
    Handles query execution, response caching, and error management.
    """

    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM interface.

        Args:
            config: LLMConfig object with model and execution parameters

        Raises:
            FileNotFoundError: If executable or model paths are invalid
        """
        self.config = config
        self._validate_paths()
        self._cache: Dict[str, str] = {}
        self._cache_max_size = 100

    def _validate_paths(self) -> None:
        """
        Validate that executable and model paths exist.

        Raises:
            FileNotFoundError: If paths don't exist
        """
        executable = Path(self.config.executable_path)
        if not executable.exists():
            raise FileNotFoundError(
                f"llama.cpp executable not found at {self.config.executable_path}"
            )

        model = Path(self.config.model_path)
        if not model.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.config.model_path}"
            )

    def _build_command(self, prompt: str, max_tokens: int = 2048) -> List[str]:
        """
        Build the command line arguments for llama.cpp.

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate

        Returns:
            List of command arguments
        """
        cmd = [
            str(Path(self.config.executable_path).absolute()),
            '--model', str(Path(self.config.model_path).absolute()),
            '--prompt', prompt,
            '--ctx-size', str(self.config.context_size),
            '--temp', str(self.config.temperature),
            '--top-p', str(self.config.top_p),
            '--top-k', str(self.config.top_k),
            '--repeat-penalty', str(self.config.repeat_penalty),
            '--threads', str(self.config.threads),
            '--n-predict', str(max_tokens),
            '--log-disable',
            '--no-display-prompt',
        ]

        if self.config.gpu_layers > 0:
            cmd.extend(['--n-gpu-layers', str(self.config.gpu_layers)])

        return cmd

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        use_cache: bool = True,
        timeout: int = 120
    ) -> str:
        """
        Generate text completion using llama.cpp.

        Args:
            prompt: Input prompt for the model
            max_tokens: Maximum tokens to generate
            use_cache: Whether to use cached responses
            timeout: Timeout in seconds for generation

        Returns:
            Generated text

        Raises:
            TimeoutError: If generation takes too long
            RuntimeError: If subprocess fails
        """
        # Check cache first
        cache_key = self._get_cache_key(prompt, max_tokens)
        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Build command
        cmd = self._build_command(prompt, max_tokens)

        try:
            # Run llama.cpp subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                raise RuntimeError(
                    f"llama.cpp failed with return code {result.returncode}: {error_msg}"
                )

            # Extract and clean the output
            output = result.stdout.strip()

            # Cache the result
            if use_cache:
                self._add_to_cache(cache_key, output)

            return output

        except subprocess.TimeoutExpired:
            raise TimeoutError(
                f"Generation timed out after {timeout} seconds. "
                f"Try reducing max_tokens or context_size."
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"Could not execute llama.cpp at {self.config.executable_path}. "
                f"Ensure it's built and the path is correct."
            )
        except Exception as e:
            raise RuntimeError(f"Error during generation: {str(e)}")

    def _get_cache_key(self, prompt: str, max_tokens: int) -> str:
        """
        Generate a cache key from prompt and parameters.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens

        Returns:
            Cache key string
        """
        # Use first 100 chars of prompt + max_tokens as key
        prompt_hash = prompt[:100]
        return f"{prompt_hash}_{max_tokens}"

    def _add_to_cache(self, key: str, value: str) -> None:
        """
        Add entry to cache, removing oldest if at max size.

        Args:
            key: Cache key
            value: Response to cache
        """
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry (first item)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = value

    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache.clear()

    def test_connection(self) -> bool:
        """
        Test if llama.cpp is working correctly.

        Returns:
            True if test successful, False otherwise
        """
        try:
            test_prompt = "Hello"
            result = self.generate(
                test_prompt,
                max_tokens=10,
                use_cache=False,
                timeout=30
            )
            return len(result) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache size and max size
        """
        return {
            'current_size': len(self._cache),
            'max_size': self._cache_max_size
        }


def load_config_from_file(config_path: str = "data/config.json") -> Optional[LLMConfig]:
    """
    Load LLM configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        LLMConfig object or None if file doesn't exist
    """
    config_file = Path(config_path)

    if not config_file.exists():
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        return LLMConfig(
            model_path=config_data.get('model_path', ''),
            executable_path=config_data.get('executable_path', ''),
            context_size=config_data.get('context_size', 4096),
            temperature=config_data.get('temperature', 0.7),
            top_p=config_data.get('top_p', 0.9),
            top_k=config_data.get('top_k', 40),
            repeat_penalty=config_data.get('repeat_penalty', 1.1),
            threads=config_data.get('threads', 4),
            gpu_layers=config_data.get('gpu_layers', 0)
        )
    except Exception as e:
        print(f"Error loading config: {e}")
        return None


def save_config_to_file(config: LLMConfig, config_path: str = "data/config.json") -> None:
    """
    Save LLM configuration to a JSON file.

    Args:
        config: LLMConfig object to save
        config_path: Path where to save the configuration
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config_data = asdict(config)

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)


if __name__ == "__main__":
    # Test the LLM interface
    print("Testing LLM Interface...")

    # Try to load existing config
    config = load_config_from_file()

    if config:
        print(f"✓ Configuration loaded")
        print(f"  Model: {config.model_path}")
        print(f"  Executable: {config.executable_path}")

        try:
            llm = LLMInterface(config)
            print("✓ LLM Interface initialized")

            # Test connection
            if llm.test_connection():
                print("✓ Connection test passed")
            else:
                print("✗ Connection test failed")

        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print("✗ No configuration found")
        print("  Run: python main.py --setup")
