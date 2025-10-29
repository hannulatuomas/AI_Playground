from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
import uuid
from datetime import datetime, timezone
from enum import Enum

# User and Authentication Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    gdpr_consent: bool = True
    data_residency: str = "EU"  # EU, US, APAC

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    gdpr_consent: bool = True
    data_residency: str = "EU"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Microsoft Integration Models
class MicrosoftAuth(BaseModel):
    tenant_id: str
    client_id: str
    client_secret: str
    scope: List[str] = ["https://graph.microsoft.com/.default"]

class AzureService(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    service_type: str  # "graph", "storage", "keyvault", "functions"
    endpoint: str
    auth_config: MicrosoftAuth
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Workflow Models
class WorkflowNodeType(str, Enum):
    API_CALL = "api_call"
    CONDITION = "condition"
    TRANSFORM = "transform"
    DELAY = "delay"
    NOTIFICATION = "notification"
    MICROSOFT_GRAPH = "microsoft_graph"
    AZURE_FUNCTION = "azure_function"

class WorkflowNode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: WorkflowNodeType
    position: Dict[str, float]  # {"x": 100, "y": 200}
    config: Dict[str, Any] = {}  # Node-specific configuration
    connections: List[str] = []  # IDs of connected nodes

class Workflow(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode] = []
    user_id: str
    is_active: bool = False
    schedule: Optional[str] = None  # Cron expression
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_run: Optional[datetime] = None

class WorkflowExecution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: str  # "running", "completed", "failed", "cancelled"
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    logs: List[Dict[str, Any]] = []
    result: Optional[Dict[str, Any]] = None

# Collections and Requests (Enhanced)
class Collection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    user_id: str
    tags: List[str] = []
    is_public: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class AuthConfig(BaseModel):
    type: str = "none"  # none, bearer, basic, apikey, oauth2, microsoft
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    location: Optional[str] = "header"  # header, query
    oauth2_config: Optional[Dict[str, str]] = None
    microsoft_config: Optional[MicrosoftAuth] = None

class APIRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    protocol: str = "REST"
    method: str = "GET"
    url: str
    headers: Optional[Dict[str, str]] = {}
    query_params: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    auth: Optional[AuthConfig] = None
    collection_id: str
    user_id: str
    tags: List[str] = []
    test_script: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

# Monitoring Models
class MonitoringRule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    request_id: str
    user_id: str
    rule_type: str  # "response_time", "status_code", "uptime"
    condition: Dict[str, Any]  # {"operator": "<", "value": 500}
    interval_minutes: int = 5
    is_active: bool = True
    notifications: List[str] = []  # email addresses
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MonitoringMetric(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None

class Alert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    user_id: str
    message: str
    severity: str  # "info", "warning", "error", "critical"
    is_resolved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

# Environment Models (Enhanced)
class Environment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    variables: Dict[str, str] = {}
    user_id: str
    is_active: bool = False
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

# GDPR and Audit Models
class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DataExportRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    status: str = "pending"  # pending, processing, completed, failed
    export_format: str = "json"  # json, csv, xml
    data_types: List[str] = []  # ["requests", "collections", "workflows"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None

class ConsentRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    consent_type: str
    granted: bool
    version: str = "1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ip_address: Optional[str] = None

# Request/Response Models for API
class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    is_public: bool = False

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
    tags: List[str] = []
    test_script: Optional[str] = None

class EnvironmentCreate(BaseModel):
    name: str
    variables: Dict[str, str] = {}
    is_active: bool = False
    description: Optional[str] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode] = []
    schedule: Optional[str] = None

class MonitoringRuleCreate(BaseModel):
    name: str
    request_id: str
    rule_type: str
    condition: Dict[str, Any]
    interval_minutes: int = 5
    notifications: List[str] = []

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

# Dashboard Models
class DashboardMetrics(BaseModel):
    total_requests: int
    total_collections: int
    total_workflows: int
    avg_response_time: float
    success_rate: float
    active_monitors: int
    recent_alerts: List[Alert]

class SystemHealth(BaseModel):
    status: str  # "healthy", "degraded", "down"
    uptime_percentage: float
    avg_response_time: float
    error_rate: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))