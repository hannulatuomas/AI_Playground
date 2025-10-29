
# Python Best Practices

## Code Organization and Structure

### Project Structure
```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── docs/
├── requirements.txt
├── setup.py
├── README.md
├── .gitignore
└── pyproject.toml
```

### Module Organization
```python
"""
Module-level docstring describing the module's purpose.

This module provides user management functionality including
authentication, authorization, and profile management.
"""

# Standard library imports
import os
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

# Third-party imports
import requests
import numpy as np
from django.db import models

# Local application imports
from .models import User
from .utils import validate_email
from ..config import settings

# Constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Module-level variables
_cache: Dict[str, Any] = {}
```

### Package Structure
```python
# __init__.py - Expose public API
from .user_service import UserService
from .auth_service import AuthService

__all__ = ['UserService', 'AuthService']
__version__ = '1.0.0'
```

## Naming Conventions

### General Rules
```python
# Variables and functions: snake_case
user_name = "John"
def get_user_data():
    pass

# Classes: PascalCase
class UserService:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
API_BASE_URL = "https://api.example.com"

# Private attributes: _snake_case (convention, not enforced)
class User:
    def __init__(self):
        self._private_attr = "private"
        self.__name_mangled = "mangled"  # Name mangling with __

# Boolean variables: use is_/has_/can_ prefix
is_active = True
has_permission = False
can_edit = True

# Type variables: PascalCase, descriptive
from typing import TypeVar
T = TypeVar('T')
UserType = TypeVar('UserType', bound='User')

# Module names: short, lowercase, underscores if needed
# user_service.py, not UserService.py or user-service.py
```

### Function Naming
```python
# Action verbs for functions
def get_user(user_id: int) -> User:
    """Fetch a user by ID."""
    pass

def create_order(data: dict) -> Order:
    """Create a new order."""
    pass

def validate_email(email: str) -> bool:
    """Validate email format."""
    pass

def is_admin(user: User) -> bool:
    """Check if user is admin."""
    pass

# Avoid abbreviations unless very common
# GOOD: calculate_total, get_user_profile
# BAD: calc_tot, get_usr_prof
```

## Error Handling Patterns

### Exception Handling
```python
# Use specific exceptions
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    logger.warning(f"User {user_id} not found")
    return None
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise

# Don't catch and ignore
# BAD:
try:
    risky_operation()
except Exception:
    pass

# Use finally for cleanup
try:
    file = open('data.txt')
    process_file(file)
finally:
    file.close()

# Or use context managers (preferred)
with open('data.txt') as file:
    process_file(file)
```

### Custom Exceptions
```python
# Create domain-specific exceptions
class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass

class UserNotFoundError(UserServiceError):
    """Raised when a user is not found."""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with ID {user_id} not found")

class ValidationError(UserServiceError):
    """Raised when validation fails."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error in {field}: {message}")

# Use in code
def get_user(user_id: int) -> User:
    if user_id <= 0:
        raise ValidationError('user_id', 'Must be positive')
    
    user = find_user(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    
    return user
```

### Exception Chaining
```python
# Preserve exception context
try:
    result = process_data(data)
except ValueError as e:
    raise ProcessingError("Failed to process data") from e

# Suppress exception context when intentional
try:
    alternative = get_alternative()
except Exception:
    raise NewError("Custom message") from None
```

### Context Managers
```python
# Create custom context managers
from contextlib import contextmanager

@contextmanager
def database_connection(db_url: str):
    """Context manager for database connections."""
    connection = connect(db_url)
    try:
        yield connection
    finally:
        connection.close()

# Usage
with database_connection(DB_URL) as conn:
    execute_query(conn)

# Class-based context manager
class FileHandler:
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False  # Don't suppress exceptions
```

## Performance Considerations

### List Comprehensions and Generators
```python
# List comprehensions for small datasets
squares = [x**2 for x in range(10)]

# Generator expressions for large datasets
squares_gen = (x**2 for x in range(1000000))

# Use generators for memory efficiency
def read_large_file(filepath: str):
    """Read file line by line without loading all into memory."""
    with open(filepath) as file:
        for line in file:
            yield line.strip()

# Generator functions
def fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Use generators with iteration
for num in fibonacci(10):
    print(num)
```

### Efficient Data Structures
```python
# Use sets for membership testing
items = {'apple', 'banana', 'cherry'}
if 'apple' in items:  # O(1) average case
    pass

# Use deque for queue operations
from collections import deque
queue = deque([1, 2, 3])
queue.append(4)      # O(1)
queue.popleft()      # O(1)

# Use defaultdict to avoid key checks
from collections import defaultdict
word_count = defaultdict(int)
for word in words:
    word_count[word] += 1  # No need to check if key exists

# Use Counter for counting
from collections import Counter
counts = Counter(['a', 'b', 'a', 'c', 'b', 'a'])
# Counter({'a': 3, 'b': 2, 'c': 1})
```

