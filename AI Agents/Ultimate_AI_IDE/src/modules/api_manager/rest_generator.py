"""
REST API Generator

Generates REST API code for various frameworks.
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Endpoint:
    """REST API endpoint definition."""
    path: str
    method: str  # GET, POST, PUT, DELETE, PATCH
    description: str
    request_body: Optional[Dict] = None
    response_body: Optional[Dict] = None
    auth_required: bool = True


@dataclass
class Model:
    """Data model definition."""
    name: str
    fields: Dict[str, str]  # field_name: type
    relationships: Dict[str, str] = field(default_factory=dict)


@dataclass
class RESTSpec:
    """REST API specification."""
    name: str
    models: List[Model]
    endpoints: List[Endpoint]
    framework: str  # 'fastapi', 'flask', 'express', 'nestjs'
    database: str = 'sqlite'
    auth_type: str = 'jwt'


@dataclass
class APICode:
    """Generated API code."""
    files: Dict[str, str]  # filename: content
    dependencies: List[str]
    setup_instructions: str


class RESTGenerator:
    """Generates REST API code."""
    
    def __init__(self, ai_backend, project_rules: Optional[List[str]] = None):
        """
        Initialize REST generator.
        
        Args:
            ai_backend: AI backend for generation
            project_rules: Project-specific rules
        """
        self.ai_backend = ai_backend
        self.project_rules = project_rules or []
    
    def generate_rest_api(self, spec: RESTSpec) -> APICode:
        """
        Generate REST API code.
        
        Args:
            spec: API specification
            
        Returns:
            APICode with generated files
        """
        if spec.framework == 'fastapi':
            return self._generate_fastapi(spec)
        elif spec.framework == 'flask':
            return self._generate_flask(spec)
        elif spec.framework == 'express':
            return self._generate_express(spec)
        elif spec.framework == 'nestjs':
            return self._generate_nestjs(spec)
        else:
            raise ValueError(f"Unsupported framework: {spec.framework}")
    
    def _generate_fastapi(self, spec: RESTSpec) -> APICode:
        """Generate FastAPI application."""
        files = {}
        
        # Generate models
        models_code = self._generate_fastapi_models(spec.models)
        files['models.py'] = models_code
        
        # Generate routes
        routes_code = self._generate_fastapi_routes(spec.endpoints, spec.models)
        files['routes.py'] = routes_code
        
        # Generate main app
        main_code = self._generate_fastapi_main(spec)
        files['main.py'] = main_code
        
        # Generate database setup
        if spec.database:
            db_code = self._generate_fastapi_database(spec.database)
            files['database.py'] = db_code
        
        # Generate auth
        if spec.auth_type:
            auth_code = self._generate_fastapi_auth(spec.auth_type)
            files['auth.py'] = auth_code
        
        dependencies = [
            'fastapi',
            'uvicorn',
            'pydantic',
            'sqlalchemy' if spec.database else None,
            'python-jose[cryptography]' if spec.auth_type == 'jwt' else None,
            'passlib[bcrypt]' if spec.auth_type else None
        ]
        dependencies = [d for d in dependencies if d]
        
        setup_instructions = """
# FastAPI Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Run the application:
   uvicorn main:app --reload

3. Access API documentation:
   http://localhost:8000/docs
"""
        
        return APICode(
            files=files,
            dependencies=dependencies,
            setup_instructions=setup_instructions
        )
    
    def _generate_fastapi_models(self, models: List[Model]) -> str:
        """Generate FastAPI/Pydantic models."""
        code = '''"""
Data models for the API.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


