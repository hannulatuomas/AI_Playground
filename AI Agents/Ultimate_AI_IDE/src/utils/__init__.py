"""
Utilities Package

Common utilities for UAIDE.
"""

from .logger import setup_logger, get_logger
from .constants import *
from .file_ops import (
    ensure_dir, read_file, write_file, copy_file, delete_file,
    list_files, get_file_size, file_exists, dir_exists
)
from .path_utils import (
    normalize_path, get_relative_path, join_paths, get_parent_dir,
    get_filename, get_extension, change_extension, is_subpath,
    find_project_root, sanitize_filename, expand_user, get_size_str
)
from .validators import (
    validate_project_name, validate_path, validate_language,
    validate_framework, validate_email, validate_url, validate_version,
    validate_identifier, validate_json_string, validate_port, sanitize_input
)

__all__ = [
    'setup_logger', 'get_logger',
    'ensure_dir', 'read_file', 'write_file', 'copy_file', 'delete_file',
    'list_files', 'get_file_size', 'file_exists', 'dir_exists',
    'normalize_path', 'get_relative_path', 'join_paths', 'get_parent_dir',
    'get_filename', 'get_extension', 'change_extension', 'is_subpath',
    'find_project_root', 'sanitize_filename', 'expand_user', 'get_size_str',
    'validate_project_name', 'validate_path', 'validate_language',
    'validate_framework', 'validate_email', 'validate_url', 'validate_version',
    'validate_identifier', 'validate_json_string', 'validate_port', 'sanitize_input'
]