### String Operations
```python
# Use join for string concatenation
# BAD:
result = ""
for item in items:
    result += str(item) + ", "

# GOOD:
result = ", ".join(str(item) for item in items)

# Use f-strings (Python 3.6+)
name = "Alice"
age = 30
message = f"Hello, {name}! You are {age} years old."

# For complex formatting
value = 3.14159
formatted = f"{value:.2f}"  # "3.14"

# Multi-line f-strings
message = (
    f"User: {user.name}\n"
    f"Email: {user.email}\n"
    f"Status: {user.status}"
)
```

### Avoid Premature Optimization
```python
# Profile before optimizing
import cProfile
import pstats

def main():
    # Your code here
    pass

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()

# Use timeit for micro-benchmarks
import timeit

# Compare list comprehension vs map
time1 = timeit.timeit('[x**2 for x in range(100)]', number=10000)
time2 = timeit.timeit('list(map(lambda x: x**2, range(100)))', number=10000)
```

### Caching
```python
from functools import lru_cache, cache

# LRU cache for expensive computations
@lru_cache(maxsize=128)
def expensive_function(n: int) -> int:
    # Expensive computation
    return result

# Simple cache (Python 3.9+)
@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Custom caching
from functools import wraps

def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper
```

## Security Best Practices

### Input Validation
```python
# Validate and sanitize user input
def create_user(email: str, age: int) -> User:
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError('email', 'Invalid email format')
    
    # Validate age range
    if not 0 <= age <= 150:
        raise ValidationError('age', 'Age must be between 0 and 150')
    
    return User(email=email, age=age)

# Use type hints and validation libraries
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    age: int
    
    @validator('age')
    def validate_age(cls, v):
        if not 0 <= v <= 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

### SQL Injection Prevention
```python
# ALWAYS use parameterized queries
# BAD:
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# GOOD:
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))

# Use ORM (Django example)
from django.db import models

# Safe by default
users = User.objects.filter(username=username)

# Even raw queries support parameters
User.objects.raw(
    'SELECT * FROM users WHERE username = %s',
    [username]
)
```

### Password Handling
```python
# Use bcrypt or Argon2 for password hashing
import bcrypt

def hash_password(password: str) -> bytes:
    """Hash password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Or use Argon2 (recommended)
from argon2 import PasswordHasher

ph = PasswordHasher()

def hash_password_argon2(password: str) -> str:
    return ph.hash(password)

def verify_password_argon2(password: str, hashed: str) -> bool:
    try:
        ph.verify(hashed, password)
        return True
    except:
        return False
```

### Secure Configuration
```python
# Use environment variables for secrets
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
API_KEY = os.getenv('API_KEY')

# Never commit .env files
# Add to .gitignore:
# .env
# .env.local
# *.pem
# *.key

# Use secrets module for tokens
import secrets

def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def generate_secure_password(length: int = 16) -> str:
    """Generate a secure random password."""
    import string
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))
```

### Path Traversal Prevention
```python
from pathlib import Path

def safe_file_read(filename: str, base_directory: str) -> str:
    """Safely read a file preventing path traversal."""
    base_path = Path(base_directory).resolve()
    file_path = (base_path / filename).resolve()
    
    # Ensure file is within base directory
    if not str(file_path).startswith(str(base_path)):
        raise SecurityError("Path traversal attempt detected")
    
    with open(file_path) as f:
        return f.read()
```

## Testing Approaches

### Unit Testing
```python
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestUserService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.service = UserService()
        self.user = User(id=1, name="Test User")
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_get_user_success(self):
        """Test successful user retrieval."""
        result = self.service.get_user(1)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)
    
    def test_get_user_not_found(self):
        """Test user not found raises exception."""
        with self.assertRaises(UserNotFoundError):
            self.service.get_user(999)
    
    @patch('user_service.database.query')
    def test_get_user_with_mock(self, mock_query):
        """Test user retrieval with mocked database."""
        mock_query.return_value = self.user
        
        result = self.service.get_user(1)
        
        self.assertEqual(result.id, 1)
        mock_query.assert_called_once_with(id=1)

# Use pytest (modern alternative)
import pytest

def test_user_creation():
    """Test user can be created."""
    user = User(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"

def test_invalid_email_raises_error():
    """Test invalid email raises ValueError."""
    with pytest.raises(ValidationError) as exc_info:
        User(name="Bob", email="invalid")
    assert "email" in str(exc_info.value).lower()

@pytest.fixture
def user_service():
    """Fixture for UserService."""
    return UserService()

def test_with_fixture(user_service):
    """Test using fixture."""
    result = user_service.get_all_users()
    assert isinstance(result, list)

@pytest.mark.parametrize("input,expected", [
    ("alice@example.com", True),
    ("invalid", False),
    ("test@test.co.uk", True),
])
def test_email_validation(input, expected):
    """Test email validation with various inputs."""
    assert is_valid_email(input) == expected
```

### Mocking
```python
from unittest.mock import Mock, MagicMock, patch

# Mock objects
mock_database = Mock()
mock_database.query.return_value = [User(id=1)]

# Mock with side effects
mock_api = Mock()
mock_api.get.side_effect = [
    {'data': 'first'},
    {'data': 'second'},
    Exception('API Error')
]

# Patch decorators
@patch('module.external_api')
def test_with_patch(mock_api):
    mock_api.get_data.return_value = {'result': 'mocked'}
    result = my_function()
    assert result == 'mocked'

# Context manager patching
def test_with_context_manager():
    with patch('module.time.sleep') as mock_sleep:
        my_function_with_sleep()
        mock_sleep.assert_called()

# Patch multiple
@patch('module.function1')
@patch('module.function2')
def test_multiple_patches(mock_func2, mock_func1):
    # Note: decorators are applied bottom-up
    pass
```

### Integration Testing
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope='module')
def test_db():
    """Create test database."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

