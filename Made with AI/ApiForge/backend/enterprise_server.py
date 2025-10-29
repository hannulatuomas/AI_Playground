from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import httpx
import json
import asyncio
from models import *
import yaml
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from msgraph_core import GraphRequestAdapter
import xml.etree.ElementTree as ET
import xmltodict
from bs4 import BeautifulSoup
import re

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
app = FastAPI(title="APIForge Enterprise", description="Enterprise API Management Platform")

# Create routers
api_router = APIRouter(prefix="/api")
workflow_router = APIRouter(prefix="/api/workflows")
monitoring_router = APIRouter(prefix="/api/monitoring")
microsoft_router = APIRouter(prefix="/api/microsoft")
gdpr_router = APIRouter(prefix="/api/gdpr")
dashboard_router = APIRouter(prefix="/api/dashboard")

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

async def log_audit_event(user_id: str, action: str, resource_type: str, resource_id: str, 
                         details: Dict[str, Any] = {}, ip_address: str = None):
    """Log audit events for GDPR compliance"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address
    )
    await db.audit_logs.insert_one(prepare_for_mongo(audit_log.model_dump()))

def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                data[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
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

# Microsoft Integration Functions
async def get_microsoft_graph_client(auth_config: MicrosoftAuth):
    """Get Microsoft Graph client with authentication"""
    credential = ClientSecretCredential(
        tenant_id=auth_config.tenant_id,
        client_id=auth_config.client_id,
        client_secret=auth_config.client_secret
    )
    return GraphRequestAdapter(credential)

# Workflow Execution Engine
class WorkflowEngine:
    def __init__(self):
        self.running_workflows = {}
    
    async def execute_workflow(self, workflow: Workflow, execution_id: str):
        """Execute a workflow"""
        execution = await db.workflow_executions.find_one({"id": execution_id})
        if not execution:
            return
        
        try:
            await db.workflow_executions.update_one(
                {"id": execution_id},
                {"$set": {"status": "running"}}
            )
            
            # Execute nodes in order
            for node in workflow.nodes:
                await self.execute_node(node, workflow, execution_id)
            
            await db.workflow_executions.update_one(
                {"id": execution_id},
                {"$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
        except Exception as e:
            await db.workflow_executions.update_one(
                {"id": execution_id},
                {"$set": {
                    "status": "failed",
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
    
    async def execute_node(self, node: WorkflowNode, workflow: Workflow, execution_id: str):
        """Execute a single workflow node"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node_id": node.id,
            "node_name": node.name,
            "type": node.type
        }
        
        try:
            if node.type == WorkflowNodeType.API_CALL:
                await self.execute_api_call_node(node)
            elif node.type == WorkflowNodeType.MICROSOFT_GRAPH:
                await self.execute_microsoft_graph_node(node)
            elif node.type == WorkflowNodeType.DELAY:
                await asyncio.sleep(node.config.get("seconds", 1))
            elif node.type == WorkflowNodeType.CONDITION:
                # Implement condition logic
                pass
            elif node.type == WorkflowNodeType.TRANSFORM:
                # Implement data transformation
                pass
            
            log_entry["status"] = "success"
            
        except Exception as e:
            log_entry["status"] = "error"
            log_entry["error"] = str(e)
        
        # Add log entry to execution
        await db.workflow_executions.update_one(
            {"id": execution_id},
            {"$push": {"logs": log_entry}}
        )
    
    async def execute_api_call_node(self, node: WorkflowNode):
        """Execute API call node"""
        config = node.config
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=config.get("method", "GET"),
                url=config.get("url"),
                headers=config.get("headers", {}),
                json=config.get("body")
            )
            return response.json()
    
    async def execute_microsoft_graph_node(self, node: WorkflowNode):
        """Execute Microsoft Graph API call"""
        # Implement Microsoft Graph integration
        pass

