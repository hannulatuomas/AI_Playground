from fastapi import FastAPI, APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import json
import asyncio
import subprocess
import tempfile
import openai
import anthropic
import google.generativeai as genai
from system_prompts import SYSTEM_MESSAGES
from embedding_service import get_embedding_service
from agent_memory import get_agent_memory


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
embedding_service = None
agent_memory = None

# Create the main app without a prefix
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global embedding_service, agent_memory
    try:
        logging.info("Initializing AI services...")
        embedding_service = get_embedding_service()
        agent_memory = await get_agent_memory(db)
        logging.info("AI services initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize AI services: {str(e)}")
        # Continue without embeddings if initialization fails
        embedding_service = None
        agent_memory = None

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class LLMProvider(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    model: str
    api_key: str
    endpoint: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LLMProviderCreate(BaseModel):
    name: str
    model: str
    api_key: str
    endpoint: Optional[str] = None
    is_active: bool = True

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: str
    content: str
    provider_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    agent_type: str
    provider_id: str
    summary: Optional[str] = None
    summary_at: Optional[str] = None
    messages_summarized: Optional[int] = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationCreate(BaseModel):
    title: str
    agent_type: str
    provider_id: str

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    provider_id: str
    agent_type: str
    title: Optional[str] = "New Chat"
    project_id: Optional[str] = None

class LocalModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    endpoint: str
    model_path: Optional[str] = None
    context_size: Optional[int] = 2048
    status: str = "stopped"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LocalModelCreate(BaseModel):
    name: str
    endpoint: str
    model_path: Optional[str] = None
    context_size: Optional[int] = 2048

class APIRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collection_id: Optional[str] = None
    name: str
    method: str
    url: str
    headers: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    request_type: str = "REST"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APIRequestCreate(BaseModel):
    collection_id: Optional[str] = None
    name: str
    method: str
    url: str
    headers: Optional[Dict[str, str]] = {}
    body: Optional[str] = None
    request_type: str = "REST"

class APICollection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    environment_vars: Optional[Dict[str, str]] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APICollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    environment_vars: Optional[Dict[str, str]] = {}

class CodeProject(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    language: str
    framework: Optional[str] = None
    files: Dict[str, str] = {}
    file_tree: Optional[Dict] = {}
    active_files: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CodeProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str
    framework: Optional[str] = None
    files: Optional[Dict[str, str]] = {}

class CodeExecuteRequest(BaseModel):
    language: str
    code: str
    project_id: Optional[str] = None


# System messages imported from system_prompts.py for better management
# SYSTEM_MESSAGES contains comprehensive prompts for all agents


# ============= ENHANCED CONVERSATION SUMMARIZATION SYSTEM =============

def calculate_message_importance(message: dict, embedding_svc=None) -> float:
    """
    Calculate importance score for a message based on multiple factors
    Returns a score from 0.0 to 1.0
    """
    content = message.get('content', '').lower()
    role = message.get('role', '')
    score = 0.5  # Base score
    
    # High-priority keywords that indicate important content
    critical_keywords = [
        'error', 'bug', 'issue', 'problem', 'fix', 'solution',
        'implement', 'create', 'build', 'develop', 'design',
        'requirement', 'feature', 'must', 'need', 'critical',
        'decision', 'choose', 'selected', 'approved',
        'database', 'api', 'endpoint', 'integration',
        'deployment', 'production', 'release'
    ]
    
    # Code-related indicators (very important)
    code_indicators = ['```', 'function', 'class', 'import', 'def ', 'const ', 'let ', 'var ', 'async']
    
    # Count critical keywords
    keyword_count = sum(1 for keyword in critical_keywords if keyword in content)
    if keyword_count > 0:
        score += min(0.3, keyword_count * 0.1)
    
    # Check for code blocks (high importance)
    if any(indicator in content for indicator in code_indicators):
        score += 0.2
    
    # User messages often contain requirements (slightly higher priority)
    if role == 'user':
        score += 0.1
    
    # Long, detailed messages are often important
    if len(content) > 500:
        score += 0.1
    
    # Cap at 1.0
    return min(1.0, score)


def extract_topics_from_messages(messages: list) -> dict:
    """
    Group messages by detected topics for better summarization
    Returns dict with topic -> message indices
    """
    topics = {
        'code_implementation': [],
        'errors_and_fixes': [],
        'requirements': [],
        'decisions': [],
        'general': []
    }
    
    for idx, msg in enumerate(messages):
        content = msg.get('content', '').lower()
        
        # Check for code-related content
        if any(kw in content for kw in ['```', 'function', 'class', 'implement', 'code']):
            topics['code_implementation'].append(idx)
        # Check for error-related content
        elif any(kw in content for kw in ['error', 'bug', 'issue', 'problem', 'fix']):
            topics['errors_and_fixes'].append(idx)
        # Check for requirements
        elif any(kw in content for kw in ['need', 'want', 'should', 'require', 'feature']):
            topics['requirements'].append(idx)
        # Check for decisions
        elif any(kw in content for kw in ['decide', 'choose', 'select', 'approve', 'confirm']):
            topics['decisions'].append(idx)
        else:
            topics['general'].append(idx)
    
    return topics


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count (1 token ~= 4 characters)"""
    return len(text) // 4


async def summarize_conversation_progressive(
    provider: dict, 
    messages: list,
    existing_summary: str = None,
    embedding_svc=None,
    max_context_tokens: int = 4000
) -> tuple[str, dict]:
    """
    Enhanced intelligent summarization with progressive updates and semantic analysis
    
    Returns:
        tuple: (summary_text, metadata_dict)
    """
    
    # Calculate importance scores for all messages
    message_scores = [
        (idx, msg, calculate_message_importance(msg, embedding_svc))
        for idx, msg in enumerate(messages)
    ]
    
    # Extract topics for structured summarization
    topics = extract_topics_from_messages(messages)
    
    # Build topic-based summary sections
    topic_summaries = []
    
    # Prioritize important topics
    priority_topics = [
        ('errors_and_fixes', '🔧 Issues & Resolutions'),
        ('code_implementation', '💻 Code & Implementation'),
        ('requirements', '📋 Requirements & Features'),
        ('decisions', '✓ Key Decisions'),
        ('general', '💬 Discussion')
    ]
    
    for topic_key, topic_label in priority_topics:
        if topics[topic_key]:
            # Get messages for this topic
            topic_messages = [messages[idx] for idx in topics[topic_key]]
            
            # Select most important messages (top 70% by score)
            topic_msg_scores = [(msg, calculate_message_importance(msg)) 
                                for msg in topic_messages]
            topic_msg_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Take top messages up to a token limit
            selected_msgs = []
            token_count = 0
            for msg, score in topic_msg_scores:
                msg_tokens = estimate_token_count(msg.get('content', ''))
                if token_count + msg_tokens < 1000:  # Per-topic limit
                    selected_msgs.append(msg)
                    token_count += msg_tokens
            
            if selected_msgs:
                topic_summaries.append({
                    'topic': topic_label,
                    'messages': selected_msgs,
                    'count': len(topic_messages)
                })
    
    # Build progressive summary prompt
    if existing_summary:
        summarization_prompt = """You are enhancing an existing conversation summary with new information.

EXISTING SUMMARY:
{existing_summary}

NEW MESSAGES TO INTEGRATE:
{new_messages}

TASK: Update and enhance the summary by:
1. Preserving critical information from the existing summary
2. Integrating new important details from recent messages
3. Removing redundant or outdated information
4. Maintaining technical accuracy and specificity
5. Keeping the summary concise but comprehensive

Focus on: Code changes, error resolutions, feature implementations, requirements, decisions, and project state.

Output a single cohesive summary paragraph."""
    else:
        summarization_prompt = """Create a comprehensive technical summary of this conversation.

ORGANIZE BY TOPICS:
{topic_breakdown}

REQUIREMENTS:
1. Be specific and technical (include function names, file paths, technologies)
2. Prioritize: Errors/fixes > Code implementation > Requirements > Decisions
3. Include concrete details: "Implemented X in file Y" not "Made some changes"
4. Note unresolved issues and next steps
5. Keep concise but preserve all critical context

Output a structured summary with clear sections."""
    
    # Format messages by topic
    topic_breakdown = []
    for topic_summary in topic_summaries:
        topic_label = topic_summary['topic']
        messages_text = "\n".join([
            f"  - {msg.get('role', 'user').capitalize()}: {msg.get('content', '')[:200]}..."
            for msg in topic_summary['messages'][:3]  # Top 3 per topic
        ])
        topic_breakdown.append(f"\n{topic_label} ({topic_summary['count']} messages):\n{messages_text}")
    
    # Prepare the summarization request
    if existing_summary:
        # Progressive update
        new_messages_text = "\n\n".join([
            f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
            for msg in messages[-10:]  # Last 10 messages
        ])
        
        prompt_content = summarization_prompt.format(
            existing_summary=existing_summary,
            new_messages=new_messages_text
        )
    else:
        # New summary
        prompt_content = summarization_prompt.format(
            topic_breakdown="\n".join(topic_breakdown)
        )
    
    summary_messages = [{
        "role": "user",
        "content": prompt_content
    }]
    
    try:
        summary = await call_llm(
            provider, 
            summary_messages, 
            "You are an expert at creating concise, technical conversation summaries. Be specific and preserve critical details."
        )
        
        # Generate metadata
        metadata = {
            'total_messages': len(messages),
            'topics_detected': {k: len(v) for k, v in topics.items() if v},
            'avg_importance': sum(score for _, _, score in message_scores) / len(message_scores),
            'high_priority_count': sum(1 for _, _, score in message_scores if score > 0.7),
            'estimated_tokens_saved': estimate_token_count("".join(msg.get('content', '') for msg in messages)) - estimate_token_count(summary)
        }
        
        return summary, metadata
        
    except Exception as e:
        logging.error(f"Enhanced summarization error: {str(e)}")
        
        # Intelligent fallback: Extract key points manually
        fallback_points = []
        
        # Extract errors and fixes
        for msg in messages:
            content = msg.get('content', '').lower()
            if 'error' in content or 'fix' in content:
                snippet = msg.get('content', '')[:150]
                fallback_points.append(f"Issue: {snippet}...")
        
        # Extract implementations
        for msg in messages:
            content = msg.get('content', '')
            if '```' in content or 'implement' in content.lower():
                snippet = content[:150]
                fallback_points.append(f"Implementation: {snippet}...")
        
        if fallback_points:
            summary = "Previous conversation covered:\n" + "\n".join(fallback_points[:5])
        else:
            summary = f"Previous conversation: {len(messages)} messages covering project development and discussions."
        
        metadata = {
            'total_messages': len(messages),
            'fallback_used': True
        }
        
        return summary, metadata


# Legacy function for backward compatibility
async def summarize_conversation(provider: dict, messages: list) -> str:
    """
    Legacy summarization function - calls enhanced version
    Maintained for backward compatibility
    """
    summary, _ = await summarize_conversation_progressive(provider, messages)
    return summary


# Helper function to call LLMs
async def call_llm(provider: dict, messages: list, system_message: str) -> str:
    provider_name = provider['name'].lower()
    
    try:
        if provider_name == "openai":
            client_obj = openai.AsyncOpenAI(api_key=provider['api_key'])
            response = await client_obj.chat.completions.create(
                model=provider['model'],
                messages=[{"role": "system", "content": system_message}] + messages,
                stream=False
            )
            return response.choices[0].message.content
        
        elif provider_name in ["claude", "anthropic"]:
            client_obj = anthropic.AsyncAnthropic(api_key=provider['api_key'])
            response = await client_obj.messages.create(
                model=provider['model'],
                max_tokens=4096,
                system=system_message,
                messages=messages
            )
            return response.content[0].text
        
        elif provider_name in ["google", "gemini"]:
            genai.configure(api_key=provider['api_key'])
            model = genai.GenerativeModel(provider['model'])
            
            prompt_parts = [system_message + "\\n\\n"]
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt_parts.append(f"{role}: {msg['content']}\\n")
            prompt_parts.append("Assistant: ")
            
            response = model.generate_content("".join(prompt_parts))
            return response.text
        
        elif provider_name == "local":
            import aiohttp
            endpoint = provider.get('endpoint', 'http://localhost:8080')
            
            async with aiohttp.ClientSession() as session:
                prompt_parts = [system_message + "\\n\\n"]
                for msg in messages:
                    role = msg["role"].capitalize()
                    prompt_parts.append(f"{role}: {msg['content']}\\n")
                prompt_parts.append("Assistant: ")
                
                payload = {
                    "prompt": "".join(prompt_parts),
                    "n_predict": 2048,
                    "temperature": 0.7,
                    "stop": ["User:", "\\nUser"]
                }
                
                async with session.post(f"{endpoint}/completion", json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get('content', '')
                    else:
                        raise HTTPException(status_code=500, detail="Local model error")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    except Exception as e:
        logging.error(f"LLM call error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper function for streaming
async def call_llm_stream(provider: dict, messages: list, system_message: str):
    provider_name = provider['name'].lower()
    
    try:
        if provider_name == "openai":
            client_obj = openai.AsyncOpenAI(api_key=provider['api_key'])
            stream = await client_obj.chat.completions.create(
                model=provider['model'],
                messages=[{"role": "system", "content": system_message}] + messages,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        elif provider_name in ["claude", "anthropic"]:
            client_obj = anthropic.AsyncAnthropic(api_key=provider['api_key'])
            
            async with client_obj.messages.stream(
                model=provider['model'],
                max_tokens=4096,
                system=system_message,
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        
        elif provider_name in ["google", "gemini"]:
            response_text = await call_llm(provider, messages, system_message)
            yield response_text
        
        elif provider_name == "local":
            import aiohttp
            endpoint = provider.get('endpoint', 'http://localhost:8080')
            
            prompt_parts = [system_message + "\\n\\n"]
            for msg in messages:
                role = msg["role"].capitalize()
                prompt_parts.append(f"{role}: {msg['content']}\\n")
            prompt_parts.append("Assistant: ")
            
            payload = {
                "prompt": "".join(prompt_parts),
                "n_predict": 2048,
                "temperature": 0.7,
                "stop": ["User:", "\\nUser"],
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{endpoint}/completion", json=payload) as resp:
                    if resp.status == 200:
                        async for line in resp.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8').strip())
                                    if 'content' in data:
                                        yield data['content']
                                except (json.JSONDecodeError, UnicodeDecodeError):
                                    pass
                    else:
                        raise HTTPException(status_code=500, detail="Local model error")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    except Exception as e:
        logging.error(f"LLM streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# LLM Provider endpoints
@api_router.post("/providers", response_model=LLMProvider)
async def create_provider(input: LLMProviderCreate):
    provider = LLMProvider(**input.model_dump())
    doc = provider.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.llm_providers.insert_one(doc)
    return provider

@api_router.get("/providers", response_model=List[LLMProvider])
async def get_providers():
    providers = await db.llm_providers.find({}, {"_id": 0}).to_list(1000)
    for provider in providers:
        if isinstance(provider['created_at'], str):
            provider['created_at'] = datetime.fromisoformat(provider['created_at'])
    return providers

@api_router.put("/providers/{provider_id}", response_model=LLMProvider)
async def update_provider(provider_id: str, input: LLMProviderCreate):
    doc = input.model_dump()
    result = await db.llm_providers.update_one(
        {"id": provider_id},
        {"$set": doc}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    updated = await db.llm_providers.find_one({"id": provider_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return LLMProvider(**updated)

@api_router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    result = await db.llm_providers.delete_one({"id": provider_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"message": "Provider deleted"}


# Conversation endpoints
@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(input: ConversationCreate):
    conversation = Conversation(**input.model_dump())
    doc = conversation.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.conversations.insert_one(doc)
    return conversation

@api_router.get("/conversations", response_model=List[Conversation])
async def get_conversations(agent_type: Optional[str] = None):
    query = {"agent_type": agent_type} if agent_type else {}
    conversations = await db.conversations.find(query, {"_id": 0}).sort("updated_at", -1).to_list(1000)
    for conv in conversations:
        if isinstance(conv['created_at'], str):
            conv['created_at'] = datetime.fromisoformat(conv['created_at'])
        if isinstance(conv['updated_at'], str):
            conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
    return conversations

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    result = await db.conversations.delete_one({"id": conversation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.chat_messages.delete_many({"conversation_id": conversation_id})
    return {"message": "Conversation deleted"}


@api_router.post("/conversations/{conversation_id}/summarize")
async def summarize_conversation_endpoint(conversation_id: str):
    """Manually trigger enhanced conversation summarization"""
    conversation = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    provider = await db.llm_providers.find_one({"id": conversation["provider_id"]}, {"_id": 0})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Get conversation history
    history = await db.chat_messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    messages = [{"role": msg["role"], "content": msg["content"]} 
                for msg in history if msg["role"] in ["user", "assistant"]]
    
    if len(messages) < 3:
        return {"message": "Conversation too short to summarize", "summary": None, "metadata": {}}
    
    try:
        # Use enhanced progressive summarization
        existing_summary = conversation.get('summary')
        summary, metadata = await summarize_conversation_progressive(
            provider=provider,
            messages=messages,
            existing_summary=existing_summary,
            embedding_svc=embedding_service,
            max_context_tokens=4000
        )
        
        await db.conversations.update_one(
            {"id": conversation_id},
            {"$set": {
                "summary": summary,
                "summary_at": datetime.now(timezone.utc).isoformat(),
                "messages_summarized": len(messages),
                "summary_metadata": metadata
            }}
        )
        
        return {
            "message": "Conversation summarized with enhanced intelligence", 
            "summary": summary,
            "metadata": metadata
        }
    except Exception as e:
        logging.error(f"Manual summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")



# Chat endpoints
@api_router.post("/chat")
async def chat(request: ChatRequest):
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation = Conversation(
            title=request.title,
            agent_type=request.agent_type,
            provider_id=request.provider_id
        )
        doc = conversation.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.conversations.insert_one(doc)
        conversation_id = conversation.id
    
    provider = await db.llm_providers.find_one({"id": request.provider_id}, {"_id": 0})
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    user_message = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        provider_id=request.provider_id
    )
    user_doc = user_message.model_dump()
    user_doc['timestamp'] = user_doc['timestamp'].isoformat()
    await db.chat_messages.insert_one(user_doc)
    
    history = await db.chat_messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    
    conversation_doc = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    
    messages = [{"role": msg["role"], "content": msg["content"]} 
                for msg in history if msg["role"] in ["user", "assistant"]]
    
    # Add project context if available
    project_context = ""
    if request.project_id:
        project = await db.code_projects.find_one({"id": request.project_id}, {"_id": 0})
        if project:
            files_list = list(project.get('files', {}).keys())[:10]
            project_context = f"""
CURRENT PROJECT: {project['name']}
Language: {project['language']}, Framework: {project.get('framework', 'None')}
Files: {len(project.get('files', {}))} files - {', '.join(files_list)}
You have full file access (read/create/modify/delete).
"""
    
    # Enhanced context management with embeddings and smart selection
    messages_to_send = messages
    recent_message_content = request.message
    
    # Store message embeddings if service is available
    if embedding_service:
        try:
            # Store user message for future semantic search
            embedding_service.store_message(
                conversation_id=conversation_id,
                message_id=user_message.id,
                role="user",
                content=request.message,
                metadata={"agent_type": request.agent_type}
            )
        except Exception as e:
            logging.error(f"Failed to store message embedding: {str(e)}")
    
    # ENHANCED INTELLIGENT SUMMARIZATION
    # More aggressive: triggers after 10 messages (was 15) and updates more frequently
    if len(messages) > 10:
        existing_summary = conversation_doc.get('summary')
        messages_since_last_summary = len(messages) - conversation_doc.get('messages_summarized', 0)
        
        # Trigger summarization if:
        # 1. No summary exists yet, OR
        # 2. More than 10 new messages since last summary, OR
        # 3. More than 25 messages total (aggressive summarization for long conversations)
        should_summarize = (
            not existing_summary or 
            messages_since_last_summary > 10 or
            len(messages) > 25
        )
        
        if should_summarize:
            # Progressive summarization: update existing summary with new context
            try:
                # For progressive update, use existing summary + recent messages
                # For new summary, use all messages except last 6 (keep for immediate context)
                if existing_summary and messages_since_last_summary <= 15:
                    # Progressive update: only summarize new messages
                    messages_to_summarize = messages[conversation_doc.get('messages_summarized', 0):-6]
                    logging.info(f"Progressive summary update: {len(messages_to_summarize)} new messages")
                else:
                    # Full re-summarization for very long conversations or first summary
                    messages_to_summarize = messages[:-6]
                    existing_summary = None  # Force new summary
                    logging.info(f"Full summarization: {len(messages_to_summarize)} messages")
                
                # Use enhanced progressive summarization
                summary, metadata = await summarize_conversation_progressive(
                    provider=provider,
                    messages=messages_to_summarize,
                    existing_summary=existing_summary,
                    embedding_svc=embedding_service,
                    max_context_tokens=4000
                )
                
                logging.info(f"Summarization metadata: {metadata}")
                
                # Get learnings from agent memory if available
                learnings_text = ""
                if agent_memory:
                    try:
                        # Extract learnings with improved intelligence
                        learnings = []
                        
                        # Look for error resolutions in recent messages
                        for i, msg in enumerate(messages[-15:]):
                            content_lower = msg['content'].lower()
                            
                            # Detect error patterns
                            if msg['role'] == 'assistant' and any(
                                keyword in content_lower 
                                for keyword in ['error', 'issue', 'problem', 'bug', 'fail']
                            ):
                                # Check if next few messages contain resolution
                                resolution_found = False
                                for j in range(i+1, min(i+4, len(messages[-15:]))):
                                    if any(keyword in messages[-15:][j]['content'].lower() 
                                           for keyword in ['fix', 'solved', 'resolved', 'working']):
                                        resolution_found = True
                                        break
                                
                                if resolution_found:
                                    learnings.append({
                                        'error': msg['content'][:200],
                                        'resolved': True
                                    })
                        
                        # Store learnings in agent memory
                        if learnings:
                            for learning in learnings[:3]:  # Top 3 learnings
                                try:
                                    await agent_memory.store_error_resolution(
                                        agent_type=request.agent_type,
                                        error_pattern=learning['error'][:100],
                                        resolution="Resolved in conversation",
                                        conversation_id=conversation_id,
                                        success=learning['resolved']
                                    )
                                except Exception as le:
                                    logging.error(f"Failed to store learning: {str(le)}")
                            
                            learnings_text = "\n\n💡 LEARNINGS:\n" + "\n".join([
                                f"- Resolved: {learning['error'][:150]}..."
                                for learning in learnings[:2]
                            ])
                    
                    except Exception as e:
                        logging.error(f"Failed to extract learnings: {str(e)}")
                
                # Update conversation with enhanced summary and metadata
                await db.conversations.update_one(
                    {"id": conversation_id},
                    {"$set": {
                        "summary": summary + learnings_text,
                        "summary_at": datetime.now(timezone.utc).isoformat(),
                        "messages_summarized": len(messages) - 6,  # Exclude recent messages
                        "summary_metadata": metadata
                    }}
                )
                
                # Build context with summary + recent messages
                summary_context = f"📝 CONVERSATION SUMMARY:\n{summary}{learnings_text}\n\n"
                if project_context:
                    summary_context = project_context + "\n\n" + summary_context
                
                # Use last 6 messages for immediate context (was 8, now more aggressive)
                messages_to_send = messages[-6:]
                if messages_to_send and messages_to_send[0]["role"] != "system":
                    messages_to_send.insert(0, {"role": "system", "content": summary_context})
                
                logging.info(f"Using summary + {len(messages_to_send)-1} recent messages")
                
            except Exception as e:
                logging.error(f"Enhanced summarization failed: {str(e)}")
                # Fallback: More aggressive truncation - keep last 10 messages
                messages_to_send = messages[-10:]
                if project_context:
                    messages_to_send.insert(0, {"role": "system", "content": project_context})
        else:
            # Use existing summary + recent messages
            recent_messages = messages[-6:]  # More aggressive: 6 instead of 8
            summary_message = {
                "role": "system",
                "content": f"📝 CONVERSATION SUMMARY:\n{conversation_doc['summary']}\n\n{project_context if project_context else ''}"
            }
            messages_to_send = [summary_message] + recent_messages
            logging.info(f"Using existing summary + {len(recent_messages)} recent messages")
    
    # Use smart context with embeddings if available and conversation is long
    elif embedding_service and len(messages) > 8:
        try:
            recent_messages = messages[-5:]  # Keep last 5 messages
            smart_context = embedding_service.get_smart_context(
                conversation_id=conversation_id,
                recent_messages=recent_messages,
                current_message=recent_message_content,
                max_context_messages=10
            )
            messages_to_send = smart_context
            if project_context and (not messages_to_send or messages_to_send[0]["role"] != "system"):
                messages_to_send.insert(0, {"role": "system", "content": project_context})
        except Exception as e:
            logging.error(f"Smart context failed: {str(e)}")
            messages_to_send = messages[-8:]
            if project_context:
                messages_to_send.insert(0, {"role": "system", "content": project_context})
    elif project_context:
        # Short conversation, just add project context
        messages_to_send.insert(0, {"role": "system", "content": project_context})
    
    async def generate_response():
        try:
            system_msg = SYSTEM_MESSAGES.get(request.agent_type, "You are a helpful AI assistant.")
            full_response = ""
            
            async for chunk in call_llm_stream(provider, messages_to_send, system_msg):
                full_response += chunk
                yield json.dumps({
                    "type": "chunk",
                    "content": chunk,
                    "conversation_id": conversation_id
                }) + "\\n"
            
            assistant_message = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                provider_id=request.provider_id
            )
            assistant_doc = assistant_message.model_dump()
            assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
            await db.chat_messages.insert_one(assistant_doc)
            
            # Store assistant message embedding
            if embedding_service:
                try:
                    embedding_service.store_message(
                        conversation_id=conversation_id,
                        message_id=assistant_message.id,
                        role="assistant",
                        content=full_response,
                        metadata={"agent_type": request.agent_type}
                    )
                except Exception as e:
                    logging.error(f"Failed to store assistant message embedding: {str(e)}")
            
            await db.conversations.update_one(
                {"id": conversation_id},
                {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            yield json.dumps({
                "type": "done",
                "conversation_id": conversation_id
            }) + "\\n"
            
        except Exception as e:
            logging.error(f"Chat error: {str(e)}")
            yield json.dumps({"type": "error", "error": str(e)}) + "\\n"
    
    return StreamingResponse(generate_response(), media_type="application/x-ndjson")


@api_router.get("/messages/{conversation_id}", response_model=List[ChatMessage])
async def get_messages(conversation_id: str):
    messages = await db.chat_messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg['timestamp'], str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return messages


# Local models endpoints
@api_router.post("/local-models", response_model=LocalModel)
async def create_local_model(input: LocalModelCreate):
    model = LocalModel(**input.model_dump())
    doc = model.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.local_models.insert_one(doc)
    return model

@api_router.get("/local-models", response_model=List[LocalModel])
async def get_local_models():
    models = await db.local_models.find({}, {"_id": 0}).to_list(1000)
    for model in models:
        if isinstance(model['created_at'], str):
            model['created_at'] = datetime.fromisoformat(model['created_at'])
    return models

@api_router.put("/local-models/{model_id}")
async def update_local_model(model_id: str, input: LocalModelCreate):
    doc = input.model_dump()
    result = await db.local_models.update_one(
        {"id": model_id},
        {"$set": doc}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model updated"}

@api_router.delete("/local-models/{model_id}")
async def delete_local_model(model_id: str):
    result = await db.local_models.delete_one({"id": model_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted"}

@api_router.get("/local-models/{model_id}/test")
async def test_local_model(model_id: str):
    model = await db.local_models.find_one({"id": model_id}, {"_id": 0})
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{model['endpoint']}/health", timeout=5) as resp:
                if resp.status == 200:
                    return {"status": "connected", "message": "Model is reachable"}
                else:
                    return {"status": "error", "message": f"HTTP {resp.status}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# API Testing endpoints
@api_router.post("/api-collections", response_model=APICollection)
async def create_api_collection(input: APICollectionCreate):
    collection = APICollection(**input.model_dump())
    doc = collection.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.api_collections.insert_one(doc)
    return collection

@api_router.get("/api-collections", response_model=List[APICollection])
async def get_api_collections():
    collections = await db.api_collections.find({}, {"_id": 0}).to_list(1000)
    for coll in collections:
        if isinstance(coll['created_at'], str):
            coll['created_at'] = datetime.fromisoformat(coll['created_at'])
    return collections

@api_router.put("/api-collections/{collection_id}", response_model=APICollection)
async def update_api_collection(collection_id: str, input: APICollectionCreate):
    doc = input.model_dump()
    result = await db.api_collections.update_one(
        {"id": collection_id},
        {"$set": doc}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    updated = await db.api_collections.find_one({"id": collection_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return APICollection(**updated)

@api_router.delete("/api-collections/{collection_id}")
async def delete_api_collection(collection_id: str):
    result = await db.api_collections.delete_one({"id": collection_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    await db.api_requests.delete_many({"collection_id": collection_id})
    return {"message": "Collection deleted"}

@api_router.post("/api-requests", response_model=APIRequest)
async def create_api_request(input: APIRequestCreate):
    api_request = APIRequest(**input.model_dump())
    doc = api_request.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.api_requests.insert_one(doc)
    return api_request

@api_router.get("/api-requests", response_model=List[APIRequest])
async def get_api_requests(collection_id: Optional[str] = None):
    query = {"collection_id": collection_id} if collection_id else {}
    requests = await db.api_requests.find(query, {"_id": 0}).to_list(1000)
    for req in requests:
        if isinstance(req['created_at'], str):
            req['created_at'] = datetime.fromisoformat(req['created_at'])
    return requests

@api_router.delete("/api-requests/{request_id}")
async def delete_api_request(request_id: str):
    result = await db.api_requests.delete_one({"id": request_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"message": "Request deleted"}

@api_router.post("/api-requests/{request_id}/execute")
async def execute_api_request(request_id: str, env_vars: Optional[Dict[str, str]] = None):
    import aiohttp
    import time
    
    api_req = await db.api_requests.find_one({"id": request_id}, {"_id": 0})
    if not api_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    url = api_req['url']
    headers = api_req.get('headers', {})
    body = api_req.get('body')
    
    if env_vars:
        for key, value in env_vars.items():
            url = url.replace(f"{{{{{key}}}}}", value)
            if body:
                body = body.replace(f"{{{{{key}}}}}", value)
            headers = {k: v.replace(f"{{{{{key}}}}}", value) for k, v in headers.items()}
    
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            method = api_req['method'].upper()
            
            kwargs = {
                'url': url,
                'headers': headers,
                'timeout': aiohttp.ClientTimeout(total=30)
            }
            
            if body and method in ['POST', 'PUT', 'PATCH']:
                if headers.get('Content-Type') == 'application/json':
                    kwargs['json'] = json.loads(body)
                else:
                    kwargs['data'] = body
            
            async with session.request(method, **kwargs) as resp:
                response_time = (time.time() - start_time) * 1000
                response_body = await resp.text()
                
                try:
                    response_json = json.loads(response_body)
                except json.JSONDecodeError:
                    response_json = None
                
                return {
                    "status": resp.status,
                    "statusText": resp.reason,
                    "headers": dict(resp.headers),
                    "body": response_json if response_json else response_body,
                    "responseTime": round(response_time, 2),
                    "size": len(response_body)
                }
    
    except Exception as e:
        return {
            "status": 0,
            "statusText": "Error",
            "error": str(e),
            "responseTime": 0
        }


# Code Project endpoints
@api_router.post("/code-projects", response_model=CodeProject)
async def create_code_project(input: CodeProjectCreate):
    project = CodeProject(**input.model_dump())
    doc = project.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.code_projects.insert_one(doc)
    return project

@api_router.get("/code-projects", response_model=List[CodeProject])
async def get_code_projects():
    projects = await db.code_projects.find({}, {"_id": 0}).to_list(1000)
    for proj in projects:
        if isinstance(proj['created_at'], str):
            proj['created_at'] = datetime.fromisoformat(proj['created_at'])
        if isinstance(proj['updated_at'], str):
            proj['updated_at'] = datetime.fromisoformat(proj['updated_at'])
    return projects

@api_router.get("/code-projects/{project_id}", response_model=CodeProject)
async def get_code_project(project_id: str):
    project = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if isinstance(project['created_at'], str):
        project['created_at'] = datetime.fromisoformat(project['created_at'])
    if isinstance(project['updated_at'], str):
        project['updated_at'] = datetime.fromisoformat(project['updated_at'])
    return CodeProject(**project)

@api_router.put("/code-projects/{project_id}", response_model=CodeProject)
async def update_code_project(project_id: str, input: CodeProjectCreate):
    doc = input.model_dump()
    doc['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    result = await db.code_projects.update_one(
        {"id": project_id},
        {"$set": doc}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if isinstance(updated['created_at'], str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    if isinstance(updated['updated_at'], str):
        updated['updated_at'] = datetime.fromisoformat(updated['updated_at'])
    return CodeProject(**updated)

@api_router.delete("/code-projects/{project_id}")
async def delete_code_project(project_id: str):
    result = await db.code_projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


# File Management endpoints
@api_router.post("/code-projects/{project_id}/files")
async def create_file(project_id: str, file_path: str = Body(...), content: str = Body(default="")):
    project = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get('files', {})
    files[file_path] = content
    
    await db.code_projects.update_one(
        {"id": project_id},
        {"$set": {
            "files": files,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "File created/updated", "file_path": file_path}


@api_router.get("/code-projects/{project_id}/files/{file_path:path}")
async def get_file(project_id: str, file_path: str):
    project = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get('files', {})
    if file_path not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"file_path": file_path, "content": files[file_path]}


@api_router.delete("/code-projects/{project_id}/files/{file_path:path}")
async def delete_file(project_id: str, file_path: str):
    project = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get('files', {})
    if file_path not in files:
        raise HTTPException(status_code=404, detail="File not found")
    
    del files[file_path]
    
    await db.code_projects.update_one(
        {"id": project_id},
        {"$set": {
            "files": files,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {"message": "File deleted"}


@api_router.get("/code-projects/{project_id}/file-tree")
async def get_file_tree(project_id: str):
    project = await db.code_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    files = project.get('files', {})
    
    tree = {}
    for file_path in files.keys():
        parts = file_path.split('/')
        current = tree
        
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                current[part] = {"type": "file", "path": file_path}
            else:
                if part not in current:
                    current[part] = {"type": "directory", "children": {}}
                current = current[part]["children"]
    
    return {"tree": tree, "files": list(files.keys())}


@api_router.post("/code-projects/{project_id}/active-files")
async def update_active_files(project_id: str, file_paths: List[str] = Body(...)):
    result = await db.code_projects.update_one(
        {"id": project_id},
        {"$set": {"active_files": file_paths}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Active files updated", "active_files": file_paths}


# ============= AI API TESTING ENDPOINTS =============

class AIRequestBuilderInput(BaseModel):
    description: str
    provider_id: str

class AIAnalysisInput(BaseModel):
    request: Dict
    response: Dict
    provider_id: str
    analysis_type: str  # "response", "security", "explain"

class AITestDataInput(BaseModel):
    endpoint: str
    method: str
    description: Optional[str] = None
    provider_id: str

class AIDocumentationInput(BaseModel):
    documentation: str
    provider_id: str

@api_router.post("/ai/build-request")
async def ai_build_request(input: AIRequestBuilderInput):
    """AI Request Builder: Natural language description -> Complete API request"""
    try:
        provider = await db.llm_providers.find_one({"id": input.provider_id}, {"_id": 0})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        system_prompt = """You are an expert API testing assistant. Given a natural language description, 
generate a complete, valid API request configuration in JSON format.

Your response MUST be a valid JSON object with this exact structure:
{
  "method": "GET|POST|PUT|PATCH|DELETE",
  "url": "complete URL with protocol",
  "headers": {"Header-Name": "value"},
  "queryParams": [{"key": "name", "value": "value", "enabled": true}],
  "bodyType": "none|json|raw|form-data|xml",
  "body": "body content based on bodyType",
  "description": "brief explanation of what this request does"
}

Be specific with URLs, headers, and body content. Use realistic example data.
Only respond with the JSON object, nothing else."""

        user_message = f"Create an API request for: {input.description}"
        
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        # Call LLM
        async def generate():
            try:
                full_response = ""
                async for chunk in call_llm_stream(provider, messages, system_prompt):
                    full_response += chunk
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                
                # Try to parse and validate the response
                try:
                    parsed = json.loads(full_response)
                    yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', full_response, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(1))
                        yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                    else:
                        yield json.dumps({"type": "error", "message": "Failed to parse AI response"}) + "\n"
                        
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/analyze-response")
async def ai_analyze_response(input: AIAnalysisInput):
    """Smart Response Analysis: Analyze API response and provide insights"""
    try:
        provider = await db.llm_providers.find_one({"id": input.provider_id}, {"_id": 0})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        request_info = f"""
Request:
- Method: {input.request.get('method')}
- URL: {input.request.get('url')}
- Headers: {json.dumps(input.request.get('headers', {}), indent=2)}
- Body: {input.request.get('body', 'None')}
"""
        
        response_info = f"""
Response:
- Status: {input.response.get('status')} {input.response.get('statusText')}
- Time: {input.response.get('responseTime')}ms
- Size: {input.response.get('size')} bytes
- Body: {json.dumps(input.response.get('body', {}), indent=2)}
"""
        
        if input.analysis_type == "response":
            system_prompt = """You are an expert API testing assistant. Analyze the API request and response.

Provide a detailed analysis including:
1. **Response Status**: What the status code means
2. **Data Structure**: Analyze the response structure and data types
3. **Potential Issues**: Identify any problems, errors, or unexpected behavior
4. **Suggestions**: Recommendations for improvement or follow-up tests
5. **Key Insights**: Important observations about the API behavior

Be specific, technical, and actionable."""

        elif input.analysis_type == "security":
            system_prompt = """You are a security expert analyzing API requests and responses.

Perform a comprehensive security analysis:
1. **Authentication Issues**: Check for weak or missing authentication
2. **Authorization Problems**: Identify potential privilege escalation
3. **Data Exposure**: Look for sensitive data in responses
4. **Input Validation**: Assess request parameter handling
5. **Security Headers**: Check for missing security headers
6. **Vulnerabilities**: Identify common API vulnerabilities (OWASP API Top 10)
7. **Recommendations**: Specific security improvements

Be thorough and prioritize by severity (Critical, High, Medium, Low)."""

        else:  # explain
            system_prompt = """You are an API documentation expert. Explain what this API endpoint does.

Provide a comprehensive explanation:
1. **Purpose**: What this endpoint is designed to do
2. **Functionality**: How it works and what it returns
3. **Parameters**: Explain query params, headers, and body fields
4. **Response Format**: Structure and meaning of response data
5. **Use Cases**: When and why to use this endpoint
6. **Best Practices**: How to use it effectively

Make it clear and educational."""
        
        user_message = request_info + "\n" + response_info
        
        messages = [{"role": "user", "content": user_message}]
        
        async def generate():
            try:
                async for chunk in call_llm_stream(provider, messages, system_prompt):
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                yield json.dumps({"type": "complete"}) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/generate-test-data")
async def ai_generate_test_data(input: AITestDataInput):
    """Auto-generate realistic test data for API requests"""
    try:
        provider = await db.llm_providers.find_one({"id": input.provider_id}, {"_id": 0})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        system_prompt = """You are an expert at generating realistic test data for API testing.

Generate realistic, varied test data that covers:
1. **Happy Path**: Valid data that should work
2. **Edge Cases**: Boundary values, empty strings, max lengths
3. **Error Cases**: Invalid data to test error handling
4. **Different Scenarios**: Various realistic use cases

Provide the test data as a JSON array of test cases, each with:
- name: Description of the test case
- type: "valid", "edge", or "error"
- data: The actual test data object
- expectedResult: What should happen

Only respond with valid JSON."""
        
        description = input.description or f"Generate test data for {input.method} {input.endpoint}"
        user_message = f"""
Endpoint: {input.endpoint}
Method: {input.method}
Description: {description}

Generate comprehensive test data covering multiple scenarios."""
        
        messages = [{"role": "user", "content": user_message}]
        
        async def generate():
            try:
                full_response = ""
                async for chunk in call_llm_stream(provider, messages, system_prompt):
                    full_response += chunk
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                
                # Try to parse JSON
                try:
                    parsed = json.loads(full_response)
                    yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                except (json.JSONDecodeError, ValueError):
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', full_response, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(1))
                        yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                        
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/parse-documentation")
async def ai_parse_documentation(input: AIDocumentationInput):
    """Parse API documentation and create request configuration"""
    try:
        provider = await db.llm_providers.find_one({"id": input.provider_id}, {"_id": 0})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        system_prompt = """You are an expert at parsing API documentation and creating request configurations.

From the provided API documentation, extract and create a complete API request configuration.

Your response MUST be valid JSON with this structure:
{
  "method": "HTTP method",
  "url": "complete endpoint URL",
  "headers": {"required headers": "values"},
  "queryParams": [{"key": "param name", "value": "example value", "description": "what it does", "enabled": true}],
  "bodyType": "none|json|raw|form-data|xml",
  "body": "example request body with realistic data",
  "authentication": "description of auth requirements",
  "description": "what this endpoint does",
  "notes": "important notes or warnings"
}

Be thorough and accurate. Use realistic example values."""
        
        user_message = f"Parse this API documentation and create a request:\n\n{input.documentation}"
        
        messages = [{"role": "user", "content": user_message}]
        
        async def generate():
            try:
                full_response = ""
                async for chunk in call_llm_stream(provider, messages, system_prompt):
                    full_response += chunk
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                
                try:
                    parsed = json.loads(full_response)
                    yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                except (json.JSONDecodeError, ValueError):
                    import re
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', full_response, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(1))
                        yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                        
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/ai/generate-assertions")
async def ai_generate_assertions(input: AIAnalysisInput):
    """Auto-generate test assertions based on request and response"""
    try:
        provider = await db.llm_providers.find_one({"id": input.provider_id}, {"_id": 0})
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        system_prompt = """You are an expert at writing API test assertions.

Generate comprehensive test assertions in multiple formats (JavaScript/Jest, Python/pytest, and plain English).

Include assertions for:
1. Status code validation
2. Response time benchmarks
3. Response structure validation
4. Data type checks
5. Required field presence
6. Value range validation
7. Error handling scenarios

Format your response as JSON:
{
  "javascript": "// Jest test code",
  "python": "# pytest test code",
  "descriptions": ["Assertion 1 description", "Assertion 2 description"]
}"""
        
        request_info = json.dumps(input.request, indent=2)
        response_info = json.dumps(input.response, indent=2)
        
        user_message = f"Generate test assertions for:\n\nRequest:\n{request_info}\n\nResponse:\n{response_info}"
        
        messages = [{"role": "user", "content": user_message}]
        
        async def generate():
            try:
                full_response = ""
                async for chunk in call_llm_stream(provider, messages, system_prompt):
                    full_response += chunk
                    yield json.dumps({"type": "chunk", "content": chunk}) + "\n"
                
                try:
                    parsed = json.loads(full_response)
                    yield json.dumps({"type": "complete", "data": parsed}) + "\n"
                except (json.JSONDecodeError, ValueError):
                    pass
                        
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
        
        return StreamingResponse(generate(), media_type="application/x-ndjson")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/")
async def root():
    return {"message": "DevGenius AI API"}


# Include the router in the main app
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
