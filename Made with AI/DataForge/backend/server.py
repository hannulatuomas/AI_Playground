from fastapi import FastAPI, APIRouter, HTTPException, Depends, Cookie, Response
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import requests
from cryptography.fernet import Fernet
import json
import psycopg2
import mysql.connector
import pymssql
import sqlite3
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins, guarded_iter_unpack_sequence
import io
import sys
import traceback

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production-2024')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Encryption key for database credentials
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Session(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DatabaseConnection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    db_type: str  # postgresql, mysql, mongodb, sqlite, mssql
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    encrypted_password: Optional[str] = None
    file_path: Optional[str] = None  # for SQLite
    connection_string: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConnectionCreate(BaseModel):
    name: str
    db_type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None
    connection_string: Optional[str] = None

class QueryExecute(BaseModel):
    connection_id: str
    query: str

class Notebook(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    cells: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotebookCreate(BaseModel):
    name: str

class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    cells: Optional[List[Dict[str, Any]]] = None

class CellExecute(BaseModel):
    notebook_id: str
    cell_index: int

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()

def parse_connection_string(connection_string: str, db_type: str) -> dict:
    """Parse connection string into components"""
    try:
        from urllib.parse import urlparse, parse_qs
        
        # Handle different connection string formats
        if not connection_string.startswith(db_type + '://') and not connection_string.startswith('mongodb://'):
            # Try to add protocol if missing
            connection_string = f"{db_type}://{connection_string}"
        
        parsed = urlparse(connection_string)
        
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port,
            'database': parsed.path.lstrip('/') if parsed.path else None,
            'username': parsed.username,
            'password': parsed.password
        }
    except Exception as e:
        raise ValueError(f"Invalid connection string format: {str(e)}")

async def get_current_user(session_token: Optional[str] = Cookie(None)) -> User:
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check session in database
    session = await db.sessions.find_one({"session_token": session_token})
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check if session expired
    expires_at = datetime.fromisoformat(session['expires_at']) if isinstance(session['expires_at'], str) else session['expires_at']
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user = await db.users.find_one({"id": session['user_id']}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user)

# Authentication routes
@api_router.post("/auth/signup")
async def signup(user_data: UserSignup):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create user
    user = User(name=user_data.name, email=user_data.email)
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    user_dict['hashed_password'] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create session
    session_token = create_access_token({"user_id": user.id, "email": user.email})
    expires_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    session = Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at
    )
    session_dict = session.model_dump()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    
    await db.sessions.insert_one(session_dict)
    
    response = JSONResponse(content={"user": user.model_dump_json(), "message": "User created successfully"})
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/"
    )
    return response

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not pwd_context.verify(user_data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session_token = create_access_token({"user_id": user['id'], "email": user['email']})
    expires_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    session = Session(
        user_id=user['id'],
        session_token=session_token,
        expires_at=expires_at
    )
    session_dict = session.model_dump()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    session_dict['expires_at'] = session_dict['expires_at'].isoformat()
    
    await db.sessions.insert_one(session_dict)
    
    user_obj = User(**user)
    response = JSONResponse(content={"user": json.loads(user_obj.model_dump_json()), "message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/"
    )
    return response

@api_router.get("/auth/session")
async def get_session_data(x_session_id: Optional[str] = None):
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Call Emergent auth service
    try:
        response = requests.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": x_session_id}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session ID")
        
        user_data = response.json()
        
        # Check if user exists, if not create
        existing_user = await db.users.find_one({"email": user_data['email']})
        if existing_user:
            user = User(**existing_user)
        else:
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                picture=user_data.get('picture')
            )
            user_dict = user.model_dump()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            await db.users.insert_one(user_dict)
        
        # Create session
        session_token = user_data['session_token']
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session = Session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at
        )
        session_dict = session.model_dump()
        session_dict['created_at'] = session_dict['created_at'].isoformat()
        session_dict['expires_at'] = session_dict['expires_at'].isoformat()
        
        await db.sessions.insert_one(session_dict)
        
        return {
            "user": json.loads(user.model_dump_json()),
            "session_token": session_token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/auth/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user), session_token: Optional[str] = Cookie(None)):
    if session_token:
        await db.sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", samesite="none", secure=True)
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return json.loads(current_user.model_dump_json())

