from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security - using pbkdf2_sha256 as fallback for bcrypt issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the main app without a prefix
app = FastAPI(title="Linux Admin Tool API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class Command(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    syntax: str
    examples: List[str]
    category: str
    tags: List[str]
    created_by: str  # user_id
    is_public: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CommandCreate(BaseModel):
    name: str
    description: str
    syntax: str
    examples: List[str]
    category: str
    tags: List[str]
    is_public: bool = True

class CommandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    syntax: Optional[str] = None
    examples: Optional[List[str]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class CommandResponse(BaseModel):
    id: str
    name: str
    description: str
    syntax: str
    examples: List[str]
    category: str
    tags: List[str]
    created_by: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

class SavedCommand(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    command_id: str
    notes: Optional[str] = None
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SavedCommandCreate(BaseModel):
    command_id: str

class CategoryWithSubcategories(BaseModel):
    category: str
    subcategories: List[str]
    notes: Optional[str] = None

class SearchQuery(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

# Helper functions
def get_password_hash(password: str) -> str:
    # Ensure password is a string for bcrypt compatibility
    if isinstance(password, bytes):
        password = password.decode('utf-8')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Ensure password is a string for bcrypt compatibility
    if isinstance(plain_password, bytes):
        plain_password = plain_password.decode('utf-8')
    return pwd_context.verify(plain_password, hashed_password)

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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return UserResponse(**user)

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_create: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": user_create.email}, {"username": user_create.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    user_data = {
        "id": str(uuid.uuid4()),
        "email": user_create.email,
        "username": user_create.username,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc),
        "is_active": True
    }
    
    await db.users.insert_one(user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["id"]}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**user_data)
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"email": user_login.email})
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse(**user)
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    return current_user

# Command Routes
@api_router.get("/commands", response_model=List[CommandResponse])
async def get_commands(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
    current_user: Optional[UserResponse] = None
):
    query = {"$or": [{"is_public": True}]}
    if current_user:
        query["$or"].append({"created_by": current_user.id})
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}
    
    commands = await db.commands.find(query).skip(offset).limit(limit).to_list(length=None)
    return [CommandResponse(**cmd) for cmd in commands]

@api_router.post("/commands/search", response_model=List[CommandResponse])
async def search_commands(
    query: Optional[str] = Body(None), 
    category: Optional[str] = Body(None), 
    tags: Optional[List[str]] = Body(None), 
    limit: Optional[int] = Body(1000), 
    offset: Optional[int] = Body(0), 
    current_user: Optional[UserResponse] = None
):
    # Build the complete query with proper $and structure
    conditions = []
    
    # Access control
    access_condition = {"$or": [{"is_public": True}]}
    if current_user:
        access_condition["$or"].append({"created_by": current_user.id})
    conditions.append(access_condition)
    
    # Full-text search
    if query:
        search_conditions = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"syntax": {"$regex": query, "$options": "i"}},
                {"examples": {"$elemMatch": {"$regex": query, "$options": "i"}}},
                {"tags": {"$elemMatch": {"$regex": query, "$options": "i"}}}
            ]
        }
        conditions.append(search_conditions)
    
    # Category filter
    if category:
        conditions.append({"category": {"$regex": category, "$options": "i"}})
    
    # Tags filter
    if tags:
        conditions.append({"tags": {"$in": tags}})
    
    # Construct final query
    if len(conditions) == 1:
        mongo_query = conditions[0]
    else:
        mongo_query = {"$and": conditions}
    
    commands = await db.commands.find(mongo_query).skip(offset).limit(limit).to_list(length=None)
    return [CommandResponse(**cmd) for cmd in commands]