'''
        
        for model in models:
            code += f"class {model.name}(BaseModel):\n"
            code += f'    """{ model.name} model."""\n'
            
            for field_name, field_type in model.fields.items():
                code += f"    {field_name}: {field_type}\n"
            
            code += "\n\n"
        
        return code
    
    def _generate_fastapi_routes(self, endpoints: List[Endpoint], 
                                 models: List[Model]) -> str:
        """Generate FastAPI routes."""
        code = '''"""
API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .models import *
from .auth import get_current_user

router = APIRouter()


'''
        
        for endpoint in endpoints:
            method = endpoint.method.lower()
            path = endpoint.path
            
            # Determine response model
            response_model = "dict"
            for model in models:
                if model.name.lower() in path.lower():
                    response_model = model.name
                    break
            
            auth_dep = ", current_user = Depends(get_current_user)" if endpoint.auth_required else ""
            
            code += f'@router.{method}("{path}")\n'
            code += f'async def {self._endpoint_to_function_name(endpoint)}'
            code += f'({auth_dep}):\n'
            code += f'    """{endpoint.description}"""\n'
            code += f'    # TODO: Implement endpoint logic\n'
            code += f'    return {{"message": "Not implemented"}}\n\n\n'
        
        return code
    
    def _generate_fastapi_main(self, spec: RESTSpec) -> str:
        """Generate FastAPI main application."""
        code = f'''"""
{spec.name} API - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="{spec.name}",
    description="API for {spec.name}",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {{"message": "Welcome to {spec.name} API"}}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {{"status": "healthy"}}
'''
        
        return code
    
    def _generate_fastapi_database(self, db_type: str) -> str:
        """Generate database setup code."""
        code = '''"""
Database configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        return code
    
    def _generate_fastapi_auth(self, auth_type: str) -> str:
        """Generate authentication code."""
        code = '''"""
Authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
'''
        
        return code
    
    def _generate_flask(self, spec: RESTSpec) -> APICode:
        """Generate Flask application."""
        files = {}
        
        # Main app
        files['app.py'] = f'''"""
{spec.name} Flask API
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return jsonify({{"message": "Welcome to {spec.name} API"}})


@app.route('/health')
def health():
    return jsonify({{"status": "healthy"}})


if __name__ == '__main__':
    app.run(debug=True)
'''
        
        dependencies = ['flask', 'flask-cors']
        
        setup_instructions = """
# Flask Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Run the application:
   python app.py

3. Access API:
   http://localhost:5000
"""
        
        return APICode(
            files=files,
            dependencies=dependencies,
            setup_instructions=setup_instructions
        )
    
    def _generate_express(self, spec: RESTSpec) -> APICode:
        """Generate Express.js application."""
        files = {}
        
        # Main app
        files['index.js'] = f'''/**
 * {spec.name} Express API
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {{
  res.json({{ message: 'Welcome to {spec.name} API' }});
}});

app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy' }});
}});

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});
'''
        
        # Package.json
        files['package.json'] = f'''{{
  "name": "{spec.name.lower().replace(' ', '-')}",
  "version": "1.0.0",
  "description": "{spec.name} API",
  "main": "index.js",
  "scripts": {{
    "start": "node index.js",
    "dev": "nodemon index.js"
  }},
  "dependencies": {{
    "express": "^4.18.0",
    "cors": "^2.8.5"
  }},
  "devDependencies": {{
    "nodemon": "^2.0.0"
  }}
}}
'''
        
        dependencies = []
        
        setup_instructions = """
# Express.js Setup

1. Install dependencies:
   npm install

2. Run the application:
   npm start

3. Access API:
   http://localhost:3000
"""
        
        return APICode(
            files=files,
            dependencies=dependencies,
            setup_instructions=setup_instructions
        )
    
    def _generate_nestjs(self, spec: RESTSpec) -> APICode:
        """Generate NestJS application (basic structure)."""
        files = {}
        
        files['main.ts'] = f'''/**
 * {spec.name} NestJS API
 */

import {{ NestFactory }} from '@nestjs/core';
import {{ AppModule }} from './app.module';

async function bootstrap() {{
  const app = await NestFactory.create(AppModule);
  app.enableCors();
  await app.listen(3000);
}}
bootstrap();
'''
        
        dependencies = []
        
        setup_instructions = """
# NestJS Setup

1. Install NestJS CLI:
   npm i -g @nestjs/cli

2. Install dependencies:
   npm install

3. Run the application:
   npm run start:dev

4. Access API:
   http://localhost:3000
"""
        
        return APICode(
            files=files,
            dependencies=dependencies,
            setup_instructions=setup_instructions
        )
    
    def _endpoint_to_function_name(self, endpoint: Endpoint) -> str:
        """Convert endpoint to function name."""
        path_parts = endpoint.path.strip('/').split('/')
        method = endpoint.method.lower()
        
        # Remove path parameters
        path_parts = [p for p in path_parts if not p.startswith('{')]
        
        if path_parts:
            name = '_'.join(path_parts)
            return f"{method}_{name}"
        else:
            return f"{method}_root"
