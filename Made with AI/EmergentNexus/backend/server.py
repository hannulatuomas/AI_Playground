from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Shared Data Models
class NodeRelation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    from_id: str
    to_id: str
    relation_type: str  # 'links-to', 'parent-of', 'references', etc.
    color: Optional[str] = "#64748b"
    label: Optional[str] = ""

class Node(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_type: str  # 'markdown', 'kanban-card', 'evidence-item', etc.
    title: str
    content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    relations: List[str] = []  # List of relation IDs
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NodeCreate(BaseModel):
    node_type: str
    title: str
    content: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

class RelationCreate(BaseModel):
    from_id: str
    to_id: str
    relation_type: str
    color: Optional[str] = "#64748b"
    label: Optional[str] = ""


# Node endpoints
@api_router.post("/nodes", response_model=Node)
async def create_node(input: NodeCreate):
    node_dict = input.model_dump()
    node_obj = Node(**node_dict)
    
    # Convert to dict and serialize datetime
    doc = node_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    result = await db.nodes.insert_one(doc)
    return node_obj

@api_router.get("/nodes", response_model=List[Node])
async def get_nodes():
    nodes = await db.nodes.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for node in nodes:
        if isinstance(node['created_at'], str):
            node['created_at'] = datetime.fromisoformat(node['created_at'])
        if isinstance(node['updated_at'], str):
            node['updated_at'] = datetime.fromisoformat(node['updated_at'])
    
    return nodes

@api_router.get("/nodes/{node_id}", response_model=Node)
async def get_node(node_id: str):
    node = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    if isinstance(node['created_at'], str):
        node['created_at'] = datetime.fromisoformat(node['created_at'])
    if isinstance(node['updated_at'], str):
        node['updated_at'] = datetime.fromisoformat(node['updated_at'])
    
    return node

@api_router.put("/nodes/{node_id}", response_model=Node)
async def update_node(node_id: str, input: NodeCreate):
    node = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    update_dict = input.model_dump()
    update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.nodes.update_one({"id": node_id}, {"$set": update_dict})
    
    updated_node = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if isinstance(updated_node['created_at'], str):
        updated_node['created_at'] = datetime.fromisoformat(updated_node['created_at'])
    if isinstance(updated_node['updated_at'], str):
        updated_node['updated_at'] = datetime.fromisoformat(updated_node['updated_at'])
    
    return updated_node

@api_router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    result = await db.nodes.delete_one({"id": node_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Also delete related relations
    await db.relations.delete_many({"$or": [{"from_id": node_id}, {"to_id": node_id}]})
    
    return {"message": "Node deleted successfully"}

@api_router.get("/nodes/type/{node_type}", response_model=List[Node])
async def get_nodes_by_type(node_type: str):
    nodes = await db.nodes.find({"node_type": node_type}, {"_id": 0}).to_list(1000)
    
    for node in nodes:
        if isinstance(node['created_at'], str):
            node['created_at'] = datetime.fromisoformat(node['created_at'])
        if isinstance(node['updated_at'], str):
            node['updated_at'] = datetime.fromisoformat(node['updated_at'])
    
    return nodes


# Relation endpoints
@api_router.post("/relations", response_model=NodeRelation)
async def create_relation(input: RelationCreate):
    relation_dict = input.model_dump()
    relation_obj = NodeRelation(**relation_dict)
    
    # Check if nodes exist
    from_node = await db.nodes.find_one({"id": input.from_id})
    to_node = await db.nodes.find_one({"id": input.to_id})
    
    if not from_node or not to_node:
        raise HTTPException(status_code=404, detail="One or both nodes not found")
    
    # Store relation
    doc = relation_obj.model_dump()
    await db.relations.insert_one(doc)
    
    return relation_obj

@api_router.get("/relations", response_model=List[NodeRelation])
async def get_relations():
    relations = await db.relations.find({}, {"_id": 0}).to_list(1000)
    return relations

@api_router.get("/relations/node/{node_id}", response_model=List[NodeRelation])
async def get_node_relations(node_id: str):
    relations = await db.relations.find({
        "$or": [{"from_id": node_id}, {"to_id": node_id}]
    }, {"_id": 0}).to_list(1000)
    return relations

@api_router.delete("/relations/{from_id}/{to_id}")
async def delete_relation(from_id: str, to_id: str):
    result = await db.relations.delete_one({"from_id": from_id, "to_id": to_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Relation not found")
    
    return {"message": "Relation deleted successfully"}


# Basic endpoints
@api_router.get("/")
async def root():
    return {"message": "Emergent Nexus API"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


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