@api_router.post("/commands", response_model=CommandResponse)
async def create_command(command_create: CommandCreate, current_user: UserResponse = Depends(get_current_user)):
    command_data = command_create.dict()
    command_data.update({
        "id": str(uuid.uuid4()),
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    await db.commands.insert_one(command_data)
    return CommandResponse(**command_data)

@api_router.get("/commands/{command_id}", response_model=CommandResponse)
async def get_command(command_id: str):
    command = await db.commands.find_one({"id": command_id})
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return CommandResponse(**command)

@api_router.put("/commands/{command_id}", response_model=CommandResponse)
async def update_command(command_id: str, command_update: CommandUpdate, current_user: UserResponse = Depends(get_current_user)):
    command = await db.commands.find_one({"id": command_id})
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    if command["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this command")
    
    update_data = {k: v for k, v in command_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.commands.update_one({"id": command_id}, {"$set": update_data})
    
    updated_command = await db.commands.find_one({"id": command_id})
    return CommandResponse(**updated_command)

@api_router.delete("/commands/{command_id}")
async def delete_command(command_id: str, current_user: UserResponse = Depends(get_current_user)):
    command = await db.commands.find_one({"id": command_id})
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    if command["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this command")
    
    await db.commands.delete_one({"id": command_id})
    await db.saved_commands.delete_many({"command_id": command_id})
    
    return {"message": "Command deleted successfully"}

# Saved Commands Routes
@api_router.post("/saved-commands", response_model=SavedCommand)
async def save_command(saved_command: SavedCommandCreate, current_user: UserResponse = Depends(get_current_user)):
    # Check if command exists
    command = await db.commands.find_one({"id": saved_command.command_id})
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    # Check if already saved
    existing = await db.saved_commands.find_one({
        "user_id": current_user.id,
        "command_id": saved_command.command_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Command already saved")
    
    saved_data = saved_command.dict()
    saved_data.update({
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "saved_at": datetime.now(timezone.utc)
    })
    
    await db.saved_commands.insert_one(saved_data)
    return SavedCommand(**saved_data)

@api_router.get("/saved-commands", response_model=List[CommandResponse])
async def get_saved_commands(current_user: UserResponse = Depends(get_current_user)):
    saved_commands = await db.saved_commands.find({"user_id": current_user.id}).to_list(length=None)
    command_ids = [sc["command_id"] for sc in saved_commands]
    
    commands = await db.commands.find({"id": {"$in": command_ids}}).to_list(length=None)
    return [CommandResponse(**cmd) for cmd in commands]

@api_router.delete("/saved-commands/{command_id}")
async def unsave_command(command_id: str, current_user: UserResponse = Depends(get_current_user)):
    result = await db.saved_commands.delete_one({
        "user_id": current_user.id,
        "command_id": command_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved command not found")
    
    return {"message": "Command unsaved successfully"}

# Category to Subcategory mapping
CATEGORY_SUBCATEGORIES = {
    "File Management": ["Permissions", "Search", "Compression", "Navigation", "Operations"],
    "Network Configuration": ["DNS", "Routing", "Interfaces", "Monitoring", "Troubleshooting"],
    "Networking": ["Tools", "Analysis", "Configuration", "Security", "Monitoring"],
    "System Monitoring": ["Processes", "Resources", "Logs", "Performance", "Health"],
    "Process Control": ["Management", "Scheduling", "Monitoring", "Signals"],
    "Security": ["Authentication", "Encryption", "Audit", "Firewall", "Permissions"],
    "Package Management": ["Installation", "Updates", "Repositories", "Dependencies"],
    "Text Processing": ["Editing", "Search", "Manipulation", "Analysis"],
    "Archive & Compression": ["Creation", "Extraction", "Conversion", "Management"],
    "Digital Forensics": ["Investigation", "Recovery", "Analysis", "Evidence"],
    "Exploitation": ["Testing", "Scanning", "Assessment", "Tools"],
    "Password Attacks": ["Cracking", "Analysis", "Brute Force", "Dictionary"],
    "Sniffing & Spoofing": ["Network Analysis", "Traffic Capture", "Protocol Analysis"],
    "Vulnerability Analysis": ["Scanning", "Assessment", "Reporting", "Testing"],
    "Web Application Security": ["Testing", "Scanning", "Analysis", "Exploitation"],
    "Wireless Security": ["Scanning", "Testing", "Monitoring", "Analysis"],
    "Hardware Information": ["Detection", "Monitoring", "Configuration", "Analysis"],
    "User Management": ["Accounts", "Permissions", "Groups", "Authentication"],
    "Development Tools": ["Compiling", "Debugging", "Version Control", "Testing"],
    "Text Editors": ["Configuration", "Usage", "Extensions", "Automation"],
    "Disk Management": ["Partitioning", "Mounting", "Analysis", "Maintenance"],
    "Information Gathering": ["System Info", "Network Info", "User Info", "Service Info"],
    "Network Discovery": ["Scanning", "Enumeration", "Mapping", "Analysis"],
    "Reporting": ["Generation", "Export", "Analysis", "Documentation"],
    "Social Engineering": ["Testing", "Awareness", "Tools", "Analysis"]
}

@api_router.get("/categories")
async def get_categories():
    categories = await db.commands.distinct("category")
    return {"categories": categories}

@api_router.get("/categories-with-subcategories")
async def get_categories_with_subcategories():
    """Get all categories with their subcategories"""
    db_categories = await db.commands.distinct("category")
    
    categories_with_subs = []
    for category in db_categories:
        subcategories = CATEGORY_SUBCATEGORIES.get(category, [])
        categories_with_subs.append({
            "category": category,
            "subcategories": subcategories
        })
    
    return {"categories": categories_with_subs}

@api_router.get("/tags")
async def get_tags():
    # Get all unique tags
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags"}},
        {"$sort": {"_id": 1}}
    ]
    result = await db.commands.aggregate(pipeline).to_list(length=None)
    tags = [item["_id"] for item in result]
    return {"tags": tags}

# Legacy route
@api_router.get("/")
async def root():
    return {"message": "Linux Admin Tool API"}

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