# Database connection routes
@api_router.post("/connections")
async def create_connection(conn_data: ConnectionCreate, current_user: User = Depends(get_current_user)):
    # Encrypt password if provided
    encrypted_password = None
    if conn_data.password:
        encrypted_password = encrypt_password(conn_data.password)
    
    connection = DatabaseConnection(
        user_id=current_user.id,
        name=conn_data.name,
        db_type=conn_data.db_type,
        host=conn_data.host,
        port=conn_data.port,
        database=conn_data.database,
        username=conn_data.username,
        encrypted_password=encrypted_password,
        file_path=conn_data.file_path,
        connection_string=conn_data.connection_string
    )
    
    conn_dict = connection.model_dump()
    conn_dict['created_at'] = conn_dict['created_at'].isoformat()
    
    await db.connections.insert_one(conn_dict)
    
    return json.loads(connection.model_dump_json())

@api_router.get("/connections")
async def get_connections(current_user: User = Depends(get_current_user)):
    connections = await db.connections.find({"user_id": current_user.id}, {"_id": 0}).to_list(None)
    return connections

@api_router.delete("/connections/{connection_id}")
async def delete_connection(connection_id: str, current_user: User = Depends(get_current_user)):
    result = await db.connections.delete_one({"id": connection_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {"message": "Connection deleted"}

@api_router.post("/connections/test")
async def test_connection(conn_data: ConnectionCreate, current_user: User = Depends(get_current_user)):
    try:
        # Parse connection string if provided
        if conn_data.connection_string and conn_data.db_type != "sqlite":
            if conn_data.db_type == "mongodb":
                # MongoDB uses connection string directly
                test_client = AsyncIOMotorClient(conn_data.connection_string)
                await test_client.server_info()
                test_client.close()
                return {"status": "success", "message": "Connection successful"}
            else:
                # Parse connection string for other databases
                parsed = parse_connection_string(conn_data.connection_string, conn_data.db_type)
                conn_data.host = parsed['host']
                conn_data.port = parsed['port']
                conn_data.database = parsed['database']
                conn_data.username = parsed['username']
                conn_data.password = parsed['password']
        
        if conn_data.db_type == "postgresql":
            conn = psycopg2.connect(
                host=conn_data.host,
                port=conn_data.port or 5432,
                database=conn_data.database,
                user=conn_data.username,
                password=conn_data.password
            )
            conn.close()
        elif conn_data.db_type == "mysql":
            conn = mysql.connector.connect(
                host=conn_data.host,
                port=conn_data.port or 3306,
                database=conn_data.database,
                user=conn_data.username,
                password=conn_data.password
            )
            conn.close()
        elif conn_data.db_type == "mssql":
            conn = pymssql.connect(
                server=conn_data.host,
                port=conn_data.port or 1433,
                database=conn_data.database,
                user=conn_data.username,
                password=conn_data.password
            )
            conn.close()
        elif conn_data.db_type == "sqlite":
            conn = sqlite3.connect(conn_data.file_path)
            conn.close()
        else:
            raise HTTPException(status_code=400, detail="Unsupported database type")
        
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Query execution
@api_router.post("/query/execute")
async def execute_query(query_data: QueryExecute, current_user: User = Depends(get_current_user)):
    # Get connection
    connection = await db.connections.find_one({"id": query_data.connection_id, "user_id": current_user.id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        results = []
        columns = []
        
        if connection['db_type'] == "postgresql":
            password = decrypt_password(connection['encrypted_password']) if connection.get('encrypted_password') else None
            conn = psycopg2.connect(
                host=connection['host'],
                port=connection.get('port', 5432),
                database=connection['database'],
                user=connection['username'],
                password=password
            )
            cursor = conn.cursor()
            cursor.execute(query_data.query)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            
            conn.commit()
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "mysql":
            password = decrypt_password(connection['encrypted_password']) if connection.get('encrypted_password') else None
            conn = mysql.connector.connect(
                host=connection['host'],
                port=connection.get('port', 3306),
                database=connection['database'],
                user=connection['username'],
                password=password
            )
            cursor = conn.cursor()
            cursor.execute(query_data.query)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            
            conn.commit()
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "mssql":
            password = decrypt_password(connection['encrypted_password']) if connection.get('encrypted_password') else None
            conn = pymssql.connect(
                server=connection['host'],
                port=connection.get('port', 1433),
                database=connection['database'],
                user=connection['username'],
                password=password
            )
            cursor = conn.cursor()
            cursor.execute(query_data.query)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            
            conn.commit()
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "sqlite":
            conn = sqlite3.connect(connection['file_path'])
            cursor = conn.cursor()
            cursor.execute(query_data.query)
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
            
            conn.commit()
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "mongodb":
            # For MongoDB, parse the query as JSON
            query_obj = json.loads(query_data.query)
            collection_name = query_obj.get('collection')
            operation = query_obj.get('operation', 'find')
            query = query_obj.get('query', {})
            
            mongo_client = AsyncIOMotorClient(connection['connection_string'])
            mongo_db = mongo_client[connection['database']]
            collection = mongo_db[collection_name]
            
            if operation == 'find':
                cursor = collection.find(query)
                docs = await cursor.to_list(length=1000)
                results = [{k: str(v) if k == '_id' else v for k, v in doc.items()} for doc in docs]
            
            mongo_client.close()
        
        return {
            "status": "success",
            "results": results,
            "columns": columns,
            "row_count": len(results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

# Notebook routes
@api_router.post("/notebooks")
async def create_notebook(notebook_data: NotebookCreate, current_user: User = Depends(get_current_user)):
    notebook = Notebook(
        user_id=current_user.id,
        name=notebook_data.name
    )
    
    notebook_dict = notebook.model_dump()
    notebook_dict['created_at'] = notebook_dict['created_at'].isoformat()
    notebook_dict['updated_at'] = notebook_dict['updated_at'].isoformat()
    
    await db.notebooks.insert_one(notebook_dict)
    
    return json.loads(notebook.model_dump_json())

@api_router.get("/notebooks")
async def get_notebooks(current_user: User = Depends(get_current_user)):
    notebooks = await db.notebooks.find({"user_id": current_user.id}, {"_id": 0}).to_list(None)
    return notebooks

@api_router.get("/notebooks/{notebook_id}")
async def get_notebook(notebook_id: str, current_user: User = Depends(get_current_user)):
    notebook = await db.notebooks.find_one({"id": notebook_id, "user_id": current_user.id}, {"_id": 0})
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return notebook

@api_router.put("/notebooks/{notebook_id}")
async def update_notebook(notebook_id: str, notebook_data: NotebookUpdate, current_user: User = Depends(get_current_user)):
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if notebook_data.name:
        update_data['name'] = notebook_data.name
    if notebook_data.cells is not None:
        update_data['cells'] = notebook_data.cells
    
    result = await db.notebooks.update_one(
        {"id": notebook_id, "user_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    notebook = await db.notebooks.find_one({"id": notebook_id}, {"_id": 0})
    return notebook

@api_router.delete("/notebooks/{notebook_id}")
async def delete_notebook(notebook_id: str, current_user: User = Depends(get_current_user)):
    result = await db.notebooks.delete_one({"id": notebook_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {"message": "Notebook deleted"}

# Python execution for notebooks
@api_router.post("/notebooks/execute-python")
async def execute_python(code: Dict[str, str], current_user: User = Depends(get_current_user)):
    try:
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        # Compile restricted code
        byte_code = compile_restricted(code['code'], '<string>', 'exec')
        
        # Safe globals
        safe_globals = {
            '__builtins__': safe_builtins,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            'json': json,
        }
        
        # Execute
        exec(byte_code, safe_globals)
        
        # Get output
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        return {
            "status": "success",
            "output": output
        }
    except Exception as e:
        sys.stdout = old_stdout
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Schema explorer
@api_router.get("/schema/{connection_id}")
async def get_schema(connection_id: str, current_user: User = Depends(get_current_user)):
    connection = await db.connections.find_one({"id": connection_id, "user_id": current_user.id}, {"_id": 0})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        schema = []
        
        if connection['db_type'] == "postgresql":
            password = decrypt_password(connection['encrypted_password']) if connection.get('encrypted_password') else None
            conn = psycopg2.connect(
                host=connection['host'],
                port=connection.get('port', 5432),
                database=connection['database'],
                user=connection['username'],
                password=password
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """)
                columns = cursor.fetchall()
                schema.append({
                    "table": table_name,
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                })
            
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "mysql":
            password = decrypt_password(connection['encrypted_password']) if connection.get('encrypted_password') else None
            conn = mysql.connector.connect(
                host=connection['host'],
                port=connection.get('port', 3306),
                database=connection['database'],
                user=connection['username'],
                password=password
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                schema.append({
                    "table": table_name,
                    "columns": [{"name": col[0], "type": col[1]} for col in columns]
                })
            
            cursor.close()
            conn.close()
            
        elif connection['db_type'] == "sqlite":
            conn = sqlite3.connect(connection['file_path'])
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                schema.append({
                    "table": table_name,
                    "columns": [{"name": col[1], "type": col[2]} for col in columns]
                })
            
            cursor.close()
            conn.close()
        
        return {"schema": schema}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