def test_user_crud_operations(test_db):
    """Test CRUD operations on User."""
    # Create
    user = User(name="Test", email="test@example.com")
    test_db.add(user)
    test_db.commit()
    
    # Read
    retrieved = test_db.query(User).filter_by(email="test@example.com").first()
    assert retrieved.name == "Test"
    
    # Update
    retrieved.name = "Updated"
    test_db.commit()
    
    # Delete
    test_db.delete(retrieved)
    test_db.commit()
    
    assert test_db.query(User).count() == 0
```

### Test Coverage
```python
# Run tests with coverage
# pip install pytest-cov
# pytest --cov=mymodule --cov-report=html

# Or with unittest
# coverage run -m unittest discover
# coverage report
# coverage html
```

## Documentation Standards

### Docstrings (PEP 257)
```python
def function_with_docstring(param1: int, param2: str) -> bool:
    """
    One-line summary of function.
    
    More detailed description of what the function does,
    how it works, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is negative
        TypeError: When param2 is not a string
    
    Examples:
        >>> function_with_docstring(5, "test")
        True
        >>> function_with_docstring(-1, "test")
        Traceback (most recent call last):
        ...
        ValueError: param1 must be positive
    """
    if param1 < 0:
        raise ValueError("param1 must be positive")
    return True

class DocumentedClass:
    """
    Summary of class purpose.
    
    Detailed description of the class, its behavior,
    and how to use it.
    
    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2
    
    Examples:
        >>> obj = DocumentedClass("value")
        >>> obj.method()
        'result'
    """
    
    def __init__(self, value: str):
        """
        Initialize the class.
        
        Args:
            value: Initial value for the object
        """
        self.value = value
```

### Type Hints (PEP 484)
```python
from typing import List, Dict, Optional, Union, Tuple, Callable, Any, TypeVar, Generic

# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Collections
def process_items(items: List[int]) -> Dict[str, int]:
    return {'count': len(items), 'sum': sum(items)}

# Optional (can be None)
def find_user(user_id: int) -> Optional[User]:
    return User.objects.get(id=user_id) if exists else None

# Union (multiple types)
def process_value(value: Union[int, str]) -> str:
    return str(value)

