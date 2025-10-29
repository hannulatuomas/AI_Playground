
"""
Configuration management module for AI Agent Console.

This module handles loading and validation of configuration settings from
YAML files (preferred) or TOML files (legacy) and environment variables using Pydantic models.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Literal, Dict, List, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import logging

# Import tomllib for backward compatibility with legacy TOML configs
try:
    import tomllib
    TOML_AVAILABLE = True
except ImportError:
    try:
        import tomli as tomllib
        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False


logger = logging.getLogger(__name__)


class OllamaSettings(BaseModel):
    """Configuration settings for Ollama LLM provider."""
    
    host: str = Field(default="http://localhost", description="Ollama server host")
    port: int = Field(default=11434, ge=1, le=65535, description="Ollama server port")
    timeout: int = Field(default=120, ge=1, description="Request timeout in seconds")
    
    @property
    def base_url(self) -> str:
        """Construct the full base URL for Ollama."""
        return f"{self.host}:{self.port}"
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, v: str) -> str:
        """Validate and normalize the host URL."""
        v = v.strip()
        if not v.startswith(('http://', 'https://')):
            v = f"http://{v}"
        return v.rstrip('/')


class OpenAISettings(BaseModel):
    """Configuration settings for OpenAI LLM provider."""
    
    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    base_url: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL (for compatible services)"
    )
    timeout: int = Field(default=120, ge=1, description="Request timeout in seconds")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens in response")
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize the base URL."""
        if v:
            v = v.strip().rstrip('/')
        return v
    
    @model_validator(mode='after')
    def check_api_key_if_url_provided(self):
        """Warn if base_url is set but api_key is not."""
        if self.base_url and not self.api_key:
            logger.warning("OpenAI base_url is set but api_key is missing")
        return self


