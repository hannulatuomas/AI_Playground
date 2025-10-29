"""
Constants

Application-wide constants and enumerations.
"""

# Version
VERSION = "0.1.0"

# Supported Languages
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "csharp",
    "cpp",
    "bash",
    "powershell",
    "batch"
]

# Supported Frameworks
FRAMEWORKS = {
    "python": ["django", "flask", "fastapi"],
    "javascript": ["react", "express", "nextjs"],
    "typescript": ["react", "nextjs", "nestjs"],
}

# File Size Limits
MAX_FILE_LINES = 500
MAX_FUNCTION_LINES = 50

# Default Paths
DEFAULT_DB_PATH = "data/uaide.db"
DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_LOG_PATH = "logs/uaide.log"
DEFAULT_MODEL_PATH = "models/llama-3-8b-q4.gguf"

# Database Tables
DB_TABLES = [
    "projects",
    "rules",
    "memory",
    "logs",
    "prompts",
    "code_summaries"
]