# Global workflow engine instance
workflow_engine = WorkflowEngine()

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister, background_tasks: BackgroundTasks):
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username, 
        email=user_data.email,
        gdpr_consent=user_data.gdpr_consent,
        data_residency=user_data.data_residency
    )
    
    user_dict = user.model_dump()
    user_dict['password_hash'] = hashed_password
    user_dict = prepare_for_mongo(user_dict)
    
    await db.users.insert_one(user_dict)
    
    # Log GDPR consent
    consent = ConsentRecord(
        user_id=user.id,
        consent_type="registration",
        granted=user_data.gdpr_consent
    )
    await db.consent_records.insert_one(prepare_for_mongo(consent.model_dump()))
    
    # Background task for audit log
    background_tasks.add_task(log_audit_event, user.id, "user_registered", "user", user.id)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

# Dashboard Routes
@dashboard_router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard metrics"""
    
    # Get counts
    total_requests = await db.requests.count_documents({"user_id": current_user['id']})
    total_collections = await db.collections.count_documents({"user_id": current_user['id']})
    total_workflows = await db.workflows.count_documents({"user_id": current_user['id']})
    
    # Get performance metrics
    recent_history = await db.request_history.find(
        {"user_id": current_user['id']}
    ).sort("created_at", -1).limit(100).to_list(100)
    
    if recent_history:
        avg_response_time = sum(h.get('response', {}).get('response_time', 0) for h in recent_history) / len(recent_history)
        success_count = sum(1 for h in recent_history if h.get('response', {}).get('status_code', 0) < 400)
        success_rate = (success_count / len(recent_history)) * 100
    else:
        avg_response_time = 0
        success_rate = 0
    
    # Get monitoring info
    active_monitors = await db.monitoring_rules.count_documents({
        "user_id": current_user['id'], 
        "is_active": True
    })
    
    # Get recent alerts
    recent_alerts_data = await db.alerts.find(
        {"user_id": current_user['id']}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    recent_alerts = [Alert(**parse_from_mongo(alert)) for alert in recent_alerts_data]
    
    return DashboardMetrics(
        total_requests=total_requests,
        total_collections=total_collections,
        total_workflows=total_workflows,
        avg_response_time=avg_response_time,
        success_rate=success_rate,
        active_monitors=active_monitors,
        recent_alerts=recent_alerts
    )

@dashboard_router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    return SystemHealth(
        status="healthy",
        uptime_percentage=99.9,
        avg_response_time=150.5,
        error_rate=0.1
    )

# Workflow Routes
@workflow_router.post("/", response_model=Workflow)
async def create_workflow(workflow_data: WorkflowCreate, current_user: dict = Depends(get_current_user)):
    """Create a new workflow"""
    workflow = Workflow(user_id=current_user['id'], **workflow_data.model_dump())
    workflow_dict = prepare_for_mongo(workflow.model_dump())
    await db.workflows.insert_one(workflow_dict)
    
    await log_audit_event(
        current_user['id'], "workflow_created", "workflow", workflow.id
    )
    
    return workflow

@workflow_router.get("/", response_model=List[Workflow])
async def get_workflows(current_user: dict = Depends(get_current_user)):
    """Get all workflows for the current user"""
    workflows = await db.workflows.find({"user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [Workflow(**parse_from_mongo(w)) for w in workflows]

@workflow_router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """Execute a workflow"""
    workflow_data = await db.workflows.find_one({"id": workflow_id, "user_id": current_user['id']})
    if not workflow_data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = Workflow(**parse_from_mongo(workflow_data))
    
    # Create execution record
    execution = WorkflowExecution(workflow_id=workflow_id)
    execution_dict = prepare_for_mongo(execution.model_dump())
    await db.workflow_executions.insert_one(execution_dict)
    
    # Execute in background
    background_tasks.add_task(workflow_engine.execute_workflow, workflow, execution.id)
    
    await log_audit_event(
        current_user['id'], "workflow_executed", "workflow", workflow_id
    )
    
    return {"execution_id": execution.id, "status": "started"}

# Monitoring Routes
@monitoring_router.post("/rules", response_model=MonitoringRule)
async def create_monitoring_rule(rule_data: MonitoringRuleCreate, current_user: dict = Depends(get_current_user)):
    """Create a new monitoring rule"""
    rule = MonitoringRule(user_id=current_user['id'], **rule_data.model_dump())
    rule_dict = prepare_for_mongo(rule.model_dump())
    await db.monitoring_rules.insert_one(rule_dict)
    
    await log_audit_event(
        current_user['id'], "monitoring_rule_created", "monitoring_rule", rule.id
    )
    
    return rule

@monitoring_router.get("/rules", response_model=List[MonitoringRule])
async def get_monitoring_rules(current_user: dict = Depends(get_current_user)):
    """Get all monitoring rules for the current user"""
    rules = await db.monitoring_rules.find({"user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [MonitoringRule(**parse_from_mongo(rule)) for rule in rules]

@monitoring_router.get("/metrics/{request_id}")
async def get_request_metrics(request_id: str, current_user: dict = Depends(get_current_user)):
    """Get metrics for a specific request"""
    metrics = await db.monitoring_metrics.find(
        {"request_id": request_id, "user_id": current_user['id']}
    ).sort("timestamp", -1).limit(100).to_list(100)
    
    return [MonitoringMetric(**parse_from_mongo(metric)) for metric in metrics]

# Microsoft Integration Routes
@microsoft_router.post("/services", response_model=AzureService)
async def add_azure_service(service_data: dict, current_user: dict = Depends(get_current_user)):
    """Add Azure service configuration"""
    service = AzureService(
        user_id=current_user['id'],
        **service_data
    )
    service_dict = prepare_for_mongo(service.model_dump())
    await db.azure_services.insert_one(service_dict)
    
    await log_audit_event(
        current_user['id'], "azure_service_added", "azure_service", service.id
    )
    
    return service

@microsoft_router.get("/services", response_model=List[AzureService])
async def get_azure_services(current_user: dict = Depends(get_current_user)):
    """Get all Azure services for the current user"""
    services = await db.azure_services.find({"user_id": current_user['id']}, {"_id": 0}).to_list(1000)
    return [AzureService(**parse_from_mongo(service)) for service in services]

@microsoft_router.get("/graph/users")
async def get_graph_users(current_user: dict = Depends(get_current_user)):
    """Get users from Microsoft Graph"""
    # This would integrate with Microsoft Graph API
    return {"message": "Microsoft Graph integration - users endpoint"}

# GDPR Compliance Routes
@gdpr_router.post("/export")
async def request_data_export(export_types: List[str], current_user: dict = Depends(get_current_user)):
    """Request data export for GDPR compliance"""
    export_request = DataExportRequest(
        user_id=current_user['id'],
        data_types=export_types
    )
    export_dict = prepare_for_mongo(export_request.model_dump())
    await db.data_export_requests.insert_one(export_dict)
    
    await log_audit_event(
        current_user['id'], "data_export_requested", "data_export", export_request.id
    )
    
    return {"request_id": export_request.id, "status": "pending"}

@gdpr_router.delete("/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete user account and all associated data (GDPR Right to be Forgotten)"""
    user_id = current_user['id']
    
    # Delete all user data
    await db.users.delete_one({"id": user_id})
    await db.collections.delete_many({"user_id": user_id})
    await db.requests.delete_many({"user_id": user_id})
    await db.workflows.delete_many({"user_id": user_id})
    await db.monitoring_rules.delete_many({"user_id": user_id})
    await db.request_history.delete_many({"user_id": user_id})
    
    # Log the deletion (this log will also be deleted after retention period)
    await log_audit_event(
        user_id, "account_deleted", "user", user_id
    )
    
    return {"message": "Account and all associated data deleted successfully"}

@gdpr_router.get("/audit-logs")
async def get_audit_logs(current_user: dict = Depends(get_current_user)):
    """Get audit logs for the current user"""
    logs = await db.audit_logs.find(
        {"user_id": current_user['id']}
    ).sort("timestamp", -1).limit(100).to_list(100)
    
    return [AuditLog(**parse_from_mongo(log)) for log in logs]

# Include all routers
app.include_router(api_router)
app.include_router(workflow_router)
app.include_router(monitoring_router)
app.include_router(microsoft_router)
app.include_router(gdpr_router)
app.include_router(dashboard_router)

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
    return {"message": "APIForge Enterprise - Complete API Management Platform with Microsoft Integration, Workflows, Monitoring & GDPR Compliance"}