class LlamaCppSettings(BaseModel):
    """Configuration settings for Llama-cpp LLM provider."""
    
    model_config = {'protected_namespaces': ()}  # Allow 'model_' prefix
    
    model_path: Optional[str] = Field(default=None, description="Path to GGUF model file")
    models_dir: str = Field(default="./models", description="Directory containing model files")
    context_size: int = Field(default=2048, ge=128, le=32768, description="Context window size")
    n_threads: Optional[int] = Field(default=None, ge=1, description="Number of threads (None = auto-detect)")
    n_gpu_layers: int = Field(default=0, ge=0, description="Number of layers to offload to GPU")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    
    @field_validator('model_path')
    @classmethod
    def validate_model_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate model path."""
        if v:
            v = v.strip()
            if not v:
                return None
        return v


class RetryPolicy(BaseModel):
    """Retry policy configuration for LLM requests."""
    
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum number of retry attempts")
    initial_delay: float = Field(default=1.0, ge=0.1, description="Initial retry delay in seconds")
    max_delay: float = Field(default=60.0, ge=1.0, description="Maximum retry delay in seconds")
    exponential_base: float = Field(default=2.0, ge=1.0, description="Exponential backoff base")
    
    @model_validator(mode='after')
    def validate_delays(self):
        """Ensure max_delay is greater than initial_delay."""
        if self.max_delay < self.initial_delay:
            raise ValueError("max_delay must be greater than or equal to initial_delay")
        return self


class FallbackPreferences(BaseModel):
    """Fallback behavior configuration for LLM routing."""
    
    enabled: bool = Field(default=True, description="Enable fallback to secondary provider")
    primary_provider: Literal["ollama", "llamacpp", "openai"] = Field(
        default="ollama",
        description="Primary LLM provider to use"
    )
    fallback_provider: Literal["ollama", "llamacpp", "openai"] = Field(
        default="llamacpp",
        description="Fallback LLM provider"
    )
    secondary_fallback_provider: Optional[Literal["ollama", "llamacpp", "openai"]] = Field(
        default="openai",
        description="Secondary fallback provider (tertiary option)"
    )
    
    @model_validator(mode='after')
    def validate_providers(self):
        """Ensure primary and fallback providers are different."""
        providers = [self.primary_provider, self.fallback_provider]
        if self.secondary_fallback_provider:
            providers.append(self.secondary_fallback_provider)
        
        if self.enabled and len(providers) != len(set(providers)):
            raise ValueError("Primary, fallback, and secondary fallback providers must be different")
        return self


class LoggingSettings(BaseModel):
    """Logging configuration settings."""
    
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_enabled: bool = Field(default=True, description="Enable file logging")
    file_path: str = Field(default="logs/app.log", description="Log file path")
    console_enabled: bool = Field(default=True, description="Enable console logging")


class ModelSettings(BaseModel):
    """Default model configuration."""
    
    ollama_default: str = Field(default="llama2", description="Default Ollama model")
    llamacpp_default: str = Field(default="default.gguf", description="Default Llama-cpp model filename")
    openai_default: str = Field(default="gpt-3.5-turbo", description="Default OpenAI model")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    
    @field_validator('ollama_default', 'llamacpp_default', 'openai_default')
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Model name cannot be empty")
        return v


class UISettings(BaseModel):
    """Rich console UI configuration."""
    
    use_rich_console: bool = Field(default=True, description="Use Rich library for enhanced console output")
    color_scheme: Literal["dark", "light", "auto"] = Field(
        default="auto",
        description="Console color scheme"
    )
    show_progress_bars: bool = Field(default=True, description="Show progress bars for long operations")
    show_panels: bool = Field(default=True, description="Show panels for structured output")
    show_tables: bool = Field(default=True, description="Show tables for tabular data")
    animate: bool = Field(default=True, description="Enable animations and spinners")
    emoji_enabled: bool = Field(default=True, description="Enable emoji in console output")


class SecuritySettings(BaseModel):
    """Security and confirmation settings."""
    
    require_file_confirmation: bool = Field(
        default=True,
        description="Require confirmation before file operations"
    )
    require_git_confirmation: bool = Field(
        default=True,
        description="Require confirmation before git operations"
    )
    require_shell_confirmation: bool = Field(
        default=True,
        description="Require confirmation before shell command execution"
    )
    sandboxing_level: Literal["none", "basic", "strict"] = Field(
        default="basic",
        description="Sandboxing level for tool execution"
    )
    allowed_file_extensions: List[str] = Field(
        default=[".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml", ".toml", ".md", ".txt"],
        description="Allowed file extensions for file operations"
    )
    blocked_paths: List[str] = Field(
        default=["/etc", "/sys", "/proc", "/boot"],
        description="Blocked paths for file operations (absolute paths)"
    )


class LanguageEditorSettings(BaseModel):
    """Default editor agents for different programming languages."""
    
    python_editor: str = Field(default="code_editor", description="Default agent for Python files")
    javascript_editor: str = Field(default="code_editor", description="Default agent for JavaScript files")
    typescript_editor: str = Field(default="code_editor", description="Default agent for TypeScript files")
    html_editor: str = Field(default="code_editor", description="Default agent for HTML files")
    css_editor: str = Field(default="code_editor", description="Default agent for CSS files")
    markdown_editor: str = Field(default="code_editor", description="Default agent for Markdown files")
    json_editor: str = Field(default="code_editor", description="Default agent for JSON files")
    yaml_editor: str = Field(default="code_editor", description="Default agent for YAML files")


class ModelAssignment(BaseModel):
    """Model assignment configuration for a specific agent."""
    
    primary: str = Field(description="Primary model to use for this agent")
    fallback: Optional[str] = Field(default=None, description="Fallback model if primary unavailable")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum response tokens")
    
    @field_validator('primary', 'fallback')
    @classmethod
    def validate_model_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate model name is not empty."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Model name cannot be empty")
        return v


class ShellExecutionSettings(BaseModel):
    """Shell command execution settings."""
    
    allowed_commands: List[str] = Field(
        default=["ls", "cd", "pwd", "echo", "cat", "grep", "find", "git", "python", "pip", "npm", "node"],
        description="Whitelist of allowed shell commands (empty list = all allowed)"
    )
    blocked_commands: List[str] = Field(
        default=["rm -rf /", "mkfs", "dd", ":(){ :|:& };:"],
        description="Blacklist of dangerous shell commands"
    )
    timeout: int = Field(default=300, ge=1, description="Default timeout for shell commands in seconds")
    max_output_size: int = Field(
        default=10485760,  # 10 MB
        ge=1024,
        description="Maximum output size in bytes (10 MB default)"
    )
    enable_sudo: bool = Field(default=False, description="Allow sudo commands (USE WITH EXTREME CAUTION)")


class AgentSettings(BaseModel):
    """Configuration for agent system."""
    
    model_config = {'protected_namespaces': ()}  # Allow 'model_' prefix
    
    enabled_agents: list[str] = Field(
        default=["code_planner", "code_editor", "git_agent", "web_data"],
        description="List of enabled agents"
    )
    auto_confirm: bool = Field(
        default=False,
        description="Auto-confirm agent actions (USE WITH CAUTION)"
    )
    max_iterations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum iterations for agent orchestration"
    )
    language_editors: Dict[str, str] = Field(
        default={
            "python": "code_editor_python",
            "javascript": "code_editor_webdev",
            "typescript": "code_editor_webdev",
            "default": "code_editor"
        },
        description="Default editor agents for each language"
    )
    model_assignments: Dict[str, ModelAssignment] = Field(
        default_factory=dict,
        description="Model assignments for each agent"
    )


class ToolSettings(BaseModel):
    """Configuration for tool system."""
    
    enabled_tools: list[str] = Field(
        default=["web_fetch", "git"],
        description="List of enabled tools"
    )
    use_gitpython: bool = Field(
        default=True,
        description="Use gitpython library if available"
    )
    web_timeout: int = Field(
        default=30,
        ge=1,
        description="Default timeout for web requests in seconds"
    )
    enable_sandboxing: bool = Field(
        default=True,
        description="Enable sandboxing for tool execution"
    )
    sandbox_working_directory: Optional[str] = Field(
        default=None,
        description="Working directory for sandboxed tool execution (None = use temp directory)"
    )
    max_file_size: int = Field(
        default=104857600,  # 100 MB
        ge=1024,
        description="Maximum file size for file operations in bytes"
    )


class MCPServerConfig(BaseModel):
    """Configuration for a single MCP server."""
    
    server_id: str = Field(description="Unique server identifier")
    transport: Literal["stdio", "sse", "http"] = Field(description="Transport type")
    endpoint: str = Field(description="Server endpoint (command or URL)")
    auth: Optional[Dict[str, str]] = Field(default=None, description="Authentication credentials")
    auto_connect: bool = Field(default=False, description="Auto-connect on startup")
    timeout: int = Field(default=30, ge=1, description="Connection timeout in seconds")
    retry_count: int = Field(default=3, ge=0, le=10, description="Number of retry attempts on failure")


class MCPSettings(BaseModel):
    """Configuration for MCP (Model Context Protocol) integration."""
    
    enabled: bool = Field(default=False, description="Enable MCP integration")
    servers: list[MCPServerConfig] = Field(
        default_factory=list,
        description="List of MCP servers to connect to"
    )
    discovery_timeout: int = Field(
        default=10,
        ge=1,
        description="Timeout for tool discovery in seconds"
    )


class AppConfig(BaseModel):
    """Main application configuration."""
    
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    llamacpp: LlamaCppSettings = Field(default_factory=LlamaCppSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    models: ModelSettings = Field(default_factory=ModelSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    fallback: FallbackPreferences = Field(default_factory=FallbackPreferences)
    ui: UISettings = Field(default_factory=UISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    shell_execution: ShellExecutionSettings = Field(default_factory=ShellExecutionSettings)
    agents: AgentSettings = Field(default_factory=AgentSettings)
    tools: ToolSettings = Field(default_factory=ToolSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    
    @classmethod
    def from_yaml(cls, config_path: Path) -> "AppConfig":
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            AppConfig instance with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Handle empty YAML file
            if config_data is None:
                config_data = {}
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls(**config_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML configuration: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}") from e
    
    @classmethod
    def from_toml(cls, config_path: Path) -> "AppConfig":
        """
        Load configuration from a TOML file (legacy support).
        
        DEPRECATED: TOML format is deprecated. Please migrate to config.yaml.
        This method is kept for backward compatibility.
        
        Args:
            config_path: Path to the TOML configuration file
            
        Returns:
            AppConfig instance with loaded settings
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid or TOML support not available
        """
        if not TOML_AVAILABLE:
            raise ValueError(
                "TOML support is not available. Please install 'tomli' package "
                "or migrate to YAML configuration (config.yaml)"
            )
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        logger.warning(
            f"Loading configuration from TOML file {config_path}. "
            "TOML format is deprecated. Please migrate to config.yaml."
        )
        
        try:
            with open(config_path, 'rb') as f:
                config_data = tomllib.load(f)
            
            logger.info(f"Loaded configuration from {config_path}")
            return cls(**config_data)
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}") from e
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Load configuration from environment variables.
        
        Environment variables should be prefixed with 'AI_AGENT_' and use
        double underscores for nested settings. For example:
        - AI_AGENT_OLLAMA__HOST
        - AI_AGENT_OPENAI__API_KEY
        - AI_AGENT_LOGGING__LEVEL
        
        Returns:
            AppConfig instance with settings from environment
        """
        config_data = {}
        
        # Parse environment variables
        prefix = "AI_AGENT_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split by double underscore
                key_parts = key[len(prefix):].lower().split('__')
                
                # Build nested dictionary
                current = config_data
                for part in key_parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value (handle boolean strings)
                final_key = key_parts[-1]
                if value.lower() in ('true', 'false'):
                    current[final_key] = value.lower() == 'true'
                elif value.isdigit():
                    current[final_key] = int(value)
                else:
                    try:
                        current[final_key] = float(value)
                    except ValueError:
                        current[final_key] = value
        
        logger.info("Loaded configuration from environment variables")
        return cls(**config_data)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "AppConfig":
        """
        Load configuration with fallback strategy.
        
        Priority order:
        1. Provided config_path (YAML or TOML based on extension)
        2. config.yaml in current directory
        3. config.toml in current directory (legacy, with deprecation warning)
        4. Environment variables
        5. Default values
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            AppConfig instance with loaded settings
        """
        # Try to load from provided config_path
        if config_path and config_path.exists():
            try:
                # Determine format from extension
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return cls.from_yaml(config_path)
                elif config_path.suffix.lower() == '.toml':
                    return cls.from_toml(config_path)
                else:
                    # Try YAML first, then TOML
                    try:
                        return cls.from_yaml(config_path)
                    except Exception:
                        return cls.from_toml(config_path)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        # Try default config.yaml location (preferred)
        default_yaml = Path("config.yaml")
        if default_yaml.exists():
            try:
                return cls.from_yaml(default_yaml)
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {e}")
        
        # Try default config.toml location (legacy, backward compatibility)
        default_toml = Path("config.toml")
        if default_toml.exists():
            try:
                return cls.from_toml(default_toml)
            except Exception as e:
                logger.warning(f"Failed to load config.toml: {e}")
        
        # Try environment variables
        try:
            env_config = cls.from_env()
            
            # If we have any env config, use it, otherwise use defaults
            default_config = cls()
            has_env_vars = any(
                getattr(env_config, attr) != getattr(default_config, attr)
                for attr in vars(env_config)
            )
            
            if has_env_vars:
                logger.info("Using configuration from environment variables")
                return env_config
        except Exception as e:
            logger.warning(f"Failed to load environment config: {e}")
        
        logger.info("Using default configuration")
        return cls()
    
    def mask_sensitive_data(self) -> dict:
        """
        Return configuration as dictionary with sensitive data masked.
        
        Returns:
            Dictionary with API keys and sensitive fields masked
        """
        config_dict = self.model_dump()
        
        # Mask OpenAI API key
        if config_dict.get('openai', {}).get('api_key'):
            key = config_dict['openai']['api_key']
            config_dict['openai']['api_key'] = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
        
        return config_dict


