"""
Result Class

Generic result object for operation outcomes.
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass


@dataclass
class Result:
    """
    Generic result object for operations.
    
    Attributes:
        success: Whether the operation succeeded
        message: Human-readable message
        data: Optional data payload
        errors: Optional list of error messages
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize default values"""
        if self.data is None:
            self.data = {}
        if self.errors is None:
            self.errors = []