# Callable
def apply_function(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Generics
T = TypeVar('T')

def first_element(items: List[T]) -> Optional[T]:
    return items[0] if items else None

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value
    
    def get(self) -> T:
        return self.value

# Complex types
from typing import Protocol

class Drawable(Protocol):
    """Protocol for objects that can be drawn."""
    def draw(self) -> None:
        ...

def render(obj: Drawable) -> None:
    obj.draw()
```

### Module Documentation
```python
"""
Module Name: user_service.py

Description:
    This module provides user management functionality including
    user creation, retrieval, update, and deletion operations.
    
Usage:
    from user_service import UserService
    
    service = UserService()
    user = service.create_user(name="Alice", email="alice@example.com")

Author: Your Name
Date: 2024-01-01
Version: 1.0.0
"""
```

## Common Pitfalls to Avoid

### 1. Mutable Default Arguments
```python
# BAD:
def append_to_list(item, items=[]):
    items.append(item)
    return items

# GOOD:
def append_to_list(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2. Late Binding Closures
```python
# BAD:
functions = []
for i in range(5):
    functions.append(lambda: i)  # All will return 4

# GOOD:
functions = []
for i in range(5):
    functions.append(lambda x=i: x)  # Each returns its own value
```

### 3. Catching All Exceptions
```python
# BAD:
try:
    do_something()
except:  # Catches everything including KeyboardInterrupt!
    pass

# GOOD:
try:
    do_something()
except Exception as e:  # Doesn't catch system exits
    logger.error(f"Error: {e}")
```

### 4. Modifying List While Iterating
```python
# BAD:
for item in items:
    if condition(item):
        items.remove(item)  # Modifies list during iteration

# GOOD:
items = [item for item in items if not condition(item)]
# Or:
items[:] = [item for item in items if not condition(item)]
```

### 5. Using `is` for Value Comparison
```python
# BAD:
if value is True:  # Checks identity, not equality
    pass

# GOOD:
if value is True:  # Only for singletons (None, True, False)
    pass
if value == True:  # For value comparison
    pass
if value:  # Most Pythonic for truthiness
    pass
```

## Language-Specific Idioms and Patterns

### Pythonic Patterns

#### List Comprehensions
```python
# Filter and transform
squares = [x**2 for x in range(10) if x % 2 == 0]

# Nested comprehensions
matrix = [[i*j for j in range(3)] for i in range(3)]

# Dict comprehensions
word_lengths = {word: len(word) for word in words}

# Set comprehensions
unique_lengths = {len(word) for word in words}
```

#### Unpacking
```python
# Multiple assignment
a, b = 1, 2
a, b = b, a  # Swap

# Extended unpacking
first, *middle, last = [1, 2, 3, 4, 5]

# Dictionary unpacking
defaults = {'a': 1, 'b': 2}
overrides = {'b': 3, 'c': 4}
merged = {**defaults, **overrides}  # {'a': 1, 'b': 3, 'c': 4}
```

#### Context Managers
```python
# Multiple context managers
with open('input.txt') as infile, open('output.txt', 'w') as outfile:
    outfile.write(infile.read())

# Suppress exceptions
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove('file.txt')
```

#### Decorators
```python
from functools import wraps
import time

def timer(func):
    """Decorator to time function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)

# Decorator with arguments
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hello!")
```

#### Iterators and Iterables
```python
# Custom iterator
class Fibonacci:
    def __init__(self, max_count):
        self.max_count = max_count
        self.count = 0
        self.a, self.b = 0, 1
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.count >= self.max_count:
            raise StopIteration
        self.count += 1
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        return result

# Use built-in functions
from itertools import islice, cycle, chain

# Take first 5 elements
first_five = list(islice(infinite_sequence, 5))

# Cycle through items
cycling = cycle([1, 2, 3])  # 1, 2, 3, 1, 2, 3, ...

# Chain iterables
combined = chain([1, 2], [3, 4])  # 1, 2, 3, 4
```

#### Property Decorators
```python
class User:
    def __init__(self, first_name, last_name):
        self._first_name = first_name
        self._last_name = last_name
    
    @property
    def full_name(self):
        """Get full name."""
        return f"{self._first_name} {self._last_name}"
    
    @full_name.setter
    def full_name(self, name):
        """Set full name."""
        parts = name.split()
        self._first_name = parts[0]
        self._last_name = parts[-1]
    
    @property
    def email(self):
        """Get email address."""
        return f"{self._first_name.lower()}@example.com"
```

### Design Patterns

#### Singleton
```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Or use module-level instance
# singleton.py
class _Singleton:
    pass

instance = _Singleton()
```

#### Factory
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type: str) -> Animal:
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")
```

#### Observer
```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class Observer(ABC):
    @abstractmethod
    def update(self, event):
        pass
```

### Framework-Specific Patterns

#### Django
```python
# Model best practices
from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.email

# Manager methods
class UserManager(models.Manager):
    def active_users(self):
        return self.filter(is_active=True)

# Queryset optimization
users = User.objects.select_related('profile').prefetch_related('orders')
```

#### Flask
```python
from flask import Flask, jsonify, request
from functools import wraps

app = Flask(__name__)

# Decorator for authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/users')
@requires_auth
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404
```

#### FastAPI
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    
    class Config:
        orm_mode = True

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # Create user
    return user

@app.get("/users/", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100):
    users = get_users(skip=skip, limit=limit)
    return users

# Dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```
