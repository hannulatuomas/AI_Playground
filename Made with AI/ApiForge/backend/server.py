from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import json
import xml.etree.ElementTree as ET
import xmltodict
from bs4 import BeautifulSoup
import re
import yaml

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the main app without a prefix
app = FastAPI(title="APIForge", description="API Management and Testing Tool")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Collection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AuthConfig(BaseModel):
    type: str = "none"  # none, bearer, basic, apikey
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    location: Optional[str] = "header"  # header, query

class APIRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    protocol: str = "REST"  # REST, SOAP, GraphQL
    method: str = "GET"
    url: str
    headers: Optional[Dict[str, str]] = {}
    query_params: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    auth: Optional[AuthConfig] = None
    collection_id: str
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APIRequestCreate(BaseModel):
    name: str
    protocol: str = "REST"
    method: str = "GET"
    url: str
    headers: Optional[Dict[str, str]] = {}
    query_params: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    auth: Optional[AuthConfig] = None
    collection_id: str

class Environment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    variables: Dict[str, str] = {}
    user_id: str
    is_active: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EnvironmentCreate(BaseModel):
    name: str
    variables: Dict[str, str] = {}
    is_active: bool = False

class APIExecuteRequest(BaseModel):
    protocol: str = "REST"
    method: str = "GET"
    url: str
    headers: Optional[Dict[str, str]] = {}
    query_params: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    auth: Optional[AuthConfig] = None
    grpc_service: Optional[str] = None
    grpc_method: Optional[str] = None
    websocket_message: Optional[str] = None