def setup_logging(config: AppConfig) -> None:
    """
    Configure logging based on application configuration.
    
    Args:
        config: Application configuration containing logging settings
    """
    handlers = []
    
    # Console handler
    if config.logging.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(config.logging.format))
        handlers.append(console_handler)
    
    # File handler
    if config.logging.file_enabled:
        # Ensure log directory exists
        log_path = Path(config.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(config.logging.format))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    logger.info(f"Logging configured at {config.logging.level} level")



# Backward compatibility aliases
Config = AppConfig


class ConfigLoader:
    """
    Configuration loader class for backward compatibility.
    
    Wraps AppConfig to provide a simpler interface for loading and
    accessing configuration values.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Optional path to config file
        """
        if config_path:
            self.config = AppConfig.load(config_path)
        else:
            self.config = AppConfig.load()
    
    def load(self, config_path: str) -> dict:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            self.config = AppConfig()
            return self.config.model_dump()
        
        self.config = AppConfig.load(path)
        return self.config.model_dump()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., 'llm.default_model')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            # Split key by dots and traverse config
            parts = key.split('.')
            value = self.config
            
            for part in parts:
                if hasattr(value, part):
                    value = getattr(value, part)
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def validate(self, config_dict: dict) -> bool:
        """
        Validate configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            AppConfig(**config_dict)
            return True
        except Exception:
            return False
    
    def merge(self, base_config: dict, override_config: dict) -> dict:
        """
        Merge two configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Override configuration
            
        Returns:
            Merged configuration dictionary
        """
        def deep_merge(base: dict, override: dict) -> dict:
            """Deep merge two dictionaries."""
            result = base.copy()
            
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            
            return result
        
        return deep_merge(base_config, override_config)
