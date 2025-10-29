from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import hashlib
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the main app
app = FastAPI(title="IT Asset Management System")
api_router = APIRouter(prefix="/api")

# ========== MODELS ==========

class UserRole(str):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str = UserRole.USER
    organization_ids: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class FieldDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    label: str
    type: str  # text, number, date, boolean, dataset, file, rich_text, multi_select, asset_reference, ip_address, mac_address, url, email, phone, serial_number, version, currency, file_size, duration, password
    required: bool = False
    optional: bool = True
    default_value: Optional[Any] = None
    dataset_values: Optional[List[str]] = []  # For dataset type
    validation_rules: Optional[Dict[str, Any]] = {}
    hidden: bool = False  # Can be hidden in UI but still present
    inherited_from: Optional[str] = None  # Track where this field came from

class CustomTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    icon: Optional[str] = None
    template_type: str  # 'asset_group', 'asset_type', 'asset'
    custom_fields: List[FieldDefinition] = []
    created_by: str  # user_id
    organization_id: Optional[str] = None  # if organization-specific, None for global
    is_public: bool = False  # if other users can use it
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomTemplateCreate(BaseModel):
    name: str
    description: str
    icon: Optional[str] = None
    template_type: str
    custom_fields: List[FieldDefinition] = []
    organization_id: Optional[str] = None
    is_public: bool = False

class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    created_by: str
    custom_fields: List[FieldDefinition] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class AssetGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None  # Lucide icon name
    organization_id: str
    custom_fields: List[FieldDefinition] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssetGroupCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None
    organization_id: str
    custom_fields: List[FieldDefinition] = []

class AssetType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None  # Lucide icon name
    asset_group_id: str
    organization_id: str
    custom_fields: List[FieldDefinition] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssetTypeCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None
    asset_group_id: str
    custom_fields: List[FieldDefinition] = []

class Asset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None  # Lucide icon name
    asset_type_id: str
    asset_group_id: str
    organization_id: str
    custom_fields: List[FieldDefinition] = []
    custom_data: Dict[str, Any] = {}
    tags: List[str] = []
    relationships: List[str] = []  # Asset IDs this asset depends on
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = None
    asset_type_id: str
    custom_fields: List[FieldDefinition] = []
    custom_data: Dict[str, Any] = {}
    tags: List[str] = []
    relationships: List[str] = []

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    asset_type_id: Optional[str] = None
    custom_fields: Optional[List[FieldDefinition]] = None
    custom_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    relationships: Optional[List[str]] = None

# ========== HELPER FUNCTIONS ==========

def verify_password(plain_password, hashed_password):
    # Simple SHA-256 hash comparison for MVP
    return hashlib.sha256((plain_password + SECRET_KEY).encode()).hexdigest() == hashed_password

def get_password_hash(password):
    # Simple SHA-256 hash for MVP
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

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
    except jwt.PyJWTError:
        raise credentials_exception
    
    user_data = await db.users.find_one({"id": user_id})
    if user_data is None:
        raise credentials_exception
    return User(**user_data)

def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                result[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result
    return data

def parse_from_mongo(item):
    """Parse datetime strings back from MongoDB and remove MongoDB ObjectId"""
    if isinstance(item, dict):
        # Create a new dict to avoid modifying the original
        cleaned_item = {}
        for key, value in item.items():
            # Skip MongoDB's _id field to avoid ObjectId serialization issues
            if key == '_id':
                continue
            elif key in ['created_at', 'updated_at'] and isinstance(value, str):
                try:
                    cleaned_item[key] = datetime.fromisoformat(value)
                except:
                    cleaned_item[key] = value
            else:
                cleaned_item[key] = value
        return cleaned_item
    return item

# ========== AUTHENTICATION ROUTES ==========

@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    del user_dict["password"]
    user_obj = User(**user_dict)
    
    # Store user with hashed password
    user_store = prepare_for_mongo(user_obj.dict())
    user_store["hashed_password"] = hashed_password
    
    await db.users.insert_one(user_store)
    return user_obj

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user_data = await db.users.find_one({"email": user_credentials.email})
    if not user_data or not verify_password(user_credentials.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["id"]}, expires_delta=access_token_expires
    )
    
    user_obj = User(**parse_from_mongo(user_data))
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ========== ORGANIZATION ROUTES ==========

@api_router.post("/organizations", response_model=Organization)
async def create_organization(org_data: OrganizationCreate, current_user: User = Depends(get_current_user)):
    org_obj = Organization(**org_data.dict(), created_by=current_user.id)
    org_store = prepare_for_mongo(org_obj.dict())
    await db.organizations.insert_one(org_store)
    
    # Add user to organization
    await db.users.update_one(
        {"id": current_user.id},
        {"$addToSet": {"organization_ids": org_obj.id}}
    )
    
    return org_obj

@api_router.get("/organizations", response_model=List[Organization])
async def get_organizations(current_user: User = Depends(get_current_user)):
    orgs = await db.organizations.find({"id": {"$in": current_user.organization_ids}}).to_list(1000)
    cleaned_orgs = []
    for org in orgs:
        cleaned_org = parse_from_mongo(org)
        cleaned_orgs.append(Organization(**cleaned_org))
    return cleaned_orgs

@api_router.get("/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: str, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    org_data = await db.organizations.find_one({"id": org_id})
    if not org_data:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return Organization(**parse_from_mongo(org_data))

@api_router.put("/organizations/{org_id}", response_model=Organization)
async def update_organization(org_id: str, org_data: OrganizationCreate, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Update organization
    update_data = prepare_for_mongo({
        **org_data.dict(),
        "updated_at": datetime.now(timezone.utc)
    })
    await db.organizations.update_one({"id": org_id}, {"$set": update_data})
    
    # Return updated organization
    updated_org = await db.organizations.find_one({"id": org_id})
    return Organization(**parse_from_mongo(updated_org))

@api_router.delete("/organizations/{org_id}")
async def delete_organization(org_id: str, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Check if organization has asset groups
    groups_count = await db.asset_groups.count_documents({"organization_id": org_id})
    if groups_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete organization with existing asset groups")
    
    # Delete organization
    await db.organizations.delete_one({"id": org_id})
    
    # Remove organization from user's organization list
    await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"organization_ids": org_id}}
    )
    
    return {"message": "Organization deleted successfully"}

# ========== ASSET GROUP ROUTES ==========

@api_router.post("/asset-groups", response_model=AssetGroup)
async def create_asset_group(group_data: AssetGroupCreate, current_user: User = Depends(get_current_user)):
    if group_data.organization_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    group_obj = AssetGroup(**group_data.dict())
    group_store = prepare_for_mongo(group_obj.dict())
    await db.asset_groups.insert_one(group_store)
    return group_obj