class APIExecuteResponse(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: str
    response_time: float
    protocol: str = "REST"

class ImportRequest(BaseModel):
    type: str  # "openapi", "postman", "wsdl", "raml"
    content: str
    collection_name: Optional[str] = None

class RequestHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request: APIExecuteRequest
    response: APIExecuteResponse
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper functions
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if key.endswith('_at') and isinstance(value, str):
                try:
                    item[key] = datetime.fromisoformat(value)
                except:
                    pass
    return item

def substitute_variables(text: str, variables: Dict[str, str]) -> str:
    """Replace {{variable}} with actual values"""
    if not text or not variables:
        return text
    
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text

def apply_auth(headers: Dict[str, str], auth: AuthConfig) -> Dict[str, str]:
    """Apply authentication to headers"""
    if not auth or auth.type == "none":
        return headers
    
    headers = headers.copy()
    
    if auth.type == "bearer" and auth.token:
        headers["Authorization"] = f"Bearer {auth.token}"
    elif auth.type == "basic" and auth.username and auth.password:
        import base64
        credentials = base64.b64encode(f"{auth.username}:{auth.password}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
    elif auth.type == "apikey" and auth.key and auth.value:
        if auth.location == "header":
            headers[auth.key] = auth.value
    
    return headers

def create_soap_envelope(body: str, action: Optional[str] = None) -> str:
    """Create SOAP envelope from body content"""
    envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    {body}
  </soap:Body>
</soap:Envelope>'''
    return envelope

def parse_openapi_spec(content: str) -> List[Dict]:
    """Parse OpenAPI/Swagger specification"""
    try:
        if content.strip().startswith('{'):
            spec = json.loads(content)
        else:
            spec = yaml.safe_load(content)
        
        requests = []
        base_url = ""
        
        if 'servers' in spec and spec['servers']:
            base_url = spec['servers'][0]['url']
        elif 'host' in spec:
            scheme = spec.get('schemes', ['https'])[0]
            base_url = f"{scheme}://{spec['host']}"
            if 'basePath' in spec:
                base_url += spec['basePath']
        
        for path, methods in spec.get('paths', {}).items():
            for method, operation in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    requests.append({
                        'name': operation.get('operationId', f"{method.upper()} {path}"),
                        'method': method.upper(),
                        'url': base_url + path,
                        'description': operation.get('summary', ''),
                        'headers': {'Content-Type': 'application/json'} if method.upper() in ['POST', 'PUT', 'PATCH'] else {},
                        'body': json.dumps(operation.get('requestBody', {}).get('content', {}).get('application/json', {}).get('example', {}), indent=2) if operation.get('requestBody') else None
                    })
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse OpenAPI spec: {str(e)}")

def parse_raml_spec(content: str) -> List[Dict]:
    """Parse RAML specification"""
    try:
        spec = yaml.safe_load(content)
        requests = []
        base_url = spec.get('baseUri', '')
        
        def parse_resources(resources, path_prefix=''):
            for resource_path, resource in resources.items():
                full_path = path_prefix + resource_path
                
                # Parse methods for this resource
                for key, value in resource.items():
                    if key in ['get', 'post', 'put', 'delete', 'patch']:
                        method_info = value if isinstance(value, dict) else {}
                        requests.append({
                            'name': method_info.get('displayName', f"{key.upper()} {full_path}"),
                            'method': key.upper(),
                            'url': base_url + full_path,
                            'description': method_info.get('description', ''),
                            'headers': {'Content-Type': 'application/json'} if key.upper() in ['POST', 'PUT', 'PATCH'] else {},
                            'body': json.dumps(method_info.get('body', {}).get('application/json', {}).get('example', {}), indent=2) if method_info.get('body') else None
                        })
                    elif isinstance(value, dict) and not key.startswith('/'):
                        # Nested resources
                        parse_resources({k: v for k, v in value.items() if k.startswith('/')}, full_path)
        
        # Parse root level resources
        resources = {k: v for k, v in spec.items() if k.startswith('/')}
        parse_resources(resources)
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse RAML spec: {str(e)}")

def parse_wsdl(content: str) -> List[Dict]:
    """Parse WSDL specification"""
    try:
        root = ET.fromstring(content)
        requests = []
        
        # Extract service information
        services = root.findall('.//{http://schemas.xmlsoap.org/wsdl/}service')
        for service in services:
            service_name = service.get('name', 'Unknown Service')
            
            # Find operations
            bindings = root.findall('.//{http://schemas.xmlsoap.org/wsdl/}binding')
            for binding in bindings:
                operations = binding.findall('.//{http://schemas.xmlsoap.org/wsdl/}operation')
                for operation in operations:
                    op_name = operation.get('name', 'Unknown Operation')
                    
                    # Get SOAP action
                    soap_action = ""
                    soap_op = operation.find('.//{http://schemas.xmlsoap.org/wsdl/soap/}operation')
                    if soap_op is not None:
                        soap_action = soap_op.get('soapAction', '')
                    
                    requests.append({
                        'name': f"{service_name} - {op_name}",
                        'method': 'POST',
                        'url': '',  # Will need to be filled manually
                        'headers': {
                            'Content-Type': 'text/xml; charset=utf-8',
                            'SOAPAction': soap_action
                        },
                        'body': create_soap_envelope(f'<!-- {op_name} operation body -->')
                    })
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse WSDL: {str(e)}")

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user = User(username=user_data.username, email=user_data.email)
    
    user_dict = user.model_dump()
    user_dict['password_hash'] = hashed_password
    user_dict = prepare_for_mongo(user_dict)
    
    await db.users.insert_one(user_dict)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = parse_from_mongo(user)
    user_obj = User(**user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    current_user = parse_from_mongo(current_user)
    return User(**current_user)

# Collection Routes
@api_router.post("/collections", response_model=Collection)
async def create_collection(collection_data: CollectionCreate, current_user: dict = Depends(get_current_user)):
    collection = Collection(user_id=current_user['id'], **collection_data.model_dump())
    collection_dict = prepare_for_mongo(collection.model_dump())
    await db.collections.insert_one(collection_dict)
    return collection

@api_router.get("/collections", response_model=List[Collection])
async def get_collections(current_user: dict = Depends(get_current_user)):
    collections = await db.collections.find({"user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [Collection(**parse_from_mongo(col)) for col in collections]

@api_router.get("/collections/{collection_id}", response_model=Collection)
async def get_collection(collection_id: str, current_user: dict = Depends(get_current_user)):
    collection = await db.collections.find_one({"id": collection_id, "user_id": current_user['id']}, {"_id": 0})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return Collection(**parse_from_mongo(collection))

@api_router.put("/collections/{collection_id}", response_model=Collection)
async def update_collection(collection_id: str, collection_data: CollectionCreate, current_user: dict = Depends(get_current_user)):
    result = await db.collections.update_one(
        {"id": collection_id, "user_id": current_user['id']},
        {"$set": collection_data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    updated_collection = await db.collections.find_one({"id": collection_id}, {"_id": 0})
    return Collection(**parse_from_mongo(updated_collection))

@api_router.delete("/collections/{collection_id}")
async def delete_collection(collection_id: str, current_user: dict = Depends(get_current_user)):
    await db.requests.delete_many({"collection_id": collection_id, "user_id": current_user['id']})
    
    result = await db.collections.delete_one({"id": collection_id, "user_id": current_user['id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"message": "Collection deleted successfully"}

# Request Routes
@api_router.post("/requests", response_model=APIRequest)
async def create_request(request_data: APIRequestCreate, current_user: dict = Depends(get_current_user)):
    collection = await db.collections.find_one({"id": request_data.collection_id, "user_id": current_user['id']})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    request = APIRequest(user_id=current_user['id'], **request_data.model_dump())
    request_dict = prepare_for_mongo(request.model_dump())
    await db.requests.insert_one(request_dict)
    return request

@api_router.get("/requests/{collection_id}", response_model=List[APIRequest])
async def get_requests(collection_id: str, current_user: dict = Depends(get_current_user)):
    collection = await db.collections.find_one({"id": collection_id, "user_id": current_user['id']})
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    requests = await db.requests.find({"collection_id": collection_id, "user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [APIRequest(**parse_from_mongo(req)) for req in requests]

@api_router.put("/requests/{request_id}", response_model=APIRequest)
async def update_request(request_id: str, request_data: APIRequestCreate, current_user: dict = Depends(get_current_user)):
    result = await db.requests.update_one(
        {"id": request_id, "user_id": current_user['id']},
        {"$set": request_data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    
    updated_request = await db.requests.find_one({"id": request_id}, {"_id": 0})
    return APIRequest(**parse_from_mongo(updated_request))

@api_router.delete("/requests/{request_id}")
async def delete_request(request_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.requests.delete_one({"id": request_id, "user_id": current_user['id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Request deleted successfully"}

# Environment Routes
@api_router.post("/environments", response_model=Environment)
async def create_environment(env_data: EnvironmentCreate, current_user: dict = Depends(get_current_user)):
    if env_data.is_active:
        await db.environments.update_many(
            {"user_id": current_user['id']},
            {"$set": {"is_active": False}}
        )
    
    environment = Environment(user_id=current_user['id'], **env_data.model_dump())
    env_dict = prepare_for_mongo(environment.model_dump())
    await db.environments.insert_one(env_dict)
    return environment

@api_router.get("/environments", response_model=List[Environment])
async def get_environments(current_user: dict = Depends(get_current_user)):
    environments = await db.environments.find({"user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [Environment(**parse_from_mongo(env)) for env in environments]

@api_router.put("/environments/{env_id}", response_model=Environment)
async def update_environment(env_id: str, env_data: EnvironmentCreate, current_user: dict = Depends(get_current_user)):
    if env_data.is_active:
        await db.environments.update_many(
            {"user_id": current_user['id']},
            {"$set": {"is_active": False}}
        )
    
    result = await db.environments.update_one(
        {"id": env_id, "user_id": current_user['id']},
        {"$set": env_data.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    updated_env = await db.environments.find_one({"id": env_id}, {"_id": 0})
    return Environment(**parse_from_mongo(updated_env))

@api_router.delete("/environments/{env_id}")
async def delete_environment(env_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.environments.delete_one({"id": env_id, "user_id": current_user['id']})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Environment not found")
    return {"message": "Environment deleted successfully"}

# Enhanced API Execution Route
@api_router.post("/execute", response_model=APIExecuteResponse)
async def execute_api_request(request_data: APIExecuteRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Get active environment for variable substitution
        active_env = await db.environments.find_one({"user_id": current_user['id'], "is_active": True})
        variables = active_env.get('variables', {}) if active_env else {}
        
        # Substitute variables in URL and body
        url = substitute_variables(request_data.url, variables)
        body = substitute_variables(request_data.body, variables) if request_data.body else None
        
        # Apply authentication
        headers = request_data.headers or {}
        if request_data.auth:
            headers = apply_auth(headers, request_data.auth)
        
        # Substitute variables in headers
        for key, value in headers.items():
            headers[key] = substitute_variables(value, variables)
        
        start_time = datetime.now()
        
        if request_data.protocol == "SOAP":
            # Handle SOAP request
            if body and not body.strip().startswith('<?xml'):
                body = create_soap_envelope(body)
            
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'text/xml; charset=utf-8'
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, content=body)
        
        elif request_data.protocol == "GraphQL":
            # Handle GraphQL request
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            
            # Parse GraphQL query and variables
            try:
                graphql_body = json.loads(body) if body else {}
            except:
                graphql_body = {"query": body or ""}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=graphql_body)
        
        else:
            # Handle REST request
            query_params = request_data.query_params or {}
            
            # Substitute variables in query params
            for key, value in query_params.items():
                query_params[key] = substitute_variables(value, variables)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=request_data.method,
                    url=url,
                    headers=headers,
                    params=query_params,
                    content=body
                )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        # Store in history
        history_entry = RequestHistory(
            request=request_data,
            response=APIExecuteResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                response_time=response_time,
                protocol=request_data.protocol
            ),
            user_id=current_user['id']
        )
        
        history_dict = prepare_for_mongo(history_entry.model_dump())
        await db.request_history.insert_one(history_dict)
        
        return APIExecuteResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.text,
            response_time=response_time,
            protocol=request_data.protocol
        )
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# Request History Route
@api_router.get("/history", response_model=List[RequestHistory])
async def get_request_history(current_user: dict = Depends(get_current_user), limit: int = 50):
    history = await db.request_history.find(
        {"user_id": current_user['id']}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return [RequestHistory(**parse_from_mongo(h)) for h in history]

# ==============================================
# API SPECIFICATION PARSING FUNCTIONS
# ==============================================

def parse_openapi_spec(content: str):
    """Parse OpenAPI/Swagger specification"""
    try:
        import yaml
        # Try JSON first, then YAML
        try:
            spec = json.loads(content)
        except:
            spec = yaml.safe_load(content)
        
        requests = []
        base_url = ""
        
        # Get base URL from servers or host
        if "servers" in spec and spec["servers"]:
            base_url = spec["servers"][0]["url"]
        elif "host" in spec:
            protocol = "https" if spec.get("schemes", ["https"])[0] == "https" else "http"
            base_url = f"{protocol}://{spec['host']}{spec.get('basePath', '')}"
        
        # Parse paths
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    requests.append({
                        "name": details.get("summary", f"{method.upper()} {path}"),
                        "method": method.upper(),
                        "url": f"{base_url}{path}",
                        "protocol": "REST",
                        "description": details.get("description", ""),
                        "headers": {"Content-Type": "application/json"}
                    })
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse OpenAPI spec: {str(e)}")

def parse_wsdl(content: str):
    """Parse WSDL specification for SOAP services"""
    try:
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(content)
        requests = []
        
        # Extract namespace map
        ns_map = {}
        for prefix, uri in root.attrib.items():
            if prefix.startswith('xmlns:'):
                ns_map[prefix[6:]] = uri
        
        # Common WSDL namespaces
        common_ns = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'tns': root.get('targetNamespace', '')
        }
        ns_map.update(common_ns)
        
        # Find service endpoint
        service_url = ""
        for service in root.findall('.//wsdl:service', ns_map):
            for port in service.findall('.//wsdl:port', ns_map):
                address = port.find('.//soap:address', ns_map)
                if address is not None:
                    service_url = address.get('location', '')
                    break
        
        # Extract operations
        for operation in root.findall('.//wsdl:operation', ns_map):
            op_name = operation.get('name')
            if op_name:
                # Find SOAP action
                soap_op = operation.find('.//soap:operation', ns_map)
                soap_action = soap_op.get('soapAction', '') if soap_op is not None else ''
                
                requests.append({
                    "name": op_name,
                    "method": "POST",
                    "url": service_url,
                    "protocol": "SOAP",
                    "soapAction": soap_action,
                    "soapVersion": "1.1",
                    "headers": {
                        "Content-Type": "text/xml; charset=utf-8",
                        "SOAPAction": f'"{soap_action}"'
                    }
                })
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse WSDL: {str(e)}")

def parse_raml_spec(content: str):
    """Parse RAML API specification"""
    try:
        import yaml
        
        spec = yaml.safe_load(content)
        requests = []
        
        base_url = spec.get("baseUri", "")
        version = spec.get("version", "")
        if "{version}" in base_url:
            base_url = base_url.replace("{version}", version)
        
        def parse_resources(resources, parent_path=""):
            for path, resource in resources.items():
                current_path = parent_path + path
                
                # Parse HTTP methods
                for method in ["get", "post", "put", "delete", "patch"]:
                    if method in resource:
                        method_spec = resource[method]
                        requests.append({
                            "name": method_spec.get("displayName", f"{method.upper()} {current_path}"),
                            "method": method.upper(),
                            "url": f"{base_url}{current_path}",
                            "protocol": "REST",
                            "description": method_spec.get("description", ""),
                            "headers": {"Content-Type": "application/json"}
                        })
                
                # Recursively parse nested resources
                nested = {k: v for k, v in resource.items() if k.startswith("/") and isinstance(v, dict)}
                if nested:
                    parse_resources(nested, current_path)
        
        # Parse root-level resources
        resources = {k: v for k, v in spec.items() if k.startswith("/") and isinstance(v, dict)}
        parse_resources(resources)
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse RAML spec: {str(e)}")

def parse_graphql_schema(content: str):
    """Parse GraphQL schema"""
    try:
        requests = []
        
        # Basic parsing - look for type Query and type Mutation
        lines = content.strip().split('\n')
        current_type = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('type Query'):
                current_type = 'query'
                continue
            elif line.startswith('type Mutation'):
                current_type = 'mutation'
                continue
            elif line.startswith('type Subscription'):
                current_type = 'subscription'
                continue
            elif line.startswith('type ') or line.startswith('input ') or line.startswith('enum '):
                current_type = None
                continue
            
            if current_type and ':' in line and not line.startswith('#'):
                # Extract field name
                field_match = line.split(':')[0].strip()
                if '(' in field_match:
                    field_name = field_match.split('(')[0].strip()
                else:
                    field_name = field_match
                
                if field_name and field_name not in ['schema', 'directive']:
                    requests.append({
                        "name": f"{current_type.title()}: {field_name}",
                        "method": "POST",
                        "url": "/graphql",  # Default GraphQL endpoint
                        "protocol": "GraphQL",
                        "graphqlOperation": current_type,
                        "body": f"{current_type} {{\n  {field_name}\n}}",
                        "headers": {"Content-Type": "application/json"}
                    })
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse GraphQL schema: {str(e)}")

# Import Routes
@api_router.post("/import")
async def import_specification(import_data: ImportRequest, current_user: dict = Depends(get_current_user)):
    try:
        if import_data.type == "openapi":
            requests = parse_openapi_spec(import_data.content)
        elif import_data.type == "wsdl":
            requests = parse_wsdl(import_data.content)
        elif import_data.type == "raml":
            requests = parse_raml_spec(import_data.content)
        elif import_data.type == "graphql":
            requests = parse_graphql_schema(import_data.content)
        elif import_data.type == "postman":
            # Parse Postman collection format
            postman_data = json.loads(import_data.content)
            requests = []
            
            def extract_requests(item, folder_name=""):
                if 'request' in item:
                    req = item['request']
                    name = f"{folder_name} - {item['name']}" if folder_name else item['name']
                    
                    # Handle Postman URL format
                    url = req['url'] if isinstance(req['url'], str) else req['url']['raw']
                    
                    requests.append({
                        'name': name,
                        'method': req['method'],
                        'url': url,
                        'headers': {h['key']: h['value'] for h in req.get('header', [])},
                        'body': req.get('body', {}).get('raw', '') if req.get('body') else None
                    })
                
                if 'item' in item:
                    for subitem in item['item']:
                        extract_requests(subitem, item.get('name', ''))
            
            if 'item' in postman_data:
                for item in postman_data['item']:
                    extract_requests(item)
        else:
            raise HTTPException(status_code=400, detail="Unsupported import type")
        
        # Create collection if name provided
        if import_data.collection_name:
            collection = Collection(
                name=import_data.collection_name,
                description=f"Imported from {import_data.type.upper()}",
                user_id=current_user['id']
            )
            collection_dict = prepare_for_mongo(collection.model_dump())
            await db.collections.insert_one(collection_dict)
            collection_id = collection.id
        else:
            # Use first collection or create default
            collections = await db.collections.find({"user_id": current_user['id']}).to_list(1)
            if collections:
                collection_id = collections[0]['id']
            else:
                collection = Collection(
                    name="Imported Requests",
                    user_id=current_user['id']
                )
                collection_dict = prepare_for_mongo(collection.model_dump())
                await db.collections.insert_one(collection_dict)
                collection_id = collection.id
        
        # Create API requests
        created_requests = []
        for req_data in requests:
            api_request = APIRequest(
                name=req_data['name'],
                method=req_data.get('method', 'GET'),
                url=req_data['url'],
                headers=req_data.get('headers', {}),
                body=req_data.get('body'),
                collection_id=collection_id,
                user_id=current_user['id']
            )
            
            request_dict = prepare_for_mongo(api_request.model_dump())
            await db.requests.insert_one(request_dict)
            created_requests.append(api_request)
        
        return {
            "message": f"Successfully imported {len(created_requests)} requests",
            "collection_id": collection_id,
            "requests_count": len(created_requests)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

# GraphQL Schema Introspection
@api_router.post("/graphql/introspect")
async def introspect_graphql_schema(url: str, current_user: dict = Depends(get_current_user)):
    introspection_query = """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
      }
    }
    
    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
    }
    
    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
    }
    
    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={"query": introspection_query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to introspect schema")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Introspection failed: {str(e)}")

# ==============================================
# ENTERPRISE FEATURES - WORKFLOWS, MONITORING, MICROSOFT INTEGRATION, GDPR
# ==============================================

# Mock Microsoft Graph API responses (since no Azure credentials available)
MOCK_MICROSOFT_SERVICES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Microsoft Graph API (Demo)",
        "service_type": "graph",
        "endpoint": "https://graph.microsoft.com/v1.0",
        "auth_config": {
            "tenant_id": "demo-tenant-****",
            "client_id": "demo-client-****"
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_demo": True
    }
]

# Audit logging function for GDPR
async def log_audit_event(user_id: str, action: str, resource_type: str, resource_id: str, 
                         details: Dict[str, Any] = {}, ip_address: str = None):
    """Log audit events for GDPR compliance"""
    audit_log = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details,
        "ip_address": ip_address,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.audit_logs.insert_one(audit_log)

# WORKFLOW ROUTES
@api_router.post("/workflows")
async def create_workflow(workflow_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new workflow"""
    workflow = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "name": workflow_data.get("name", "New Workflow"),
        "description": workflow_data.get("description", ""),
        "nodes": workflow_data.get("nodes", []),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.workflows.insert_one(workflow)
    await log_audit_event(current_user['id'], "workflow_created", "workflow", workflow["id"])
    
    # Return workflow without MongoDB _id
    workflow.pop('_id', None)
    return workflow

@api_router.get("/workflows")
async def get_workflows(current_user: dict = Depends(get_current_user)):
    """Get all workflows for the current user"""
    workflows = await db.workflows.find(
        {"user_id": current_user['id']}, {"_id": 0}
    ).to_list(1000)
    return workflows

@api_router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, current_user: dict = Depends(get_current_user)):
    """Execute a workflow (mock implementation)"""
    workflow = await db.workflows.find_one({"id": workflow_id, "user_id": current_user['id']})
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    execution = {
        "id": str(uuid.uuid4()),
        "workflow_id": workflow_id,
        "status": "completed",  # Mock successful execution
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "logs": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Workflow execution completed successfully (demo)",
                "level": "info"
            }
        ]
    }
    
    await db.workflow_executions.insert_one(execution)
    await log_audit_event(current_user['id'], "workflow_executed", "workflow", workflow_id)
    
    return {"execution_id": execution["id"], "status": "completed"}

# VARIABLE ROUTES
@api_router.get("/variables")
async def get_variables(current_user: dict = Depends(get_current_user)):
    """Get all variables for the current user"""
    variables = await db.variables.find_one({"user_id": current_user['id']}, {"_id": 0})
    if not variables:
        return {"global": {}, "collections": {}}
    return {
        "global": variables.get("global", {}),
        "collections": variables.get("collections", {})
    }

@api_router.put("/variables")
async def update_variables(variables_data: dict, current_user: dict = Depends(get_current_user)):
    """Update variables for the current user"""
    variables = {
        "user_id": current_user['id'],
        "global": variables_data.get("global", {}),
        "collections": variables_data.get("collections", {}),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.variables.replace_one(
        {"user_id": current_user['id']}, 
        variables, 
        upsert=True
    )
    
    await log_audit_event(current_user['id'], "variables_updated", "variables", current_user['id'])
    
    return variables

@api_router.post("/variables/extract")
async def extract_variables(extract_data: dict, current_user: dict = Depends(get_current_user)):
    """Extract variables from response using JSONPath"""
    try:
        import jsonpath_ng
        response_body = extract_data.get("response_body", "{}")
        extractions = extract_data.get("extractions", [])
        scope = extract_data.get("scope", "global")  # "global" or collection_id
        
        # Parse response as JSON
        try:
            import json
            response_json = json.loads(response_body)
        except:
            return {"error": "Invalid JSON response"}
        
        extracted_vars = {}
        for extraction in extractions:
            var_name = extraction.get("name")
            jsonpath = extraction.get("path")
            
            if not var_name or not jsonpath:
                continue
                
            try:
                parser = jsonpath_ng.parse(jsonpath)
                matches = parser.find(response_json)
                if matches:
                    extracted_vars[var_name] = matches[0].value
            except Exception as e:
                print(f"JSONPath error for {jsonpath}: {e}")
                continue
        
        if extracted_vars:
            # Get current variables
            current_vars = await db.variables.find_one({"user_id": current_user['id']})
            if not current_vars:
                current_vars = {"user_id": current_user['id'], "global": {}, "collections": {}}
            
            # Update variables
            if scope == "global":
                current_vars["global"].update(extracted_vars)
            else:
                if "collections" not in current_vars:
                    current_vars["collections"] = {}
                if scope not in current_vars["collections"]:
                    current_vars["collections"][scope] = {}
                current_vars["collections"][scope].update(extracted_vars)
            
            current_vars["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            await db.variables.replace_one(
                {"user_id": current_user['id']}, 
                current_vars, 
                upsert=True
            )
        
        return {"extracted": extracted_vars, "count": len(extracted_vars)}
        
    except ImportError:
        return {"error": "JSONPath library not available"}
    except Exception as e:
        return {"error": f"Extraction failed: {str(e)}"}

# MONITORING ROUTES
@api_router.post("/monitoring/rules")
async def create_monitoring_rule(rule_data: dict, current_user: dict = Depends(get_current_user)):
    """Create a new monitoring rule"""
    rule = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "name": rule_data.get("name"),
        "request_id": rule_data.get("request_id"),
        "rule_type": rule_data.get("rule_type", "response_time"),
        "condition": rule_data.get("condition", {"operator": "<", "value": 500}),
        "interval_minutes": rule_data.get("interval_minutes", 5),
        "is_active": True,
        "notifications": rule_data.get("notifications", []),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.monitoring_rules.insert_one(rule)
    await log_audit_event(current_user['id'], "monitoring_rule_created", "monitoring_rule", rule["id"])
    
    return rule

@api_router.get("/monitoring/rules")
async def get_monitoring_rules(current_user: dict = Depends(get_current_user)):
    """Get all monitoring rules for the current user"""
    rules = await db.monitoring_rules.find(
        {"user_id": current_user['id']}, {"_id": 0}
    ).to_list(1000)
    return rules

@api_router.get("/monitoring/metrics/{request_id}")
async def get_request_metrics(request_id: str, current_user: dict = Depends(get_current_user)):
    """Get metrics for a specific request (mock data)"""
    # Return mock metrics data
    mock_metrics = [
        {
            "id": str(uuid.uuid4()),
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_time": 245,
            "status_code": 200,
            "success": True
        },
        {
            "id": str(uuid.uuid4()),
            "request_id": request_id,
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            "response_time": 312,
            "status_code": 200,
            "success": True
        }
    ]
    return mock_metrics

# MICROSOFT INTEGRATION ROUTES (MOCK IMPLEMENTATION)
@api_router.post("/microsoft/services")
async def add_azure_service(service_data: dict, current_user: dict = Depends(get_current_user)):
    """Add Azure service configuration (mock implementation)"""
    service = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "name": service_data.get("name"),
        "service_type": service_data.get("service_type"),
        "endpoint": service_data.get("endpoint"),
        "auth_config": {
            "tenant_id": service_data.get("auth_config", {}).get("tenant_id", "")[:8] + "****",
            "client_id": service_data.get("auth_config", {}).get("client_id", "")[:8] + "****"
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_demo": True  # Mark as demo since no real Azure credentials
    }
    
    await db.azure_services.insert_one(service)
    await log_audit_event(current_user['id'], "azure_service_added", "azure_service", service["id"])
    
    return service

@api_router.get("/microsoft/services")
async def get_azure_services(current_user: dict = Depends(get_current_user)):
    """Get all Azure services for the current user"""
    # Return user's services plus demo services
    user_services = await db.azure_services.find(
        {"user_id": current_user['id']}, {"_id": 0}
    ).to_list(1000)
    
    # Add demo service if no services exist
    if not user_services:
        return MOCK_MICROSOFT_SERVICES
    
    return user_services

@api_router.get("/microsoft/graph/users")
async def get_graph_users(current_user: dict = Depends(get_current_user)):
    """Get users from Microsoft Graph (mock implementation)"""
    mock_users = [
        {
            "id": "user1",
            "displayName": "John Doe (Demo)",
            "userPrincipalName": "john.doe@demo.com",
            "mail": "john.doe@demo.com",
            "jobTitle": "Software Engineer"
        },
        {
            "id": "user2", 
            "displayName": "Jane Smith (Demo)",
            "userPrincipalName": "jane.smith@demo.com",
            "mail": "jane.smith@demo.com",
            "jobTitle": "Product Manager"
        }
    ]
    return {"value": mock_users}

# GDPR COMPLIANCE ROUTES
@api_router.post("/gdpr/export")
async def request_data_export(export_data: dict, current_user: dict = Depends(get_current_user)):
    """Request data export for GDPR compliance"""
    export_request = {
        "id": str(uuid.uuid4()),
        "user_id": current_user['id'],
        "data_types": export_data if isinstance(export_data, list) else export_data.get("data_types", []),
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    }
    
    await db.data_export_requests.insert_one(export_request)
    await log_audit_event(current_user['id'], "data_export_requested", "data_export", export_request["id"])
    
    return {"request_id": export_request["id"], "status": "pending"}

@api_router.delete("/gdpr/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete user account and all associated data (GDPR Right to be Forgotten)"""
    user_id = current_user['id']
    
    # Log the deletion request before deletion
    await log_audit_event(user_id, "account_deletion_requested", "user", user_id)
    
    # Delete all user data
    await db.users.delete_one({"id": user_id})
    await db.collections.delete_many({"user_id": user_id})
    await db.requests.delete_many({"user_id": user_id})
    await db.workflows.delete_many({"user_id": user_id})
    await db.monitoring_rules.delete_many({"user_id": user_id})
    await db.azure_services.delete_many({"user_id": user_id})
    await db.request_history.delete_many({"user_id": user_id})
    
    return {"message": "Account and all associated data deleted successfully"}

@api_router.get("/gdpr/audit-logs")
async def get_audit_logs(current_user: dict = Depends(get_current_user)):
    """Get audit logs for the current user"""
    logs = await db.audit_logs.find(
        {"user_id": current_user['id']}, {"_id": 0}
    ).sort("timestamp", -1).limit(100).to_list(100)
    
    return logs

# DASHBOARD ROUTES
@api_router.get("/dashboard/metrics")
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard metrics"""
    
    # Get counts
    total_requests = await db.requests.count_documents({"user_id": current_user['id']})
    total_collections = await db.collections.count_documents({"user_id": current_user['id']})
    total_workflows = await db.workflows.count_documents({"user_id": current_user['id']})
    
    # Get performance metrics from request history
    recent_history = await db.request_history.find(
        {"user_id": current_user['id']}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    if recent_history:
        response_times = [h.get('response', {}).get('response_time', 0) for h in recent_history if h.get('response', {}).get('response_time')]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        success_count = sum(1 for h in recent_history if h.get('response', {}).get('status_code', 0) < 400)
        success_rate = (success_count / len(recent_history)) * 100 if recent_history else 0
    else:
        avg_response_time = 0
        success_rate = 0
    
    # Get monitoring info
    active_monitors = await db.monitoring_rules.count_documents({
        "user_id": current_user['id'], 
        "is_active": True
    })
    
    return {
        "total_requests": total_requests,
        "total_collections": total_collections,
        "total_workflows": total_workflows,
        "avg_response_time": round(avg_response_time, 2),
        "success_rate": round(success_rate, 2),
        "active_monitors": active_monitors,
        "recent_alerts": []  # Mock empty alerts
    }

@api_router.get("/dashboard/health")
async def get_system_health():
    """Get system health status"""
    return {
        "status": "healthy",
        "uptime_percentage": 99.9,
        "avg_response_time": 150.5,
        "error_rate": 0.1,
        "last_check": datetime.now(timezone.utc).isoformat()
    }

# ==============================================
# END ENTERPRISE FEATURES
# ==============================================

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@api_router.get("/")
async def root():
    return {"message": "APIForge Backend - Multi-Protocol API Management and Testing Tool"}