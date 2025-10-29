"""
Validation Utilities

Provides validation functions for various inputs.
"""

import re
from pathlib import Path
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def validate_project_name(name: str) -> bool:
    """
    Validate project name.
    
    Args:
        name: Project name
        
    Returns:
        True if valid
    """
    if not name or len(name) < 1:
        return False
    
    # Allow alphanumeric, underscore, hyphen
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, name))


def validate_path(path: str, must_exist: bool = False) -> bool:
    """
    Validate file/directory path.
    
    Args:
        path: Path to validate
        must_exist: Check if path exists
        
    Returns:
        True if valid
    """
    if not path:
        return False
    
    try:
        p = Path(path)
        if must_exist:
            return p.exists()
        return True
    except Exception:
        return False


def validate_language(language: str, supported: Optional[List[str]] = None) -> bool:
    """
    Validate programming language.
    
    Args:
        language: Language name
        supported: List of supported languages
        
    Returns:
        True if valid
    """
    if supported is None:
        supported = [
            'python', 'javascript', 'typescript', 'java', 'c', 'cpp',
            'csharp', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin',
            'html', 'css', 'sql', 'bash', 'powershell'
        ]
    
    return language.lower() in supported


def validate_framework(framework: str, language: Optional[str] = None) -> bool:
    """
    Validate framework name.
    
    Args:
        framework: Framework name
        language: Programming language (optional)
        
    Returns:
        True if valid
    """
    frameworks = {
        'python': ['django', 'flask', 'fastapi', 'pyramid'],
        'javascript': ['react', 'vue', 'angular', 'express', 'nextjs'],
        'typescript': ['react', 'vue', 'angular', 'express', 'nextjs'],
    }
    
    if not framework:
        return True  # Optional
    
    if language:
        return framework.lower() in frameworks.get(language.lower(), [])
    
    # Check if framework exists in any language
    all_frameworks = set()
    for fw_list in frameworks.values():
        all_frameworks.update(fw_list)
    
    return framework.lower() in all_frameworks


def validate_email(email: str) -> bool:
    """
    Validate email address.
    
    Args:
        email: Email address
        
    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL.
    
    Args:
        url: URL string
        
    Returns:
        True if valid
    """
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_version(version: str) -> bool:
    """
    Validate semantic version string.
    
    Args:
        version: Version string (e.g., 1.0.0)
        
    Returns:
        True if valid
    """
    pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
    return bool(re.match(pattern, version))


def validate_identifier(identifier: str) -> bool:
    """
    Validate Python identifier (variable/function name).
    
    Args:
        identifier: Identifier string
        
    Returns:
        True if valid
    """
    return identifier.isidentifier()


def validate_json_string(json_str: str) -> bool:
    """
    Validate JSON string.
    
    Args:
        json_str: JSON string
        
    Returns:
        True if valid
    """
    import json
    try:
        json.loads(json_str)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def validate_port(port: int) -> bool:
    """
    Validate port number.
    
    Args:
        port: Port number
        
    Returns:
        True if valid
    """
    return 1 <= port <= 65535


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input.
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Sanitized text
    """
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text