@api_router.get("/organizations/{org_id}/asset-groups", response_model=List[AssetGroup])
async def get_asset_groups(org_id: str, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    groups = await db.asset_groups.find({"organization_id": org_id}).to_list(1000)
    cleaned_groups = []
    for group in groups:
        cleaned_group = parse_from_mongo(group)
        cleaned_groups.append(AssetGroup(**cleaned_group))
    return cleaned_groups

@api_router.put("/asset-groups/{group_id}", response_model=AssetGroup)
async def update_asset_group(group_id: str, group_data: AssetGroupCreate, current_user: User = Depends(get_current_user)):
    # Verify access
    group = await db.asset_groups.find_one({"id": group_id})
    if not group or group["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update group
    update_data = prepare_for_mongo({
        **group_data.dict(),
        "updated_at": datetime.now(timezone.utc)
    })
    await db.asset_groups.update_one({"id": group_id}, {"$set": update_data})
    
    # Return updated group
    updated_group = await db.asset_groups.find_one({"id": group_id})
    return AssetGroup(**parse_from_mongo(updated_group))

@api_router.delete("/asset-groups/{group_id}")
async def delete_asset_group(group_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    group = await db.asset_groups.find_one({"id": group_id})
    if not group or group["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if group has asset types
    types_count = await db.asset_types.count_documents({"asset_group_id": group_id})
    if types_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete group with existing asset types")
    
    # Delete group
    await db.asset_groups.delete_one({"id": group_id})
    return {"message": "Asset group deleted successfully"}

# ========== ASSET TYPE ROUTES ==========

@api_router.post("/asset-types", response_model=AssetType)
async def create_asset_type(type_data: AssetTypeCreate, current_user: User = Depends(get_current_user)):
    # Verify asset group exists and user has access
    group = await db.asset_groups.find_one({"id": type_data.asset_group_id})
    if not group or group["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Inherit fields from asset group
    inherited_fields = []
    if group.get("custom_fields"):
        for field in group["custom_fields"]:
            inherited_field = field.copy()
            inherited_field["inherited_from"] = f"group_{group['id']}"
            inherited_fields.append(inherited_field)
    
    type_obj = AssetType(**type_data.dict(), organization_id=group["organization_id"])
    type_obj.custom_fields = inherited_fields + type_obj.custom_fields
    
    type_store = prepare_for_mongo(type_obj.dict())
    await db.asset_types.insert_one(type_store)
    return type_obj

@api_router.get("/asset-groups/{group_id}/asset-types", response_model=List[AssetType])
async def get_asset_types(group_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    group = await db.asset_groups.find_one({"id": group_id})
    if not group or group["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    types = await db.asset_types.find({"asset_group_id": group_id}).to_list(1000)
    cleaned_types = []
    for type_obj in types:
        cleaned_type = parse_from_mongo(type_obj)
        cleaned_types.append(AssetType(**cleaned_type))
    return cleaned_types

@api_router.put("/asset-types/{type_id}", response_model=AssetType)
async def update_asset_type(type_id: str, type_data: AssetTypeCreate, current_user: User = Depends(get_current_user)):
    # Verify access
    asset_type = await db.asset_types.find_one({"id": type_id})
    if not asset_type or asset_type["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update type
    update_data = prepare_for_mongo({
        **type_data.dict(),
        "updated_at": datetime.now(timezone.utc),
        "organization_id": asset_type["organization_id"]
    })
    await db.asset_types.update_one({"id": type_id}, {"$set": update_data})
    
    # Return updated type
    updated_type = await db.asset_types.find_one({"id": type_id})
    return AssetType(**parse_from_mongo(updated_type))

@api_router.delete("/asset-types/{type_id}")
async def delete_asset_type(type_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    asset_type = await db.asset_types.find_one({"id": type_id})
    if not asset_type or asset_type["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if type has assets
    assets_count = await db.assets.count_documents({"asset_type_id": type_id})
    if assets_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete asset type with existing assets")
    
    # Delete type
    await db.asset_types.delete_one({"id": type_id})
    return {"message": "Asset type deleted successfully"}

# ========== ASSET ROUTES ==========

@api_router.post("/assets", response_model=Asset)
async def create_asset(asset_data: AssetCreate, current_user: User = Depends(get_current_user)):
    # Verify asset type exists and user has access
    asset_type = await db.asset_types.find_one({"id": asset_data.asset_type_id})
    if not asset_type or asset_type["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get asset group for additional field inheritance
    asset_group = await db.asset_groups.find_one({"id": asset_type["asset_group_id"]})
    
    # Prepare custom data with default values from inherited fields
    custom_data = asset_data.custom_data.copy() if asset_data.custom_data else {}
    
    # Apply defaults from asset type fields
    if asset_type.get("custom_fields"):
        for field in asset_type["custom_fields"]:
            if field["name"] not in custom_data and field.get("default_value") is not None:
                custom_data[field["name"]] = field["default_value"]
    
    # Apply defaults from asset group fields
    if asset_group and asset_group.get("custom_fields"):
        for field in asset_group["custom_fields"]:
            if field["name"] not in custom_data and field.get("default_value") is not None:
                custom_data[field["name"]] = field["default_value"]
    
    # Create asset without duplicate custom_data parameter
    asset_dict = asset_data.dict()
    asset_dict["custom_data"] = custom_data
    asset_dict["asset_group_id"] = asset_type["asset_group_id"]
    asset_dict["organization_id"] = asset_type["organization_id"]
    
    asset_obj = Asset(**asset_dict)
    asset_store = prepare_for_mongo(asset_obj.dict())
    await db.assets.insert_one(asset_store)
    return asset_obj

@api_router.get("/organizations/{org_id}/assets", response_model=List[Asset])
async def get_assets(org_id: str, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    assets = await db.assets.find({"organization_id": org_id}).to_list(1000)
    cleaned_assets = []
    for asset in assets:
        cleaned_asset = parse_from_mongo(asset)
        cleaned_assets.append(Asset(**cleaned_asset))
    return cleaned_assets

@api_router.get("/asset-types/{type_id}/assets", response_model=List[Asset])
async def get_assets_by_type(type_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    asset_type = await db.asset_types.find_one({"id": type_id})
    if not asset_type or asset_type["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    assets = await db.assets.find({"asset_type_id": type_id}).to_list(1000)
    return [Asset(**parse_from_mongo(asset)) for asset in assets]

# Duplicate endpoint removed - using the AssetUpdate version below

@api_router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    asset = await db.assets.find_one({"id": asset_id})
    if not asset or asset["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete asset
    await db.assets.delete_one({"id": asset_id})
    return {"message": "Asset deleted successfully"}

@api_router.put("/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, asset_data: AssetUpdate, current_user: User = Depends(get_current_user)):
    # Verify access
    existing_asset = await db.assets.find_one({"id": asset_id})
    if not existing_asset or existing_asset["organization_id"] not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Prepare update data
    update_data = {}
    for field, value in asset_data.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    # If asset_type_id is being changed, verify access and update relationships
    if "asset_type_id" in update_data:
        new_asset_type = await db.asset_types.find_one({"id": update_data["asset_type_id"]})
        if not new_asset_type or new_asset_type["organization_id"] not in current_user.organization_ids:
            raise HTTPException(status_code=403, detail="Access denied to new asset type")
        
        # Update asset_group_id and organization_id if asset_type changes
        update_data["asset_group_id"] = new_asset_type["asset_group_id"]
        update_data["organization_id"] = new_asset_type["organization_id"]
    
    # Add updated timestamp
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Update the asset
    await db.assets.update_one(
        {"id": asset_id},
        {"$set": prepare_for_mongo(update_data)}
    )
    
    # Return updated asset
    updated_asset_data = await db.assets.find_one({"id": asset_id})
    cleaned_asset = parse_from_mongo(updated_asset_data)
    return Asset(**cleaned_asset)

@api_router.get("/organizations/{org_id}/assets/detailed", response_model=List[Dict])
async def get_assets_detailed(org_id: str, current_user: User = Depends(get_current_user)):
    if org_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to this organization")
    
    # Get all assets with their type and group information
    assets = await db.assets.find({"organization_id": org_id}).to_list(1000)
    asset_types = await db.asset_types.find({"organization_id": org_id}).to_list(1000)
    asset_groups = await db.asset_groups.find({"organization_id": org_id}).to_list(1000)
    
    # Create lookup dictionaries
    types_dict = {t["id"]: t for t in asset_types}
    groups_dict = {g["id"]: g for g in asset_groups}
    
    # Enrich assets with type and group info
    detailed_assets = []
    for asset in assets:
        # Clean the asset data first
        cleaned_asset = parse_from_mongo(asset)
        asset_type = types_dict.get(asset["asset_type_id"], {})
        asset_group = groups_dict.get(asset["asset_group_id"], {})
        
        detailed_asset = {
            **cleaned_asset,
            "asset_type_name": asset_type.get("name", "Unknown"),
            "asset_group_name": asset_group.get("name", "Unknown"),
            "asset_type_description": asset_type.get("description", ""),
            "asset_group_description": asset_group.get("description", "")
        }
        detailed_assets.append(detailed_asset)
    
    return detailed_assets

# Old template routes removed - replaced with enhanced template endpoints below

# ========== TEMPLATE ENDPOINTS ==========

@api_router.get("/templates/default-asset-groups")
async def get_default_asset_group_templates():
    """Get pre-defined asset group templates with custom fields"""
    return [
        {
            "name": "Hardware",
            "description": "Physical IT equipment and devices",
            "icon": "Monitor",
            "custom_fields": [
                {
                    "id": "warranty_date",
                    "name": "warranty_date",
                    "label": "Warranty Expiration",
                    "type": "date",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "purchase_date",
                    "name": "purchase_date", 
                    "label": "Purchase Date",
                    "type": "date",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "cost",
                    "name": "cost",
                    "label": "Purchase Cost",
                    "type": "currency",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "location",
                    "name": "location",
                    "label": "Physical Location",
                    "type": "text",
                    "required": True,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Software",
            "description": "Software applications and licenses",
            "icon": "Code",
            "custom_fields": [
                {
                    "id": "license_key",
                    "name": "license_key",
                    "label": "License Key",
                    "type": "password",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "version",
                    "name": "version",
                    "label": "Version Number",
                    "type": "version",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "license_expiry",
                    "name": "license_expiry",
                    "label": "License Expires",
                    "type": "date",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "vendor",
                    "name": "vendor",
                    "label": "Software Vendor",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "license_seats",
                    "name": "license_seats",
                    "label": "License Seats",
                    "type": "number",
                    "required": False,
                    "default_value": 1
                }
            ]
        },
        {
            "name": "Network Equipment",
            "description": "Network infrastructure and connectivity devices",
            "icon": "Router",
            "custom_fields": [
                {
                    "id": "ip_address",
                    "name": "ip_address",
                    "label": "IP Address",
                    "type": "ip_address",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "mac_address",
                    "name": "mac_address",
                    "label": "MAC Address",
                    "type": "mac_address",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "network_status",
                    "name": "network_status",
                    "label": "Network Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Online", "Offline", "Maintenance", "Error"],
                    "default_value": "Online"
                },
                {
                    "id": "port_count",
                    "name": "port_count",
                    "label": "Port Count",
                    "type": "number",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Cloud Services",
            "description": "Cloud-based services and subscriptions",
            "icon": "Cloud",
            "custom_fields": [
                {
                    "id": "service_url",
                    "name": "service_url",
                    "label": "Service URL",
                    "type": "url",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "monthly_cost",
                    "name": "monthly_cost",
                    "label": "Monthly Cost",
                    "type": "currency",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "renewal_date",
                    "name": "renewal_date",
                    "label": "Renewal Date",
                    "type": "date",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "service_tier",
                    "name": "service_tier",
                    "label": "Service Tier",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["Basic", "Standard", "Premium", "Enterprise"],
                    "default_value": "Standard"
                }
            ]
        },
        {
            "name": "Security",
            "description": "Security tools and access management",
            "icon": "Shield",
            "custom_fields": [
                {
                    "id": "security_level",
                    "name": "security_level",
                    "label": "Security Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Low", "Medium", "High", "Critical"],
                    "default_value": "Medium"
                },
                {
                    "id": "access_control",
                    "name": "access_control",
                    "label": "Access Control Required",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "compliance_standard",
                    "name": "compliance_standard",
                    "label": "Compliance Standard",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["ISO27001", "SOC2", "GDPR", "HIPAA", "PCI-DSS"],
                    "default_value": None
                }
            ]
        },
        {
            "name": "Identity & Access",
            "description": "User accounts, credentials, and identity management",
            "icon": "User",
            "custom_fields": [
                {
                    "id": "username",
                    "name": "username",
                    "label": "Username",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "email_address",
                    "name": "email_address",
                    "label": "Email Address",
                    "type": "email",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "access_level",
                    "name": "access_level",
                    "label": "Access Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Guest", "User", "Power User", "Admin", "Super Admin"],
                    "default_value": "User"
                },
                {
                    "id": "account_status",
                    "name": "account_status",
                    "label": "Account Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Active", "Inactive", "Suspended", "Pending", "Locked"],
                    "default_value": "Active"
                },
                {
                    "id": "last_login",
                    "name": "last_login",
                    "label": "Last Login",
                    "type": "date",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Network Infrastructure",
            "description": "Cables, adapters, and network connectivity components",
            "icon": "Cable",
            "custom_fields": [
                {
                    "id": "cable_type",
                    "name": "cable_type",
                    "label": "Cable Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Ethernet Cat5e", "Ethernet Cat6", "Ethernet Cat6a", "Fiber Optic", "Coaxial", "USB-C", "HDMI", "Power"],
                    "default_value": "Ethernet Cat6"
                },
                {
                    "id": "cable_length",
                    "name": "cable_length",
                    "label": "Cable Length (meters)",
                    "type": "number",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "connector_a",
                    "name": "connector_a",
                    "label": "Connector Type A",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "connector_b",
                    "name": "connector_b",
                    "label": "Connector Type B",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "max_bandwidth",
                    "name": "max_bandwidth",
                    "label": "Max Bandwidth",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Adapters & Accessories",
            "description": "Dongles, converters, and peripheral adapters",
            "icon": "Plug",
            "custom_fields": [
                {
                    "id": "adapter_type",
                    "name": "adapter_type",
                    "label": "Adapter Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["USB-C to HDMI", "USB-C to VGA", "USB Hub", "Power Adapter", "Audio Adapter", "Network Adapter", "Display Adapter", "Docking Station"],
                    "default_value": "USB Hub"
                },
                {
                    "id": "input_connector",
                    "name": "input_connector",
                    "label": "Input Connector",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "output_connector",
                    "name": "output_connector",
                    "label": "Output Connector",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "power_rating",
                    "name": "power_rating",
                    "label": "Power Rating (W)",
                    "type": "number",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "compatibility",
                    "name": "compatibility",
                    "label": "Device Compatibility",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Security Testing Tools",
            "description": "Penetration testing and cybersecurity equipment",
            "icon": "Bug",
            "custom_fields": [
                {
                    "id": "tool_category",
                    "name": "tool_category",
                    "label": "Tool Category",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Network Scanner", "WiFi Auditing", "USB Testing", "RFID/NFC", "Radio Frequency", "Physical Security", "Social Engineering"],
                    "default_value": "Network Scanner"
                },
                {
                    "id": "operating_frequency",
                    "name": "operating_frequency",
                    "label": "Operating Frequency",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "supported_protocols",
                    "name": "supported_protocols",
                    "label": "Supported Protocols",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["WiFi", "Bluetooth", "NFC", "RFID", "GSM", "LTE", "Zigbee", "LoRa"],
                    "default_value": None
                },
                {
                    "id": "legal_status",
                    "name": "legal_status",
                    "label": "Legal Usage Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Authorized Use Only", "Professional Testing", "Educational", "Research", "Restricted"],
                    "default_value": "Authorized Use Only"
                },
                {
                    "id": "certification_required",
                    "name": "certification_required",
                    "label": "Certification Required",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Smart Devices & Gadgets",
            "description": "IoT devices, smart home, and electronic gadgets",
            "icon": "Smartphone",
            "custom_fields": [
                {
                    "id": "device_category",
                    "name": "device_category",
                    "label": "Device Category",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Smart Home", "Wearable", "IoT Sensor", "Smart Speaker", "Streaming Device", "Gaming", "Health Monitor", "Automation"],
                    "default_value": "Smart Home"
                },
                {
                    "id": "connectivity",
                    "name": "connectivity",
                    "label": "Connectivity Options",
                    "type": "multi_select",
                    "required": True,
                    "dataset_values": ["WiFi", "Bluetooth", "Zigbee", "Z-Wave", "Thread", "Ethernet", "Cellular", "USB"],
                    "default_value": "WiFi"
                },
                {
                    "id": "power_source",
                    "name": "power_source",
                    "label": "Power Source",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Battery", "USB Powered", "Wall Adapter", "PoE", "Solar", "Hardwired"],
                    "default_value": "USB Powered"
                },
                {
                    "id": "battery_life",
                    "name": "battery_life",
                    "label": "Battery Life (hours)",
                    "type": "number",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "firmware_version",
                    "name": "firmware_version",
                    "label": "Firmware Version",
                    "type": "version",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Storage Devices",
            "description": "USB drives, external HDDs, SSDs, and storage media",
            "icon": "HardDrive",
            "custom_fields": [
                {
                    "id": "storage_type",
                    "name": "storage_type",
                    "label": "Storage Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["USB Flash Drive", "External HDD", "External SSD", "SD Card", "microSD", "CD/DVD", "Blu-ray", "Tape Drive"],
                    "default_value": "External SSD"
                },
                {
                    "id": "capacity",
                    "name": "capacity",
                    "label": "Storage Capacity",
                    "type": "file_size",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "interface",
                    "name": "interface",
                    "label": "Interface Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["USB 2.0", "USB 3.0", "USB 3.1", "USB-C", "Thunderbolt", "eSATA", "FireWire"],
                    "default_value": "USB 3.0"
                },
                {
                    "id": "encryption_enabled",
                    "name": "encryption_enabled",
                    "label": "Encryption Enabled",
                    "type": "boolean",
                    "required": True,
                    "default_value": False
                },
                {
                    "id": "file_system",
                    "name": "file_system",
                    "label": "File System",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["NTFS", "exFAT", "FAT32", "ext4", "HFS+", "APFS"],
                    "default_value": "NTFS"
                }
            ]
        },
        {
            "name": "Cloud & Virtual Resources",
            "description": "Cloud instances, virtual infrastructure, and SaaS platforms",
            "icon": "Cloud",
            "custom_fields": [
                {
                    "id": "provider",
                    "name": "provider",
                    "label": "Cloud Provider",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["AWS", "Microsoft Azure", "Google Cloud", "DigitalOcean", "Linode", "Vultr", "IBM Cloud", "Oracle Cloud"],
                    "default_value": "AWS"
                },
                {
                    "id": "region",
                    "name": "region",
                    "label": "Region/Zone",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "instance_type",
                    "name": "instance_type",
                    "label": "Instance Type/Size",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "monthly_cost",
                    "name": "monthly_cost",
                    "label": "Monthly Cost",
                    "type": "currency",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "auto_scaling",
                    "name": "auto_scaling",
                    "label": "Auto Scaling Enabled",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "Digital & Data Assets",
            "description": "Digital files, documents, intellectual property, and data repositories",
            "icon": "FileText",
            "custom_fields": [
                {
                    "id": "asset_type",
                    "name": "asset_type",
                    "label": "Digital Asset Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Document", "Image", "Video", "Audio", "Code Repository", "Dataset", "License", "Certificate", "Backup"],
                    "default_value": "Document"
                },
                {
                    "id": "file_format",
                    "name": "file_format",
                    "label": "File Format",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "file_size",
                    "name": "file_size",
                    "label": "File Size",
                    "type": "file_size",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "confidentiality_level",
                    "name": "confidentiality_level",
                    "label": "Confidentiality Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Public", "Internal", "Confidential", "Restricted", "Top Secret"],
                    "default_value": "Internal"
                },
                {
                    "id": "retention_period",
                    "name": "retention_period",
                    "label": "Retention Period",
                    "type": "duration",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Databases",
            "description": "Database servers, instances, and data management systems",
            "icon": "Database",
            "custom_fields": [
                {
                    "id": "database_type",
                    "name": "database_type",
                    "label": "Database Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["MySQL", "PostgreSQL", "SQL Server", "Oracle", "MongoDB", "Redis", "Cassandra", "Elasticsearch", "InfluxDB", "SQLite"],
                    "default_value": "PostgreSQL"
                },
                {
                    "id": "database_version",
                    "name": "database_version",
                    "label": "Version",
                    "type": "version",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "environment",
                    "name": "environment",
                    "label": "Environment",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Development", "Testing", "Staging", "Production", "Backup"],
                    "default_value": "Production"
                },
                {
                    "id": "database_size",
                    "name": "database_size",
                    "label": "Database Size",
                    "type": "file_size",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "backup_frequency",
                    "name": "backup_frequency",
                    "label": "Backup Frequency",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Hourly", "Daily", "Weekly", "Monthly", "On-Demand", "Continuous"],
                    "default_value": "Daily"
                }
            ]
        },
        {
            "name": "Virtual Machines",
            "description": "VMs, containers, and virtualized computing resources",
            "icon": "Server",
            "custom_fields": [
                {
                    "id": "hypervisor",
                    "name": "hypervisor",
                    "label": "Hypervisor/Platform",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["VMware vSphere", "Microsoft Hyper-V", "KVM", "Xen", "Proxmox", "VirtualBox", "Docker", "Kubernetes", "OpenStack"],
                    "default_value": "VMware vSphere"
                },
                {
                    "id": "operating_system",
                    "name": "operating_system",
                    "label": "Operating System",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "virtualization_type",
                    "name": "virtualization_type",
                    "label": "Virtualization Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Full Virtualization", "Paravirtualization", "Container", "OS-level Virtualization"],
                    "default_value": "Full Virtualization"
                },
                {
                    "id": "allocated_cpu",
                    "name": "allocated_cpu",
                    "label": "Allocated CPU Cores",
                    "type": "number",
                    "required": False,
                    "default_value": 2
                },
                {
                    "id": "allocated_memory",
                    "name": "allocated_memory",
                    "label": "Allocated Memory (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 4
                },
                {
                    "id": "primary_services",
                    "name": "primary_services",
                    "label": "Primary Services",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["Web Server", "Database", "Application Server", "Load Balancer", "Cache", "Monitoring", "Backup", "Development"],
                    "default_value": None
                }
            ]
        },
        {
            "name": "Licenses & Compliance",
            "description": "Software licenses, certificates, and compliance documentation",
            "icon": "FileText",
            "custom_fields": [
                {
                    "id": "license_type",
                    "name": "license_type",
                    "label": "License Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Software License", "SSL Certificate", "Domain Registration", "Patent", "Trademark", "Copyright", "Compliance Certificate"],
                    "default_value": "Software License"
                },
                {
                    "id": "license_key",
                    "name": "license_key",
                    "label": "License Key/Certificate",
                    "type": "password",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "expiration_date",
                    "name": "expiration_date",
                    "label": "Expiration Date",
                    "type": "date",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "renewal_required",
                    "name": "renewal_required",
                    "label": "Auto-Renewal Required",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "compliance_standard",
                    "name": "compliance_standard",
                    "label": "Compliance Standard",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["ISO 27001", "SOC 2", "GDPR", "HIPAA", "PCI DSS", "FedRAMP", "NIST"],
                    "default_value": None
                }
            ]
        },
        {
            "name": "Networks & VLANs",
            "description": "Network segments, VLANs, WiFi networks, and network infrastructure",
            "icon": "Network",
            "custom_fields": [
                {
                    "id": "network_type",
                    "name": "network_type",
                    "label": "Network Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["LAN", "VLAN", "WiFi", "WAN", "VPN", "DMZ", "Guest Network", "Management Network"],
                    "default_value": "LAN"
                },
                {
                    "id": "network_address",
                    "name": "network_address",
                    "label": "Network Address (CIDR)",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "vlan_id",
                    "name": "vlan_id",
                    "label": "VLAN ID",
                    "type": "number",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "gateway_ip",
                    "name": "gateway_ip",
                    "label": "Gateway IP Address",
                    "type": "ip_address",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "dhcp_enabled",
                    "name": "dhcp_enabled",
                    "label": "DHCP Enabled",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "security_level",
                    "name": "security_level",
                    "label": "Security Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Open", "WPA2", "WPA3", "Enterprise", "802.1X", "VPN Required"],
                    "default_value": "WPA3"
                }
            ]
        },
        {
            "name": "Network Interfaces",
            "description": "Physical and virtual network interfaces, ports, and connections",
            "icon": "Plug",
            "custom_fields": [
                {
                    "id": "interface_type",
                    "name": "interface_type",
                    "label": "Interface Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Ethernet", "Fiber Optic", "WiFi", "Virtual", "Loopback", "Tunnel", "Bond", "Bridge"],
                    "default_value": "Ethernet"
                },
                {
                    "id": "port_speed",
                    "name": "port_speed",
                    "label": "Port Speed",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["10 Mbps", "100 Mbps", "1 Gbps", "10 Gbps", "25 Gbps", "40 Gbps", "100 Gbps"],
                    "default_value": "1 Gbps"
                },
                {
                    "id": "interface_status",
                    "name": "interface_status",
                    "label": "Interface Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Up", "Down", "Admin Down", "Testing", "Dormant", "Not Present"],
                    "default_value": "Up"
                },
                {
                    "id": "assigned_ip",
                    "name": "assigned_ip",
                    "label": "Assigned IP Address",
                    "type": "ip_address",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "mac_address",
                    "name": "mac_address",
                    "label": "MAC Address",
                    "type": "mac_address",
                    "required": True,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Firewalls & Switches",
            "description": "Network security devices, managed switches, and routing equipment",
            "icon": "Shield",
            "custom_fields": [
                {
                    "id": "device_type",
                    "name": "device_type",
                    "label": "Device Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Firewall", "Managed Switch", "Layer 3 Switch", "Router", "Load Balancer", "IDS/IPS", "Proxy", "Access Point"],
                    "default_value": "Firewall"
                },
                {
                    "id": "port_count",
                    "name": "port_count",
                    "label": "Port Count",
                    "type": "number",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "management_ip",
                    "name": "management_ip",
                    "label": "Management IP",
                    "type": "ip_address",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "firmware_version",
                    "name": "firmware_version",
                    "label": "Firmware Version",
                    "type": "version",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "security_features",
                    "name": "security_features",
                    "label": "Security Features",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["Stateful Inspection", "DPI", "VPN Support", "IPS", "Anti-malware", "Content Filtering", "DDoS Protection"],
                    "default_value": None
                },
                {
                    "id": "high_availability",
                    "name": "high_availability",
                    "label": "High Availability Configured",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "Internal Services",
            "description": "Internal applications, microservices, APIs, and system services",
            "icon": "Cog",
            "custom_fields": [
                {
                    "id": "service_type",
                    "name": "service_type",
                    "label": "Service Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Web Service", "API", "Database Service", "Authentication", "Monitoring", "Logging", "Backup", "File Service", "Print Service"],
                    "default_value": "Web Service"
                },
                {
                    "id": "service_port",
                    "name": "service_port",
                    "label": "Service Port",
                    "type": "number",
                    "required": True,
                    "default_value": 80
                },
                {
                    "id": "protocol",
                    "name": "protocol",
                    "label": "Protocol",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["HTTP", "HTTPS", "TCP", "UDP", "SSH", "FTP", "SMTP", "DNS", "LDAP"],
                    "default_value": "HTTPS"
                },
                {
                    "id": "service_status",
                    "name": "service_status",
                    "label": "Service Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Running", "Stopped", "Starting", "Stopping", "Failed", "Unknown"],
                    "default_value": "Running"
                },
                {
                    "id": "auto_start",
                    "name": "auto_start",
                    "label": "Auto Start on Boot",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "dependencies",
                    "name": "dependencies",
                    "label": "Service Dependencies",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Website Links & URLs",
            "description": "External websites, web applications, and online resources",
            "icon": "Globe",
            "custom_fields": [
                {
                    "id": "url_address",
                    "name": "url_address",
                    "label": "URL Address",
                    "type": "url",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "site_category",
                    "name": "site_category",
                    "label": "Site Category",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Corporate Website", "Web Application", "Admin Panel", "Documentation", "Monitoring", "Support Portal", "API Endpoint", "Third-party Service"],
                    "default_value": "Web Application"
                },
                {
                    "id": "authentication_required",
                    "name": "authentication_required",
                    "label": "Authentication Required",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "ssl_certificate",
                    "name": "ssl_certificate",
                    "label": "SSL Certificate Status",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Valid", "Expired", "Self-Signed", "Invalid", "Not Present"],
                    "default_value": "Valid"
                },
                {
                    "id": "last_checked",
                    "name": "last_checked",
                    "label": "Last Availability Check",
                    "type": "date",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "criticality_level",
                    "name": "criticality_level",
                    "label": "Criticality Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Low", "Medium", "High", "Critical", "Business Critical"],
                    "default_value": "Medium"
                }
            ]
        }
    ]

@api_router.get("/templates/default-asset-types")
async def get_default_asset_type_templates():
    """Get pre-defined asset type templates with custom fields"""
    return [
        {
            "name": "Desktop Computer",
            "description": "Desktop workstations and PCs",
            "icon": "Monitor",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "serial_number",
                    "name": "serial_number", 
                    "label": "Serial Number",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "processor",
                    "name": "processor",
                    "label": "Processor",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "memory_gb",
                    "name": "memory_gb",
                    "label": "Memory (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 16
                },
                {
                    "id": "storage_gb",
                    "name": "storage_gb",
                    "label": "Storage (GB)", 
                    "type": "number",
                    "required": False,
                    "default_value": 512
                }
            ]
        },
        {
            "name": "Laptop",
            "description": "Portable laptops and notebooks",
            "icon": "Laptop",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "serial_number",
                    "name": "serial_number",
                    "label": "Serial Number",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "processor",
                    "name": "processor",
                    "label": "Processor",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "memory_gb",
                    "name": "memory_gb",
                    "label": "Memory (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 8
                },
                {
                    "id": "battery_health",
                    "name": "battery_health",
                    "label": "Battery Health (%)",
                    "type": "number",
                    "required": False,
                    "default_value": 100
                }
            ]
        },
        {
            "name": "Server",
            "description": "Physical and virtual servers",
            "icon": "Server",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "server_type",
                    "name": "server_type",
                    "label": "Server Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Physical", "Virtual", "Container", "Cloud Instance"],
                    "default_value": "Physical"
                },
                {
                    "id": "cpu_cores",
                    "name": "cpu_cores",
                    "label": "CPU Cores",
                    "type": "number",
                    "required": False,
                    "default_value": 8
                },
                {
                    "id": "memory_gb",
                    "name": "memory_gb",
                    "label": "Memory (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 32
                }
            ]
        },
        {
            "name": "Network Switch",
            "description": "Network switching hardware",
            "icon": "Network",
            "asset_group_name": "Network Equipment",
            "custom_fields": [
                {
                    "id": "port_count",
                    "name": "port_count",
                    "label": "Number of Ports",
                    "type": "number",
                    "required": True,
                    "default_value": 24
                },
                {
                    "id": "port_speed",
                    "name": "port_speed",
                    "label": "Port Speed",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["10/100 Mbps", "Gigabit", "10 Gigabit", "25 Gigabit", "40 Gigabit", "100 Gigabit"],
                    "default_value": "Gigabit"
                },
                {
                    "id": "management_ip",
                    "name": "management_ip",
                    "label": "Management IP Address",
                    "type": "ip_address",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "vlan_support",
                    "name": "vlan_support",
                    "label": "VLAN Support",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Router",
            "description": "Network routing hardware",
            "icon": "Wifi",
            "asset_group_name": "Network Equipment",
            "custom_fields": [
                {
                    "id": "wan_ports",
                    "name": "wan_ports",
                    "label": "WAN Ports",
                    "type": "number",
                    "required": True,
                    "default_value": 1
                },
                {
                    "id": "lan_ports",
                    "name": "lan_ports",
                    "label": "LAN Ports",
                    "type": "number",
                    "required": True,
                    "default_value": 4
                },
                {
                    "id": "wifi_standard",
                    "name": "wifi_standard",
                    "label": "WiFi Standard",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["802.11n", "802.11ac", "802.11ax (WiFi 6)", "802.11be (WiFi 7)"],
                    "default_value": "802.11ax (WiFi 6)"
                },
                {
                    "id": "vpn_support",
                    "name": "vpn_support",
                    "label": "VPN Support",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Printer",
            "description": "Office printing devices",
            "icon": "Printer",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "print_type",
                    "name": "print_type",
                    "label": "Print Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Laser", "Inkjet", "Dot Matrix", "Thermal", "3D Printer"],
                    "default_value": "Laser"
                },
                {
                    "id": "color_support",
                    "name": "color_support",
                    "label": "Color Support",
                    "type": "boolean",
                    "required": True,
                    "default_value": False
                },
                {
                    "id": "pages_per_minute",
                    "name": "pages_per_minute",
                    "label": "Pages Per Minute",
                    "type": "number",
                    "required": False,
                    "default_value": 20
                },
                {
                    "id": "network_enabled",
                    "name": "network_enabled",
                    "label": "Network Enabled",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Mobile Device",
            "description": "Smartphones and tablets",
            "icon": "Smartphone",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "device_type",
                    "name": "device_type",
                    "label": "Device Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Smartphone", "Tablet", "Smartwatch", "Other"],
                    "default_value": "Smartphone"
                },
                {
                    "id": "operating_system",
                    "name": "operating_system",
                    "label": "Operating System",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["iOS", "Android", "Windows Mobile", "Other"],
                    "default_value": "iOS"
                },
                {
                    "id": "phone_number",
                    "name": "phone_number",
                    "label": "Phone Number",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "carrier",
                    "name": "carrier",
                    "label": "Carrier",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Storage Device",
            "description": "External and internal storage devices",
            "icon": "HardDrive",
            "asset_group_name": "Storage Devices",
            "custom_fields": [
                {
                    "id": "storage_capacity",
                    "name": "storage_capacity",
                    "label": "Storage Capacity (GB)",
                    "type": "number",
                    "required": True,
                    "default_value": 1000
                },
                {
                    "id": "interface_type",
                    "name": "interface_type",
                    "label": "Interface Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["SATA", "NVMe", "USB 3.0", "USB-C", "Thunderbolt", "Ethernet"],
                    "default_value": "SATA"
                },
                {
                    "id": "storage_type",
                    "name": "storage_type",
                    "label": "Storage Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["HDD", "SSD", "NAS", "External Drive", "Cloud Storage"],
                    "default_value": "SSD"
                },
                {
                    "id": "raid_level",
                    "name": "raid_level",
                    "label": "RAID Level",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["None", "RAID 0", "RAID 1", "RAID 5", "RAID 10"],
                    "default_value": "None"
                }
            ]
        },
        {
            "name": "Monitor",
            "description": "Display monitors and screens",
            "icon": "Monitor",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "screen_size",
                    "name": "screen_size",
                    "label": "Screen Size (inches)",
                    "type": "number",
                    "required": True,
                    "default_value": 24
                },
                {
                    "id": "resolution",
                    "name": "resolution",
                    "label": "Resolution",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["1920x1080", "2560x1440", "3840x2160", "1366x768", "2560x1080"],
                    "default_value": "1920x1080"
                },
                {
                    "id": "panel_type",
                    "name": "panel_type",
                    "label": "Panel Type",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["IPS", "TN", "VA", "OLED", "QLED"],
                    "default_value": "IPS"
                },
                {
                    "id": "refresh_rate",
                    "name": "refresh_rate",
                    "label": "Refresh Rate (Hz)",
                    "type": "number",
                    "required": False,
                    "default_value": 60
                }
            ]
        },
        {
            "name": "UPS Device",
            "description": "Uninterruptible Power Supply units",
            "icon": "Zap",
            "asset_group_name": "Hardware",
            "custom_fields": [
                {
                    "id": "power_rating",
                    "name": "power_rating",
                    "label": "Power Rating (VA)",
                    "type": "number",
                    "required": True,
                    "default_value": 1500
                },
                {
                    "id": "battery_backup_time",
                    "name": "battery_backup_time",
                    "label": "Battery Backup Time (minutes)",
                    "type": "number",
                    "required": False,
                    "default_value": 15
                },
                {
                    "id": "outlet_count",
                    "name": "outlet_count",
                    "label": "Number of Outlets",
                    "type": "number",
                    "required": True,
                    "default_value": 8
                },
                {
                    "id": "network_management",
                    "name": "network_management",
                    "label": "Network Management Card",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "Security Camera",
            "description": "Surveillance and security cameras",
            "icon": "Camera",
            "asset_group_name": "Security",
            "custom_fields": [
                {
                    "id": "camera_resolution",
                    "name": "camera_resolution",
                    "label": "Camera Resolution",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["720p", "1080p", "4K", "8MP", "12MP"],
                    "default_value": "1080p"
                },
                {
                    "id": "camera_type",
                    "name": "camera_type",
                    "label": "Camera Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Indoor", "Outdoor", "PTZ", "Dome", "Bullet"],
                    "default_value": "Indoor"
                },
                {
                    "id": "night_vision",
                    "name": "night_vision",
                    "label": "Night Vision",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                },
                {
                    "id": "recording_storage",
                    "name": "recording_storage",
                    "label": "Recording Storage (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 500
                }
            ]
        }
    ]

# Duplicate endpoint removed - consolidated into enhanced version above

@api_router.get("/templates/default-assets")
async def get_default_asset_templates():
    """Get pre-defined asset templates with custom fields"""
    return [
        {
            "name": "Production Web Server",
            "description": "Production web server instance",
            "icon": "Globe",
            "asset_group_name": "Hardware",
            "asset_type_name": "Web Server",
            "custom_fields": [
                {
                    "id": "environment",
                    "name": "environment",
                    "label": "Environment",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Production", "Staging", "Development", "Testing"],
                    "default_value": "Production"
                },
                {
                    "id": "load_balancer_backend",
                    "name": "load_balancer_backend",
                    "label": "Load Balancer Backend",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                },
                {
                    "id": "domain_names",
                    "name": "domain_names",
                    "label": "Domain Names",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Employee Laptop",
            "description": "Standard employee laptop configuration",
            "icon": "Laptop",
            "asset_group_name": "Hardware",
            "asset_type_name": "Laptop",
            "custom_fields": [
                {
                    "id": "encryption_enabled",
                    "name": "encryption_enabled",
                    "label": "Full Disk Encryption",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "vpn_configured",
                    "name": "vpn_configured",
                    "label": "VPN Configured",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "assigned_user",
                    "name": "assigned_user",
                    "label": "Assigned User",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Database Server Instance",
            "description": "Production database server setup",
            "icon": "Database",
            "asset_group_name": "Hardware",
            "asset_type_name": "Server",
            "custom_fields": [
                {
                    "id": "database_name",
                    "name": "database_name",
                    "label": "Database Name",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "backup_schedule",
                    "name": "backup_schedule",
                    "label": "Backup Schedule",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Daily", "Weekly", "Monthly", "Real-time"],
                    "default_value": "Daily"
                },
                {
                    "id": "high_availability",
                    "name": "high_availability",
                    "label": "High Availability Setup",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "Office Workstation",
            "description": "Standard office desktop computer",
            "icon": "Monitor",
            "asset_group_name": "Hardware",
            "asset_type_name": "Desktop Computer",
            "custom_fields": [
                {
                    "id": "department",
                    "name": "department",
                    "label": "Department",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["IT", "Finance", "HR", "Sales", "Marketing", "Operations"],
                    "default_value": "IT"
                },
                {
                    "id": "primary_user",
                    "name": "primary_user",
                    "label": "Primary User",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "domain_joined",
                    "name": "domain_joined",
                    "label": "Domain Joined",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Network Switch Config",
            "description": "Configured network switch",
            "icon": "Network",
            "asset_group_name": "Network Equipment",
            "asset_type_name": "Network Switch",
            "custom_fields": [
                {
                    "id": "switch_location",
                    "name": "switch_location",
                    "label": "Physical Location",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "uplink_port",
                    "name": "uplink_port",
                    "label": "Uplink Port",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "managed_switch",
                    "name": "managed_switch",
                    "label": "Managed Switch",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Wireless Access Point",
            "description": "WiFi access point configuration",
            "icon": "Wifi",
            "asset_group_name": "Network Equipment",
            "asset_type_name": "Router",
            "custom_fields": [
                {
                    "id": "ssid_name",
                    "name": "ssid_name",
                    "label": "SSID Name",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "coverage_area",
                    "name": "coverage_area",
                    "label": "Coverage Area",
                    "type": "text",
                    "required": False,
                    "default_value": None
                },
                {
                    "id": "max_clients",
                    "name": "max_clients",
                    "label": "Maximum Clients",
                    "type": "number",
                    "required": False,
                    "default_value": 50
                }
            ]
        },
        {
            "name": "Color Laser Printer",
            "description": "Office color laser printer",
            "icon": "Printer", 
            "asset_group_name": "Hardware",
            "asset_type_name": "Printer",
            "custom_fields": [
                {
                    "id": "toner_levels",
                    "name": "toner_levels",
                    "label": "Toner Levels (%)",
                    "type": "number",
                    "required": False,
                    "default_value": 100
                },
                {
                    "id": "duplex_printing",
                    "name": "duplex_printing",
                    "label": "Duplex Printing",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                },
                {
                    "id": "paper_tray_capacity",
                    "name": "paper_tray_capacity",
                    "label": "Paper Tray Capacity",
                    "type": "number",
                    "required": False,
                    "default_value": 250
                }
            ]
        },
        {
            "name": "Company iPhone",
            "description": "Corporate mobile device",
            "icon": "Smartphone",
            "asset_group_name": "Hardware",
            "asset_type_name": "Mobile Device",
            "custom_fields": [
                {
                    "id": "mdm_enrolled",
                    "name": "mdm_enrolled",
                    "label": "MDM Enrolled",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "data_plan",
                    "name": "data_plan",
                    "label": "Data Plan (GB)",
                    "type": "number",
                    "required": False,
                    "default_value": 10
                },
                {
                    "id": "employee_assigned",
                    "name": "employee_assigned",
                    "label": "Assigned Employee",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Office Security Camera",
            "description": "Indoor security camera for office monitoring",
            "icon": "Camera",
            "asset_group_name": "Security",
            "asset_type_name": "Security Camera",
            "custom_fields": [
                {
                    "id": "camera_location",
                    "name": "camera_location",
                    "label": "Camera Location",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "motion_detection",
                    "name": "motion_detection",
                    "label": "Motion Detection Enabled",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "id": "audio_recording",
                    "name": "audio_recording",
                    "label": "Audio Recording",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "External Storage Drive",
            "description": "Portable external storage device",
            "icon": "HardDrive",
            "asset_group_name": "Storage Devices",
            "asset_type_name": "Storage Device",
            "custom_fields": [
                {
                    "id": "encryption_enabled",
                    "name": "encryption_enabled",
                    "label": "Hardware Encryption",
                    "type": "boolean",
                    "required": True,
                    "default_value": False
                },
                {
                    "id": "backup_purpose",
                    "name": "backup_purpose",
                    "label": "Backup Purpose",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["System Backup", "User Data", "Archive", "Temporary", "Media Storage"],
                    "default_value": "User Data"
                },
                {
                    "id": "assigned_department",
                    "name": "assigned_department",
                    "label": "Assigned Department",
                    "type": "text",
                    "required": False,
                    "default_value": None
                }
            ]
        },
        {
            "name": "Conference Room Display",
            "description": "Large display for conference rooms and presentations",
            "icon": "Monitor",
            "asset_group_name": "Hardware",
            "asset_type_name": "Monitor",
            "custom_fields": [
                {
                    "id": "room_location",
                    "name": "room_location",
                    "label": "Conference Room",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "wireless_display",
                    "name": "wireless_display",
                    "label": "Wireless Display Support",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                },
                {
                    "id": "touch_enabled",
                    "name": "touch_enabled",
                    "label": "Touch Screen Enabled",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                }
            ]
        },
        {
            "name": "Data Center UPS",
            "description": "High-capacity UPS for data center equipment",
            "icon": "Zap",
            "asset_group_name": "Hardware", 
            "asset_type_name": "UPS Device",
            "custom_fields": [
                {
                    "id": "rack_location",
                    "name": "rack_location",
                    "label": "Rack Location",
                    "type": "text",
                    "required": True,
                    "default_value": None
                },
                {
                    "id": "redundancy_level",
                    "name": "redundancy_level",
                    "label": "Redundancy Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["N", "N+1", "2N", "2N+1"],
                    "default_value": "N+1"
                },
                {
                    "id": "maintenance_contract",
                    "name": "maintenance_contract",
                    "label": "Maintenance Contract Active",
                    "type": "boolean",
                    "required": False,
                    "default_value": True
                }
            ]
        },
        {
            "name": "Corporate Firewall",
            "description": "Network firewall device for security",
            "icon": "Shield",
            "asset_group_name": "Network Equipment",
            "asset_type_name": "Network Switch",
            "custom_fields": [
                {
                    "id": "firewall_rules_count",
                    "name": "firewall_rules_count",
                    "label": "Number of Active Rules",
                    "type": "number",
                    "required": False,
                    "default_value": 50
                },
                {
                    "id": "vpn_tunnels",
                    "name": "vpn_tunnels",
                    "label": "VPN Tunnels Supported",
                    "type": "number",
                    "required": False,
                    "default_value": 10
                },
                {
                    "id": "intrusion_detection",
                    "name": "intrusion_detection",
                    "label": "Intrusion Detection Enabled",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                }
            ]
        }
    ]

# ========== CUSTOM TEMPLATE MANAGEMENT ==========

@api_router.get("/templates/custom")
async def get_custom_templates(current_user: User = Depends(get_current_user)):
    """Get custom templates created by user or public templates"""
    templates = await db.custom_templates.find({
        "$or": [
            {"created_by": current_user.id},
            {"is_public": True},
            {"organization_id": {"$in": current_user.organization_ids}}
        ]
    }).to_list(length=None)
    
    cleaned_templates = [parse_from_mongo(template) for template in templates]
    return [CustomTemplate(**template) for template in cleaned_templates]

@api_router.post("/templates/custom", response_model=CustomTemplate)
async def create_custom_template(template_data: CustomTemplateCreate, current_user: User = Depends(get_current_user)):
    """Create a new custom template"""
    template = CustomTemplate(
        **template_data.dict(),
        created_by=current_user.id
    )
    
    template_store = prepare_for_mongo(template.dict())
    await db.custom_templates.insert_one(template_store)
    
    return template

@api_router.put("/templates/custom/{template_id}", response_model=CustomTemplate)
async def update_custom_template(template_id: str, template_data: CustomTemplateCreate, current_user: User = Depends(get_current_user)):
    """Update a custom template"""
    # Verify ownership or public access
    existing_template = await db.custom_templates.find_one({"id": template_id})
    if not existing_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if existing_template["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Prepare update data
    update_data = template_data.dict()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.custom_templates.update_one(
        {"id": template_id},
        {"$set": prepare_for_mongo(update_data)}
    )
    
    # Return updated template
    updated_template_data = await db.custom_templates.find_one({"id": template_id})
    cleaned_template = parse_from_mongo(updated_template_data)
    return CustomTemplate(**cleaned_template)

@api_router.delete("/templates/custom/{template_id}")
async def delete_custom_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Delete a custom template"""
    # Verify ownership
    existing_template = await db.custom_templates.find_one({"id": template_id})
    if not existing_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if existing_template["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.custom_templates.delete_one({"id": template_id})
    return {"message": "Template deleted successfully"}

# ========== AUTO-CREATE PARENT ENTITIES ==========

@api_router.post("/templates/create-from-template")
async def create_from_template(
    template_type: str,
    template_source: str,  # 'default' or 'custom'  
    template_id_or_name: str,
    organization_id: str,
    current_user: User = Depends(get_current_user)
):
    """Create asset group/type/asset from template with auto-creation of parent entities"""
    
    # Verify access to organization
    if organization_id not in current_user.organization_ids:
        raise HTTPException(status_code=403, detail="Access denied to organization")
    
    template_data = None
    
    # Get template data
    if template_source == 'default':
        if template_type == 'asset_group':
            default_templates = await get_default_asset_group_templates()
            template_data = next((t for t in default_templates if t['name'] == template_id_or_name), None)
        elif template_type == 'asset_type':
            default_templates = await get_default_asset_type_templates()
            template_data = next((t for t in default_templates if t['name'] == template_id_or_name), None)
        elif template_type == 'asset':
            default_templates = await get_default_asset_templates()
            template_data = next((t for t in default_templates if t['name'] == template_id_or_name), None)
    else:
        # Custom template
        custom_template = await db.custom_templates.find_one({"id": template_id_or_name})
        if custom_template and custom_template["template_type"] == template_type:
            template_data = parse_from_mongo(custom_template)
    
    if not template_data:
        raise HTTPException(status_code=404, detail="Template not found")
    
    result = {"created": []}
    
    if template_type == 'asset_group':
        # Create asset group directly
        group_data = AssetGroupCreate(
            name=template_data['name'],
            description=template_data['description'],
            icon=template_data.get('icon'),
            organization_id=organization_id,
            custom_fields=template_data.get('custom_fields', [])
        )
        
        group = AssetGroup(**group_data.dict(), created_by=current_user.id)
        group_store = prepare_for_mongo(group.dict())
        await db.asset_groups.insert_one(group_store)
        
        result["created"].append({"type": "asset_group", "id": group.id, "name": group.name})
        result["primary_entity"] = {"type": "asset_group", "id": group.id}
    
    elif template_type == 'asset_type':
        # Ensure asset group exists
        asset_group_name = template_data.get('asset_group_name', 'Hardware')
        existing_group = await db.asset_groups.find_one({
            "name": asset_group_name,
            "organization_id": organization_id
        })
        
        if not existing_group:
            # Create the asset group
            group_data = AssetGroupCreate(
                name=asset_group_name,
                description=f"Auto-created for {template_data['name']} asset type",
                icon="Package",
                organization_id=organization_id,
                custom_fields=[]
            )
            
            group = AssetGroup(**group_data.dict(), created_by=current_user.id)
            group_store = prepare_for_mongo(group.dict())
            await db.asset_groups.insert_one(group_store)
            
            result["created"].append({"type": "asset_group", "id": group.id, "name": group.name})
            asset_group_id = group.id
        else:
            asset_group_id = existing_group["id"]
        
        # Create asset type
        type_data = AssetTypeCreate(
            name=template_data['name'],
            description=template_data['description'],
            icon=template_data.get('icon'),
            asset_group_id=asset_group_id,
            custom_fields=template_data.get('custom_fields', [])
        )
        
        asset_type = AssetType(**type_data.dict(), organization_id=organization_id, created_by=current_user.id)
        type_store = prepare_for_mongo(asset_type.dict())
        await db.asset_types.insert_one(type_store)
        
        result["created"].append({"type": "asset_type", "id": asset_type.id, "name": asset_type.name})
        result["primary_entity"] = {"type": "asset_type", "id": asset_type.id}
    
    elif template_type == 'asset':
        # Ensure asset group and type exist
        asset_group_name = template_data.get('asset_group_name', 'Hardware')
        asset_type_name = template_data.get('asset_type_name', 'Server')
        
        existing_group = await db.asset_groups.find_one({
            "name": asset_group_name,
            "organization_id": organization_id
        })
        
        if not existing_group:
            # Create the asset group
            group_data = AssetGroupCreate(
                name=asset_group_name,
                description=f"Auto-created for {template_data['name']} asset",
                icon="Package",
                organization_id=organization_id,
                custom_fields=[]
            )
            
            group = AssetGroup(**group_data.dict(), created_by=current_user.id)
            group_store = prepare_for_mongo(group.dict())
            await db.asset_groups.insert_one(group_store)
            
            result["created"].append({"type": "asset_group", "id": group.id, "name": group.name})
            asset_group_id = group.id
        else:
            asset_group_id = existing_group["id"]
        
        # Check for asset type
        existing_type = await db.asset_types.find_one({
            "name": asset_type_name,
            "asset_group_id": asset_group_id
        })
        
        if not existing_type:
            # Create the asset type
            type_data = AssetTypeCreate(
                name=asset_type_name,
                description=f"Auto-created for {template_data['name']} asset",
                icon=template_data.get('icon', 'Server'),
                asset_group_id=asset_group_id,
                custom_fields=[]
            )
            
            asset_type = AssetType(**type_data.dict(), organization_id=organization_id, created_by=current_user.id)
            type_store = prepare_for_mongo(asset_type.dict())
            await db.asset_types.insert_one(type_store)
            
            result["created"].append({"type": "asset_type", "id": asset_type.id, "name": asset_type.name})
            asset_type_id = asset_type.id
        else:
            asset_type_id = existing_type["id"]
        
        # Create asset
        asset_data = AssetCreate(
            name=template_data['name'],
            description=template_data['description'],
            icon=template_data.get('icon'),
            asset_type_id=asset_type_id,
            custom_fields=template_data.get('custom_fields', []),
            custom_data={},
            tags=[],
            relationships=[]
        )
        
        asset = Asset(**asset_data.dict(), asset_group_id=asset_group_id, organization_id=organization_id)
        asset_store = prepare_for_mongo(asset.dict())
        await db.assets.insert_one(asset_store)
        
        result["created"].append({"type": "asset", "id": asset.id, "name": asset.name})
        result["primary_entity"] = {"type": "asset", "id": asset.id}
    
    return result

# ========== MAIN APP SETUP ==========
app.include_router(api_router)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
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
